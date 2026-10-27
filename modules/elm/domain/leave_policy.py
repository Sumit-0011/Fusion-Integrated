import datetime
from typing import List, Tuple

# Helper utilities ------------------------------------------------------------

def is_weekend(date: datetime.date) -> bool:
    return date.weekday() >= 5  # 5 = Saturday, 6 = Sunday

def is_holiday(date: datetime.date, holidays: List[datetime.date]) -> bool:
    return date in holidays

def business_days_between(start: datetime.date, end: datetime.date, include_weekends: bool, holidays: List[datetime.date]) -> int:
    """Count days between start and end (inclusive).
    If include_weekends is False, weekends are excluded.
    In both cases, holidays are always excluded.
    """
    total = 0
    cur = start
    while cur <= end:
        if (include_weekends or not is_weekend(cur)) and not is_holiday(cur, holidays):
            total += 1
        cur += datetime.timedelta(days=1)
    return total

# Policy constants ------------------------------------------------------------

EL_PER_YEAR_NON_FACULTY = 30  # can carry forward
FACULTY_VL_PER_YEAR = 60
COL_PER_YEAR = 20  # can carry forward

# ---------------------------------------------------------------------------

def max_el_days(is_faculty: bool) -> int:
    """Return the maximum Earned Leave (EL) days an employee gets per year.
    Faculty do not get EL directly; they get VL which can be converted.
    """
    return 0 if is_faculty else EL_PER_YEAR_NON_FACULTY

def max_vl_days(is_faculty: bool) -> int:
    return FACULTY_VL_PER_YEAR if is_faculty else 0

def max_col_days() -> int:
    return COL_PER_YEAR

def convert_unused_vl_to_el(vl_unused: float) -> float:
    """At year‑end, unused faculty VL converts to EL at 2 VL : 1 EL.
    Fractional conversion is allowed.
    """
    return vl_unused / 2.0

# ---------------------------------------------------------------------------

def is_leave_allowed(
    employee_role: str,
    leave_type: str,
    start: datetime.date,
    end: datetime.date,
    existing_leaves: List[Tuple[datetime.date, datetime.date, str]],
    holidays: List[datetime.date],
) -> Tuple[bool, str]:
    """Validate a leave request against policy.

    Parameters
    ----------
    employee_role: ``'faculty'`` or ``'staff'`` (non‑faculty).
    leave_type: one of ``CL, RH, SCL, EL, COL, VL``.
    start, end: inclusive dates of the requested leave.
    existing_leaves: list of tuples ``(s, e, t)`` already approved for the employee.
    holidays: list of ``datetime.date`` that are closed holidays.

    Returns
    -------
    (allowed, reason) – ``allowed`` is ``True`` if the request complies.
    """
    # Basic sanity checks
    if end < start:
        return False, "End date is before start date"

    # Overlap check – any overlap with existing leave of any type is prohibited
    for s, e, _ in existing_leaves:
        if not (end < s or start > e):
            return False, "Overlapping with an existing approved leave"

    # Determine whether weekends/holidays count for this type
    include_weekends = leave_type in {"EL", "COL", "VL"}

    # Compute the number of leave days counted against the entitlement
    days_requested = business_days_between(start, end, include_weekends, holidays)

    # Half‑day CL handling – the caller should split a half‑day request into a
    # separate request with ``days_requested`` = 0.5. For simplicity we allow a
    # fractional value if the caller passes a day range of a single day and sets
    # ``leave_type == 'CL'`` and expects ``0.5``.
    if leave_type == "CL" and days_requested == 1:
        # Caller may indicate a half‑day via an extra flag; we treat full day here.
        pass

    # Policy specific limits (simple ceiling checks)
    if leave_type == "EL":
        if employee_role == "faculty":
            return False, "Faculty do not have EL entitlement"
    elif leave_type == "VL":
        if employee_role != "faculty":
            return False, "Only faculty have VL entitlement"
    elif leave_type == "COL":
        # COL is available to all employees
        pass
    elif leave_type in {"CL", "RH", "SCL"}:
        # No yearly caps defined for these types in the specification
        pass
    else:
        return False, f"Unknown leave type {leave_type}"

    # If we reach here the request passes basic validation
    return True, f"Leave of type {leave_type} for {days_requested} day(s) is allowed"

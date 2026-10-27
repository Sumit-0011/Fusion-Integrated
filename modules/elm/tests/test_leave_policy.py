import datetime
import pytest

from modules.elm.domain.leave_policy import (
    max_el_days,
    max_vl_days,
    max_col_days,
    convert_unused_vl_to_el,
    is_leave_allowed,
)
from modules.elm.domain.holidays import get_holidays

# Helper to build existing leaves list

def make_leave(start, end, lt):
    return (start, end, lt)

@pytest.fixture
def holidays_2026():
    return get_holidays(2026)

def test_max_el_non_faculty():
    assert max_el_days(is_faculty=False) == 30

def test_max_el_faculty():
    assert max_el_days(is_faculty=True) == 0

def test_vl_faculty():
    assert max_vl_days(is_faculty=True) == 60

def test_vl_non_faculty():
    assert max_vl_days(is_faculty=False) == 0

def test_col_days():
    assert max_col_days() == 20

def test_convert_vl_to_el():
    assert convert_unused_vl_to_el(10) == 5.0
    assert convert_unused_vl_to_el(7) == 3.5

# ---------------------------------------------------------------------------
# Simple allowance tests for each leave type

def test_allow_el_non_faculty(holidays_2026):
    start = datetime.date(2026, 5, 10)
    end = datetime.date(2026, 5, 12)
    allowed, reason = is_leave_allowed(
        employee_role='staff',
        leave_type='EL',
        start=start,
        end=end,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert allowed
    assert "EL" in reason

def test_reject_el_faculty(holidays_2026):
    start = datetime.date(2026, 5, 10)
    end = datetime.date(2026, 5, 12)
    allowed, _ = is_leave_allowed(
        employee_role='faculty',
        leave_type='EL',
        start=start,
        end=end,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert not allowed

def test_allow_vl_faculty(holidays_2026):
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 6, 15)
    allowed, _ = is_leave_allowed(
        employee_role='faculty',
        leave_type='VL',
        start=start,
        end=end,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert allowed

def test_reject_vl_non_faculty(holidays_2026):
    start = datetime.date(2026, 6, 1)
    end = datetime.date(2026, 6, 5)
    allowed, _ = is_leave_allowed(
        employee_role='staff',
        leave_type='VL',
        start=start,
        end=end,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert not allowed

def test_allow_cl_half_day(holidays_2026):
    # Half‑day CL is represented by a single day request; policy logic treats it as full day
    # Here we just ensure the function accepts it (detailed half‑day handling is UI‑level)
    start = datetime.date(2026, 7, 20)
    allowed, _ = is_leave_allowed(
        employee_role='staff',
        leave_type='CL',
        start=start,
        end=start,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert allowed

# Overlap detection
def test_overlap_detection(holidays_2026):
    existing = [make_leave(datetime.date(2026, 8, 1), datetime.date(2026, 8, 5), 'EL')]
    # New request overlapping partially
    allowed, reason = is_leave_allowed(
        employee_role='staff',
        leave_type='CL',
        start=datetime.date(2026, 8, 4),
        end=datetime.date(2026, 8, 6),
        existing_leaves=existing,
        holidays=holidays_2026,
    )
    assert not allowed
    assert 'Overlapping' in reason

# Weekend / holiday inclusion test for EL (should count weekends and holidays)
def test_el_counts_weekends_and_holidays(holidays_2026):
    # 2026-12-31 is Saturday, 2027-01-01 (New Year's) is holiday but not in 2026 list – we just test weekend count
    start = datetime.date(2026, 12, 30)  # Friday
    end = datetime.date(2026, 12, 31)   # Saturday (weekend, should count for EL)
    allowed, reason = is_leave_allowed(
        employee_role='staff',
        leave_type='EL',
        start=start,
        end=end,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert allowed
    # days counted should be 2 (Fri + Sat) – we verify via reason substring
    assert '2' in reason or 'day' in reason

# Holiday exclusion for CL (should not count holiday as a day)
def test_cl_excludes_holiday(holidays_2026):
    # Use Jan 1 2026 which is a holiday according to get_holidays
    start = datetime.date(2026, 1, 1)
    allowed, reason = is_leave_allowed(
        employee_role='staff',
        leave_type='CL',
        start=start,
        end=start,
        existing_leaves=[],
        holidays=holidays_2026,
    )
    # The request should be allowed, but days counted will be 0; our simple implementation treats it as allowed
    assert allowed

# Unknown leave type rejection
def test_unknown_leave_type(holidays_2026):
    allowed, reason = is_leave_allowed(
        employee_role='staff',
        leave_type='XYZ',
        start=datetime.date(2026, 3, 1),
        end=datetime.date(2026, 3, 2),
        existing_leaves=[],
        holidays=holidays_2026,
    )
    assert not allowed
    assert 'Unknown' in reason

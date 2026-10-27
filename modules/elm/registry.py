# Module metadata for ELM (Employee Leave Management)
MODULE = {
    "code": "elm",
    "label": "Employee Leave Management",
    "icon": "CalendarCheck",
    "base_path": "/elm",
    "nav_section": "Leave Management",
    "sort_order": 20,
    "status": "inactive",  # will be enabled once fully implemented
}

# Permissions recognized by the ELM module. The string format mirrors other modules:
# "elm.<entity>.<action>"
PERMISSIONS = [
    ("elm.leave.apply", "Apply for a leave request"),
    ("elm.leave.approve", "Approve / reject a leave request"),
    ("elm.leave.cancel", "Cancel a pending leave request"),
    ("elm.leave.modify", "Modify an ongoing leave request (extension, early return)"),
    ("elm.leave.view_self", "View own leave history"),
    ("elm.leave.view_all", "View all employees' leave history (manager / unit head)"),
    ("elm.leave.report", "Generate leave balance and year‑end reports"),
]

# Simple role definitions – these will be referenced by the IAM via ROLE_GRANTS.
# The actual hierarchy (unit head → manager → employee) is enforced elsewhere.
_EMPLOYEE = ["elm.leave.apply", "elm.leave.view_self"]
_MANAGER = [_EMPLOYEE[0], "elm.leave.approve", "elm.leave.cancel", "elm.leave.view_all", "elm.leave.report"]
_UNIT_HEAD = [_MANAGER[0], "elm.leave.modify", "elm.leave.report"]

ROLE_GRANTS = {
    "employee": _EMPLOYEE,
    "manager": _MANAGER,
    "unit_head": _UNIT_HEAD,
}

from modules.department.models.allocation import (
    TAAllocation,
    ThesisSupervisorAllocation,
)
from modules.department.models.announcement import (
    DepartmentAnnouncement,
)
from modules.department.models.seminar import (
    GraduateSeminar,
    SeminarSchedulingHistory,
    SeminarSchedulingRequest,
)

__all__ = [
    "DepartmentAnnouncement",
    "GraduateSeminar",
    "SeminarSchedulingHistory",
    "SeminarSchedulingRequest",
    "TAAllocation",
    "ThesisSupervisorAllocation",
]


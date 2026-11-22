"""Functional Requirements (FR) specification-driven tests for Department module.

Covers CFR-OAP-019 to CFR-OAP-022 and AFR-OAP-043 to AFR-OAP-051 per FR_DESIGN.json.
"""
from __future__ import annotations

import pytest

from modules.department.models.allocation import TAAllocation, ThesisSupervisorAllocation
from modules.department.models.announcement import DepartmentAnnouncement
from modules.department.models.seminar import (
    GraduateSeminar,
    SeminarSchedulingHistory,
    SeminarSchedulingRequest,
)
from modules.department.tests.spec.conftest import future_date_str

pytestmark = pytest.mark.django_db


def test_fr_dep_001_supervisor_assignment(admin_client):
    """FR-DEP-001 | CFR-OAP-019 / AFR-OAP-043 - supervisor assignment.

    Verify Department Administrator can record a thesis supervisor assignment.
    """
    payload = {
        "student_id": 1001,
        "student_name": "Aman Verma",
        "programme": "M.Tech",
        "department": "CSE",
        "supervisor_id": 201,
        "supervisor_name": "Dr. P. Gupta",
        "co_supervisor_name": "Dr. R. Sen",
        "thesis_topic": "Deep Learning for Audio Signals",
        "academic_year": "2026-27",
    }
    resp = admin_client.post("/api/v1/department/allocations/supervisors/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["student_id"] == 1001
    assert resp.data["supervisor_id"] == 201
    assert ThesisSupervisorAllocation.objects.filter(student_id=1001, supervisor_id=201).exists()


def test_fr_dep_002_unauthorized_supervisor_assignment(student_client):
    """FR-DEP-002 | CFR-OAP-019 / AFR-OAP-043 - unauthorized supervisor assignment.

    Verify an unauthorized user cannot record a thesis supervisor assignment.
    """
    payload = {
        "student_id": 1002,
        "student_name": "Rohan Das",
        "programme": "M.Tech",
        "department": "CSE",
        "supervisor_id": 202,
        "supervisor_name": "Dr. S. Roy",
    }
    resp = student_client.post("/api/v1/department/allocations/supervisors/", data=payload, format="json")
    assert resp.status_code == 403
    assert not ThesisSupervisorAllocation.objects.filter(student_id=1002).exists()


def test_fr_dep_003_ta_assignment_course_and_faculty(admin_client):
    """FR-DEP-003 | CFR-OAP-019 / AFR-OAP-044 - TA assignment to course and faculty.

    Verify Department Administrator can record TA assignment linking scholar to course and faculty.
    """
    payload = {
        "student_id": 1003,
        "student_name": "Kavita Rao",
        "programme": "M.Tech",
        "department": "CSE",
        "course_code": "CS301",
        "course_name": "Operating Systems",
        "faculty_id": 203,
        "faculty_name": "Dr. K. Nair",
        "semester": "Monsoon",
        "academic_year": "2026-27",
        "hours_per_week": 8,
    }
    resp = admin_client.post("/api/v1/department/allocations/ta/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["course_code"] == "CS301"
    assert resp.data["faculty_id"] == 203
    assert TAAllocation.objects.filter(student_id=1003, course_code="CS301", faculty_id=203).exists()


def test_fr_dep_004_ta_assignment_course_only(admin_client):
    """FR-DEP-004 | CFR-OAP-019 / AFR-OAP-044 - TA assignment to course only.

    Verify Department Administrator can record TA assignment linking to course only.
    """
    payload = {
        "student_id": 1004,
        "student_name": "Vikas Singh",
        "programme": "Ph.D.",
        "department": "CSE",
        "course_code": "CS101",
        "course_name": "Introduction to Programming",
        "faculty_id": None,
        "faculty_name": "",
        "hours_per_week": 6,
    }
    resp = admin_client.post("/api/v1/department/allocations/ta/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["course_code"] == "CS101"
    assert resp.data["faculty_id"] is None
    assert TAAllocation.objects.filter(student_id=1004, course_code="CS101", faculty_id__isnull=True).exists()


def test_fr_dep_005_ta_assignment_faculty_only(admin_client):
    """FR-DEP-005 | CFR-OAP-019 / AFR-OAP-044 - TA assignment to faculty only.

    Verify Department Administrator can record TA assignment linking to faculty only.
    """
    payload = {
        "student_id": 1005,
        "student_name": "Meera Patel",
        "programme": "M.Tech",
        "department": "CSE",
        "course_code": "",
        "course_name": "Departmental Lab Duties",
        "faculty_id": 205,
        "faculty_name": "Dr. V. Sharma",
        "hours_per_week": 8,
    }
    resp = admin_client.post("/api/v1/department/allocations/ta/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["faculty_id"] == 205
    assert TAAllocation.objects.filter(student_id=1005, faculty_id=205).exists()


def test_fr_dep_006_pg_student_initiates_seminar_request(student_client):
    """FR-DEP-006 | CFR-OAP-020 / AFR-OAP-045 - PG student initiates seminar request.

    Verify a postgraduate student can initiate a graduate seminar scheduling request.
    """
    payload = {
        "topic": "Zero-Knowledge Proofs in Blockchain Scalability",
        "abstract": "We evaluate recursive zk-SNARK constructions on decentralized ledgers.",
        "programme": "Ph.D.",
        "department": "CSE",
        "preferred_date": future_date_str(10),
    }
    resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["status"] == "AWAITING_SCHEDULING"
    assert resp.data["topic"] == payload["topic"]
    assert SeminarSchedulingRequest.objects.filter(topic=payload["topic"], status="AWAITING_SCHEDULING").exists()


def test_fr_dep_007_undergraduate_student_prohibited(make_dept_client):
    """FR-DEP-007 | CFR-OAP-020 / AFR-OAP-045 - Undergraduate student prohibited.

    Verify an undergraduate student attempting to initiate a seminar request is rejected.
    """
    ug_client = make_dept_client(user_id=1007, role="student", permissions=("department.seminar.request",))
    payload = {
        "topic": "Undergraduate Capstone Seminar",
        "abstract": "Undergraduate seminar presentation.",
        "programme": "B.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(12),
    }
    resp = ug_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert resp.status_code in (400, 403)
    assert not SeminarSchedulingRequest.objects.filter(topic=payload["topic"]).exists()


def test_fr_dep_008_pending_requests_available_to_admin(admin_client, student_client):
    """FR-DEP-008 | CFR-OAP-020 / AFR-OAP-046 - Pending requests available to Department Administrator.

    Verify submitted seminar requests in AWAITING_SCHEDULING status appear in the admin pending queue.
    """
    # Create request as student
    payload = {
        "topic": "Federated Learning over Non-IID Mobile Datasets",
        "abstract": "Convergence rate improvements under differential privacy constraints.",
        "programme": "M.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(15),
    }
    create_resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert create_resp.status_code == 201
    req_id = create_resp.data["id"]

    # Admin queries pending queue
    resp = admin_client.get("/api/v1/department/pending/")
    assert resp.status_code == 200
    pending_ids = [item["id"] for item in (resp.data.get("results") or resp.data)]
    assert req_id in pending_ids


def test_fr_dep_009_admin_schedules_seminar(admin_client, student_client):
    """FR-DEP-009 | CFR-OAP-021 / AFR-OAP-047 - Department Administrator schedules seminar.

    Verify Department Administrator can schedule a pending seminar request.
    """
    # 1. Create request
    payload = {
        "topic": "Graph Attention Networks for Drug Discovery",
        "abstract": "Screening molecular graphs using relational graph transformers.",
        "programme": "Ph.D.",
        "department": "CSE",
        "preferred_date": future_date_str(20),
    }
    create_resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert create_resp.status_code == 201
    req_id = create_resp.data["id"]

    # 2. Schedule request
    sched_payload = {
        "scheduled_date": future_date_str(21),
        "start_time": "14:00:00",
        "end_time": "15:30:00",
        "venue": "Department Conference Room 204",
        "session_chair": "Prof. D. Sen",
        "remarks": "Approved by DRC Committee",
    }
    resp = admin_client.post(f"/api/v1/department/requests/{req_id}/schedule/", data=sched_payload, format="json")
    assert resp.status_code in (200, 201)
    assert resp.data["status"] == "SCHEDULED"

    # Verify GraduateSeminar is created
    sem = GraduateSeminar.objects.get(request_id=req_id)
    assert sem.venue == sched_payload["venue"]
    assert sem.session_chair == sched_payload["session_chair"]


def test_fr_dep_010_audit_history_log_maintained(admin_client, student_client):
    """FR-DEP-010 | CFR-OAP-021 / AFR-OAP-048 - Audit history log maintained on scheduling.

    Verify system records an audit history entry in SeminarSchedulingHistory on scheduling.
    """
    payload = {
        "topic": "Autonomous Drone Path Planning in Cluttered Environments",
        "abstract": "Real-time trajectory optimization using hybrid MPC and neural priors.",
        "programme": "M.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(18),
    }
    create_resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    req_id = create_resp.data["id"]

    sched_payload = {
        "scheduled_date": future_date_str(22),
        "start_time": "11:00:00",
        "end_time": "12:30:00",
        "venue": "Lecture Hall L-102",
        "session_chair": "Dr. V. Prasad",
        "remarks": "Scheduled on faculty confirmation",
    }
    admin_client.post(f"/api/v1/department/requests/{req_id}/schedule/", data=sched_payload, format="json")

    sem = GraduateSeminar.objects.get(request_id=req_id)
    logs = SeminarSchedulingHistory.objects.filter(seminar=sem)
    assert logs.exists()
    assert logs.filter(action="SCHEDULED").exists()


def test_fr_dep_011_view_scheduled_seminars_calendar(student_client, faculty_client, admin_client):
    """FR-DEP-011 | CFR-OAP-022 / AFR-OAP-049 - PG students and faculty view scheduled seminars.

    Verify PG students and faculty can view confirmed seminars on public schedule.
    """
    # Create and schedule one seminar
    payload = {
        "topic": "Quantum Error Correction via Surface Codes",
        "abstract": "Syndrome measurement decoding with graph neural networks.",
        "programme": "Ph.D.",
        "department": "CSE",
        "preferred_date": future_date_str(25),
    }
    c_resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    req_id = c_resp.data["id"]

    admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(26),
            "start_time": "15:00:00",
            "end_time": "16:30:00",
            "venue": "Auditorium Annex",
            "session_chair": "Prof. Roy",
            "remarks": "Public colloquium",
        },
        format="json",
    )

    # Faculty views calendar
    fac_resp = faculty_client.get("/api/v1/department/seminars/")
    assert fac_resp.status_code == 200
    results = fac_resp.data.get("results") or fac_resp.data
    assert any(item["title"] == payload["topic"] for item in results)


def test_fr_dep_012_department_announcements(admin_client, student_client):
    """FR-DEP-012 | CFR-OAP-022 / AFR-OAP-050 - Department announcements publishing and visibility.

    Verify Department Administrator can publish announcements and students can view them.
    """
    payload = {
        "title": "Annual Research Symposium Submissions Open",
        "content": "All M.Tech and Ph.D. scholars must submit abstracts before the deadline.",
        "target_audience": "ALL",
        "department": "CSE",
        "is_pinned": True,
    }
    pub_resp = admin_client.post("/api/v1/department/announcements/", data=payload, format="json")
    assert pub_resp.status_code == 201
    assert DepartmentAnnouncement.objects.filter(title=payload["title"]).exists()

    # Student views announcements
    view_resp = student_client.get("/api/v1/department/announcements/")
    assert view_resp.status_code == 200
    results = view_resp.data.get("results") or view_resp.data
    assert any(item["title"] == payload["title"] for item in results)

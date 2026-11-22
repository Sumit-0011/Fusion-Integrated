"""Use Case (UC) specification-driven tests for Department module.

Covers OA-UC-51, OA-UC-53, OA-UC-54, OA-UC-41, OA-UC-42 per UC_DESIGN.json.
"""
from __future__ import annotations

import pytest

from modules.department.models.allocation import TAAllocation, ThesisSupervisorAllocation
from modules.department.models.seminar import (
    GraduateSeminar,
    SeminarSchedulingHistory,
    SeminarSchedulingRequest,
)
from modules.department.tests.spec.conftest import future_date_str

pytestmark = pytest.mark.django_db


def test_uc_dep_001_request_seminar_main_flow(student_client):
    """UC-DEP-001 | OA-UC-51 Main Flow - Request Graduate Seminar.

    Verify main success flow where an eligible PG student submits a graduate seminar request.
    """
    payload = {
        "topic": "Distributed Consensus in Fusion ERP",
        "abstract": "Analysis of Raft and Paxos protocols for cross-campus transactional state.",
        "programme": "M.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(14),
    }
    resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert resp.status_code == 201
    assert resp.data["status"] == "AWAITING_SCHEDULING"
    assert resp.data["student_id"] == 1001


def test_uc_dep_002_non_pg_ineligibility_flow(make_dept_client):
    """UC-DEP-002 | OA-UC-51 Alternative A1 - Non-PG Student Ineligibility.

    Verify alternative exception flow where a non-PG student is refused.
    """
    ug_client = make_dept_client(user_id=1002, role="student", permissions=("department.seminar.request",))
    payload = {
        "topic": "Intro to Web Design Seminar",
        "abstract": "Undergraduate seminar submission.",
        "programme": "B.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(10),
    }
    resp = ug_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert resp.status_code in (400, 403)
    assert not SeminarSchedulingRequest.objects.filter(topic=payload["topic"]).exists()


def test_uc_dep_003_missing_required_fields_flow(student_client):
    """UC-DEP-003 | OA-UC-51 Alternative A2 - Missing Required Fields.

    Verify validation exception flow when mandatory fields are omitted.
    """
    payload = {
        "topic": "",
        "abstract": "",
        "programme": "M.Tech",
        "department": "CSE",
        "preferred_date": future_date_str(10),
    }
    resp = student_client.post("/api/v1/department/requests/", data=payload, format="json")
    assert resp.status_code == 400


def test_uc_dep_004_schedule_seminar_main_flow(admin_client, student_client):
    """UC-DEP-004 | OA-UC-53 Main Flow - Schedule Graduate Seminar.

    Verify main success flow where Department Administrator schedules an awaiting seminar.
    """
    create_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Neural Network Pruning Algorithms",
            "abstract": "Magnitude-based and structured pruning techniques in edge deployment.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(16),
        },
        format="json",
    )
    req_id = create_resp.data["id"]

    sched_payload = {
        "scheduled_date": future_date_str(17),
        "start_time": "10:00:00",
        "end_time": "11:30:00",
        "venue": "Seminar Hall A",
        "session_chair": "Prof. A. Kumar",
        "remarks": "Approved by DRC",
    }
    resp = admin_client.post(f"/api/v1/department/requests/{req_id}/schedule/", data=sched_payload, format="json")
    assert resp.status_code in (200, 201)
    assert resp.data["status"] == "SCHEDULED"

    req = SeminarSchedulingRequest.objects.get(pk=req_id)
    assert req.status == "SCHEDULED"
    assert GraduateSeminar.objects.filter(request=req).exists()
    assert SeminarSchedulingHistory.objects.filter(seminar__request=req, action="SCHEDULED").exists()


def test_uc_dep_005_reject_seminar_alternative_flow(admin_client, student_client):
    """UC-DEP-005 | OA-UC-53 Alternative A1 - Reject Seminar Request.

    Verify alternative flow where Department Administrator rejects a pending request.
    """
    create_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Preliminary Thesis Topic",
            "abstract": "Initial unreviewed abstract draft.",
            "programme": "M.Tech",
            "department": "CSE",
            "preferred_date": future_date_str(10),
        },
        format="json",
    )
    req_id = create_resp.data["id"]

    reject_payload = {
        "reason": "Topic requires DRC approval before formal department scheduling.",
    }
    resp = admin_client.post(f"/api/v1/department/requests/{req_id}/reject/", data=reject_payload, format="json")
    assert resp.status_code == 200
    assert resp.data["status"] == "REJECTED"
    assert not GraduateSeminar.objects.filter(request_id=req_id).exists()


def test_uc_dep_006_unauthorized_scheduling_flow(faculty_client, student_client):
    """UC-DEP-006 | OA-UC-53 Alternative A2 - Non-Admin Unauthorized Scheduling Attempt.

    Verify security exception flow where non-admin attempts to schedule a seminar.
    """
    create_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Quantum Key Distribution",
            "abstract": "BB84 protocol simulations under noise.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(20),
        },
        format="json",
    )
    req_id = create_resp.data["id"]

    sched_payload = {
        "scheduled_date": future_date_str(21),
        "start_time": "10:00:00",
        "end_time": "11:30:00",
        "venue": "Lab 1",
    }
    resp = faculty_client.post(f"/api/v1/department/requests/{req_id}/schedule/", data=sched_payload, format="json")
    assert resp.status_code == 403


def test_uc_dep_007_view_seminar_schedule_main_flow(admin_client, student_client, faculty_client):
    """UC-DEP-007 | OA-UC-54 Main Flow - View Seminar Schedule.

    Verify main success flow where campus users view public schedule of confirmed graduate seminars.
    """
    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "High-Throughput Genomics Pipelines",
            "abstract": "GPU accelerated sequence alignment.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(30),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(31),
            "start_time": "11:00:00",
            "end_time": "12:30:00",
            "venue": "Main Hall",
        },
        format="json",
    )

    resp = faculty_client.get("/api/v1/department/seminars/")
    assert resp.status_code == 200
    results = resp.data.get("results") or resp.data
    assert any(s["title"] == "High-Throughput Genomics Pipelines" for s in results)


def test_uc_dep_008_supervisor_allocation_main_flow(admin_client):
    """UC-DEP-008 | OA-UC-41 Main Flow - Record Thesis Supervisor Allocation.

    Verify main success flow where Department Administrator records research supervisor allocation.
    """
    payload = {
        "student_id": 1008,
        "student_name": "Siddharth Jain",
        "programme": "Ph.D.",
        "department": "CSE",
        "supervisor_id": 208,
        "supervisor_name": "Dr. A. Mitra",
        "thesis_topic": "Quantum Computing",
    }
    resp = admin_client.post("/api/v1/department/allocations/supervisors/", data=payload, format="json")
    assert resp.status_code == 201
    assert ThesisSupervisorAllocation.objects.filter(student_id=1008, supervisor_id=208).exists()


def test_uc_dep_009_ta_allocation_main_flow(admin_client):
    """UC-DEP-009 | OA-UC-42 Main Flow - Record TA Allocation.

    Verify main success flow where Department Administrator records teaching assistant assignment.
    """
    payload = {
        "student_id": 1009,
        "student_name": "Ananya Sen",
        "programme": "M.Tech",
        "department": "CSE",
        "course_code": "CS202",
        "course_name": "Data Structures",
        "faculty_id": 102,
        "faculty_name": "Dr. N. Bose",
        "hours_per_week": 10,
    }
    resp = admin_client.post("/api/v1/department/allocations/ta/", data=payload, format="json")
    assert resp.status_code == 201
    assert TAAllocation.objects.filter(student_id=1009, course_code="CS202").exists()

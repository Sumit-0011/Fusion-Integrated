"""Business Rules (BR) specification-driven tests for Department module.

Covers OA-BR-61, OA-BR-62, OA-BR-51, OA-BR-63 per BR_DESIGN.json.
"""
from __future__ import annotations

import pytest

from modules.department.domain.eligibility import check_seminar_eligibility, is_pg_student
from modules.department.models.allocation import TAAllocation
from modules.department.models.seminar import (
    GraduateSeminar,
    SeminarSchedulingHistory,
)
from modules.department.tests.spec.conftest import future_date_str

pytestmark = pytest.mark.django_db


def test_br_dep_001_mtech_eligible():
    """BR-DEP-001 | OA-BR-61 condition-true (M.Tech).

    Verify OA-BR-61 permits an M.Tech postgraduate student to request a graduate seminar.
    """
    assert is_pg_student("M.Tech") is True
    res = check_seminar_eligibility("M.Tech")
    assert res.allowed is True


def test_br_dep_002_phd_eligible():
    """BR-DEP-002 | OA-BR-61 condition-true (PhD).

    Verify OA-BR-61 permits a Ph.D. research scholar to request a graduate seminar.
    """
    assert is_pg_student("Ph.D.") is True
    assert is_pg_student("PhD") is True
    res = check_seminar_eligibility("Ph.D.")
    assert res.allowed is True


def test_br_dep_003_mdes_eligible():
    """BR-DEP-003 | OA-BR-61 condition-true (M.Des).

    Verify OA-BR-61 permits an M.Des postgraduate student to request a graduate seminar.
    """
    assert is_pg_student("M.Des") is True
    assert is_pg_student("MDes") is True
    res = check_seminar_eligibility("M.Des")
    assert res.allowed is True


def test_br_dep_004_btech_ineligible():
    """BR-DEP-004 | OA-BR-61 condition-false (B.Tech).

    Verify OA-BR-61 strictly prohibits undergraduate (B.Tech) students from requesting graduate seminars.
    """
    assert is_pg_student("B.Tech") is False
    assert is_pg_student("BTech") is False
    res = check_seminar_eligibility("B.Tech")
    assert res.allowed is False
    assert "Only postgraduate" in res.reason


def test_br_dep_005_empty_programme_fails_closed():
    """BR-DEP-005 | OA-BR-61 condition-false (Empty/Null programme).

    Verify OA-BR-61 fails closed when programme is unspecified or null.
    """
    assert is_pg_student(None) is False
    assert is_pg_student("") is False
    res = check_seminar_eligibility(None)
    assert res.allowed is False


def test_br_dep_006_audit_logging_on_scheduling(admin_client, student_client):
    """BR-DEP-006 | OA-BR-62 audit-logging.

    Verify OA-BR-62 mandates automatic creation of an audit log entry on seminar scheduling.
    """
    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Graph Theoretical Approaches to Cyber Defense",
            "abstract": "Dynamic spectral analysis of attack graphs.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(15),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(16),
            "start_time": "14:00:00",
            "end_time": "15:30:00",
            "venue": "Hall 1",
            "session_chair": "Dr. Chair",
            "remarks": "Scheduled by DRC committee",
        },
        format="json",
    )

    sem = GraduateSeminar.objects.get(request_id=req_id)
    history = SeminarSchedulingHistory.objects.filter(seminar=sem, action="SCHEDULED")
    assert history.exists()
    log_entry = history.first()
    assert log_entry.recorded_by_id == 2001
    assert "Hall 1" in log_entry.details


def test_br_dep_007_audit_log_linked_to_seminar(admin_client, student_client):
    """BR-DEP-007 | OA-BR-62 log-persistence.

    Verify OA-BR-62 history log is linked to GraduateSeminar through foreign key.
    """
    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Zero Trust Architecture Modeling",
            "abstract": "Continuous authentication protocols in distributed clusters.",
            "programme": "M.Tech",
            "department": "CSE",
            "preferred_date": future_date_str(18),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(19),
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Auditorium",
        },
        format="json",
    )

    sem = GraduateSeminar.objects.get(request_id=req_id)
    assert sem.history_logs.count() >= 1


def test_br_dep_008_ta_allocation_integrity(admin_client):
    """BR-DEP-008 | OA-BR-51 allocation-integrity (TA Target).

    Verify OA-BR-51 ensures TA allocation links to course, faculty, or both.
    """
    # 1. Valid course + faculty
    p1 = {
        "student_id": 1101,
        "student_name": "Student A",
        "programme": "M.Tech",
        "department": "CSE",
        "course_code": "CS201",
        "course_name": "Algorithms",
        "faculty_id": 201,
        "faculty_name": "Prof. Rao",
        "hours_per_week": 8,
    }
    r1 = admin_client.post("/api/v1/department/allocations/ta/", data=p1, format="json")
    assert r1.status_code == 201

    # 2. Query persisted allocation
    assert TAAllocation.objects.filter(student_id=1101, course_code="CS201").exists()


def test_br_dep_009_public_calendar_scheduled_only(admin_client, student_client, faculty_client):
    """BR-DEP-009 | OA-BR-63 visibility-scheduled-only.

    Verify OA-BR-63 ensures public calendar displays only seminars in SCHEDULED status.
    """
    # Request 1: Remains in AWAITING_SCHEDULING
    student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Pending Topic - Hidden from Calendar",
            "abstract": "This request is pending scheduling.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(20),
        },
        format="json",
    )

    # Request 2: Rejected
    r2 = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Rejected Topic - Hidden from Calendar",
            "abstract": "This request is rejected.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(22),
        },
        format="json",
    )
    admin_client.post(f"/api/v1/department/requests/{r2.data['id']}/reject/", data={"reason": "Rejected"}, format="json")

    # Request 3: Scheduled
    r3 = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Confirmed Seminar - Visible on Calendar",
            "abstract": "This request is confirmed scheduled.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(25),
        },
        format="json",
    )
    admin_client.post(
        f"/api/v1/department/requests/{r3.data['id']}/schedule/",
        data={
            "scheduled_date": future_date_str(26),
            "start_time": "15:00:00",
            "end_time": "16:30:00",
            "venue": "Hall 2",
        },
        format="json",
    )

    # Public list check
    cal_resp = faculty_client.get("/api/v1/department/seminars/")
    assert cal_resp.status_code == 200
    titles = [s["title"] for s in (cal_resp.data.get("results") or cal_resp.data)]
    assert "Confirmed Seminar - Visible on Calendar" in titles
    assert "Pending Topic - Hidden from Calendar" not in titles
    assert "Rejected Topic - Hidden from Calendar" not in titles

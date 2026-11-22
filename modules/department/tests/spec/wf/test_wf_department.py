"""Workflow (WF) specification-driven tests for Department module.

Covers BW-OAP-09 state machine and workflow transitions per WF_DESIGN.json.
"""
from __future__ import annotations

import pytest

from modules.department.domain.state_machine import (
    SeminarEvent,
    SeminarStatus,
    can_transition,
    get_next_status,
)
from modules.department.models.seminar import (
    GraduateSeminar,
    SeminarSchedulingRequest,
)
from modules.department.tests.spec.conftest import future_date_str

pytestmark = pytest.mark.django_db


def test_wf_dep_001_submit_transition_path(student_client):
    """WF-DEP-001 | BW-OAP-09 submit-transition.

    Verify workflow path from NO_SUBMITTED_REQUEST to AWAITING_SCHEDULING via SUBMIT event.
    """
    allowed, _msg, rule = can_transition(SeminarStatus.NO_SUBMITTED_REQUEST, SeminarEvent.SUBMIT)
    assert allowed is True
    assert rule.to_status == SeminarStatus.AWAITING_SCHEDULING

    resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Workflow Submission Path Test",
            "abstract": "Validating initial state machine transition to Awaiting Scheduling.",
            "programme": "M.Tech",
            "department": "CSE",
            "preferred_date": future_date_str(10),
        },
        format="json",
    )
    assert resp.status_code == 201
    assert resp.data["status"] == SeminarStatus.AWAITING_SCHEDULING.value


def test_wf_dep_002_schedule_transition_path(admin_client, student_client):
    """WF-DEP-002 | BW-OAP-09 schedule-transition.

    Verify workflow path from AWAITING_SCHEDULING to SCHEDULED via SCHEDULE event.
    """
    allowed, _msg, rule = can_transition(SeminarStatus.AWAITING_SCHEDULING, SeminarEvent.SCHEDULE)
    assert allowed is True
    assert rule.to_status == SeminarStatus.SCHEDULED

    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Workflow Schedule Path Test",
            "abstract": "Testing terminal success transition.",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(12),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    sched_resp = admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(13),
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Hall 3",
        },
        format="json",
    )
    assert sched_resp.status_code in (200, 201)
    assert sched_resp.data["status"] == SeminarStatus.SCHEDULED.value
    assert GraduateSeminar.objects.filter(request_id=req_id).exists()


def test_wf_dep_003_reject_transition_path(admin_client, student_client):
    """WF-DEP-003 | BW-OAP-09 reject-transition.

    Verify workflow path from AWAITING_SCHEDULING to REJECTED via REJECT event.
    """
    allowed, _msg, rule = can_transition(SeminarStatus.AWAITING_SCHEDULING, SeminarEvent.REJECT)
    assert allowed is True
    assert rule.to_status == SeminarStatus.REJECTED

    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Workflow Rejection Path Test",
            "abstract": "Testing terminal rejection transition.",
            "programme": "M.Tech",
            "department": "CSE",
            "preferred_date": future_date_str(14),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    rej_resp = admin_client.post(
        f"/api/v1/department/requests/{req_id}/reject/",
        data={"reason": "Topic outside departmental research cluster scope."},
        format="json",
    )
    assert rej_resp.status_code == 200
    assert rej_resp.data["status"] == SeminarStatus.REJECTED.value

    req = SeminarSchedulingRequest.objects.get(pk=req_id)
    assert req.status == SeminarStatus.REJECTED.value
    assert "Topic outside" in req.rejection_reason


def test_wf_dep_004_cancel_transition_path():
    """WF-DEP-004 | BW-OAP-09 cancel-transition.

    Verify workflow path from AWAITING_SCHEDULING to CANCELLED via CANCEL event.
    """
    allowed, _msg, rule = can_transition(SeminarStatus.AWAITING_SCHEDULING, SeminarEvent.CANCEL)
    assert allowed is True
    assert rule.to_status == SeminarStatus.CANCELLED
    assert get_next_status(SeminarStatus.AWAITING_SCHEDULING.value, SeminarEvent.CANCEL.value) == SeminarStatus.CANCELLED.value


def test_wf_dep_005_invalid_transition_from_scheduled(admin_client, student_client):
    """WF-DEP-005 | BW-OAP-09 invalid-transition-from-scheduled.

    Verify illegal transition attempt: Attempting to schedule an already SCHEDULED seminar is refused.
    """
    # 1. State machine refusal
    allowed, _msg, _rule = can_transition(SeminarStatus.SCHEDULED, SeminarEvent.SCHEDULE)
    assert allowed is False
    with pytest.raises(ValueError, match="Illegal transition"):
        get_next_status(SeminarStatus.SCHEDULED.value, SeminarEvent.SCHEDULE.value)

    # 2. API refusal
    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Duplicate Schedule Transition Test",
            "abstract": "Abstract",
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
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Hall A",
        },
        format="json",
    )

    # Re-schedule attempt
    dup_resp = admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(17),
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Hall B",
        },
        format="json",
    )
    assert dup_resp.status_code in (400, 409)


def test_wf_dep_006_invalid_transition_from_rejected(admin_client, student_client):
    """WF-DEP-006 | BW-OAP-09 invalid-transition-from-rejected.

    Verify illegal transition attempt: Attempting to schedule a REJECTED request is refused.
    """
    allowed, _msg, _rule = can_transition(SeminarStatus.REJECTED, SeminarEvent.SCHEDULE)
    assert allowed is False

    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Schedule Rejected Request Test",
            "abstract": "Abstract",
            "programme": "M.Tech",
            "department": "CSE",
            "preferred_date": future_date_str(18),
        },
        format="json",
    )
    req_id = c_resp.data["id"]
    admin_client.post(f"/api/v1/department/requests/{req_id}/reject/", data={"reason": "Rejected"}, format="json")

    # Attempt to schedule rejected request
    sched_resp = admin_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(19),
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Hall C",
        },
        format="json",
    )
    assert sched_resp.status_code in (400, 409)


def test_wf_dep_007_role_guard_student_scheduling_refused(student_client):
    """WF-DEP-007 | BW-OAP-09 role-guard-student-scheduling-refused.

    Verify workflow role guard: Student is unauthorized to execute the SCHEDULE or REJECT event.
    """
    c_resp = student_client.post(
        "/api/v1/department/requests/",
        data={
            "topic": "Student Self-Schedule Guard Test",
            "abstract": "Abstract",
            "programme": "Ph.D.",
            "department": "CSE",
            "preferred_date": future_date_str(20),
        },
        format="json",
    )
    req_id = c_resp.data["id"]

    # Student attempts schedule action
    sched_resp = student_client.post(
        f"/api/v1/department/requests/{req_id}/schedule/",
        data={
            "scheduled_date": future_date_str(21),
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "venue": "Hall D",
        },
        format="json",
    )
    assert sched_resp.status_code == 403

    # Student attempts reject action
    rej_resp = student_client.post(
        f"/api/v1/department/requests/{req_id}/reject/",
        data={"reason": "Self rejection"},
        format="json",
    )
    assert rej_resp.status_code == 403

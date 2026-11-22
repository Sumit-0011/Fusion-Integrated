"""Shared fixtures and helpers for Department specification-driven tests."""
from __future__ import annotations

import datetime

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from conftest import make_session
from modules.department.registry import ROLE_GRANTS

pytestmark = pytest.mark.django_db


def future_date_str(days: int = 14) -> str:
    """Return an ISO formatted date guaranteed to be in the future."""
    return (timezone.localdate() + datetime.timedelta(days=days)).isoformat()


def future_date(days: int = 14) -> datetime.date:
    """Return a date object guaranteed to be in the future."""
    return timezone.localdate() + datetime.timedelta(days=days)


@pytest.fixture
def make_dept_client(stub_iam):
    """Factory fixture returning an authenticated APIClient with requested session details."""
    def _create(
        user_id: int = 101,
        role: str = "student",
        kind: str = "student",
        permissions: tuple[str, ...] | None = None,
        modules: tuple[str, ...] = ("department",),
    ) -> APIClient:
        perms = permissions if permissions is not None else tuple(ROLE_GRANTS.get(role, ()))
        session = make_session(
            user_id=user_id,
            kind=kind,
            roles=(role,),
            active_role=role,
            permissions=perms,
            modules=modules,
        )
        stub_iam(session)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token tok-{user_id}-{role}")
        return client

    return _create


@pytest.fixture
def admin_client(make_dept_client):
    """Department Administrator authenticated client."""
    return make_dept_client(
        user_id=2001,
        role="department_admin",
        kind="staff",
    )


@pytest.fixture
def student_client(make_dept_client):
    """Postgraduate student authenticated client."""
    return make_dept_client(
        user_id=1001,
        role="student",
        kind="student",
    )


@pytest.fixture
def faculty_client(make_dept_client):
    """Faculty authenticated client."""
    return make_dept_client(
        user_id=3001,
        role="faculty",
        kind="faculty",
    )

import pytest

from app.services.access_service import (
    approve_access_request,
    create_access_request,
    get_access_request,
)


def test_access_request_lifecycle():
    request = create_access_request(
        user_id=1,
        resource="test-resource",
        requested_role="reader",
        risk="low",
    )

    assert request["status"] == "pending"
    assert get_access_request(request["id"])["status"] == "pending"

    approved = approve_access_request(request["id"], "security-reviewer")

    assert approved["status"] == "approved"
    assert approved["approved_by"] == "security-reviewer"

    with pytest.raises(ValueError, match="already approved"):
        approve_access_request(request["id"], "another-reviewer")


def test_access_request_rejects_invalid_risk():
    with pytest.raises(ValueError, match="Invalid risk"):
        create_access_request(
            user_id=1,
            resource="test-resource",
            requested_role="reader",
            risk="critical",
        )
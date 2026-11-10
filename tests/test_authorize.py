"""OAuth callback validation tests; no network or real credentials."""

import pytest

from google_workspace_mcp import authorize


@pytest.fixture(autouse=True)
def reset_handler():
    authorize._Handler.code = None
    authorize._Handler.error = None
    authorize._Handler.state = None


def test_received_code_accepts_matching_state():
    authorize._Handler.code = "authorization-code"
    authorize._Handler.state = "expected-state"
    assert authorize._received_code("expected-state") == "authorization-code"


@pytest.mark.parametrize("returned_state", [None, "wrong-state"])
def test_received_code_rejects_bad_state(returned_state):
    authorize._Handler.code = "authorization-code"
    authorize._Handler.state = returned_state
    with pytest.raises(RuntimeError, match="state mismatch"):
        authorize._received_code("expected-state")


def test_received_code_requires_a_code():
    authorize._Handler.state = "expected-state"
    with pytest.raises(RuntimeError, match="no authorization code"):
        authorize._received_code("expected-state")


def test_received_code_surfaces_oauth_errors():
    authorize._Handler.error = "access_denied"
    with pytest.raises(RuntimeError, match="access_denied"):
        authorize._received_code("expected-state")

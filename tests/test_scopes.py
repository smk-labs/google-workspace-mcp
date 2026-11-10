"""Adding a scope must not break accounts authorized before it existed.

Passing the full SCOPES list to a token refresh makes Google answer
`invalid_scope`, which takes out Gmail, Calendar, Drive and Tasks as well as
the new service. These tests pin the two halves of the fix: refresh uses the
granted scopes, and a tool needing a scope the token lacks says so clearly.

Pure-function tests: no Google auth, no network.
"""

import json

import pytest

from google_workspace_mcp import auth


@pytest.fixture
def token_dir(tmp_path, monkeypatch):
    def email_for(slug):
        if slug != "work":
            raise ValueError(f"Unknown account '{slug}'")
        return f"{slug}@example.com"

    monkeypatch.setattr(auth, "TOKENS_DIR", tmp_path)
    monkeypatch.setattr(auth, "email_for", email_for)
    auth._service.cache_clear()
    return tmp_path


def _write_token(dirpath, slug, scopes):
    (dirpath / f"{slug}.json").write_text(json.dumps({
        "token": "x", "refresh_token": "y", "scopes": scopes,
    }))


# The four scopes an account authorized before 0.7.0 actually holds.
PRE_CONTACTS = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/tasks",
]


def test_granted_scopes_reads_the_token(token_dir):
    _write_token(token_dir, "work", PRE_CONTACTS)
    assert auth.granted_scopes("work") == PRE_CONTACTS


def test_granted_scopes_empty_when_no_token(token_dir):
    assert auth.granted_scopes("missing") == []


def test_people_names_the_missing_scopes(token_dir):
    """An old token must get a legible error, not Google's bare invalid_scope."""
    _write_token(token_dir, "work", PRE_CONTACTS)
    with pytest.raises(RuntimeError) as e:
        auth.people("work")
    msg = str(e.value)
    assert "contacts.readonly" in msg
    assert "google-workspace-authorize work" in msg
    assert "People API" in msg


def test_people_passes_once_the_scopes_are_granted(token_dir, monkeypatch):
    _write_token(token_dir, "work", PRE_CONTACTS + [
        "https://www.googleapis.com/auth/contacts.readonly",
        "https://www.googleapis.com/auth/contacts.other.readonly",
    ])
    monkeypatch.setattr(auth, "_load_credentials", lambda slug: "creds")
    monkeypatch.setattr(auth, "build", lambda *a, **k: f"{a[0]}-service")
    assert auth.people("work") == "people-service"


def test_other_services_never_gated_on_contacts(token_dir, monkeypatch):
    """The whole point: an old token keeps Gmail, Calendar, Drive and Tasks."""
    _write_token(token_dir, "work", PRE_CONTACTS)
    monkeypatch.setattr(auth, "_load_credentials", lambda slug: "creds")
    monkeypatch.setattr(auth, "build", lambda *a, **k: f"{a[0]}-service")
    assert auth.gmail("work") == "gmail-service"
    assert auth.calendar("work") == "calendar-service"
    assert auth.drive("work") == "drive-service"
    assert auth.tasks("work") == "tasks-service"


def test_unlisted_account_rejected_even_with_a_token(token_dir, monkeypatch):
    """A token on disk must not bypass the instance's GWM_ACCOUNTS allowlist."""
    _write_token(token_dir, "other", PRE_CONTACTS)
    monkeypatch.setattr(
        auth,
        "_load_credentials",
        lambda slug: pytest.fail("unlisted account reached the token loader"),
    )
    with pytest.raises(ValueError, match="Unknown account 'other'"):
        auth.gmail("other")

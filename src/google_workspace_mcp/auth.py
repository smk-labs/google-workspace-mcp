"""OAuth + Google service builders.

Each account has a token file at TOKENS_DIR/<slug>.json. The
authorize.py script writes these; the server reads + refreshes them.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from functools import lru_cache

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .accounts import config_home, email_for

# Config lives OUTSIDE the code tree so it survives the server being
# installed anywhere (uv tool venv, a Claude Code plugin cache, etc.)
# and so secrets never sit next to (or get committed with) the source.
# Honors $GWM_HOME / $XDG_CONFIG_HOME; override either path explicitly
# with $GWM_CREDENTIALS / $GWM_TOKENS_DIR.
CONFIG_DIR = config_home()

CREDENTIALS_PATH = Path(
    os.environ.get("GWM_CREDENTIALS", CONFIG_DIR / "credentials.json")
)
TOKENS_DIR = Path(os.environ.get("GWM_TOKENS_DIR", CONFIG_DIR / "tokens"))

# Broad scopes — these are the user's own accounts, full control.
# Narrower scopes would force re-auth every time a tool is added.
SCOPES = [
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/tasks",
    # Contacts are READ-ONLY: this server reads people, never writes back.
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/contacts.other.readonly",
]

# Scopes a service needs beyond the original four. A token granted before the
# scope existed cannot call these, so we say so plainly instead of letting
# Google answer with a bare 403.
_SCOPES_FOR_API = {
    "people": (
        "https://www.googleapis.com/auth/contacts.readonly",
        "https://www.googleapis.com/auth/contacts.other.readonly",
    ),
}


def _token_path(slug: str) -> Path:
    return TOKENS_DIR / f"{slug}.json"


def granted_scopes(slug: str) -> list[str]:
    """The scopes this account's stored token was actually granted."""
    try:
        return json.loads(_token_path(slug).read_text()).get("scopes") or []
    except (OSError, ValueError):
        return []


def _load_credentials(slug: str) -> Credentials:
    path = _token_path(slug)
    if not path.exists():
        raise RuntimeError(
            f"No token for account '{slug}' ({email_for(slug)}). "
            f"Run: google-workspace-authorize {slug}"
        )
    # Refresh against the scopes the token was ACTUALLY granted, never SCOPES.
    # Google rejects a refresh that asks for more than the original grant with
    # `invalid_scope`, so passing SCOPES here bricks every existing token the
    # moment a scope is added — every account loses Gmail, Calendar, Drive and
    # Tasks too, not just the new service. Adding Tasks (0.3.0) and Contacts
    # (0.7.0) both did this. The account keeps working on what it has; only the
    # new service asks for re-auth, in _service() below.
    creds = Credentials.from_authorized_user_file(
        str(path), granted_scopes(slug) or SCOPES
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json())
    if not creds.valid:
        raise RuntimeError(
            f"Token for '{slug}' is invalid and cannot refresh. "
            f"Re-run: google-workspace-authorize {slug}"
        )
    return creds


# Cache built services per account+api so we don't rebuild on every call.
# The Credentials object refreshes itself in place, so this is safe.
@lru_cache(maxsize=32)
def _service(slug: str, api: str, version: str):
    # Enforce this instance's account allowlist before reading any token.
    email_for(slug)
    needed = _SCOPES_FOR_API.get(api, ())
    if needed:
        missing = [s for s in needed if s not in granted_scopes(slug)]
        if missing:
            raise RuntimeError(
                f"Account '{slug}' ({email_for(slug)}) was authorized before "
                f"the {api} scopes existed, so it cannot use these tools yet. "
                f"Missing: {', '.join(missing)}. Enable the People API in the "
                f"Google Cloud project, then re-run: "
                f"google-workspace-authorize {slug}"
            )
    creds = _load_credentials(slug)
    return build(api, version, credentials=creds, cache_discovery=False)


def gmail(slug: str):
    return _service(slug, "gmail", "v1")


def calendar(slug: str):
    return _service(slug, "calendar", "v3")


def drive(slug: str):
    return _service(slug, "drive", "v3")


def tasks(slug: str):
    return _service(slug, "tasks", "v1")


def people(slug: str):
    return _service(slug, "people", "v1")

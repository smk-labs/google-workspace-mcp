"""Unit tests for the Contacts (People API) summary helper.

Pure-function tests — no Google auth or network required.
"""

from google_workspace_mcp.server import _person_summary


def test_person_summary_basic():
    p = {
        "resourceName": "people/c1",
        "names": [{"displayName": "Alex Example"}],
        "nicknames": [{"value": "Alex"}],
        "emailAddresses": [{"value": "alex@example.com", "type": "work"}],
        "phoneNumbers": [
            {"value": "+1 555 0100", "canonicalForm": "+15550100", "type": "mobile"}
        ],
        "organizations": [{"name": "Acme", "title": "Engineer"}],
        "birthdays": [{"text": "1990-01-01"}],
    }
    s = _person_summary(p)
    assert s["resourceName"] == "people/c1"
    assert s["name"] == "Alex Example"
    assert s["nicknames"] == ["Alex"]
    assert s["emails"] == [{"value": "alex@example.com", "type": "work"}]
    # The E.164 canonical form is the strong dedup key.
    assert s["phones"][0]["canonical"] == "+15550100"
    assert s["orgs"] == [{"name": "Acme", "title": "Engineer"}]
    assert s["birthdays"] == ["1990-01-01"]


def test_person_summary_empty():
    s = _person_summary({})
    assert s["name"] is None
    assert s["names"] == []
    assert s["emails"] == []
    assert s["phones"] == []
    assert s["orgs"] is None
    assert s["birthdays"] is None


def test_person_summary_skips_valueless_entries():
    p = {
        "names": [{"displayName": "No Contacts"}],
        "emailAddresses": [{"type": "home"}],  # no "value"
        "phoneNumbers": [{"type": "mobile"}],  # no "value"
    }
    s = _person_summary(p)
    assert s["emails"] == []
    assert s["phones"] == []


def test_contacts_tools_registered():
    """All Contacts (People API) tools are defined on the server module."""
    import google_workspace_mcp.server as server

    for name in (
        "contacts_list",
        "contacts_search",
        "contact_get",
        "contacts_batch_get",
        "other_contacts_list",
        "contact_groups_list",
        "contact_group_get",
    ):
        assert hasattr(server, name), f"missing tool: {name}"

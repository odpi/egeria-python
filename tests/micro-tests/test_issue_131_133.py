"""
ISSUE-131: 13 *_by_name wrappers passed the type filter to _async_get_name_request as
`metadata_element_type` (the _async_find_request spelling); the helper reads `metadata_element_type_name`,
so the key fell into **kwargs, FilterRequestBody dropped it, and the search ran unfiltered by type.
ISSUE-133: Egeria returns a solution component's children as nestedSolutionComponents; there is no
subComponents field in any REST response.
"""
import json

import pytest

from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.location_arena import LocationArena
from pyegeria.omvs.runtime_manager import RuntimeManager
from pyegeria.omvs.solution_architect import SolutionArchitect
from pyegeria.omvs.subject_area import SubjectArea
from pyegeria.omvs.time_keeper import TimeKeeper


class _Response:
    def json(self):
        return {"relatedHTTPCode": 200, "elements": []}


def _capture(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


# --- ISSUE-131 ------------------------------------------------------------------------------

BY_NAME_WRAPPERS = [
    (ActorManager, "_async_get_actor_profiles_by_name"),
    (ActorManager, "_async_get_actor_roles_by_name"),
    (ActorManager, "_async_get_user_identities_by_name"),
    (ActorManager, "_async_get_contribution_records_by_name"),
    (ActorManager, "_async_get_contact_details_by_name"),
    (ActorManager, "_async_get_perspectives_by_name"),
    (ActorManager, "_async_get_skills_by_name"),
    (CollectionManager, "_async_get_collections_by_name"),
    (DigitalBusiness, "_async_get_business_capabilities_by_name"),
    (LocationArena, "_async_get_locations_by_name"),
    (RuntimeManager, "_async_get_metadata_repository_cohorts_by_name"),
    (SubjectArea, "_async_get_subject_areas_by_name"),
    (TimeKeeper, "_async_get_context_events_by_name"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method", BY_NAME_WRAPPERS)
async def test_by_name_wrappers_send_the_type_filter(cls, method, monkeypatch):
    client, calls = _capture(cls, monkeypatch)

    await getattr(client, method)("x", metadata_element_type_name="ProbeType")

    assert calls[0]["body"]["metadataElementTypeName"] == "ProbeType"


@pytest.mark.asyncio
async def test_name_request_accepts_the_find_request_spelling(monkeypatch):
    client, calls = _capture(CollectionManager, monkeypatch)

    await client._async_get_name_request("https://localhost:1/x/by-name", _type="T", _gen_output=None,
                                         filter_string="x", metadata_element_type="ProbeType")

    assert calls[0]["body"]["metadataElementTypeName"] == "ProbeType"


@pytest.mark.asyncio
async def test_name_request_prefers_the_canonical_spelling(monkeypatch):
    client, calls = _capture(CollectionManager, monkeypatch)

    await client._async_get_name_request("https://localhost:1/x/by-name", _type="T", _gen_output=None,
                                         filter_string="x", metadata_element_type_name="Canonical",
                                         metadata_element_type="Legacy")

    assert calls[0]["body"]["metadataElementTypeName"] == "Canonical"


# --- ISSUE-133 ------------------------------------------------------------------------------

def _component_with_child():
    return {
        "elementHeader": {"guid": "parent-guid"},
        "properties": {"displayName": "Parent", "qualifiedName": "SolutionComponent::Parent"},
        "nestedSolutionComponents": [{
            "relatedElement": {
                "elementHeader": {"guid": "child-guid"},
                "properties": {"displayName": "Child", "qualifiedName": "SolutionComponent::Child"},
            }
        }],
    }


def test_governance_officer_reads_nested_solution_components(monkeypatch):
    monkeypatch.setattr(GovernanceOfficer, "check_connection", lambda self: "test")
    client = GovernanceOfficer("view-server", "https://localhost:1", "user", "pwd")

    props = client._extract_solution_components_properties(_component_with_child())

    assert props["sub_components"].strip() == "Child"


def test_solution_architect_reads_nested_solution_components(monkeypatch):
    monkeypatch.setattr(SolutionArchitect, "check_connection", lambda self: "test")
    client = SolutionArchitect("view-server", "https://localhost:1", "user", "pwd")

    rel = client._get_component_rel_elements_dict(_component_with_child())

    assert rel["sub_component_guids"] == ["child-guid"]

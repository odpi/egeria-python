"""
Role-to-profile appointment links (PersonRoleAppointment, TeamRoleAppointment,
ITProfileRoleAppointment) must send Egeria's real properties class name when the
caller passes no body -- the SDK previously defaulted to PersonAppointmentProperties /
TeamAppointmentProperties / ITProfileAppointmentProperties, which don't exist
(see open-metadata-framework .../properties/actors/*RoleAppointmentProperties.java).
No live server: the HTTP call is captured and the URL and body asserted.
"""
import json

import pytest

from md_processing.v2.actor_manager import ActorManagerLinkProcessor
from pyegeria.omvs.actor_manager import ActorManager


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "rel-guid", "relatedHTTPCode": 200}


def _actor_manager(calls, monkeypatch):
    monkeypatch.setattr(ActorManager, "check_connection", lambda self: "test")
    client = ActorManager("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("method, segment, expected_class", [
    ("_async_link_person_role_to_profile", "person-role-appointments", "PersonRoleAppointmentProperties"),
    ("_async_link_team_role_to_profile", "team-role-appointments", "TeamRoleAppointmentProperties"),
    ("_async_link_it_profile_role_to_it_profile", "it-profile-role-appointments",
     "ITProfileRoleAppointmentProperties"),
])
async def test_link_role_to_profile_without_body_sends_real_class_name(monkeypatch, method, segment,
                                                                       expected_class):
    calls: list = []
    client = _actor_manager(calls, monkeypatch)

    await getattr(client, method)("role-guid", "profile-guid")

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"/actor-roles/role-guid/{segment}/profile-guid/attach")
    assert calls[0]["body"]["properties"]["class"] == expected_class


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url_tail", [
    ("_async_detach_person_role_from_profile", "/actor-roles/a-guid/person-role-appointments/b-guid/detach"),
    ("_async_detach_team_role_from_profile", "/actor-roles/a-guid/team-role-appointments/b-guid/detach"),
    ("_async_detach_it_profile_role_from_it_profile",
     "/actor-roles/a-guid/it-profile-role-appointments/b-guid/detach"),
    ("_async_detach_identity_from_profile", "/user-identities/a-guid/profile-identity/b-guid/detach"),
])
async def test_detach_sends_a_relationship_body_not_an_element_body(monkeypatch, method, url_tail):
    # ActorManagerResource.java declares DeleteRelationshipRequestBody for these
    # /detach endpoints; a DeleteElementRequestBody got a live 400 (IT profile role).
    calls: list = []
    client = _actor_manager(calls, monkeypatch)

    await getattr(client, method)("a-guid", "b-guid",
                                  {"class": "DeleteRelationshipRequestBody", "forLineage": True})

    assert calls[0]["url"].endswith(url_tail)
    assert calls[0]["body"]["class"] == "DeleteRelationshipRequestBody"


@pytest.mark.asyncio
@pytest.mark.parametrize("method, url_tail", [
    ("_async_delete_actor_role", "/actor-roles/a-guid/delete"),
    ("_async_delete_contribution_record", "/contribution-records/a-guid/delete"),
])
async def test_element_delete_sends_an_element_body(monkeypatch, method, url_tail):
    # ActorManagerResource.java declares DeleteElementRequestBody for these /delete
    # endpoints (the .http file says DeleteRelationshipRequestBody for actor-roles -- wrong).
    calls: list = []
    client = _actor_manager(calls, monkeypatch)

    await getattr(client, method)("a-guid", {"class": "DeleteElementRequestBody", "forLineage": True})

    assert calls[0]["url"].endswith(url_tail)
    assert calls[0]["body"]["class"] == "DeleteElementRequestBody"


@pytest.mark.asyncio
async def test_remove_is_context_definition_sends_a_classification_body(monkeypatch):
    # GlossaryManagerResource.java: .../is-context-definition/delete takes DeleteClassificationRequestBody.
    from pyegeria.omvs.glossary_manager import GlossaryManager
    monkeypatch.setattr(GlossaryManager, "check_connection", lambda self: "test")
    client = GlossaryManager("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    await client._async_remove_is_context_definition(
        "term-guid", {"class": "DeleteClassificationRequestBody", "forLineage": True})

    assert calls[0]["url"].endswith("/glossaries/terms/term-guid/is-context-definition/delete")
    assert calls[0]["body"]["class"] == "DeleteClassificationRequestBody"


def test_dr_egeria_it_profile_role_appointment_targets_an_existing_sdk_method():
    # Dr.Egeria's Link IT Profile Role Appointment used to reference
    # _async_link_it_profile_role_to_profile, which ActorManager doesn't define.
    import inspect
    source = inspect.getsource(ActorManagerLinkProcessor)
    for name in ("_async_link_person_role_to_profile", "_async_link_team_role_to_profile",
                 "_async_link_it_profile_role_to_it_profile",
                 "_async_detach_it_profile_role_from_it_profile"):
        assert name in source
        assert hasattr(ActorManager, name)
    assert "_async_link_it_profile_role_to_profile" not in source

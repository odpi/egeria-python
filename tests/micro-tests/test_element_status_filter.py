# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""`limitResultsByStatus` takes Egeria's ElementStatus only; anything else is refused in words, before sending.

Seen 2026-11-13 17:32:01Z on laz: a draft-spec preview passed limit_result_by_status ["DRAFT", ...] through to
GovernanceOfficer.find_governance_definitions, and Egeria answered 400 ("Cannot deserialize value of type
ElementStatus from String "DRAFT""). DRAFT is a contentStatus value; the header-status filter never accepted it.
"""
import json
import os
import re
import warnings
from pathlib import Path

import pytest

from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.models.element_status import (ELEMENT_STATUSES, ELEMENT_STATUS_SOURCE, STATUS_PROPERTIES,
                                            InvalidElementStatus, UnheldElementStatusWarning,
                                            check_element_statuses)
from pyegeria.models.models import FilterRequestBody, SearchStringRequestBody
from pyegeria.view.format_set_executor import _normalize_report_params

pytestmark = pytest.mark.unit
REPO = Path(__file__).resolve().parents[2]


def test_the_constant_is_egerias_element_status_enum_and_names_its_source():
    assert ELEMENT_STATUSES == {"UNKNOWN", "ACTIVE", "INVALID", "DELETED", "OTHER"}
    assert "ElementStatus.java" in ELEMENT_STATUS_SOURCE and "3c8970b656" in ELEMENT_STATUS_SOURCE


def test_element_statuses_pass_upper_cased_and_no_filter_stays_no_filter():
    body = SearchStringRequestBody.model_validate(
        {"class": "SearchStringRequestBody", "limitResultsByStatus": ["active", " Deleted "]})
    assert body.limit_results_by_status == ["ACTIVE", "DELETED"]
    for value in (None, []):
        assert check_element_statuses(value) == value
    assert FilterRequestBody.model_validate({"class": "FilterRequestBody"}).limit_results_by_status is None


def test_draft_is_refused_as_a_content_status_in_the_request_body():
    with pytest.raises(ValueError) as caught:
        SearchStringRequestBody.model_validate({"class": "SearchStringRequestBody", "limitResultsByStatus": ["DRAFT"]})
    assert ("DRAFT is a contentStatus value (AuthoredReferenceable, DataAsset), or termRelationshipStatus on term "
            "relationships, not an element status; filter on contentStatus instead") in str(caught.value)


def test_each_wrong_value_is_named_with_what_it_is():
    with pytest.raises(InvalidElementStatus) as caught:
        check_element_statuses(["ACTIVE", "APPROVED", "UNDER_DEVELOPMENT", "APPROVED_CONCEPT"])
    words = str(caught.value)
    assert ("APPROVED is a contentStatus value (AuthoredReferenceable, DataAsset), or activityStatus (Process; "
            "ActionTarget and NotificationSubscriber relationships), not an element status; filter on contentStatus "
            "or activityStatus instead") in words
    assert ("UNDER_DEVELOPMENT is a deploymentStatus value (DigitalProduct, Infrastructure, SoftwareCapability, "
            "SolutionComponent, the Promise classification), not an element status; filter on deploymentStatus "
            "instead") in words
    assert "APPROVED_CONCEPT is not an element status, nor a value of any status property" in words   # 5.x leftover
    assert "ACTIVE is" not in words                                        # a valid value isn't complained about
    assert "Element statuses are ACTIVE, DELETED, INVALID, OTHER, UNKNOWN" in words


@pytest.mark.parametrize("key", ["limit_result_by_status", "limit_results_by_status"])
def test_a_report_run_refuses_before_any_client_is_built(key):
    with pytest.raises(InvalidElementStatus, match="DRAFT is a contentStatus value"):
        _normalize_report_params({key: "['DRAFT', 'ACTIVE']"})               # the Dr.Egeria / form string shape
    assert _normalize_report_params({key: "ACTIVE"})["limit_results_by_status"] == ["ACTIVE"]


class _Response:
    def json(self):
        return {"elements": []}


@pytest.mark.asyncio
async def test_the_sdk_find_the_preview_reached_refuses_without_sending(monkeypatch):
    from pyegeria.omvs.governance_officer import GovernanceOfficer
    monkeypatch.setattr(GovernanceOfficer, "check_connection", lambda self: "test")
    client = GovernanceOfficer("view-server", "https://localhost:1", "user", "pwd")
    sent = []

    async def fake_make_request(method, url, body=None, *a, **k):
        sent.append(body)
        return _Response()
    client._async_make_request = fake_make_request

    with pytest.raises(PyegeriaInvalidParameterException) as caught:
        await client._async_find_governance_definitions(
            "*", limit_results_by_status=["DRAFT", "APPROVED", "UNDER_DEVELOPMENT"], output_format="JSON")
    assert sent == []                                                      # nothing reached Egeria
    assert "DRAFT is a contentStatus value" in json.dumps(caught.value.__dict__, default=str) + str(caught.value)

    sent.clear()                                                           # a real element status still goes out
    await client._async_find_governance_definitions("*", limit_results_by_status=["ACTIVE"], output_format="JSON")
    assert sent and json.loads(sent[0])["limitResultsByStatus"] == ["ACTIVE"]


def test_the_report_commands_offer_only_element_statuses():
    spec = json.loads((REPO / "md_processing/data/compact_commands/commands_report_compact.json").read_text())
    assert set(spec["attribute_definitions"]["Limit Result by Status"]["valid_values"]) == ELEMENT_STATUSES
    seed = (REPO / "pyegeria/view/seed/Views & Reports.json").read_text()
    assert '"limit_result_by_status", "label": "Limit Result by Status", "valid_values": ["UNKNOWN", "ACTIVE", ' \
           '"INVALID", "DELETED", "OTHER"]' in seed and "APPROVED_CONCEPT" not in seed


def test_relationship_only_values_name_where_they_live_and_suggest_no_element_filter():
    with pytest.raises(InvalidElementStatus) as caught:
        check_element_statuses(["VALIDATED", "DEPRECATED"])
    words = str(caught.value)
    # VALIDATED is only on relationships: there is no element property to filter on instead
    assert ("VALIDATED is a membershipStatus value on collection memberships, or termAssignmentStatus on semantic "
            "assignments, not an element status;") in words and "VALIDATED is a membershipStatus value on collection " \
           "memberships, or termAssignmentStatus on semantic assignments, not an element status; filter" not in words
    assert ("DEPRECATED is a contentStatus value (AuthoredReferenceable, DataAsset), or membershipStatus on collection "
            "memberships, or termRelationshipStatus on term relationships, or termAssignmentStatus on semantic "
            "assignments, not an element status; filter on contentStatus instead") in words


def test_statuses_no_element_can_hold_pass_with_a_warning():
    with pytest.warns(UnheldElementStatusWarning, match="OTHER is an element status Egeria accepts, but no type "
                                                        "lets an element hold it"):
        assert check_element_statuses(["ACTIVE", "OTHER"]) == ["ACTIVE", "OTHER"]
    with pytest.warns(UnheldElementStatusWarning, match="UNKNOWN, INVALID are element statuses"):
        check_element_statuses(["UNKNOWN", "INVALID"])
    with warnings.catch_warnings():
        warnings.simplefilter("error")                                     # ACTIVE / DELETED warn about nothing
        assert check_element_statuses(["ACTIVE", "DELETED"]) == ["ACTIVE", "DELETED"]


# Opt-in: set PYEGERIA_EGERIA_SRC to an odpi/egeria checkout (its root) on the commit you want to compare with.
# Never a default path: a stale local checkout would otherwise fail an unrelated release run.
_SRC = os.environ.get("PYEGERIA_EGERIA_SRC")
_ENUMS = Path(_SRC).expanduser() / "open-metadata-implementation/frameworks/open-metadata-framework/src/main/java" \
                                   "/org/odpi/openmetadata/frameworks/openmetadata" if _SRC else None


@pytest.mark.skipif(not _SRC, reason="PYEGERIA_EGERIA_SRC not set (an odpi/egeria checkout to compare the enums with)")
def test_the_offline_tables_equal_egerias_java_enums():
    assert _ENUMS.is_dir(), f"PYEGERIA_EGERIA_SRC={_SRC!r} has no {_ENUMS}"
    def constants(path):
        return set(re.findall(r"^\s+([A-Z_]+)\s*\(", path.read_text(), re.M))
    assert constants(_ENUMS / "search/ElementStatus.java") == ELEMENT_STATUSES
    for prop in STATUS_PROPERTIES:
        assert constants(_ENUMS / "enums" / f"{prop.enum}.java") == prop.values, prop.name

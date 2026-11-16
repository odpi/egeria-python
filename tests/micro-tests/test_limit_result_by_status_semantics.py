# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Limit Result by Status has Egeria's current element-status semantics; lifecycle filters are separate.

An element's (header) status is Egeria's ElementStatus (pyegeria.models.element_status): UNKNOWN, ACTIVE,
INVALID, DELETED, OTHER. Empty means ACTIVE only, [DELETED] means only soft-deleted elements, [ACTIVE, DELETED]
means both; a lifecycle value such as DRAFT is refused by Egeria (400).
Lifecycle moved to typed properties (contentStatus / deploymentStatus / activityStatus), so Create Report
and View Report carry three more filters: Limit Result by Content Status / Deployment Status / Activity
Status. All four are lists, validated locally -- Egeria's valid-metadata-value check is never called for
them (it answered 400 every time, and Create Report warned "['ACTIVE'] is not a valid metadata value").
"""
import json
import warnings
from typing import Any, Optional, cast

import pytest

from md_processing.md_processing_utils.common_md_utils import set_filter_request_body, set_find_body
from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
from md_processing.v2.extraction import UniversalExtractor
from md_processing.v2.parsing import AttributeFirstParser
from md_processing.v2.report import _report_additional_properties, report_parameters_document
from pyegeria.core.request_filters import UnknownFilterWarning
from pyegeria.view import format_set_executor as fse

pytestmark = pytest.mark.unit

STATUS = "Limit Result by Status"
CONTENT = "Limit Result by Content Status"
DEPLOYMENT = "Limit Result by Deployment Status"
ACTIVITY = "Limit Result by Activity Status"


class _RecordingValidMetadata:
    """Records every valid-metadata-value question; other Valid Value attributes may still ask."""

    def __init__(self):
        self.asked = []
        self.valid_metadata = self

    async def _async_validate_metadata_value(self, prop_name, type_name, value):
        self.asked.append((prop_name, value))
        return None

    async def _async_validate_metadata_map_value(self, prop_name, type_name, map_name, value):
        self.asked.append((prop_name, value))
        return None

    async def _async_get_valid_metadata_values(self, prop_name, type_name=None):
        self.asked.append((prop_name, None))
        return []


async def _parse(verb_object: str, attrs: dict, client: Optional[Any] = None, directive: str = "validate"):
    if not get_command_spec("Create Report"):
        load_commands()
    body = "\n\n".join(f"### {k}\n{v}" for k, v in attrs.items())
    cmd = UniversalExtractor(f"## {verb_object}\n\n{body}\n").extract_commands()[0]
    return await AttributeFirstParser(cmd, client=client, directive=directive).parse()


def _create_report(**extra):
    return {"Display Name": "Status Semantics Report", "Report Spec": "Collections", **extra}


# ── the spec ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("command", ["Create Report", "View Report"])
def test_both_report_commands_carry_all_four_status_filters(command):
    load_commands()
    spec = get_command_spec(command)
    names = {a["name"] if "name" in a else next(iter(a)) for a in spec["Attributes"]}
    assert {STATUS, CONTENT, DEPLOYMENT, ACTIVITY} <= names


def test_limit_result_by_status_spec_is_a_local_list_of_the_element_statuses():
    from pyegeria.models.element_status import ELEMENT_STATUSES
    load_commands()
    attr = get_command_spec("Create Report")["attribute_definitions"][STATUS]
    assert attr["style"] == "Simple List"
    assert set(attr["valid_values"]) == set(ELEMENT_STATUSES)
    assert attr["default_value"] == "ACTIVE"
    assert attr["variable_name"] == "limit_result_by_status"
    for name in (CONTENT, DEPLOYMENT, ACTIVITY):
        lifecycle = get_command_spec("Create Report")["attribute_definitions"][name]
        assert lifecycle["style"] == "Simple List" and lifecycle["default_value"] == ""


# ── the parser ──────────────────────────────────────────────────────────────

async def test_omitted_status_gets_the_active_default():
    out = await _parse("Create Report", _create_report())
    attr = out["attributes"][STATUS]
    assert attr["value"] == ["ACTIVE"] and attr["is_default"]
    assert not [w for w in out["warnings"] if "Status" in w]


@pytest.mark.parametrize("written, expected", [
    ("ACTIVE, DELETED", ["ACTIVE", "DELETED"]),
    ("active; deleted", ["ACTIVE", "DELETED"]),
    ("- ACTIVE\n- DELETED", ["ACTIVE", "DELETED"]),
    ("DELETED", ["DELETED"]),
    ("['ACTIVE']", ["ACTIVE"]),          # the legacy default, as stored Reports and old documents hold it
    ('["ACTIVE"]', ["ACTIVE"]),
    ("['ACTIVE', 'DELETED']", ["ACTIVE", "DELETED"]),
])
async def test_status_values_parse_to_a_list(written, expected):
    out = await _parse("Create Report", _create_report(**{STATUS: written}))
    assert out["attributes"][STATUS]["value"] == expected
    assert not [w for w in out["warnings"] if STATUS in w], out["warnings"]
    assert not out["errors"]


async def test_an_old_lifecycle_value_is_a_warning_with_a_pointer_not_an_error():
    out = await _parse("Create Report", _create_report(**{STATUS: "DRAFT"}), directive="process")
    assert not out["errors"]
    msg = " ".join(out["warnings"])
    assert "DRAFT is no longer an element status" in msg
    assert "Content Status" in msg and "Deployment Status" in msg and "Activity Status" in msg
    assert "DRAFT" not in (out["attributes"][STATUS]["value"] or [])


async def test_a_dropped_value_marks_the_attribute_as_a_warning_not_valid():
    """The attribute table must not say "✅ Valid" next to a value the Warnings say was ignored."""
    from md_processing.v2.processors import AsyncBaseCommandProcessor

    out = await _parse("View Report", {"Report Spec": "Collections", STATUS: "DRAFT"})
    assert out["attributes"][STATUS]["status"] == "WARNING"
    assert out["attributes"]["Report Spec"]["status"] == "INFO"
    clean = await _parse("View Report", {"Report Spec": "Collections", STATUS: "DELETED"})
    assert clean["attributes"][STATUS]["status"] == "INFO"

    import inspect
    src = inspect.getsource(AsyncBaseCommandProcessor)
    assert '"⚠️ Warning"' in src and 'details.get("status") == "WARNING"' in src


async def test_a_mixed_value_keeps_the_valid_entries():
    out = await _parse("View Report", {"Report Spec": "Collections", STATUS: "ACTIVE, DEPRECATED"})
    assert out["attributes"][STATUS]["value"] == ["ACTIVE"]
    assert any("DEPRECATED is no longer an element status" in w for w in out["warnings"])


async def test_egeria_is_never_asked_about_the_status_attributes():
    client = _RecordingValidMetadata()
    out = await _parse("Create Report", _create_report(**{
        STATUS: "['ACTIVE']", CONTENT: "DRAFT, APPROVED", DEPLOYMENT: "ACTIVE", ACTIVITY: "IN_PROGRESS"}),
        client=client)
    assert not [p for p, _ in client.asked if "status" in str(p).lower()], client.asked
    assert out["attributes"][STATUS]["value"] == ["ACTIVE"]
    assert not [w for w in out["warnings"] if "valid metadata value" in w]


# ── the lifecycle filters ───────────────────────────────────────────────────

@pytest.mark.parametrize("name, written, expected", [
    (CONTENT, "draft, Approved", ["DRAFT", "APPROVED"]),
    (CONTENT, "OBSOLETE", ["OBSOLETE"]),
    (DEPLOYMENT, "- UNDER_DEVELOPMENT\n- REJECTED", ["UNDER_DEVELOPMENT", "REJECTED"]),
    (ACTIVITY, "in progress, COMPLETED", ["IN_PROGRESS", "COMPLETED"]),
    (ACTIVITY, "['WAITING']", ["WAITING"]),
])
async def test_lifecycle_filters_validate_locally(name, written, expected):
    out = await _parse("Create Report", _create_report(**{name: written}))
    assert out["attributes"][name]["value"] == expected
    assert not [w for w in out["warnings"] if name in w], out["warnings"]


@pytest.mark.parametrize("name, bad", [(CONTENT, "IN_PROGRESS"), (DEPLOYMENT, "DRAFT"), (ACTIVITY, "OBSOLETE")])
async def test_a_value_from_the_wrong_lifecycle_enum_is_a_warning(name, bad):
    out = await _parse("Create Report", _create_report(**{name: bad}), directive="process")
    assert not out["errors"]
    assert any(name in w and bad in w for w in out["warnings"]), out["warnings"]
    assert bad not in (out["attributes"].get(name, {}).get("value") or [])


async def test_lifecycle_filters_have_no_default():
    out = await _parse("Create Report", _create_report())
    for name in (CONTENT, DEPLOYMENT, ACTIVITY):
        assert not (out["attributes"].get(name) or {}).get("value")


# ── body builders ───────────────────────────────────────────────────────────

def test_find_body_reads_the_real_label_and_lists_a_string():
    assert set_find_body("Report", {STATUS: {"value": ["DELETED"]}})["limitResultsByStatus"] == ["DELETED"]
    assert set_find_body("Report", {STATUS: {"value": "ACTIVE"}})["limitResultsByStatus"] == ["ACTIVE"]
    assert set_filter_request_body("Report", {STATUS: {"value": "DELETED"}})["limitResultsByStatus"] == ["DELETED"]
    assert set_filter_request_body("Report", {})["limitResultsByStatus"] is None


# ── report.py ───────────────────────────────────────────────────────────────

def test_status_lists_are_stored_as_json_lists():
    attrs = {"Report Spec": {"value": "Collections"},
             STATUS: {"value": ["ACTIVE", "DELETED"]},
             CONTENT: {"value": ["DRAFT", "APPROVED"]},
             ACTIVITY: {"value": ["IN_PROGRESS"]}}
    ap = _report_additional_properties(attrs)
    assert ap["limitResultByStatus"] == '["ACTIVE", "DELETED"]'
    assert json.loads(ap["limitResultByContentStatus"]) == ["DRAFT", "APPROVED"]
    assert json.loads(ap["limitResultByActivityStatus"]) == ["IN_PROGRESS"]
    assert "limitResultByDeploymentStatus" not in ap
    doc = report_parameters_document(attrs)
    assert doc["limit_result_by_status"] == ["ACTIVE", "DELETED"]
    assert doc["limit_result_by_content_status"] == ["DRAFT", "APPROVED"]


def test_the_defaulted_status_is_stored_as_json_but_not_pinned():
    attrs = {"Report Spec": {"value": "Collections"}, STATUS: {"value": ["ACTIVE"], "is_default": True}}
    assert _report_additional_properties(attrs)["limitResultByStatus"] == '["ACTIVE"]'
    assert "limit_result_by_status" not in report_parameters_document(attrs)


# ── the executor ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw", ["draft, approved", "['DRAFT', 'APPROVED']", '["DRAFT","APPROVED"]',
                                 ["draft", "APPROVED"]])
def test_executor_normalizes_lifecycle_filters(raw):
    out = fse._normalize_report_params({"limit_result_by_content_status": raw}, action_mode="find")
    assert out["content_status_list"] == ["DRAFT", "APPROVED"]


class _LifecycleClient:
    """content_status_list is an explicit parameter, as on ClassificationExplorer.find_authored_elements."""

    def __init__(self):
        self.last_kwargs = None

    async def _async_find_authored_elements(self, search_string: str = "*", content_status_list=None,
                                            limit_results_by_status=None, output_format="JSON",
                                            report_spec=None, **kwargs):
        self.last_kwargs = dict(search_string=search_string, content_status_list=content_status_list,
                                limit_results_by_status=limit_results_by_status, **kwargs)
        return [{"guid": "1"}]


class _PlainFindClient:
    """Only the standard filters (**kwargs), like CollectionManager.find_collections."""

    def __init__(self):
        self.last_kwargs = None

    async def _async_find_collections(self, search_string: str = "*", output_format="JSON", report_spec=None,
                                      **kwargs):
        self.last_kwargs = dict(search_string=search_string, **kwargs)
        return [{"guid": "1"}]


class _FakeTech:
    def __init__(self, client):
        self.view_server, self.platform_url, self.user_id, self.user_pwd, self.token = "vs", "u", "u", "p", "t"
        self._client = client
        self._subclient_map = {"c": type(client)}

    def _get_subclient(self, name):
        return self._client

    def get_token(self):
        return self.token


async def _run(client, method, params, monkeypatch):
    fmt = {"action": {"function": f"X.{method}", "required_params": ["search_string"], "optional_params": [],
                      "spec_params": {}}, "target_type": "Referenceable"}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, out: fmt)
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (type(client), "_async_" + method))
    return await fse._async_run_report(report_name="R", egeria_client=cast(Any, _FakeTech(client)),
                                       output_format="DICT", params=params)


async def test_a_lifecycle_filter_reaches_a_method_that_takes_it(monkeypatch):
    client = _LifecycleClient()
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFilterWarning)
        await _run(client, "find_authored_elements",
                   {"search_string": "x", "limit_result_by_content_status": "DRAFT",
                    "limit_result_by_status": "['ACTIVE']"}, monkeypatch)
    assert client.last_kwargs["content_status_list"] == ["DRAFT"]
    assert client.last_kwargs["limit_results_by_status"] == ["ACTIVE"]
    assert "limit_result_by_content_status" not in client.last_kwargs


async def test_a_lifecycle_filter_is_dropped_with_a_warning_where_the_method_cannot_take_it(monkeypatch):
    client = _PlainFindClient()
    with pytest.warns(UnknownFilterWarning, match="content_status_list"):
        await _run(client, "find_collections",
                   {"search_string": "x", "limit_result_by_content_status": "DRAFT"}, monkeypatch)
    assert "content_status_list" not in client.last_kwargs
    assert "limit_result_by_content_status" not in client.last_kwargs


def test_add_lifecycle_filters_for_the_sync_path():
    def takes(search_string="*", deployment_status_list=None, **kwargs):
        return None

    params = fse._normalize_report_params({"limit_result_by_deployment_status": "active",
                                           "limit_result_by_activity_status": "COMPLETED"}, action_mode="find")
    with pytest.warns(UnknownFilterWarning, match="activity_status_list"):
        call = fse._add_lifecycle_filters("R", takes, params, {"search_string": "x"})
    assert call == {"search_string": "x", "deployment_status_list": ["ACTIVE"]}

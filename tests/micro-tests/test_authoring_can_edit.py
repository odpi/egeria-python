"""P2 can_edit, the owner's decision C (the Architect's ruling (b), 2026-11-14 late): yes for your own private
draft or a held artifact you created or own; no for a built-in spec or nothing you can read; unknown otherwise."""
import asyncio
import json

import pytest

from pyegeria.authoring import AuthoringRefused, async_can_edit, can_edit
from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
OLD = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00Z"})


@pytest.fixture(autouse=True)
def _fresh_gate():
    paging._GATE_CACHE.clear()
    yield
    paging._GATE_CACHE.clear()


def _el(qn, type_name="ReportSpec", zones=(), created_by="someone", owner=None):
    header = {"guid": f"g-{qn}", "type": {"typeName": type_name},
              "versions": {"version": 3, "createdBy": created_by}}
    if zones:
        header["zoneMembership"] = {"classificationProperties": {"zoneMembership": list(zones)}}
    if owner:
        header["ownership"] = {"classificationName": "Ownership", "classificationProperties": owner}
    return {"elementHeader": header, "properties": {"qualifiedName": qn, "displayName": qn.split("::")[-1]}}


class _Client:
    def __init__(self, elements=(), user="peterprofile", error=None):
        self.user_id, self.platform_url, self.error = user, "https://p:9443", error
        self.elements = {e["properties"]["qualifiedName"]: e for e in elements}
        outer = self

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                if outer.error:
                    raise outer.error
                return outer.elements.get(qn) or NULL

            async def _async_get_elements_by_property_value(self, *a, **kw):
                return NULL

        self.classification_manager = CM()

    def get_platform_origin(self):
        return OLD

    async def async_get_platform_origin(self):
        return OLD


def _ask(kind, ref, client):
    return asyncio.run(async_can_edit(kind, ref, client))


def test_your_own_private_draft_is_yes():
    c = _Client([_el("ReportSpec::Mine", zones=["peterprofile"], created_by="peterprofile")])
    assert _ask("spec", "Mine", c) == {"answer": "yes", "why": "It's your private draft."}


def test_a_held_spec_you_created_is_yes():
    c = _Client([_el("ReportSpec::Made", created_by="peterprofile")])
    out = _ask("spec", "Made", c)
    assert out["answer"] == "yes" and "You created it" in out["why"] and "new version" in out["why"]


def test_a_held_sheet_you_own_is_yes():
    c = _Client([_el("Dashboard::ops", "Dashboard", owner={"owner": "peterprofile", "ownerPropertyName": "userId",
                                                           "ownerTypeName": "UserIdentity"})])
    out = _ask("sheet", "ops", c)
    assert out["answer"] == "yes" and "You own it" in out["why"]


def test_a_built_in_spec_is_no():
    out = _ask("spec", "Referenceable", _Client())
    assert out["answer"] == "no" and "built-in" in out["why"]


def test_nothing_you_can_read_is_no():
    out = _ask("sheet", "nowhere", _Client())
    assert out["answer"] == "no" and "holds no sheet" in out["why"]


def test_someone_elses_held_spec_is_unknown():
    c = _Client([_el("ReportSpec::Theirs", created_by="garygeeke",
                     owner={"owner": "garygeeke", "ownerPropertyName": "userId"})])
    out = _ask("spec", "Theirs", c)
    assert out["answer"] == "unknown" and "Studio checks on open and at publish" in out["why"]


def test_an_owner_named_by_a_guid_is_unknown_not_no():
    c = _Client([_el("ReportSpec::ByGuid", owner={"owner": "f1e2-guid", "ownerPropertyName": "guid"})])
    out = _ask("spec", "ByGuid", c)
    assert out["answer"] == "unknown" and "not a user id" in out["why"]


def test_a_read_that_fails_is_unknown_never_no():
    out = _ask("spec", "Anything", _Client(error=TimeoutError("slow")))
    assert out["answer"] == "unknown" and "TimeoutError" in out["why"]


def test_a_report_on_an_older_platform_is_unknown():
    out = _ask("report", "Some Report", _Client())   # display-name read with no confirmed end
    assert out["answer"] == "unknown" and "couldn't be told" in out["why"]


def test_bad_arguments_are_refused_and_the_sync_form_works():
    with pytest.raises(AuthoringRefused):
        _ask("table", "x", _Client())
    with pytest.raises(AuthoringRefused):
        _ask("spec", "x", None)
    assert can_edit("spec", "Referenceable", _Client())["answer"] == "no"

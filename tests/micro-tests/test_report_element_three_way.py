"""Pager step 6 (the Architect's _report_element ruling, 2026-11-14): load_held("report") and the authoring
lookups read a Report by display name three-way: found -> the Report; absent -> "holds no Report named X";
unknown -> "couldn't confirm whether Egeria holds a Report named X" with the trace, never "holds no"."""
import asyncio
import json

import pytest

from pyegeria.authoring.lifecycle import _report_element, async_load_held
from pyegeria.authoring.models import AuthoringRefused
from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
GATED = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39.317Z"})
OLD = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00Z"})


@pytest.fixture(autouse=True)
def _fresh_gate():
    paging._GATE_CACHE.clear()
    yield
    paging._GATE_CACHE.clear()


def _report(name, guid="r1"):
    return {"elementHeader": {"guid": guid, "type": {"typeName": "Report"}},
            "properties": {"displayName": name, "qualifiedName": f"Report::{name}",
                           "additionalProperties": {"reportSpec": "Analytic Demo - Stale Assets"}}}


class _Client:
    def __init__(self, reports, about=OLD, url="https://p:9443"):
        self.reports, self.about, self.platform_url, self.reads = reports, about, url, []
        outer = self

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                return NULL

            async def _async_get_elements_by_property_value(self, value, names, start_from=0, page_size=0, **kw):
                outer.reads.append(start_from)
                hits = [r for r in outer.reports if r["properties"]["displayName"] == value]
                return hits[start_from:start_from + page_size] or NULL

        self.classification_manager = CM()

    def get_platform_origin(self):
        return self.about

    async def async_get_platform_origin(self):
        return self.about


def test_found_is_the_report_and_reads_one_page():
    c = _Client([_report("Stale Assets")])
    assert asyncio.run(_report_element(c, "Stale Assets"))["elementHeader"]["guid"] == "r1"
    assert c.reads == [0]


def test_two_on_the_page_are_refused():
    c = _Client([_report("Twin", "r1"), _report("Twin", "r2")])
    with pytest.raises(AuthoringRefused, match="2 Reports are named 'Twin'"):
        asyncio.run(_report_element(c, "Twin"))


def test_absent_on_a_gated_platform_says_holds_no():
    c = _Client([], about=GATED, url="https://gated:9443")
    assert asyncio.run(_report_element(c, "Nothing")) is None
    with pytest.raises(AuthoringRefused, match="Egeria holds no Report named 'Nothing'"):
        asyncio.run(async_load_held("report", "Nothing", c))


def test_unknown_on_an_older_platform_never_says_holds_no():
    c = _Client([], about=OLD, url="https://old:9443")
    with pytest.raises(AuthoringRefused) as exc:
        asyncio.run(async_load_held("report", "Nothing", c))
    words = str(exc.value)
    assert "Couldn't confirm whether Egeria holds a Report named 'Nothing'" in words
    assert "null_then_empty_probes" in words and "holds no" not in words


def test_a_preview_placement_on_an_unknown_read_isnt_called_missing_for_no_report():
    from pyegeria.authoring.models import SheetDraft
    from pyegeria.authoring.preview import _sheet_for_resolver
    draft = SheetDraft.model_validate({"name": "s", "heading": "S", "placements": [{"report": "Nothing"}]}) \
        if hasattr(SheetDraft, "model_validate") else None
    if draft is None:
        pytest.skip("SheetDraft has no model_validate")
    notes = []
    sheet = asyncio.run(_sheet_for_resolver(draft, _Client([], about=OLD, url="https://old2:9443"), notes))
    [placement] = sheet.placements
    assert placement.kind == "missing" and "Couldn't confirm" in placement.note
    assert "no Report by this name" not in placement.note

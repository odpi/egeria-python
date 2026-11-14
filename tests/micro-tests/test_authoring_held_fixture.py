# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""load_held on a real sheet: the catalog-health sheet and its Reports, as Egeria answered.

Fixture: tests/micro-tests/data/authoring/catalog_health_scratch.json, every client call load_held made and
Egeria's answer, captured on the round-trip probe's scratch Egeria (757a5df0, PostgreSQL) after processing the
Catalog Health section of LOCAL_DASHBOARDS_USEFUL_SHEETS.dr-egeria.md, the document that seeded the sheet on
laz. Not read from laz. Replayed here offline. It has 6 placements: laz's sheet also has the saved-query tile
(LOCAL_DASHBOARDS_SAVED_QUERY_TILE.dr-egeria.md), covered from laz's real shape in test_authoring_laz_sheet.py.
"""
import asyncio
import json
from pathlib import Path

import pytest

from pyegeria.authoring import diff, serialize
from pyegeria.authoring.lifecycle import async_load_held
from pyegeria.authoring.serialize import parsed_commands, report_parameter_maps

pytestmark = pytest.mark.unit

FX = json.loads((Path(__file__).parent / "data" / "authoring" / "catalog_health_scratch.json").read_text())


def _key(sub, method, args, kwargs):
    return json.dumps([sub, method, list(args), kwargs], sort_keys=True, default=str)


class _Replay:
    """A client that answers each call with the recorded answer; an unrecorded call fails the test."""
    user_id = "garygeeke"

    def __init__(self):
        self.synthesised = []
        self._answers = {}
        for c in FX["calls"]:
            self._answers.setdefault(_key(c["sub"], c["method"], c["args"], c["kwargs"]), c["result"])

    def _past_recorded_null(self, sub, method, args, kwargs):
        """Pager step 4: the reader now advances by the page size and probes 3 pages past a null (a suspect
        path); this fixture was captured before, so it stops at the null. A page past a RECORDED null of the
        same call (same arguments but start_from) is answered with that null, and listed in `synthesised`. On
        a suspect path a null only ends a read as not_confirmed, never as a confirmed end. To be replaced by
        a re-capture that includes the probe pages."""
        start = kwargs.get("start_from")
        if not isinstance(start, int):
            return None
        rest = {k: v for k, v in kwargs.items() if k != "start_from"}
        for c in FX["calls"]:
            ks = c["kwargs"]
            if ((c["sub"], c["method"], c["args"]) == (sub, method, args) and isinstance(ks.get("start_from"), int)
                    and ks["start_from"] < start and {k: v for k, v in ks.items() if k != "start_from"} == rest
                    and isinstance(c["result"], str)):
                self.synthesised.append((sub, method, start))
                return c["result"]
        return None

    def __getattr__(self, sub):
        outer = self

        class Sub:
            def __getattr__(self, method):
                async def call(*args, **kwargs):
                    a = json.loads(json.dumps(list(args), default=str))
                    kw = json.loads(json.dumps(kwargs, default=str))
                    key = _key(sub, method, a, kw)
                    if key not in outer._answers and (null := outer._past_recorded_null(sub, method, a, kw)):
                        return null
                    assert key in outer._answers, f"unrecorded call {sub}.{method}{args}{kwargs}"
                    return outer._answers[key]
                return call
        return Sub()


def _sheet():
    return asyncio.run(async_load_held("sheet", "catalog-health", _Replay()))


def test_load_held_reads_the_real_sheet():
    sheet = _sheet()
    assert sheet.heading == "Catalog Health" and sheet.family == "Overview"
    assert sheet.guid and sheet.base_version is not None
    assert [(p.kind, p.name) for p in sheet.placements] == [
        ("text", "What these tiles measure"),
        ("report", "Catalog Health - AI Context Readiness"),
        ("report", "Catalog Health - Asset Ownership"),
        ("report", "Catalog Health - Stale Assets"),
        ("report", "Catalog Health - Asset Composition"),
        ("report", "Catalog Health - Catalog Growth, 90 Days"),
    ]
    assert sheet.placements[0].span == "full" and sheet.placements[0].emphasis == "panel"
    assert not [n for n in sheet.notes if "missing" in n]


def test_held_sheet_serializes_and_parses_back_to_the_same_placements():
    sheet = _sheet()
    parsed = parsed_commands(serialize(sheet))
    assert parsed[0][0] == "Create Dashboard Sheet"
    got = []
    for command, attrs in parsed[1:]:
        name = attrs.get("Report Name", attrs.get("Placement Name"))["value"]
        got.append((command, name, attrs["Placement Span"]["value"], attrs["Placement Emphasis"]["value"]))
    want = [("Add Text on Dashboard Sheet" if p.text is not None else "Link Report to Dashboard Sheet",
             p.name, p.span, p.emphasis) for p in sheet.placements]
    assert got == want
    assert parsed[1][1]["MD Content"]["value"].strip() == sheet.placements[0].text.strip()


def test_held_sheet_round_trip_has_no_diff():
    sheet = _sheet()
    again = sheet.model_copy(deep=True)
    assert diff(sheet, again).changes == []


def test_held_reports_read_their_parameters():
    reports = {r: asyncio.run(async_load_held("report", r, _Replay())) for r in
               ("Catalog Health - Stale Assets", "Catalog Health - Asset Composition",
                "Catalog Health - Catalog Growth, 90 Days")}
    stale = reports["Catalog Health - Stale Assets"]
    assert stale.spec == "Analytic Demo - Stale Assets" and stale.output_format.upper() == "DICT"
    assert stale.analytic_params == {"days": 180}
    growth = reports["Catalog Health - Catalog Growth, 90 Days"]
    assert growth.analytic_params == {"window": "90d", "points": 6}
    composition = reports["Catalog Health - Asset Composition"]
    assert composition.analytic_params["type_map"][0] == ["Data Stores", "DataStore"]
    # The serialized Report keeps its analytic parameters, typed.
    maps = report_parameter_maps(growth)
    assert json.loads(maps["additionalProperties"]["analyticParams"]) == {"window": "90d", "points": 6}

# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""load_held on a real sheet: the catalog-health sheet and its Reports, as Egeria answered.

Fixture: tests/micro-tests/data/authoring/catalog_health_scratch.json, every client call load_held made and
Egeria's answer, captured on the round-trip probe's scratch Egeria (757a5df0, PostgreSQL) after processing the
Catalog Health section of LOCAL_DASHBOARDS_USEFUL_SHEETS.dr-egeria.md, the document that seeded the sheet on
laz. Not read from laz. Replayed here offline.
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
        self._answers = {}
        for c in FX["calls"]:
            self._answers.setdefault(_key(c["sub"], c["method"], c["args"], c["kwargs"]), c["result"])

    def __getattr__(self, sub):
        outer = self

        class Sub:
            def __getattr__(self, method):
                async def call(*args, **kwargs):
                    key = _key(sub, method, json.loads(json.dumps(list(args), default=str)),
                               json.loads(json.dumps(kwargs, default=str)))
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

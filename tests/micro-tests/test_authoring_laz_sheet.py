# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The authoring API on the catalog-health sheet as laz holds it: all 7 placements, the saved-query tile included.

Fixture: tests/micro-tests/data/authoring/catalog_health_laz_2026_11_12.json, copied unchanged from the
Portal's real-shape capture (egeria-workspaces PyegeriaWebHandler/tests/fixtures/
local_dashboards_real_shape_2026_11_12.json, read-only from laz). The scratch replay
(test_authoring_held_fixture.py) covers reading the sheet's element chain; this covers what laz actually holds,
including the one analytic-with-cached-count Report (`Saved Query Result`, analytic `saved_query`).
"""
import json
from pathlib import Path

import pytest

from pyegeria.authoring import diff, serialize
from pyegeria.authoring.lifecycle import report_draft_from_element, sheet_draft_from_sheet
from pyegeria.authoring.serialize import FIND_PARAMETERS, parsed_commands, report_parameter_maps
from pyegeria.view.dashboards import EgeriaDashboardSheet

pytestmark = pytest.mark.unit

FX = json.loads((Path(__file__).parent / "data" / "authoring" / "catalog_health_laz_2026_11_12.json").read_text())
SAVED_QUERY_TILE = "Catalog Health - Assets with No Lineage"


def _sheet():
    return sheet_draft_from_sheet(EgeriaDashboardSheet.model_validate(FX["sheet"]))


def _reports():
    return {el["properties"]["displayName"]: report_draft_from_element(el) for el in FX["reports"].values()}


def test_the_laz_sheet_reads_as_seven_placements_in_order():
    sheet = _sheet()
    assert sheet.name == "catalog-health" and sheet.heading == "Catalog Health" and sheet.family == "Overview"
    assert [(p.text is not None, p.name, p.span, p.emphasis) for p in sheet.placements] == [
        (True, "What these tiles measure", "full", "panel"),
        (False, "Catalog Health - AI Context Readiness", "2", "panel"),
        (False, "Catalog Health - Asset Ownership", "2", "panel"),
        (False, "Catalog Health - Stale Assets", "1", "kpi"),
        (False, "Catalog Health - Asset Composition", "2", "panel"),
        (False, "Catalog Health - Catalog Growth, 90 Days", "full", "panel"),
        (False, SAVED_QUERY_TILE, "full", "panel"),
    ]
    assert sheet.notes == []


def test_the_laz_sheet_serializes_and_parses_back_to_the_same_seven_placements():
    sheet = _sheet()
    parsed = parsed_commands(serialize(sheet))
    assert parsed[0][0] == "Create Dashboard Sheet"
    got = [(command, attrs.get("Report Name", attrs.get("Placement Name"))["value"],
            attrs["Placement Span"]["value"], attrs["Placement Emphasis"]["value"]) for command, attrs in parsed[1:]]
    assert got == [("Add Text on Dashboard Sheet" if p.text is not None else "Link Report to Dashboard Sheet",
                    p.name, p.span, p.emphasis) for p in sheet.placements]
    assert len(got) == 7 and got[-1][1] == SAVED_QUERY_TILE
    assert diff(sheet, sheet.model_copy(deep=True)).changes == []


def test_the_saved_query_report_reads_its_cached_count_parameters():
    tile = _reports()[SAVED_QUERY_TILE]
    assert tile.spec == "Saved Query Result" and tile.output_format == "DICT"
    assert tile.analytic_params == {"name": "SavedQuery::useful-sheets::Assets with no lineage",
                                    "mode": "cached", "output": "count"}
    assert tile.parameters == {} and tile.pinned_version is None


def test_every_laz_report_round_trips_through_the_serializer():
    """What publishing would write for each Report gives back the same draft when read as an element."""
    for name, draft in _reports().items():
        maps = report_parameter_maps(draft)
        stored = FX["reports"][draft.guid]["properties"]["additionalProperties"]
        assert maps["additionalProperties"]["reportSpec"] == stored["reportSpec"], name
        if "analyticParams" in stored:
            assert json.loads(maps["additionalProperties"]["analyticParams"]) == json.loads(stored["analyticParams"])
        again = report_draft_from_element({"elementHeader": {"guid": draft.guid},
                                           "properties": {**FX["reports"][draft.guid]["properties"],
                                                          "additionalProperties": maps["additionalProperties"]}})
        # Dr.Egeria's Create Report writes the common find parameters with their defaults; the captured
        # elements don't show them (the capture is trimmed to the fields the Portal reads, so whether laz
        # holds them isn't known from here). Anything else that differs is a real round-trip loss.
        changes = diff(draft, again).changes
        assert all(c.area == "parameter" and c.change == "added" and c.name in FIND_PARAMETERS
                   and not c.breaking for c in changes), (name, changes)
        assert again.analytic_params == draft.analytic_params and again.spec == draft.spec
        assert again.output_format == draft.output_format

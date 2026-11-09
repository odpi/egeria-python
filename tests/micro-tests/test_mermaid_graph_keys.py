"""Egeria graph keys (6.2.29): a generic rule recognises every graph Egeria returns, and the action
and activity graphs follow the context graph wherever a report offers it.

From Egeria 6.2.29 the context graph (mermaidGraph) leaves out relationships whose purpose is
Action or Activity; actionMermaidGraph and activityMermaidGraph show them.

Recorded input (read only, qs-view-server):
- `data/graph_keys_responses.json`: a GovernanceZone carrying zoneProfileMermaidPieChart and
  zoneProfileAllMermaidPieChart, and an asset lineage graph carrying fullLineageMermaidGraph and
  edgeMermaidGraph;
- `data/asset_graph_by_guid_response.json`: an asset graph carrying anchorMermaidGraph and
  actionMermaidGraph.
The platform did not yet return activityMermaidGraph, collectionMermaidMindMap, the anchored-zone
and user-account pie charts, fieldLevelLineageGraph or localLineageGraph; the tests add those to
copies of the recorded elements.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pyegeria.view import output_formatter as of
from pyegeria.view.base_report_formats import select_report_spec

pytestmark = pytest.mark.unit

DATA = Path(__file__).parent / "data"
RESPONSES = json.loads((DATA / "graph_keys_responses.json").read_text())
ZONE = RESPONSES["zone"]
LINEAGE = RESPONSES["lineage"]
ASSET_GRAPH = json.loads((DATA / "asset_graph_by_guid_response.json").read_text())["response"]

#: The 25 graph keys Egeria returns (owner's list, 2026-11-09).
EGERIA_GRAPH_KEYS = [
    "mermaidGraph", "anchorMermaidGraph", "actionMermaidGraph", "activityMermaidGraph", "edgeMermaidGraph",
    "specificationMermaidGraph", "solutionBlueprintMermaidGraph", "solutionSubcomponentMermaidGraph",
    "informationSupplyChainMermaidGraph", "iscImplementationMermaidGraph", "iscSystemFabricMermaidGraph",
    "iscDataMeshMermaidGraph", "iscDataMappingMermaidGraph", "iscDataFabricMermaidGraph",
    "organizationTreeMermaidGraph", "rootHierarchyMermaidGraph", "fullLineageMermaidGraph",
    "collectionMermaidMindMap",
    "zoneProfileMermaidPieChart", "zoneProfileAnchoredMermaidPieChart", "zoneProfileAllMermaidPieChart",
    "userAccountTypeProfileMermaidPieChart", "userAccountStatusProfileMermaidPieChart",
    "fieldLevelLineageGraph", "localLineageGraph",
]

ACTION = "flowchart LR\n  A[Engine] -->|ActionTarget| B[Stock]"
ACTIVITY = "flowchart LR\n  P[Process] -->|ProcessCall| S[Step]"


def _with(element, **graphs):
    el = copy.deepcopy(element)
    el.update(graphs)
    return el


# ── the generic rule ──

def test_every_egeria_graph_key_is_recognised():
    assert len(EGERIA_GRAPH_KEYS) == 25
    for key in EGERIA_GRAPH_KEYS:
        assert of.is_mermaid_graph_key(key), key
        assert of._is_mermaid_attribute("Whatever", key), key


def test_a_new_kind_of_graph_is_recognised_without_a_code_change():
    for key in ("somethingNewMermaidGraph", "glossaryMermaidMindMap", "zoneAgeMermaidPieChart",
                "columnLineageGraph", "iscimplementationMermaidGraph"):
        assert of.is_mermaid_graph_key(key), key
    for title in ("Something New Mermaid Graph", "Glossary Mermaid Mind Map", "Zone Age Mermaid Pie Chart",
                  "Column Lineage Graph"):
        assert of._is_mermaid_attribute(title, None), title


def test_vega_and_ordinary_keys_are_not_mermaid():
    for key in ("typeMembershipPieGraph", "typeMembershipBarGraph", "userAccountTypeProfileBarGraph",
                "displayName", "graph", "mermaid_like", None, ""):
        assert not of.is_mermaid_graph_key(key), key


def test_every_key_in_the_recorded_responses_renders_as_mermaid():
    seen = set()
    for element in (ZONE, LINEAGE, ASSET_GRAPH):
        for key, value in element.items():
            if not of.is_mermaid_graph_key(key) or not value:
                continue
            seen.add(key)
            out = of.make_md_attribute(key, value, "REPORT", attribute_key=key)
            assert out.count("```mermaid") == 1, key
    assert {"mermaidGraph", "anchorMermaidGraph", "actionMermaidGraph", "edgeMermaidGraph",
            "fullLineageMermaidGraph", "zoneProfileMermaidPieChart", "zoneProfileAllMermaidPieChart"} <= seen


@pytest.mark.parametrize("key, value", [
    ("collectionMermaidMindMap", "mindmap\n  root((Collection))\n    Member"),
    ("zoneProfileAnchoredMermaidPieChart", 'pie\ntitle Anchored\n"Asset (3)" : 3'),
    ("userAccountTypeProfileMermaidPieChart", 'pie\ntitle Types\n"EMPLOYEE (4)" : 4'),
    ("userAccountStatusProfileMermaidPieChart", 'pie\ntitle Status\n"AVAILABLE (4)" : 4'),
    ("fieldLevelLineageGraph", "flowchart LR\n  a.col --> b.col"),
    ("localLineageGraph", "flowchart LR\n  x --> y"),
    ("activityMermaidGraph", ACTIVITY),
])
def test_keys_the_platform_does_not_return_yet_render_when_selected(key, value):
    element = _with(ZONE, **{key: value})
    columns = {"formats": {"attributes": [{"name": "Graph", "key": key}]}}
    out = of.extract_mermaid_only([element], columns)
    assert out.count("```mermaid") == 1
    assert value.splitlines()[0] in out


def test_populate_common_columns_fills_a_generic_graph_key_only_when_present():
    columns = {"formats": {"attributes": [{"name": "Mind Map", "key": "collectionMermaidMindMap", "value": None}]}}
    filled = of.populate_common_columns(_with(ZONE, collectionMermaidMindMap="mindmap\n  root((C))"),
                                        copy.deepcopy(columns))
    assert filled["formats"]["attributes"][0]["value"] == "mindmap\n  root((C))"
    absent = of.populate_common_columns(copy.deepcopy(ZONE), copy.deepcopy(columns))
    assert absent["formats"]["attributes"][0]["value"] is None


# ── the action and activity graphs follow the context graph ──

COLLECTIONS = "Collections"  # declares mermaidGraph in REPORT and MERMAID, not the companions


def _render(element, fmt, spec=COLLECTIONS):
    return of.generate_output([copy.deepcopy(element)], "x", "Thing", fmt, of.populate_columns_from_properties,
                              None, copy.deepcopy(select_report_spec(spec, fmt)))


def test_mermaid_shows_context_then_action_then_activity():
    element = _with(ZONE, actionMermaidGraph=ACTION, activityMermaidGraph=ACTIVITY)
    out = _render(element, "MERMAID")
    blocks = [of._format_mermaid_value(element[k]) for k in ("mermaidGraph", "actionMermaidGraph",
                                                              "activityMermaidGraph")]
    assert out.count("```mermaid") == 3
    positions = [out.index(b) for b in blocks]
    assert positions == sorted(positions)


def test_report_and_html_show_the_companions_after_the_context_graph():
    element = _with(ZONE, actionMermaidGraph=ACTION, activityMermaidGraph=ACTIVITY)
    report = _render(element, "REPORT")
    assert report.index("### Mermaid\n") < report.index("### Action Mermaid Graph") \
        < report.index("### Activity Mermaid Graph")
    assert report.count("```mermaid") == 3
    html = of.generate_output([copy.deepcopy(element)], "x", "Thing", "HTML", of.populate_columns_from_properties,
                              None, copy.deepcopy(select_report_spec(COLLECTIONS, "REPORT")))
    assert "Action Mermaid Graph" in html and "Activity Mermaid Graph" in html


def test_dict_carries_the_companions_and_table_does_not():
    element = _with(ZONE, actionMermaidGraph=ACTION, activityMermaidGraph=ACTIVITY)
    spec = select_report_spec("Governance-Zone-Overview-Charts", "DICT")
    assert any(c["key"] in ("mermaidGraph", "mermaid") for c in spec["formats"]["attributes"])
    row = of.generate_output([copy.deepcopy(element)], "x", "Thing", "DICT", of.populate_columns_from_properties,
                             None, copy.deepcopy(spec))[0]
    assert row["Action Mermaid Graph"] == ACTION and row["Activity Mermaid Graph"] == ACTIVITY
    names = list(row)
    context = next(c["name"] for c in spec["formats"]["attributes"] if c["key"] in ("mermaidGraph", "mermaid"))
    assert names.index(context) < names.index("Action Mermaid Graph") < names.index("Activity Mermaid Graph")
    table = of.generate_entity_dict([copy.deepcopy(element)], of.populate_columns_from_properties,
                                    columns_struct=copy.deepcopy(spec), output_format="TABLE")[0]
    assert "Action Mermaid Graph" not in table and "Activity Mermaid Graph" not in table


def test_only_the_companions_the_element_carries_are_added():
    report = _render(_with(ZONE, activityMermaidGraph=ACTIVITY), "REPORT")
    assert "### Activity Mermaid Graph" in report and "Action Mermaid Graph" not in report


def test_no_companion_keys_means_no_change():
    for fmt in ("MERMAID", "REPORT"):
        out = _render(ZONE, fmt)
        assert "Action Mermaid Graph" not in out and "Activity Mermaid Graph" not in out
    assert of.extract_mermaid_only([copy.deepcopy(ZONE)], None) == of._format_mermaid_value(ZONE["mermaidGraph"])


def test_a_report_without_the_context_graph_gets_no_companions():
    columns = {"formats": {"attributes": [{"name": "Pie", "key": "zoneProfileMermaidPieChart"}]}}
    out = of.extract_mermaid_only([_with(ZONE, actionMermaidGraph=ACTION)], columns)
    assert out.count("```mermaid") == 1 and "Engine" not in out


def test_a_companion_the_spec_already_selects_is_not_repeated():
    # Asset-Graph's REPORT declares Mermaid Graph, Anchor Graph and Action Graph itself.
    element = _with(ASSET_GRAPH, activityMermaidGraph=ACTIVITY)
    report = _render(element, "REPORT", spec="Asset-Graph")
    action = of._format_mermaid_value(ASSET_GRAPH["actionMermaidGraph"])
    assert report.count(action) == 1
    assert "### Action Mermaid Graph" not in report  # shown under the spec's own "Action Graph"
    assert report.count("### Activity Mermaid Graph") == 1

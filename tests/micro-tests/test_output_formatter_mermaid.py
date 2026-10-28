from pyegeria.view import output_formatter as of


def test_normalize_mermaid_graph_transforms_renderer_hostile_syntax(monkeypatch):
    monkeypatch.setattr(of, "NORMALIZE_MERMAID", True)

    raw = """---
title: Sample
---
flowchart TD
1@{ shape: rounded, label: \"*A*\n**B**\"}
"""

    normalized = of._normalize_mermaid_graph(raw)

    assert "title: Sample" not in normalized
    assert '1("*A*<br/>**B**")' in normalized
    assert "@{" not in normalized


def test_resolve_normalize_mermaid_flag_defaults_true_when_unset(monkeypatch):
    monkeypatch.delenv("PYEGERIA_NORMALIZE_MERMAID", raising=False)
    monkeypatch.delenv("EGERIA_NORMALIZE_MERMAID", raising=False)
    assert of._resolve_normalize_mermaid_flag(default=True) is True


def test_resolve_normalize_mermaid_flag_honors_false_and_invalid(monkeypatch):
    monkeypatch.setenv("PYEGERIA_NORMALIZE_MERMAID", "false")
    assert of._resolve_normalize_mermaid_flag(default=True) is False

    monkeypatch.setenv("PYEGERIA_NORMALIZE_MERMAID", "maybe")
    assert of._resolve_normalize_mermaid_flag(default=True) is True

def test_extract_mermaid_only_uses_selected_report_spec_field():
    elements = [{
        "collectionMermaidMindMap": "mindmap\\n  root((Collection))",
        "mermaidGraph": "flowchart TD\\n  A-->B",
    }]
    columns_struct = {
        "formats": {
            "attributes": [
                {"name": "Collection Mermaid Mind Map", "key": "collectionMermaidMindMap"},
            ]
        }
    }

    result = of.extract_mermaid_only(elements, columns_struct)

    assert "```mermaid\nmindmap" in result
    assert "root((Collection))" in result
    assert "flowchart TD" not in result

def test_extract_mermaid_only_missing_selected_field_renders_separator():
    elements = [{
        "mermaidGraph": "flowchart TD\\n  A-->B",
    }]
    columns_struct = {
        "formats": {
            "attributes": [
                {"name": "Collection Mermaid Mind Map", "key": "collectionMermaidMindMap"},
            ]
        }
    }

    result = of.extract_mermaid_only(elements, columns_struct)

    assert result == "---"


def test_extract_mermaid_only_legacy_fallback_uses_mermaid_graph():
    elements = [{
        "mermaidGraph": "flowchart TD\\n  A-->B",
    }]

    result = of.extract_mermaid_only(elements)

    assert "```mermaid" in result
    assert "flowchart TD" in result
    assert "A-->B" in result


def test_extract_mermaid_only_selected_field_does_not_include_other_mermaid_graphs():
    elements = [{
        "collectionMermaidMindMap": "mindmap\\n  root((Collection))",
        "mermaidGraph": "flowchart TD\\n  A-->B",
        "solutionBlueprintMermaidGraph": "flowchart LR\\n  X-->Y",
    }]
    columns_struct = {
        "formats": {
            "attributes": [
                {"name": "Collection Mermaid Mind Map", "key": "collectionMermaidMindMap"},
            ]
        }
    }

    result = of.extract_mermaid_only(elements, columns_struct)

    assert "mindmap" in result
    assert "flowchart TD" not in result
    assert "flowchart LR" not in result


def test_flowchart_escaped_newline_in_label_becomes_br():
    raw = 'flowchart TD\n1("*Solution Blueprint*\\n**Open Metadata Digital Products Content Pack**")'

    result = of._format_mermaid_value(raw)

    assert "<br/>" in result
    assert "\\n" not in result


def test_mindmap_escaped_newlines_become_real_newlines():
    raw = "mindmap\\n**DigitalProductFamily** Open Metadata Digital Products\\n    **DigitalProductFamily** Reference Data Sets"

    result = of._format_mermaid_value(raw)

    assert "mindmap\n**DigitalProductFamily**" in result
    assert "\\n" not in result

def test_resolve_normalize_mermaid_flag_reads_from_app_config(monkeypatch):
    monkeypatch.delenv("PYEGERIA_NORMALIZE_MERMAID", raising=False)
    monkeypatch.delenv("EGERIA_NORMALIZE_MERMAID", raising=False)

    class _Env:
        egeria_normalize_mermaid = False

    class _Cfg:
        Environment = _Env()

    import pyegeria.core.config as cfg_mod

    monkeypatch.setattr(cfg_mod, "get_app_config", lambda *args, **kwargs: _Cfg())
    assert of._resolve_normalize_mermaid_flag(default=True) is False




def test_isc_6_3_graph_keys_render_as_mermaid():
    elements = [{
        "iscImplementationMermaidGraph": "flowchart TD\\n  I-->J",
        "iscDataMeshMermaidGraph": "flowchart LR\\n  P-->Q",
        "iscDataMappingMermaidGraph": "flowchart LR\\n  C-->D",
    }]
    columns_struct = {
        "formats": {
            "attributes": [
                {"name": "ISC Implementation Graph", "key": "iscImplementationMermaidGraph"},
                {"name": "ISC Data Mesh Graph", "key": "iscDataMeshMermaidGraph"},
                {"name": "ISC Data Mapping Graph", "key": "iscDataMappingMermaidGraph"},
            ]
        }
    }

    result = of.extract_mermaid_only(elements, columns_struct)

    assert result.count("```mermaid") == 3
    assert "I-->J" in result and "P-->Q" in result and "C-->D" in result


def test_isc_implementation_graph_matches_pre_6_3_lower_case_key():
    # Servers before Egeria 6.3 wrote the key with a lower-cased 'ISC'.
    element = {"iscimplementationMermaidGraph": "flowchart TD\\n  A-->B"}
    columns_struct = {
        "formats": {
            "attributes": [
                {"name": "ISC Implementation Graph", "key": "iscImplementationMermaidGraph"},
            ]
        }
    }

    assert of._get_mermaid_graph_value(element, "iscImplementationMermaidGraph") == element["iscimplementationMermaidGraph"]
    result = of.extract_mermaid_only([element], columns_struct)
    assert "```mermaid" in result
    assert "A-->B" in result


def test_mermaid_graph_titles_stay_aligned_with_keys():
    from pyegeria.core._globals import MERMAID_GRAPH_TITLES, MERMAID_GRAPHS

    assert len(MERMAID_GRAPHS) == len(MERMAID_GRAPH_TITLES)
    assert MERMAID_GRAPH_TITLES[MERMAID_GRAPHS.index("iscDataFabricMermaidGraph")] == "ISC Data Fabric Graph"


def test_isc_graph_heading_keeps_acronym():
    from pyegeria.core.utils import camel_to_title_case

    assert camel_to_title_case("ISC Data Mesh Graph") == "ISC Data Mesh Graph"
    assert camel_to_title_case("iscDataMeshMermaidGraph") == "ISC Data Mesh Mermaid Graph"

    heading = of.make_md_attribute("ISC Data Mesh Graph", "flowchart LR\\n  P-->Q", "REPORT",
                                   attribute_key="iscDataMeshMermaidGraph")
    assert heading.startswith("### ISC Data Mesh Graph")
    assert "```mermaid" in heading

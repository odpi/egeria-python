"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Shapes for an Egeria asset graph (AssetCatalog.get_asset_graph_by_guid, the `Asset-Graph` report
spec), one per output format (pyegeria 6.2.28):

- DICT / TABLE: one row per edge: the from element (display name, type, GUID), the relationship
  type, and the to element (display name, type, GUID). Includes the asset's own relationships.
- LIST: the nodes, as a markdown table: the asset, the elements anchored to it, and every element
  an edge reaches.
- REPORT / MD: the asset summary, its graph (mermaid) and the edge table, as markdown. HTML is the
  same document rendered to HTML.
- MERMAID: the graph (handled by the generic mermaid path; see AssetCatalog).
- JSON: the full graph response, unchanged.

A graph is never one row of mermaid text.

How the response holds edges: `relationships` lists the edges among the asset and its anchored
elements, each with `startingElementGUID` (one end), `relatedElement` (the other end) and
`relatedElementAtEnd1` (which end that is). The asset's own relationships are keyed lists at the
top level (for example `governedBy`, `requestedActions`), each item a `relatedElement` with
`relatedElementAtEnd1`, the asset being the other end. An edge reported twice (the same
relationship GUID) is listed once. Rows are sorted, so the order never depends on the order Egeria
returned them in. Paging (`start_from`, `page_size`) is Egeria's, on the graph request.

Pure functions: no I/O, no client.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

#: DICT/TABLE row keys, in column order: the edge table.
EDGE_COLUMNS: List[Tuple[str, str]] = [
    ("From Display Name", "from_display_name"),
    ("From Type", "from_type"),
    ("From GUID", "from_guid"),
    ("Relationship", "relationship_type"),
    ("To Display Name", "to_display_name"),
    ("To Type", "to_type"),
    ("To GUID", "to_guid"),
]

#: LIST columns: the node table.
NODE_COLUMNS: List[Tuple[str, str]] = [
    ("Display Name", "display_name"),
    ("Type", "type_name"),
    ("GUID", "guid"),
    ("Role", "role"),
]

#: The REPORT/MD asset summary: (label, how to read it from the asset element).
_SUMMARY_FIELDS = [
    ("Display Name", ("properties", "displayName")),
    ("Qualified Name", ("properties", "qualifiedName")),
    ("Description", ("properties", "description")),
    ("Type", ("elementHeader", "type", "typeName")),
    ("GUID", ("elementHeader", "guid")),
    ("Created By", ("elementHeader", "versions", "createdBy")),
    ("Create Time", ("elementHeader", "versions", "createTime")),
    ("Updated By", ("elementHeader", "versions", "updatedBy")),
    ("Update Time", ("elementHeader", "versions", "updateTime")),
    ("Version", ("elementHeader", "versions", "version")),
]

#: The graphs the REPORT shows, in order, when the response carries them.
_REPORT_GRAPHS = [("Graph", "mermaidGraph"), ("Anchor Graph", "anchorMermaidGraph"),
                  ("Action Graph", "actionMermaidGraph"), ("Field Level Lineage Graph", "fieldLevelLineageGraph")]


def _dig(obj: Any, path) -> Any:
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _node(element: Dict[str, Any]) -> Dict[str, str]:
    header = element.get("elementHeader") or {}
    props = element.get("properties") or {}
    return {"guid": header.get("guid") or "",
            "type_name": _dig(header, ("type", "typeName")) or "",
            "display_name": (props.get("displayName") or props.get("name") or props.get("qualifiedName")
                             or element.get("uniqueName") or "")}


def _is_edge(item: Any) -> bool:
    return isinstance(item, dict) and "relationshipHeader" in item and isinstance(item.get("relatedElement"), dict)


def _asset_edge_lists(graph: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    """The asset's own relationships: every top-level list (other than `relationships`) of edges."""
    return [v for k, v in graph.items()
            if k != "relationships" and isinstance(v, list) and v and all(_is_edge(i) for i in v)]


def graph_nodes(graph: Dict[str, Any]) -> List[Dict[str, str]]:
    """Every node: the asset first, then anchored elements, then other related elements, by name."""
    asset = _node(graph)
    asset["role"] = "asset"
    seen = {asset["guid"]: asset}
    anchored, related = [], []
    for el in graph.get("anchoredElements") or []:
        n = _node(el)
        if n["guid"] and n["guid"] not in seen:
            n["role"] = "anchored"
            seen[n["guid"]] = n
            anchored.append(n)
    for edges in [graph.get("relationships") or []] + _asset_edge_lists(graph):
        for item in edges:
            if not _is_edge(item):
                continue
            n = _node(item["relatedElement"])
            if n["guid"] and n["guid"] not in seen:
                n["role"] = "related"
                seen[n["guid"]] = n
                related.append(n)
    order = lambda n: (n["display_name"].lower(), n["type_name"], n["guid"])  # noqa: E731
    return [asset] + sorted(anchored, key=order) + sorted(related, key=order)


def graph_edges(graph: Dict[str, Any]) -> List[Dict[str, str]]:
    """One row per edge (keys: the labels of EDGE_COLUMNS), sorted, each relationship once."""
    nodes = {n["guid"]: n for n in graph_nodes(graph)}
    asset_guid = _node(graph)["guid"]
    rows: Dict[str, Dict[str, str]] = {}

    def add(item: Dict[str, Any], starting_guid: Optional[str]) -> None:
        header = item["relationshipHeader"]
        rel_guid = header.get("guid") or ""
        related = _node(item["relatedElement"])
        start = nodes.get(starting_guid or "") or {"guid": starting_guid or "", "type_name": "", "display_name": ""}
        if item.get("relatedElementAtEnd1"):
            end1, end2 = related, start
        else:
            end1, end2 = start, related
        key = rel_guid or f"{end1['guid']}|{_dig(header, ('type', 'typeName'))}|{end2['guid']}"
        if key in rows:
            return
        values = {"from_display_name": end1["display_name"], "from_type": end1["type_name"],
                  "from_guid": end1["guid"], "relationship_type": _dig(header, ("type", "typeName")) or "",
                  "to_display_name": end2["display_name"], "to_type": end2["type_name"], "to_guid": end2["guid"]}
        rows[key] = {label: values[k] for label, k in EDGE_COLUMNS} | {"_relationship_guid": rel_guid}

    for item in graph.get("relationships") or []:
        if _is_edge(item):
            add(item, item.get("startingElementGUID") or asset_guid)
    for edges in _asset_edge_lists(graph):
        for item in edges:
            add(item, asset_guid)

    def order(r):
        return (r["From Display Name"].lower(), r["Relationship"], r["To Display Name"].lower(),
                r["From GUID"], r["To GUID"], r["_relationship_guid"])

    out = sorted(rows.values(), key=order)
    for r in out:
        r.pop("_relationship_guid")
    return out


def _md_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _md_table(columns: List[str], rows: List[Dict[str, Any]]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    lines += ["| " + " | ".join(_md_cell(r.get(c)) for c in columns) + " |" for r in rows]
    return "\n".join(lines)


def render_nodes_list(graph: Dict[str, Any]) -> str:
    """LIST: the nodes as a markdown table."""
    nodes = graph_nodes(graph)
    rows = [{label: n[key] for label, key in NODE_COLUMNS} for n in nodes]
    name = nodes[0]["display_name"] or nodes[0]["guid"]
    return f"### Asset Graph nodes: {name} ({len(nodes)})\n\n" + _md_table([c for c, _ in NODE_COLUMNS], rows) + "\n"


def render_report(graph: Dict[str, Any]) -> str:
    """REPORT/MD: the asset summary, its graph(s) and the edge table, as markdown."""
    from pyegeria.view.output_formatter import _format_mermaid_value

    asset = _node(graph)
    name = asset["display_name"] or asset["guid"]
    parts = [f"# Asset Graph: {name}", "", "## Asset", ""]
    summary = [(label, _dig(graph, path)) for label, path in _SUMMARY_FIELDS]
    parts.append(_md_table(["Property", "Value"],
                           [{"Property": label, "Value": value} for label, value in summary
                            if value not in (None, "")]))
    for title, key in _REPORT_GRAPHS:
        if graph.get(key):
            parts += ["", f"## {title}", "", _format_mermaid_value(graph[key])]
    edges = graph_edges(graph)
    parts += ["", f"## Relationships ({len(edges)})", ""]
    parts.append(_md_table([c for c, _ in EDGE_COLUMNS], edges) if edges else "No relationships.")
    return "\n".join(parts) + "\n"


def render(graph: Any, output_format: str) -> Any:
    """The shape for `output_format` (DICT, TABLE, LIST, REPORT, MD, HTML), or None when this module
    has no shape for it (the caller uses its generic path). A list of graphs is shaped one by one:
    rows concatenated, documents joined."""
    fmt = (output_format or "").upper()
    if fmt not in {"DICT", "TABLE", "LIST", "REPORT", "MD", "HTML"}:
        return None
    graphs = graph if isinstance(graph, list) else [graph]
    graphs = [g for g in graphs if isinstance(g, dict)]
    if fmt in {"DICT", "TABLE"}:
        return [row for g in graphs for row in graph_edges(g)]
    if fmt == "LIST":
        return "\n".join(render_nodes_list(g) for g in graphs)
    report = "\n".join(render_report(g) for g in graphs)
    if fmt == "HTML":
        from pyegeria.view.output_formatter import markdown_to_html
        return markdown_to_html(report)
    return report

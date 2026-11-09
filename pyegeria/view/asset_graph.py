"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Edges and nodes of an Egeria asset graph (the response of AssetCatalog.get_asset_graph_by_guid).

A helper kept for the planned Wave 3 edge-table spec (a processor stage that turns a graph into one
row per edge). No report spec uses it yet: `Asset-Graph` declares DICT and JSON for code and REPORT,
HTML and MERMAID for people (6.2.28).

How the response holds edges: `relationships` lists the edges among the asset and its anchored
elements, each with `startingElementGUID` (one end), `relatedElement` (the other end) and
`relatedElementAtEnd1` (which end that is). The asset's own relationships are keyed lists at the
top level (for example `governedBy`, `requestedActions`), each item a `relatedElement` with
`relatedElementAtEnd1`, the asset being the other end. An edge reported twice (the same
relationship GUID) is listed once, and rows are sorted, so the order never depends on Egeria's.

Pure functions: no I/O, no client.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

#: Edge row keys, in column order.
EDGE_COLUMNS: List[Tuple[str, str]] = [
    ("From Display Name", "from_display_name"),
    ("From Type", "from_type"),
    ("From GUID", "from_guid"),
    ("Relationship", "relationship_type"),
    ("To Display Name", "to_display_name"),
    ("To Type", "to_type"),
    ("To GUID", "to_guid"),
]

#: Node keys, in column order.
NODE_COLUMNS: List[Tuple[str, str]] = [
    ("Display Name", "display_name"),
    ("Type", "type_name"),
    ("GUID", "guid"),
    ("Role", "role"),
]

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

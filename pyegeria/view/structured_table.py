# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The structured TABLE result (R1, DESIGN-REPORT-SPEC-COMPLEX-VALUES-RENDERING-2026-11-11 §2.2).

`exec_report_spec(..., output_format="TABLE", table_shape="structured")` returns

    {"kind": "table",
     "columns": [{"key", "name", "type", "render", "detail_spec", "valid_values", "max_items", "max_lines"}],
     "rows": [{key: native value}],
     "total": int | None, "shown": int, "notes": [str]}

- Rows hold native values (lists, maps, related elements as {guid, qualifiedName, displayName, type},
  sub-rows for a detail_spec column), keyed by column key.
- A column's `type` is inferred from the values in it: scalar < text < list < map < elements < table.
  A column that mixes kinds takes the widest, and the notes say so.
- `render` is the column's own (R2), else the default for its type.
- Two levels only (§2.4): an object or list of objects inside a sub-row cell is reduced to
  {"count", "names", "guid"?}, with a note.
- `total` is the number of rows when the query did not fill its page; when it did, `total` is None and
  the notes say "more may exist" (Egeria's paging contract). It is never a bare N.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

TABLE_SHAPES = ("rows", "structured")
COLUMN_TYPES = ("scalar", "text", "list", "map", "elements", "table")
_WIDTH = {t: i for i, t in enumerate(COLUMN_TYPES)}
#: The render a column gets when its spec sets none (R2 makes it a spec field; this is the default).
DEFAULT_RENDER = {"scalar": "text", "text": "text", "list": "bullets", "map": "kv", "elements": "join",
                  "table": "subtable"}
#: Text longer than this, or with a line break, is "text" (clamped by renderers), not a short scalar.
_LONG_TEXT = 120


def check_table_shape(table_shape: Optional[str]) -> str:
    shape = table_shape or "rows"
    if shape not in TABLE_SHAPES:
        raise ValueError(f"table_shape must be one of {', '.join(TABLE_SHAPES)}, not {table_shape!r}")
    return shape


def _is_element(value: Any) -> bool:
    return isinstance(value, dict) and bool(value.get("guid") or value.get("qualifiedName"))


def value_type(value: Any) -> Optional[str]:
    """The type of one cell value, or None for an empty one."""
    if value in (None, "", [], {}):
        return None
    if isinstance(value, dict):
        return "elements" if _is_element(value) else "map"
    if isinstance(value, list):
        if all(isinstance(v, dict) for v in value):
            return "elements" if all(_is_element(v) for v in value) else "table"
        if any(isinstance(v, (dict, list)) for v in value):
            return "table"
        return "list"
    if isinstance(value, str) and (len(value) > _LONG_TEXT or "\n" in value):
        return "text"
    return "scalar"


def _names(items: List[Any]) -> List[str]:
    out = []
    for item in items:
        if isinstance(item, dict):
            name = (item.get("displayName") or item.get("name") or item.get("qualifiedName")
                    or item.get("Display Name") or item.get("Qualified Name"))
            out.append(str(name) if name else "(unnamed)")
        elif item not in (None, ""):
            out.append(str(item))
    return out


def reduce_third_level(value: Any) -> Dict[str, Any]:
    """An object (or list of objects) inside a sub-row cell, as {count, names, guid?} (§2.4)."""
    items = value if isinstance(value, list) else [value]
    reduced: Dict[str, Any] = {"count": len(items), "names": _names(items)}
    if len(items) == 1 and isinstance(items[0], dict) and items[0].get("guid"):
        reduced["guid"] = items[0]["guid"]
    return reduced


def _two_levels(rows: List[Dict[str, Any]], column_name: str, notes: List[str]) -> List[Dict[str, Any]]:
    out, reduced_keys = [], set()
    for row in rows:
        if not isinstance(row, dict):
            out.append(row)
            continue
        new_row = {}
        for k, v in row.items():
            if isinstance(v, dict) or (isinstance(v, list) and any(isinstance(i, (dict, list)) for i in v)):
                new_row[k] = reduce_third_level(v)
                reduced_keys.add(k)
            else:
                new_row[k] = v
        out.append(new_row)
    for k in sorted(reduced_keys):
        notes.append(f"{column_name}: '{k}' is a third level, shown as a count and names (a table shows two "
                     f"levels; use REPORT or a detail_spec drill-down for more).")
    return out


def _column_meta(attributes: List[Any]) -> List[Dict[str, Any]]:
    meta = []
    for col in attributes:
        col = col if isinstance(col, dict) else col.model_dump()
        meta.append({"key": col.get("key"), "name": col.get("name"), "detail_spec": col.get("detail_spec"),
                     "valid_values": col.get("valid_values"), "render": col.get("render"),
                     "max_items": col.get("max_items"), "max_lines": col.get("max_lines")})
    return meta


def build_structured_table(dict_rows: Any, attributes: List[Any], *, notes: Optional[List[str]] = None,
                           capped: bool = False) -> Dict[str, Any]:
    """The structured TABLE from native DICT rows (keyed by column display name, as DICT is) and the
    spec format's attributes. `capped` says the query filled its page (its words are in `notes`)."""
    notes = list(notes or [])
    rows_in = dict_rows if isinstance(dict_rows, list) else ([dict_rows] if isinstance(dict_rows, dict) else [])
    columns = _column_meta(attributes)
    # DICT rows are keyed by display name, a repeated name suffixed _1, _2 ... (generate_entity_dict)
    name_to_key: Dict[str, str] = {}
    for col in columns:
        name, n = col["name"], 1
        while name in name_to_key:
            name, n = f"{col['name']}_{n}", n + 1
        name_to_key[name] = col["key"]
    extra: List[Tuple[str, str]] = []  # columns the rows carry beyond the spec (e.g. companion graphs)
    rows: List[Dict[str, Any]] = []
    for row in rows_in:
        if not isinstance(row, dict):
            continue
        out = {}
        for name, value in row.items():
            key = name_to_key.get(name)
            if key is None:
                key = name
                if (name, name) not in extra:
                    extra.append((name, name))
            out[key] = value
        rows.append(out)
    columns += [{"key": k, "name": n, "detail_spec": None, "valid_values": None, "render": None,
                 "max_items": None, "max_lines": None} for k, n in extra]

    for col in columns:
        seen = []
        for row in rows:
            t = value_type(row.get(col["key"]))
            if t and t not in seen:
                seen.append(t)
        widest = max(seen, key=_WIDTH.get) if seen else "scalar"
        if len(seen) > 1 and not set(seen) <= {"scalar", "text"}:  # short and long strings are not a mix
            notes.append(f"{col['name']}: values are {', '.join(sorted(seen, key=_WIDTH.get))}; shown as {widest}.")
        col["type"] = widest
        if not col.get("render"):
            col["render"] = DEFAULT_RENDER[widest]
        if widest == "table":
            for row in rows:
                if isinstance(row.get(col["key"]), list):
                    row[col["key"]] = _two_levels(row[col["key"]], col["name"], notes)
    ordered = ["key", "name", "type", "render", "detail_spec", "valid_values", "max_items", "max_lines"]
    columns = [{k: c.get(k) for k in ordered} for c in columns]
    unique_notes = list(dict.fromkeys(notes))
    return {"kind": "table", "columns": columns, "rows": rows,
            "total": None if capped else len(rows), "shown": len(rows), "notes": unique_notes}

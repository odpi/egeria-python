# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Typed Egeria property bodies from Dr.Egeria dictionaries, and a sentence for every key that can't be sent.

Egeria's RelationshipProperties, ClassificationProperties and EntityProperties are polymorphic: a value
sent without a "class" is a 400 (InvalidTypeIdException) that loses the whole create, and a property the
named class doesn't declare is silently ignored. So a Dr.Egeria dictionary aimed at one of them
(Parent Relationship Attributes, Generic Initial Classifications, Initial Classifications, Template
Properties) goes through here:

- the class is `<TypeName>Properties` (or `<TypeName>ClassificationProperties`), checked against
  properties_class_fields (generated from Egeria's Java source) for the expected kind;
- each key the class reads is sent; every other key is left out and reported as
  "not applied: <attribute>: <key> isn't a property of <TypeName>".

Each function returns (value_to_send_or_None, notes); callers add the notes to the command's warnings.
"""
from __future__ import annotations

import json
from typing import Any

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS

_ALWAYS_IGNORED = {"class", "typeName"}


def properties_class(kind: str, type_name: str | None) -> str | None:
    """The Egeria properties class of `kind` for a type name, or None."""
    if not type_name:
        return None
    name = str(type_name).strip().replace(" ", "")
    for candidate in (name if name.endswith("Properties") else f"{name}Properties", f"{name}ClassificationProperties"):
        found = PROPERTIES_CLASS_FIELDS.get(candidate)
        if found and found[0] == kind:
            return candidate
    return None


def _as_dict(value: Any) -> dict | None:
    if value in (None, "", {}):
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def typed_properties(kind: str, type_name: str | None, values: dict, attribute: str) -> tuple[dict | None, list[str]]:
    """{"class": <TypeName>Properties, <only keys that class reads>} plus a note per key left out."""
    notes: list[str] = []
    cls = properties_class(kind, type_name)
    if cls is None:
        notes.append(f"not applied: {attribute}: {type_name or '(no type)'} has no {kind} properties in Egeria"
                     + (f" ({', '.join(sorted(values))})" if values else ""))
        return None, notes
    fields = PROPERTIES_CLASS_FIELDS[cls][1]
    body = {"class": cls}
    for key, value in values.items():
        if key in _ALWAYS_IGNORED:
            continue
        if key in fields:
            body[key] = value
        else:
            notes.append(f"not applied: {attribute}: {key} isn't a property of {type_name}")
    return body, notes


def parent_relationship_properties(attributes: dict, attribute: str = "Parent Relationship Attributes",
                                   type_attribute: str = "Parent Relationship Type Name") -> tuple[dict | None, list[str]]:
    """The NewElementRequestBody/TemplateRequestBody `parentRelationshipProperties`, typed by the parent
    relationship type."""
    raw = (attributes.get(attribute) or {}).get("value")
    if raw in (None, "", {}) and attribute == "Parent Relationship Attributes":
        attribute = "Parent Relationship Properties"
        raw = (attributes.get(attribute) or {}).get("value")
    if raw in (None, "", {}):
        return None, []
    values = _as_dict(raw)
    if values is None:
        return None, [f"not applied: {attribute}: expected a dictionary of relationship properties, got {raw!r}"]
    rel_type = ((attributes.get(type_attribute) or {}).get("value")
                or (attributes.get("Parent Relationship Type") or {}).get("value"))
    if not rel_type:
        return None, [f"not applied: {attribute}: it needs a {type_attribute} to say which relationship "
                      f"properties these are ({', '.join(sorted(values))})"]
    body, notes = typed_properties("relationship", rel_type, values, attribute)
    if body is not None and len(body) == 1:  # only "class": nothing the relationship reads
        return None, notes
    return body, notes


def classification_map(raw: Any, attribute: str) -> tuple[dict | None, list[str]]:
    """`initialClassifications` / `replacementClassifications`: {ClassificationName: {"class": ..., props}}.

    The Dr.Egeria value is a dictionary of classification name -> dictionary of its properties (or
    empty for a classification with no properties)."""
    if raw in (None, "", {}):
        return None, []
    values = _as_dict(raw)
    if values is None:
        return None, [f"not applied: {attribute}: expected a dictionary of classification name -> properties, "
                      f"got {raw!r}"]
    out, notes = {}, []
    for name, props in values.items():
        props_dict = {} if props in (None, "", {}) else _as_dict(props)
        if props_dict is None:
            notes.append(f"not applied: {attribute}: {name} needs a dictionary of its properties, got {props!r}")
            continue
        body, more = typed_properties("classification", name, props_dict, f"{attribute}: {name}")
        notes += [n.replace(f"not applied: {attribute}: {name}: ", f"not applied: {attribute}: ")
                  .replace(f"{name} has no classification properties in Egeria",
                           f"{name} isn't an Egeria classification") for n in more]
        if body is not None:
            out[name] = body
    return (out or None), notes


def entity_properties(type_name: str | None, raw: Any, attribute: str) -> tuple[dict | None, list[str]]:
    """Typed entity properties (e.g. a template's `replacementProperties`) for a known element type."""
    if raw in (None, "", {}):
        return None, []
    values = _as_dict(raw)
    if values is None:
        return None, [f"not applied: {attribute}: expected a dictionary of properties, got {raw!r}"]
    if not type_name:
        return None, [f"not applied: {attribute}: the element type isn't known, so its properties can't be "
                      f"checked ({', '.join(sorted(values))})"]
    body, notes = typed_properties("entity", type_name, values, attribute)
    if body is not None and len(body) == 1:
        return None, notes
    return body, notes


def long_value(attributes: dict, attribute: str) -> tuple[int | None, list[str]]:
    """An attribute Egeria stores as a Java Long: integral input becomes an int; anything else is refused
    with a sentence (and not sent)."""
    raw = (attributes.get(attribute) or {}).get("value")
    if raw in (None, ""):
        return None, []
    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None, [f"not applied: {attribute}: {raw!r} isn't a number"]
    if not number.is_integer():
        return None, [f"not applied: {attribute}: {raw!r} isn't a whole number; Egeria stores it as an integer"]
    return int(number), []


def record_not_applied(attributes: dict, attribute: str, notes: list[str]) -> None:
    """Keep each note on the attribute it is about (attributes[attribute]["not_applied"]); the command
    processor reports them all as warnings, so a body builder needs no access to the processor."""
    if not notes:
        return
    entry = attributes.get(attribute)
    if not isinstance(entry, dict):
        entry = attributes.setdefault(attribute, {"value": None})
        if not isinstance(entry, dict):
            return
    held = entry.setdefault("not_applied", [])
    held.extend(n for n in notes if n not in held)


def not_applied_notes(attributes: dict) -> list[str]:
    """Every not-applied note recorded on a command's attributes, in attribute order."""
    out: list[str] = []
    for entry in (attributes or {}).values():
        if isinstance(entry, dict):
            out.extend(n for n in entry.get("not_applied") or [] if n not in out)
    return out


_PRIMITIVES = {bool: ("boolean", "OM_PRIMITIVE_TYPE_BOOLEAN"), int: ("int", "OM_PRIMITIVE_TYPE_INT"),
               float: ("double", "OM_PRIMITIVE_TYPE_DOUBLE")}


def new_element_properties(typed: dict | None) -> dict | None:
    """A typed properties body as the OMF `NewElementProperties` property-value map, the shape the
    metadata-expert `related-elements` endpoint reads (frameworkservices/omf/rest/
    NewRelatedElementsRequestBody.properties is a NewElementProperties, not a RelationshipProperties)."""
    if not typed:
        return None
    values = {}
    for key, value in typed.items():
        if key in _ALWAYS_IGNORED or value is None:
            continue
        type_name, category = _PRIMITIVES.get(type(value), ("string", "OM_PRIMITIVE_TYPE_STRING"))
        values[key] = {"class": "PrimitiveTypePropertyValue", "typeName": type_name,
                       "primitiveTypeCategory": category,
                       "primitiveValue": value if type_name != "string" else str(value)}
    return {"class": "NewElementProperties", "propertyValueMap": values} if values else None

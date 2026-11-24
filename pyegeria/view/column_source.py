# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-53: a report-spec column that shows related information, through `Column.source`.

One string, three forms:

    class:<Classification>[,<Classification>...][.<property>]
        A classification of the element, matched by its type name (`classificationName`), or the name of any
        subtype of it (PolicyManagementPoint also takes a PolicyEnforcementPoint), wherever it sits in
        elementHeader: the `classifications` list, a named slot such as `zoneMembership`, or
        `otherClassifications`. Without a property the value is the names of ALL the listed classifications
        the element has, joined. With a property it is that property of the classification (one name only).
    rel:<end>.<property>
        A property of the relationship at each related element of the end `<end>` (a name from
        RELATIONSHIP_FIELDS, e.g. `projectTargets`). Read from a flat bean or a propertyValueMap.
    of:<end>.<attribute>
        An attribute of each related element at that end.

Results: `rel:` and `of:` are lists aligned with the element's related elements of that end, a "" where one
has no value, so two columns of the same end line up by position. The text value (TABLE, MD) keeps every
position too, joined with ", " and a "\u2014" for a blank slot ("" when every slot is blank); the native value
(DICT, JSON) is the list with "" placeholders. Absent is "", never "None".
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, List, Optional, Tuple

#: The text of a blank slot among filled ones in a `rel:` or `of:` column, so two columns of one end keep
#: their positions in TABLE and MD. A column with every slot blank is "".
BLANK_SLOT = "\u2014"

_NAME = r"[A-Za-z][A-Za-z0-9_]*"
_CLASS_RE = re.compile(rf"^class:({_NAME}(?:,{_NAME})*)(?:\.({_NAME}))?$")
_END_RE = re.compile(rf"^(rel|of):({_NAME})\.({_NAME})$")


class SourceError(ValueError):
    """A `source` string the grammar or the 6.4 type tables do not accept."""


@dataclass(frozen=True)
class Source:
    kind: str                      # "class", "rel" or "of"
    names: Tuple[str, ...]         # classification names (class) or the one end name (rel, of)
    prop: Optional[str] = None     # property / attribute name, camelCase as written


def parse_source(text: str) -> Source:
    """The parsed `source`, or SourceError with the words to show."""
    if not isinstance(text, str) or not text.strip():
        raise SourceError("a column's source is empty")
    text = text.strip()
    m = _CLASS_RE.match(text)
    if m:
        return Source("class", tuple(m.group(1).split(",")), m.group(2))
    m = _END_RE.match(text)
    if m:
        return Source(m.group(1), (m.group(2),), m.group(3))
    raise SourceError(f"source {text!r} is not class:<A[,B]>[.<property>], rel:<end>.<property> or "
                      f"of:<end>.<attribute>")


def _snake(camel: str) -> str:
    out = []
    for ch in camel:
        out.append("_" + ch.lower() if ch.isupper() else ch)
    return "".join(out).lstrip("_")


def _fields(type_name: str, kind: str) -> Optional[set]:
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    entry = PROPERTIES_CLASS_FIELDS.get(f"{type_name}Properties")
    if not entry or entry[0] != kind:
        return None
    return {_snake(f) for f in entry[1]}


def _end_entity_types() -> dict:
    """{relationship list (end attribute) name: the entity type(s) at that end}, from the 6.4 typedefs."""
    from md_processing.md_processing_utils.properties_class_fields import END_ENTITY_TYPES
    return END_ENTITY_TYPES


def _entity_supertypes() -> dict:
    from md_processing.md_processing_utils.properties_class_fields import ENTITY_SUPERTYPES
    return ENTITY_SUPERTYPES


_UNIVERSAL_ATTRIBUTES = {"guid", "type", "status", "name", "origin"}


def _union_has(wanted: str) -> bool:
    """The PY-53 check: some entity type has the attribute (catches a typo, not a wrong end)."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    return wanted in _UNIVERSAL_ATTRIBUTES or any(
        wanted in {_snake(f) for f in fields}
        for kind, fields in PROPERTIES_CLASS_FIELDS.values() if kind == "entity")


def _type_attributes(type_name: str) -> Optional[set]:
    """The snake_case attributes of an entity type, its typedef supertypes included, or None if none is known."""
    found, known = set(), False
    for t in (type_name, *_entity_supertypes().get(type_name, ())):
        fields = _fields(t, "entity")
        if fields is not None:
            known = True
            found |= fields
    return found if known else None


def check_source_with_warnings(text: str) -> Tuple[List[str], List[str]]:
    """(errors, warnings) for a `source`. Classification and relationship names and their properties are checked
    against the 6.4 Properties-class tables. An `of:` attribute is checked against the entity type(s) at that
    relationship end and their supertypes (the typedefs, PY-61); where the end's type is not in the tables it is
    checked against the union of all entity types and a warning says so, never silently."""
    try:
        src = parse_source(text)
    except SourceError as exc:
        return [str(exc)], []
    from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS
    if src.kind != "of":
        return check_source_core(text, src), []
    end = src.names[0]
    rel_types = RELATIONSHIP_FIELDS.get(end)
    if rel_types is None:
        return [f"source {text!r}: {end!r} is not a relationship list an Egeria element carries "
                f"(RELATIONSHIP_FIELDS)."], []
    wanted = _snake(src.prop)
    types = _end_entity_types().get(end)
    attrs_by_type = {t: _type_attributes(t) for t in types} if types else {}
    if not types or any(a is None for a in attrs_by_type.values()):
        unknown = ", ".join(t for t, a in attrs_by_type.items() if a is None) or "unknown"
        warning = (f"source {text!r}: the entity type at the {end!r} end ({unknown}) is not in the 6.4 tables, so "
                   f"{src.prop!r} was checked against the union of all entity types, which cannot tell a wrong end.")
        errors = [] if _union_has(wanted) else [f"source {text!r}: no Egeria entity type has the attribute {src.prop!r}."]
        return errors, [warning]
    if wanted in _UNIVERSAL_ATTRIBUTES or any(wanted in attrs for attrs in attrs_by_type.values()):
        return [], []
    held = " / ".join(f"{t} (with its supertypes {', '.join(_entity_supertypes().get(t, ())) or 'none'})"
                      for t in types)
    rel = " / ".join(rel_types) if rel_types else "?"
    return [f"source {text!r}: the {end!r} end of relationship {rel} holds {held}, which has no attribute "
            f"{src.prop!r}."], []


def check_source(text: str) -> List[str]:
    """Why a `source` is wrong, as validator error messages ([] when it is right). See check_source_with_warnings,
    which also gives the warnings."""
    return check_source_with_warnings(text)[0]


def check_source_core(text: str, src: Source) -> List[str]:
    """The class: and rel: checks (an `of:` source goes through check_source_with_warnings)."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS
    errors: List[str] = []
    if src.kind == "class":
        if src.prop and len(src.names) > 1:
            return [f"source {text!r}: a named property allows only one classification (class:A.prop), not "
                    f"{len(src.names)}; the values could not be told apart."]
        for name in src.names:
            fields = _fields(name, "classification")
            if fields is None:
                errors.append(f"source {text!r}: {name!r} is not a classification in the Egeria 6.4 type tables "
                              f"(no {name}Properties of kind classification).")
            elif src.prop and _snake(src.prop) not in fields:
                errors.append(f"source {text!r}: classification {name} has no property {src.prop!r}.")
        return errors
    end = src.names[0]
    rel_types = RELATIONSHIP_FIELDS.get(end)
    if rel_types is None:
        return [f"source {text!r}: {end!r} is not a relationship list an Egeria element carries "
                f"(RELATIONSHIP_FIELDS)."]
    if not rel_types:
        return [f"source {text!r}: the end {end!r} names no relationship type, so {src.prop!r} cannot be checked."]
    tables = [_fields(t, "relationship") for t in rel_types]
    if not any(t is not None and _snake(src.prop) in t for t in tables):
        errors.append(f"source {text!r}: relationship {' / '.join(rel_types)} has no property {src.prop!r}.")
    return errors


# ── resolving a source against an element ──

def _classification_dicts(header: Any) -> Iterable[dict]:
    """Every classification in an element header, wherever it sits: the `classifications` list, a named slot
    (a dict that has a classificationName), or a list of them (`otherClassifications`)."""
    if not isinstance(header, dict):
        return
    for value in header.values():
        if isinstance(value, dict) and value.get("classificationName"):
            yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and item.get("classificationName"):
                    yield item


#: Egeria 6.4 level enums behind the governance classifications, by (classification, property): integer -> name.
#: ConfidentialityLevel, ConfidenceLevel, CriticalityLevel, SeverityLevel (Impact has no enum of its own) and
#: RetentionBasis, in open-metadata-framework refdata (read from the laz checkout 8de9572c4d).
LEVEL_NAMES = {
    ("Confidentiality", "confidentialityLevel"): {0: "Unclassified", 1: "Internal", 2: "Confidential",
                                                  3: "Sensitive", 4: "Restricted", 99: "Other"},
    ("Confidence", "confidenceLevel"): {0: "Unclassified", 1: "Ad Hoc", 2: "Transactional", 3: "Authoritative",
                                        4: "Derived", 5: "Obsolete", 99: "Other"},
    ("Criticality", "criticalityLevel"): {0: "Unclassified", 1: "Marginal", 2: "Important", 3: "Critical",
                                          4: "Catastrophic", 99: "Other"},
    ("Impact", "severityLevel"): {0: "Unclassified", 1: "Low", 2: "Medium", 3: "High", 99: "Other"},
    ("Retention", "retentionBasis"): {0: "Unclassified", 1: "Temporary", 2: "Project Lifetime", 3: "Team Lifetime",
                                      4: "Contract Lifetime", 5: "Regulated Lifetime", 6: "Time Boxed Lifetime",
                                      99: "Other"},
}


def _as_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def level_name(cls: str, prop: str, value: Any) -> str:
    """The level name of a governance-level integer; a number outside the enum reads "<n> (unknown level)";
    a missing value stays ""; anything that is not an integer is shown as it is."""
    if value in (None, ""):
        return ""
    number = _as_int(value)
    if number is None:
        return _text(value)
    return LEVEL_NAMES[(cls, prop)].get(number, f"{number} (unknown level)")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value if v not in (None, ""))
    return str(value)


def _prop_value(bean: Any, name: str) -> Any:
    """A property of a flat bean or of a propertyValueMap ({name: {"propertyValue": v}}), "" if absent."""
    if not isinstance(bean, dict):
        return ""
    value = bean.get(name)
    if value is None and isinstance(bean.get("propertyValueMap"), dict):
        value = bean["propertyValueMap"].get(name)
    if value is None and isinstance(bean.get("extendedProperties"), dict):
        value = bean["extendedProperties"].get(name)
    if isinstance(value, dict) and "propertyValue" in value:
        value = value["propertyValue"]
    elif isinstance(value, dict) and "primitiveValue" in value:
        value = value["primitiveValue"]
    return "" if value is None else value


def _related_items(element: dict, end: str) -> List[dict]:
    items = element.get(end)
    if isinstance(items, dict):
        items = [items]
    return [i for i in items if isinstance(i, dict)] if isinstance(items, list) else []


def _matching_classifications(found: dict, wanted: Iterable[str]) -> List[str]:
    """The names in `found` (the element's classifications) that a `class:` source asks for: each wanted name
    itself, then any classification that has it as a supertype (PY-59: `class:PolicyManagementPoint` also takes a
    PolicyEnforcementPoint). Each once, in the order asked."""
    from md_processing.md_processing_utils.properties_class_fields import CLASSIFICATION_SUPERTYPES
    out: List[str] = []
    for want in wanted:
        for name in found:
            if name not in out and (name == want or want in CLASSIFICATION_SUPERTYPES.get(name, ())):
                out.append(name)
    return out


def resolve_source(element: dict, text: str) -> Tuple[Any, str]:
    """(native, text) of a column's `source` for one element. Native is a string for a classification
    property or a bare class list, and a list aligned with the related elements for `rel:` and `of:`."""
    src = parse_source(text)
    if not isinstance(element, dict):
        return ("" if src.kind == "class" else []), ""
    if src.kind == "class":
        found = {}
        for cls in _classification_dicts(element.get("elementHeader")):
            found.setdefault(cls["classificationName"], cls)
        present = _matching_classifications(found, src.names)
        if src.prop is None:
            joined = ", ".join(present)
            return joined, joined
        raw = [_prop_value(found[n].get("classificationProperties") or {}, src.prop) for n in present]
        if len(present) == 1 and (present[0], src.prop) in LEVEL_NAMES:   # the five level classes have no subtypes
            number = _as_int(raw[0])
            label = level_name(present[0], src.prop, raw[0])
            return (number if number is not None else label), label
        joined = ", ".join(v for v in (_text(r) for r in raw) if v)
        return joined, joined
    items = _related_items(element, src.names[0])
    native: List[Any] = []
    for item in items:
        if src.kind == "rel":
            native.append(_prop_value(item.get("relationshipProperties") or item.get("relationship") or {}, src.prop))
        else:
            related = item.get("relatedElement") if isinstance(item.get("relatedElement"), dict) else item
            native.append(_prop_value(related.get("properties") or related, src.prop))
    cells = [_text(v) for v in native]
    return native, (", ".join(c or BLANK_SLOT for c in cells) if any(cells) else "")

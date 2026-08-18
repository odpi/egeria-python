# Reference Data vs. Valid Metadata — the 3 "Create Valid Value" flavors, and Consistent/Specification Property mechanisms

**Status: findings notes, written 2026-08-14 while designing Resource
Explorer's "measure definitions" (externalizing what data/interpretation
answers a Question, grounded in real standards like OpenSSF Scorecard) —
see `packages/resource-explorer/docs/survey-question-context-plan.md` in
the Trellis checkout for the consuming use case. Written here because the
findings are about pyegeria/Egeria itself, not Resource Explorer.**

There are two *different* mechanisms in pyegeria that both create
"valid value"-shaped things, backed by two different Egeria OMVSes
(`reference-data` vs. `valid-metadata`), plus two more specific
relationship-style operations that are easy to conflate with the missing
`SpecificationPropertyAssignment`/`ReferenceValueAssignment` gap noted in
the Trellis doc above. Documented here so the distinction doesn't get lost
before the pending pyegeria work (adding a `ValidValuesAssignment` /
`ReferenceValueAssignment` method, fixing `link_valid_value_definition()`)
gets picked up.

## The 3 flavors of "Create Valid Value"

### 1. `ReferenceDataManager.create_valid_value_definition(body)`

Creates a **first-class, standalone `ValidValueDefinition` entity** —
real domain reference data (e.g. country codes, our own repo-maintenance-
activity tiers). It has its own GUID, can be searched, can have
relationships (`ValidValueMember`, `ExternalReferenceLink`, etc.), and is
what https://egeria-project.org/types/5/0545-Reference-Data/ documents as
`ValidValueDefinition`/`ReferenceDataSet`/`ReferenceDataValue`.

```python
body = {
    "class": "NewElementRequestBody",
    "isOwnAnchor": True,
    "properties": {
        "class": "ValidValueDefinitionProperties",
        "qualifiedName": "...", "displayName": "...", "description": "...",
        "namespacePath": "...", "usage": "...", "dataType": "...",
        "scope": "...", "preferredValue": "...", "isCaseSensitive": False,
    },
}
guid = client.create_valid_value_definition(body)
```

This is the one to use when the valid value is a real, business-meaningful
piece of domain reference data that should itself be catalogable, citable
(via `ExternalReferenceLink`), and organizable into sets.

### 2. `ReferenceDataManager.create_valid_value_definition_from_template(body)`

Same entity type as #1, but instantiated from an existing
`ValidValueDefinition` used as a template (`TemplateRequestBody` — template
GUID + property overrides). Not otherwise different in kind from #1; just
a different creation path when a similar value already exists to clone
from.

### 3. `ValidMetadataManager.setup_valid_metadata_value(property_name, type_name, body)`

**A completely different mechanism** — this does *not* create a
standalone entity at all. It registers what values are **valid for a
specific open-metadata TYPE's PROPERTY**, i.e. it's Egeria's own type-
system extensibility feature (this is what backs `TechnologyType`, a
`ValidMetadataValue` specialization for `deployedImplementationType`
values). Keyed by `(property_name, type_name)`, stored as metadata *about
the property itself*, not as a separately GUID-addressable thing you'd
link other elements to. Sibling methods: `setup_valid_metadata_map_name` /
`setup_valid_metadata_map_value` for map-shaped properties (name→value
pairs), `clear_valid_metadata_value` / `clear_valid_metadata_map_name` /
`clear_valid_metadata_map_value` to remove, `validate_metadata_value` /
`validate_metadata_map_name` / `validate_metadata_map_value` to check
whether a value is currently valid, `get_valid_metadata_value(s)` /
`get_valid_metadata_map_name` / `get_valid_metadata_map_value` to read.

```python
body = {
    "displayName": "", "description": "", "preferredValue": "",
    "dataType": "", "isCaseSensitive": False, "isDeprecated": False,
    "additionalProperties": {"colour": "purple"},
}
client.setup_valid_metadata_value(property_name="deployedImplementationType",
                                   type_name="SoftwareServer", body=body)
```

**Use #1/#2 when the value needs to be its own catalogable, linkable,
citable metadata element** (our measure-definition use case). **Use #3
when you're constraining what a specific open-metadata property can
legally hold** — a type-system-level concern, not a domain-reference-data
one.

## `set_consistent_metadata_values` — the file-type/file-suffix example

`ValidMetadataManager.set_consistent_metadata_values(property_name1,
type_name1, map_name1, preferred_value1, property_name2, type_name2,
map_name2, preferred_value2)` is real and dedicated — backs the
`ConsistentValidValues` relationship from the Reference Data types page.
It cross-references two **`ValidMetadataValue`** entries (flavor #3 above,
not flavor #1's `ValidValueDefinition`) as required to co-occur — e.g.
"file type = Python Source" (`property_name="fileType"`) should be
consistent with "file suffix = .py" (`property_name="fileExtension"`).
Both values must already exist via `setup_valid_metadata_value`/
`setup_valid_metadata_map_value` before linking them consistent — this
operates entirely within the type-property system (#3), not on standalone
`ValidValueDefinition` elements (#1/#2). `get_consistent_metadata_values`
is the read side.

**Practical implication**: if Resource Explorer (or anything else) ever
wants "these two properties' values must agree" validation — e.g. file
classification's type/suffix pairing — this is the real, already-built
mechanism, and it's a type-property-level concern (flavor #3), not
something to route through `ValidValueDefinition`/`ValidValueMember`.

## Correction: `SpecificationPropertyAssignment`-shaped functionality
**does** have a dedicated method — just not one matching that literal name,
and it may not fit our use case

Confirmed via `ValidMetadataManager`: `setup_specification_property(
element_guid, body)` / `delete_specification_property(...)` /
`find_specification_property(...)` / `get_specification_property_by_type`
/ `_by_name` / `_by_guid` / `get_specification_property_types` — a real,
dedicated CRUD set. This attaches a "specification property" to an
element, with two documented payload shapes:

```python
# ReplacementAttribute — a customizable attribute a template exposes
{
  "class": "ReplacementAttribute",
  "name": "...", "description": "...", "datatype": "...",
  "example": "...", "required": False,
  "otherPropertyValues": {"property1": "propertyValue1"},
}

# SupportedTemplate — declares what open-metadata type a template produces
{
  "class": "SupportedTemplate",
  "name": "...", "description": "...",
  "openMetadataTypeName": "...", "required": False,
  "otherPropertyValues": {"property1": "propertyValue1"},
}
```

Both documented shapes are specifically about **template/connector
configuration** (what a template can be customized with, what type a
template instantiates) — not the generic "attach an interpretation
`ValidValueDefinition` to an arbitrary Annotation Type's property" shape
the Trellis measure-definitions work actually needs. **This needs a live
check before assuming it covers our case** — worth confirming against a
real server whether `setup_specification_property` accepts other
`class` values beyond the two documented ones, or whether the still-
missing `SpecificationPropertyAssignment` relationship (per the Reference
Data types page) is a genuinely separate thing pyegeria doesn't expose
yet. Flagging this now specifically so it doesn't get assumed-solved and
skipped when the pending pyegeria work happens.

## Summary table

| Mechanism | Entity created? | Keyed by | pyegeria class | Real/dedicated? |
|---|---|---|---|---|
| `create_valid_value_definition` | Yes — standalone `ValidValueDefinition` | qualifiedName | `ReferenceDataManager` | ✅ |
| `create_valid_value_definition_from_template` | Yes — same, from template | qualifiedName | `ReferenceDataManager` | ✅ |
| `setup_valid_metadata_value` | No — property-level metadata | `(property_name, type_name)` | `ValidMetadataManager` | ✅ |
| `set_consistent_metadata_values` | No — relates two property-level values | `(property_name, type_name)` pairs | `ValidMetadataManager` | ✅ |
| `setup_specification_property` | Attaches to an existing element | `element_guid` + `class` (2 known shapes) | `ValidMetadataManager` | ✅ for template use cases; unconfirmed for general use |
| `link_valid_value_definition` (ValidValueMember) | Relates two `ValidValueDefinition`s | vv_set_guid + vv_member_guid | `ReferenceDataManager` | ⚠️ documented body fails client-side validation — real bug, see Trellis doc |
| `ValidValuesAssignment` (Question → measure set) | — | — | — | ❌ no dedicated method yet |
| `ReferenceValueAssignment` (tag a result) | — | — | — | ❌ no dedicated method yet |

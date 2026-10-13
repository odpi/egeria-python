# Reference Data and Valid Metadata

Egeria has two separate mechanisms for "allowed values". They are served by
different view services, wrapped by different pyegeria clients, and authored
by different Dr.Egeria families. Both store their values as subtypes of
`ValidValueDefinition`, which is why the generic phrase "valid values" causes
confusion. This guide uses two specific terms:

| | **Reference data** | **Valid metadata values** |
|---|---|---|
| What it governs | Your business value lists: order statuses, country codes, contact types | The allowed values of Egeria's own properties, e.g. `fileType`, `deployedImplementationType`, `projectHealth` on `Project` |
| Egeria view service | Reference Data (`/api/open-metadata/reference-data`) | Valid Metadata (`/api/open-metadata/valid-metadata`) |
| pyegeria client | `ReferenceDataManager` (`pyegeria/omvs/reference_data.py`) | `ValidMetadataManager` (`pyegeria/omvs/valid_metadata.py`) |
| Dr.Egeria family | Reference Data | Valid Metadata |
| Stored as | `ReferenceDataSet` and `ReferenceDataValue` elements | `ValidMetadataValue` elements, built by the server |
| How a value is identified | Its own qualified name and GUID | The property name, plus optional type name and map name |
| How values are grouped | `ReferenceDataSet` → `ValidValueMember` → `ReferenceDataValue` | Implicitly, per (property, type) |

Use **reference data** when the value is a business-meaningful thing that
should be catalogued, cited, linked and organised into sets. Use **valid
metadata values** when you are constraining what an open metadata property
may hold. Dr.Egeria validates its own "Valid Value"-style attributes against
this registry, so a new valid metadata value is accepted by Dr.Egeria
straight away.

Behaviour described as "verified" below was checked against a live
qs-view-server on 2026-10-13.

---

## Reference data

### Types

All of these are in Egeria's model 0545:

- `ValidValueDefinition` — the base type. Properties: `preferredValue`,
  `dataType`, `usage`, `scope`, `namespacePath`, `isCaseSensitive`, `ordinal`,
  plus `contentStatus` from `AuthoredReferenceable`.
- `ReferenceDataValue` — a single business value. Subtype of
  `ValidValueDefinition`.
- `ReferenceDataSet` — a named list of values. Subtype of `ReferenceDataValue`.
- `ValidMetadataValue` and `SpecificationPropertyValue` are the other
  `ValidValueDefinition` subtypes. They belong to the Valid Metadata side.

`ValidValueSet` is a 5.x name. It is not a 6.x type.

Relationships, with the properties each carries:

| Relationship | Ends | Properties |
|---|---|---|
| `ValidValueMember` | set (end 1) → member (end 2) | `isDefaultValue`, `ordinal` |
| `ValidValuesAssignment` | element → set | `strictRequirement` |
| `ReferenceValueAssignment` | element → value | `attributeName`, `confidence`, `steward`, `stewardTypeName`, `stewardPropertyName`, `notes` |
| `ValidValueAssociation` | value ↔ value | `associationName`, `associationType`, `additionalProperties` |
| `ConsistentValidValues` | value ↔ value | none |
| `ValidValuesMapping` | value ↔ value | `associationDescription`, `confidence`, `steward*`, `notes` |
| `ValidValuesImplementation` | value → implementing element | `symbolicName`, `implementationValue`, `additionalValues` |

### Create sets and values as the subtypes, not plain definitions

Pass `ReferenceDataSetProperties` or `ReferenceDataValueProperties` as the
properties class. `create_valid_value_definition` creates exactly that subtype
(verified).

**Do not create plain `ValidValueDefinition`s for business data.** The
Reference Data view service builds its handler with a default type of
`ReferenceDataValue` (Egeria `ReferenceDataInstance.java:65-69`). So
`find_valid_value_definitions` and `get_valid_value_definitions_by_name`
without `metadata_element_type` do not return plain `ValidValueDefinition`
elements (verified). If you must read them, pass
`metadata_element_type="ValidValueDefinition"`. Note that this also sweeps in
every `ValidMetadataValue` on the server, which is several hundred.

Egeria's own Coco Pharmaceuticals content follows this shape. For example,
`ReferenceDataSet::ContactType` has 8 `ReferenceDataValue` members, each linked
with `isDefaultValue` and `ordinal`.

```python
from pyegeria import EgeriaTech

client = EgeriaTech("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
client.create_egeria_bearer_token("erinoverview", "secret")

set_guid = client.create_valid_value_definition({
    "class": "NewElementRequestBody", "isOwnAnchor": True,
    "properties": {"class": "ReferenceDataSetProperties",
                   "qualifiedName": "ReferenceDataSet::OrderStatus", "displayName": "Order Status",
                   "contentStatus": "DRAFT"}})
value_guid = client.create_valid_value_definition({
    "class": "NewElementRequestBody", "isOwnAnchor": True,
    "properties": {"class": "ReferenceDataValueProperties",
                   "qualifiedName": "ReferenceDataSet::OrderStatus::PENDING", "displayName": "Pending",
                   "preferredValue": "PENDING"}})
client.link_valid_value_definition(set_guid, value_guid, {   # ValidValueMember
    "class": "NewRelationshipRequestBody",
    "properties": {"class": "ValidValueMemberProperties", "isDefaultValue": True, "ordinal": 1}})
```

### Behaviour worth knowing

- **Re-linking is an upsert.** Linking the same set and member again updates
  the existing `ValidValueMember` (e.g. a new `ordinal`) rather than adding a
  second one (verified). Re-running a script or document is safe.
- **Listing a set's members:** the Reference Data service has no "members"
  call. Use
  `get_related_metadata_elements(set_guid, "ValidValueMember", {"class": "ResultsRequestBody"}, starting_at_end=1)`.
  Each item's `element` is the member, and `relationshipProperties.propertiesAsStrings`
  holds `isDefaultValue` and `ordinal`.
- **Updates:** `update_valid_value_definition` with `"mergeUpdate": True`
  changes only the properties you send (verified).
- **Deletes:** `delete_valid_value_definition` by GUID. Cascade does not reach
  the server today (ISSUE-132), so delete members you no longer need
  explicitly.
- **The sync wrapper name:** `link_valid_value_definition` /
  `detach_valid_value_definition` are the sync wrappers for the member link
  (`_async_link_valid_value_member`).

### pyegeria methods (`ReferenceDataManager`)

| Operation | Method |
|---|---|
| Create, from template, update, delete | `create_valid_value_definition`, `create_valid_value_definition_from_template`, `update_valid_value_definition`, `delete_valid_value_definition` |
| Find, by name, by GUID | `find_valid_value_definitions`, `get_valid_value_definitions_by_name`, `get_valid_value_definition_by_guid` |
| Member | `link_valid_value_definition` / `detach_valid_value_definition` |
| Assign a set to an element | `link_valid_values_assignment` / `detach_valid_values_assignment` |
| Tag an element with a value | `link_reference_value_assignment` / `detach_reference_value_assignment` |
| Associated, consistent, mapped | `link_associated_valid_values`, `link_consistent_valid_values`, `link_mapped_valid_values` (and `detach_*`) |
| Implementation | `link_valid_value_implementation` / `detach_valid_value_implementation`, `update_valid_value_implementation`, `detach_valid_value_implementation_by_id` |

### Dr.Egeria: the Reference Data family

| Command | Does |
|---|---|
| `Create Reference Data Set` | Creates or updates a `ReferenceDataSet`, and its members (see below) |
| `Create Reference Data Value` | Creates or updates a `ReferenceDataValue`; `In Reference Data Set` adds it to a set, with `Is Default Member` and `Member Ordinal` |
| `Link`/`Detach Valid Value Member` | `ValidValueMember` (`Valid Value Set`, `Member Value`) |
| `Link`/`Detach Consistent Valid Values` | `ConsistentValidValues` (`Valid Value 1`, `Valid Value 2`) |
| `Link`/`Detach Associated Valid Values` | `ValidValueAssociation` |
| `Link`/`Detach Mapped Valid Values` | `ValidValuesMapping` |
| `Link`/`Detach Valid Value Implementation` | `ValidValuesImplementation` (`Valid Value`, `Implementation Element`) |
| `Link`/`Detach Element to Valid Values` | `ValidValuesAssignment`, with `Strict Requirement` (default true) |
| `Link`/`Detach Reference Value Assignment` | `ReferenceValueAssignment`, with Attribute Name, Confidence, Steward, Notes |

`Link Question to Valid Values` (Glossary) and `Link Data Field to Valid
Values` (Data Designer) are contextual forms of `ValidValuesAssignment`. They
live in their own families.

A set's members can be given three ways, in one `Create Reference Data Set`:

- `Members` — existing values, by name or GUID.
- `Values` — new values, one per line. This is a **Line List**: only new
  lines separate entries, so `Washington, D.C.` stays one value.
- `Value Table` — new values with their own properties, as a markdown
  **Table**. Columns: Value (required), Display Name, Description, Usage,
  Data Type, Is Case Sensitive, Default, Ordinal. Write a literal pipe as `\|`.

```markdown
## Create Reference Data Set
### Display Name
Order Status

### Value Table
| Value     | Display Name | Description         | Default | Ordinal |
|-----------|--------------|---------------------|---------|---------|
| PENDING   | Pending      | Order received      | true    | 1       |
| SHIPPED   | Shipped      | Left the warehouse  |         | 2       |
```

Rules:

- An inline value is named `<set qualified name>::<value>`. The set's
  qualified name is derived as usual, with the local prefix and version, e.g.
  `Coco Pharmaceuticals::ReferenceDataSet::Order Status::1.0::PENDING`. So
  re-running a document finds the value and updates it rather than creating a
  duplicate (verified).
- When any of the three attributes is given, the set's membership is made to
  match. Listed values are linked; changed defaults or ordinals are updated in
  place. Members no longer listed are **unlinked, never deleted**, since other
  sets or fields may use them. When none of the three is given, an update
  leaves membership alone.
- Ordinal comes from the `Ordinal` column, or from list position. `Default
  Member` names the default when you use `Values`.
- To link values across sets in a portable document, give them unique display
  names with `Create Reference Data Value`. An inline value's display name is
  just its value, which may repeat across sets.
- There are no Delete commands in Dr.Egeria (no family has them). Use the SDK.

Report specs `Reference-Data-Set-DrE-Basic/Advanced` and
`Reference-Data-Value-DrE-Basic/Advanced` work with `View Report`.

---

## Valid metadata values

### What they are

`ValidMetadataManager.setup_valid_metadata_value(property_name, type_name, body)`
registers a value as valid for an open metadata property, optionally for one
type only. The server builds a `ValidMetadataValue` element for it, with a
qualified name like `Egeria:ValidMetadataValue::<property>-<type>`. You
address it by property, type and value, never by GUID. `TechnologyType` (the
values of `deployedImplementationType`) is a specialisation of this.

Siblings: `setup_valid_metadata_map_name` / `setup_valid_metadata_map_value`
for map-valued properties; `clear_valid_metadata_value` /
`clear_valid_metadata_map_name` / `clear_valid_metadata_map_value`;
`validate_metadata_value` (and map forms); `get_valid_metadata_value(s)` (and
map forms). `get_valid_metadata_values` has no `asOfTime` (ISSUE-18, an
Egeria limit).

```python
client.valid_metadata.setup_valid_metadata_value(
    "projectHealth", "Project",
    {"displayName": "At Risk", "description": "Slipping; needs attention", "preferredValue": "At Risk"})
```

Omit `type_name` (pass `None`) to make a value valid for the property on every
type. pyegeria omits the query parameter in that case (ISSUE-82).

### Behaviour worth knowing

- **Re-running setup is safe.** Setting up the same value again does not
  duplicate it (verified).
- **Setup also creates a per-property container**
  (`Egeria:ValidMetadataValue::<property>-<type>`), and clearing the values
  does not remove it. To remove it, find it with
  `find_valid_value_definitions(<property>, metadata_element_type="ValidMetadataValue")`
  and delete it by GUID.
- **Clearing:** in the 2026-10-13 live check, the first
  `clear_valid_metadata_value` calls returned an error, yet the values were gone
  afterwards. A repeat call answered "not found" (`OPEN-METADATA-400-011`). Read
  the values back rather than trusting the response.
- **Consistent values:** `set_consistent_metadata_values(property1, type1,
  map1, value1, property2, type2, map2, value2)` says two valid metadata values
  go together — e.g. `fileType` "Python Source" with `fileExtension` ".py".
  Both must already be set up. `get_consistent_metadata_values` reads them.

### Specification properties

`SpecificationPropertyValue` is the third `ValidValueDefinition` subtype. It
describes a template's or connector's configuration: placeholders, replacement
attributes, supported templates, action targets, guards.

- `setup_specification_property(element_guid, body)`,
  `delete_specification_property`, `find_specification_property`,
  `get_specification_property_by_type` / `_by_name` / `_by_guid`,
  `get_specification_property_types`.
- `link_specification_property` / `detach_specification_property` create
  and remove the `SpecificationPropertyAssignment` relationship (with
  `propertyName`) between an element and a valid value.

### Dr.Egeria: the Valid Metadata family

| Command | Does |
|---|---|
| `Setup`/`Clear Valid Metadata Value` | One value for a property (and optional type) |
| `Setup`/`Clear Valid Metadata Map Name` | A valid name for a map-valued property |
| `Setup`/`Clear Valid Metadata Map Value` | A valid value for a name in a map-valued property |
| `Set Consistent Metadata Values` | Two values that go together |
| `Link`/`Detach Specification Property Assignment` | `SpecificationPropertyAssignment` |

`Setup Valid Metadata Value` also accepts a `Metadata Value Table`, to set up
several values for one property in one command:

```markdown
## Setup Valid Metadata Value
### Metadata Property Name
projectHealth

### Type Name
Project

### Metadata Value Table
| Preferred Value | Display Name | Description               |
|-----------------|--------------|---------------------------|
| On Track        | On Track     | Progressing to plan       |
| At Risk         | At Risk      | Slipping; needs attention |
```

These commands were part of the Reference Data family until 2026-10-13.
Their names did not change when they moved.

---

## Summary

| You want to… | Use |
|---|---|
| Publish a business code list | Reference data: `Create Reference Data Set` with `Values` or `Value Table` |
| Say which code list a field or question uses | `Link Element to Valid Values` / `Link Data Field to Valid Values` / `Link Question to Valid Values` |
| Tag an element with one code | `Link Reference Value Assignment` |
| Relate codes in two lists | `Link Mapped Valid Values` (same meaning), `Link Associated Valid Values` (named relation), `Link Consistent Valid Values` (used together) |
| Record how a system stores a code | `Link Valid Value Implementation` |
| Allow a new value for an Egeria property | Valid metadata: `Setup Valid Metadata Value` |
| Say two Egeria property values go together | `Set Consistent Metadata Values` |

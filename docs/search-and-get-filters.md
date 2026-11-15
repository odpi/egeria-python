# Search and get filters

Every pyegeria `find_*` and `get_*` method that sends a request body to Egeria accepts the
standard **filters** as keyword arguments, and passes them to one shared request helper. The
signatures stay short: a method lists its everyday parameters (`search_string`, `start_from`,
`page_size`, `output_format`, `report_spec`, `body` ...) and takes the rest through `**kwargs`.

```python
from pyegeria import EgeriaTech

client = EgeriaTech("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
client.create_egeria_bearer_token()

# Only the DataClass subtype of DataValueSpecification:
data_classes = client.find_data_value_specifications(
    "*", metadata_element_subtypes=["DataClass"],
)

# Glossary terms that are ACTIVE, newest first, as they were on 1 March:
terms = client.find_glossary_terms(
    "customer",
    limit_results_by_status=["ACTIVE"],
    sequencing_order="CREATION_DATE_RECENT",
    as_of_time="2026-03-01T00:00:00Z",
)

# A get-by-GUID that leaves the noisy relationships out of the returned graph:
spec = client.get_data_value_specification_by_guid(
    guid, skip_relationships=["SemanticAssignment"], graph_query_depth=1,
)

# A by-name lookup restricted to elements anchored in one glossary:
fields = client.get_data_fields_by_name("customer id", anchor_guid=glossary_guid)
```

## Which filters a method accepts

There are three request kinds, each with its own Egeria request body, and so its own filter set:

| Methods | Filter set | Egeria request body |
|---|---|---|
| `find_*` | `SearchFilters` | `SearchStringRequestBody` (or `FindPropertyNamesProperties` when `property_names` is given) |
| `get_*_by_name` and other list gets | `ListFilters` | `FilterRequestBody` / `ResultsRequestBody` |
| `get_*_by_guid` and other single-element gets | `GetFilters` | `GetRequestBody` |
| `find_metadata_elements`, `find_root_elements` | `FindFilters` | `FindRequestBody` |

`SearchFilters` ⊃ `ListFilters` ⊃ `GetFilters`: a search accepts everything a list does,
and a list everything a get does. Each method's docstring has one line naming its set.

The sets are PEP 692 `TypedDict`s in `pyegeria.core.request_filters`. Where a method's
signature is `**kwargs: Unpack[SearchFilters]`, your editor completes the filter names and
shows each one's description.

The activity-, content- and deployment-status finds (for example `find_digital_products`)
accept the same filters plus their own explicit status-list parameter.

### One name for the type filters

Since 6.2.28 every method spells the element-type filters the same way:
`metadata_element_type` (one type name) and `metadata_element_subtypes` (a list). The older
spellings (`metadata_element_type_name`, `metadata_element_subtype_names`,
`metadata_element_sub_type`, `metadata_element_subtype`, `metadata_element_name`) still work,
with a `DeprecationWarning` naming the new one. A lone string given for a subtype list becomes
a one-item list. Giving the old and the new name with different values raises `TypeError`,
because pyegeria cannot tell which you meant.

```python
explorer.find_elements_by_property_value("pump", ["displayName"],
                                         metadata_element_type="EmbeddedProcess")
```

Report specs and Dr.Egeria parameter lists may still use the old spellings; the report
executor renames them quietly.

### Filters are checked

The names you pass are checked against the fields of the request body that call sends — the
check is derived from pyegeria's request-body models, not a hand-kept list. An unknown name
(usually a typo) is **ignored with a warning**:

```text
UnknownFilterWarning: DataDesigner.find_data_value_specifications: unknown filter
'metadata_element_subtipes' ignored. Valid filters for this request: anchor_domain,
anchor_guid, ... metadata_element_subtypes, metadata_element_type, ...
```

`UnknownFilterWarning` is a `UserWarning`, so it shows by default. The same message goes to
pyegeria's log (loguru, level WARNING), so it is not lost where stderr is not visible (the
Egeria portal, the MCP server). A filter that exists but does not apply to the request (for
example `anchor_guid` on a get-by-GUID, which `GetRequestBody` has no field for) warns too.

To turn the warnings into errors now, for example in tests:

```python
import warnings
from pyegeria.core.request_filters import UnknownFilterWarning

warnings.simplefilter("error", UnknownFilterWarning)
```

**Plan:** pyegeria 6.2.28 warns. A later release will raise `TypeError` for an unknown
filter name instead. Fix any warnings you see now.

### Report specs

A report spec's `spec_params` (and the parameters a caller passes to `run_report` /
`exec_report_spec`) go into the same `**kwargs`, so a typo there warns in the same way —
through the report executor, with the method's name in the message:

```python
"Data-Classes": FormatSet(
    ...,
    action=ActionParameter(
        function="DataDesigner.find_data_value_specifications",
        required_params=["search_string"],
        spec_params={"metadata_element_subtypes": ["DataClass"]},
    ),
)
```

### Which wins: a report spec's `spec_params` or the caller's parameters

A report spec's `spec_params` are pinned: when a caller passes the same parameter to
`run_report` / `exec_report_spec`, **the spec's value wins** (the spec is what the report *is*;
see the design note §9.13). A caller's parameter that the report does not take at all is
dropped, and now says so with an `UnknownFilterWarning` naming it and listing what the report
does take.

### Generic searches name a type

`ClassificationExplorer.find_elements_by_property_value` searches `property_names` (for report
specs: `displayName` and `qualifiedName`) within `metadata_element_type`.

- `'*'` with a type lists the elements of that type (it calls `get_elements`), one page at a
  time: the caller's `page_size`, 100 when none is given, never more than 100 per call — page on
  with `start_from`. `'*'` with no type, or with a root type (`OpenMetadataRoot`,
  `Referenceable`), is refused: "give a search string or a narrower type". The refusal is
  `pyegeria.core.request_filters.SearchRefused`, a `ValueError` subclass, raised before any request
  is sent to Egeria (`find_elements_by_property_value` and `find_metadata_elements_with_string`
  raise it), so `except ValueError` still catches it. A report spec run that hits it logs a
  warning rather than an error.
- `deployed_implementation_type="PostgreSQL Server"` restricts the search to exactly that
  technology within the type. Egeria evaluates it in one complex query:
  `deployedImplementationType` **equals** the technology (ignoring case, so `"postgresql server"` works), **and**, for a search string other than
  `'*'`, one of `property_names` matches it (`starts_with` / `ends_with` / `ignore_case` choose the
  operator: STARTS_WITH, ENDS_WITH, EQ or LIKE (contains), case-insensitive variants with
  `ignore_case`). So a Postgres-Server report never lists a Kafka server or a "Databricks Unity
  Catalog Server", and paging stays exact. The technology report specs also show a *Deployed
  Implementation Type* column.
- In the technology report specs (Kafka, Postgres server/database, Unity Catalog ...) the
  technology is a **run parameter**, `deployed_implementation_type`, whose default is the spec's
  own technology (the spec pins it as `default_deployed_implementation_type`):
  - not given → the spec's technology, matched exactly;
  - `"*"` → any technology: the report lists or searches every element of its type (e.g. every
    `SoftwareServer`); `'*'` as the search string still lists at most 100 per call, and a root type
    is still refused;
  - any other value → that technology, matched exactly.

`MetadataExpert.find_metadata_elements_with_string("*")` with no type is refused with
"give a search string or a type" instead of passing Egeria's "searchString is null" through.

### Notes

- `None` means "not set": a filter passed as `None` never overrides the method's own default.
- When you pass a complete `body=`, the body is sent as given and the filter keywords are not
  merged into it (their names are still checked).
- `metadata_element_subtypes` is honoured by searches and lists. Egeria ignores it on a
  get-by-GUID (Egeria moved it from `GetOptions` to `QueryOptions`); it is still accepted there.
- Some older methods name a filter explicitly in their signature (for example
  `metadata_element_type`, `skip_relationships`). Those parameters work as before. PEP 692 does
  not allow a `TypedDict` key to repeat a named parameter, so those methods keep a plain
  `**kwargs` annotation; the filters still pass through and are still checked.

## Filter reference

The tables below are generated from `pyegeria.core.request_filters` (a micro-test fails if
they drift). The "Wire name" is the field name in the JSON request body Egeria receives.

<!-- BEGIN GENERATED FILTER TABLES -->
### `GetFilters`

Used by get_*_by_guid and other single-element gets. Maps to `GetRequestBody`.

| Filter | Type | Wire name | Meaning |
|---|---|---|---|
| `metadata_element_type` | `str` | `metadataElementTypeName` | Restrict results to this open metadata type (and its subtypes), e.g. `"DataClass"`. |
| `metadata_element_subtypes` | `list[str]` | `metadataElementSubtypeNames` | Only return elements of these subtypes, e.g. `["DataClass"]`. Honoured on searches and lists; Egeria ignores it on a get-by-GUID. |
| `skip_relationships` | `list[str]` | `skipRelationships` | Relationship type names to leave out of each element's related-element graph. |
| `include_only_relationships` | `list[str]` | `includeOnlyRelationships` | Only include these relationship type names in each element's related-element graph. |
| `skip_classified_elements` | `list[str]` | `skipClassifiedElements` | Leave out elements that carry any of these classifications. |
| `include_only_classified_elements` | `list[str]` | `includeOnlyClassifiedElements` | Only return elements that carry one of these classifications. |
| `max_mermaid_node_count` | `int` | `maxMermaidNodeCount` | Largest number of nodes Egeria draws in the returned Mermaid graph. |
| `governance_zone_filter` | `list[str]` | `governanceZoneFilter` | Only return elements in these governance zones. |
| `as_of_time` | `datetime \| str` | `asOfTime` | Query the repository as it was at this time (ISO-8601 string or datetime). |
| `effective_time` | `datetime \| str` | `effectiveTime` | Only return elements (and relationships) effective at this time. |
| `relationship_page_size` | `int` | `relationshipsPageSize` | Page size for the relationships returned with each element (0 = server default). |
| `for_lineage` | `bool` | `forLineage` | Include elements marked Memento (deleted but kept for lineage). |
| `for_duplicate_processing` | `bool` | `forDuplicateProcessing` | Return duplicates as stored, without deduplication processing. |
| `external_source_guid` | `str` | `externalSourceGUID` | GUID of the external metadata source the request is made on behalf of. |
| `external_source_name` | `str` | `externalSourceName` | Qualified name of the external metadata source the request is made on behalf of. |
| `request_id` | `str` | `requestId` | Caller-supplied id echoed in Egeria's audit log for tracing the request. |

### `ListFilters`

Used by get_*_by_name and other list gets. Maps to `FilterRequestBody` (by name) / `ResultsRequestBody`. Everything in `GetFilters`, plus:

| Filter | Type | Wire name | Meaning |
|---|---|---|---|
| `anchor_guid` | `str` | `anchorGUID` | Only return elements anchored to the element with this GUID. |
| `anchor_domain` | `str` | `anchorDomainName` | Only return elements whose anchor is in this domain (an open metadata type name). |
| `anchor_scope_guid` | `str` | `anchorScopeGUID` | Only return elements whose anchor scope is the element with this GUID. |
| `limit_results_by_status` | `list[str]` | `limitResultsByStatus` | Only return elements whose status is one of these, e.g. `["ACTIVE"]`; Egeria's ElementStatus: UNKNOWN, ACTIVE, INVALID, DELETED, OTHER (a content status such as DRAFT is refused). |
| `sequencing_order` | `str` | `sequencingOrder` | Order of the results; `PROPERTY_ASCENDING`/`PROPERTY_DESCENDING` need `sequencing_property`. |
| `sequencing_property` | `str` | `sequencingProperty` | Property name to sort on when `sequencing_order` is a PROPERTY_* order. |

### `SearchFilters`

Used by find_*. Maps to `SearchStringRequestBody` / `FindPropertyNamesRequestBody`. Everything in `ListFilters`, plus:

| Filter | Type | Wire name | Meaning |
|---|---|---|---|
| `property_names` | `list[str]` | `propertyNames` | Search only these properties (switches the request to `FindPropertyNamesProperties`). |

### `FindFilters`

Used by the complex-query finds (find_metadata_elements, find_root_elements). Maps to `FindRequestBody`. Everything in `ListFilters`, plus:

| Filter | Type | Wire name | Meaning |
|---|---|---|---|
| `search_properties` | `dict` | `searchProperties` | A `SearchProperties` structure: property conditions the elements must match. |
| `match_classifications` | `dict` | `matchClassifications` | A `MatchClassifications` structure: classification conditions the elements must match. |
| `skip_subtypes` | `bool` | `skipSubtypes` | When true, `metadata_element_subtypes` lists subtypes to EXCLUDE rather than the only ones to include. |

### Call parameters (explicit on the method, also accepted as filters)

| Request body | Parameters |
|---|---|
| `GetRequestBody` | `graph_query_depth` |
| `ResultsRequestBody` | `graph_query_depth`, `page_size`, `start_from` |
| `FilterRequestBody` | `filter_string`, `graph_query_depth`, `page_size`, `start_from` |
| `SearchStringRequestBody` | `ends_with`, `graph_query_depth`, `ignore_case`, `page_size`, `property_value`, `search_string`, `start_from`, `starts_with` |
| `FindRequestBody` | `graph_query_depth`, `page_size`, `start_from` |

### Other accepted spellings

| You may write | Same as |
|---|---|
| `metadata_element_type` | `metadata_element_type_name` |
| `metadata_element_subtypes` | `metadata_element_subtype_names` |
| `anchor_domain` | `anchor_domain_name` |
| `relationship_page_size` | `relationships_page_size` |
| `classification_names` | `include_only_classified_elements` |
| `limit_result_by_status` | `limit_results_by_status` |
| `sort_order` | `sequencing_order` |
| `output_sort_order` | `sequencing_order` |
| `order_property_name` | `sequencing_property` |
| `anchor_scope_id` | `anchor_scope_guid` |

### Deprecated spellings

These still work, with a `DeprecationWarning` naming the new name. Giving both the old and the new name with different values raises `TypeError`.

| Deprecated | Use |
|---|---|
| `metadata_element_type_name` | `metadata_element_type` |
| `metadata_element_name` | `metadata_element_type` |
| `metadata_element_subtype_names` | `metadata_element_subtypes` |
| `metadata_element_sub_type` | `metadata_element_subtypes` |
| `metadata_element_subtype` | `metadata_element_subtypes` |

Each model field's camelCase wire name (e.g. `metadataElementSubtypeNames`) is accepted as well. These rendering options are passed through to output formatting and are not warned about: `filter_string`, `include_children`, `include_peers`, `include_preamble`, `max_depth`, `refresh_spec`, `report_format`, `search_string`.
<!-- END GENERATED FILTER TABLES -->

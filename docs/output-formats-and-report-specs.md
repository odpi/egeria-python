<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Output Formats and Report Specs in pyegeria

This document explains how pyegeria turns Egeria responses into useful output using report specs (a.k.a. format sets). It covers available output formats, the report spec model, how nested/master–detail views work, and how to create and load your own specs.

If you are new to pyegeria, start with the README for installation and configuration, then return here when you need to tailor the output of find/get operations.

---

### Quick Start

- Show a user profile with master–detail output (table + linked detail sections):

```python
from pyegeria.omvs.my_profile import MyProfile

client = MyProfile("qs-view-server", "https://localhost:9443", user_id="user", user_pwd="secret")
client.create_egeria_bearer_token("user", "secret")

md = client.get_my_profile(output_format="LIST", report_spec="My-User-MD")
print(md)  # Markdown table with [details] links for Contact Methods, Roles, Teams, Communities
```

- Get the same data as a nested dictionary (ideal for programmatic processing/UIs):

```python
profile = client.get_my_profile(output_format="DICT", report_spec="My-User-MD")
# dict with scalar attributes + lists of dicts for contact_methods, roles, teams, communities
```

---

### Output Formats

pyegeria supports multiple output types. Each report spec declares which types it supports.

- DICT: Python list/dict structures — best for programmatic use and tests. This format provides a "materialized" view where properties are cleaned up and nested elements are promoted to logical keys.
- JSON: Raw Egeria response dictionary — ideal for advanced users who need to process the exact response from the Egeria platform without any pyegeria-specific transformations.
- LIST: Markdown table (horizontal). Good for compact overviews. Nested values are automatically summarized (names/display names). If a `detail_spec` is configured, master rows include `[details]` links to rich detail sections appended below the table.
- REPORT: Rich Markdown (vertical). Ideal for deep dives. Renders nested dict/list values as hierarchical bullet lists (using the hyphen `-` as the default bullet character) and includes vertical detail sections for master-detail columns.
- REPORT-GRAPH: Recursive, linked Markdown report. Builds anchor-linked sections per element (by GUID), and adds link lists for peer and child/nested elements; recurses while avoiding cycles.
- FORM: Markdown suitable for Dr.Egeria editable forms. Complex values are summarized to keep the form concise and manageable.
- MD: Plain Markdown (legacy simple rendering).
- MERMAID: Mermaid graph text for supported responses.
- HTML: HTML wrapper around Markdown (when enabled in generators).
- GRAPH: Generates a standalone HTML page natively rendering dynamic Vega-Lite visualizations. Functions identically to `HTML` when rendering but signals intent for rich visualization output.
- TABLE: Used for generating a rich textual table for terminal display.

Tip: Use DICT for APIs and automation; use LIST for dashboards/browsing; use REPORT for deep, readable details; use FORM when producing updateable forms.

### Custom Column Formatting

You can customize how column data is rendered in `LIST` format (Markdown tables) by setting the `format` attribute to a string, such as `"bulleted-list"`.

- `bulleted-list`: Renders list values as a vertical bulleted list using HTML line breaks (`<br>`) within the Markdown table cell. This is useful for improving the readability of long lists.

Example:
```python
Column(name="Containing Members", key="collection_members", format="bulleted-list"),
```

---

### Method Parameter Consistency

All `find_*` and `get_*` methods in `pyegeria` that support formatted output follow a consistent parameter pattern:

- `output_format`: The desired output type (e.g., "DICT", "LIST", "REPORT"). Defaults to "DICT" or "JSON" depending on the method.
- `report_spec`: Optional name or dictionary defining the columns and layout.
- `search_string` / `filter_string`: 
    - `find_*` methods use `search_string` for substring matching.
    - `get_*` methods use `filter_string` for exact value matching.
    - **Normalization**: The output layer automatically handles both. Whichever string was used to fetch the data will be displayed in the output preamble (e.g., in Markdown reports).
- `**kwargs`: Methods accept additional keyword arguments which are passed safely through to the output formatter. This allows for future rendering flags without breaking method signatures.

---

### Parameter naming: snake_case vs camelCase

- For method/CLI parameters and action specs, prefer snake_case names (e.g., `metadata_element_subtypes`, `page_size`, `start_from`, `effective_time`, `sequencing_order`).
- The report executor (`exec_report_spec`/`run_report`) and CLI adaptors expect snake_case; underlying clients convert to on‑wire camelCase when calling Egeria.
- Column `key` names in report specs: **use camelCase**. While the formatter tries exact key, then `to_camel_case`, then uppercase for value *lookup*, the mermaid detection system only recognises camelCase keys (see [Mermaid Graphs](#mermaid-graphs-and-normalization) below for details).
- CLI flags like `--param page_size=50` or `--params-json '{"metadata_element_subtypes":["Asset"],"page_size":100}'` must use snake_case.

### The Report Spec Model

Report specs are defined using Pydantic models in `pyegeria/view/_output_format_models.py` and registered in `pyegeria/view/base_report_formats.py`.

- FormatSet
  - `target_type`: logical type (e.g., "Glossary", "Project", "My-User")
  - `heading`, `description`, optional `family`, optional `aliases`
  - `formats`: a list of `Format` entries
  - optional `action`: how to call a client method (used by higher-level tooling)
- Format
  - `types`: list of output types this format supports (e.g., `["DICT", "LIST"]`)
  - `attributes`: list of `Column` (alias: `Attribute`)
- Column (Attribute)
  - `name`: display name in the output
  - `key`: property key to extract from the data (snake_case or camelCase supported)
  - `format`: optional flag to apply formatting suitable for tables/links
  - `detail_spec`: optional name of another report spec to render a nested detail section (master–detail)

Example (Python) — simplified snippet:

```python
from pyegeria.view._output_format_models import Column, Format, FormatSet

My_User_MD = FormatSet(
    target_type="My-User",
    heading="My Information Master-Detail",
    description="User Information with links to details",
    family="MyProfile",
    formats=[
        Format(
            types=["DICT", "LIST", "REPORT"],
            attributes=[
                Column(name="Full Name", key="full_name"),
                Column(name="User ID", key="user_id"),
                Column(name="Roles", key="roles", detail_spec="My-User-Roles-Detail"),
            ],
        )
    ],
)
```

---

### Selecting Specs and Generating Output

Most client methods already call the output pipeline for you. Under the hood, the following helpers are used (in `pyegeria/view/output_formatter.py` and `pyegeria/view/base_report_formats.py`):

- `select_report_format(label: str, output_type: str) -> dict`: pick a spec by name/label and match the requested type (with fallback to `ALL`).
- `resolve_output_formats(entity_type: str, output_format: str, report_spec: str|dict|None)`: flexible resolver used by clients (by name, by dict, or by entity type default).
- `generate_output(...)`: orchestrates DICT/LIST/REPORT/FORM rendering given elements and a spec. It supports an `include_preamble` parameter (default `True`) to control whether the report header/preamble is included; this is automatically disabled during recursive master-detail calls to prevent redundant headings.

### `target_type` fallback behavior

If a report spec resolves successfully but has `target_type = None`, pyegeria logs a warning and falls back to `Referenceable` for rendering. This prevents LIST/REPORT failures caused by missing type labels in a spec.

### Type matching and the 'ALL' shorthand

When you request an `output_format`, pyegeria selects the best matching `Format` inside the `formats` list for the chosen spec:
- Exact match: a `Format` whose `types` contains the requested type (e.g., `"LIST"`).
- Fallback to `ALL`: if no exact match is found, a `Format` whose `types` includes `"ALL"` will be used.
- Final fallback: if neither is present, the first `Format` entry is used.
- Precedence: if both a type‑specific `Format` and an `ALL` `Format` are present, the type‑specific one wins.

Example JSON using `ALL`:
```json
{
  "My-User-Compact": {
    "target_type": "My-User",
    "formats": [
      {"types": ["ALL"], "attributes": [
        {"name":"Name","key":"display_name"},
        {"name":"GUID","key":"guid","format":true}
      ]}
    ]
  }
}
```
This single spec works for `DICT`, `LIST`, and `REPORT` with the same attribute set. You can add another `Format` with `types: ["REPORT"]` later if you want a richer vertical report while keeping `ALL` for other types.

Basic example using a registered spec:

```python
from pyegeria.view.base_report_formats import select_report_format
from pyegeria.view.output_formatter import generate_output

spec = select_report_format("My-User-MD", "LIST")
md = generate_output(elements=[element], search_string="", entity_type="My-User", output_format="LIST",
                     extract_properties_func=my_extractor, columns_struct=spec)
```

In practice you will call a client method (e.g., `MyProfile.get_my_profile`) and pass `output_format` + `report_spec`.

---

### Automated Schema Discovery

If you are a report author creating a new report specification, you may want to know all available attribute paths, classifications, and nested relationship properties for a given Egeria element without manually guessing paths. pyegeria provides an automated discovery capability to flatten and expose these properties using dot notation (e.g., `zoneMembership.type.typeCategory`). 

By default, the discovery utility filters out boilerplate Egeria system properties (like `versions`, `status`, `metadataOrigin`) to reduce cognitive noise. You can control this via the `exclude_system_properties` parameter if calling the SDK directly.

1.  **Using `Report-Spec-Schema` (CLI / Dr. Egeria)**  
    Execute the special `Report-Spec-Schema` format set and pass your "skinny" target report specification as an argument. The engine will run the underlying action, flatten the materialization tree, and output a table mapping each available `attribute_path` to its observed `data_type`.
    ```bash
    run_report --report Report-Spec-Schema --param report_spec_name=My-New-Report --param search_string="example"
    ```

2.  **Using the SDK (`get_report_spec_schema`)**  
    You can directly invoke the schema discovery utility from the `EgeriaTech` client:
    ```python
    from pyegeria.egeria_tech_client import EgeriaTech
    client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="user", user_pwd="secret")
    schema = client.get_report_spec_schema(report_spec_name="Digital-Product-DrE-Basic", search_string="example", exclude_system_properties=True)
    print(schema) # returns a list of {"attribute_path": "...", "data_type": "..."}
    ```

### Using Dot-Notation for Nested Attributes

Once you have discovered the nested attributes you want to include, you can reference them directly in your `Column` definitions using dot notation. The formatting engine recursively traverses the data structure to resolve these paths automatically.

You can specify the dot paths in **either** exact `camelCase` (as returned by the discovery tool) or standard `snake_case`.

```python
# Both approaches are fully supported and resolve to the same underlying data:
Column(name="Zone Category", key="zoneMembership.type.typeCategory")
Column(name="Zone Category", key="zone_membership.type.type_category")
```

---

### Step-by-Step: Creating a New Report Spec

Creating a new report spec is a straightforward process when combining the schema discovery tools and JSON spec loading. 

1. **Create a "Skinny" Spec**: Start by defining the minimum required fields, targeting the Egeria action you wish to report on. Place this in your user specs directory (e.g., `my_specs.json`).
   ```json
   {
     "My-New-Report": {
       "target_type": "DigitalProduct",
       "heading": "My Digital Products",
       "formats": [
         {
           "types": ["ALL"],
           "attributes": [
             {"name": "Display Name", "key": "display_name"}
           ]
         }
       ],
       "action": {
         "function": "AssetCatalog.find_assets",
         "required_params": ["search_string"]
       }
     }
   }
   ```
2. **Discover Available Attributes**: Load your spec and run the `Report-Spec-Schema` tool against it to see the exact structure of the data it returns.
   ```bash
   run_report --report Report-Spec-Schema --param report_spec_name=My-New-Report --param search_string="*"
   ```
3. **Enhance Your Spec**: Review the generated schema table. Pick the dot-notation paths (e.g., `zoneMembership.type.typeCategory`, `typeMembershipPieGraph`) that are relevant to your users and add them as new `attributes` in your JSON file.
4. **Run Your Finished Report**: Execute your updated report spec to see the rich, nested data formatted perfectly in your chosen output style.
   ```bash
   run_report --report My-New-Report --output-format TABLE --param search_string="*"
   ```

---

### Nested Data and the Master–Detail Pattern

Egeria OMVS responses often include related elements and nested hierarchies. pyegeria preserves this richness and makes it navigable across all primary output formats (`LIST`, `REPORT`, `DICT`, and CLI `TABLE`).

- Rich materialization: `materialize_egeria_summary(summary, columns_struct=None)` turns a `RelatedMetadata*Summary` into a clean dict that includes:
  - relationship properties (e.g., `assignmentType`)
  - related element properties (e.g., `name`, `qualifiedName`, `guid`, `type`, `description`)
  - recursively processed `nested_elements`
- Schema‑driven promotion: if the current spec includes attributes with `detail_spec`, pyegeria builds a type→key map from those linked specs and promotes matching nested elements into those keys. Example: a role that has nested `Project` items becomes `{"projects": [ ... ]}` when the column points to a `Project` detail spec.
- Smart Summarization: when rendering collections in tables (`LIST` or CLI `TABLE`), pyegeria now attempts to summarize them by joining the names or display names of child elements, rather than just showing a count.

### How formats handle nested values

- DICT: returns full nested dict/lists for downstream processing (materialized).
- JSON: returns the raw Egeria response structure.
- LIST: shows a compact summary (names/identifiers) in the master row and adds a `[details]` link if a `detail_spec` is configured. A detail section is appended below using the linked spec.
- REPORT: renders nested dicts/lists as hierarchical markdown bullet lists (using the hyphen `-` as the default bullet character) for a clean read-only view.
- FORM: shows summarized values only to keep the form updateable and concise.

### Example: Roles → Projects

In `base_report_formats.py`:

```python
# Master: roles column links to a detail spec
Column(name="Roles", key="roles", detail_spec="My-User-Roles-Detail")

# Roles detail spec includes a nested projects column that links again
"My-User-Roles-Detail": FormatSet(
  target_type="PersonRole",
  formats=[
    Format(types=["LIST", "REPORT"], attributes=[
      Column(name="Name", key="name"),
      Column(name="GUID", key="guid", format=True),
      Column(name="Projects", key="projects", detail_spec="My-User-Projects-Detail"),
    ])
  ]
)

"My-User-Projects-Detail": FormatSet(
  target_type="Project",
  formats=[
    Format(types=["LIST", "REPORT"], attributes=[
      Column(name="Name", key="display_name"),
      Column(name="Qualified Name", key="qualified_name"),
      Column(name="Project Status", key="project_status"),
      Column(name="GUID", key="guid", format=True),
    ])
  ]
)
```

Result:
- LIST master shows role names with a `[details]` link.
- A "Roles" section appears below the table; each row’s projects appear as a nested table or report using `My-User-Projects-Detail`.

### Handling Hierarchical Conflicts (Namespaced Keys)

Egeria's JSON responses are highly hierarchical, and common keys like `displayName` or `description` are often reused at different levels (e.g., at the root of a template and inside its `relatedElement.properties`).

The default extractor `populate_columns_from_properties` prioritizes properties blocks, which can lead to "shadowing" where the root element's properties are overwritten by nested ones.

#### Short-Term Solution: Namespaced Keys
To resolve this without changing the core reporting engine, custom extraction functions (like `_extract_tech_type_properties` or `_extract_catalog_target_properties`) can pre-calculate unique, namespaced keys for the report spec to use.

Commonly used namespaced keys in `AutomatedCuration`:

| Key | Origin | Used in Spec |
|-----|--------|--------------|
| `template_display_name` | Root `displayName` of a Template | `Catalog-Template-Detail` |
| `target_display_name` | `displayName` from `relatedElement.properties` | `Catalog-Template-Detail`, `Action-Targets-Detail`, `Catalog-Target` |
| `proc_display_name` | `displayName` from `relatedElement.properties` of a Process | `Governance-Action-Processes-Detail` |
| `ref_display_name` | `displayName` from `relatedElement.properties` of an External Reference | `External-Reference-Detail` |
| `step_display_name` | Root `displayName` of a Governance Action Step | `Governance-Action-Steps-Detail` |
| `type_display_name` | `displayName` from `relatedElement.properties` of an Action Step's type | `Governance-Action-Steps-Detail` |
| `source_display_name` | `displayName` from `relatedElement.properties` of a Request Source | `Action-Request-Sources-Detail` |

Example from `base_report_formats.py`:
```python
Column(name="Catalog Template Name", key="template_display_name"),
Column(name="Target Asset Name", key="target_display_name"),
```

Example from `automated_curation.py` normalization loop:
```python
t_copy['template_display_name'] = t_copy.get('displayName')
related_props = t_copy.get('relatedElement', {}).get('properties', {})
t_copy['target_display_name'] = related_props.get('displayName')
```

#### Long-Term Solution: Dot Notation (Future)
A more robust approach planned for the future is to support path-based keys directly in the `Column` spec. This will allow traversing the hierarchy without needing to modify the extraction logic for every new conflict.

Example (Planned):
```python
Column(name="Target Name", key="relatedElement.properties.displayName")
```

---

### Linked Graph REPORTs (REPORT-GRAPH)

The `REPORT-GRAPH` output type produces a recursive, wiki-style Markdown document with working intra-document links. It is ideal for exploring networks of related metadata (peers and nested/child elements) from a `find_*` response.

Key traits
- One section per element, with an anchor (`<a id="{guid}">`) and heading `# <Type> Name: <Display Name>`
- Shows key identifiers (Qualified Name, GUID) and scalar properties
- Lists Peers and Children as bullet lists with Markdown links that jump to their sections
- Recurses to render each referenced element exactly once (subsequent references render only as links), avoiding cycles
- Works with most specs out-of-the-box due to `ALL` fallback; you typically do not need to edit the spec to try it

Examples
```bash
# Generate a linked Markdown graph for governance definitions
poetry run run_report --report "Governance Policies" --output-format REPORT-GRAPH --param search_string="*"

# Any spec with types:["ALL"] can also be rendered as a graph
poetry run run_report --report "Collections" --output-format REPORT-GRAPH --param search_string="*"
```

Notes
- The outbox file is saved as Markdown (`.md`).
- The top preamble (title/description) is automatically included by the executor.
- Use optional parameters (if supported by the calling client/spec), for example `page_size`, `start_from`.

---

### Structured tables and native rows

Report specs render complex values (lists, maps, related elements) from **native values**. Two caller
flags expose them; neither is a spec field, and the defaults return today's shapes unchanged.

- `exec_report_spec(name, output_format="TABLE", table_shape="structured")` returns:

  ```
  {"kind": "table",
   "columns": [{"key", "name", "type", "render", "detail_spec", "valid_values", "max_items", "max_lines"}],
   "rows": [{key: native value}],
   "total": int | None, "shown": int, "notes": [str]}
  ```

  `type` is inferred from the column's values: `scalar` (a short value), `text` (long or multi-line),
  `list` (of scalars), `map`, `elements` (related elements) or `table` (sub-rows, e.g. a `detail_spec`
  column). A column that mixes kinds takes the widest and the notes say so. `render` is the column's own,
  else the default for its type (`text`, `bullets`, `kv`, `join`, `subtable`). Related elements are
  `{guid, qualifiedName, displayName, type}`. A table shows two levels: an object inside a sub-row is
  reduced to `{count, names, guid?}` with a note. `total` is the row count when the query did not fill
  its page; when it did, `total` is `None` and the notes say "more may exist" (Egeria's paging contract).
- `exec_report_spec(name, output_format="DICT", dict_shape="native")` (and `generate_output(...,
  dict_shape="native")`) returns DICT rows with native values: lists stay lists, related elements are
  objects with both names, classifications and zones are lists, and `format=True` columns are not
  stringified. The default `"flat"` is unchanged. `dict_shape` does not change TABLE (its structured form
  is `table_shape`).
- Both apply to find-method specs; DOCUMENT, chart and analytic results ignore them. Any other value is
  refused with a sentence. `_async_run_report` takes the same flags.

### Document outputs

A **DOCUMENT** spec produces one document in a published standard (for example DCAT-AP 3 as
JSON-LD), not a rendering of columns. The document is built by an **exporter**: a function
registered as an analytic function (`register_analytic_functions`) and named as the spec's
`action.analytic_function`. A DOCUMENT spec has exactly one format, of type `DOCUMENT`, and it
carries a `document` block:

```python
FormatSet(
    heading="Toy Catalog", description="A toy document",
    action=ActionParameter(analytic_function="toy_export"),
    formats=[Format(types=["DOCUMENT"], document={
        "standard": "toy-1",
        "media_type": "application/json",
        "file_name": "{scope}-toy.json",          # filled from the run's parameters
        "validator": "json-schema",               # optional, a registered validator name
        "validator_options": {"schema": "package:my_exporters/schemas/toy.schema.json"},
    })])
```

Load rules (each refusal is a sentence):

- `DOCUMENT` needs `action.analytic_function`. A DOCUMENT spec with a `function` (a find) and no
  analytic function is refused: a find returns elements, not a document.
- `DOCUMENT` stands alone in its format row, needs its `document` block, and the spec has no
  other formats. Only a DOCUMENT format carries a `document` block.
- `file_name` is a single file name: no path separators, no `..`, not hidden. Parameter values
  filled into it are made file-name safe (`Folder::Sales/EU` becomes `Folder_Sales_EU`) and the
  result is checked again. A parameter the run did not supply is refused.

Run it with `exec_report_spec(name, output_format="DOCUMENT", params={...})`. Any other output
format asked of a DOCUMENT spec is refused with a sentence naming DOCUMENT, and DOCUMENT asked of
any other spec is refused. The exporter returns `{"text": str, "notes": [str, ...]}` (or a plain
string). The result is:

```
{"kind": "document",
 "standard": "toy-1", "media_type": "application/json", "file_name": "Sales-toy.json",
 "text": "...",
 "validation": {"state": "valid" | "invalid" | "not_validated",
                "validator": "json-schema" | None,
                "findings": ["/age: -1 is less than the minimum of 0", ...],
                "reason": None | "why it was not validated"},
 "notes": ["what the exporter left out, and why", ...]}
```

`validation` is **always present**; an unvalidated document says so and why, and is never
presented as conforming:

- no validator declared: `not_validated`, "no validator is declared for this standard";
- a validator name not registered: `not_validated`, "the validator <name> is not registered";
- a validator that raises: `not_validated`, "the validator <name> failed: <error type>[ at line L,
  column C]". A crash says nothing about the document, so it is never a finding and never
  `invalid`. The parser's own text is never put in `reason`: it can quote the input.
- a spec's `schema`/`shapes` option that is not a `package:` reference: `not_validated`, "was not
  run" (and refused when the spec loads as a model).

`notes` is always present too: every field the exporter omitted or left empty is named there
with the reason.

**Validators** are registered by name with
`pyegeria.view.document_validators.register_document_validators({name: fn})`, where
`fn(text, media_type, **validator_options) -> (valid: bool, findings: list[str])`; a name already
registered raises `DocumentValidatorCollision`. Two are built in:

- `json-schema` (jsonschema): option `schema`, for JSON or YAML text;
- `shacl` (pySHACL over rdflib): option `shapes` (Turtle), for JSON-LD, Turtle, RDF/XML,
  N-Triples… by media type. Findings read "<severity> <focus node> <path>: <message>".

A validator **never fetches over the network**. In a report spec, `schema`/`shapes` must be
package data (`package:<dotted.package>/<resource path>`): specs can be held in Egeria and written
by any user, so a spec may not make pyegeria read a local file or a URL. Code may pass a local path
or `file://` URL to the validator functions directly, and `make_shacl_validator(shapes)` binds the
`shacl` built-in to one shapes graph, for registering a validator per standard. An `http(s)`
reference is refused; a JSON Schema `$ref` that is not in the schema is `Unresolvable`, never
fetched; JSON-LD whose `@context` names another document is refused (inline the context). rdflib, pySHACL and jsonschema are plain pyegeria dependencies, so
`not_validated` never means "an extra is missing".

**CLI.** `run_report --report <spec> --output-format DOCUMENT --output <dir> --param scope=...`
writes the document to `<dir>/<file_name>` and prints the validation line and any notes. It
refuses to overwrite an existing file unless `--force` is given.

#### DCAT Catalog (DCAT-AP 3)

The built-in specs **DCAT Catalog** (JSON-LD) and **DCAT Catalog (Turtle)** export the Assets in
a collection or folder as a DCAT-AP 3 catalog. The exporter is the analytic function
`export_dcat` (`pyegeria/view/export_dcat.py`); the validator is `dcat-ap-3-shacl`, pySHACL over
the DCAT-AP 3.0.1 shapes vendored in `pyegeria/view/data/dcat-ap-3/` (CC BY 4.0; source, commit
and hashes in the README there).

```bash
run_report --report "DCAT Catalog" --output-format DOCUMENT --output ./out --param scope=DashboardFolder::Consumer::Portal
```

- `scope` is a collection qualifiedName or GUID; `export_dcat` also takes `search_string` (assets
  in the asset domain), `format` (`jsonld` or `turtle`) and `page_size`.
- A `dcat:Dataset` is an **Asset**. DigitalProducts and Agreements are Bitol's: each is named in
  the notes ("<qn>: a DigitalProduct, not a DCAT dataset (Bitol)"), never exported.
- It reads as the caller. A zoned Asset the caller can read is `dct:accessRights NON_PUBLIC`. A
  member Egeria refuses with a 403 is noted as "not visible to <user>", never as absent.
- Identity is the qualifiedName (`dct:identifier`); the GUID is `adms:identifier`. Nodes are
  `urn:egeria:guid:<guid>` IRIs and the output is sorted, so the same metadata gives the same bytes.
- Every property left out says why in the notes, grouped by reason with the datasets it applies
  to (no Ownership, no License, no access path, no keywords...).

---

### Vega-Lite Graphs and Automated Extraction

PyEgeria supports dynamic Vega-Lite visualization for categorical data. Instead of manually extracting charting attributes for each API payload, the `materialize_egeria_summary` engine automatically scans Egeria API responses for numeric dictionaries (e.g. `typeMembership: {"Asset": 5, "GlossaryTerm": 10}`). When found, it automatically generates two attributes at the root level of the materialized object:
- `<key>BarGraph` (e.g., `typeMembershipBarGraph`): A Vega-Lite specification for a bar chart.
- `<key>PieGraph` (e.g., `typeMembershipPieGraph`): A Vega-Lite specification for a pie/donut chart.

To include these in a report spec, simply reference them in a `Column` definition. 
When rendered in `REPORT` format, they appear as ` ```vega-lite ` Markdown code fences. When rendered in `HTML` or `GRAPH` formats, they are automatically injected as interactive web components using `vega-embed`.

Example:
```python
Column(name='Asset Type Breakdown (Bar)', key='typeMembershipBarGraph'),
Column(name='Asset Type Breakdown (Pie)', key='typeMembershipPieGraph'),
```

### Attribute Discovery

When authoring report specs, it can be difficult to know exactly what properties are available (including dynamically generated graphs). PyEgeria provides a utility method to flatten and discover the schema of any materialized object.

```python
from pyegeria.core.utils import discover_element_schema

# After getting a materialized summary from an API...
schema = discover_element_schema(materialized_summary)
for path, data_type in schema.items():
    print(f"{path}: {data_type}")
```
This returns a clear dictionary mapping dot-separated JSON paths to their data types, such as `'typeMembershipBarGraph': 'dict'`.

---

### Mermaid Graphs and Normalization

Many Egeria elements include Mermaid graph definitions to visualize relationships. pyegeria automatically detects and renders these in Markdown reports (`REPORT`, `REPORT-GRAPH`, `MERMAID`).

### Column `key` naming for Mermaid attributes — use camelCase

When a column in a report spec holds a Mermaid graph or pie chart, pyegeria must detect it as such so it can wrap the content in the correct ` ```mermaid ``` ` code fence. Detection works via two routes, tried in order:

1. **Key-based (primary)**: the column `key` is checked against the built-in `MERMAID_ATTRIBUTE_KEYS` set. These are all **camelCase**. If the key matches, the attribute is fenced regardless of the column `name`.
2. **Name-based (fallback)**: if no key match, the column `name` is title-cased and checked against `MERMAID_GRAPH_TITLES`. Only a small number of generic names are in this list (e.g. "Mermaid Graph", "Anchor Mermaid Graph").

**Consequence**: if you use `snake_case` for a mermaid column key, value *lookup* still works (the formatter converts it to camelCase internally), but mermaid *detection* fails and the raw graph text is output as plain text instead of a rendered diagram.

**Rule: always use camelCase for the `key` field of any column that contains Mermaid content.**

```python
# Correct — key matches MERMAID_ATTRIBUTE_KEYS, pie charts render properly
Column(name='Zone Profiles',       key='zoneProfileMermaidPieChart'),
Column(name='Zone Profile Anchored', key='zoneProfileAnchoredMermaidPieChart'),
Column(name='Zone Profile All',    key='zoneProfileAllMermaidPieChart'),

# Wrong — value is retrieved but the mermaid fence is not added
Column(name='Zone Profiles',       key='zone_profile_mermaid_pie_chart'),
```

Detection goes by the `key` first. A `name` also counts when its title ends in "Mermaid Graph", "Mermaid Mind Map", "Mermaid Pie Chart" or "Lineage Graph" (or is "Mermaid Graph" or "Mermaid"). For the generic flowchart case (`key='mermaidGraph'`, `name='Mermaid Graph'`) both routes match, which is why it appears to work with either case.

#### Any graph key Egeria returns is recognised (6.2.29)

`is_mermaid_graph_key()` in `pyegeria/view/output_formatter.py` treats a key as a Mermaid graph when it ends in `MermaidGraph`, `MermaidMindMap`, `MermaidPieChart` or `LineageGraph` (the ending's case is ignored). The last covers `fieldLevelLineageGraph` and `localLineageGraph`, which carry no "Mermaid". So a new kind of graph from Egeria renders as Mermaid in a REPORT, HTML or MERMAID output with no code change; the table below lists the keys known so far. Vega-Lite keys (`...BarGraph`, `...PieGraph` and so on) are not matched and are checked first.

#### The action and activity graphs follow the context graph (6.2.29)

From Egeria 6.2.29 the context graph, `mermaidGraph`, leaves out relationships whose purpose is Action or Activity; `actionMermaidGraph` and `activityMermaidGraph` show them. So wherever a report offers the context graph (a column keyed `mermaidGraph`, or the `mermaid` column filled from it), pyegeria shows each of these two right after it, when the element carries it:

| Output | What is added |
| :--- | :--- |
| MERMAID | A Mermaid block per companion graph, after the context graph |
| REPORT, and HTML (rendered from the REPORT) | `### Action Mermaid Graph` and `### Activity Mermaid Graph` sections, after the context graph |
| DICT | `Action Mermaid Graph` and `Activity Mermaid Graph` entries, after the context graph's entry |
| TABLE, LIST, MD, FORM | Nothing: every row of a table has the same columns, and MD/FORM show no graphs |

A companion the spec already selects (for example `Asset-Graph`'s own `Action Graph` column) is not repeated, and an element that carries neither key gives exactly the output it gave before. Egeria already returns `actionMermaidGraph` (for Assets, for example), so this changes output today: `Asset-Graph`'s MERMAID shows the context graph, then the action graph.

**Key on every row.** In a DICT result of several rows, when any row carries a companion, every row gets that key right after its context graph, with `""` where the element has none, so a table renderer sees one row shape. A single row, or rows none of which carries a companion, are left as they are.

#### Mermaid keys named so far (`MERMAID_ATTRIBUTE_KEYS`)

| Key | Typical content |
| :--- | :--- |
| `mermaidGraph` | General-purpose flowchart |
| `anchorMermaidGraph` | Anchor graph |
| `informationSupplyChainMermaidGraph` | Information supply chain |
| `fieldLevelLineageGraph` | Field-level lineage |
| `actionMermaidGraph` | Relationships whose purpose is Action (left out of `mermaidGraph` from Egeria 6.2.29) |
| `activityMermaidGraph` | Relationships whose purpose is Activity (left out of `mermaidGraph` from Egeria 6.2.29) |
| `localLineageGraph` | Local lineage |
| `edgeMermaidGraph` | Edge graph |
| `iscImplementationMermaidGraph` | ISC implementation graph (context, solution-component design, implementation status). Servers before Egeria 6.3 sent `iscimplementationMermaidGraph`; it is matched case-insensitively |
| `iscDataMeshMermaidGraph` | ISC data mesh graph: digital products and their dependencies (Egeria 6.3+) |
| `iscSystemFabricMermaidGraph` | ISC system fabric graph: IT infrastructure and software capabilities (Egeria 6.3+) |
| `iscDataFabricMermaidGraph` | ISC data fabric graph: data assets, processes and actions linked by lineage, control flow and action-requester relationships (Egeria 6.3+) |
| `iscDataMappingMermaidGraph` | ISC data mapping graph: elements linked by data mappings, with their anchors (Egeria 6.3+) |
| `specificationMermaidGraph` | Specification graph |
| `solutionBlueprintMermaidGraph` | Solution blueprint |
| `solutionSubcomponentMermaidGraph` | Solution sub-components |
| `governanceActionProcessMermaidGraph` | Governance action process |
| `collectionMermaidMindMap` | Collection mind map |
| `zoneProfileMermaidPieChart` | Zone membership profile |
| `zoneProfileAnchoredMermaidPieChart` | Zone anchored-elements profile |
| `zoneProfileAllMermaidPieChart` | Zone all-elements profile |
| `userAccountTypeProfileMermaidPieChart` | Secrets collection: user accounts by type |
| `userAccountStatusProfileMermaidPieChart` | Secrets collection: user accounts by status |
| `organizationTreeMermaidGraph` | Organization tree |
| `rootHierarchyMermaidGraph` | Root hierarchy |
| `fullLineageMermaidGraph` | Full lineage |

A key with one of the endings above needs no entry here. Add a key to `MERMAID_ATTRIBUTE_KEYS` only if Egeria ever names a graph without one of those endings.

### Syntax Compatibility
Egeria often produces Mermaid output using newer syntax features (like `@ { shape: ... }`) or YAML frontmatter that some Markdown renderers (e.g., Obsidian, PyCharm) do not yet support.

By default, pyegeria applies a **normalization** process to these graphs to ensure they render correctly across a wide range of tools.

#### Normalization Rules:
1. **Line Endings**: Standardizes all line endings to `\n`.
2. **Frontmatter Removal**: Strips YAML frontmatter blocks (delimited by `---`) from the Mermaid code, as these often cause parsing errors in older renderers.
3. **Label Escaping**: Automatically escapes literal newlines inside double-quoted labels (changing them to `\n`) to prevent parser crashes.
4. **Shape Syntax Conversion**: Converts newer node-with-shape syntax to standard, broadly compatible Mermaid syntax:
   - `rounded` or `stadium` → `(text)`
   - `diamond` or `decision` → `{text}`
   - `circle` → `((text))`
   - `hexagon` → `{{text}}`
   - Unknown or document shapes → `[text]` (standard square box)

### Configuring Normalization
Mermaid normalization defaults to enabled. You can control it without code changes:

- JSON config: set `Environment -> Egeria Normalize Mermaid` in your selected config profile.
- Environment variables:
  - Preferred: `PYEGERIA_NORMALIZE_MERMAID` (`true/false`)
  - Backward-compatible fallback: `EGERIA_NORMALIZE_MERMAID`

Precedence for Mermaid normalization is:
1. Environment variables
2. Config value (`Environment.egeria_normalize_mermaid`)
3. Built-in default (`true`)

Invalid env values are ignored and fall back to config/default.

---

### Deep Nesting and Recursive Aggregation

When generating output for complex entities like User Profiles, pyegeria can recursively search through the relationship hierarchy to find and aggregate nested elements.

For example, a User Profile report spec might include a `projects` attribute. Since Egeria usually returns projects nested within roles or teams, pyegeria's profile extractor automatically scans the `performsRoles` hierarchy to find all elements of type `Project` and pulls them up to the top level of your report.

### Key Features:
- **Recursive Search**: Scans multiple levels deep (configurable, default is 3).
- **Automatic Deduplication**: Elements are automatically deduplicated by their GUID, ensuring that a project linked via multiple roles only appears once in the aggregated list.
- **Type-Aware**: Uses the `target_type` defined in the attribute's `detail_spec` to decide what to aggregate. Matches both primary type names and supertype names.

### Configurable Depth
The recursion depth can be controlled in the client code. For the `MyProfile` client, you can set the `aggregation_depth` parameter:

```python
client = MyProfile(..., aggregation_depth=5)
# Or update it on an existing client
client.aggregation_depth = 1  # Only look at immediate children of roles
```

---

### Writing Your Own Report Specs

You can add report specs without changing pyegeria’s source. List them in configuration: any number of JSON files and/or Python loader functions. pyegeria merges them into the report-spec registry.

### Where pyegeria looks for user specs

Every report-spec lookup (`select_report_spec`, `get_report_spec_match`, `list_report_specs`, `hey_egeria`, Dr.Egeria, Egeria Explorer) goes through `get_report_registry()` in `pyegeria/view/base_report_formats.py`. It merges three tiers, and
**a label held by a higher tier shadows the lower one: local > egeria > builtin** (6.2.29):

| Tier | Source |
|---|---|
| `builtin` | **The seed** (6.2.29): pyegeria's shipped specs as packaged JSON in `pyegeria/view/seed/`, one file per family plus `manifest.json`. It holds the hand-maintained built-ins (`base_report_specs`), the generated Dr.Egeria specs (`generated_format_sets`, written by `refresh_specs`), the analytic demo specs and the question specs. The seed is generated from those Python constants by `python -m pyegeria.view.seed build` (which `refresh_specs` runs); `... seed check` fails when it is stale. Never edit it by hand. |
| `egeria` | Report specs held in Egeria, synced into a local cache (RS-EGERIA-TIER) |
| local: `CONFIG` | Installed packages' entry points and your JSON files (below) |
| local: `RUNTIME` | Anything registered in code with `register_report_specs(...)`; survives `refresh_report_specs()` |

**Overriding a built-in (6.2.29).** A local spec (a user-directory file, an entry point, or a runtime
registration) with a built-in's or an Egeria-held spec's label **wins**, with one warning per label per process:

```
Report spec 'Questions': the local copy shadows the builtin copy (they are the same); the builtin copy stays addressable as 'builtin:Questions'.
```

`builtin:<label>` (or `seed:<label>`) and `egeria:<label>` still reach the shadowed copy, and
`list_report_specs(with_status=True)` lists it under that address with `shadowed_by`. An alias of a local spec
that a built-in or Egeria-held spec already holds as its label or alias is dropped from the local copy, with one
warning, so a local spec never takes over another spec's name; a local copy keeps the aliases of the spec it
shadows. With no local specs, the registry is exactly the seed.

A local spec may shadow **any** built-in, including the bootstrap core (`Referenceable`, `Default`,
`Report-Types`, `Report-Specs`, `Report-Spec-DrE-Basic` and the like) and the Dr.Egeria display specs (the
`*-DrE`, `*-DrE-Basic` and `*-DrE-Advanced` specs, for example `Glossary-DrE-Basic`). Doing so changes what
Dr.Egeria and the Portal show for that label, everywhere that label is used. `builtin:<label>` still reaches the
original, and the shadow is logged once per label per process. To undo it, remove the local spec and refresh.

A stale `analytic_demos` entry point left in an editable install's metadata from before 6.2.29 is skipped by
name, with one log line, rather than loaded; reinstall pyegeria to drop it.

**Adding specs (the `CONFIG` tier).** There are two sources:

- **A package's entry points (ISSUE-173).** A package contributes report specs by installing. Declare an entry point in the `pyegeria.report_specs` group that names a callable returning a `FormatSetDict` (or a plain `dict` of label to `FormatSet`), or such a dict itself:
  ```toml
  [project.entry-points."pyegeria.report_specs"]
  my_pkg = "my_pkg.specs:report_specs"
  ```
  Entry points load first. An editable install needs `uv sync` (or `pip install -e .`) after a change to entry points. pyegeria's own analytic demo specs loaded this way (`analytic_demos`) until 6.2.29; they now ship in the seed (`builtin` tier).

- **The user report specs directory.** Every `*.json` file in it is loaded, in alphabetical order, after the list above. Subdirectories and non-JSON files are ignored. The directory is resolved in this order:
  1. the `PYEGERIA_USER_REPORT_SPECS_DIR` env var (or the older `PYEGERIA_USER_FORMAT_SETS_DIR`);
  2. config.json's `"Pyegeria User Report Specs Dir"`;
  3. `~/.pyegeria/report_specs`.

  If the directory doesn't exist, it's skipped quietly.

- **Removed in 6.2.19 (ISSUE-173):** config.json's `"Pyegeria Report Spec Modules"` list, the env vars `PYEGERIA_REPORT_SPEC_MODULES`, `PYEGERIA_REPORT_FORMATS_JSON` and `PYEGERIA_REPORT_FORMATS_MODULES`, and the `trellis.report_specs` alias group. They warned in 6.2.18 and are no longer read. If one of the first four is still set, each refresh logs one WARNING naming it, so a stale setting doesn't quietly do nothing. Move a package's loader to an entry point, and JSON files to the user report specs directory.

**Code that isn't an installed package** (a web app's own tiles, a notebook) can't declare an entry point. It registers its specs in the `RUNTIME` tier instead:

```python
from pyegeria.view.base_report_formats import register_report_specs
register_report_specs(my_specs, source="my_app")
```

Registering a label again from the same `source` replaces it and is not an error, so it's safe on every handler load. A label that another source or a `CONFIG` spec already holds raises `ReportFormatCollision`, and nothing from that call is registered. A built-in's or an Egeria-held spec's label is not a clash: the registration shadows it (above). `unregister_report_spec(label)` releases a label.

**When entries are loaded.** The `CONFIG` tier loads automatically the first time anything calls `get_report_registry()`, so no consumer needs to register anything. It loads once per process. If you add or edit a file while a process is running, call `refresh_report_specs()` to reload. `load_user_report_specs()` does the same reload and also copies the directory's files into the legacy `report_specs` dict, for older code that reads that dict directly.

**What happens when an entry is bad.** Each entry loads on its own, and a bad entry is skipped as a whole. Every other entry still loads, before and after it. An entry is skipped when:

- its file doesn't exist or isn't valid report-spec JSON;
- its entry point, module or function can't be imported, or the function raises an error;
- it defines a label that another local source already defined (an earlier `CONFIG` entry or a `RUNTIME` registration). Labels must be unique within the local tier, so nothing local is silently overridden; the first entry to claim a label keeps it. A built-in's label is not a clash: since 6.2.29 the local entry shadows the built-in, with a warning (above).

Each skip is logged as a warning (`Skipping report spec source JSON:<path>: <reason>`). `refresh_report_specs()` also returns the skips as a list of `(source, reason)` pairs, with an empty list meaning everything loaded. Use that to check your configuration:

```python
from pyegeria.view.base_report_formats import refresh_report_specs
for source, reason in refresh_report_specs():
    print(f"{source} was not loaded: {reason}")
```

**Gotcha: `config.json` must be discoverable.** pyegeria only finds `config/config.json` if `PYEGERIA_CONFIG_DIRECTORY` (or `PYEGERIA_ROOT_PATH`) is set. Otherwise its `"Pyegeria User Report Specs Dir"` setting is silently ignored. If you're not sure, use `PYEGERIA_USER_REPORT_SPECS_DIR`.

**Changed behavior in the user specs directory.** A later file no longer overwrites an earlier file's label: the directory is part of the `CONFIG` tier, and a file that reuses another local label is skipped with a warning. Before 6.2.29 a file with a built-in's label was skipped too; **since 6.2.29 it overrides the built-in** (local > egeria > builtin), with one warning, and `builtin:<label>` still reaches the original. Also, before this fix the directory defaulted to `../`, the parent of the current working directory; it now defaults to `~/.pyegeria/report_specs`.

Tip: You can also export the built‑in specs, edit them, and load the edited file as a `CONFIG` entry:

```python
from pyegeria.view.base_report_formats import save_report_specs
save_report_specs("/tmp/builtin_specs.json")                       # dump all built‑ins
save_report_specs("/tmp/my_subset.json", ["My-User-MD"])         # dump a subset
```

### JSON structure for user specs

User JSON files contain a dictionary of FormatSets keyed by label. The shape mirrors the Pydantic models (attributes may appear as `attributes` or legacy `columns`). Example:

```json
{
  "My-Custom-Assets": {
    "target_type": "Asset",
    "heading": "My Asset Overview",
    "description": "Compact asset table for my team",
    "family": "AssetCatalog",
    "formats": [
      {
        "types": ["LIST"],
        "attributes": [
          {"name": "Display Name", "key": "display_name"},
          {"name": "Type", "key": "type_name"},
          {"name": "GUID", "key": "guid", "format": true}
        ]
      }
    ]
  }
}
```

Drop this file into your user report specs directory, as described in [Where pyegeria looks for user specs](#where-pyegeria-looks-for-user-specs).

### Notes on keys and labels

- Column `key` **should be camelCase**. Both cases work for value lookup (the formatter tries exact, then `to_camel_case`, then uppercase for `GUID`), but camelCase is required for Mermaid detection — snake_case keys will not be recognised as Mermaid content and the graph will not be fenced. See the [Mermaid Graphs](#mermaid-graphs-and-normalization) section for details.
- Display labels (`name`) are prettified (camel/snake → Title Case) and respect common acronyms (GUID, ID, QN, API, UI). The `name` does not affect mermaid detection except for a small list of generic titles ("Mermaid Graph", "Anchor Mermaid Graph", etc.).
- Use `detail_spec` to implement master–detail links. The linked spec’s `target_type` drives automatic promotion of nested elements when possible.

---

### Generating Report Specs from Commands

pyegeria includes powerful tooling to automatically generate report specifications, markdown templates, and help documentation from Egeria command definitions (compact commands). This ensures that the metadata you create or update using Dr.Egeria can be consistently reported on and documented using the exact same attribute names and types.

### Using the `refresh_specs.py` script (Recommended)

The easiest way to keep your documentation, templates, and report specs fully synchronized with your compact command schemas is to use the `refresh_specs.py` utility. This script executes all three generation steps in sequence.

```bash
## Run the complete refresh process (generates both Basic and Advanced)
uv run commands/tech/refresh_specs.py

# Automatically persist generated report specs to base_report_formats.py
uv run commands/tech/refresh_specs.py --merge-reports

# Filter generation by usage level and family (applies to markdown templates)
uv run commands/tech/refresh_specs.py --usage-level Advanced --family AssetCatalog
```

When `--usage-level` is omitted, the script refreshes **both** Basic and Advanced
templates and help (each usage level is written to its own folder); pass
`--usage-level Basic` or `--usage-level Advanced` to restrict generation to a
single level. The script automatically picks up all `.json` files inside the
`md_processing/data/compact_commands` directory, resolves attributes across
inherited bundles, and regenerates all artifacts.

### Using the individual CLI Tools

If you need finer control over a specific generation step, you can run the individual modules:

**1. Generating Report Specs (`gen-report-specs`)**
Converts compact commands into PyEgeria `FormatSet` specifications.

```bash
# Get help and see available options
hey_egeria tech gen-report-specs --help

# Generate report specs from the default compact_commands directory and list them
hey_egeria tech gen-report-specs --emit dict --list

# Persist generated specs into pyegeria/view/base_report_formats.py
hey_egeria tech gen-report-specs --merge
```

**2. Generating Markdown Command Templates**
Creates skeleton `.md` files for writing Dr.Egeria metadata updates. Output files are saved to `sample-data/templates/`.

```bash
uv run -m commands.tech.generate_md_cmd_templates --usage-level Basic
```

**3. Generating Dr. Egeria Glossary Help**
Creates glossary term definitions that describe the Dr.Egeria commands. Optional `--advanced` flag includes advanced attributes and commands. Output files are saved to your configured Egeria Inbox directory (by default, `sample-data/egeria-inbox/`).

```bash
uv run -m commands.tech.generate_dr_help --advanced
```

### Key Features of Generation:
- **Compact Command Exclusivity**: The tooling natively supports Egeria's precise compact command JSON schema.
- **Attribute Resolution**: Automatically resolves attributes from inherited `bundles` and `attribute_definitions` across all JSON files in the compact commands directory.
- **Persistent Updates (`--merge`)**: When generating report specs, the tool can automatically update the managed `# --- GENERATED FORMAT SETS ---` section in `pyegeria/view/base_report_formats.py`. This is the easiest way to keep your built-in report specs in sync with your command definitions.

### Example: Syncing with Dr.Egeria Commands

If you have added new commands or attributes to the JSON files in `md_processing/data/compact_commands` and want them available for immediate use across reporting, templates, and documentation:

```bash
# Safely regenerate everything and update your python source file
uv run commands/tech/refresh_specs.py --merge-reports
```

---

### Question Specs: Linking Reports to User Intent

A *question spec* describes the human questions a report is designed to answer and associates those questions with user *perspectives* (roles or viewpoints). This metadata lives inside each `FormatSet` as the `question_spec` attribute and can also be persisted into the Egeria metadata repository as first-class entities.

#### Entity Model

When persisted into Egeria, four entity types are created:

| Entity Type | QN Prefix | Description |
| :--- | :--- | :--- |
| `ReportType` | `ReportType::` | Identifies a class of report — one per `FormatSet` with a `question_spec` |
| `QuestionSpec` | `QuestionSpec::<label>::<n>` | A folder grouping related questions; linked to a `ReportType` |
| `Question` | `Question::` | A `GlossaryTerm` classified as a `Question` |
| `Perspective` | `Perspective::` | A viewpoint (role/persona) that scopes one or more Questions via a `ScopedBy` link |

#### Dr. Egeria Commands

Dr. Egeria supports four markdown commands for creating question-spec entities:

- **Create Report Type** — creates a `ReportType` collection
- **Create Question Spec** — creates a `QuestionSpec` folder collection and links it to its parent `ReportType`
- **Create Question** — creates a `Question` (`GlossaryTerm` with the `Question` classification)
- **Link Perspective to Question** — creates a `ScopedBy` relationship from a `Perspective` entity to a `Question`

#### Bootstrapping: Generating Install Files

`commands/generate_question_spec_markdown.py` generates a complete set of Dr. Egeria markdown install files from `base_report_specs` and `generated_format_sets`:

```bash
python commands/generate_question_spec_markdown.py [--output-dir <path>]
# Default output: sample-data/question-spec-install/
```

Each report type with a `question_spec` produces one `.md` file containing the full sequence of `Create Report Type → Create Question Spec → Create Question → Link Perspective to Question` blocks. The generator also writes `00_perspectives.md` (all unique `Perspective` entities) and an executable `run_all.sh`.

Process all files in order:

```bash
cd sample-data/question-spec-install
bash run_all.sh [--url <platform_url>] [--server <view_server>] \
                [--userid <user_id>] [--user_pass <user_pwd>]
```

Process `00_perspectives.md` first — the report-type files reference the `Perspective` qualified names created there.

#### Bootstrapping: Direct API Migration

For direct programmatic migration (no Dr. Egeria markdown processing):

```bash
python commands/migrate_question_specs.py \
    [--url <platform_url>]  [--server <view_server>] \
    [--user <user_id>]      [--password <user_pwd>]  \
    [--dry-run]             [--label <label>]
```

- `--dry-run`: reports what would be created without making any API calls
- `--label`: repeat to migrate only specific report types (e.g. `--label Glossaries --label Projects`)
- The script is idempotent — all three entity types (ReportType, QuestionSpec, Question) are find-or-create; re-runs skip existing entities.

Qualified name format used by both scripts (and `load_egeria_report_specs`):

```
[LocalQualifier::]TypeName::DisplayName
```

The `LocalQualifier` prefix (set via `EGERIA_LOCAL_QUALIFIER` or the config profile) is prepended by `__create_qualified_name__` in `_base_server_client.py`. The migration script replicates this logic at line `_build_qn(client, type_name, display_name)`.

#### Loading Persisted Question Specs at Runtime

`load_egeria_report_specs` reads `ReportType` and `QuestionSpec` collections from Egeria and merges their `question_spec` data into the in-process registry. Results are **cached** — by default for 1 day — so that repeated calls within a session are instant.

**Python SDK:**

```python
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.view.base_report_formats import load_egeria_report_specs

client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="user", user_pwd="secret")
client.create_egeria_bearer_token()

# Normal call — skips reload if the cache is still fresh (< TTL)
load_egeria_report_specs(client)

# Force a reload regardless of the cache age
load_egeria_report_specs(client, force=True)

# Override the TTL for this call only (0 = always reload)
load_egeria_report_specs(client, ttl_seconds=3600)
```

Returns `True` if Egeria was queried and the registry updated; `False` if the cache was reused or Egeria was unreachable.

**CLI (standalone):**

```bash
load_report_specs [--force] [--ttl <seconds>] \
    [--server <view_server>] [--url <platform_url>] \
    [--userid <user>] [--password <pwd>]
```

**CLI (`hey_egeria`):**

```bash
hey_egeria cat show info load-report-specs
hey_egeria cat show info load-report-specs --force
hey_egeria cat show info load-report-specs --ttl 3600
```

**Cache control:**

| Mechanism | Effect |
| :--- | :--- |
| `PYEGERIA_REPORT_SPECS_CACHE_TTL=86400` | Default TTL (seconds). Set to `0` to always reload. |
| `--force` flag | Bypass TTL unconditionally for this call. |
| `--ttl <n>` flag | Per-call TTL override. |

**Automatic loading:**

The MCP server (`pyegeria/core/mcp_server.py`) calls `load_egeria_report_specs` automatically at startup, so `find_report_specs` tool calls are always Egeria-aware without any extra setup. For short-lived CLI commands (`run_report`, `dr_egeria`) the function must be called explicitly — the in-process cache does not persist between separate invocations.

The function handles an optional `LocalQualifier` prefix in stored QNs — it extracts the label by splitting on `"ReportType::"` regardless of what precedes it. If Egeria is unreachable the merge step is skipped silently and the function returns `False`.

#### Viewing Migrated Content

Three built-in report specs let you inspect question-spec entities that have been persisted in Egeria:

| Report Spec | What It Shows |
| :--- | :--- |
| `Questions` | All `GlossaryTerm` entities classified as `Question` |
| `Report-Types` | All `ReportType` collections |
| `Question-Specs` | All `QuestionSpec` folder collections |

```bash
run_report --report Questions      --output-format TABLE --param search_string="*"
run_report --report Report-Types   --output-format TABLE --param search_string="*"
run_report --report Question-Specs --output-format TABLE --param search_string="*"
```

---

### Discoverability & Introspection

- List all spec names (optionally grouped): `report_spec_list(show_family=True, sort_by_family=True)`
- Get a spec by name and match a type: `select_report_format("Collections", "TABLE")`
- Render a documentation page of all specs (names, types, columns): `report_spec_markdown()`
- Search by perspective or question (if a spec defines `question_spec`):
  - `find_report_specs_by_perspective("Solution Architect")`
  - `find_report_specs_by_question("list my teams")`

---

### Report Commands (CLI)

pyegeria provides ready-to-use CLI commands to discover and run report specs.

- `list_reports`: Lists all registered report specs with their Family, Description, and Available Formats. Use `--search/-s` to filter by name, family, description, or aliases.
- `run_report`: Executes a report spec and renders output:
  - `TABLE`: paged, interactive Rich table in the terminal
  - `MD`/`REPORT`/`FORM`/`LIST`/`HTML`: writes a timestamped file to your outbox
  - `DICT`: returns machine-readable data (materialized)
  - `JSON`: returns raw machine-readable data from Egeria
- `load_report_specs`: Refreshes the in-process report-spec registry from Egeria (ReportType collections and their QuestionSpec question data). Results are cached; use `--force` to reload unconditionally.

Examples

```bash
# List all reports (paged table)
poetry run list_reports

# Filter by keyword (matches name, family, description, aliases)
poetry run list_reports --search glossary

## Run a report as a table (Rich table in terminal)
poetry run run_report --report “Digital-Products” --output-format TABLE --param search_string=”*”

## Run a report and save Markdown to the outbox
poetry run run_report --report “My-User-MD” --output-format REPORT --param search_string=”*”

# Pass multiple parameters in snake_case
poetry run run_report \
  --report “Collections” \
  --output-format TABLE \
  --param search_string=”*” \
  --param page_size=100 \
  --param start_from=0

# Or pass parameters as JSON (snake_case keys)
poetry run run_report --report “Collections” --output-format TABLE \
  --params-json '{“search_string”:”*”,”page_size”:100,”start_from”:0}'

# Load (or refresh) question specs from Egeria into the local registry
poetry run load_report_specs
poetry run load_report_specs --force              # bypass cache
poetry run load_report_specs --ttl 3600           # re-check every hour
```

From the main CLI (`hey_egeria`):

```bash
hey_egeria cat show info list-reports --search user
hey_egeria cat show info “Run Report” --report “Digital-Products” --output-format TABLE --search-string “*”
hey_egeria cat show info load-report-specs
hey_egeria cat show info load-report-specs --force
```

Notes
- Unknown report vs unsupported format: error messages clearly distinguish a mistyped/unknown report from a known report that does not support the requested `output_format`. Hints include the list of available formats and suggest running `list_reports`.
- CLI parameters must use snake_case (see “Parameter naming: snake_case vs camelCase”).
- `load_report_specs` only affects the current process — the cache is in-memory and does not persist between separate CLI invocations.

---

### MCP tools for reports

If you use an MCP-compatible client, pyegeria exposes report-related tools via a lightweight server at `pyegeria/core/mcp_server.py`.

Start the server

```bash
# Using Poetry
poetry run pyegeria-mcp

# If installed via pip, the same entry point is available as a script
pyegeria-mcp
```

Exposed tools and parameters

- `list_reports(output_type="DICT"|"JSON"|"MARKDOWN")`
  - Lists eligible report specs (those that support `DICT` or `ALL`), including description, target type, and required/optional params.
- `describe_report(name, output_type="DICT"|"JSON"|"MARKDOWN")`
  - Returns the schema and details for a single report spec. `MARKDOWN` maps to a narrative description; `JSON` maps to DICT.
- `find_report_specs(perspective=None, question=None, report_spec=None, output_type="DICT"|"JSON"|"MARKDOWN")`
  - Searches report specs by perspective and/or example question (when provided in the spec’s `question_spec`). Use `"*"` to skip a filter.
- `run_report(report_name, search_string="*", page_size=0, start_from=0, starts_with=None, ends_with=None, ignore_case=None, output_type="DICT"|"JSON"|"MARKDOWN")`
  - Executes a report spec. Prefer `output_type="DICT"` for tool consumption; `MARKDOWN` returns a human-readable narrative.

Conventions
- Parameters are snake_case, matching the rest of pyegeria. The server adapts these to on‑wire camelCase when calling Egeria.
- Return payloads follow the normalized shapes used across pyegeria’s report executor:
  - `{"kind":"empty"}` when no rows are found
  - `{"kind":"json","data": ...}` for DICT/JSON results
  - `{"kind":"text","mime":"text/markdown"|"text/html","content": ...}` for narrative outputs

Tip: You can combine `find_report_specs` to discover candidates and then `run_report` with the same report name.

---

### Analytic functions and chart output formats (SERIES, BAR, PIE)

A `FormatSet`'s `action` (`ActionParameter`, in `pyegeria/view/_output_format_models.py`) has **two independent execution paths**, mirroring the two function slots Dr.Egeria commands have always carried (`find_method`/`find_constraints` and `extra_find`/`extra_constraints`):

- `function` (from `find_method`): an element-query call, typically a `pyegeria.omvs.*` method (e.g. `MetadataExpert.find_metadata_elements_with_string`) — returns a list of Egeria elements, formatted per-column by the `FormatSet`'s `Format.attributes` (the TABLE/DICT/REPORT/MERMAID path already documented above).
- `analytic_function` (from `extra_find`): a registered analytic function's name (a dotted path is refused from 6.2.19; see below), naming a plain Python function — typically in `pyegeria.view.overview_metrics` — that takes an already-constructed, already-authenticated client as its first argument (or first two, for a function needing two client roles — see `_bind_client_args` in `pyegeria/view/format_set_executor.py`) and returns an already-aggregated scalar/dict/list result, **not** raw elements. Deliberately no fixed required/optional-param whitelist: every caller-supplied param is forwarded as-is (`**kwargs`); Python's own `TypeError` on an unexpected keyword is the validation. Which names and paths are accepted is described under [Which functions a report spec may name](#which-functions-a-report-spec-may-name).

A `FormatSet` can declare either path, or both (in which case the analytic path only runs for `SERIES`/`BAR`/`PIE` output formats — see below — and the find path handles everything else, unchanged).

**Running the analytic path — output format selects the shape:**

- `DICT` / `JSON` (or any non-chart format): the function's raw result is returned as-is (`{"kind":"json","data": <scalar|dict|list>}`) — no per-column formatting, since there's no element list to format. `DICT` and `JSON` are indistinguishable here by design (both return the same raw payload); the distinction only matters on the find path, where different output types can select different rendering.
- `SERIES`: expects a time-series shape — `List[Dict]` of `{label, date, <metric>: value, ...}` points (e.g. `overview_metrics.growth_series`) — wrapped as a Vega-Lite **line** chart, one line per numeric metric key.
- `BAR` / `PIE`: expects a category-breakdown shape — either a plain `{category: value}` dict, or a `List[Dict]` with one label-like field and exactly one numeric field (e.g. `overview_metrics.counts_by_type`'s `[{label, type, count}, ...]`) — wrapped as a Vega-Lite bar or pie/donut chart. If the result is a dict with fewer than 2 top-level numeric fields, the executor looks one level down for a nested dict-of-numerics (e.g. `governed_coverage`'s `byClassification`) rather than charting a single meaningless bar/slice — see `_as_category_value_dict` in `format_set_executor.py`.

All three chart formats are dispatched *before* the normal Format-row lookup (`exec_report_spec`), since no `FormatSet` needs to declare a `SERIES`/`BAR`/`PIE` `Format` row for this to work — only `DICT`/`JSON` (or whatever find-path formats it also supports) need a declared row.

**Result state (the envelope).** A routine can say how sure it is by returning a state with its result: `measured`, `nothing_found`, `not_established` or `not_applicable`, plus a reason. The executor recognises a dict with `state`/`state_reason` (and an optional ready-made `subtitle`), a dict with `resultState`/`resultStateReason`, a nested `envelope` dict in either style, or an object whose `envelope` attribute has `result_state`/`result_state_reason`. When it finds one:
- every output shape gets `"envelope": {"state", "reason", "subtitle"}` beside `kind`/`data`;
- a chart gets the subtitle on it (`title: {"text", "subtitle"}`);
- **a chart is drawn only for an established answer: `measured`, or `nothing_found`** (the routine read the record and the count really is zero, so a chart of zeros is honest).
- **`not_established` and `not_applicable` return a sentence, not data** (ISSUE-171), on every output format:

  ```json
  {"kind": "absent",
   "content": "Coverage was not measured: the catalog could not be read.",
   "absence": {"state": "not_measured", "sentence": "...", "reason": "could not open the ODS", "declared": true},
   "envelope": {"state": "not_established", "reason": "could not open the ODS", "subtitle": "..."},
   "detail": {"...": "the routine's partial result, if any"}}
  ```

  There is no top-level `data`, so no table or tile can show placeholder zeros as an answer. A consumer should show `content`. `detail` is there for diagnosis, not display.
- `nothing_found` keeps its data or chart and gains the same `absence` block (state `nothing_found`). If the function declares sentences, its chart subtitle is the declared one.

The `absence` states are the four of trellis-analytics: `not_measured`, `not_permitted`, `not_applicable` and `nothing_found`. `not_established` becomes `not_measured`, unless the result itself says `"absence": "not_permitted"`; the reason text is never parsed to guess. The sentence is the function's declared one (see [Declaring what results mean](#declaring-what-results-mean)). A function with no declaration gets words built from its own reason, with `declared: false`.

A result without an envelope is returned exactly as before. A result that is a pydantic model is returned as plain data (`model_dump`). See ISSUE-139/140/171.

**Non-JSON arguments are declared `inputs` (RS-W2-3).** Report-spec params are JSON. A routine's other arguments (Egeria clients, readers, the viewer, the subject in view) are its registry entry's `inputs`, one role word per leading positional argument, in order:

```python
AnalyticFunctionSpec(
    name="semantic_grounding",
    function="pyegeria.view.overview_metrics.semantic_grounding",
    inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
)
```

The role words are `egeria_client:<Class>`, `reader:<name>`, `viewer` and `subject`. Full detail, a custom supply and the errors are under [Routines, declarations and roles](#routines-declarations-and-roles). The executor asks a role supply for each input before the routine runs and passes them positionally; declared params follow by name. No parameter name is read to decide what to pass. `exec_report_spec(..., supply=...)` takes an environment's own supply (`pyegeria.view.role_supply.RoleSupply`). Without one, `PlainSupply` hands the caller's single `EgeriaTech` to every `egeria_client` input whose class it serves, and refuses readers, the viewer and the subject. A role the supply cannot provide raises `RoleRefused` with the supply's words before any stage runs. A routine that declares no `egeria_client` input still connects to nothing (ISSUE-137).

Check 5 refuses, at load and at run with the same words, a routine whose binding takes leading `mgr`/`ce`/`expert`/`client` arguments that its `inputs` do not declare. The fix is to declare them. See the compatibility note under [Routines, declarations and roles](#routines-declarations-and-roles) and the checks under [Will this spec run?](#will-this-spec-run-load-time-resolution).

`analytic_binders` (ISSUE-138's factories) was removed in RS-W2-3 PR-B. For one release a spec that still carries the key loads, and the key is ignored: silently when empty, with a `DeprecationWarning` and a logged warning when not. Declare a reader as a `reader:<name>` input instead, and have the environment's supply provide it. The recipe is under [Routines, declarations and roles](#routines-declarations-and-roles); the key will be refused in a later release.

**`analytic_spec_params` are defaults, not pins.** Unlike the find path's `spec_params` (always fixed — a caller-supplied value for the same key is silently overridden), `analytic_spec_params` set a *default* that a caller-supplied value for the same key overrides. This is what lets a report spec like the demo "Element Count by Type" (which pins `type_name: "GlossaryTerm"` as its default) actually be re-pointed at a different type at run time instead of being permanently locked to the demo's own default.

**The analytic function registry** (`pyegeria/view/analytic_registry.py`) is a separate, hand-written catalog of every analytic function available to point `analytic_function` at — `AnalyticFunctionSpec` entries carry `function` (dotted import path, which is the entry's one python binding), `description`, `returns` (result shape), `params`, `inputs` (role words) and a `generic: bool` flag with a `binding_note`; each entry is also a `RoutineDeclaration` (see [Routines, declarations and roles](#routines-declarations-and-roles)):
- `generic=True` — what the function counts/aggregates is itself a parameter (e.g. `count_elements(type_name=...)`), freely retargetable at any element type via `analytic_spec_params`.
- `generic=False` — the vocabulary is hardcoded in the function body (e.g. `governed_coverage` always counts a fixed set of governance classifications); a report spec can still point at it, but always gets that one fixed metric.

**Manifest fields (ISSUE-149).** `AnalyticFunctionSpec` also carries optional fields for analytic libraries such as trellis-analytics. All have defaults, so existing entries are unchanged:
- `kind`: `routine` (runs in the caller's process, the default) or `step` (a survey-style step);
- `source`: where the data comes from, as free text. Known values are `ods`, `egeria` and `resource`; any other value logs a warning and is kept;
- `version`;
- `envelope: bool` (the result carries a state, see above);
- `annotation_type` (a step's result type);
- `resource_types`;
- `family`: the same word and meaning as `FormatSet.family`; in Egeria a family is a Collection;
- `tags`.

`get_analytic_registry()` combines four tiers, mirroring `base_report_formats.py`'s report-spec registry shape:
- `BUILTINS`: the `overview_metrics` functions shipped in pyegeria;
- `CONFIG`: JSON files and loader functions named by `PYEGERIA_ANALYTIC_FUNCTIONS_JSON` / `PYEGERIA_ANALYTIC_FUNCTIONS_MODULES`;
- installed packages, through entry points (see [Registering functions from an installed package](#registering-functions-from-an-installed-package));
- `RUNTIME`: `register_analytic_functions(...)` calls.

A name defined twice raises `AnalyticRegistryCollision`, except that an installed package's entry clashing with a built-in or config name is skipped and reported, so one package can't break the registry for everyone.

#### Which functions a report spec may name

A report spec is data: it can come from a user's report-spec directory or a config file. So `exec_report_spec` does not import whatever it names (ISSUE-169). `analytic_function` and an action's `fetch`/`analytic` steps are resolved in this order:

1. **A registered name** resolves to that entry's `function`. This is the form report specs use.
2. **A dotted path that a registered entry declares** is trusted, but not in a report spec (below).
3. **Any other dotted path** must be in a module under an allowed prefix. The defaults are `pyegeria` and `trellis_analytics`. Set `PYEGERIA_ANALYTIC_MODULE_PREFIXES` (comma-separated) to change the list. A prefix is a package boundary: `pyegeria` admits `pyegeria.view.x`, not `pyegeria_extras.x`. These resolve as before and log at DEBUG.
4. **Anything else** raises `AnalyticFunctionRefused` (a `ValueError`) before anything is imported.

To use a function from your own package, register it (any tier above, usually an entry point), or add your package to `PYEGERIA_ANALYTIC_MODULE_PREFIXES`. Registering is better: the function then appears in the registry for authoring tools, and it can carry a declaration.

**Report specs name functions by registered name (ISSUE-173).** A report spec's `analytic_function`, or a function-valued parameter such as `metric_trend`'s `metric_path`, must be a registered name. From 6.2.19 anything else, including a dotted path that steps 2 and 3 would accept, raises `AnalyticFunctionRefused` before any import. The message names the registered name to use or, if there is none, says to register the function. (6.2.18 still resolved dotted paths with a `DeprecationWarning`.) Steps 2 and 3 still apply to code rather than report-spec data: registry entries themselves (`AnalyticFunctionSpec.function`, an action's `fetch`/`analytic`) keep their dotted paths.

#### Declaring what results mean

`AnalyticFunctionSpec.declaration` (optional, ISSUE-170) lets a function say what its results are. A screen, report or chat answer can then show them with no code written for that function:

```python
AnalyticFunctionSpec(
    name="column_coverage",
    function="my_pkg.analytics.column_coverage",
    declaration={
        "result_kind": "measure",
        "measures": [{
            "name": "described_columns", "unit": "columns", "as_of": "asOf",
            "value_field": "described",
            "basis": {"denominator_field": "column_count", "denominator_label": "columns"},
        }],
        "absence": {
            "not_measured": "Coverage was not measured: the catalog could not be read.",
            "not_permitted": "Coverage was not measured: reading the catalog is not permitted.",
            "not_applicable": "Coverage does not apply to this resource.",
            "nothing_found": "The catalog was read and holds no columns.",
        },
    },
)
```

- `result_kind` is one of `measure`, `series`, `distribution`, `list`, `graph`, `finding`, `proposal` or `table`.
- `measures` are required for `measure`, `series`, `distribution` and `graph`. Each has a `unit` in words and an `as_of` field: a number never travels without them.
- `basis` lets a count be read as "456 of 1,236 columns" without anyone writing the "of".
- `capped_field` names a result field that is true when the value is only a lower bound.
- All four `absence` sentences are required. An absence is declared, never improvised; these are the sentences `kind: "absent"` returns (see the result envelope above).

This is the minimum of trellis-analytics' `Declaration`, with the same field names, so a trellis declaration validates here. Its richer blocks (extents, confidence, answers, ...) are ignored by pyegeria, not refused. An incomplete declaration is refused with a sentence naming what is missing.

#### Registering functions from an installed package

A package can add analytic functions and steps to the registry by installing (ISSUE-172). Declare an entry point in the `pyegeria.analytics` group that names an `AnalyticFunctionSpec` (or a subclass), a list of them, or a callable returning either:

```toml
[project.entry-points."pyegeria.analytics"]
my_pkg = "my_pkg.manifests:ANALYTICS"
```

- **No alias group:** the `trellis.analytics` alias was removed in 6.2.19; declare entry points in `pyegeria.analytics`.
- **When it's read:** lazily, on the first `get_analytic_registry()` call, and cached; `refresh_analytic_functions()` forgets the cache.
- **What loads:** only the manifests load then. Each function's own module is imported on its first run, so keep the manifest module free of heavy imports.
- **Resolver:** a registered function is trusted whatever its module, so installing is all a package needs to do.
- **Report specs too:** a package that also ships report specs for its functions declares them in the `pyegeria.report_specs` group (see [Where pyegeria looks for user specs](#where-pyegeria-looks-for-user-specs)), and those specs name the functions by registered name.
- **Discovering what's installed:** `get_analytic_registry()` returns every function, including entry-point ones, and `analytic_registry_payload()` gives the JSON a UI lists. `get_report_registry()` returns every report spec, including entry-point ones. Both read entry points on first call; `refresh_analytic_functions()` and `refresh_report_specs()` re-read them.
- **Failures:** an entry point that fails to load, or names something that isn't a spec, is reported by `analytic_entry_point_errors()` and in `analytic_registry_payload()["entry_point_errors"]`. It is logged at WARNING and never stops the rest loading, so "installed but not loadable" is never shown as "nothing installed".

**Demo report specs** (`pyegeria/view/analytic_demo_specs.py`) — one real, executable `FormatSet` per registered analytic function, proving each is actually runnable as a report spec (not just documented in the registry). Named `Analytic Demo - <Heading>`, family `"Analytic Function Demo"`. Each spec's `description` states plainly whether the underlying function is generic or a fixed metric (pulled from the registry, not duplicated by hand).

**Making extra report specs visible everywhere** — since 6.2.29 the demo specs ship in the report-spec seed (the `builtin` tier), so any installed pyegeria shows them to `dr_egeria`, `hey_egeria`, and every other consumer, with no config.json or env var. (From ISSUE-173 to 6.2.28 they loaded through pyegeria's own `pyegeria.report_specs` entry point, `analytic_demos`, in the `CONFIG` tier.) Another package's specs load through that entry-point group; one bad entry is skipped without affecting the rest. See [Where pyegeria looks for user specs](#where-pyegeria-looks-for-user-specs) and `refresh_report_specs()`/`get_report_registry()` in `base_report_formats.py`.

**Dashboard authoring** — a `Report` (a real Egeria asset naming a report spec plus default execution params, created via Dr.Egeria's `Create Report`) can be placed on a user-authored Dashboard Sheet (`Create Dashboard Sheet` / `Link Report to Dashboard Sheet`), alongside literal markdown text placements (`Add Text on Dashboard Sheet`) for section headers and explanations. See the "Report" family in `docs/dr_egeria_manual.md` and `pyegeria/view/_output_dashboard_sheet_models.py`.

#### Counts: not measured, and whose population

A count a routine could not establish is `None`, never `0` and never the cap (#555, 6.2.27). A native count that fails or times out, or a find fallback that stopped at its page cap (`DEFAULT_CAP`, 500, which is a lower bound and not a total), records a note: `{"count", "reason", "at_least"}`. `exec_report_spec` collects the notes around an analytic routine (`overview_metrics.recording_unmeasured`), and then:

- the output gains `"unmeasured": [ ...the notes... ]` beside `kind`;
- a scalar result that is such a count becomes `kind: "absent"`, with the reason, and the lower bound if there is one, in `content`;
- a `SERIES`/`BAR`/`PIE` over a result that holds one becomes `kind: "absent"` too: a missing bar, or a pie re-proportioned without its missing slice, would read as an answer;
- a dict or list result keeps its measured values; the unmeasured ones are `None` and the notes name each one.

Measured results are unchanged. Since 6.2.28 there is no exception to "never `0`": a `viewer` count whose query fails is `None` with a note too, whatever `strict` says (6.2.27 still returned `0` there unless `strict=True`). `strict` is still accepted, and changes nothing.

**Scans (6.2.28).** A figure computed from a scan, rather than from a native count, is only a figure when the scan read everything. The relationship scans (`orphan_glossary_terms`, `certifications_summary`, `contextualised_coverage`, `solution_component_realisation`, `active_contributors`, `engagement_series`, the DataFlow lineage in `ai_ready_assets`/`drl_readiness_gates`, and `count_relationships` in the viewer population) and the element finds of `governed_coverage`, `ownership_coverage` and `karma_leaderboard` page until Egeria returns an **empty** page. That is Egeria's paging contract: a short page is not the last page. A scan that cannot finish (more than `MAX_SCAN_PAGES` pages, 40 by default, or a server that repeats its page) is `None` with a note, never a figure from the part it read. `ai_ready_assets` and `drl_readiness_gates` read one page of Assets, which is too many to page through; when that page is full, their figures are `None` with a note (`capped` is `true`), because a page of Assets is a sample, not the catalog. (`stale_assets` did the same in 6.2.28; see **Counting by update time** below.) In 6.2.27 `orphan_glossary_terms` read one 500-relationship page that held 8 distinct terms, so it reported 1,053 orphans where all 747 relationships give 984.

**Population (#556, 6.2.27).** The count routines take `population=` (`"viewer"` or `"repository"`; `scope=` is a deprecated alias and passing both with different values is a `ValueError`). They now default to `"repository"`: totals count the whole repository, **including elements the viewer may not be able to see**, via the native push-down count. This is a deliberate interim choice until zone-aware push-down exists, and the registry descriptions say so. `"viewer"` is an explicit opt-in; `scope=None` omits the argument and takes the server default. A failed repository count has no find fallback, so it is `None` with a note, strict or not. Routines that scan elements (for example `certifications_summary`, `orphan_glossary_terms`) stay viewer-scoped, and no payload mixes the two populations in one ratio. `stale_assets` is in the repository population from 6.2.29.

**Counting by update time (6.2.29).** Egeria cannot count by an update-time condition: a search condition reaches only an element's own properties, and `updateTime` is in its header, so a count with `updateTime LT <cutoff>` answers 0. Egeria can sort by update time (`sequencingOrder: LAST_UPDATE_OLDEST`), and `startFrom` is an offset into the repository's own sorted rows: a row the viewer cannot see keeps its offset and comes back as an empty one-row page. So `stale_assets` counts the Assets last updated before the cutoff as the offset of the first row updated at or after it, found by bisection: about log2(total / 25) one-row reads, then one read of the last window of at most 25 rows (12 reads for 37,000 Assets). A hidden row between two rows updated before the cutoff was updated before it too, so `staleCount` is in the repository population, like its `assetTotal`. Only hidden rows exactly at the cutoff cannot be placed; then `staleCount` is `None` with a note giving the range. Live, as `erinoverview` on 2026-11-09: 287 of 37,568 Assets in 13 s, where 6.2.28 took 35 s to report "not measured".

**Distinct relationship ends cannot be counted natively.** `orphan_glossary_terms` therefore still scans every `SemanticAssignment` relationship (about 8 KB each). Its term total is a viewer count, to match the scan's population, and that is slow (13.5 s live for 1,061 terms, against 0.7 s in the repository population); from 6.2.29 it runs on its own thread while the scan pages.

#### Routines, declarations and roles

A routine is a registry entry (`AnalyticFunctionSpec` in `pyegeria/view/analytic_registry.py`) that says how it is called and what it returns. The declaration lives in the registry, **not in the report spec**: a spec only names the routine (`action.analytic_function`) and supplies parameters. The model behind it is `RoutineDeclaration`; `AnalyticFunctionSpec.routine()` returns an entry as one, and `get_routine_registry()` returns them all (an entry that breaks a declaration rule is listed by `routine_declaration_errors()` instead of raising).

A routine declares:

| Field | Meaning |
|---|---|
| `bindings` | How it is reached: a list of `Binding(kind, target)`, `kind` one of `python`, `egeria_query`, `sql`, `step`. At most one `python` binding; `function` and the python binding are one value (name it once). pyegeria runs `python` bindings only: a routine with none is listed as unrunnable (check 1), by name. |
| `inputs` | Role words, one per leading positional argument, in order (below). |
| `params` | `ParamDeclaration(name, type, default, required, category, description)`, bound **by name** after the inputs. `category` is `content` (what data comes back), `shape` (how it is arranged) or `performance` (operational tuning); the default is `content`. A parameter is required or has a default, never both. |
| `declaration` | What the results mean (see [Declaring what results mean](#declaring-what-results-mean)), including `out`. |
| `tile_safe` | `TileSafety(safe, cap, reason)`: may it run on a tile's request path? `cap` (param to value) says within what it is safe; `reason` is the evidence and is required. |
| `admission` | `Admission(resource_types, test_only)`: where the routine may be offered (`[]` = any type). |
| `constants` | Values fixed for every call. A name is never both a constant and a parameter. |

**`out`** names the fields of the result (for a list or series, the fields of one row). `AnalyticDeclaration.out` takes three forms, and you always read it through `declaration.out_fields()`, never by iterating `out`:

- a list of field declarations (`out=[...]`, as the example below; every built-in does this);
- the name of a registered row shape (a string looked up in `ROW_SHAPES`);
- an inline shape, `{"fields": [...]}`, kept as data. A field that is an `include`, and a shape name pyegeria does not hold, are not resolved here and read as no fields.

When `out_fields()` is empty the routine declares no result fields, and check 4 notes that its columns are not checked, rather than failing them. Otherwise check 4 compares every column an analytic spec lists with these names.

**One worked declaration**, abridged from the built-in `semantic_grounding` (`analytic_registry.py`), which takes two client arguments (`...` marks what is left out; this block is illustrative, not runnable as written):

```python
AnalyticFunctionSpec(
    name="semantic_grounding",
    function="pyegeria.view.overview_metrics.semantic_grounding",
    inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
    params=[_as_of()],            # a ParamDeclaration-shaped AnalyticParam; category defaults to "content"
    returns="dict (groundingLinks, groundingPct)",
    generic=False,
    binding_note="Fixed to the SemanticAssignment relationship type -- not a parameter.",
    declaration=AnalyticDeclaration(
        result_kind="measure",
        measures=[...],           # groundingLinks, groundingPct, each with unit, as_of and population
        absence=_absence(...),    # the four sentences
        out=[_field("groundingLinks", "Grounding links", "int", unit="relationships"),
             _field("groundingPct", "Links per hundred Assets", "int", unit="percent")],
    ),
)
```

(`_as_of`, `_absence` and `_field` are the short builders at the top of the built-ins; in your own entry write `AnalyticParam(...)`, `AnalyticDeclaration(...)` and `FieldDeclaration(...)` directly.)

**The role vocabulary.** Each `inputs` entry is one of:

| Role word | What the routine receives | From |
|---|---|---|
| `egeria_client:<Class>` | a client whose methods the routine calls, e.g. `egeria_client:MetadataExpert` | `supply.client(<Class>)` |
| `viewer` | who is looking: a `Viewer(user_id, is_admin, display_name)`; a field the environment does not know is `None`, not guessed | `supply.viewer()` |
| `subject` | the resource in view: a `Subject(guid, type_name, display_name)` | `supply.subject()` |
| `reader:<name>` | a reader the environment owns (a lowercase name) | `supply.reader(<name>)` |
| `param` | not an input: a parameter is declared under `params` and bound by name | the caller |

An `egeria_client:<Class>` names the class whose methods that argument calls; use `EgeriaTech` only for an argument that calls across several classes. An input may be declared only once, and a word that is not one of these is refused with a sentence naming it (by `AnalyticFunctionSpec.routine()`, and by check 5 at load and at run).

**Binding.** Inputs are bound to the routine's leading positional parameters in declared order; declared `params` follow by name. No parameter name is read to decide what to pass. Every input is obtained before the routine's first stage runs, so a role the environment cannot provide refuses the run before anything is called.

**`PlainSupply`** (`pyegeria/view/role_supply.py`) is what plain pyegeria uses when you pass no `supply=`. It holds the caller's single `EgeriaTech`, or a factory that builds one on the first request. A routine that declares no `egeria_client` input therefore never connects or mints a token (ISSUE-137). For `EgeriaTech` and every class it proxies to (`egeria_tech_classes()`), `client(cls)` returns that one `EgeriaTech` itself, not a separate subclient (handing out per-class clients is later work). It supplies **no readers**, no viewer, and no subject: a routine that declares one runs only where an environment's own supply provides it (Resource Explorer or the Portal, or your own supply).

**A minimal custom supply** has five methods (`RoleSupply` is a runtime-checkable `Protocol`). It must return a role or raise `RoleRefused`, or a subclass, whose words say why. The example is illustrative: `MyOdsReader` stands for a reader class of your own, and "My Report Spec" for a registered spec that declares `viewer` and `reader:ods`:

```python
from pyegeria.view.role_supply import RoleRefused, NoSuchReader, Viewer
from pyegeria.view.format_set_executor import exec_report_spec

class MySupply:
    def client(self, cls):  raise RoleRefused("this environment supplies no clients")
    def viewer(self):       return Viewer(user_id="erinoverview", is_admin=False)
    def reader(self, source):
        if source != "ods":
            raise NoSuchReader(f"no reader '{source}'")
        return MyOdsReader()
    def subject(self):      return None            # None = no resource in view; the run is refused
    def refusal_words(self, kind):                  # the environment's own sentence for a missing role
        return f"My environment does not supply '{kind}'."

result = exec_report_spec("My Report Spec", params={"depth": 3}, supply=MySupply())
```

`exec_report_spec(..., supply=)` hands the supply to the analytic routine. **A find-method spec (no analytic routine) ignores `supply`:** it builds its client class from the `view_server` / `user` / `token` arguments, as before.

The errors are all `ValueError`s (`RoleRefused` subclasses it):

- `RoleRefused`: a declared input the supply cannot provide.
- `NoSuchReader(RoleRefused)`: the environment has no reader of that name.
- `CallerTokenExpired(RoleRefused)`: the environment cannot mint or refresh a client for the caller, for example because the token has expired. Only an environment's supply raises it; plain pyegeria never does.

The words a person sees are `Routine '<name>' cannot run: its declared input '<role>' is not supplied (<the supply's words>)`, built from your supply's own sentence, and the exception carries `.words`, `.role`, `.routine` and `.reason`. Subject to the same wrapping, a `viewer` input under plain pyegeria reads:

> Routine 'who_am_i' cannot run: its declared input 'viewer' is not supplied (Plain pyegeria does not know who is viewing; run this routine where the viewer is supplied (Resource Explorer or the Portal).)

> **Compatibility (6.2.26).** A routine registered from outside pyegeria (CONFIG JSON, an installed entry point, or at runtime) whose function takes leading client arguments (`mgr`, `ce`, `expert`, `client`) but declares no `inputs` is refused from 6.2.26. Before, it was bound by argument name. **Fix: declare its inputs.** The refusal reads:
>
> Routine 'uses_client' cannot run: routine uses_client's binding takes 1 leading client argument(s) and its declaration lists 0 egeria_client input(s).
>
> It is the same sentence at load (listed as unrunnable, check 5) and at run (raised as `RoleRefused`), because the resolver and the executor share one function, `spec_resolver.declared_inputs`. The built-in entries all declare theirs.

**Migrating off `analytic_binders`.** A binder `{"ods": "pkg.Reader"}` on an action becomes a declared `reader:ods` input on the routine that needed it, and the environment's supply provides the reader. See the paragraph above for the one-release grace; the warning's own words are *"analytic_binders is no longer supported and is ignored (binders for: ods). ... The key will be refused in a later release."* Remove the key from specs you own. Plain pyegeria's `PlainSupply` provides no readers (above), so a routine that needs one runs only where a supply provides it. The release that will refuse the key outright is not yet named; it is "a later release".

#### Will this spec run? Load-time resolution

A report spec is resolved **when it is loaded**, not when it is run (`pyegeria/view/spec_resolver.py`). `resolve(spec)` runs seven checks and returns a `ResolvedSpec`, or an `Unrunnable` carrying one sentence per failed check, each naming its check. An unrunnable spec is **still listed**; it is not deleted, and resolution never stops loading or changes what a run does (check 5 is the one check the executor repeats, with the same words). Each sentence reads `Spec '<name>' cannot run (check N): ...`.

| # | Check | Example of its words |
|---|---|---|
| 1 | **Names.** The find method exists on the client class the executor would use; the analytic routine is a registered name with a python binding that imports; function-valued parameters (`metric_path`) name a registered routine. | `its find method 'ServerClient.get_asset_graph' does not exist: EgeriaTech or any client it proxies to has no '_async_get_asset_graph'` |
| 2 | **Parameters.** What the executor always sends (required params, `spec_params`, `output_format`, `report_spec`) is accepted by the find method; every `analytic_spec_params` key is a parameter the routine declares. An optional parameter the method does not accept is a warning, not a failure. | `its analytic_spec_params nope is not declared by routine 'count_elements' (declared: type_name, as_of, strict, classifications, population)` |
| 3 | **Stage shapes.** Today's specs are single-stage, so there is no previous stage to check against; this is recorded as a note, not run. | (note: `a single stage, so there is no previous stage's shape to check against`) |
| 4 | **Formatter vs `out`.** Every output format is one the executor knows; a chart format needs an analytic routine; every column an analytic spec lists is a field the routine declares in `out`; every column's `detail_spec` is a registered spec. A find method declares no `out`, so a find spec's columns are not checked. | `its column 'X' reads field 'nope', which routine 'semantic_grounding' does not declare in out (declared: groundingLinks, groundingPct)` |
| 5 | **Role inputs.** The declared inputs agree with the leading client arguments the python binding takes (see the compatibility box). Which environment supplies each role is the run's, not the load's. | `routine uses_client's binding takes 1 leading client argument(s) and its declaration lists 0 egeria_client input(s)` |
| 6 | **Admission and `tile_safe`.** Recorded from the routine's declaration, never a failure. | (note: `routine 'x' declares no tile_safe`) |
| 7 | **Seeding.** The find method a spec may be seeded by is recorded. | (recorded in `ResolvedSpec.seeds`) |

Check 1 on a report spec that names a dotted path says, for example: *Report spec names analytic function 'pyegeria.view.overview_metrics.count_elements', which is not a registered name; use its registered name 'count_elements'. ...*

**Three states.**

- **Runnable:** a `ResolvedSpec`. Its `notes` say which checks did not run and why; its `warnings` are defects that bite only when a caller uses an optional parameter.
- **Unrunnable:** an `Unrunnable` with `words` and `checks`. It failed at least one check.
- **Format-only:** an `Unrunnable` of `kind="format_only"` with `checks=[1]`: the spec has no `action`, so it formats elements another call fetched (a detail view, or a command's output format). **This is not broken**: the words say `it has no action, so it formats elements another call fetched`. On the registry as of 6.2.28 there are 376 runnable, 61 format-only and no unrunnable specs (6.2.27 had 374 runnable and 2 unrunnable; see below).

**Listing them.**

```python
from pyegeria.view.base_report_formats import list_report_specs
from pyegeria.view.spec_resolver import unrunnable_specs

list_report_specs(with_status=True)
# [{"name": "Referenceable", "runnable": False, "unrunnable_reason": "Spec 'Referenceable' cannot run on its own: it has no action, ..."}, ...]

for name, spec in unrunnable_specs().items():          # format-only left out; pass include_format_only=True for them
    print(name, spec.checks, spec.words)
```

**When resolution runs.** Results are cached per spec and re-resolved when the spec object, the set of registered spec names, or the analytic registry changes. A summary (how many cannot run, and each one's words; at WARNING when any cannot, otherwise INFO) is logged on:

- the first registry load (`get_report_registry()`, which also auto-loads the CONFIG tier);
- `refresh_report_specs()`, once the first load is done;
- `load_egeria_report_specs()` (the Egeria question-spec load);
- `commands/tech/refresh_specs.py`, which resolves everything after regenerating and logs the count.

**Reading the words: the two specs that were unrunnable in 6.2.27.** Both failed check 1, both were `find` specs, and both named a find method that no longer existed, so the words said exactly what to fix:

- `Spec 'Asset-Graph' cannot run (check 1): its find method 'ServerClient.get_asset_graph' does not exist: EgeriaTech or any client it proxies to has no '_async_get_asset_graph'.`
- `Spec 'Data-Classes' cannot run (check 1): its find method 'DataDesigner.find_data_classes' does not exist: client class DataDesigner has no '_async_find_data_classes'.`

Read it left to right: *the check* (1, names), *the thing named* (`ServerClient.get_asset_graph`), *where the resolver looked* (the client class the executor would use for that name, here EgeriaTech and everything it proxies to), and *what was missing* (an `_async_` method of that name). They are listed with these words by `list_report_specs(with_status=True)` rather than being left to fail when someone runs them.

6.2.28 fixed both, as the words pointed: `Asset-Graph` now calls `AssetCatalog.get_asset_graph_by_guid` (parameter `guid`), and `Data-Classes` calls `DataDesigner.find_data_value_specifications` with `metadata_element_subtypes=["DataClass"]` (a DataClass is a DataValueSpecification subtype and shares its search).

**What `Asset-Graph` returns (6.2.28).** It declares DICT and JSON for code, and REPORT, HTML and MERMAID for people:

| Output format | Shape |
|---|---|
| `DICT` | One row: the asset itself, with its own fields and its graph fields (`Mermaid Graph`, `Anchor Graph`, `Action Graph`, `Field Level Lineage Graph`) as text. |
| `JSON` | The full graph response. |
| `REPORT`, `HTML` | The asset's fields, with the asset, anchor and action graphs rendered as mermaid. A fetch by GUID is not a search, so the report does not say "found from the search string". |
| `MERMAID` | The asset graph. |

`TABLE`, `LIST`, `MD`, `FORM` and `ALL` are not declared, and asking for them is an error that names the declared formats. `Asset-Graph` is in `NO_TABLE_FALLBACK`, so `TABLE` does not fall back to the DICT row: a table of a graph is its edges, and that edge table is planned as its own spec in Wave 3, built by a processor stage (`pyegeria/view/asset_graph.py` holds the edge helper it will use).

> **Planned, not shipped.** Report specs held in Egeria itself (synced, cached and addressed as `egeria:...`) are being built in a first stage; see `portal-docs/Internals/report-spec-pipeline-model.md` (v5.5) in egeria-workspaces. This section describes only specs loaded from files, entry points and the runtime registry.


---

### Troubleshooting

- Cell shows `---` in LIST: the value is empty or the key didn’t match. Check your column `key` (snake vs camel), and confirm your extractor/materializer emits that key.
- Detail link not shown: the master column has `detail_spec` but the value is empty. Ensure nested elements are materialized and (for generic promotion) that the linked spec’s `target_type` matches the nested element’s `type`.
- GUID not visible: include a `Column(name="GUID", key="guid", format=True)` in the detail spec. The formatter maps `guid` and formats it safely for tables/links.
- FORM output shows summaries only: this is by design to keep forms concise and editable.
- `Spec '<name>' cannot run (check N): ...` (in `list_report_specs(with_status=True)`, `unrunnable_specs()` or the log): the spec failed load-time resolution. The check number says what to look at; see [Will this spec run?](#will-this-spec-run-load-time-resolution). For check 1, fix the name (the words say what is missing or which registered name to use); for check 2, add the parameter to the routine's `params` or remove it from the spec; for check 4, correct the column `key` to a field in the routine's `out`; for check 5, declare the routine's `inputs`. A spec with `it has no action` is format-only, not broken.
- `RoleRefused`: `Routine '<name>' cannot run: its declared input '<role>' is not supplied (...)`. The environment's supply cannot provide a role the routine declares (plain pyegeria's `PlainSupply` provides the caller's `EgeriaTech` only, no readers, viewer or subject). Run the report spec where its supply provides the role, or pass `exec_report_spec(..., supply=...)` with your own. `NoSuchReader` is the same error for a `reader:<name>` the environment does not hold.
- `CallerTokenExpired`: raised by an environment's supply (never by plain pyegeria) when it cannot mint or refresh a client for the caller. Sign in again, or pass a fresh `token`. It is a `RoleRefused`, so `except RoleRefused` catches it too.
- `SearchRefused` (`pyegeria.core.request_filters`, a `ValueError`): a find-method spec asked for `*` with no type, or with a root type (`OpenMetadataRoot`, `Referenceable`). It reads `give a search string or a narrower type`. Nothing is sent to Egeria. Give a search string, or name a narrower type; `*` with a real type is allowed. A refusal reaching `exec_report_spec`'s failure log is logged at WARNING (any other `ValueError` at ERROR), and is raised either way.
- A count shows `kind: "absent"` with `Not measured: ...`, or `unmeasured` notes: a count failed, timed out or stopped at its 500-element page cap and was not reported as a total. See [Counts: not measured, and whose population](#counts-not-measured-and-whose-population).
- Pydantic validation failures in report execution: these are surfaced with structured validation details (via `print_validation_error`) before being re-raised. Start by checking field names and expected types in the printed validation table.

---

### Building and running report specs from Egeria Advisor

The Egeria Advisor web UI (`http://localhost:8880`) includes a conversational **Report Spec
Builder** that generates, saves, and re-runs report specs without writing Python.

**Lifecycle:**

| State | Location |
|---|---|
| Draft (in-progress) | `~/egeria-reports/drafts/draft_report_<ts>_<slug>.json` |
| Catalog entry (saved spec) | `~/egeria-reports/inbox/<spec_id>.md` |
| Result snapshot (after run) | `~/egeria-reports/outbox/<spec_id>_executed_<ts>.md` |

Running a spec **never removes it from the catalog** — each run writes a new timestamped
result snapshot.  The spec is always available to run again.

**Three parameter categories** (stored in the markdown spec and passed to `exec_report_spec`):

| Category | Fields | Purpose |
|---|---|---|
| Content filters | `search_string`, `status_filter`, … | What data the report returns |
| Shape defaults | `sort_field`, `sort_order`, `graph_query_depth`, … | How results are organized |
| Performance hints | `page_size`, `start_from` | Operational tuning |

**Markdown format in the catalog entry** — these three sections appear under
`## Create Report Spec` as `### Content Filters`, `### Shape Defaults`, `### Performance Hints`.
Each section is a block of `key=value` pairs.  The parser merges all three into
`ActionParameter.spec_params` at parse time, which `exec_report_spec` then uses.

**Validation:** `validate_report_spec(spec)` checks that the `ClientClass` named in
`action_function` exists in `pyegeria` and that the method exists on that class.  Validation
warnings are logged but do not block execution.

**Registration:** `register_report_spec(name, spec)` registers a `FormatSet` in the
in-memory `report_specs` / `_RUNTIME_REPORT_FORMATS` dicts.  The name used is always
`base_doc_id` (with any `_executed_<ts>` suffix stripped) — the same name passed to
`exec_report_spec`.  This ensures the lookup always hits the registration from the same run.

See `docs/user-docs/REPORT_SPEC_GUIDE.md` in the `egeria-advisor` repo for the full user
guide, and `docs/design/REPORT_SPEC_BUILDER_DESIGN.md` for the design reference.

---

### References

- Specs registry and helpers: `pyegeria/view/base_report_formats.py`
- Output engine and materializer: `pyegeria/view/output_formatter.py`
- Pydantic models for specs: `pyegeria/view/_output_format_models.py`
- Example built‑ins (including My-User‑MD): `pyegeria/view/base_report_formats.py`
- Report spec + analytic-function execution: `pyegeria/view/format_set_executor.py`
- Role supply (`RoleSupply`, `PlainSupply`, `RoleRefused`): `pyegeria/view/role_supply.py`
- Load-time resolution (`resolve`, `unrunnable_specs`, checks 1–7): `pyegeria/view/spec_resolver.py`
- Analytic function registry: `pyegeria/view/analytic_registry.py`
- Analytic function demo report specs: `pyegeria/view/analytic_demo_specs.py`
- Analytic functions themselves: `pyegeria/view/overview_metrics.py`
- Chart generators (line/bar/pie/funnel/area/scatter): `pyegeria/view/vega_utilities.py`
- Dashboard Sheet / Placement model: `pyegeria/view/_output_dashboard_sheet_models.py`

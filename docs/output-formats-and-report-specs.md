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

The `name` field has no effect on detection for pie chart or custom graph columns — only the `key` matters. For the generic flowchart case (`key='mermaidGraph'`, `name='Mermaid Graph'`) both routes happen to match, which is why it appears to work with either case.

#### Recognised camelCase mermaid keys (`MERMAID_ATTRIBUTE_KEYS`)

| Key | Typical content |
| :--- | :--- |
| `mermaidGraph` | General-purpose flowchart |
| `anchorMermaidGraph` | Anchor graph |
| `informationSupplyChainMermaidGraph` | Information supply chain |
| `fieldLevelLineageGraph` | Field-level lineage |
| `actionMermaidGraph` | Governance action graph |
| `localLineageGraph` | Local lineage |
| `edgeMermaidGraph` | Edge graph |
| `iscImplementationGraph` | ISC implementation graph |
| `specificationMermaidGraph` | Specification graph |
| `solutionBlueprintMermaidGraph` | Solution blueprint |
| `solutionSubcomponentMermaidGraph` | Solution sub-components |
| `governanceActionProcessMermaidGraph` | Governance action process |
| `collectionMermaidMindMap` | Collection mind map |
| `zoneProfileMermaidPieChart` | Zone membership profile |
| `zoneProfileAnchoredMermaidPieChart` | Zone anchored-elements profile |
| `zoneProfileAllMermaidPieChart` | Zone all-elements profile |

If you add a new mermaid attribute not in this table, add its camelCase key to `MERMAID_ATTRIBUTE_KEYS` in `pyegeria/view/output_formatter.py`.

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

You can add/override report specs without changing pyegeria’s source by providing JSON files and loading them at runtime.

### Where pyegeria looks for user specs

`pyegeria/view/base_report_formats.py` supports loading JSON files from a user directory via:

- Environment variable `PYEGERIA_USER_REPORT_SPECS_DIR` (preferred)
- Fallback env var `PYEGERIA_USER_FORMAT_SETS_DIR`

All `*.json` files in that directory are loaded and merged. Later files overwrite earlier keys on collision.

Load them early in your program:

```python
from pyegeria.view.base_report_formats import load_user_report_specs
load_user_report_specs()
```

Tip: You can also export the built‑in specs, edit them, and re‑load from your directory:

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

Place this JSON file into your user specs directory and call `load_user_report_specs()`.

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

### Troubleshooting

- Cell shows `---` in LIST: the value is empty or the key didn’t match. Check your column `key` (snake vs camel), and confirm your extractor/materializer emits that key.
- Detail link not shown: the master column has `detail_spec` but the value is empty. Ensure nested elements are materialized and (for generic promotion) that the linked spec’s `target_type` matches the nested element’s `type`.
- GUID not visible: include a `Column(name="GUID", key="guid", format=True)` in the detail spec. The formatter maps `guid` and formats it safely for tables/links.
- FORM output shows summaries only: this is by design to keep forms concise and editable.
- Pydantic validation failures in report execution: these are surfaced with structured validation details (via `print_validation_error`) before being re-raised. Start by checking field names and expected types in the printed validation table.

---

### References

- Specs registry and helpers: `pyegeria/view/base_report_formats.py`
- Output engine and materializer: `pyegeria/view/output_formatter.py`
- Pydantic models for specs: `pyegeria/view/_output_format_models.py`
- Example built‑ins (including My-User‑MD): `pyegeria/view/base_report_formats.py`

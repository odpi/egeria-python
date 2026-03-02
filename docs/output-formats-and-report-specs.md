<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Output Formats and Report Specs in pyegeria

This document explains how pyegeria turns Egeria responses into useful output using report specs (a.k.a. format sets). It covers available output formats, the report spec model, how nested/master–detail views work, and how to create and load your own specs.

If you are new to pyegeria, start with the README for installation and configuration, then return here when you need to tailor the output of find/get operations.

---

## Quick Start

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

## Output Formats

pyegeria supports multiple output types. Each report spec declares which types it supports.

- DICT: Python list/dict structures — best for programmatic use and tests. This format provides a "materialized" view where properties are cleaned up and nested elements are promoted to logical keys.
- JSON: Raw Egeria response dictionary — ideal for advanced users who need to process the exact response from the Egeria platform without any pyegeria-specific transformations.
- LIST: Markdown table (horizontal). Good for compact overviews. Nested values are automatically summarized (names/display names). If a `detail_spec` is configured, master rows include `[details]` links to rich detail sections appended below the table.
- REPORT: Rich Markdown (vertical). Ideal for deep dives. Renders nested dict/list values as hierarchical bullet lists and includes vertical detail sections for master-detail columns.
- REPORT-GRAPH: Recursive, linked Markdown report. Builds anchor-linked sections per element (by GUID), and adds link lists for peer and child/nested elements; recurses while avoiding cycles.
- FORM: Markdown suitable for Dr.Egeria editable forms. Complex values are summarized to keep the form concise and manageable.
- MD: Plain Markdown (legacy simple rendering).
- MERMAID: Mermaid graph text for supported responses.
- HTML: HTML wrapper around Markdown (when enabled in generators).

Tip: Use DICT for APIs and automation; use LIST for dashboards/browsing; use REPORT for deep, readable details; use FORM when producing updateable forms.

---

## Method Parameter Consistency

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
- Column `key` names in report specs can be snake_case or camelCase. The formatter tries exact key, then `to_camel_case`, then uppercase for well‑known IDs. Prefer snake_case for consistency.
- CLI flags like `--param page_size=50` or `--params-json '{"metadata_element_subtypes":["Asset"],"page_size":100}'` must use snake_case.

## The Report Spec Model

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

## Selecting Specs and Generating Output

Most client methods already call the output pipeline for you. Under the hood, the following helpers are used (in `pyegeria/view/output_formatter.py` and `pyegeria/view/base_report_formats.py`):

- `select_report_format(label: str, output_type: str) -> dict`: pick a spec by name/label and match the requested type (with fallback to `ALL`).
- `resolve_output_formats(entity_type: str, output_format: str, report_spec: str|dict|None)`: flexible resolver used by clients (by name, by dict, or by entity type default).
- `generate_output(...)`: orchestrates DICT/LIST/REPORT/FORM rendering given elements and a spec. It supports an `include_preamble` parameter (default `True`) to control whether the report header/preamble is included; this is automatically disabled during recursive master-detail calls to prevent redundant headings.

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

## Nested Data and the Master–Detail Pattern

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
- REPORT: renders nested dicts/lists as hierarchical markdown bullet lists (read‑only view).
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

---

## Linked Graph REPORTs (REPORT-GRAPH)

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

## Mermaid Graphs and Normalization

Many Egeria elements include Mermaid graph definitions to visualize relationships. pyegeria automatically detects and renders these in Markdown reports (`REPORT`, `REPORT-GRAPH`, `MERMAID`).

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

### Disabling Normalization
If you are using a modern Mermaid renderer that supports the native Egeria output, you can disable this transformation by changing the `NORMALIZE_MERMAID` flag in `pyegeria/view/output_formatter.py` to `False`.

---

## Deep Nesting and Recursive Aggregation

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

## Writing Your Own Report Specs

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

- Column `key` can be snake_case or camelCase. The formatter tries exact, then `to_camel_case`, then uppercase (useful for `GUID`).
- Display labels are prettified (camel/snake → Title Case) and respect common acronyms (GUID, URL, ID, API, UI).
- Use `detail_spec` to implement master–detail links. The linked spec’s `target_type` drives automatic promotion of nested elements when possible.

---

## Discoverability & Introspection

- List all spec names (optionally grouped): `report_spec_list(show_family=True, sort_by_family=True)`
- Get a spec by name and match a type: `select_report_format("Collections", "TABLE")`
- Render a documentation page of all specs (names, types, columns): `report_spec_markdown()`
- Search by perspective or question (if a spec defines `question_spec`):
  - `find_report_specs_by_perspective("Solution Architect")`
  - `find_report_specs_by_question("list my teams")`

---

## Report Commands (CLI)

pyegeria provides ready-to-use CLI commands to discover and run report specs.

- `list_reports`: Lists all registered report specs with their Family, Description, and Available Formats. Use `--search/-s` to filter by name, family, description, or aliases.
- `run_report`: Executes a report spec and renders output:
  - `TABLE`: paged, interactive Rich table in the terminal
  - `MD`/`REPORT`/`FORM`/`LIST`/`HTML`: writes a timestamped file to your outbox
  - `DICT`: returns machine-readable data (materialized)
  - `JSON`: returns raw machine-readable data from Egeria

Examples

```bash
# List all reports (paged table)
poetry run list_reports

# Filter by keyword (matches name, family, description, aliases)
poetry run list_reports --search glossary

# Run a report as a table (Rich table in terminal)
poetry run run_report --report "Digital-Products" --output-format TABLE --param search_string="*"

# Run a report and save Markdown to the outbox
poetry run run_report --report "My-User-MD" --output-format REPORT --param search_string="*"

# Pass multiple parameters in snake_case
poetry run run_report \
  --report "Collections" \
  --output-format TABLE \
  --param search_string="*" \
  --param page_size=100 \
  --param start_from=0

# Or pass parameters as JSON (snake_case keys)
poetry run run_report --report "Collections" --output-format TABLE \
  --params-json '{"search_string":"*","page_size":100,"start_from":0}'
```

From the main CLI (`hey_egeria`):

```bash
# Inside the Hey Egeria CLI
hey_egeria cat show info list-reports --search user
hey_egeria cat show info "Run Report" --report "Digital-Products" --output-format TABLE --search-string "*"
```

Notes
- Unknown report vs unsupported format: error messages clearly distinguish a mistyped/unknown report from a known report that does not support the requested `output_format`. Hints include the list of available formats and suggest running `list_reports`.
- CLI parameters must use snake_case (see “Parameter naming: snake_case vs camelCase”).

---

## MCP tools for reports

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

## Troubleshooting

- Cell shows `---` in LIST: the value is empty or the key didn’t match. Check your column `key` (snake vs camel), and confirm your extractor/materializer emits that key.
- Detail link not shown: the master column has `detail_spec` but the value is empty. Ensure nested elements are materialized and (for generic promotion) that the linked spec’s `target_type` matches the nested element’s `type`.
- GUID not visible: include a `Column(name="GUID", key="guid", format=True)` in the detail spec. The formatter maps `guid` and formats it safely for tables/links.
- FORM output shows summaries only: this is by design to keep forms concise and editable.

---

## References

- Specs registry and helpers: `pyegeria/view/base_report_formats.py`
- Output engine and materializer: `pyegeria/view/output_formatter.py`
- Pydantic models for specs: `pyegeria/view/_output_format_models.py`
- Example built‑ins (including My-User‑MD): `pyegeria/view/base_report_formats.py`

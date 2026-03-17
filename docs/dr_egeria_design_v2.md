# Dr. Egeria v2: Architecture and Design

## Overview
Dr. Egeria v2 is a command-line interface (CLI) driven metadata ingestion and processing engine built on top of the `pyegeria` SDK. It parses Markdown documents (`.md` files) styled with specific heading conventions and executes mapping functions against Open Metadata Repository Services (OMRS) and Open Metadata Access Services (OMAS).

The primary goal of the v2 redesign was to eliminate rigid class hierarchies and hardcoded Python method implementations for every Egeria operation, favoring a data-driven, specification-based approach utilizing JSON files (compact commands). This transition drastically reduces the boilerplate code necessary to support new Open Metadata types and provides robust inter-element referencing.

## Core Architecture

The architecture is built around several decoupled components that work in tandem to process a payload:

1. **The CLI & Entrypoint (`dr_egeria.py` and `md_processing/dr_egeria.py`)**
   - The user interacts via Typer command-line arguments.
   - Responsible for environment configuration, token creation, and resolving whether to fall back to the legacy v1 pipeline or use the v2 pipeline based on configuration (or absence of the legacy `commands.json`).

2. **The Dispatcher (`v2Dispatcher.py`)**
   - The heart of the v2 engine. It loads the JSON-based command specifications (`commands_*_compact.json`) during initialization.
   - It maintains a global registry mapping `Command Verb` + `Object Type` (e.g., "Create Collection") to specific specialized sub-processors or the generic `AsyncBaseCommandProcessor`.
   - It iterates through the parsed Markdown blocks and coordinates their resolution.

3. **The Parser (`parsing.py`)**
   - Responsible for extracting structured data from Markdown text.
   - **`AttributeFirstParser`**: Extracts tables or key-value pairs from Markdown blocks and maps them into dictionary structures. It trims values and standardizes keys.

4. **The Processors (`processors.py`)**
   - The actual executors that translate parsed dictionaries into `pyegeria` SDK calls.
   - **`AsyncBaseCommandProcessor`**: The generic workhorse. Uses the JSON spec to know exactly the REST API payload requirements and SDK method signatures.
   - **Specialized Processors**: `CollectionProcessor`, `CommunityProcessor`, `FeedbackProcessor`, `AssetProcessor`, etc. These inherit from `AsyncBaseCommandProcessor` and override specific lifecycle methods (`fetch_as_is`, `execute`) if the generic approach is insufficient.

5. **The SDK Client Layer (`EgeriaTech` and Subclients)**
   - Dr. Egeria interacts exclusively with `EgeriaTech`, a facade client. `EgeriaTech` relies on `__getattr__` dynamic delegation to route methods to highly specific capability clients (e.g., `AssetCatalog`, `ClassificationExplorer`, `FeedbackManager`).

## Execution Flow

The typical execution flow when a user runs `dr_egeria --input-file myfile.md --directive process` is as follows:

### Phase 1: Initialization and Parsing
1. `dr_egeria` CLI receives the request, sets up environment variables, and instantiates the `ServerClient`.
2. `parse_commands(markdown_text)` breaks the document into blocks (lists of strings) and identifies headers representing commands (e.g., `## Create Collection`).
3. The blocks are packaged into `ParsedCommand` objects.
4. The `dr_egeria` core requests `dispatcher.dispatch_commands`.

### Phase 2: Processing Pipeline
For each `ParsedCommand` in the file, the dispatcher invokes a localized processing pipeline:

1. **Routing:** The dispatcher matches the command name (e.g., "Create Collection") against its registry to instantiate the appropriate `AsyncBaseCommandProcessor` (or subclass).
2. **Parsing Attributes:** The processor uses `AttributeFirstParser` to transform the markdown lines underneath the header into a `dict` representing raw attributes.
3. **Spec Alignment:** The generic processor pulls the command's JSON specification from memory. It strictly loops through the specification's required and optional attributes, mapping the parsed Markdown values into their canonical keys.

### Phase 3: Resolution and Lookup
Before execution, Dr. Egeria must resolve references inside the input string.
1. **Local Resolution (`resolve_element_guid`):** 
   - Dr. Egeria looks at the payload values for known "Reference" or "ID" patterns (e.g., looking up a parent glossary category).
   - It first checks a localized cache dictionary (`get_element_dictionary`).
   - If missing, it uses `ClassificationExplorer`'s `get_elements_by_property_value` or `_async_get_guid_for_name` to search Egeria for the underlying GUID of the referenced qualified string.
   - If the element is marked for creation earlier in the same Markdown file, it is resolved as `(Planned: Name)`.
2. **Target State Resolution (`fetch_as_is`):**
   - If the command is an "Update", Dr. Egeria looks up the specific element currently attached to the Egeria instance by GUID or Qualified Name.
   - It explicitly favors `ClassificationExplorer` over `MetadataExplorer/Expert` due to its resilient JSON structures and broader view server compatibility, minimizing unexpected 400 errors during deep fetches.

### Phase 4: Execution / Dry-Run
1. **Validation Mode (`directive == validate`):**
   - No data is modified. Dr. Egeria uses `fetch_as_is` to determine if Update targets are missing returning actionable GUI output via `rich`.
   - The properties to be sent to Egeria are displayed in a `ValidationDiagnosis` table.
2. **Process Mode (`directive == process`):**
   - The method constructs the specific Python method signature found in the JSON spec (e.g., `client.collections.update_collection_properties(guid, body)`).
   - Values are injected dynamically via keyword arguments (`**kwargs`).
   - Standard output summarizes success or captures Python exceptions.

## Robust Inter-Command Architecture (`planned_elements`)

Because users define multiple elements in a single file (e.g., defining a Glossary, and then a Category bound to that Glossary), Dr. Egeria must track elements that don't exist yet but *will* exist.

The v2 design implements a shared context array: `context["planned_elements"]`. 
During processing, anytime an element is validated for creation or modification, its calculated Qualified Name is appended to the set. When succeeding commands attempt to resolve references against the server, hitting the `planned_elements` cache immediately short-circuits to success rather than throwing an unresolved dependency error. 

## JSON Compact Commands Design

The v2 JSON dictionary (e.g., `commands_project_compact.json`) forms the contract between Markdown parsing and SDK execution.

```json
{
  "Update Collection": {
    "module": "pyegeria.omvs.collection_manager",
    "method": "update_collection_properties",
    "description": "Updates the properties of a collection.",
    "object_type": "Collection",
    "verb": "Update",
    "attributes": [
      {
        "name": "Display Name",
        "description": "The display name of the collection.",
        "type": "string"
      },
      ...
    ]
  }
}
```

The system is extensible. To support new types or capabilities in Egeria:
1. One generates a new compact command definition.
2. The `v2Dispatcher` natively understands the new types without requiring custom hard-coded classes if they follow traditional primitive property architectures. Ensure to map verbs ("Create", "Update", "Setup", "Define") accurately.

## Integration with Report Specs

To provide a consistent experience between creating metadata with Dr.Egeria and reporting on it within `pyegeria`, the same compact command definitions are used to automatically generate Report Specs.

The tool `hey_egeria tech gen-report-specs` can be used to:
- Resolve all attributes from command bundles and definitions.
- Generate standard `FormatSet` objects for each command.
- Automatically update `pyegeria/view/base_report_formats.py` with the latest generated specs using the `--merge` flag.

This ensures that the `Display Names`, `keys`, and `descriptions` used in Dr.Egeria markdown files are identical to the labels and data fields used in pyegeria reports.

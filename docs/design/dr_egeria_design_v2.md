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
   - **Fuzzy Command Matching**: The dispatcher implements a preposition-stripping rule to improve command resolution. If an exact match for a command is not found, the dispatcher attempts a "fuzzy" match by removing common prepositions (e.g., `to`, `from`, `at`, `for`). This allows natural Markdown headers like `Link Agreement to Actor` to successfully match registry keys like `Link Agreement Actor`.
   - **Verb-Family Aware Resolution**: To prevent mis-mapping between commands sharing similar nouns (e.g., `Update External Reference` vs. `Link External Reference`), the dispatcher enforces verb-group alignment. This ensures that a creation/update synonym (like `Modify`) correctly resolves to its respective Create specification, while a relationship synonym (like `Attach`) resolves to its Link specification.
   - It iterates through the parsed Markdown blocks and coordinates their resolution.
   - **Diagnostic Feedback**: When a user executes the `process` directive, the dispatcher and its processors generate a detailed diagnostic analysis (the "Command Analysis" and "Parsed Attributes" tables). This information is printed to the console using `rich.markdown.Markdown`, ensuring the user receives immediate feedback while the resulting Markdown file remains clean and focused on the output reports.

3. **The Parser (`parsing.py`)**
   - Responsible for extracting structured data from Markdown text.
   - **`AttributeFirstParser`**: An asynchronous parser that extracts structured data from Markdown text. It handles tables, lists, and key-value pairs. It includes robust normalization for Enum and Valid Value resolution (case-insensitive, space/underscore/dash flexible) and automatically transforms input to canonical forms.
   - **Attribute Synonym Support**: The parser utilizes `attr_labels` defined in the command specifications to allow multiple user-friendly labels to map to the same canonical attribute. For example, `Category Name` can be used as a synonym for `Category`. This ensures that user-provided Markdown remains natural while mapping to strict Egeria properties.
   - **Reference Name List Support**: The parser identifies attributes with the `Reference Name List` style (such as `Folders` or `Glossary Names`) and automatically splits values containing commas or newlines into individual identifiers for lookup.
   - **Egeria-First Validation**: For `Valid Value` attributes, the parser prioritizes live validation against the Egeria server. It uses `_async_validate_metadata_value` for direct checks and `_async_get_valid_metadata_values` for list-based lookups. This allows mapping user-friendly `displayName` values (e.g., "Catalog Resource") to Egeria's internal `preferredValue`.
   - **Validation Caching**: To improve performance and reduce API traffic, the parser implements a class-level `_valid_values_cache` for metadata values fetched from the server.
   - **Dynamic Type Resolution**: The parser utilizes the `dataType` field (e.g., `int`, `integer`) to automatically cast values to the correct Python type, ensuring compatibility with the Egeria API and avoiding 400 errors due to type mismatches.
   - **Fault Tolerance**: If the Egeria server is unreachable, the parser gracefully falls back to the `valid_values` list defined in the local command specification.

4. **The Processors (`processors.py`)**
   - The actual executors that translate parsed dictionaries into `pyegeria` SDK calls.
   - **`AsyncBaseCommandProcessor`**: The generic workhorse. Uses the JSON spec to know exactly the REST API payload requirements and SDK method signatures. It coordinates the asynchronous parsing and validation of attributes before execution.
   - **`ViewProcessor`**: A specialized processor for the "View" verb. It handles generic "View <Object>" commands (like `View Report` or `View Asset`) by falling back to the Egeria report engine (`FormatSets`). This allows users to execute any defined report specification directly from Markdown.
   - **Specialized Processors**: `CollectionProcessor`, `CommunityProcessor`, `FeedbackProcessor`, `AssetProcessor`, etc. These inherit from `AsyncBaseCommandProcessor` and override specific lifecycle methods (`fetch_as_is`, `execute`) if the generic approach is insufficient.
   - **`ExternalReferenceProcessor`**: A specialized processor within the Feedback module that supports the creation and update of various `External Reference` subtypes, including `External Data Source`, `External Model Source`, `Source Code`, `Media`, and `Cited Documents`. It handles bibliographic metadata for `Cited Document` and media usage properties for `Related Media`.
   - **`FeedbackLinkProcessor`**: Extended to handle linking and detaching operations for `Media Reference`, `Cited Document`, `Comment`, `Rating`, `Like`, and `Accepted Answer` relationships, utilizing specialized SDK methods and constructing the appropriate property-rich request bodies.
   - **`CollectionLinkProcessor`**: Specialized for managing relationships between collections and other elements. It has been extended to support **Digital Product Agreement** relationships, specifically for linking and detaching `Agreement Actors` and `Agreement Items`. It handles multiple actor GUID resolution and maps them to the appropriate SDK methods.

5. **The SDK Client Layer (`EgeriaTech` and Subclients)**
   - Dr. Egeria interacts exclusively with `EgeriaTech`, a facade client. `EgeriaTech` relies on `__getattr__` dynamic delegation to route methods to highly specific capability clients (e.g., `AssetCatalog`, `ClassificationExplorer`, `FeedbackManager`).

## Execution Flow

The typical execution flow when a user runs `dr_egeria --input-file myfile.md --process` is as follows:

### Phase 1: Initialization and Parsing
1. `dr_egeria` CLI receives the request, sets up environment variables, and instantiates the `ServerClient`.
2. `parse_commands(markdown_text)` breaks the document into blocks (lists of strings) and identifies headers representing commands (e.g., `## Create Collection`).
3. The blocks are packaged into `ParsedCommand` objects.
4. The `dr_egeria` core requests `dispatcher.dispatch_commands`.

### Phase 2: Processing Pipeline
For each `ParsedCommand` in the file, the dispatcher invokes a localized processing pipeline:

1. **Routing:** The dispatcher matches the command name (e.g., "Create Collection") against its registry to instantiate the appropriate `AsyncBaseCommandProcessor` (or subclass).
2. **Parsing Attributes:** The processor awaits the `AttributeFirstParser.parse()` method to transform the markdown lines underneath the header into a `dict` representing raw attributes and validated values.
3. **Spec Alignment:** The generic processor pulls the command's JSON specification from memory. It strictly loops through the specification's required and optional attributes, mapping the parsed Markdown values into their canonical keys.

### Phase 3: Resolution and Lookup
Before execution, Dr. Egeria must resolve references inside the input string.
1. **Local Resolution (`resolve_element_guid`):** 
   - Dr. Egeria looks at the payload values for known "Reference" or "ID" patterns (e.g., looking up a parent glossary category).
   - It first checks a localized cache dictionary (`get_element_dictionary`).
   - If missing, it uses `ClassificationExplorer`'s `get_elements_by_property_value` or `_async_get_guid_for_name` to search Egeria for the underlying GUID of the referenced qualified string.
   - **Qualified Name Integrity**: The resolver treats strings containing colons (e.g., `PDR::Glossary::My-Glossary`) as single identifiers. This prevents accidental splitting of Egeria's standard Qualified Names.
   - If the element is marked for creation earlier in the same Markdown file, it is resolved as `(Planned: Name)`.
2. **Target State Resolution (`fetch_as_is`):**
   - If the command is an "Update", Dr. Egeria looks up the specific element currently attached to the Egeria instance by GUID or Qualified Name.
   - It explicitly favors `ClassificationExplorer` over `MetadataExplorer/Expert` due to its resilient JSON structures and broader view server compatibility, minimizing unexpected 400 errors during deep fetches.

### Phase 4: Execution / Dry-Run
1. **Display Mode (`directive == display`):**
   - Purely parses the document and displays identified commands and attributes without connecting to Egeria.
2. **Validation Mode (`directive == validate`):**
   - No data is modified. Dr. Egeria uses `fetch_as_is` to determine if Update targets are missing, returning actionable output.
   - Properties to be sent to Egeria are displayed in a `ValidationDiagnosis` table.
3. **Process Mode (`directive == process`):**
   - The method constructs the specific Python method signature found in the JSON spec.
   - **Merge Update Semantics**: If the command includes a `Merge Update` (Egeria's `isMergeUpdate`) attribute, it defaults to `True`. This ensures that properties and relationship memberships are additive unless the user explicitly sets it to `False` for a full synchronization.
   - Commands are executed, and secondary outcomes (like attached journal entries) are tracked via `add_related_result`.
   - Standard output summarizes success, including all generated GUIDs in the message.
   - **Console Analysis**: During `process`, the detailed "Command Analysis" is sent to the console (standard out) instead of the markdown file.

## Robust Inter-Command Architecture (`planned_elements`)

Because users define multiple elements in a single file (e.g., defining a Glossary, and then a Category bound to that Glossary), Dr. Egeria must track elements that don't exist yet but *will* exist.

The v2 design implements a shared context array: `context["planned_elements"]`. 
During processing, anytime an element is validated for creation or modification, its calculated Qualified Name is appended to the set. When succeeding commands attempt to resolve references against the server, hitting the `planned_elements` cache immediately short-circuits to success rather than throwing an unresolved dependency error. 

### Update on Planned Elements
Dr. Egeria v2 supports `Update` commands on elements that are marked as "Planned" in the current document. If an `Update` command targets an element created earlier in the same file, the processor recognizes it as a planned update. In `validate` mode, these commands are marked as `🕒 Planned` in the diagnostic summary, and the "Found" status indicates `Planned` instead of `No`, providing a realistic preview of the final state.

## Document Preservation and Provenance

Dr. Egeria v2 implements full document awareness. Unlike v1, which only extracted and re-emitted command blocks, v2:
1. Identifies all non-command text blocks (headers, paragraphs, notes).
2. Preserves these blocks in their original positions in the output file.
3. Appends a `# Provenance:` section at the end of the document to record processing metadata, including timestamps and processing mode.

## Standardized Verbs for Relationship Management

Dr. Egeria v2 standardizes the verbs used for managing relationships between elements. This ensures consistency across different object types (Terms, Governance, Collections, etc.).

### Relationship Creation and Removal
The following verbs are equivalent within their respective groups:

| Action | Supported Verbs |
| :--- | :--- |
| **Creation** | `Link`, `Attach`, `Add` |
| **Removal** | `Detach`, `Unlink`, `Remove` |

### Key Principles
1. **Verb Independence**: The verb used to establish a relationship does not restrict which verb can be used to remove it. For example, a relationship established with `Link` can be removed with `Detach`, `Unlink`, or `Remove`.
2. **Case Insensitivity**: Verbs are case-insensitive and normalized by the parser (e.g., `UnLink` resolves to `Unlink`).
3. **Relationship vs. Entity Deletion**: The `Delete` verb is reserved for the deletion of the metadata entities themselves (e.g., `Delete Glossary Term`). To remove a relationship without deleting the participating entities, use one of the relationship removal verbs (`Detach`, `Unlink`, or `Remove`).

## JSON Compact Commands Design

The v2 JSON dictionary (e.g., `commands_project_compact.json`) forms the contract between Markdown parsing and SDK execution. It supports automatic mapping from user-friendly labels to Egeria property names via the `property_name` field (e.g., `Resource Use` -> `resourceUse`).

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

## Debug Mode

Dr.Egeria v2 ships a built-in request debugger activated with the `--debug` flag (CLI) or `debug=True` kwarg (Python API). It is designed to be **non-invasive**: it patches and restores a single method, never persists state between calls, and adds zero overhead when disabled.

### What it prints

For every HTTP call made to the Egeria server, the debug mode prints three pieces of information to the Rich console:

```
[DEBUG] POST → https://host:9443/servers/viewServer/api/open-metadata/…/attach
[DEBUG] Called from: pyegeria/omvs/data_designer.py:2418 in _async_link_nested_data_field()
             ← pyegeria/core/_server_client.py:6887 in _async_new_relationship_request()
             ← md_processing/v2/data_designer.py:695 in apply_changes()
[DEBUG] Body:
{
  "class": "NewRelationshipRequestBody",
  "properties": {
    "class": "MemberDataFieldProperties"
  }
}
```

Additionally, just before each command's `apply_changes()` is called the processor prints a cyan boundary line:

```
══ DEBUG CMD: Link Data Field | display_name='CustomerID' | GUID=abc123 ══
```

### How it works

1. `process_md_file_v2` saves a reference to `BaseServerClient._async_make_request`.
2. It replaces the method on the **class** with a closure (`_debug_make_request`) that:
   - Resolves the call-chain via `inspect.stack()`, walking up to 15 frames and collecting the first 3 that are outside asyncio/stdlib internals.
   - Displays the HTTP method, URL (with query params if present), call chain, and pretty-printed JSON body.
   - Delegates to the original method unchanged.
3. `"debug": True` is placed in the shared `context` dict, making it available to every processor.
4. `AsyncBaseCommandProcessor.execute()` reads `self.context.get("debug")` and prints a per-command header before delegating to `apply_changes()`.
5. After the entire batch completes (or raises), `process_md_file_v2` unconditionally restores the original method from its saved reference.

### Usage

```bash
# CLI
hey_egeria cat process-markdown-file --input-file MyFile.md --debug

# __main__
python -m md_processing.dr_egeria --input-file MyFile.md --debug
```

```python
# Programmatic
await process_md_file_v2(input_file, output_folder, directive, client, debug=True)
```


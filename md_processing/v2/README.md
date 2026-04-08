# Dr.Egeria v2 (Async Architecture)

Dr.Egeria v2 is a complete re-architecture of the Egeria Markdown (Freddie) processing engine. It adopts an **Async-First** approach, natively integrating with the `pyegeria` SDK's asynchronous methods to provide a more efficient and extensible command processor.

## Design Goals

1. **Efficiency**: Spec-agnostic, attribute-first parsing reduces complexity from O(SpecSize) to O(ProvidedAttributes).
2. **Extensibility**: Adding new command families is streamlined through JSON specifications and class-based processors.
3. **Robustness**: Universal extraction handles commands in Markdown docs, Jupyter Notebooks, and LLM prompts.
4. **Literate Programming**: Supports modern Markdown structures like tables and lists for attribute definition.

## Design Decisions

- **Strict Specification Adherence**: The `AttributeFirstParser` is intentionally specification-agnostic. It does not contain hardcoded logic for specific verbs or objects (e.g., "Display Name should be optional for Links"). If a requirement exists in the Egeria type system, it must be defined in the JSON specification.
- **Diagnostic-First Validation**: Validation is treated as a first-class citizen. Even when a command fails to parse or execute, the system provides a diagnostic analysis including the "Command Analysis" and "Parsed Attributes" tables. When using the `process` directive, this diagnostic information is output to the console (using `rich.markdown`) to keep the resulting Markdown file clean and focused on the processed report.
- **Reference Name List Support**: Attributes can be defined with the `Reference Name List` style, allowing users to provide multiple element names or GUIDs separated by commas or newlines. The parser automatically splits these into individual identifiers for resolution.
- **Merge Update Semantics**: The `Merge Update` attribute (mapped to Egeria's `isMergeUpdate`) defaults to `True`. When `True`, synchronization operations (like folder or glossary memberships) are additive. When `False`, the system performs a full synchronization, removing existing memberships not specified in the command.
- **Inter-Command Dependency Management**: The system tracks "Planned" elements (those defined in the current markdown file but not yet in Egeria) to allow subsequent commands to resolve their GUIDs without requiring a multi-pass process.
- **Update on Planned Elements**: Dr. Egeria v2 supports `Update` commands on elements defined earlier in the same Markdown document. During validation, these are correctly identified as `🕒 Planned` and shown as "Found" in the diagnostic summary, allowing for a complete dry-run of complex metadata ingestion workflows.
- **Attribute Label Synonyms**: The parser utilizes `attr_labels` from command specifications to map multiple user-friendly labels (e.g., `Category Name`) to the same canonical attribute (e.g., `Category`). This provides flexibility in Markdown authoring while maintaining strict SDK compatibility.
- **Graceful Attribute Validation**: Attributes with styles `Enum` or `Valid Value` (those that don't match the defined set in the specification) are now flagged as **WARNINGS** instead of **ERRORS**. This allows processing to continue even if values are unknown, deferring final validation to the Egeria server.
- **Reference Resolution Resilience**: If a reference (e.g., to a term or glossary) cannot be resolved, it is flagged as a **WARNING** rather than an **ERROR**. This prevents a missing dependency from blocking the entire processing pipeline.
- **Qualified Name Integrity**: The name resolution logic treats strings containing colons as single identifiers. This ensures that Egeria's standard Qualified Names (which often use `::` as a separator) are resolved correctly without being incorrectly split by the processor.
- **Reference Candidate Heuristic**: The processor is smarter about identifying which attributes are actually element references. It avoids attempting to resolve GUIDs for attributes that are clearly data fields (like Enums, Valid Values, Dictionaries, or Integers).
- **Multi-Step Result Reporting**: Complex commands that perform multiple Egeria operations (e.g., creating a blueprint and attaching a journal entry) now track and report all secondary outcomes. This ensures users receive feedback on partial successes and all generated GUIDs.
- **Standardized Verbs for Relationship Management**: Dr. Egeria v2 standardizes the verbs used for managing relationships. Creating or adding relationships can use `Link`, `Attach`, or `Add`. Removing or detaching relationships can use `Detach`, `Unlink`, or `Remove`. These verbs are equivalent within their respective groups and are normalized by the parser.
- **Dynamic Subtype Registration**: The v2 engine automatically handles various subtypes for **Collections** and **Projects**. If a new subtype is added to Egeria (e.g., a new type of `Collection`), adding it to the `COLLECTION_SUBTYPES` list in `md_processing_constants.py` will automatically enable support with the correct unified processor (`CollectionManagerProcessor`).
- **Unified Collection Management**: All collection subtypes (Root Collections, Folders, Products, Agreements, and even Glossaries) are handled by a single, robust `CollectionManagerProcessor`. This processor automatically manages subtype-specific properties, parent relationships, status updates, and journal entries.
- **Document Preservation**: Dr.Egeria now preserves all non-command text in the input Markdown file, copying it to the output file along with processed command blocks. A `# Provenance:` section is appended at the end to track the document's processing history.
- **Non-Invasive Debug Instrumentation**: The `--debug` flag temporarily monkey-patches `BaseServerClient._async_make_request` for the duration of a single `process_md_file_v2` call. The original method is always restored (even on failure), so debug runs cannot affect subsequent calls or other tests in the same process. Per-command context is printed via `AsyncBaseCommandProcessor.execute()` before `apply_changes()` fires, giving a clear boundary between commands in the debug stream.

## Architecture Overview

### 1. Extraction (`extraction.py`)

The `UniversalExtractor` identifies DrE command blocks (`# Verb Object`) and their attributes (`## Label`). It handles various delimiters including horizontal rules (`---`, `___`).

### 2. Parsing (`parsing.py`)

The `AttributeFirstParser` maps raw Markdown attributes to the canonical command specification.

- **KeyValue Parsing**: Supports tables (`| Key | Value |`), lists (`* Key: Value`), and inline maps.
- **Enum and Valid Value Resolution**: Maps user-friendly labels (e.g., 'Draft') to Egeria internal values or integers. The resolution is case-insensitive and normalizes spaces, underscores, and dashes (e.g., `in progress`, `IN_PROGRESS`, and `in-progress` all resolve to the same value).
- **Automatic Transformation**: User input is automatically transformed to match the canonical form if a case-insensitive match is found, ensuring data consistency even with loose input.
- **Improved Property Handling**: Uses safe access for optional fields (like `Description`) and prevents runtime crashes if metadata is missing from the input document.
- **Table Formatting**: List-style attributes (like `Reference Name List`) are rendered in Markdown tables with clear comma separators (`", "`), improving readability over newline or space-joined values.

### 3. Dispatching (`dispatcher.py`)

The `v2Dispatcher` routes extracted `DrECommand` objects to their respective `AsyncBaseCommandProcessor` subclasses.

- **Safety**: Executes commands **sequentially** by default to handle inter-command dependencies (e.g., creating a term in a newly created glossary).

### 4. Processors (`processors.py`)

Every command family implements a subclass of `AsyncBaseCommandProcessor`.

- **Standard Flow**: `Parse -> Validate -> Fetch As-Is -> Action Dispatch`.
- **Generic View Processor**: The `ViewProcessor` handles any "View" verb by falling back to the Egeria report engine. It executes report specifications (`FormatSets`) and returns the results in the requested format (LIST, MD, TABLE, etc.).
- **Efficient Existence Checks**: Integrates `__async_get_guid__` into the reference resolution logic, providing a more reliable and efficient method for verifying if elements already exist in Egeria.
- **Secondary Operation Reporting**: Uses `add_related_result` to track operations like journal entries, membership syncing, and term linking. These are summarized in the final execution message.
- **Relationship Sync**: Includes generic logic for synchronizing one-to-many relationships, catching individual failures so that one bad link doesn't block the rest.

## Usage

### Installation

Before running, ensure the project is installed in your python environment:

```bash
pip install -e .
```

### CLI Integration

The v2 engine is integrated into the `dr_egeria` script (located in `commands/cat/dr_egeria.py`).

```bash
# --- Directive shortcuts (recommended) ---

# Validate the file against Egeria (default if no flag is given)
dr_egeria --input-file report.md --validate

# Execute all commands and make permanent changes to Egeria
dr_egeria --input-file report.md --process

# --- Full --directive option (for display mode or explicit control) ---

# Display the file contents (parse-only, no Egeria lookup)
dr_egeria --input-file report.md --directive display

# Validate (equivalent to --validate)
dr_egeria --input-file report.md --directive validate

# Process (equivalent to --process)
dr_egeria --input-file report.md --directive process

# --- Directive resolution order (highest priority first) ---
# 1. --process flag  → "process"
# 2. --validate flag → "validate"
# 3. --directive     → value provided (default: "validate")

# --- Other flags ---

# Advanced usage level (shows extra attributes; default is Basic)
dr_egeria --input-file report.md --validate --advanced

# Debug: print every Egeria API request URL and body to the console
dr_egeria --input-file report.md --process --debug

# Show only the summary table (suppress per-command analysis output)
dr_egeria --input-file report.md --process --summary-only
```

### Debug Mode (`--debug`)

When `--debug` is set, every HTTP request sent to Egeria is printed to the console **before** it is dispatched. For each request you will see:

| Item | Description |
|------|-------------|
| **Method + URL** | The HTTP verb and full endpoint, e.g. `POST → https://host:9443/…/elements/{guid}/…/attach` |
| **Call chain** | Up to 3 stack frames showing `file:line in function()`, walking from the SDK helper up to the processor that triggered the call |
| **Request body** | The JSON body pretty-printed at 2-space indent (both `dict` and pre-serialised `str` forms are handled) |

The per-command boundary is announced before `apply_changes()` is called with a cyan header line:

```
══ DEBUG CMD: Create Data Field | display_name='CustomerID' | GUID=new ══
```

Debug mode is implemented as a temporary monkey-patch of `BaseServerClient._async_make_request` that is **automatically restored** when `process_md_file_v2` returns (or raises), so it does not persist across calls.

The flag is also available when running the module directly:

```bash
python -m md_processing.dr_egeria --input-file MyFile.md --debug
```

And can be passed programmatically:

```python
await process_md_file_v2(input_file, output_folder, directive, client, debug=True)
```

### Output Summary

The processing results are presented in a concise table. The `GUID` of the processed element is included directly in the `Message` column for easier tracking. Related results (like new Journal Entries) are appended to the message as well:

`Executed Update Solution Blueprint (GUID: fb6cc...d) | Related: Journal Entry (GUID: a188...2)`

### Environment Variables

- `EGERIA_ROOT_PATH`: Base directory for inbox/outbox.
- `EGERIA_INBOX_PATH`: Path to folder containing input files.
- `EGERIA_OUTBOX_PATH`: Path to folder for processed output.

## Utility Tools

Dr.Egeria includes several utility tools to assist with command specification, documentation, and reporting. These are registered as CLI commands in the project's virtual environment.

### 1. Command Template Generator (`gen_md_cmd_templates`)

Generates Markdown templates for all supported Egeria commands, organized by family. These templates include descriptions, alternate names, and attribute details (with dynamic default value fetching).

**Usage**:

```bash
# Generate basic templates (default)
gen_md_cmd_templates

# Generate advanced templates
gen_md_cmd_templates --advanced
```

Outputs are saved to `sample-data/templates/basic/` or `sample-data/templates/advanced/`.

### 2. Help Documentation Generator (`gen_dr_help`)

Generates a comprehensive Markdown help file for all Dr.Egeria commands, intended for inclusion in "Knowledge Collections" or technical documentation.

**Usage**:

```bash
gen_dr_help
```

The resulting help file is saved to your configured Egeria Inbox path.

### 3. Report Specification Generator (`gen_report_specs`)

Converts compact command specifications into `FormatSet` (report specification) files used by the `run_report` command.

**Usage**:

```bash
# Generate report specs from compact commands
gen_report_specs md_processing/data/compact_commands --emit json
```

---

## Extending Dr.Egeria v2

To add a new command family (e.g., "AI Manager"):

1. **Define the Spec**: Add the command definitions to the JSON files in `md_processing/data/compact_commands/`.
2. **Create a Processor**:
    - Create `v2/ai_manager.py`.
    - Inherit from `AsyncBaseCommandProcessor`.
    - Implement `get_command_spec()`, `fetch_as_is()`, and `apply_changes()`.
3. **Register the Processor**:
    - Update `dr_egeria.py` to import your new processor.
    - Call `dispatcher.register("Create AI Element", AIProcessor)` in the v2 setup block.

## Engine History

The v2 async engine replaced the former sync v1 engine (previously in `md_processing/v1_legacy/`). The v1 code has been removed; all processing now goes through the v2 pipeline.

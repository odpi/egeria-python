# Dr.Egeria v2 (Async Architecture)

Dr.Egeria v2 is a complete re-architecture of the Egeria Markdown (Freddie) processing engine. It adopts an **Async-First** approach, natively integrating with the `pyegeria` SDK's asynchronous methods to provide a more efficient and extensible command processor.

## Design Goals

1. **Efficiency**: Spec-agnostic, attribute-first parsing reduces complexity from O(SpecSize) to O(ProvidedAttributes).
2. **Extensibility**: Adding new command families is streamlined through JSON specifications and class-based processors.
3. **Robustness**: Universal extraction handles commands in Markdown docs, Jupyter Notebooks, and LLM prompts.
4. **Literate Programming**: Supports modern Markdown structures like tables and lists for attribute definition.

## Architecture Overview

### 1. Extraction (`extraction.py`)

The `UniversalExtractor` identifies DrE command blocks (`# Verb Object`) and their attributes (`## Label`). It handles various delimiters including horizontal rules (`---`, `___`).

### 2. Parsing (`parsing.py`)

The `AttributeFirstParser` maps raw Markdown attributes to the canonical command specification.

- **KeyValue Parsing**: Supports tables (`| Key | Value |`), lists (`* Key: Value`), and inline maps.
- **Enum Resolution**: Maps user-friendly labels (e.g., 'Draft') to Egeria internal integers.

### 3. Dispatching (`dispatcher.py`)

The `v2Dispatcher` routes extracted `DrECommand` objects to their respective `AsyncBaseCommandProcessor` subclasses.

- **Safety**: Executes commands **sequentially** by default to handle inter-command dependencies (e.g., creating a term in a newly created glossary).

### 4. Processors (`processors.py`)

Every command family implements a subclass of `AsyncBaseCommandProcessor`.

- **Standard Flow**: `Parse -> Validate -> Fetch As-Is -> Action Dispatch`.
- **Relationship Sync**: Includes generic logic for synchronizing one-to-many relationships.

## Usage

### Installation

Before running, ensure the project is installed in your python environment:

```bash
pip install -e .
```

### CLI Integration

The v2 engine is integrated into the `dr_egeria` script (located in `commands/cat/dr_egeria.py`).

```bash
# Process a file using the v2 engine (default)
dr_egeria --input-file report.md --directive process

# Or using python directly
python commands/cat/dr_egeria.py --input-file report.md --directive process

# Explicitly disable v2 and fallback to legacy sync engine
DR_EGERIA_V2=false dr_egeria --input-file report.md
```

### Environment Variables

- `DR_EGERIA_V2`: Set to `true` (default) or `false`.
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

## Legacy Compatibility

Legacy code has been moved to `v1_legacy/`. The system will automatically fallback to this code if `DR_EGERIA_V2=false` is specified.

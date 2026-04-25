# Dr.Egeria User and Reference Manual

Dr.Egeria is a Markdown-based processing engine for Egeria. It allows users to intermix narrative text with Egeria commands using standard Markdown notation. This "literate programming" approach makes it easy to document and manage metadata workflows in a human-readable format.

## Table of Contents

1. [Overview](#overview)
2. [Syntax](#syntax)
    - [Document Structure](#document-structure)
    - [Command Blocks](#command-blocks)
    - [Attributes](#attributes)
3. [Core Concepts](#core-concepts)
    - [Directives](#directives)
    - [Planned Elements](#planned-elements)
    - [Reference Resolution](#reference-resolution)
4. [CLI Utility: dr_egeria](#cli-utility-dr_egeria)
5. [Supporting Utilities](#supporting-utilities)
    - [Template Generation (`gen_md_cmd_templates`)](#template-generation-gen_md_cmd_templates)
    - [Help Documentation (`gen_dr_help`)](#help-documentation-gen_dr_help)
    - [Command Search (`dr_egeria_help`)](#command-search-dr_egeria_help)
    - [Report Specification (`gen_report_specs`)](#report-specification-gen_report_specs)
    - [Spec Validation (`validate_compact_specs`)](#spec-validation-validate_compact_specs)
    - [Migration Tool (`migrate_dr_egeria.py`)](#migration-tool-migrate_dr_egeriapy)
6. [Advanced Configuration](#advanced-configuration)
7. [Jupyter Notebook Support](#jupyter-notebook-support)

---

## Overview

Dr.Egeria (Egeria Markdown) treats Markdown files as executable specifications for metadata operations. It parses command blocks within the file, validates them against Egeria's type system, and can optionally execute those commands to create or update metadata in an Egeria repository.

## Syntax

Dr.Egeria utilizes a specific header hierarchy to distinguish between document content, commands, and attributes.

### Document Structure

- `# Title`: Single-hash headers are reserved for document titles and narrative text. Dr.Egeria ignores these during command processing but preserves them in the output.
- `---` or `___`: Horizontal rules are used as optional delimiters between command blocks.
- **Bullet Points**: Dr.Egeria supports both `*` and `-` for list-style attributes on input. For generated output, it defaults to using `-` for better compatibility with various Markdown editors.

### Command Blocks

Commands are initiated with a double-hash header that follows the `## Verb Object` pattern:

```markdown
## Verb Object
```

- **Verb**: The action to perform (e.g., `Create`, `Update`, `Link`, `View`, `Delete`, `Provenance`, `Run`).
- **Object**: The Egeria element type (e.g., `Glossary`, `Term`, `Project`, `Asset`).

**Notes**:
- Headers starting with `##` that do not match a valid `Verb Object` pattern are treated as narrative text and preserved in the output.
- **Fuzzy Preposition Stripping**: Dr.Egeria automatically ignores prepositions like `to`, `from`, `in`, `with`, or `on` in command headers. This allows for more natural language headers such as `## Link Term to Category` which is internally treated as `## Link Term Category`.
- Standard verbs for relationship management include `Link`, `Attach`, `Add` (for creation) and `Detach`, `Unlink`, `Remove` (for removal).
- **Relationship Mapping**: For certain commands, Dr.Egeria automatically maps common aliases to canonical Egeria relationship types. For example, `ISA` or `IS A` maps to `ISARelationship`, and `HASA` or `HAS A` maps to `TermHASARelationship`.

**Examples**:
- `## Create Glossary`
- `## Link Term to Category`
- `## View Project`

### Attributes

Attributes for a command are defined using triple-hash headers followed by the attribute value on the next line(s):

```markdown
### Attribute Name
Attribute Value
```

Attributes can also be defined using lists or tables for better readability:

**List Style**:
```markdown
### Attributes
- **Glossary Name**: My Glossary
- **Description**: A sample glossary
```

**Table Style**:
```markdown
### Configuration
| Key | Value |
| --- | --- |
| Page Size | 10 |
| Start From | 0 |
```

---

## Core Concepts

### Directives

When running Dr.Egeria, you specify a **directive** that determines how the file is handled:

- **display**: Parses the file and displays the command analysis without connecting to Egeria.
- **validate**: Parses the file and validates the commands against Egeria (e.g., checks if referenced elements exist) without making any changes.
- **process**: Validates and executes the commands, making permanent changes in Egeria.

### Automatic Command Rewriting (Upsert)

Dr.Egeria implements "Upsert" logic to make metadata scripts more robust and idempotent:
- **Create → Update**: If a `Create` command is issued but the element already exists (matched by Qualified Name), Dr.Egeria automatically rewrites the command to `Update`.
- **Update → Create**: If an `Update` command is issued but the element does not exist and hasn't been "Planned" by a previous command, it is rewritten to `Create`.

### Planned Elements

Dr.Egeria supports inter-command dependencies within a single file. If a command creates a new element (e.g., a Glossary), subsequent commands in the same file (e.g., creating a Term in that Glossary) can resolve the new element's GUID even before the first command is fully committed to Egeria. These are tracked as "Planned" elements.

### Reference Resolution

Dr.Egeria attempts to resolve element references (like a parent Glossary for a Term) using:
1. **GUID**: A unique identifier.
2. **Reference Name**: A structured name in the format `Type::QualifiedName` (e.g., `Glossary::PDR::SalesGlossary`). This is the preferred way to refer to elements in Link commands.
3. **Qualified Name**: The unique string path for the element.
4. **Display Name**: The human-readable name (ambiguous matches will result in warnings/errors).

---

## CLI Utility: dr_egeria

The primary interface for processing Markdown files is the `dr_egeria` command.

**Usage**:
```bash
dr_egeria [OPTIONS] [INPUT_FILE]
```

**Key Options**:
- `INPUT_FILE`: The Markdown file to process (defaults to `dr_egeria_intro_part1.md` if omitted).
- `--validate`: Shortcut for `--directive validate`.
- `--process`: Shortcut for `--directive process`.
- `--advanced`: Enables advanced usage level, exposing additional attributes in templates and validation.
- `--summary-only`: Suppresses per-command diagnostic output, showing only the final summary table.
- `--debug`: Prints every Egeria API request URL and body to the console for troubleshooting.
- `--server`, `--url`, `--userid`: Connection details for the Egeria platform.

---

## Supporting Utilities

### Template Generation (`gen_md_cmd_templates`)

Generates a library of Markdown templates for all supported Egeria commands.

- **Usage**: `gen_md_cmd_templates [--advanced]`
- **Output**: Templates are saved to `sample-data/templates/` organized by "Family" (e.g., Governance Officer, Data Designer).

### Help Documentation (`gen_dr_help`)

Generates comprehensive Markdown help documentation describing every available command and its attributes.

- **Usage**: `gen_dr_help [--advanced]`
- **Output**: A `DrEgeria_Help.md` file is written to your configured Egeria Inbox path.

### Command Search (`dr_egeria_help`)

A CLI tool to search for Dr.Egeria command terms and their descriptions in the Egeria Glossary.

- **Usage**: `dr_egeria_help [--search <pattern>] [--mode {terminal|md|md-html}]`
- **Output**: Lists matching command terms with their summaries and detailed descriptions.

### Report Specification (`gen_report_specs`)

Converts command definitions into "FormatSets" used by the Egeria reporting engine. This ensures that the output of `View` commands in Dr.Egeria matches the expected schema.

- **Usage**: `gen_report_specs md_processing/data/compact_commands --merge`
- **Details**: 
    - The tool scans the specified directory for compact command JSON files.
    - The `--merge` flag updates the built-in report specs in `pyegeria/view/base_report_formats.py`.
    - Use `--emit code` to generate a standalone Python module.

### Spec Validation (`validate_compact_specs`)

Validates the integrity of the compact command JSON files used by Dr.Egeria.

- **Usage**: `validate_compact_specs`
- **Checks**: Verifies that attributes are correctly defined, bundles are resolvable, and required fields are present.

### Migration Tool (`migrate_dr_egeria.py`)

A utility to convert old Dr.Egeria files (using `#` for commands) to the new hierarchy (`##` for commands). The tool is **idempotent** and safe to run multiple times on the same file.

- **Usage**: `python migrate_dr_egeria.py [-r] <path>`
- **Options**: `-r` for recursive processing of directories.

---

## Advanced Configuration

Dr.Egeria respects the standard `pyegeria` configuration precedence:
1. Explicit CLI arguments.
2. Environment variables (e.g., `EGERIA_PLATFORM_URL`).
3. `.env` file in the current directory.
4. `config/config.json`.

**Key Environment Variables**:
- `EGERIA_INBOX_PATH`: Where Dr.Egeria looks for input files.
- `EGERIA_OUTBOX_PATH`: Where processed "receipt" documents are saved.
- `PYEGERIA_NORMALIZE_MERMAID`: Set to `false` to preserve native Egeria graph syntax in reports.

---

## Jupyter Notebook Support

Dr.Egeria also supports processing commands within Jupyter Notebooks (.ipynb).

**Usage**:
```bash
dr_egeria_jupyter [OPTIONS] [INPUT_FILE]
```

The processor extracts Markdown cells from the notebook, processes them similarly to standard Markdown files, and generates a new notebook containing the results.

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
4. [Supported Command Families](#supported-command-families)
5. [CLI Utility: dr_egeria](#cli-utility-dr_egeria)
6. [Python API](#python-api)
    - [process_md_file (synchronous)](#process_md_file-synchronous)
    - [process_md_file_v2 (async)](#process_md_file_v2-async)
7. [Supporting Utilities](#supporting-utilities)
    - [Template Generation (`gen_md_cmd_templates`)](#template-generation-gen_md_cmd_templates)
    - [Help Documentation (`gen_dr_help`)](#help-documentation-gen_dr_help)
    - [Command Search (`dr_egeria_help`)](#command-search-dr_egeria_help)
    - [Report Specification (`gen_report_specs`)](#report-specification-gen_report_specs)
    - [Spec Validation (`validate_compact_specs`)](#spec-validation-validate_compact_specs)
    - [Migration Tool (`migrate_dr_egeria.py`)](#migration-tool-migrate_dr_egeriapy)
8. [Advanced Configuration](#advanced-configuration)
9. [Jupyter Notebook Support](#jupyter-notebook-support)

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

## Supported Command Families

Dr.Egeria organizes its commands into "families," each corresponding to a specific area of metadata management. You can discover all available commands for each family using the `gen_md_cmd_templates` and `gen_dr_help` utilities.

### Core Families

- **Glossary**: Manage business terms, categories, and their relationships (e.g., `Create Glossary`, `Create Term`, `Link Term to Category`).
- **Data Designer**: Define data structures, fields, data classes, and value specifications (e.g., `Create Data Structure`, `Create Data Field`).
- **Actor Manager**: Manage organizational metadata, including people, teams, organizations, and roles (e.g., `Create Person`, `Create Team`, `Create Organization`, `Create Person Role`). Supports linking team structures and role appointments.
- **Project**: Manage projects and their dependencies or hierarchies (e.g., `Create Project`, `Link Project Dependency`).
- **Collection Manager**: Manage various collections of elements, including Folders, Products, and Agreements (e.g., `Create Collection Folder`, `Create Digital Product`).
- **Solution Architect**: Manage solution blueprints, components, information supply chains, and design patterns (e.g., `Create Design Pattern`, `Link Nested Design Patterns`, `Link Specialized Design Patterns`, `Link Related Design Patterns`).
- **Governance Officer**: Manage governance definitions, policies, and responsibilities.
- **Action Author**: Define governance action process flows — reusable single-step action types and multi-step processes — without writing code (e.g., `Create Governance Action Process`, `Create Governance Action Process Step`, `Link First Process Step`, `Link Next Process Step`).

### Enrichment and Metadata Management

- **Feedback**: Add comments, ratings, and informal tags to any Egeria element (e.g., `Add Comment`, `Attach Tag`).
- **External Reference**: Link Egeria elements to external resources, media, or cited documents (e.g., `Create External Reference`, `Link Media Reference`).

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

## Python API

In addition to the CLI, Dr.Egeria exposes two Python functions in `md_processing.dr_egeria` that let you drive processing programmatically — useful for scripting, testing, or embedding in a larger workflow or Jupyter Notebook.

### Configuration module

Both functions read connection details and paths from the `pyegeria` configuration system rather than requiring you to hard-code values. Call `load_app_config()` once at startup to load the appropriate `config.json` (or `config_workspaces.json`), then read values from `settings.Environment`.

```python
from pyegeria.core.config import load_app_config, settings, pretty_print_config

load_app_config()                              # reads config.json via env vars / .env
env = settings.Environment

print(env.egeria_view_server)                  # e.g. "qs-view-server"
print(env.egeria_view_server_url)              # e.g. "https://localhost:9443"
```

**Configuration precedence** (last wins):
1. Built-in defaults in Pydantic models
2. `config.json` (or `config_workspaces.json`) located via `PYEGERIA_CONFIG_DIRECTORY` + `PYEGERIA_CONFIG_FILE`
3. Environment variables (including a `.env` file in the working directory)

**Key environment variables for file discovery:**

| Variable                    | Purpose                                       |
|-----------------------------|-----------------------------------------------|
| `PYEGERIA_CONFIG_DIRECTORY` | Directory that contains your JSON config file |
| `PYEGERIA_CONFIG_FILE`      | Filename to load (default `config.json`)      |
| `PYEGERIA_ROOT_PATH`        | Base path for inbox/outbox/mermaid folders    |

**Use case 1 — local development / PyCharm (egeria-python repo)**

Point to `config/config.json` in the repo:

```bash
export PYEGERIA_CONFIG_DIRECTORY="/path/to/egeria-python/config"
export PYEGERIA_CONFIG_FILE="config.json"
export PYEGERIA_ROOT_PATH="/path/to/egeria-python/sample-data"
```

Or put the same lines in a `.env` file at the project root.

**Use case 2 — Egeria Workspaces (JupyterLab container)**

Switch to `config_workspaces.json`, which pre-sets `host.docker.internal` URLs and `/home/jovyan` paths:

```python
import os
os.environ["PYEGERIA_CONFIG_FILE"] = "config_workspaces.json"
# PYEGERIA_CONFIG_DIRECTORY should already point to the config folder in your workspace
```

Or export `PYEGERIA_CONFIG_FILE=config_workspaces.json` in the container's environment.

**Inspecting the effective configuration:**

```python
from pyegeria.core.config import load_app_config, pretty_print_config

load_app_config()
pretty_print_config(safe=True)   # prints a table showing every value and its source
```

---

### process_md_file (synchronous)

```python
from md_processing.dr_egeria import process_md_file

process_md_file(
    input_file,        # path to the .md file (absolute, or relative to EGERIA_INBOX_PATH)
    output_folder,     # subfolder inside EGERIA_OUTBOX_PATH for the receipt file; "" for root
    directive,         # "display" | "validate" | "process"
    server,            # Egeria view-server name
    url,               # Egeria platform URL
    userid,            # Egeria user id
    user_pass,         # Egeria user password
    parse_summary,     # "all" | "errors" | "none"  (default "none")
    attribute_logs,    # "debug" | "info" | "none"  (default "debug")
    usage_level,       # "Basic" | "Advanced"  (default None → "Basic")
    summary_only,      # True → suppress per-command output, show only summary table (default False)
    debug,             # True → log every Egeria API call URL + body (default False)
)
```

This is the simplest entry point. It creates the `EgeriaTech` client internally from the connection parameters you supply, then runs the async v2 engine synchronously via `asyncio.run()`.

**Example — validate a file (reading connection details from config):**

```python
import os
from pyegeria.core.config import load_app_config, settings
from md_processing.dr_egeria import process_md_file

load_app_config()
env = settings.Environment

process_md_file(
    input_file="my_glossary.md",
    output_folder="",
    directive="validate",
    server=env.egeria_view_server,
    url=env.egeria_view_server_url,
    userid=os.environ.get("EGERIA_USER", "erinoverview"),
    user_pass=os.environ.get("EGERIA_USER_PASSWORD", "secret"),
)
```

**Example — execute commands and write a receipt:**

```python
import os
from pyegeria.core.config import load_app_config, settings
from md_processing.dr_egeria import process_md_file

load_app_config()
env = settings.Environment

process_md_file(
    input_file="my_glossary.md",
    output_folder="receipts",
    directive="process",
    server=env.egeria_view_server,
    url=env.egeria_view_server_url,
    userid=os.environ.get("EGERIA_USER", "erinoverview"),
    user_pass=os.environ.get("EGERIA_USER_PASSWORD", "secret"),
    summary_only=True,
)
```

---

### process_md_file_v2 (async)

```python
import asyncio
from pyegeria import EgeriaTech
from md_processing.dr_egeria import process_md_file_v2

client = EgeriaTech(server, url, user_id=userid)
client.create_egeria_bearer_token(userid, user_pass)

asyncio.run(
    process_md_file_v2(
        input_file,        # path to the .md file
        output_folder,     # output subfolder inside EGERIA_OUTBOX_PATH; "" for root
        directive,         # "display" | "validate" | "process"
        client,            # pre-built EgeriaTech client
        parse_summary,     # "all" | "errors" | "none"  (default "none")
        attribute_logs,    # "debug" | "info" | "none"  (default "info")
        usage_level,       # "Basic" | "Advanced"  (default None → "Basic")
        summary_only,      # True → suppress per-command output (default False)
        debug,             # True → log every Egeria API call URL + body (default False)
    )
)
```

Use this form when you already have an `EgeriaTech` client (e.g., reusing a shared connection across multiple calls) or when you are working inside an existing `async` context such as a Jupyter Notebook cell using `await`.

**Example — reuse a client across multiple files:**

```python
import asyncio, os
from pyegeria import EgeriaTech
from pyegeria.core.config import load_app_config, settings
from md_processing.dr_egeria import process_md_file_v2

load_app_config()
env = settings.Environment

client = EgeriaTech(env.egeria_view_server, env.egeria_view_server_url,
                    user_id=os.environ.get("EGERIA_USER", "erinoverview"))
client.create_egeria_bearer_token(os.environ.get("EGERIA_USER", "erinoverview"),
                                  os.environ.get("EGERIA_USER_PASSWORD", "secret"))

files = ["glossary.md", "projects.md", "data_structures.md"]

for md_file in files:
    asyncio.run(
        process_md_file_v2(
            input_file=md_file,
            output_folder="batch-run",
            directive="process",
            client=client,
        )
    )
```

**Example — inside an async function or Jupyter cell (using `await`):**

```python
import os
from pyegeria import EgeriaTech
from pyegeria.core.config import load_app_config, settings
from md_processing.dr_egeria import process_md_file_v2

load_app_config()
env = settings.Environment

client = EgeriaTech(env.egeria_view_server, env.egeria_view_server_url,
                    user_id=os.environ.get("EGERIA_USER", "erinoverview"))
client.create_egeria_bearer_token(os.environ.get("EGERIA_USER", "erinoverview"),
                                  os.environ.get("EGERIA_USER_PASSWORD", "secret"))

# In a Jupyter cell, the event loop is already running — use await directly
await process_md_file_v2(
    input_file="my_glossary.md",
    output_folder="",
    directive="validate",
    client=client,
    usage_level="Advanced",
)
```

> **Note**: Jupyter kernels run their own event loop, so `asyncio.run()` will raise a `RuntimeError` inside a notebook cell. Use `await` directly (as shown above) or install `nest_asyncio` and call `nest_asyncio.apply()` once at the top of your notebook if you need to keep `asyncio.run()` calls.

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

### Configuration precedence

pyegeria resolves settings in the following order — **later sources win**:

1. Built-in Pydantic model defaults
2. JSON config file (`config.json` or `config_workspaces.json`)
3. OS environment variables and `.env` file in the working directory

CLI `--server`/`--url`/`--userid` flags (when using the `dr_egeria` CLI) override the above for that run only.

### Config file selection

The JSON file to load is located using two environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `PYEGERIA_CONFIG_DIRECTORY` | `""` | Directory containing the JSON config files |
| `PYEGERIA_CONFIG_FILE` | `config.json` | Filename to load |
| `PYEGERIA_ROOT_PATH` | `sample-data` (if present) | Base path for inbox/outbox/mermaid folders |

**Local development (PyCharm / egeria-python repo)** — use `config/config.json`:
```bash
export PYEGERIA_CONFIG_DIRECTORY="/path/to/egeria-python/config"
export PYEGERIA_CONFIG_FILE="config.json"
export PYEGERIA_ROOT_PATH="/path/to/egeria-python/sample-data"
```

**Egeria Workspaces (JupyterLab container)** — use `config/config_workspaces.json`:
```bash
export PYEGERIA_CONFIG_FILE="config_workspaces.json"
# PYEGERIA_CONFIG_DIRECTORY should already point to the config folder in your workspace
```

The file `config/env` in the repository is a **reference template** listing every supported environment variable with its default value. It is **not** a `.env` file — copy and rename it to `.env` (or source it in your shell) if you want to use it directly.

### Key environment variables

**Config discovery**

| Variable | Maps to JSON key | Purpose |
|---|---|---|
| `PYEGERIA_CONFIG_DIRECTORY` | `Pyegeria Config Directory` | Directory containing the JSON config file |
| `PYEGERIA_CONFIG_FILE` | `Egeria Config File` | JSON filename to load |
| `PYEGERIA_ROOT_PATH` | `Pyegeria Root` | Base path for inbox/outbox/mermaid folders |

**Egeria endpoints**

| Variable | Maps to JSON key | Purpose |
|---|---|---|
| `EGERIA_PLATFORM_URL` | `Egeria Platform URL` | Platform URL |
| `EGERIA_VIEW_SERVER` | `Egeria View Server` | View-server name |
| `EGERIA_VIEW_SERVER_URL` | `Egeria View Server URL` | View-server URL |
| `EGERIA_INTEGRATION_DAEMON` | `Egeria Integration Daemon` | Integration daemon name |
| `EGERIA_INTEGRATION_DAEMON_URL` | `Egeria Integration Daemon URL` | Integration daemon URL |
| `EGERIA_ENGINE_HOST` | `Egeria Engine Host` | Engine host name |
| `EGERIA_ENGINE_HOST_URL` | `Egeria Engine Host URL` | Engine host URL |
| `EGERIA_METADATA_STORE` | `Egeria Metadata Store` | Metadata store name |
| `EGERIA_KAFKA` | `Egeria Kafka Endpoint` | Kafka broker endpoint |

**Inbox / Outbox paths**

| Variable | Maps to JSON key | Purpose |
|---|---|---|
| `EGERIA_INBOX` | `Egeria Inbox` | General inbox base folder |
| `EGERIA_OUTBOX` | `Egeria Outbox` | General outbox base folder |
| `DR_EGERIA_INBOX_PATH` | `Dr.Egeria Inbox` | Dr.Egeria input folder (primary) |
| `DR_EGERIA_OUTBOX_PATH` | `Dr.Egeria Outbox` | Dr.Egeria output/receipt folder (primary) |
| `EGERIA_GLOSSARY_PATH` | `Egeria Glossary Path` | Glossary folder |
| `EGERIA_MERMAID_FOLDER` | `Egeria Mermaid Folder` | Mermaid graph output folder |

> **Note**: `EGERIA_INBOX_PATH` and `EGERIA_OUTBOX_PATH` are accepted as fallbacks for `DR_EGERIA_INBOX_PATH` / `DR_EGERIA_OUTBOX_PATH` for backward compatibility, but the `DR_EGERIA_*` names are preferred.

**User and display**

| Variable | Maps to JSON key | Purpose |
|---|---|---|
| `EGERIA_USER` | `user_name` (User Profile) | Egeria user id |
| `EGERIA_USER_PASSWORD` | `user_pwd` (User Profile) | Egeria user password |
| `EGERIA_USAGE_LEVEL` | `Egeria Usage Level` | `Basic` or `Advanced` |
| `EGERIA_JUPYTER` | `Egeria Jupyter` | `True` for notebook-friendly Rich output |
| `PYEGERIA_NORMALIZE_MERMAID` | `Egeria Normalize Mermaid` | `False` to preserve native Egeria Mermaid syntax |
| `CONSOLE_WIDTH` | `Console Width` | Console output width (characters) |

**Logging**

| Variable | Maps to JSON key | Purpose |
|---|---|---|
| `PYEGERIA_ENABLE_LOGGING` | `enable_logging` | `True` to enable file logging |
| `PYEGERIA_LOG_DIRECTORY` | `log_directory` | Directory for log files |
| `PYEGERIA_CONSOLE_LOG_LVL` | `console_logging_level` | Console log level (`ERROR`, `WARNING`, etc.) |
| `PYEGERIA_FILE_LOG_LVL` | `file_logging_level` | File log level |
| `PYEGERIA_CONSOLE_FILTER_LEVELS` | `console_filter_levels` | Comma-separated levels to display |

Call `pretty_print_config(safe=True)` from `pyegeria.core.config` to see the effective value and source (`default`, `config`, or `env`) of every setting at runtime.

---

## Jupyter Notebook Support

Dr.Egeria also supports processing commands within Jupyter Notebooks (.ipynb).

**Usage**:
```bash
dr_egeria_jupyter [OPTIONS] [INPUT_FILE]
```

The processor extracts Markdown cells from the notebook, processes them similarly to standard Markdown files, and generates a new notebook containing the results.

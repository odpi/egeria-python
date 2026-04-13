# INSTRUCTIONS.md

## Overview
This file provides default contributor and usage instructions for the main components of the Egeria Python project:
- `pyegeria` (Python SDK)
- `pyegeria commands` (CLI: `hey_egeria`)
- `dr_egeria` (Markdown processing: `md_processing`)

---

## 1. pyegeria (Python SDK)
- **Purpose:**
  - Core Python SDK for interacting with Egeria OMVS and view services.
  - Provides transport, authentication, configuration, and client APIs for Egeria metadata operations.
- **Key modules:**
  - `pyegeria/core/`: Transport, config, and base client logic.
  - `pyegeria/omvs/`: Service-specific clients (e.g., asset catalog, glossary, lineage).
  - `pyegeria/egeria_tech_client.py`: Facade for OMVS subclients.
  - `pyegeria/view/`: Output formatting and report spec registry.
- **Usage:**
  - Import and instantiate service clients for programmatic access.
  - Respect config precedence: explicit args > env vars > .env > JSON config > defaults.
  - Use async-core + sync-wrapper pattern for new OMVS operations.
- **Testing:**
  - Run unit and integration tests from the repo root with `pytest`.
  - Live Egeria server required for full integration tests.

---

## 2. pyegeria commands (CLI: hey_egeria)
- **Purpose:**
  - Command-line interface and simple TUI for invoking SDK operations and generating reports.
- **Entrypoint:**
  - `commands/cli/hey_egeria.py` (CLI)
- **Usage:**
  - Run `python -m commands.cli.hey_egeria [command] [options]` from the repo root.
  - Command groups and arguments are in snake_case.
  - Use `--help` for command documentation.
  - For report and command schema changes, regenerate specs with:
    ```
    hey_egeria tech gen-report-specs md_processing/data/compact_commands --merge
    ```
- **Compatibility:**
  - CLI and TUI must remain compatible with existing command names and argument conventions.

---

## 3. dr_egeria (Markdown processing: md_processing)
- **Purpose:**
  - Markdown parser, dispatcher, and processor pipeline for Dr.Egeria v2.
  - Executes SDK operations and produces reports from Markdown command blocks.
- **Key modules:**
  - `md_processing/v2/parsing.py`: Asynchronous parser with attribute validation cache.
  - `md_processing/v2/dispatcher.py`: Command routing and fuzzy-matching logic.
  - `md_processing/v2/data_designer.py`: Data Designer command processors.
  - `md_processing/data/compact_commands/`: JSON command and report spec registry.
- **Usage:**
  - Use Dr.Egeria CLI or import as a library for Markdown-driven automation.
  - Ensure Markdown command headers match verb/object_type conventions for correct routing.
  - When editing command attributes, keep Markdown, dispatcher, and report specs in sync.
- **Testing:**
  - Validate Markdown files with Dr.Egeria CLI or test harness.
  - Check for missing processors, spec lookup errors, and cross-reference validation.

---

## Contributor Notes
- Start with `CONTRIBUTING.md` for repo-wide guidelines.
- See `AGENTS.md` for architecture, dependency, and high-signal rules.
- Prefer extending existing specs/processors over introducing new abstractions.
- Always validate changes in all three layers: SDK, CLI, and Markdown processing.
- For config-sensitive changes, always respect precedence and test with different config sources.

---

## Troubleshooting
- If a test fails due to a missing report spec or missing find command, update the report spec registry and re-run the test.
- For HTTP 401/403 errors, check server status, credentials, and user permissions.
- For command mapping or attribute errors, ensure dispatcher, Markdown, and spec files are aligned.

---

## References
- [Egeria Python SDK Documentation](https://egeria-project.org/guides/developer/pyegeria/)
- [Egeria CLI Usage](https://egeria-project.org/guides/developer/pyegeria/cli/)
- [Dr.Egeria Markdown Automation](https://egeria-project.org/guides/developer/pyegeria/dr_egeria/)
- [Egeria Main Project](https://egeria-project.org/)


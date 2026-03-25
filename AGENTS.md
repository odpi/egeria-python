# AGENTS.md

## Contributor scope
- This file is for code contributors to `pyegeria` (SDK + CLI), not end users.
- Start with `CONTRIBUTING.md`, then use this as a repo-specific implementation map.

## Sub-project map (dependency order)
- `pyegeria/`: foundational Python SDK for Egeria; includes transport/auth/config, OMVS clients, and report generation/spec registry.
- `commands/` (`hey_egeria`): CLI + simple textual UI layer that invokes `pyegeria` clients and reporting utilities.
- `md_processing/` + `commands/cat/dr_egeria.py` (Dr.Egeria): markdown language/parser/dispatcher/processors that execute `pyegeria` operations and produce reports.
- Explicit dependency flow:
  - `pyegeria` -> `commands/` (`hey_egeria`)
  - `pyegeria` -> `md_processing/` + `commands/cat/dr_egeria.py` (Dr.Egeria)
- Change impact (`pyegeria/`): SDK API, config, report formatting/spec changes can break both `hey_egeria` and Dr.Egeria flows.
- Change impact (`commands/`): CLI/TUI argument and output behavior changes must remain compatible with existing command names and snake_case params.
- Change impact (`md_processing/`): markdown attribute/routing changes must stay aligned with `md_processing/data/compact_commands` and generated report specs.

## Architecture map (read before edits)
- `pyegeria/core/_server_client.py` + `pyegeria/core/config.py`: transport/auth and config precedence logic used by most clients.
- `pyegeria/egeria_tech_client.py`: lazy facade (`__getattr__`) across OMVS subclients; token propagation happens via `set_bearer_token()`.
- `pyegeria/omvs/*`: service implementations; new API behavior should usually be added here first.
- `pyegeria/view/output_formatter.py` + `pyegeria/view/base_report_formats.py`: materialization/rendering and report spec registry.
- `commands/cli/*`: `hey_egeria` command groups and TUI entrypoints over SDK operations.
- `md_processing/` + `commands/cat/dr_egeria.py`: Dr.Egeria v2 parser/dispatcher/processor pipeline over SDK operations.

## Contributor workflows
- Dev setup: `uv sync`, activate `.venv`, run tests from repo root.
- Default tests are unit/fake; live mode is opt-in via `pytest --live-egeria` or `PYEG_LIVE_EGERIA=1` (`tests/conftest_full.py`).
- For command/report schema changes, regenerate and merge specs with `hey_egeria tech gen-report-specs md_processing/data/compact_commands --merge`.
- Validate compatibility by exercising at least one report in `DICT`, `LIST`, and `REPORT` output modes after formatter/spec edits.

## Repo conventions that matter in reviews
- Prefer snake_case for new report `Column.key` values even though camelCase is supported.
- For nested Egeria responses with repeated names, use namespaced extractor keys (for example `template_display_name`, `target_display_name`).
- See `High-signal rules` for async-wrapper, snake_case param, and lazy-loading requirements.

## High-signal rules (verbatim)
- [HIGH SIGNAL] New OMVS operations should follow async-core + sync-wrapper pattern (`_async_*` + public sync method).
- [HIGH SIGNAL] Keep CLI/report params in snake_case (`page_size`, `start_from`); adapters handle wire camelCase.
- [HIGH SIGNAL] Preserve lazy-loading behavior in facade clients; do not eagerly instantiate all subclients unless clearly justified.
- [HIGH SIGNAL] For config-sensitive changes, respect precedence: explicit args > env vars > `.env` > JSON config > defaults.
- [HIGH SIGNAL] When changing command attributes, verify both markdown processing (`dr_egeria`) and generated report specs still agree on keys/labels.

## Integration constraints before refactors
- Many flows assume a live HTTPS Egeria view server; self-signed localhost behavior is common in this repo.
- Dr. Egeria v2 depends on compact command JSON in `md_processing/data/compact_commands`; routing is data-driven through dispatcher logic.
- Reporting and Dr. Egeria are coupled by design: generated report specs should stay aligned with compact command labels/attributes.
- `pyegeria/core/mcp_server.py` exposes report discovery/run interfaces (`pyegeria-mcp`), so report contract changes affect MCP clients.

## Contributor editing guardrails
- Prefer extending existing specs/processors over introducing parallel abstractions.
- Keep CLI compatibility in `commands/` unless migration is explicit and documented.
- Apply the config-precedence and command-attribute alignment requirements from `High-signal rules`.




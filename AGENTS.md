# AGENTS.md

## Contributor scope
- This file is for code contributors to `pyegeria` (SDK + CLI), not end users.
- Start with `CONTRIBUTING.md`, then use this as a repo-specific implementation map.

## Sub-project map (dependency order)
- `pyegeria/`: foundational Python SDK for Egeria; includes transport/auth/config, OMVS clients, and report generation/spec registry.
- `commands/` (`hey_egeria`): CLI + simple textual UI layer that invokes `pyegeria` clients and reporting utilities.
- `md_processing/` + `commands/cat/dr_egeria.py` (Dr.Egeria): markdown language/parser/dispatcher/processors that execute `pyegeria` operations and produce reports.
  - v2 engine (the only engine): `md_processing/v2/` — async-first, spec-driven.
- Explicit dependency flow:
  - `pyegeria` -> `commands/` (`hey_egeria`)
  - `pyegeria` -> `md_processing/` + `commands/cat/dr_egeria.py` (Dr.Egeria)
- Change impact (`pyegeria/`): SDK API, config, report formatting/spec changes can break both `hey_egeria` and Dr.Egeria flows.
- Change impact (`commands/`): CLI/TUI argument and output behavior changes must remain compatible with existing command names and snake_case params.
- Change impact (`md_processing/`): markdown attribute/routing changes must stay aligned with `md_processing/data/compact_commands` and generated report specs.

## Architecture map (read before edits)
- `pyegeria/core/_base_platform_client.py` → `_base_server_client.py` → `_server_client.py`: layered transport/auth/GUID-resolution stack used by all OMVS clients.
- `pyegeria/core/config.py`: Pydantic-settings–based config; precedence = explicit args > OS env > `.env` > `config.json` > defaults.
- `pyegeria/egeria_tech_client.py`: lazy facade (`__getattr__`) across OMVS subclients; token propagation happens via `set_bearer_token()`.
- `pyegeria/egeria_client.py` (`Egeria`) / `pyegeria/egeria_cat_client.py` (`EgeriaCat`): additional role-based facades; `EgeriaCat` uses MI over `ProjectManager`, `GlossaryManager`, `AssetCatalog`, `MyProfile`.
- `pyegeria/omvs/*`: service implementations (40+ modules); new API behavior should usually be added here first.
- `pyegeria/models/`: Pydantic models for Egeria API request/response bodies (`models.py`, `collection_models.py`).
- `pyegeria/view/_output_format_models.py`: Pydantic models (`Column`/`Format`/`FormatSet`/`ActionParameter`) backing the report spec registry.
- `pyegeria/view/output_formatter.py` + `pyegeria/view/base_report_formats.py`: materialization/rendering and report spec registry; generated specs live in `base_report_formats.py` under `generated_format_sets`.
- `pyegeria/view/format_set_executor.py`: side-effect-free FormatSet runner used by the MCP adapter and the `ViewProcessor` in Dr.Egeria.
- `pyegeria/core/mcp_server.py` + `pyegeria/core/mcp_adapter.py`: MCP server entry point and its thin adapter helpers (`list_reports`, `describe_report`, `run_report`, `run_find_report_specs`); keep adapter logic in `mcp_adapter.py`, server wiring in `mcp_server.py`.
- `commands/cli/*`: `hey_egeria` command groups and TUI entrypoints over SDK operations.
- `md_processing/` + `commands/cat/dr_egeria.py`: Dr.Egeria v2 parser/dispatcher/processor pipeline over SDK operations; `commands/cat/dr_egeria.py` is the CLI wrapper only.
- `md_processing/v2/extraction.py` (`UniversalExtractor`): identifies DrE command blocks (`# Verb Object`) and their `## Label` attributes; handles horizontal-rule delimiters (`---`, `___`).
- `md_processing/v2/parsing.py`: `AttributeFirstParser.parse()` is asynchronous and utilizes a class-level cache (`_valid_values_cache`) for metadata validation results from Egeria.
- `md_processing/v2/dispatcher.py` (`V2Dispatcher`): routes `DrECommand` objects to `AsyncBaseCommandProcessor` subclasses; uses fuzzy preposition-stripping and dynamic fallback to `CollectionManagerProcessor`/`ProjectProcessor` for registered subtypes.
- `md_processing/v2/processors.py` (`AsyncBaseCommandProcessor`): base class for all v2 processors; standard flow is Parse → Validate → Fetch-As-Is → Action Dispatch.
- `md_processing/v2/rewriters.py` (`CommandRewriter`): invoked by `V2Dispatcher` before the processor fires; rewrites `Create→Update` when the element already exists and `Update→Create` when it is absent.
- `md_processing/md_processing_utils/md_processing_constants.py`: `COLLECTION_SUBTYPES` and `PROJECT_SUBTYPES` lists drive dynamic dispatcher fallback; adding a subtype here enables it automatically. Also defines standardized verb groups: `LINK_VERBS = ("Link", "Attach", "Add", "Detach", "Unlink", "Remove")`, `CREATION_LINK_VERBS`, and `REMOVAL_LINK_VERBS`.

## Contributor workflows
- Dev setup: `uv sync`, activate `.venv`, run tests from repo root.
- Tests are split into three sub-folders: `tests/functional-tests/` (per-OMVS live tests), `tests/scenario-tests/` (lifecycle scenario tests), `tests/micro-tests/` (unit/formatter/MCP tests).
- Default tests are unit/fake; live mode is opt-in via `pytest --live-egeria` or `PYEG_LIVE_EGERIA=1` (`tests/micro-tests/conftest_full.py`).
- Pytest markers in `tests/pytest.ini`: `unit`, `integration`, `slow`, `auth`, `format_sets`, `mcp`.
- For command/report schema changes, regenerate and merge specs with `hey_egeria tech gen-report-specs md_processing/data/compact_commands --merge`.
- Validate compatibility by exercising at least one report in `DICT`, `LIST`, and `REPORT` output modes after formatter/spec edits.
- Generate Markdown command templates: `gen_md_cmd_templates` (basic) or `gen_md_cmd_templates --advanced` → outputs to `sample-data/templates/`.
- Generate Dr.Egeria help docs: `gen_dr_help` → writes to configured Egeria Inbox path.
- Validate compact command JSON specs: `validate_compact_specs`.
- Debug Dr.Egeria API calls: `dr_egeria --input-file <file> --process --debug` (monkey-patches `_async_make_request` for the duration of the call; auto-restored on exit).
- Dr.Egeria directive shortcuts: `--validate` and `--process` are shorthand for `--directive validate/process`; `--summary-only` suppresses per-command diagnostic output; `--advanced` shows non-Basic attributes. Resolution order: `--process` > `--validate` > `--directive` > default (`"validate"`).
- Async tests: `asyncio_mode = auto` in `tests/pytest.ini` — write `async def test_*` functions without explicit event-loop boilerplate.
- Docstrings: use NumPy/SciPy format; every public OMVS method must have a `Notes` section with a sample JSON body where the wire format is non-obvious.

## Repo conventions that matter in reviews
- Prefer snake_case for new report `Column.key` values even though camelCase is supported.
- For nested Egeria responses with repeated names, use namespaced extractor keys (for example `template_display_name`, `target_display_name`).
- Report specs (FormatSets) are now Pydantic models (`FormatSet`/`Format`/`Column` from `pyegeria/view/_output_format_models.py`); define new specs using these models, not raw dicts.
- Generated report specs follow the `{Type}-DrE-{Basic|Advanced}` naming pattern and carry an optional `family` string (e.g., `"Data Designer"`, `"Governance Officer"`) used for discovery via `report_spec_list(show_family=True)` and `report_specs.filter_by_family(...)`.
- Mermaid output is normalized by default (`PYEGERIA_NORMALIZE_MERMAID=true`); set to `false` to preserve native Egeria graph syntax for modern renderers.
- Compact command specs in `md_processing/data/compact_commands/` use `attribute_definitions` + `bundles` (single-inheritance via `"inherits"`) + `commands`; drop a new `*.json` file there to add a family — picked up automatically at startup without code changes (see `compact_loader.py` + `parse_compact_export.py`). Control loading via `USE_COMPACT_RESOURCES`/`COMPACT_FAMILIES` in `md_processing_constants.py`.
- Use `attr_labels` in compact spec attribute definitions to declare user-facing label synonyms that map to the canonical attribute name.
- Link-verb commands use standardized groups from `md_processing_constants.py`; do not hardcode raw verb strings in processors — compare against `LINK_VERBS`, `CREATION_LINK_VERBS`, or `REMOVAL_LINK_VERBS` instead.
- See `High-signal rules` for async-wrapper, snake_case param, and lazy-loading requirements.

## High-signal rules (verbatim)
- [HIGH SIGNAL] New OMVS operations should follow async-core + sync-wrapper pattern (`_async_*` + public sync method).
- [HIGH SIGNAL] Keep CLI/report params in snake_case (`page_size`, `start_from`); adapters handle wire camelCase.
- [HIGH SIGNAL] Preserve lazy-loading behavior in facade clients; do not eagerly instantiate all subclients unless clearly justified.
- [HIGH SIGNAL] For config-sensitive changes, respect precedence: explicit args > env vars > `.env` > JSON config > defaults.
- [HIGH SIGNAL] When changing command attributes, verify both markdown processing (`dr_egeria`) and generated report specs still agree on keys/labels.
- [HIGH SIGNAL] Use the fuzzy-matching preposition stripping rule in `v2/dispatcher.py` to allow natural Markdown headers without adding redundant `alternate_names` to the JSON spec.
- [HIGH SIGNAL] To prevent command mis-mapping, always check that the header verb matches its intended verb group (CREATE, LINK, VIEW) in `find_alternate_names`.
- [HIGH SIGNAL] To add a new collection or project subtype, add it to `COLLECTION_SUBTYPES` or `PROJECT_SUBTYPES` in `md_processing/md_processing_utils/md_processing_constants.py`; the dispatcher will automatically route it to `CollectionManagerProcessor` or `ProjectProcessor` without a new registration.
- [HIGH SIGNAL] New "View" commands need only a report spec (FormatSet) — the `ViewProcessor` auto-routes any `View` verb to the report engine; no custom processor required.
- [HIGH SIGNAL] `CommandRewriter` auto-rewrites `Create→Update` when an element already exists and `Update→Create` when it is absent, before the processor fires; do not re-implement this upsert logic inside individual processors.
- [HIGH SIGNAL] Processors that create new elements must register their GUID in `context["planned_elements"]` so subsequent commands in the same `dispatch_batch` call can resolve them without requiring a multi-pass workflow.

## Integration constraints before refactors
- Many flows assume a live HTTPS Egeria view server; self-signed localhost behavior is common in this repo.
- Dr. Egeria v2 depends on compact command JSON in `md_processing/data/compact_commands`; routing is data-driven through dispatcher logic.
- Reporting and Dr. Egeria are coupled by design: generated report specs should stay aligned with compact command labels/attributes.
- `pyegeria/core/mcp_server.py` exposes report discovery/run interfaces (`pyegeria-mcp`), so report contract changes affect MCP clients.
- `pyegeria/core/mcp_adapter.py` is the programmatic API layer between `mcp_server.py` and pyegeria internals; keep adapter logic in `mcp_adapter.py` and server wiring in `mcp_server.py` — do not intermingle them.

## Contributor editing guardrails
- Prefer extending existing specs/processors over introducing parallel abstractions.
- Keep CLI compatibility in `commands/` unless migration is explicit and documented.
- Apply the config-precedence and command-attribute alignment requirements from `High-signal rules`.




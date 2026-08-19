# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **See also:** `AGENTS.md` (deep architecture map + high-signal rules) and `INSTRUCTIONS.md` (contributor scope per sub-project).

---

## Development setup

```bash
uv sync
source .venv/bin/activate
```

## Running tests

```bash
# All tests (unit/fake, no live server required)
pytest tests/

# Single test file or test function
pytest tests/micro-tests/test_v2.py
pytest tests/micro-tests/test_v2.py::test_name

# Filter by marker (unit | integration | slow | auth | format_sets | mcp)
pytest -m unit
pytest -m integration

# Live Egeria server required
pytest tests/ --live-egeria
# or
PYEG_LIVE_EGERIA=1 pytest tests/
```

`asyncio_mode = auto` — async test functions need no event-loop boilerplate.

Tests live in three folders under `tests/`:
- `micro-tests/` — unit/formatter/MCP tests, no live server
- `functional-tests/` — per-OMVS tests
- `scenario-tests/` — full lifecycle (Create → Link → Delete) tests

Each OMVS module has a corresponding test file in its matching folder.

## Key CLI tools (installed via `uv` / `pip install -e .`)

```bash
# Dr. Egeria — process a markdown file
dr_egeria <file>                   # default: validate
dr_egeria <file> --validate
dr_egeria <file> --process
dr_egeria <file> --process --debug         # prints every Egeria API call + body
dr_egeria <file> --process --summary-only  # suppress per-command analysis

# Dr. Egeria — process every markdown file in a folder, one CLI call
dr_egeria_folder <folder>                       # default: validate, every *.md in the folder
dr_egeria_folder <folder> --process             # real writes; continues past per-file failures, reports all
dr_egeria_folder <folder> --results-file out.txt  # also write the full per-file report to a file

# Regenerate report specs after adding/changing compact command JSON
refresh_specs                           # both Basic + Advanced (default)
refresh_specs --usage-level Basic       # restrict to a single usage level

# Validate compact command JSON files
validate_compact_specs

# Generate Markdown command template files (for user authoring)
gen_md_cmd_templates                # Basic attributes only
gen_md_cmd_templates --advanced     # All attributes

# Local web editor for compact command JSON (attributes/bundles/commands) —
# replaces Tinderbox for editing existing families. One-time: uv sync --extra spec-editor
dr_egeria_spec_editor                   # http://localhost:8420
dr_egeria_spec_editor --port 8500       # custom port
dr_egeria_spec_editor --dir <path>      # target a different compact_commands directory
```
### Dr.Egeria Spec Editor

`commands/tech/spec_editor.py` — a local FastAPI + vanilla-JS tool for editing
`md_processing/data/compact_commands/*.json` directly, without Tinderbox.
Reuses `parse_compact_export`, `validate_compact_json`, and
`compact_spec_validator` rather than reimplementing their logic. Writes
straight to the JSON files on disk; review changes with `git diff` the same
way you'd review a Tinderbox export.

Scope: create/edit/delete attributes, bundles, and commands within an
**existing** family, plus a "New Family" action that scaffolds an empty
compact-JSON file from a template. Every attribute/bundle/command
reference in the UI is a picker over real names (never free text), so it's
not possible to create a dangling reference from the editor.

### Dr.Egeria Folder Batch Runner

`commands/cat/dr_egeria_folder.py` — runs every Dr.Egeria markdown file in a
folder through `process_md_file_v2` with one shared `EgeriaTech` client (one
bearer token for the whole run, not one process per file). Ordering and
manifest semantics were agreed 2026-08-19 with the equivalent folder-batch
runner in `egeria-workspaces-fs` (`bootstrap_batches.py`, documented there in
`PORTAL_STARTUP.md`) so "run all commands in a folder" means the same thing
in both repos:

- An optional `_batch.json` manifest (`{"files": ["a.md", "b.md", ...]}`) at
  the folder root gives the explicit order for those files; any other `*.md`
  file not listed is appended after, alphabetically. No manifest → pure
  alphabetical. A manifest entry naming a file that no longer exists on disk
  is silently dropped, not an error.
- Only `*.md` files are processed; `_batch.json` itself is always excluded.
- Continues through every file regardless of earlier failures and reports a
  full per-file summary at the end (exit code 1 if anything failed) — an
  interactive CLI invocation is the "someone explicitly triggered this and
  wants full visibility" case. (The peer's own unattended auto-heal path
  makes the opposite, stop-on-first-failure, choice for its own use case —
  not implemented here.)
- Every file is expected to be upsert-safe, so the command is safe to re-run
  against the same folder repeatedly — no staleness tracking, only
  presence/absence, matching the peer implementation's own assumption.

One deliberate difference from the peer: this command defaults to
`--validate` (matching this repo's single-file `dr_egeria` CLI's own
default), not straight to process — pass `--process` for real writes.

**This is Claude's edit path, not just a human UI, and Tinderbox is
retired.** Confirmed 2026-08-05: when Claude needs to change a compact
command spec, it makes the edit itself through this app's REST API (start
it with `dr_egeria_spec_editor` if not already running, then
`GET/POST/PUT/DELETE` against
`http://localhost:8420/api/families/{family}/attributes|bundles|commands/{name}`,
`POST /api/validate/{family}` to check the result) — not by hand-editing
the JSON text directly (skips the API's structural validation:
bundle-chain resolution, unknown-attribute checks, duplicate-name checks).
The compact JSON files in this repo are now the sole system of record —
the user confirmed the same day they will not maintain the Tinderbox file
going forward, so there's no mirroring step: once the API edit +
`refresh_specs` regeneration + processor wiring are done and verified,
that's the complete change.

## Auditing the OMVS clients against the `.http` ground truth

`scripts/omvs_audit.py` reconciles every `_async_*` method in `pyegeria/omvs/`
against the `.http` collections, which are the ground truth for URLs, verbs,
and request-body classes.

```bash
# pyegeria/http clients/ is GITIGNORED — absent in fresh worktrees.
# Point the script at a checkout that has it:
export PYEGERIA_HTTP_DIR="/path/to/egeria-python/pyegeria/http clients"

python scripts/omvs_audit.py --quiet              # full audit -> omvs_audit_report.md
python scripts/omvs_audit.py --service location-arena   # one service
```

Exit status is 1 when any confirmed defect is found, so it can gate CI.

**What it checks, and why each check exists** — every category below was added
after a real defect slipped through an earlier, weaker version of this script:

- **VERB** — compares the actual HTTP verb. Helper verbs are discovered by
  parsing `_server_client.py` rather than hardcoded: *every* `_async_*_request`
  helper is POST, and an earlier hardcoded table wrongly mapped the `get_*`
  helpers to GET, which is how a batch of GET-vs-POST defects went undetected.
  A direct `_async_make_request` wins over a helper, because some methods call
  a GUID-resolution helper first.
- **PATH** — compares full normalised paths. It deliberately does **not** strip
  trailing verbs (`/attach` vs `/detach`) or the leading service segment; an
  earlier version did, and that masked exactly the bugs worth finding.
- **BODY** — compares the request-body class (`FilterRequestBody` vs
  `ResultsRequestBody`, etc.). Heuristic: it takes the first `*RequestBody`
  identifier in the method, which may be a signature annotation, so treat body
  findings as lower-confidence than verb/path.
- **LINT** — structural URL defects detectable without ground truth: double
  slashes, a path parameter with no separator before it (`/agreements{guid}`),
  and underscores in path segments (Egeria uses hyphens).

URL extraction is AST-based, not regex — multi-line f-strings silently produced
empty paths under the regex version, which made whole modules look clean.

When triaging a finding, confirm it against the `.http` file before changing
code, and prefer the SDK's existing helpers (`_async_get_name_request`,
`_async_get_results_body_request`, …) over hand-rolled `_async_make_request`
calls, so verb and body shape stay correct by construction.

## Commits

- Always use `git commit -s` to sign off commits. This appends `Signed-off-by: Dan Wolfson <dan.wolfson@pdr-associates.com>` — DCO is enforced on this repo and unsigned commits will be rejected.
- Do **not** add `Co-Authored-By:` lines to commit messages.

---

## Architecture

### Sub-project dependency order

```
pyegeria/  →  commands/  (hey_egeria CLI)
pyegeria/  →  md_processing/  (Dr. Egeria)
```

Changes to `pyegeria/` (SDK API, config, report formatting) can break both.

---

### pyegeria SDK

**`pyegeria/core/`** — transport, auth, config
- `_base_platform_client.py` → `_base_server_client.py` → `_server_client.py`: layered HTTP stack
- `config.py`: Pydantic-settings config; precedence = explicit args > OS env > `.env` > `config.json` > defaults
- `utils.py`: shared helpers (`body_slimmer`, `make_format_set_name_from_type`, etc.)
- **Gotcha — a request-body Pydantic model (`pyegeria/models/models.py`) missing a field silently drops it, not an error.** Every model inherits `PyegeriaModel`'s `extra='ignore'`, so a caller-supplied dict (or a raw no-body-provided construction in `_server_client.py`'s `validate_delete_*_request`-style helpers) with a field the model doesn't declare validates successfully and just vanishes before serialization — no exception, no warning. Confirmed live impact: `DeleteElementRequestBody` had neither `cascadeDelete` nor `deleteMethod` for a long time despite both being real, documented fields on the actual Egeria DTO (`.http` ground truth) — every caller passing `cascade_delete=True` through `_async_delete_element_request` had silently been sending it as unset (PYEGERIA_ISSUES.md ISSUE-62). When adding/using a request-body model, check its fields against the real body in `pyegeria/http clients/Egeria-api-*.http` rather than assuming "it validated without error" means the field will actually be sent.

**`pyegeria/omvs/`** — 40+ service-specific clients (one file per OMVS)
- Every public method has an `_async_*` implementation and a sync wrapper calling `asyncio.get_event_loop().run_until_complete(...)`.
- All public methods decorated with `@dynamic_catch`.
- Ground truth for API URLs and request bodies is in `pyegeria/http clients/Egeria-api-*.http` — check these files before constructing URLs.

**`pyegeria/egeria_tech_client.py`** — `EgeriaTech` facade
- Uses `__getattr__` to lazily proxy attribute access across all OMVS subclients; do not eagerly instantiate.
- `create_egeria_bearer_token()` / `set_bearer_token()` propagate tokens to every subclient.

**`pyegeria/view/`** — output formatting and report spec registry
- `base_report_formats.py`: two separate dicts merged by `get_report_registry()` — `generated_format_sets` (auto-generated by `refresh_specs`; do not hand-edit) and `base_report_specs` (hand-maintained BUILTINS, e.g. `Referenceable`; safe to edit directly, `refresh_specs` never touches it). `get_report_registry()` also auto-loads a CONFIG tier on first call, from `settings.Environment.pyegeria_report_spec_modules` (config.json's `"Pyegeria Report Spec Modules"` list) or the `PYEGERIA_REPORT_SPEC_MODULES` env var — each entry a `.json` path or a `"pkg.mod:func"` loader. **Gotcha:** `config/config.json` is only auto-discovered if `PYEGERIA_CONFIG_DIRECTORY` (or `PYEGERIA_ROOT_PATH`) is set — a bare shell with neither falls back to defaults silently, so a probe script that just imports `settings` may not see config.json values at all; use the `PYEGERIA_REPORT_SPEC_MODULES` env var directly when in doubt.
- `output_formatter.py`: `generate_output()` — materializes elements into MD/LIST/DICT/REPORT formats.
- `_output_format_models.py`: Pydantic models `Column`/`Format`/`FormatSet`/`ActionParameter` — define new specs with these, not raw dicts. `ActionParameter` has two independent execution paths: `function`/`find_method` (element-query, formatted per-column) and `analytic_function`/`extra_find` (a plain function returning an already-aggregated result — see `output-formats-and-report-specs.md`'s "Analytic functions" section).
- `format_set_executor.py`: `exec_report_spec()` — runs either path; `SERIES`/`BAR`/`PIE` output formats wrap an analytic function's result as a Vega-Lite chart (dispatched before normal Format-row lookup, so no `FormatSet` needs to declare those as a `Format` row).
- `analytic_registry.py` / `analytic_demo_specs.py`: the catalog of analytic functions (`AnalyticFunctionSpec.generic` marks whether what it counts is a parameter or hardcoded) and one real, executable demo `FormatSet` per registered function.
- `_output_dashboard_sheet_models.py`: `DashboardSheet`/`Placement` — a local (not yet Egeria-native) model for user-authored dashboards, built via Dr.Egeria's `Create Dashboard Sheet`/`Link Report to Dashboard Sheet`/`Add Text on Dashboard Sheet` (`md_processing/v2/dashboard_sheet.py`).
- Generated report specs follow `{Type}-DrE-{Basic|Advanced}` naming; carry an optional `family` string for discovery.

---

### Dr. Egeria v2 pipeline (`md_processing/`)

Full pipeline for one `process_md_file_v2()` call:

```
Markdown file
  ↓ UniversalExtractor (extraction.py)
      splits on ## headers / horizontal rules → DrECommand objects
  ↓ setup_dispatcher() (dr_egeria.py)
      loads COMMAND_DEFINITIONS from compact JSON specs
      registers {command_key → ProcessorClass} in V2Dispatcher
  ↓ V2Dispatcher.dispatch_batch() (dispatcher.py)
      sequential; shared context["planned_elements"] for inter-command GUID resolution
      alias resolution → fuzzy verb-stripping → subtype fallbacks
  ↓ AsyncBaseCommandProcessor.execute() (processors.py)
      1. AttributeFirstParser.parse()
      2. derive qualified name
      3. fetch_as_is (cache → Egeria lookup)
      4. CommandRewriter: Create↔Update upsert transitions
      5. resolve reference GUIDs for all attributes
      6. validate_only() → markdown analysis table
      7. apply_changes()  ← abstract; implemented per processor
      8. render_result_markdown(guid)
  ↓ dr_egeria.py: assemble final_output, write processed-*.md
```

**Key files:**

| File | Role |
|---|---|
| `dr_egeria.py` | Entry point; `setup_dispatcher()`; `process_md_file_v2()` |
| `v2/extraction.py` | `UniversalExtractor` → `DrECommand` dataclass |
| `v2/dispatcher.py` | `V2Dispatcher` — routing, alias resolution, fallbacks |
| `v2/processors.py` | `AsyncBaseCommandProcessor` — base parse/validate/apply logic |
| `v2/rewriters.py` | `CommandRewriter` — Create↔Update auto-transitions |
| `md_processing_utils/md_processing_constants.py` | `COLLECTION_SUBTYPES`, `PROJECT_SUBTYPES`, `COMMAND_DEFINITIONS`, verb groups |
| `md_processing_utils/common_md_utils.py` | Body builders (`set_element_prop_body`, domain helpers) |
| `data/compact_commands/*.json` | Compact command specs — ground truth for attributes; system of record as of 2026-08-05 (Tinderbox retired) |

**Compact command JSON format** — three sections per file:
- `attribute_definitions` — full metadata per attribute (style, labels, valid values, etc.)
- `bundles` — reusable attribute groups; single inheritance via `"inherits"`
- `commands` — references a bundle + adds custom attributes; expands to a full command spec at load time

**Never hand-edit the JSON text directly.** Use the Dr.Egeria Spec Editor's
REST API (`dr_egeria_spec_editor`, `http://localhost:8420` — see the
"Dr.Egeria Spec Editor" section above) to make the change — it does
structural validation (bundle-chain resolution, unknown-attribute checks)
that raw editing skips. These files were originally Tinderbox exports, but
as of 2026-08-05 that's retired: the user confirmed they will not maintain
the Tinderbox file going forward, so this repo's compact JSON is the sole
system of record — no mirroring/re-export step needed after an edit. After
any change, run `refresh_specs` to regenerate `base_report_formats.py`.

**Dispatcher registration** — how new commands get wired in:
- `COLLECTION_SUBTYPES` and `PROJECT_SUBTYPES` drive automatic `Create/Update` routing to `CollectionManagerProcessor` / `ProjectProcessor` — adding a type to these lists is all that's required.
- Families driven entirely by compact spec (Actor Manager, Governance, Solution Architect, Curation) use a `register_*_processors()` helper loop in `dr_egeria.py`.
- **`register_curation_processors()` routes by `OM_TYPE`, not verb** — `"Update"` is ambiguous between a classification update and a relationship update, so it looks up each command's `OM_TYPE` in `CLASSIFICATION_METHODS` (`md_processing/v2/curation.py`) → `CurationClassifyProcessor`, or in the local `CURATION_LINK_OM_TYPES` set → `CurationLinkProcessor`; anything in neither (currently: Class Word/Modifier/Policy Management Point — real Egeria classification types confirmed live via `get_all_classification_defs`, but with no backing pyegeria SDK method) is left unregistered on purpose and stays parse-only. `CLASSIFICATION_METHODS` keys must be the real Egeria classification type name (confirmed against a live server), not a Dr.Egeria-side display convention — a prior Tinderbox export used `ImpactClassification`/`ConfidenceClassification`/etc., which `validate_compact_specs`' `OM_TYPE_INVALID` check caught since the real names are unsuffixed (`Impact`, `Confidence`, ...).
- **`register_governance_processors()` is family-name-gated, not automatic** — it only registers commands whose compact-spec `family` is literally `"Governance Officer"` (or, as of the `Action Author` family, also `"Action Author"`). Adding a brand-new family whose commands should reuse `GovernanceProcessor`/`GovernanceLinkProcessor` means adding its name to that check explicitly — nothing is wired up just because the compact JSON exists and validates. Within `Action Author`, the four `Link` commands are routed by `OM_TYPE`, not by verb alone, across two dedicated processors in `md_processing/v2/action_author.py` (neither uses the generic peer-link mechanism, since both need relationship properties `PeerDefinitionProperties` has no room for):
  - `Link First/Next Process Step` (`OM_TYPE` `GovernanceActionProcessFlow`/`NextGovernanceActionProcessStep`) → `ActionProcessStepLinkProcessor`, calling `action_author.setup_first/next_action_process_step` with `GovernanceActionProcessFlowProperties` (guard/requestParameters) / `NextGovernanceActionProcessStepProperties` (guard/mandatoryGuard). Verified end-to-end against a live server — relationship properties persist correctly.
  - `Link Action to Action Executor/Target` (`OM_TYPE` `GovernanceActionExecutor`/`TargetForGovernanceAction`) → `ActionExecutorTargetLinkProcessor`, calling `action_author.link_governance_action_executor`/`link_target_for_governance_action` with `GovernanceActionExecutorProperties` (requestType/requestParameters/requestParameterFilter/requestParameterMap/actionTargetFilter/actionTargetMap) / `TargetForGovernanceActionProperties` (actionTargetName). Added 2026-07-15 — not yet verified against a live server.
- Everything else is an explicit `reg("Verb Object", ProcessorClass)` call in `setup_dispatcher()`.

**Body builders** — all flow through one function:
- `set_element_prop_body()` in `common_md_utils.py` is the base inner-properties builder for all element types.
- Every domain helper (`set_collection_manager_body`, `set_actor_manager_prop_body`, `set_gov_prop_body`, `set_data_field_body`) calls it and adds type-specific fields on top.
- To add a new `Referenceable`-level property, add it once to `set_element_prop_body()`.

**Adding a new processor** — minimum steps:
1. Add the command spec to the relevant compact JSON via the Dr.Egeria Spec Editor's REST API (see above — Tinderbox is retired, this repo's compact JSON is the system of record).
2. Add the type to `COLLECTION_SUBTYPES` / `PROJECT_SUBTYPES` if it's a collection/project subtype (auto-routes).
3. Otherwise implement `apply_changes()` in a new `AsyncBaseCommandProcessor` subclass and register it in `setup_dispatcher()`.
4. Run `refresh_specs` to generate the result-table format spec.
5. **If any downstream app has its own copy of dispatcher/command-registration logic, verify it too — don't assume registering here is sufficient.** egeria-workspaces-fs's `PyegeriaWebHandler/dr_egeria_md.py` carried a hand-duplicated `setup_dispatcher()` (pre-dating this session, ~3+ months old) that silently missed `Create Report` and the entire Dashboard Sheet family added here, because it was never updated in parallel — the commands worked perfectly via `dr_egeria --process` in this repo's own dev venv while being completely unrecognized ("No processor registered") through that app's actual web UI. That local duplicate has since been deleted in favor of importing this module's `setup_dispatcher` directly (2026-07-31), but the general risk — a consumer wiring its own copy of dispatch logic instead of importing it — isn't structurally prevented, so re-check after any new command lands if a consumer app's behavior doesn't match a working `dr_egeria` CLI run.
6. **If the new command introduces a local (non-Egeria) persisted store** — e.g. `dashboard_sheet.py`'s `~/.pyegeria/dashboard_sheets.json` — **tell the user it needs a bind mount in every consuming app's deploy config**, or it's silently ephemeral (wiped on the consumer's next container rebuild). This repo has no deploy config of its own to fix; egeria-workspaces-fs's `AGENTS.md` has the checklist item for its compose files.

**Creating a type with no dedicated OMVS wrapper — pick the right generic endpoint, don't assume `MetadataExpert`.** `MetadataExpert._async_create_metadata_element` (the raw `/metadata-expert/metadata-elements` endpoint) looks like the obvious generic fallback, but it requires the verbose typed `ElementProperties`/`propertyValueMap` body shape (confirmed live: passing the flat properties dict every other processor uses gets `OMAG-COMMON-400-006 ... qualifiedName parameter ... is null`, a 400, even though `qualifiedName` was set — the flat value is silently not read). For an `Asset` subtype (Report, and presumably other DataSet/Asset-derived types with no bespoke OMVS class), use `AssetMaker._async_create_asset(["<Type>Properties"], body)` / `_async_update_asset(guid, body)` instead (`asset-maker/assets`) — it accepts the same flat `set_create_body()`/`set_element_prop_body()` shape as every bespoke wrapper. See `md_processing/v2/report.py` (`Create Report`) for the worked example, verified end-to-end against a live server including the create→update upsert transition.

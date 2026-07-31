# Egeria Python — Backlog

Consolidated work list. Update status when items start or finish.
Status: `open` · `in-progress` · `done` · `deferred`

---

## 🟠 High Priority — Missing/absent catalog templates crash or silently proceed in `_async_get_template_guid_for_technology_type` callers — needs discussion

**Status:** open (partial fix landed 2026-07-27)
**Added:** 2026-07-27

`tests/scenario-tests/test_automated_curation_scenarios.py::scenario_manage_client_side_secrets` crashed with a bare `KeyError: 0` calling `create_secrets_store_element_from_template`. Root cause: `_async_get_template_guid_for_technology_type()` (`pyegeria/omvs/automated_curation.py:4476`, shared by **13** `create_X_element_from_template` methods — Kafka, CSV, PostgreSQL x2, File System Directory, 6x Unity Catalog, YAML File Secrets Collection) blindly indexed `details.get("catalogTemplates", {})[0]` with a wrong default (`{}` instead of `[]`), turning a missing/empty `catalogTemplates` into a confusing `KeyError` instead of a clear error.

**Fixed:** the indexing bug itself — now raises a clear `PyegeriaException` naming the technology type and stating no catalog template is registered, instead of crashing opaquely.

**Live-checked all 13 call sites against `qs-view-server` (2026-07-27) — two real gaps found, need a decision on each:**
1. **`YAML File Secrets Collection`** — technology type exists (it's a real, standard Egeria type per `DeployedImplementationType.java` in egeria core) but has **zero** catalog templates registered on this server (`catalogTemplates: []`). This is a server-side sample-data/archive gap, not a pyegeria bug — `create_secrets_store_element_from_template` cannot work at all against this server until the template is loaded. Confirm which archive/sample-data load is supposed to seed this template, and whether it's missing from the quickstart setup or was never added upstream.
2. **`Apache Kafka Server`** — technology type is **not registered at all** on this server (`_async_get_tech_type_detail` returns `NO_ELEMENTS_FOUND`). `_async_get_template_guid_for_technology_type` already handles this branch gracefully (returns `None`, no crash) — but every caller (e.g. `create_kafka_server_element_from_template`) then proceeds to build a `TemplateRequestBody` with `templateGUID: None`, which `body_slimmer` will likely strip, sending a request silently missing a required field — masking the real problem behind a probably-confusing downstream 400 from the server instead of failing fast client-side. Needs a decision: should `_async_get_template_guid_for_technology_type` returning `None` cause the 13 callers to raise immediately (consistent with the empty-catalogTemplates case above), rather than let each one send a doomed request?

All other 10 call sites (`CSV Data File`, `PostgreSQL Server`, `PostgreSQL Relational Database`, `File System Directory`, and all 6 `Unity Catalog *` types) checked clean — tech type found, exactly one catalog template registered, no issue.

---

## 🟡 Medium Priority — `add_comment_reply` has no real implementation or Egeria endpoint

**Status:** open (partially resolved 2026-07-27)
**Added:** 2026-07-02

`tests/functional-tests/test_comments.py` originally had 9 failing tests, all `AttributeError` on `pyegeria.core._server_client.ServerClient`. Root cause turned out to be **test bugs, not missing SDK methods** — the file was written by copy-pasting a `note_logs` test file and missed several renames:
- 7 tests patched `async_X` when the real method is `_async_X` (this repo's documented convention: private `_async_*` impl + public sync wrapper) — simple naming typo.
- `test_remove_comment_from_element_sync_calls_async` called `client.remove_note_log(...)` instead of `client.remove_comment_from_element(...)`, with a stale fake signature (extra `element_guid` param the real method doesn't have).
- `test_get_attached_comments_sync_calls_async` called `client.get_attached_note_logs(...)` instead of `client.get_attached_comments(...)`, with wrong fake param names/order.
- `test_find_comments_sync_calls_async` called `client.find_note_logs(...)` instead of `client.find_comments(...)`.
- `test_get_comment_by_guid_sync_calls_async` had a fake signature with a nonexistent `element_type` param instead of the real `graph_query_depth`.
- `test_update_comment_sync_calls_async` asserted a return value (`{"status": "OK"}`) that `update_comment()`'s sync wrapper never actually propagates (matches `_async_update_comment`'s own `-> None` contract) — assertion was just wrong.

All 8 of the above are now fixed in `tests/functional-tests/test_comments.py`; `pytest tests/functional-tests/test_comments.py` passes.

**Still open:** `test_add_comment_reply_sync_calls_async` is marked `@pytest.mark.skip` — `add_comment_reply` has no `_async_*` method on `ServerClient`, and Egeria's feedback-manager REST API (`Egeria-api-feedback-manager.http`) has no distinct comment-reply endpoint either; replies appear to just be regular comments attached via `addCommentToElement`, not a separate mechanism. Needs a product decision: implement real reply support (if Egeria core actually has one this reference file is missing), or delete the test.

---

## 🟢 Low Priority — Produced Guards has no valid values constraint

**Status:** open
**Added:** 2026-07-02

The new `Produced Guards` attribute (`Action Author` family, on `Governance Action Type Base` bundle — used by `Create Governance Action Type` / `Create Governance Action Process Step`) is a `Simple List` of strings with no `valid_values` constraint. Unlike `Domain Identifier`-style Enum attributes (which list every allowed value in `valid_values`, e.g. `ALL;DATA;PRIVACY;...`), guard names are process-author-defined labels rather than a fixed global enum, so there's no universal list to seed it with today.

**Future validation idea:** once real governance action processes exist with real guard names in use, consider whether `Produced Guards` values should be validated against something more specific than free text — e.g. cross-checked against the `Guard`/`Next Governance Action Process Step` relationship attributes actually declared in the same process, so a typo'd guard name that never matches a real transition gets caught at validate time instead of silently producing a dead-end step. Not blocking Phase 1 or Phase 2 — flagging so it isn't forgotten once there's real usage data to design the check against.

---

## 🟡 Medium Priority — SalesForecast regression fixtures need a baseline seed sequence

**Status:** open
**Added:** 2026-07-02

47 of the failures across `tests/dr-egeria-command-tests/dr_test_*.md` (validate mode) are all the same root cause: `Referenced element 'X' ... not found`, where `X` is a specific named element from a "SalesForecast" demo scenario (a pipeline, a master collection, an agreement, glossary terms, a governance zone) plus a couple of similar campaigns ("Clinical Trials Management", "Sustainability"). Confirmed directly against the live server (`localhost:9443`) that zero `SalesForecast` elements currently exist — `client.find_collections('SalesForecast')` returns "No elements found".

This means the `Create` commands that would establish this baseline dataset are scattered across several of the `dr_test_*.md` files rather than living together, and nothing has actually run them in `--process` mode against this server (or the server was reset since they last were). Every `Link`/`Attach`/`Detach`/`Unlink` command elsewhere that references one of those named elements by qualified name fails to resolve it.

**Fix:** collect up the `Create` commands that establish the SalesForecast baseline (and the couple of campaign elements), work out the correct dependency order, and either (a) run them once in `--process` mode against whichever server these fixtures are meant to run against, or (b) consolidate them into a dedicated seed file that `run_dr_tests.py` (or a setup step before it) runs first. Not blocking Action Author Phase 1/2 — pre-existing gap, unrelated to those commands.

---

## 🟡 Medium Priority — Bearer token expires mid-run on long `dr_egeria --process` batches

**Status:** fixed (2026-07-31)
**Added:** 2026-07-08

Running `dr_egeria <100+ command file> --process` against `localhost:9443` (e.g. the generated `dr-egeria-help-*.md`, ~100+ commands) took ~1h20m end to end and started failing every remaining command with HTTP 401 partway through — the bearer token created at the start of the run expired before the run finished, and nothing re-authenticates or refreshes it mid-batch. Confirmed directly in `logs/pyegeria.log`: the "Create Risk" term's `_async_create_element_body_request` call at 23:12:14 got a 401 (`Client error '401' for url .../glossary-manager/glossaries/terms`), as did every command after it in that run (~6+ trailing Solution Architect `Link` commands all failed the same way). Re-running the single "Create Risk" term in isolation (a few seconds) succeeded immediately with the same credentials — confirming it's a token-lifetime/duration issue, not a bad request or bad credentials.

**Fixed:** option (b) implemented, but in `pyegeria` core (`_async_make_request` in `pyegeria/core/_base_server_client.py`) rather than the v2 dispatcher loop — so it fixes every caller of any pyegeria client, not just Dr.Egeria's batch pipeline. On a 401, if the client holds stored credentials, it now transparently re-authenticates via `_async_create_egeria_bearer_token()` and retries the original request exactly once before surfacing a failure. Also fixed a bug in `_async_create_egeria_bearer_token()` itself found while implementing this: it was sending the token-refresh request with the stale/expired Authorization header still attached, which got that request itself rejected with 401 — silently defeating both this new auto-retry and the pre-existing manual "call this if your token expired" use case. See `PYEGERIA_GAPS.md` item #6 for full detail; live-verified end-to-end against `qs-view-server`.

---

## 🟠 High Priority — Egeria server silently overwrites SolutionLinkingWire instead of creating a parallel relationship

**Status:** open (client-side warning added; server-side behavior not fixable from egeria-python)
**Added:** 2026-07-09

Issuing two `Link Solution Components` Dr.Egeria commands with the *same ordered* `(Component1, Component2)` pair but different `Label`s does not create two parallel `SolutionLinkingWire` relationships — the second call silently overwrites the first's properties (including label) in place. Discovered because `sample-data/egeria-inbox/dr-egeria-inbox/solution-design.md` was missing exactly one relationship on the live server (`DataHub -> Finance | expenses`) after processing, while a same-direction sibling link (`DataHub -> Finance | new-orders`) survived.

Confirmed with a controlled repro (two throwaway components, two same-direction `Link Solution Components` calls) and verified two independent ways: the `wiredTo` convenience summary field, and the generic `get_related_elements` relationship query — both show only one relationship, carrying the *second* call's properties. Reversing direction between two calls (`C→D` then `D→C`) correctly produces two distinct relationships, so it's specifically the *ordered pair* that collapses, not direction in general.

Checked the Egeria core Java handler (`SolutionComponentHandler.linkSolutionLinkingWire` → `openMetadataClient.createRelatedElementsInStore`) — no find-first/update logic visible at that layer, so the collapse happens deeper in the server/repository stack. Also checked the live `SolutionLinkingWire` relationship type definition directly (`get_all_relationship_defs`): both `endDef1`/`endDef2` declare `attributeCardinality: "ANY_NUMBER"`, meaning the **type system itself permits multiple relationships between the same pair** — so this looks like a REST/view-service handler bug (an unwanted idempotent "find matching relationship, update it" pattern) rather than a fundamental repository constraint. Nothing to fix in `pyegeria` or `dr_egeria`'s Python code for the write path itself — the request sent is exactly what was asked for.

**Mitigation added 2026-07-09:** the user extended `Link Solution Components` with a `One Way` attribute (bool, default `True`) as a workaround — set `One Way: False` to express a bidirectional flow with a single command instead of issuing two same-direction commands. `SolutionLinkProcessor.apply_changes()` in `md_processing/v2/solution_architect.py` now also pre-checks for an existing same-direction wire before creating a new one and surfaces a `WARNING`-status "Existing Wire Overwrite" result if a call is about to silently clobber an existing relationship — so this is no longer a silent, undetectable data-loss surprise, but the underlying overwrite behavior itself is still present.

**Fix (if ever pursued upstream):** report/fix in Egeria core so the `attach` REST handler for `SolutionLinkingWire` creates a new relationship instance per call (matching the type system's `ANY_NUMBER` cardinality) rather than upserting by ordered end-GUID pair. Out of scope for `egeria-python` to fix directly.

---

## 🟢 Low Priority — `examples/` has two broken test-collection files

**Status:** open
**Added:** 2026-07-24

Running `pytest` broadly enough to sweep in `examples/` (rather than scoping to `tests/` per this repo's convention) surfaces two pre-existing collection errors, unrelated to any Dr.Egeria/glossary work:
- `examples/extract_attribute_test.py:13` — a stray trailing `/` after `if zones and isinstance(zones, list):` is a plain `SyntaxError`, so the file can't even be parsed.
- `examples/test_jacquard_data_sets.py` and `examples/test_jacquard_data_sets_scenarios.py` — both `from examples.jacquard_data_sets import JacquardDataSets`, which fails with `ModuleNotFoundError: No module named 'examples'` (no `__init__.py`/path setup makes `examples` importable as a package).

Neither breaks `pytest tests/`, so day-to-day test runs are unaffected — this only bites if `examples/` is included in the collection path.

**Fix:** remove the stray `/` in `extract_attribute_test.py:13`; either add `examples/__init__.py` (and confirm `examples` is on `sys.path`/rootdir-relative import works) or change the two Jacquard test imports to a path that resolves without treating `examples` as a package.

---

## 🟡 Medium Priority — Migrate Pydantic v1-style validators to v2 syntax

**Status:** open
**Added:** 2026-07-24

`pyegeria/view/_output_format_models.py` (lines 164, 172, 221, 238, 275) still uses Pydantic v1-style `@root_validator(pre=True)` and `@validator(...)` decorators. These emit `PydanticDeprecatedSince20` warnings on every collection/import that touches this module (visible in `pytest` output) — they still work today (v2 keeps them as deprecated shims) but are slated for removal in a future Pydantic major version. Not urgent — no functional bug, and the project's Pydantic version (2.12.3) is current — but the warning noise will become a hard break eventually.

**Fix:** migrate `@root_validator(pre=True)` → `@model_validator(mode="before")` and `@validator(...)` → `@field_validator(...)` for each of the 5 flagged validators in `_output_format_models.py`, then re-run `pytest -m unit` to confirm the warnings are gone and behavior is unchanged.

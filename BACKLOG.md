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

**Fixed:** option (b) implemented, but in `pyegeria` core (`_async_make_request` in `pyegeria/core/_base_server_client.py`) rather than the v2 dispatcher loop — so it fixes every caller of any pyegeria client, not just Dr.Egeria's batch pipeline. On a 401, if the client holds stored credentials, it now transparently re-authenticates via `_async_create_egeria_bearer_token()` and retries the original request exactly once before surfacing a failure. Also fixed a bug in `_async_create_egeria_bearer_token()` itself found while implementing this: it was sending the token-refresh request with the stale/expired Authorization header still attached, which got that request itself rejected with 401 — silently defeating both this new auto-retry and the pre-existing manual "call this if your token expired" use case. See `PYEGERIA_ISSUES.md` ISSUE-7 for full detail; live-verified end-to-end against `qs-view-server`.

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

---

## 🟠 High Priority — Forward references to elements later in the same Dr.Egeria file don't actually resolve

**Status:** done (fixed 2026-08-02)
**Added:** 2026-08-01

**Context:** investigating a user report that `Sub-Projects` on `Create Project`
(and variants: Campaign/Task/Personal Project/Study Project) was "being
ignored." The wiring itself is correct and works (fixed 2026-07-08, commit
`71202ef`) — live-verified end-to-end for both plain `Create Project` and
`Create Campaign`, both correctly created `ProjectHierarchy` relationships.
The actual bug: it only works when every referenced sub-project is already
created *or listed earlier* in the same file. If the parent project is
listed **before** its children — a very natural way to write a Dr.Egeria
doc — the reference silently failed to resolve. (A related, smaller bug —
list-style reference resolution silently dropping unresolvable items with
zero error, instead of reporting them like single-value references already
did — was fixed same day, see `md_processing/v2/processors.py`'s Step 7
list-resolution loop. That fix alone turns "silently ignored" into "clearly
reported: `Execution blocked: Referenced element(s) [...] not found`," so
users at least get an actionable error now.)

**Root cause (why true forward-reference support is a bigger job):**
Dr.Egeria processes commands strictly sequentially in `--process` mode. By
the time command N runs, commands 1..N-1 have *already fully executed* —
so a **backward** reference (child listed before parent) never needs the
"planned" placeholder mechanism at all; it just finds the real,
already-created GUID via cache/live-lookup. The "planned" mechanism
(`context["planned_elements"]`, populated incrementally as each command
executes) only helps a **forward** reference if the referenced name is
already registered by the time the referencing command's own resolution
step runs — which is never true for command K > N referenced by command N,
since command K hasn't executed yet. There's already a well-built "resolve
planned GUIDs right before applying changes" step in the code (~line
557-610 in `processors.py`) that correctly detects a still-unresolved
planned item and blocks with a clear "Prerequisite element ... was not
successfully created" error — but it can only help if the item was
recognized as *planned* in the first place, which requires it to already be
in `planned_elements`, which requires its own command to have executed.

**Real fix would require a two-phase batch design:**
1. A pre-scan pass over the whole batch (before any command executes) to
   register every Create/Update-verb command's target name into
   `planned_elements` upfront — so forward references are recognized as
   "planned" rather than "not found at all."
2. Defer the actual relationship-sync API calls (e.g.
   `_sync_sub_projects`'s `add_fn`/`remove_fn`) for any reference still
   showing a `(Planned:...)` placeholder until *after* the full batch has
   executed and the referenced element genuinely exists — not just
   "recognized as planned."
3. Error handling for the case where the referenced element's own command
   later fails (e.g. the forward-referenced child project itself fails to
   create) — the deferred relationship-sync needs to surface a clear error
   in that case too, not fail silently or crash.

This is a genuine architectural change to the core dispatch pipeline
(`md_processing/v2/dispatcher.py`, `processors.py`), affecting every
list-style *and* single-value reference attribute across every command
family — not scoped to Sub-Projects. Deferred pending a scoping discussion;
not started.

**Workaround for users today:** list every element a command will
reference *before* the command that references it, in file order (e.g.
create sub-projects first, then the parent project that lists them under
`Sub-Projects`). This is exactly what the newly-added blocking error
message will now tell you to do if you get it wrong.

**Bonus finding while validating the Tier 1 fix:** the same silent-drop bug
was independently reproduced (pre-existing, unrelated to Sub-Projects) in
two of the regression fixtures under `tests/dr-egeria-command-tests/`:
- `dr_test_glossary.md`'s GL-08 scenario ("member of multiple glossaries")
  references `Glossary::CRM::Domain::1.0` as a second glossary membership,
  but no such glossary is ever actually created anywhere in the file — the
  term was silently only added to one glossary instead of two.
- `dr_test_products_good.md`'s `Link Agreement to Actor` scenario
  references actor `<jane.smith@example.com>`, which was never created —
  same root cause as the already-tracked "SalesForecast regression
  fixtures need a baseline seed sequence" entry above.

Both now correctly fail with a clear blocking error instead of silently
"succeeding." Not fixed as part of this entry — the fixtures themselves
need either a missing `Create Glossary`/actor block added, or the stale
reference corrected.

**Fixed 2026-08-02:** implemented the two-phase batch design described
above, smaller in scope than originally framed — none of the 11
relationship-establishing call sites across `project.py`/
`solution_architect.py`/`glossary.py`/`data_designer.py`/`governance.py`/
`collection_manager_processor.py` needed to change; the entire mechanism
lives in `dispatcher.py` and `processors.py`:
- `V2Dispatcher.prescan_batch_target_qns()` walks the full batch once
  before execution, deriving each Create/Update command's own qualified
  name (reusing the real `derive_qualified_name()`, byte-identical to the
  later real parse) plus its raw Display Name (a forward reference is
  typically typed as the display name, matching how a *backward* reference
  already resolves via `find_key_with_value()`).
- `dispatch_batch()` now runs in rounds: a command whose reference is
  recognized as a legitimate batch target but not yet resolvable is
  deferred (not failed) and retried next round; stops when nothing's
  deferred, or forces one final round (treating anything still unresolved
  as a genuine, final failure) once a round makes zero progress.
- Two "flavors" of command, discriminated automatically by whether
  `derive_qualified_name()` returns non-empty: **embedded** (`Create
  Project` etc.) always creates its own element immediately regardless of
  unresolved embedded references, so same-round dependents aren't falsely
  blocked; **standalone** (`Link Project Hierarchy` etc., the whole command
  *is* the relationship) defers the entire command.
- Also fixed a genuine multi-level-chain bug found during design (grandparent→parent→child
  forward-reference chains failed one level too early without a
  `context["final_round"]` guard on the existing "resolve Planned GUIDs"
  gate), and a pre-existing silent-success bug in
  `SolutionLinkProcessor.apply_changes()` (unresolved `id1`/`id2` returned
  `raw_block` without setting an error, so `execute()` reported `"success"`
  on a silently-skipped link).

Live-verified against `qs-view-server`: a parent-before-child `Sub-Projects`
forward reference now resolves and creates the real `ProjectHierarchy`
relationship. New test coverage: `tests/micro-tests/test_dispatcher_forward_references.py`.
Backward-compatibility confirmed byte-for-byte via all 12 `dr_test_*.md`
regression fixtures (identical SCORE lines before/after). Full design
history and validated rationale in the session that implemented this — see
git history around 2026-08-02 for `md_processing/v2/dispatcher.py` and
`md_processing/v2/processors.py`.

The two bonus fixtures noted above (`dr_test_glossary.md` GL-08,
`dr_test_products_good.md` Agreement-to-Actor) are still open — not
forward-reference cases (nothing in either file ever creates the referenced
element), so this fix doesn't change their outcome. Still need a decision:
add the missing block, or correct the stale reference.

---

## 🟡 Medium Priority — `Parent ID`/`Parent Relationship Type Name` silently dropped on Update (fixed); `Anchor ID`/`Anchor Scope ID` cannot be changed post-creation (confirmed architectural constraint, not a bug)

**Status:** done (Parent Relationship fixed 2026-08-02); Anchor — confirmed not fixable, no further action planned
**Added:** 2026-08-02

**Context:** also fixed in passing: `set_create_body()` looked up the
attribute under the wrong key, `'Anchor Scope GUID'`, when the compact
spec's actual attribute name is `'Anchor Scope ID'` — silently broke
`anchorScopeGUID` even on **Create**, independent of the Update-time gap
below. Corrected the key name.

`set_create_body()` bakes `Anchor ID`/`Parent ID`/`Anchor Scope
ID` (+ `Parent Relationship Type Name`/`Parent Relationship Attributes`/
`Parent at End1`) into Create's `NewElementRequestBody` as a shortcut —
Egeria's create endpoint bundles "create the element" and "establish this
one relationship/anchor" into a single call. `set_update_body()` has no
equivalent fields at all (confirmed: Egeria's real `UpdateElementRequestBody`
Java class has only a `properties` field — no anchor/parent slot exists on
the update endpoint). Since the compact spec marks these attributes
`inUpdate: True`, they were being resolved to real GUIDs on `Update`
commands and then silently discarded — parsed, resolved, never sent
anywhere.

**Parent ID / Parent Relationship Type Name — fixed.** The relationship
these fields represent (an ordinary Egeria relationship, e.g.
`ProjectHierarchy`) can be established explicitly post-creation, the same
way a standalone `Link X` command would. Added
`AsyncBaseCommandProcessor._sync_parent_relationship()` (one generic method,
called from `execute()` after `apply_changes()` succeeds, for both Create
and Update) using `MetadataExpert`'s generic relationship calls
(`_async_create_related_elements`/`_async_get_all_related_elements`/
`_async_delete_related_elements` — any Egeria relationship type, not just
ones with a dedicated OMVS wrapper). Live-verified against `qs-view-server`:
creates the relationship on Update, idempotent on repeat (checked via direct
GUID comparison), and correctly re-parents (old relationship removed, new
one created) when `Parent ID` changes.

Fixing this surfaced three independent, pre-existing pyegeria bugs (all
fixed as part of this same pass, since they directly blocked verifying the
above):
1. `validate_new_related_elements_request()` (`pyegeria/core/_server_client.py`)
   used the wrong `TypeAdapter` (`_new_relationship_request_adapter`, for an
   unrelated model) instead of the already-defined-but-unused
   `_new_related_elements_request_adapter`.
2. `NewRelatedElementsRequestBody` (`pyegeria/models/models.py`) had field
   names (`relationship_type_name`/`end_1_guid`/`end_2_guid`) that don't
   match the real Java DTO (`typeName`/`metadataElement1GUID`/
   `metadataElement2GUID`, confirmed against
   `frameworkservices/omf/rest/NewRelatedElementsRequestBody.java`) — the
   server silently ignored the wrong field names rather than erroring.
3. `_async_get_all_related_elements()` (`pyegeria/omvs/metadata_expert.py`)
   returns a **dict** (`{"startingElement":..., "elementList":[...],
   "mermaidGraph":...}`), not a list, and `elementList` entries use a
   different, lower-level shape (`type.typeName`/`relationshipGUID`/
   `element.elementGUID`) than domain-specific calls like
   `ProjectManager._async_get_project_by_guid()`'s `managedProjects` field.

**Anchor ID / Anchor Scope ID — investigated, confirmed NOT fixable the same
way; no code change made.** Anchoring is implemented as a **classification**
(`"Anchors"`/`AnchorsProperties`: `anchorGUID`, `anchorTypeName`,
`anchorDomainName`, `anchorScopeGUIDs`, `zoneMembership`), not a
relationship, so the relationship-based fix above doesn't apply. Tried the
obvious equivalent — `MetadataExpert._async_reclassify_metadata_element()`
with an updated `anchorGUID` — and it **succeeds at the API level but does
not establish real anchor semantics**: live-tested twice (two independent
throwaway-element pairs), reclassifying one element's `Anchors` to point at
another, then deleting the "anchor" with `cascade=True` — the reclassified
element survived both times and had to be deleted independently, proving no
real cascade-delete relationship was established. Traced into
`OpenMetadataAPIAnchorHandler.java`: `anchorGUID` maintenance there is wired
into specific entity-**creation** flows (schema types, attributes,
connections, comments, ratings, etc.), not into any generic post-creation
reclassify path. This reads as an intentional constraint — anchoring
governs lifecycle/security/visibility scope, which is the kind of thing
that's reasonable to keep immutable after creation for governance reasons,
unlike an ordinary Parent relationship. **Recommendation: leave `Anchor
ID`/`Anchor Scope ID`'s current Update-time silent-no-op behavior as-is.**
If this needs revisiting, the next step would be finding whichever
repository-services-level operation (if any) actually re-evaluates an
entity's anchor after creation — not found via the generic MetadataExpert
API surface in this investigation.

---

## 🟢 Low Priority — `Confidentiality`/`Confidence`/`Criticality`/`Retention`/`Impact` classifications were completely unwired (all five now fixed and working)

**Status:** done — all five classifications, including Retention (fixed server-side 2026-08-03)
**Added:** 2026-08-02

**Context:** per dwolfson — unlike `Anchor ID` (confirmed immutable-by-design, see
entry above), Confidentiality/Retention/Criticality/Confidence genuinely need
to be changeable over an element's lifetime. Investigating this found these
five "0422 Governed Data Classifications" attributes (`Confidentiality
Classification`, `Confidence Classification`, `Criticality Classification`,
`Retention Classification`, `Impact Classification` — all `style: "Valid
Value"`, `inUpdate: true`, present on every family via the shared bundle)
were **not wired into any processor at all** — not Create, not Update. Parsed
and validated by `AttributeFirstParser`, then silently discarded; a bigger gap
than the Parent/Anchor case, which at least worked on Create.

**Fixed:** added `AsyncBaseCommandProcessor._sync_governance_classifications()`
(`md_processing/v2/processors.py`), called from `execute()` alongside
`_sync_zone_membership`/`_sync_parent_relationship` for both Create and
Update. Uses `classification_manager`'s (`ClassificationExplorer`) dedicated
`_async_set_X_classification`/`_async_clear_X_classification` methods.

**Found and worked around a systemic, previously-unknown bug across ALL FIVE
of pyegeria's own classification methods while implementing this:** both
`classification_explorer.py`'s docstrings and the compact spec's attribute
descriptions document the "level" property uniformly (and wrongly) as
`levelIdentifier` (Retention: `basisIdentifier`, Impact:
`severityIdentifier`). **Confirmed live** that calling `set_confidentiality_
classification` with the documented `levelIdentifier` field returns **no
error** but the classification silently fails to attach at all. Cross-checked
each real Java class
(`frameworks/openmetadata/properties/governance/*Properties.java`) and
confirmed live, round-trip, that the *real* field names are:
`confidentialityLevel`, `confidenceLevel`, `criticalityLevel`,
`severityLevel` (Impact), and `retentionBasis` (Retention — matches its
docstring, unlike the other four). Verified end-to-end: set on Create,
re-set to a different value on Update (confirmed idempotent — Egeria
reclassifies in place, same as `_sync_zone_membership`'s existing
established pattern), values read back correctly via direct element fetch
for Confidentiality/Confidence/Criticality/Impact.

**Retention Classification — was a separate server-side gap, confirmed fixed 2026-08-03.**
Every attempt to set Retention was previously rejected server-side:
`OMRS-REPOSITORY-400-028 A property called statusIdentifier has been
proposed for a metadata instance of category ClassificationDef and type
Retention; it is not supported for this type`, even though the outgoing
request never included that field (confirmed via a wire-body dump at the
time) — an Egeria core / `ClassificationDef` type-registration gap, not a
pyegeria or Dr.Egeria issue.

**Re-verified live 2026-08-03 per dwolfson's report that the Egeria bug was fixed** — confirmed:
the same call (`RetentionClassificationProperties` / `retentionBasis`, this
codebase's class name and field were already correct) now succeeds, with
the server correctly auto-populating a `statusIdentifier` default (`0`) on
its own, no error. Verified end-to-end through the real Dr.Egeria pipeline
(`Create Project` with `Retention Classification: PROJECT_LIFETIME`) and via
direct element fetch showing `retentionBasis: 2` persisted correctly.

**Caught in the process: a "fix" documented here on 2026-08-02 was never actually committed.**
This entry previously claimed the client-side class name had been corrected
to `"RetentionProperties"` (the real Java properties class's simple name).
That change was never actually present in the committed code — and, more
importantly, it would have been **wrong**: live testing today showed the
server's own Jackson deserializer error lists its exact registered subtype
IDs, and it recognizes `"RetentionClassificationProperties"`, not
`"RetentionProperties"` — sending the latter gets rejected outright as an
unrecognized type ID, before ever reaching the (now-fixed)
`ClassificationDef`-registration check. The original class name in
`pyegeria/omvs/classification_explorer.py`'s `_async_set_retention_classification`
was correct all along; left unchanged (confirmed via a full revert-and-retest
in this session).

**Also fixed in passing:** `pyegeria/omvs/classification_explorer.py`'s
docstrings for these five `_async_set_X_classification` methods are stale
(still show the wrong "level" field names) — not corrected as part of this
pass since they're documentation only (the actual behavior is determined by
whatever the caller passes, not by the docstring), but worth a follow-up
cleanup so future users don't fall into the same "no error, but silently
did nothing" trap this session found for Confidentiality.

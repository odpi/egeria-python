## Summary

Implements forward-reference support for Dr.Egeria batch processing (BACKLOG.md: "Forward references to elements later in the same Dr.Egeria file don't actually resolve") and fixes two related gaps where governance-relevant attributes were silently dropped: `Parent ID`/`Parent Relationship Type Name` on `Update`, and the `Confidentiality`/`Confidence`/`Criticality`/`Retention`/`Impact` classifications (not wired into any processor at all, Create or Update). Along the way, fixes a pre-existing silent-success bug in `SolutionLinkProcessor` and several independent pyegeria bugs, all discovered only by live-verifying each fix end-to-end.

## Governance classifications (Confidentiality/Confidence/Criticality/Retention/Impact)

Per dwolfson: unlike `Anchor ID` (investigated separately below, confirmed immutable by design), these classifications genuinely need to change over an element's lifetime. Found they were **completely unwired** — not just missing on Update like Parent ID, but never applied on Create either. Parsed and validated, then silently discarded.

Added `AsyncBaseCommandProcessor._sync_governance_classifications()`, called alongside the existing `_sync_zone_membership()`/new `_sync_parent_relationship()` for both Create and Update, using `ClassificationExplorer`'s dedicated `_async_set_X_classification` methods.

**Found a systemic, previously-unknown bug across all five of pyegeria's own classification methods while implementing this:** both the method docstrings and the compact spec's attribute descriptions document the "level" property uniformly (and wrongly) as `levelIdentifier`. Live-confirmed calling `set_confidentiality_classification` with that field returns **no error** but silently fails to attach the classification at all. Cross-checked each real Java `*Properties.java` class and confirmed live that the real field names are `confidentialityLevel`/`confidenceLevel`/`criticalityLevel`/`severityLevel` (Impact)/`retentionBasis` (Retention). Verified end-to-end for four of the five: set on Create, changed on Update (idempotent — Egeria reclassifies in place), correct values read back via direct fetch.

**Retention is a separate, unresolved, apparent server-side gap** — even after fixing pyegeria's own client-side class-name mismatch (`RetentionClassificationProperties`, not `RetentionProperties`), the server rejects every attempt: `a property called statusIdentifier ... is not supported for this type`. Confirmed via a wire-body dump that the actual outgoing request never includes that field — this looks like Egeria's own `Retention` `ClassificationDef` registration issue, not fixable from this codebase. Left wired in since it fails cleanly as an isolated per-item error, not a silent no-op or a blocked command. Full details in `BACKLOG.md`.

## Forward references

A `Reference Name`/`Reference Name List` attribute (e.g. `Sub-Projects` on `Create Project`) previously could only reference an element already created *earlier* in the same file — referencing one defined later (a very natural way to write a Dr.Egeria document) failed with `Referenced element(s) [...] not found`.

**Design note:** none of the 11 relationship-establishing call sites across `project.py`/`solution_architect.py`/`glossary.py`/`data_designer.py`/`governance.py`/`collection_manager_processor.py` needed to change. The entire mechanism lives in `dispatcher.py` and `processors.py`, because `context["planned_elements"]` was already unconditionally, cumulatively populated for every Create/Update command regardless of its own eventual success — the missing piece was populating it *before* the batch runs instead of only incrementally during it, and letting a command retry on a later pass instead of failing permanently on the first.

- `V2Dispatcher.prescan_batch_target_qns()` — walks the full batch once before execution, deriving each command's own qualified name (reusing the real `derive_qualified_name()`) and its raw Display Name (a forward reference is typically typed as the display name, matching how a *backward* reference already resolves via cache).
- `dispatch_batch()` now runs in rounds — a command whose reference is a recognized batch target but not yet resolvable is deferred, not failed, and retried next round. Stops when nothing's deferred, or forces one final round (treating anything still unresolved as a genuine failure) once a round makes zero progress. Results stay positionally aligned to the input command list regardless of completion round.
- Two command "flavors," discriminated automatically by whether `derive_qualified_name()` returns non-empty: **embedded** (`Create Project`, etc.) always creates its own element immediately even with an unresolved embedded reference, so same-round dependents aren't falsely blocked; **standalone** (`Link Project Hierarchy`, etc. — the whole command *is* the relationship) defers entirely.
- Fixed a multi-level-chain bug found during design validation: a `context["final_round"]` guard on the existing "resolve Planned GUIDs" gate, needed so grandparent→parent→child forward-reference chains resolve correctly instead of failing one level too early.
- `--validate` mode's message now says plainly when a forward reference "will resolve during --process" instead of misleadingly reporting bare success.

## Parent relationship on Update

`Anchor ID`/`Parent ID`/`Anchor Scope ID` (+ `Parent Relationship Type Name`/`Attributes`/`at End1`) get baked into Create's `NewElementRequestBody` as a shortcut — Egeria's create endpoint bundles "create the element" and "establish this one relationship" into a single call. `set_update_body()` has no equivalent fields at all (confirmed: Egeria's real `UpdateElementRequestBody` Java class has only a `properties` field). These attributes were being resolved to real GUIDs on `Update` and then silently discarded.

**`Parent ID`/`Parent Relationship Type Name` — fixed.** Added one generic method, `AsyncBaseCommandProcessor._sync_parent_relationship()`, called from `execute()` after `apply_changes()` succeeds for both Create and Update, using `MetadataExpert`'s generic relationship calls (works for any Egeria relationship type, not just ones with a dedicated OMVS wrapper). Live-verified: creates the relationship on Update, idempotent on repeat, correctly re-parents (old relationship removed, new one created) when `Parent ID` changes.

**`Anchor ID`/`Anchor Scope ID` — investigated, confirmed not fixable the same way, no code change.** Anchoring is a *classification* (`Anchors`/`AnchorsProperties`), not a relationship. Tried the obvious equivalent (`_async_reclassify_metadata_element` with an updated `anchorGUID`) — it succeeds at the API level but does **not** establish real anchor semantics: live-tested twice, reclassifying one throwaway element to point at another, then deleting the "anchor" with `cascade=True` — the reclassified element survived both times. Traced into `OpenMetadataAPIAnchorHandler.java`: anchor maintenance is wired into specific entity-creation flows, not any generic post-creation path. Reads as an intentional constraint (anchoring governs lifecycle/security scope, reasonably immutable after creation) rather than a bug. Documented in `BACKLOG.md` as a confirmed architectural constraint; current silent-no-op behavior left as-is.

Also fixed in passing: `set_create_body()` looked up `'Anchor Scope GUID'` instead of the compact spec's actual `'Anchor Scope ID'` — silently broke `anchorScopeGUID` even on Create.

## Other fixes surfaced along the way

- **`SolutionLinkProcessor.apply_changes()`** (pre-existing bug, unrelated to forward references): unresolved `id1`/`id2` returned `raw_block` without setting an error, so `execute()` unconditionally reported `"status": "success"` on a silently-skipped link. Now raises clearly, with a forward-reference-aware check first so a genuine forward reference still defers rather than hard-failing.
- **Three pyegeria bugs**, found only by live-verifying the Parent Relationship fix end-to-end (all blocked it from actually working, despite validating cleanly):
  1. `validate_new_related_elements_request()` used the wrong `TypeAdapter` (`_new_relationship_request_adapter`, for an unrelated model) instead of the already-defined-but-unused `_new_related_elements_request_adapter`.
  2. `NewRelatedElementsRequestBody`'s field names (`relationship_type_name`/`end_1_guid`/`end_2_guid`) didn't match the real Java DTO (`typeName`/`metadataElement1GUID`/`metadataElement2GUID`) — the server silently ignored them rather than erroring.
  3. `_async_get_all_related_elements()` returns a dict (`{"elementList": [...], ...}`), not a list, with a lower-level per-entry shape than sibling domain-specific calls — the original idempotency check silently no-op'd every time as a result.

## Validation

- `pytest -m unit` clean; new test file `tests/micro-tests/test_dispatcher_forward_references.py` (3 tests: parent-before-child forward reference resolves across rounds, genuinely-unresolvable reference still fails clearly, structural discriminator between embedded/standalone commands).
- Zero regression: all 12 `dr_test_*.md` regression fixtures produce byte-for-byte identical SCORE lines before/after (only timestamps differ).
- `SolutionLinkProcessor`'s existing functional (`test_solution_architect_omvs.py`, 13 tests) and scenario tests still pass.
- `tests/functional-tests/test_metadata_expert.py` (36 tests, live server) re-run clean after the pyegeria model/validator fixes.
- Live-verified against `qs-view-server` throughout (throwaway elements created and deleted): forward-reference resolution + real `ProjectHierarchy` relationship creation; parent-relationship create/idempotent-no-op/re-parent; the negative anchor-reclassify result (twice, independent element pairs); Confidentiality/Confidence/Criticality/Impact set on Create and changed on Update, values confirmed via direct fetch; Retention's server-side failure confirmed clean (isolated per-item error, command still succeeds).

## Files changed

- `md_processing/v2/dispatcher.py` — pre-scan, round-based `dispatch_batch()`
- `md_processing/v2/processors.py` — Step-7 deferral logic, pre-apply_changes guard, final_round gate, new `_sync_parent_relationship()` and `_sync_governance_classifications()`
- `md_processing/v2/solution_architect.py` — `SolutionLinkProcessor` silent-success fix
- `md_processing/md_processing_utils/common_md_utils.py` — `Anchor Scope ID` key-name fix
- `pyegeria/core/_server_client.py` — `validate_new_related_elements_request()` adapter fix
- `pyegeria/models/models.py` — `NewRelatedElementsRequestBody` field-name fix
- `tests/micro-tests/test_dispatcher_forward_references.py` — new
- `BACKLOG.md` — forward-references entry marked done; new entries for Parent Relationship (fixed) / Anchor (confirmed constraint), and governance classifications (4/5 fixed, Retention a separate server-side gap)

# Open Egeria Server Issues

A standalone extract of the **Egeria-Server-side** issues in [`PYEGERIA_ISSUES.md`](PYEGERIA_ISSUES.md), for whoever owns the Egeria side. None of them can be fixed by editing this repo: each needs a server-side fix, an upstream bug report, or a deployment change.

**`PYEGERIA_ISSUES.md` is the source of record.** This file was **re-derived from it on 2026-10-13** (its "Open Egeria Server issues" and "Awaiting re-test" index lists, plus the Egeria-side entries filed under pyegeria items). Don't edit the two independently. When an entry changes status, change it in `PYEGERIA_ISSUES.md`, then re-derive this file.

It replaces the 2026-10-05 snapshot `docs/egeria-open-bugs-2026-10-05.md` (deleted; it's in git history). That snapshot's Egeria-team verdicts and fix evidence are now in the individual `PYEGERIA_ISSUES.md` entries.

## Summary

| Group | Issues |
|---|---|
| **Open on the Egeria side** (full entries below) | ISSUE-166, ISSUE-147, ISSUE-143, ISSUE-130, ISSUE-128, ISSUE-108 |
| **Awaiting re-test:** a fix landed (mostly Egeria `main`, odpi/egeria#9363, merged 2026-10-06), not yet verified live | ISSUE-125, ISSUE-124, ISSUE-117, ISSUE-112, ISSUE-95, ISSUE-90, ISSUE-89, ISSUE-79, ISSUE-38 |
| **Egeria-side, but tracked as pyegeria items** (a pyegeria change waits on Egeria) | ISSUE-146, ISSUE-132 |

## Awaiting re-test

| Issue | Status (from `PYEGERIA_ISSUES.md`) |
|---|---|
| ISSUE-125: `deleteEnumDef` answers 500 "unknown TypeDef" for an enum the server lists -- an enum added through the API cannot be removed | open; reported to the Egeria team (response 2026-10-05); Egeria fix merged to Egeria `main` 2026-10-06 (odpi/egeria#9363), not yet re-tested on a platform built from it |
| ISSUE-124: `updateTypeDef` (Metadata Expert `open-metadata-types/update`) can never succeed -- the server builds the patch without `updatedBy`, which the repository services require | open; reported to the Egeria team (response 2026-10-05); Egeria fix merged to Egeria `main` 2026-10-06 (odpi/egeria#9363), not yet re-tested on a platform built from it |
| ISSUE-117: Cascade delete that takes the soft-delete (Memento) path fails partway with `OMAG-REPOSITORY-HANDLER-400-010` unless `forLineage=true` — leaves the asset live and an anchored element already soft-deleted | open, workaround known; reported to the Egeria team (response 2026-10-05); Egeria fix merged to Egeria `main` 2026-10-06 (odpi/egeria#9363), not yet re-tested on a platform built from it |
| ISSUE-112: `AutomatedCurationRESTServices.saveClientSideSecret`/`deleteClientSideSecret` return a plain success `VoidResponse` when the resolved connector isn't a `YAMLSecretsFileConnector` — no error, no write, no indication anything was skipped | open |
| ISSUE-95: No catalog template registered for the "Apache Kafka Server" technology type — `Create Kafka Server Element` (Asset Maker) fails with a 400 on `qs-view-server` | awaiting re-test (addressed on the Egeria side, confirmed live 2026-10-05) |
| ISSUE-90: [fixed?] `qs-engine-host` retries `startMissedEngineActions` forever when one incomplete engine action's anchor is unreadable by the engine-host user | open |
| ISSUE-89: No configurable bearer-token lifetime in `application.properties` — platform tokens are fixed at 3600 s, and the signing key is random per restart | awaiting re-test (addressed in Egeria source 2026-09-19; not verified on the dev platform) |
| ISSUE-79: native survey against a template-created `FileFolder` asset fails server-side — `assetConnector` is null in `BasicFolderConnector.getFile()` | open (Egeria Server), reproduced live 2026-08-27, **re-checked |
| ISSUE-38 (PY-18): `count_relationships_between_elements("Exception")` (276) disagrees with `ClassificationExplorer.get_relationships("Exception")` (55) | re-confirmed 2026-08-18, byte-for-byte identical to the |

## Egeria-side issues tracked as pyegeria items

- **ISSUE-146: Deleting a journal entry fails with OMAG-REPOSITORY-HANDLER-400-008, and pyegeria's `remove_note` reaches the delete only through the generic Asset Maker service**: Egeria has no note/action delete, and the only route (the asset delete) fails with 400-008 for journal entries; awaiting Egeria's delete fixes. Full entry in `PYEGERIA_ISSUES.md`.
- **ISSUE-132: `DeleteElementRequestBody` serializes the cascade flag as `cascadeDelete`; Egeria's field is `cascadedDelete` and unknown fields are ignored, so no pyegeria cascade delete has ever cascaded**: Egeria's DeleteOptions field is `cascadedDelete`; the pyegeria fix is on hold until Egeria's cascade-delete fix lands. Full entry in `PYEGERIA_ISSUES.md`.

## Open on the Egeria side

### ISSUE-166: Security annotation properties are Java primitives, so an unset CVSS score, exploit/patch flag or posture count reads back as 0 / false

**Layer:** Egeria Server (type model / properties classes) · **Status:** open, question for the Egeria team · **Found:** 2026-10-26, while adding the 6.3 security annotation types to pyegeria (odpi/egeria-workspaces#702 hand-off, step 3; PR #495).

**What happens:** in `SecurityFindingAnnotationProperties`, `VulnerabilityAnnotationProperties` and `SecurityPostureAnnotationProperties` (`frameworks/open-metadata-framework/.../properties/surveyreports/`), these fields are Java primitives with a 0 / false default:

| Class | Fields |
|---|---|
| `SecurityFindingAnnotationProperties` | `float cvssScore`, `boolean exploitAvailable` |
| `VulnerabilityAnnotationProperties` | `boolean patchAvailable` |
| `SecurityPostureAnnotationProperties` | `long resourcesInScopeCount`, `resourcesTestedCount`, `newFindingCount`, `resolvedFindingCount` |
| `AnnotationProperties` (inherited by all four) | `long sampleSize`, `int samplePercent`, `int confidence`, `long absoluteUncertainty`, `relativeUncertainty` |

So "never set" and "set to 0 / false" come back identical. Confirmed live on 2026-10-26 (egeria-platform:latest quickstart, as erinoverview on qs-view-server, throwaway `SecTest*` elements, since deleted and verified gone by GUID): a `VulnerabilityAnnotation` created with only `severity: "Medium"` read back with `cvssScore: 0.0`, `exploitAvailable: false` and `patchAvailable: false`. A `SecurityPostureAnnotation` created with only `findingCountsBySeverity` and `newFindingCount` read back with `resourcesInScopeCount: 0`, `resourcesTestedCount: 0` and `resolvedFindingCount: 0`.

**Why it matters:** each of these values is a reassuring answer. A findings table that shows them as returned tells a reader "CVSS 0, no public exploit, no patch" about a finding nobody assessed, and "0 findings resolved" about a run that never recorded it. `exploitAvailable: false` is the most dangerous, since it is the field a triager sorts on.

**Question for the Egeria team (Mandy):** could these become boxed types (`Float`, `Boolean`, `Long`, `Integer`) with a `null` default, so that an unset value is omitted from the response? `cvssScore` matters most: a CVSS score of 0.0 is a real rating (severity "None").

**pyegeria workaround (PR #495, until then):** the security report rows (`DataDiscovery._security_row`, behind the `Security-Findings`, `Penetration-Test-Findings` and `Security-Posture` report specs) leave a value blank where a 0 or false would read as an answer nobody gave:
- a CVSS score of 0.0 is shown only when the severity is "None";
- `exploitAvailable` and `patchAvailable` are shown only when true;
- 0 resources in scope means not recorded, so both resource counts are blank.

`newFindingCount` / `resolvedFindingCount` of 0 cannot be told apart from unrecorded on the client at all, and the `Security-Posture` description says so. Once Egeria returns `null` for unset values, the workaround can go, apart from the "None" severity rule, which stays true either way.

---

### ISSUE-147: Every valid-metadata clear call answers OPEN-METADATA-400-011 "not found", even after a successful delete; clear-map-value deletes nothing; clear-map-name leaves the map's value set behind

**Layer:** Egeria Server (`ValidMetadataValueHandler`) · **Status:** open · **Found:** 2026-10-13. The first live run of the Valid Metadata commands showed it (the error text wasn't captured then). Re-tested the same day with the full responses captured.

**Re-test:** run once on qs-view-server as erinoverview, with all four live sessions clearing it first. It used made-up properties `pyegeriaClearRetest` and `pyegeriaClearRetestMap` (typeName `Asset`) and called the SDK methods in `pyegeria/omvs/valid_metadata.py`. The Dr.Egeria `Clear Valid Metadata *` commands call the same methods (`md_processing/v2/reference_data.py:198-242`).

| Call | Response | Actual effect |
|---|---|---|
| `clear_valid_metadata_value(alpha)`, set up just before | 400-011 "value alpha ... is not found" | **alpha removed** (gone from the list afterwards) |
| same call again (alpha already gone) | 400-011 | nothing to remove |
| `clear_valid_metadata_value(beta)` | 400-011 | **beta removed** |
| `clear_valid_metadata_map_value(mapOne, v1)` | 400-011 "value v1 ... is not found" | **nothing removed**: `get_valid_metadata_map_value` still returns v1 |
| `clear_valid_metadata_map_name(mapTwo)` | 400-011 | **mapTwo removed** |
| `clear_valid_metadata_map_name(mapOne)`, with v1 under it | 400-011 | the mapOne name value is removed, but the map's value set "mapOne" (holding v1) stays in `get_valid_metadata_values` |

Request ids: `ec9052e7` and `3975182d` (alpha), `38759736` (beta), `475e68f1` (map value), `407c0e17` and `07886f29` (map names). pyegeria surfaces each one as `SERVER_ERROR_500` wrapping `relatedHTTPCode` 400 `InvalidParameterException`.

**Cause (Egeria source, `af400039c2`, `frameworks/open-metadata-framework/.../handlers/ValidMetadataValueHandler.java`):**
1. **No `return` after the delete (lines ~541-680).** In all three `clear*` methods, `if (validValueGUID != null) deleteMetadataElementInStore(...)` is followed unconditionally by the audit log and `throw new InvalidParameterException(VALID_METADATA_MISSING ...)`. So every call throws, whether or not it deleted anything. The "not found" error is the method's normal exit.
2. **Map name dropped in `clearValidMetadataMapValue`.** It calls `getValidValueGUID(userId, typeName, propertyName, null, preferredValue)`, passing `null` where `mapName` belongs. It therefore searches for `v1` as a plain value of the property, finds nothing, and deletes nothing.
3. **`clearValidMetadataMapName` deletes only the name's own value.** It doesn't touch the per-map value set created by `setup-map-value` (the "Set of valid values for the mapOne map name ..." element) or its members. Whether that should cascade is Egeria's call.

**Effect on Dr.Egeria:** `Clear Valid Metadata Value` and `Clear Valid Metadata Map Name` report failure although the clear worked. `Clear Valid Metadata Map Value` reports failure and really did fail.

**Leftovers on qs-view-server:** the map value set "mapOne" with member v1 under `pyegeriaClearRetestMap`/`Asset`, plus whatever per-property container elements setup creates (`Egeria:ValidMetadataValue::pyegeriaClearRetest-Asset` and `...pyegeriaClearRetestMap-Asset`). These are test elements, not content-pack elements. RE's blueprint materializer treats `Egeria:ValidMetadataValue:` qualifiedNames as content-pack origin, but only for SolutionComponents, so they don't affect it.

**pyegeria follow-on (not done, needs the owner's go-ahead):** Dr.Egeria's clear processor could treat 400-011 from `clear-value`/`clear-map-name` as success when a follow-up read confirms the value is gone. Otherwise, wait for the Egeria fix and re-test (see the BACKLOG.md delete re-test item).

---

### ISSUE-143: `includeOnlyRelationships: ["PersonRoleAppointment"]` returns no relationships for a Person, although the unfiltered read has its role appointments

**Layer:** Egeria Server (not pyegeria) · **Status:** open, not yet reported to the Egeria team · **Found:** 2026-10-13, reported by the egeria-workspaces-fs Resource Browser session; reproduced read-only the same day.

**What:** reading a Person with a `GetRequestBody` whose
`includeOnlyRelationships` is `["PersonRoleAppointment"]` returns the element
with no relationships at all. The same read with no filter returns 8
`performsRoles` entries, each with relationship type `PersonRoleAppointment`.
Other filters on the same Person work.

**Reproduction** (Person `10dc7da9-e9e1-471f-9afd-46a7ff414cb7`, Erin Overview,
as erinoverview on qs-view-server;
`ClassificationExplorer.get_element_by_guid(guid, graph_query_depth=1,
output_format="JSON", body={"class": "GetRequestBody", "graphQueryDepth": 1,
"includeOnlyRelationships": [...]})`):

| Filter | Relationship keys returned |
|---|---|
| none | performsRoles 8, assignmentScope 15, requestedActions 11, contactDetails 1, userIdentities 1, contributionRecord 1 |
| `["ContactThrough"]` | contactDetails 1 |
| `["AssignmentScope"]` | assignmentScope 15 |
| `["PersonRoleAppointment"]` | none |

A spy on the request confirmed pyegeria sends the body exactly as given, so
the filtering happens in Egeria.

**Likely cause (not confirmed):** Egeria's relationship filter
(`OpenMetadataHandlerBase`, around line 478) keeps a relationship when
`propertyHelper.isTypeOf(rel, name)`, which should match. But `performsRoles` is
filled in a separate step (`OpenMetadataHandlerBase`, around line 1282), so the
role appointments may be dropped or never fetched once a filter is set.

**Workaround:** read the Person without `includeOnlyRelationships` and take
`performsRoles` from the result. The Resource Browser already does this.

---

### ISSUE-130: The YAML secrets store's user directory caches a user forever, so editing an existing user needs a platform restart

**Layer:** Egeria server (`YAMLSecretsStoreConnector`) · **Status:** open, reported to the Egeria lead · **Found:** 2026-10-09, while adding Resource Explorer's own account (`resourceexplorernpa`).

**What:** `getUser(userId)` returns the entry from `userAccountMap` if it is already there. `refreshSecrets()` re-reads the YAML file every `refreshTimeInterval` minutes, but `userAccountMap` (and `securityAccessControlMap`) are created only on the first load (when `secretsStoreFile == null`) and are never cleared afterwards. Re-reading the file only helps users the cache has never seen; the comment says "this may be a new user".

**Seen:** the account was first added without its `secrets` block, and the first token request cached it. After the password was added (and matched the servers file), `/api/token` still answered 401 for more than 10 minutes. It worked straight after a platform restart.

**Effect:** any change to an existing user (password, status, named-list membership) needs a platform restart.

**Fix (Egeria):** clear or rebuild `userAccountMap` and `securityAccessControlMap` in `refreshSecrets()`.

---

### ISSUE-128: Retention cannot be set on Egeria 6.2: the server registers the Jackson subtype as `RetentionProperties.class` (typo), and pyegeria only allows `RetentionClassificationProperties`

**Status:** open, found 2026-10-09 by Resource Explorer's first Retention publish on Egeria 6.2. **Layer:** Egeria server (a type registration typo). **Decision (owner, 2026-10-09):** wait for the Egeria fix; no pyegeria workaround. Retention publishing stays blocked until then.

**What (all proven live on 6.2, with raw HTTP POSTs to `classification-explorer/elements/{guid}/retention` on a throwaway asset):**
- `"class": "RetentionClassificationProperties"` is refused with `InvalidTypeIdException`. This is what pyegeria documents and whitelists, and it worked on the pre-6.2 server (processors.py comment, 2026-08-03).
- `"class": "RetentionProperties"` (the `.http` ground truth) is also refused with `InvalidTypeIdException`.
- `"class": "RetentionProperties.class"` gets **HTTP 200**, and the classification reads back with `retentionBasis` 2 and the notes.
- The server's known-type list in the error has 96 ids. The only Retention entry is literally `RetentionProperties.class`. That looks like an `@JsonSubTypes.Type(name = "RetentionProperties.class")` typo in Egeria's `ClassificationProperties`.
- pyegeria's `validate_new_classification_request` whitelist (`prop=["RetentionClassificationProperties"]`) refuses anything else client-side, so no Retention can be set through pyegeria on 6.2.

(An earlier version of this entry said 6.2 knows `RetentionProperties`. That was a misread of the error text, corrected the same day.)

**Where seen:** Resource Explorer's Curate classifications step on two repository assets. Both were refused, so nothing was written. Confidentiality, Criticality, Confidence and Impact property classes are registered normally.

**Candidate fix:**
1. **Egeria:** correct the subtype name to `RetentionProperties`, matching the `.http` file. Report it to Mandy.
2. **pyegeria, after Egeria's fix:** change the whitelist and docstring to `RetentionProperties`, the `.http` name. No workaround for the typo, by the owner's decision.
3. Re-check `md_processing/v2/processors.py` and `v2/curation.py`, which both pin `RetentionClassificationProperties`.

---

### ISSUE-108: newly created relationships stay invisible to related-element queries for up to ~20 minutes after creation

**Layer:** Egeria Server · **Status:** open · **Found:** 2026-09-20, reported by
the user from a Dr.Egeria bulk load session (1,027 expected field-link
relationships).

**What:** a catalog walk run immediately after a load found only 876 of 1,027
expected field links. A second walk 12 minutes later still showed 82
structures short. A third walk, 20 minutes after the load, showed every link
present. No errors were raised at any point in the load itself — the
relationships were created successfully, they simply did not show up in
related-element queries for a long window afterward, then all became visible
at once with no further action taken.

**Not yet root-caused.** This looks like the same family of symptom as the
2026-08-15 Postgres-checkpoint/background-connector-load entry above (server
falling behind under load, catching up later) rather than a paging defect
like ISSUE-54 (which would not self-heal purely by waiting — ISSUE-54's
bug is about tie-ordering across separately-executed pages, not about data
not existing yet). But this has not been directly correlated with connector
log activity or checkpoint timing the way that entry was — this is a fresh
report, not yet independently reproduced or diagnosed by a pyegeria session.

**Impact:** any workflow that verifies a bulk write immediately after
issuing it (a post-load catalog walk, an integration test, an automated
Dr.Egeria "did it work" check) can get a false-negative "missing" result
that resolves itself given enough time — worth knowing before treating an
immediate post-write verification gap as evidence of a real data-loss bug.

**Candidate next step (not yet done):** reproduce with a smaller, timed
sample (e.g. create N relationships, poll related-element queries at 1-minute
intervals, log when each becomes visible) to get a real latency
distribution instead of the three anecdotal checkpoints here, and check
whether it correlates with the same background-connector/checkpoint load
already documented above. Worth raising with the Egeria team directly, per
the original report.

**Update 2026-09-20 (peer check, no upstream issue filed yet):** checked
`odpi/egeria`'s issue tracker directly — nothing filed for this symptom, so
no response from the Egeria team via GitHub. Asked three peer sessions
working against the same dev Egeria server:
- **egeria-workspaces-fs-4a:** hasn't seen this specific symptom, no word
  from the Egeria team either. Raised a speculative, explicitly-unconfirmed
  lead worth checking: a chronic, still-open issue on `egeria-shared-kafka`
  where the `GroupCoordinator` repeatedly times out writing to
  `__consumer_offsets` (5000ms) and triggers a consumer-group rebalance
  roughly every 90s (confirmed via broker logs 2026-09-03; root cause still
  open, CPU/GC/Postgres-restarts/virtiofs I/O already ruled out; historically
  "Information" severity, self-heals within seconds, not chased further
  since it wasn't visibly causing downstream harm). If `qs-view-server`'s
  related-element queries are backed by Kafka-driven indexing/event
  propagation rather than a direct repository read, a chronic rebalance
  storm could plausibly manifest as exactly this "relationship exists but
  isn't visible to queries yet" lag. **Explicitly not a confirmed
  correlation** — the timescales don't obviously line up (a recurring ~90s
  self-healing blip vs. a one-shot ~20-minute resolution) — and the peer
  offered to check Kafka broker logs around the original bulk-load window
  for the same rebalance pattern if useful.
- **Resource Explorer experimental UI:** no direct evidence either way —
  today's two live writes against the same server (a Governance Action
  Process Step upsert, and a native-survey `SurveyReport` lookup) both
  checked either *immediately* after the write or only *after* polling to a
  terminal status, never in the 1-20 minute gap this entry describes, so
  neither confirms nor rules it out. Flagged that a background agent on
  their side doing a related connection-refresh fix will trigger fresh
  engine actions/relationships shortly and will report back if it surfaces
  the same lag.
- **Egeria-trellis backlog review:** also nothing from the Egeria team (no
  channel to them; checked RE docs/Backlog/design notes for this exact
  shape first — a checked "no", not a guess). Offered a different, measured
  precedent on this same platform as a *pattern* to distinguish causes, not
  a diagnosis: `packages/resource-explorer/docs/investigation-classification-and-zoning-design.md`
  (~line 830) documents a privately-zoned element still readable by a
  non-owner *six minutes* after the control was written (denial began at
  seven), caused by the security connector's `refreshTimeInterval` (10 min)
  reload — "read it back immediately, so it must be fine" was exactly the
  misleading evidence there too. Their key diagnostic point: a
  **fixed-wall-clock cause** (everything becomes visible at once, at a time
  unrelated to load size — test with 50 links instead of 1,027 and see if
  the delay is still ~20 min) and a **volume-proportional cause** (async
  indexing/event-driven materialisation catching up, arriving in a stream)
  look identical from a single observation but have different fixes; the
  876→945(implied)→1,027 partial-recovery-at-12-minutes data point *mildly*
  favours volume-proportional, but "two points don't make a curve." Also
  worth checking directly: fetch one of the missing links by its own GUID
  during the window — if that resolves but the relationship is still absent
  from the related-element query, the write landed fine and only the
  traversal/index path lags, narrowing which service is actually behind. If
  this gets filed upstream, the volume-vs-fixed measurement is what turns
  it into a real bug report instead of getting bounced as "eventual
  consistency, working as intended."

Two independent, unconfirmed leads now on record (Kafka rebalance storms;
a refresh-interval-style cache) alongside a concrete diagnostic method
(fixed-wall-clock vs. volume-proportional, plus the direct-GUID-fetch
isolation check) for telling them apart before assuming either. Next real
step is still reproducing with a smaller, timed, instrumented load using
that method — not yet done.

**Reproduction attempt, 2026-09-20 (small end of the curve, not reproduced):**
after clearing with all 5 live peer sessions first (per `coordinate-shared-writes`),
ran a timed, instrumented small-scale reproduction against `qs-view-server`:
20 throwaway `Collection` elements created and each linked to a parent via
`CollectionMembership` (not the original `MemberDataField`/"field link" type
— a different relationship type, noted as a limitation below), polling
`get_collection_members` every 30s for up to 20 minutes, with a direct-GUID
isolation check ready for anything still missing at the deadline.

**Result: all 20 relationships were visible on the very first poll, ~1.1s
after the last one was created — no lag at all.** Cleanup (delete all 21
fixture elements) verified two independent ways: a direct-GUID fetch on
each (`404`/`OMAG-REPOSITORY-HANDLER-404-007`, confirmed real soft-delete,
not an ISSUE-63-style silent no-op) and a broad `find_collections` search
for the `test-fixture-issue108` prefix (0 results). The script itself was
run from an ephemeral per-session scratch directory, not committed anywhere
— reproduce via the same approach (create N Collections linked to a parent
via `_async_add_to_collection`, poll `_async_get_collection_members`) if
needed later; the approach, not the script file, is what's worth keeping.

**Per Egeria-trellis backlog review's own framework, this is one point on
the curve, not a refutation.** It's consistent with either "no bug under
current load" or "the lag is genuinely volume-proportional and 20 elements
is nowhere near the ~1,027-link scale that surfaced it originally" — the
one data point this run *can't* distinguish those two. Also a real
methodology gap versus the original report: this used `CollectionMembership`
on plain `Collection` elements, not the `MemberDataField` "field link"
relationship the original 1,027-link load actually exercised (ISSUE-102 is
in the same `MemberDataField` neighborhood, worth checking together). Server
load conditions also weren't recorded this run (no `ListAgents`/`:8810`
snapshot taken alongside the timings, despite the earlier plan to do so —
an execution gap, not a design one).

**Candidate next step, still open:** a same-relationship-type
(`MemberDataField`), same-order-of-magnitude (~200+) run, following the
same peer-clearance and independent-verification discipline, is what would
actually test the volume-proportional hypothesis — this run didn't attempt
that scale on its own initiative, since committing to it wasn't part of
what peers were asked to clear.

**Egeria team response, relayed 2026-10-05 (source `oak2026` fb3d6fce53; **fixes are in two unmerged PRs, so no build contains them, and nothing was tested against a live platform**):** not validated; no cache found. Best lead: a client clock ahead of the server's, with `effectiveFrom` set from it (related-element queries silently hide a relationship whose `effectiveFrom` is later than the server's "now"). They need, for one link still missing at ~12 minutes: its `effectiveFrom` and `createTime`, the server clock then, and whether the loader sets `effectiveFrom`. **Our facts:** pyegeria sets no `effectiveFrom`/`effectiveTo`/`effectiveTime` by default (model defaults are `None`; no clock call is tied to any `effective*` field; Dr.Egeria forwards an "Effective From" only if typed). Host and container clocks agree within 1 s on 2026-10-05; the 2026-09-20 load's values are unavailable.

**Update 2026-10-10:** the `oak2026` source (`fb3d6fce53`) the team examined is now in Egeria `main` (merged 2026-10-06, odpi/egeria#9363). No fix was made for this issue; the team's questions above still stand.

---

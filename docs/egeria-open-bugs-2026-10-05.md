# Open Egeria server bugs: validated, ranked, with fix status

**Compiled:** 2026-10-05, from `PYEGERIA_ISSUES.md` (the pyegeria issues log), then checked against Egeria's source and the running dev platform.
**Scope:** Egeria-side defects and gaps only. pyegeria-side issues (121, 126, 127, ...) and everything already resolved are excluded.

## Baseline (read this first)

| | |
|---|---|
| **Source analysed** | `odpi/egeria` `main` at **`449ad06894`** (2026-10-05 14:12 UTC, "Merge pull request #9357 from mandy-chessell/oak2026"), pulled into `~/localGit/egeria-v5-1/egeria-aug-5-24` |
| **Platform observed** | the running quickstart platform, image `egeria-quickstart-platform:local` **built 2026-10-03 ~18:46 UTC**, last (re)started 2026-10-05 01:43 UTC |
| **Redeploy** | **done 2026-10-05.** The platform image was rebuilt at 14:19 UTC (after the 14:12 UTC source tip) and `egeria-main` restarted at 14:39 UTC. Items marked "live" below were observed on the **2026-10-03** build unless they say "after redeploy". |

**Update, 2026-10-05, after the redeploy** (platform rebuilt from the pulled source: image created 14:19 UTC, `egeria-main` restarted 14:39 UTC, healthy). Four live checks have now been run on that build:

| Issue | Result on the rebuilt platform |
|---|---|
| **ISSUE-125** (`deleteEnumDef`) | **still fails**, identically; the enum also survived the restart |
| **ISSUE-124** (`updateTypeDef`) | **still fails**, with the same `updatedBy` error |
| **ISSUE-102** (`MemberDataField` min/max) | **no longer reproduces**: four min/max pairs all stored correctly. **This corrects my source-based call of "not addressed"** (see "How to read this") |
| **ISSUE-90** (engine-host retry loop) | **not reproduced, but the trigger was absent**, so it is *not shown fixed*: no refusals and calm CPU, yet no `APPROVED` engine action exists for the loop to retry |

**ISSUE-79** (folder from template, run 2026-10-06 with current pyegeria): the new folder **has a `ResourceConnection`**, so the old `deepCopy:false` default was the cause of the missing connection; the survey itself was not run, so "survey completes" is still unproven (section 5).

The remaining re-tests (112, 117, 85 create, 89, 95 create, 108) have not been run yet.

**Earlier update, 2026-10-05 afternoon:** after pulling the source, every "not addressed" finding was re-checked against `449ad06894` itself. **No status changed.** The result for each is repeated under "Re-check at `449ad06894`" below. The next step is to redeploy and re-test live (plan at the end), because a fix present in source says nothing about the build that is running.

## Egeria team response (relayed 2026-10-05 evening)

The Egeria team answered this list (via the owner and the Resource Explorer coordinator), from source `oak2026` `fb3d6fce53` (main through #9358). **Read their hedges first:** every fix below is in source on the `oak2026` branch in **two PRs that are not merged to `main`, so no build contains them**. They traced code and, for ISSUE-102, ran a scratch program; they **tested nothing against a live platform** and will confirm when the fixes merge.

| Issue | Egeria team verdict | Our check (2026-10-05) |
|---|---|---|
| 102 | **Not reproduced** in Egeria; builder and converter round trip returns `position=3, min=1, max=5`; lower layers not traced. They want the raw request, raw response and read-back endpoint | Agrees: it also **no longer reproduces** on our rebuilt platform. The original raw response was never captured |
| 90 | **Valid, fixed pending merge**: one unreadable action target throws, the outer `catch` ends the sweep, newest-first paging brings the bad page back; the sweep is also unfiltered by engine | Agrees with our source reading; the engine-scoped sweep is new to us |
| 112 | **Valid, fixed pending merge**: a store whose connector cannot write now answers 400 `OMAG-COMMON-400-034` | Agrees |
| 124 | **Valid, fixed pending merge**; `updateTime` was missing as well as `updatedBy` | Our `updatedBy` analysis was right but **incomplete** |
| 117 | **Valid, fixed pending merge**: the `qualifiedName` rename happens *after* the Memento classification; the top-level asset is also never renamed | Agrees with the symptom; the cause is sharper than our inference |
| 125 | **Valid, fixed pending merge**; cause is **not** a GUID-map problem: `OMRSRepositoryContentValidator:877` passes `(guidParameterName, guid)` to an overload expecting `(guid, name)`, so every `deleteAttributeTypeDef` fails | **Confirmed in source; our GUID-map theory was wrong** |
| 79 | **Very likely fixed** by `e01426db86` (2026-08-30); also: *check pyegeria does not send `deepCopy:false`* | **Probably our bug**: pyegeria sent `deepCopy:false` by default until 2026-09-29 (see section 5) |
| 89 | `bearerTokenTimeout` in hours, default 1; **correction: `rsa.key-id` does not make tokens survive a restart** | **Confirmed in `RSAGenerator`**; our earlier statement was wrong |
| 95, 85 | Confirmed (content pack present; server endpoints exist) | Agrees; the pyegeria `SolutionPort` methods are still missing |
| 108 | **Not validated**; best lead: a client clock ahead of the server's, with `effectiveFrom` set from it | pyegeria sets **no** `effectiveFrom` by default; clocks agree within 1 s now; the Sept 20 load cannot be inspected |

The stray enum `PyegeriaTmpCuisineType` (`118441be-6e03-4442-96c6-e431f75fcb3f`) can only be deleted after a build with the ISSUE-125 fix is deployed.

## How to read this

- **Ranking** is by (1) silent wrong data, (2) whole-platform impact, (3) a feature blocked outright, (4) workflow friction or missing capability. Within a tier, deterministic beats intermittent.
- **Validated** means the log records a live reproduction or a confirmation against Egeria's source. Ten are validated; a further one (ISSUE-108) is a single report that has not been reproduced and is listed separately.
- **Fix status** compares the source at `449ad06894` (2026-10-05) with the checkout as it stood on 2026-09-15 (`df82f4feca`, 70 commits earlier), by file, by commit message and by reading the code.
- **Caveat that matters:** "fixed in source" is not "fixed on the dev platform", and the reverse also holds. Items marked *live* were tested against a running server; the build is named where it matters.
- **Lesson from ISSUE-102:** comparing source files said "not addressed" (no commits to the bean, converter or builder), yet the live re-test shows the bug gone. A source comparison can miss a fix in a file I did not inspect, or the build that originally reproduced the bug may simply have been older than my baseline. **Treat every "not addressed" below that rests on source alone as provisional until it is live-tested.** The live-tested ones (124, 125) are firm.

## Summary

| Rank | Issue | Defect | Fix status |
|---|---|---|---|
| 1 | **ISSUE-90** | `qs-engine-host` retries a failing `startMissedEngineActions` forever; platform and Postgres CPU saturated | **Valid; fix in Egeria source, pending merge** (no build has it). Live after redeploy: not reproduced, but the trigger was absent |
| 2 | **ISSUE-112** | `saveClientSideSecret` / `deleteClientSideSecret` report success without writing when the connector is not a `YAMLSecretsFileConnector` | **Valid; fix in Egeria source, pending merge** (no build has it); not live-tested |
| 3 | **ISSUE-124** | `updateTypeDef` can never succeed: the patch is built without the mandatory `updatedBy` | **Valid; fix in Egeria source, pending merge**; **re-tested live after the redeploy: still fails** |
| 4 | **ISSUE-117** | Cascade delete on the soft-delete path fails partway, leaving a half-deleted state | **Valid; fix in Egeria source, pending merge** (no build has it); not live-tested |
| 5 | **ISSUE-79** | Native survey of a template-created `FileFolder` fails: `assetConnector` is null in `BasicFolderConnector.getFile()` | **Probably a pyegeria bug** (`deepCopy:false` default until 2026-09-29); Egeria also repaired a related server issue; needs a live re-test |
| 6 | **ISSUE-125** | `deleteEnumDef` answers 500 "unknown TypeDef" for an enum the server lists | **Valid; fix in Egeria source, pending merge**; cause corrected (argument order, not a GUID map); **re-tested live: still fails** |
| 7 | **ISSUE-95** | No catalog template for "Apache Kafka Server" | **Addressed**, confirmed by live probe |
| 8 | **ISSUE-85** | No REST endpoint to create a `SolutionPort` | **Addressed** in source, confirmed by live probe |
| 9 | **ISSUE-89** | No configurable bearer-token lifetime | **Addressed** in source (2026-09-19) |
| 10 | **ISSUE-102** | `MemberDataField.minCardinality` silently stored as `maxCardinality`'s value (was rank 1) | **No longer reproduces** on the rebuilt platform (live, four cases); the Egeria team could not reproduce it either |
| n/a | ISSUE-108 | Relationships invisible to queries for up to ~20 min after creation | **Not validated**, cannot assess |

**Status with the Egeria team:** 90, 112, 117, 124 and 125 are acknowledged as valid with fixes in source (`oak2026`), pending merge and then a deployed build; 102 and 108 could not be reproduced by them; 79 is probably on our side; 95, 85 and 89 are settled.

---

## Open and validated

### 1. ISSUE-90: engine host retries `startMissedEngineActions` forever

- **Evidence:** observed on one quickstart: the same refusal, `OMAG-SERVER-SECURITY-403-007 User generalnpa is not authorized to issue operation Read on <guid> anchor element DigitalProductFamily`, thousands of times; the platform container at 200-330% CPU and its Postgres at 500-750% on an idle machine. A second, identical platform never showed it, so it depends on initialisation history. The log entry's title carries "[fixed?]", which is unconfirmed.
- **Impact:** platform-wide slowdown while it lasts. It is intermittent, which lowers its rank despite the severity.
- **Fix status: not addressed.** `GovernanceEngineHandler.startMissedEngineActions` wraps the paged fetch in one outer `try`/`catch`: an exception from `getActiveEngineActions` aborts the whole pass at that page, and the next scheduled pass fails at the same page again. The only change between 2026-09-15 and now is in the per-action `catch`, where `logException` became `logMessage` (less log volume), which does not touch the loop.
- **Suggested upstream change (from the log):** treat an authorization failure for a specific engine action as terminal for that action (log once, skip, continue), and/or give `generalnpa` read access to the elements its engine actions anchor to.
- **Re-tested after the redeploy (2026-10-05, read-only, 32 minutes after the 14:39 UTC restart):**
  - **Not reproduced.** Zero `ENGINE-HOST-SERVICES-2002`, `startMissedEngineActions` or `OMAG-SERVER-SECURITY-403-007` in the platform log; the engine host refreshes its engines normally. The platform container is at about 50% of one core and Postgres at about 30%, against 200-330% and 500-750% originally.
  - **The trigger was absent, so this proves little.** Only two engine actions are active, a `REQUESTED` PostgreSQL survey and the `IN_PROGRESS` watchdog, and `startMissedEngineActions` only processes `APPROVED` ones. A clean run cannot tell "fixed" from "not triggered", exactly as the original report warned.
  - **Unreadable anchors do exist.** 381 `OPEN-METADATA-SECURITY-0011` read refusals, all for `erinoverview` (my scripts' account), across 11 elements anchored to a `DigitalProduct` (6) or `DigitalProductFamily` (5), in bursts of 20 that match page-sized searches, not a steady loop. None were for the engine-host user `generalnpa`, and the original element (`a0baa4da-...`) is not among them. So quickstart content does carry elements an ordinary user cannot read, which is the precondition the report hypothesised. Whether an engine action anchors to one is not shown.
  - **Verdict: still open, latent.** The outer `catch` in source is unchanged, so an `APPROVED` action with an unreadable anchor would still loop.
- **Egeria team response (2026-10-05):** valid; fix in source on `oak2026`, pending merge. Cause: `startMissedEngineActions` runs every 5 s per engine; `getActiveEngineActions` reads every action target and requester, so one target anchored to an element the engine's user cannot read (zone) throws, the outer `catch` ends the sweep, and newest-first paging brings the bad page back. The sweep is also unfiltered by engine (every engine pages all active actions every 5 s), a likely contributor to the idle CPU (unmeasured). Fixes: unreadable actions filtered out, one-time error logging, anchor message arguments in the right order, an engine-scoped sweep via a new `.../governance-engines/{guid}/approved-engine-actions` endpoint, and anchor-refused search results filtered instead of logged as unauthorized. The last point may also explain the very high rate of read refusals seen on the platform.

### 2. ISSUE-112: secrets calls report success without writing

- **Evidence:** confirmed in source and live. `AutomatedCurationRESTServices.saveClientSideSecret` and `deleteClientSideSecret` only act `if (connector instanceof YAMLSecretsFileConnector)`; there is no `else`, no error and no log, so any other connector resolves to a plain success `VoidResponse`.
- **Impact:** a secret is not saved while the call says it was. No workaround is recorded; a caller would have to read back to know.
- **Fix status: not addressed.** `AutomatedCurationRESTServices.java` has no commits since 2026-09-15, and the `instanceof` block at line 480 still has no `else` branch.
- **Egeria team response (2026-10-05):** valid; fix in source on `oak2026`, pending merge. A store whose connector cannot write secrets collections now gets a 400 `OMAG-COMMON-400-034` naming the operation, asset and connector class. Only `YAMLSecretsFileConnector` supports save and delete (`SecretsStoreConnector` gained `isSecretsCollectionUpdateSupported()`, and the others reject with `OCF-CONNECTOR-400-012`). Also fixes a `methodName` slip and always disconnects the connector.

### 3. ISSUE-124: `updateTypeDef` can never succeed

- **Evidence:** live and from source, 2026-10-05. A valid `OpenMetadataTypeDefPatch` is rejected with `OMRS-REPOSITORY-400-069 ... mandatory field updatedBy set to null`. The request arrived intact: its attribute definition is visible in the error text.
- **Cause:** `OpenMetadataStoreRESTServices.updateTypeDef` calls `converter.getTypeDefPatch(requestBody, methodName)`. `OMRSTypeDefConverter.getTypeDefPatch` takes no user id and contains no `setUpdatedBy`, yet `OMRSMetadataCollection.updateTypeDef` requires `updatedBy` to be non-null. `OpenMetadataTypeDefPatch` has no `updatedBy` field, so a client cannot supply it.
- **Impact:** the feature is blocked outright, with no client workaround. The upstream fix is small: pass `userId` to the converter and set it.
- **Fix status: not addressed.** The dynamic type APIs arrived in commit `a33921ffd9` (2026-09-24). Nothing since has touched this path. The one `setUpdatedBy` in `OpenMetadataStoreRESTServices.java` is in the *response* conversion, not the patch.
- **Re-tested after the redeploy (2026-10-05, build of 14:19 UTC):** a throwaway entity type (primitive attribute only) was added, then patched with one new attribute. The server rejected the patch with the **same** `OMRS-REPOSITORY-400-069 ... mandatory field updatedBy set to null` (`TypeDefPatch{... applyToVersion=1, updateToVersion=2, newVersionName=2.0, updatedBy=null ...}`). The type was deleted afterwards and verified gone. **Confirmed still present.**
- **Upstream:** not yet reported.
- **Egeria team response (2026-10-05):** valid, and `updateTime` was missing as well as `updatedBy` (so our analysis was right but incomplete). Fix in source on `oak2026`, pending merge: `getTypeDefPatch` takes the user and sets both, with a new `DynamicTypeFVT`. No build contains it.

### 4. ISSUE-117: cascade delete fails partway on the soft-delete path

- **Evidence:** reproduced live. The failure is `OMAG-REPOSITORY-HANDLER-400-010` when the delete takes the soft-delete (Memento) path, which it does for an asset that lineage relationships point at. The failure is **not atomic**: the anchored `Endpoint` had already been soft-deleted when the call errored, leaving the asset and its Connection live. A fresh asset with the identical call purges cleanly.
- **Cause:** inferred from the error and timestamps, not confirmed in source: the cascade re-reads anchored elements it has just marked with Memento using the caller's `forLineage=false`.
- **Impact:** a half-deleted state. **Workaround confirmed:** repeat the delete with `forLineage: true`.
- **Fix status: not addressed.** A search of commit messages since 2026-10-02 for memento / soft-delete / cascade / forLineage finds nothing. (That is a message search, not a code diff.)
- **Upstream:** not yet reported.
- **Egeria team response (2026-10-05):** valid; the cause is the `qualifiedName` rename that happens *after* the Memento classification in `archiveBeanInRepository`: the re-read uses `forLineage=false`, so the Memento'd element is invisible and the first member (the Endpoint) fails with 400-010. There is also a silent defect: the **top-level archived asset is never renamed** (the generic `OpenMetadataRoot` type fails the `Referenceable` test). Fix in source on `oak2026`, pending merge: a two-pass archive (collect, then archive deepest-first, renaming before the Memento), internal reads with `forLineage=true`, the top-level asset renamed, and retries that finish a half-done archive.

### 5. ISSUE-79: native survey of a template-created `FileFolder` fails

- **Live result 2026-10-06:** with current pyegeria (no `deepCopy` in the request) a folder created from the File System Directory template **has 1 connection (`ResourceConnection`)**, read back through the classification explorer; it was then deleted and verified gone. **This confirms the `deepCopy:false` default as the cause of the missing connection.** The survey was not run, so "the survey completes" remains unproven.
- **Evidence:** reproduced live 2026-08-27, re-checked 2026-08-28 with an identical failure (`assetConnector` null in `BasicFolderConnector.getFile()`). The Egeria team (2026-08-30) found the originally recorded cause ("template creation never wires a Connection") to be **false**, fixed a related NPE, and left the reported failure open.
- **Impact:** blocks surveying those folders.
- **Fix status: probably a pyegeria bug, now fixed on our side; not yet shown live.** The Egeria team points to `e01426db86` (2026-08-30: PostgreSQL supertype-chain repair on server start after the 08-27 `ResourceConnection` re-parenting, plus a clearer "no connector for asset" error) and asked us to check that pyegeria did not send `deepCopy:false`. **It did.** `TemplateRequestBody.deep_copy` defaulted to `False` from 2026-01-09 until it was fixed on 2026-09-29 (#399, first released in v6.1.23), and the model is serialised with `exclude_none`, which keeps `False`. The report's helper, `create_folder_element_from_template`, builds its body without `deepCopy`, so every folder it created sent `"deepCopy": false`; Egeria then copies only the top-level element, **no `ResourceConnection`**, which is exactly a null `assetConnector` in `BasicFolderConnector.getFile()`. That fits the Egeria team's own observation that connector-created folders all had a connection. **To confirm:** create a folder from the template with current pyegeria, check it has a `ResourceConnection`, then survey it (a write window). The Egeria server fix may matter too, but it is no longer the first suspect.

### 6. ISSUE-125: `deleteEnumDef` answers 500 for a listed enum

- **Evidence:** live, 2026-10-05. After `add_enum_def`, an entity type using the enum, and a successful `delete_type_def` of that type, the enum delete answered `OMRS-CONTENT-MANAGER-500-001 ... getAttributeTypeDef has detected an unknown TypeDef <guid> ... on behalf of method deleteAttributeTypeDef`. `get_attribute_types` still lists the enum.
- **Cause (found by the Egeria team; I confirmed it in source at `449ad06894`):** `OMRSRepositoryContentValidator.java:877` calls `repositoryContentManager.getAttributeTypeDef(sourceName, guidParameterName, guid, methodName)`, but that 4-argument overload is `(sourceName, attributeTypeDefGUID, attributeTypeDefName, methodName)`. So the "GUID" passed is the *parameter-name string* and the "name" is the real GUID, which is exactly why the error text prints our real GUID as the unknown type. Every `deleteAttributeTypeDef` through the local repository fails (and `reIdentifyAttributeTypeDef` and the enterprise equivalents). **My earlier theory (a GUID map written in only one place) was wrong.**
- **Impact:** an enum added through the API cannot be removed. **A stray throwaway enum, `PyegeriaTmpCuisineType` (`118441be-6e03-4442-96c6-e431f75fcb3f`), is left on the shared dev platform**; the Egeria team says it is deletable only after a build containing the fix is deployed.
- **Fix status:** the Egeria team has the fix in source on `oak2026`, pending merge to `main`; **no build contains it**.
- **Re-tested after the redeploy (2026-10-05, build of 14:19 UTC from `449ad06894`, `egeria-main` restarted 14:39 UTC):** the enum **survived the restart** (still listed by `get_attribute_types`: API-defined types do persist), and `delete_enum_def` failed with the **identical** `OMRS-CONTENT-MANAGER-500-001 ... unknown TypeDef 118441be-... on behalf of method deleteAttributeTypeDef`. This is now explained: the failure is the argument-order bug above, which does not depend on what was loaded at startup.
- **Upstream:** not yet reported.

---

## Addressed (or appear to be)

### 7. ISSUE-95: no catalog template for "Apache Kafka Server"

- **Status: addressed on the dev platform, confirmed live.** The running platform now resolves a template: `get_template_guid_for_technology_type("Apache Kafka Server")` returns `5e1ff810-5418-43f7-b7c4-e6e062f9aff7`. Egeria's source at `449ad06894` also ships `ApacheKafkaContentPack.omarchive` (109 mentions of "Apache Kafka Server"). This looks like a content-pack loading matter rather than a code defect; the log said the owner was investigating.
- **Follow-up:** `Create Kafka Server Element` can be re-tested live.

### 8. ISSUE-85: no REST endpoint to create a `SolutionPort`

- **Status: addressed in the server.** At `449ad06894`, `createSolutionPort` and `createSolutionPortFromTemplate` exist, with endpoints `POST /solution-ports`, `/solution-ports/from-template`, `/solution-ports/{guid}/update`, `.../delete`, `/by-name`, `/by-search-string` and `.../retrieve`. They first appear in commit `571034df11` (2026-09-06), three days after the issue was logged. **Live probe:** the running platform answers `POST /solution-ports/by-name` with a 200, so those endpoints exist there too.
- **pyegeria follow-up, not an Egeria bug:** the refreshed `.http` snapshot lists none of these endpoints and `pyegeria/omvs/solution_architect.py` has no `create_solution_port` (or update, delete, find). This belongs on the audit triage list.

### 9. ISSUE-89: no configurable bearer-token lifetime

- **Status: addressed in source.** Commit `a1f228d4a9` (2026-09-19, "Add control of bearer token timeout") added a `bearerTokenTimeout` property, read by `TokenService`, in **hours** with a default of 1, present in `application.properties` and `container.application.properties`. The request asked for seconds; Egeria chose hours.
- **Not covered:** a token refresh operation (the issue's optional second ask). The signing key changes on every restart, and **`rsa.key-id` does not prevent that** (confirmed in `RSAGenerator.generateRSAKeyPair`: it always makes a fresh key pair and only uses the id as a label); the Egeria team plans to persist the signing key in the next release. **Not verified on the dev platform**, whose image may predate the change.

### 10. ISSUE-102: `MemberDataField.minCardinality` silently persisted as `maxCardinality`

- **Original finding (2026-09-17):** with a raw request, `position=3, minCardinality=1, maxCardinality=5` read back as `minCardinality=5`, with no error.
- **Raw capture for the Egeria team (2026-10-06):** one more link with the exact request `position 3, minCardinality 1, maxCardinality 5` (answer `VoidResponse`) and a read-back through the endpoints lookup (`OpenMetadataRelationshipListResponse`) returned `minCardinality "1"`, `maxCardinality "5"`: still no repro, now with raw request, response and read-back recorded (local file `live_102_raw.out`; their three asks are met).
- **Re-tested live after the redeploy (2026-10-05, build of 14:19 UTC from `449ad06894`):** one throwaway `DataStructure` and four `DataField`s were linked with `MemberDataField` and each relationship was read back through the endpoints lookup. **All four stored correctly**; `position` was right every time:

  | sent (min, max) | stored (min, max) |
  |---|---|
  | 1, 5 | 1, 5 |
  | 2, 7 | 2, 7 |
  | 0, 5 | 0, 5 |
  | 3, *omitted* | 3, 0 |

  Everything was deleted child-first and verified gone; no leftovers.
- **Status: no longer reproduces.** I cannot say *why*. My earlier source comparison found no change to `MemberDataFieldProperties`, `PartOfRelationshipProperties`, the read converter or the relationship builder, and called the bug "not addressed". That call was wrong. Either the fix is in code I did not inspect, or the build that showed the bug on 2026-09-17 was older than my 2026-09-15 baseline. It would be worth asking the Egeria team which change fixed it before closing the issue for good.
- **A side observation, not part of this bug:** when `maxCardinality` is omitted it is stored as `0`, which sits below a supplied minimum (case 4). The bean's default is `0` and its documentation says `-1` means unlimited, so an omitted maximum silently becomes "at most zero". That is plausibly a separate wart, not something I have validated further.

---
- **Egeria team response (2026-10-05):** **not reproduced** in Egeria. They traced every layer, and a server-side builder-plus-converter round trip returns `position=3, min=1, max=5`; the layers below the builder store properties by name and were not traced. They asked for the exact request body, the raw response before pyegeria formatting, and the read-back endpoint, to tell a client-side formatting fault from a read-path fault. **Our answer:** the request was `NewRelationshipRequestBody` with `properties` `{class: MemberDataFieldProperties, position: 3, minCardinality: 1, maxCardinality: 5}` sent through `DataDesigner._async_link_member_data_field`. The original raw response was **not captured** on 2026-09-17 (the entry's read-back shows camelCase property names, which suggests a raw property read, but I cannot prove which call). On the 2026-10-05 build it does **not** reproduce for us either. A fresh raw capture on the current build is possible if useful.

## Reported but not validated

### ISSUE-108: relationships invisible to related-element queries for up to ~20 minutes

- One report from a Dr.Egeria bulk load: 876 of 1,027 expected links visible immediately, 82 structures still short at 12 minutes, all present at 20 minutes, with no errors at any point. Not independently reproduced. Two unconfirmed leads are on record (Kafka rebalance storms, and a fixed wall-clock delay), and the log's own next step is a smaller, timed, instrumented reproduction.
- **Cannot be assessed against source without a reproduction.** If real it would rank high, because it produces false "missing" results after a bulk load.
- **Egeria team response (2026-10-05):** **not validated**; no cache found. Best lead: a client clock ahead of the server's, with `effectiveFrom` set from it (related-element queries hide a relationship whose `effectiveFrom` is later than the server's "now", silently). They need, for one link still missing at about 12 minutes: its `effectiveFrom` and `createTime`, the server clock at that moment, and whether the loader sets `effectiveFrom` at all. **Our facts:** pyegeria sets **no** `effectiveFrom`, `effectiveTo` or `effectiveTime` by default (the model defaults are `None`, no clock call is tied to any `effective*` field, and Dr.Egeria forwards an "Effective From" only if the author typed one), so the lead needs a load document that set it. Host and container clocks agree within 1 s now; whether they did on 2026-09-20 cannot be checked, and Docker Desktop VM clock drift after laptop sleep is a hypothesis I have not measured. The load's `effectiveFrom` and `createTime` values are not available to me.

### Two further reports from the Resource Explorer coordinator's JDBC cataloguer scratch test (2026-10-05)

Reported by the Coordinator session after its own live run on the rebuilt platform. **Not reproduced by me and not yet in `PYEGERIA_ISSUES.md`**; recorded here as leads, with the Coordinator's wording.

- **`/archive` endpoint answers 500.** Archiving a `DeployedDatabaseSchema` through the view server fails with a `DeployedRequestBody` class-name error, on the build running since 14:39 UTC.
- **An array `includeSchemaNames` in a survey's own connection configuration is ignored.** The survey runs but does not restrict itself to the listed schemas.

Both need a minimal reproduction (the request body and the response) before they can be ranked or filed.

---

## Re-check at `449ad06894`

Run against the pulled source on 2026-10-05. Each line is what was measured; "unchanged" means the defect's code path is as described above.

| Issue | Measured at `449ad06894` | Result |
|---|---|---|
| 124 | `OMRSTypeDefConverter.getTypeDefPatch`: `setUpdatedBy` occurrences = 0 | unchanged, still missing; **live re-test after redeploy confirms it still fails** |
| 125 | `OMRSRepositoryContentValidator.java:877` calls `getAttributeTypeDef(sourceName, guidParameterName, guid, methodName)`; the overload is `(sourceName, guid, name, methodName)` | unchanged, and **this is the real cause** (found by the Egeria team, confirmed here); our earlier GUID-map explanation was wrong |
| 112 | `AutomatedCuration...RESTServices`: the `instanceof YAMLSecretsFileConnector` block (line 480) has no `else` | unchanged |
| 90 | `startMissedEngineActions` vs 2026-09-15: 11 changed lines, all in the per-action `catch` (`logException` to `logMessage`); the outer `catch` that aborts the pass is untouched | unchanged apart from less log output |
| 102 | `MemberDataFieldProperties` and `PartOfRelationshipProperties`: 0 commits since 2026-09-15 | source unchanged, **yet the bug no longer reproduces live** (section 10): the source comparison gave a false "not addressed" |
| 117 | commit messages since 2026-10-02 matching memento / soft-delete / cascade / forLineage: 0 | unchanged |
| 79 | `BasicFolderConnector.java`: 0 commits since 2026-09-15 | unchanged in that file; the Egeria team points to `e01426db86` (2026-08-30) and to our own `deepCopy:false` default (section 5) |
| 85 | `createSolutionPort(` present in `SolutionArchitectRESTServices` | still addressed |
| 89 | `bearerTokenTimeout` present in `application.properties` | still addressed |
| 95 | (live) template lookup resolves | still addressed |

## Live re-test plan after the redeploy

Nothing here has been run against a build containing `449ad06894`. Items marked **write** create and then remove throwaway elements, so they need a coordinated write window on the shared platform.

| Issue | Test | Kind | If fixed, expect |
|---|---|---|---|
| 125 | First confirm the stray enum `PyegeriaTmpCuisineType` (`118441be-6e03-4442-96c6-e431f75fcb3f`) is still listed by `get_attribute_types`, then retry `delete_enum_def` | read-only, then one **write** | the enum survives a redeploy (types persist), and the delete now succeeds. **DONE 2026-10-05: it survived; the delete still fails identically.** |
| 124 | Add a throwaway entity type (no enum), send a patch that adds one attribute, read back, delete it | **write** | the patch is accepted and the new attribute appears in version 2. **DONE 2026-10-05: still rejected with the same `updatedBy` error.** |
| 102 | Link a throwaway `DataField` to a `DataStructure` with `position=3, minCardinality=1, maxCardinality=5`, read the relationship back | **write** | `minCardinality` reads back as 1, not 5. **DONE 2026-10-05: reads back correctly in all four cases; no longer reproduces. 2026-10-06: raw request/response captured, same result.** |
| 112 | Call `saveClientSideSecret` against a secrets store whose connection resolves to a non-YAML connector | **write** | an error, not a silent success |
| 117 | Cascade-delete an asset that is a subscription destination, with `forLineage=false` | **write** | the delete completes, or fails atomically |
| 79 | Create a folder from the template with current pyegeria (deepCopy omitted), check it has a `ResourceConnection`, then initiate a native survey on it | **write** (creates an element and an engine action) | a connection is present and the survey completes, with no null `assetConnector`. If it fails only on a build without `e01426db86`, the server fix matters too **Connection check DONE 2026-10-06: present. Survey not run.** |
| 90 | Watch `qs-engine-host` logs for `ENGINE-HOST-SERVICES-2002` repeating, and container CPU, over ten minutes | read-only | no repeating refusal. Note it depends on startup history, so a clean run proves little. **DONE 2026-10-05: clean, but no `APPROVED` engine action existed to trigger it, so inconclusive. A real test needs an `APPROVED` action anchored to an element the engine-host user cannot read.** |
| 85 | Create a throwaway `SolutionPort`, read it back, delete it | **write** | create succeeds (the by-name read already answers 200) |
| 89 | Set `bearerTokenTimeout` to a non-default value, restart, decode a token's `exp - iat` | config change and restart | the lifetime follows the property (hours) |
| 95 | Re-run the Kafka template lookup, then `Create Kafka Server Element` | read-only, then **write** | the lookup resolves (it already does) and the element is created |
| 108 | A timed, instrumented bulk link load, polling related-element queries each minute | **write** | all links visible promptly (this one is not yet validated at all) |

The refreshed `.http` collection has not been updated yet; once it has, the new endpoints (for example the `SolutionPort` set) should be checked against it as well.

---

## Method and limits

- The ten validated items come from the issues log; ISSUE-124 and ISSUE-125 were found and live-tested in this session, so their evidence is first-hand. I did **not** re-test the older items live today.
- Fix status comes from comparing the source at `449ad06894` with the 2026-09-15 checkout for the specific files involved, searching commit messages, and reading the code. Source comparison can show that a fix exists but not that a given platform build contains it.
- Live checks: two read-only probes on the 2026-10-03 build (`POST /solution-ports/by-name`, the Kafka template lookup), then three write re-tests on the **rebuilt** platform (ISSUE-125, 124 and 102), each cleaned up and verified gone by GUID, and one read-only check of the rebuilt platform's logs, CPU and active engine actions (ISSUE-90).
- Commit-message searches (ISSUE-117) find nothing relevant, but a message search is weaker than reading the diff; a fix could be hiding under an unrelated message.
- `~/localGit/egeria-v6/egeria` is still on the 2026-09-15 commit (70 commits behind); the pulled copy is `~/localGit/egeria-v5-1/egeria-aug-5-24`.

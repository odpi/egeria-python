# Open Egeria Server Issues

This is a standalone extract of every **currently open, Egeria-Server-side**
issue from [`PYEGERIA_ISSUES.md`](PYEGERIA_ISSUES.md) — nothing here can be
resolved by editing this repo; each needs a server-side fix, an upstream bug
report, or a deployment/config change. It exists to hand to whoever owns the
Egeria server side of a question without making them wade through
`PYEGERIA_ISSUES.md`'s pyegeria-side entries and closed/resolved appendix.

**`PYEGERIA_ISSUES.md` remains the source of record.** This file is a
generated-by-hand extract of its "Open Egeria Server issues" section as of
2026-08-30 — re-derive it from that section (don't edit the two
independently) whenever an entry here changes status, gets fixed upstream,
or a new server-side issue is filed.

**Down to 2 entries as of this refresh** (was 5): ISSUE-52, ISSUE-54, and
ISSUE-41/PY-21 were all confirmed fixed server-side 2026-08-30 (Egeria team)
and moved to `PYEGERIA_ISSUES.md`'s "Fixed / Resolved" appendix — see that
file for the full writeups. ISSUE-38/PY-18 also has a server-side fix as of
the same date but is deliberately kept open here pending pyegeria-side
verification against real data.

---

These need an Egeria Server-side fix, an upstream bug report, or a
deployment/config change — nothing here can be resolved by editing this
repo. Where an entry has a known pyegeria/Dr.Egeria follow-on once the
Egeria side lands, it's noted inline (also cross-referenced from the
"Open pyegeria items" section below where the follow-on is substantial
enough to track there too).

---

### ISSUE-38 (PY-18): `count_relationships_between_elements("Exception")` (276) disagrees with `ClassificationExplorer.get_relationships("Exception")` (55)

**Update 2026-08-30, from the Egeria team (Mandy Chessell).** Leaving this
entry in "Open Egeria Server issues" until the verification below has been
run against real data — the Egeria side is done, but this entry has been
re-measured and re-confirmed several times, and it shouldn't move to
Fixed/Resolved on the strength of a change nobody has yet pointed at the
data that produced the original report.

**Status: resolved on the Egeria side 2026-08-30** (`omf-metadata-spring`,
`omf-metadata-server`, `generic-handlers`, and the OMF Java client) —
**awaiting verification from the pyegeria side**, see below. The two
numbers are not going to be made equal, because they are answers to two
different questions and both are wanted; what has changed is that the
caller now chooses which one they get.

**What the difference actually was.** `findAttachmentLinks()` puts every
relationship it retrieves through a visibility check on the entities at
both ends, and silently drops the ones whose anchor the caller cannot
read. `countAttachmentLinks()` skipped that check — deliberately, and
documented as such in its own javadoc, because applying it means fetching
every matching relationship, which is the cost the count exists to avoid
— and also ignored `effectiveTime`. So the count was of what matches the
search and the list was of what the caller may see. That answers this
entry's open question ("what does the metadata-expert count include for
`Exception` that the classification-explorer traversal excludes?"):
relationships with an end whose anchor is not readable by the calling
user, plus anything outside the effectivity window. It also explains why
only `Exception` diverged among the types tested — it is the type whose
ends are most likely to have been deleted or anchored to something the
caller cannot see — and why the divergence tracked the demo data rather
than staying at a fixed size.

**The new option.** Both counting endpoints take a `pushDown` query
parameter, `required=false`, default `true`:
```
POST .../users/{userId}/relationships/by-search-conditions/count?pushDown=false
POST .../users/{userId}/metadata-elements/by-search-conditions/count?pushDown=false
```
- `pushDown=true` (the default, and exactly the existing behaviour) — the
  repository counts the matching rows itself. Fast, and counts what
  matches the search.
- `pushDown=false` — the relationships are retrieved and counted, so the
  answer agrees with the list by construction, at the cost of reading
  every one of them.

Nothing changes for a caller that does not send the parameter. The same
choice is on the Java client (`countMetadataElements(..., pushDown)` and
`countRelationshipsBetweenMetadataElements(..., pushDown)` on
`OpenMetadataStore` and `OpenMetadataClient`), with the existing
signatures kept and defaulting to `true`.

**The test the pyegeria side should run to prove it.** Against the
environment that produced the original numbers, using whatever the
current counts are rather than the 58/57 recorded here — the demo data
has moved several times during this entry's life, and what matters is the
relationship between the numbers, not their values:

1. **The accurate count should equal the list.** For
   `relationshipTypeName: "Exception"`, the count with `pushDown=false`
   should equal `len(ClassificationExplorer.get_relationships("Exception"))`
   exactly. This is the assertion that closes the entry — it is the
   discrepancy this entry is about, stated as an equality.
2. **The fast count should be unchanged.** The same call with
   `pushDown=true`, and with the parameter omitted altogether, should both
   return what the count returns today. If either moves, something
   regressed for every existing caller.
3. **A type that already agreed should still agree both ways.**
   `SemanticAssignment` matched at 401=401 when this entry was last
   measured. Both `pushDown` values should return that same number — the
   retrieval route must not lose or double-count anything on a type where
   there was never a discrepancy to resolve.

Worth capturing while verifying: the difference between the two counts is
the number of matching relationships the calling user cannot fully see.
If it is not the 1 recorded here, that is not a failure — it is a
measurement of the current data — but it is worth writing down, because a
large difference on a type that should be fully visible would be a
separate finding. If test 1 comes out unequal, the remaining difference is
not the visibility check and this entry should stay open with both
numbers recorded.

**Follow-on for pyegeria, once verified:** the Overview dashboard's
current workaround — keeping relationship counts on
`ClassificationExplorer.get_relationships` while using native counting
only for element counts — can be revisited.
`count_relationships_between_elements(..., pushDown=False)` gives the same
number as the traversal without materialising the list client-side. Keep
in mind that `pushDown=false` reads every matching relationship
server-side, so it is the right choice for a number a user is going to
compare against a list they can also see, and the wrong choice for a
headline figure over a large type where speed is what matters. That
trade-off is now the caller's to make, which is what this entry was
ultimately asking for.

**Egeria-side test cover:** `CountPushDownFVT` in
`open-metadata-test/open-metadata-fvt/query-fvt` checks that both routes,
over REST and through the Java client, agree when every matching element
is visible, and that omitting the parameter changes nothing. It
deliberately does not attempt the case where they differ — that needs an
element the calling user cannot read, which that suite cannot arrange.
Which is why the verification above, against real data, is the part that
actually proves the fix.

**Status:** re-confirmed 2026-08-18, byte-for-byte identical to the
2026-08-15 numbers below — `count_relationships_between_elements("Exception")`
still returns 58, `get_relationships("Exception")` still returns 57, same
off-by-one. No change.

**Status:** re-investigated 2026-08-15, narrowed and re-confirmed
**Egeria server, not pyegeria-fixable** — this is a genuine, real bug, just
smaller than originally measured (demo data has evidently changed since
2026-07-24: `count` is now 58 and `get_relationships` is now 57, not
276/55). Cross-checked against a **second, independent pyegeria list-based
method** — `MetadataExpert.find_relationships_between_elements` (a
different OMVS client, different endpoint,
`.../relationships/by-search-conditions` rather than
`ClassificationExplorer`'s `.../relationships/{type}`) — with the same
`relationshipTypeName: "Exception"` filter: it also returns exactly 57,
and its 57 relationship GUIDs are the **identical set** to
`get_relationships`'s 57 (zero difference either direction). Two
independently-implemented pyegeria code paths through two different
endpoints agree exactly with each other; only the server's native
`COUNT(*)` endpoint (`.../relationships/by-search-conditions/count`)
disagrees, by exactly 1. Also re-confirmed the original "not the type
filter" finding still holds with current data — re-ran `count` vs.
`get_relationships` for `SemanticAssignment` (401=401), `License` (2=2),
`Certification` (0=0), `AttachedRating` (0=0): all match; only `Exception`
diverges. Also checked whether the count includes non-`ACTIVE`/soft-deleted
relationships the list endpoints filter out — no: `limitResultsByStatus:
["ACTIVE"]` and `["ACTIVE","DELETED"]` both still return 58 from `count`
(no status-filter difference). Since both retrieval paths agree with each
other and only the count differs, there's genuinely nothing to fix on the
pyegeria side — this is squarely a server-side discrepancy between the
native COUNT(*) query and the list-materialization logic for this one
relationship type. No further pyegeria action needed; still needs
Egeria-side investigation to say what specifically triggers it for
`Exception`.

**Original status:** open (Egeria server) — needs Egeria-side investigation. Found
2026-07-24 while wiring the Egeria Overview dashboard to native counting
(odpi/egeria#9168). Consolidated in from `egeria-workspaces-fs/
PYEGERIA_ISSUES.md` 2026-08-05.

**Summary:** the OMF metadata-expert native relationship count and the
classification-explorer `get_relationships` return materially different
totals for the `Exception` relationship type — and *only* that type, among
those tested.

**How to trigger:**
```python
from pyegeria import MetadataExpert, ClassificationExplorer
me = MetadataExpert(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret"); me.create_egeria_bearer_token()
ce = ClassificationExplorer(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret"); ce.create_egeria_bearer_token()

me.count_relationships_between_elements({"class":"FindRelationshipRequestBody","relationshipTypeName":"Exception"})
# -> 276
len(ce.get_relationships(relationship_type="Exception", output_format="JSON", start_from=0, page_size=5000))
# -> 55  (all 55 have exact typeName "Exception"; no effectivity dates)
```

**What it is NOT:**
- Not the type filter — `count("SemanticAssignment")` = 397 =
  `get_relationships` = 397; `License` 2 = 2; `Certification` 0 = 0;
  `AttachedRating` 0 = 0. Every other tested type matches; only `Exception`
  diverges.
- Not status/effectivity — `count("Exception")` is 276 with
  `limitResultsByStatus=[ACTIVE]`, with `effectiveTime=<now>`, and with
  neither; the 55 `get_relationships` results carry no
  `effectiveFromTime`/`effectiveToTime`.
- `count(no relationshipTypeName)` = 31857 (all relationships), so 276 is
  a genuine type-scoped subset, not "count ignores the filter".

**Open question for Egeria:** what does the metadata-expert count include
for `Exception` that the classification-explorer traversal excludes
(subtypes counted under the supertype? relationships to non-visible/
anchored/dangling ends? access/zone filtering that differs between the two
OMVS)? Whichever is "true", the two APIs should agree for a given type —
or the difference should be documented.

**Impact / workaround:** egeria-workspaces-fs's Overview dashboard keeps
**relationship** counts on `ClassificationExplorer.get_relationships` (so
"Open Exceptions" stays consistent with the Audit app at 55) and uses
native counting only for **element** counts.

---

### ISSUE-79: native survey against a template-created `FileFolder` asset fails server-side — `assetConnector` is null in `BasicFolderConnector.getFile()`

**Update 2026-08-30, from the Egeria team (Mandy Chessell).** The entry
stays in "Open Egeria Server issues" — the reported failure is not
explained and not fixed. What has changed is that the cause recorded in
this entry, and in Resource Explorer's `re-as-engine-host-plan.md`, is now
known to be wrong, and the error it produces has been made legible.

**Status: still open (Egeria Server)** — but the recorded cause is
disproved, and this entry and `re-as-engine-host-plan.md` should both be
corrected. Investigated 2026-08-30 from the Egeria side, including a new
FVT suite built to run this exact scenario.

**The premise is false.** This entry, and the design doc's hold, rest on
"template-based asset creation never wires up a working Connection." That
is not true, in either environment it was checked against:

- **On the quickstart that produced the report.** Every element created
  from a template that itself carries a `ResourceConnection` got one — 10
  of 10. Every `FileFolder` in that repository has one, including all
  three that were created from a template (`/deployments/content-packs`,
  `/deployments/loading-bay/sample-data`, `/deployments/secrets`).
- **In a clean environment built from the current archives.** A folder
  catalogued through `FileGovernance::create-file-folder` came back with a
  `ResourceConnection` attached.
- **The `FilesContentPack` template itself is also well formed:**
  `FileFolder` template `fbdd8efd-...` carries an `Anchors`-classified
  `Connection` with both a `ConnectToEndpoint` and a
  `ConnectionConnectorType`.

**The folder survey works.** A new `files-fvt` suite runs the reported
scenario end to end — catalogue a folder from the `FileFolder` template,
then survey it natively — and it passes:
```
OMES-SURVEY-ACTION-0019 The survey action service folder-survey-service has completed the
analysis of asset 7050dc50-... with request type survey-folder in 1927 milliseconds; the
results are stored in survey report 7e7892e2-...
```
The report carried six annotations. The test asserts the survey
*completed*, not merely that it ran: a survey that dies on a null
connector still produces an engine action, and the waiter throws on any
terminal status other than `COMPLETED`.

**A second hypothesis was also eliminated.** While investigating, a real
defect was found in the PostgreSQL repository: a `TypeDefPatch` that
reparents a type does not update the denormalised supertype chain stored
on existing rows, so instances written before the patch become invisible
to searches for the new supertype. That would have hidden connections
exactly as reported, since `AssetConnection` was reparented under
`ResourceConnection` on 2026-08-27. It is fixed — but it was never the
cause here: the quickstart repository stores 202 rows as
`:ResourceConnection:LabeledRelationship:` and none as
`:AssetConnection:`, because it was reloaded after the type change.

**What has been fixed, and what it does and does not buy.** The NPE
itself is now a clean error. `getConnectorForAsset()` returns `null` by
contract when an asset has no connection; `FolderSurveyService` cast that
null and dereferenced it, and the framework's own
`performCheckAssetAnalysisStep()` had the same hole on its error path.
Both now report `OPEN-SURVEY-400-008` / `OPEN-SURVEY-0009`
(`NO_ASSET_CONNECTOR`), naming the asset.

This does not make such a survey succeed — an asset with no connection
describes a resource nothing can open. It makes the failure say *which*
asset, which is what the original report was missing: the NPE named
`BasicFolderConnector`, a class the caller had never heard of, and pointed
away from the asset.

**Why that matters for how this entry reads.** Four further defects were
found in the same connectors, all on paths nothing else exercises: both
file survey services failed on every invocation (annotations created
without a qualified name, in three places), the CSV survey dereferenced a
null root schema type, wrote a relationship property to an entity, and
produced colliding annotation qualified names. The file survey path had,
on this evidence, never run to completion. Someone hitting an NPE in this
family had every reason to suspect the asset — the errors never named
anything else. That is context for the original diagnosis, not a
criticism of it.

**The naming trap, which is directly actionable on the pyegeria side.**
This entry already records that `initiate_file_folder_survey`'s default
(`FileSurveys:survey-folder`) and the `.http` example
(`AssetSurvey:survey-folder`) are both wrong. Confirmed and now
understood: a governance action type is registered under
`<governanceEngineName>::<requestType>` — two colons — so the real name is
`FileSurvey::survey-folder`. `AssetSurvey` is not an engine that exists at
all. The `.http` examples have been corrected upstream
(`FileSurvey::survey-folder`, `ApacheKafkaSurvey::survey-kafka-server`,
`PostgreSQLSurvey::survey-postgres-server`,
`PostgreSQLSurvey::survey-postgres-database`) with a note stating the
shape, because the error a wrong name produces —
`OMAG-GENERIC-HANDLERS-400-013`, "the name is not recognized" — does not
say what it wanted instead. `initiate_file_folder_survey`'s default still
needs fixing in pyegeria.

**What is left, and what would settle it.** The remaining candidate is
the deployment rather than the cataloguing or the survey: which server
and userId the engine host's connected-asset client resolves
`SurveyAssetStore.getConnectorToAsset()` against. That cannot be tested
from the Egeria side — it needs the engine host that produced the
failure. Suggested, in order:

1. Re-run the original repro against a build carrying the NPE fix. If the
   asset genuinely has no connection the run now fails with
   `OPEN-SURVEY-400-008` naming it, which turns the question from "why is
   this connector null" into "why does this asset have no connection that
   this userId can see". If instead the survey completes, the deployment
   has moved on and this entry can be closed.
2. Check the folder asset at the moment of failure for a
   `ResourceConnection`, using the same userId the engine host runs as —
   not an admin one. If the relationship is there but the survey cannot
   see it, that is a visibility or server-routing problem, and the userId
   is where to look next.
3. Compare against `files-fvt`, which is a known-good baseline for this
   exact scenario. Pointing the same two actions at a
   differently-configured engine host isolates the variable.

Also worth correcting: this entry's earlier note about leftover probe
elements (`FileFolder::localhost:/tmp/re-e1-probe-*`,
`FileFolder::localhost:/tmp/re-issue79-recheck-*`) is out of date — the
quickstart repository has been reloaded since and holds none of them, so
that evidence is gone.

**Status:** open (Egeria Server), reproduced live 2026-08-27, **re-checked
2026-08-28 — still reproduces, identical failure.** Same class/method
(`BasicFolderConnector.getFile()`, `assetConnector` null), same error IDs
(`OMES-SURVEY-ACTION-0018`/`OPEN-SURVEY-500-001`), same
`java.lang.NullPointerException`, against a freshly created `FileFolder`
and a fresh survey run — not a one-off. Filed by content, not by number —
see "why this entry exists" below.

**Layer:** Egeria Server (survey action framework / `BasicFolderConnector`),
not pyegeria. `create_folder_element_from_template` and the survey-initiate
call both succeed and are correctly formed; the failure happens entirely
inside the server's survey action service.

**Why this entry exists.** Resource Explorer's `re-as-engine-host-plan.md`
is ON HOLD citing this exact symptom ("connector is null" on a native
survey against a template-created asset) under the name `PYEGERIA_ISSUES.md`
**ISSUE-51** — but this file was renumbered on 2026-08-15, and today's
ISSUE-51 is an unrelated, already-fixed `fetch_element()` shape problem.
The blocker's own content had no surviving entry anywhere in this file.
Investigated fresh rather than guessed at, per the plan's own citation
being untrustworthy.

**Two candidate bugs were in play, and they are not the same bug:**

1. **Resource Explorer's superseded tracker, entry E1** (`packages/
   resource-explorer/docs/egeria-pyegeria-issues.md`) describes a *different*
   symptom: a 500 from the PostgreSQL repository connector on
   `createMetadataElementFromTemplate` (`metadata_collection_guid` null
   while saving a classification) — a failure to *create* the element at
   all. **Re-tested live 2026-08-27 and does not reproduce**:
   `create_folder_element_from_template(path_name=..., folder_name=...,
   file_system="localhost")` against `qs-view-server` returned a real GUID
   with no error. Whatever this was, it looks fixed.
2. **The design doc's actual blocker** — a template-created asset surveyed
   natively fails with a null connector — **does still reproduce**, and is
   what this entry tracks.

**Reproduction** (against `qs-view-server`, no pyegeria bug involved):
```python
from pyegeria import AutomatedCuration
c = AutomatedCuration("qs-view-server", "https://localhost:9443", "erinoverview", "secret")
c.create_egeria_bearer_token()

folder_guid = c.create_folder_element_from_template(
    path_name="/tmp/some-new-path", folder_name="probe-folder", file_system="localhost")

# Note: initiate_file_folder_survey's own default survey_name
# ("FileSurveys:survey-folder") and the .http ground truth's example
# ("AssetSurvey:survey-folder") are BOTH wrong on this server -- neither
# GovernanceActionType is registered (OMAG-GENERIC-HANDLERS-400-013). The
# real registered qualifiedName, confirmed via
# `EgeriaTech.get_elements("GovernanceActionType")`, is "FileSurvey::survey-folder".
action_guid = c.initiate_file_folder_survey(folder_guid, survey_name="FileSurvey::survey-folder")
```

Poll the resulting `EngineAction` (`EgeriaTech.get_elements("EngineAction")`,
match on `elementHeader.guid`) — it completes (fast, ~1s) with
`activityStatus: "FAILED"` and `completionGuards: ["survey-failed"]`. Full
`completionMessage`:
```
OMES-SURVEY-ACTION-0018 The survey action service folder-survey-service
threw a org.odpi.openmetadata.frameworks.connectors.ffdc.ConnectorCheckedException
exception during the generation of survey report ... for asset
<folder-guid> during request type survey-folder in survey action engine
FileSurvey (guid=4168abb9-6c60-46fb-b9c0-b44180d19500). The error message
was OPEN-SURVEY-500-001 Unexpected exception in survey action service
folder-survey-service of type java.lang.NullPointerException detected by
method start. The error message was Cannot invoke
"org.odpi.openmetadata.adapters.connectors.datastore.basicfile.BasicFolderConnector.getFile()"
because "assetConnector" is null
```

**Analysis.** `create_folder_element_from_template` creates the `FileFolder`
element and it looks entirely normal (confirmed via `get_elements`: proper
`pathName`, `resourceName`, `Anchors` classification) — but no working
`Connection`/`Connector` got wired to it, so when `folder-survey-service`
tries to open the asset via `BasicFolderConnector.getFile()`, the
connector reference is null and the survey action service crashes with an
NPE rather than a clean error. This matches the design doc's
characterization exactly ("template-based asset creation never wires up a
working Connection, so any native survey against a template-created asset
fails server-side with a NullPointerException") — just with the precise
class/method now on record, which the design doc didn't have.

**Impact:** blocks Resource Explorer's engine-host participation design
(`re-as-engine-host-plan.md`, cases 1/2/4 — anything needing a native
survey to actually *complete*, not just be triggered; case 3, RE-local
surveying, is unaffected). The hold should be re-evaluated against this
entry specifically, not against the old ISSUE-51 number. As of 2026-08-28
this is confirmed the *only* thing still blocking that work on the
pyegeria side — ISSUE-78's engine-host method trio shipped in 6.1.5 and RE
has upgraded and verified it end to end, and the two other gaps
identified alongside it (no REST way to create a `GovernanceEngine`/
`GovernanceService` element; no per-engine "claimable work" listing,
`get_active_engine_actions()` filtered client-side is the only option) are
both genuine server-side gaps, not pyegeria ones. This entry is the real
holdup.

**Leftover from this investigation:** probe `FileFolder` elements
(`qualifiedName: "FileFolder::localhost:/tmp/re-e1-probe-*"` from
2026-08-27, `"FileFolder::localhost:/tmp/re-issue79-recheck-*"` from the
2026-08-28 re-check) on `qs-metadata-store`, plus their failed
`SurveyReport`/`EngineAction` pairs, left in place as reproduction
evidence for both dates — not yet deleted.

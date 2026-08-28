# Open Egeria Server Issues

This is a standalone extract of every **currently open, Egeria-Server-side**
issue from [`PYEGERIA_ISSUES.md`](PYEGERIA_ISSUES.md) — nothing here can be
resolved by editing this repo; each needs a server-side fix, an upstream bug
report, or a deployment/config change. It exists to hand to whoever owns the
Egeria server side of a question without making them wade through
`PYEGERIA_ISSUES.md`'s pyegeria-side entries and closed/resolved appendix.

**`PYEGERIA_ISSUES.md` remains the source of record.** This file is a
generated-by-hand extract of its "Open Egeria Server issues" section as of
2026-08-28 — re-derive it from that section (don't edit the two
independently) whenever an entry here changes status, gets fixed upstream,
or a new server-side issue is filed.

---

These need an Egeria Server-side fix, an upstream bug report, or a
deployment/config change — nothing here can be resolved by editing this
repo. Where an entry has a known pyegeria/Dr.Egeria follow-on once the
Egeria side lands, it's noted inline (also cross-referenced from
`PYEGERIA_ISSUES.md`'s "Open pyegeria items" section where the follow-on
is substantial enough to track there too).

---

### ISSUE-52: `qs-nanny-daemon`/`qs-integration-daemon`'s own connectors generate sustained, heavy background write load against the shared repository — starves interactive requests, plausible cause of "frequent Postgres checkpoints"

**Update 2026-08-16, more specific root-cause evidence.** Recurred while
retrying the `dr-egeria` help-Glossary `--process` step (see ISSUE-52's own
earlier "cold-start crawl" postscript — this shows the earlier optimism was
premature, it recurs under real batch load, not just right after a
restart): `docker stats` showed `egeria-shared-postgres` at up to **650%
CPU**, and connecting directly (`docker exec ... psql -U postgres -p 5442
-d egeria`) found the real mechanism — **38 connections stuck `idle in
transaction`** against the `egeria` database, all holding open the same
query shape (`select distinct * from entity where (version_end_time is
null) and (exists (select 1 from en...`). This is a connection/transaction
pileup, not simple CPU starvation as originally framed — many connections
opened a transaction, are waiting on something (`wait_event_type: Client`/
`ClientRead`, i.e. waiting on their own client, not blocked by Postgres
itself), and never committed/closed, so newer requests (including a plain
`get_glossaries_by_name` lookup) queue behind them. CPU eased from 650% →
340% → 298% over ~15 minutes while sitting at this same connection count,
without by-name-search latency improving at all (stayed pinned at
25-30s/timeout) — the two aren't tightly coupled, reinforcing that this is
a connection-holding problem, not a raw compute-load problem. Whatever is
opening these `entity`-table transactions and not releasing them (almost
certainly the same `qs-nanny-daemon`/`qs-integration-daemon` connectors
already suspected) is the actual thing to fix, not just "connector load"
in the abstract.

**Original status:** open (Egeria server / deployment config), found 2026-08-15 (Dan)
investigating why a `dr_egeria --validate`/`--process` run against the
`dr-egeria` help file (100+ commands) was taking 70+ minutes and timing out
individual calls (see ISSUE-51), and independently reported by the user as
"frequent checkpoints" observed in the Postgres console.

**Layer:** Egeria Server (`egeria-quickstart` deployment's integration
daemon connector configuration), not pyegeria — this is a deployment/config
issue in the `egeria-shared-postgres`-backed local quickstart stack, not a
pyegeria code defect.

**What:** confirmed live, same session:
- `egeria-shared-postgres` (the `pgvector/pgvector:pg17` container backing
  `qs-view-server`'s repository, port 5442) is issuing time-based
  checkpoints every 5 minutes (the Postgres default `checkpoint_timeout`)
  with real, non-trivial WAL volume behind each one (~10-22 MB/checkpoint,
  i.e. roughly 35-75 KB/s of sustained write throughput) continuously,
  including in windows where no interactive Dr.Egeria/pyegeria work was
  running — meaning the load is coming from something else running inside
  the platform itself, not from client-side testing.
- `docker logs quickstart-egeria-main` shows the source: `qs-nanny-daemon`'s
  `JacquardDigitalProductLoom` integration connector logged a single
  refresh cycle that took **4,370,395 ms (~73 minutes)** to complete
  (`INTEGRATION-DAEMON-SERVICES-0043`). `qs-integration-daemon`'s
  `OpenAPICataloguer` connector is continuously creating new `APIOperation`
  catalog entities — confirmed 703 total in the container's full log
  history, 36 of them in the last 30 minutes of a single ~2 hour window
  sampled — each one a real metadata write, evidently crawling/re-crawling
  the platform's own REST API surface (dozens of
  `/open-metadata/access-services/open-metadata-store/...` and
  `/open-metadata/conformance-suite/...` paths) rather than converging to a
  steady state.
- Directly reproduced the contention: a single, otherwise-simple
  `client._async_get_element_by_guid_(guid)` call against `qs-view-server`,
  issued from a fresh script with nothing else running client-side, hit the
  30-second client timeout and raised `PyegeriaTimeoutException` —
  confirming the server itself, not the client or network, is the
  bottleneck.

**Impact:** any pyegeria/Dr.Egeria workload that does more than a handful
of sequential server calls (bulk `--process` runs, the help-file Glossary
sync in particular) becomes unreliable — individual calls time out
(`TIMEOUT_ERROR_408`) or the whole run takes an order of magnitude longer
than expected — while these background connectors are active. This is very
likely the direct cause of ISSUE-51's crash (the ClassificationExplorer
call it depends on timed out under this exact load) and of the multi-hour
`dr_egeria --validate` run in this same session.

**Update 2026-08-15, same day:** user restarted the Egeria environment with
the latest configuration. Post-restart, a `dr_egeria --process` run against
the same 100+-command help file completed its first ~4 minutes with 0
errors (vs. timing out repeatedly before), and `OpenAPICataloguer` created
0 new `APIOperation` entities in a 10-minute post-restart sample (vs. 36 in
30 minutes before) — consistent with the crawl having converged/settled
after the restart rather than continuously re-cataloguing. Not yet
confirmed whether this is a durable fix or the connectors will resume the
same pattern once they hit their next scheduled refresh; worth re-checking
`docker logs quickstart-egeria-main | grep JacquardDigitalProductLoom` after
it's been up for a few hours.

**Candidate next step (not yet done):** narrow which specific connector(s)
are the dominant contributor — `JacquardDigitalProductLoom`'s single
73-minute cycle and `OpenAPICataloguer`'s continuous entity creation are
the two strongest leads — and either increase their refresh interval,
narrow `OpenAPICataloguer`'s crawl scope (it may be re-cataloguing
`localhost:9443`'s own REST surface on every refresh instead of once), or
disable/reconfigure them in the `egeria-quickstart` compose config if
they're not needed for this deployment's actual use case. This needs
Egeria-server-side (or deployment-config-side) investigation — nothing here
is fixable from pyegeria's side.

**Update 2026-08-15, done (partial):** `quickstart-egeria-main` had been
restarted again since the note above (container uptime ~1h at check time,
vs. the earlier 8h+ uptime of sibling containers) — so this was actually a
fresh post-restart observation window, not a stale one. Findings:
- **`OpenAPICataloguer`'s behavior is better characterized as a one-time
  cold-start catalog crawl that converges, not continuous unbounded
  re-crawling** — the earlier framing was too pessimistic. Creation rate
  measured in shrinking trailing windows since restart: 134 (50 min) → 86
  (40 min) → 48 (30 min) → 26 (20 min) → 8 (10 min) → 6 (5 min) new
  `APIOperation` entities — a clear deceleration, not a steady/repeating
  rate. 201 total `APIOperation`s exist in the full container log history;
  171 of them were created in just this last hour, meaning the connector
  is doing its first post-restart crawl right now and tapering off, not
  perpetually re-cataloguing the same ground.
- **`JacquardDigitalProductLoom` logged zero refresh-cycle activity in this
  1-hour post-restart window** — can't yet say whether its 73-minute cycle
  is gone for good or just hasn't fired again yet (container too young to
  rule out a recurrence on its next scheduled interval).
- **Server responsiveness confirmed fast right now**: 3 sequential
  `get_metadata_element_by_guid` calls against `qs-view-server` completed
  in 0.19s/0.03s/0.02s — no timeouts, nothing close to the earlier
  30-second `PyegeriaTimeoutException` symptom.
- Could not directly inspect Postgres checkpoint stats this pass (`psql`
  isn't installed as a client tool inside the `egeria-shared-postgres`
  container in a way this session could reach it) — server-response timing
  above stands in as an indirect but consistent signal instead.

**Net assessment:** the acute symptom (timeouts, multi-hour bulk-processing
runs) is not currently reproducing, and the mechanism now looks more like
"cold-start crawl briefly saturates the server after every restart, then
settles" than "sustained, unbounded background load." Still genuinely
Egeria-server/deployment-config territory, not pyegeria-fixable — if this
pattern recurs and is disruptive on every restart, the original candidate
fixes (narrow `OpenAPICataloguer`'s crawl scope, stagger connector startup,
or increase refresh intervals) remain the right next step, just lower
urgency than originally assessed.

---

### ISSUE-54: `findMetadataElements` scoped to `Referenceable` silently returns an incomplete, arbitrary subset instead of the true population

**Update 2026-08-26: re-confirmed again, unchanged.** Re-ran the exhaustive
`Referenceable` scan (unsequenced, `pageSize=500`, advancing unconditionally,
stopping only on an empty page — the correct pagination contract per the
note below) against the current server build (`6.2-SNAPSHOT`, platform
timestamp `2026-08-24T18:27:04Z` — the same redeploy that turned out to
have fixed ISSUE-69, checked in the same pass on the chance this one had
also moved). It hadn't: 9,344 raw elements fetched across 19 pages, only
**6,789 distinct GUIDs** (2,555 duplicates) against a native
`count_metadata_elements` population of **9,636** — ~70% coverage, in the
same range as every prior check (54-73% across past re-checks). Cross-check
against a direct exhaustive `GlossaryTerm` scan (262 real, distinct GUIDs):
only **80 (31%)** of them appear anywhere in the broad `Referenceable`
scan, **183 missing**. Same shape as originally documented — this is a
live, unresolved Egeria server bug, not something that rides along with
whatever fixed ISSUE-69.

**Status:** still open (Egeria server) — **NOT fixed, re-confirmed
2026-08-18, and this pass corrects a misdiagnosis made earlier the same
day.** First re-check (prompted by dwolfson asking to double-check after
ISSUE-53/57/60) found `pageSize=500`/`startFrom=0` on a `Referenceable`
scan returning only 494 elements, and mistook that short page for the bug
itself (reasoning: "a naive `len(page) < page_size` pagination loop halts
here"). **dwolfson caught this and pointed at Egeria's own paging docs**
(https://egeria-project.org/guides/developer/finding-metadata/overview/#paging),
which explicitly document that a short-but-nonempty page does **not** mean
"last page" — server-side filtering can legitimately shorten an individual
page without ending the result set, and the only correct termination
signal is a genuinely **empty** page. `len(page) < page_size` is a
documented anti-pattern, not evidence of an Egeria bug — re-running the
scan correctly (always advance `startFrom` by the full `pageSize`,
regardless of how many came back, stop only on `not page`) confirms this:
`startFrom=500` (not `startFrom=494`) picks up cleanly with no gap.

**The real remaining defect, once paginated correctly:** exhaustively
scanning `Referenceable` with the *correct* stop condition (23 pages,
`pageSize=500`, advancing by 500 unconditionally) fetched **10,548**
elements total against a true native-count population of **11,019** — but
those 10,548 contained **1,394 duplicate GUIDs**, leaving only **9,154
distinct** elements, still **~17% short** of the true 11,019. `GlossaryTerm`
coverage in this corrected scan: **243/357 (68%)** — much better than the
27% the flawed short-page-as-stop-signal method found, but still
genuinely incomplete. So the original 2026-08-06 hypothesis (unstable
server-side result ordering across pages causing both duplication *and*
omission) remains the best-supported explanation — this is a real,
still-open Egeria server pagination-stability bug for this specific
broad-type query, just not the mechanism this session initially
misdiagnosed. Nothing fixable client-side.

**Checked dwolfson's hypothesis that the duplicates might just be multiple
versions of the same object (not a true dupe)** — ruled out definitively.
Re-ran the corrected exhaustive scan and compared `versions.version`/
`versions.updateTime` across every occurrence of every duplicated GUID
(1,112 duplicated GUIDs found this run — close to, not identical to, the
1,394 above; population drifts slightly between runs since this is a live
shared server). **Every single occurrence of every duplicate has the
identical version number and `updateTime`** — 0 of 1,112 duplicated GUIDs
showed two different versions of the same element; all 1,112 were the
exact same version appearing 2-3 times (`{2: 1092, 3: 20}` occurrence-count
distribution). So this is not "the repository returned two historical
versions of one element and we're not deduplicating" — it's the literal
same element-state appearing more than once in the raw paginated response,
which is consistent only with unstable result ordering shifting an
element's position between page fetches (the same mechanism suspected
since the original 2026-08-06 finding), not a versioning artifact.
Duplicated types skew heavily toward `ValidMetadataValue` (659 of 1,112)
and `SpecificationPropertyValue` (300) — both likely large, frequently-
reordered collections, consistent with an ordering-instability theory.

**Follow-up, same day** — dwolfson asked the natural next question: how can
a duplicate GUID even happen if the repository enforces uniqueness? Ruled
out every "this is actually fine" explanation with direct evidence rather
than just asserting server-side instability:
- **Not a live-mutating dataset causing drift mid-scan.** Native
  `count_metadata_elements` for `Referenceable` stayed exactly stable
  (11,079 → 11,079) across a full 7.4-second, 23-page scan. Page 1
  (`startFrom=0`) came back byte-for-byte identical before and after the
  entire scan. Two immediate back-to-back identical requests also returned
  the exact same elements in the exact same order — no evidence of
  anything being written to this dataset during or around the scan.
- **Not a simple page-boundary tie-break either** — checked how far apart
  (in page-index terms) each duplicated GUID's two occurrences were: only
  245/1,619 (15%) were adjacent pages; 1,374 (85%) spanned 2+ pages apart,
  with a max observed gap of **10 pages** (~5,000 elements apart). An
  element legitimately can't shift ~5,000 positions between two `startFrom`
  calls unless the server's ordering for this query isn't a true
  deterministic total order at all.
- **Best-supported mechanism:** `findMetadataElements` on a broad
  `Referenceable` scan most likely sorts by something like creation time
  with no unique tiebreaker (e.g. GUID) appended to the effective
  `ORDER BY`. `ValidMetadataValue`/`SpecificationPropertyValue` (the two
  most-duplicated types, 659 + 300 of 1,112) are both bulk-loaded from an
  archive, so plausibly thousands of rows share the *exact same* creation
  timestamp. Each `startFrom`/`pageSize` call is a fresh query execution,
  not a stable server-side cursor — when many rows tie on the sort key, the
  database is free to resolve that tie differently on separate query
  executions, so the identical single row can legitimately land in very
  different offset windows across two calls. This is the well-known
  `OFFSET`/`LIMIT`-without-a-fully-unique-`ORDER BY` SQL pagination
  anti-pattern, surfacing here in Egeria's repository query — not a
  pyegeria bug, not a real repository-level duplicate GUID.

**Theory tested directly, same day** — dwolfson's suggestion: force a
deterministic sort by a genuinely unique property and see whether
duplicates disappear. They did, confirming the theory outright, and the
test surfaced a second, related defect in the process:

| Sort | Duplicates | Completeness (distinct / true count) |
|---|---|---|
| None (baseline, this run) | 853 | 9,752 / 10,605 (92%) |
| `sequencingProperty=GUID` | **1** (plausibly one live edit mid-scan, not a leftover tie) | not measured — session blocked mid-check by an unrelated concurrent edit breaking `pyegeria` imports (`pyegeria/omvs/feedback_manager.py`, not touched by this investigation) |
| `sequencingProperty=qualifiedName` | **0** | 10,597 / 11,081 (95.6%) — still short |

Sorting by `qualifiedName` fully eliminates duplication (confirms the
theory) but the resulting scan is still incomplete — and *not* randomly:
every element of the omission is concentrated in exactly two types,
`ValidMetadataValue` (211 missing of 2,296) and `PersonRole` (63 missing of
334), while every other type in the scan matched its native count exactly
(`SpecificationPropertyValue`, `GovernanceActionProcessStep`,
`GovernanceActionProcess`, `GlossaryTerm`, `NotificationType`,
`SolutionComponent` all diff=0). Root cause of the omission: **every
single element of both `ValidMetadataValue` and `PersonRole` has
`qualifiedName = None`** — confirmed directly (2,296/2,296 and 323/323
have a null `qualifiedName`, not just "some"). Sorting by `qualifiedName`
ties every element of these two types together into one giant unresolved
group at the null position — the *same* missing-tiebreaker defect as the
duplication case, just manifesting as omission instead of duplication when
the caller's own chosen `sequencingProperty` happens to be null for an
entire type. This means `GUID` is the objectively safer workaround for
anyone needing a reliable exhaustive scan today — it's the one property
guaranteed non-null and unique for every element regardless of type, so it
shouldn't hit either failure mode (consistent with its near-zero-duplicate
result above; completeness under `GUID` sequencing not yet confirmed, see
blocker note in the table).

**Also found as a byproduct of this correction:** pyegeria's own
`pyegeria/view/base_report_formats.py` (`load_egeria_report_specs()`) had
exactly the `len(page) < page_size` anti-pattern in a real fetch-all loop
(`find_collections` for `ReportType` collections) — fixed 2026-08-18 to
advance unconditionally and stop only on an empty page, per the now-clear
Egeria paging contract. Worth grepping the rest of this codebase (and any
sibling repo — `egeria-workspaces-fs`, `egeria-advisor`/`trellis`) for the
same pattern (`len(page) <` / `< page_size` / `< _page_size`); not
exhaustively audited beyond this one hit in this pass.

**Status:** still open (Egeria server), re-confirmed 2026-08-15 against the
current, restarted `qs-view-server` — magnitude has shifted (as with
ISSUE-38/52's re-checks) but the core defect persists. Re-ran the same two
independent cross-checks with a fully-paginated exhaustive scan
(`page_size=200`, following pagination to exhaustion):
- Direct exhaustive `metadataElementTypeName="GlossaryTerm"`: **532**
  elements. Of the exhaustive `Referenceable` scan's 19,166 elements
  (19,127 distinct GUIDs — see below), only **324** carry `typeName:
  "GlossaryTerm"` — **61%** coverage (better than the original run's ~54%,
  still clearly incomplete, not just a rounding gap).
- Independent check against `SemanticAssignment` relationship participants
  (`ClassificationExplorer.get_relationships`, unrelated API path): 414
  distinct participant GUIDs; only **302 (73%)** appear anywhere in the
  19,166-element `Referenceable` scan (up from the original run's 23/410 =
  5.6%, but still missing more than a quarter of real, independently-known
  participants).
- **New observation this pass:** the exhaustive `Referenceable` scan itself
  returned 19,166 total elements across pages but only 19,127 **distinct**
  GUIDs — 39 duplicate entries showing up more than once across different
  pages of the same paginated scan. Not previously noted; suggests server-side
  result ordering/stability issues for this specific broad-type scan, which
  would also explain why elements can be silently skipped between pages
  (an element shifting position between page fetches, due to unstable
  ordering, could cause both duplication *and* omission depending on which
  way it moves) — a plausible mechanism for the core bug, not confirmed as
  the actual root cause.

Both cross-checks still clearly demonstrate the defect; nothing changed
client-side to warrant re-testing pyegeria's own pagination logic (already
ruled out in the original investigation — direct exhaustive scans of real
types are complete and correct, only the broad-base-type scan is affected).

**Original status:** open (Egeria server), found 2026-08-06 fixing egeria-workspaces-fs's
relationship-only search (see ISSUE-45's same investigation thread —
looking for a safe fallback type once `metadataElementTypeName="Asset"`
was confirmed wrong for `SemanticAssignment`, and `metadataElementSubtypeNames`
confirmed non-functional).

**Layer:** Egeria Server — not fixable in pyegeria.

**What:** an exhaustive, fully-paginated `find_metadata_elements` scoped to
`metadataElementTypeName="Referenceable"` (**not** the true type-hierarchy
root — that's `OpenMetadataRoot`, confirmed live via `get_all_entity_defs`;
`Referenceable` is one of five direct subtypes of `OpenMetadataRoot`
alongside `SearchKeyword`/`Rating`/`Like`/`TranslationDetail`, but it's the
practical common ancestor of essentially every entity type an
application-level search actually cares about, which is why it's the type
most callers reach for as a "find everything" scope) returns a small,
arbitrary subset instead of the true population, with no error, no truncation flag,
and pagination genuinely terminating normally (`added == 0`/`len(page) <
page_size` on the last page — the loop believes it's done). Confirmed live
against `qs-view-server` by direct comparison:

| Scope | Elements found |
|---|---|
| `metadataElementTypeName="Referenceable"` (exhaustive) | 3,999 total |
| ...of which `typeName="GlossaryTerm"` | 241 |
| ...of which `typeName="GovernanceActionProcess"` | 22 |
| `metadataElementTypeName="GlossaryTerm"` (exhaustive, direct) | **450** |
| `metadataElementTypeName="GovernanceActionProcess"` (exhaustive, direct) | **378** |

Cross-checked against a real, independently-known population: fetching
every participant GUID of the `SemanticAssignment` relationship type
(`ClassificationExplorer.get_relationships`, a separate, unrelated API
path, previously verified complete) gives 410 distinct GUIDs. Only 23 of
those 410 appear anywhere in the 3,999-element `Referenceable` scan — 387
real participants (94%) are simply absent from a scan of the type that is
supposed to be their common ancestor and therefore cover all of them.

**Impact:** `metadataElementTypeName="Referenceable"` cannot be used as a
"safe, unscoped, find-everything" fallback the way its practical role as
the common ancestor of nearly every real entity type implies — a caller
that scopes a search this broadly on purpose (not just as an accidental fallback) will silently miss
the majority of real results, not just cap them at a boundary. Confirmed
this is specific to the base-type-wide scan, not pagination itself —
directly-typed exhaustive searches for the exact same real types
(`GlossaryTerm`, `GovernanceActionProcess`) are complete and correct.

**Candidate fix:** none client-side. `egeria-workspaces-fs`'s workaround
(see its `EGERIA_INSIGHTS_QUERY_MODEL.md`/`insights_handler.py`, commit
`015916d0`) is to never scope a search to `Referenceable` (or any other
broad base type) as a "safe fallback" — when the real target type isn't
known, derive the actual candidate types from other data (e.g. a
relationship's real participants) and search each directly instead.

---

### ISSUE-38 (PY-18): `count_relationships_between_elements("Exception")` (276) disagrees with `ClassificationExplorer.get_relationships("Exception")` (55)

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

### ISSUE-41 (PY-21): `find_glossary_terms(sequencing_order=..., include_only_classified_elements=...)` returns ZERO results when combined — each filter alone works fine

**Update 2026-08-27: regression — `include_only_classified_elements` alone
now also returns ZERO, no `sequencing_order` involved at all.** Found
debugging Egeria Explorer's Questions tab showing no questions on the
left (`egeria-workspaces-fs`'s `perspectives_handler.py`'s `get_questions()`,
which had already dropped `sequencing_order` per this issue's earlier
guidance). Reproduced directly against `qs-view-server`:
`find_glossary_terms(search_string="*", starts_with=True, graph_query_depth=0,
include_only_classified_elements=["Question"], page_size=200)` → **0** hits,
where the **2026-08-26** update immediately below recorded this exact call
(classification filter alone) returning **43** hits one day earlier. Ruled
out a `"Question"`-specific cause: swapped in `include_only_classified_elements=
["Template"]` (a long-established classification, unrelated to anything
created recently) → also **0**. An unfiltered call on the same connection
(`find_glossary_terms(search_string="*", starts_with=True, graph_query_depth=0,
page_size=200)`, no classification filter at all) → **200** hits (page-size
ceiling), so the connection/server itself is healthy and the classification
data is intact (confirmed via direct `get_term_by_guid` on one of the
"missing" terms — its `elementHeader.otherClassifications` correctly carries
`classificationName: "Question"`). So as of this server instance today,
`include_only_classified_elements` appears to return zero regardless of
`sequencing_order` — a strictly worse regression than this issue's original
scope. Workaround applied in `perspectives_handler.py`: drop the server-side
classification filter entirely, fetch unfiltered (`page_size=1000`, the
server's own max), and filter client-side on `otherClassifications`.
Worth re-testing the classification-filter-alone case again on a later
server build, the way this issue's own history already does for the
combined-filter case.

**Update 2026-08-26: re-confirmed again, unchanged.** Re-ran the exact
repro against the current server build (`6.2-SNAPSHOT`, platform
timestamp `2026-08-24T18:27:04Z` — the same build that turned out to have
resolved ISSUE-69, checked in the same pass on the chance this one had
also moved). It hadn't: `include_only_classified_elements=["Question"]`
alone returns 43 hits (count has drifted from the 33 in earlier checks —
unrelated to the bug, just live data), `sequencing_order=
"PROPERTY_ASCENDING"` alone returns 200 (page-size ceiling), and combining
both still returns exactly **0**. Same symptom as every prior check.

**Status:** double-checked again 2026-08-18 (per dwolfson's explicit
request) — core defect persists, and this pass rules out a client-side
cause definitively by capturing the actual outgoing request body via a
traced `_async_make_request`: `include_only_classified_elements=["Question"]`
alone sends a well-formed body (`includeOnlyClassifiedElements: ["Question"]`,
no `sequencingOrder` key) and returns **2 hits** (data has changed since the
original 33 — unrelated to the bug). Adding *only* `sequencing_order=
"PROPERTY_ASCENDING"` to that exact same body (confirmed via the trace —
every other field byte-identical) drops the result to **0**. Also tried
adding `sequencing_property="displayName"` on top — still 0. Since ISSUE-60
(sequencing order itself) is now fixed server-side, this entry's trigger
condition may have shifted from what it was originally — worth a fresh
root-cause dig rather than assuming the original mechanism still applies
unchanged — but the *symptom* (combining `sequencing_order` with a
classification filter zeroes the result) is unambiguously still present,
confirmed via real request/response, not just method-level return values.

**Status:** confirmed bug (Egeria server) — found 2026-07-28 debugging
Egeria Explorer's Perspectives page showing Perspectives but no Questions.
Related to ISSUE-40 below (same broken parameter, different — and more
severe — failure mode: not just wrong order, but zero rows). Consolidated
in from `egeria-workspaces-fs/PYEGERIA_ISSUES.md` 2026-08-05.

**How to trigger** (`GlossaryManager.find_glossary_terms`, qs-view-server,
33 `GlossaryTerm`s classified `Question`):
```python
# classification filter alone: 33 hits
mgr.find_glossary_terms(search_string="*", starts_with=True, output_format="JSON",
                        page_size=200, graph_query_depth=0,
                        include_only_classified_elements=["Question"])

# sequencing_order alone (no classification filter): 200 hits (unrelated terms, page_size ceiling)
mgr.find_glossary_terms(search_string="*", starts_with=True, output_format="JSON",
                        page_size=200, graph_query_depth=0,
                        sequencing_order="PROPERTY_ASCENDING")

# BOTH together: 0 hits
mgr.find_glossary_terms(search_string="*", starts_with=True, output_format="JSON",
                        page_size=200, graph_query_depth=0,
                        sequencing_order="PROPERTY_ASCENDING",
                        include_only_classified_elements=["Question"])
# -> []  (or a "No elements found" string, depending on call shape)
```
Isolated further: `sequencing_order="PROPERTY_ASCENDING"` is the trigger —
`sequencing_property` alone (no `sequencing_order`) does **not** break it
(still 33 hits). It's specifically `sequencing_order` + a classification
filter.

**Expected:** the classification filter's 33 matches, sorted by the given
sequencing property (or, per ISSUE-40, at least returned in server-internal
order — but not silently emptied).

**Actual:** zero rows, with no error — the query silently looks like
"nothing matches" rather than failing loudly, which is what made this hard
to spot (the egeria-workspaces-fs `/api/questions` endpoint returned
`{"total": 0}` with a 200 status; only comparing against a live count of
Question-classified terms in Egeria surfaced that this was wrong, not just
an empty demo).

**Impact / workaround:** egeria-workspaces-fs's `perspectives_handler.py`'s
`get_questions()` used exactly this broken combination. Fixed by dropping
`sequencing_order`/`sequencing_property` from the call — the endpoint
already sorts client-side, so the server-side sequencing was redundant
even before this bug was found. No other known callers currently combine
`sequencing_order` with a classification filter, but worth checking
`include_only_classified_elements`/`matchClassifications` callers
generally if new zero-result reports show up elsewhere.

---

### ISSUE-79: native survey against a template-created `FileFolder` asset fails server-side — `assetConnector` is null in `BasicFolderConnector.getFile()`

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

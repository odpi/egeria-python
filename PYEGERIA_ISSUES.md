# Pyegeria / Egeria Issue Tracker

Merged from the former `PYEGERIA_ISSUES.md` (Egeria Explorer usage bugs,
started 2026-06) and `PYEGERIA_GAPS.md` (exception/validation infrastructure
gaps, started 2026-07-31) into one file, with every entry re-verified against
the current codebase as of 2026-07-31 rather than trusting old status claims.
Reorganized 2026-08-04 so **open issues are at the top** and fixed/not-a-bug
entries live in the Appendix — read top-to-bottom for "what's still
outstanding," jump to the Appendix only when you need the history of
something already resolved.

**Layer classification** — every entry is tagged with where the defect
actually lives, since that determines who can fix it:
- **Pyegeria** — a defect in this repo's own code (`pyegeria/`). Fixable
  here directly.
- **Egeria Server** — the view server / repository returns wrong or
  inconsistent behavior; no pyegeria client-side change can fix it. Track
  against the Egeria server issue tracker.
- **Not a bug** — deliberate behavior, a deployment/version-pinning issue,
  or a docs/class-organization sharp edge rather than a defect.

**Status values:** `open` (found, not yet reviewed) · `fixed` (patched in
this repo, verified) · `wont-fix` (owner decided against it, reason noted) ·
`n/a` (not a bug / nothing to fix here).

**Numbering:** unified as `ISSUE-#`, sequential in the order each was found
— stable across the 2026-08-04 reorg (an issue keeps its number regardless
of which section it now sits in), so old references stay valid. Old
references carried forward in parens for traceability (`PY-#` from the
original issues doc, `GAP-#` from the gaps doc). Note: the original issues
doc's header claimed compact status tracking also lived in `BACKLOG.md`
under a "pyegeria Upstream Bugs" section using the same `PY-#` numbering —
checked git history, that section never existed in `BACKLOG.md`. That
cross-reference was already stale; not carried forward here.

**Renumbered 2026-08-15**: found three `ISSUE-#` collisions — each number
had been independently reused for a genuinely different entry (`ISSUE-45`,
`ISSUE-46`, `ISSUE-47`, each with two unrelated titles). Kept the original
number on whichever entry came first by file position and renumbered the
later duplicate: old `ISSUE-45` (`findMetadataElements` subtype filter,
found 2026-08-05) → `ISSUE-53`; old `ISSUE-47` (`findMetadataElements`
scoped to `Referenceable`, found 2026-08-06) → `ISSUE-54`; old `ISSUE-46`
(exclude-type enhancement, found 2026-08-05) → `ISSUE-55`. No content
changed, only the header numbers.

Unless noted otherwise, repro commands assume a running Egeria view server
reachable at `https://localhost:9443`, view server name `qs-view-server`,
user `erinoverview` / `secret` (adjust to your env) — updated from the
original `peterprofile` since several of the old repro snippets used a
class (`NoteLogManager`, `CommentManager`) that doesn't exist in the current
package; replaced with `EgeriaTech`, which does. **Caveat added 2026-08-04**
(see ISSUE-29): different demo users can see genuinely different data for
the same query, thanks to governance zone visibility — don't assume a
result mismatch is a pyegeria bug before checking whether the same user was
used on both sides of the comparison.

**Consolidated 2026-08-05**: `egeria-workspaces-fs` had grown its own
independent `PYEGERIA_ISSUES.md` (started 2026-06, own `PY-#` numbering,
last entry `PY-23`) in parallel with this file — the two repos accumulated
overlapping and unique issues separately rather than sharing one tracker.
**This file is now the sole canonical tracker for both repos.**
`egeria-workspaces-fs/PYEGERIA_ISSUES.md` has been replaced with a pointer
here. Reconciliation: `PY-1` through `PY-14` in that file were pure
duplicates of entries already tracked here (via this file's own
`ISSUE-# (PY-#)` aliases) and were dropped, not re-added.
`PY-15`/`PY-16`/`PY-17`/`PY-18`/`PY-19`/`PY-20`/`PY-21`/`PY-22` were unique
to that file and are now `ISSUE-35` through `ISSUE-42` respectively (same
`ISSUE-# (PY-#)` alias convention as the original merge). `PY-23` was the
same investigation as this file's own `ISSUE-34` (both about
`find_metadata_elements` ignoring pagination) — merged into `ISSUE-34`
rather than duplicated. **Update 2026-08-05, same day:** `ISSUE-34` was
itself provisionally misdiagnosed as a residual Egeria-server-side bug at
the point of that merge; further investigation (prompted by the user)
found the real root cause — a moved Egeria pagination convention pyegeria
was tracking incorrectly — and fully fixed it, so `ISSUE-34` is now closed
and lives in the Appendix, not the open "Egeria Server" section. Read
`ISSUE-34`'s own entry for the full story; it's worth reading even though
it's closed. If a comment anywhere still cites a bare `PY-#` in the 15-22
range, search this file for `(PY-#)` to find its new `ISSUE-#` home.

---

# Open Issues

## Pyegeria — fixable here

### ISSUE-59: `Create <X>` upsert commands (`upsert: true` in the compact spec) silently create a duplicate element, instead of updating in place, when the caller changes `### Qualified Name` to something the as-is lookup has never seen before — an explicit `### GUID` on the same command is also ignored for that lookup

**Status:** fixed 2026-08-15 (Pyegeria/Dr.Egeria — `md_processing/v2/processors.py`).
Applied both halves of the candidate fix:
1. **`fetch_as_is()` now honors an explicit `### GUID`** — tries
   `fetch_element(guid)` directly, before any qualified-name-derivation or
   name-based lookup, so an author who supplies a GUID to target a specific
   element (e.g. to rename its qualified name) is no longer silently
   ignored.
2. **The existing "same Display Name, different QN" guard (step 4a) now
   surfaces a real warning** (`self._add_warning(...)`, visible in
   `--process`/`--validate` output) instead of only a `logger.info()` line
   nobody authoring markdown would ever see. The message names the
   existing element's GUID and tells the caller to re-run with
   `### GUID <guid>` if they meant to update/rename it — turning a silent
   duplicate into a caught, actionable warning when no GUID is supplied.

**Verified live**, exact repro from the original report: created a
`Perspective` with only `### Display Name` (auto-derived QN). Re-running
`Create Perspective` with the same Display Name and a new
`### Qualified Name`, no GUID → now correctly creates a second element
**and prints an explicit warning** naming the original GUID and how to
target it (previously: fully silent). Re-running a third time with the
same new QN plus `### GUID <original-guid>` → correctly rewrote to
`Update Perspective`, `Found: Yes`, same original GUID returned (no third
duplicate) — confirmed via direct fetch that the *original* element's
`qualifiedName` property actually changed and its version incremented
(1→2), not a new element. Test elements cleaned up. `pytest tests/ -m unit`
passes.

**Original status:** open.

**Layer:** Pyegeria (`md_processing/v2/processors.py` — the `fetch_as_is`/
`CommandRewriter` Create↔Update upsert-detection path; exact function not
yet traced past the symptom).

**Repro:** an existing `Perspective` named "Financial" already exists,
created previously with no explicit qualified name (so it got
Dr.Egeria's auto-generated `Coco Pharmaceuticals::Perspective::
Financial::1.0`). Re-running `Create Perspective` for the same
`### Display Name`, this time adding an explicit
`### Qualified Name\nPerspective::Financial` (to give it a caller-chosen,
portable qualified name instead — see ISSUE-58 above for why), was
expected to update the existing element in place (`upsert: true`,
matched by display name). Instead it silently created a **second**,
distinct `Perspective` element sharing the display name "Financial" —
confirmed via `get_element_by_guid()` on both GUIDs (the original and the
new one) and via `get_guid_for_name("Financial")` immediately starting to
raise `"Multiple elements found for supplied name!"` right after the
re-run, where it had resolved cleanly before. The rendered output even
prints `## Update Perspective` as its header, which reads as confirmation
of an in-place update — that label is misleading here; it does not
reflect what actually happened server-side.

Also tried supplying `### GUID` (the bundle backing `Create Perspective`,
`Referenceable` → `New-Element`, declares a `GUID` attribute) set to the
existing element's real GUID, on the theory that an explicit GUID would
let the as-is check target that specific element regardless of name/QN
matching. Same result — a second, unrelated new GUID assigned, existing
element untouched, `### GUID` had no observable effect on the outcome.

**Impact:** any attempt to "rename" an existing element's qualified name
via a `Create <X>` markdown command — the natural way to do it, since
there is no separate `Update <X>` command family exposed to Dr.Egeria
authors for most types — silently multiplies the element instead of
correcting it, and only the *next* by-name lookup against that display
name reveals anything went wrong (a `PyegeriaException`, not a validation
error at authoring time). A caller who doesn't immediately re-query by
name after the "successful" `Update` output has no signal that a
duplicate was just created.

**Workaround used:** deleted the accidental duplicates
(`MetadataExpert.delete_metadata_element(guid)`) and instead used the
type-specific dedicated update method directly against pyegeria
(`ActorManager.update_perspective(perspective_guid, {"class":
"UpdateElementRequestBody", "mergeUpdate": True, "properties": {"class":
"PerspectiveProperties", "qualifiedName": "<new value>"}})`) — this
targets the element purely by GUID with no name/QN-based as-is lookup
involved at all, and correctly updated all 12 Perspectives in place
(same GUID before/after, confirmed via direct read-back and via
`get_guid_for_name()` on the new qualified name resolving to the
unchanged GUID). Not a Dr.Egeria-markdown-level workaround — required
dropping to raw pyegeria SDK calls.

**Candidate fix:** when an explicit `### GUID` is present on a `Create`
command whose spec has `upsert: true`, the as-is fetch should try that
GUID directly (`fetch_element_by_guid`) before falling back to name-based
matching — this is the more surprising half of the bug, since the
attribute is declared and accepted without error, it just isn't used for
what the author would reasonably expect. Separately, when no GUID is
given but the as-is lookup by display name finds an existing element
under a *different* qualified name than the one just supplied, that's a
real ambiguity Dr.Egeria itself should surface to the caller (e.g. "found
an existing element with this display name under a different qualified
name — did you mean to update it? re-run with `### GUID <its-guid>` to
confirm") rather than silently treating "new qualified name" as "new
element."

### ISSUE-58: ~~Dr.Egeria's by-display-name element resolver has no type-scoping~~ — corrected: not a bug, a caller error (used a display name where a qualified name was needed, and used the wrong qualified-name string on the one retry)

**Status:** n/a — not a bug. Corrected 2026-08-15, same day filed, by the
same reporting session. (Originally misnumbered ISSUE-57 — collided with
the pre-existing, unrelated `GovernanceResults` entry of that number;
renumbered same-day before anything referenced it externally.)

**What actually happened:** the original repro below is real (the
"Multiple elements found" failure did occur, repeatedly), but the
diagnosis was wrong twice over:
1. The `Link Perspective to Question` compact-spec attribute
   (`md_processing/data/compact_commands/commands_actor_manager_compact.json`)
   literally documents `Perspective Name`'s `description` as **"Qualified
   name of the Perspective"** — the field was never meant to take a bare
   display name at all. `resolve_element_guid()`
   (`md_processing/v2/processors.py`) confirms this: Pass 1 calls
   `self.client.__async_get_guid__(qualified_name=name_or_guid,
   display_name=name_or_guid, property_name="displayName",
   tech_type=tech_type or None)` — it tries the input string as *both* an
   exact qualified-name match and a display-name search in one call.
   Passing a bare display name that happens to be non-unique
   (`"Governance"`) hits the display-name branch and finds multiple
   matches, exactly as designed for an ambiguous input — this is the
   resolver behaving correctly given what it was handed, not a resolver
   defect.
2. The original repro's "the qualified name doesn't work either" claim
   was itself wrong: the qualified name tried
   (`Coco Pharmaceuticals::Term::Governance::1.0`) used the wrong type
   segment — Questions (GlossaryTerms) really do get a `::Term::` segment,
   but a `Perspective`-typed element's actual qualified name is
   `Coco Pharmaceuticals::Perspective::Governance::1.0` (confirmed via
   direct `get_element_by_guid()` read) — `::Term::` vs `::Perspective::`.
   Retried with the correct string and it resolved cleanly on the first
   try, no ambiguity error at all:
   ```
   ### Perspective Name
   Coco Pharmaceuticals::Perspective::Governance::1.0
   → "Successfully linked Perspective to Question relationship."
   ```

**Real root cause, on the consumer-repo side, not here:**
`resource-explorer`'s `docs/dr-egeria/foundations.md` never gave its
Perspective terms an explicit `### Qualified Name` at creation time, so
they only had Dr.Egeria's auto-generated one — and every
`Link Perspective to Question` command in that repo was passing the bare
`### Display Name` instead of a qualified name, in violation of what the
attribute actually expects. Fixed on that side: every Perspective now gets
an explicit, unique `### Qualified Name` (`Perspective::<Name>`, not the
auto-generated `Coco Pharmaceuticals::Perspective::<Name>::1.0` — kept
portable rather than baking in this instance's default local
qualifier/org name), and `Link Perspective to Question` commands reference
Perspectives by that qualified name going forward. See
`resource-explorer`'s `docs/dr-egeria/foundations.md` Perspectives section
and `docs/survey-question-context-plan.md` for the full writeup.

**No pyegeria/Dr.Egeria code change needed.** Kept as a closed entry
(rather than deleted) since the original repro and the corrected
diagnosis are both useful — the type-scoping idea in the old "candidate
fix" below is still a reasonable resilience improvement (resolving
`Perspective Name` should arguably fail loudly and immediately if handed a
non-unique display name in a field documented as "qualified name", rather
than the correct-but-easy-to-misread ambiguous-match error it already
gives), but it's a nice-to-have, not a defect fix.

<details>
<summary>Original (incorrect) repro and diagnosis, kept for context</summary>

**Repro:** in a live Egeria instance carrying the stock Coco
Pharmaceuticals demo data alongside application-authored `GlossaryTerm`s,
running `Link Perspective to Question` (`resource-explorer`'s
`docs/dr-egeria/scouting-questions.md` pattern — see its `CLAUDE.md`-
adjacent `docs/survey-question-context-plan.md`) with `Perspective Name`
set to any of `Governance`, `Steward`, `Privacy`, `Community`, `Security`
fails 100% of the time (confirmed across ~50+ independent attempts, 6
separate batched Dr.Egeria `process` calls) with:
```
❌ Execution Blocked
Referenced element 'Governance' for attribute 'Perspective Name' not found.
```
Direct `ClassificationExplorer.get_guid_for_name("Governance")` (no
`type_name` filter) reproduces the underlying cause exactly:
```
PyegeriaException: CLIENT_ERROR_400 ... output=`Multiple elements found for supplied name!`
```
The other 7 names used in the same file (`Financial`, `Data Owner`,
`Consumer`, `App/AI Builder`, `Data Expert`, `Architecture`, `Admin`)
resolve cleanly every time — this is a real, 100%-reproducible collision
for specific names, not transient indexing/resolution lag.

**Workaround used at the time (superseded by the real fix above):** since
the ambiguous elements' own GUIDs were already known from their original
creation, every blocked `ScopedBy` link was completed by calling
`ClassificationExplorer.add_scope_to_element(scoped_by_guid=
<known_perspective_guid>, element_guid=<question_guid>, body=
{"class": "NewRelationshipRequestBody", "properties": {"class":
"ScopedByProperties"}})` directly — bypassing Dr.Egeria's name resolver
entirely. Not needed going forward now that Perspectives carry explicit
qualified names.

</details>

### ISSUE-56: `ReferenceDataManager`'s 6 relationship-link methods all route through the element-body validator, not the relationship-body validator — every call built per the method's own documented sample body fails Pydantic validation

**Re-verified 2026-08-15 (same day, third check — asked twice more after
the original fix), no regression.** Created a fresh `ValidValueDefinition`
pair and linked them via `_async_link_valid_value_member()` — succeeds
(previously failed 100% of the time). Test elements cleaned up.

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/reference_data.py`).
Applied the candidate fix as described (mechanical, same call shape):
swapped `_async_create_element_body_request(url, [PropClassName], body)` →
`_async_new_relationship_request(url, [PropClassName], body)` at all 7
sites — the 6 listed below plus a 7th the original report flagged as
"not individually re-checked" (`_async_link_consistent_valid_values`,
which needed `None` instead of a properties-class list since that
relationship has no properties of its own — same wrong helper, same fix).
Verified live: created a real `ValidValueDefinition` pair and linked them
via `link_valid_value_member()` with exactly the body shape shown in the
Reproduced section below — succeeded (previously failed with
`PyegeriaInvalidParameterException`). `pytest tests/ -m unit` passes.

**Independently re-verified from the reporting side** (resource-explorer
session, same day, after `uv lock --upgrade-package pyegeria` picked up
6.0.18.1 from PyPI): confirmed via `inspect.getsource` that
`_async_link_valid_value_member`/`_async_link_valid_values_assignment`/
`_async_link_reference_value_assignment` now call
`_async_new_relationship_request` instead of
`_async_create_element_body_request`; ran the real blocked caller
(`resource-explorer/scripts/create_measure_definitions.py`) against a live
server — all 3 `ValidValueMember` links that previously failed 100% of the
time now succeed, and a second run confirms idempotency (find-or-create
skips existing elements, re-linking an already-linked member doesn't
error). `resource-explorer/pyproject.toml`'s `pyegeria` constraint bumped
to `>=6.0.18.1` accordingly.

**Original status:** open, found 2026-08-15 (Dan/Claude, resource-explorer session)
resuming `scripts/create_measure_definitions.py`'s `ValidValueMember` linking
step (docs/survey-question-context-plan.md), which was blocked on this exact
bug (`link_valid_value_definition()`) as of 2026-08-13 — expected it to be
fixed now that `ValidValuesAssignment`/`ReferenceValueAssignment` linking
methods exist (they didn't before), but re-verified live and the underlying
bug is unchanged, just now present in 2 additional methods that didn't
exist when it was first hit.

**Layer:** Pyegeria (`pyegeria/omvs/reference_data.py`).

**What:** `ReferenceDataManager` has (at least) 6 async relationship-link
methods, each documented with a `"class": "NewRelationshipRequestBody"`
sample body in its own docstring, but each calls
`self._async_create_element_body_request(url, [PropClassName], body)`:

- `_async_link_valid_value_member` (line 964) → `ValidValueMemberProperties`
- `_async_link_valid_values_assignment` (line 1149) →
  `ValidValuesAssignmentProperties`
- `_async_link_reference_value_assignment` (line 1334) →
  `ReferenceValueAssignmentProperties`
- `_async_link_valid_values_implementation` (line 1521) →
  `ValidValuesImplementationProperties`
- `_async_link_valid_values_mapping` (line 2076) →
  `ValidValuesMappingProperties`
- (a 6th, ConsistentValidValues-shaped call — not individually re-checked
  this session, flagged as likely affected by the same pattern; grep
  `_async_create_element_body_request(url, \["` in this file to find any
  others)

`_async_create_element_body_request` (`pyegeria/core/_server_client.py:7134`)
unconditionally calls `self.validate_new_element_request(body, prop)`
(`_server_client.py:6045`), which validates a dict body against
`TypeAdapter(NewElementRequestBody)` — a Pydantic model whose `class_` field
is `Annotated[Literal["NewElementRequestBody"], ...]`
(`pyegeria/models/models.py:418`). A `NewRelationshipRequestBody`-shaped
dict (`class_: Literal["NewRelationshipRequestBody"]`,
`pyegeria/models/models.py:277`) — exactly what each method's own docstring
tells the caller to build — always fails that Literal check. The correct
helper already exists and is unused by any of these 6 methods:
`_async_new_relationship_request` (`_server_client.py:7188`), which calls
`self.validate_new_relationship_request(body, prop)`
(`_server_client.py:6090`) against `TypeAdapter(NewRelationshipRequestBody)`
— the matching validator for the body shape these methods actually need.

**Reproduced** (pure validation, no live server needed — confirmed the
defect is in the client-side Pydantic check itself, not a server response):
```python
from pydantic import TypeAdapter
from pyegeria.models.models import NewElementRequestBody

body = {
    "class": "NewRelationshipRequestBody",
    "properties": {"class": "ValidValueMemberProperties",
                    "isDefaultValue": False, "label": "test", "description": ""},
}
TypeAdapter(NewElementRequestBody).validate_python(body)
# ValidationError: 1 validation error for NewElementRequestBody
# class
#   Input should be 'NewElementRequestBody' [type=literal_error, input_value='NewRelationshipRequestBody', ...]
```
`_validate_body` (`_server_client.py:6013`) re-raises any `ValidationError`
as `PyegeriaInvalidParameterException` rather than degrading silently, so
every one of these 6 methods raises that exception on any body built per
its own documented sample — there is no way to call them successfully as
documented today.

**Impact:** `ReferenceDataManager.link_valid_value_definition()` (the only
one of the 6 with a real caller in this session — `resource-explorer`'s
`scripts/create_measure_definitions.py`) cannot link a `ValidValueMember`
to its parent `ValidValueSet` at all — confirmed live 2026-08-13, the
script's `ValidValueDefinition` elements are created successfully but every
`link_valid_value_definition()` call fails, caught and reported by the
script rather than crashing the run. The other 5 methods are unused by any
downstream caller in this codebase yet (no live repro attempted for them),
but the same Literal mismatch applies identically by inspection — same
call pattern, same underlying helper.

**Candidate fix:** swap
`self._async_create_element_body_request(url, [PropClassName], body)` →
`self._async_new_relationship_request(url, [PropClassName], body)` at each
of the 6 (or more — re-grep) call sites. Mechanical, single-line-per-site
change; `_async_new_relationship_request`'s signature
(`url, prop, body`) already matches the existing call shape exactly, no
other code needs to change. Not applied here — per this repo's own policy,
egeria-python bugs are logged here and fixed only with explicit owner
approval, not patched directly by an assisting session.

### ISSUE-51: `AsyncBaseCommandProcessor.fetch_element()`'s two fallback paths return incompatible shapes — the MetadataExpert fallback crashes downstream code that assumes ClassificationExplorer's envelope

**Status:** fixed 2026-08-15 (Pyegeria — `md_processing/v2/processors.py`).
Fix shape changed from the original candidate below after discussion: on a
`PyegeriaTimeoutException` specifically, `fetch_element()` now retries the
*same* ClassificationExplorer call (up to 2 attempts) instead of falling
through to the shape-incompatible MetadataExpert path — a timeout means
either the request was transient (retrying the same call is exactly as
likely to succeed as switching endpoints) or the server is under sustained
load (in which case a different endpoint is no more likely to help, and
risks the exact shape-mismatch crash this issue describes). MetadataExpert
remains the fallback for every *non*-timeout failure (not found,
unsupported type, etc.), and as a last resort after timeout retries are
exhausted. Verified: `pytest tests/ -m unit` passes; re-ran the same
100+-command help file that originally triggered the crash against a
freshly-restarted server with 0 errors in the first several minutes (vs.
crashing on the very first command before). The underlying shape
inconsistency between the two paths (described below) still exists — this
fix avoids hitting it in the timeout case rather than resolving the shape
mismatch itself; a genuine non-timeout MetadataExpert-fallback call could
still hit it, so the original diagnosis is left below for reference.

**Original status:** open, found 2026-08-15 (Dan) processing the regenerated
`dr-egeria` help file (100+ `Create`/`Update Term` commands) against
`qs-view-server` while the server was under heavy, unrelated background
load (see ISSUE-52 — same session).

**Layer:** Pyegeria (`md_processing/v2/processors.py`).

**What:** `AsyncBaseCommandProcessor.fetch_element()` (`processors.py:1146`)
tries ClassificationExplorer first (`self.client._async_get_element_by_guid_`),
unwraps `res["element"]` if present, and returns that. If that call raises
(caught silently, logged at `debug` only), it falls back to
`self.client._async_get_metadata_element_by_guid(guid)` (MetadataExpert) and
returns *that* result directly, with no unwrapping. Every caller of
`fetch_as_is()`/`fetch_element()` downstream (e.g.
`CollectionManagerProcessor.apply_changes()`) then does
`self.as_is_element['elementHeader']['guid']` unconditionally, assuming both
paths hand back the same `{"elementHeader": {...}, "properties"/"element"...}`
envelope shape.

**Reproduced:** processing `## Update Glossary` for the pre-existing
`dr-egeria` glossary crashed with `KeyError: 'elementHeader'` —
`self.as_is_element` at the point of the crash was
`{'headerVersion': 0, 'status': 'ACTIVE', 'type': {..., 'typeName':
'Glossary', ...}, ...}`, i.e. the *contents* of an `elementHeader` object,
not a dict containing one — consistent with the ClassificationExplorer call
timing out under load (confirmed independently: a standalone repro of
`client._async_get_element_by_guid_(guid)` against the same server, same
session, hit a hard 30s `PyegeriaTimeoutException` on this exact endpoint),
falling through to the MetadataExpert path, whose
`_async_get_metadata_element_by_guid` routes through
`_async_get_guid_request(..., output_format="JSON")` — that helper's
`output_format == "JSON"` branch returns `resp_json.get("element", ...)`
raw, without the normalization/unwrapping ClassificationExplorer's own path
already does elsewhere in the codebase, for at least this element type.

**Impact:** any `Update`/upsert-style Dr.Egeria command whose primary
element-lookup call fails or times out (not narrow to Glossary — any type
routed through the shared base `fetch_element()`) crashes with an
unhandled `KeyError` instead of retrying, warning, or falling back to
`Create`, and aborts that one command while the rest of a batch continues
(confirmed: the batch run kept going after this crash).

**Candidate fix:** make the two fallback paths agree on shape before
`fetch_element()` returns — either normalize the MetadataExpert path to
always produce `{"elementHeader": ..., ...}` (checking what
`_async_get_metadata_element_by_guid` actually returns for a few element
types to confirm whether it's ever *already* wrapped, or always flat), or
make the single downstream contract explicit and defensive
(`self.as_is_element.get('elementHeader', self.as_is_element).get('guid')`
as a minimal guard) so a shape mismatch degrades to "treat as not found"
rather than crashing. Needs a live server that isn't under load (see
ISSUE-52) to safely re-verify the exact MetadataExpert raw shape without
every repro attempt itself timing out.

### ISSUE-49: `MetadataExpert.get_metadata_element_relationships` (lookup a relationship by its two endpoint GUIDs) returns "No elements found" for a relationship confirmed to exist

**Re-verified 2026-08-15 (same day, follow-up run), no regression.**
Recreated the exact repro fresh (new `ResultsSet` + `SavedQuery` pair,
real `SmartQuery` link) — `get_metadata_element_relationships(rs_guid,
sq_guid, "SmartQuery", None)` correctly returns the real relationship
(`relationshipGUID`, both ends populated) instead of "No elements found".
Test elements cleaned up. `pytest tests/ -m unit` passes.

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/metadata_expert.py`).
Root cause: the shared `process_related_element_list()` helper has two
envelope shapes it can parse — a related-*element* envelope
(`{"relatedElementList": {"elementList": [...]}}`) and a relationship-list
envelope (`{"relationshipList": {"relationships": [...]}}`) — selected by
its `relationship_list` parameter. Two bugs stacked: (1)
`_async_get_metadata_element_relationships` (and its sibling
`_async_get_all_metadata_element_relationships`) called the helper with
the default `relationship_list=False`, so it looked for the wrong
top-level key (`relatedElementList`, which doesn't exist in a relationship
response) and returned the `NO_ELEMENTS_FOUND` sentinel immediately; (2)
even with `relationship_list=True` set (as `_async_find_relationships_
between_elements`, ISSUE-39's method, already did), the helper's inner
lookup used the wrong key too — `elementList` instead of the real
`relationships` key nested inside `relationshipList`. Confirmed live via
raw response inspection: `POST .../linked-by-type/{type}/to-elements/{guid}`
returns `{"relationshipList": {"relationships": [...]}}` — never
`relatedElementList`/`elementList` at all.

**Fixed both bugs**: `process_related_element_list()` now looks up
`"relationships"` (not `"elementList"`) when `relationship_list=True`; the
two relationship-endpoint call sites that weren't already passing
`relationship_list=True` now do
(`_async_get_metadata_element_relationships`,
`_async_get_all_metadata_element_relationships`).

**Verified live**: recreated the exact repro below (`ResultsSet` +
`SavedQuery` + real `SmartQuery` link via
`link_saved_query_to_results_set`) — `get_metadata_element_relationships`
now returns the relationship with the matching GUID instead of "No
elements found". Also fixed ISSUE-39 as a side effect (same root cause,
same helper) — see that entry. `pytest tests/ -m unit` passes throughout.

**Original status:** open, found 2026-08-10 (Dan) building egeria-workspaces-fs's
migration of Egeria Insights' saved queries onto the real `SavedQuery`/
`SmartQuery` types (`insights_handler.py`, Track C.1 of
`EGERIA_INSIGHTS_QUERY_MODEL.md`).

**Layer:** Pyegeria (`pyegeria/omvs/metadata_expert.py`) — or possibly the
view-service endpoint it calls; not yet narrowed further, see Candidate fix.

**What:** created a `SmartQuery` relationship between a `ResultsSet` and a
`SavedQuery` via `CollectionManager.link_saved_query_to_results_set()`
(itself new in 6.0.17.18, part of the same feature — see that method's own
docstring), which returned a real relationship GUID. Immediately after,
looked the same relationship up by its two endpoint GUIDs via
`MetadataExpert.get_metadata_element_relationships(end1_guid=<ResultsSet
guid>, end2_guid=<SavedQuery guid>, relationship_type="SmartQuery",
body={"class": "ResultsRequestBody"})` — the exact body shape from the
method's own docstring sample — and got back the string `"No elements
found"` rather than the relationship. Tried both `body={}` and
`body={"class": "ResultsRequestBody"}`; same result both times.

The relationship is genuinely there — independently confirmed via
`ClassificationExplorer.get_relationships(relationship_type="SmartQuery",
output_format="JSON")`, which lists it with the correct `end1`/`end2` and
the same GUID `link_saved_query_to_results_set()` returned.

**Where seen:** `insights_handler.py`'s saved-query delete path would have
used this method to look up the `SmartQuery` relationship's GUID from the
`ResultsSet`/`SavedQuery` GUIDs alone, if it needed to. Worked around
entirely rather than root-caused further — see Candidate fix.

**Repro:**
```python
from pyegeria import CollectionManager, MetadataExpert
cm = CollectionManager(view_server="qs-view-server", platform_url=url, user_id=user, user_pwd=pwd)
cm.create_egeria_bearer_token()
rel_guid = cm.link_saved_query_to_results_set(results_set_guid, saved_query_guid)  # succeeds, real guid

me = MetadataExpert(view_server="qs-view-server", platform_url=url, user_id=user, user_pwd=pwd)
me.create_egeria_bearer_token()
me.get_metadata_element_relationships(
    end1_guid=results_set_guid, end2_guid=saved_query_guid,
    relationship_type="SmartQuery", body={"class": "ResultsRequestBody"},
)
# -> "No elements found"

from pyegeria import ClassificationExplorer
ce = ClassificationExplorer(view_server="qs-view-server", platform_url=url, user_id=user, user_pwd=pwd)
ce.create_egeria_bearer_token()
ce.get_relationships(relationship_type="SmartQuery", output_format="JSON", body=None)
# -> [{"relationshipHeader": {..."guid": rel_guid...}, "end1": {...ResultsSet...}, "end2": {...SavedQuery...}}]
# same rel_guid, so the relationship is real and correctly formed
```

**Candidate fix:** not yet investigated — could be a body-shape mismatch
this repro hasn't found, a wrong end1/end2 ordering assumption in the
method's URL construction (`.../metadata-elements/{end1_guid}/linked-by-
type/{relationship_type}/to-elements/{end2_guid}`), or a real server-side
gap specific to this endpoint (`SmartQuery` has no bespoke view-service
endpoint of its own — types/properties only, per Egeria PR #9200 — so it's
plausible the generic linked-by-type endpoint doesn't handle every
relationship type uniformly). Whoever picks this up should try swapping
end1/end2, and try a relationship type with an established working example
of this same method (if one exists) to isolate whether `SmartQuery`
specifically is the problem or the method itself.

**Workaround in use:** don't rely on this lookup at all — capture the
relationship GUID from `link_saved_query_to_results_set()`'s own return
value at creation time and persist it (in `insights_handler.py`'s case, in
the `SavedQuery`'s own `additionalProperties`), so any later operation that
needs to detach the relationship already has its GUID in hand.

---

### ISSUE-23: `max_mermaid_node_count` defaults to 5 across every shared find/get request helper, silently truncating server-generated mermaid graphs

**Status:** fixed 2026-08-15 (Pyegeria). Raised every remaining
`max_mermaid_node_count` default from 5 to 10, matching
`_async_find_request`'s default (already 10 from an earlier pass):
`_async_get_name_request`, `_async_get_guid_request`,
`_async_get_request_body_request`, `_async_activity_status_search_request`,
and the content-status/deployment-status search variants (all in
`pyegeria/core/_server_client.py`), plus `AssetCatalog`'s three lineage-graph
methods in `pyegeria/omvs/asset_catalog.py` (`_async_get_asset_lineage_graph_by_guid`,
`get_asset_lineage_graph_by_guid`, `get_asset_lineage_mermaid_graph`, added
as part of ISSUE-24 at 5, now raised to 10 for consistency). Verified live
via request-body spies that the new default (10) actually reaches the wire
for `_async_get_guid_request` and `_async_get_asset_lineage_graph_by_guid`.

Also fixed the "third case" this issue flagged as a candidate follow-up:
`get_solution_blueprint_by_guid`/`_async_get_solution_blueprint_by_guid`
(`pyegeria/omvs/solution_architect.py`) built no body at all when the
caller left `body=None`, so `graph_query_depth`/`max_mermaid_node_count`
were genuinely dead parameters regardless of the shared default — same
"dead parameter" shape ISSUE-26 already fixed for
`get_info_supply_chain_by_guid`/`get_solution_role_by_guid`. Fixed the same
way: build an `AnyTimeRequestBody` with `graphQueryDepth`/
`maxMermaidNodeCount` populated when `body is None`, and added
`max_mermaid_node_count` as an explicit parameter (was previously not even
accepted). Verified live: a request-body spy confirmed caller-supplied
`graph_query_depth=9`/`max_mermaid_node_count=77` now reach the wire, where
previously neither did. `get_solution_component_by_guid` turned out **not**
to share this bug — it already routes through the (now-also-fixed)
`_async_get_guid_request` shared helper, so it correctly forwards both
parameters; verified live the same way (`graph_query_depth=8`/
`max_mermaid_node_count=66` both reached the wire) before ruling it out.

`pytest tests/ -m unit -q` passes (exit 0) after all changes.

**Original status:** open at the pyegeria-default level (the user is raising the
shared default from 5 to 10 separately); worked around explicitly in
egeria-workspaces-fs across all detail-view call sites that render a
mermaid diagram — `isc_handler.py`, `mermaid_handler.py`,
`solution_architect_handler.py`, `tech_catalog_handler.py`,
`digital_products_handler.py`, `action_center_handler.py`,
`actor_handler.py`, `community_handler.py`, `context_events_handler.py`,
`data_design_handler.py`, `external_links_handler.py`,
`glossary_handler.py`, `governance_definitions_handler.py`,
`lineage_handler.py` (asset graph only, see ISSUE-24 for the lineage
graph endpoint), `location_handler.py`, `perspectives_handler.py`,
`reference_data_handler.py` — found 2026-08-04 investigating a report
that Egeria Explorer's Information Supply Chain view wasn't rendering the
full chain. `audit_handler.py`'s two `get_element_by_guid` calls are
deliberately left at `graphQueryDepth: 0` (a lightweight side-panel
lookup with no relationship traversal, so no mermaid graph is generated
there anyway) and `notelog_handler.py` doesn't render mermaid fields —
both confirmed not affected, not just skipped.

**Two distinct fix shapes were needed depending on the call site**,
learned the hard way after an initial fix silently didn't work:
- If the portal handler passes **no** `body=` argument (stays `None`),
  a `max_mermaid_node_count=250` kwarg on the outer call correctly
  threads through — every `_by_guid`/`find_*` wrapper method in pyegeria
  follows the same `params.update(kwargs); ...; **params` idiom that
  forwards it into the shared helper's own `max_mermaid_node_count`
  parameter.
- If the portal handler already builds an explicit `body={"class":
  "GetRequestBody", ...}` dict (common wherever `as_of_time` needs to be
  conditionally added), `_async_get_guid_request`/`_async_find_request`
  validate that body **as-is** and silently ignore the sibling
  `max_mermaid_node_count`/`graph_query_depth` kwargs entirely — the
  field must be embedded directly in the body dict
  (`"maxMermaidNodeCount": 250`) instead.
- A third shape: `get_solution_blueprint_by_guid`/
  `get_solution_component_by_guid` hit dedicated `.../retrieve` REST
  endpoints whose own `graph_query_depth` **parameter is dead** — never
  reaches the request at all, body or no body. Passing an explicit
  `AnyTimeRequestBody` with `graphQueryDepth`/`maxMermaidNodeCount` set
  is the only way to raise it (verified live: 74 → 187 mermaid lines).
  **Update 2026-08-04:** `get_info_supply_chain_by_guid`/
  `get_solution_role_by_guid` have the identical shape — see ISSUE-26.

**Layer:** Pyegeria (`pyegeria/core/_server_client.py`).

**What:** `_async_find_request`, `_async_get_name_request`, and
`_async_get_guid_request` — the three shared helpers behind essentially
every `find_*`/`get_*_by_guid` OMVS method — all declare
`max_mermaid_node_count: int = 5`, which gets sent to the server as
`maxMermaidNodeCount` in the request body. The server caps the generated
mermaid flowchart at that many nodes. 5 is far too small for any real
graph with more than a handful of related elements — a value seemingly
picked as a lightweight default for broad/unbounded listings, not for a
"show me everything about one element" detail view, but it applies
identically to both.

**Where seen:** live repro against a Coco Pharmaceuticals demo server —
`SolutionArchitect.find_information_supply_chains("Open Metadata Highway
Information Supply Chain")`'s `mermaidGraph` field was 165 lines at the
default `max_mermaid_node_count=5`, vs. 619 lines at `250` (graph actually
complete at that point — verified by also trying `50`/`100`, no further
growth past ~200). `graph_query_depth` (default 3), by contrast, made no
measurable difference for any information supply chain tested (1 through
10) — the node-count cap, not query depth, is the actual bottleneck for
mermaid graph completeness. Every OMVS wrapper method that calls one of
these three shared helpers (`find_information_supply_chains`,
`get_element_by_guid`, `find_solution_blueprints`,
`find_solution_components`, `get_solution_component_by_guid`, etc.)
inherits the same 5-node cap unless the caller explicitly overrides it —
confirmed via grep that essentially none of egeria-workspaces-fs's
`PyegeriaWebHandler` handlers do (`isc_handler.py`, now fixed;
`solution_architect_handler.py`, `tech_catalog_handler.py`,
`mermaid_handler.py`, `digital_products_handler.py`, `audit_handler.py`
all still rely on the pyegeria default).

**Candidate fix (still open):** raise the shared `max_mermaid_node_count`
default itself (planned separately by the repo owner, 5 → 10) — the
per-handler overrides above are generous enough (250) that they don't
depend on that change, but the two "dead parameter" methods
(`get_solution_blueprint_by_guid`/`get_solution_component_by_guid`) would
benefit from an actual fix to thread `graph_query_depth`/
`max_mermaid_node_count` into their request the same way every other
`_by_guid` method does, rather than requiring callers to know the
`AnyTimeRequestBody` workaround.

---

### ISSUE-24: `AssetCatalog._async_get_asset_lineage_graph_by_guid` hardcodes `queryGraphDepth: 5` with no override parameter at all

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/asset_catalog.py`).
Turned out to be worse than "no override" — checked the real
`AssetLineageGraphRequestBody` Java class (`-> QueryOptions -> GetOptions`)
and the field pyegeria was sending, `"queryGraphDepth"`, **doesn't exist on
the real body at all**; the actual field is `"graphQueryDepth"`. So the
hardcoded `5` was always silently dropped by the server regardless — the
server's own default (also 5, coincidentally) was what actually applied
the whole time, even before this fix. Found the same problem one field
over: `"relationshipTypes"` isn't real either — the actual field,
`GetOptions.includeOnlyRelationships`, means that caller-supplied
relationship-type filter has also never worked. Fixed both field names,
added `graph_query_depth`/`max_mermaid_node_count` parameters (the real
`GetOptions.maxMermaidNodeCount` field was never sent at all before) to
all three call layers (`_async_get_asset_lineage_graph_by_guid`,
`get_asset_lineage_graph_by_guid`, `get_asset_lineage_mermaid_graph`).

**Verified live**: created a real throwaway asset, spied on the outgoing
request body, and confirmed `graph_query_depth=7`/`max_mermaid_node_count=42`
now actually appear in the POST body as `graphQueryDepth`/
`maxMermaidNodeCount` and the server accepts the call successfully.
`pytest tests/ -m unit` passes.

**Original status:** open, found 2026-08-04 alongside ISSUE-23 while auditing
`egeria-workspaces-fs/.../lineage_handler.py`'s mermaid-graph call sites.

**Layer:** Pyegeria (`pyegeria/omvs/asset_catalog.py`).

**What:** unlike every other `_by_guid` method in this codebase,
`_async_get_asset_lineage_graph_by_guid` builds its `AssetLineageGraphRequestBody`
manually with `"queryGraphDepth": 5` hardcoded, and does not spread
`**kwargs` into that body at all — the method's own `**kwargs` parameter
exists but is never used. There is currently no way to override this from
a caller, unlike `get_asset_graph_by_guid` (a different, sibling method on
the same class going through `_async_get_results_body_request`, which
**does** correctly forward a `max_mermaid_node_count` kwarg — confirmed
and fixed in `lineage_handler.py`'s `get_asset_graph` route this session).

**Where seen:** `egeria-workspaces-fs/compose-configs/*/PyegeriaWebHandler/lineage_handler.py`'s
`get_asset_lineage_graph` route (`/api/lineage/asset/{guid}/lineage-graph`)
— serves `mermaidGraph`/`fullLineageMermaidGraph`/`edgeMermaidGraph` for
the lineage explorer's full end-to-end diagram, exactly the kind of view
most likely to need a depth greater than 5 for a long pipeline. Left
unmodified in the portal since there's no parameter to pass.

**Candidate fix:** add `graph_query_depth`/`max_mermaid_node_count`
parameters to `_async_get_asset_lineage_graph_by_guid`/
`get_asset_lineage_graph_by_guid`, threading them into
`queryGraphDepth`/a new `maxMermaidNodeCount` body field (need to confirm
the server actually honors a `maxMermaidNodeCount` field on
`AssetLineageGraphRequestBody` specifically — this body class differs
from the more common `GetRequestBody`/`ResultsRequestBody` shapes seen
elsewhere in this file).

---

### ISSUE-27: ~50 more sync methods delegate to their async counterpart with an all-positional argument list — unaudited for the same scrambling bug as ISSUE-21/25

**Status:** fixed 2026-08-15 (Pyegeria). Full audit via a script (not manual
grepping): every multi-line all-positional `self._async_*(...)` delegation
across `pyegeria/omvs/*.py` (62 sites, dominated by
`classification_explorer.py`), plus every single-line all-positional call
with 3+ bare-identifier args (285 more candidates), each cross-checked
against its target async method's *actual* parameter order (careful to use
the target's **last** definition in the file, matching Python's real
same-name-method resolution — one earlier false lead came from a stale,
fully-shadowed duplicate `_async_delete_solution_blueprint` definition still
sitting in `solution_architect.py`, dead code but harmless since it's never
reachable).

Of ~350 candidate sites, found and fixed **4 real bugs**, all in
`pyegeria/omvs/governance_officer.py` and `pyegeria/omvs/solution_architect.py`
(the rest were either exact matches or "different local variable name, same
value, same position" false positives — e.g. `add_term_to_folder(folder_guid,
term_guid, body)` calling `_async_add_to_collection(folder_guid, term_guid,
body)` against a target expecting `(collection_guid, element_guid, body)` —
positionally correct, just domain-specific local names):

1. **`solution_architect.py`: `delete_solution_role`** — sync wrapper's own
   signature is `(guid, body=None, cascade_delete=False)` (correct order,
   matching the async target), but it called
   `self._async_delete_solution_role(guid, cascade_delete, body)` —
   transposed, sending the boolean into the `body` slot and the body dict
   into the `cascade_delete` slot. Fixed to
   `self._async_delete_solution_role(guid, body, cascade_delete)`.

2. **`governance_officer.py`: `add_regulator_to_regulation`** — called the
   **wrong async method entirely**: `self._async_link_governance_results(...)`
   (a copy-paste leftover — a completely different relationship, hitting
   `governance-metrics/{gov_metric_guid}/measurements/{data_asset_guid}/attach`
   with `GovernanceResultsProperties`) instead of the correct
   `self._async_add_regulator_to_regulation(...)`. Fixed the call target.

3. **`governance_officer.py`: `_async_add_regulator_to_regulation`/
   `_async_detach_regulator_from_regulation`** — found while fixing #2: both
   built the wrong URL (`.../{url_marker}/governance-officer/regulations/...`
   — `self.url_marker` is itself `"governance-officer"`, so this duplicated
   the segment; ground truth per `Egeria-api-governance-officer.http` is
   `.../governance-officer/regulations/{regulationGUID}/regulators/organizations/{regulatorGUID}/attach`,
   single segment) and the attach method also used the wrong properties
   class (`"GovernanceResultsProperties"` instead of `"RegulatorProperties"`,
   also confirmed against the `.http` file). Fixed both URLs and the
   properties class.

4. **`governance_officer.py`: `detach_governance_results`** — sync wrapper
   passed `data_asset_guid` **twice**:
   `self._async_detach_governance_results(gov_metric_guid, data_asset_guid,
   data_asset_guid, body)` against a 3-parameter target
   `(gov_metric_guid, data_asset_guid, body)` — the extra positional arg
   landed in the `body` slot, and the real `body` argument was silently
   dropped (extra arg beyond the target's parameter count). Fixed by
   removing the duplicate.

**Verified live** against `qs-view-server`: `delete_solution_role`'s fix
confirmed via a request-body spy (cascade/body no longer transposed);
`add_regulator_to_regulation`/`detach_regulator_from_regulation` verified
fully end-to-end — created a throwaway `Regulation` + `Organization`,
linked via the fixed method, confirmed via `.http`-matching URL/body,
detached, cleaned up. `detach_governance_results`'s fix confirmed via a
request-body spy showing the correct 2-argument call now reaches
`_async_delete_relationship_request` cleanly.

**Found as a byproduct, NOT part of this issue's scope, tracked separately:**
attempting to live-verify `_async_link_governance_results` (unrelated,
untouched method) surfaced a real server-side/endpoint-design bug — see
ISSUE-57.

`pytest tests/ -m unit -q` passes (exit 0).

**Original status:** open, found 2026-08-04 as a byproduct of the ISSUE-25 sentinel
audit.

**Layer:** Pyegeria (`classification_explorer.py`, `runtime_manager.py`,
`project_manager.py`, `automated_curation.py`, `glossary_manager.py`).

**What:** grep for `self\._async_\w+\(\s*\n(?:\s+\w+,?\s*\n)+\s*\)` (a
multi-line, all-positional call with no `=`, `*`, or `**` on any line) in
`pyegeria/omvs/*.py` turns up ~50 more call sites, mostly write/action
methods (set/clear classification, add/remove relationship) that don't
carry `graph_query_depth` — so ISSUE-25's sentinel-injection method (which
specifically hunted for that one parameter) couldn't confirm or rule them
out. ISSUE-21 and ISSUE-25's `find_root_elements` finding both prove this
call shape is a real, recurring risk in this codebase whenever a
delegate's parameter order doesn't exactly match the caller's.

**Candidate fix:** for each of the ~50 call sites, diff the caller's
positional argument order against the target method's actual parameter
order (the same manual check done for `find_root_elements` in ISSUE-25)
and convert to keyword arguments wherever they've drifted. Not attempted
here — flagged for a dedicated follow-up pass.

---

### ISSUE-31: `MetadataExpert.delete_metadata_element` crashes with `AttributeError: 'NoneType' object has no attribute 'model_dump'` when called with no explicit body

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/core/_server_client.py`).
`validate_open_metadata_delete_request` now builds a default
`{"class": "OpenMetadataDeleteRequestBody"}` when `body` is `None`,
matching `validate_delete_element_request`'s existing pattern, instead of
returning `None` straight into `.model_dump()`. Verified live:
`client.metadata_expert.delete_metadata_element(<guid>)` with no body now
raises a clean `PyegeriaNotFoundException` for a nonexistent GUID instead
of crashing with `AttributeError`. Fixes the wider blast radius too, since
every other caller of the shared `_async_open_metadata_delete_body_request`
helper goes through this same validator.

**Original status:** open, found 2026-08-04/05 while cleaning up throwaway test
elements created during the ISSUE-32 (`Note` type) live verification.

**Layer:** Pyegeria (`pyegeria/core/_server_client.py`).

**What:** `_async_open_metadata_delete_body_request(url, body=None)` calls
`self.validate_open_metadata_delete_request(body)` and immediately calls
`.model_dump(...)` on the result — but `validate_open_metadata_delete_request`
returns `None` (not a default `OpenMetadataDeleteRequestBody()` instance)
when `body` is `None`, so the very next line always crashes for the common
"just delete it, no special options" case:

```python
from pyegeria import EgeriaTech
client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="erinoverview")
client.create_egeria_bearer_token("erinoverview", "secret")
client.metadata_expert.delete_metadata_element("<any-guid>")
# AttributeError: 'NoneType' object has no attribute 'model_dump'
```

**Workaround (used during this investigation):** always pass an explicit
`body={"class": "OpenMetadataDeleteRequestBody"}` — works correctly once a
non-`None` body is supplied.

**Candidate fix:** `validate_open_metadata_delete_request` should construct
and return a default `OpenMetadataDeleteRequestBody()` when `body is None`,
matching the pattern every other `validate_*_request` helper in this file
uses (they all handle the "no body given" case by building sensible
defaults, not returning `None`). Not attempted here — found in passing,
outside the scope of the `Note` type work that surfaced it.

**Confirmed wider blast radius (2026-08-09):** this isn't specific to
`delete_metadata_element` — `_async_open_metadata_delete_body_request` is a
shared base-class helper, so every caller with an optional/default-`None`
body hits the same crash. Reproduced live via the new
`CollectionManager._async_detach_saved_query_from_results_set` (added for
Egeria PR #9200's SmartQuery relationship, which itself calls
`_async_open_metadata_delete_body_request` the same way
`MetadataExpert._async_delete_related_elements` does) — worked around
locally in that method the same way (`body or {"class":
"OpenMetadataDeleteRequestBody"}`), rather than waiting on this issue.
Any other no-args delete-style call sharing this helper (grep
`_async_open_metadata_delete_body_request` for the full caller list) is
suspect until the base helper itself is fixed.

---

### ISSUE-30: `updateNote` REST operation (`POST .../feedback-manager/notes/{noteGUID}`) returns 404 on a live server, despite matching the documented `.http` ground truth exactly

**Status:** still open (Egeria Server), re-confirmed 2026-08-15 against the
current `qs-view-server` (post the environment restart noted in ISSUE-52) —
not just a stale finding from the original redeploy. Re-ran the full
repro end-to-end via pyegeria itself this time (not just raw `curl`):
created a throwaway `DataStructure`, attached a `NoteLog`, created a `Note`
on it — all three succeeded — then `_async_update_note` on the real note
GUID still 404s with the identical shape (`CLIENT_ERROR_400`/HTTP 404 at
`.../feedback-manager/notes/{noteGUID}`). Test elements cleaned up
(cascade-deleting the anchor `DataStructure` also removed the attached
`NoteLog`/`Note`, confirmed via a follow-up GUID lookup on all three).
Nothing changed client-side — still not fixable in pyegeria; genuinely
looks like an unregistered/unshipped endpoint on this server build.

**Original status:** open (Egeria Server), found 2026-08-05 while live-verifying the
ISSUE-32 `Note` type fix end-to-end (create worked; update did not).

**Layer:** Egeria Server — not fixable in pyegeria. `_async_update_note`'s
URL (`{command_root}feedback-manager/notes/{note_guid}`) was double-checked
against `Egeria-api-feedback-manager.http`'s `@name updateNote` worked
example and matches it exactly, method and body shape included; this isn't
a pyegeria URL-construction bug.

**What:** confirmed via both pyegeria and a raw `curl` (bypassing pyegeria
entirely) against a freshly-created, real `Note` element on `qs-view-server`
— both get a bare HTTP 404 with no Egeria FFDC error body, just a generic
Spring "Not Found" response, meaning the operation doesn't appear to be
routed/registered on this server at all:

```bash
curl -sk -X POST "https://localhost:9443/servers/qs-view-server/api/open-metadata/feedback-manager/notes/<real-note-guid>" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"class":"UpdateElementRequestBody","mergeUpdate":true,"properties":{"class":"NoteProperties","typeName":"Note","displayName":"x"}}'
# {"timestamp":"...","status":404,"error":"Not Found","path":"/servers/qs-view-server/api/open-metadata/feedback-manager/notes/<guid>"}
```

**Impact:** `update_note`/`_async_update_note` cannot be verified working
end-to-end on this server today — create + fetch both work correctly
(confirmed live, see ISSUE-32), but update is blocked. Not related to the
`Note` type change itself (same 404 shape would occur regardless of
`typeName`) — looks like a genuine gap in this endpoint's registration on
the current server build.

**Candidate fix:** none client-side. Worth confirming against a different/
newer Egeria server build whether this is a temporary gap in the specific
redeploy used for this session, or a real, currently-unreleased endpoint.

---

### ISSUE-45: `tests/functional-tests/test_my_profile.py::test_create_my_todo` has no teardown — leaves a live ToDo behind on every run

**Re-verified 2026-08-15 (same day, follow-up run), no regression.**
Re-ran the test directly (`PYEG_LIVE_EGERIA=1 pytest
tests/functional-tests/test_my_profile.py::TestMyProfile::test_create_my_todo
-v`) — passes, prints its own "Deleted test to-do <guid>" confirmation, and
a direct `get_metadata_element_by_guid` on that exact GUID immediately
afterward correctly raises `PyegeriaNotFoundException` — genuinely gone
server-side, not just claimed by the test's own output.

**Status:** fixed 2026-08-15 (test hygiene —
`tests/functional-tests/test_my_profile.py`). Added a `finally` block that
deletes the created `ToDo` via a `MetadataExpert` client
(`delete_metadata_element(guid, body={"class":
"OpenMetadataDeleteRequestBody"})`), matching the candidate fix below.
Verified live: ran the test, confirmed the `ToDo` was created (real GUID
returned), then confirmed via a direct `get_metadata_element_by_guid` call
immediately after the test run that the same GUID is now soft-deleted
(`OMRS-REPOSITORY-404-013`). `pytest tests/ -m unit` passes.

**Original status:** open (test hygiene) — found 2026-08-05 while investigating
ISSUE-44's follow-up. Running the test suite against the live
`qs-view-server` created a real `ToDo` (`do-my-backup`, confirmed via
`find_metadata_elements(metadataElementTypeName="ToDo")` immediately after a
test run, `createTime` matching the run) that isn't deleted afterward. Over
repeated test runs this silently accumulates orphaned `ToDo` entities on
whatever server the suite is pointed at. Same class of issue as the
already-known pattern in this file of "confirm via live GUID, then clean up
afterward" — this test doesn't do the second half.

**Candidate fix:** add a fixture/teardown that deletes the created GUID via
`MetadataExpert.delete_metadata_element(guid, body={"class":
"OpenMetadataDeleteRequestBody"})`, matching the pattern used everywhere else
in this file's own verification steps.

---

### ISSUE-46: `logger.info(self.__str__(), ip=..., http_code=..., pyegeria_code=...)` crashed with `KeyError` on any exception whose message contained literal `{}` — masked the real error behind an opaque traceback across 5 of 7 exception classes

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/core/_exceptions.py`). Found
while investigating the user's report that "many CLI scripts under
`/commands` are broken" — the first repro (`create_todo` CLI) crashed not
with a clean Egeria error but with a bare `KeyError: '\`parameterName\`'`.

**Root cause:** loguru's `Logger.info(message, *args, **kwargs)` always calls
`message.format(*args, **kwargs)` when any args/kwargs are given (this is
loguru's structured-logging feature — `logger.info("Processing {file}",
file=name)`). `PyegeriaException.__str__()` embeds `additional_info` values
(e.g. `exceptionProperties`) via `str(value).replace('"','\`').replace("'",
'\`')`, which preserves any literal `{`/`}` characters already present in a
dict repr (e.g. `` `{`parameterName`: `elementGUID`}` ``). Six call sites
across five exception classes did `logger.info(self.__str__(), ip=...,
http_code=..., pyegeria_code=...)` — passing that literal-brace string as
the format string. Whenever the underlying Egeria error included any
`exceptionProperties` (common - it's present on most `InvalidParameterException`
translations), `.format()` tried to resolve `parameterName` as a kwarg,
found only `ip`/`http_code`/`pyegeria_code`, and raised `KeyError` from
*inside the exception's own constructor* - so the caller never even got a
`PyegeriaException` to catch; it got a raw `KeyError` traceback instead.

**Not a new regression** - `PyegeriaAPIException.__init__` (the class
actually raised for real Egeria error responses) already had the fix,
complete with an explanatory comment: `msg.replace("{", "{{").replace("}",
"}}")`. But the identical `logger.info(self.__str__(), ...)` pattern in
`PyegeriaInvalidParameterException`, `PyegeriaClientException`,
`PyegeriaUnauthorizedException`, `PyegeriaNotFoundException`, and
`PyegeriaUnknownException` never got the same treatment - so any 404, 401,
or invalid-parameter response with a curly-brace-shaped error message
crashed instead of printing.

**Fix:** applied the same `.replace("{", "{{").replace("}", "}}")` escaping
to all five remaining call sites.

**Verified live:** re-ran `create_todo --name ... --description ...` (no
`--assigned-to`, so the CLI's stale hardcoded `peter_guid` default 404s) -
before the fix this crashed with `KeyError: '\`parameterName\`'`; after the
fix it prints a clean, readable Egeria error message via
`print_basic_exception` with no traceback. `tests/micro-tests` clean (same
one pre-existing unrelated failure).

---

### ISSUE-47: CLI scan of `/commands` (triggered by ISSUE-44's `create_todo` follow-up) - several genuine breakages found and fixed, 8 stale `pyproject.toml` entries removed

**Status:** fixed 2026-08-05. User reported "many of my cli
scripts/commands (under the /commands folder) are broken - probably due to
the change in signatures" and asked for a scan. Ran a static AST pass over
all ~337 `client.<method>(...)` calls across every file in `commands/`
cross-referenced against every real method signature in
`pyegeria/omvs/*.py` + `_server_client.py` + `egeria_tech_client.py`
(2131 unique callable names), plus an import/`--help`-level smoke test of
all 106 `pyproject.toml` console-script entry points.

**Confirmed NOT caused by today's `my_profile.py`/`find_metadata_elements`
signature changes** - the static AST cross-reference found zero calls
incompatible with every registered overload of the method name they use;
nothing in `commands/` calls `find_metadata_elements` directly at all.

**Genuine bugs found and fixed:**
1. `commands/tech/element_actions.py`'s `delete-element` called
   `m_client.delete_metadata_element_in_store(guid, cascade=cascade)` - that
   method never existed anywhere in pyegeria, and the real
   `delete_metadata_element(metadata_element_guid, body)` has no `cascade`
   concept at all (`OpenMetadataDeleteRequestBody` has no such field).
   Fixed to call the real method with a bare `OpenMetadataDeleteRequestBody`.
2. `commands/cat/list_assets.py`'s `display_assets()` had a literal duplicate
   parameter - `timeout: int = 60,` immediately followed by `timeout: int =
   None,` - a guaranteed `SyntaxError` that made the module (and therefore
   anything importing from it, including the top-level `hey_egeria` CLI
   group) fail to import at all. Fixed by removing the dead second
   declaration.
3. `commands/cli/egeria_ops.py` (`hey_egeria_ops`) referenced `settings` at
   module level (`app_settings = settings`) without ever importing it -
   `NameError` at import time, so the whole `hey_egeria_ops` CLI group was
   unusable. Fixed by adding `from pyegeria.core.config import settings`
   (the same import every sibling command file uses).
4. Two 1-line `pyproject.toml` entry-point typos, both trivial renames now
   corrected: `generate_md_cmd_templates` pointed at the (nonexistent)
   module `commands.tech.generate_md_cmd_template` (missing trailing "s");
   `delete_element` pointed at the (nonexistent, long-deleted per `git log`)
   module `commands.tech.generic_actions` instead of the real
   `commands.tech.element_actions`.

**Also found: 6 stale hardcoded GUIDs in `commands/my/todo_actions.py`**
(`peter_guid`/`tanya_guid`/`erins_guid`, used as CLI option defaults) that no
longer exist on the current `qs-view-server` - confirmed live (a `create-todo`
run with no `--assigned-to` 404s: `OMAG-REPOSITORY-HANDLER-404-007 ...
59f0232c-f834-4365-8e06-83695d238d2d ... not found`). Not fixed here (no
single correct replacement GUID - depends on which demo actors exist on
whatever server the CLI is pointed at); flagging so the defaults aren't
mistaken for real, working values.

**5. Removed 8 stale `pyproject.toml` entries pointing at genuinely removed
code** (confirmed via `git log --all` that these files existed and were
deleted/renamed at various points; not silently re-implemented, just
removed so `uv sync`/`pip install` no longer advertises commands guaranteed
to fail):
- `create_category`/`update_category`/`delete_category`/
  `add_term_to_category`/`remove_term_from_category` → pointed at
  `commands.cat.glossary_actions`, which has never (as far as current source
  shows) defined any of these five functions - only glossary/term-level
  commands remain in that file today. Restoring category-management is a
  separate feature task, not a re-add of these entries.
- `load_archive_tui` → `commands.ops.load_archive:tui` - no `tui` function
  exists in that module (only `load_archive`).
- `run_report_orig`, `list_todos`, `list_categories`, `monitor_coco_status`,
  `monitor_server_list` (→ `commands.ops.orig_monitor_server_list`) - all
  five point at files that no longer exist.
- `start_daemon`/`stop_daemon` → `commands.ops.engine_actions` - file no
  longer exists; equivalent functionality lives on today as
  `hey_egeria_ops start`/`hey_egeria_ops stop`
  (`gov_server_actions.py`'s `start_server`/`stop_server` - those are click
  subcommands taking a `@click.pass_context` config object, not standalone
  entry points, so this isn't a 1:1 script rename).

**Verified after fixes:** `uv sync --extra spec-editor` (needed to
regenerate the installed console-script wrappers after the `pyproject.toml`
corrections) then a full re-scan of all entry points: **0 of 93 remaining
entries fail to import** (down from 18 of 106 failing at the start of this
investigation - the 13-entry gap between 106 and 93 is the 8 removed plus a
handful the smoke-test script itself double-counted across duplicated
`[project.scripts]` table keys). `tests/micro-tests` clean throughout (same
one pre-existing unrelated failure). Also added
`tests/scenario-tests/test_todo_scenarios.py`, a full-lifecycle regression
suite (Create → verify relationships → verify visibility → Dr.Egeria
reporting → reassign/update → Delete) for ToDo/Meeting/Review that asserts
real failures rather than swallowing them - written specifically to catch a
regression on ISSUE-44's three bugs.

---

## Dr.Egeria / compact-spec design gap

### ISSUE-22: `Ownership`/`Impact`/`Confidence`/`Confidentiality`/`Criticality` classification `status` field expects an int enum, not the free-text value the Dr.Egeria "Status" attribute style implies

**Status:** fixed 2026-08-15. `Ownership` was never actually affected — its
`ClassificationSpec` uses its own explicit field map (`owner`/
`ownerTypeName`/`ownerPropertyName`), not `_GOVERNANCE_SHARED_FIELDS`, so
the issue title overstated its scope; `Retention` *is* affected (it also
consumes `_GOVERNANCE_SHARED_FIELDS`) and is fixed by the same change as
`Impact`/`Confidence`/`Confidentiality`/`Criticality`.

Two separate bugs were involved:
1. **Attribute-definition gap.** Between this issue being filed and now,
   the compact-spec attribute had already been renamed `Status` →
   `Governance Status` and migrated to `style: "Valid Value"` — but with no
   explicit `property_name`, so it auto-derived to `governanceStatus` (a
   property that doesn't exist), causing the live valid-metadata-value
   lookup to silently return empty and fall through to a stale ALL-CAPS
   fallback list, passing through an un-converted string. Fixed via the
   Spec Editor API: `Governance Status` now has `property_name:
   "statusIdentifier"` and `valid_values` = `["Discovered", "Proposed",
   "Imported", "Validated", "Deprecated", "Obsolete", "Other"]`, matching
   `GovernanceClassificationStatus`.
2. **Wire-key mapping bug**, in `md_processing/v2/curation.py`:
   `_GOVERNANCE_SHARED_FIELDS` mapped `"Governance Status"` to the outgoing
   JSON key `"status"`, but the real field on `ImpactProperties`/
   `ConfidenceProperties`/`ConfidentialityProperties`/`CriticalityProperties`/
   `RetentionClassificationProperties` is `statusIdentifier` — `"status"` is
   silently ignored by the server (confirmed live: sending `"status": 4`
   left readback `statusIdentifier: "0"`; sending `"statusIdentifier": 4`
   directly persisted correctly). Fixed: `_GOVERNANCE_SHARED_FIELDS =
   {"Governance Status": "statusIdentifier", ...}`.

Verified end-to-end through the real Dr.Egeria pipeline (not just manual
body construction): `Create Data Structure` + `Classify Impact` with
`Governance Status: Validated`, `Level Identifier: 2`, `Steward:
test-steward` — both commands SUCCESS, and a direct element fetch afterward
showed `statusIdentifier: 3` (the correct ordinal for `Validated`) alongside
`severityLevel: 2` and `steward: "test-steward"`. Test element deleted
afterward. `pytest tests/ -m unit -q` passes (exit 0).

**Original status:** open, found 2026-08-03 during a live smoke test of `Classify
Impact` (Curation family).

**Layer:** Not strictly a pyegeria bug — a Dr.Egeria compact-spec design
gap (`md_processing/data/compact_commands/commands_curation_compact.json`,
`Status` attribute, style `Simple`) combined with `curation.py`'s field
mapping (`_GOVERNANCE_SHARED_FIELDS = {"Status": "status", ...}`).

**What:** `ImpactProperties`/etc.'s real `status` field is an integer
`GovernanceClassificationStatus` enum ordinal (per
`Egeria-api-classification-explorer.http`'s worked example: `"status" : 0`),
not a free-text string. Passing `"ACTIVE"` (a plausible-looking value given
the attribute's `Simple` style) doesn't error — it's silently dropped by
the server, and the classification's `statusIdentifier` (the field's
readback name) stays at its default `0`.

**Where seen:** live repro — `Classify Impact` with `Status: ACTIVE`,
`Level Identifier: 2`, `Steward`/`Source`/`Description` set. Fetching the
classified element back showed `severityLevel: "2"`, `steward`, `source`,
`notes` all correct, but `statusIdentifier: "0"` regardless of the `Status`
value sent — confirms `status` never took effect as text.

**Candidate fix:** change the `Status` attribute's style to `Valid Value`/
`Enum` with the real `GovernanceClassificationStatus` ordinal labels (needs
confirming the exact enum from the Egeria type system rather than guessing
further), authored in Tinderbox per the usual compact-spec workflow — not
attempted here, since it's a spec authoring change, not a Curation
processor-wiring bug. Doesn't block Impact/Confidence/etc. classification
overall — `severityLevel`, `steward`, `source`, `notes` all confirmed
working correctly.

---

## Egeria Server — not fixable in pyegeria

### ISSUE-57: `GovernanceResults` relationship rejects the exact end1/end2 GUID order the `.http` ground truth and pyegeria's URL both use

**Status:** open, found 2026-08-15 as a byproduct of live-verifying the
ISSUE-27 fix (`detach_governance_results`'s duplicate-argument bug).

**Layer:** Egeria Server (type definition or the governance-officer view
service's endpoint handler), not pyegeria — pyegeria's request exactly
matches `Egeria-api-governance-officer.http`'s `linkGovernanceResults`
worked example (URL, body, and `GovernanceResultsProperties` class all
byte-for-byte identical), so there's nothing to fix on the client side.

**What:** calling `GovernanceOfficer._async_link_governance_results(
governance_metric_guid, data_asset_guid)` — which builds
`POST .../governance-metrics/{governanceMetricGUID}/measurements/{dataAssetGUID}/attach`,
matching the `.http` file exactly — fails with a 500:

```
OMRS-REPOSITORY-400-047 A addRelationship request has been made ... for a
relationship that has one or more ends of the wrong or invalid type.
Relationship type is GovernanceResults; entity proxy <dataAssetGUID> for
end 1 is of type DataSet rather than GovernanceMetric and entity proxy
<governanceMetricGUID> for end 2 is of type GovernanceMetric rather than Asset
```

The server assigned end1 to the *second* URL path GUID (the data asset) and
end2 to the *first* (the governance metric) — the reverse of what the
`GovernanceResults` relationship type (end1=GovernanceMetric, end2=Asset)
and the URL's own naming (`governance-metrics/{...}/measurements/{...}`)
both imply. Reproduced live against `qs-view-server`: created a throwaway
`GovernanceMetric` + `DataSet` asset, confirmed the 500, cleaned up both
elements afterward.

**Candidate fix:** none on the pyegeria side — either the
`governance-officer` view service's endpoint handler has end1/end2
swapped internally, or the `GovernanceResults` relationship's own type
definition has end1/end2 the other way round from what the URL segment
order and `.http` documentation suggest. Needs investigation against the
Egeria server/type-system source, not pyegeria.

---

### ISSUE-52: `qs-nanny-daemon`/`qs-integration-daemon`'s own connectors generate sustained, heavy background write load against the shared repository — starves interactive requests, plausible cause of "frequent Postgres checkpoints"

**Status:** open (Egeria server / deployment config), found 2026-08-15 (Dan)
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

### ISSUE-53: `findMetadataElements`'s `metadataElementSubtypeNames` is silently ignored — restricting to specific subtypes has no effect on results

**Status:** still open (Egeria server), re-confirmed 2026-08-15 against the
current, restarted `qs-view-server` — not a stale finding. Re-ran with a
raw body passed straight through `MetadataExpert.find_metadata_elements`
(bypassing any pyegeria body-construction logic, equivalent to the original
raw-`curl` repro): `metadataElementTypeName: "Referenceable"` with and
without `metadataElementSubtypeNames: ["GlossaryTerm"]` returned the
byte-identical type mix both times (`APIParameter`/`ConnectorActivityReport`/
`ContributionRecord`, 50/50 results) — the subtype filter still has zero
effect. Nothing changed client-side; still not fixable in pyegeria.

**Original status:** open (Egeria server), found 2026-08-05 investigating whether
Egeria Insights could express "elements that have a SemanticAssignment but
are NOT type Notification" via an allow-list of subtypes (`Referenceable`
+ `metadataElementSubtypeNames: ["GlossaryTerm", "DataAsset"]`, per
`Egeria-api-metadata-expert.http`'s worked "findMetadataElements (nested
condition)" example, which documents this field alongside
`metadataElementTypeName`).

**Layer:** Egeria Server — not fixable in pyegeria. Confirmed via a raw
`curl` bypassing pyegeria entirely (so this isn't a body-construction bug
on the client side):

```bash
curl -sk -X POST ".../metadata-expert/metadata-elements/by-search-conditions" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"class":"FindRequestBody","metadataElementTypeName":"Referenceable",
       "metadataElementSubtypeNames":["GlossaryTerm"],
       "limitResultsByStatus":["ACTIVE"],"graphQueryDepth":0,"startFrom":0,"pageSize":10}'
# returns ContributionRecord/EngineAction/NotificationType — NOT GlossaryTerm
```

**What:** `metadataElementSubtypeNames` is accepted (no error, HTTP 200)
but has **zero effect** on which elements come back — results are
byte-identical to the same query with the field omitted entirely.
Reproduced with two different base-type/subtype pairs to rule out a
one-off: `Referenceable` + `["GlossaryTerm"]`, `Referenceable` +
`["GlossaryTerm","DataAsset"]`, and `Asset` + `["DataAsset"]` — all three
returned the same type mix (`ContributionRecord`/`EngineAction`/
`Notification(Type)`) as the equivalent query with no subtype restriction
at all.

**Impact:** there is currently no way to narrow a `findMetadataElements`
query to a specific allow-list of subtypes under a common base type — the
only working filter is the single `metadataElementTypeName` (which
includes ALL subtypes of that type, with no way to exclude any of them).
This blocks the Egeria Insights use case that prompted the investigation:
excluding noisy `Action` subtypes (`Notification`/`ToDo`/`Meeting`/
`Review` — all real `Asset` subtypes, see ISSUE for the Explorer routing
fix on 2026-08-05) from a broader `Asset`/`Referenceable` search without
also losing every other subtype.

**Candidate fix:** none client-side. Worth confirming against a newer
Egeria server build whether this is a currently-unimplemented parameter
(present in the request body schema/`.http` docs but never wired up
server-side) versus a regression.

---

### ISSUE-54: `findMetadataElements` scoped to the universal base type `Referenceable` silently returns an incomplete, arbitrary subset instead of the true population

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
`metadataElementTypeName="Referenceable"` (the universal base type — every
open-metadata entity is a `Referenceable`) returns a small, arbitrary
subset instead of the true population, with no error, no truncation flag,
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
"safe, unscoped, find-everything" fallback the way its position at the
root of the type hierarchy implies — a caller that scopes a search this
broadly on purpose (not just as an accidental fallback) will silently miss
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

### ISSUE-14 (PY-4): `update_comment` demands `qualifiedName` even with `mergeUpdate: true`

**Status:** tracker was stale — re-checked 2026-08-15 and found the
workaround has actually been **in pyegeria itself** since 2026-08-03
(`92cde6a`), not "application code" as this entry previously said.
`_async_update_comment` (`pyegeria/core/_server_client.py`) already
auto-fetches the comment's current `qualifiedName` via
`_async_get_comment_by_guid` whenever the caller's body doesn't supply one,
and injects it before sending — the exact workaround this entry describes,
just already shipped and never reflected here. **Verified live**: created a
throwaway `DataStructure`, attached a comment via `add_comment_to_element`,
then called `update_comment(comment_guid, comment="edited text")` with no
`qualifiedName` in the body at all — succeeds cleanly (previously would
have hit `OMAG-METADATA-400-004`). Cleaned up the test element afterward.
Underlying server behavior (still demanding `qualifiedName` despite
`mergeUpdate: true`) is unchanged and still worth an upstream Egeria report,
but there is nothing left to do on the pyegeria side — every caller of
`update_comment`/`_async_update_comment` already gets the workaround for
free, no application-level workaround needed.

**Original status:** open (Egeria server) — workaround shipped in application code,
not a pyegeria fix. Passing `"mergeUpdate": true` should allow a partial
update (only supplied fields required), but the server still demands
`qualifiedName` regardless.

**Original workaround (superseded, no longer needed by callers):** fetch the
element first via `get_comment_by_guid`, extract `qualifiedName`, and always
include it in the update body regardless of `mergeUpdate`.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.update_comment(comment_guid="<guid>", body={"commentText": "edited text"})
# OMAG-METADATA-400-004 demanding qualifiedName even though mergeUpdate: true is set.
```

---

### ISSUE-17 (PY-13): `SpecificationProperties.get_specification_property_by_type` always returns 400

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/valid_metadata.py`).
**The original diagnosis was wrong** — not a server-side enum-binding drift.
Checked `Egeria-api-valid-metadata.http`'s `getSpecificationPropertyByType`
worked example: it uses `specificationPropertyType=PRODUCED_GUARD` —
`SCREAMING_SNAKE_CASE`, not the value shape the original repro tried
(`"SpecificationPropertyType{placeholderProperty}"`, nor the raw
PascalCase keys `get_specification_property_types()` returns, e.g.
`"ProducedGuard"`). Tried `PRODUCED_GUARD` directly — **succeeded
immediately**, no 400 at all. Root cause: `get_specification_property_types()`
returns its `stringMap` verbatim from the server's own
`specification-properties/type-names` endpoint, which genuinely uses
PascalCase keys (`"ProducedGuard"`) — a different server endpoint using a
different casing convention for the same enum than `by-type` expects. This
is a real cross-endpoint inconsistency in the server, but the client-visible
symptom ("every input 400s") was entirely avoidable: `get_specification_property_by_type`
did zero conversion, so the single most natural, discoverable input for a
caller (feeding it a key from `get_specification_property_types()`) always
failed.

**Fix:** `_async_get_specification_property_by_type` now auto-converts a
PascalCase/camelCase input to `SCREAMING_SNAKE_CASE` before building the URL
(a plain regex insert-underscore-before-each-capital + uppercase — no
hardcoded type list, so it isn't tied to today's enum values); an
already-`SCREAMING_SNAKE_CASE` value passes through untouched.

**Verified live** against `qs-view-server`: all 12 real specification
property types returned by `get_specification_property_types()`, fed
straight into `get_specification_property_by_type()` unmodified, now
resolve successfully (10 return real results, 2 correctly return "No
elements found" — no data of that type, not an error); the already-correct
`PRODUCED_GUARD` form still works unchanged. `pytest tests/ -m unit`
passes.

**Impact on the workaround downstream:** `find_specification_property("*",
...)` + client-side filtering is no longer necessary to work around this
specific method, though it may still be independently useful/faster for
some callers.

**Original status:** open (Egeria server), re-verified 2026-07-31 (live) — still
reproduces exactly as described. Root cause is server-side: the OpenAPI
schema declares `specificationPropertyType` as a required enum query param
with values like `"SpecificationPropertyType{placeholderProperty}"`, but
every form of that value (plain, enum-wrapped, percent-encoded) still 400s
— the Spring `@RequestParam` enum binding appears to have drifted from the
OpenAPI-declared enum. No pyegeria code change can fix a 400 the server
returns for every input.

**Original workaround (superseded, no longer needed for this method):** use
`find_specification_property("*", ...)` (by-search-string) instead, and
filter client-side on `element["properties"]["identifier"]` (camelCase form
of the type name).

```python
from pyegeria import SpecificationProperties
mgr = SpecificationProperties(view_server="qs-view-server", platform_url="https://localhost:9443",
                               user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
types = mgr.get_specification_property_types()
mgr.get_specification_property_by_type(list(types.keys())[0])
# Now succeeds -- was previously 400ing for every input, confirmed 2026-07-31.
```

---

### ISSUE-43: Pagination location for `find_metadata_elements`'s endpoint — audit finding, plausible but not yet confirmed live

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/runtime_manager.py`).
Resolved the "not yet empirically confirmed" `_async_get_server_templates_by_dep_impl_type`
finding via ground-truth comparison rather than waiting for 2+-page demo
data (the blocker noted below, still unavailable): checked
`Egeria-api-runtime-manager.http`'s `getServerTemplatesByDeployedImplementationType`
worked example — a plain `POST .../software-servers/by-deployed-implementation-type`
with **no query string at all**, pagination and the `Template` filter both
carried entirely in the `FilterRequestBody` (`includeOnlyClassifiedElements:
["Template"]`). The sibling, non-templates method in the same file
(`_async_get_servers_by_dep_impl_type`) already builds the URL with no query
string, confirming the correct pattern exists right next to the bug. Removed
the spurious `?startFrom={..}&pageSize={..}&getTemplates=true` suffix
entirely — none of those three query params exist on the real endpoint;
pagination was already being built correctly into the body by the shared
`_async_get_name_request` helper regardless (confirmed via a request-body
spy, before and after: `startFrom`/`pageSize` land in the body either way,
so the URL suffix was purely spurious/redundant, not silently required for
anything to work).

**Verified live:** the call now succeeds against `qs-view-server`
(`get_server_templates_by_dep_impl_type("cots-application-server", ...)` →
`No elements found`, same empty-but-successful result as before, for the
reason already documented below — no `Template`-classified software servers
of any tested type exist in this demo dataset, so a real 2+-page comparison
still isn't possible here). `pytest tests/ -m unit` passes.

**Original status:** open (pyegeria, suspected) — found 2026-08-05 while auditing
for the same drift class as ISSUE-34 (see that entry's "design principle"
paragraph — Egeria's pagination convention moved from URL query params to
request-body fields for at least one endpoint a few months ago; worth
checking any method still doing URL-based `startFrom`/`pageSize`
injection). Grepped `pyegeria/omvs/*.py` for the same
`?startFrom={..}&pageSize={..}` URL-construction shape ISSUE-34 had; found
2 more matches besides `metadata_expert.py` (already fixed there) —
`runtime_manager.py` and `valid_metadata.py`.

**`valid_metadata.py`'s `_async_get_valid_metadata_values`: checked, NOT a
bug.** This is a plain `GET` request (`get-valid-metadata-values/{property_name}`)
— there is no request body at all for a GET, so URL query parameters are
the only place `startFrom`/`pageSize` *can* go. Confirmed against the
`.http` ground truth (`Egeria-api-classification-explorer.http`) — also a
bare GET, no body shown. Correctly implemented as-is.

**`runtime_manager.py`'s `_async_get_server_templates_by_dep_impl_type`:
suspicious, not yet confirmed.** Line ~2612 unconditionally appends
`?startFrom={start_from}&pageSize={page_size}&getTemplates=true` to the URL
*regardless* of whether `start_from`/`page_size` are also meaningful via
the `body` path — and the shared helper it delegates to
(`ServerClient._async_get_name_request`) **already** builds a correct
`"startFrom"`/`"pageSize"` pair into the body it constructs when the
caller doesn't supply an explicit `body` (confirmed by reading
`_async_get_name_request`'s source directly, `_server_client.py` ~line
6493). So the URL suffix here is at best redundant with what the body path
already does correctly, and at worst sends conflicting information when a
caller supplies their own explicit `body` without `startFrom`/`pageSize`
set (in that case pagination could only come from the URL, which per
ISSUE-34's finding is exactly the convention that stopped working for a
sibling endpoint).

**Not yet empirically confirmed**, unlike ISSUE-34's `find_metadata_elements`
finding — this demo dataset doesn't have enough `Template`-classified
servers of the same `deployedImplementationType` to construct a real
2-page pagination test (tried `cots-application-server` — 5 total
`SoftwareServer`s of that type exist, but zero are `Template`-classified;
every filter value tested returned either 0 or 1 `Template`-classified
result, never 2+, so a same-content-vs-distinct-content comparison isn't
possible with this data). **Next step:** either seed enough demo data to
get a real 2+ result test, or read the Java source for this specific
endpoint the way ISSUE-15's `QueryBuilder` investigation did, rather than
guessing from the pattern match alone.

---

### ISSUE-38 (PY-18): `count_relationships_between_elements("Exception")` (276) disagrees with `ClassificationExplorer.get_relationships("Exception")` (55)

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

### ISSUE-39 (PY-19): `MetadataExpert.find_relationships_between_elements(relationshipTypeName=…)` returns "No elements found" even when the matching count is non-zero

**Status:** fixed 2026-08-15 (Pyegeria — `pyegeria/omvs/metadata_expert.py`).
**Reclassified from Egeria Server to Pyegeria** — the original diagnosis
was wrong; this was never a server-side gap. Same root cause as ISSUE-49
(read that entry for the full mechanism): the shared
`process_related_element_list()` helper's `relationship_list=True` branch
looked for the relationships under `elementList` instead of the real key,
`relationships`. `_async_find_relationships_between_elements` already
correctly passed `relationship_list=True`, so this method only ever hit
the second half of the bug — fixed by the same one-line change to the
shared helper, no call-site change needed here. Verified live: re-ran
`find_relationships_between_elements({"relationshipTypeName": "SmartQuery"})`
against a real, freshly-created `SmartQuery` relationship — now returns it
instead of "No elements found". `pytest tests/ -m unit` passes.

**Original status:** open (Egeria server) — found 2026-07-24 alongside ISSUE-38,
same environment. Consolidated in from `egeria-workspaces-fs/
PYEGERIA_ISSUES.md` 2026-08-05.

**How to trigger:**
```python
me.count_relationships_between_elements({"class":"FindRelationshipRequestBody","relationshipTypeName":"SemanticAssignment"})
# -> 397
me.find_relationships_between_elements({"class":"FindRelationshipRequestBody","relationshipTypeName":"SemanticAssignment"},
                                       start_from=0, page_size=5000)
# -> "No elements found"   (same for "Exception", which counts 276)
```

**Expected:** a plain type-scoped `find_relationships_between_elements`
should return the relationships the sibling
`count_relationships_between_elements` counts (or the two methods should
document why they differ).

**Actual:** the find returns the empty-result string for a bare
`relationshipTypeName` query even though the count is non-zero —
suggesting the find needs anchor element GUIDs (or has a bug), while the
count does not.

**Impact / workaround:** none needed in egeria-workspaces-fs — element
counts use `count_metadata_elements`; relationship counts/lists use
`ClassificationExplorer.get_relationships`, which works. Flagged because
the count/find asymmetry within the same OMVS is confusing and blocks
using the metadata-expert find as a fallback for the native relationship
count.

---

### ISSUE-41 (PY-21): `find_glossary_terms(sequencing_order=..., include_only_classified_elements=...)` returns ZERO results when combined — each filter alone works fine

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

## Docs / class-organization sharp edges

### ISSUE-19 (PY-12): `ReferenceDataManager` has no specification-property or valid-metadata-value methods

**Status:** fixed — re-verified 2026-08-15, found already resolved (never
marked closed here). `ReferenceDataManager`'s class docstring
(`pyegeria/omvs/reference_data.py`) now has a `Note` section stating it
does NOT cover Specification Properties and pointing callers at
`SpecificationProperties`/`MetadataExpert` instead — exactly the
"suggested improvement" below, already applied. Not clear which session
added it since this entry was last touched; recommending a class-selection
decision tree across `ReferenceDataManager`/`SpecificationProperties`/
`ValidMetadataLists`/`ValidTypeLists`/`MetadataExpert` is still open as a
nice-to-have, not a defect.

**Originally filed as:** open (docs/organization), re-verified 2026-07-31 — still true.
`ReferenceDataManager` inherits only from `ServerClient` (it's for
*business* reference data — country codes, currency codes, etc.), not from
`ValidMetadataManager`. `get_valid_metadata_values` happens to work on it
because that method lives on the shared `ServerClient` base, not on
`ValidMetadataManager` — easy to misjudge the class boundary from that
alone. The specification-property methods
(`get_specification_property_types`, `get_specification_property_by_type`,
`get_specification_property_by_name`, `get_specification_property_by_guid`,
`find_specification_property`) only exist on
**`pyegeria.SpecificationProperties`** (also on `ValidMetadataManager`
subclasses `ValidMetadataLists`, `ValidTypeLists`).

**Fix:** use `pyegeria.SpecificationProperties(...)` for these calls
instead of `ReferenceDataManager`.

**Suggested improvement:** either a class-level docstring note on
`ReferenceDataManager` clarifying the boundary, or a single unified
decision tree for "which OMVS client class do I need" across
`ReferenceDataManager` / `SpecificationProperties` / `ValidMetadataLists` /
`ValidTypeLists` / `MetadataExpert`, since several overlap in purpose.

---

## Design discussions (not confirmed bugs — decisions needed)

### ISSUE-48: No OMVS wrapper exists for the `SchemaAttributeDefinition` relationship (physical `SchemaAttribute` ↔ logical `DataField`)

**Status:** deferred 2026-08-15 — user's decision: wait until Egeria ships
the actual REST endpoint for this relationship before building a pyegeria
wrapper or Dr.Egeria command against it. Both options considered below
remain valid candidates once that lands; no implementation work done here.

**Original status:** open — SDK gap to validate with the team, not yet a confirmed
bug. Raised 2026-08-07 while triaging a request to add three "missing"
Dr.Egeria Data Designer commands (SemanticAssignment, DataClassAssignment,
SchemaTypeImplementation). Two of the three turned out not to be gaps at
all once checked against the real type system and existing compact specs:

- **SemanticAssignment** (schema/field → glossary term) already exists —
  `Link Semantic Assignment` / `Unlink Semantic Assignment` in the
  **Curation** family (`commands_curation_compact.json`, `OM_TYPE:
  SemanticAssignment`, wired to `ClassificationExplorer.
  _async_setup_semantic_assignment` in `CurationLinkProcessor`). Its
  `Target Element` is a generic GUID, so it already works against a data
  field or schema attribute today.
- **DataClassAssignment** on a physical schema attribute is also already
  covered — and the type name itself is stale. The old `DataClassAssignment`
  relationship was replaced in this Egeria version by
  `DataValueAssignmentRelationship` (0540 —
  `OpenMetadataTypesArchive1_2.java`), whose end 1 is `Referenceable` (any
  element, including a schema attribute). Data Designer's existing `Assign
  Data Value Specification` command (`OM_TYPE: DataValueAssignment`)
  already covers this generically via its `Element Id` attribute.

**The third one is a real gap, at the SDK level, not just the Dr.Egeria
command-spec level.** "SchemaTypeImplementation" isn't a real type name in
this Egeria version at all. The type that actually connects a physical
`SchemaAttribute` to a logical `DataField` is `SchemaAttributeDefinition`
(0580, `OpenMetadataTypesArchive5_3.java` —
`getSchemaAttributeDefinitionRelationship()`), ends `derivedFromDataField`
(on `DataField`, AT_MOST_ONE) / `equivalentSchemaAttribute` (on
`SchemaAttribute`, AT_MOST_ONE). Confirmed via grep across `pyegeria/omvs/`
and `pyegeria/http clients/*.http`: **no bespoke wrapper method exists**
for setting up or clearing this relationship — no `_async_link_*`/
`_async_setup_*` method, no `.http` worked example, in `data_designer.py`,
`data_engineer.py`, or `classification_explorer.py`.

**Options considered, not yet decided:**
1. Add a bespoke wrapper (e.g.
   `DataDesigner._async_link_schema_attribute_definition`/
   `_async_detach_schema_attribute_definition`) mirroring
   `_async_setup_semantic_assignment`'s shape, then wire a Dr.Egeria
   `Link/Unlink Schema Attribute Definition` command to it. Most
   consistent with how other bespoke-family relationships are handled, but
   requires new SDK surface first.
2. Skip the bespoke wrapper and drive it through the existing generic
   `MetadataExpert._async_create_related_elements`/
   `_async_delete_related_elements` (typeName-based) — the same mechanism
   `CurationLinkProcessor` already uses for other Tier-2 gaps with no
   dedicated method (`ResourceList`, `MoreInformation`). No new SDK method
   needed, but less discoverable/typed than a bespoke wrapper.

No command has been added to the compact JSON for this yet — deferred
pending the team's input on which approach (or whether the relationship
is even meant to be user-authorable via Dr.Egeria, vs. only ever
system-derived from a physical→logical mapping tool).

---

### ISSUE-55: Desired enhancement — true "exclude type" / NOT semantics for `findMetadataElements`

**Status:** open — desired enhancement, not a bug. Raised 2026-08-05
alongside ISSUE-45, from the same Egeria Insights use case ("elements that
have a SemanticAssignment relationship but are NOT type Notification").

**What's missing:** `FindRequestBody` has no negation operator for type at
all. `metadataElementTypeName` is a single positive inclusion filter
(that type plus all its subtypes); `metadataElementSubtypeNames` is meant
to narrow that to a specific allow-list of subtypes (see ISSUE-45 — doesn't
currently work, but even fixed, an allow-list is still not the same thing
as an exclude-list: excluding one noisy subtype out of a large,
open-ended family — e.g. "any `Asset` except `Notification`" — would
require enumerating every OTHER `Asset` subtype by hand, which is
impractical and silently stale the moment a new subtype is added).
`searchProperties`/element-property conditions can't reach `typeName`
either, since it's a structural/type-system attribute, not a regular
property in `propertyValueMap`.

**Desired shape (not designed in detail — flagging the need):** a genuine
exclude-list, e.g. `metadataElementExcludedSubtypeNames` (or a NOT/negation
option on the existing field), so a caller can say "type X or narrower,
except these specific subtypes" without enumerating the full positive
allow-list. Needs real Egeria-side API design work — this entry exists to
make sure the need doesn't get lost, not to prescribe the exact shape.

**Interim workaround, planned for Egeria Insights (`egeria-workspaces-fs`,
not pyegeria):** client-side post-filter, mirroring the pattern already
used there for relationship-presence conditions (which also have no
server-side equivalent) — fetch normally, then drop results whose
`typeName`/`superTypeNames` match a caller-specified exclude set, with an
honest note that the exclusion applies only to the fetched page (same
`relationshipFilterNote`/`defaultedTypeNote` transparency convention that
module already uses). Not yet built.

---

### ISSUE-60: `find_glossary_terms`'s `sequencing_order`/`sequencing_property` sorts only the fetched page, not the full result set — a "fetch one page, sort in JS" pattern silently drops alphabetically-early/late terms once the collection exceeds the page

**Status:** re-verified 2026-08-15 — **open question #1 below is now
answered, confirmed a real defect, not a design ambiguity.** Checked
pyegeria's request shape against `Egeria-api-glossary-manager.http`'s
`findGlossaryTerms` worked example first — byte-identical
(`sequencingOrder`/`sequencingProperty` field names and
`"PROPERTY_ASCENDING"` value form both match exactly), so this isn't a
pyegeria body-construction bug. Then tested live against `qs-view-server`:
`sequencing_property="displayName"` and `sequencing_property="qualifiedName"`
both still return **server-internal order, not alphabetical**
(`['Inventory', 'GHG offset', 'GHG Protocol...', 'Ratio indicator', ...]`
— not A→Z under either property). Went further than the original repro:
compared `None`/`PROPERTY_ASCENDING`/`PROPERTY_DESCENDING`/
`CREATION_DATE_RECENT` against the same query — `None`, `DESCENDING`, and
`CREATION_DATE_RECENT` all return the *identical* first-page term set,
while `ASCENDING` returns a genuinely different subset — so the parameter
isn't fully inert (it does influence which underlying scan/index strategy
picks the first page), it just never resolves to an actual sorted-by-property
order. **Answers open question #1: no, `sequencing_order`/`sequencing_property`
is not reliably usable as a true server-side sort for this endpoint today**
— any UI needing real alphabetical order must fetch-all-then-sort
client-side, confirming the workaround already in use is necessary, not
just cautious. Questions #2–4 (fetch-all vs. paged-UI strategy,
`maxPageSize` ceiling, shared-helper consistency) remain genuine product
decisions for the team/user, not resolved by this investigation and not
attempted here — nothing client-side to fix regardless of how those are
answered, since the underlying sort isn't reliable at the source.

**Original status:** open — design discussion, not a confirmed bug. High-priority
follow-up. Raised 2026-07-24 from a glossary-term aliases fix: aliased
terms were missing from egeria-workspaces-fs's default listing because of
how the portal loads and sorts lists. Consolidated in from
`egeria-workspaces-fs/PYEGERIA_ISSUES.md` 2026-08-05. **Split out
2026-08-15 from ISSUE-55** — this entry had been accidentally merged under
that heading with no `---` divider during the original consolidation
(unrelated topic: this is about sort scope, not exclude-type semantics);
no content changed, just given its own number so it's no longer buried
inside a different issue.

**Observations** (repro, `find_glossary_terms`, qs-view-server, 388 terms):
```python
# start_from paging works -- each page is a different, non-overlapping slice:
m.find_glossary_terms(search_string="*", start_from=0,  page_size=10, output_format="JSON")   # 10 terms
m.find_glossary_terms(search_string="*", start_from=10, page_size=10, output_format="JSON")   # next 10, no overlap

# BUT sequencing is not reflected in the result order:
m.find_glossary_terms(search_string="*", page_size=10, output_format="JSON",
                      sequencing_order="PROPERTY_ASCENDING", sequencing_property="displayName")
# -> ['Rolling base year','Carbon Intensity','Megawatt Hour','Inventory','Shall', ...]  (server-internal order, not A->Z)
```

So a "load-all up to a page-size ceiling, then sort/filter in JS" pattern
(used across several egeria-workspaces-fs apps) silently returns an
*arbitrary* subset when a collection exceeds the ceiling: e.g. default
`page_size=200` on 388 terms returns some 200, the endpoint re-sorts *those
200* by `displayName`, and terms outside that slice (incl.
alphabetically-early ones) simply never appear. (Note: `find_glossary_terms`
paginates correctly here via `start_from`/`page_size` as method parameters
— a different method from ISSUE-34's `find_metadata_elements`, whose
pagination bug/fix was about a different endpoint's request shape
entirely; this entry's own issue is about sequencing order, not
duplication or missing pages.)

**Open questions to decide (not asserting any of these is a defect):**
1. Is `sequencing_order`/`sequencing_property` expected to order the
   result here, or is that behavior config/connector-dependent?
   (Determines whether true server-side paged UIs are even feasible, or
   whether fetch-all-then-sort-in-JS remains the only reliable sort.)
2. Preferred model: **bounded server-side fetch-all** (loop `start_from`
   until the native `count_metadata_elements` total is reached or a
   ceiling is hit, return a `truncated`/`total` flag) vs. a true paged UI.
   Fetch-all keeps the existing instant client-side search; paged UI needs
   #1 resolved first.
3. **Page-size ceiling is bounded by the view server's configured
   `maxPageSize`** (OMAG server config) — likely well below 5000. Any
   fetch-all loop must chunk at ≤ that limit; the overall load ceiling is a
   separate product decision. TBD.
4. Apply the chosen strategy consistently via a shared helper across all
   "load-all" endpoints, rather than per-handler.

**Current mitigation:** none beyond raising `page_size`, which only lowers
the odds (a single page is still unsorted, so it sorts an arbitrary
slice). Tracked for a deliberate fix once the strategy + `maxPageSize` are
agreed. See ISSUE-41 for the more severe related failure mode (combined
with a classification filter, this doesn't just misorder — it silently
returns zero rows).

---

# Quick reference: which OMVS client class for which purpose

| Need | Class | Notes |
|---|---|---|
| Business reference data (country/currency codes) | `ReferenceDataManager` | Does **not** cover specification properties (ISSUE-19, docs-only) |
| Valid metadata values for a property name | `ReferenceDataManager` or `MetadataExpert` | `get_valid_metadata_values` lives on shared `ServerClient` base; no `as_of_time` support — Egeria endpoint doesn't expose it (ISSUE-18) |
| Specification properties (placeholders, guards, action targets, etc.) | `SpecificationProperties` | `get_specification_property_by_type` now works with either PascalCase or `SCREAMING_SNAKE_CASE` input (ISSUE-17, fixed 2026-08-15); `find_specification_property` with `graph_query_depth=0` also available (ISSUE-15); `get_specification_property_by_guid` works too, `NameError` fixed (ISSUE-28, fixed 2026-08-05, re-verified 2026-08-15) |
| `DataGrain` / `DataClass` listing | `find_data_value_specifications` / `get_data_value_specifications_by_name("*")` | Both fixed (ISSUE-1, ISSUE-2) |
| `DataSpec` (Collection subtype) | `CollectionManager.find_collections(metadata_element_type="DataSpec")` | |
| `DataStructure` / `DataField` | `DataDesigner.find_data_structures` / `find_data_fields` | |
| Solution blueprints/components (any pyegeria version) | `SolutionArchitect.find_solution_blueprints/components(search_string="*")` | Avoid `find_all_*` variants on old versions (ISSUE-11) |
| Note logs (list) | `find_note_logs("*", graph_query_depth=0)` | ISSUE-15 |
| Note logs (entries) | `get_notes_for_note_log(guid, page_size=100)` | ISSUE-3 — never pass `metadata_element_type_name="NoteLog"` |
| Collection members | `get_collection_members(collection_guid)` | ISSUE-8 — now returns members of any type, not just the collection's own type |
| Comparing results across two runs/environments that don't match | — | Check whether the same user's credentials were used in both — governance zone visibility can legitimately change results per-user (ISSUE-29) before assuming a pyegeria bug |
| Multi-classification search (`matchClassifications`, 2+ conditions) | `MetadataExpert.find_metadata_elements` | Fixed in Egeria server (ISSUE-35) |
| Paging a `find_metadata_elements` result | Set `"startFrom"`/`"pageSize"` **in the body dict** | Fixed (ISSUE-34) — these are NOT separate parameters on this method anymore; passing them as kwargs is silently a no-op. Same for `"graphQueryDepth"`. |
| Relationships for a single element by guid | `MetadataExpert.get_all_related_elements(guid)` | **Not** `get_metadata_element_by_guid` — that call never returns relationships, by design (ISSUE-37, not a bug) |
| Project parent/child hierarchy (any linked project, not just hierarchy) | `ProjectManager.get_linked_projects(guid)` | Fixed (ISSUE-42) — was silently returning "No elements found" regardless of real data |

---

# Appendix: Closed / Not-a-bug entries

## Fixed (Pyegeria)

### ISSUE-50: `base_report_formats.py`'s `Collections` FormatSet aliased the real Egeria type `ResultsSet` as `"ResultSet"` (missing the "s")

**Status:** fixed 2026-08-09, alongside adding pyegeria SDK support for
Egeria PR #9200 (SavedQuery/SmartQuery/ResultsSet). Originally found
2026-08-05 building egeria-workspaces-fs's saved-query prototype (Egeria
Insights `EGERIA_INSIGHTS_QUERY_MODEL.md`, Track A), which needed to
create a real `ResultsSet` collection.

Root cause: `pyegeria/view/base_report_formats.py`'s `"Collections"`
`FormatSet` listed `aliases=[..., "ResultSet", ...]` — missing the "s".
The real Egeria entity type is spelled **`ResultsSet`** (confirmed live
against `qs-view-server`'s `/api/types` entity catalog); passing
`"ResultSet"` as a `typeName` to `CollectionManager.create_collection` was
rejected outright by the server (`OMAG-COMMON-400-018`). Impact was
narrow but real: any caller rendering a genuine `ResultsSet` element
through `generate_output()`'s alias-based `FormatSet` lookup would miss
the match and silently fall through to a generic/default format instead
of `Collections`.

Fix: one-line change, `"ResultSet"` → `"ResultsSet"` in the `aliases`
list (`pyegeria/view/base_report_formats.py`, `"Collections"` FormatSet).

---

### ISSUE-44: `create_my_todo`/`create_meeting`/`create_review` (my_profile.py) always invented their own `qualifiedName` (random timestamp suffix, wrong casing), silently diverging from what Dr.Egeria's `Create ToDo`/`Create Meeting`/`Create Review` reported having created

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/omvs/my_profile.py` +
`md_processing/v2/actor_manager.py`/`project.py`/`feedback.py`). Reported
directly by the user: "the Dr.Egeria command Create ToDo does not appear to
create a todo."

**What actually happened:** `Create ToDo` genuinely succeeded — a real
`ToDo` entity was created, correct `displayName`/`description`/`situation`/
`priority`/`activityStatus`, `SUCCESS` reported with a real GUID. But
`_async_create_my_todo(todo_name, ...)` has no parameter at all for
accepting a caller-supplied qualified name — it always computes its own via
`self.__create_qualified_name__("Todo", todo_name)+f"-{int(time.time())}"`,
ignoring whatever qualified name Dr.Egeria's dispatcher already derived and
displays in its own analysis table. Confirmed live: Dr.Egeria reported
creating `Coco Pharmaceuticals::ToDo::Go-to-Lunch-with-Peter`; the entity
actually stored was `Coco Pharmaceuticals::Todo::Go-to-Lunch-with-Peter-1785955953`
— different casing (`Todo` vs `ToDo`) *and* an unpredictable numeric
suffix. Anyone searching for the element by the name Dr.Egeria reported —
Egeria Explorer, a fresh `find_*` call, a later Dr.Egeria command
referencing it by qualified name in a separate run — finds nothing, which
is exactly why it "does not appear to" have been created even though it
was.

**Systemic, not isolated:** `_async_create_meeting` and `_async_create_review`
have the identical pattern (confirmed by reading both) — both already wired
as Dr.Egeria commands (`Create Meeting` via `ProjectProcessor`, `Create
Review` via `FeedbackProcessor`), so both had the same latent bug.

**Fix:** added an optional `qualified_name: Optional[str] = None` parameter
to all three async methods and their sync wrappers — used verbatim when
provided (falls back to the existing auto-generation only when the caller
doesn't supply one, so no other caller's behavior changes). Updated all
three Dr.Egeria processor call sites
(`actor_manager.py`'s `Create ToDo` branch, `project.py`'s `Create Meeting`
branch, `feedback.py`'s `Create Review` branch) to pass the `qualified_name`
the dispatcher already computed.

**Verified live:** re-ran the user's exact `actor_actions.md` — `Create
ToDo` still `SUCCESS`, and the real stored element's `qualifiedName` now
matches Dr.Egeria's reported qualified name exactly (`Coco
Pharmaceuticals::ToDo::Go-to-Lunch-with-Peter`, confirmed via direct
`get_element_by_guid` comparison). Cleaned up both the original mismatched
throwaway and the corrected one afterward. Full `tests/micro-tests` suite
clean (same one pre-existing unrelated failure).

**Follow-up 2026-08-05 — the deeper bug: assigned ToDos never showed up in
`get_my_to_dos()` at all.** User reported: "I ran test_get_to_dos in
test_my_profile.py as erinoverview and don't see any Todos?" Root-caused in
three layers, all now fixed:

1. **`_async_get_my_assigned_actions` had a parameter-name bug** (typo
   `metadtata_element_subtypes` plus wrong field names `metadata_element_type`/
   `metadata_element_subtypes` instead of the real `GetRequestBody` fields
   `metadata_element_type_name`/`metadata_element_subtype_names`) — silently
   dropped by pydantic's `extra='ignore'` on every call. Fixing the names
   uncovered that this endpoint's own worked example
   (`Egeria-api-my-profile.http`) never sends these fields at all, and doing
   so live produces `OMAG-COMMON-400-019 ... type name ToDo ... is not a
   sub-type of UserIdentity` — the endpoint evidently applies them against
   the assigned actor's type, not the action's. Fix: stop forwarding these
   two fields into the request body for this endpoint (kept as inert public
   parameters for call-site compatibility with `get_my_to_dos`/
   `get_my_sponsored_actions`).
2. **The actual root cause: `_async_create_my_todo`/`_async_create_meeting`/
   `_async_create_review` put `originatorGUID`/`assignToActorGUID` *inside*
   `properties` (i.e. as fields of `ToDoProperties`/`MeetingProperties`/
   `ReviewProperties`)**, instead of at the top level of `ActionRequestBody`
   as siblings of `properties` — confirmed against
   `AssetMaker._async_create_action`'s own docstring/worked example, which
   shows `originatorGUID`/`actionSponsorGUID`/`assignToActorGUID` as
   top-level `ActionRequestBody` fields. Since `ToDoProperties` etc. have no
   such fields, they were silently dropped there too — the create call always
   succeeded, but no `ActionRequester`/`AssignmentScope` relationship was
   ever created, so the new ToDo was structurally invisible to any
   "assigned to me" query, no matter how the query itself was fixed. This
   was misdiagnosed mid-investigation as a possible Egeria-server-side gap
   (a raw REST call reproducing the same nested-properties mistake showed
   the identical missing-relationship symptom) before the nesting bug was
   spotted — flagged by the user, not found independently. Fix: moved both
   fields to the top level of the body in all three methods.
3. Also added `qualified_name: Optional[str] = None` support to
   `_async_log_my_activity`/`_async_journal_my_activity`/`_async_blog_my_activity`
   (the milder, deterministic-but-still-caller-ignored variant noted below in
   the original write-up), and added hand-maintained `ToDo-DrE`/`Meeting-DrE`/
   `Review-DrE` `FormatSet`s to `base_report_specs` (same fallback pattern as
   the existing `Journal-Entry-DrE`), fixing the `Report spec
   'ToDo-DrE-Basic' not found. Falling back to default.` warning noted below.

**Verified live (2026-08-05):** created a fresh ToDo via `create_my_todo()`;
`get_all_related_elements(guid)` now shows a real `ActionRequester`
relationship to the `Person` entity; `get_my_to_dos(output_format='JSON')`
returns the new ToDo's GUID. `select_report_spec('ToDo-DrE-Basic', 'MD')`
correctly falls through to the new `ToDo-DrE` spec. Cleaned up all
throwaway test elements afterward.

**Second follow-up 2026-08-05 — checked Meeting/Review through to reporting
too, not just ToDo:**

4. Verified live that `create_meeting`/`create_review` also now produce real
   `ActionRequester`/`AssignmentScope` relationships after the fix, and both
   show up via `get_my_assigned_actions()`.
5. **Found and fixed a separate, `Meeting`-specific bug**:
   `ProjectProcessor.fetch_element()` (`md_processing/v2/project.py`)
   unconditionally calls `_async_get_project_by_guid` — but `Meeting` is a
   Person Action Base type routed through `my_profile.create_meeting`, not a
   `Project` at all (see the `Meeting` branch in `apply_changes()`). Calling
   the Project-typed getter on a Meeting GUID 404s server-side
   (`OMAG-REPOSITORY-HANDLER-404-001 ... retrieved an object ... of type
   Meeting rather than type Project`), which `fetch_element` silently
   swallowed and turned into "Could not fetch element" — so
   `render_result_markdown` never rendered a Meeting's report at all, always
   falling back to `raw_block`. `Review` was unaffected (`FeedbackProcessor`
   doesn't override `fetch_element`, so it already used the generic
   `ClassificationExplorer`-based fetch in the base class). Fix: special-case
   `Meeting` in `ProjectProcessor.fetch_element()` to use the inherited
   base-class fetch instead. Verified live end-to-end (`fetch_element` +
   `render_result_markdown`) — a Meeting now renders its full `Meeting-DrE`
   report with no warnings.
6. Confirmed `AssetMaker._async_create_action`'s own worked examples in
   `Egeria-api-asset-maker.http` were already correct (top-level
   `originatorGUID`/`actionSponsorGUID`/`assignToActorGUID`) — the bug was
   purely in `my_profile.py` not following its own ground truth, not a gap in
   the `.http` file. Confirmed no other caller of `_async_create_action`
   exists, so the bug's blast radius was exactly the three methods fixed
   above.
7. Added a `KNOWN ISSUE` comment directly above the `getMyAssignedActions`
   worked example in `Egeria-api-my-profile.http`, documenting the confirmed
   `metadataElementTypeName`/`metadataElementSubtypeNames` 400 so it isn't
   reintroduced by a future edit that "helpfully" adds those fields back
   without re-checking live.
8. **Pre-existing broken ToDos found and deleted** (user's explicit
   decision): 6 `ToDo` entities existed from before this fix (`Go to Lunch
   with Peter` ×2, `Have a burger`/`Burger` ×2, `Curation Smoke ToDo`, plus
   one test-run leftover `do-my-backup`) — all created via the pre-fix nested
   -properties bug, so none had an `ActionRequester`/`AssignmentScope`
   relationship and none would ever appear in `get_my_to_dos()`. There is no
   retroactive repair (the relationship was simply never created); user chose
   to delete all 6 rather than recreate them. Also note: `do-my-backup`
   reveals `tests/functional-tests/test_my_profile.py::test_create_my_todo`
   has no teardown/cleanup — it leaves a live ToDo behind on every run.

---

### ISSUE-1 (PY-1): `DataDesigner.find_data_value_specifications` called non-existent `_async_post`

**Status:** fixed, re-verified 2026-07-31 — `_async_post` no longer exists
anywhere in the codebase (`grep -rn "_async_post\b" pyegeria/` returns
nothing); `find_data_value_specifications` now routes through the shared
`_async_find_request` helper.

```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.find_data_value_specifications(search_string="*")
```

---

### ISSUE-2 (PY-2): `get_data_value_specifications_by_name("*")` rejected the wildcard

**Status:** fixed, re-verified 2026-07-31 — the shared
`_async_get_name_request` helper (`_server_client.py`) still correctly maps
`filter_string = None if filter_string == "*" else filter_string`, aligned
with every sibling helper's "any" sentinel handling.

Root cause was the `"*"` convenience sentinel being sent to Egeria as the
literal string `".*"` instead of `None` — Egeria's by-name `filter` field is
not a regex, so `".*"` either matched nothing or matched literally.

```python
from pyegeria import DataDesigner
mgr = DataDesigner(view_server="qs-view-server", platform_url="https://localhost:9443",
                    user_id="erinoverview", user_pwd="secret")
mgr.create_egeria_bearer_token()
mgr.get_data_value_specifications_by_name("*")
```

---

### ISSUE-3 (PY-5): `get_notes_for_note_log` broken on pyegeria 6.0.14.4/.5

**Status:** fixed, re-verified 2026-07-31 (live). The default
`metadata_element_type_name="Action"` in `_async_get_notes_for_note_log`
(`_server_client.py`) looks superficially like it could still trigger the
originally-reported 404, but a live call against a real note log guid
(`901aab3a-e6f9-4bd1-8899-f013150fbcd4`) returned the correct note list (1
note, no error) — confirmed by direct test, not just by reading the code.

Originally on 6.0.14.4/.5: the default caused
`OMAG-REPOSITORY-HANDLER-404-001` ("guid is of type NoteLog rather than
Action"); passing `metadata_element_type_name="NoteLog"` returned the log
itself, not its notes. Fixed in 6.0.14.6+.

**Regression risk carried forward:** a `pip install pyegeria --upgrade`
that lands on exactly 6.0.14.4/.5 (a yanked/reordered PyPI point release)
would resurface this. Floor-pin `pyegeria>=6.0.14.6` in any deployment that
installs from PyPI rather than an editable local checkout. Also: do NOT
pass `metadata_element_type_name="NoteLog"` — it returns 0 notes even on
fixed versions.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.get_notes_for_note_log(note_log_guid="<guid-of-a-note-log>")
```

---

### ISSUE-4 (PY-7/8/11): `as_of_time` missing or silently dropped on several find methods

**Status:** fixed, re-verified 2026-07-31 — `find_information_supply_chains`,
`find_governance_definitions`, `find_note_logs`, `find_collections`,
`find_data_structures`, and `get_technology_type_elements` all route
through shared helpers (`_async_find_request` / `_async_get_name_request`)
that take `as_of_time` as an explicit named parameter or splat `**kwargs`
into the validated request body.

`get_valid_metadata_values` was reclassified, not a pyegeria fix — see
ISSUE-11 (Egeria Server section): the underlying REST endpoint is a plain
GET that never accepted `asOfTime` in the first place.

Originally (surfaced during a "time travel" audit): all of the following
accepted `as_of_time` either not at all, or silently swallowed it because
the method built its request body from explicit named parameters instead
of forwarding kwargs — `find_information_supply_chains`,
`find_governance_definitions`, `find_note_logs`, `find_collections`,
`find_data_structures`, `get_technology_type_elements`.

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
r1 = client.find_note_logs("*", graph_query_depth=0)
r2 = client.find_note_logs("*", graph_query_depth=0, as_of_time="2020-01-01T00:00:00Z")
# Fixed: r2 now genuinely reflects historical state instead of being identical to r1.
```

---

### ISSUE-6 (GAP-1): `PyegeriaAPIException` was a catch-all; typed subclasses existed but weren't raised

**Status:** fixed 2026-07-31. `_async_make_request` in
`_base_server_client.py` now branches on `related_http_code` and raises
`PyegeriaNotFoundException` (404) / `PyegeriaUnauthorizedException`
(401/403) instead of the generic `PyegeriaAPIException`. Both exception
classes re-parented from `PyegeriaException` to subclass
`PyegeriaAPIException` (with `__init__` calling `PyegeriaException.__init__`
directly, bypassing `PyegeriaAPIException.__init__`'s `response.json()`
call, since these two are now also raised for bare HTTP error responses
with no JSON body — see ISSUE-7) so all 63 existing
`except PyegeriaAPIException` handlers found across the codebase keep
working unchanged.

**Regression caught and fixed post-merge:** bypassing
`PyegeriaAPIException.__init__` also skipped the line that sets
`self.related_http_code`, which existing code relies on
(`except PyegeriaAPIException as e: if e.related_http_code == 404`). Fixed
by setting it explicitly in both subclasses' `__init__`.

```python
from pyegeria import EgeriaTech
from pyegeria.core._exceptions import PyegeriaNotFoundException
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
try:
    client.get_digital_product_by_guid("00000000-0000-0000-0000-000000000000")
except PyegeriaNotFoundException as e:
    print(e.related_http_code)  # 404
```

---

### ISSUE-7 (GAP-6): expired/invalid bearer token had no specific exception and no auto-renew

**Status:** fixed 2026-07-31. Connects to the (now closed) `BACKLOG.md`
issue "Bearer token expires mid-run on long `dr_egeria --process` batches."

Confirmed by direct repro against `qs-view-server`: a bad/expired bearer
token returns a bare HTTP 401 with an **empty response body** — no JSON,
nothing to distinguish "expired" from "wrong credentials" from
"insufficient permission." Since there's no way to detect "expired"
specifically from the response, `_async_make_request` now treats any 401
as a candidate for "the token might be stale": if the client holds stored
credentials, it calls the already-existing
`_async_create_egeria_bearer_token()` once and retries the original
request once before giving up. Default-on, no opt-out flag; at most one
retry ever (internal `_retry_on_auth` guard).

**Bonus bug found and fixed while implementing this:**
`_async_create_egeria_bearer_token()` (both the `BaseServerClient` and
`BasePlatformClient` copies) sent the token-creation POST with
`headers=self.headers` — which still carried the stale Authorization header
being replaced. The `/api/token` endpoint rejects requests with a bad
Authorization header outright (confirmed via direct curl repro), so the
refresh call itself always 401'd, silently defeating the whole mechanism
(both this new auto-retry and the pre-existing manual "call this if your
token expired" use case). Fixed to send a plain `Content-Type`-only header
for that one request.

**Verified live:** corrupted a real client's Authorization header, made a
real API call, confirmed exactly one auto-retry occurred and the call
succeeded transparently with a freshly-obtained token.

---

### ISSUE-8 (GAP-5): `get_collection_members` silently dropped non-Collection members

**Status:** fixed 2026-07-31. `_type` was overloaded in
`_async_get_results_body_request` for two purposes — genuine results
filtering (correct for most of its ~30 callers, e.g. "attached comments are
always type Comment") vs. a pure output-rendering hint (wrong only for
`_async_get_collection_members`'s `/{guid}/members` endpoint, since a
collection's members are never guaranteed to share its own type — e.g. a
`WorkItemList`'s members are `Project`s).

Rather than dropping the default filter for all ~30 callers, added an
explicit `filter_results_by_type: bool = True` parameter (default preserves
existing behavior everywhere) and set it `False` only at the one
confirmed-broken call site. Checked `get_collection_hierarchy` (same file,
same `_type="Collection"` default) separately — its endpoint's own docs say
"return a hierarchy of nested collections," so that filter is legitimate
and was left unchanged. Also added `"body"` to the `"Collection Members"`
FormatSet's `optional_params` in `base_report_formats.py` so report callers
can pass a fully custom body.

Live-verified against the original golden anchor (`WorkItemList` guid
`0affb580-fa81-4d00-9438-b26faf11845d`) — now correctly returns all 5
`Project`-typed members instead of an empty list.

---

### ISSUE-9 (GAP-3): malformed `as_of_time` reached pydantic as a raw `ValidationError`

**Status:** fixed 2026-07-31. Scope turned out bigger than originally
suspected: `as_of_time` is inherited by the whole get/find/search model
family (`GetRequestBody` and its ~4 subclasses), and 51
`.model_validate(...)`/`.validate_python(...)` call sites in
`_server_client.py` shared the same unguarded-validation pattern. Added a
generic `ServerClient._validate_body(validator, body)` static helper
(handles both the `self._xxx_adapter.validate_python` and
`SomeModel.model_validate` call shapes uniformly) that catches
`pydantic.ValidationError` and re-raises as
`PyegeriaInvalidParameterException` naming the offending field(s). Routed
all 49 active call sites through it (2 were already commented out).

```python
from pyegeria import EgeriaTech
client = EgeriaTech(view_server="qs-view-server", platform_url="https://localhost:9443",
                     user_id="erinoverview", user_pwd="secret")
client.create_egeria_bearer_token()
client.find_collections("*", as_of_time="null")
# Now: PyegeriaInvalidParameterException citing the asOfTime field.
# Previously: raw pydantic_core.ValidationError.
```

---

### ISSUE-10 (GAP-2): `user_id`/`server_name` with URL-unsafe characters weren't validated

**Status:** fixed 2026-07-31. `user_id` is embedded raw (no URL-encoding)
into several URL paths (e.g. `pyegeria/omvs/server_operations.py`'s
`.../users/{self.user_id}/status`). Neither `validate_server_name` nor
`validate_user_id` previously checked for characters unsafe in a URL path,
and `validate_user_id` wasn't even called during client construction.

Note: the original report's exact symptom ("a raw `httpx.InvalidURL`
propagates") didn't fully match what was found — the existing bare
`except Exception` in `_async_make_request` already wrapped it as the
generic `PyegeriaUnknownException`, just not a helpful, specific type.

Added a shared `_validate_url_path_safe(value, param_name)` check in
`_validators.py` (rejects ASCII control characters and URL-structural
characters `/ ? # \` plus whitespace), wired into both
`validate_server_name` (already called in both client constructors, so
`server_name` was fixed for free) and `validate_user_id` (now also called
explicitly in both constructors). Now raises
`PyegeriaInvalidParameterException` immediately at construction time,
naming the exact bad character.

```python
from pyegeria.omvs.server_operations import ServerOps
ServerOps("qs-view-server", "https://localhost:9443", user_id="bad\x00user", user_pwd="secret")
# Now: PyegeriaInvalidParameterException at construction, naming the character.
```

---

### ISSUE-20: `Analytic Parameters`/`Report Parameters` stringify every value, breaking list-valued analytic function params (e.g. `type_map`)

**Status:** fixed 2026-08-01 (Pyegeria — `md_processing/v2/report.py`),
found 2026-07-31 while building an Analytic Function demo (Projects/Terms
comparison) for the Local Dashboards sample.

**What:** `parse_key_value()` (`md_processing/v2/utils.py`) parses every
Dictionary-style attribute value (simple/list/table form) as a plain string
— there's no JSON/type coercion. `_report_additional_properties()`
(`md_processing/v2/report.py:132-135`) then does
`{str(k): str(v) for k, v in analytic_params.items() if v is not None}`
before `json.dumps(...)` into the stored `analyticParams` key. For a scalar
param (`window: 90d`, `type_name: Project`) this round-trips fine — the
string IS the value. But for a param whose real type is a list (e.g.
`counts_by_type`/`growth_series`'s `type_map: list[tuple[str, str]]`), the
markdown author's only way to express it is typing the literal text
`type_map: [["Projects", "Project"], ["Terms", "GlossaryTerm"]]` on one
line — `parse_key_value` stores that whole thing as ONE string value, which
then gets `str()`'d (no-op, already a string) and JSON-encoded as a STRING,
not a real JSON array. At read time (`local_dashboards_handler.py`'s
`json.loads(raw_analytic_params)`, or any other consumer), `type_map` comes
back as a Python `str`, not a `list`. When `format_set_executor.py`'s
`_run_analytic_function` forwards it as a kwarg,
`counts_by_type(type_map="[[\"Projects\", \"Project\"], ...]")` tries to
iterate the string character-by-character and unpack each character into
`(label, type_name)` → `ValueError: not enough values to unpack (expected
2, got 1)`.

**Where seen:** live repro — created a throwaway `Report` via `Create
Report` with `Report Spec: Analytic Demo - Assets by Type Breakdown` and
`Analytic Parameters: type_map: [["Projects", "Project"], ["Terms",
"GlossaryTerm"]]`. `--validate`/`--process` both succeeded (no attribute-
level error — the value parses as *a* string just fine). Fetching the
created element's `additionalProperties.analyticParams` showed
`{"type_map": "[[\"Projects\", \"Project\"], [\"Terms\", \"GlossaryTerm\"]]"}`
— the outer JSON is valid, but `type_map`'s VALUE is itself a string, not a
nested array. Calling `POST /api/report-specs/execute` with that exact
params dict reproduced the crash: `"not enough values to unpack (expected
2, got 1)"`. Cleaned up the throwaway Report afterward (`AssetMaker.delete_asset`).

**Impact:** any analytic function whose parameter type is a list/dict
(`counts_by_type`'s `type_map`, `growth_series`'s custom `type_map`,
`metric_trend`'s `metric_params`) cannot be set via Dr.Egeria's `Analytic
Parameters` (or `Report Parameters`, same code path) today — only flat
scalar params (`type_name`, `window`, `points`, `collection_guid`, etc.)
work. Worked around in the Local Dashboards sample/tutorial by sticking to
`count_elements(type_name=...)` (scalar) instead of `counts_by_type`
(list) for the Projects-vs-Terms comparison.

**Fix:** added `_coerce_analytic_value()` in `md_processing/v2/report.py` —
attempts `json.loads(v)` per-value before it's packed into the
`analyticParams` JSON blob, falling back to the original string if it isn't
valid JSON. Applied in `_report_additional_properties()`'s `Analytic
Parameters` handling (`Create Report`) and, since `View Report`
(`md_processing/v2/view.py`) turned out to have a second, related gap —
`Analytic Parameters` wasn't handled there **at all**, falling through to
the generic per-attribute branch and being treated as one param literally
named `analytic_parameters` holding the whole dict — added a matching
`Analytic Parameters` branch there too (merges flat into `params`, coerced,
mirroring the existing `Report Parameters` branch immediately above it).

Deliberately scoped to `analyticParams` only, not `_REPORT_PARAM_ATTRS` or
`Report Parameters` — those remain `Map<String,String>` at the Egeria
element level (a real constraint, not a bug) and must stay strings;
`analyticParams` is a single JSON-encoded blob consumed purely by Python's
own `**kwargs` at execution time, where real types matter.

**Verified live** (not just `--validate`): created a throwaway `Report`
with the exact original repro (`type_map: [["Projects", "Project"],
["Terms", "GlossaryTerm"]]`), confirmed `additionalProperties.analyticParams`
now stores `type_map` as a real nested JSON array, then called
`POST /api/report-specs/execute` with it — `counts_by_type` returned the
correct per-type breakdown (`Projects: 29, Terms: 591`) instead of
crashing. Also caught and fixed a second latent bug the same coercion
exposes: an `int`-typed scalar param (`points: 3`) previously round-tripped
as the string `"3"` too, which broke `growth_series` outright
(`TypeError: unsupported operand type(s) for -: 'str' and 'int'`) — now
correctly coerces to a real `int`. Ran
`tests/micro-tests/test_overview_metrics.py`,
`test_gen_report_specs.py`, `test_base_report_formats_mermaid.py` (34
tests) — all pass, no regressions. Cleaned up the throwaway Report
afterward. Not yet released to PyPI — still pinned at `6.0.17.8` in
egeria-workspaces-fs's `requirements.txt`; needs a version bump when the
next release goes out.

---

### ISSUE-25: `graph_query_depth` silently dropped (or scrambled) by ~20 sync/async OMVS wrapper methods — the actual root cause behind ISSUE-23/24's symptoms

**Re-verified 2026-08-15, no regression.** Spot-checked live against
`qs-view-server`: `find_information_supply_chains("Onboarding",
graph_query_depth=9)` (the exact original repro) correctly forwards
`graphQueryDepth: 9` into the body (request-spy confirmed); the three
previously-crashing scramble sites (`find_all_information_supply_chains`,
`find_all_solution_blueprints`, `find_all_solution_components`) all run
clean with no `TypeError`; `ClassificationExplorer.find_root_elements`'s
field-scramble fix also holds (`graphQueryDepth: 7` lands correctly,
`output_format`/`report_spec`/`timeout`/`body` no longer misrouted).
`pytest tests/ -m unit` passes. Fix from 2026-08-04 below is intact.

**Status:** fixed 2026-08-04 (Pyegeria — 8 files). Found while investigating a live
repro: `SolutionArchitect.find_information_supply_chains("Onboarding")`
returned a 3-node mermaid graph vs. 5 nodes for the equivalent raw REST call,
and neither `graph_query_depth` nor `max_mermaid_node_count` appeared to
change the result no matter what the caller passed.

**Root cause:** two distinct bug shapes, found via a runtime audit (not just
reading code) — every public sync method with a `graph_query_depth`
parameter across all `pyegeria/omvs/*.py` classes was instantiated, called
with a sentinel value, and `ServerClient._async_make_request` was
monkeypatched to capture the actual outgoing JSON body, to see whether the
sentinel ever reached the wire:

1. **Silent drop.** A sync wrapper (or an async method one layer further in)
   declares `graph_query_depth` as a parameter but never forwards it into the
   call it delegates to — the delegate's own default (always `3`) is what
   actually reaches the server, regardless of what the caller passed. This
   was the exact mechanism behind the reported repro:
   `SolutionArchitect.find_information_supply_chains`'s sync wrapper listed
   `graph_query_depth` in its signature but omitted it from the call to
   `_async_find_information_supply_chains` entirely. (`max_mermaid_node_count`
   was *not* affected the same way — it only ever reaches these methods via
   `**kwargs`, which does forward correctly — but since
   `_async_find_request`'s default of 10 already exceeds the graph size in
   the repro, raising it further couldn't add the missing nodes either;
   the 3-vs-5-node gap was purely a depth problem, and depth was the one
   parameter that had been silently stuck at 3 the whole time.)

2. **Positional scramble (same shape as ISSUE-21).** A sync wrapper calls its
   async counterpart, or a `find_all_*` convenience wrapper calls its
   `find_*` counterpart, using an all-positional argument list that doesn't
   match the target's actual parameter order. Beyond just losing
   `graph_query_depth`, this shifts *every subsequent argument* into the
   wrong slot. Two of these were bad enough that the method could never be
   called successfully at all —
   `SolutionArchitect.find_all_solution_blueprints`/`find_all_solution_components`
   raised `TypeError: ... takes from 1 to 11 positional arguments but 12
   were given` on every call (confirmed live before the fix), and
   `find_all_information_supply_chains` similarly overflowed
   (`... but 27 were given`). `ClassificationExplorer.find_root_elements`
   was more insidious — it didn't crash, but silently sent `output_format`
   (a string) into the `graphQueryDepth` body field, `report_spec` into
   `output_format`, `timeout` into `report_spec`, and `body` into `timeout`,
   dropping the caller's actual `body` entirely; found only because pydantic
   validation happened to reject the string-into-int case
   (`graphQueryDepth: Input should be a valid integer ... input_value='JSON'`)
   — a positional scramble that validation doesn't happen to catch would
   fail silently the same way ISSUE-21 did. **This general shape isn't fully
   swept yet — see ISSUE-27 for ~50 more unaudited call sites.**

**Fixed (verified via the same sentinel-injection harness, now 0 false
negatives across all ~734 methods with a `graph_query_depth` parameter):**
- `solution_architect.py`: `find_information_supply_chains` (drop),
  `find_all_information_supply_chains` (scramble/crash),
  `find_all_solution_blueprints` (scramble/crash),
  `find_all_solution_components` (scramble/crash),
  `find_all_solution_roles` (drop)
- `classification_explorer.py`: `get_element_by_guid` (drop),
  `find_root_elements` (scramble)
- `runtime_manager.py`: `get_platforms_by_name`, `get_platform_by_guid`,
  `get_server_by_guid`, `get_servers_by_name` (all: async-layer drop, one
  level past the sync wrapper, which already forwarded correctly)
- `product_manager.py`: `get_digital_products_by_name`,
  `get_digital_product_catalogs_by_name` (async-layer drop)
- `collection_manager.py`: `find_digital_products` — also fixes
  `DigitalBusiness.find_digital_products` and
  `GlossaryManager.find_digital_products`, both inherited from here
  (dead parameter: `graph_query_depth`, `metadata_element_type_name`,
  `metadata_element_subtypes`, `include_only_relationships`,
  `skip_relationships`, and `**kwargs` were all accepted but never placed
  into the hand-built `DeploymentStatusSearchString` body dict at all)
- `data_discovery.py`: `get_annotations_by_name`, `get_annotation_by_guid`
  (drop)
- `asset_catalog.py`: `get_assets_by_metadata_collection_id` (dead
  parameter — `graph_query_depth`, `include_only_relationships`,
  `skip_relationships` accepted but never placed into the hand-built body;
  **unverified against a live server** that the endpoint's body actually
  accepts `graphQueryDepth`/`includeOnlyRelationships`/`skipRelationships`
  under those exact names — the `.http` ground-truth file has no worked
  example with a body for this endpoint, so the names were inferred from
  the same fields' spelling everywhere else in this codebase, not confirmed
  live)
- `reference_data.py`: `get_valid_value_definitions_by_name` (drop)

**Not a bug — false positive from the same sweep, left alone:**
`get_typedef_by_name` (present on `ValidMetadataManager` and inherited by
`ValidMetadataLists`/`ValidTypeLists`/`SpecificationProperties`) also never
forwards `graph_query_depth`, but its REST endpoint
(`open-metadata-types/name/{name}`) is a plain GET with no request body at
all — same class as ISSUE-18 (`get_valid_metadata_values`). The parameter
is simply dead on that endpoint; there's nowhere to forward it to.

**Also found, promoted to their own tracked entries:** the same sentinel
sweep and its follow-up investigation surfaced three more distinct
findings, each now tracked separately rather than buried here —
ISSUE-26 (`get_info_supply_chain_by_guid`/`get_solution_role_by_guid` dead
parameters), ISSUE-27 (~50 unaudited all-positional call sites), and
ISSUE-28 (`NameError` breaking `get_specification_property_by_guid`).

**Consequence for ISSUE-23/24:** ISSUE-23 (raising the shared
`max_mermaid_node_count` default) and ISSUE-24
(`AssetCatalog._async_get_asset_lineage_graph_by_guid`'s hardcoded
`queryGraphDepth: 5`) are still open and still worth doing, but neither
would have fixed the reported symptom on its own — a configurable default
has nowhere useful to land while the value that's supposed to carry it
never reaches the request. This issue was the actual blocker; ISSUE-23/24
remain valid, narrower follow-ups on top of it.

**Postscript — the original repro's 3-vs-5 node gap was ultimately not a bug
at all.** After the fix above, live-verified with the user's exact raw REST
body (`searchString: "Onboarding"`, `startsWith: false`, `ignoreCase: true`,
no explicit `graphQueryDepth`/`maxMermaidNodeCount`) run through
`find_information_supply_chains`: pyegeria's `iscimplementationMermaidGraph`
for "New Employee Onboarding" was byte-for-byte the graph the user was
comparing against — the "3 nodes" vs. "5 nodes" difference was two valid but
different ways of counting the same mermaid text (3 `@{shape:...}` content
nodes vs. 5 total numbered flowchart boxes once the two `subgraph` container
boxes — "Context" and "Implementation" — are also counted, which is what a
person eyeballing the rendered diagram would naturally do). No truncation,
no depth issue, no forwarding bug in this specific case — the ISSUE-25 fix
above was still correct and necessary (confirmed via the runtime
sentinel-injection audit), it just wasn't the explanation for this
particular before/after comparison. **A second, genuinely separate effect
was layered on top of this in the user's actual comparison — see ISSUE-29
(governance zone visibility differs by user identity).**

**One more minor casing fix found and fixed along the way:**
`find_information_supply_chains` built its URL with
`f"...?addImplementation={add_implementation}"` where `add_implementation`
is a Python `bool` — this interpolates as `True`/`False` (capitalized)
rather than the lowercase `true`/`false` a REST boolean query parameter
normally expects. Live-verified this had no actual effect against the
current `qs-view-server` (Spring's boolean query-param binding is
case-insensitive, so `implementation` data was already coming back
correctly) — but fixed to `str(add_implementation).lower()` anyway for
robustness against stricter servers, matching the casing convention already
used at the sibling `get_info_supply_chain_by_guid` call site in the same
file.

---

### ISSUE-32: `create_note`/`update_note` used `"Notification"` as a placeholder `typeName`/`class` — replaced with the real `Note` type now that it's shipped (Egeria PR #9191)

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/core/_server_client.py`,
`md_processing/v2/feedback.py`), found/actioned same day the user redeployed
Egeria with the new type.

**Background:** Dr.Egeria's `Create Note` command was already a known,
explicitly-flagged placeholder — its compact-spec entry
(`md_processing/data/compact_commands/commands_feedback_compact.json`) reads
*"PARSE-ONLY STUB: no NoteProperties/NoteLogEntryProperties type exists
anywhere in pyegeria yet — a new Egeria type is in progress. ... do NOT wire
a processor for this command until the type ships and is confirmed."* with
`OM_TYPE: "Notification"` as the placeholder. Separately,
`ServerClient.create_note`/`update_note` (the note-log-entry creation/update
methods used by `_async_add_journal_entry` and directly by tests) built
their default request bodies with `"class": "NotificationProperties",
"typeName": "Notification"` for the same reason — no dedicated type existed.

**What changed:** confirmed via the actual Egeria source (not the stale
local `egeria-v6/egeria` checkout, which was 13 commits behind — checked
`git fetch` + `origin/main` directly) that commit `8d3b8d9a99` ("Add Note
type - a subtype of Notification", merged via PR #9191) added a real
`Note` `EntityDef` (typeGUID `391f73ff-c184-41b6-8620-310b4284039f`,
superType `Notification`, model area 0160 "Notes" — the same area as
`NoteLog`/`AttachedNoteLogEntry`, confirming `Note` is exactly the proper
type for what `create_note` already builds via the `AttachedNoteLogEntry`
relationship, not a separate new concept). `NoteProperties extends
NotificationProperties` with **zero new fields** — purely a type-identity
fix, no new attributes needed anywhere.

**Verified live** (user redeployed Egeria with the new type same day):
- `ValidMetadataManager.get_typedef_by_name("Note")` confirms the type is
  registered on `qs-view-server` (`beanClassName: NoteProperties`, correct
  GUID).
- Created a real `Note`-typed element end-to-end via the fixed
  `create_note` default body (no manual override needed) and fetched it
  back — `elementHeader.type.typeName == "Note"`, confirmed.
- Cleaned up all throwaway test elements afterward
  (`MetadataExpert.delete_metadata_element`, see ISSUE-31 for a bug hit
  along the way).

**Fixed:**
- `_server_client.py`: `_async_create_note`/`create_note` and
  `_async_update_note`/`update_note` — default body's `"class"`/`"typeName"`
  changed from `"NotificationProperties"`/`"Notification"` to
  `"NoteProperties"`/`"Note"` (6 docstring sample-body occurrences too, for
  consistency); the dead/vestigial `prop` type-list arguments passed to
  `_async_create_element_body_request`/`_async_update_element_body_request`
  updated to match (`['NoteProperties']`/`['Note']`) even though currently
  unused by the validation code, to avoid leaving stale documentation of
  intent.
- `md_processing/v2/feedback.py`: `FeedbackProcessor`'s `"Note" in
  object_type` branch — `set_element_prop_body("Notification", ...)` →
  `set_element_prop_body("Note", ...)` (this one has real effect — produces
  `"class": "NoteProperties", "typeName": "Note"`); `set_update_body(...)`'s
  first argument also updated for consistency, though that helper doesn't
  actually use it (dead parameter, confirmed by reading the function body).

**Update 2026-08-05 — Dr.Egeria's `Create Note` command is now fully wired,
not just unblocked at the SDK level.** The Tinderbox-only bottleneck this
entry originally described no longer applies — as of the same day, compact-
spec edits go through the Dr.Egeria Spec Editor's local REST API instead
(`commands/tech/spec_editor.py`, `http://localhost:8420`; see `CLAUDE.md`'s
"Dr.Egeria Spec Editor" section and the `dr-egeria-command-sync` skill).
Using that API: `Create Note`'s `OM_TYPE` changed `"Notification"` →
`"Note"`, its stub description replaced with a real one, and
`"Commented On Element"` (the same reference attribute `Create Comment`
already uses, conveniently pre-aliased `"Associated Element"`) added to its
`custom_attributes` — the spec previously had no way to say what element a
note was about at all. `refresh_specs --merge-reports` regenerated
templates/help/report-specs; unit tests pass. Registered
`FeedbackProcessor` for `Create Note` in `setup_dispatcher()` and
implemented its `Create` branch (previously a stub with no code at all): it
now creates a dedicated `NoteLog` for the target element
(`_async_create_note_log`) and the `Note` entry on it
(`_async_create_note`, using the fixed `Note`/`NoteProperties` typing from
above). **Verified live end-to-end**, not just `--validate`: processed a
throwaway `dr_test_create_note_smoketest.md`, confirmed
`elementHeader.type.typeName == "Note"` on the created element via direct
fetch, then cleaned up both the `Note` and its `NoteLog`
(`MetadataExpert.delete_metadata_element`, see ISSUE-31 for a bug hit
along the way). Note: each `Create Note` call currently creates its own
private `NoteLog` rather than reusing an existing one on repeated notes
against the same element — not wrong (a `NoteLog` can hold many notes,
this just doesn't dedupe), flagged as a possible future improvement, not
attempted here.

**Still not fixed:**
- `update_note`'s underlying REST operation 404s on this server regardless
  of the type fix — see ISSUE-30, unrelated to this change, blocks live
  verification of the update path specifically (create + fetch are
  confirmed working). `Create Note`'s compact spec has no companion
  `Update Note` command at all today (only `Create` was ever defined), so
  this doesn't block Dr.Egeria usage — only direct SDK callers of
  `update_note`/`_async_update_note`.
- **Fixed 2026-08-05, same day, follow-up session:** the orphaned
  `"Create Journal Entry"` registration flagged above is resolved — see
  ISSUE-33.

---

### ISSUE-33: `Create Journal Activity`/`Create Log Activity` used the `Notification` placeholder typeName; renamed to match real `JournalEntry`/`ActivityEntry` types, and the orphaned dead `Create Journal Entry` registration from ISSUE-32 is now a real, working command

**Status:** fixed 2026-08-05 (Pyegeria + Dr.Egeria compact spec, same day as
ISSUE-32, follow-up in the same session). User question: since `JournalEntry`
is a real `Notification` subtype, why is Dr.Egeria's command called `Journal
Activity` instead — could it be renamed for consistency?

**Investigation, grounded in the actual Egeria type system and docs (not
guessed):**
- Live type query confirmed `JournalEntry`, `ActivityEntry`, `BlogEntry` are
  all real, distinct `Notification` subtypes (siblings of `Note` from
  ISSUE-32) — `superType: Notification` for all three, live on
  `qs-view-server`.
- Fetched `egeria-project.org/concepts/notification/`,
  `/types/1/0160-Notes/`, and `/types/1/0135-Actions-For-People/` before
  proceeding (per explicit user instruction) — confirmed `Note` and
  `JournalEntry`/`ActivityEntry`/`BlogEntry` are siblings under the *same*
  `NoteLog` + `AttachedNoteLogEntry` mechanism (`AttachedNoteLogEntry`
  connects a NoteLog to "an Action (**typically a Notification**)" — not
  restricted to one subtype), differing only in target (any element, for
  `Note`; the calling user's own profile, for the other three) and
  visibility (`JournalEntry` private; `ActivityEntry`/`BlogEntry` public).
- This also surfaced that `Create Journal Activity`/`Create Log Activity`
  (bundle `My Journal Base`, mapping to `my_profile.py`'s
  `journal_my_activity`/`log_my_activity`) were **not registered in the
  dispatcher at all** — a bigger gap than a naming mismatch. `Create Blog
  Entry` already had the correct `OM_TYPE: "BlogEntry"` but was equally
  unregistered.
- Confirmed the pre-existing `reg("Create Journal Entry", FeedbackProcessor)`
  (ISSUE-32's finding) was genuinely dead/orphaned — no command by that name
  existed in the compact spec, and its code branch referenced attributes
  that don't exist anywhere in `commands_feedback_compact.json`. Renaming
  `Journal Activity` → `Journal Entry` would otherwise collide with that
  dead registration, so it was removed first.

**Fixed, via the Dr.Egeria Spec Editor's REST API** (compact spec — see
ISSUE-32's entry for why raw JSON edits aren't used):
- Deleted `Create Journal Activity`, created `Create Journal Entry`
  (`OM_TYPE: "JournalEntry"`, `alternate_names: ["Journal Activity"]`).
- Deleted `Create Log Activity`, created `Create Activity Entry`
  (`OM_TYPE: "ActivityEntry"`, `alternate_names: ["Log Activity"]`) — same
  consistency rationale as the Journal rename, so it wasn't left half-fixed.
- `refresh_specs --merge-reports` regenerated templates/help/report-specs;
  unit tests pass.

**Fixed, code (`md_processing/dr_egeria.py`, `md_processing/v2/feedback.py`):**
- Removed the dead `reg("Create Journal Entry", FeedbackProcessor)` +
  its broken code branch.
- Registered `Create Journal Entry`, `Create Activity Entry`, `Create Blog
  Entry` → `FeedbackProcessor`.
- Implemented one shared branch (`object_type in ("Journal Entry",
  "Activity Entry", "Blog Entry")`) dispatching to
  `my_profile._async_journal_my_activity`/`_async_log_my_activity`/
  `_async_blog_my_activity` respectively.

**Verified live, all three, end-to-end** (not just `--validate`): processed
a throwaway smoke-test doc through the real `dr_egeria --process` pipeline —
all three `SUCCESS` with real GUIDs — then fetched each back and confirmed
`elementHeader.type.typeName` was exactly `JournalEntry`/`ActivityEntry`/
`BlogEntry` respectively. Cleaned up all three afterward.

**Not touched:** `my_profile.py`'s journal/log/blog-my-activity NoteLogs
(the containers these entries were created in) — unlike `Create Note`'s
throwaway per-note `NoteLog`, these are the user's own persistent
activity-stream containers and weren't deleted during cleanup, only the
three created entries were.

**Downstream propagation completed same session:** templates regenerated
and mirrored into `egeria-workspaces-fs`/`egeria-advisor` (old
`Create_Journal_Activity.md`/`Create_Log_Activity.md` deleted, new
`Create_Journal_Entry.md`/`Create_Activity_Entry.md` added, confirmed via
`git status` in both downstream repos); `docs/dr_egeria_manual.md`'s
Feedback family description updated; `egeria-workspaces-fs/portal-docs/
tools/dr-egeria/templates-basic.md`'s Journal Entry example corrected to
use real attribute names (`Display Name`/`Description`, not the
placeholder `Subject`/`Entry` it previously showed) and noted the sibling
commands; dr-egeria Glossary (help Terms) regenerated and reprocessed
against the live server.

---

### ISSUE-21: `ClassificationExplorer.get_scoped_elements`/`get_scopes` — real bug was a stray `glossaries/` URL segment, not the positional-arg scramble originally suspected

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/omvs/classification_explorer.py`).

**Original report (2026-08-03):** suspected `get_scoped_elements`/`get_scopes`'s
sync wrappers passed `output_format` into the wrong positional slot when
calling their async counterparts, based on a `pydantic_core.ValidationError`
citing `page_size` receiving the string `'JSON'`.

**Re-investigated 2026-08-05:** checked the current code directly rather
than assuming the original diagnosis still applied — the sync-to-async
positional calls in both methods now match their target signatures exactly
(`element_guid/scope_guid, start_from, page_size, output_format,
report_spec, body` in both the caller and the callee), so the originally
reported scramble either was already fixed by an unrelated prior change or
the diagnosis was off. Re-running the exact original repro no longer
reproduces a `ValidationError` at all.

**What was actually still broken:** `_async_get_scoped_elements` built its
URL with a stray `glossaries/` path segment —
`{classification_command_root}/glossaries/elements/scoped-by/{scope_guid}`
— that doesn't match the real endpoint. Checked
`Egeria-api-classification-explorer.http`'s worked example ("Retrieve the
elements linked via the ScopedBy relationship to the scope"): the real path
is `.../classification-explorer/elements/scoped-by/{scopeGUID}`, no
`glossaries/` segment — ScopedBy isn't glossary-specific, it works on any
`Referenceable`. Every call 404'd regardless of arguments.
`_async_get_scopes`'s URL was already correct.

**Fix:** removed the stray `glossaries/` segment.

**Verified live:** `get_scoped_elements`/`get_scopes` against a real
element guid both now return `"No elements found"` (correct — that
element has no `ScopedBy` relationships) instead of a 404 exception.
Confirmed the fix doesn't regress the write path
(`add_scope_to_element`/`clear_scope_from_element`, unaffected by this
change, still used successfully elsewhere in this session's work).

---

### ISSUE-26: `get_info_supply_chain_by_guid`/`get_solution_role_by_guid` accept `graph_query_depth`/`max_mermaid_node_count` but never use them — same "dead parameter" shape as ISSUE-23's third case

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/omvs/solution_architect.py`).

**What:** `_async_get_info_supply_chain_by_guid` and
`_async_get_solution_role_by_guid` declared `graph_query_depth` but, when
`body` was `None`, sent **no body at all**
(`self._async_make_request("POST", url, **kwargs)`); passing
`max_mermaid_node_count` explicitly landed in `**kwargs` and was forwarded
straight into `_async_make_request()`, which doesn't accept it — a
`TypeError` on every attempt. Confirmed live before the fix:

```python
sa.get_info_supply_chain_by_guid("<any-guid>", graph_query_depth=10, max_mermaid_node_count=10)
# TypeError: BaseServerClient._async_make_request() got an unexpected keyword argument 'max_mermaid_node_count'
```

Same shape as ISSUE-23's "third case" for `get_solution_blueprint_by_guid`/
`get_solution_component_by_guid` (those two remain open/unfixed — this
entry only covers the two methods ISSUE-26 was scoped to).

**Fix:** when `body is None`, build an `AnyTimeRequestBody` with
`graphQueryDepth`/`maxMermaidNodeCount` populated from the (now also
added) `max_mermaid_node_count` parameter, instead of sending no body /
dumping stray kwargs into `_async_make_request`.

**Verified live, both methods:** calls that previously raised `TypeError`
on every attempt now succeed and return the expected element.

---

### ISSUE-28: `get_specification_property_by_guid` raised a bare `NameError: name 'validate_guid' is not defined` — cannot be called at all

**Re-verified 2026-08-15, no regression.** Bogus GUID now correctly raises
`PyegeriaNotFoundException` (not `NameError`); a real round trip (find a
specification property, fetch it by the returned GUID) succeeds and
returns the correct `identifier` (`supportedAnalysisStep`). Also fixed a
stale "currently broken outright" note pointing at this issue in the
Quick-reference table further down this file.

**Status:** fixed 2026-08-05 (Pyegeria — `pyegeria/omvs/valid_metadata.py`).

**What:** `validate_guid` was referenced in
`_async_get_specification_property_by_guid` but never imported anywhere in
`valid_metadata.py`. Every call failed immediately with `NameError`,
regardless of arguments — affecting `SpecificationProperties`,
`ValidMetadataManager`, `ValidMetadataLists`, `ValidTypeLists` (all share
this one implementation via inheritance).

**Fix:** added `from pyegeria.core._validators import validate_guid`,
matching the exact import convention already used in sibling OMVS modules
(`solution_architect.py`, `glossary_manager.py`, `automated_curation.py`,
`core_omag_server_config.py`).

**Verified live, end-to-end:** confirmed the `NameError` is gone (a bogus
guid now correctly raises `PyegeriaNotFoundException` instead), then ran a
full round trip — found a real specification property via
`find_specification_property`, fetched it by guid, got back the correct
`identifier` (`placeholderProperty`).

---

### ISSUE-35 (PY-15): Postgres repository connector ignored `matchCriteria` on `SearchClassifications` — multi-classification search always returned 0

**Status: FIXED and CLOSED (Egeria server, not pyegeria)** — verified
2026-07-17. Consolidated in from `egeria-workspaces-fs/PYEGERIA_ISSUES.md`
2026-08-05 (both files independently tracked pyegeria/Egeria issues; this
one and ISSUE-36 through ISSUE-41 below were unique to that copy — see this
file's top-of-doc note for the consolidation).

Originally confirmed as a server-side bug 2026-07-15, while building Egeria
Insights (`insights_handler.py`) — not a pyegeria client bug, the client
sent the body faithfully; the Postgres repository connector's SQL
generation dropped `matchCriteria` on the classification-matching path
only. Fixed server-side and re-verified live against `qs-view-server` once
the fixed server was deployed:

```
ZoneMembership ANY:      150   (unchanged -- single-condition baseline)
Confidentiality ANY:       1   (unchanged -- single-condition baseline)
Both ANY:                150   (was 0 -- now a real, differentiated union)
Both ALL:                  0   ("No elements found" -- correct, empty intersection)
Both NONE:               1000  (was 0 -- now a real, differentiated count)
```

`ANY`/`ALL`/`NONE` now produce distinct, semantically correct results
instead of all being an unconditional AND that always returned zero.

**Root cause:** `QueryBuilder.getSearchClassificationsClause()` in
`open-metadata-implementation/adapters/open-connectors/repository-services-connectors/open-metadata-collection-store-connectors/postgres-repository-connector/src/main/java/org/odpi/openmetadata/adapters/repositoryservices/postgres/repositoryconnector/database/QueryBuilder.java`
(lines 1036–1078) unconditionally `AND`s an `AND (type_name LIKE
'%:<Name>:%' ...)` clause per classification condition and never reads
`matchClassifications.getMatchCriteria()` at all — confirmed by grepping
the whole file: `MatchCriteria` is read in the *property*-matching path
(`getPropertyComparisonFromPropertyConditions()`, ~line 896) but never in
the classification-matching path. So the generated SQL always required
every named classification to appear on the same classification-table join
simultaneously, regardless of what `matchCriteria` the caller asked for.

**Regression coverage:**
- `egeria-python/tests/functional-tests/test_metadata_expert.py::test_find_metadata_elements_multi_classification_any_match_criteria`
  (pytest, asserts ANY's count >= max of the two single-condition counts) —
  passes as of 2026-07-17.
- `egeria-python/pyegeria/http clients/Egeria-PY15-matchClassifications-bug.http`
  (PyCharm/IntelliJ HTTP Client collection, same assertions via raw REST
  calls).

---

### ISSUE-36 (PY-16): `ClassificationExplorer.link_elements_as_peer_duplicates` (and its `_async_*` twin) POST to the wrong URL path — always 404s

**Status: FIXED** — confirmed 2026-07-17 on pyegeria 6.0.16.20.
Consolidated in from `egeria-workspaces-fs/PYEGERIA_ISSUES.md` 2026-08-05.

`_async_link_elements_as_peer_duplicates` now builds the URL from
`f"{self.classification_command_root}/related-elements/{element_guid}/peer-duplicate/{peer_duplicate_guid}/attach"`
— verified directly against the running `quickstart-pyegeria-web`
container's installed pyegeria source. Originally confirmed as a
client-side bug 2026-07-16, while seeding demo data for
egeria-workspaces-fs's Duplicate Resolution Review pane
(`duplicate_review_handler.py`).

**Root cause:** the client posted to
`.../classification-explorer/elements/{elementGUID}/peer-duplicate/{peerDuplicateGUID}/attach`
but the real Spring endpoint
(`ClassificationExplorerResource.linkElementsAsPeerDuplicates`) is mapped
at `.../classification-explorer/related-elements/{elementGUID}/peer-duplicate/{peerDuplicateGUID}/attach`
— `elements` vs `related-elements`. Same root cause likely affected
`unlink_elements_as_peer_duplicates` (detach, same path shape).
Classification calls (`set_known_duplicate_classification`/
`set_consolidated_duplicate_classification`) and the read path
(`get_relationships`/`get_elements_by_classification`) were unaffected.

**Fix:** `pyegeria/omvs/classification_explorer.py`,
`_async_link_elements_as_peer_duplicates` (and its detach twin) now build
the URL from the `related-elements` path.

---

### ISSUE-42 (PY-22): `ProjectManager.get_linked_projects()` didn't surface real `ProjectHierarchy` relationships

**Status: FIXED** (2026-08-05, `pyegeria/core/_server_client.py`).

**Layer:** Pyegeria (shared response-parsing helper, not the Egeria
server). Originally found 2026-07-31 while finishing an `as_of_time`
verification pass; consolidated in from `egeria-workspaces-fs/
PYEGERIA_ISSUES.md` 2026-08-05 as open, then investigated and fixed the
same day.

**Root cause:** `get_linked_projects` delegates to the shared
`ServerClient._async_get_guid_request` helper (used by 40+ callers across
the OMVS classes), which parsed a response by checking only two keys —
singular `"element"`, then `"elementGraph"` — before giving up and
returning `NO_ELEMENTS_FOUND`. But the real Egeria response for this
endpoint (`.../project-manager/metadata-elements/{guid}/projects`) returns
a genuine list under the **plural** `"elements"` key, which was never
checked at all. Confirmed live via a request-spy on `_async_make_request`:

```
RAW RESPONSE KEYS: ['class', 'requestId', 'relatedHTTPCode', 'elements']
get_linked_projects("5d0057f6-...") -> "No elements found"   # wrong
# but the raw body's "elements" list genuinely had 1 item
```

**Confirmed not a data-availability problem** (as originally suspected
when this was found): checked all 29 qs demo projects — every single one
returned `"No elements found"` regardless of whether it had real linked
projects (confirmed via `get_project_by_guid`'s own `managedProjects`
field, which does surface the same `ProjectHierarchy` relationships
correctly through a different code path).

**Fix:** added the plural `"elements"` key as a third fallback in
`_async_get_guid_request`, checked *last* (only reached once both
`"element"` and `"elementGraph"` have already failed) — purely additive,
so the other 40+ callers whose endpoints genuinely return the singular
shape are unaffected; none of their existing behavior changes since they
never reach the new branch.

**Verified:**
- Live against `qs-view-server`: `get_linked_projects("5d0057f6-...")` (no
  body, matching the original repro exactly) now returns a real 1-element
  list (`"Sustainability Bootstrap Project"`); a second project
  ("Next 30 Days (Initiation Phase)") returns 11 linked projects — matches
  its 10 `managedProjects` (children) + 1 `managingProjects` (parent),
  consistent with the method's own docstring ("any relationship will do").
- New unit tests, `tests/micro-tests/test_get_guid_request.py` (4 tests,
  mocked `_async_make_request`): the plural-`elements` case now parses
  correctly; the singular-`element` and `elementGraph` cases are
  unaffected (still checked first); the true-empty case still degrades to
  `NO_ELEMENTS_FOUND`, not an exception.
- Full micro-test suite: 228 passed (was 224; +4 new), same single
  pre-existing unrelated failure (`test_dashboard_sheet_models.py`) as
  before this change — no regressions across the other 40+ callers of the
  shared helper.

---

### ISSUE-34: `MetadataExpert.find_metadata_elements` ignored `start_from`/`page_size` — traced through THREE fix attempts before landing on the actual root cause (a moved Egeria convention), and a design change to prevent the whole bug class recurring

**Status: FIXED** (final fix 2026-08-05, `pyegeria/omvs/metadata_expert.py` +
`pyegeria/view/overview_metrics.py` + tests). Worth reading in full even
though it's closed — the misdiagnosis in the middle is as instructive as
the fix.

**Attempt 1 (dropped parameter).** `_async_find_metadata_elements`
originally built its request with a bare URL and the caller's `body`
passed straight through unmodified — `start_from`/`page_size`/
`graph_query_depth` were silently dropped, never merged into `body`, never
appended to `url`. Root-caused against the `.http` ground truth
(`Egeria-api-metadata-expert.http`'s worked examples): `graphQueryDepth`
**is** a body field there; `startFrom`/`pageSize` are not shown in the body
at all, so the fix assumed they were URL query parameters (matching the
older, pre-migration Egeria convention this same file's `.http` examples
still document) — appended `?startFrom={..}&pageSize={..}` to the URL and
merged `graphQueryDepth` into `body` when not already present. Verified via
runtime capture that the values reached the wire correctly.

**Attempt 2 (misdiagnosed as an Egeria-server bug).** Re-verified live
against `qs-view-server` and found real pagination still didn't work —
`start_from=0`/`start_from=5` (both `page_size=5`) returned the identical
full ~1,837-element population both times, 100% GUID overlap. Since the
*client* was confirmed (via request-spy) to be sending the spec-correct
URL, this was logged as an open **Egeria-server-side** gap — "the server
ignores these query parameters regardless of client version." **This
conclusion was wrong.**

**Attempt 3 (the actual root cause, found by the user).** Egeria's
pagination convention for this endpoint changed a few months before this
investigation — from URL query parameters to **request-body fields**. The
`.http` contract files pyegeria's fix was root-caused against were
themselves stale for this specific endpoint. Confirmed empirically:
```python
body1 = {..., "startFrom": 0, "pageSize": 5}
body2 = {..., "startFrom": 5, "pageSize": 5}
# len(r1) == len(r2) == 5 (page_size genuinely respected, not the full 1837)
# set(guids in r1) & set(guids in r2) == set()  -- two real, distinct pages
```
There is no Egeria-server-side bug here at all — pagination works
correctly and always has; pyegeria was sending the right values to the
wrong location, and "the server ignores it" was the visible symptom of
that, not evidence the server itself was broken.

**Final fix — a design change, not just a relocated injection.** Rather
than moving the URL-based injection into a body-based injection (which
would just be the same "pyegeria guesses where pagination goes for this
endpoint" model, now proven to go stale at least once already),
`start_from`/`page_size` were **removed from the method signature
entirely** — same treatment `graph_query_depth` had already gotten a few
hours earlier in this same investigation, for the same underlying reason
(pushback from the user: "I think that they should have full control over
the body and not have me inject anything in it"). For endpoints where the
caller already constructs the full `body` themselves, a second parameter
channel for the same information is exactly the shape that goes stale —
this is the second time in one investigation (dropped parameter, then
wrong location) that pyegeria's own tracking of "where does this value
belong" broke a caller. The caller already has to know Egeria's current
contract to build a correct body; they're better positioned to keep
`startFrom`/`pageSize` current for a given endpoint than pyegeria's
hardcoded assumption is. `body` is now sent to `_async_make_request`
completely unmodified, in every code path, for both the async and sync
forms of this method.

**Design principle adopted from this investigation** (see also ISSUE-43,
an audit for the same drift shape elsewhere): for any method where the
caller is required to supply the complete request body, do not *also*
accept overlapping parameters (`start_from`, `page_size`,
`graph_query_depth`, or similar) that pyegeria tries to inject somewhere —
document where the field belongs in the body and let the caller put it
there. This does **not** apply to convenience methods that build their own
body internally from named kwargs (most of the OMVS-specific `find_*`/
`get_*` wrappers) — there, pyegeria owns body construction either way, so
there's no second channel to remove.

**Callers updated to the new signature:**
`pyegeria/view/overview_metrics.py`'s `_find()` (production code — now
puts `"startFrom": 0, "pageSize": page_size` directly in the body dict
alongside the already-updated `"graphQueryDepth": 0`) and 5 call sites
across `tests/functional-tests/test_metadata_expert.py` /
`test_metadata_explorer.py` (previously passed `page_size=`/`start_from=`
as kwargs; now set `"pageSize"`/`"startFrom"` in the body dict itself). A
stale `PY-15` cross-reference in `test_metadata_expert.py` (predating this
file's 2026-08-05 consolidation) was also corrected to `ISSUE-35 (PY-15)`
while in there.

**Verified:** live against `qs-view-server`, two real distinct 5-element
pages via the *public* `find_metadata_elements(body)` call (no separate
pagination parameters at all) — confirms the fix works through the whole
call chain, not just the internal request construction. Full
`tests/micro-tests` suite: 228 passed, same one pre-existing unrelated
failure as throughout this session, no regressions.

**Follow-up cleanup, same day:** `output_format`, `for_lineage`,
`for_duplicate_processing`, and `**kwargs` were also removed from both
`_async_find_metadata_elements` and `find_metadata_elements` — none of the
four were ever referenced anywhere in either method's body (confirmed by
reading the full implementation), so declaring them implied controls that
never existed, the same "extraneous parameter" shape as `start_from`/
`page_size`/`graph_query_depth` above. Final signature for both: `(self,
body: dict, timeout: int = default_timeout)` — nothing else. Verified: live
call still succeeds (a `pageSize: 1` body field correctly limits to 1
result), full `tests/micro-tests` suite still clean.

**This raises the severity of the note below** — removing `**kwargs`
specifically means a caller still passing `start_from=`/`page_size=`/
`graph_query_depth=` as keyword arguments no longer gets silently ignored,
it now gets a hard `TypeError: find_metadata_elements() got an unexpected
keyword argument`. Worth knowing before upgrading pyegeria in any consumer
that hasn't been updated yet.

**Not carried over from pyegeria's fix:** `egeria-workspaces-fs/
insights_handler.py`'s `search_elements()` still calls `find_metadata_elements`
with `start_from=`/`page_size=`/`graph_query_depth=` as keyword arguments —
as of the follow-up cleanup above, this will now **raise `TypeError` on
every call** rather than silently no-op (see previous paragraph; this is a
stronger warning than when this entry was first written). That repo's own
call site needs a follow-up update to put `startFrom`/`pageSize` in its own
`find_body` dict to get real, efficient pagination — flagged, not fixed
here (different repo), but now genuinely blocking rather than just a
missed optimization.

---

## Not a bug / n/a

### ISSUE-5 (PY-9): local `as_of_time` fixes not shipped to the deployed package

**Status:** fixed / moot, re-verified 2026-07-31 — `get_linked_projects`,
`get_collection_members`, and `get_data_field_by_guid` all accept
`as_of_time` (directly or via `**kwargs`) in current source. This was a
deployment-timing issue, not a code defect — see ISSUE-12, below.

---

### ISSUE-11 (PY-3): `find_all_solution_blueprints`/`find_all_solution_components` missing in 6.0.12.2

**Status:** n/a — re-verified 2026-07-31, both methods exist in current
source. Was a version-pinning issue at the time (container pinned to
6.0.12.2, methods added in 6.0.12.4), not a code defect.

---

### ISSUE-12 (PY-9): local `as_of_time` fixes not shipped to a deployed container

**Status:** n/a — same root cause class as ISSUE-11. The fix landed in
source; the failure mode was a deployed container `pip install`-ing an
older released version instead of using an editable local checkout. Cut a
release / mount the local checkout as editable for dev+test to avoid this
recurring.

---

### ISSUE-13 (GAP-4): `pyegeria.core.mcp_server` pinned to a stale `mcp` package API

**Status:** n/a — re-verified 2026-07-31. `pyegeria/core/mcp_server.py` at
HEAD already imports `from mcp.server.mcpserver import MCPServer` (the
current API) and imports/runs cleanly with `mcp==2.0.0` installed in this
repo's venv (confirmed:
`python3 -c "from pyegeria.core import mcp_server"` succeeds). The
originally-reported `ModuleNotFoundError` was observed against a
**different, stale installed pyegeria wheel** inside the separate
`quickstart-pyegeria-web` container, not this dev tree — a
deployment/versioning gap in that other project, not a fix needed here.

---

### ISSUE-15 (PY-6, PY-14): `find_*`/list-style methods are O(n × graph-computation-cost) at default `graph_query_depth`

**Status:** n/a / reclassified as expected Egeria behavior — not a defect.
`graph_query_depth` controls how much relationship graph the server
computes per returned element; defaulting to depth 3 is a deliberate
trade-off (rich results by default). Confirmed on both `find_note_logs`
(PY-6, ~30-70s at default depth on demo data with large logs) and
`find_specification_property` (PY-14, ~50s vs ~0.6-2s at depth 0 for a
1000-element result set) — same root cause, two different methods.

**Workaround, already in use:** always pass `graph_query_depth=0` on any
bulk-listing call unless the caller genuinely needs the graph/mermaid
output — it's accepted via `**kwargs` even on methods that don't list it in
their signature.

**Possible future Egeria-side improvement** (not a bug, a suggestion):
default `graph_query_depth` to `0` for list-style methods (opt-in to the
expensive graph rather than opt-out), or split "list" and "graph" into
separate REST operations.

---

### ISSUE-16 (PY-10): asset detail by-guid appeared to "reject" `asOfTime`

**Status:** n/a — investigated and confirmed not a defect.
`get_asset_graph_by_guid`/`get_asset_by_guid` do honor `asOfTime` correctly;
the original 404/500 reports were caused by test timestamps that predated
the entity's repository version after demo data was reloaded — Egeria
correctly reports "not found at that time." The graph endpoint returning
500 instead of 404 for this case is a minor rough edge, not the originally
reported bug.

---

### ISSUE-18 (part of PY-7/8/11): `get_valid_metadata_values` has no `asOfTime` support

**Status:** n/a — reclassified, not a pyegeria fix. Checked the
ground-truth `.http` files: `get-valid-metadata-values/{propertyName}` is a
plain GET endpoint taking only `typeName`/`startFrom`/`pageSize` query
params; `asOfTime` never appears there, only on POST-body search/filter
endpoints elsewhere. The Egeria server doesn't expose historical-query
capability on this endpoint at all — adding an `as_of_time` param
client-side would be dead code (silently ignored server-side). Would need
an Egeria REST API change to add `asOfTime` support to this endpoint first.

---

### ISSUE-29: Information Supply Chain search results/mermaid graphs differ by user identity — governance zone visibility, not a pyegeria bug

**Status:** n/a (Egeria Server — deliberate zone-based visibility
filtering), found 2026-08-04 chasing down the last piece of ISSUE-25's
original repro.

**Layer:** Egeria Server (governance zone / visible-zones configuration).

**What:** the exact same `find_information_supply_chains` search, run at
the same instant against the same view server, returns materially
different data depending on which user's credentials are used. Live-
verified side-by-side for "New Employee Onboarding Information Supply
Chain":
- `peterprofile`: implementation graph shows 5 `SoftwareServer`s
  (`coco-hrim`, `NL payroll`, `CA payroll`, `UK payroll`, `ocopages`)
- `erinoverview`: implementation graph shows only 2 (`coco-hrim`,
  `ocopages`) — the 3 payroll systems are filtered out entirely

Confirmed via raw `curl` against `/api/token` + the `by-search-string`
endpoint directly, with zero pyegeria code involved — same request body,
same moment, different user, different result. Not a caching artifact
(re-ran both back-to-back) and not explained by anything on the client
side.

**Where seen:** originally surfaced as part of ISSUE-25's repro
investigation — initially looked like a "3 nodes vs 5 nodes" pyegeria bug,
but turned out to be two unrelated effects layered together: a
node-counting-convention difference (see ISSUE-25's postscript, resolved,
not a bug) plus this genuine zone-visibility difference (this entry).

**Why not a bug:** pyegeria faithfully returns whatever the server sends
for the credentials it's given. The 3 payroll systems are presumably
scoped to a governance zone `erinoverview`/`IvorPadlock` aren't members of,
while `peterprofile` (likely a broader-access/admin-style demo user) can
see them. This is Egeria's zone-based security model working as designed,
not a pyegeria defect — nothing here is client-side fixable.

**Worth knowing:** if comparing pyegeria output against a raw REST call or
Egeria Explorer UI result and results don't match, check whether the same
user/credentials were used in both before assuming a client-side bug —
this cost real investigation time in ISSUE-25's process. Added a pointer
to this in the Quick Reference table above and in this file's intro.

---

### ISSUE-37 (PY-17): `MetadataExpert.get_metadata_element_by_guid` never returns relationships, at any `graph_query_depth` — use `get_all_related_elements` instead

**Status: not a bug — working as designed** (confirmed 2026-07-17, Dan).
Consolidated in from `egeria-workspaces-fs/PYEGERIA_ISSUES.md` 2026-08-05.

`get_metadata_element_by_guid` is deliberately scoped to the element
itself; `get_all_related_elements` is the correct, separate call for
relationships — a two-call design, not a gap in the by-guid method.
Originally flagged 2026-07-16 while fixing egeria-workspaces-fs's Action
Center pane cross-links (`action_center_handler.py`), because the accepted
`graph_query_depth` parameter suggested it should affect relationship
inclusion; it doesn't, and that's correct behavior.

**How to trigger:**
```python
guid = "<a Notification guid known to have Actions/ActionRequester/AssignmentScope relationships>"
for depth in (0, 1, 2, 3):
    el = mgr.get_metadata_element_by_guid(guid, graph_query_depth=depth, output_format="JSON")
    print(depth, sorted(el.keys()))
# every depth prints the same 8 keys -- no relationship key ever appears:
# ['classifications', 'elementGUID', 'elementProperties', 'headerVersion',
#  'origin', 'status', 'type', 'versions']
```

**Working alternative:** `MetadataExpert.get_all_related_elements(guid, output_format="JSON")`
returns `{"startingElement": <the element>, "elementList": [...], "mermaidGraph": ...}`.
Each `elementList` entry is a relationship-header dict with its own
`type.typeName` (the *relationship* type) and a nested `element` key
holding the *other* end, in the same raw `elementGUID`/
`elementProperties.propertyValueMap` shape everything else uses. Confirmed
live against a real Notification with 3 genuine relationships — all three
showed up via this call, none via `get_metadata_element_by_guid` at any
depth.

**Usage note (not a fix, a caller guideline):** any by-guid detail call
that needs relationships should use `get_all_related_elements` (or a
type-specific OMVS method that already merges both, e.g.
`ActorManager.get_actor_role_by_guid`), never
`get_metadata_element_by_guid` alone, plus `graph_query_depth` as if it
controlled relationship inclusion.

---

*(Add new entries at the top of the appropriate Open Issues subsection as
they're found; move an entry to the Appendix once it's fixed/reclassified,
keeping its original `ISSUE-#`. Keep the format: status, layer
classification, what, where seen, candidate fix — so entries are
self-contained enough to hand to whoever eventually reviews/fixes them.)*

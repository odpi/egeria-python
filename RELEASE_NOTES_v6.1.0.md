# pyegeria v6.1.0

This is the first tagged release in a while — the last was `v6.0.17.1` (2026-07-20), but that undersells the real gap: it's been **since April** that this project last had a properly summarized release. Between April and now: ~380 commits, 60+ merged PRs, and several genuine architectural shifts, not just accumulated bug fixes. The version scheme also moves from the old 4-part `6.0.18.x` numbering to clean semver (`6.1.0`) going forward.

## Headline changes since April

### Full coverage of Egeria's view services

Every one of Egeria's 40 view-service `.http` collections now has a matching, audited `pyegeria/omvs/` client module (44 modules total — some services split across more than one client). This wasn't just "a module exists per service" — a dedicated audit tool (`scripts/omvs_audit.py`) was built to mechanically reconcile every `_async_*` method's HTTP verb, URL, and request-body class against the `.http` files, which are the ground truth. That audit was then run service-by-service (feedback-manager, classification-explorer, runtime-manager, solution-architect, metadata-expert, governance-officer, and more) and every real mismatch it found was fixed: broken helper calls, wrong request-body classes, silently-dropped URL path segments. Current state: 726 of ~751 checked methods confirmed correct, the rest triaged as either intentional cross-service duplication or tracked as known gaps — a very different starting point than "hope the URL is right."

### Dr. Egeria is now a two-pass interpreter

Dr. Egeria markdown files routinely define several related elements in one file — e.g. a parent Project followed by a child Project it references, or a Glossary followed by Categories that belong to it. The original single-pass dispatcher could only resolve a **backward** reference (something defined *earlier* in the file); a **forward** reference (something defined *later*) failed outright with "referenced element not found," forcing users to manually reorder their markdown around the tool's execution order.

`V2Dispatcher.dispatch_batch()` now processes a file in two passes instead of one:
1. **Pre-scan** — before any command executes, the whole batch is walked once to collect every Create/Update command's own eventual qualified name (and display name) into a "will exist" set.
2. **Round-based resolution** — commands run in rounds; a command whose reference resolves to something in that "will exist" set but isn't creatable *yet* is deferred (not failed) and retried next round, until nothing more can progress. Only then is a truly unresolvable reference treated as a real error.

Net effect: users can write markdown in whatever order makes sense to them — parent before child or child before parent — instead of in dependency order. See `docs/design/dr_egeria_design_v2.md` ("Robust Inter-Command Architecture") for the full mechanism.

### Test automation

Test coverage grew substantially over the same period — 103 test files in April to 161 today (~56% growth) — spanning all three tiers (`micro-tests/` unit tests, `functional-tests/` per-OMVS, `scenario-tests/` full create→link→delete lifecycles). A GitHub Actions release workflow now gates every tagged release on the `micro-tests/` suite passing before a build is even attempted (scoped deliberately to the no-live-server tier — the full suite requires a running Egeria instance and isn't CI-appropriate).

### Compact JSON is now the sole system of record for Dr. Egeria commands

Dr. Egeria's command specifications (attributes, bundles, commands — 15 compact JSON files today) used to be authored in an external Tinderbox file and exported. That workflow is retired: a local Dr.Egeria Spec Editor (`dr_egeria_spec_editor`, FastAPI + vanilla JS, `commands/tech/spec_editor.py`) now edits the JSON files directly through a REST API with real structural validation (bundle-chain resolution, unknown-attribute checks, duplicate-name checks) — including for AI-driven edits, not just the human UI. `refresh_specs` regenerates markdown templates, help docs, and report specs from those files.

## New Dr. Egeria command families (April → August)

- **Dashboard Sheet family** — `Create Dashboard Sheet`, `Link Report to Dashboard Sheet`, `Add Text on Dashboard Sheet` — a locally-persisted (not-yet-Egeria-native) layout model for user-authored dashboards.
- **Curation family** — classification and relationship commands wired to real pyegeria calls, routed by `OM_TYPE` rather than verb (since "Update" is ambiguous between a classification update and a relationship update).
- **Action Author family** (`Governance Officer` extension) — process-step and executor/target linking commands (`Link First/Next Process Step`, `Link Action to Action Executor/Target`), each with real relationship-property handling the generic peer-link mechanism doesn't support.
- **Multi-link relationship support (ISSUE-68)** — relationship types with `MULTI_LINK`/`REVERSIBLE` cardinality now surface their relationship GUIDs and get proper `Update` commands instead of only `Link`/`Detach`.
- **`skipSubtypes` exclude-list semantics (ISSUE-55)** — find/search commands can exclude specific subtypes from a type hierarchy instead of only supporting a fixed include-list.
- **`Link/Detach Schema Attribute Definition` (ISSUE-48)** — implemented against the generic `MetadataExpert` relationship endpoint as a deliberate stopgap pending a dedicated Egeria endpoint; documented as temporary and will be swapped out once that endpoint ships.
- **Folder-batch CLI** (`dr_egeria_folder`) — runs every markdown file in a folder through one shared client/bearer-token, with manifest-ordering support, replacing one-process-per-file.
- **New Report type**, new metric/analytic functions, and expanded report-spec/format-set coverage.

## Performance

Glossary term membership sync is roughly **35-40x faster** — the processor used to always fetch "what does this element currently belong to" before syncing; that fetch is now skipped entirely for known-new elements (a brand-new term can't have existing memberships) and for no-op syncs.

## SDK fixes

- Systematic forwarding-bug fixes surfaced by the OMVS audit (see above) across most service modules.
- `DeleteElementRequestBody` was missing `cascadeDelete`/`deleteMethod` fields despite both being real, documented Egeria fields — every caller passing `cascade_delete=True` had silently been sending it unset (ISSUE-62).
- Classify Term as Question request body corrected; `get_guid_info` crash guard added.
- ToDo/Meeting/Review assignment relationships fixed, with regression tests.
- Stale `OpenMetadataDeleteRequestBody` in ToDo scenario tests corrected.
- MCP server migrated to `mcp` 2.0.0's `MCPServer`; stale-tool-list bug fixed; `run_report` reliability fix.
- Mermaid rendering no longer hard-depends on the public `kroki.io` service.
- My Profile app: multiple report/format and profile-comment updates.

## Docs

- README added to every meaningful code/data folder; stale docs corrected across the repo.
- `PYEGERIA_ISSUES.md` restructured by who can fix it (Egeria first, pyegeria second, closed last) and re-verified end to end — several long-open issues closed as already fixed server-side.

## Known issues

- **ISSUE-69**: term/description text containing a single apostrophe gets doubled (`'` → `''`) on round-trip. Re-diagnosed this release and confirmed via a raw `curl` reproduction (bypassing pyegeria entirely) that the corruption happens server-side in Egeria, not in this client. No pyegeria-side fix is possible; a fix is in-progress.
- **ISSUE-48**: `SchemaAttributeDefinition` linking uses the generic-relationship-endpoint workaround described above rather than a dedicated OMVS method, because Egeria doesn't yet expose one yet - in progress.

## Upgrade notes

- Minimum supported Python remains 3.12+.
- No breaking API changes; existing Dr.Egeria markdown files and SDK client code should continue to work unchanged.

---

*Full commit history: [`v6.0.17.1...v6.1.0`](https://github.com/odpi/egeria-python/compare/v6.0.17.1...v6.1.0)* (covers the tagged range; the April work described above predates that tag and is summarized from the broader commit history since this project's last real release-notes pass).

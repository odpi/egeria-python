<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# docs/design

Design documents and architecture walkthroughs for the Dr.Egeria v2
pipeline, written during/after the work they describe rather than kept
continuously updated — treat these as historical design records, not live
specs. For the current architecture, see `CLAUDE.md`/`AGENTS.md` at the
repo root first.

| File | Covers |
|---|---|
| `dr_egeria_design_v2.md` | The v2 pipeline's overall design: extraction → dispatch → processor → render. |
| `dr-egeria-module-structure.md` | How `md_processing/` is organized and why. |
| `dr-egeria-execution-engine-walkthrough.md` | Walkthrough of `AsyncBaseCommandProcessor.execute()`'s step-by-step flow. |
| `dr-egeria-parser-change.md`, `dr-egeria-refactoring-walkthrough.md` | Historical notes on parser/processor refactors. |
| `dr-egeria-v2-robustness-walkthrough.md` | Error-handling and validation robustness pass. |
| `dr-egeria-validation-dependencies-walkthrough.md` | How attribute validation dependencies are resolved. |
| `dr-egeria-forward-references-and-governance-attrs-walkthrough.md` | Forward-reference resolution (`(Planned: ...)` GUIDs) and governance-specific attribute handling. |
| `output_generation_and_normalization.md` | How rendered markdown output is generated and normalized. |
| `report_spec_migration_design.md` | Design for migrating hand-maintained report specs to the generated `base_report_formats.py` registry. |

If a document here contradicts current code behavior, trust the code (and
`CLAUDE.md`) — these are point-in-time design notes.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# docs

Reference documentation for pyegeria and Dr.Egeria, aimed at users and
contributors who need more depth than the top-level `README.md`/`CLAUDE.md`/
`AGENTS.md` provide.

| File | Covers |
|---|---|
| `dr_egeria_manual.md` | The Dr.Egeria user manual — command reference, markdown authoring conventions, attribute styles. |
| `output-formats-and-report-specs.md` | How `generate_output()`/report specs work: `FormatSet`/`Format`/`Column`/`ActionParameter` models, analytic functions, chart output formats. |
| `reference-data-and-valid-metadata-mechanisms.md` | Reference data (`ReferenceDataManager`) vs. valid metadata values — what each mechanism is for and when to use which. |
| `parameter_cleanup_plan.md` | Working notes from an in-progress parameter-naming/consistency audit across OMVS clients. |
| `user_programming.md` | Notes on programmatic (non-CLI) use of pyegeria. |

`design/` holds architecture and design-history documents — see its own
`README.md`.

For day-to-day contributor guidance (dev setup, running tests, dispatch
pipeline architecture), start at the repo root's `CLAUDE.md`/`AGENTS.md`
instead; these docs go deeper on specific subsystems.

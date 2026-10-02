<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# docs

Reference documentation for pyegeria and Dr.Egeria, aimed at users and
contributors who need more depth than the top-level `README.md`/`CLAUDE.md`/
`AGENTS.md` provide.

| File | Covers |
|---|---|
| `developer_guide_pyegeria_textual.md` | Developer Guide for Python programmers new to Egeria and Textual — step-by-step examples (`examples/developer_guide/`), then My Profile, Dr.Egeria and hey_egeria as case studies. Screenshots in `images/developer-guide/`. |
| `dr_egeria_manual.md` | The Dr.Egeria user manual — command reference, markdown authoring conventions, attribute styles. |
| `my_profile_app_manual.md` | The My Profile App user manual — configuration, starting the app, change user, every screen and key, comments, feedback, return codes, known limitations, running the tests. |
| `My-Egeria-Doc.md` | My Profile App reference guide — source layout, mixin structure, routing tables, Egeria calls and report specs per flow, flow and sequence diagrams. |
| `output-formats-and-report-specs.md` | How `generate_output()`/report specs work: `FormatSet`/`Format`/`Column`/`ActionParameter` models, analytic functions, chart output formats. |
| `reference-data-and-valid-metadata-mechanisms.md` | Reference data (`ReferenceDataManager`) vs. valid metadata values — what each mechanism is for and when to use which. |
| `parameter_cleanup_plan.md` | Working notes from an in-progress parameter-naming/consistency audit across OMVS clients. |
| `user_programming.md` | Notes on programmatic (non-CLI) use of pyegeria. |

`design/` holds architecture and design-history documents — see its own
`README.md`.

For day-to-day contributor guidance (dev setup, running tests, dispatch
pipeline architecture), start at the repo root's `CLAUDE.md`/`AGENTS.md`
instead; these docs go deeper on specific subsystems.

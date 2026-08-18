<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests/micro-tests

Unit/formatter/parser/dispatcher tests — no live Egeria server required
(fake clients, in-memory fixtures). This is where most pyegeria/Dr.Egeria
bug-fix regression tests belong (see `PYEGERIA_ISSUES.md` — most `Fixed`
entries reference a test here).

Notable groupings:
- `test_v2*.py`, `test_dispatcher_forward_references.py`, `test_parser.py`,
  `test_dr_egeria_extraction.py` — Dr.Egeria v2 pipeline (extraction →
  dispatch → processor) tests.
- `test_output_formatter_*.py`, `test_base_report_formats_mermaid.py`,
  `test_format_set_*.py`, `test_gen_report_specs.py`,
  `test_report_spec_any_lookup.py` — report-spec/output-formatting tests.
- `test_*_processor_coverage.py`, `test_*_multilink*.py`,
  `test_governance_link_multilink_guid.py` — per-processor/command coverage
  tests, usually added alongside a specific `PYEGERIA_ISSUES.md` fix.
- `governance/` — Governance Officer family tests (compact-spec validation,
  processor routing, zone/domain resolution).
- `my_profile/` — tests for a separate `MyProfileApp` Textual TUI (not the
  `pyegeria.omvs.my_profile` OMVS client — that's covered in
  `tests/functional-tests/`).
- `conftest.py` — the active fixture file (`test_credentials`/`test_params`).
  `conftest_full.py` is a fuller, currently-inactive alternate conftest;
  see `tests/README.md`'s note on the `--live-egeria` flag it documents.
- `action_perf.py`, `asset_perf.py` — standalone performance-check scripts,
  not pytest test files.

Run with `pytest tests/micro-tests/` (or the repo-root `pytest tests/`,
which includes these).

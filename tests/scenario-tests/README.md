<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests/scenario-tests

Full-lifecycle scenario tests (`test_*_scenarios.py`) — each exercises a
realistic multi-step sequence (typically Create → Link → Update → Detach →
Delete, sometimes across several related OMVS clients) against a live
Egeria server, rather than testing one method in isolation like
`tests/functional-tests/`. Requires `PYEG_LIVE_EGERIA=1` (see
`tests/README.md`).

Most files here don't use `pytest` fixtures directly — each defines a
`*ScenarioTester` class with individual `scenario_*` methods, a
`run_all_scenarios()` driver, and its own teardown/cleanup of created test
elements, then a single `test_*` pytest function asserts none of the
scenarios failed.

`run_scenario_tests.py` is a standalone runner (not a pytest entry point)
that discovers and runs every `test_*_scenarios.py` file, printing a
combined summary table — useful for a full-suite smoke run outside pytest.

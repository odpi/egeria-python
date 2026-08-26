<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests/dr-egeria-command-tests

Markdown files exercising every Dr.Egeria command family (`dr_test_*.md`,
one file per family — Action Author, Collections, Curation, Data Designer,
Design Patterns, External References, Feedback, Glossary, Governance,
Projects, Reports, Solution Architect, Dashboard Sheets, Digital Products —
plus `dr_test_new_commands.md` for commands still being shaken out and
`dr_test_collections_mean.md` for deliberately-malformed/error-path input).

Run with:
```
python run_dr_tests.py            # --validate only, no writes
python run_dr_tests.py --process  # also --process (writes to Egeria)
```

`run_dr_tests.py` uses absolute paths for these fixtures (self-contained,
reviewable in a normal git diff) rather than resolving through the
configured Dr.Egeria inbox path — see its own docstring for why (migrated
from an earlier version under `tests/scenario-tests/` that mixed fixtures
into the working `sample-data/egeria-inbox/` scratch folder). Output goes
to `dr_test_results.txt` and `logs/`.

When adding a new command family or a command to an existing family, add
markdown examples to the matching `dr_test_*.md` file here so
`--process` coverage stays current.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests

```bash
pytest tests/                          # all unit/fake tests, no live server
PYEG_LIVE_EGERIA=1 pytest tests/       # include live-server tests
pytest -m unit                         # filter by marker: unit | integration | slow | auth | format_sets | mcp
```

Note: `--live-egeria` as a CLI flag is documented in some places (e.g. the
root `CLAUDE.md`) but isn't currently registered as a pytest option in any
active `conftest.py` — `PYEG_LIVE_EGERIA=1` is the form that actually
works today.

`asyncio_mode = auto` (`pytest.ini`) — async test functions need no
event-loop boilerplate.

| Folder | Contents |
|---|---|
| `micro-tests/` | Unit/formatter/MCP tests — no live Egeria server required. |
| `functional-tests/` | Per-OMVS-client tests (one file per `pyegeria/omvs/*.py` module), live server. |
| `scenario-tests/` | Full-lifecycle scenarios (Create → Link → Delete) exercising multiple methods/relationships together, live server. |
| `dr-egeria-command-tests/` | Markdown files exercising every Dr.Egeria command family, run via `dr_egeria <file> --process`. |

Each OMVS module has a corresponding test file in its matching folder —
add new SDK method tests to `functional-tests/`, new command tests to
`dr-egeria-command-tests/`, and pure-logic/no-server tests to
`micro-tests/`.

Live-server tests assume a reachable Egeria view server at
`https://localhost:9443`, view server name `qs-view-server`, user
`erinoverview`/`secret` (see `PYEGERIA_ISSUES.md`'s header for the same
convention used in its repro snippets).

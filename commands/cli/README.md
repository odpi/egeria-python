<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# commands/cli

The `hey_egeria*` command-line entry points — see `commands/README.md`
for the overall CLI organization (`cat`/`my`/`ops`/`tech` role-based
widget groups this dispatches into).

| File | Role |
|---|---|
| `egeria.py` | The main `hey_egeria` entry point — a `click`-based CLI (with a `trogon`-powered `tui` subcommand for a forms-based interface) that dispatches to the role-based command groups. |
| `egeria_ops.py` | `hey_egeria_ops` — operations-focused entry point. |
| `egeria_login_tui.py` | Standalone login TUI screen, reused by the other entry points. |
| `ops_config.py` | Configuration for the ops CLI. |
| `txt_custom_v2.tcss` | Textual CSS styling for the TUI screens. |

Entry points are registered in the repo root `pyproject.toml`'s
`[project.scripts]` section.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Operations commands

Commands for watching and operating an Egeria deployment: platforms, servers, the integration daemon, the
engine host and archives. Most are reached through `hey_egeria_ops` (and `hey_egeria`), and many also have
their own console script.

## Status displays

`monitor_*` is a live display that refreshes; `list_*` is the same information as a paged list.

| Module | Shows | Console scripts |
|---|---|---|
| `monitor_platform_status.py` | The cataloged platforms and their servers | `monitor_platform_status` |
| `monitor_server_status.py` | The status of every registered server across the platforms | `monitor_server_status` |
| `monitor_server_startup.py` | Server start-up status | `monitor_server_startup` |
| `monitor_daemon_status.py` | The integration daemon and its connectors | `monitor_daemon_status`, `list_daemon_status` |
| `monitor_engine_status.py` | The governance engines on the engine host | `monitor_engine_status`, `list_engine_status` |
| `monitor_engine_activity.py` | Engine actions | `monitor_engine_activity`, `list_engine_activity` |
| `monitor_active_engine_activity.py` | Engine actions still running | `monitor_active_engine_activity`, `list_active_engine_activity` |
| `list_catalog_targets.py` | An integration connector's catalog targets (`hey_egeria_ops show integrations targets <connector>`) | `list_catalog_targets` |
| `list_archives.py` | The open metadata archives loaded | `list_archives` |

## Actions

| Module | Does | How to run it |
|---|---|---|
| `gov_server_actions.py` | Start and stop an OMAG server; ask the engine host to reload its governance engine configuration; add, update and remove an integration connector's catalog targets | `hey_egeria_ops tell servers start --server <name>` / `stop --server <name>`; `hey_egeria_ops tell engine-host refresh [--engine-host-guid <guid>] [--engine <name>]`; `hey_egeria_ops tell integration-daemon add-target` / `update-target` / `remove-target` |
| `refresh_integration_daemon.py` | Refresh integration connectors | `refresh_integration_daemon` |
| `restart_integration_daemon.py` | Restart integration connectors | `restart_integration_daemon` |
| `load_archive.py` | Load an open metadata archive into a server | `load_archive` |

A server is named by its display name (for example `qs-engine-host`) and found by its resource name,
`<organization name>.<server name>`; `--organization-name` defaults to the configured organization.

## Legacy

- `table_integ_daemon_status.py`: an older integration-daemon status table, still exported as
  `commands.table_integ_daemon_status`; `monitor_daemon_status.py` is the current display.
- `x_engine_actions.py`: older start/stop/refresh commands, kept for reference; use `gov_server_actions.py`.

----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# commands/deprecated

Standalone scripts kept for reference but superseded by commands
integrated into the main `hey_egeria` CLI (`commands/cli/`,
`commands/tech/`) — not installed as entry points, not maintained.

- `list_data_designer.py` — listing categories/terms; superseded by the
  `hey_egeria cat show data_designer` command group.
- `list_data_structures_full.py` — listing data structures.

Don't build new functionality on these; use the equivalent `hey_egeria`
subcommand instead.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# commands/deprecated

Standalone scripts kept for reference but superseded by commands
integrated into the main `hey_egeria` CLI (`commands/cli/`,
`commands/tech/`) — not installed as entry points, not maintained.

Nothing is kept here at the moment. `list_data_designer.py` (superseded by the `hey_egeria cat show data_designer`
command group) and `list_data_structures_full.py` were deleted in PY-36: neither parsed, and nothing imported them or
named them as an entry point (only commented-out lines in pyproject.toml, which pointed at `commands.cat`).

Don't build new functionality on these; use the equivalent `hey_egeria`
subcommand instead.

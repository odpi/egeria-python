<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# md_processing/data

- `compact_commands/` — the compact command JSON specs, system of record
  for every Dr.Egeria command's attributes/bundles/commands (own
  `README.md`; **edit via the Dr.Egeria Spec Editor's REST API, not by
  hand** — see the root `CLAUDE.md`'s "Dr.Egeria Spec Editor" section).
- `compact_commands_backup/` — a backup snapshot of `compact_commands/`
  (own `README.md`).
- `generated_format_sets.json` — a JSON export/snapshot of the
  `{Type}-DrE-{Basic|Advanced}` report specs, written by
  `commands/tech/gen_report_specs.py` (run via `refresh_specs`) alongside
  its other output: the literal Python `generated_format_sets` dict in
  `pyegeria/view/base_report_formats.py`, which is what's actually loaded
  at runtime — this JSON file is not read back in by anything, it's a
  by-product snapshot. Do not hand-edit either.

After editing a compact command spec, run `refresh_specs` to regenerate
`generated_format_sets.json` and `base_report_formats.py`.

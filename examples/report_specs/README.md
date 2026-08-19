<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# examples/report_specs

Sample `FormatSet` registry JSON files, used by
`examples/format_sets_save_load_example.py` to demonstrate saving/loading
custom report specs (`pyegeria.view.output_formatter`).

- `all_format_sets.json` — a full exported registry.
- `custom_format_sets.json` — a small hand-authored set of custom `FormatSet`s.
- `subset_format_sets.json` — a filtered subset, for testing selective load.

These are example/fixture data, not the live registry — the real one is
generated at `md_processing/data/generated_format_sets.json` plus the
hand-maintained `base_report_specs` in
`pyegeria/view/base_report_formats.py`.

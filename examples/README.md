<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# examples

Standalone, runnable example scripts showing pyegeria SDK usage against a
live Egeria server (Coco Pharmaceuticals demo data unless noted) — these
are not part of the test suite; run them directly with `python
examples/<script>.py` after adjusting connection settings (or via a local
`.env`).

| Script | Demonstrates |
|---|---|
| `audit_coco_users.py`, `prime_user.py` | Actor/user-identity setup and auditing. |
| `define_coco_sales_regions.py` | Creating a location/region hierarchy. |
| `jacquard_data_sets.py`, `test_jacquard_data_sets.py`, `test_jacquard_data_sets_scenarios.py`, `Egeria-jacquard-data-sets.http` | A worked data-set cataloging example, with both a Python script and raw `.http` requests covering the same scenario. |
| `GeoSpatial Products Example.py` | Digital product catalog example. |
| `format_sets_save_load_example.py`, `output_formats_example.py` | Saving/loading custom report `FormatSet`s and generating output in different formats. |
| `extract_attribute_test.py` | Small standalone parser/extraction check. |

Subdirectories:
- `doc_samples/` — worked examples referenced from `docs/output-formats-and-report-specs.md`.
- `report_specs/` — sample `FormatSet` JSON files (`all_format_sets.json`, `custom_format_sets.json`, `subset_format_sets.json`) for `format_sets_save_load_example.py`.
- `Jupyter Notebooks/` — notebook versions of some of the above (own `README.md`).
- `surveys/` — survey/discovery examples (own `README.md`).

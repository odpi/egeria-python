<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# md_processing/md_processing_utils

Shared parsing, body-building, and constant/config helpers used by
`md_processing/v2/`'s processors.

| File | Role |
|---|---|
| `md_processing_constants.py` | `COLLECTION_SUBTYPES`, `PROJECT_SUBTYPES`, `COMMAND_DEFINITIONS`, verb groups (`LINK_VERBS`, `CREATE_VERBS`, ...), `build_command_variants()`/`get_command_spec()`/`resolve_command_spec()` — command-name resolution and variant generation. |
| `common_md_utils.py` | Body builders — `set_element_prop_body()` (the base inner-properties builder every domain helper calls) plus domain-specific ones (`set_collection_manager_body`, `set_actor_manager_prop_body`, `set_gov_prop_body`, `set_data_field_body`, `set_rel_prop_body`, `set_delete_rel_request_body`, ...). |
| `common_md_proc_utils.py` | Older/broader processing utilities predating the v2 rewrite; still used by some shared helpers. |
| `compact_loader.py` | Loads compact command JSON specs from `md_processing/data/compact_commands/` into `COMMAND_DEFINITIONS`. |
| `compact_spec_validator.py` | Structural validation for compact command JSON (bundle-chain resolution, unknown-attribute checks, duplicate-name checks) — the same logic the Dr.Egeria Spec Editor's REST API runs on every edit; also exposed as the `validate_compact_specs` CLI tool. |
| `extraction_utils.py` | Lower-level markdown extraction helpers used by `v2/extraction.py`. |
| `determine_width.py` | Terminal-width detection for console output formatting. |

To add a new `Referenceable`-level property available to every command,
add it once to `set_element_prop_body()` in `common_md_utils.py` rather
than each domain helper individually.

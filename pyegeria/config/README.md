<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# pyegeria/config

Contains a single file, `dr_egeria_reports.py`.

**This appears to be a stale, orphaned copy** of `pyegeria/view/dr_egeria_reports.py`
(same size, near-identical content — a `diff` finds only minor content
drift between the two, e.g. one `ActionParameter.spec_params` entry using
`metadata_element_types: [...]` here vs. `metadata_element_type: ...` in
the `view/` copy). Nothing in the codebase imports from
`pyegeria.config.dr_egeria_reports` — `grep -rn "from pyegeria.config"`
only turns up references to `pyegeria.config.settings` (the Pydantic
settings object, defined in `pyegeria/core/config.py`, not this
directory) and `pyegeria/core/load_config.py`'s docstring, which describes
itself as re-exporting from "pyegeria.config" as a *concept*, not this
literal path.

If you're looking for the actual config-loading logic, see
`pyegeria/core/config.py`/`pyegeria/core/load_config.py`. If you're
looking for report specs, see `pyegeria/view/dr_egeria_reports.py` and
`pyegeria/view/base_report_formats.py`. This directory's file is very
likely safe to delete, but hasn't been removed here since that wasn't
this pass's purpose — flagging it for whoever next touches this area.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# sample-data

Sample/demo data and markdown files used by examples, manual testing, and
Dr.Egeria's inbox/outbox workflow. Not part of the installed package.

- `egeria-inbox/` — markdown files ready to be processed by
  `dr_egeria <file> --process` (Dr.Egeria's "inbox" convention); processed
  output is written back as `processed-*.md`.
- `egeria-outbox/` — output/generated artifacts from prior processing runs.
- `question-spec-install/` — a large set of markdown command files used to
  bootstrap a demo/dev Egeria server with sample content (glossaries,
  collections, actor profiles, etc.) via Dr.Egeria; its own
  `dr-egeria-outbox/` subfolder holds the processing output.
- `templates/` — generated Dr.Egeria markdown command templates (own `README.md`).
- `logs/` — log output from local runs.
- `apis.csv`, `callie.json`, `erin-profile.json`, `gary_team.json` — sample
  reference/demo data files used by various examples and tests.

Files here are working data, not documentation — expect churn and
generated content (`processed-*.md`, `debug_log.log`) as a normal
byproduct of running Dr.Egeria locally.

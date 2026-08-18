<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# sample-data/question-spec-install

A large set of markdown command files that bootstrap a demo/dev Egeria
server with a broad sample of content — glossaries, collections, actor
profiles/roles, agreements, business capabilities, asset types, catalog
targets, and more — one file (or numbered group, e.g.
`00_perspectives.md`) per content area, meant to be processed roughly in
order.

Process with:
```
dr_egeria <file> --process
```

`dr-egeria-outbox/` holds the output from a prior processing run.

This is demo/bootstrap data for setting up a server with realistic sample
content, not a test fixture set — see `tests/dr-egeria-command-tests/`
for the actual command-coverage test files.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# tests/functional-tests

Per-OMVS-client tests — one `test_<module>.py` file per matching
`pyegeria/omvs/<module>.py`, exercising each client's methods against a
live Egeria view server (`PYEG_LIVE_EGERIA=1`, see `tests/README.md`).

Adding a new OMVS client or method: add its test cases to the matching
file here (create one named after the module if it doesn't exist yet) —
this is where "does the call actually work against a real server" is
verified, as opposed to `tests/micro-tests/` (pure logic, fake clients).

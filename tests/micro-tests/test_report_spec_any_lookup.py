# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for ISSUE-67: `get_report_spec_match`'s handling of a
`select_report_spec(kind, "ANY")` result did a reverse lookup by
heading+description text, which is ambiguous whenever two FormatSets share
identical heading/description text (confirmed live: "Collections" and
"BasicCollections" both use "Common Collection Information"/"Attributes
generic to all Collections.") -- the wrong FormatSet could be silently
resolved, returning its (possibly much narrower) formats list with no
error. Fixed by having select_report_spec's "ANY" branch carry the
resolved registry key through as "_report_spec_name", and having
get_report_spec_match prefer an exact lookup via that key.

Also covers the "Terms" alias added to "Glossary-Terms" (was resolving to
None with no error for any caller using the pre-rename bare name).
"""
from pyegeria.view.base_report_formats import (
    select_report_spec,
    get_report_spec_match,
    report_specs,
)


def test_any_lookup_carries_resolved_name():
    fmt = select_report_spec("Collections", "ANY")
    assert fmt is not None
    assert fmt.get("_report_spec_name") == "Collections"


def test_ambiguous_heading_description_pair_exists_as_documented():
    # Confirms the actual ambiguity this fix guards against still exists in
    # the registry (i.e. this test would have caught the original bug) --
    # if this ever stops being true the test itself should be revisited,
    # not silently left green for the wrong reason.
    matches = [
        k for k, v in report_specs.items()
        if v.heading == "Common Collection Information"
        and v.description == "Attributes generic to all Collections."
    ]
    assert len(matches) >= 2
    assert "Collections" in matches


def test_get_report_spec_match_resolves_correct_format_set_despite_ambiguity():
    fmt = select_report_spec("Collections", "ANY")
    matched = get_report_spec_match(fmt, "TABLE")
    assert "TABLE" in matched["formats"]["types"]


def test_get_report_spec_match_falls_back_to_text_match_without_resolved_name():
    # Backward compatibility: a hand-built or pre-fix-saved dict without
    # "_report_spec_name" still resolves via the legacy heading+description
    # match (ambiguous, but not broken -- same behavior as before this fix
    # for any caller that never had the key in the first place).
    fmt = select_report_spec("Collections", "ANY")
    fmt.pop("_report_spec_name", None)
    matched = get_report_spec_match(fmt, "TABLE")
    assert "formats" in matched


def test_terms_alias_resolves_glossary_terms():
    fmt = select_report_spec("Terms", "LIST")
    assert fmt is not None
    assert fmt.get("target_type") in ("Term", "Terms", None)

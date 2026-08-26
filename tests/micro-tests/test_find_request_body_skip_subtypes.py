# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-55: Egeria PR #9215 (odpi/egeria) added exclude-list ("NOT") semantics
for metadataElementSubtypeNames via a new skipSubtypes boolean on QueryOptions.
Confirms pyegeria's FindRequestBody model round-trips the new field correctly
through the validated path (any caller going through
FindRequestBody.model_validate()/TypeAdapter -- e.g.
ClassificationExplorer._async_find_root_elements -- would otherwise have it
silently dropped by PyegeriaModel's extra='ignore', same bug class as
ISSUE-62/63).

No live server needed for these; see PYEGERIA_ISSUES.md ISSUE-55 for the
separate live confirmation performed against a running server (both the
raw-dict pass-through path and the validated FindRequestBody path correctly
exclude the named subtype when skipSubtypes=true).
"""
from pyegeria.models.models import FindRequestBody, GetRequestBody


def test_find_request_body_accepts_skip_subtypes_true():
    body = FindRequestBody.model_validate({
        "class": "FindRequestBody",
        "metadataElementTypeName": "Referenceable",
        "metadataElementSubtypeNames": ["GlossaryTerm"],
        "skipSubtypes": True,
    })
    assert body.skip_subtypes is True
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert dumped["skipSubtypes"] is True
    assert dumped["metadataElementSubtypeNames"] == ["GlossaryTerm"]


def test_find_request_body_skip_subtypes_defaults_to_none_not_dropped_as_unknown():
    # Without skip_subtypes explicitly set, the field must still exist on the
    # model (not silently absorbed by extra='ignore') -- default None, which
    # exclude_none=True correctly omits from the wire body (matches Egeria's
    # own server-side default of false when the field is absent).
    body = FindRequestBody.model_validate({
        "class": "FindRequestBody",
        "metadataElementTypeName": "Referenceable",
    })
    assert body.skip_subtypes is None
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert "skipSubtypes" not in dumped


def test_find_request_body_skip_subtypes_false_is_explicit_in_wire_body():
    body = FindRequestBody.model_validate({
        "class": "FindRequestBody",
        "skipSubtypes": False,
    })
    assert body.skip_subtypes is False
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert dumped["skipSubtypes"] is False


def test_get_request_body_still_has_legacy_metadata_element_subtype_names_field():
    # GetRequestBody's field is now vestigial server-side (Egeria PR #9215
    # moved it to QueryOptions), but pyegeria keeps it rather than removing it
    # -- confirm it still round-trips without error rather than being dropped
    # as an unknown key, since removing it entirely was deliberately not done
    # (see the field's own comment in models.py).
    body = GetRequestBody.model_validate({
        "class": "GetRequestBody",
        "metadata_element_subtype_names": ["GlossaryTerm"],
    })
    assert body.metadata_element_subtype_names == ["GlossaryTerm"]

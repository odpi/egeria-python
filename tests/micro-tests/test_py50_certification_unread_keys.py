"""PY-50: Link/Update Certification sent entitlements, obligations and restrictions inside CertificationProperties, which does not
read them (Egeria drops unknown keys silently), so a person who typed them got no error and no value. The Certification
relationship has no home for them: they are properties of the Certification TYPE (CertificationTypeProperties), as they are
of License/LicenseType. So the command is now REFUSED, loudly, naming where they belong; nothing is sent. License is unchanged.
No live server: fake clients capture the body."""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor

GUID = "aaaaaaaa-0000-0000-0000-000000000001"
THREE = ("Entitlements", "Obligations", "Restrictions")


class _Client:
    def __init__(self):
        self.calls = []

    async def _async_add_certification_to_element(self, type_guid, element_guid, body):
        self.calls.append(("certification", body))
        return {"guid": "rel-1"}

    async def _async_add_license_to_element(self, type_guid, element_guid, body):
        self.calls.append(("license", body))
        return {"guid": "rel-1"}

    async def _async_update_certification(self, rel_guid, body):
        self.calls.append(("certification", body))

    async def _async_update_license(self, rel_guid, body):
        self.calls.append(("license", body))


def _processor(verb, object_type, attributes):
    client = _Client()
    cmd = DrECommand(verb=verb, object_type=object_type, attributes={}, raw_block=f"# {verb} {object_type}")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.canonical_object_type = object_type
    p.get_command_spec = lambda: {"OM_TYPE": object_type}
    p.parsed_output = {"qualified_name": f"{object_type}::t::1", "attributes": attributes}
    return p, client


def _attrs(verb, object_type, **extra):
    id_key = "Certificate GUID" if object_type == "Certification" else "License GUID"
    base = {id_key: {"value": GUID if verb == "Update" else "ID-1"}}
    if verb == "Link":
        base.update({f"{object_type} Type": {"guid": "type-guid"}, "Referenceable": {"guid": "el-guid"}})
    base.update(extra)
    return base


@pytest.mark.parametrize("attr", THREE)
@pytest.mark.parametrize("verb", ["Link", "Update"])
@pytest.mark.asyncio
async def test_a_certification_with_an_attribute_it_cannot_hold_is_refused_naming_the_home(verb, attr):
    p, client = _processor(verb, "Certification", _attrs(verb, "Certification", **{attr: {"value": {"read": "yes"}}}))
    with pytest.raises(ValueError) as exc:
        await p.apply_changes()
    words = str(exc.value)
    assert attr in words and "Certification Type" in words and "nothing was sent" in words.lower()
    assert client.calls == []                                   # nothing reached Egeria


@pytest.mark.parametrize("verb", ["Link", "Update"])
@pytest.mark.asyncio
async def test_a_certification_without_them_is_sent_and_carries_none_of_the_three(verb):
    p, client = _processor(verb, "Certification", _attrs(verb, "Certification", **{"Conditions": {"value": "renewed"}}))
    await p.apply_changes()
    props = [b["properties"] for _k, b in client.calls][0]
    assert props["conditions"] == "renewed"
    assert not {"entitlements", "obligations", "restrictions"} & set(props)


@pytest.mark.parametrize("blank", [None, "", {}])
@pytest.mark.asyncio
async def test_an_attribute_left_blank_is_not_a_refusal(blank):
    p, client = _processor("Link", "Certification", _attrs("Link", "Certification", Entitlements={"value": blank}))
    await p.apply_changes()
    assert client.calls


@pytest.mark.parametrize("verb", ["Link", "Update"])
@pytest.mark.asyncio
async def test_license_still_sends_the_three_because_license_reads_them(verb):
    p, client = _processor(verb, "License", _attrs(verb, "License", **{a: {"value": {"k": "v"}} for a in THREE}))
    await p.apply_changes()
    props = [b["properties"] for _k, b in client.calls][0]
    assert {"entitlements", "obligations", "restrictions"} <= set(props)


def test_the_properties_table_says_why_certification_cannot_hold_them():
    cert = set(PROPERTIES_CLASS_FIELDS["CertificationProperties"][1])
    assert not cert & {"entitlements", "obligations", "restrictions"}
    assert {"entitlements", "obligations", "restrictions"} <= set(PROPERTIES_CLASS_FIELDS["CertificationTypeProperties"][1])
    assert {"entitlements", "obligations", "restrictions"} <= set(PROPERTIES_CLASS_FIELDS["LicenseProperties"][1])

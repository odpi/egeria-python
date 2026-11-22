"""PY-43: the Dr.Egeria Link/Update Certification and License commands sent startDate and endDate. Egeria's
CertificationProperties and LicenseProperties read coverageStart and coverageEnd and drop any other key silently
(ignoreUnknown), so the dates a user typed were lost. The attribute names the user types ("Start Date",
"End Date") are unchanged; only the keys sent change. No live server: fake clients capture the body."""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor

START, END = "2030-01-01T00:00:00", "2031-01-01T00:00:00"
DATES = {"Start Date": {"value": START}, "End Date": {"value": END}}


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


def _sent_properties(client):
    props = [b["properties"] for _kind, b in client.calls]
    assert props, "no call reached the client"
    return props[0]


@pytest.mark.parametrize("object_type,props_class", [("Certification", "CertificationProperties"),
                                                     ("License", "LicenseProperties")])
@pytest.mark.parametrize("verb", ["Link", "Update"])
@pytest.mark.asyncio
async def test_dates_are_sent_as_the_keys_egeria_reads(verb, object_type, props_class):
    attrs = dict(DATES)
    if verb == "Link":
        attrs.update({f"{object_type} Type": {"guid": "type-guid"}, "Referenceable": {"guid": "el-guid"},
                      ("Certificate GUID" if object_type == "Certification" else "License GUID"): {"value": "ID-1"}})
    else:
        attrs[("Certificate GUID" if object_type == "Certification" else "License GUID")] = {
            "value": "aaaaaaaa-0000-0000-0000-000000000001"}
    p, client = _processor(verb, object_type, attrs)

    await p.apply_changes()

    props = _sent_properties(client)
    assert props["class"] == props_class
    assert props["coverageStart"] == START and props["coverageEnd"] == END
    assert "startDate" not in props and "endDate" not in props
    read = set(PROPERTIES_CLASS_FIELDS[props_class][1])
    assert {"coverageStart", "coverageEnd"} <= read                      # the keys sent are ones the class reads


@pytest.mark.asyncio
async def test_no_date_typed_is_no_date_sent():
    p, client = _processor("Update", "License", {"License GUID": {"value": "aaaaaaaa-0000-0000-0000-000000000001"}})
    await p.apply_changes()
    props = _sent_properties(client)
    assert "coverageStart" not in props and "coverageEnd" not in props
    assert "startDate" not in props and "endDate" not in props

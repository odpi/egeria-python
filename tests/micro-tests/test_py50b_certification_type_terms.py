"""PY-50 follow-up: where Entitlements, Obligations and Restrictions DO belong for a certification: the Certification TYPE.
Create Certification Type already lists them (the compact spec's "Terms and Conditions" bundle) and its processor already sends
them in CertificationTypeProperties (set_gov_prop_body, ISSUE-157); these tests pin that, so PY-50's refusal never points at a
command that cannot take them. There is no "Update Certification Type" command (Create Certification Type is not an upsert), so
the refusal must not name one. No live server: a fake client captures the body."""
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from md_processing.md_processing_utils.parse_compact_export import resolve_bundle_chain
from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceProcessor, refuse_certification_attributes_it_cannot_hold

SPEC = Path(__file__).resolve().parents[2] / "md_processing" / "data" / "compact_commands" / "commands_governance_officer_compact.json"
THREE = ("Entitlements", "Obligations", "Restrictions")


class _Client:
    def __init__(self):
        self.create_body = None

    async def _async_create_governance_definition(self, body: dict):
        self.create_body = body
        return "11111111-1111-1111-1111-111111111111"


def _spec():
    return json.loads(SPEC.read_text())


def test_create_certification_type_lists_the_three_attributes_through_its_bundle():
    d = _spec()
    cmd = d["commands"]["Create Certification Type"]
    own = [a for b in resolve_bundle_chain(cmd["bundle"], d["bundles"]) for a in d["bundles"].get(b, {}).get("own_attributes", [b])]
    assert all(a in resolve_bundle_chain(cmd["bundle"], d["bundles"]) for a in THREE) or all(a in own for a in THREE)
    assert cmd["OM_TYPE"] == "CertificationType"


def test_there_is_no_update_certification_type_command_so_no_words_may_name_one():
    d = _spec()
    assert "Update Certification Type" not in d["commands"]
    assert d["commands"]["Create Certification Type"]["upsert"] is False
    with pytest.raises(ValueError) as exc:
        refuse_certification_attributes_it_cannot_hold("Link", {"Entitlements": {"value": {"k": "v"}}})
    words = str(exc.value)
    assert "Update Certification Type" not in words
    assert "Create Certification Type" in words and "Certification Type" in words


async def _create(attributes):
    client = _Client()
    cmd = DrECommand(verb="Create", object_type="Certification Type", attributes={}, raw_block="# Create Certification Type")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p._sync_rels = AsyncMock(return_value=None)
    p.canonical_object_type = "Certification Type"
    p.get_command_spec = lambda: {"OM_TYPE": "CertificationType"}
    p.parsed_output = {"attributes": {"Display Name": {"value": "PY50 cert type"}, **attributes},
                       "qualified_name": "CertificationType::PY50::1.0"}
    await p.apply_changes()
    return client.create_body["properties"]


@pytest.mark.asyncio
async def test_create_certification_type_sends_the_three_in_certification_type_properties():
    props = await _create({"Entitlements": {"value": {"use": "permitted"}}, "Obligations": {"value": {"renew": "annually"}},
                           "Restrictions": {"value": {"export": "no"}}})
    assert props["class"] == "CertificationTypeProperties"
    assert props["entitlements"] == {"use": "permitted"}
    assert props["obligations"] == {"renew": "annually"}
    assert props["restrictions"] == {"export": "no"}


@pytest.mark.asyncio
async def test_a_blank_attribute_sends_nothing_not_an_empty_value():
    props = await _create({"Entitlements": {"value": None}})            # one blank, two not given at all
    assert not {"entitlements", "obligations", "restrictions"} & set(props)


# ── the Link/Update Certification commands no longer offer what they refuse (Dan, via the Coordinator) ──────────────

TEMPLATES = Path(__file__).resolve().parents[2] / "sample-data" / "templates"


def test_link_and_update_certification_no_longer_list_the_three_but_license_still_does():
    d = _spec()
    for name in ("Link Certification", "Update Certification"):
        assert not set(THREE) & set(d["commands"][name]["custom_attributes"]), name
    for name in ("Link License", "Update License"):
        assert set(THREE) <= set(d["commands"][name]["custom_attributes"]), name
    assert set(THREE) <= set(d["attribute_definitions"])                  # the shared definitions stay: License and the type use them


def test_the_generated_templates_agree_with_the_spec():
    seen = 0
    for level in ("advanced", "basic"):
        for name in ("Link_Certification.md", "Update_Certification.md"):
            f = TEMPLATES / level / "Governance Officer" / name
            if f.exists():
                seen += 1
                text = f.read_text(encoding="utf-8")
                assert [a for a in THREE if f"### {a}" in text] == [], f"{f} still offers fields its command refuses"
        for name in ("Link_License.md", "Update_License.md"):
            f = TEMPLATES / level / "Governance Officer" / name
            if f.exists():
                text = f.read_text(encoding="utf-8")
                assert all(f"### {a}" in text for a in THREE), f"{f} lost fields License reads"
    assert seen >= 2


def test_create_certification_type_still_offers_the_three_in_its_template():
    f = TEMPLATES / "advanced" / "Governance Officer" / "Create_Certification_Type.md"
    text = f.read_text(encoding="utf-8")
    assert all(f"### {a}" in text for a in THREE)

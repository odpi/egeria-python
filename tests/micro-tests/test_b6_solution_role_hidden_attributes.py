# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
B6: Create Solution Role hides Role Domain Identifier and Title (SolutionActorRoleProperties has neither) but still accepts them so older documents keep working.
"""

import pytest
from md_processing.md_processing_utils.md_processing_constants import get_command_spec, load_commands
from md_processing.v2.extraction import UniversalExtractor
from md_processing.v2.parsing import AttributeFirstParser
from md_processing.md_processing_utils.common_md_utils import set_solution_architect_body
from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing import templates as tpl

pytestmark = pytest.mark.unit
HIDDEN = ("Role Domain Identifier", "Title")
COMMAND = "Create Solution Role"


class _NoValidValues:
    def __init__(self):
        self.valid_metadata = self

    async def _async_validate_metadata_value(self, prop_name, type_name, value):
        return None

    async def _async_validate_metadata_map_value(self, prop_name, type_name, map_name, value):
        return None

    async def _async_get_valid_metadata_values(self, prop_name, type_name=None):
        return []


async def _parse(attrs: dict) -> dict:
    if not get_command_spec(COMMAND):
        load_commands()
    body = "\n\n".join(f"### {k}\n{v}" for k, v in attrs.items())
    cmd = UniversalExtractor(f"## {COMMAND}\n\n{body}\n").extract_commands()[0]
    return await AttributeFirstParser(cmd, client=_NoValidValues(), directive="validate").parse()


@pytest.fixture(autouse=True)
def _clear_template_caches():
    tpl._root_and_source.cache_clear()
    tpl._index.cache_clear()
    yield
    tpl._root_and_source.cache_clear()
    tpl._index.cache_clear()


def test_hidden_attributes_are_invisible_but_still_declared():
    load_commands()
    spec = get_command_spec(COMMAND)
    defs = spec["attribute_definitions"]
    for name in HIDDEN:
        assert defs[name]["level"] == "Invisible"
    names = {a["name"] if "name" in a else next(iter(a)) for a in spec["Attributes"]}
    assert set(HIDDEN) <= names


def test_role_domain_identifier_has_no_default():
    load_commands()
    d = get_command_spec(COMMAND)["attribute_definitions"]["Role Domain Identifier"]
    assert d["default_value"] == ""
    assert d["min_cardinality"] == 0


async def test_old_document_with_hidden_attributes_still_parses_and_reports_not_applied():
    out = await _parse({"Display Name": "Old Role", "Title": "Chief Steward", "Role Domain Identifier": "Data", "Scope": "Enterprise"})
    assert out["valid"] is True
    assert out["errors"] == []
    a = out["attributes"]
    assert a["Title"]["value"] == "Chief Steward"
    assert a["Role Domain Identifier"]["raw_value"] == "Data"
    props = set_solution_architect_body("SolutionActorRole", "QN", a)
    assert "title" not in props
    assert "domainIdentifier" not in props
    notes = not_applied_notes(a)
    assert "not applied: Title: SolutionActorRoleProperties has no title property" in notes
    assert "not applied: Role Domain Identifier: SolutionActorRoleProperties has no domainIdentifier property" in notes


async def test_role_without_hidden_attributes_has_no_not_applied_note():
    out = await _parse({"Display Name": "New Role", "Scope": "Enterprise"})
    assert out["valid"] is True
    a = out["attributes"]
    for name in HIDDEN:
        assert (a.get(name) or {}).get("value") in (None, "")
    set_solution_architect_body("SolutionActorRole", "QN", a)
    assert not_applied_notes(a) == []


@pytest.mark.parametrize("name, key", [("Title", "title"), ("Role Domain Identifier", "domainIdentifier")])
async def test_each_hidden_attribute_alone_gives_only_its_own_note(name, key):
    value = "Data" if name == "Role Domain Identifier" else "Chief Steward"
    out = await _parse({"Display Name": "One Field Role", name: value})
    assert out["valid"] is True
    a = out["attributes"]
    props = set_solution_architect_body("SolutionActorRole", "QN", a)
    assert key not in props
    assert not_applied_notes(a) == [f"not applied: {name}: SolutionActorRoleProperties has no {key} property"]


def test_hidden_attribute_definitions_keep_their_mapping_keys():
    # common_md_utils reads these when reporting the not-applied note; old documents depend on them.
    load_commands()
    d = get_command_spec(COMMAND)["attribute_definitions"]["Role Domain Identifier"]
    assert d["property_name"] == "domainIdentifier"
    assert d["legacy_enum_type"] == "GovernanceDomains"


def test_descriptions_say_accepted_but_not_stored():
    load_commands()
    spec = get_command_spec(COMMAND)
    assert "accepted but not stored" in spec["description"]
    for name in HIDDEN:
        desc = spec["attribute_definitions"][name]["description"]
        assert "accepted but not stored" in desc
        assert "deprecated" not in desc.lower()


@pytest.mark.parametrize("level", tpl.LEVELS)
def test_template_omits_hidden_attributes(level):
    text = tpl.read_template(COMMAND, level, family="Solution Architect")
    assert f"## {COMMAND}" in text
    assert "### Scope" in text
    for name in HIDDEN:
        assert f"### {name}\n" not in text and not text.rstrip().endswith(f"### {name}")

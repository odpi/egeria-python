"""Zone Membership is a Basic attribute with an empty default; empty means "set no zones".

The Basic templates show "### Zone Membership" with no value. A blank heading parses to an
empty list, and it must not clear an element's existing zones on Update (or call Egeria at all).
"""
from __future__ import annotations

import asyncio
import glob
import json
from pathlib import Path

import pytest

from md_processing.md_processing_utils.md_processing_constants import load_commands
from md_processing.v2.parsing import parse_dr_egeria_content
from md_processing.v2.processors import AsyncBaseCommandProcessor

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
COMPACT = ROOT / "md_processing" / "data" / "compact_commands"


def test_zone_membership_is_basic_with_an_empty_default_in_every_family():
    seen = 0
    for path in sorted(COMPACT.glob("*.json")):
        attr = json.loads(path.read_text())["attribute_definitions"].get("Zone Membership")
        if attr is None:
            continue
        seen += 1
        assert attr["level"] == "Basic", path.name
        assert attr["default_value"] == "", path.name
    assert seen == 14


def test_basic_templates_show_zone_membership_without_a_value():
    files = glob.glob(str(ROOT / "sample-data" / "templates" / "basic" / "*" / "Create_Glossary_Term.md"))
    assert files
    text = Path(files[0]).read_text()
    section = text.split("### Zone Membership", 1)[1].split("###", 1)[0]
    assert "Default Value" not in section


def _doc(verb: str, zone_section: str) -> str:
    return (f"## {verb} Glossary\n\n### Display Name\nZone Test Glossary\n\n### Description\nx\n"
            f"{zone_section}\n___\n")


@pytest.mark.parametrize("verb", ["Create", "Update"])
@pytest.mark.parametrize("section, expected", [
    ("", None),                                       # heading absent
    ("\n### Zone Membership\n\n", []),                # heading, no value (the Basic template)
    ("\n### Zone Membership\nquarantine\n", ["quarantine"]),
])
def test_parsing(verb, section, expected):
    load_commands()
    parsed = asyncio.run(parse_dr_egeria_content(_doc(verb, section)))
    zone = parsed[0]["attributes"].get("Zone Membership")
    assert (zone or {}).get("value") == expected


class _Client:
    def __init__(self):
        self.calls = []

    async def _async_add_zone_membership(self, guid, body):
        self.calls.append(("add", guid, body["properties"]["zoneMembership"]))

    async def _async_clear_zone_membership(self, guid, body):
        self.calls.append(("clear", guid))


class _Processor(AsyncBaseCommandProcessor):
    async def apply_changes(self):  # pragma: no cover - not used here
        raise NotImplementedError


def _sync(attributes):
    proc = object.__new__(_Processor)
    proc.client = _Client()
    proc.related_results = []
    asyncio.run(proc._sync_zone_membership("g-1", attributes))
    return proc.client.calls


@pytest.mark.parametrize("attributes", [
    {},                                        # absent
    {"Zone Membership": {"value": []}},        # blank heading
    {"Zone Membership": {"value": None}},
    {"Zone Membership": {"value": ""}},
], ids=["absent", "empty-list", "none", "empty-string"])
def test_empty_zone_membership_sets_and_clears_nothing(attributes):
    assert _sync(attributes) == []


def test_a_zone_list_is_set():
    assert _sync({"Zone Membership": {"value": ["quarantine", "clinical"]}}) == [
        ("add", "g-1", ["quarantine", "clinical"])]

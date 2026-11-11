# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dashboard folders (LD-1): sheets listed by consumer folder, through the walk report specs use.

    RootCollection::DashboardSheets
      DashboardFolder::Consumer::Portal            -> Dashboard::Ops, sub-folder Portal::Exec
        DashboardFolder::Consumer::Portal::Exec    -> Dashboard::Board
      DashboardFolder::Consumer::EgeriaAdvisor     -> Dashboard::Ops (one sheet, two consumers)

The Egeria is dashboard_fake_egeria's (element shapes checked live on 2026-11-09; sheets are written
through the real sheet writer), plus the two collection reads the folder walk makes.
"""
import copy

import pytest

# micro-tests is on sys.path under pytest; the fake's element shapes were checked live on 2026-11-09.
from dashboard_fake_egeria import FakeEgeria

from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
from pyegeria.view import dashboards as dash
from pyegeria.view import egeria_folders as folders
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement

pytestmark = pytest.mark.unit

ROOT = dash.DEFAULT_DASHBOARD_ROOT
PORTAL = "DashboardFolder::Consumer::Portal"
EXEC = PORTAL + "::Exec"
ADVISOR = "DashboardFolder::Consumer::EgeriaAdvisor"


class FolderEgeria(FakeEgeria):
    """FakeEgeria plus CollectionFolder / RootCollection membership, read the way the walk reads it."""

    def __init__(self):
        super().__init__()
        self.members = {}
        self.failing = set()     # GUIDs whose members cannot be read (a genuine error: HTTP 500)
        self.user_id = "erinoverview"

    def folder(self, qn, display=None, type_name="CollectionFolder"):
        guid = self.add_entity(type_name, qn, display or qn.rsplit("::", 1)[-1])
        self.members[guid] = []
        return guid

    def put(self, parent_guid, child_guid):
        self.members[parent_guid].append(child_guid)

    def get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON", **_):
        hits = [self.element(g) for g, e in self.entities.items() if e["props"].get("qualifiedName") == name
                and metadata_element_type in (None, e["type"])]
        return copy.deepcopy(hits) or "No elements found"

    def get_collection_members(self, collection_guid=None, output_format="JSON", **_):
        if collection_guid in self.failing:
            raise RuntimeError("HTTP 500 from the view server")
        return [self.element(g) for g in self.members.get(collection_guid, [])] or "No elements found"


async def _sheet(fake, name):
    await DashboardSheetEgeriaWriter(fake).write_sheet(
        DashboardSheet(name=name, heading=name, placements=[Placement(ref="note", content=f"{name} text")]))
    return fake.by_qn(f"Dashboard::{name}")


@pytest.fixture
async def tree():
    fake = FolderEgeria()
    root = fake.folder(ROOT, type_name="RootCollection")
    portal, exec_, advisor = fake.folder(PORTAL, "Portal"), fake.folder(EXEC, "Exec"), fake.folder(ADVISOR, "EgeriaAdvisor")
    ops, board, loose = await _sheet(fake, "Ops"), await _sheet(fake, "Board"), await _sheet(fake, "Loose")
    fake.put(root, portal)
    fake.put(root, advisor)
    fake.put(portal, ops)
    fake.put(portal, exec_)
    fake.put(exec_, board)
    fake.put(advisor, ops)
    return {"fake": fake, "root": root, "portal": portal, "exec": exec_, "advisor": advisor, "loose": loose}


@pytest.fixture(autouse=True)
def _no_configured_folders(monkeypatch):
    monkeypatch.setenv(dash.DASHBOARD_FOLDERS_ENV, "")
    monkeypatch.delenv(dash.DASHBOARD_ROOT_ENV, raising=False)


# ── listing ──

async def test_no_folders_configured_lists_every_sheet_and_says_so(tree):
    listing = await dash.async_list_dashboard_sheets(tree["fake"])
    assert [s.name for s in listing] == ["Board", "Loose", "Ops"]
    assert listing.notes == [dash.NO_FOLDERS_NOTE]
    assert all(s.folders == [] and s.used_by == [] for s in listing)


async def test_a_consumer_folder_lists_its_sheets_recursively_and_tags_them(tree):
    listing = await dash.async_list_dashboard_sheets(tree["fake"], [PORTAL])
    assert [s.name for s in listing] == ["Board", "Ops"]          # Board is in the Exec sub-folder; Loose in none
    assert all(s.folders == [PORTAL] and s.used_by == ["Portal"] for s in listing)
    assert listing.notes == []
    assert listing.folders == [{"qualifiedName": PORTAL, "status": "read", "reason": None, "sheets": 2}]


async def test_a_sheet_in_two_consumer_folders_is_listed_once_with_both(tree):
    listing = await dash.async_list_dashboard_sheets(tree["fake"], [PORTAL, ADVISOR])
    ops = next(s for s in listing if s.name == "Ops")
    assert [s.name for s in listing].count("Ops") == 1
    assert ops.folders == [PORTAL, ADVISOR] and ops.used_by == ["EgeriaAdvisor", "Portal"]


async def test_a_sub_folder_is_used_by_its_consumer(tree):
    listing = await dash.async_list_dashboard_sheets(tree["fake"], [EXEC])
    assert [(s.name, s.used_by) for s in listing] == [("Board", ["Portal"])]


async def test_the_configured_folders_come_from_the_environment(tree, monkeypatch):
    monkeypatch.setenv(dash.DASHBOARD_FOLDERS_ENV, f" {ADVISOR} , ")
    assert dash.configured_dashboard_folders() == [ADVISOR]
    listing = await dash.async_list_dashboard_sheets(tree["fake"])
    assert [s.name for s in listing] == ["Ops"]


async def test_a_folder_not_found_is_stated_never_an_empty_list(tree):
    listing = await dash.async_list_dashboard_sheets(tree["fake"], ["DashboardFolder::Consumer::Nope", ADVISOR])
    assert [s.name for s in listing] == ["Ops"]                  # the other folder is still read
    assert listing.folders[0]["status"] == "not found"
    assert listing.notes == ["DashboardFolder::Consumer::Nope: not found, or not visible to erinoverview"]


async def test_an_unreadable_folder_is_not_read_with_its_reason(tree):
    tree["fake"].failing.add(tree["portal"])
    listing = await dash.async_list_dashboard_sheets(tree["fake"], [PORTAL])
    assert list(listing) == []
    assert listing.folders[0]["status"] == "not read"
    assert "HTTP 500" in listing.notes[0] and listing.notes[0].startswith(PORTAL)


async def test_an_unreadable_sub_folder_makes_the_folder_partial(tree):
    tree["fake"].failing.add(tree["exec"])
    listing = await dash.async_list_dashboard_sheets(tree["fake"], [PORTAL])
    assert [s.name for s in listing] == ["Ops"]
    assert listing.folders[0]["status"] == "partial"
    assert listing.notes == [f"{PORTAL}: not fully read: {PORTAL} / {EXEC}: HTTP 500 from the view server"]


async def test_the_walk_never_goes_across_to_a_sibling_consumer_or_up_to_the_root(tree):
    fake = tree["fake"]
    fake.put(tree["exec"], tree["advisor"])      # a sibling consumer, filed inside Portal by mistake
    fake.put(tree["exec"], tree["root"])         # and the root
    listing = await dash.async_list_dashboard_sheets(fake, [EXEC])
    assert [s.name for s in listing] == ["Board"]                # not Ops, which only Advisor would add here
    walk = folders.walk_folder(fake, fake.element(tree["exec"]), recursive=True,
                               consumer_prefix=dash.DASHBOARD_CONSUMER_PREFIX)
    reasons = [why for _p, why in walk.not_followed]
    assert "another consumer folder; the walk never goes across" in reasons
    assert "a RootCollection; the walk never goes up to the root" in reasons


async def test_a_cycle_is_read_once(tree):
    fake = tree["fake"]
    fake.put(tree["exec"], tree["portal"])
    listing = await dash.async_list_dashboard_sheets(fake, [PORTAL])
    assert [s.name for s in listing] == ["Board", "Ops"]
    assert listing.folders[0]["status"] == "read"


async def test_the_depth_cap_is_stated(tree):
    fake = tree["fake"]
    parent = tree["exec"]
    for i in range(3):
        child = fake.folder(f"{EXEC}::L{i}")
        fake.put(parent, child)
        parent = child
    deep = await _sheet(fake, "Deep")
    fake.put(parent, deep)
    listing = await dash.async_list_dashboard_sheets(fake, [PORTAL], depth_cap=2)
    assert "Deep" not in [s.name for s in listing]
    assert listing.folders[0]["status"] == "partial"
    assert "depth cap reached (2 levels)" in listing.notes[0]


async def test_only_dashboard_members_count(tree):
    fake = tree["fake"]
    fake.put(tree["portal"], fake.add_entity("Report", "DeployedReport::X", "X"))
    walk = folders.walk_folder(fake, fake.element(tree["portal"]), recursive=True,
                               consumer_prefix=dash.DASHBOARD_CONSUMER_PREFIX, member=dash._is_dashboard_member)
    assert sorted(m["properties"]["qualifiedName"] for m in walk.members) == ["Dashboard::Board", "Dashboard::Ops"]
    assert walk.paths[tree["fake"].by_qn("Dashboard::Board")] == [f"{PORTAL} / {EXEC}"]


# ── the consumer index ──

async def test_the_consumer_index_has_the_spec_index_shape(tree):
    idx = dash.build_dashboard_consumer_index(tree["fake"])
    assert idx["format"] == dash.DASHBOARD_CONSUMERS_FORMAT and idx["root"] == ROOT
    assert idx["status"] == "read" and idx["reason"] is None
    assert idx["index"] == {"Board": ["Portal"], "Ops": ["EgeriaAdvisor", "Portal"]}
    assert [(c["name"], c["status"], c["sheets"]) for c in idx["consumers"]] == [("EgeriaAdvisor", "read", 1),
                                                                                 ("Portal", "read", 2)]


async def test_a_missing_root_is_not_read_never_empty(tree, monkeypatch):
    monkeypatch.setenv(dash.DASHBOARD_ROOT_ENV, "RootCollection::Elsewhere")
    idx = dash.build_dashboard_consumer_index(tree["fake"])
    assert idx["status"] == "not read" and idx["index"] == {} and "RootCollection::Elsewhere" in idx["reason"]


async def test_an_unreadable_consumer_makes_the_index_partial(tree):
    tree["fake"].failing.add(tree["exec"])
    idx = dash.build_dashboard_consumer_index(tree["fake"])
    assert idx["status"] == "partial" and "Portal" in idx["reason"]
    assert idx["index"] == {"Ops": ["EgeriaAdvisor", "Portal"]}

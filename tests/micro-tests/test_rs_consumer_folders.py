"""Report-spec consumer folders, phase 2: recursive consumer-folder sync and the consumer index.

Covers: sub-folders followed inside a consumer folder (and not, by default, inside any other
folder); the cycle guard; the depth cap ("depth cap reached", nothing pruned on a capped walk);
never walking up to the root or across into a sibling consumer; a sub-folder read error keeping
the cached specs; and the consumer index ({label: [consumers]}), including "not read" and
"partial" so that absence is never shown as "used by none". No live Egeria: an in-memory fake.
"""
from __future__ import annotations

import copy
import json

import pytest

import pyegeria.view.egeria_spec_cache as esc
from test_rs_egeria_tier import spec_element, tier  # noqa: F401 -- `tier` is a fixture

pytestmark = pytest.mark.unit

ROOT_QN = esc.DEFAULT_ROOT
PORTAL = "ReportSpecFolder::Consumer::Portal"
ADVISOR = "ReportSpecFolder::Consumer::EgeriaAdvisor"
JUPYTER = "ReportSpecFolder::Consumer::Jupyter"
SCRATCH = "ReportSpecFolder::scratch::Nested"


def _guid(n: int) -> str:
    return f"00000000-0000-0000-0000-{n:012d}"


def folder(qn, guid, display=None, type_name="CollectionFolder"):
    supers = ["Collection", "Referenceable"]
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name, "superTypeNames": supers},
                              "versions": {"version": 1}},
            "properties": {"qualifiedName": qn, "displayName": display or qn.rsplit("::", 1)[-1]}}


class Tree:
    """An in-memory Egeria holding folders, a root and specs; members are by GUID."""

    def __init__(self):
        self.user_id = "erinoverview"
        self.platform_url = "https://localhost:9443"
        self.view_server = "qs-view-server"
        self.by_guid = {}
        self.members = {}
        self.failing = set()   # GUIDs whose members cannot be read
        self.root_error = None
        self.member_reads = []
        self._n = 100

    def add(self, el):
        self.by_guid[el["elementHeader"]["guid"]] = el
        self.members.setdefault(el["elementHeader"]["guid"], [])
        return el

    def new_folder(self, qn, display=None, type_name="CollectionFolder"):
        self._n += 1
        return self.add(folder(qn, _guid(self._n), display, type_name))

    def new_spec(self, label):
        self._n += 1
        return self.add(spec_element(label=label, guid=_guid(self._n), aliases=[]))

    def link(self, parent, child):
        self.members[parent["elementHeader"]["guid"]].append(child)

    def get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON", **_):
        if metadata_element_type == "RootCollection" and self.root_error:
            raise RuntimeError(self.root_error)
        hits = [e for e in self.by_guid.values() if e["properties"]["qualifiedName"] == name
                and (metadata_element_type in (None, e["elementHeader"]["type"]["typeName"]))]
        return copy.deepcopy(hits) or "No elements found"

    def get_collection_members(self, collection_guid=None, output_format="JSON", **_):
        self.member_reads.append(collection_guid)
        if collection_guid in self.failing:
            raise RuntimeError("HTTP 500 from the view server")
        return copy.deepcopy(self.members.get(collection_guid)) or "No elements found"

    def get_collection_by_guid(self, guid, output_format="JSON", **_):
        e = self.by_guid.get(guid)
        return copy.deepcopy(e) if e else "No elements found"


def manifest(tier):
    return json.loads((tier["cache"] / esc.MANIFEST).read_text())


@pytest.fixture
def portal_tree():
    """Portal holds A and the sub-folder Overview; Overview holds B and Overview/Tiles; Tiles holds C."""
    t = Tree()
    portal = t.new_folder(PORTAL, "Portal")
    overview = t.new_folder(PORTAL + "::Overview", "Overview")
    tiles = t.new_folder(PORTAL + "::Overview::Tiles", "Tiles")
    a, b, c = t.new_spec("Spec-A"), t.new_spec("Spec-B"), t.new_spec("Spec-C")
    t.link(portal, a)
    t.link(portal, overview)
    t.link(overview, b)
    t.link(overview, tiles)
    t.link(tiles, c)
    return t, portal, overview, tiles


# ── Recursive sync ──

def test_consumer_folder_sync_follows_sub_folders(tier, portal_tree):
    t, *_ = portal_tree
    report = esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)
    assert sorted(report.added) == ["Spec-A", "Spec-B", "Spec-C"]
    assert report.folders_read == [PORTAL, f"{PORTAL} / {PORTAL}::Overview",
                                   f"{PORTAL} / {PORTAL}::Overview / {PORTAL}::Overview::Tiles"]
    assert not report.depth_cap_reached and not report.skipped
    # A spec in a sub-folder is recorded against the folder that was named (what a tool configures).
    assert manifest(tier)["entries"]["Spec-C"]["folders"] == [PORTAL]
    assert "Folders read (3)" in report.render()


def test_any_other_folder_reads_direct_members_unless_asked(tier):
    t = Tree()
    top, sub = t.new_folder(SCRATCH), t.new_folder(SCRATCH + "::Sub")
    a, b = t.new_spec("Spec-A"), t.new_spec("Spec-B")
    t.link(top, a)
    t.link(top, sub)
    t.link(sub, b)
    flat = esc.sync_report_specs(t, folders=[SCRATCH], index_consumers=False)
    assert flat.added == ["Spec-A"] and flat.folders_read == [SCRATCH]
    assert any("not a ReportSpec (it is a CollectionFolder)" in why for _, why in flat.skipped)
    deep = esc.sync_report_specs(t, folders=[SCRATCH], recursive=True, index_consumers=False)
    assert deep.added == ["Spec-B"] and deep.unchanged == ["Spec-A"]
    off = esc.sync_report_specs(t, folders=[SCRATCH], recursive=False, index_consumers=False)
    assert off.pruned == ["Spec-B"]


def test_cycle_guard_reads_each_folder_once(tier, portal_tree):
    t, portal, overview, tiles = portal_tree
    t.link(tiles, portal)       # Tiles -> Portal: a cycle back to the top
    t.link(overview, overview)  # a folder that is its own member
    t.link(portal, tiles)       # a second path to Tiles
    report = esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)
    assert sorted(report.added) == ["Spec-A", "Spec-B", "Spec-C"]
    for g in (portal, overview, tiles):
        assert t.member_reads.count(g["elementHeader"]["guid"]) == 1
    assert len(report.folders_read) == 3
    assert sum("already read" in n for n in report.notes) == 3


def test_depth_cap_stops_and_says_so_and_prunes_nothing(tier):
    t = Tree()
    chain = [t.new_folder(PORTAL, "Portal")]
    for i in range(1, 8):  # Portal / L1 / ... / L7
        chain.append(t.new_folder(f"{PORTAL}::L{i}"))
        t.link(chain[i - 1], chain[i])
    for i, f in enumerate(chain):
        t.link(f, t.new_spec(f"Spec-L{i}"))
    full = esc.sync_report_specs(t, folders=[PORTAL], depth_cap=10, index_consumers=False)
    assert len(full.added) == 8 and not full.depth_cap_reached
    capped = esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)  # the default cap, 5
    assert esc.DEPTH_CAP == 5
    assert len(capped.folders_read) == 6  # the top and five levels below it
    assert capped.depth_cap_reached == [" / ".join([PORTAL] + [f"{PORTAL}::L{i}" for i in range(1, 7)])]
    assert "Depth cap reached" in capped.render()
    assert any("depth cap reached" in n for n in capped.notes)
    # L6 and L7 were not read, which is not "no longer a member": they stay cached.
    assert not capped.pruned
    assert {"Spec-L6", "Spec-L7"} <= set(manifest(tier)["entries"])


def test_never_up_to_the_root_nor_across_to_a_sibling_consumer(tier):
    t = Tree()
    root = t.new_folder(ROOT_QN, "Report Specs", type_name="RootCollection")
    portal, advisor = t.new_folder(PORTAL, "Portal"), t.new_folder(ADVISOR, "Egeria Advisor")
    t.link(root, portal)
    t.link(root, advisor)
    t.link(portal, t.new_spec("Spec-P"))
    t.link(advisor, t.new_spec("Spec-EA"))
    t.link(portal, advisor)  # misfiled: a sibling consumer inside Portal
    t.link(portal, root)     # misfiled: the root inside Portal
    report = esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)
    assert report.added == ["Spec-P"]
    assert report.folders_read == [PORTAL]
    notes = " ".join(report.notes)
    assert "another consumer folder" in notes and "never goes up to the root" in notes
    assert advisor["elementHeader"]["guid"] not in t.member_reads
    assert root["elementHeader"]["guid"] not in t.member_reads


def test_a_sub_folder_read_error_keeps_the_cached_specs(tier, portal_tree):
    t, _portal, overview, _tiles = portal_tree
    esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)
    t.failing.add(overview["elementHeader"]["guid"])
    report = esc.sync_report_specs(t, folders=[PORTAL], index_consumers=False)
    assert not report.pruned
    assert any(who.endswith("::Overview") and "could not be read" in why for who, why in report.skipped)
    assert {"Spec-A", "Spec-B", "Spec-C"} <= set(manifest(tier)["entries"])


# ── The consumer index ──

@pytest.fixture
def rooted(portal_tree):
    """The root holds Portal (A; Overview: B; Tiles: C), Egeria Advisor (A) and Jupyter (empty)."""
    t, portal, *_ = portal_tree
    root = t.new_folder(ROOT_QN, "Report Specs", type_name="RootCollection")
    advisor, jupyter = t.new_folder(ADVISOR, "Egeria Advisor"), t.new_folder(JUPYTER, "Jupyter")
    for f in (portal, advisor, jupyter):
        t.link(root, f)
    t.link(advisor, next(m for m in t.members[portal["elementHeader"]["guid"]]
                         if m["properties"]["qualifiedName"] == "ReportSpec::Spec-A"))
    return t, root


def test_the_index_maps_each_label_to_every_consumer(tier, rooted):
    t, _root = rooted
    idx = esc.build_consumer_index(t)
    assert idx["status"] == "read" and idx["reason"] is None
    assert idx["index"] == {"Spec-A": ["Egeria Advisor", "Portal"], "Spec-B": ["Portal"], "Spec-C": ["Portal"]}
    assert [(c["name"], c["status"], c["specs"]) for c in idx["consumers"]] == [
        ("Egeria Advisor", "read", 1), ("Jupyter", "read", 0), ("Portal", "read", 3)]
    # Names and labels only: no spec is fetched in full.
    assert all(g not in t.member_reads or t.by_guid[g]["elementHeader"]["type"]["typeName"] != "ReportSpec"
               for g in t.member_reads)


def test_a_folder_sync_refreshes_the_cached_index(tier, rooted):
    t, _root = rooted
    before = esc.read_consumer_index()
    assert before["status"] == "not read" and "a report-spec sync writes it" in before["reason"]
    report = esc.sync_report_specs(t, folders=[PORTAL])
    assert report.consumers == {"status": "read", "reason": None, "consumers": 3, "labels": 3}
    assert "Consumers: read (3 consumer folders, 3 specs)" in report.render()
    cached = esc.read_consumer_index()
    assert cached["index"]["Spec-A"] == ["Egeria Advisor", "Portal"]
    assert esc.read_consumer_index() is cached  # memoised until the file changes
    # A --spec sync leaves the index alone, and does not delete it.
    assert esc.sync_report_specs(t, specs=["Spec-A"]).consumers is None
    assert (tier["cache"] / esc.CONSUMERS).is_file()


def test_no_root_is_not_read_never_used_by_none(tier, portal_tree):
    t, *_ = portal_tree
    report = esc.sync_report_specs(t, folders=[PORTAL])
    assert report.consumers["status"] == "not read"
    assert "not found, or is not visible to erinoverview" in report.consumers["reason"]
    assert "Consumers: not read (" in report.render()
    cached = esc.read_consumer_index()
    assert cached["status"] == "not read" and cached["index"] == {} and cached["consumers"] == []


def test_a_root_read_error_is_not_read_with_the_reason(tier, rooted):
    t, _root = rooted
    t.root_error = "HTTP 503 from the view server"
    idx = esc.build_consumer_index(t)
    assert idx["status"] == "not read" and "HTTP 503" in idx["reason"]
    t.root_error = None
    t.failing.add(_root["elementHeader"]["guid"])
    idx = esc.build_consumer_index(t)
    assert idx["status"] == "not read" and "members of the root" in idx["reason"]


def test_one_unreadable_consumer_makes_the_index_partial(tier, rooted):
    t, _root = rooted
    advisor = t.get_collections_by_name(ADVISOR, metadata_element_type="CollectionFolder")[0]
    t.failing.add(advisor["elementHeader"]["guid"])
    idx = esc.build_consumer_index(t)
    assert idx["status"] == "partial" and idx["reason"] == "not fully read: Egeria Advisor"
    by_name = {c["name"]: c for c in idx["consumers"]}
    assert by_name["Egeria Advisor"]["status"] == "not read"
    assert idx["index"]["Spec-A"] == ["Portal"]  # what was read; the status says it is incomplete


def test_the_index_is_cycle_safe_and_depth_capped(tier, rooted):
    t, root = rooted
    portal = t.get_collections_by_name(PORTAL, metadata_element_type="CollectionFolder")[0]
    tiles = t.get_collections_by_name(PORTAL + "::Overview::Tiles", metadata_element_type="CollectionFolder")[0]
    t.link(tiles, portal)
    t.link(tiles, root)
    idx = esc.build_consumer_index(t)
    assert idx["status"] == "read" and idx["index"]["Spec-C"] == ["Portal"]
    capped = esc.build_consumer_index(t, depth_cap=1)
    assert capped["status"] == "partial"
    portal_entry = next(c for c in capped["consumers"] if c["name"] == "Portal")
    assert portal_entry["status"] == "partial" and "depth cap reached" in portal_entry["reason"]
    assert "Spec-C" not in capped["index"]


def test_root_is_configurable(tier, monkeypatch):
    assert esc.configured_root() == "RootCollection::ReportSpecs"
    monkeypatch.setenv(esc.ROOT_ENV, "RootCollection::Other")
    assert esc.configured_root() == "RootCollection::Other"


def test_cli_recursive_flags():
    import argparse
    from commands.tech import report_specs as cli
    seen = {}
    real = argparse.ArgumentParser.parse_args

    def capture(self, *a, **k):
        ns = real(self, *a, **k)
        seen["ns"] = ns
        raise SystemExit(0)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(argparse.ArgumentParser, "parse_args", capture)
        for argv, want in ((["report-specs", "sync"], None), (["report-specs", "sync", "--recursive"], True),
                           (["report-specs", "sync", "--no-recursive"], False)):
            with pytest.raises(SystemExit):
                cli.main(argv)
            assert seen["ns"].recursive is want

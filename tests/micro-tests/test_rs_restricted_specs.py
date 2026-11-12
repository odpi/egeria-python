"""B6: `list_visible_restricted_specs`, the zone-restricted report specs one signed-in user can see.

The shared cache never takes a zoned spec (§9), so restricted specs are read per user, as that
user's token, and Egeria's zone check decides what comes back. The fake below enforces zones the way
Egeria does (an element in a zone the reader lacks is simply not returned, and a direct read is a
403), on the same in-memory tree and element shapes as the consumer-folder tests. No live Egeria.
"""
from __future__ import annotations

import copy

import pytest

import pyegeria.view.egeria_spec_cache as esc
from test_rs_consumer_folders import ADVISOR, PORTAL, Tree, zone

pytestmark = pytest.mark.unit


class ZonedEgeria(Tree):
    """A Tree read as one user holding `grants`: zoned elements outside them are invisible."""

    def __init__(self, grants=()):
        super().__init__()
        self.grants = set(grants)

    def _visible(self, el):
        zones = esc._zones(self.by_guid.get(el["elementHeader"]["guid"], el))
        return not zones or bool(set(zones) & self.grants)

    def get_collection_members(self, collection_guid=None, output_format="JSON", **kw):
        got = super().get_collection_members(collection_guid=collection_guid, output_format=output_format, **kw)
        if isinstance(got, str):
            return got
        return [m for m in got if self._visible(m)] or "No elements found"

    def get_collection_by_guid(self, guid, output_format="JSON", **_):
        e = self.by_guid.get(guid)
        if e and not self._visible(e):
            raise RuntimeError(f"OPEN-METADATA-SECURITY-403-020 The element {guid} is not visible to user "
                               f"{self.user_id}")
        return copy.deepcopy(e) if e else "No elements found"

    def as_user(self, user_id, grants):
        other = copy.copy(self)
        other.user_id, other.grants = user_id, set(grants)
        return other


@pytest.fixture
def advisor_tree():
    """EA's folder holds a public spec, Fin (zone finance) and, in a sub-folder, Hr (zone hr)."""
    t = ZonedEgeria()
    advisor = t.new_folder(ADVISOR, "EgeriaAdvisor")
    sub = t.new_folder(ADVISOR + "::People", "People")
    pub, fin, hr = t.new_spec("Spec-Public"), zone(t.new_spec("Spec-Fin"), "finance"), \
        zone(t.new_spec("Spec-Hr"), "hr", where="classifications")
    for parent, child in ((advisor, pub), (advisor, fin), (advisor, sub), (sub, hr)):
        t.link(parent, child)
    return t


def test_a_user_with_the_zone_sees_the_spec_and_its_zones(advisor_tree):
    out = esc.list_visible_restricted_specs(advisor_tree.as_user("ivorpadlock", {"finance"}), folders=[ADVISOR])
    assert out["status"] == "read" and out["identity"] == "ivorpadlock"
    assert [(s["label"], s["zones"], s["folders"]) for s in out["specs"]] == [("Spec-Fin", ["finance"], [ADVISOR])]
    assert out["specs"][0]["qualified_name"] == "ReportSpec::Spec-Fin"


def test_a_user_without_the_zone_does_not_see_it_and_is_told_why(advisor_tree):
    out = esc.list_visible_restricted_specs(advisor_tree.as_user("peterprofile", set()), folders=[ADVISOR])
    assert out["specs"] == [] and out["status"] == "read"
    assert "hold no zone-restricted report spec visible to peterprofile" in out["reason"]


def test_public_specs_are_never_listed_they_belong_to_the_shared_cache(advisor_tree):
    out = esc.list_visible_restricted_specs(advisor_tree.as_user("u", {"finance", "hr"}), folders=[ADVISOR])
    assert [s["label"] for s in out["specs"]] == ["Spec-Fin", "Spec-Hr"]  # the sub-folder is walked too


def test_zones_only_on_the_full_element_are_found(advisor_tree):
    t = advisor_tree
    advisor = t.get_collections_by_name(ADVISOR, metadata_element_type="CollectionFolder")[0]
    z = t.new_spec("Spec-Late")
    t.link(advisor, copy.deepcopy(z))                       # the listing carries no zones
    zone(t.by_guid[z["elementHeader"]["guid"]], "finance")  # the full element does
    out = esc.list_visible_restricted_specs(t.as_user("u", {"finance"}), folders=[ADVISOR])
    assert "Spec-Late" in [s["label"] for s in out["specs"]]


def test_a_spec_in_two_folders_is_listed_once_with_both(advisor_tree):
    t = advisor_tree
    portal = t.new_folder(PORTAL, "Portal")
    fin = next(e for e in t.by_guid.values() if e["properties"]["qualifiedName"] == "ReportSpec::Spec-Fin")
    t.link(portal, fin)
    out = esc.list_visible_restricted_specs(t.as_user("u", {"finance"}), folders=[ADVISOR, PORTAL])
    assert [(s["label"], s["folders"]) for s in out["specs"]] == [("Spec-Fin", [ADVISOR, PORTAL])]


def test_a_missing_folder_is_stated_never_an_empty_list(advisor_tree):
    out = esc.list_visible_restricted_specs(advisor_tree.as_user("u", {"finance"}),
                                            folders=["ReportSpecFolder::Consumer::Nowhere"])
    assert out["status"] == "not read" and out["specs"] == []
    assert out["folders"][0]["result"] == "not_found" and "not visible to u" in out["folders"][0]["detail"]
    assert "no folder could be read" in out["reason"]


def test_one_unreadable_folder_makes_the_result_partial(advisor_tree):
    t = advisor_tree
    broken = t.new_folder(PORTAL, "Portal")
    t.failing.add(broken["elementHeader"]["guid"])
    out = esc.list_visible_restricted_specs(t.as_user("u", {"finance"}), folders=[ADVISOR, PORTAL])
    assert out["status"] == "partial" and [s["label"] for s in out["specs"]] == ["Spec-Fin"]
    assert {r["folder"]: r["result"] for r in out["folders"]} == {ADVISOR: "ok", PORTAL: "unreadable"}


def test_no_folders_configured_says_so(advisor_tree, monkeypatch):
    monkeypatch.setenv(esc.FOLDERS_ENV, "")
    out = esc.list_visible_restricted_specs(advisor_tree)
    assert out["status"] == "not read" and "no report spec folders are configured" in out["reason"]


def test_a_draft_restricted_spec_is_not_listed_and_says_so():
    t = ZonedEgeria({"finance"})
    advisor = t.new_folder(ADVISOR)
    d = zone(t.new_spec("Spec-Draft"), "finance")
    d["properties"]["contentStatus"] = "DRAFT"
    t.link(advisor, d)
    out = esc.list_visible_restricted_specs(t, folders=[ADVISOR])
    assert out["specs"] == [] and any("Spec-Draft: contentStatus DRAFT" in n for n in out["notes"])


def test_nothing_is_written_to_any_cache(advisor_tree, tmp_path, monkeypatch):
    monkeypatch.setenv(esc.CACHE_DIR_ENV, str(tmp_path / "cache"))
    esc.list_visible_restricted_specs(advisor_tree.as_user("u", {"finance"}), folders=[ADVISOR])
    assert not (tmp_path / "cache").exists()

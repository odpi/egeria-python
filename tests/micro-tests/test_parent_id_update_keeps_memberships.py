"""Parent ID never deletes a relationship it does not manage (ISSUE-181, 6.2.32).

The repro: a folder (end 1 of its members' CollectionMembership links) is updated with a Parent ID.
Before the fix, `_sync_parent_relationship` read the folder's CollectionMembership links at both ends,
took the last one that was not the named parent - one of the folder's own members - and deleted it.

The fake MetadataExpert holds relationships as (guid, type, end1, end2) and answers
related-elements requests like Egeria: `startingAtEnd` 0 = either end, 1 = the element at end 1,
2 = the element at end 2; paged by startFrom/pageSize; `elementAtEnd1` says whether the related
element is at end 1. Nothing reaches Egeria.
"""
from __future__ import annotations

import asyncio

import pytest

from md_processing.v2.processors import AsyncBaseCommandProcessor

pytestmark = pytest.mark.unit

MEMBERSHIP = "CollectionMembership"


class _MetadataExpert:
    def __init__(self, relationships, honour_starting_end=True):
        self.relationships = list(relationships)  # (rel_guid, type, end1, end2)
        self.honour_starting_end = honour_starting_end
        self.reads, self.created, self.deleted = [], [], []

    async def _async_get_all_related_elements(self, guid, starting_at_end=0, start_from=0, page_size=0, **kw):
        self.reads.append((guid, starting_at_end, start_from, page_size))
        entries = []
        for rel_guid, type_name, end1, end2 in self.relationships:
            if guid not in (end1, end2):
                continue
            at_end1 = guid == end1
            if self.honour_starting_end and (starting_at_end == 1 and not at_end1
                                             or starting_at_end == 2 and at_end1):
                continue
            entries.append({"relationshipGUID": rel_guid, "type": {"typeName": type_name},
                            "elementAtEnd1": not at_end1,
                            "element": {"elementGUID": end2 if at_end1 else end1}})
        page = entries[start_from:start_from + page_size] if page_size else entries[start_from:]
        return {"startingElement": {"guid": guid}, "elementList": page}

    async def _async_create_related_elements(self, body):
        self.created.append((body["type_name"], body["metadata_element_1_guid"], body["metadata_element_2_guid"]))

    async def _async_delete_related_elements(self, rel_guid, body=None):  # must never be called
        self.deleted.append(rel_guid)


class _Processor(AsyncBaseCommandProcessor):
    async def apply_changes(self):  # pragma: no cover - not used here
        raise NotImplementedError


def _sync(expert, guid, parent, parent_at_end1=True, page_size=None):
    proc = object.__new__(_Processor)
    proc.client = type("C", (), {"metadata_expert": expert})()
    proc.related_results = []
    if page_size:
        proc._PARENT_LINK_PAGE_SIZE = page_size
    attributes = {"Parent ID": {"guid": parent}, "Parent Relationship Type Name": {"value": MEMBERSHIP},
                  "Parent at End1": {"value": parent_at_end1}}
    asyncio.run(proc._sync_parent_relationship(guid, attributes))
    return proc.related_results


# The ReportSpecFolder::EgeriaPortal shape: the folder holds two specs and is not yet under the root.
FOLDER_WITH_TWO_SPECS = [("m-1", MEMBERSHIP, "folder", "spec-1"),
                         ("m-2", MEMBERSHIP, "folder", "spec-2")]


@pytest.mark.parametrize("honour", [True, False], ids=["server-filters-ends", "server-returns-both-ends"])
def test_parent_id_on_a_folder_keeps_its_members(honour):
    expert = _MetadataExpert(FOLDER_WITH_TWO_SPECS, honour_starting_end=honour)
    _sync(expert, "folder", "root")
    assert expert.deleted == []
    assert expert.created == [(MEMBERSHIP, "root", "folder")]
    assert expert.reads[0][1] == 2  # the folder is the child: end 2


def test_an_existing_link_to_the_parent_is_a_no_op():
    expert = _MetadataExpert(FOLDER_WITH_TWO_SPECS + [("m-3", MEMBERSHIP, "root", "folder")])
    _sync(expert, "folder", "root")
    assert expert.created == [] and expert.deleted == []


def test_the_parent_on_a_later_page_is_found():
    rels = [(f"m-{i}", MEMBERSHIP, f"other-{i}", "folder") for i in range(5)] + [("m-p", MEMBERSHIP, "root", "folder")]
    expert = _MetadataExpert(rels)
    _sync(expert, "folder", "root", page_size=2)
    assert expert.created == [] and expert.deleted == []
    assert [r[2] for r in expert.reads] == [0, 2, 4]


def test_a_different_parent_is_kept_and_reported():
    expert = _MetadataExpert([("m-old", MEMBERSHIP, "old-root", "folder")])
    results = _sync(expert, "folder", "root")
    assert expert.deleted == []
    assert expert.created == [(MEMBERSHIP, "root", "folder")]
    assert "old-root" in str(results) and "left in place" in str(results)


def test_parent_at_end2_reads_the_element_at_end1():
    expert = _MetadataExpert([("r-1", MEMBERSHIP, "child", "something-else")])
    _sync(expert, "child", "parent", parent_at_end1=False)
    assert expert.reads[0][1] == 1
    assert expert.deleted == []
    assert expert.created == [(MEMBERSHIP, "child", "parent")]


def test_too_many_pages_adds_nothing_and_says_so():
    rels = [(f"m-{i}", MEMBERSHIP, f"other-{i}", "folder") for i in range(10)]
    expert = _MetadataExpert(rels)
    proc = object.__new__(_Processor)
    proc.client = type("C", (), {"metadata_expert": expert})()
    proc.related_results = []
    proc._PARENT_LINK_PAGE_SIZE, proc._PARENT_LINK_MAX_PAGES = 2, 3
    attributes = {"Parent ID": {"guid": "root"}, "Parent Relationship Type Name": {"value": MEMBERSHIP}}
    asyncio.run(proc._sync_parent_relationship("folder", attributes))
    proc_results = proc.related_results
    assert expert.created == [] and expert.deleted == []
    assert proc_results[-1]["status"] == "failure"
    assert "could not read every CollectionMembership link; not added" in proc_results[-1]["message"]

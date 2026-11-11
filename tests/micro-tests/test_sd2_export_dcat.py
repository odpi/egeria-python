# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""SD-2: export_dcat, the DCAT-AP 3 exporter for Assets, and the "DCAT Catalog" DOCUMENT spec.

Every Egeria answer here is real: captured read-only from laz on 2026-11-11 as erinoverview by
`scripts/capture_dcat_fixtures.py`, which runs the exporter through a recording proxy
(tests/micro-tests/data/dcat/). A replay client answers each call with the recorded response, or
raises the recorded Egeria error. The fixtures and what they cover:

- portal_dashboards: CollectionFolder DashboardFolder::Consumer::Portal, 5 owned Dashboard Assets
  (publisher; no access path, licence, keywords or themes).
- org_structure_products: DigitalProductFamily Organization Structure, whose DigitalProduct members
  are Bitol's (the exclusion).
- clinical_trial_files: a search over zoned (NON_PUBLIC), licensed CSVFiles with a path and an
  endpoint (distribution, licence, access rights).
- coco_data_hub: a search for a RelationalDatabase with no connection (no access path).
- not_visible_report: a real OPEN-METADATA-SECURITY-403-020 answer (a Report zoned to another user).

Gaps (no real shape on laz to capture): no Asset with SearchKeywords, a SemanticAssignment, a url
or ExternalReference, and no non-template DataStore/Database or DeployedAPI with an endpoint. Those
rows are checked only for their absence notes.
"""
import copy
import json
import random
from pathlib import Path

import httpx
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import DCAT, DCTERMS, RDF

import pyegeria.view.base_report_formats as brf
from pyegeria.core._exceptions import PyegeriaUnauthorizedException
from pyegeria.view import export_dcat as ed
from pyegeria.view import format_set_executor as fse
from pyegeria.view.document_validators import get_document_validator, run_document_validator
from pyegeria.view.role_supply import PlainSupply

DATA = Path(__file__).parent / "data" / "dcat"
PUBLIC = URIRef("http://publications.europa.eu/resource/authority/access-right/PUBLIC")
NON_PUBLIC = URIRef("http://publications.europa.eu/resource/authority/access-right/NON_PUBLIC")


def _fixture(name):
    return json.loads((DATA / f"{name}.json").read_text())


def _egeria_error(err):
    info = err.get("additional_info") or {}
    if err["class"] == "PyegeriaUnauthorizedException":
        response = httpx.Response(200, json=info, request=httpx.Request("POST", "https://localhost:9443/replay"))
        return PyegeriaUnauthorizedException(response, {"caller method": "replay"}, additional_info=info)
    return RuntimeError(err.get("message") or err["class"])


class Replay:
    """Answers each call with the recorded response (matched on method, args and kwargs)."""

    def __init__(self, *fixtures, overrides=None):
        self.user_id = fixtures[0]["user"]
        self.calls = [c for f in fixtures for c in f["calls"]]
        self.overrides = overrides or {}
        self.made = []

    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.made.append((name, args, kwargs))
            for key in ((name, args[0] if args else None), (name, None)):   # (method, None): every call
                if key in self.overrides:
                    return self.overrides[key](*args, **kwargs)
            want = json.loads(json.dumps({"args": list(args), "kwargs": kwargs}, default=str))
            for c in self.calls:
                if c["method"] == name and c["args"] == want["args"] and c["kwargs"] == want["kwargs"]:
                    if "error" in c:
                        raise _egeria_error(c["error"])
                    return copy.deepcopy(c["result"])
            raise AssertionError(f"no recorded answer for {name}{args} {kwargs}")
        return call


def _export(name, **kw):
    fx = _fixture(name)
    return ed.export_dcat(Replay(fx), **{**fx["params"], **kw})


def _graph(text, fmt="json-ld"):
    g = Graph()
    g.parse(data=text, format=fmt)
    return g


def _datasets(g):
    return sorted(g.subjects(RDF.type, DCAT.Dataset))


# ── The fixtures are what the brief asked for (or name their gaps) ──

def test_fixtures_are_real_captures():
    for name in ("portal_dashboards", "org_structure_products", "clinical_trial_files", "coco_data_hub",
                 "not_visible_report"):
        fx = _fixture(name)
        assert fx["user"] == "erinoverview" and fx["server"] == "laz qs-view-server" and fx["calls"]
        assert all(c["method"].startswith(("get_", "find_")) for c in fx["calls"])  # read-only


# ── §7 mapping, row by row ──

def test_catalog_from_the_scope_collection():
    out = _export("portal_dashboards")
    g = _graph(out["text"])
    [catalog] = g.subjects(RDF.type, DCAT.Catalog)
    assert str(g.value(catalog, DCTERMS.identifier)) == "DashboardFolder::Consumer::Portal"
    assert g.value(catalog, DCTERMS.title) is not None
    assert len(list(g.objects(catalog, DCAT.dataset))) == 5


def test_datasets_are_assets_with_identity_dates_and_publisher():
    g = _graph(_export("portal_dashboards")["text"])
    ds = _datasets(g)
    assert len(ds) == 5
    for d in ds:
        qn = str(g.value(d, DCTERMS.identifier))
        assert qn.startswith("Dashboard::")
        assert str(d).startswith("urn:egeria:guid:")
        ident = g.value(d, URIRef("http://www.w3.org/ns/adms#identifier"))
        assert str(g.value(ident, URIRef("http://www.w3.org/2004/02/skos/core#notation"))) == str(d).rsplit(":", 1)[-1]
        assert g.value(d, DCTERMS.issued) is not None and g.value(d, DCTERMS.modified) is not None
        assert g.value(d, DCTERMS.publisher) is not None            # owned Dashboards
        assert g.value(d, DCTERMS.accessRights) == PUBLIC          # not zoned


def test_distribution_licence_and_non_public_for_zoned_files():
    out = _export("clinical_trial_files")
    g = _graph(out["text"])
    ds = _datasets(g)
    assert len(ds) == 5
    for d in ds:
        assert g.value(d, DCTERMS.accessRights) == NON_PUBLIC     # zoned, and readable by the viewer
        lic = g.value(d, DCTERMS.license)
        assert (lic, RDF.type, DCTERMS.LicenseDocument) in g
        assert str(g.value(lic, DCTERMS.title)) == "Standard Clinical Trial License"
        [dist] = g.objects(d, DCAT.distribution)
        assert str(g.value(dist, DCAT.accessURL)).startswith("file:///deployments/coco-data-lake/")
        assert str(g.value(dist, DCAT.downloadURL)).endswith(".csv")
        assert str(g.value(dist, DCAT.mediaType)) == "http://www.iana.org/assignments/media-types/text/csv"
        assert str(g.value(dist, DCTERMS["format"])).endswith("/file-type/CSV")


def test_missing_owner_licence_and_access_path_are_omitted_and_noted():
    out = _export("coco_data_hub")
    g = _graph(out["text"])
    [d] = _datasets(g)
    assert g.value(d, DCTERMS.publisher) is None and g.value(d, DCTERMS.license) is None
    assert g.value(d, DCAT.distribution) is None
    qn = "PostgreSQL Relational Database::Coco PostgreSQL Server 1::coco_data_hub"
    notes = "\n".join(out["notes"])
    for reason in ("dct:publisher omitted: no Ownership classification",
                   "dct:license omitted: no License relationship",
                   "dcat:distribution omitted: the endpoint address is not a URL"):
        assert any(n.startswith(reason) and qn in n for n in out["notes"]), (reason, notes)


def test_keywords_themes_landing_and_data_service_say_why_they_are_absent():
    notes = _export("clinical_trial_files")["notes"]
    for reason in ("dcat:keyword omitted: no SearchKeywords", "dcat:theme omitted: no glossary term",
                   "dcat:landingPage omitted"):
        assert any(n.startswith(reason) and "for 5 datasets" in n for n in notes), reason
    assert "dcat:DataService omitted: no DeployedAPI with an endpoint in scope." in notes
    assert "dcat:contactPoint omitted: this exporter does not read owners' contact details." in notes


def test_viewer_rule_is_stated():
    notes = _export("clinical_trial_files")["notes"]
    assert any(n.startswith("Read as erinoverview:") and "only what erinoverview can see" in n for n in notes)


# ── Exclusions and refusals ──

def test_digital_products_are_excluded_and_named():
    out = _export("org_structure_products")
    products = [n for n in out["notes"] if n.endswith(": a DigitalProduct, not a DCAT dataset (Bitol)")]
    assert products, out["notes"]
    g = _graph(out["text"])
    exported = {str(g.value(d, DCTERMS.identifier)) for d in _datasets(g)}
    assert not any(n.split(": a DigitalProduct")[0] in exported for n in products)


def test_a_403_member_is_noted_as_not_visible_never_absent():
    fx = _fixture("portal_dashboards")
    [refused] = _fixture("not_visible_report")["calls"]
    assert refused["error"]["additional_info"]["exceptionErrorMessageId"] == "OPEN-METADATA-SECURITY-403-020"
    members = next(c["result"] for c in fx["calls"] if c["method"] == "get_collection_members")
    victim = sorted(members, key=lambda m: m["elementHeader"]["guid"])[0]
    guid, qn = victim["elementHeader"]["guid"], victim["properties"]["qualifiedName"]

    def refuse(*a, **k):
        raise _egeria_error(refused["error"])

    out = ed.export_dcat(Replay(fx, overrides={("get_element_by_guid", guid): refuse}), **fx["params"])
    assert f"{qn}: not visible to erinoverview (Egeria refused the read: zone security); it is in scope but " \
           f"not exported" in out["notes"]
    assert len(_datasets(_graph(out["text"]))) == 4


# ── Paging ──

def test_members_are_read_until_an_empty_page():
    fx = _fixture("portal_dashboards")
    members = next(c["result"] for c in fx["calls"] if c["method"] == "get_collection_members")
    pages = [members[:2], members[2:3], members[3:], []]          # a short page is not the last
    seen = []

    def page(*a, start_from=0, page_size=0, **k):
        seen.append(start_from)
        return pages[len(seen) - 1]

    client = Replay(fx, overrides={("get_collection_members", None): page})
    out = ed.export_dcat(client, scope=fx["params"]["scope"], page_size=2)
    assert seen == [0, 2, 4, 6]                                    # startFrom advances by the page size
    assert len(_datasets(_graph(out["text"]))) == 5


def test_a_repeated_page_ends_the_reading_with_a_note():
    """laz's asset-domain search rounds startFrom down to a page boundary, so a naive reader sees
    the same page again; it must stop, say so, and never count the repeat."""
    fx = _fixture("clinical_trial_files")
    first = next(c["result"] for c in fx["calls"] if c["method"] == "find_in_asset_domain")
    calls = []

    def search(*a, start_from=0, **k):
        calls.append(start_from)
        return copy.deepcopy(first)

    out = ed.export_dcat(Replay(fx, overrides={("find_in_asset_domain", None): search}),
                         search_string=fx["params"]["search_string"], page_size=2)
    assert calls == [0, 2]
    assert any(n.startswith("Stopped reading the assets matching") and "exactly the page before" in n
               for n in out["notes"])
    assert len(_datasets(_graph(out["text"]))) == 5


def _paged_members(pages):
    """Real portal members dealt into `pages` (lists of indexes); returns (fake listing, startFrom log)."""
    fx = _fixture("portal_dashboards")
    members = sorted(next(c["result"] for c in fx["calls"] if c["method"] == "get_collection_members"),
                     key=lambda m: m["elementHeader"]["guid"])
    log = []

    def listing(*a, start_from=0, **k):
        log.append(start_from)
        i = len(log) - 1
        return copy.deepcopy([members[j] for j in pages[i]]) if i < len(pages) else []

    return fx, listing, log


def test_overlapping_short_pages_are_all_read():
    """Like laz's 'Clinical' search: pages are short AND overlap (one element on page 0 and page 5).
    A page with something new keeps the reading going; the shared element is exported once."""
    fx, listing, log = _paged_members([[0, 1], [1, 2], [2], [3, 4], []])
    out = ed.export_dcat(Replay(fx, overrides={("get_collection_members", None): listing}),
                         scope=fx["params"]["scope"], page_size=2)
    assert log == [0, 2, 4, 6, 8]                                   # [2] brought nothing new: not a stop
    assert len(_datasets(_graph(out["text"]))) == 5
    assert not any(n.startswith("Stopped reading") for n in out["notes"])


def test_two_pages_in_a_row_with_nothing_new_end_the_reading_with_a_note():
    fx, listing, log = _paged_members([[0, 1], [1], [0], [2, 3, 4]])
    out = ed.export_dcat(Replay(fx, overrides={("get_collection_members", None): listing}),
                         scope=fx["params"]["scope"], page_size=2)
    assert log == [0, 2, 4]
    assert len(_datasets(_graph(out["text"]))) == 2
    assert any("two pages in a row held only elements already read" in n for n in out["notes"])


# ── Why a catalog has no dataset (read-back C2) ──

def _no_dataset_note(out):
    [note] = [n for n in out["notes"] if n.startswith("No dataset exported")]
    assert _datasets(_graph(out["text"])) == []
    return note


def test_empty_scope_says_it_has_no_members():
    fx = _fixture("portal_dashboards")
    out = ed.export_dcat(Replay(fx, overrides={("get_collection_members", None): lambda *a, **k: []}),
                         **fx["params"])
    assert _no_dataset_note(out) == "No dataset exported: the scope has no members that erinoverview can see."


def test_a_scope_of_bitol_types_and_non_assets_says_so():
    fx = _fixture("org_structure_products")
    members = next(c["result"] for c in fx["calls"] if c["method"] == "get_collection_members")
    kept = [m for m in members if "Asset" not in (m["elementHeader"]["type"].get("superTypeNames") or [])]
    out = ed.export_dcat(Replay(fx, overrides={("get_collection_members", None):
                                               lambda *a, start_from=0, **k: copy.deepcopy(kept) if start_from == 0 else []}),
                         **fx["params"])
    assert _no_dataset_note(out) == ("No dataset exported: of the 4 element(s) in scope, 3 a DigitalProduct or "
                                     "Agreement (Bitol's, not DCAT's); 1 not an Asset.")


def test_a_scope_whose_assets_are_all_refused_says_not_visible():
    fx = _fixture("portal_dashboards")
    [refused] = _fixture("not_visible_report")["calls"]

    def refuse(*a, **k):
        raise _egeria_error(refused["error"])

    out = ed.export_dcat(Replay(fx, overrides={("get_element_by_guid", None): refuse}), **fx["params"])
    assert _no_dataset_note(out) == ("No dataset exported: of the 5 element(s) in scope, 5 not visible to "
                                     "erinoverview.")


def test_a_search_that_matches_nothing_says_so():
    fx = _fixture("coco_data_hub")
    out = ed.export_dcat(Replay(fx, overrides={("find_in_asset_domain", None): lambda *a, **k: "No elements found"}),
                         **fx["params"])
    assert _no_dataset_note(out) == "No dataset exported: the search matched nothing that erinoverview can see."


# ── Output ──

def test_output_is_deterministic():
    fx = _fixture("portal_dashboards")
    first = ed.export_dcat(Replay(fx), **fx["params"])
    shuffled = copy.deepcopy(fx)
    for c in shuffled["calls"]:
        if c["method"] == "get_collection_members" and isinstance(c["result"], list):
            random.Random(7).shuffle(c["result"])
    second = ed.export_dcat(Replay(shuffled), **fx["params"])
    assert first == second


@pytest.mark.parametrize("name", ["portal_dashboards", "clinical_trial_files", "coco_data_hub"])
def test_jsonld_and_turtle_parse_back_to_the_same_graph(name):
    ld = _export(name)["text"]
    ttl = _export(name, format="turtle")["text"]
    assert isomorphic(_graph(ld), _graph(ttl, "turtle"))
    assert json.loads(ld)["@context"] == ed.JSONLD_CONTEXT          # inline, never fetched


# ── Validation against the vendored DCAT-AP 3.0.1 shapes ──

#: The documented gaps: each fixture catalog's SHACL findings, exactly.
EXPECTED_FINDINGS = {
    "portal_dashboards": ["Catalog DashboardFolder::Consumer::Portal: missing dct:publisher"],
    "org_structure_products": [
        "Catalog DigitalProductFamily::Jacquard::ORGANIZATION-STRUCTURE-FAMILY::Organization Structure: missing "
        "dct:publisher"],
    "clinical_trial_files": [
        "Catalog search:DataLake::PROJ-CT-TBDF::WeeklyMeasurements::Oak Dene Hospital::PROJ-CT-TBDF_00002: "
        "missing dct:publisher"],
    "coco_data_hub": [
        "Catalog search:PostgreSQL Relational Database::Coco PostgreSQL Server 1::coco_data_hub: missing "
        "dct:publisher"],
}
#: The one documented gap: none of the real scope collections carries an Ownership classification, and a
#: search has no owner, while DCAT-AP requires a Catalog publisher. The exporter omits it and says so.


@pytest.mark.parametrize("name", sorted(EXPECTED_FINDINGS))
def test_fixture_catalogs_findings_are_exactly_the_documented_gaps(name):
    v = run_document_validator(_export(name)["text"], "application/ld+json", "dcat-ap-3-shacl")
    assert v["findings"] == EXPECTED_FINDINGS[name]
    assert v["state"] == ("valid" if not EXPECTED_FINDINGS[name] else "invalid")


def test_a_hand_broken_graph_is_invalid_with_named_findings():
    g = _graph(_export("clinical_trial_files")["text"])
    d = _datasets(g)[0]
    qn = str(g.value(d, DCTERMS.identifier))
    g.remove((d, DCTERMS.title, None))
    g.remove((d, DCTERMS.description, None))
    ok, findings = get_document_validator("dcat-ap-3-shacl")(ed.serialise(g, "jsonld"), "application/ld+json")
    assert not ok
    assert f"Dataset {qn}: missing dct:description" in findings
    assert f"Dataset {qn}: missing dct:title" in findings


# ── The DCAT Catalog spec, end to end through SD-1's executor ──

def test_dcat_catalog_spec_runs_as_a_document():
    fx = _fixture("portal_dashboards")
    out = fse.exec_report_spec("DCAT Catalog", output_format="DOCUMENT", params={"scope": fx["params"]["scope"]},
                               supply=PlainSupply(Replay(fx)), view_server="vs", view_url="https://x",
                               user="u", user_pass="p")
    assert out["kind"] == "document" and out["standard"] == "dcat-ap-3"
    assert out["media_type"] == "application/ld+json"
    assert out["file_name"] == "DashboardFolder_Consumer_Portal-dcat.jsonld"
    assert out["validation"]["validator"] == "dcat-ap-3-shacl"
    assert out["validation"]["findings"] == EXPECTED_FINDINGS["portal_dashboards"]
    assert any(n.startswith("Read as erinoverview:") for n in out["notes"])


def test_dcat_catalog_turtle_spec_validates_its_own_media_type():
    fx = _fixture("portal_dashboards")
    assert brf.get_report_registry()["DCAT Catalog (Turtle)"].document_format().document.media_type == "text/turtle"
    out = fse.exec_report_spec("DCAT Catalog (Turtle)", output_format="DOCUMENT",
                               params={"scope": fx["params"]["scope"]},
                               supply=PlainSupply(Replay(fx)), view_server="vs", view_url="https://x",
                               user="u", user_pass="p")
    assert out["file_name"].endswith("-dcat.ttl") and out["text"].startswith("@prefix")
    assert out["validation"]["findings"] == EXPECTED_FINDINGS["portal_dashboards"]   # Turtle read as Turtle


def test_export_needs_a_scope_or_search_and_a_known_format():
    with pytest.raises(ValueError, match="needs a scope"):
        ed.export_dcat(Replay(_fixture("coco_data_hub")))
    with pytest.raises(ValueError, match="not jsonld or turtle"):
        ed.export_dcat(Replay(_fixture("coco_data_hub")), search_string="x", format="xml")


# ── Egeria-held DOCUMENT specs (microflow) — SD-2 read-back N2 ──

def _held_spec(document):
    import pyegeria.view.microflow as mfm
    mf = {"format": "microflow/1", "params": {},
          "stages": [{"stage": "producer/analytic", "function": "export_dcat", "params": {"format": "jsonld"}}],
          "formatters": {"DOCUMENT": {"columns": [], "document": document}}}
    props = {"class": "ReportSpecProperties", "qualifiedName": "ReportSpec::Held DCAT", "displayName": "Held DCAT",
             "description": "d", "versionIdentifier": "1.0", "category": "Standard Documents", "purpose": "Held DCAT",
             "microflow": json.dumps(mf), "targetTypeName": "Collection", "outputTypes": ["DOCUMENT"],
             "contentStatus": "ACTIVE"}
    return {"elementHeader": {"guid": "5d0c0000-0000-0000-0000-000000000001",
                              "type": {"typeName": "ReportSpec",
                                       "superTypeNames": ["ReportType", "DataSpec", "Collection", "Referenceable"]},
                              "versions": {"version": 1, "updateTime": "2026-11-11T20:00:00.000+00:00"}},
            "properties": props}


GOOD_DOCUMENT = {"standard": "dcat-ap-3", "media_type": "application/ld+json", "file_name": "{scope}-dcat.jsonld",
                 "validator": "dcat-ap-3-shacl"}


def test_a_held_document_spec_round_trips_through_microflow():
    import pyegeria.view.egeria_spec_cache as esc
    built = esc._build(_held_spec(GOOD_DOCUMENT), folders=[], identity="erinoverview", registry_names=set())
    fs = built.format_set if hasattr(built, "format_set") else built[0]
    assert fs.document_format().document.validator == "dcat-ap-3-shacl"


@pytest.mark.parametrize("bad, words", [
    ({**GOOD_DOCUMENT, "validator": "shacl", "validator_options": {"shapes": "/etc/passwd"}},
     "must be a package: reference"),
    ({**GOOD_DOCUMENT, "file_name": "../x.jsonld"}, "file_name refused"),
])
def test_a_held_document_spec_that_refuses_to_load_is_skipped_with_words(bad, words):
    import pyegeria.view.egeria_spec_cache as esc
    with pytest.raises(esc._Skip) as caught:
        esc._build(_held_spec(bad), folders=[], identity="erinoverview", registry_names=set())
    assert caught.value.who == "Held DCAT"
    assert caught.value.reason.startswith("the spec does not load:") and words in caught.value.reason

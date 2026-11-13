# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Unit tests for the Dr.Egeria round-trip probe's release gate (scripts/dr_egeria_roundtrip_probe).

No platform and no Docker: scratch.py's edit-and-refuse logic runs on a copy of the base image's own
configuration (fixtures/roundtrip_probe/image_config), the gate's compare rules on hand-made verdict
maps, and the raw-store parsing on an EntityDetailResponse captured from a scratch run.
"""
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dr_egeria_roundtrip_probe"))

import gate  # noqa: E402
import probe  # noqa: E402
import scratch  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "roundtrip_probe"


# ── scratch.py: the edits and the host.docker.internal refusal ──

@pytest.fixture
def image_copy(tmp_path):
    """The layout `docker cp` produces: <dir>/application.properties and <dir>/data/servers/view-server/config."""
    (tmp_path / "data" / "servers" / "view-server" / "config").mkdir(parents=True)
    shutil.copy(FIXTURES / "image_config" / "view-server.config",
                tmp_path / "data" / "servers" / "view-server" / "config" / "view-server.config")
    shutil.copy(FIXTURES / "image_config" / "application.properties", tmp_path / "application.properties")
    (tmp_path / "data" / "servers" / "simple-metadata-store" / "config").mkdir(parents=True)
    shutil.copy(FIXTURES / "image_config" / "simple-metadata-store.config",
                tmp_path / "data" / "servers" / "simple-metadata-store" / "config" / "simple-metadata-store.config")
    return tmp_path


def test_image_config_names_the_host_before_the_edits(image_copy):
    assert scratch.forbidden_references(image_copy) == ["application.properties"]


def test_edits_point_everything_away_from_the_host(image_copy):
    scratch.apply_edits(image_copy)  # would raise Refused if anything still named the host
    props = (image_copy / "application.properties").read_text()
    assert "host.docker.internal" not in props
    assert "startup.server.list=simple-metadata-store,view-server" in props
    assert '"kafkaEndpoint" : "kafka-disabled.invalid:9092",\\' in props
    assert '"egeriaEndpoint" : "https://localhost:7443",\\' in props
    # the image's own typo is fixed (`".\` -> `",\`)
    assert 'YAMLSecretsStoreProvider".\\' not in props
    assert 'YAMLSecretsStoreProvider",\\' in props


def test_view_server_repointed_and_kafka_audit_destination_removed(image_copy):
    scratch.apply_edits(image_copy)
    config = json.loads((image_copy / "data/servers/view-server/config/view-server.config").read_text())
    text = json.dumps(config)
    assert "active-metadata-store" not in text
    assert text.count('"omagserverName": "simple-metadata-store"') == 2
    audit = config["repositoryServicesConfig"]["auditLogConnections"]
    assert audit and all("kafka" not in json.dumps(c).lower() for c in audit)


def test_refuses_a_config_that_still_names_the_host(image_copy):
    extra = image_copy / "data" / "servers" / "view-server" / "config" / "extra.config"
    extra.write_text('{"localServerURL": "https://host.docker.internal:7443"}')
    with pytest.raises(scratch.Refused) as exc:
        scratch.apply_edits(image_copy)
    assert "host.docker.internal" in str(exc.value)
    assert "extra.config" in str(exc.value)


def test_edits_are_idempotent(image_copy):
    scratch.apply_edits(image_copy)
    first = (image_copy / "application.properties").read_text()
    scratch.apply_edits(image_copy)
    assert (image_copy / "application.properties").read_text() == first


# ── probe.py: the guard refuses laz before any request ──

@pytest.mark.parametrize("url", ["https://localhost:9443", "https://laz.example:8443", "https://127.0.0.1:7443",
                                 "http://localhost:19443", "https://laz.example:19443",
                                 "https://localhost:19443/servers/view-server"])
def test_guard_refuses_anything_but_the_scratch_platform(url, monkeypatch):
    def no_docker(*a, **k):
        raise AssertionError("the guard must refuse before asking Docker or the platform anything")
    monkeypatch.setattr(probe.subprocess, "run", no_docker)
    monkeypatch.setattr(probe.urllib.request, "urlopen", no_docker)
    with pytest.raises(probe.Refused):
        probe.guard(url)


# ── gate.py: compare rules ──

KNOWN = {
    "Create Regulation|Regulators": {"reason": "Egeria write gap", "verdict": "DROPPED (not stored)"},
    "*|Effective From": {"reason": "Egeria read gap", "verdict": "NOT RETURNED (stored)"},
    "*|Project Scope": {"reason": "owner decision pending"},
}


def test_identical_run_passes():
    base = {"Create Glossary|Description": "MATCH", "Create Glossary|Search Keywords": "DROPPED (not stored)"}
    result = gate.compare(base, dict(base), KNOWN)
    assert not result["failed"]


def test_match_lost_is_a_regression():
    result = gate.compare({"Create Glossary|Description": "MATCH"},
                          {"Create Glossary|Description": "DROPPED (not stored)"}, KNOWN)
    assert result["failed"] and result["regressions"] == [
        ("Create Glossary|Description", "MATCH", "DROPPED (not stored)")]


@pytest.mark.parametrize("new", ["REJECTED (breaks the create)", "CREATE-FAILED", "UNRESOLVED"])
def test_new_failure_fails(new):
    result = gate.compare({"Create Note|": "DROPPED (not stored)"}, {"Create Note|": new}, KNOWN)
    assert result["failed"] and result["new_failures"]


def test_new_failing_row_not_in_baseline_fails():
    result = gate.compare({"Create Note|Description": "MATCH"},
                          {"Create Note|Description": "MATCH", "Create Thing|": "CREATE-FAILED"}, KNOWN)
    assert result["failed"] and result["new_failures"] == [("Create Thing|", None, "CREATE-FAILED")]


def test_command_gone_fails():
    result = gate.compare({"Create Gone|Description": "MATCH", "Create Gone|Summary": "MATCH",
                           "Create Here|Description": "MATCH"}, {"Create Here|Description": "MATCH"}, KNOWN)
    assert result["failed"] and result["commands_gone"] == ["Create Gone"]


def test_improvement_does_not_fail_and_asks_for_a_baseline_update():
    result = gate.compare({"Create Glossary|Search Keywords": "DROPPED (not stored)", "Create Note|": "CREATE-FAILED"},
                          {"Create Glossary|Search Keywords": "MATCH", "Create Note|": "DROPPED (not stored)"}, KNOWN)
    assert not result["failed"]
    assert len(result["improvements"]) == 2
    assert "update the baseline" in gate.render(result)


def test_known_gap_never_fails_and_flipping_says_remove():
    base = {"Create Regulation|Regulators": "DROPPED (not stored)", "Create Project|Project Scope": "DROPPED (not stored)",
            "Create Glossary|Effective From": "NOT RETURNED (stored)"}
    still = gate.compare(base, dict(base), KNOWN)
    assert not still["failed"] and still["known_gap_hits"] == 3
    fixed = gate.compare(base, {**base, "Create Regulation|Regulators": "MATCH"}, KNOWN)
    assert not fixed["failed"]
    assert fixed["known_gap_fixed"][0][0] == "Create Regulation|Regulators"
    assert "remove from known gaps" in gate.render(fixed)


def test_known_gap_with_a_verdict_does_not_hide_another_failure():
    # Effective From is a known READ gap (stored, not returned); "not stored at all" is a different bug
    result = gate.compare({"Create Glossary|Effective From": "MATCH"},
                          {"Create Glossary|Effective From": "DROPPED (not stored)"}, KNOWN)
    assert result["failed"] and result["regressions"]


def test_rebaseline_lists_changed_rows_for_a_reason(tmp_path):
    path = tmp_path / "757a5df0.json"
    meta = {"image": "odpi/egeria-platform@sha256:757a5df0aaaa", "pyegeria": "6.2.39"}
    rows = [{"command": "Create Glossary", "attribute": "Description", "verdict": "DROPPED (not stored)"}]
    gate.write_baseline(path, {"meta": meta, "rows": rows}, "RESULTS-1.json")
    rows[0]["verdict"] = "MATCH"
    b = gate.write_baseline(path, {"meta": meta, "rows": rows}, "RESULTS-2.json")
    assert b["rows"] == {"Create Glossary|Description": "MATCH"}
    assert b["changes"]["Create Glossary|Description"]["from"] == "DROPPED (not stored)"
    assert b["changes"]["Create Glossary|Description"]["reason"] == "<one-line reason>"
    assert gate.baseline_path(meta).name == "757a5df0.json"


def test_gate_results_fails_without_a_baseline(tmp_path):
    results = tmp_path / "RESULTS-x.json"
    results.write_text(json.dumps({"meta": {"image": "x@sha256:0123456789"}, "rows": []}))
    assert gate.gate_results(results, tmp_path / "missing.json", tmp_path / "none.json") == 2


def test_committed_baseline_and_known_gaps_load():
    baseline = json.loads((gate.BASELINE_DIR / "757a5df0.json").read_text())
    assert baseline["rows"]["Create Regulation|Regulators"] == "DROPPED (not stored)"
    assert all(change["reason"] != "<one-line reason>" for change in baseline.get("changes", {}).values())
    known = json.loads(gate.KNOWN_GAPS.read_text())["gaps"]
    assert all(v.get("reason") and v.get("ref") for v in known.values())


# ── probe.py: the raw-store column ──

@pytest.fixture
def raw():
    data = json.loads((FIXTURES / "raw_entity_external_reference.json").read_text())
    return probe.parse_raw_entity(data)


def test_raw_entity_parses_properties_arrays_and_effective_times(raw):
    assert raw["properties"]["authors"] == ["RTP CreateExternalReference Authors-1",
                                            "RTP CreateExternalReference Authors-2"]
    assert raw["properties"]["additionalProperties"] == {"rtpKey": "RTP CreateExternalReference AdditionalProperties"}
    assert raw["effectiveFromTime"].startswith("2020-01-02")
    assert raw["effectiveToTime"].startswith("2031-01-02")
    assert "Anchors" in raw["classifications"]


def test_stored_raw_separates_not_stored_from_not_returned(raw):
    authors = {"attribute": "Authors"}
    assert probe.stored_raw(authors, "properties.authors", raw, None)[0] == "yes"
    assert probe.stored_raw({"attribute": "Effective From"}, "properties.effectiveFrom", raw, None)[0] == "yes"
    assert probe.stored_raw({"attribute": "Regulators"}, "properties.regulators", raw, None) == ("no", None)
    assert probe.stored_raw({"attribute": "Search Keywords"}, "rel.searchKeywords.keyword", raw, None)[0] == "not checked"
    assert probe.stored_raw(authors, "properties.authors", None, "HTTP 404")[0] == "not checked"
    assert probe.split_verdict("DROPPED", "yes") == "NOT RETURNED (stored)"
    assert probe.split_verdict("DROPPED", "no") == "DROPPED (not stored)"
    assert probe.split_verdict("DROPPED", "not checked") == "DROPPED (raw read not applicable)"
    assert probe.split_verdict("CHANGED", "yes") == "CHANGED"


def test_parse_raw_entity_without_an_entity():
    assert probe.parse_raw_entity({"class": "EntityDetailResponse", "relatedHTTPCode": 404}) is None


# ── probe.py: Status is read from the type's own field ──

def test_status_plan_uses_the_types_own_field():
    kind, md, expected, location = probe.status_plan({"OM_TYPE": "Glossary"}, set())
    assert (md, location) == ("DRAFT", "properties.contentStatus")
    kind, md, expected, location = probe.status_plan({"OM_TYPE": "Person"}, set())
    assert kind == "SKIPPED (no status property)" and md is None


# ── the digest pin (read-back follow-up a) ──

def test_full_digest_is_accepted():
    assert scratch.checked_digest(scratch.DEFAULT_DIGEST) == scratch.DEFAULT_DIGEST


@pytest.mark.parametrize("digest", ["latest", "6.3", "sha256:757a5df0", "sha256:" + "g" * 64,
                                    "757a5df0db06f526cd92565210eed55ab60adc8e7ab6536a402f33efafc7ea9a", ""])
def test_a_tag_or_partial_digest_is_refused(digest):
    with pytest.raises(scratch.Refused):
        scratch.checked_digest(digest)


def test_scratch_cli_refuses_a_tag_before_docker(monkeypatch):
    monkeypatch.setattr(scratch, "docker", lambda *a, **k: (_ for _ in ()).throw(AssertionError("docker called")))
    with pytest.raises(scratch.Refused):
        scratch.main(["up", "--digest", "latest"])


def test_gate_cli_refuses_a_tag_before_anything():
    with pytest.raises(scratch.Refused):
        gate.main(["--digest", "latest"])


# ── "not applied" reports from Dr.Egeria's warnings section ──

def test_not_applied_reports_are_read_per_qualified_name():
    log = """Processing Warnings:

-- Create Governance Action Process (RTP::X::CreateGovernanceActionProcess) --
   - not applied: Parent Relationship Attributes: it needs a Parent Relationship Type Name to say which relationship properties these are (rtpKey)
   - some other warning
-- Create Data Value Specification (RTP::X::CreateDataValueSpecification) --
   - not applied: Absolute Uncertainty: '7.5' isn't a whole number; Egeria stores it as an integer
"""
    reports = probe.not_applied_reports(log)
    assert reports["RTP::X::CreateGovernanceActionProcess"] == {
        "Parent Relationship Attributes": "it needs a Parent Relationship Type Name to say which relationship "
                                          "properties these are (rtpKey)"}
    assert reports["RTP::X::CreateDataValueSpecification"]["Absolute Uncertainty"].startswith("'7.5' isn't")


def test_send_rejected_only_unblocks_the_pyegeria_side_attributes(monkeypatch):
    monkeypatch.setattr(probe, "SEND_REJECTED", True)
    assert probe.plan({"name": "Parent Relationship Attributes", "style": "Dictionary"}, "X")[1] is not None
    assert probe.plan({"name": "Extended Properties", "style": "Dictionary"}, "X")[0].startswith("REJECTED")
    monkeypatch.setattr(probe, "SEND_REJECTED", False)
    assert probe.plan({"name": "Parent Relationship Attributes", "style": "Dictionary"}, "X")[0].startswith("REJECTED")


def test_a_command_that_now_creates_brings_its_static_rejected_rows_as_new_rows():
    base = {"Create Schema Type|": "CREATE-FAILED"}
    cur = {"Create Schema Type|Description": "MATCH",
           "Create Schema Type|Extended Properties": "REJECTED (breaks the create)"}
    result = gate.compare(base, cur, {})
    assert not result["failed"]
    assert ("Create Schema Type|Extended Properties", "REJECTED (breaks the create)") in result["new_rows"]
    assert result["rows_gone"] == [("Create Schema Type|", "CREATE-FAILED")]


def test_a_new_rejected_row_in_a_command_that_already_created_still_fails():
    result = gate.compare({"Create Glossary|Description": "MATCH"},
                          {"Create Glossary|Description": "MATCH",
                           "Create Glossary|New Thing": "REJECTED (breaks the create)"}, {})
    assert result["failed"] and result["new_failures"]


# ── scratch fidelity: PostgreSQL repository, Core Content Pack, defaults ──

def test_store_loads_only_the_listed_content_packs(image_copy):
    scratch.apply_edits(image_copy, "postgres")
    text = (image_copy / "data/servers/simple-metadata-store/config/simple-metadata-store.config").read_text()
    assert "SimpleCatalog" not in text and "Coco" not in text
    assert scratch.archive_files(text) == list(scratch.CONTENT_PACKS)
    assert scratch.CONTENT_PACKS[0] == "content-packs/CoreContentPack.omarchive"
    assert not any("Coco" in pack for pack in scratch.CONTENT_PACKS)


def test_postgres_mode_starts_no_server_and_points_at_the_scratch_database(image_copy):
    scratch.apply_edits(image_copy, "postgres")
    props = (image_copy / "application.properties").read_text()
    assert "startup.server.list=\n" in props + "\n" or "startup.server.list=" in props.splitlines()
    assert '"repositoryDatabaseURL" : "jdbc:postgresql://egeria-scratch-roundtrip-pg:5432/egeria",\\' in props
    assert "localhost:5432" not in props


def test_memory_mode_starts_both_servers(image_copy):
    scratch.apply_edits(image_copy, "memory")
    assert "startup.server.list=simple-metadata-store,view-server" in (image_copy / "application.properties").read_text()


def test_down_removes_containers_network_and_volume(monkeypatch, tmp_path):
    calls = []
    state = {"ps": ["egeria-scratch-roundtrip", "egeria-scratch-roundtrip-pg"], "network": ["roundtrip-net"],
             "volume": ["roundtrip-pg-data"]}

    def fake_docker(*args, check=True):
        calls.append(args)
        if args[0] == "ps":
            return "\n".join(state["ps"])
        if args[:2] == ("network", "ls"):
            return "\n".join(state["network"])
        if args[:2] == ("volume", "ls"):
            return "\n".join(state["volume"])
        if args[0] == "rm":
            state["ps"].remove(args[-1])
        if args[:2] == ("network", "rm"):
            state["network"].remove(args[-1])
        if args[:2] == ("volume", "rm"):
            state["volume"].remove(args[-1])
        return ""
    monkeypatch.setattr(scratch, "docker", fake_docker)
    monkeypatch.setattr(scratch, "port_free", lambda port=19443: True)
    scratch.down(tmp_path)
    assert ("network", "rm", "roundtrip-net") in calls and ("volume", "rm", "roundtrip-pg-data") in calls
    assert ("rm", "-f", "egeria-scratch-roundtrip-pg") in calls


def test_up_refuses_below_15_gb(monkeypatch, tmp_path):
    monkeypatch.setattr(scratch, "labelled", lambda: [])
    monkeypatch.setattr(scratch, "labelled_networks", lambda: [])
    monkeypatch.setattr(scratch, "labelled_volumes", lambda: [])
    monkeypatch.setattr(scratch, "port_free", lambda port=19443: True)
    monkeypatch.setattr(scratch, "docker", lambda *a, **k: "present")
    monkeypatch.setattr(scratch, "docker_free_gb", lambda image: 9.5)
    with pytest.raises(SystemExit) as exc:
        scratch.up(scratch.DEFAULT_DIGEST, tmp_path)
    assert "9.5 GB free" in str(exc.value)


def test_send_rejected_is_the_default():
    assert probe.SEND_REJECTED is True


# ── read-back locations (F-B) ──

def test_domain_names_compare_as_egerias_numbers():
    assert probe.domain_number("Data") == 1 and probe.domain_number("All Domains") == 0
    assert probe.domain_number("IT Infrastructure") == 4 and probe.domain_number("Nonsense") == "Nonsense"
    row = {"attribute": "Domain Identifier", "kind": "valid", "sent": "Data", "property": "domainIdentifier",
           "variable": "domain_identifier", "default": "All Domains", "location": None}
    assert probe.verdict(row, {"properties": {"domainIdentifier": 1}})[0] == "MATCH"


def test_search_keywords_read_back_by_display_name():
    element = {"searchKeywords": [{"relatedElement": {"properties": {"displayName": "RTP kw-2"}}},
                                  {"relatedElement": {"properties": {"displayName": "RTP kw-1"}}}]}
    row = {"attribute": "Search Keywords", "kind": "list", "sent": ["RTP kw-1", "RTP kw-2"], "property": None,
           "variable": "search_keywords", "default": None, "location": None}
    assert probe.verdict(row, element)[0] == "MATCH"
    assert sorted(probe.dig(element, "rel.searchKeywords.displayName")) == ["RTP kw-1", "RTP kw-2"]


def test_project_type_reads_the_classification_it_names():
    element = {"elementHeader": {"projectKinds": [{"classificationName": "Campaign",
                                                   "classificationProperties": {"class": "CampaignProperties"}}]}}
    row = {"attribute": "Project Type", "kind": "valid", "sent": "Campaign", "property": None,
           "variable": "project_type", "default": None, "location": None}
    assert probe.verdict(row, element)[0] == "MATCH"


def test_a_stored_dict_with_extra_keys_matches():
    row = {"attribute": "Additional Properties", "kind": "dict", "sent": {"rtpKey": "x"}, "property": None,
           "variable": "additional_properties", "default": None, "location": None}
    assert probe.verdict(row, {"properties": {"additionalProperties": {"rtpKey": "x", "other": "y"}}})[0] == "MATCH"


def test_summary_row_returns_the_qualified_name_dr_egeria_used():
    log = ("│ Create ToDo │ Create ToDo │ SUCCESS │ No │ RTP CreateTodo DisplayName X │ "
           "Coco Pharmaceuticals::ToDo::RTP-x │ Executed Create ToDo (GUID: 5d2a1857-27fb-4615-aaae-e90e362f09b5) │")
    status, message, guid, qn = probe.summary_row(log, "Create ToDo", "RTP CreateTodo DisplayName X")
    assert status == "SUCCESS" and guid == "5d2a1857-27fb-4615-aaae-e90e362f09b5"
    assert qn == "Coco Pharmaceuticals::ToDo::RTP-x"


def test_external_source_guid_is_a_control_attribute():
    assert probe.plan({"name": "External Source GUID", "style": "GUID"}, "X")[0] == "SKIPPED (control)"


def test_schema_link_properties_are_phase_2():
    for name in ("Element Position", "Min Cardinality", "Max Cardinality"):
        assert probe.plan({"name": name, "style": "Simple Int"}, "X")[0] == "SKIPPED (relationship – phase 2)"

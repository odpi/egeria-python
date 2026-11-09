"""RS-EGERIA-TIER stage 1: report specs held in Egeria, run from plain pyegeria.

Covers the brief's gate list: the microflow/1 converter (format 0 -> v1 -> FormatSet, v1 ->
FormatSet), precedence and shadowing, egeria:/builtin:/seed: addressing, manifest-last and an
interrupted sync, the sync lock, the Class.method allowlist (every function today's local specs
name, and a dotted path refused), fetch-on-call write-through versus a shared cache, and the
spec_source envelope key. No live Egeria: a fake client serves recorded elements.
"""
from __future__ import annotations

import copy
import json
import os

import pytest

import pyegeria.view.base_report_formats as brf
import pyegeria.view.egeria_spec_cache as esc
from pyegeria.view import microflow as mfm
from pyegeria.view._output_format_models import FormatSetDict

pytestmark = pytest.mark.unit

E_GUID = "54aae5b9-96c9-42a5-a357-aaa281cb76f9"
FOLDER_QN = "ReportSpecFolder::scratch::E-Collections-test"
FOLDER_GUID = "f01de400-0000-0000-0000-000000000001"

# E-Collections exactly as Egeria holds it on 2026-11-08 (format 0: a bare list).
E_COLLECTIONS_FORMAT0 = json.dumps([{
    "stage": "producer/find", "type": "Collection", "function": "CollectionManager.find_collections",
    "params": {"search_string": "$search_string"}, "required_params": ["search_string"],
    "optional_params": ["sequencing_order", "sequencing_property", "page_size", "start_from", "starts_with",
                        "ends_with", "ignore_case", "classification_names", "metadata_element_subtypes",
                        "metadata_element_type"],
    "out": "CollectionRow",
    "columns": ["display_name", "qualified_name", "category", "description", "type_name", "url"]}])
BUILTIN_ALIASES = ["Collection", "RootCollection", "Folder", "ReferenceList", "HomeCollection", "ResultsSet",
                   "RecentAccess", "WorkItemList", "Namespace"]


def spec_element(label="E-Collections", guid=E_GUID, version=1, microflow=E_COLLECTIONS_FORMAT0, *,
                 status="ACTIVE", type_name="ReportSpec", qn=None, display=None, aliases=None,
                 version_identifier="1.0", description="Attributes generic to all Collections.",
                 annotations='{"wikilinks": ["[[Commons]]"]}'):
    supers = ["ReportType", "DataSpec", "Collection", "Referenceable"] if type_name == "ReportSpec" else ["Collection"]
    props = {"class": "ReportSpecProperties", "qualifiedName": qn or f"ReportSpec::{label}",
             "displayName": display if display is not None else label, "description": description,
             "versionIdentifier": version_identifier, "category": "Collections",
             "purpose": "Common Collection Information", "microflow": microflow, "targetTypeName": "Collection",
             "aliases": list(BUILTIN_ALIASES if aliases is None else aliases), "outputTypes": ["ALL"]}
    if status is not None:
        props["contentStatus"] = status
    if annotations is not None:
        props["additionalProperties"] = {"annotations": annotations}
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name, "superTypeNames": supers},
                              "versions": {"version": version, "updateTime": "2026-11-08T20:22:10.414+00:00"}},
            "properties": props}


def folder_element(qn=FOLDER_QN, guid=FOLDER_GUID):
    return {"elementHeader": {"guid": guid, "type": {"typeName": "CollectionFolder"}, "versions": {"version": 1}},
            "properties": {"qualifiedName": qn, "displayName": "E-Collections test folder"}}


class FakeEgeria:
    """Recorded elements, served the way CollectionManager's sync methods return them."""

    def __init__(self):
        self.user_id = "erinoverview"
        self.platform_url = "https://localhost:9443"
        self.view_server = "qs-view-server"
        self.folders = {FOLDER_QN: folder_element()}
        self.members = {FOLDER_GUID: []}
        self.elements = {}
        self.full_fetches = []

    def put(self, el, *, folder=FOLDER_GUID):
        self.elements[el["elementHeader"]["guid"]] = el
        if folder:
            self.members.setdefault(folder, [])
            self.members[folder] = [m for m in self.members[folder] if m["elementHeader"]["guid"] !=
                                    el["elementHeader"]["guid"]] + [el]

    def remove_member(self, guid, folder=FOLDER_GUID):
        self.members[folder] = [m for m in self.members[folder] if m["elementHeader"]["guid"] != guid]

    def get_collections_by_name(self, name, metadata_element_type_name=None, output_format="JSON", **_):
        if metadata_element_type_name == "CollectionFolder":
            f = self.folders.get(name)
            return [f] if f else "No elements found"
        hits = [e for e in self.elements.values()
                if name in (e["properties"]["qualifiedName"], e["properties"]["displayName"])]
        return hits or "No elements found"

    def get_collection_members(self, collection_guid=None, output_format="JSON", **_):
        return copy.deepcopy(self.members.get(collection_guid)) or "No elements found"

    def get_collection_by_guid(self, guid, output_format="JSON", **_):
        self.full_fetches.append(guid)
        e = self.elements.get(guid)
        return copy.deepcopy(e) if e else "No elements found"


@pytest.fixture
def tier(monkeypatch, tmp_path):
    """An isolated cache and user specs directory; the registry's CONFIG/RUNTIME tiers empty."""
    cache = tmp_path / "cache"
    user = tmp_path / "user_specs"
    user.mkdir()
    monkeypatch.setenv(esc.CACHE_DIR_ENV, str(cache))
    monkeypatch.setenv("PYEGERIA_USER_REPORT_SPECS_DIR", str(user))
    monkeypatch.delenv("PYEGERIA_USER_FORMAT_SETS_DIR", raising=False)
    monkeypatch.delenv(esc.DRAFTS_ENV, raising=False)
    monkeypatch.delenv(esc.FOLDERS_ENV, raising=False)
    # CONFIG reloads from the entry points (pyegeria's own demo specs are part of the 437) and the
    # empty temporary user directory; monkeypatch restores the original tier object afterwards.
    monkeypatch.setattr(brf, "_CONFIG_REPORT_FORMATS", FormatSetDict())
    monkeypatch.setattr(brf, "_config_report_specs_loaded", True)
    brf.refresh_report_specs()
    monkeypatch.setattr(brf, "_SHADOW_WARNED", set())
    monkeypatch.setattr(brf, "_ALIAS_WARNED", set())
    monkeypatch.setattr(esc, "_FETCHED", {})
    esc._invalidate_tier()
    yield {"cache": cache, "user": user, "mp": monkeypatch}
    brf.unregister_report_spec("E-Collections")
    esc._invalidate_tier()


@pytest.fixture
def log_lines():
    from loguru import logger
    lines = []
    sink = logger.add(lambda m: lines.append(m.record["message"]), level="WARNING")
    yield lines
    logger.remove(sink)


def builtin(label="Collections"):
    return brf.base_report_specs[label]


def dump_formats(fs):
    return [f.model_dump() for f in fs.formats]


def per_type(fs):
    out = {}
    for f in fs.formats:
        for t in f.types:
            out.setdefault(t, [c.model_dump() for c in f.attributes])
    return out


# ── 1. The converter ──

def test_format0_converts_to_v1_with_params_and_all_columns():
    notes = []
    mf = mfm.microflow_from_legacy(json.loads(E_COLLECTIONS_FORMAT0), notes=notes)
    assert mf.format == "microflow/1"
    assert mf.params["search_string"].required is True
    assert [n for n, p in mf.params.items() if not p.required][0] == "sequencing_order"
    assert all(p.type == "string" for p in mf.params.values())
    assert mf.formatters["ALL"].columns[0] == "display_name"
    assert "required_params" not in (mf.stages[0].model_extra or {})
    assert mf.stages[0].out == "CollectionRow" and mf.stages[0].type == "Collection"
    assert any("typed 'string'" in n for n in notes)


def test_format0_to_format_set_equals_the_builtin_action_and_all_format():
    mf, stored, _ = mfm.parse_microflow(E_COLLECTIONS_FORMAT0)
    assert stored == 0
    fs = mfm.microflow_to_format_set(mf, label="E-Collections", target_type="Collection")
    assert fs.action.model_dump() == builtin().action.model_dump()
    all_fmt = next(f for f in builtin().formats if "ALL" in f.types)
    assert dump_formats(fs) == [all_fmt.model_dump()]


def test_v1_round_trips_the_builtin_collections_exactly():
    b = builtin()
    mf = mfm.format_set_to_microflow(b)
    text = mf.to_json()
    mf2, stored, _ = mfm.parse_microflow(text)
    assert stored == 1
    fs = mfm.microflow_to_format_set(mf2, label="X", heading=b.heading, description=b.description,
                                     target_type=b.target_type, aliases=b.aliases, family=b.family)
    assert fs.action.model_dump() == b.action.model_dump()
    assert dump_formats(fs) == dump_formats(b)
    assert set(mf2.formatters) == {"MERMAID", "DICT", "TABLE", "REPORT", "ALL"}


@pytest.mark.parametrize("label", ["Glossaries", "Digital-Products", "Projects"])
def test_v1_round_trips_other_builtins(label):
    b = brf.get_report_registry().get(label)
    if b is None or not b.action:
        pytest.skip(f"{label} is not a built-in with an action here")
    fs = mfm.microflow_to_format_set(mfm.format_set_to_microflow(b), label=label, target_type=b.target_type)
    assert fs.action.model_dump() == b.action.model_dump()
    # a Format row serving several output types becomes one formatter per type; what each output
    # type selects is unchanged
    assert per_type(fs) == per_type(b)


def test_analytic_stage_maps_to_analytic_function():
    text = json.dumps({"format": "microflow/1", "params": {"element_type": {"required": False}},
                       "stages": [{"stage": "producer/analytic", "function": "count_elements",
                                   "params": {"limit": 5}}],
                       "formatters": {"DICT": {"columns": ["label", "value"]}}})
    mf, _, _ = mfm.parse_microflow(text)
    fs = mfm.microflow_to_format_set(mf, label="A")
    assert fs.action.analytic_function == "count_elements"
    assert fs.action.analytic_spec_params == {"limit": 5}
    assert fs.action.function is None


@pytest.mark.parametrize("stages,words", [
    ([{"stage": "producer/find", "function": "CollectionManager.find_collections"},
      {"stage": "producer/find", "function": "GlossaryManager.find_glossaries"}], "2 find producers"),
    ([{"stage": "producer/find", "function": "CollectionManager.find_collections"},
      {"stage": "processor/join"}], "processor/join"),
    ([{"stage": "snapshot/write"}], "snapshot/write"),
    ([{"stage": "producer/find", "type": "Glossary"}], "no function"),
])
def test_stages_stage1_cannot_run_are_refused_with_words(stages, words):
    mf, _, _ = mfm.parse_microflow({"format": "microflow/1", "stages": stages,
                                    "formatters": {"ALL": {"columns": ["display_name"]}}})
    with pytest.raises(mfm.CannotRunYet) as exc:
        mfm.microflow_to_format_set(mf, label="X")
    assert str(exc.value).startswith("uses stages this pyegeria cannot run yet: ")
    assert words in str(exc.value)


def test_columns_star_needs_a_shape():
    mf, _, _ = mfm.parse_microflow({"format": "microflow/1", "stages": [
        {"stage": "producer/find", "function": "CollectionManager.find_collections"}],
        "formatters": {"DICT": {"columns": "*"}}})
    with pytest.raises(mfm.CannotRunYet, match="registered shape"):
        mfm.microflow_to_format_set(mf, label="X")


@pytest.mark.parametrize("text,words", [
    ("[{not json", "not valid JSON"),
    ('{"format": "microflow/2", "stages": []}', "unknown microflow format"),
    ('"just a string"', "not a microflow/1 object"),
    ('{"format": "microflow/1", "stages": []}', "at least one stage"),
    ('{"format": "microflow/1", "stages": [{"stage": "producer/find"}], "bogus": 1}', "not valid"),
])
def test_bad_microflow_text_is_an_error_with_words(text, words):
    with pytest.raises(mfm.MicroflowError, match=words):
        mfm.parse_microflow(text)


def test_json_schema_file_ships_and_agrees_on_the_format_const():
    path = os.path.join(os.path.dirname(mfm.__file__), "schemas", "microflow-1.json")
    schema = json.load(open(path))
    assert schema["properties"]["format"]["const"] == mfm.MICROFLOW_FORMAT


# ── 2. The allowlist ──

def _all_local_functions():
    funcs, analytics = {}, {}
    for label, fs in brf.get_report_registry().items():
        a = fs.action if isinstance(fs.action, dict) or fs.action is None else fs.action.model_dump()
        if not a:
            continue
        if a.get("function"):
            funcs.setdefault(a["function"], []).append(label)
        if a.get("analytic_function"):
            analytics.setdefault(a["analytic_function"], []).append(label)
    return funcs, analytics


def test_every_function_todays_runnable_local_specs_name_passes_the_allowlist(tier):
    from pyegeria.view.spec_resolver import resolve_all
    results = resolve_all()
    funcs, analytics = _all_local_functions()
    refused = {}
    for func, labels in funcs.items():
        ok, why = mfm.find_method_allowed(func)
        if not ok:
            refused[func] = (labels, why)
    # Exactly the find methods of the two specs the resolver already lists as unrunnable (their
    # methods do not exist); every other find method a local spec names is allowed.
    assert set(refused) == {"ServerClient.get_asset_graph", "DataDesigner.find_data_classes"}, refused
    for func, (labels, _why) in refused.items():
        assert all(not results[lb].runnable for lb in labels)
    for name in analytics:
        ok, why = mfm._analytic_allowed(name)
        assert ok, (name, why)


@pytest.mark.parametrize("func,words", [
    ("pyegeria.omvs.collection_manager.CollectionManager.find_collections", "dotted module path"),
    ("os.system", "not an EgeriaTech client class"),
    ("CollectionManager.create_collection", "not on the allowlist"),
    ("CollectionManager.delete_collection", "not on the allowlist"),
    ("CollectionManager.get_collection_by_guid", "not on the allowlist"),  # read-only by name, not listed
    ("EgeriaTech.find_collections", "not on the allowlist"),  # entries are Class.method as written
    ("NotAClient.find_things", "not an EgeriaTech client class"),
    ("CollectionManager.find_no_such_thing", "not on the allowlist"),
])
def test_allowlist_refuses_with_words(func, words):
    ok, why = mfm.find_method_allowed(func)
    assert not ok and words in why


def test_allowlist_refuses_python_binding_and_dotted_analytic():
    mf, _, _ = mfm.parse_microflow({"format": "microflow/1", "stages": [
        {"stage": "producer/analytic", "function": "pyegeria.view.overview_metrics.count_elements"}],
        "formatters": {"DICT": {"columns": ["value"]}}})
    with pytest.raises(mfm.AllowlistRefusal, match="dotted path"):
        mfm.check_allowlist(mf)
    mf, _, _ = mfm.parse_microflow({"format": "microflow/1", "stages": [
        {"stage": "producer/find", "function": "CollectionManager.find_collections", "python": "os:system"}],
        "formatters": {"DICT": {"columns": ["value"]}}})
    with pytest.raises(mfm.AllowlistRefusal, match="python binding"):
        mfm.check_allowlist(mf)


_WRITE_CSV = "get_create_csv_data_file_element_from_template"


def test_denylist_refuses_the_csv_template_write_on_every_class_and_async_twin():
    assert f"AutomatedCuration.{_WRITE_CSV}" in mfm.FIND_METHOD_DENYLIST
    for decl in (f"AutomatedCuration.{_WRITE_CSV}", f"AutomatedCuration._async_{_WRITE_CSV}",
                 f"EgeriaTech.{_WRITE_CSV}", f"_client_new.{_WRITE_CSV}"):
        ok, why = mfm.find_method_allowed(decl)
        assert not ok and "denylist" in why, (decl, why)


def test_async_twin_of_an_allowlisted_method_is_allowed():
    assert mfm.find_method_allowed("CollectionManager._async_find_collections") == (True, "")


def test_allowlist_is_the_census_plus_additions_and_never_meets_the_denylist():
    assert mfm.FIND_METHOD_ALLOWLIST == mfm._CENSUS_FIND_METHODS | mfm.FIND_METHOD_ADDITIONS
    assert len(mfm._CENSUS_FIND_METHODS) == 45
    assert not (mfm.FIND_METHOD_ALLOWLIST & mfm.FIND_METHOD_DENYLIST)
    denied = {e.rsplit(".", 1)[-1] for e in mfm.FIND_METHOD_DENYLIST}
    assert not {e.rsplit(".", 1)[-1] for e in mfm.FIND_METHOD_ALLOWLIST} & denied


def test_every_allowlist_entry_passes_the_allowlist():
    """Each entry's class maps to an EgeriaTech client class and the method exists there."""
    refused = {}
    for decl in sorted(mfm.FIND_METHOD_ALLOWLIST):
        ok, why = mfm.find_method_allowed(decl)
        if not ok:
            refused[decl] = why
    assert not refused, refused


def test_every_runnable_builtin_spec_function_is_on_the_allowlist(tier):
    """The stage-2 seed writes today's built-in and generated specs into Egeria; none may be refused."""
    from pyegeria.view.spec_resolver import resolve
    missing = {}
    for source in (brf.base_report_specs, brf.generated_format_sets):
        for label, fs in source.items():
            a = fs.action if isinstance(fs.action, dict) or fs.action is None else fs.action.model_dump()
            func = (a or {}).get("function")
            if not func or not resolve(fs, label).runnable:
                continue
            ok, why = mfm.find_method_allowed(func)
            if not ok:
                missing.setdefault(func, []).append(label)
    assert not missing, missing


# Write words, per the Architect's read-back of stage 1 (P1). A name matches when one of its
# _-separated words starts with one; a docstring's first line when a word there does.
_WRITE_WORDS = r"(create|add|update|delete|remove|attach|detach|set|start|stop|run|register|refresh|clear|load)"

# Reviewed 2026-11-09, keyed by Class.method as on the allowlist: each matches a write word and is a
# read. Why it matched:
_REVIEWED_READS = {
    "DataDiscovery.get_security_posture_history": "'one per test run' - returns posture summaries",
    "ServerClient.get_attached_comments": "'attached' - lists the comments attached to an element",
}


def test_no_allowlisted_method_reads_as_a_write():
    """Scan every FIND_METHOD_ALLOWLIST entry for write words in its method name or its docstring's
    first line (sync and `_async_` twin). A hit must be in `_REVIEWED_READS`, keyed by Class.method.
    A new hit means: read the method; if it writes, take it off the allowlist (and add it to
    FIND_METHOD_DENYLIST); if it reads, add it to `_REVIEWED_READS` with why it matched."""
    import inspect
    import re
    import sys
    from pyegeria.view.spec_resolver import _find_method

    name_re = re.compile(r"(^|_)" + _WRITE_WORDS)
    doc_re = re.compile(r"\b" + _WRITE_WORDS, re.I)
    hits = {}
    for decl in sorted(mfm.FIND_METHOD_ALLOWLIST):
        bare = decl.rsplit(".", 1)[-1]
        method, why = _find_method(decl)
        assert method is not None, (decl, why)
        # `_find_method` returns the `_async_` function; its defining class holds the sync twin.
        owner = getattr(sys.modules.get(method.__module__), method.__qualname__.split(".")[0], None)
        firsts = []
        for m in (method, getattr(owner, bare, None)):
            doc = (inspect.getdoc(m) or "").strip().splitlines() if m is not None else []
            firsts.append(doc[0] if doc else "")
        if name_re.search(bare) or any(doc_re.search(f) for f in firsts):
            hits[decl] = " | ".join(f[:120] for f in firsts if f)
    unreviewed = {k: v for k, v in hits.items() if k not in _REVIEWED_READS}
    assert not unreviewed, unreviewed
    stale = set(_REVIEWED_READS) - set(hits)
    assert not stale, f"reviewed entries no longer hit (remove them): {sorted(stale)}"


def test_unknown_stage_keys_are_recorded_as_notes_and_binders_go_to_the_action():
    import warnings
    mf, _, _ = mfm.parse_microflow({"format": "microflow/1", "stages": [
        {"stage": "producer/find", "function": "CollectionManager.find_collections",
         "analytic_binders": {"x": 1}, "colour": "blue"}],
        "formatters": {"DICT": {"columns": ["display_name"]}}})
    notes = []
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        fs = mfm.microflow_to_format_set(mf, label="T", notes=notes)
    assert any("stage 0 (producer/find)" in n and n.endswith("colour; ignored") for n in notes), notes
    assert not any("analytic_binders" in n for n in notes), notes
    assert fs.action._dropped_binders == ["x"]
    assert "analytic_binders" not in fs.model_dump()["action"]


# ── 2b. A binder on an Egeria-held spec warns exactly as #561 does for a local one (O1-a) ──

def _binder_text(names):
    from pyegeria.view import spec_resolver as sr
    return (f"{sr.BINDERS_DEPRECATED_PREFIX} (binders for: {names}); declare these arguments as the routine's "
            f"inputs, which the environment's role supply provides")


def _binder_microflow(fmt, binders):
    stage = {"stage": "producer/find", "type": "Collection", "function": "CollectionManager.find_collections",
             "params": {"search_string": "$search_string"}}
    if binders is not _ABSENT:
        stage["analytic_binders"] = binders
    if fmt == 0:
        return json.dumps([dict(stage, required_params=["search_string"], columns=["display_name"])])
    return json.dumps({"format": "microflow/1", "params": {"search_string": {"type": "string", "required": True}},
                       "stages": [stage], "formatters": {"ALL": {"columns": ["display_name"]}}})


_ABSENT = object()
_BINDER_GUID = "b1d0e400-0000-0000-0000-000000000002"


def _sync_and_resolve(fmt, binders):
    import warnings
    from pyegeria.view import spec_resolver as sr
    eg = FakeEgeria()
    eg.put(spec_element("E-Binder", guid=_BINDER_GUID, microflow=_binder_microflow(fmt, binders), aliases=[]))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
        assert report.added == ["E-Binder"] and not report.skipped, report.render()
        esc._invalidate_tier()
        assert brf.report_spec_source("E-Binder")["tier"] == "egeria"
        result = sr.resolve_all()["E-Binder"]
    found = [w for w in result.warnings if w.startswith(sr.BINDERS_DEPRECATED_PREFIX)]
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)
                    and "analytic_binders" in str(w.message)]
    brf.unregister_report_spec("E-Binder")
    return found, deprecations, report


@pytest.mark.parametrize("fmt", [0, 1])
def test_egeria_held_spec_with_a_binder_resolves_with_exactly_the_561_warning(tier, fmt):
    found, deprecations, report = _sync_and_resolve(fmt, {"ods": "x.OdsReader", "mgr": "os.getcwd"})
    assert found == [_binder_text("mgr, ods")]
    assert deprecations  # the PR-B shim's DeprecationWarning fired on the Egeria-held spec too
    assert not any("analytic_binders" in n and "ignored" in n and "does not read" in n for n in report.notes)


@pytest.mark.parametrize("fmt", [0, 1])
@pytest.mark.parametrize("empty", [{}, None, [], _ABSENT])
def test_egeria_held_spec_with_an_empty_binder_stays_silent(tier, fmt, empty):
    found, deprecations, report = _sync_and_resolve(fmt, empty)
    assert found == [] and deprecations == []
    assert not any("analytic_binders" in n for n in report.notes)


# ── 3. The sync ──

def test_plain_sync_with_no_folders_configured_says_so(tier):
    report = esc.sync_report_specs(FakeEgeria())
    assert not report.added and "no report spec folders are configured" in report.notes[0]
    assert not (tier["cache"] / esc.MANIFEST).exists()


def test_sync_adds_format0_spec_warns_once_and_records_provenance(tier, log_lines):
    eg = FakeEgeria()
    eg.put(spec_element())
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert report.added == ["E-Collections"] and not report.skipped
    assert len([m for m in log_lines if "format-0" in m and "E-Collections" in m]) == 1
    manifest = json.loads((tier["cache"] / esc.MANIFEST).read_text())
    entry = manifest["entries"]["E-Collections"]
    assert entry["guid"] == E_GUID and entry["version"] == 1 and entry["folders"] == [FOLDER_QN]
    prov = json.loads((tier["cache"] / entry["provenance"]).read_text())
    assert prov["stored_format"] == 0 and prov["version_identifier"] == "1.0" and prov["sync_identity"] == "erinoverview"
    spec = json.loads((tier["cache"] / entry["file"]).read_text())
    assert spec["microflow"]["format"] == "microflow/1"
    assert entry["file"].startswith("E-Collections-54aae5b9")


def test_incremental_sync_fetches_only_new_or_higher_versions_and_prunes_by_membership(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    eg.full_fetches.clear()
    again = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert again.unchanged == ["E-Collections"] and eg.full_fetches == []
    v1 = mfm.format_set_to_microflow(builtin()).to_json()
    eg.put(spec_element(version=2, microflow=v1, version_identifier="1.1"))
    updated = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert updated.updated == ["E-Collections"] and eg.full_fetches == [E_GUID]
    eg.remove_member(E_GUID)
    pruned = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert pruned.pruned == ["E-Collections"]
    assert any("no longer a member" in n for n in pruned.notes)
    assert json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"] == {}
    assert sorted(p.name for p in tier["cache"].glob("*.json")) == [esc.MANIFEST]


def test_spec_in_two_folders_is_cached_once_listing_both(tier):
    eg = FakeEgeria()
    other_qn, other_guid = "ReportSpecFolder::scratch::other", "f01de400-0000-0000-0000-000000000002"
    eg.folders[other_qn] = folder_element(other_qn, other_guid)
    eg.put(spec_element())
    eg.put(spec_element(), folder=other_guid)
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN, other_qn])
    assert report.added == ["E-Collections"]
    entry = json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]["E-Collections"]
    assert entry["folders"] == sorted([FOLDER_QN, other_qn])


@pytest.mark.parametrize("element,words", [
    (spec_element(display="Other"), "label mismatch"),
    (spec_element(qn="Collection::E-Collections"), "neither 'ReportSpec::' nor 'ReportType::'"),
    (spec_element(type_name="CollectionFolder"), "not a ReportSpec"),
    (spec_element(microflow="[{not json"), "not valid JSON"),
    (spec_element(microflow='{"format": "microflow/9"}'), "unknown microflow format"),
    (spec_element(microflow=json.dumps([{"stage": "producer/find", "function": "os.path.join",
                                         "columns": ["display_name"]}])), "refused by the allowlist"),
    (spec_element(microflow=json.dumps({"format": "microflow/1", "stages": [
        {"stage": "producer/find", "function": "CollectionManager.find_collections"}],
        "formatters": {"ALL": {"columns": [{"field": "display_name", "detail_spec": "No-Such-Spec"}]}}})),
     "refused by load-time resolution"),
    (spec_element(microflow=json.dumps({"format": "microflow/1", "stages": [
        {"stage": "producer/find", "function": "CollectionManager.find_collections"}, {"stage": "processor/join"}],
        "formatters": {"ALL": {"columns": ["display_name"]}}})), "uses stages this pyegeria cannot run yet"),
    (spec_element(status="DEPRECATED"), "contentStatus DEPRECATED"),
])
def test_one_bad_spec_is_skipped_with_its_reason_and_never_fails_the_sync(tier, element, words):
    eg = FakeEgeria()
    eg.put(element)
    good = spec_element("Good-One", guid="99999999-0000-0000-0000-000000000000", aliases=[])
    eg.put(good)
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert "Good-One" in report.added
    reasons = " | ".join(f"{w}: {r}" for w, r in report.skipped)
    assert words in reasons, reasons


def test_one_label_held_by_two_elements_skips_both_naming_both_guids(tier):
    eg = FakeEgeria()
    g2 = "aaaaaaaa-0000-0000-0000-000000000000"
    eg.put(spec_element())
    eg.put(spec_element(guid=g2, qn="ReportType::E-Collections"))
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert not report.added
    who, why = report.skipped[0]
    assert who == "E-Collections" and E_GUID in why and g2 in why


def test_no_content_status_counts_as_active_with_a_note(tier):
    eg = FakeEgeria()
    eg.put(spec_element(status=None))
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert report.added == ["E-Collections"]
    assert any("no contentStatus" in n for n in report.notes)


def test_drafts_go_to_a_separate_cache_the_registry_reads_only_on_request(tier):
    eg = FakeEgeria()
    eg.put(spec_element("Draft-Spec", guid="dddddddd-0000-0000-0000-000000000000", status="DRAFT", aliases=[]))
    skipped = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert "--include-drafts" in skipped.skipped[0][1]
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN], include_drafts=True)
    assert report.drafts.added == ["Draft-Spec"]
    assert (tier["cache"] / esc.DRAFTS_DIR / esc.MANIFEST).exists()
    assert "Draft-Spec" not in brf.get_report_registry()
    tier["mp"].setenv(esc.DRAFTS_ENV, "1")
    esc._invalidate_tier()
    assert "Draft-Spec" in brf.get_report_registry()


def test_spec_sync_takes_only_that_label_and_prunes_nothing_else(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    other = spec_element("Other-Spec", guid="bbbbbbbb-0000-0000-0000-000000000000", aliases=[])
    eg.put(other, folder=None)
    eg.remove_member(E_GUID)  # would be pruned by a folder sync
    report = esc.sync_report_specs(eg, specs=["Other-Spec"])
    assert report.added == ["Other-Spec"] and report.pruned == []
    entries = json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]
    assert set(entries) == {"E-Collections", "Other-Spec"} and entries["Other-Spec"]["pinned"] is True


def test_folder_read_error_keeps_its_specs(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])

    def boom(*a, **k):
        raise RuntimeError("timeout")
    eg.get_collection_members = boom
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert report.pruned == [] and "kept as cached" in report.skipped[0][1]
    assert "E-Collections" in json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]


# ── 4. Manifest last; an interrupted sync; the lock ──

def test_interrupted_sync_leaves_the_previous_set_in_force(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    before = brf.select_report_format("E-Collections", "DICT")
    assert before["formats"]["types"] == ["ALL"]
    eg.put(spec_element(version=2, microflow=mfm.format_set_to_microflow(builtin()).to_json()))

    def crash(directory, manifest):
        raise KeyboardInterrupt("killed before the manifest")
    tier["mp"].setattr(esc, "_write_manifest", crash)
    with pytest.raises(KeyboardInterrupt):
        esc.sync_report_specs(eg, folders=[FOLDER_QN])
    esc._invalidate_tier()
    after = brf.select_report_format("E-Collections", "DICT")
    assert after["formats"]["types"] == ["ALL"]  # still version 1: the new file is not named yet
    assert json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]["E-Collections"]["version"] == 1


def test_second_sync_refuses_at_once_while_one_runs(tier):
    tier["cache"].mkdir(parents=True)
    with esc._SyncLock(tier["cache"]):
        import multiprocessing  # noqa: F401 -- flock is per open file description, so a second open conflicts
        with pytest.raises(esc.SyncAlreadyRunning, match=r"a sync is already running \(pid \d+\)"):
            eg = FakeEgeria()
            eg.put(spec_element())
            esc.sync_report_specs(eg, folders=[FOLDER_QN])
    # released: the next sync runs
    eg = FakeEgeria()
    eg.put(spec_element())
    assert esc.sync_report_specs(eg, folders=[FOLDER_QN]).added == ["E-Collections"]


# ── 5. The tier: precedence, shadowing, addressing, census ──

def _sync_e_collections(tier, microflow=E_COLLECTIONS_FORMAT0, version=1):
    eg = FakeEgeria()
    eg.put(spec_element(microflow=microflow, version=version))
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    return eg


def test_census_unchanged_by_an_empty_tier_and_plus_one_with_e_collections_only(tier):
    # (437 on a clean process, the stage-1 baseline; checked by the live census script. Here the
    # count is relative: earlier tests in the suite change the RUNTIME tier.)
    from pyegeria.view.spec_resolver import resolve_all
    base = set(brf.list_report_specs())
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(brf, "_egeria_tier", lambda: FormatSetDict())
        assert set(brf.list_report_specs()) == base  # tier disabled == tier loaded but empty
    n = len(resolve_all())
    assert n == len(base)
    _sync_e_collections(tier)
    now = set(brf.list_report_specs())
    assert now - base == {"E-Collections"} and base <= now and len(resolve_all()) == n + 1
    assert resolve_all()["E-Collections"].runnable
    # its aliases are the built-in's, so they are dropped: "Collection" still reaches the built-in
    assert brf.lookup_report_spec("Collection")[2] == "Collections"
    assert brf.get_report_registry()["E-Collections"].aliases == []


def test_egeria_spec_selects_like_the_builtin_on_formats_that_fall_back_to_all(tier):
    _sync_e_collections(tier)
    for fmt in ("MD", "ALL"):
        a = brf.select_report_format("Collections", fmt)
        b = brf.select_report_format("E-Collections", fmt)
        assert a["formats"] == b["formats"] and a["action"] == b["action"]


def test_egeria_v1_spec_selects_like_the_builtin_on_every_format(tier):
    _sync_e_collections(tier, microflow=mfm.format_set_to_microflow(builtin()).to_json())
    for fmt in ("DICT", "TABLE", "REPORT", "MERMAID", "ALL", "MD"):
        a = brf.select_report_format("Collections", fmt)
        b = brf.select_report_format("egeria:E-Collections", fmt)
        assert a["formats"] == b["formats"], fmt
        assert a["action"] == b["action"] and a["target_type"] == b["target_type"] and a["heading"] == b["heading"]


def test_local_copy_shadows_egeria_with_one_warning_and_egeria_prefix_still_reaches_it(tier, log_lines):
    _sync_e_collections(tier)
    local = FormatSetDict({"E-Collections": builtin().model_copy(update={"aliases": []})})
    local.save_to_json(str(tier["user"] / "e.json"))
    assert brf.refresh_report_specs() == []
    for _ in range(3):
        brf.get_report_registry()
    shadow_warnings = [m for m in log_lines if "shadows the egeria copy" in m]
    assert len(shadow_warnings) == 1 and "they differ" in shadow_warnings[0]
    assert brf.lookup_report_spec("E-Collections")[1] == "local"
    assert brf.select_report_format("E-Collections", "DICT")["formats"]["types"] == ["DICT"]
    assert brf.select_report_format("egeria:E-Collections", "DICT")["formats"]["types"] == ["ALL"]
    rows = {r["name"]: r for r in brf.list_report_specs(with_status=True)}
    assert rows["E-Collections"]["source"] == "local" and rows["E-Collections"]["shadows"] == "egeria"
    assert rows["egeria:E-Collections"]["shadowed_by"] == "local"
    assert rows["egeria:E-Collections"]["cache_age_s"] is not None


def test_runtime_registration_shadows_egeria_instead_of_raising(tier):
    _sync_e_collections(tier)
    brf.register_report_specs(FormatSetDict({"E-Collections": builtin().model_copy(update={"aliases": []})}),
                              source="portal")
    assert brf.lookup_report_spec("E-Collections")[1] == "local"


def test_egeria_shadows_a_builtin_label_and_builtin_and_seed_prefixes_reach_it(tier, log_lines):
    eg = FakeEgeria()
    eg.put(spec_element("Collections", aliases=[]))
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert brf.lookup_report_spec("Collections")[1] == "egeria"
    assert len([m for m in log_lines if "the egeria copy shadows the builtin copy" in m]) == 1
    assert brf.select_report_format("Collections", "DICT")["formats"]["types"] == ["ALL"]
    for prefix in ("builtin:", "seed:"):
        assert brf.select_report_format(f"{prefix}Collections", "DICT")["formats"]["types"] == ["DICT"]
    # the built-in's aliases go with it while it is shadowed... and come back when the copy is pruned
    eg.remove_member(E_GUID)
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    assert brf.lookup_report_spec("Collection")[2] == "Collections"
    assert brf.lookup_report_spec("Collections")[1] == "builtin"


def test_tier_is_reloaded_when_the_manifest_changes(tier):
    assert "E-Collections" not in brf.get_report_registry()
    _sync_e_collections(tier)  # the sync invalidates the in-process tier
    assert "E-Collections" in brf.get_report_registry()


def test_cache_dir_is_never_under_the_user_specs_dir_and_never_read_as_config(tier):
    tier["mp"].setenv(esc.CACHE_DIR_ENV, str(tier["user"] / "cache"))
    with pytest.raises(ValueError, match="inside the user report specs directory"):
        esc.cache_dir()
    with pytest.raises(ValueError):
        esc.sync_report_specs(FakeEgeria(), folders=[FOLDER_QN])
    # and the default location is outside it
    tier["mp"].delenv(esc.CACHE_DIR_ENV)
    default = esc.cache_dir("https://localhost:9443", "qs-view-server")
    assert default.parts[-4:] == ("cache", "report_specs", "localhost_9443", "qs-view-server")
    # a cache file that somehow sits in the user dir is not a top-level *.json, so CONFIG never reads it
    nested = tier["user"] / "cache" / "x"
    nested.mkdir(parents=True)
    (nested / "manifest.json").write_text("{}")
    assert all("cache" not in p for p in brf._user_report_spec_files())


def test_configured_folders_from_env(tier):
    tier["mp"].setenv(esc.FOLDERS_ENV, f"{FOLDER_QN}, ReportSpecFolder::b")
    assert esc.configured_folders() == [FOLDER_QN, "ReportSpecFolder::b"]
    eg = FakeEgeria()
    eg.put(spec_element())
    report = esc.sync_report_specs(eg)
    assert report.added == ["E-Collections"]
    assert ("ReportSpecFolder::b", "folder not found, or not visible to erinoverview") in report.skipped


# ── 6. Fetch on a call ──

def test_fetch_on_call_writes_through_to_a_per_user_cache(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    name = esc.fetch_spec_for_call(eg, "E-Collections")
    assert name == "egeria:E-Collections@v1"
    entries = json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]
    assert entries["E-Collections"]["guid"] == E_GUID
    assert brf.select_report_format(name, "ALL")["formats"]["types"] == ["ALL"]
    assert brf.report_spec_source(name)["tier"] == "egeria"


def test_fetch_on_call_never_writes_a_shared_cache_and_keeps_the_copy_in_process(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN], shared=True)
    manifest_before = (tier["cache"] / esc.MANIFEST).read_text()
    eg.put(spec_element(version=2, microflow=mfm.format_set_to_microflow(builtin()).to_json(),
                        version_identifier="1.1"))
    name = esc.fetch_spec_for_call(eg, "E-Collections")
    assert name == "egeria:E-Collections@v2"
    assert (tier["cache"] / esc.MANIFEST).read_text() == manifest_before
    assert esc._FETCHED[("E-Collections", 2)][1]["shared"] is True
    assert brf.select_report_format(name, "DICT")["formats"]["types"] == ["DICT"]  # the fetched v1.1
    assert brf.select_report_format("E-Collections", "DICT")["formats"]["types"] == ["ALL"]  # cache untouched
    assert eg.full_fetches[-1] == E_GUID  # looked up by the guid the cache knows


def test_failed_fetch_raises_with_words_and_never_falls_back(tier):
    _sync_e_collections(tier)
    eg = FakeEgeria()  # Egeria no longer has it
    with pytest.raises(esc.SpecFetchError, match="never falls back"):
        esc.fetch_spec_for_call(eg, "E-Collections")
    with pytest.raises(esc.SpecFetchError, match="built-in tier"):
        esc.fetch_spec_for_call(eg, "builtin:Collections")


async def test_async_fetch_through_a_find_request_helper(tier):
    from pyegeria.core._server_client import ServerClient

    class AsyncFake(FakeEgeria):
        async def _async_get_collection_by_guid(self, guid, output_format="JSON", **k):
            return self.get_collection_by_guid(guid)

        async def _async_get_collections_by_name(self, name, metadata_element_type_name=None, output_format="JSON",
                                                 **k):
            return self.get_collections_by_name(name, metadata_element_type_name)

    eg = AsyncFake()
    eg.put(spec_element())
    kwargs = {"refresh_spec": True, "page_size": 5}
    name = await ServerClient._async_refresh_report_spec(eg, "E-Collections", kwargs)
    assert name == "egeria:E-Collections@v1" and kwargs == {"page_size": 5}
    kwargs = {}
    assert await ServerClient._async_refresh_report_spec(eg, "Collections", kwargs) == "Collections"


# ── 7. Provenance in the run envelope ──

def test_spec_source_is_beside_kind_and_never_inside_data(tier, monkeypatch):
    from pyegeria.view import format_set_executor as fse
    _sync_e_collections(tier)
    rows = [{"display_name": "x"}]
    monkeypatch.setattr(fse, "_exec_report_spec_impl", lambda name, **k: {"kind": "json", "data": list(rows)})
    out = fse.exec_report_spec("E-Collections", output_format="DICT", params={"search_string": "x"})
    assert out["data"] == rows
    assert out["spec_source"] == {"tier": "egeria", "label": "E-Collections", "version": "1.0", "guid": E_GUID,
                                  "synced_at": out["spec_source"]["synced_at"]}
    out = fse.exec_report_spec("Collections", output_format="DICT", params={})
    assert out["spec_source"] == {"tier": "builtin", "label": "Collections", "version": None}


def test_footer_on_report_md_html_only_for_egeria_specs(tier, monkeypatch):
    from pyegeria.view import format_set_executor as fse
    _sync_e_collections(tier)
    monkeypatch.setattr(fse, "_exec_report_spec_impl",
                        lambda name, **k: {"kind": "text", "mime": "text/markdown", "content": "# H\nbody\n"})
    md = fse.exec_report_spec("E-Collections", output_format="MD")["content"]
    assert md.rstrip().splitlines()[-1].startswith("_E-Collections v1.0 (Egeria, synced ")
    assert brf.add_spec_footer(md, "E-Collections", "MD") == md  # idempotent
    assert fse.exec_report_spec("Collections", output_format="MD")["content"] == "# H\nbody\n"
    assert brf.add_spec_footer([{"a": 1}], "E-Collections", "DICT") == [{"a": 1}]
    assert brf.add_spec_footer("t", "E-Collections", "TABLE") == "t"
    html = brf.add_spec_footer("<p>x</p>", "E-Collections", "HTML")
    assert 'class="spec-source"' in html


def test_in_method_path_adds_the_footer_through_generate_formatted_output(tier):
    from pyegeria.core._server_client import ServerClient
    _sync_e_collections(tier)
    element = {"elementHeader": {"guid": "g1", "type": {"typeName": "Collection"},
                                 "origin": {"homeMetadataCollectionId": "m", "homeMetadataCollectionName": "m"},
                                 "versions": {"createdBy": "u", "createTime": "2026-11-08T00:00:00Z"}},
               "properties": {"displayName": "Coll A", "qualifiedName": "Collection::A"}}

    class Bare:
        pass
    out = ServerClient._generate_formatted_output(Bare(), [element], query_string="A", entity_type="Collection",
                                                  output_format="MD", report_spec="egeria:E-Collections")
    plain = ServerClient._generate_formatted_output(Bare(), [element], query_string="A", entity_type="Collection",
                                                    output_format="MD", report_spec="Collections")
    assert out.rstrip().splitlines()[-1].startswith("_E-Collections v1.0 (Egeria")
    assert out.rsplit("\n\n_E-Collections", 1)[0] == plain.rstrip()

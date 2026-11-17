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

    def get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON", start_from=0, **_):
        if start_from:   # one page of hits, then Egeria's null
            return "No elements found"
        if metadata_element_type == "CollectionFolder":
            f = self.folders.get(name)
            return [f] if f else "No elements found"
        hits = [e for e in self.elements.values()
                if name in (e["properties"]["qualifiedName"], e["properties"]["displayName"])]
        return hits or "No elements found"

    def get_element_by_unique_name(self, name, *_, **__):
        """Egeria's exact unique-name read (folders and recorded elements), or its not-found."""
        if name in self.folders:
            return copy.deepcopy(self.folders[name])
        for e in self.elements.values():
            if e["properties"]["qualifiedName"] == name:
                return copy.deepcopy(e)
        return "No elements found"

    def get_collection_members(self, collection_guid=None, output_format="JSON", start_from=0, page_size=0, **_):
        items = list(self.members.get(collection_guid) or [])
        items = items[start_from:start_from + page_size] if page_size else items[start_from:]
        return copy.deepcopy(items) or "No elements found"

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
    # T1: no tier test depends on the developer's shell; a test that needs a configured user sets it itself
    monkeypatch.delenv("EGERIA_USER", raising=False)
    monkeypatch.delenv("PYEGERIA_MULTI_USER", raising=False)
    monkeypatch.delenv("PYEGERIA_USER_FORMAT_SETS_DIR", raising=False)
    monkeypatch.delenv(esc.DRAFTS_ENV, raising=False)
    monkeypatch.delenv(esc.FOLDERS_ENV, raising=False)
    # Hermetic: a test that constructs a real client must not reach a platform (CI has none on :9443).
    from pyegeria.core._base_server_client import BaseServerClient
    monkeypatch.setattr(BaseServerClient, "check_connection", lambda self: "test")
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
    logger.enable("pyegeria")  # another test module may have left pyegeria's logger disabled
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
    # Since 6.2.28 repointed Asset-Graph and Data-Classes, every spec is runnable and every find
    # method a local spec names is allowed.
    assert not refused, refused
    assert all(r.runnable or r.kind == "format_only" for r in results.values())
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
    assert len(mfm._CENSUS_FIND_METHODS) == 47  # +find_elements_by_property_value (generic-search specs, 6.2.28)
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
    """The stage-2 seed writes today's built-in and generated specs into Egeria; none may be refused.
    Covers the two specs 6.2.28 repointed (Asset-Graph, Data-Classes)."""
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
    assert brf.base_report_specs["Asset-Graph"].action.function == "AssetCatalog.get_asset_graph_by_guid"
    assert brf.base_report_specs["Data-Classes"].action.function == "DataDesigner.find_data_value_specifications"
    for label in ("Asset-Graph", "Data-Classes"):
        assert resolve(brf.base_report_specs[label], label).runnable, label


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
    # No spec file is left behind; the consumer index (written by every folder sync) stays.
    assert sorted(p.name for p in tier["cache"].glob("*.json")) == [esc.CONSUMERS, esc.MANIFEST]


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
    assert esc.egeria_tier_info("E-Collections@v2")["shared"] is True
    assert brf.select_report_format(name, "DICT")["formats"]["types"] == ["DICT"]  # the fetched v1.1
    assert brf.select_report_format("E-Collections", "DICT")["formats"]["types"] == ["ALL"]  # cache untouched
    assert eg.full_fetches[-1] == E_GUID  # looked up by the guid the cache knows


def test_failed_fetch_raises_with_words_and_never_falls_back(tier):
    _sync_e_collections(tier)
    eg = FakeEgeria()  # Egeria no longer has it (or, before #9453, can't confirm it hasn't)
    with pytest.raises(esc.SpecFetchError, match="never falls back") as raised:
        esc.fetch_spec_for_call(eg, "E-Collections")
    assert "couldn't tell whether Egeria holds report spec 'E-Collections'" in str(raised.value)
    with pytest.raises(esc.SpecFetchError, match="built-in tier"):
        esc.fetch_spec_for_call(eg, "builtin:Collections")


async def test_async_fetch_through_a_find_request_helper(tier):
    from pyegeria.core._server_client import ServerClient

    class AsyncFake(FakeEgeria):
        async def _async_get_collection_by_guid(self, guid, output_format="JSON", **k):
            return self.get_collection_by_guid(guid)

        async def _async_get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON",
                                                 **k):
            return self.get_collections_by_name(name, metadata_element_type, start_from=k.get("start_from", 0))

    eg = AsyncFake()
    eg.put(spec_element())
    kwargs = {"refresh_spec": True, "page_size": 5}
    name = await ServerClient._async_refresh_report_spec(eg, "E-Collections", kwargs)
    assert name == "egeria:E-Collections@v1" and kwargs == {"page_size": 5}
    kwargs = {}
    assert await ServerClient._async_refresh_report_spec(eg, "Collections", kwargs) == "Collections"


# ── 7. Provenance in the run envelope ──

# exec_report_spec runs as its `user` (default: the configured user at import); the tests name the fake's user
AS_ERIN = dict(user="erinoverview", view_url="https://localhost:9443", view_server="qs-view-server")


def test_spec_source_is_beside_kind_and_never_inside_data(tier, monkeypatch):
    from pyegeria.view import format_set_executor as fse
    _sync_e_collections(tier)
    rows = [{"display_name": "x"}]
    monkeypatch.setattr(fse, "_exec_report_spec_impl", lambda name, **k: {"kind": "json", "data": list(rows)})
    out = fse.exec_report_spec("E-Collections", output_format="DICT", params={"search_string": "x"}, **AS_ERIN)
    assert out["data"] == rows
    assert out["spec_source"] == {"tier": "egeria", "label": "E-Collections", "version": "1.0", "guid": E_GUID,
                                  "synced_at": out["spec_source"]["synced_at"]}
    out = fse.exec_report_spec("Collections", output_format="DICT", params={}, **AS_ERIN)
    # RS-EGERIA-TIER stage 2: a builtin spec also names the seed file it was loaded from.
    assert out["spec_source"] == {"tier": "builtin", "label": "Collections", "version": None,
                                  "seed": "Collection Manager.json"}


def test_footer_on_report_md_html_only_for_egeria_specs(tier, monkeypatch):
    from pyegeria.view import format_set_executor as fse
    _sync_e_collections(tier)
    monkeypatch.setattr(fse, "_exec_report_spec_impl",
                        lambda name, **k: {"kind": "text", "mime": "text/markdown", "content": "# H\nbody\n"})
    md = fse.exec_report_spec("E-Collections", output_format="MD", **AS_ERIN)["content"]
    assert md.rstrip().splitlines()[-1].startswith("_E-Collections v1.0 (Egeria, synced ")
    assert brf.add_spec_footer(md, "E-Collections", "MD") == md  # idempotent
    assert fse.exec_report_spec("Collections", output_format="MD", **AS_ERIN)["content"] == "# H\nbody\n"
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


# ── The pinned-spec prune is three-way (Architect, after the by-name dispositions) ──

OTHER_GUID = "bbbbbbbb-0000-0000-0000-000000000000"


def _pinned_then_folder_sync(tier, read_other):
    """Pin Other-Spec (a --spec sync), then run a folder sync that doesn't hold it: its entry is re-checked by
    GUID with `read_other` standing in for Egeria's read of Other-Spec's element."""
    eg = FakeEgeria()
    eg.put(spec_element())
    eg.put(spec_element("Other-Spec", guid=OTHER_GUID, aliases=[]), folder=None)
    esc.sync_report_specs(eg, specs=["Other-Spec"])
    real = eg.get_collection_by_guid

    def by_guid(guid, *a, **k):
        return read_other() if guid == OTHER_GUID else real(guid, *a, **k)
    eg.get_collection_by_guid = by_guid
    report = esc.sync_report_specs(eg, folders=[FOLDER_QN])
    entries = json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]
    return report, entries


def _api_error(message_id, text):
    import httpx
    from pyegeria.core._exceptions import PyegeriaAPIException, PyegeriaNotFoundException
    info = {"exceptionErrorMessageId": message_id, "exceptionErrorMessage": text, "relatedHTTPCode": 404}
    response = httpx.Response(200, json=info, request=httpx.Request("POST", "https://localhost:9443/x"))
    cls = PyegeriaAPIException if message_id.startswith("OMAG-MULTI-TENANT") else PyegeriaNotFoundException
    return cls(response, {"caller method": "test"}, additional_info=info)


def test_pinned_found_is_kept(tier):
    report, entries = _pinned_then_folder_sync(tier, lambda: spec_element("Other-Spec", guid=OTHER_GUID, aliases=[]))
    assert "Other-Spec" in entries and "Other-Spec" not in report.pruned


@pytest.mark.parametrize("read_other", [
    lambda: "No elements found",
    lambda: (_ for _ in ()).throw(_api_error("OMAG-COMMON-404-001", "The element is not found")),
], ids=["no-elements", "not-found-exception"])
def test_pinned_gone_is_pruned_as_no_longer_existing(tier, read_other):
    report, entries = _pinned_then_folder_sync(tier, read_other)
    assert "Other-Spec" not in entries and "Other-Spec" in report.pruned
    assert any(n == f"Other-Spec: pruned, its element {OTHER_GUID} no longer exists" for n in report.notes)


@pytest.mark.parametrize("error, cls", [
    (RuntimeError("timeout"), "RuntimeError"),
    (_api_error("OMAG-MULTI-TENANT-404-001", "The OMAG Server qs-view-server is not available to service a "
                "request from user erinoverview"), "PyegeriaAPIException"),
], ids=["error", "server-not-available"])
def test_pinned_unknown_is_kept_with_words(tier, error, cls):
    def boom():
        raise error
    report, entries = _pinned_then_folder_sync(tier, boom)
    assert "Other-Spec" in entries and "Other-Spec" not in report.pruned   # a fault never drops a pinned spec
    assert any(n == f"Other-Spec: kept; couldn't confirm whether its element {OTHER_GUID} still exists ({cls})"
               for n in report.notes)


def test_server_not_available_is_never_element_not_found():
    from pyegeria.view import dashboard_resolver as dr
    from pyegeria.view.egeria_folders import is_gone_error
    down = _api_error("OMAG-MULTI-TENANT-404-001", "The OMAG Server qs-view-server is not available")
    assert dr.is_server_not_available_error(down) and not dr._is_not_found_error(down) and not is_gone_error(down)
    gone = _api_error("OMAG-COMMON-404-001", "The element is not found")
    assert dr._is_not_found_error(gone) and is_gone_error(gone)


# ── A private manifest is bound to its sync identity (ruling item 3) ──

def _identity(user):
    return esc.credential_identity(user, "https://localhost:9443", "qs-view-server")


def test_a_private_cache_loads_for_its_own_identity_only(tier):
    _sync_e_collections(tier)   # FakeEgeria syncs as erinoverview, privately
    manifest = json.loads((tier["cache"] / esc.MANIFEST).read_text())
    assert manifest["shared"] is False and manifest["bound_identity"] == _identity("erinoverview")
    with esc.spec_identity(_identity("erinoverview")):
        esc._invalidate_tier()
        assert "E-Collections" in esc.egeria_tier()
    with esc.spec_identity(_identity("peterprofile")):   # a different identity: refused, logged once
        assert "E-Collections" not in esc.egeria_tier()
        assert "E-Collections" not in esc.egeria_tier()
    assert sum(1 for k in esc._REFUSED_LOGGED if k[2] == _identity("peterprofile")) == 1


def test_a_shared_cache_loads_for_anyone(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN], shared=True)
    for user in ("erinoverview", "peterprofile"):
        with esc.spec_identity(_identity(user)):
            assert "E-Collections" in esc.egeria_tier()


def test_a_private_cache_with_no_binding_loads_for_no_one(tier):
    _sync_e_collections(tier)
    path = tier["cache"] / esc.MANIFEST
    manifest = json.loads(path.read_text())
    manifest.pop("bound_identity")   # a cache synced before private caches were bound
    path.write_text(json.dumps(manifest))
    with esc.spec_identity(_identity("erinoverview")):
        esc._invalidate_tier()
        assert "E-Collections" not in esc.egeria_tier()


def test_exec_report_spec_reads_the_tier_as_its_caller(tier, monkeypatch):
    from pyegeria.view import format_set_executor as fse
    seen = []
    monkeypatch.setattr(fse, "_exec_report_spec_impl", lambda *a, **k: seen.append(esc.current_spec_identity()) or {})
    monkeypatch.setattr(fse, "_with_spec_source", lambda result, *a: result)
    fse.exec_report_spec("E-Collections", user="peterprofile", view_url="https://localhost:9443",
                         view_server="qs-view-server")
    assert seen == [_identity("peterprofile")]


def test_identity_is_the_egeria_user_never_the_os_user():
    assert esc.credential_identity("erinoverview", "https://localhost:9443", "qs-view-server") == \
        "erinoverview@localhost_9443/qs-view-server"
    assert esc.credential_identity("", "https://x", "s") is None and esc.credential_identity("?") is None


# ── A fetched spec is served only to the identity that fetched it (ruling item 4) ──

def _as(user):
    return esc.credential_identity(user, "https://localhost:9443", "qs-view-server")


def test_a_fetched_spec_is_served_only_to_its_fetcher(tier):
    eg = FakeEgeria()   # fetches as erinoverview
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN], shared=True)
    eg.put(spec_element(version=2, microflow=mfm.format_set_to_microflow(builtin()).to_json(),
                        version_identifier="1.1"))
    name = esc.fetch_spec_for_call(eg, "E-Collections")
    internal = name.split(":", 1)[1]
    with esc.spec_identity(_as("erinoverview")):
        assert esc.fetched_spec(internal) is not None and esc.fetched_spec_source(name)["header_version"] == 2
        assert esc.fetched_refusal(name) is None
        assert brf.select_report_format(name, "DICT")["formats"]["types"] == ["DICT"]
    with esc.spec_identity(_as("peterprofile")):   # another identity: no copy, no fallback to erin's
        assert esc.fetched_spec(internal) is None and esc.fetched_spec_source(name) is None
        assert esc.egeria_tier_info(internal) is None
        assert esc.fetched_refusal(name) == "Report spec 'E-Collections' v2: not fetched for you; fetch it as yourself"
        assert brf.select_report_format(name, "DICT") is None
    assert esc.fetched_spec(internal, identity=_as("erinoverview")) is not None   # an explicit identity


def test_each_identity_gets_its_own_fetched_copy(tier):
    for user in ("erinoverview", "peterprofile"):
        eg = FakeEgeria()
        eg.user_id = user
        eg.put(spec_element())
        esc.fetch_spec_for_call(eg, "E-Collections")
    assert {k[0] for k in esc._FETCHED} == {_as("erinoverview"), _as("peterprofile")}


def test_a_name_never_fetched_has_no_refusal(tier):
    assert esc.fetched_refusal("egeria:Nobody@v1") is None


def test_no_identity_gets_no_refusal_words_and_none_are_logged(tier):
    """PY-11: fetched_refusal has the same None guard as _fetched_hit. Someone fetched it, the reader is no one:
    nothing is served, and there is no one to tell "fetch it as yourself" to, so no words and no log entry."""
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN], shared=True)
    eg.put(spec_element(version=2, microflow=mfm.format_set_to_microflow(builtin()).to_json(),
                        version_identifier="1.1"))
    name = esc.fetch_spec_for_call(eg, "E-Collections")
    internal = name.split(":", 1)[1]
    esc._REFUSAL_LOGGED.clear()
    with esc.spec_identity(None):                    # explicitly no one
        assert esc.current_spec_identity() is None
        assert esc.fetched_refusal(name) is None
        assert esc.fetched_spec(internal) is None
    assert esc._REFUSAL_LOGGED == set()              # no (None, name) key
    with esc.spec_identity(_as("peterprofile")):     # a real other identity still gets the words, once logged
        assert esc.fetched_refusal(name) == "Report spec 'E-Collections' v2: not fetched for you; fetch it as yourself"
        assert esc.fetched_spec(internal) is None
    assert esc._REFUSAL_LOGGED == {(_as("peterprofile"), internal)}


def test_same_identity_readers_share_one_tier_entry_and_other_identities_do_not(tier):
    """PY-11 (documented): the tier entry's specs are handed to every reader with that identity, uncopied."""
    with esc.spec_identity(_as("erinoverview")):
        first, second = esc.egeria_tier(), esc.egeria_tier()
    with esc.spec_identity(_as("peterprofile")):
        other = esc.egeria_tier()
    assert first is second
    assert other is not first
    assert "read-only" in (esc._TierEntry.__doc__ or "") and "read-only" in (esc.egeria_tier.__doc__ or "")


# ── Fetch-on-call never writes a zoned (or visibility-unknown) spec to any disk manifest (ruling item 2) ──

ZONED_GUID = "cccccccc-0000-0000-0000-000000000000"


def _zoned(label, zone_membership):
    el = spec_element(label, guid=ZONED_GUID, aliases=[])
    el["elementHeader"]["zoneMembership"] = zone_membership
    return el


@pytest.mark.parametrize("shared", [False, True], ids=["private", "shared"])
@pytest.mark.parametrize("zone_membership, visibility", [
    ({"classificationProperties": {"zoneMembership": ["finance"]}}, "zoned"),
    ({"classificationProperties": {"zoneMembership": {"not": "a list"}}}, "unknown"),
    ("garbled", "unknown"),
], ids=["zoned", "unreadable-zones", "unreadable-classification"])
def test_a_zoned_or_unknown_fetch_is_never_written_to_disk(tier, shared, zone_membership, visibility):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN], shared=shared)
    manifest_before = (tier["cache"] / esc.MANIFEST).read_text()
    files_before = sorted(p.name for p in tier["cache"].iterdir())
    eg.put(_zoned("Fin-Spec", zone_membership), folder=None)
    name = esc.fetch_spec_for_call(eg, "Fin-Spec")
    assert (tier["cache"] / esc.MANIFEST).read_text() == manifest_before   # no manifest entry
    assert sorted(p.name for p in tier["cache"].iterdir()) == files_before  # no spec file either
    assert esc.egeria_tier_info("Fin-Spec@v1")["visibility"] == visibility   # this process only
    assert brf.select_report_format(name, "DICT") is not None


def test_a_public_fetch_still_writes_through_to_a_private_cache(tier):
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    open_el = spec_element("Open-Spec", guid=ZONED_GUID, aliases=[])
    open_el["elementHeader"]["zoneMembership"] = {"classificationProperties": {"zoneMembership": []}}  # no zones: open
    eg.put(open_el, folder=None)
    esc.fetch_spec_for_call(eg, "Open-Spec")
    entries = json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]
    assert entries["Open-Spec"]["pinned"] is True
    assert esc.egeria_tier_info("Open-Spec@v1")["visibility"] == "public"


def test_zone_state():
    assert esc._zone_state({}) == ("unknown", [])
    assert esc._zone_state(spec_element()) == ("public", [])
    assert esc._zone_state(_zoned("X", {"classificationProperties": {"zoneMembership": "hr"}})) == ("zoned", ["hr"])


# ── The default identity: the process's own client, never the shell's EGERIA_USER (Coordinator 2026-11-14) ──

@pytest.mark.parametrize("egeria_user", [None, "erinoverview", "someoneelse"])
def test_a_single_user_process_reads_its_own_private_cache_whatever_egeria_user_says(tier, monkeypatch,
                                                                                      egeria_user):
    """A CLI that syncs as its client's user then lists specs (no spec_identity) loads its own private cache,
    with EGERIA_USER unset, matching, or naming someone else: the identity is the client's credential."""
    if egeria_user is None:
        monkeypatch.delenv("EGERIA_USER", raising=False)
    else:
        monkeypatch.setenv("EGERIA_USER", egeria_user)
    eg = FakeEgeria()
    eg.user_id = "peterprofile"
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    esc._invalidate_tier()
    assert esc.current_spec_identity() == _identity("peterprofile")
    assert brf.report_spec_source("E-Collections")["tier"] == "egeria"


def test_a_real_client_is_this_process_identity(tier, monkeypatch):
    """Constructing a view-server client records its credentials; the default identity is that client's,
    not the configured user's."""
    from pyegeria.core._client_identities import note_credentials, seen_credentials
    from pyegeria.omvs.collection_manager import CollectionManager
    monkeypatch.setenv("EGERIA_USER", "someoneelse")
    CollectionManager("qs-view-server", "https://localhost:9443", user_id="peterprofile", user_pwd="secret")
    assert seen_credentials() == [("peterprofile", "https://localhost:9443", "qs-view-server")]
    assert esc.current_spec_identity() == _identity("peterprofile")
    note_credentials("peterprofile", "https://localhost:9443", "qs-view-server")   # the same one again: still one
    assert esc.current_spec_identity() == _identity("peterprofile")


def test_a_multi_user_process_loads_no_private_cache_outside_a_request(tier, monkeypatch):
    """Two identities in one process (a Portal, EA): a read outside spec_identity is for no one, so neither
    user's private cache loads; each still loads inside its own spec_identity."""
    monkeypatch.setenv("EGERIA_USER", "erinoverview")
    _sync_e_collections(tier)                       # bound to erinoverview
    from pyegeria.core._client_identities import note_credentials
    note_credentials("peterprofile", "https://localhost:9443", "qs-view-server")
    esc._invalidate_tier()
    assert esc.current_spec_identity() is None
    assert brf.report_spec_source("E-Collections") is None
    with esc.spec_identity(_identity("erinoverview")):
        assert brf.report_spec_source("E-Collections")["tier"] == "egeria"
    with esc.spec_identity(_identity("peterprofile")):
        assert brf.report_spec_source("E-Collections") is None


def test_with_no_client_the_configured_user_is_the_identity(tier, monkeypatch):
    monkeypatch.setenv("EGERIA_USER", "someoneelse")
    assert esc.current_spec_identity().startswith("someoneelse@")
    monkeypatch.delenv("EGERIA_USER", raising=False)
    from pyegeria.core.config import settings
    monkeypatch.setattr(settings.User_Profile, "user_name", "configured")
    assert esc.current_spec_identity().startswith("configured@")


def test_client_credential_identity_uses_server_name_when_there_is_no_view_server():
    class Omvs:
        user_id, platform_url, server_name = "peterprofile", "https://localhost:9443", "qs-view-server"
    assert esc.client_credential_identity(Omvs()) == _identity("peterprofile")


# ── T2: a path with a client in hand reads the tier as that client; T3: one "configured user" ──

class _Client:
    """A stand-in client: only the credential attributes the tier binding reads."""

    def __init__(self, user):
        self.user_id, self.platform_url, self.view_server = user, "https://localhost:9443", "qs-view-server"


def _in_method_md(client):
    from pyegeria.core._server_client import ServerClient
    element = {"elementHeader": {"guid": "g1", "type": {"typeName": "Collection"},
                                 "origin": {"homeMetadataCollectionId": "m", "homeMetadataCollectionName": "m"},
                                 "versions": {"createdBy": "u", "createTime": "2026-11-08T00:00:00Z"}},
               "properties": {"displayName": "Coll A", "qualifiedName": "Collection::A"}}
    return ServerClient._generate_formatted_output(client, [element], query_string="A", entity_type="Collection",
                                                   output_format="MD", report_spec="E-Collections")


@pytest.mark.parametrize("egeria_user", [None, "erinoverview", "someoneelse"])
def test_the_in_method_path_reads_the_tier_as_its_client(tier, monkeypatch, egeria_user):
    """generate_formatted_output binds to the client it runs on: its private cache loads for it and for no
    other client, whatever EGERIA_USER says and even in a multi-user process (no fallback identity)."""
    if egeria_user:
        monkeypatch.setenv("EGERIA_USER", egeria_user)
    _sync_e_collections(tier)                                   # bound to erinoverview
    from pyegeria.core._client_identities import note_credentials
    note_credentials("peterprofile", "https://localhost:9443", "qs-view-server")   # now a multi-user process
    esc._invalidate_tier()
    assert esc.current_spec_identity() is None
    assert _in_method_md(_Client("erinoverview")).rstrip().splitlines()[-1].startswith("_E-Collections v1.0")
    assert "_E-Collections v1.0" not in _in_method_md(_Client("peterprofile"))


@pytest.mark.parametrize("egeria_user", [None, "erinoverview", "someoneelse"])
def test_a_fetch_writes_through_and_reads_as_its_client(tier, monkeypatch, egeria_user):
    if egeria_user:
        monkeypatch.setenv("EGERIA_USER", egeria_user)
    eg = FakeEgeria()
    eg.put(spec_element())
    esc.sync_report_specs(eg, folders=[FOLDER_QN])
    open_el = spec_element("Open-Spec", guid=ZONED_GUID, aliases=[])
    open_el["elementHeader"]["zoneMembership"] = {"classificationProperties": {"zoneMembership": []}}
    eg.put(open_el, folder=None)
    from pyegeria.core._client_identities import note_credentials
    note_credentials("peterprofile", "https://localhost:9443", "qs-view-server")
    internal = esc.fetch_spec_for_call(eg, "Open-Spec")
    assert json.loads((tier["cache"] / esc.MANIFEST).read_text())["entries"]["Open-Spec"]["pinned"] is True
    assert internal == "egeria:Open-Spec@v1"
    with esc.as_client(eg):
        assert esc.egeria_tier_info("Open-Spec@v1")["visibility"] == "public"
        assert esc.fetched_spec("Open-Spec@v1") is not None
    with esc.as_client(_Client("peterprofile")):
        assert esc.egeria_tier_info("Open-Spec@v1") is None


def test_as_client_with_no_identity_leaves_the_current_one():
    with esc.spec_identity("x@h_1/v"):
        with esc.as_client(object()):
            assert esc.current_spec_identity() == "x@h_1/v"
        with esc.as_client(_Client("erinoverview")):
            assert esc.current_spec_identity() == _identity("erinoverview")


def test_one_configured_user_for_client_construction_and_the_tier(tier, monkeypatch):
    """T3: a CLI with no configuration builds its client as resolve_egeria_credentials' user and the tier's
    client-less identity is that same user, so its own private cache loads."""
    from pyegeria.core import config
    monkeypatch.delenv("EGERIA_USER", raising=False)
    monkeypatch.setattr(config.settings.User_Profile, "user_name", None)
    user, _pwd = config.resolve_egeria_credentials()
    assert user == config.configured_user_id() == "erinoverview"
    assert esc.current_spec_identity() == esc.credential_identity(user)
    monkeypatch.setenv("EGERIA_USER", "someoneelse")
    assert config.resolve_egeria_credentials()[0] == config.configured_user_id() == "someoneelse"
    assert esc.current_spec_identity() == esc.credential_identity("someoneelse")


# ── R-A: a multi-user process declares itself; no fallback identity there (Architect, delta 3984046d) ──

def _swapped_client(service_user="erinoverview", signed_in="peterprofile"):
    """The Portal's shape: built as the service user, then user_id swapped to the token's subject."""
    from pyegeria.omvs.collection_manager import CollectionManager
    client = CollectionManager("qs-view-server", "https://localhost:9443", user_id=service_user, user_pwd="secret")
    client.user_id = signed_in
    return client


@pytest.mark.parametrize("how", ["call", "env"])
def test_a_declared_process_built_as_the_service_user_then_swapped_has_no_fallback(tier, monkeypatch, how):
    from pyegeria.core._client_identities import declare_multi_user
    if how == "call":
        declare_multi_user()
    else:
        monkeypatch.setenv("PYEGERIA_MULTI_USER", "1")
    client = _swapped_client()
    assert esc.client_credential_identity(client) == _identity("peterprofile")
    assert esc.current_spec_identity() is None              # never the service user erinoverview
    with esc.as_client(client):
        assert esc.current_spec_identity() == _identity("peterprofile")
    assert esc.current_spec_identity() is None


def test_undeclared_the_swap_is_caught_once_the_client_is_used(tier):
    """Backstop only: undeclared, the service user is the one identity until the swapped client is used."""
    client = _swapped_client()
    assert esc.current_spec_identity() == _identity("erinoverview")   # why a server must declare itself
    with esc.as_client(client):
        pass
    assert esc.current_spec_identity() is None              # two identities seen now


def test_an_undeclared_cli_with_userid_x_reads_as_x(tier, monkeypatch):
    from pyegeria.omvs.collection_manager import CollectionManager
    monkeypatch.setenv("EGERIA_USER", "someoneelse")
    CollectionManager("qs-view-server", "https://localhost:9443", user_id="peterprofile", user_pwd="secret")
    assert esc.current_spec_identity() == _identity("peterprofile")


def _open_spec_for(user):
    eg = FakeEgeria()
    eg.user_id = user
    el = spec_element("Open-Spec", guid=ZONED_GUID, aliases=[], version_identifier=f"1.0-{user}")
    el["elementHeader"]["zoneMembership"] = {"classificationProperties": {"zoneMembership": []}}
    eg.put(el, folder=None)
    return eg


def _footer(client, spec):
    from pyegeria.core._server_client import ServerClient
    element = {"elementHeader": {"guid": "g1", "type": {"typeName": "Collection"},
                                 "origin": {"homeMetadataCollectionId": "m", "homeMetadataCollectionName": "m"},
                                 "versions": {"createdBy": "u", "createTime": "2026-11-08T00:00:00Z"}},
               "properties": {"displayName": "Coll A", "qualifiedName": "Collection::A"}}
    try:
        out = ServerClient._generate_formatted_output(client, [element], query_string="A", entity_type="Collection",
                                                      output_format="MD", report_spec=spec)
    except Exception as exc:  # noqa: BLE001 -- a spec not served to this caller doesn't resolve
        return f"refused: {exc}"
    last = out.rstrip().splitlines()[-1] if isinstance(out, str) and out.strip() else ""
    return last if last.startswith("_Open-Spec") else None


@pytest.mark.parametrize("declared", [True, False])
def test_the_footer_serves_each_user_only_their_own_fetched_copy(tier, declared):
    from pyegeria.core._client_identities import declare_multi_user
    if declared:
        declare_multi_user()
    erin, peter = _open_spec_for("erinoverview"), _open_spec_for("peterprofile")
    assert esc.fetch_spec_for_call(erin, "Open-Spec") == "egeria:Open-Spec@v1"
    assert esc.fetch_spec_for_call(peter, "Open-Spec") == "egeria:Open-Spec@v1"
    assert _footer(_Client("erinoverview"), "egeria:Open-Spec@v1").startswith("_Open-Spec v1.0-erinoverview ")
    assert _footer(_Client("peterprofile"), "egeria:Open-Spec@v1").startswith("_Open-Spec v1.0-peterprofile ")
    assert not (_footer(_Client("someoneelse"), "egeria:Open-Spec@v1") or "").startswith("_Open-Spec")
    # outside any client: two identities fetched (and, when declared, a multi-user process): no one's copy
    assert esc.current_spec_identity() is None
    assert esc.fetched_spec("Open-Spec@v1") is None


def test_the_mcp_server_declares_itself_multi_user(monkeypatch):
    import pyegeria.core.mcp_server as ms
    from pyegeria.core._client_identities import is_multi_user
    monkeypatch.setattr(ms, "_startup_client", lambda settings: None)

    class Stop(Exception):
        pass

    def stop(*a, **k):
        raise Stop
    monkeypatch.setattr(ms, "MCPServer", stop)
    with pytest.raises(Stop):
        ms.main()
    assert is_multi_user()

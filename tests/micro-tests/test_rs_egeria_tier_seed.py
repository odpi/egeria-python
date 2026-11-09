"""RS-EGERIA-TIER stage 2: the seed (pyegeria's shipped report specs as packaged JSON).

Covers the brief's gates that run without Egeria: the seed is current (`seed check`), every seed spec equals the
constant-defined one (envelope, action, get_additional_props, every format and column), the label set and order
are unchanged, the census in the manifest is the resolver's, every seed micro-flow passes the allowlist, the
bootstrap core is in the seed, one bad file never empties the tier, and the microflow/1 additions (format-only
specs with no stages, the `additional_props` hook, `same_as` formatters). No live Egeria.
"""
from __future__ import annotations

import json
import shutil
import warnings
from pathlib import Path

import pytest

import pyegeria.view.base_report_formats as brf
from pyegeria.view import microflow as mfm
from pyegeria.view import seed
from pyegeria.view._output_format_models import ActionParameter, Column, Format, FormatSet

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def source():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return seed.source_specs()


def _seed_entries(directory: Path = seed.SEED_DIR):
    for path in sorted(directory.glob("*.json")):
        if path.name == seed.MANIFEST:
            continue
        for entry in json.loads(path.read_text(encoding="utf-8"))["specs"]:
            yield path.name, entry


# ── The seed is current and complete ──

def test_seed_is_not_stale(source):
    """`python -m pyegeria.view.seed check`: run `... seed build` after changing a built-in spec."""
    assert seed.check_seed(specs=source) == []


def test_every_seed_spec_equals_the_constant_defined_one(source):
    loaded = seed.seed_report_specs()
    assert seed.seed_skipped() == []
    assert list(loaded.keys()) == list(source.keys())
    differ = [label for label, fs in source.items() if loaded[label].model_dump() != fs.model_dump()]
    assert differ == []


def test_registry_builtin_tier_is_the_seed(source):
    registry = brf.get_report_registry()
    for label in source.keys():
        assert brf._REGISTRY_TIERS[label] == "builtin", label
        assert registry[label] is seed.seed_report_specs()[label]


def test_analytic_demos_and_question_specs_are_builtin_now():
    """Owner decision S2-2: the 23 analytic demos and the 3 question specs ship in the seed."""
    from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs
    brf.get_report_registry()
    for label in list(get_analytic_demo_specs()) + ["Questions", "Report-Types", "Question-Specs"]:
        assert brf._REGISTRY_TIERS[label] == "builtin", label
        assert label not in brf._CONFIG_REPORT_FORMATS
        assert label not in brf._RUNTIME_REPORT_FORMATS


def test_spec_source_names_the_seed_file():
    src = brf.report_spec_source("Search-Keywords")
    assert src["tier"] == "builtin"
    assert src["seed"] and (seed.SEED_DIR / src["seed"]).exists()
    assert "Search-Keywords" in [e["label"] for f, e in _seed_entries() if f == src["seed"]]


def test_manifest_census_is_the_resolvers(source):
    manifest = json.loads((seed.SEED_DIR / seed.MANIFEST).read_text(encoding="utf-8"))
    census = manifest["census"]
    assert census == seed._census(seed.seed_report_specs())
    assert census["total"] == len(source) == census["runnable"] + census["unrunnable"] + census["format_only"]
    assert manifest["order"] == list(source.keys())
    assert sum(f["count"] for f in manifest["files"]) == len(source)


def test_one_file_per_family_and_the_family_is_inside():
    for name, entry in _seed_entries():
        assert seed.family_file_name(entry["envelope"]["family"]) == name


def test_every_seed_microflow_passes_the_allowlist():
    refused = {}
    for _name, entry in _seed_entries():
        mf, stored, _ = mfm.parse_microflow(entry["microflow"])
        assert stored == 1
        try:
            mfm.check_allowlist(mf)
        except mfm.AllowlistRefusal as exc:
            refused[entry["label"]] = str(exc)
    assert refused == {}


def test_every_seed_microflow_matches_the_json_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((Path(mfm.__file__).parent / "schemas" / "microflow-1.json").read_text())
    validator = jsonschema.Draft202012Validator(schema)
    bad = {e["label"]: next(iter(validator.iter_errors(e["microflow"]))).message
           for _n, e in _seed_entries() if not validator.is_valid(e["microflow"])}
    assert bad == {}


def test_bootstrap_core_is_in_the_seed():
    labels = set(seed.seed_report_specs().keys())
    assert sorted(seed.BOOTSTRAP_CORE - labels) == []
    assert any(seed.is_bootstrap_core(label) and label.endswith("-DrE-Basic") for label in labels)


def test_scratch_elements_are_not_in_the_seed():
    """E-Collections and the scratch folder stay EGERIA-tier only (brief gate 8)."""
    labels = set(seed.seed_report_specs().keys())
    assert not {label for label in labels if label.startswith("E-Collections")}


def test_hook_specs_keep_get_additional_props(source):
    hooks = {label: fs.get_additional_props.function for label, fs in source.items() if fs.get_additional_props}
    assert set(hooks.values()) == set(mfm.ADDITIONAL_PROPS_HOOKS)
    loaded = seed.seed_report_specs()
    for label, func in hooks.items():
        assert loaded[label].get_additional_props.function == func


# ── One bad file never empties the tier ──

def _copy_seed(tmp_path: Path) -> Path:
    d = tmp_path / "seed"
    shutil.copytree(seed.SEED_DIR, d, ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    return d


def test_a_bad_seed_file_is_skipped_with_words_and_the_rest_load(tmp_path):
    d = _copy_seed(tmp_path)
    (d / "Glossary Manager.json").write_text("{not json", encoding="utf-8")
    data = json.loads((d / "Projects.json").read_text())
    data["specs"][0]["microflow"]["stages"][0]["function"] = None
    data["specs"][0]["microflow"]["params"] = {"x": {"bogus": 1}}
    (d / "Projects.json").write_text(json.dumps(data), encoding="utf-8")
    specs, where, skipped = seed.load_seed_dir(d)
    names = dict(skipped)
    assert "not readable JSON" in names["Glossary Manager.json"]
    assert "entry 0" in names["Projects.json"]
    full = seed.seed_report_specs()
    lost = {label for label, f in seed._SEED_FILES.items() if f in ("Glossary Manager.json", "Projects.json")}
    assert set(specs.keys()) == set(full.keys()) - lost
    assert len(specs) > 400


def test_without_a_manifest_every_file_still_loads(tmp_path):
    d = _copy_seed(tmp_path)
    (d / seed.MANIFEST).unlink()
    specs, _where, skipped = seed.load_seed_dir(d)
    assert set(specs.keys()) == set(seed.seed_report_specs().keys())
    assert [s[0] for s in skipped] == [seed.MANIFEST]


def test_a_label_in_two_files_keeps_the_first(tmp_path):
    d = _copy_seed(tmp_path)
    dup = json.loads((d / "Projects.json").read_text())
    other = json.loads((d / "Glossary.json").read_text())
    other["specs"].append(dup["specs"][0])
    (d / "Glossary.json").write_text(json.dumps(other), encoding="utf-8")
    specs, where, skipped = seed.load_seed_dir(d)
    assert where[dup["specs"][0]["label"]] in ("Glossary.json", "Projects.json")
    assert len(skipped) == 1 and "already loaded" in skipped[0][1]


# ── microflow/1 additions ──

def _fs(**kw):
    base = dict(heading="H", description="D", family="F",
                formats=[Format(types=["DICT", "TABLE"], attributes=[Column(name="Name", key="display_name")]),
                         Format(types=["REPORT"], attributes=[Column(name="GUID", key="guid", format=True)])])
    base.update(kw)
    return FormatSet(**base)


def _round_trip(fs):
    mf, _, _ = mfm.parse_microflow(mfm.format_set_to_microflow(fs).to_json())
    return mf, mfm.microflow_to_format_set(mf, label="L", heading=fs.heading, description=fs.description,
                                           target_type=fs.target_type, aliases=fs.aliases, family=fs.family,
                                           annotations=fs.annotations, question_spec=fs.question_spec)


def test_format_only_spec_round_trips_with_empty_stages():
    fs = _fs()
    mf, back = _round_trip(fs)
    assert mf.stages == [] and mf.params == {}
    assert back.model_dump() == fs.model_dump()


@pytest.mark.parametrize("obj,words", [
    ({"format": "microflow/1", "stages": [], "params": {"a": {}}, "formatters": {"ALL": {"columns": ["guid"]}}},
     "declares no params"),
    ({"format": "microflow/1", "stages": []}, "at least one stage"),
])
def test_empty_stages_need_formatters_and_no_params(obj, words):
    with pytest.raises(mfm.MicroflowError, match=words):
        mfm.parse_microflow(json.dumps(obj))


def test_same_as_keeps_a_format_with_several_types_as_one():
    fs = _fs(action=ActionParameter(function="CollectionManager.find_collections", required_params=["search_string"]))
    mf, back = _round_trip(fs)
    assert mf.formatters["TABLE"].same_as == "DICT"
    assert back.model_dump() == fs.model_dump()


@pytest.mark.parametrize("formatters,words", [
    ({"TABLE": {"same_as": "DICT"}, "DICT": {"columns": ["guid"]}}, "not an output format written before"),
    ({"DICT": {"columns": ["guid"]}, "TABLE": {"same_as": "DICT", "columns": ["guid"]}}, "no 'columns'"),
    ({"DICT": {"columns": ["guid"]}, "TABLE": {"same_as": "DICT"}, "MD": {"same_as": "TABLE"}}, "itself a same_as"),
])
def test_same_as_is_checked(formatters, words):
    obj = {"format": "microflow/1", "stages": [], "formatters": formatters}
    with pytest.raises(mfm.MicroflowError, match=words):
        mfm.parse_microflow(json.dumps(obj))


def test_one_output_type_in_two_formats_is_refused_on_write():
    fs = _fs(formats=[Format(types=["DICT"], attributes=[Column(name="A", key="a")]),
                      Format(types=["DICT"], attributes=[Column(name="B", key="b")])])
    with pytest.raises(mfm.MicroflowError, match="listed by two formats"):
        mfm.format_set_to_microflow(fs)


def test_additional_props_hook_round_trips():
    fs = _fs(action=ActionParameter(function="CollectionManager.find_collections", required_params=["search_string"]),
             get_additional_props=ActionParameter(function="CollectionManager._extract_agreement_properties"))
    mf, back = _round_trip(fs)
    assert mf.stages[0].model_extra["additional_props"] == "CollectionManager._extract_agreement_properties"
    mfm.check_allowlist(mf)
    assert back.model_dump() == fs.model_dump()


def _with_hook(stage: dict):
    return mfm.MicroflowV1.model_validate({"format": "microflow/1", "params": {"search_string": {"required": True}},
                                          "stages": [stage], "formatters": {"ALL": {"columns": ["guid"]}}})


def test_an_unlisted_additional_props_hook_is_refused_with_words():
    mf = _with_hook({"stage": "producer/find", "function": "CollectionManager.find_collections",
                     "params": {"search_string": "$search_string"}, "additional_props": "os.system"})
    with pytest.raises(mfm.AllowlistRefusal, match="ADDITIONAL_PROPS_HOOKS"):
        mfm.check_allowlist(mf)
    with pytest.raises(mfm.MicroflowError, match="ADDITIONAL_PROPS_HOOKS"):
        mfm.microflow_to_format_set(mf, label="L")


def test_additional_props_belongs_on_the_find_stage_only():
    mf = _with_hook({"stage": "producer/analytic", "function": "count_elements_by_type",
                     "additional_props": "CollectionManager._extract_agreement_properties"})
    with pytest.raises(mfm.AllowlistRefusal, match="find stage"):
        mfm.check_allowlist(mf)


def test_a_hook_that_is_not_a_bare_listed_function_is_not_written():
    fs = _fs(action=ActionParameter(function="CollectionManager.find_collections"),
             get_additional_props=ActionParameter(function="CollectionManager._extract_agreement_properties",
                                                  spec_params={"x": 1}))
    with pytest.raises(mfm.MicroflowError, match="bare function"):
        mfm.format_set_to_microflow(fs)


def test_the_analytic_demo_entry_point_is_gone():
    from importlib.metadata import entry_points
    names = [ep.value for ep in entry_points(group=brf.REPORT_SPEC_ENTRY_POINT_GROUP)]
    assert "pyegeria.view.analytic_demo_specs:get_analytic_demo_specs" not in names

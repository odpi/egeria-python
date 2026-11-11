# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""SD-1: the DOCUMENT output type.

A DOCUMENT spec's exporter (an analytic function) returns `{text, notes?}`; the executor names the
file, runs the declared validator and returns the document with a `validation` block that is
always present. Validators are registered by name; the `json-schema` and `shacl` built-ins read
only local files and never fetch over the network. The run_report CLI writes the document."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import pyegeria.view.base_report_formats as brf
import pyegeria.view.overview_metrics as om
from commands.cat import run_report
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import ActionParameter, DocumentSpec, Format, FormatSet
from pyegeria.view.analytic_registry import (AnalyticFunctionSpec, clear_runtime_analytic_functions,
                                             register_analytic_functions)
from pyegeria.view.document_validators import (DocumentValidatorCollision, DocumentValidatorRefused,
                                               clear_runtime_document_validators, get_document_validators,
                                               json_schema_validator, make_shacl_validator,
                                               register_document_validators, run_document_validator,
                                               shacl_validator)
from pyegeria.view.spec_resolver import resolve

FIXTURES = Path(__file__).parent / "fixtures" / "documents"
SCHEMA = str(FIXTURES / "person.schema.json")
SHAPES = str(FIXTURES / "dataset.shapes.ttl")
MOD = "pyegeria.view.overview_metrics"


@pytest.fixture(autouse=True)
def _clean():
    yield
    clear_runtime_analytic_functions()
    clear_runtime_document_validators()
    brf.clear_runtime_report_specs()


def _doc(**kw):
    base = dict(standard="toy-1", media_type="application/json", file_name="{scope}-toy.json")
    base.update(kw)
    return base


def _exporter(monkeypatch, name="toy_export", returns=None):
    """Register a toy exporter (no Egeria client: it declares no inputs)."""
    calls = []

    def _export(**params):
        calls.append(params)
        if returns is not None:
            return returns
        return {"text": json.dumps({"name": params.get("scope"), "age": 3}), "notes": ["one note"]}

    monkeypatch.setattr(om, f"_sd1_{name}", _export, raising=False)
    register_analytic_functions({name: AnalyticFunctionSpec(name=name, function=f"{MOD}._sd1_{name}")})
    return calls


def _spec(label="SD1-Toy", exporter="toy_export", **doc):
    brf.register_report_specs({label: FormatSet(
        heading=label, description="toy document", target_type="Collection",
        action=ActionParameter(analytic_function=exporter),
        formats=[Format(types=["DOCUMENT"], document=_doc(**doc))])}, source="test")
    return label


def _run(label, output_format="DOCUMENT", **params):
    return fse.exec_report_spec(label, output_format=output_format, params=params or {"scope": "Sales"},
                                view_server="vs", view_url="https://x", user="u", user_pass="p")


# ── Model load: accepts and refuses ──

def test_document_format_loads():
    fs = FormatSet(heading="D", description="d", action={"analytic_function": "toy"},
                   formats=[{"types": ["DOCUMENT"], "document": _doc(validator="json-schema")}])
    fmt = fs.document_format()
    assert fmt.document.standard == "toy-1" and fmt.attributes == []
    assert fs.dict()["formats"][0]["document"]["file_name"] == "{scope}-toy.json"


def test_document_needs_analytic_function():
    with pytest.raises(ValidationError, match="no action.analytic_function"):
        FormatSet(heading="D", description="d", formats=[{"types": ["DOCUMENT"], "document": _doc()}])


def test_document_with_find_function_only_is_refused_with_a_sentence():
    with pytest.raises(ValidationError, match="a find returns elements, not a document"):
        FormatSet(heading="D", description="d", action={"function": "MetadataExpert.find_x"},
                  formats=[{"types": ["DOCUMENT"], "document": _doc()}])


def test_document_format_needs_its_block_and_stands_alone():
    with pytest.raises(ValidationError, match="needs a 'document' block"):
        Format(types=["DOCUMENT"])
    with pytest.raises(ValidationError, match="cannot share its row"):
        Format(types=["DOCUMENT", "DICT"], document=_doc())
    with pytest.raises(ValidationError, match="Only a DOCUMENT format carries"):
        Format(types=["DICT"], document=_doc())
    with pytest.raises(ValidationError, match="cannot also offer DICT"):
        FormatSet(heading="D", description="d", action={"analytic_function": "toy"},
                  formats=[{"types": ["DOCUMENT"], "document": _doc()}, {"types": ["DICT"], "attributes": []}])


@pytest.mark.parametrize("bad", ["../x", "a/b", "a\\b", "..", "", ".hidden", "{scope}/x.json"])
def test_hostile_file_name_template_is_refused(bad):
    with pytest.raises(ValidationError, match="file_name refused"):
        DocumentSpec(**_doc(file_name=bad))


def test_resolver_knows_document():
    spec = FormatSet(heading="D", description="d", action={"analytic_function": "toy"},
                     formats=[{"types": ["DOCUMENT"], "document": _doc()}])
    res = resolve(spec, "D", registry_names=set())
    assert not any("not one the executor renders" in w for w in res.words)


# ── File names filled from parameters ──

def test_file_name_values_cannot_become_paths():
    assert fse.fill_document_file_name("{scope}-dcat.jsonld", {"scope": "Folder::Sales/EU"}) == \
        "Folder_Sales_EU-dcat.jsonld"
    assert fse.fill_document_file_name("{scope}.json", {"scope": "../../etc/passwd"}) == "etc_passwd.json"


def test_file_name_missing_param_or_odd_field_is_refused():
    with pytest.raises(ValueError, match="needs parameter 'scope'"):
        fse.fill_document_file_name("{scope}.json", {})
    with pytest.raises(ValueError, match="only plain parameter names"):
        fse.fill_document_file_name("{scope.__class__}.json", {"scope": "x"})


# ── The executor: full shape under each validation state ──

def test_not_validated_when_no_validator_declared(monkeypatch):
    calls = _exporter(monkeypatch)
    out = _run(_spec())
    assert out["kind"] == "document"
    assert {k: out[k] for k in ("standard", "media_type", "file_name")} == {
        "standard": "toy-1", "media_type": "application/json", "file_name": "Sales-toy.json"}
    assert json.loads(out["text"]) == {"name": "Sales", "age": 3}
    assert out["notes"] == ["one note"]
    assert out["validation"] == {"state": "not_validated", "validator": None, "findings": [],
                                 "reason": "no validator is declared for this standard"}
    assert calls == [{"scope": "Sales"}]


def test_not_validated_when_validator_not_registered(monkeypatch):
    _exporter(monkeypatch)
    out = _run(_spec(validator="nope"))
    assert out["validation"]["state"] == "not_validated"
    assert out["validation"]["reason"] == "the validator nope is not registered"


def test_valid_with_json_schema(monkeypatch):
    _exporter(monkeypatch)
    out = _run(_spec(validator="json-schema", validator_options={"schema": SCHEMA}))
    assert out["validation"] == {"state": "valid", "validator": "json-schema", "findings": [], "reason": None}


def test_invalid_with_json_schema(monkeypatch):
    _exporter(monkeypatch, returns={"text": json.dumps({"name": "x", "age": -1})})
    out = _run(_spec(validator="json-schema", validator_options={"schema": SCHEMA}))
    assert out["validation"]["state"] == "invalid"
    assert out["validation"]["findings"] == ["/age: -1 is less than the minimum of 0"]
    assert out["notes"] == []


def test_validator_crash_is_not_validated_with_the_error(monkeypatch):
    _exporter(monkeypatch)

    def boom(text, media_type):
        raise RuntimeError("shapes file is corrupt")

    register_document_validators({"boom": boom})
    out = _run(_spec(validator="boom"))
    assert out["validation"]["state"] == "not_validated"
    assert out["validation"]["findings"] == []
    assert out["validation"]["reason"] == "the validator boom failed: RuntimeError: shapes file is corrupt"


def test_exporter_plain_string_and_bad_return(monkeypatch):
    _exporter(monkeypatch, returns="just text")
    out = _run(_spec())
    assert out["text"] == "just text" and out["notes"] == []
    clear_runtime_analytic_functions()
    _exporter(monkeypatch, returns=[1, 2])
    with pytest.raises(ValueError, match="not a document"):
        _run("SD1-Toy")


@pytest.mark.parametrize("fmt", ["DICT", "TABLE", "REPORT", "SERIES", "BAR"])
def test_other_formats_of_a_document_spec_are_refused(monkeypatch, fmt):
    _exporter(monkeypatch)
    label = _spec()
    with pytest.raises(ValueError, match="is a DOCUMENT spec.*Ask for output_format DOCUMENT"):
        _run(label, output_format=fmt)


def test_document_of_a_non_document_spec_is_refused():
    brf.register_report_specs({"SD1-Plain": FormatSet(
        heading="P", description="p", action=ActionParameter(analytic_function="toy_export"),
        formats=[Format(types=["ALL"], attributes=[])])}, source="test")
    with pytest.raises(ValueError, match="does not produce a document"):
        _run("SD1-Plain")


def test_hostile_param_never_reaches_disk(monkeypatch):
    _exporter(monkeypatch)
    out = _run(_spec(), scope="../../x")
    assert out["file_name"] == "x-toy.json"


# ── Validator registry ──

def test_registry_builtins_and_collision():
    assert {"json-schema", "shacl"} <= set(get_document_validators())
    register_document_validators({"mine": lambda t, m: (True, [])})
    with pytest.raises(DocumentValidatorCollision):
        register_document_validators({"mine": lambda t, m: (True, [])})
    with pytest.raises(DocumentValidatorCollision):
        register_document_validators({"shacl": lambda t, m: (True, [])})


def test_run_document_validator_bad_return_is_a_crash():
    register_document_validators({"odd": lambda t, m: "yes"})
    v = run_document_validator("x", "text/plain", "odd")
    assert v["state"] == "not_validated" and "the validator odd failed" in v["reason"]


# ── The built-ins on tiny inputs ──

def test_json_schema_validator_tiny_inputs():
    assert json_schema_validator('{"name": "a", "age": 1}', "application/json", schema=SCHEMA) == (True, [])
    ok, findings = json_schema_validator('{"age": "x"}', "application/json", schema=SCHEMA)
    assert not ok and findings == ["(document): 'name' is a required property",
                                   "/age: 'x' is not of type 'integer'"]
    assert json_schema_validator("name: a\nage: 2\n", "application/yaml", schema=SCHEMA) == (True, [])


def test_json_schema_validator_file_url_and_package_resource(tmp_path):
    assert json_schema_validator('{"name": "a", "age": 1}', "application/json",
                                 schema=Path(SCHEMA).as_uri())[0] is True
    with pytest.raises(FileNotFoundError):
        json_schema_validator("{}", "application/json", schema="package:pyegeria.view/no-such.json")


def test_validators_never_fetch_over_the_network():
    with pytest.raises(DocumentValidatorRefused, match="never fetches over the network"):
        json_schema_validator("{}", "application/json", schema="https://example.org/s.json")
    with pytest.raises(DocumentValidatorRefused, match="never fetches over the network"):
        shacl_validator("", "text/turtle", shapes="http://example.org/shapes.ttl")
    remote_ctx = json.dumps({"@context": "https://example.org/ctx.jsonld", "@id": "urn:x"})
    with pytest.raises(DocumentValidatorRefused, match="would fetch over the network"):
        shacl_validator(remote_ctx, "application/ld+json", shapes=SHAPES)
    v = run_document_validator(remote_ctx, "application/ld+json", "shacl", {"shapes": SHAPES})
    assert v["state"] == "not_validated" and "would fetch over the network" in v["reason"]


_TTL_HEAD = "@prefix dcat: <http://www.w3.org/ns/dcat#> . @prefix dct: <http://purl.org/dc/terms/> . "


def test_shacl_validator_tiny_inputs():
    good = _TTL_HEAD + '<urn:ds:1> a dcat:Dataset ; dct:title "One" .'
    bad = _TTL_HEAD + "<urn:ds:2> a dcat:Dataset ."
    assert shacl_validator(good, "text/turtle", shapes=SHAPES) == (True, [])
    ok, findings = shacl_validator(bad, "text/turtle", shapes=SHAPES)
    assert not ok and findings == ["Violation <urn:ds:2> dct:title: missing dct:title"]


def test_shacl_validator_reads_inline_json_ld():
    doc = {"@context": {"dcat": "http://www.w3.org/ns/dcat#", "dct": "http://purl.org/dc/terms/"},
           "@id": "urn:ds:3", "@type": "dcat:Dataset", "dct:title": "Three"}
    assert shacl_validator(json.dumps(doc), "application/ld+json", shapes=SHAPES) == (True, [])
    bound = make_shacl_validator(SHAPES)
    del doc["dct:title"]
    ok, findings = bound(json.dumps(doc), "application/ld+json")
    assert not ok and len(findings) == 1


def test_executor_with_shacl(monkeypatch):
    _exporter(monkeypatch, returns={"text": _TTL_HEAD + "<urn:ds:2> a dcat:Dataset ."})
    out = _run(_spec(media_type="text/turtle", file_name="{scope}.ttl", validator="shacl",
                     validator_options={"shapes": SHAPES}))
    assert out["validation"]["state"] == "invalid"
    assert out["validation"]["findings"] == ["Violation <urn:ds:2> dct:title: missing dct:title"]


# ── The CLI ──

def _doc_result(**kw):
    out = {"kind": "document", "standard": "toy-1", "media_type": "application/json",
           "file_name": "Sales-toy.json", "text": "{}",
           "validation": {"state": "valid", "validator": "json-schema", "findings": [], "reason": None},
           "notes": []}
    out.update(kw)
    return out


def test_write_document_with_and_without_force(tmp_path):
    path = run_report.write_document(_doc_result(), str(tmp_path))
    assert Path(path) == tmp_path / "Sales-toy.json" and Path(path).read_text() == "{}"
    with pytest.raises(FileExistsError, match="--force"):
        run_report.write_document(_doc_result(text="new"), str(tmp_path))
    assert Path(path).read_text() == "{}"
    run_report.write_document(_doc_result(text="new"), str(tmp_path), force=True)
    assert Path(path).read_text() == "new"


@pytest.mark.parametrize("bad", ["../x", "a/b"])
def test_write_document_refuses_hostile_file_name(tmp_path, bad):
    with pytest.raises(ValueError, match="file_name refused"):
        run_report.write_document(_doc_result(file_name=bad), str(tmp_path / "out"))
    assert not (tmp_path / "x").exists()


def test_cli_main_writes_and_prints_validation(monkeypatch, tmp_path, capsys):
    _exporter(monkeypatch)
    label = _spec()
    monkeypatch.setattr(run_report, "exec_report_spec",
                        lambda *a, **kw: fse.exec_report_spec(*a, **{**kw, "view_server": "vs"}))
    argv = ["--report", label, "--output-format", "DOCUMENT", "--output", str(tmp_path), "--param", "scope=Sales"]
    assert run_report.main(argv) == 0
    printed = capsys.readouterr().out
    assert "toy-1 document written to" in printed
    assert "Validation: not validated (no validator is declared for this standard)" in printed
    assert "note: one note" in printed
    assert (tmp_path / "Sales-toy.json").exists()
    assert run_report.main(argv) == 1  # exists, no --force
    assert run_report.main(argv + ["--force"]) == 0


def test_validation_line_states():
    assert run_report.validation_line(_doc_result()) == "Validation: valid (json-schema)"
    inv = _doc_result(validation={"state": "invalid", "validator": "shacl", "findings": ["a", "b"], "reason": None})
    assert run_report.validation_line(inv) == "Validation: invalid (shacl, 2 findings)"

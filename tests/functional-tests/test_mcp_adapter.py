import pytest


def test_list_reports_smoke():
    from pyegeria.core.mcp_adapter import list_reports

    out = list_reports()
    assert isinstance(out, dict)
    assert len(out) > 0
    # Each entry is {name: {description, target_type, required_params, optional_params}}
    name, meta = next(iter(out.items()))
    assert isinstance(name, str)
    assert isinstance(meta, dict)
    assert "description" in meta
    assert "target_type" in meta
    assert "required_params" in meta
    assert "optional_params" in meta


def test_describe_known_report():
    from pyegeria.core.mcp_adapter import describe_report

    # Choose a commonly defined report spec present in base_report_formats.py
    meta = describe_report("Digital-Products", "ANY")
    assert isinstance(meta, dict)
    assert meta.get("target_type") in {"DigitalProduct", "Collection", "Referenceable"}
    assert "action" in meta


def test_run_report_monkeypatched(monkeypatch):
    # Monkeypatch the executor used by mcp_adapter so there is no network call
    import pyegeria.core.mcp_adapter as m

    fake_result = {"kind": "json", "data": [{"guid": "123", "display_name": "X"}]}

    def fake_exec(**kwargs):
        # Validate some inputs flow through
        assert kwargs["format_set_name"] == "Digital-Products"
        assert kwargs["output_format"] == "DICT"
        return fake_result

    monkeypatch.setattr(m, "exec_report_spec", fake_exec)

    out = m.run_report(report="Digital-Products", params={"search_string": "*"})
    assert out == fake_result


def test_run_find_report_specs_wildcards():
    from pyegeria.core.mcp_adapter import run_find_report_specs

    # "*" is the documented "skip this filter" sentinel for each argument
    out = run_find_report_specs(perspective="*", question="*", report_spec="*")
    assert isinstance(out, dict)
    assert "Matching Report Specs" in out

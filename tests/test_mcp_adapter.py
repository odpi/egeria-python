import types
import pytest


def test_list_tools_smoke():
    from pyegeria.mcp.mcp_adapter import list_mcp_tools

    out = list_mcp_tools()
    assert isinstance(out, dict)
    assert "formatSets" in out
    assert isinstance(out["formatSets"], list)


def test_describe_known_set():
    from pyegeria.mcp.mcp_adapter import describe_mcp_tool

    # Choose a commonly defined format set present in _output_formats.py
    meta = describe_mcp_tool("Digital-Products", outputType="ANY")
    assert isinstance(meta, dict)
    assert meta.get("target_type") in {"DigitalProduct", "Collection", "Referenceable"}
    assert "action" in meta


def test_run_tool_monkeypatched(monkeypatch):
    # Monkeypatch the executor used by mcp_adapter so there is no network call
    import pyegeria.mcp.mcp_adapter as m

    fake_result = {"kind": "json", "data": [{"guid": "123", "display_name": "X"}]}

    def fake_exec(**kwargs):
        # Validate some inputs flow through
        assert kwargs["format_set_name"] == "Digital-Products"
        assert kwargs["output_format"] == "DICT"
        return fake_result

    monkeypatch.setattr(m, "run_format_set_action_return", fake_exec)

    out = m.run_mcp_tool(formatSet="Digital-Products", outputFormat="DICT", params={"search_string": "*"})
    assert out == fake_result

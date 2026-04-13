from pyegeria.view import output_formatter as of


def test_normalize_mermaid_graph_transforms_renderer_hostile_syntax(monkeypatch):
    monkeypatch.setattr(of, "NORMALIZE_MERMAID", True)

    raw = """---
title: Sample
---
flowchart TD
1@{ shape: rounded, label: \"*A*\n**B**\"}
"""

    normalized = of._normalize_mermaid_graph(raw)

    assert "title: Sample" not in normalized
    assert "1(\"*A*\\n**B**\")" in normalized
    assert "@{" not in normalized


def test_resolve_normalize_mermaid_flag_defaults_true_when_unset(monkeypatch):
    monkeypatch.delenv("PYEGERIA_NORMALIZE_MERMAID", raising=False)
    monkeypatch.delenv("EGERIA_NORMALIZE_MERMAID", raising=False)
    assert of._resolve_normalize_mermaid_flag(default=True) is True


def test_resolve_normalize_mermaid_flag_honors_false_and_invalid(monkeypatch):
    monkeypatch.setenv("PYEGERIA_NORMALIZE_MERMAID", "false")
    assert of._resolve_normalize_mermaid_flag(default=True) is False

    monkeypatch.setenv("PYEGERIA_NORMALIZE_MERMAID", "maybe")
    assert of._resolve_normalize_mermaid_flag(default=True) is True


def test_resolve_normalize_mermaid_flag_reads_from_app_config(monkeypatch):
    monkeypatch.delenv("PYEGERIA_NORMALIZE_MERMAID", raising=False)
    monkeypatch.delenv("EGERIA_NORMALIZE_MERMAID", raising=False)

    class _Env:
        egeria_normalize_mermaid = False

    class _Cfg:
        Environment = _Env()

    import pyegeria.core.config as cfg_mod

    monkeypatch.setattr(cfg_mod, "get_app_config", lambda *args, **kwargs: _Cfg())
    assert of._resolve_normalize_mermaid_flag(default=True) is False



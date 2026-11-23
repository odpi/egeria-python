"""PY-52 read-back F1: a real offline run (a ServerClient whose sign-in fails) writes the "valid values not read"
marker into the generated templates; before, main() kept the half-built client and the lookup's [] dropped the line."""
import os
import sys

import pytest

import importlib

MARKER = "valid values not read (no Egeria connection)"


class _FailingSignIn:
    """What ServerClient is when the platform cannot be reached: it builds, and the sign-in raises."""
    instances = []

    def __init__(self, *args, **kwargs):
        type(self).instances.append(self)

    def create_egeria_bearer_token(self, *args, **kwargs):
        raise ConnectionError("platform unreachable")

    def get_valid_metadata_values(self, *args, **kwargs):  # what the old code kept calling; it swallowed every error
        return []


def _run_offline(monkeypatch, tmp_path, family="Views & Reports"):
    # the generator adds a log file named "debug_log" in the working directory when it is first imported
    monkeypatch.chdir(tmp_path)
    gen = importlib.import_module("commands.tech.generate_md_cmd_templates")
    monkeypatch.setattr(gen, "ServerClient", _FailingSignIn)
    monkeypatch.setattr(gen, "EGERIA_ROOT_PATH", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["generate_md_cmd_templates", "--usage-level", "Advanced", "--family", family,
                                      "--url", "https://nowhere.invalid:9443", "--userid", "u", "--pass", "p"])
    gen.main()
    out = tmp_path / "templates" / "advanced" / family
    return {p.name: p.read_text() for p in out.glob("*.md")}


def test_a_failed_sign_in_writes_the_marker_into_the_templates(monkeypatch, tmp_path):
    files = _run_offline(monkeypatch, tmp_path)
    assert files, "no template was written"
    assert any(MARKER in text for text in files.values()), sorted(files)


def test_the_real_client_path_was_taken(monkeypatch, tmp_path):
    _FailingSignIn.instances.clear()
    _run_offline(monkeypatch, tmp_path)
    assert _FailingSignIn.instances, "main() never built the client, so the test did not cover the real path"


def test_no_valid_values_line_is_silently_dropped(monkeypatch, tmp_path):
    files = _run_offline(monkeypatch, tmp_path)
    dash = files.get("Create_Dashboard.md", "")
    assert "Valid Values" in dash and MARKER in dash

"""
ISSUE-161: Dr.Egeria's entry points resolved the Egeria user differently, and the
dr_egeria / dr_egeria_folder CLIs fixed their --userid defaults at import time.
All of them now call resolve_egeria_credentials() when they run:
explicit value > EGERIA_USER env (as it is now) > settings User Profile
(config.json / .env) > quickstart default.
No live server: EgeriaTech and the Dr.Egeria processor are replaced with fakes.
"""
import pyegeria
import pytest
from click.testing import CliRunner

import commands.cat.dr_egeria as dr_cli
import commands.cat.dr_egeria_folder as dr_folder
from pyegeria.core.config import resolve_egeria_credentials, settings


class _FakeClient:
    instances = []

    def __init__(self, server, url, user, pwd=None, *args, **kwargs):
        self.user, self.pwd = user, pwd
        _FakeClient.instances.append(self)

    def create_egeria_bearer_token(self, *args, **kwargs):
        return "token"


@pytest.fixture
def fakes(monkeypatch):
    _FakeClient.instances = []
    monkeypatch.setattr(pyegeria, "EgeriaTech", _FakeClient)

    async def fake_process(*args, **kwargs):
        return None

    async def fake_run_one_file(input_file, display_name, *args, **kwargs):
        return (display_name, 1, 0, 0, "")

    monkeypatch.setattr(dr_cli, "process_md_file_v2", fake_process)
    monkeypatch.setattr(dr_folder, "run_one_file", fake_run_one_file)
    monkeypatch.delenv("EGERIA_USER", raising=False)
    monkeypatch.delenv("EGERIA_USER_PASSWORD", raising=False)
    return _FakeClient


def test_precedence_explicit_env_settings_default(monkeypatch):
    monkeypatch.delenv("EGERIA_USER", raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_name", "config_user")
    assert resolve_egeria_credentials()[0] == "config_user"
    monkeypatch.setenv("EGERIA_USER", "env_user")
    assert resolve_egeria_credentials()[0] == "env_user"
    assert resolve_egeria_credentials("explicit_user")[0] == "explicit_user"
    monkeypatch.delenv("EGERIA_USER")
    monkeypatch.setattr(settings.User_Profile, "user_name", None)
    assert resolve_egeria_credentials()[0] == "erinoverview"


def test_dr_egeria_cli_uses_env_set_after_import(fakes, monkeypatch, tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# empty\n")
    monkeypatch.setenv("EGERIA_USER", "late_env_user")
    monkeypatch.setenv("EGERIA_USER_PASSWORD", "late_pwd")
    result = CliRunner().invoke(dr_cli.process_markdown_file, [str(doc), "--validate"])
    assert result.exit_code == 0, result.output
    assert fakes.instances and fakes.instances[-1].user == "late_env_user"
    assert fakes.instances[-1].pwd == "late_pwd"


def test_dr_egeria_cli_uses_config_user_when_env_unset(fakes, monkeypatch, tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# empty\n")
    monkeypatch.setattr(settings.User_Profile, "user_name", "config_only_user")
    result = CliRunner().invoke(dr_cli.process_markdown_file, [str(doc), "--validate"])
    assert result.exit_code == 0, result.output
    assert fakes.instances[-1].user == "config_only_user"


def test_dr_egeria_cli_explicit_userid_wins(fakes, monkeypatch, tmp_path):
    doc = tmp_path / "doc.md"
    doc.write_text("# empty\n")
    monkeypatch.setenv("EGERIA_USER", "env_user")
    result = CliRunner().invoke(dr_cli.process_markdown_file, [str(doc), "--validate", "--userid", "flag_user"])
    assert result.exit_code == 0, result.output
    assert fakes.instances[-1].user == "flag_user"


def test_dr_egeria_folder_uses_env_set_after_import(fakes, monkeypatch, tmp_path):
    (tmp_path / "a.md").write_text("# empty\n")
    monkeypatch.setenv("EGERIA_USER", "late_folder_user")
    result = CliRunner().invoke(dr_folder.dr_egeria_folder, [str(tmp_path), "--validate"])
    assert result.exit_code == 0, result.output
    assert fakes.instances and fakes.instances[-1].user == "late_folder_user"

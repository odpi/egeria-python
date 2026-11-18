"""
PY-32: a run with no caller identity never falls back to the configured user in a multi-user process.

EA's U3 (2026-11-17): EA handed preview `as_client(client)`, a context manager, as the client. preview read
user_id/token from it as None, exec_report_spec then took the configured user (EA's service account), and the
run signed in as it. Now:
- async_preview refuses an object with no user_id, before anything runs;
- exec_report_spec, in a process declared multi-user, refuses a run with no user;
- in a single-user process (a CLI) an omitted user still takes the configured one, read at call time.
No live server: the executor's implementation is replaced and records who it was asked to run as.
"""
import asyncio
from contextlib import nullcontext

import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.authoring.preview import async_preview
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core.config import settings


@pytest.fixture
def recorded(monkeypatch):
    calls = []

    def fake_impl(name, **kwargs):
        calls.append({"user": kwargs.get("user"), "user_pass": kwargs.get("user_pass"), "token": kwargs.get("token")})
        return {"kind": "empty"}

    monkeypatch.setattr(fse, "_exec_report_spec_impl", fake_impl)
    monkeypatch.setattr(fse, "_with_spec_source", lambda result, *a, **k: result)
    return calls


@pytest.fixture
def multi_user(monkeypatch):
    monkeypatch.setenv("PYEGERIA_MULTI_USER", "1")


@pytest.fixture
def single_user(monkeypatch):
    monkeypatch.delenv("PYEGERIA_MULTI_USER", raising=False)
    import pyegeria.core._client_identities as ci
    monkeypatch.setattr(ci, "_MULTI_USER", False, raising=False)


def test_preview_refuses_a_context_manager_as_the_client():
    from pyegeria.authoring.models import AuthoringRefused
    with pytest.raises(AuthoringRefused) as info:
        asyncio.run(async_preview({"label": "x"}, client=nullcontext()))
    assert "has no user_id" in str(info.value)
    assert "not as_client(client)" in str(info.value)


@pytest.mark.parametrize("user", [None, ""])
def test_multi_user_exec_with_no_user_is_refused(multi_user, recorded, monkeypatch, user):
    monkeypatch.setattr(settings.User_Profile, "user_name", "the-service-account", raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_pwd", "service-pw", raising=False)
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        fse.exec_report_spec("Some-Spec", user=user, user_pass=None, token=None)
    assert "no user" in str(info.value) and "multi-user" in str(info.value)
    assert recorded == []   # never ran, so never as the service account


def test_multi_user_exec_with_no_identity_at_all_is_refused(multi_user, recorded, monkeypatch):
    monkeypatch.setattr(settings.User_Profile, "user_name", "the-service-account", raising=False)
    with pytest.raises(PyegeriaInvalidParameterException):
        fse.exec_report_spec("Some-Spec")
    assert recorded == []


def test_multi_user_exec_runs_as_the_given_user_and_never_takes_the_configured_password(multi_user, recorded,
                                                                                        monkeypatch):
    monkeypatch.setattr(settings.User_Profile, "user_pwd", "service-pw", raising=False)
    fse.exec_report_spec("Some-Spec", user="erinoverview", token="her-token")
    fse.exec_report_spec("Some-Spec", user="erinoverview")
    assert recorded[0] == {"user": "erinoverview", "user_pass": None, "token": "her-token"}
    assert recorded[1]["user"] == "erinoverview" and recorded[1]["user_pass"] is None


def test_single_user_exec_takes_the_configured_user_at_call_time(single_user, recorded, monkeypatch):
    monkeypatch.setattr(settings.User_Profile, "user_name", "cli-user", raising=False)
    monkeypatch.setattr(settings.User_Profile, "user_pwd", "cli-pw", raising=False)
    from pyegeria.core.config import configured_user_id
    fse.exec_report_spec("Some-Spec")
    fse.exec_report_spec("Some-Spec", user="someone")
    # EGERIA_USER (when set) wins over the settings' user, as for a CLI's client
    assert recorded[0] == {"user": configured_user_id(), "user_pass": "cli-pw", "token": None}
    assert recorded[1] == {"user": "someone", "user_pass": "cli-pw", "token": None}


def test_single_user_exec_with_no_user_configured_takes_the_cli_default(single_user, recorded, monkeypatch):
    from pyegeria.core.config import configured_user_id
    monkeypatch.setattr(settings.User_Profile, "user_name", None, raising=False)
    fse.exec_report_spec("Some-Spec")
    assert recorded[0]["user"] == configured_user_id()   # 6.x: a CLI's own resolution, not a refusal

"""
ISSUE-121: mcp_adapter must not write the caller's password (or bearer token) to
stderr or the log when running a report.
"""
import pytest
from loguru import logger

from pyegeria.core import mcp_adapter

SENTINEL_PASSWORD = "s3ntinel-PASSWORD-do-not-log"
SENTINEL_TOKEN = "s3ntinel-TOKEN-do-not-log"


@pytest.fixture
def captured_log():
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(str(m)), level="DEBUG")
    yield messages
    logger.remove(sink_id)


@pytest.fixture(autouse=True)
def _stub_exec(monkeypatch):
    monkeypatch.setattr(mcp_adapter, "exec_report_spec", lambda **kwargs: {"ok": True})


@pytest.mark.parametrize("fn_name", ["run_report", "_execute_egeria_call_blocking"])
def test_password_not_written_to_stderr_or_log(fn_name, capsys, captured_log):
    getattr(mcp_adapter, fn_name)(report="Some-Report", params={"a": 1}, view_server="vs",
                                  view_url="https://localhost:1", user="someone",
                                  user_pass=SENTINEL_PASSWORD)

    out = capsys.readouterr()
    assert SENTINEL_PASSWORD not in out.err + out.out
    assert SENTINEL_PASSWORD not in "".join(captured_log)
    # still useful for debugging: report, user and the kind of credential are shown
    assert "Some-Report" in out.err and "someone" in out.err
    assert "explicit user/password" in out.err


@pytest.mark.parametrize("fn_name", ["run_report", "_execute_egeria_call_blocking"])
def test_token_not_written_to_stderr_or_log(fn_name, capsys, captured_log):
    getattr(mcp_adapter, fn_name)(report="Some-Report", token=SENTINEL_TOKEN)

    out = capsys.readouterr()
    assert SENTINEL_TOKEN not in out.err + out.out
    assert SENTINEL_TOKEN not in "".join(captured_log)
    assert "bearer token" in out.err


def test_fallback_to_settings_is_described(capsys):
    mcp_adapter.run_report(report="Some-Report")

    assert "defaults from settings" in capsys.readouterr().err

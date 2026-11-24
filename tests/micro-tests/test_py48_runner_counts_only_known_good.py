# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-48 W2 (Architect): the runner counts ONLY known good statuses as succeeded.

Statuses in use: success, deferred, read (good); failure; warning. The runner used to count "anything but failure,
error or unknown" as succeeded, so the next new status would have been a silent success. Now a status outside
success/deferred/read (a new one, a missing one, or "warning") is a failure, with words naming the status.

No Egeria: a fake dispatcher hands back canned rows.
"""
import pytest

from pyegeria.authoring.runner import GOOD_STATUSES, async_run_markdown

pytestmark = pytest.mark.unit

DOC = "## Create Project\n### Display Name\nPY48W2::Widget\n"


class _Dispatcher:
    def __init__(self, rows):
        self.rows = rows

    async def dispatch_batch(self, commands, context):
        return self.rows


def _row(status, **extra):
    row = {"verb": "Create", "object_type": "Project", "message": "m", "display_name": "PY48W2::Widget"}
    if status is not None:
        row["status"] = status
    return {**row, **extra}


async def _run(monkeypatch, rows, directive="process"):
    import md_processing.dr_egeria as dr

    monkeypatch.setattr(dr, "setup_dispatcher", lambda client: _Dispatcher(rows))
    return await async_run_markdown(object(), DOC, directive)


def test_the_good_statuses_are_success_deferred_read():
    assert set(GOOD_STATUSES) == {"success", "deferred", "read"}


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["success", "deferred", "read"])
async def test_a_known_good_status_is_succeeded(monkeypatch, status):
    out = await _run(monkeypatch, [_row(status)])
    assert out["success"] is True and out["commands_succeeded"] == 1 and out["commands_failed"] == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["something_new", "warning", "", None, "SUCCESS"])
async def test_any_other_status_is_a_failure_with_words(monkeypatch, status):
    out = await _run(monkeypatch, [_row(status)])
    assert out["success"] is False and out["commands_succeeded"] == 0 and out["commands_failed"] == 1
    [err] = out["execution_errors"]
    assert "not a known good status" in err["message"]
    assert (repr(status) if status else "no status") in err["message"] or status in (None, "")


@pytest.mark.asyncio
async def test_a_new_status_among_good_rows_fails_only_that_row(monkeypatch):
    out = await _run(monkeypatch, [_row("success"), _row("something_new"), _row("deferred")])
    assert out["commands_total"] == 3 and out["commands_succeeded"] == 2 and out["commands_failed"] == 1
    assert out["success"] is False


@pytest.mark.asyncio
async def test_a_failure_row_keeps_its_own_errors(monkeypatch):
    out = await _run(monkeypatch, [_row("failure", errors=["boom"])])
    assert [e["message"] for e in out["execution_errors"]] == ["boom"]


@pytest.mark.asyncio
async def test_the_validate_run_reports_a_new_status_under_validation_errors(monkeypatch):
    out = await _run(monkeypatch, [_row("something_new")], directive="validate")
    assert out["success"] is False and out["validation_errors"]

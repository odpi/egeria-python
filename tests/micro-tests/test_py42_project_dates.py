"""PY-42: project create, update and task sent startDate and plannedEndDate. Egeria's ProjectProperties reads
plannedStartDate, actualStartDate, plannedCompletionDate and actualCompletionDate and drops any other key
silently, so the dates were lost. Each test captures the body actually sent. No live server."""
import json
import warnings

import pytest

from pyegeria.omvs.project_manager import ProjectManager

READ = {"plannedStartDate", "actualStartDate", "plannedCompletionDate", "actualCompletionDate"}
DROPPED = {"startDate", "plannedEndDate"}


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "g", "elements": [], "relatedHTTPCode": 200}


@pytest.fixture
def sent(monkeypatch):
    calls: list = []
    monkeypatch.setattr(ProjectManager, "check_connection", lambda self: "test")
    client = ProjectManager("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


def _props(calls):
    return calls[-1]["body"]["properties"]


CALLS = {
    "create": lambda c, **kw: c.create_project(display_name="p", **kw),
    "update": lambda c, **kw: c.update_project("guid-1", display_name="p", **kw),
    "task": lambda c, **kw: c.create_project_task("guid-1", display_name="t", **kw),
}


@pytest.mark.parametrize("op", CALLS)
def test_the_four_dates_egeria_reads_are_sent_under_those_names(sent, op):
    client, calls = sent
    CALLS[op](client, planned_start_date="2030-01-01T00:00:00", actual_start_date="2030-01-02T00:00:00",
              planned_completion_date="2030-06-01T00:00:00", actual_completion_date="2030-06-02T00:00:00")
    props = _props(calls)
    assert props["plannedStartDate"] == "2030-01-01T00:00:00"
    assert props["actualStartDate"] == "2030-01-02T00:00:00"
    assert props["plannedCompletionDate"] == "2030-06-01T00:00:00"
    assert props["actualCompletionDate"] == "2030-06-02T00:00:00"
    assert not DROPPED & set(props)


@pytest.mark.parametrize("op", CALLS)
def test_the_old_parameter_names_still_work_are_sent_under_the_real_keys_and_warn(sent, op):
    client, calls = sent
    with pytest.warns(FutureWarning, match="start_date.*plannedStartDate|planned_start_date"):
        CALLS[op](client, start_date="2030-01-01T00:00:00", planned_end_date="2030-06-01T00:00:00")
    props = _props(calls)
    assert props["plannedStartDate"] == "2030-01-01T00:00:00"
    assert props["plannedCompletionDate"] == "2030-06-01T00:00:00"
    assert not DROPPED & set(props)


def test_the_old_names_still_work_positionally(sent):
    client, calls = sent
    # create_project(..., status, phase, health, start_date, planned_end_date, body): the positions are unchanged
    with pytest.warns(FutureWarning):
        client.create_project(None, None, None, False, "p", "d", "Project", "id", True, "s", "ph", "h",
                              "2030-01-01T00:00:00", "2030-06-01T00:00:00")
    assert _props(calls)["plannedStartDate"] == "2030-01-01T00:00:00"
    assert _props(calls)["plannedCompletionDate"] == "2030-06-01T00:00:00"


def test_the_new_names_do_not_warn(sent):
    client, calls = sent
    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        client.create_project(display_name="p", planned_start_date="2030-01-01T00:00:00")


def test_old_and_new_name_that_disagree_are_refused_not_guessed(sent):
    client, calls = sent
    with pytest.warns(FutureWarning), pytest.raises(TypeError, match="planned_start_date"):
        client.create_project(display_name="p", start_date="2030-01-01", planned_start_date="2031-01-01")
    assert calls == []


def test_no_date_given_is_no_date_sent_never_a_made_up_one(sent):
    client, calls = sent
    client.create_project(display_name="p")
    props = _props(calls)
    assert all(props.get(k) is None for k in READ) and not DROPPED & set(props)


def test_the_warning_is_a_FutureWarning_so_ordinary_callers_see_it_and_not_a_DeprecationWarning(sent):
    """DeprecationWarning is ignored by default outside __main__ and test runners; FutureWarning is shown to every caller."""
    client, calls = sent
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        client.create_project(display_name="p", start_date="2030-01-01T00:00:00", planned_end_date="2030-06-01T00:00:00")
    kinds = {w.category for w in seen if "deprecated" in str(w.message)}
    assert kinds == {FutureWarning}
    assert not any(issubclass(w.category, DeprecationWarning) for w in seen if "start_date" in str(w.message))
    assert any("start_date" in str(w.message) for w in seen) and any("planned_end_date" in str(w.message) for w in seen)

import pytest

pytestmark = pytest.mark.unit

from pyegeria.core._server_client import ServerClient


@pytest.fixture()
def client(monkeypatch):
    # Avoid real network during client construction
    monkeypatch.setattr(
        ServerClient, "check_connection", lambda self: "OK",
        raising=False,
    )
    c = ServerClient(server_name="server", platform_url="http://localhost:9443", user_id="tester")
    return c


def test_add_comment_to_element_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_add_comment_to_element(self, element_guid, comment, comment_type, body):
        calls["args"] = (element_guid, comment, comment_type, body)
        # return a sentinel value like the real method would
        return "GUID-123"

    monkeypatch.setattr(ServerClient, "_async_add_comment_to_element", fake_async_add_comment_to_element)

    result = client.add_comment_to_element("elem-1", "hello world", "STANDARD_COMMENT", None)

    assert result == "GUID-123"
    assert calls["args"][0] == "elem-1"
    assert calls["args"][1] == "hello world"
    assert calls["args"][2] == "STANDARD_COMMENT"


@pytest.mark.skip(
    reason="add_comment_reply has no corresponding _async_* method on ServerClient, and Egeria's "
           "feedback-manager REST API (Egeria-api-feedback-manager.http) has no distinct "
           "comment-reply endpoint either — replies appear to just be regular comments attached "
           "via addCommentToElement, not a separate mechanism. Needs a product decision on whether "
           "to implement real reply support or remove this test."
)
def test_add_comment_reply_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_add_comment_reply(self, element_guid, comment_guid, comment, comment_type, body):
        calls["args"] = (element_guid, comment_guid, comment, comment_type, body)
        return {"guid": "REPLY-999"}

    monkeypatch.setattr(ServerClient, "async_add_comment_reply", fake_async_add_comment_reply)

    result = client.add_comment_reply("elem-1", "cmt-2", "a reply", "STANDARD_COMMENT", None)

    assert result == {"guid": "REPLY-999"}
    assert calls["args"][:4] == ("elem-1", "cmt-2", "a reply", "STANDARD_COMMENT")


def test_update_comment_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_update_comment(self, comment_guid, comment, comment_type, body, merge_update):
        calls["args"] = (comment_guid, comment, comment_type, body, merge_update)
        return None

    monkeypatch.setattr(ServerClient, "_async_update_comment", fake_async_update_comment)

    # update_comment's sync wrapper doesn't propagate a return value (matches
    # _async_update_comment's own "-> None" contract).
    result = client.update_comment("cmt-42", "new text", "STANDARD_COMMENT", {"x": 1}, True)

    assert result is None
    assert calls["args"] == ("cmt-42", "new text", "STANDARD_COMMENT", {"x": 1}, True)


def test_setup_accepted_answer_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_setup_accepted_answer(self, question_comment_guid, answer_comment_guid):
        calls["args"] = (question_comment_guid, answer_comment_guid)
        return None

    monkeypatch.setattr(ServerClient, "_async_setup_accepted_answer", fake_async_setup_accepted_answer)

    assert client.setup_accepted_answer("q-1", "a-1") is None
    assert calls["args"] == ("q-1", "a-1")


def test_setup_clear_answer_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_clear_accepted_answer(self, question_comment_guid, answer_comment_guid):
        calls["args"] = (question_comment_guid, answer_comment_guid)
        return None

    monkeypatch.setattr(ServerClient, "_async_clear_accepted_answer", fake_async_clear_accepted_answer)

    assert client.setup_clear_answer("q-2", "a-2") is None
    assert calls["args"] == ("q-2", "a-2")


def test_remove_comment_from_element_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_remove_comment_from_element(self, comment_guid, body, cascade_delete=False):
        calls["args"] = (comment_guid, body, cascade_delete)
        return None

    monkeypatch.setattr(
        ServerClient, "_async_remove_comment_from_element", fake_async_remove_comment_from_element
    )

    assert client.remove_comment_from_element("c-1", {"y": 2}, cascade_delete=True) is None
    assert calls["args"] == ("c-1", {"y": 2}, True)


def test_get_comment_by_guid_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_get_comment_by_guid(self, guid, graph_query_depth, output_format, report_spec, body):
        calls["args"] = (guid, graph_query_depth, output_format, report_spec, body)
        return {"comment_guid": guid, "ok": True}

    monkeypatch.setattr(ServerClient, "_async_get_comment_by_guid", fake_async_get_comment_by_guid)

    out = client.get_comment_by_guid("cg-1", graph_query_depth=3, output_format="JSON", report_spec=None, body=None)
    assert out == {"comment_guid": "cg-1", "ok": True}
    assert calls["args"] == ("cg-1", 3, "JSON", None, None)


def test_get_attached_comments_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_get_attached_comments(self, element_guid, metadata_element_type_name, graph_query_depth,
                                                start_from, page_size, output_format, report_spec, body):
        calls["args"] = (element_guid, metadata_element_type_name, graph_query_depth, start_from, page_size,
                          output_format, report_spec, body)
        return [
            {"guid": "c1"},
            {"guid": "c2"},
        ]

    monkeypatch.setattr(ServerClient, "_async_get_attached_comments", fake_async_get_attached_comments)

    result = client.get_attached_comments("elem-99", metadata_element_type_name="Comment", graph_query_depth=3,
                                          start_from=0, page_size=10, output_format="JSON", report_spec=None,
                                          body={})

    assert result == [{"guid": "c1"}, {"guid": "c2"}]
    assert calls["args"] == ("elem-99", "Comment", 3, 0, 10, "JSON", None, {})


def test_find_comments_sync_calls_async(monkeypatch, client):
    calls = {}

    async def fake_async_find_comments(
        self,
        search_string,
        classification_names,
        metadata_element_subtypes,
        starts_with,
        ends_with,
        ignore_case,
        start_from,
        page_size,
        output_format,
        report_spec,
        body,
    ):
        calls["args"] = (
            search_string,
            classification_names,
            metadata_element_subtypes,
            starts_with,
            ends_with,
            ignore_case,
            start_from,
            page_size,
            output_format,
            report_spec,
            body,
        )
        return [{"guid": "c1"}]

    monkeypatch.setattr(ServerClient, "_async_find_comments", fake_async_find_comments)

    result = client.find_comments("foo", classification_names=["X"], metadata_element_subtypes=["Comment"],
                                   starts_with=True, ends_with=False, ignore_case=False, start_from=5, page_size=25,
                                   output_format="JSON", report_spec=None, body=None)

    assert result == [{"guid": "c1"}]
    assert calls["args"] == (
        "foo",
        ["X"],
        ["Comment"],
        True,
        False,
        False,
        5,
        25,
        "JSON",
        None,
        None,
    )

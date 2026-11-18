"""
add_like_to_element ignored the emoji it was given. With an emoji it sent the docstring placeholder
"Add characters here as text" and put the like in a zone hard-coded to erinoverview. Now the body carries the
caller's emoji and no zone; without an emoji (or with the caller's own body) the request is as before.
"""
import json

from pyegeria.core._server_client import ServerClient


class _Response:
    def json(self):
        return {"relatedHTTPCode": 200, "guid": "like-guid"}


def _capture(monkeypatch):
    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "test", raising=False)
    client = ServerClient("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append((method, url, json.loads(payload) if isinstance(payload, str) else payload))
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


def test_the_emoji_passed_is_the_emoji_sent(monkeypatch):
    client, calls = _capture(monkeypatch)
    client.add_like_to_element("elem-guid", emoji="👍")
    method, url, body = calls[-1]
    assert method == "POST" and url.endswith("feedback-manager/elements/elem-guid/likes")
    assert body["properties"] == {"class": "LikeProperties", "emoji": "👍"}


def test_no_zone_is_hard_coded(monkeypatch):
    client, calls = _capture(monkeypatch)
    client.add_like_to_element("elem-guid", emoji="❤️")
    body = calls[-1][2]
    assert "initialClassifications" not in body
    assert "erinoverview" not in json.dumps(body)
    assert "Add characters here" not in json.dumps(body, ensure_ascii=False)


def test_without_an_emoji_no_body_is_sent(monkeypatch):
    client, calls = _capture(monkeypatch)
    client.add_like_to_element("elem-guid")
    assert calls[-1][2] is None


def test_a_callers_own_body_is_sent_unchanged(monkeypatch):
    client, calls = _capture(monkeypatch)
    own = {"class": "NewAttachmentRequestBody",
           "initialClassifications": {"ZoneMembership": {"class": "ZoneMembershipProperties",
                                                         "zoneMembership": ["mine"]}},
           "properties": {"class": "LikeProperties", "emoji": "🎉"}}
    client.add_like_to_element("elem-guid", emoji="👍", body=own)
    assert calls[-1][2] == own

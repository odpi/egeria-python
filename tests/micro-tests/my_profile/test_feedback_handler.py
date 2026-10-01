"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for the app-wide feedback mechanism (feedback_handler + FeedbackScreens).

   Tests marked `live_capable` run against fakes by default and against a real
   Egeria view server when PYEG_LIVE_EGERIA=1 is set.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from textual.app import App
from textual.widgets import DataTable, TextArea

from feedback_handler import FeedbackMixin, FEEDBACK_LOG_OWNER, FEEDBACK_LOG_QN
from FeedbackScreens import FeedbackScreen, FeedbackLogScreen
from pyegeria import PyegeriaException


class DummyFeedbackApp(FeedbackMixin):
    """Test harness implementing FeedbackMixin."""

    def __init__(self, backend=None, user_name=FEEDBACK_LOG_OWNER):
        self.pushed_screens = []
        self.notifications = []
        self.log_messages = []
        self.user_name = user_name
        self.user_password = "secret"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        if backend is not None:
            backend.apply_connection(self)
            self.user_name = user_name if not backend.live else backend.user_id
        self.user_GUID = "profile-guid-123"
        self.screen = MagicMock()

    def log(self, msg, *args, **kwargs):
        self.log_messages.append(str(msg))

    def notify(self, msg, *args, **kwargs):
        self.notifications.append((str(msg), kwargs.get("severity")))

    async def push_screen(self, screen, callback=None):
        self.pushed_screens.append((screen, callback))


def fake_client(existing_log_guid=None, notes=None):
    """An Egeria client stand-in whose feedback calls are AsyncMocks."""
    client = MagicMock()
    client._async_get_note_logs_by_name = AsyncMock(
        return_value=[{"elementHeader": {"guid": existing_log_guid}}] if existing_log_guid else "No elements found"
    )
    client._async_create_note_log = AsyncMock(return_value="new-log-guid")
    client._async_create_note = AsyncMock(return_value="note-guid")
    client._async_get_notes_for_note_log = AsyncMock(return_value=notes if notes is not None else "No elements found")
    return client


FEEDBACK = {"screen": "MainScreen", "screen_title": "My Profile", "category": "Bug", "text": "Table is empty"}


class TestFeedbackCallback:

    async def test_cancelled_feedback_makes_no_egeria_call(self, backend):
        app = DummyFeedbackApp()
        egeria = backend.always_fake("feedback_handler.Egeria")
        await app.feedback_callback(None)
        egeria.assert_not_called()

    async def test_creates_log_attached_to_owner_profile_on_first_use(self, backend):
        app = DummyFeedbackApp()
        client = fake_client()
        backend.always_fake("feedback_handler.Egeria", returns=client)

        await app.feedback_callback(FEEDBACK)

        client._async_get_note_logs_by_name.assert_awaited_once()
        assert client._async_get_note_logs_by_name.await_args.args[0] == FEEDBACK_LOG_QN
        create_kwargs = client._async_create_note_log.await_args.kwargs
        assert create_kwargs["element_guid"] == "profile-guid-123"
        assert create_kwargs["body"]["class"] == "NewAttachmentRequestBody"
        assert create_kwargs["body"]["properties"]["qualifiedName"] == FEEDBACK_LOG_QN

        log_guid = client._async_create_note.await_args.args[0]
        note = client._async_create_note.await_args.kwargs["body"]
        assert log_guid == "new-log-guid"
        assert note["class"] == "NoteProperties"
        assert note["description"] == "Table is empty"
        assert note["additionalProperties"]["category"] == "Bug"
        assert note["additionalProperties"]["screen"] == "MainScreen"
        assert note["additionalProperties"]["submittedBy"] == FEEDBACK_LOG_OWNER
        client.close_session.assert_called_once()
        assert app.notifications[-1][0].startswith("Thank you")

    async def test_existing_log_is_reused(self, backend):
        app = DummyFeedbackApp()
        client = fake_client(existing_log_guid="existing-log")
        backend.always_fake("feedback_handler.Egeria", returns=client)

        await app.feedback_callback(FEEDBACK)

        client._async_create_note_log.assert_not_awaited()
        assert client._async_create_note.await_args.args[0] == "existing-log"

    async def test_other_user_creates_standalone_log(self, backend):
        app = DummyFeedbackApp(user_name="erinoverview")
        client = fake_client()
        backend.always_fake("feedback_handler.Egeria", returns=client)

        await app.feedback_callback(FEEDBACK)

        create_kwargs = client._async_create_note_log.await_args.kwargs
        assert create_kwargs["element_guid"] is None
        assert create_kwargs["body"]["class"] == "NewElementRequestBody"
        assert client._async_create_note.await_args.kwargs["body"]["additionalProperties"]["submittedBy"] == "erinoverview"

    async def test_egeria_error_is_reported(self, backend):
        app = DummyFeedbackApp()
        client = fake_client(existing_log_guid="existing-log")
        client._async_create_note.side_effect = PyegeriaException("boom")
        backend.always_fake("feedback_handler.Egeria", returns=client)

        await app.feedback_callback(FEEDBACK)

        assert app.notifications[-1][1] == "error"
        client.close_session.assert_called_once()


class TestFeedbackLog:

    async def test_log_is_private_to_owner(self, backend):
        app = DummyFeedbackApp(user_name="erinoverview")
        egeria = backend.always_fake("feedback_handler.Egeria")
        await app.action_view_feedback_log()
        egeria.assert_not_called()
        assert app.pushed_screens == []
        assert app.notifications[-1] == ("The feedback log is private", "warning")

    async def test_entries_are_parsed_newest_first(self, backend):
        app = DummyFeedbackApp()
        notes = [
            {"elementHeader": {"versions": {"createTime": "t1", "createdBy": "x"}},
             "properties": {"description": "older", "additionalProperties": {
                 "submittedAt": "2026-09-01T10:00:00", "submittedBy": "garygeeke",
                 "category": "Bug", "screen": "MainScreen"}}},
            {"elementHeader": {"versions": {"createTime": "2026-09-02T10:00:00", "createdBy": "erinoverview"}},
             "properties": {"description": "newer"}},
        ]
        client = fake_client(existing_log_guid="existing-log", notes=notes)
        backend.always_fake("feedback_handler.Egeria", returns=client)

        await app.action_view_feedback_log()

        screen, _ = app.pushed_screens[0]
        assert isinstance(screen, FeedbackLogScreen)
        assert [e["text"] for e in screen.feedback_entries] == ["newer", "older"]
        assert screen.feedback_entries[0]["submitted_by"] == "erinoverview"
        assert screen.feedback_entries[1]["category"] == "Bug"

    async def test_missing_log_gives_empty_list(self, backend):
        app = DummyFeedbackApp()
        client = fake_client()
        assert await app.get_feedback_entries(client) == []
        client._async_get_notes_for_note_log.assert_not_awaited()

    @pytest.mark.live_capable
    async def test_feedback_round_trip(self, backend):
        """Submitted feedback shows up in the log (really written in live mode)."""
        if not backend.live:
            pytest.skip("round trip only meaningful against a live server")
        from pyegeria import MyProfile

        app = DummyFeedbackApp(backend)
        profile_client = MyProfile(backend.view_server, backend.platform_url, backend.user_id, backend.user_pwd)
        profile_client.create_egeria_bearer_token(backend.user_id, backend.user_pwd)
        profile = await profile_client._async_get_my_profile(output_format="JSON")
        app.user_GUID = (profile[0] if isinstance(profile, list) else profile)["elementHeader"]["guid"]

        text = backend.unique("Round trip feedback")
        await app.feedback_callback({**FEEDBACK, "text": text})
        client = app._feedback_client()
        entries = await app.get_feedback_entries(client)
        client.close_session()
        assert text in [e["text"] for e in entries]


class FeedbackHostApp(App):

    def __init__(self, screen_factory):
        super().__init__()
        self.screen_factory = screen_factory
        self.target_screen = None
        self.dismissed_result = "not dismissed"

    async def on_mount(self):
        self.target_screen = self.screen_factory()

        def _cb(result):
            self.dismissed_result = result

        await self.push_screen(self.target_screen, callback=_cb)


class TestFeedbackScreens:

    async def test_empty_feedback_is_not_submitted(self):
        app = FeedbackHostApp(lambda: FeedbackScreen("MainScreen", "My Profile"))
        async with app.run_test() as pilot:
            await pilot.pause()
            app.target_screen.action_submit()
            await pilot.pause()
            assert app.dismissed_result == "not dismissed"

    async def test_feedback_is_returned(self):
        app = FeedbackHostApp(lambda: FeedbackScreen("MainScreen", "My Profile"))
        async with app.run_test() as pilot:
            await pilot.pause()
            app.target_screen.query_one("#feedback_text", TextArea).text = "Great app"
            await pilot.press("ctrl+s")
            await pilot.pause()
            assert app.dismissed_result == {
                "screen": "MainScreen", "screen_title": "My Profile", "category": "Suggestion", "text": "Great app",
            }

    async def test_cancel_returns_none(self):
        app = FeedbackHostApp(lambda: FeedbackScreen("MainScreen"))
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert app.dismissed_result is None

    async def test_log_screen_shows_entries(self):
        entries = [{"date": "d", "submitted_by": "garygeeke", "category": "Bug", "screen": "MainScreen", "text": "t"}]
        app = FeedbackHostApp(lambda: FeedbackLogScreen(entries))
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.target_screen.query_one("#feedback_log_table", DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0) == ["d", "garygeeke", "Bug", "MainScreen", "t"]

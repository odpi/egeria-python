"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   App-wide feedback handler mixin for My Profile Textual App.

   Feedback left from any screen is accumulated as Notes in a single NoteLog owned by
   FEEDBACK_LOG_OWNER. The log is found by its fixed qualified name, so any user can
   add to it; only the owner can open it from within the app.

   Note: the Egeria server itself does not restrict who can read the log (the
   quickstart deployment enforces no zone security), so "private" is enforced by
   this app, not by Egeria.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[4]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from pyegeria import Egeria, PyegeriaException
from FeedbackScreens import FeedbackScreen, FeedbackLogScreen

FEEDBACK_LOG_OWNER = "garygeeke"
FEEDBACK_LOG_QN = f"NoteLog::{FEEDBACK_LOG_OWNER}::My-Profile-App-Feedback"
FEEDBACK_LOG_NAME = "My Profile App Feedback"


class FeedbackMixin:
    """Mixin class providing the app-wide feedback mechanism for MyProfileApp."""

    def _feedback_client(self) -> Egeria:
        client = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
        client.create_egeria_bearer_token(self.user_name, self.user_password)
        return client

    async def action_feedback(self) -> None:
        """Open the feedback form for whichever screen is currently active."""
        current = self.screen
        if isinstance(current, (FeedbackScreen, FeedbackLogScreen)):
            return
        screen_name = type(current).__name__
        screen_title = str(getattr(current, "sub_title", "") or "")
        await self.push_screen(FeedbackScreen(screen_name, screen_title), callback=self.feedback_callback)

    async def feedback_callback(self, feedback: Any) -> None:
        """Record the feedback returned from the FeedbackScreen in the feedback log."""
        if not isinstance(feedback, dict):
            self.log("Feedback cancelled")
            return
        client = None
        try:
            client = self._feedback_client()
            log_guid = await self._get_or_create_feedback_log(client)
            if not log_guid:
                self.notify("Unable to locate or create the feedback log, feedback not saved",
                            timeout=10, severity="error")
                return
            note_guid = await client._async_create_note(log_guid, body=self._build_feedback_note(log_guid, feedback))
            self.log(f"Feedback recorded as note: {note_guid}")
            self.notify("Thank you, your feedback has been recorded")
        except PyegeriaException as e:
            self.log(f"Failed to record feedback: {e}")
            self.notify(f"Failed to record feedback: {e}", timeout=10, severity="error")
        finally:
            if client:
                client.close_session()

    def _build_feedback_note(self, log_guid: str, feedback: dict) -> dict:
        timestamp = datetime.now().isoformat(timespec="seconds")
        return {
            "class": "NoteProperties",
            "typeName": "Note",
            "qualifiedName": f"Note::{log_guid}::{self.user_name}::{timestamp}",
            "displayName": f"{feedback.get('category')} - {feedback.get('screen')}",
            "description": feedback.get("text"),
            "additionalProperties": {
                "category": str(feedback.get("category") or ""),
                "screen": str(feedback.get("screen") or ""),
                "screenTitle": str(feedback.get("screen_title") or ""),
                "submittedBy": self.user_name,
                "submittedAt": timestamp,
            },
        }

    async def _find_feedback_log(self, client: Egeria) -> str | None:
        response = await client._async_get_note_logs_by_name(FEEDBACK_LOG_QN, graph_query_depth=0,
                                                             output_format="JSON")
        if isinstance(response, list) and response:
            return response[0].get("elementHeader", {}).get("guid")
        return None

    async def _get_or_create_feedback_log(self, client: Egeria) -> str | None:
        """Return the feedback log's GUID, creating the log on first use.

        When the owner creates it, it is attached to their profile. If another user
        gets there first the log is created standalone - it is still found by name.
        """
        log_guid = await self._find_feedback_log(client)
        if log_guid:
            return log_guid
        properties = {
            "class": "NoteLogProperties",
            "typeName": "NoteLog",
            "qualifiedName": FEEDBACK_LOG_QN,
            "displayName": FEEDBACK_LOG_NAME,
            "description": f"Private log of feedback on the My Profile app, owned by {FEEDBACK_LOG_OWNER}.",
        }
        owner_guid = self.user_GUID if self.user_name == FEEDBACK_LOG_OWNER else None
        if owner_guid:
            body = {"class": "NewAttachmentRequestBody", "properties": properties}
        else:
            body = {"class": "NewElementRequestBody", "properties": properties}
        log_guid = await client._async_create_note_log(element_guid=owner_guid, body=body)
        self.log(f"Created feedback log: {log_guid}")
        return log_guid

    async def action_view_feedback_log(self) -> None:
        """Show the accumulated feedback - only available to the log's owner."""
        if self.user_name != FEEDBACK_LOG_OWNER:
            self.notify("The feedback log is private", timeout=5, severity="warning")
            return
        if isinstance(self.screen, (FeedbackScreen, FeedbackLogScreen)):
            return
        client = None
        try:
            client = self._feedback_client()
            entries = await self.get_feedback_entries(client)
        except PyegeriaException as e:
            self.log(f"Failed to retrieve feedback log: {e}")
            self.notify(f"Failed to retrieve feedback log: {e}", timeout=10, severity="error")
            return
        finally:
            if client:
                client.close_session()
        await self.push_screen(FeedbackLogScreen(entries))

    async def get_feedback_entries(self, client: Egeria) -> list[dict]:
        """Retrieve the notes in the feedback log, newest first."""
        log_guid = await self._find_feedback_log(client)
        if not log_guid:
            return []
        notes = await client._async_get_notes_for_note_log(log_guid, metadata_element_type_name="Note",
                                                           graph_query_depth=0, output_format="JSON")
        if not isinstance(notes, list):
            return []
        entries = []
        for note in notes:
            props = note.get("properties") or {}
            extra = props.get("additionalProperties") or {}
            versions = (note.get("elementHeader") or {}).get("versions") or {}
            entries.append({
                "date": extra.get("submittedAt") or versions.get("createTime", ""),
                "submitted_by": extra.get("submittedBy") or versions.get("createdBy", ""),
                "category": extra.get("category", ""),
                "screen": extra.get("screen", ""),
                "text": props.get("description", ""),
            })
        entries.sort(key=lambda e: str(e["date"]), reverse=True)
        return entries

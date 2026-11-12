# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Commands the compact specs offer that Dr.Egeria can't carry out as written: a sentence, not silence.

Without a registered processor these came back as "No processor registered for '<command>'" (a WARNING
row; the round-trip probe of 2026-11-12 saw nothing created and nothing explained). Each entry says why
and what to use instead; the spec correction itself belongs to the compact spec owners (F-C).
"""
from __future__ import annotations

from md_processing.v2.processors import AsyncBaseCommandProcessor

NOT_SUPPORTED_YET: dict[str, str] = {
    "Create Rating": ("a rating is always attached to the element it rates (AttachedRating), so Egeria has no "
                      "standalone create; use Attach Rating with a Reviewed Element"),
    "Create Like": ("a like is always attached to the element it likes (AttachedLike), so Egeria has no "
                    "standalone create; use Attach Like with a Liked Element"),
    "Create Data Sharing Request": ("in Egeria a DataSharingRequest is a ToDo subtype (an action, "
                                    "DataSharingRequestProperties extends ToDoProperties), not the collection "
                                    "the spec describes, and pyegeria has no create call for it yet"),
}


class NotSupportedYetProcessor(AsyncBaseCommandProcessor):
    """Fails the command with the reason from NOT_SUPPORTED_YET; nothing is sent to Egeria."""

    async def fetch_as_is(self):
        return None

    async def apply_changes(self) -> str:
        command = f"{self.command.verb} {self.command.object_type}"
        reason = NOT_SUPPORTED_YET.get(command) or next(
            (why for name, why in NOT_SUPPORTED_YET.items() if name.lower() == command.lower()),
            "it has no Dr.Egeria implementation yet")
        raise ValueError(f"{command} is not supported yet: {reason}. Nothing was sent to Egeria.")

"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Bookmarks handler mixin for My Profile Textual App.

   pyegeria has no favourites API, so a user's bookmarks are the members of a
   private collection with a fixed qualified name (see bookmarks_qualified_name).
   The collection is created the first time the user bookmarks something. It is
   anchored to the user's profile and linked from it by a ResourceList relationship
   whose resourceUse is "Bookmarks", so MyProfile.get_my_resources() finds it.
"""

import sys
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
from MyBookMarksScreen import MyBookMarksScreen
from profile_utils import element_summary, row_identity

BOOKMARKS_DISPLAY_NAME = "My Bookmarks"
BOOKMARKS_RESOURCE_USE = "Bookmarks"


def bookmarks_qualified_name(user_name: str) -> str:
    """Qualified name of the collection holding a user's bookmarks."""
    return f"Bookmarks::{user_name}"


class BookmarksMixin:
    """Mixin class providing the bookmarks feature for MyProfileApp."""

    def _bookmarks_client(self) -> Egeria:
        client = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                        user_id=self.user_name, user_pwd=self.user_password)
        client.create_egeria_bearer_token(self.user_name, self.user_password)
        return client

    def _find_bookmarks_collection(self, client: Egeria) -> str | None:
        """GUID of the user's bookmarks collection, or None if it doesn't exist yet."""
        qualified_name = bookmarks_qualified_name(self.user_name)
        response = client.get_collections_by_name(name=qualified_name, output_format="JSON")
        for element in response if isinstance(response, list) else []:
            summary = element_summary(element)
            if summary.get("qualified_name") == qualified_name and summary.get("guid"):
                return summary["guid"]
        return None

    def _bookmarks_profile_guid(self, client: Egeria) -> str:
        """GUID of the user's profile, which owns the bookmarks collection."""
        if getattr(self, "user_GUID", ""):
            return self.user_GUID
        profile = client.get_my_profile(output_format="JSON", graph_query_depth=0)
        if isinstance(profile, list) and profile:
            profile = profile[0]
        guid = element_summary(profile).get("guid", "")
        if not guid:
            raise ValueError(f"Unable to find the profile for {self.user_name} to attach bookmarks to")
        self.user_GUID = guid
        return guid

    def _get_or_create_bookmarks_collection(self, client: Egeria) -> str:
        guid = self._find_bookmarks_collection(client)
        if guid:
            return guid
        profile_guid = self._bookmarks_profile_guid(client)
        body = {
            "class": "NewElementRequestBody",
            "anchorGUID": profile_guid,
            "isOwnAnchor": False,
            "parentGUID": profile_guid,
            "parentRelationshipTypeName": "ResourceList",
            "parentAtEnd1": True,
            "parentRelationshipProperties": {
                "class": "ResourceListProperties",
                "resourceUse": BOOKMARKS_RESOURCE_USE,
                "resourceUseDescription": f"Private bookmarks for {self.user_name}",
                },
            "properties": {
                "class": "CollectionProperties",
                "qualifiedName": bookmarks_qualified_name(self.user_name),
                "displayName": BOOKMARKS_DISPLAY_NAME,
                "description": f"Elements bookmarked by {self.user_name} in My Profile",
                "category": BOOKMARKS_RESOURCE_USE,
                }
            }
        guid = client.create_collection(body=body)
        self.log(f"Created bookmarks collection {guid}")
        return guid

    def _bookmark_rows(self, client: Egeria, collection_guid: str) -> list[tuple[str, str, str]]:
        response = client.get_collection_members(collection_guid=collection_guid, output_format="JSON")
        rows = []
        for element in response if isinstance(response, list) else []:
            summary = element_summary(element)
            if summary.get("guid"):
                rows.append((summary["name"], summary["type"], summary["guid"]))
        return rows

    def list_my_bookmarks(self) -> list[tuple[str, str, str]] | None:
        """The user's bookmarks as (name, type, GUID) rows, or None if Egeria could not be reached."""
        client = None
        try:
            client = self._bookmarks_client()
            collection_guid = self._find_bookmarks_collection(client)
            if not collection_guid:
                return []
            return self._bookmark_rows(client, collection_guid)
        except PyegeriaException as e:
            self.log(f"Retrieving bookmarks failed: {e}")
            self.notify(f"Could not retrieve your bookmarks: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()

    def show_my_bookmarks(self, target_guid: str | None = None) -> None:
        """Show the bookmarks screen for the current user.
           target_guid, if supplied, is pre-filled as the GUID of a new bookmark."""
        bookmarks = self.list_my_bookmarks()
        if bookmarks is None:
            return
        self.push_screen(MyBookMarksScreen(bookmarks, target_guid=target_guid), callback=self.my_bookmarks_callback)

    def my_bookmarks_callback(self, result: Any) -> None:
        self.log(f"Bookmarks screen returned: {result}")

    def add_my_bookmark(self, target_guid: str) -> bool:
        """Bookmark the element with the given GUID. Returns True on success."""
        client = None
        try:
            client = self._bookmarks_client()
            collection_guid = self._get_or_create_bookmarks_collection(client)
            if target_guid in {row[2] for row in self._bookmark_rows(client, collection_guid)}:
                self.notify("That element is already bookmarked", timeout=10, severity="warning")
                return False
            client.add_to_collection(collection_guid=collection_guid, element_guid=target_guid)
            self.notify(f"Bookmarked {target_guid}", timeout=10, severity="information")
            return True
        except (PyegeriaException, ValueError) as e:
            self.log(f"Adding bookmark {target_guid} failed: {e}")
            self.notify(f"Adding the bookmark failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def get_row_guid(self, table: Any, row_key: Any) -> str | None:
        """GUID of the element shown in a table row, or None if the row doesn't identify one.

        Read from the row's GUID column; rows with only a Qualified Name column
        (e.g. Shop for Data's glossaries) are resolved to a GUID through Egeria.
        """
        if table is None or row_key is None:
            return None
        guid, qualified_name = row_identity(table, row_key)
        if guid or not qualified_name:
            return guid or None
        client = None
        try:
            client = self._bookmarks_client()
            resolved = client.get_guid_for_name(qualified_name)
            # "No elements found" is returned, rather than an exception, when nothing matches
            return resolved if isinstance(resolved, str) and resolved and "No " not in resolved else None
        except PyegeriaException as e:
            self.log(f"Looking up the GUID for {qualified_name} failed: {e}")
            return None
        finally:
            if client:
                client.close_session()

    def bookmark_table_row(self, table: Any, row_key: Any) -> bool:
        """Bookmark the element shown in a table row, found by its GUID column.

        Rows with only a Qualified Name column (e.g. Shop for Data's glossaries)
        are resolved to a GUID first. Returns True if the bookmark was added.
        """
        guid = self.get_row_guid(table, row_key)
        if not guid:
            self.notify("That row doesn't identify an Egeria element, so it can't be bookmarked",
                        timeout=10, severity="warning")
            return False
        return self.add_my_bookmark(guid)

    def delete_my_bookmark(self, target_guid: str) -> bool:
        """Remove the element with the given GUID from the user's bookmarks. Returns True on success."""
        client = None
        try:
            client = self._bookmarks_client()
            collection_guid = self._find_bookmarks_collection(client)
            if not collection_guid:
                self.notify("You have no bookmarks to remove", timeout=10, severity="warning")
                return False
            client.remove_from_collection(collection_guid=collection_guid, element_guid=target_guid)
            self.notify(f"Removed bookmark {target_guid}", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            self.log(f"Removing bookmark {target_guid} failed: {e}")
            self.notify(f"Removing the bookmark failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

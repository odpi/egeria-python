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
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from pyegeria import Egeria, PyegeriaException
from pyegeria.core._exceptions import PyegeriaNotFoundException
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.paging import Exists
from MyBookMarksScreen import MyBookMarksScreen
from paging_support import (LookupUnconfirmed, PagedRows, UniqueName, by_unique_name, lookup, paged_rows, read_all,
                            refusal, unique_refusal)
from profile_utils import element_summary, row_identity

BOOKMARKS_DISPLAY_NAME = "My Bookmarks"
BOOKMARKS_RESOURCE_USE = "Bookmarks"
ROW_HAS_NO_IDENTITY = "That row doesn't identify an Egeria element"



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

    def _find_bookmarks_collection(self, client: Egeria) -> UniqueName:
        """Whether the user's bookmarks collection exists, by Egeria's exact unique-name read of its qualified
        name: found (``.guid``), absent (Egeria's specific not-found) or unknown (any other answer or error)."""
        return by_unique_name(client, bookmarks_qualified_name(self.user_name), "Collection")

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
        """The bookmarks collection's GUID, created only when Egeria's unique-name read says not-found.

        Raises LookupUnconfirmed (nothing created) on any other answer: creating then could make a second
        bookmarks collection."""
        found = self._find_bookmarks_collection(client)
        if found.found:
            return found.guid
        if found.answer != "absent":
            raise LookupUnconfirmed(unique_refusal("your bookmarks collection", found))
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
        # self.log(f"Created bookmarks collection {guid}")
        return guid

    def _bookmark_rows(self, client: Egeria, collection_guid: str) -> PagedRows:
        """Every member of the bookmarks collection as (name, type, GUID) rows, paged to Egeria's end;
        ``complete`` False (and a note) when Egeria didn't confirm there are no more."""
        # Depth 0: rows show name/type/guid only (a 30s timeout at the default depth 3 vs ~0.3s).
        def fetch(start: int, size: int) -> Any:
            return client.get_collection_members(collection_guid=collection_guid, output_format="JSON",
                                                 graph_query_depth=0, start_from=start, page_size=size)

        read = read_all(fetch, method="get_collection_members", client=client)
        rows = []
        for element in read.items:
            summary = element_summary(element)
            if summary.get("guid"):
                rows.append((summary["name"], summary["type"], summary["guid"]))
        return paged_rows(rows, read, "bookmarks")

    def _is_bookmarked(self, client: Egeria, collection_guid: str, target_guid: str) -> Exists:
        """Whether target_guid is already a member of the bookmarks collection (found / absent / unknown)."""
        def fetch(start: int, size: int) -> Any:
            return client.get_collection_members(collection_guid=collection_guid, output_format="JSON",
                                                 graph_query_depth=0, start_from=start, page_size=size)

        return lookup(fetch, lambda element: element_summary(element).get("guid") == target_guid,
                      method="get_collection_members", client=client)

    def list_my_bookmarks(self) -> list[tuple[str, str, str]] | None:
        """The user's bookmarks as (name, type, GUID) rows (PagedRows: ``complete`` says whether Egeria
        confirmed that's all of them), or None if Egeria could not be reached."""
        client = None
        try:
            client = self._bookmarks_client()
            found = self._find_bookmarks_collection(client)
            if found.answer == "absent":   # Egeria's exact not-found: the user has no bookmarks collection yet
                return PagedRows([], complete=True)
            if not found.found:   # never "no bookmarks": the collection couldn't be read
                self.notify(unique_refusal("your bookmarks collection", found, "Nothing is shown"), timeout=10,
                            severity="error")
                return None
            rows = self._bookmark_rows(client, found.guid)
            if rows.note:
                self.notify(rows.note, timeout=10, severity="warning")
            return rows
        except PyegeriaException as e:
            # self.log(f"Retrieving bookmarks failed: {e}")
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
        pass
        # self.log(f"Bookmarks screen returned: {result}")

    def add_my_bookmark(self, target_guid: str) -> bool:
        """Bookmark the element with the given GUID. Returns True on success."""
        client = None
        try:
            client = self._bookmarks_client()
            collection_guid = self._get_or_create_bookmarks_collection(client)
            already = self._is_bookmarked(client, collection_guid, target_guid)
            if already.found:
                self.notify("That element is already bookmarked", timeout=10, severity="warning")
                return False
            if already.answer != "absent":
                self.notify(refusal(f"a bookmark for {target_guid}", already, "Nothing was added"),
                            timeout=10, severity="warning")
                return False
            client.add_to_collection(collection_guid=collection_guid, element_guid=target_guid)
            self.notify(f"Bookmarked {target_guid}", timeout=10, severity="information")
            return True
        except LookupUnconfirmed as e:
            self.notify(str(e), timeout=10, severity="warning")
            return False
        except (PyegeriaException, ValueError) as e:
            # self.log(f"Adding bookmark {target_guid} failed: {e}")
            self.notify(f"Adding the bookmark failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def _resolve_row(self, table: Any, row_key: Any) -> tuple[str | None, str | None]:
        """(GUID of the element shown in a table row, None) or (None, why it couldn't be had).

        Read from the row's GUID column; rows with only a Qualified Name column (e.g. Shop for Data's
        glossaries) are resolved through Egeria's exact unique-name read. A failed read is said as such,
        never as "the row doesn't identify an element"."""
        if table is None or row_key is None:
            return None, ROW_HAS_NO_IDENTITY
        guid, qualified_name = row_identity(table, row_key)
        if guid:
            return guid, None
        if not qualified_name:
            return None, ROW_HAS_NO_IDENTITY
        client = None
        try:
            client = self._bookmarks_client()
            resolved = client.get_element_guid_by_unique_name(qualified_name)
        except PyegeriaNotFoundException:
            return None, f"Egeria holds no element with the qualified name {qualified_name}"
        except PyegeriaException as e:
            # self.log(f"Looking up the GUID for {qualified_name} failed: {e}")
            return None, f"Couldn't look up the element {qualified_name} in Egeria ({type(e).__name__}); try again"
        finally:
            if client:
                client.close_session()
        if resolved == NO_ELEMENTS_FOUND:
            return None, f"Egeria holds no element with the qualified name {qualified_name}"
        if isinstance(resolved, str) and resolved:
            return resolved, None
        return None, f"Couldn't look up the element {qualified_name} in Egeria; try again"

    def get_row_guid(self, table: Any, row_key: Any) -> str | None:
        """GUID of the element shown in a table row, or None if it couldn't be had (and why is shown when
        it was a lookup in Egeria, not the row, that failed)."""
        guid, reason = self._resolve_row(table, row_key)
        if guid is None and reason and reason != ROW_HAS_NO_IDENTITY:
            self.notify(reason, timeout=10, severity="warning")
        return guid

    def bookmark_table_row(self, table: Any, row_key: Any) -> bool:
        """Bookmark the element shown in a table row, found by its GUID column.

        Rows with only a Qualified Name column (e.g. Shop for Data's glossaries)
        are resolved to a GUID first. Returns True if the bookmark was added.
        """
        guid, reason = self._resolve_row(table, row_key)
        if not guid:
            self.notify(f"{reason}, so it can't be bookmarked", timeout=10, severity="warning")
            return False
        return self.add_my_bookmark(guid)

    def delete_my_bookmark(self, target_guid: str) -> bool:
        """Remove the element with the given GUID from the user's bookmarks. Returns True on success."""
        client = None
        try:
            client = self._bookmarks_client()
            found = self._find_bookmarks_collection(client)
            if found.answer == "absent":
                self.notify("You have no bookmarks to remove", timeout=10, severity="warning")
                return False
            if not found.found:
                self.notify(unique_refusal("your bookmarks collection", found, "Nothing was removed"), timeout=10,
                            severity="warning")
                return False
            collection_guid = found.guid
            client.remove_from_collection(collection_guid=collection_guid, element_guid=target_guid)
            self.notify(f"Removed bookmark {target_guid}", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Removing bookmark {target_guid} failed: {e}")
            self.notify(f"Removing the bookmark failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

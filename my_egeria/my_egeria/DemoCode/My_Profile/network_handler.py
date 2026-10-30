"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   My Network handler mixin for My Profile Textual App.

   A user's network is the set of people linked to their profile by a Peer
   relationship. Peers are found with find_actor_profiles, linked with
   link_peer_person and removed with unlink_peer_person.
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
from MyNetworkScreen import MyNetworkScreen

PEER_RELATIONSHIP = "Peer"


class NetworkMixin:
    """Mixin class providing the My Network feature for MyProfileApp."""

    def _network_client(self) -> Egeria:
        client = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                        user_id=self.user_name, user_pwd=self.user_password)
        client.create_egeria_bearer_token(self.user_name, self.user_password)
        return client

    def list_my_peers(self) -> list[tuple[str, str, str, str, str, str]] | None:
        """The user's peers as (qualified name, display name, full name, pronouns, GUID, description) rows,
           or None if Egeria could not be reached."""
        client = None
        try:
            client = self._network_client()
            body = {
                "class": "ResultsRequestBody",
                "metadataElementTypeName": "Referenceable",
                "includeOnlyRelationships": ["ContactThrough"],
            }
            peers = client.get_related_elements(element_guid=self.user_GUID,
                                                relationship_type=PEER_RELATIONSHIP,
                                                body=body)
        except PyegeriaException as e:
            # self.log(f"Retrieving peers failed: {e}")
            self.notify(f"Could not retrieve your network: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        # self.log(f"Peers: {peers}")
        rows = []
        # "No elements found" is returned, rather than an exception, when the user has no peers
        for peer in peers if isinstance(peers, list) else []:
            properties = peer.get("properties") or {}
            if properties.get("class") != "PersonProperties":
                continue
            # the peer's own GUID is in its elementHeader - relatedBy describes the Peer relationship
            guid = (peer.get("elementHeader") or {}).get("guid")
            if not guid:
                continue
            relationship_properties = peer.get("relationshipProperties") or {}
            rows.append((properties.get("qualifiedName") or "",
                         properties.get("displayName") or "",
                         properties.get("fullName") or "",
                         properties.get("pronouns") or "",
                         guid,
                         relationship_properties.get("description") or ""))
        return rows

    def show_my_network(self) -> None:
        """Show the My Network screen for the current user."""
        if not getattr(self, "user_GUID", ""):
            self.notify("Your profile has not loaded yet, so your network can't be shown", timeout=10,
                        severity="warning")
            return
        peers = self.list_my_peers()
        if peers is None:
            return
        self.push_screen(MyNetworkScreen(peers), callback=self.my_network_callback)

    def my_network_callback(self, result: Any) -> None:
        pass
        # self.log(f"My Network screen returned: {result}")

    def search_people(self, search_string: str) -> list[tuple[str, str, str]] | None:
        """People whose profile matches search_string, as (display name, GUID, qualified name) rows,
           or None if Egeria could not be reached."""
        client = None
        try:
            client = self._network_client()
            found = client.find_actor_profiles(search_string=search_string, ignore_case=True,
                                               output_format="DICT", report_spec="User-Identities",
                                               query_depth=0, page_size=10)
        except PyegeriaException as e:
            # self.log(f"Searching for {search_string} failed: {e}")
            self.notify(f"Searching for people failed: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        # self.log(f"People found for {search_string}: {found}")
        if isinstance(found, dict):
            found = [found]
        rows = []
        for person in found if isinstance(found, list) else []:
            guid = person.get("GUID")
            # the current user can't be their own peer
            if guid and guid != self.user_GUID:
                rows.append((person.get("Display Name") or "", guid, person.get("Qualified Name") or ""))
        return rows

    def link_peer(self, peer_guid: str, nickname: str = "", description: str = "") -> bool:
        """Add the person with the given GUID to the user's network. Returns True on success."""
        body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "PeerProperties",
                "peer_relationship_name": nickname,
                "description": description,
                "effective_from": None,
                "effective_to": None,
            }
        }
        client = None
        try:
            client = self._network_client()
            client.link_peer_person(self.user_GUID, peer_guid, body)
            self.notify("Added to your network", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Linking peer {peer_guid} failed: {e}")
            self.notify(f"Adding to your network failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def unlink_peer(self, peer_guid: str) -> bool:
        """Remove the person with the given GUID from the user's network. Returns True on success."""
        client = None
        try:
            client = self._network_client()
            # same GUID order as link_peer_person: owner first, peer second
            client.unlink_peer_person(self.user_GUID, peer_guid, {"class": "DeleteRelationshipRequestBody"})
            self.notify("Removed from your network", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Unlinking peer {peer_guid} failed: {e}")
            self.notify(f"Removing from your network failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def get_peer_details(self, peer_guid: str) -> tuple[list[dict], list[dict]] | None:
        """The peer's (contact methods, communities), or None if they could not be retrieved."""
        client = None
        try:
            client = self._network_client()
            profile = client.get_actor_profile_by_guid(peer_guid, output_format="JSON")
            # My-User's detail specs are My-User-Contact-Detail / My-User-Communities-Detail
            details = client._generate_my_profile_output(profile, output_format="DICT", report_spec="My-User")
        except PyegeriaException as e:
            # self.log(f"Retrieving details for peer {peer_guid} failed: {e}")
            self.notify(f"Could not retrieve the details: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        # self.log(f"Peer details: {details}")
        if isinstance(details, list) and details:
            details = details[0]
        if not isinstance(details, dict):
            self.notify("No profile details found", timeout=10, severity="warning")
            return None
        return details.get("Contact Methods") or [], details.get("Communities") or []

"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for the My Network mixin and screen (a user's network is the people
   linked to their profile by a Peer relationship).
"""

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import DataTable, Input, Button

from network_handler import NetworkMixin
from MyNetworkScreen import MyNetworkScreen, ConfirmRemovePeerScreen
from pyegeria import PyegeriaException


def _peer(guid, display_name, description="", type_class="PersonProperties"):
    return {"elementHeader": {"guid": guid},
            "properties": {"class": type_class, "qualifiedName": f"Person::{guid}", "displayName": display_name,
                           "fullName": f"{display_name} Full", "pronouns": "they/them"},
            "relatedBy": {"relationshipHeader": {"guid": f"rel-{guid}"}},
            "relationshipProperties": {"description": description}}


class DummyApp(NetworkMixin):
    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.user_GUID = "profile-guid"
        self.notices = []
        self.pushed = []

    def log(self, *args, **kwargs):
        pass

    def notify(self, message, **kwargs):
        self.notices.append((message, kwargs.get("severity")))

    def push_screen(self, screen, callback=None):
        self.pushed.append((screen, callback))


@pytest.fixture
def client():
    with patch("network_handler.Egeria") as mock_egeria:
        yield mock_egeria.return_value


class TestNetworkMixin:
    def test_list_returns_peer_rows_with_person_guid(self, client):
        client.get_related_elements.return_value = [
            _peer("erin-guid", "Erin", "Governance buddy"),
            _peer("thing-guid", "Not a person", type_class="AssetProperties"),
        ]
        rows = DummyApp().list_my_peers()
        assert client.get_related_elements.call_args.kwargs["element_guid"] == "profile-guid"
        assert client.get_related_elements.call_args.kwargs["relationship_type"] == "Peer"
        # The person's own GUID, not the relationship's; non-people are skipped
        assert rows == [("Person::erin-guid", "Erin", "Erin Full", "they/them", "erin-guid", "Governance buddy")]
        client.close_session.assert_called_once()

    def test_list_without_peers_is_empty(self, client):
        client.get_related_elements.return_value = "No elements found"
        assert DummyApp().list_my_peers() == []

    def test_list_error_returns_none(self, client):
        client.get_related_elements.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.list_my_peers() is None
        assert app.notices[-1][1] == "error"

    def test_show_pushes_screen(self, client):
        client.get_related_elements.return_value = [_peer("erin-guid", "Erin")]
        app = DummyApp()
        app.show_my_network()
        screen, callback = app.pushed[-1]
        assert isinstance(screen, MyNetworkScreen)
        assert screen.my_peers_data[0][4] == "erin-guid"

    def test_show_without_profile_is_refused(self, client):
        app = DummyApp()
        app.user_GUID = ""
        app.show_my_network()
        assert app.pushed == []
        client.get_related_elements.assert_not_called()
        assert app.notices[-1][1] == "warning"

    def test_search_excludes_current_user(self, client):
        client.find_actor_profiles.return_value = [
            {"Display Name": "Tanya", "GUID": "tanya-guid", "Qualified Name": "Person::tanya"},
            {"Display Name": "Gary", "GUID": "profile-guid", "Qualified Name": "Person::gary"},
        ]
        assert DummyApp().search_people("a") == [("Tanya", "tanya-guid", "Person::tanya")]

    def test_search_single_result_dict(self, client):
        client.find_actor_profiles.return_value = {"Display Name": "Tanya", "GUID": "tanya-guid",
                                                   "Qualified Name": "Person::tanya"}
        assert DummyApp().search_people("tan") == [("Tanya", "tanya-guid", "Person::tanya")]

    def test_search_error_returns_none(self, client):
        client.find_actor_profiles.side_effect = PyegeriaException("boom")
        assert DummyApp().search_people("tan") is None

    def test_link_peer(self, client):
        assert DummyApp().link_peer("tanya-guid", "Tan", "Met at the summit") is True
        owner, peer, body = client.link_peer_person.call_args.args
        assert (owner, peer) == ("profile-guid", "tanya-guid")
        assert body["properties"]["class"] == "PeerProperties"
        assert body["properties"]["peer_relationship_name"] == "Tan"
        assert body["properties"]["description"] == "Met at the summit"

    def test_link_peer_error(self, client):
        client.link_peer_person.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.link_peer("tanya-guid") is False
        assert app.notices[-1][1] == "error"

    def test_unlink_peer(self, client):
        assert DummyApp().unlink_peer("erin-guid") is True
        client.unlink_peer_person.assert_called_once_with(
            "profile-guid", "erin-guid", {"class": "DeleteRelationshipRequestBody"})

    def test_unlink_peer_error(self, client):
        client.unlink_peer_person.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.unlink_peer("erin-guid") is False
        assert app.notices[-1][1] == "error"

    def test_peer_details(self, client):
        client._generate_my_profile_output.return_value = [
            {"Contact Methods": [{"name": "Work email"}], "Communities": [{"name": "Council"}]}]
        assert DummyApp().get_peer_details("erin-guid") == ([{"name": "Work email"}], [{"name": "Council"}])
        client.get_actor_profile_by_guid.assert_called_once_with("erin-guid", output_format="JSON")

    def test_peer_details_missing(self, client):
        client._generate_my_profile_output.return_value = "No elements found"
        app = DummyApp()
        assert app.get_peer_details("erin-guid") is None
        assert app.notices[-1][1] == "warning"


PEER_ROWS = [("Person::erin", "Erin", "Erin Full", "she/her", "erin-guid", "Governance buddy"),
             ("Person::peter", "Peter", "Peter Full", "he/him", "peter-guid", "")]


class NetworkHostApp(App):
    """Host app standing in for MyProfileApp's network methods."""

    def __init__(self, rows):
        super().__init__()
        self.rows = list(rows)
        self.link_peer = MagicMock(side_effect=self._link)
        self.unlink_peer = MagicMock(side_effect=self._unlink)
        self.search_people = MagicMock(return_value=[("Tanya", "tanya-guid", "Person::tanya"),
                                                     ("Erin", "erin-guid", "Person::erin")])
        self.get_peer_details = MagicMock(return_value=([{"name": "Work email"}], [{"name": "Council"}]))
        self.dismissed = None

    def _link(self, guid, nickname="", description=""):
        self.rows.append(("Person::new", "New", "", "", guid, description))
        return True

    def _unlink(self, guid):
        self.rows = [r for r in self.rows if r[4] != guid]
        return True

    def list_my_peers(self):
        return list(self.rows)

    async def on_mount(self):
        self.screen_under_test = MyNetworkScreen(list(self.rows))
        await self.push_screen(self.screen_under_test, callback=lambda r: setattr(self, "dismissed", r))


class TestMyNetworkScreen:
    @pytest.mark.asyncio
    async def test_lists_peers(self):
        app = NetworkHostApp(PEER_ROWS)
        async with app.run_test():
            table = app.screen_under_test.query_one("#my_network_table", DataTable)
            assert table.row_count == 2
            assert table.get_row_at(0) == list(PEER_ROWS[0])
            assert app.screen_under_test.query_one("#peer_details_container").display is False

    @pytest.mark.asyncio
    async def test_view_details_of_highlighted_peer(self):
        app = NetworkHostApp(PEER_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#my_network_table", DataTable).move_cursor(row=1)
            screen.action_view_details()
            await pilot.pause()
            app.get_peer_details.assert_called_once_with("peter-guid")
            assert screen.query_one("#peer_details_container").display is True
            assert screen.query_one("#peer_contacts_table", DataTable).row_count == 1
            assert screen.query_one("#peer_communities_table", DataTable).row_count == 1

    @pytest.mark.asyncio
    async def test_remove_asks_for_confirmation(self):
        app = NetworkHostApp(PEER_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_remove_peer()
            await pilot.pause()
            assert isinstance(app.screen, ConfirmRemovePeerScreen)
            app.screen.query_one("#cancel_remove_peer_btn", Button).press()
            await pilot.pause()
            app.unlink_peer.assert_not_called()
            assert screen.query_one("#my_network_table", DataTable).row_count == 2

    @pytest.mark.asyncio
    async def test_remove_confirmed_hides_that_peers_details(self):
        app = NetworkHostApp(PEER_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_view_details()
            await pilot.pause()
            screen.action_remove_peer()
            await pilot.pause()
            app.screen.query_one("#confirm_remove_peer_btn", Button).press()
            await pilot.pause()
            app.unlink_peer.assert_called_once_with("erin-guid")
            assert screen.query_one("#my_network_table", DataTable).row_count == 1
            assert screen.query_one("#peer_details_container").display is False

    @pytest.mark.asyncio
    async def test_remove_with_empty_network(self):
        app = NetworkHostApp([])
        async with app.run_test() as pilot:
            app.screen_under_test.action_remove_peer()
            await pilot.pause()
            assert app.screen is app.screen_under_test

    @pytest.mark.asyncio
    async def test_search_and_add_peer(self):
        app = NetworkHostApp(PEER_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            search = screen.query_one("#people_search_input", Input)
            search.value = "a"
            await search.action_submit()
            await pilot.pause()
            found = screen.query_one("#people_found_table", DataTable)
            # Erin is already in the network so isn't offered again
            assert found.row_count == 1
            found.focus()
            await pilot.press("enter")
            await pilot.pause()
            screen.query_one("#peer_description_input", Input).value = "Met at the summit"
            screen.query_one("#add_peer_btn", Button).press()
            await pilot.pause()
            app.link_peer.assert_called_once_with("tanya-guid", "", "Met at the summit")
            assert screen.query_one("#my_network_table", DataTable).row_count == 3
            assert found.row_count == 0

    @pytest.mark.asyncio
    async def test_quit(self):
        app = NetworkHostApp([])
        async with app.run_test() as pilot:
            app.screen_under_test.action_quit()
            await pilot.pause()
            assert app.dismissed == 200

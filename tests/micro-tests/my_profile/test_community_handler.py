"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for the Work with Communities mixin and screens (a user belongs to a
   community when their profile, or a role they hold, is linked to it by an
   AssignmentScope relationship; a community has a blog note log and comments).
"""

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import DataTable, Input, Button, Select, Static, TextArea

import community_handler
from community_handler import CommunitiesMixin
from CommunitiesScreen import (CommunitiesScreen, ConfirmLeaveCommunityScreen, CreateCommunityScreen, DIRECT_LINK,
                               NOT_JOINING)
from CommunityScreen import CommunityScreen, NewBlogPostScreen, AddCommunityCommentScreen
from pyegeria import PyegeriaException


def _element(guid, type_name, display_name, description=""):
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
            "properties": {"displayName": display_name, "qualifiedName": f"{type_name}::{guid}",
                           "description": description}}


def _created(element, by, at):
    element["elementHeader"]["versions"] = {"createdBy": by, "createTime": at}
    return element


def _scope(element, assignment_type):
    return {"relationshipHeader": {"guid": f"rel-{element['elementHeader']['guid']}"},
            "relationshipProperties": {"class": "AssignmentScopeProperties", "assignmentType": assignment_type},
            "relatedElement": element}


# The people appointed to each role, as get_actor_role_by_guid returns them, by role GUID
ROLE_PERFORMERS: dict[str, dict] = {}


def _role(guid, type_name, display_name, people):
    """A role actor (whose type header lists its supertypes) appointed to the given people."""
    role = _element(guid, type_name, display_name)
    supertypes = ["ActorRole", "Actor", "Referenceable", "OpenMetadataRoot"]
    if type_name == "GovernanceRole":
        supertypes.insert(0, "PersonRole")
    role["elementHeader"]["type"]["superTypeNames"] = supertypes
    ROLE_PERFORMERS[guid] = {**role, "rolePerformers": [{"relatedElement": person} for person in people]}
    return role


DATA_SCI = _element("ds-guid", "Community", "Data Science SIG", "Data science")
SUSTAIN = _element("sus-guid", "Community", "Sustainability Community", "Green IT")

PROFILE = {
    "elementHeader": {"guid": "profile-guid"},
    "assignmentScope": [
        _scope(DATA_SCI, "Contributor"),
        _scope(_element("proj-guid", "Project", "A project"), "Owner"),  # not a community
    ],
    "performsRoles": [
        {"relatedElement": _element("dc-role", "GovernanceRole", "DC Leader"),
         "nestedElements": [_scope(SUSTAIN, "Contributor")]},
        {"relatedElement": _element("champ-role", "GovernanceRole", "IT Champion"),
         "nestedElements": [_scope(SUSTAIN, "Contributor"),
                            _scope(_element("loc-guid", "Location", "London"), None)]},
        {"relatedElement": _element("tester-role", "PersonRole", "Tester")},
    ],
}


class DummyApp(CommunitiesMixin):
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
    with patch("community_handler.Egeria") as mock_egeria:
        # MagicMock doesn't create dunder-named attributes on demand
        mock_egeria.return_value.__create_qualified_name__ = MagicMock(
            side_effect=lambda type_name, name: f"{type_name}::{name.replace(' ', '-')}")
        yield mock_egeria.return_value


class TestCommunitiesMixin:
    def test_list_merges_direct_and_role_memberships(self, client):
        client.get_my_profile.return_value = PROFILE
        rows = DummyApp().list_my_communities()
        client.get_my_profile.assert_called_once_with(output_format="JSON")
        # One row per community; non-communities are skipped
        assert rows == [
            ("Data Science SIG", "Contributor", DIRECT_LINK, "Data science", "ds-guid"),
            ("Sustainability Community", "Contributor", "Role: DC Leader; Role: IT Champion", "Green IT", "sus-guid"),
        ]
        client.close_session.assert_called_once()

    def test_list_without_profile_is_empty(self, client):
        client.get_my_profile.return_value = "No elements found"
        assert DummyApp().list_my_communities() == []

    def test_list_error_returns_none(self, client):
        client.get_my_profile.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.list_my_communities() is None
        assert app.notices[-1][1] == "error"

    def test_show_pushes_screen(self, client):
        client.get_my_profile.return_value = PROFILE
        app = DummyApp()
        app.show_communities()
        screen, callback = app.pushed[-1]
        assert isinstance(screen, CommunitiesScreen)
        assert screen.my_communities_data[0][4] == "ds-guid"

    def test_show_without_profile_is_refused(self, client):
        app = DummyApp()
        app.user_GUID = ""
        app.show_communities()
        assert app.pushed == []
        client.get_my_profile.assert_not_called()
        assert app.notices[-1][1] == "warning"

    def test_search(self, client):
        client.find_communities.return_value = [DATA_SCI, SUSTAIN]
        rows = DummyApp().search_communities("*")
        assert client.find_communities.call_args.kwargs["search_string"] == "*"
        assert rows == [("Data Science SIG", "Data science", "Community::ds-guid", "ds-guid"),
                        ("Sustainability Community", "Green IT", "Community::sus-guid", "sus-guid")]

    def test_empty_search_means_all(self, client):
        client.find_communities.return_value = "No elements found"
        assert DummyApp().search_communities("") == []
        assert client.find_communities.call_args.kwargs["search_string"] == "*"

    def test_search_error_returns_none(self, client):
        client.find_communities.side_effect = PyegeriaException("boom")
        assert DummyApp().search_communities("sig") is None

    def test_members_are_people_direct_and_through_roles(self, client):
        gary, erin = _element("gary-guid", "Person", "Gary"), _element("erin-guid", "Person", "Erin")
        lead_role = _role("lead-role", "PersonRole", "SIG Leader", [erin, gary])
        champ_role = _role("champ-role", "GovernanceRole", "SIG Champion", [erin])
        client.get_community_by_guid.return_value = {
            "assignedActors": [_scope(gary, "Contributor"),
                               _scope(lead_role, "Leader"),
                               _scope(champ_role, "Contributor"),
                               _scope(_element("team-guid", "Team", "A team"), "Observer")]}
        client.get_actor_role_by_guid.side_effect = lambda guid, **kwargs: ROLE_PERFORMERS[guid]
        rows = DummyApp().get_community_members("ds-guid")
        assert client.get_community_by_guid.call_args.args == ("ds-guid",)
        # Only the role's appointments are fetched
        assert client.get_actor_role_by_guid.call_args.kwargs["include_only_relationships"] == [
            "PersonRoleAppointment"]
        # One row per person, sorted by name; roles and teams aren't listed
        assert rows == [
            ("Erin", "Leader, Contributor", "Role: SIG Leader; Role: SIG Champion", "Person::erin-guid", "erin-guid"),
            ("Gary", "Contributor, Leader", "Direct; Role: SIG Leader", "Person::gary-guid", "gary-guid"),
        ]
        client.close_session.assert_called_once()

    def test_unreadable_role_is_skipped_with_a_warning(self, client):
        gary = _element("gary-guid", "Person", "Gary")
        client.get_community_by_guid.return_value = {
            "assignedActors": [_scope(gary, "Contributor"),
                               _scope(_role("lead-role", "PersonRole", "SIG Leader", []), "Leader")]}
        client.get_actor_role_by_guid.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert [row[4] for row in app.get_community_members("ds-guid")] == ["gary-guid"]
        assert app.notices[-1][1] == "warning"

    def test_members_error_returns_none(self, client):
        client.get_community_by_guid.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.get_community_members("ds-guid") is None
        assert app.notices[-1][1] == "error"

    def test_join(self, client):
        assert DummyApp().join_community("ds-guid", "Observer") is True
        scope, actor, body = client.link_assignment_scope.call_args.args
        # The community is the scope, the user's profile the actor
        assert (scope, actor) == ("ds-guid", "profile-guid")
        assert body["properties"] == {"class": "AssignmentScopeProperties", "assignmentType": "Observer"}

    def test_join_error(self, client):
        client.link_assignment_scope.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.join_community("ds-guid") is False
        assert app.notices[-1][1] == "error"

    def test_create_and_lead(self, client):
        client.create_community.return_value = "new-guid"
        app = DummyApp()
        assert app.create_community("Data Lovers", "People who love data", "Love data") == "new-guid"
        client.__create_qualified_name__.assert_called_once_with("Community", "Data Lovers")
        body = client.create_community.call_args.kwargs["body"]
        assert body["class"] == "NewElementRequestBody"
        assert body["properties"] == {"class": "CommunityProperties", "typeName": "Community",
                                      "qualifiedName": "Community::Data-Lovers", "displayName": "Data Lovers",
                                      "description": "People who love data", "mission": "Love data"}
        # The creator leads the new community by default
        scope, actor, link_body = client.link_assignment_scope.call_args.args
        assert (scope, actor) == ("new-guid", "profile-guid")
        assert link_body["properties"]["assignmentType"] == "Leader"
        assert app.notices[-1][1] == "information"
        client.close_session.assert_called_once()

    def test_create_without_mission_or_joining(self, client):
        client.create_community.return_value = "new-guid"
        assert DummyApp().create_community("Data Lovers", "People who love data", "", "") == "new-guid"
        assert "mission" not in client.create_community.call_args.kwargs["body"]["properties"]
        client.link_assignment_scope.assert_not_called()

    def test_create_refuses_an_existing_name(self, client):
        client.get_communities_by_name.return_value = [DATA_SCI]
        app = DummyApp()
        assert app.create_community("Data Science SIG", "Again") is None
        assert client.get_communities_by_name.call_args.kwargs["filter_string"] == "Community::Data-Science-SIG"
        client.create_community.assert_not_called()
        assert app.notices[-1] == ("A community called Data Science SIG already exists - find it below to join it",
                                   "warning")
        client.close_session.assert_called_once()

    def test_create_error(self, client):
        client.create_community.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.create_community("Data Lovers", "People who love data") is None
        client.link_assignment_scope.assert_not_called()
        assert app.notices[-1][1] == "error"
        client.close_session.assert_called_once()

    def test_create_with_failed_join_still_returns_the_community(self, client):
        client.create_community.return_value = "new-guid"
        client.link_assignment_scope.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.create_community("Data Lovers", "People who love data") == "new-guid"
        assert app.notices[-1][1] == "warning"
        client.close_session.assert_called_once()

    def test_leave(self, client):
        assert DummyApp().leave_community("ds-guid") is True
        client.detach_assignment_scope.assert_called_once_with(
            "ds-guid", "profile-guid", {"class": "DeleteRelationshipRequestBody"})

    def test_leave_error(self, client):
        client.detach_assignment_scope.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.leave_community("ds-guid") is False
        assert app.notices[-1][1] == "error"

    def test_blog_posts_from_every_attached_log_newest_first(self, client):
        client.get_attached_note_logs.return_value = [_element("blog-log", "NoteLog", "Blog"),
                                                      _element("other-log", "NoteLog", "Notifications")]
        old = _created(_element("p1", "BlogEntry", "First", "Hello"), "gary", "2026-10-01T09:00:00.000+00:00")
        new = _created(_element("p2", "BlogEntry", "Second", "Again"), "erin", "2026-10-20T13:27:27.750+00:00")
        client.get_notes_for_note_log.side_effect = [[old], [new]]
        rows = DummyApp().get_community_blog_posts("ds-guid")
        assert client.get_attached_note_logs.call_args.args == ("ds-guid",)
        # only blog entries are asked for, so notifications in other logs are skipped
        for call in client.get_notes_for_note_log.call_args_list:
            assert call.kwargs["metadata_element_type_name"] == "BlogEntry"
        assert rows == [("Second", "erin", "2026-10-20 13:27", "Again", "p2"),
                        ("First", "gary", "2026-10-01 09:00", "Hello", "p1")]

    def test_blog_posts_are_limited_to_the_latest(self, client):
        client.get_attached_note_logs.return_value = [_element("blog-log", "NoteLog", "Blog")]
        client.get_notes_for_note_log.return_value = [
            _created(_element(f"p{i:02}", "BlogEntry", f"Post {i}"), "gary", f"2026-10-{i:02}T09:00:00")
            for i in range(1, 26)]
        rows = DummyApp().get_community_blog_posts("ds-guid")
        assert len(rows) == community_handler.LATEST_POSTS
        assert rows[0][4] == "p25"

    def test_no_blog_yet(self, client):
        client.get_attached_note_logs.return_value = "No elements found"
        assert DummyApp().get_community_blog_posts("ds-guid") == []
        client.get_notes_for_note_log.assert_not_called()

    def test_blog_error_returns_none(self, client):
        client.get_attached_note_logs.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.get_community_blog_posts("ds-guid") is None
        assert app.notices[-1][1] == "error"

    def test_first_post_creates_the_blog(self, client):
        client.get_attached_note_logs.return_value = "No elements found"
        client.create_note_log.return_value = "new-log"
        client.make_feedback_qn.return_value = "BlogEntry::ds-guid::garygeeke::Hi::1"
        assert DummyApp().add_community_blog_post("ds-guid", "Data Science SIG", "Hi", "Hello all") is True
        body = client.create_note_log.call_args.kwargs["body"]
        assert client.create_note_log.call_args.kwargs["element_guid"] == "ds-guid"
        assert body["class"] == "NewAttachmentRequestBody"
        assert body["properties"]["qualifiedName"] == "NoteLog::ds-guid::CommunityBlog"
        log_guid = client.create_note.call_args.args[0]
        properties = client.create_note.call_args.kwargs["body"]
        assert log_guid == "new-log"
        assert properties["typeName"] == "BlogEntry"
        assert (properties["displayName"], properties["description"]) == ("Hi", "Hello all")

    def test_later_posts_reuse_the_blog(self, client):
        blog = _element("blog-log", "NoteLog", "Blog")
        blog["properties"]["qualifiedName"] = "NoteLog::ds-guid::CommunityBlog"
        client.get_attached_note_logs.return_value = [_element("other-log", "NoteLog", "Notifications"), blog]
        assert DummyApp().add_community_blog_post("ds-guid", "Data Science SIG", "Hi", "Hello") is True
        client.create_note_log.assert_not_called()
        assert client.create_note.call_args.args[0] == "blog-log"

    def test_post_error(self, client):
        client.get_attached_note_logs.return_value = "No elements found"
        client.create_note_log.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.add_community_blog_post("ds-guid", "Data Science SIG", "Hi", "Hello") is False
        client.create_note.assert_not_called()
        assert app.notices[-1][1] == "error"

    def test_comments_newest_first(self, client):
        def comment(guid, text, comment_type, at):
            element = _created(_element(guid, "Comment", ""), "gary", at)
            element["properties"].update({"description": text, "commentType": comment_type})
            return element
        client.get_attached_comments.return_value = [
            comment("c1", "Why?", "QUESTION", "2026-10-01T09:00:00"),
            comment("c2", "Because", "USAGE_EXPERIENCE", "2026-10-02T09:00:00")]
        rows = DummyApp().get_community_comments("ds-guid")
        assert client.get_attached_comments.call_args.args == ("ds-guid",)
        assert rows == [("Because", "Usage Experience", "gary", "2026-10-02 09:00", "c2"),
                        ("Why?", "Question", "gary", "2026-10-01 09:00", "c1")]

    def test_no_comments(self, client):
        client.get_attached_comments.return_value = "No elements found"
        assert DummyApp().get_community_comments("ds-guid") == []

    def test_comments_error_returns_none(self, client):
        client.get_attached_comments.side_effect = PyegeriaException("boom")
        assert DummyApp().get_community_comments("ds-guid") is None

    def test_add_comment(self, client):
        assert DummyApp().add_community_comment("ds-guid", "Nice", "SUGGESTION") is True
        client.add_comment_to_element.assert_called_once_with("ds-guid", "Nice", "SUGGESTION")

    def test_add_comment_error(self, client):
        client.add_comment_to_element.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.add_community_comment("ds-guid", "Nice", "SUGGESTION") is False
        assert app.notices[-1][1] == "error"


MY_ROWS = [("Data Science SIG", "Contributor", DIRECT_LINK, "Data science", "ds-guid"),
           ("Sustainability Community", "Contributor", "Role: DC Leader", "Green IT", "sus-guid")]
ALL_COMMUNITIES = [("Data Science SIG", "Data science", "Community::ds-guid", "ds-guid"),
                   ("Sustainability Community", "Green IT", "Community::sus-guid", "sus-guid"),
                   ("Privacy Community", "Privacy", "Community::priv-guid", "priv-guid")]


class CommunitiesHostApp(App):
    """Host app standing in for MyProfileApp's community methods."""

    def __init__(self, rows):
        super().__init__()
        self.rows = list(rows)
        self.join_community = MagicMock(side_effect=self._join)
        self.leave_community = MagicMock(side_effect=self._leave)
        self.search_communities = MagicMock(return_value=list(ALL_COMMUNITIES))
        self.get_community_members = MagicMock(return_value=[("Gary", "Contributor", "Direct", "Person::g", "g")])
        self.posts = [("Second", "erin", "2026-10-20 13:27", "Again", "p2"),
                      ("First", "gary", "2026-10-01 09:00", "Hello", "p1")]
        self.comments = [("Why?", "Question", "gary", "2026-10-01 09:00", "c1")]
        self.get_community_blog_posts = MagicMock(side_effect=lambda guid: list(self.posts))
        self.get_community_comments = MagicMock(side_effect=lambda guid: list(self.comments))
        self.add_community_blog_post = MagicMock(side_effect=self._post)
        self.add_community_comment = MagicMock(side_effect=self._comment)
        self.create_community = MagicMock(side_effect=self._create)
        self.dismissed = None

    def _create(self, name, description, mission, assignment_type):
        self.search_communities.return_value.append((name, description, f"Community::{name}", "new-guid"))
        if assignment_type:
            self.rows.append((name, assignment_type, DIRECT_LINK, description, "new-guid"))
        return "new-guid"

    def _post(self, guid, name, title, text):
        self.posts.insert(0, (title, "garygeeke", "2026-10-28 12:00", text, "p-new"))
        return True

    def _comment(self, guid, text, comment_type):
        self.comments.insert(0, (text, comment_type, "garygeeke", "2026-10-28 12:00", "c-new"))
        return True

    def _join(self, guid, assignment_type="Contributor"):
        name = next(r[0] for r in ALL_COMMUNITIES if r[3] == guid)
        self.rows.append((name, assignment_type, DIRECT_LINK, "", guid))
        return True

    def _leave(self, guid):
        self.rows = [r for r in self.rows if r[4] != guid]
        return True

    def list_my_communities(self):
        return list(self.rows)

    async def on_mount(self):
        self.screen_under_test = CommunitiesScreen(list(self.rows))
        await self.push_screen(self.screen_under_test, callback=lambda r: setattr(self, "dismissed", r))


class TestCommunitiesScreen:
    @pytest.mark.asyncio
    async def test_lists_mine_and_finds_all_others(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test():
            screen = app.screen_under_test
            assert screen.query_one("#my_communities_table", DataTable).row_count == 2
            # '*' is searched on opening, and communities the user is already in are left out
            app.search_communities.assert_called_once_with("*")
            found = screen.query_one("#communities_found_table", DataTable)
            assert found.row_count == 1
            assert found.get_row_at(0)[3] == "priv-guid"

    @pytest.mark.asyncio
    async def test_search_term(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            search = app.screen_under_test.query_one("#community_search_input", Input)
            search.value = "privacy"
            await search.action_submit()
            await pilot.pause()
            app.search_communities.assert_called_with("privacy")

    @pytest.mark.asyncio
    async def test_open_my_community(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#my_communities_table", DataTable).move_cursor(row=1)
            screen.query_one("#open_my_community_btn", Button).press()
            await pilot.pause()
            assert isinstance(app.screen, CommunityScreen)
            assert app.screen.community_guid == "sus-guid"
            app.get_community_members.assert_called_once_with("sus-guid")

    @pytest.mark.asyncio
    async def test_open_found_community(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#communities_found_table", DataTable).focus()
            await pilot.press("ctrl+o")
            await pilot.pause()
            assert isinstance(app.screen, CommunityScreen)
            assert app.screen.community_guid == "priv-guid"

    @pytest.mark.asyncio
    async def test_back_from_a_community_returns_to_the_list(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            app.screen_under_test.action_open_community()
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen is app.screen_under_test
            assert app.dismissed is None

    @pytest.mark.asyncio
    async def test_q_from_a_community_goes_to_the_main_screen(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            app.screen_under_test.action_open_community()
            await pilot.pause()
            await pilot.press("q")
            await pilot.pause()
            assert app.dismissed == 200

    @pytest.mark.asyncio
    async def test_join_with_chosen_assignment_type(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#join_assignment_type", Select).value = "Observer"
            screen.query_one("#join_community_btn", Button).press()
            await pilot.pause()
            app.join_community.assert_called_once_with("priv-guid", "Observer")
            assert screen.query_one("#my_communities_table", DataTable).row_count == 3
            assert screen.query_one("#communities_found_table", DataTable).row_count == 0

    @pytest.mark.asyncio
    async def test_join_with_nothing_found(self):
        app = CommunitiesHostApp(MY_ROWS)
        app.search_communities.return_value = []
        async with app.run_test() as pilot:
            app.screen_under_test.action_join_community()
            await pilot.pause()
            app.join_community.assert_not_called()

    @pytest.mark.asyncio
    async def test_leave_asks_for_confirmation(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_leave_community()
            await pilot.pause()
            assert isinstance(app.screen, ConfirmLeaveCommunityScreen)
            app.screen.query_one("#cancel_leave_community_btn", Button).press()
            await pilot.pause()
            app.leave_community.assert_not_called()
            assert screen.query_one("#my_communities_table", DataTable).row_count == 2

    @pytest.mark.asyncio
    async def test_leave_confirmed_offers_the_community_again(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_leave_community()
            await pilot.pause()
            app.screen.query_one("#confirm_leave_community_btn", Button).press()
            await pilot.pause()
            app.leave_community.assert_called_once_with("ds-guid")
            assert screen.query_one("#my_communities_table", DataTable).row_count == 1
            found = screen.query_one("#communities_found_table", DataTable)
            assert "ds-guid" in {found.get_row_at(i)[3] for i in range(found.row_count)}

    @pytest.mark.asyncio
    async def test_membership_through_a_role_cannot_be_left_here(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#my_communities_table", DataTable).move_cursor(row=1)
            screen.action_leave_community()
            await pilot.pause()
            assert app.screen is screen
            app.leave_community.assert_not_called()

    @pytest.mark.asyncio
    async def test_leave_with_no_communities(self):
        app = CommunitiesHostApp([])
        async with app.run_test() as pilot:
            app.screen_under_test.action_leave_community()
            await pilot.pause()
            assert app.screen is app.screen_under_test

    @pytest.mark.asyncio
    async def test_create_and_join(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.query_one("#create_community_btn", Button).press()
            await pilot.pause()
            assert isinstance(app.screen, CreateCommunityScreen)
            # The creator leads the community unless they choose otherwise
            assert app.screen.query_one("#creator_assignment_type", Select).value == "Leader"
            app.screen.query_one("#community_name_input", Input).value = "Data Lovers"
            app.screen.query_one("#community_description_input", Input).value = "People who love data"
            app.screen.query_one("#community_mission_text", TextArea).text = "Love data"
            await pilot.press("ctrl+s")
            await pilot.pause()
            assert app.screen is screen
            app.create_community.assert_called_once_with("Data Lovers", "People who love data", "Love data", "Leader")
            mine = screen.query_one("#my_communities_table", DataTable)
            assert mine.row_count == 3
            # The new community is highlighted
            assert screen.focused is mine
            assert mine.get_row_at(mine.cursor_row)[4] == "new-guid"

    @pytest.mark.asyncio
    async def test_create_without_joining(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            await pilot.press("ctrl+t")
            await pilot.pause()
            app.screen.query_one("#community_name_input", Input).value = "Data Lovers"
            app.screen.query_one("#community_description_input", Input).value = "People who love data"
            app.screen.query_one("#creator_assignment_type", Select).value = NOT_JOINING
            app.screen.query_one("#submit_create_community_btn", Button).press()
            await pilot.pause()
            app.create_community.assert_called_once_with("Data Lovers", "People who love data", "", NOT_JOINING)
            assert screen.query_one("#my_communities_table", DataTable).row_count == 2
            # ...so it is offered in the found list instead
            found = screen.query_one("#communities_found_table", DataTable)
            assert screen.focused is found
            assert found.get_row_at(found.cursor_row)[3] == "new-guid"

    @pytest.mark.asyncio
    async def test_create_needs_name_and_description(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            app.screen_under_test.action_create_community()
            await pilot.pause()
            app.screen.query_one("#community_name_input", Input).value = "Data Lovers"
            app.screen.action_submit()
            await pilot.pause()
            assert isinstance(app.screen, CreateCommunityScreen)
            app.create_community.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_create(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            app.screen_under_test.action_create_community()
            await pilot.pause()
            app.screen.query_one("#cancel_create_community_btn", Button).press()
            await pilot.pause()
            assert app.screen is app.screen_under_test
            app.create_community.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_create_leaves_the_lists_unchanged(self):
        app = CommunitiesHostApp(MY_ROWS)
        app.create_community = MagicMock(return_value=None)
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_create_community()
            await pilot.pause()
            app.screen.query_one("#community_name_input", Input).value = "Data Lovers"
            app.screen.query_one("#community_description_input", Input).value = "People who love data"
            app.screen.action_submit()
            await pilot.pause()
            assert app.screen is screen
            assert screen.query_one("#my_communities_table", DataTable).row_count == 2
            # Only the search made on opening; nothing was reloaded
            app.search_communities.assert_called_once()

    @pytest.mark.asyncio
    async def test_quit(self):
        app = CommunitiesHostApp([])
        async with app.run_test() as pilot:
            app.screen_under_test.action_quit()
            await pilot.pause()
            assert app.dismissed == 200


async def _open_community(app, pilot) -> CommunityScreen:
    app.screen_under_test.action_open_community()
    await pilot.pause()
    assert isinstance(app.screen, CommunityScreen)
    return app.screen


class TestCommunityScreen:
    @pytest.mark.asyncio
    async def test_shows_members_posts_and_comments(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            app.get_community_blog_posts.assert_called_once_with("ds-guid")
            app.get_community_comments.assert_called_once_with("ds-guid")
            assert screen.query_one("#community_members_table", DataTable).row_count == 1
            posts = screen.query_one("#community_posts_table", DataTable)
            assert [posts.get_row_at(i)[0] for i in range(posts.row_count)] == ["Second", "First"]
            assert screen.query_one("#community_comments_table", DataTable).row_count == 1
            # the highlighted post's full text is shown below the list
            assert "Again" in str(screen.query_one("#community_post_text", Static).render())

    @pytest.mark.asyncio
    async def test_highlighting_a_post_shows_its_text(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            screen.query_one("#community_posts_table", DataTable).move_cursor(row=1)
            await pilot.pause()
            assert "Hello" in str(screen.query_one("#community_post_text", Static).render())

    @pytest.mark.asyncio
    async def test_empty_blog(self):
        app = CommunitiesHostApp(MY_ROWS)
        app.posts = []
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            assert "No posts yet" in str(screen.query_one("#community_post_text", Static).render())

    @pytest.mark.asyncio
    async def test_new_blog_post(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            await pilot.press("ctrl+n")
            await pilot.pause()
            assert isinstance(app.screen, NewBlogPostScreen)
            app.screen.query_one("#blog_post_title_input", Input).value = "Hi all"
            app.screen.query_one("#blog_post_text", TextArea).text = "First post here"
            await pilot.press("ctrl+s")
            await pilot.pause()
            app.add_community_blog_post.assert_called_once_with("ds-guid", "Data Science SIG", "Hi all",
                                                                "First post here")
            assert app.screen is screen
            assert screen.query_one("#community_posts_table", DataTable).get_row_at(0)[0] == "Hi all"

    @pytest.mark.asyncio
    async def test_blog_post_needs_title_and_text(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            await _open_community(app, pilot)
            app.screen.action_new_post()
            await pilot.pause()
            app.screen.query_one("#blog_post_title_input", Input).value = "No text"
            app.screen.action_submit()
            await pilot.pause()
            assert isinstance(app.screen, NewBlogPostScreen)
            app.add_community_blog_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancel_blog_post(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            screen.query_one("#new_blog_post_btn", Button).press()
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert app.screen is screen
            app.add_community_blog_post.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_comment_from_the_comments_list(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            screen.query_one("#community_comments_table", DataTable).focus()
            await pilot.press("ctrl+n")
            await pilot.pause()
            assert isinstance(app.screen, AddCommunityCommentScreen)
            app.screen.query_one("#community_comment_type", Select).value = "SUGGESTION"
            app.screen.query_one("#community_comment_text", TextArea).text = "Meet monthly?"
            app.screen.query_one("#submit_community_comment_btn", Button).press()
            await pilot.pause()
            app.add_community_comment.assert_called_once_with("ds-guid", "Meet monthly?", "SUGGESTION")
            assert app.screen is screen
            assert screen.query_one("#community_comments_table", DataTable).row_count == 2

    @pytest.mark.asyncio
    async def test_comment_needs_text(self):
        app = CommunitiesHostApp(MY_ROWS)
        async with app.run_test() as pilot:
            await _open_community(app, pilot)
            app.screen.action_add_comment()
            await pilot.pause()
            app.screen.action_submit()
            await pilot.pause()
            assert isinstance(app.screen, AddCommunityCommentScreen)
            app.add_community_comment.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_post_leaves_the_list_unchanged(self):
        app = CommunitiesHostApp(MY_ROWS)
        app.add_community_blog_post = MagicMock(return_value=False)
        async with app.run_test() as pilot:
            screen = await _open_community(app, pilot)
            app.screen.action_new_post()
            await pilot.pause()
            app.screen.query_one("#blog_post_title_input", Input).value = "Hi"
            app.screen.query_one("#blog_post_text", TextArea).text = "Text"
            app.screen.action_submit()
            await pilot.pause()
            assert app.get_community_blog_posts.call_count == 1
            assert screen.query_one("#community_posts_table", DataTable).row_count == 2

"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for the Work with Projects mixin and screens (a user belongs to a
   project when their profile, or a role they hold, is linked to it by an
   AssignmentScope relationship; a project has a blog/note log and comments).
"""

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import DataTable, Input, Button, Select, Static, TextArea

import project_handler
from project_handler import ProjectsMixin
from ProjectsScreen import (ProjectsScreen, ConfirmLeaveProjectScreen, CreateProjectScreen, DIRECT_LINK,
                            NOT_JOINING, PROJECT_TYPES, CREATOR_ASSIGNMENT_TYPES)
from ProjectScreen import (ProjectScreen, NewProjectBlogPostScreen, AddProjectCommentScreen)
from project_handler import IN_SCOPE, LIKE_EMOJI
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


CLINICAL_TRIAL = _element("ct-guid", "Project", "Cancer Clinical Trial", "Phase 3 clinical trial")
AI_PILOT = _element("ai-guid", "Campaign", "AI Pilot Campaign", "Healthcare AI research")

PROFILE = {
    "elementHeader": {"guid": "profile-guid"},
    "assignmentScope": [
        _scope(CLINICAL_TRIAL, "Contributor"),
        _scope(_element("comm-guid", "Community", "Data Science SIG"), "Member"),  # not a project
    ],
    "performsRoles": [
        {"relatedElement": _element("lead-role", "GovernanceRole", "Research Lead"),
         "nestedElements": [_scope(AI_PILOT, "Leader")]},
        {"relatedElement": _element("champ-role", "GovernanceRole", "Trial Champion"),
         "nestedElements": [_scope(AI_PILOT, "Contributor"),
                            _scope(_element("loc-guid", "Location", "London"), None)]},
        {"relatedElement": _element("tester-role", "PersonRole", "Tester")},
    ],
}


class DummyApp(ProjectsMixin):
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

    def add_element_comment(self, element_guid: str, text: str, comment_type: str) -> bool:
        return True


@pytest.fixture
def client():
    with patch("project_handler.Egeria") as mock_egeria:
        mock_egeria.return_value.__create_qualified_name__ = MagicMock(
            side_effect=lambda type_name, name: f"{type_name}::{name.replace(' ', '-')}")
        mock_egeria.return_value.get_element_by_unique_name.return_value = "No elements found"
        yield mock_egeria.return_value


class TestProjectsMixin:
    def test_list_merges_direct_and_role_memberships(self, client):
        client.get_my_profile.return_value = PROFILE
        app = DummyApp()
        projects = app.list_my_projects()

        assert len(projects) == 2
        # AI Pilot campaign (alphabetical first)
        assert projects[0][0] == "AI Pilot Campaign"
        assert projects[0][1] == "Leader, Contributor"
        assert projects[0][2] == "Role: Research Lead; Role: Trial Champion"
        assert projects[0][3] == "Healthcare AI research"
        assert projects[0][4] == "ai-guid"

        # Cancer Clinical Trial (direct)
        assert projects[1][0] == "Cancer Clinical Trial"
        assert projects[1][1] == "Contributor"
        assert projects[1][2] == DIRECT_LINK
        assert projects[1][3] == "Phase 3 clinical trial"
        assert projects[1][4] == "ct-guid"

    def test_list_handles_empty_or_failed_profile(self, client):
        app = DummyApp()
        client.get_my_profile.return_value = {}
        assert app.list_my_projects() == []

        client.get_my_profile.side_effect = PyegeriaException("Server error")
        assert app.list_my_projects() is None
        assert any("Could not retrieve your projects" in n[0] for n in app.notices)

    def test_search_projects(self, client):
        app = DummyApp()
        client.find_projects.return_value = [
            _element("proj-1", "Project", "Alpha Project", "Alpha description"),
            _element("proj-2", "Project", "Beta Project", "Beta description"),
        ]
        results = app.search_projects("Project")
        assert len(results) == 2
        assert results[0][0] == "Alpha Project"
        assert results[0][1] == "Alpha description"
        assert results[0][3] == "proj-1"

    def test_search_projects_failure(self, client):
        app = DummyApp()
        client.find_projects.side_effect = PyegeriaException("Network Error")
        assert app.search_projects("Project") is None
        assert any("Searching for projects failed" in n[0] for n in app.notices)

    def test_get_project_members(self, client):
        app = DummyApp()
        client.get_project_by_guid.return_value = {
            "elementHeader": {"guid": "proj-1"},
            "assignedActors": [
                {"relatedElement": _element("user-1", "Person", "Gary Geeke"),
                 "relationshipProperties": {"assignmentType": "Leader"}},
            ],
            "projectTeam": [
                {"relatedElement": _element("user-2", "Person", "Callie Quartile"),
                 "relationshipProperties": {"assignmentType": "Contributor"}},
            ],
        }
        members = app.get_project_members("proj-1")
        assert len(members) == 2
        assert members[0][0] == "Callie Quartile"
        assert members[0][1] == "Contributor"
        assert members[0][2] == "Direct"
        assert members[1][0] == "Gary Geeke"
        assert members[1][1] == "Leader"

    def test_get_project_resources(self, client):
        app = DummyApp()
        client.get_project_by_guid.return_value = {
            "elementHeader": {"guid": "proj-1"},
            "resourceList": [
                {"relatedElement": _element("res-1", "DataSet", "Patient Cohort Data"),
                 "relationshipProperties": {"resourceUse": "Primary Assay"}},
            ],
            "relevantToScopes": [
                {"relatedElement": _element("res-2", "DigitalProduct", "Clinical Trial Product"),
                 "relationshipProperties": {}},
            ],
        }
        resources = app.get_project_resources("proj-1")
        assert len(resources) == 2
        assert resources[0][0] == "Clinical Trial Product"
        assert resources[0][1] == "DigitalProduct"
        assert resources[0][2] == IN_SCOPE
        assert resources[1][0] == "Patient Cohort Data"
        assert resources[1][2] == "Resource: Primary Assay"

    def test_get_project_blog_posts(self, client):
        app = DummyApp()
        client.get_attached_note_logs.return_value = [
            _element("log-1", "NoteLog", "Project Blog")
        ]
        post_elem = _created(_element("post-1", "BlogEntry", "Milestone 1 Reached", "Completed initial assay"),
                             "garygeeke", "2026-11-18T08:00:00.000+00:00")
        client.get_notes_for_note_log.return_value = [post_elem]

        posts = app.get_project_blog_posts("proj-1")
        assert len(posts) == 1
        assert posts[0][0] == "Milestone 1 Reached"
        assert posts[0][1] == "garygeeke"
        assert posts[0][2] == "2026-11-18 08:00"
        assert posts[0][3] == "Completed initial assay"
        assert posts[0][4] == "post-1"

    def test_add_project_blog_post(self, client):
        app = DummyApp()
        client.get_attached_note_logs.return_value = [
            _element("log-1", "NoteLog", "Project Blog")
        ]
        client.get_element_by_unique_name.return_value = {
            "elementHeader": {"guid": "log-1", "type": {"typeName": "NoteLog"}}
        }
        client.create_note.return_value = "post-new-guid"

        success = app.add_project_blog_post("proj-1", "Cancer Trial", "Assay Complete", "Full report attached")
        assert success is True
        assert any("Your post 'Assay Complete' has been added" in n[0] for n in app.notices)

    def test_get_and_add_project_comments(self, client):
        app = DummyApp()
        comment_elem = _created(_element("comm-1", "Comment", "Review", "Looks good"),
                                "tessatube", "2026-11-18T08:15:00.000+00:00")
        comment_elem["properties"]["commentType"] = "STANDARD_COMMENT"
        client.get_attached_comments.return_value = [comment_elem]

        comments = app.get_project_comments("proj-1")
        assert len(comments) == 1
        assert comments[0][0] == "Looks good"
        assert comments[0][2] == "tessatube"

        client.add_comment_to_element.return_value = "comm-2-guid"
        assert app.add_project_comment("proj-1", "Great progress", "QUESTION") is True

    def test_create_project(self, client):
        app = DummyApp()
        client.get_element_by_unique_name.return_value = "No elements found"
        client.create_project.return_value = "new-proj-guid"
        client.link_assignment_scope.return_value = "rel-guid"

        guid = app.create_project("New Trial", "Trial Description", "Goal 1", "Leader", "Project")
        assert guid == "new-proj-guid"
        assert getattr(app, "projects_changed", False) is True

    def test_join_and_leave_project(self, client):
        app = DummyApp()
        client.link_assignment_scope.return_value = "rel-guid"
        assert app.join_project("proj-1", "Contributor") is True
        assert getattr(app, "projects_changed", False) is True

        client.detach_assignment_scope.return_value = None
        assert app.leave_project("proj-1") is True
        assert any("You have left the project" in n[0] for n in app.notices)


ALL_PROJECTS = [
    ("Alpha Project", "Alpha description", "Project::alpha", "proj-1"),
    ("Beta Project", "Beta description", "Project::beta", "proj-2"),
    ("Privacy Review", "Privacy project", "Project::privacy", "proj-3"),
]
MY_PROJECT_ROWS = [
    ("Alpha Project", "Leader", DIRECT_LINK, "Alpha description", "proj-1"),
    ("Beta Project", "Contributor", "Role: Lead", "Beta description", "proj-2"),
]


class ProjectsHostApp(App):
    def __init__(self, rows=(), focus_search=False):
        super().__init__()
        self.rows = list(rows)
        self.focus_search = focus_search
        self.join_project = MagicMock(side_effect=self._join)
        self.leave_project = MagicMock(side_effect=self._leave)
        self.search_projects = MagicMock(return_value=list(ALL_PROJECTS))
        self.get_project_members = MagicMock(return_value=[("Gary", "Contributor", "Direct", "Person::g", "g")])
        self.posts = [("Second", "erin", "2026-10-20 13:27", "Again", "p2"),
                      ("First", "gary", "2026-10-01 09:00", "Hello", "p1")]
        self.comments = [("Why?", "Question", "gary", "2026-10-01 09:00", "c1")]
        self.get_project_blog_posts = MagicMock(side_effect=lambda guid: list(self.posts))
        self.get_project_comments = MagicMock(side_effect=lambda guid: list(self.comments))
        self.add_project_blog_post = MagicMock(side_effect=self._post)
        self.add_project_comment = MagicMock(side_effect=self._comment)
        self.create_project = MagicMock(side_effect=self._create)
        self.user_GUID = "g"
        self.resources = [("Software Servers", "DigitalProduct", IN_SCOPE, "Servers", "r1"),
                          ("Runbook", "ExternalReference", "Resource: Guidance", "How to", "r2")]
        self.get_project_resources = MagicMock(side_effect=lambda guid: list(self.resources))
        self.dismissed = None

    def _create(self, name, description, mission, assignment_type, project_type="Project"):
        self.search_projects.return_value.append((name, description, f"Project::{name}", "new-guid"))
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
        name = next(r[0] for r in ALL_PROJECTS if r[3] == guid)
        self.rows.append((name, assignment_type, DIRECT_LINK, "", guid))
        return True

    def _leave(self, guid):
        self.rows = [r for r in self.rows if r[4] != guid]
        return True

    def list_my_projects(self):
        return list(self.rows)

    async def on_mount(self):
        self.screen_under_test = ProjectsScreen(list(self.rows), focus_search=self.focus_search)
        await self.push_screen(self.screen_under_test, callback=lambda r: setattr(self, "dismissed", r))


class TestProjectsScreens:
    @pytest.mark.asyncio
    async def test_projects_screen_composition_and_tables(self):
        app = ProjectsHostApp(MY_PROJECT_ROWS)
        async with app.run_test():
            screen = app.screen_under_test
            my_table = screen.query_one("#my_projects_table", DataTable)
            assert my_table.row_count == 2

            found_table = screen.query_one("#projects_found_table", DataTable)
            assert found_table.row_count == 1
            assert found_table.get_row_at(0)[3] == "proj-3"

    @pytest.mark.asyncio
    async def test_search_term(self):
        app = ProjectsHostApp(MY_PROJECT_ROWS)
        async with app.run_test() as pilot:
            search = app.screen_under_test.query_one("#project_search_input", Input)
            search.value = "privacy"
            await search.action_submit()
            await pilot.pause()
            app.search_projects.assert_called_with("privacy")

    @pytest.mark.asyncio
    async def test_create_project_screen(self):
        screen = CreateProjectScreen()
        dismiss_val = None

        def on_dismiss(val):
            nonlocal dismiss_val
            dismiss_val = val

        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()

            screen.query_one("#project_name_input", Input).value = "Target Project"
            screen.query_one("#project_description_input", Input).value = "Project Description"
            screen.action_submit()
            await pilot.pause()

            assert dismiss_val is not None
            assert dismiss_val["name"] == "Target Project"
            assert dismiss_val["description"] == "Project Description"

    @pytest.mark.asyncio
    async def test_confirm_leave_project_screen(self):
        screen = ConfirmLeaveProjectScreen("Cancer Trial")
        dismiss_val = None

        def on_dismiss(val):
            nonlocal dismiss_val
            dismiss_val = val

        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(screen, callback=on_dismiss)
            await pilot.pause()

            screen.query_one("#submit_leave_project_btn", Button).press()
            await pilot.pause()

            assert dismiss_val is True

    @pytest.mark.asyncio
    async def test_project_screen_composition(self):
        screen = ProjectScreen("proj-1", "Test Project")
        app = ProjectsHostApp(MY_PROJECT_ROWS)

        async with app.run_test() as pilot:
            await app.push_screen(screen)
            await pilot.pause()

            assert screen.query_one("#project_posts_table", DataTable).row_count == 2
            assert screen.query_one("#project_members_table", DataTable).row_count == 1
            assert screen.query_one("#project_resources_table", DataTable).row_count == 2
            assert screen.query_one("#project_comments_table", DataTable).row_count == 1
            assert screen.is_member is True

    @pytest.mark.asyncio
    async def test_project_screen_post_modal(self):
        post_screen = NewProjectBlogPostScreen("Test Project")
        post_dismiss = None

        def on_post_dismiss(val):
            nonlocal post_dismiss
            post_dismiss = val

        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(post_screen, callback=on_post_dismiss)
            await pilot.pause()

            post_screen.query_one("#project_blog_post_title_input", Input).value = "Title 1"
            post_screen.query_one("#project_blog_post_text", TextArea).text = "Text 1"
            post_screen.action_submit()
            await pilot.pause()

            assert post_dismiss == {"title": "Title 1", "text": "Text 1"}

    @pytest.mark.asyncio
    async def test_project_screen_comment_modal(self):
        comment_screen = AddProjectCommentScreen("Test Project")
        comment_dismiss = None

        def on_comment_dismiss(val):
            nonlocal comment_dismiss
            comment_dismiss = val

        app = App()
        async with app.run_test() as pilot:
            await app.push_screen(comment_screen, callback=on_comment_dismiss)
            await pilot.pause()

            comment_screen.query_one("#project_comment_text", TextArea).text = "Comment text"
            comment_screen.action_submit()
            await pilot.pause()

            assert comment_dismiss == {"text": "Comment text", "comment_type": "STANDARD_COMMENT"}

"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Work with Projects handler mixin for My Profile Textual App.

   A person belongs to a project when an actor is linked to it by an
   AssignmentScope relationship, whose assignmentType says how they take part
   (https://egeria-project.org/types/1/0120-Assignment-Scopes/). The actor is
   either the person's own profile, or a role they are appointed to.

   Creating a project makes it with create_project and, unless the user
   chooses not to join, links their profile to it (as its Leader by default).
   Joining links the user's profile to the project with link_assignment_scope,
   and leaving removes that link with detach_assignment_scope. Memberships held
   through a role are listed but not removed here: the role may be shared, and
   changing it is a job for whoever manages the role.

   A project's blog is a NoteLog attached to the project, holding BlogEntry
   notes. The app creates the log (qualified name BLOG_LOG_QN) on the first post;
   posts are read from every note log attached to the project, so entries
   written by other tools are shown too. Comments are attached to the project
   directly.

   A project's resources are the elements it lists with ResourceList
   relationships (https://egeria-project.org/types/0/0019-More-Information/) and
   those scoped to it with ScopedBy relationships (such as datasets or deliverables
   the project looks after), as well as project dependencies. The other end of a
   ResourceList - where the project is itself someone else's resource - is not shown.

   Feedback on a blog post or a resource is its comments, likes and star ratings.
   Egeria keeps one like and one rating per user on an element: liking or rating
   again replaces the user's earlier one.
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
from paging_support import (LookupUnconfirmed, PagedRows, by_unique_name, combine, paged_rows, read_all,
                            unique_refusal)
from ProjectsScreen import ProjectsScreen, DIRECT_LINK, JOIN_ASSIGNMENT_TYPES, CREATOR_ASSIGNMENT_TYPES, PROJECT_TYPES
from ProjectScreen import ProjectScreen, comment_type_label, star_label, STAR_VALUES

PROJECT_TYPE = "Project"
PERSON_TYPE = "Person"
ROLE_TYPE = "ActorRole"
# The relationship between a role and the people appointed to it
APPOINTMENT_TYPE = "PersonRoleAppointment"
# The "Member Through" value of a person linked to a project directly, rather than through a role
MEMBER_DIRECT = "Direct"
BLOG_LOG_QN = "NoteLog::{project_guid}::ProjectBlog"
# How many of a project's most recent blog posts are listed
LATEST_POSTS = 20
# The relationships that link a project to its resources, and the "Linked As" text of a scoped element
RESOURCE_RELATIONSHIPS = ["ResourceList", "ScopedBy", "ProjectDependency", "SupportedProject"]
IN_SCOPE = "In scope"
LIKE_EMOJI = "👍"


def _type_name(element: dict) -> str:
    return ((element.get("elementHeader") or {}).get("type") or {}).get("typeName") or ""


def _is_role(element: dict) -> bool:
    """True for an ActorRole, or any of its subtypes (PersonRole, GovernanceRole, ...)."""
    element_type = (element.get("elementHeader") or {}).get("type") or {}
    return ROLE_TYPE == element_type.get("typeName") or ROLE_TYPE in (element_type.get("superTypeNames") or [])


def _is_project(element: dict) -> bool:
    """True for a Project, or any of its subtypes (Campaign, Task, StudyProject, PersonalProject, ...)."""
    element_type = (element.get("elementHeader") or {}).get("type") or {}
    type_name = element_type.get("typeName") or ""
    super_types = element_type.get("superTypeNames") or []
    return type_name in PROJECT_TYPES or PROJECT_TYPE in super_types or "Project" in type_name


def _guid(element: dict) -> str:
    return (element.get("elementHeader") or {}).get("guid") or ""


def _name(properties: dict) -> str:
    return (properties.get("displayName") or properties.get("fullName") or properties.get("identifier")
            or properties.get("name") or properties.get("qualifiedName") or "")


def _created(element: dict) -> tuple[str, str]:
    """(created by, create time) from an element's header; the time is ISO 8601 text."""
    versions = (element.get("elementHeader") or {}).get("versions") or {}
    return versions.get("createdBy") or "", str(versions.get("createTime") or "")


def _posted(create_time: str) -> str:
    """'2026-10-23T13:27:27.750+00:00' -> '2026-10-23 13:27'"""
    return create_time[:16].replace("T", " ")


class ProjectsMixin:
    """Mixin class providing the Work with Projects feature for MyProfileApp."""

    def _project_client(self) -> Egeria:
        client = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                        user_id=self.user_name, user_pwd=self.user_password)
        client.create_egeria_bearer_token(self.user_name, self.user_password)
        return client

    # --- listing and navigating ------------------------------------------------

    def list_my_projects(self) -> list[tuple[str, str, str, str, str]] | None:
        """The projects the user belongs to, as (name, assignment type, linked through, description,
           GUID) rows, or None if they could not be retrieved."""
        client = None
        try:
            client = self._project_client()
            profile = client.get_my_profile(output_format="JSON")
        except PyegeriaException as e:
            # self.log(f"Retrieving user profile for projects failed: {e}")
            self.notify(f"Could not retrieve your projects: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        if not isinstance(profile, dict):
            return []

        memberships = []
        for scope in profile.get("assignmentScope") or []:
            element = scope.get("relatedElement") or {}
            if _is_project(element):
                memberships.append((element, (scope.get("relationshipProperties") or {}).get("assignmentType") or "",
                                    DIRECT_LINK))

        for role_link in profile.get("performsRoles") or []:
            role = role_link.get("relatedElement") or {}
            role_name = _name(role.get("properties") or {})
            for scope in role_link.get("nestedElements") or []:
                element = scope.get("relatedElement") or {}
                if _is_project(element):
                    memberships.append((element,
                                        (scope.get("relationshipProperties") or {}).get("assignmentType") or "",
                                        f"Role: {role_name}"))

        projects: dict[str, dict] = {}
        for element, assignment_type, linked_through in memberships:
            guid = _guid(element)
            if not guid:
                continue
            properties = element.get("properties") or {}
            entry = projects.setdefault(guid, {"name": _name(properties),
                                               "description": properties.get("description") or "",
                                               "assignment_types": [], "linked_through": []})
            if assignment_type and assignment_type not in entry["assignment_types"]:
                entry["assignment_types"].append(assignment_type)
            if linked_through not in entry["linked_through"]:
                entry["linked_through"].append(linked_through)

        return sorted(((p["name"], ", ".join(p["assignment_types"]), "; ".join(p["linked_through"]),
                        p["description"], guid)
                       for guid, p in projects.items()), key=lambda row: row[0].lower())

    def show_projects(self, find: bool = False) -> None:
        """Open the Work with Projects screen."""
        if not self.user_GUID:
            self.notify("Please wait for your profile to load before working with projects",
                        timeout=5, severity="warning")
            return
        my_projects = self.list_my_projects()
        if my_projects is None:
            return
        self.push_screen(ProjectsScreen(my_projects, focus_search=find), callback=self.projects_callback)

    def projects_callback(self, result: Any) -> None:
        self._refresh_if_projects_changed()

    def open_project_row(self, table, row_key) -> None:
        """Open the project in a main-screen Projects row: (status_or_type, name, description, GUID)."""
        try:
            row = table.get_row(row_key)
            if len(row) == 4:
                _, name, _, guid = row
            elif len(row) >= 5:
                name, _, _, _, guid = row[:5]
            else:
                return
            if not guid:
                return
        except Exception:
            return
        self.push_screen(ProjectScreen(guid, name), callback=self.project_callback)

    def project_callback(self, result: Any) -> None:
        self._refresh_if_projects_changed()

    def _projects_changed(self) -> None:
        """Record that the user joined, left or created a project so the main screen reloads on return."""
        self.projects_changed = True

    def _refresh_if_projects_changed(self) -> None:
        if getattr(self, "projects_changed", False):
            self.projects_changed = False
            self.call_later(self.action_refresh)

    # --- finding, members, resources, blog, comments --------------------------

    def search_projects(self, search_string: str) -> list[tuple[str, str, str, str]] | None:
        """Find projects matching search_string, as (name, description, qualified name, GUID) rows,
           or None if the search could not be run."""
        client = None
        try:
            client = self._project_client()
            search = search_string or "*"

            def fetch(start: int, size: int):
                return client.find_projects(search_string=search, ignore_case=True, output_format="JSON",
                                            graph_query_depth=0, start_from=start, page_size=size)

            read = read_all(fetch, method="find_projects", client=client)
        except PyegeriaException as e:
            # self.log(f"Finding projects matching {search_string} failed: {e}")
            self.notify(f"Searching for projects failed: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()

        rows = []
        for project in read.items:
            if not isinstance(project, dict):
                continue
            properties = project.get("properties") or {}
            rows.append((_name(properties), properties.get("description") or "",
                         properties.get("qualifiedName") or "", _guid(project)))
        return paged_rows(sorted(rows, key=lambda row: row[0].lower()), read, "projects")

    def get_project_members(self, project_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The people linked to the project, as (name, assignment type, member through, qualified name,
           GUID) rows, or None if they could not be retrieved. A person linked both directly and through a
           role is one row."""
        client = None
        try:
            client = self._project_client()
            project = client.get_project_by_guid(project_guid, output_format="JSON", graph_query_depth=1)
        except PyegeriaException as e:
            # self.log(f"Retrieving the members of project {project_guid} failed: {e}")
            self.notify(f"Could not retrieve the project's members: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        if not isinstance(project, dict):
            return []

        members = []
        role_links: list[tuple[dict, str]] = []
        for link in (project.get("assignedActors") or []) + (project.get("projectTeam") or []) + (project.get("resourceListUsers") or []):
            actor = link.get("relatedElement") or {}
            assignment_type = (link.get("relationshipProperties") or {}).get("assignmentType") or ""
            if _type_name(actor) == PERSON_TYPE:
                members.append((actor, assignment_type, MEMBER_DIRECT))
            elif _is_role(actor):
                role_links.append((actor, assignment_type))

        if role_links:
            client = None
            try:
                client = self._project_client()
                for role, assignment_type in role_links:
                    role_guid = _guid(role)
                    if not role_guid:
                        continue
                    actor_role = client.get_actor_role_by_guid(role_guid, output_format="JSON", graph_query_depth=1)
                    if not isinstance(actor_role, dict):
                        continue
                    role_name = _name(role.get("properties") or {})
                    for link in actor_role.get("rolePerformers") or []:
                        person = link.get("relatedElement") or {}
                        if _type_name(person) == PERSON_TYPE:
                            members.append((person, assignment_type, f"Role: {role_name}"))
            except PyegeriaException as e:
                # self.log(f"Retrieving members through roles for project {project_guid} failed: {e}")
                self.notify(f"Could not retrieve some members through their roles: {e}", timeout=10, severity="warning")
            finally:
                if client:
                    client.close_session()

        people: dict[str, dict] = {}
        for person, assignment_type, member_through in members:
            guid = _guid(person)
            if not guid:
                continue
            properties = person.get("properties") or {}
            entry = people.setdefault(guid, {"name": _name(properties),
                                             "qualified_name": properties.get("qualifiedName") or "",
                                             "assignment_types": [], "member_through": []})
            if assignment_type and assignment_type not in entry["assignment_types"]:
                entry["assignment_types"].append(assignment_type)
            if member_through not in entry["member_through"]:
                entry["member_through"].append(member_through)
        return sorted(((p["name"], ", ".join(p["assignment_types"]), "; ".join(p["member_through"]),
                        p["qualified_name"], guid)
                       for guid, p in people.items()), key=lambda row: row[0].lower())

    def get_project_resources(self, project_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The resources linked to the project, as (name, type, linked as, description, GUID) rows,
           or None if they could not be retrieved. An element linked both ways is one row."""
        client = None
        try:
            client = self._project_client()
            project = client.get_project_by_guid(project_guid, output_format="JSON", graph_query_depth=1,
                                                 include_only_relationships=RESOURCE_RELATIONSHIPS)
        except PyegeriaException as e:
            # self.log(f"Retrieving the resources of project {project_guid} failed: {e}")
            self.notify(f"Could not retrieve the project's resources: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        if not isinstance(project, dict):
            return []

        links = []
        # resourceList is the project's own list; resourceListUsers, the other end, is left out
        for link in project.get("resourceList") or []:
            link_properties = link.get("relationshipProperties") or {}
            use = link_properties.get("resourceUse") or link_properties.get("label") or ""
            links.append((link, f"Resource: {use}" if use else "Resource"))
        links += [(link, IN_SCOPE) for link in project.get("relevantToScopes") or []]
        links += [(link, "Dependency") for link in project.get("projectDependencies") or []]
        links += [(link, "Supported Project") for link in project.get("supportedProjects") or []]

        resources: dict[str, dict] = {}
        for link, linked_as in links:
            element = link.get("relatedElement") or {}
            guid = _guid(element)
            if not guid:
                continue
            properties = element.get("properties") or {}
            entry = resources.setdefault(guid, {"name": _name(properties), "type": _type_name(element),
                                                "description": properties.get("description") or "",
                                                "linked_as": []})
            if linked_as not in entry["linked_as"]:
                entry["linked_as"].append(linked_as)
        return sorted(((r["name"], r["type"], "; ".join(r["linked_as"]), r["description"], guid)
                       for guid, r in resources.items()), key=lambda row: row[0].lower())

    def get_project_blog_posts(self, project_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The project's latest blog posts/notes, newest first, as (title, author, posted, text, GUID) rows,
           or None if they could not be retrieved."""
        client = None
        posts = []
        try:
            client = self._project_client()
            logs = self._read_note_logs(client, project_guid)
            reads = [logs]
            for log in logs.items:
                log_guid = _guid(log) if isinstance(log, dict) else ""
                if not log_guid:
                    continue

                def fetch(start: int, size: int, log_guid=log_guid):
                    return client.get_notes_for_note_log(log_guid, metadata_element_type_name="BlogEntry",
                                                         graph_query_depth=0, start_from=start, page_size=size)

                entries = read_all(fetch, method="get_notes_for_note_log", client=client)
                reads.append(entries)
                posts += [entry for entry in entries.items if isinstance(entry, dict)]
        except PyegeriaException as e:
            # self.log(f"Retrieving the blog of project {project_guid} failed: {e}")
            self.notify(f"Could not retrieve the project's blog: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        rows = []
        for post in posts:
            properties = post.get("properties") or {}
            author, create_time = _created(post)
            rows.append((create_time, (_name(properties), author, _posted(create_time),
                                       properties.get("description") or "", _guid(post))))
        rows.sort(key=lambda r: r[0], reverse=True)
        latest = [row for _, row in rows[:LATEST_POSTS]]
        if combine(*reads):   # every read reached a confirmed end
            return PagedRows(latest, complete=True)
        note = (f"Showing the newest of at least {len(rows)} posts read; Egeria didn't confirm there are no more, "
                f"so newer posts may be missing")
        self.notify(note, timeout=10, severity="warning")
        return PagedRows(latest, complete=False, note=note)

    def _read_note_logs(self, client: Egeria, project_guid: str):
        """Every note log attached to the project, paged to Egeria's end (a PageResult)."""
        def fetch(start: int, size: int):
            return client.get_attached_note_logs(project_guid, graph_query_depth=0, start_from=start,
                                                 page_size=size)

        return read_all(fetch, method="get_attached_note_logs", client=client)

    def _project_blog_log(self, client: Egeria, project_guid: str, project_name: str) -> str:
        """The GUID of the project's blog note log, which is created on first use."""
        qualified_name = BLOG_LOG_QN.format(project_guid=project_guid)
        found = by_unique_name(client, qualified_name, "NoteLog")
        if found.found:
            return found.guid
        if found.answer != "absent":
            raise LookupUnconfirmed(unique_refusal(f"a blog for {project_name}", found,
                                                   "No blog was created and nothing was posted"))
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "NoteLogProperties",
                "typeName": "NoteLog",
                "qualifiedName": qualified_name,
                "displayName": f"{project_name} Blog",
                "description": f"Blog for the team members of {project_name}.",
            }
        }
        log_guid = client.create_note_log(element_guid=project_guid, body=body)
        # self.log(f"Created blog for project {project_guid}: {log_guid}")
        return log_guid

    def add_project_blog_post(self, project_guid: str, project_name: str, title: str, text: str) -> bool:
        """Post to the project's blog, creating the blog if it doesn't exist yet. Returns True on success."""
        client = None
        try:
            client = self._project_client()
            log_guid = self._project_blog_log(client, project_guid, project_name)
            properties = {
                "class": "BlogEntryProperties",
                "typeName": "BlogEntry",
                "qualifiedName": client.make_feedback_qn("BlogEntry", project_guid, title),
                "displayName": title,
                "description": text,
            }
            post_guid = client.create_note(log_guid, body=properties)
            # self.log(f"Posted to the blog of project {project_guid}: {post_guid}")
            self.notify(f"Your post '{title}' has been added to the {project_name} blog", timeout=10,
                        severity="information")
            return True
        except LookupUnconfirmed as e:
            self.notify(str(e), timeout=10, severity="warning")
            return False
        except PyegeriaException as e:
            # self.log(f"Posting to the blog of project {project_guid} failed: {e}")
            self.notify(f"Posting to the project's blog failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    @staticmethod
    def _comment_rows(read) -> PagedRows:
        """(comment, type, author, posted, GUID) rows, newest first, from a paged read of comments"""
        rows = []
        for comment in read.items:
            if not isinstance(comment, dict):
                continue
            properties = comment.get("properties") or {}
            author, create_time = _created(comment)
            comment_type = comment_type_label(properties.get("commentType") or "")
            rows.append((create_time, (properties.get("description") or "", comment_type, author,
                                       _posted(create_time), _guid(comment))))
        rows.sort(key=lambda r: r[0], reverse=True)
        return paged_rows([row for _, row in rows], read, "comments")

    @staticmethod
    def _read_attached(client: Egeria, method: str, element_guid: str):
        """Every comment, like or rating on an element, paged to Egeria's end (a PageResult)."""
        def fetch(start: int, size: int):
            return getattr(client, method)(element_guid, graph_query_depth=0, start_from=start, page_size=size)

        return read_all(fetch, method=method, client=client)

    def get_project_comments(self, project_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The comments attached to the project, newest first, as (comment, type, author, posted, GUID) rows,
           or None if they could not be retrieved."""
        client = None
        try:
            client = self._project_client()
            read = self._read_attached(client, "get_attached_comments", project_guid)
        except PyegeriaException as e:
            # self.log(f"Retrieving the comments on project {project_guid} failed: {e}")
            self.notify(f"Could not retrieve the project's comments: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        result = self._comment_rows(read)
        if result.note:
            self.notify(result.note, timeout=10, severity="warning")
        return result

    def add_project_comment(self, project_guid: str, text: str, comment_type: str) -> bool:
        """Attach a comment to the project. Returns True on success."""
        return self.add_element_comment(project_guid, text, comment_type)

    # --- creating, joining, leaving --------------------------------------------

    def create_project(self, name: str, description: str, mission: str = "",
                       assignment_type: str = CREATOR_ASSIGNMENT_TYPES[0],
                       project_type: str = PROJECT_TYPES[0]) -> str | None:
        """Create a project, then link the user's profile to it with assignment_type (none if empty).
           Returns the new project's GUID, or None if it could not be created; a failed link still
           returns the GUID, because the project exists."""
        if project_type not in PROJECT_TYPES:
            project_type = PROJECT_TYPES[0]
        properties = {
            "class": "ProjectProperties",
            "typeName": project_type,
            "displayName": name,
            "description": description,
        }
        if mission:
            properties["plannedResults"] = mission
        client = None
        try:
            client = self._project_client()
            qualified_name = client.__create_qualified_name__(project_type, name)

            existing = by_unique_name(client, qualified_name)
            if existing.found:
                self.notify(f"A project called {name} already exists - find it below to join it",
                            timeout=10, severity="warning")
                return None
            if existing.answer != "absent":
                self.notify(unique_refusal(f"a project called {name}", existing), timeout=10, severity="warning")
                return None
            properties["qualifiedName"] = qualified_name
            project_guid = client.create_project(body={"class": "NewElementRequestBody", "isOwnAnchor": True,
                                                       "properties": properties})
            if not assignment_type:
                self.notify(f"Project {name} created", timeout=10, severity="information")
                return project_guid
            try:
                client.link_assignment_scope(project_guid, self.user_GUID, {
                    "class": "NewRelationshipRequestBody",
                    "properties": {"class": "AssignmentScopeProperties", "assignmentType": assignment_type},
                })
            except PyegeriaException as e:
                # self.log(f"Joining new project {project_guid} failed: {e}")
                self.notify(f"Project {name} created, but joining it failed: {e}", timeout=10, severity="warning")
                return project_guid
            self._projects_changed()
            self.notify(f"Project {name} created, and you have joined it as its {assignment_type}",
                        timeout=10, severity="information")
            return project_guid
        except PyegeriaException as e:
            # self.log(f"Creating project {name} failed: {e}")
            self.notify(f"Creating the project failed: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()

    def join_project(self, project_guid: str, assignment_type: str = JOIN_ASSIGNMENT_TYPES[0]) -> bool:
        """Link the user's profile to the project. Returns True on success."""
        body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "AssignmentScopeProperties",
                "assignmentType": assignment_type,
            }
        }
        client = None
        try:
            client = self._project_client()
            client.link_assignment_scope(project_guid, self.user_GUID, body)
            self._projects_changed()
            self.notify(f"You have joined the project as a {assignment_type}", timeout=10,
                        severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Joining project {project_guid} failed: {e}")
            self.notify(f"Joining the project failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def leave_project(self, project_guid: str) -> bool:
        """Remove the link between the user's profile and the project. Returns True on success."""
        client = None
        try:
            client = self._project_client()
            client.detach_assignment_scope(project_guid, self.user_GUID, {"class": "DeleteRelationshipRequestBody"})
            self._projects_changed()
            self.notify("You have left the project", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Leaving project {project_guid} failed: {e}")
            self.notify(f"Leaving the project failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

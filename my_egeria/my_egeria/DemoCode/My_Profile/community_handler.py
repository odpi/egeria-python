"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Work with Communities handler mixin for My Profile Textual App.

   A person belongs to a community when an actor is linked to it by an
   AssignmentScope relationship, whose assignmentType says how they take part
   (https://egeria-project.org/types/1/0120-Assignment-Scopes/). The actor is
   either the person's own profile, or a role they are appointed to.

   Creating a community makes it with create_community and, unless the user
   chooses not to join, links their profile to it (as its Leader by default).
   Joining links the user's profile to the community with link_assignment_scope,
   and leaving removes that link with detach_assignment_scope. Memberships held
   through a role are listed but not removed here: the role may be shared, and
   changing it is a job for whoever manages the role.

   A community's blog is a NoteLog attached to the community, holding BlogEntry
   notes. The app creates the log (qualified name BLOG_LOG_QN) on the first post;
   posts are read from every note log attached to the community, so entries
   written by other tools are shown too. Comments are attached to the community
   directly.
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
from CommunitiesScreen import CommunitiesScreen, DIRECT_LINK, JOIN_ASSIGNMENT_TYPES, CREATOR_ASSIGNMENT_TYPES
from CommunityScreen import comment_type_label

COMMUNITY_TYPE = "Community"
PERSON_TYPE = "Person"
ROLE_TYPE = "ActorRole"
# The relationship between a role and the people appointed to it
APPOINTMENT_TYPE = "PersonRoleAppointment"
# The "Member Through" value of a person linked to a community directly, rather than through a role
MEMBER_DIRECT = "Direct"
BLOG_LOG_QN = "NoteLog::{community_guid}::CommunityBlog"
# How many of a community's most recent blog posts are listed
LATEST_POSTS = 20


def _type_name(element: dict) -> str:
    return ((element.get("elementHeader") or {}).get("type") or {}).get("typeName") or ""


def _is_role(element: dict) -> bool:
    """True for an ActorRole, or any of its subtypes (PersonRole, GovernanceRole, ...)."""
    element_type = (element.get("elementHeader") or {}).get("type") or {}
    return ROLE_TYPE == element_type.get("typeName") or ROLE_TYPE in (element_type.get("superTypeNames") or [])


def _guid(element: dict) -> str:
    return (element.get("elementHeader") or {}).get("guid") or ""


def _name(properties: dict) -> str:
    # Some roles have only an identifier, such as "Community Leader of Data Science special interest group"
    return (properties.get("displayName") or properties.get("fullName") or properties.get("identifier")
            or properties.get("qualifiedName") or "")


def _created(element: dict) -> tuple[str, str]:
    """(created by, create time) from an element's header; the time is ISO 8601 text."""
    versions = (element.get("elementHeader") or {}).get("versions") or {}
    return versions.get("createdBy") or "", str(versions.get("createTime") or "")


def _posted(create_time: str) -> str:
    """'2026-10-23T13:27:27.750+00:00' -> '2026-10-23 13:27'"""
    return create_time[:16].replace("T", " ")


class CommunitiesMixin:
    """Mixin class providing the Work with Communities feature for MyProfileApp."""

    def _community_client(self) -> Egeria:
        client = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                        user_id=self.user_name, user_pwd=self.user_password)
        client.create_egeria_bearer_token(self.user_name, self.user_password)
        return client

    def list_my_communities(self) -> list[tuple[str, str, str, str, str]] | None:
        """The user's communities as (name, assignment type, linked through, description, GUID) rows,
           or None if Egeria could not be reached. A community reached through several links is one row."""
        client = None
        try:
            client = self._community_client()
            profile = client.get_my_profile(output_format="JSON")
        except PyegeriaException as e:
            # self.log(f"Retrieving my communities failed: {e}")
            self.notify(f"Could not retrieve your communities: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        if not isinstance(profile, dict):
            return []

        # (link, linked through) pairs: links from the profile itself, then links from its roles
        links = [(link, DIRECT_LINK) for link in profile.get("assignmentScope") or []]
        for appointment in profile.get("performsRoles") or []:
            role = appointment.get("relatedElement") or {}
            role_name = _name(role.get("properties") or {})
            links += [(link, f"Role: {role_name}") for link in appointment.get("nestedElements") or []]

        communities: dict[str, dict] = {}
        for link, linked_through in links:
            community = link.get("relatedElement") or {}
            guid = _guid(community)
            if _type_name(community) != COMMUNITY_TYPE or not guid:
                continue
            properties = community.get("properties") or {}
            entry = communities.setdefault(guid, {"name": _name(properties),
                                                  "description": properties.get("description") or "",
                                                  "types": [], "through": []})
            assignment_type = (link.get("relationshipProperties") or {}).get("assignmentType") or ""
            if assignment_type and assignment_type not in entry["types"]:
                entry["types"].append(assignment_type)
            if linked_through not in entry["through"]:
                entry["through"].append(linked_through)
        return [(c["name"], ", ".join(c["types"]), "; ".join(c["through"]), c["description"], guid)
                for guid, c in communities.items()]

    def show_communities(self) -> None:
        """Show the Work with Communities screen for the current user."""
        if not getattr(self, "user_GUID", ""):
            self.notify("Your profile has not loaded yet, so your communities can't be shown", timeout=10,
                        severity="warning")
            return
        communities = self.list_my_communities()
        if communities is None:
            return
        self.push_screen(CommunitiesScreen(communities), callback=self.communities_callback)

    def communities_callback(self, result: Any) -> None:
        pass
        # self.log(f"Communities screen returned: {result}")

    def search_communities(self, search_string: str) -> list[tuple[str, str, str, str]] | None:
        """Communities matching search_string ('*' for all) as (name, description, qualified name, GUID) rows,
           or None if Egeria could not be reached."""
        client = None
        try:
            client = self._community_client()
            # Depth 0: only the communities' own properties are listed; members are fetched on request
            found = client.find_communities(search_string=search_string or "*", ignore_case=True,
                                            output_format="JSON", graph_query_depth=0)
        except PyegeriaException as e:
            # self.log(f"Searching for communities matching {search_string} failed: {e}")
            self.notify(f"Searching for communities failed: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        # self.log(f"Communities found for {search_string}: {found}")
        rows = []
        # "No elements found" is returned, rather than an exception, when nothing matches
        for community in found if isinstance(found, list) else []:
            guid = _guid(community)
            if not guid:
                continue
            properties = community.get("properties") or {}
            rows.append((_name(properties), properties.get("description") or "",
                         properties.get("qualifiedName") or "", guid))
        return rows

    def get_community_members(self, community_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The people in a community as (name, assignment type, member through, qualified name, GUID) rows,
           or None if they could not be retrieved.

           A person is in the community when they are linked to it directly, or appointed to a role
           that is; roles themselves aren't listed. Other actors (such as teams) are left out. A person
           reached through several links is one row."""
        client = None
        try:
            client = self._community_client()
            community = client.get_community_by_guid(community_guid, output_format="JSON", graph_query_depth=1)
            # (person, assignment type, member through) for each way a person belongs
            memberships = []
            unread_roles = 0
            for link in (community.get("assignedActors") if isinstance(community, dict) else None) or []:
                actor = link.get("relatedElement") or {}
                assignment_type = (link.get("relationshipProperties") or {}).get("assignmentType") or ""
                if _type_name(actor) == PERSON_TYPE:
                    memberships.append((actor, assignment_type, MEMBER_DIRECT))
                elif _is_role(actor):
                    role_through = f"Role: {_name(actor.get('properties') or {})}"
                    try:
                        # Only the appointments are needed; a role can have hundreds of other links
                        role = client.get_actor_role_by_guid(_guid(actor), output_format="JSON", graph_query_depth=1,
                                                             include_only_relationships=[APPOINTMENT_TYPE])
                    except PyegeriaException as e:
                        # self.log(f"Retrieving the people in role {_guid(actor)} failed: {e}")
                        unread_roles += 1
                        continue
                    for appointment in (role.get("rolePerformers") if isinstance(role, dict) else None) or []:
                        person = appointment.get("relatedElement") or {}
                        if _type_name(person) == PERSON_TYPE:
                            memberships.append((person, assignment_type, role_through))
        except PyegeriaException as e:
            # self.log(f"Retrieving members of community {community_guid} failed: {e}")
            self.notify(f"Could not retrieve the community's members: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        if unread_roles:
            self.notify(f"Could not see who holds {unread_roles} of the community's roles, so some members "
                        f"may be missing", timeout=10, severity="warning")

        people: dict[str, dict] = {}
        for person, assignment_type, through in memberships:
            guid = _guid(person)
            if not guid:
                continue
            properties = person.get("properties") or {}
            entry = people.setdefault(guid, {"name": _name(properties),
                                             "qualified_name": properties.get("qualifiedName") or "",
                                             "types": [], "through": []})
            if assignment_type and assignment_type not in entry["types"]:
                entry["types"].append(assignment_type)
            if through not in entry["through"]:
                entry["through"].append(through)
        return sorted(((p["name"], ", ".join(p["types"]), "; ".join(p["through"]), p["qualified_name"], guid)
                       for guid, p in people.items()), key=lambda row: row[0].lower())

    def get_community_blog_posts(self, community_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The community's latest blog posts, newest first, as (title, author, posted, text, GUID) rows,
           or None if they could not be retrieved."""
        client = None
        posts = []
        try:
            client = self._community_client()
            logs = client.get_attached_note_logs(community_guid, graph_query_depth=0)
            # "No elements found" is returned, rather than an exception, when there are none
            for log in logs if isinstance(logs, list) else []:
                entries = client.get_notes_for_note_log(_guid(log), metadata_element_type_name="BlogEntry",
                                                        graph_query_depth=0)
                posts += entries if isinstance(entries, list) else []
        except PyegeriaException as e:
            # self.log(f"Retrieving the blog of community {community_guid} failed: {e}")
            self.notify(f"Could not retrieve the community's blog: {e}", timeout=10, severity="error")
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
        return [row for _, row in rows[:LATEST_POSTS]]

    def _community_blog_log(self, client: Egeria, community_guid: str, community_name: str) -> str:
        """The GUID of the community's blog note log, which is created on first use."""
        qualified_name = BLOG_LOG_QN.format(community_guid=community_guid)
        logs = client.get_attached_note_logs(community_guid, graph_query_depth=0)
        for log in logs if isinstance(logs, list) else []:
            if (log.get("properties") or {}).get("qualifiedName") == qualified_name:
                return _guid(log)
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "NoteLogProperties",
                "typeName": "NoteLog",
                "qualifiedName": qualified_name,
                "displayName": f"{community_name} Blog",
                "description": f"Blog for the members of {community_name}.",
            }
        }
        log_guid = client.create_note_log(element_guid=community_guid, body=body)
        # self.log(f"Created blog for community {community_guid}: {log_guid}")
        return log_guid

    def add_community_blog_post(self, community_guid: str, community_name: str, title: str, text: str) -> bool:
        """Post to the community's blog, creating the blog if it doesn't exist yet. Returns True on success."""
        client = None
        try:
            client = self._community_client()
            log_guid = self._community_blog_log(client, community_guid, community_name)
            properties = {
                "class": "BlogEntryProperties",
                "typeName": "BlogEntry",
                "qualifiedName": client.make_feedback_qn("BlogEntry", community_guid, title),
                "displayName": title,
                "description": text,
            }
            post_guid = client.create_note(log_guid, body=properties)
            # self.log(f"Posted to the blog of community {community_guid}: {post_guid}")
            self.notify(f"Your post '{title}' has been added to the {community_name} blog", timeout=10,
                        severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Posting to the blog of community {community_guid} failed: {e}")
            self.notify(f"Posting to the community's blog failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def get_community_comments(self, community_guid: str) -> list[tuple[str, str, str, str, str]] | None:
        """The comments attached to the community, newest first, as (comment, type, author, posted, GUID) rows,
           or None if they could not be retrieved."""
        client = None
        try:
            client = self._community_client()
            comments = client.get_attached_comments(community_guid, graph_query_depth=0)
        except PyegeriaException as e:
            # self.log(f"Retrieving the comments on community {community_guid} failed: {e}")
            self.notify(f"Could not retrieve the community's comments: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()
        rows = []
        for comment in comments if isinstance(comments, list) else []:
            properties = comment.get("properties") or {}
            author, create_time = _created(comment)
            comment_type = comment_type_label(properties.get("commentType") or "")
            rows.append((create_time, (properties.get("description") or "", comment_type, author,
                                       _posted(create_time), _guid(comment))))
        rows.sort(key=lambda r: r[0], reverse=True)
        return [row for _, row in rows]

    def add_community_comment(self, community_guid: str, text: str, comment_type: str) -> bool:
        """Attach a comment to the community. comment_type is one of pyegeria's COMMENT_TYPES.
           Returns True on success."""
        client = None
        try:
            client = self._community_client()
            response = client.add_comment_to_element(community_guid, text, comment_type)
            # self.log(f"Commented on community {community_guid}: {response}")
            self.notify("Your comment has been added", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Commenting on community {community_guid} failed: {e}")
            self.notify(f"Adding the comment failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def create_community(self, name: str, description: str, mission: str = "",
                         assignment_type: str = CREATOR_ASSIGNMENT_TYPES[0]) -> str | None:
        """Create a community, then link the user's profile to it with assignment_type (none if empty).
           Returns the new community's GUID, or None if it could not be created; a failed link still
           returns the GUID, because the community exists."""
        properties = {
            "class": "CommunityProperties",
            "typeName": COMMUNITY_TYPE,
            "displayName": name,
            "description": description,
        }
        if mission:
            properties["mission"] = mission
        client = None
        try:
            client = self._community_client()
            qualified_name = client.__create_qualified_name__(COMMUNITY_TYPE, name)
            # Egeria rejects a second element with the same qualified name, but only with a server error
            existing = client.get_communities_by_name(filter_string=qualified_name, graph_query_depth=0,
                                                      output_format="JSON")
            if isinstance(existing, list) and existing:
                self.notify(f"A community called {name} already exists - find it below to join it",
                            timeout=10, severity="warning")
                return None
            properties["qualifiedName"] = qualified_name
            community_guid = client.create_community(body={"class": "NewElementRequestBody", "isOwnAnchor": True,
                                                           "properties": properties})
            if not assignment_type:
                self.notify(f"Community {name} created", timeout=10, severity="information")
                return community_guid
            try:
                # same GUID order as join_community: the community is the scope, the profile the actor
                client.link_assignment_scope(community_guid, self.user_GUID, {
                    "class": "NewRelationshipRequestBody",
                    "properties": {"class": "AssignmentScopeProperties", "assignmentType": assignment_type},
                })
            except PyegeriaException as e:
                # self.log(f"Joining new community {community_guid} failed: {e}")
                self.notify(f"Community {name} created, but joining it failed: {e}", timeout=10, severity="warning")
                return community_guid
            self.notify(f"Community {name} created, and you have joined it as its {assignment_type}",
                        timeout=10, severity="information")
            return community_guid
        except PyegeriaException as e:
            # self.log(f"Creating community {name} failed: {e}")
            self.notify(f"Creating the community failed: {e}", timeout=10, severity="error")
            return None
        finally:
            if client:
                client.close_session()

    def join_community(self, community_guid: str, assignment_type: str = JOIN_ASSIGNMENT_TYPES[0]) -> bool:
        """Link the user's profile to the community. Returns True on success."""
        body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "AssignmentScopeProperties",
                "assignmentType": assignment_type,
            }
        }
        client = None
        try:
            client = self._community_client()
            client.link_assignment_scope(community_guid, self.user_GUID, body)
            self.notify(f"You have joined the community as a {assignment_type}", timeout=10,
                        severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Joining community {community_guid} failed: {e}")
            self.notify(f"Joining the community failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

    def leave_community(self, community_guid: str) -> bool:
        """Remove the link between the user's profile and the community. Returns True on success."""
        client = None
        try:
            client = self._community_client()
            # same GUID order as link_assignment_scope: scope (the community) first, actor second
            client.detach_assignment_scope(community_guid, self.user_GUID, {"class": "DeleteRelationshipRequestBody"})
            self.notify("You have left the community", timeout=10, severity="information")
            return True
        except PyegeriaException as e:
            # self.log(f"Leaving community {community_guid} failed: {e}")
            self.notify(f"Leaving the community failed: {e}", timeout=10, severity="error")
            return False
        finally:
            if client:
                client.close_session()

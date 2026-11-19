"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the Project view screen (team members, blog posts/notes,
   resources and comments) for My Profile.

"""
from textual import events, on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button, Select, TextArea

from CommunityScreen import (ElementFeedbackScreen, RateElementScreen, comment_type_label,
                             star_label, STAR_VALUES, COMMENT_TYPES)
from paging_support import is_complete, none_words
from profile_utils import set_screen_heading

# Assignment types offered when a user joins an existing project
JOIN_ASSIGNMENT_TYPES = ["Contributor", "Observer", "ProjectManagement"]


class NewProjectBlogPostScreen(ModalScreen):
    """Collect the title and text of a new blog post / note on a project.

    Dismisses with {"title", "text"}, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Post"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="new_project_blog_post_screen")
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("New Blog Post", classes="span-3", id="new_project_blog_post_title")
        yield ScrollableContainer(
            Static(f"[b]Post to {self.project_name} Blog[/b]"),
            Static("Title *"),
            Input(placeholder="Title of the post", id="project_blog_post_title_input"),
            Static("Post *"),
            TextArea(id="project_blog_post_text"),
            Horizontal(
                Button("Post", id="submit_project_blog_post_btn", variant="primary"),
                Button("Cancel", id="cancel_project_blog_post_btn", variant="warning"),
            ),
            id="new_project_blog_post_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Projects - New Blog Post")
        self.query_one("#project_blog_post_title_input", Input).focus()

    def action_submit(self) -> None:
        title = self.query_one("#project_blog_post_title_input", Input).value.strip()
        text = self.query_one("#project_blog_post_text", TextArea).text.strip()
        if not title or not text:
            self.notify("Please enter both a title and text for the blog post", timeout=5,
                        severity="warning")
            return
        self.dismiss({"title": title, "text": text})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_project_blog_post_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_project_blog_post_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class AddProjectCommentScreen(ModalScreen):
    """Collect the text and type of a comment on a project.

    Dismisses with {"text", "comment_type"}, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Add Comment"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="add_project_comment_screen")
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Add Comment", classes="span-3", id="add_project_comment_title")
        yield ScrollableContainer(
            Static(f"[b]Comment on {self.project_name}[/b]"),
            Static("Comment type"),
            Select([(comment_type_label(t), t) for t in COMMENT_TYPES], value=COMMENT_TYPES[0],
                   allow_blank=False, id="project_comment_type"),
            Static("Comment"),
            TextArea(id="project_comment_text"),
            Horizontal(
                Button("Add Comment", id="submit_project_comment_btn", variant="primary"),
                Button("Cancel", id="cancel_project_comment_btn", variant="warning"),
            ),
            id="add_project_comment_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Projects - Add Comment")
        self.query_one("#project_comment_text", TextArea).focus()

    def action_submit(self) -> None:
        text = self.query_one("#project_comment_text", TextArea).text.strip()
        if not text:
            self.notify("Please enter a comment", timeout=5, severity="warning")
            return
        self.dismiss({"text": text, "comment_type": self.query_one("#project_comment_type", Select).value})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_project_comment_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_project_comment_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class ProjectScreen(ModalScreen):
    """One project: its team members, the latest posts on its blog/notes, its resources and its comments.

    The Egeria work is done by the app's ProjectsMixin (get_project_members,
    get_project_blog_posts, add_project_blog_post, get_project_resources,
    get_project_comments, add_project_comment, join_project); this screen only drives it.
    Feedback on a blog post or resource opens an ElementFeedbackScreen.

    Dismisses with 200 to go back to the projects list, or 210 to go on to the main screen.
    joined is True once the user has joined the project from this screen.
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+n", "add_item", "New Post / Comment"),
        ("ctrl+o", "feedback", "Feedback on Post / Resource"),
        ("enter", "feedback", "Feedback on Post / Resource"),
        ("ctrl+w", "join", "Join Project"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_guid: str, project_name: str, *args, **kwargs):
        super().__init__(id="project_screen", *args, **kwargs)
        self.project_guid = project_guid
        self.project_name = project_name
        # Full text of each blog post, by GUID, shown below the posts table
        self.post_text: dict[str, str] = {}
        # Whether the user is a member (directly or through a role); None until the members are read
        self.is_member: bool | None = None
        self.joined = False
        self.last_active_table: str = "project_posts_table"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.project_name, classes="span-3", id="project_title")
        yield ScrollableContainer(
            Static("[b]Latest blog posts / notes[/b]  [dim]ctrl+n adds a post; Enter or ctrl+o gives feedback on one[/dim]"),
            DataTable(id="project_posts_table", zebra_stripes=True, cursor_type="row"),
            Static("", id="project_post_text"),
            Horizontal(
                Button("New Blog Post", id="new_project_blog_post_btn", variant="primary"),
                Button("Feedback on Post", id="project_post_feedback_btn", variant="primary"),
                id="project_blog_buttons",
            ),
            id="project_blog_container",
        )
        yield ScrollableContainer(
            Static("[b]Members / Team[/b]  [dim](people linked to the project, directly or through a role they hold)[/dim]"),
            DataTable(id="project_members_table", zebra_stripes=True, cursor_type="row"),
            Static("", id="project_membership_text"),
            Vertical(
                Select([(t, t) for t in JOIN_ASSIGNMENT_TYPES], value=JOIN_ASSIGNMENT_TYPES[0],
                       allow_blank=False, id="project_join_assignment_type"),
                Button("Join Project", id="project_join_btn", variant="primary"),
                id="project_join_controls",
            ),
            id="project_members_container",
        )
        yield ScrollableContainer(
            Static("[b]Resources[/b]  [dim](elements the project lists or looks after; "
                   "Enter or ctrl+o gives feedback on one)[/dim]"),
            DataTable(id="project_resources_table", zebra_stripes=True, cursor_type="row"),
            Button("Feedback on Resource", id="project_resource_feedback_btn", variant="primary"),
            id="project_resources_container",
        )
        yield ScrollableContainer(
            Static("[b]Comments[/b]  [dim]with this list selected, ctrl+n adds a comment[/dim]"),
            DataTable(id="project_comments_table", zebra_stripes=True, cursor_type="row"),
            Button("Add Comment", id="add_project_comment_btn", variant="primary"),
            id="project_comments_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, f"Project - {self.project_name}")
        self.query_one("#project_posts_table", DataTable).add_columns("Title", "Author", "Posted", "GUID")
        self.query_one("#project_members_table", DataTable).add_columns(
            "Name", "Assignment Type", "Member Through", "Qualified Name", "GUID")
        self.query_one("#project_resources_table", DataTable).add_columns(
            "Name", "Type", "Linked As", "Description", "GUID")
        self.query_one("#project_comments_table", DataTable).add_columns(
            "Comment", "Type", "Author", "Posted", "GUID")
        self._load_members()
        self._load_posts()
        self._load_resources()
        self._load_comments()

    def _load_members(self) -> None:
        members = self.app.get_project_members(self.project_guid)
        if members is None:
            self.query_one("#project_join_controls", Vertical).display = False
            return
        table = self.query_one("#project_members_table", DataTable)
        table.clear()
        self.is_member = False
        for row in members:
            table.add_row(*row, key=row[4])
            if row[4] == self.app.user_GUID:
                self.is_member = True
                through = f" (through {row[2]})" if row[2] != "Direct" else ""
                self.query_one("#project_membership_text", Static).update(
                    f"You are a member{through} with assignment type: {row[1]}")
        self.query_one("#project_join_controls", Vertical).display = not self.is_member
        if not self.is_member:
            self.query_one("#project_membership_text", Static).update("You are not a member of this project")

    def _load_posts(self) -> None:
        posts = self.app.get_project_blog_posts(self.project_guid)
        if posts is None:
            return
        table = self.query_one("#project_posts_table", DataTable)
        table.clear()
        self.post_text.clear()
        for row in posts:
            table.add_row(row[0], row[1], row[2], row[4], key=row[4])
            self.post_text[row[4]] = row[3]
        if posts:
            # Show the newest post's text straight away
            self.query_one("#project_post_text", Static).update(self.post_text.get(posts[0][4], ""))
        else:
            self.query_one("#project_post_text", Static).update(
                "No posts on the blog yet" if is_complete(posts) else none_words("blog posts", complete=False))

    def _load_resources(self) -> None:
        resources = self.app.get_project_resources(self.project_guid)
        if resources is None:
            return
        table = self.query_one("#project_resources_table", DataTable)
        table.clear()
        for row in resources:
            table.add_row(*row, key=row[4])
        if not resources:
            self.notify("This project has no resources listed or scoped to it", timeout=5)

    def _load_comments(self) -> None:
        comments = self.app.get_project_comments(self.project_guid)
        if comments is None:
            return
        table = self.query_one("#project_comments_table", DataTable)
        table.clear()
        for row in comments:
            table.add_row(*row, key=row[4])

    # --- selection and display ------------------------------------------------

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """Track which DataTable was last focused."""
        if isinstance(event.widget, DataTable):
            self.last_active_table = event.widget.id or self.last_active_table

    @on(DataTable.RowHighlighted, "#project_posts_table")
    def handle_posts_table_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Display the highlighted blog post's text."""
        self.query_one("#project_post_text", Static).update(self.post_text.get(str(event.row_key.value), ""))

    @on(DataTable.RowSelected, "#project_posts_table")
    def handle_posts_table_selected(self, event: DataTable.RowSelected) -> None:
        self.action_post_feedback()

    @on(DataTable.RowSelected, "#project_resources_table")
    def handle_resources_table_selected(self, event: DataTable.RowSelected) -> None:
        self.action_resource_feedback()

    @on(DataTable.RowSelected, "#project_comments_table")
    def handle_comments_table_selected(self, event: DataTable.RowSelected) -> None:
        self.action_add_comment()

    # --- blog -----------------------------------------------------------------

    def action_new_blog_post(self) -> None:
        def on_post(post_data: dict | None) -> None:
            if not post_data:
                return
            if self.app.add_project_blog_post(self.project_guid, self.project_name,
                                              post_data["title"], post_data["text"]):
                self._load_posts()

        self.app.push_screen(NewProjectBlogPostScreen(self.project_name), callback=on_post)

    @on(Button.Pressed, "#new_project_blog_post_btn")
    def handle_new_post_button(self, event: Button.Pressed) -> None:
        self.action_new_blog_post()

    def action_post_feedback(self) -> None:
        table = self.query_one("#project_posts_table", DataTable)
        if table.row_count == 0:
            self.notify("There are no blog posts on this project yet", timeout=5, severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        self.app.push_screen(ElementFeedbackScreen(row[3], f"Blog post: {row[0]}", "BlogEntry"))

    @on(Button.Pressed, "#project_post_feedback_btn")
    def handle_post_feedback_button(self, event: Button.Pressed) -> None:
        self.action_post_feedback()

    # --- joining --------------------------------------------------------------

    def action_join(self) -> None:
        if self.is_member:
            self.notify("You are already a member of this project", timeout=5, severity="warning")
            return
        assignment_type = self.query_one("#project_join_assignment_type", Select).value
        if self.app.join_project(self.project_guid, assignment_type):
            self.joined = True
            self._load_members()

    @on(Button.Pressed, "#project_join_btn")
    def handle_join_button(self, event: Button.Pressed) -> None:
        self.action_join()

    # --- resources ------------------------------------------------------------

    def action_resource_feedback(self) -> None:
        table = self.query_one("#project_resources_table", DataTable)
        if table.row_count == 0:
            self.notify("This project has no resources listed or scoped to it", timeout=5, severity="warning")
            return
        row = table.get_row_at(table.cursor_row)
        self.app.push_screen(ElementFeedbackScreen(row[4], f"{row[1]}: {row[0]}", row[1]))

    @on(Button.Pressed, "#project_resource_feedback_btn")
    def handle_resource_feedback_button(self, event: Button.Pressed) -> None:
        self.action_resource_feedback()

    # --- comments -------------------------------------------------------------

    def action_add_comment(self) -> None:
        def on_comment(comment: dict | None) -> None:
            if not comment:
                return
            if self.app.add_project_comment(self.project_guid, comment["text"], comment["comment_type"]):
                self._load_comments()

        self.app.push_screen(AddProjectCommentScreen(self.project_name), callback=on_comment)

    @on(Button.Pressed, "#add_project_comment_btn")
    def handle_add_comment_button(self, event: Button.Pressed) -> None:
        self.action_add_comment()

    # --- general actions (bindings) -------------------------------------------

    def action_feedback(self) -> None:
        """ctrl+o or Enter gives feedback on whichever of a post or a resource was last active."""
        resources_table = self.query_one("#project_resources_table", DataTable)
        if self.focused is resources_table or self.last_active_table == "project_resources_table":
            self.action_resource_feedback()
        else:
            self.action_post_feedback()

    def action_add_item(self) -> None:
        """ctrl+n adds a comment when the comments list was last active, a blog post otherwise."""
        comments_table = self.query_one("#project_comments_table", DataTable)
        if self.focused is comments_table or self.last_active_table == "project_comments_table":
            self.action_add_comment()
        else:
            self.action_new_blog_post()

    def action_back(self) -> None:
        self.dismiss(200)

    def action_quit(self) -> None:
        """q goes straight back to the main screen, dismissing the projects list too."""
        self.dismiss(210)

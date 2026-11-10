"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the screen for a single community in My Profile: its members,
   the latest posts on its blog and the comments attached to it, plus the forms to
   add a blog post or a comment.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button, Select, TextArea

from pyegeria import COMMENT_TYPES
from profile_utils import set_screen_heading


def comment_type_label(comment_type: str) -> str:
    """'USAGE_EXPERIENCE' -> 'Usage Experience'"""
    return comment_type.replace("_", " ").title()


class NewBlogPostScreen(ModalScreen):
    """Collect the title and text of a new post for a community's blog.

    Dismisses with {"title", "text"}, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Post"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="new_blog_post_screen")
        self.community_name = community_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("New Blog Post", classes="span-3", id="new_blog_post_title")
        yield ScrollableContainer(
            Static(f"[b]Post to the {self.community_name} blog[/b]"),
            Static("Title"),
            Input(placeholder="Title of the post", id="blog_post_title_input"),
            Static("Post"),
            TextArea(id="blog_post_text"),
            Horizontal(
                Button("Post", id="submit_blog_post_btn", variant="primary"),
                Button("Cancel", id="cancel_blog_post_btn", variant="warning"),
            ),
            id="new_blog_post_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Communities - New Blog Post")
        self.query_one("#blog_post_title_input", Input).focus()

    def action_submit(self) -> None:
        title = self.query_one("#blog_post_title_input", Input).value.strip()
        text = self.query_one("#blog_post_text", TextArea).text.strip()
        if not title or not text:
            self.notify("Please enter both a title and the text of the post", timeout=5, severity="warning")
            return
        self.dismiss({"title": title, "text": text})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_blog_post_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_blog_post_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class AddCommunityCommentScreen(ModalScreen):
    """Collect the text and type of a comment on a community.

    Dismisses with {"text", "comment_type"}, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Add Comment"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="add_community_comment_screen")
        self.community_name = community_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Add Comment", classes="span-3", id="add_community_comment_title")
        yield ScrollableContainer(
            Static(f"[b]Comment on {self.community_name}[/b]"),
            Static("Comment type"),
            Select([(comment_type_label(t), t) for t in COMMENT_TYPES], value=COMMENT_TYPES[0],
                   allow_blank=False, id="community_comment_type"),
            Static("Comment"),
            TextArea(id="community_comment_text"),
            Horizontal(
                Button("Add Comment", id="submit_community_comment_btn", variant="primary"),
                Button("Cancel", id="cancel_community_comment_btn", variant="warning"),
            ),
            id="add_community_comment_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Communities - Add Comment")
        self.query_one("#community_comment_text", TextArea).focus()

    def action_submit(self) -> None:
        text = self.query_one("#community_comment_text", TextArea).text.strip()
        if not text:
            self.notify("Please enter a comment", timeout=5, severity="warning")
            return
        self.dismiss({"text": text, "comment_type": self.query_one("#community_comment_type", Select).value})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_community_comment_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_community_comment_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class CommunityScreen(ModalScreen):
    """One community: its members, the latest posts on its blog and its comments.

    The Egeria work is done by the app's CommunitiesMixin (get_community_members,
    get_community_blog_posts, add_community_blog_post, get_community_comments,
    add_community_comment); this screen only drives it.

    Dismisses with 200 to go back to the communities list, or 210 to go on to the main screen.
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+n", "add_item", "New Post / Comment"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_guid: str, community_name: str, *args, **kwargs):
        super().__init__(id="community_screen", *args, **kwargs)
        self.community_guid = community_guid
        self.community_name = community_name
        # Full text of each blog post, by GUID, shown below the posts table
        self.post_text: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.community_name, classes="span-3", id="community_title")
        yield ScrollableContainer(
            Static("[b]Latest blog posts[/b]  [dim]ctrl+n adds a post[/dim]"),
            DataTable(id="community_posts_table", zebra_stripes=True, cursor_type="row"),
            Static("", id="community_post_text"),
            Button("New Blog Post", id="new_blog_post_btn", variant="primary"),
            id="community_blog_container",
        )
        yield ScrollableContainer(
            Static("[b]Members[/b]  [dim](people linked to the community, directly or through a role they hold)[/dim]"),
            DataTable(id="community_members_table", zebra_stripes=True, cursor_type="row"),
            id="community_members_container",
        )
        yield ScrollableContainer(
            Static("[b]Comments[/b]  [dim]with this list selected, ctrl+n adds a comment[/dim]"),
            DataTable(id="community_comments_table", zebra_stripes=True, cursor_type="row"),
            Button("Add Comment", id="add_community_comment_btn", variant="primary"),
            id="community_comments_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, f"Community - {self.community_name}")
        self.query_one("#community_posts_table", DataTable).add_columns("Title", "Author", "Posted", "GUID")
        self.query_one("#community_members_table", DataTable).add_columns(
            "Name", "Assignment Type", "Member Through", "Qualified Name", "GUID")
        self.query_one("#community_comments_table", DataTable).add_columns(
            "Comment", "Type", "Author", "Posted", "GUID")
        self._load_members()
        self._load_posts()
        self._load_comments()

    def _load_members(self) -> None:
        members = self.app.get_community_members(self.community_guid)
        if members is None:
            return
        table = self.query_one("#community_members_table", DataTable)
        table.clear()
        for row in members:
            table.add_row(*row)

    def _load_posts(self) -> None:
        """Rows of (title, author, posted, text, GUID), newest first."""
        posts = self.app.get_community_blog_posts(self.community_guid)
        if posts is None:
            return
        table = self.query_one("#community_posts_table", DataTable)
        table.clear()
        self.post_text = {}
        for title, author, posted, text, guid in posts:
            table.add_row(title, author, posted, guid, key=guid)
            self.post_text[guid] = text
        self._show_post_text()

    def _load_comments(self) -> None:
        comments = self.app.get_community_comments(self.community_guid)
        if comments is None:
            return
        table = self.query_one("#community_comments_table", DataTable)
        table.clear()
        for row in comments:
            table.add_row(*row, key=row[4])

    def _show_post_text(self) -> None:
        table = self.query_one("#community_posts_table", DataTable)
        if table.row_count:
            guid = table.get_row_at(table.cursor_row)[3]
            text = self.post_text.get(guid, "")
        else:
            text = "[dim]No posts yet - be the first to post[/dim]"
        self.query_one("#community_post_text", Static).update(text)

    @on(DataTable.RowHighlighted, "#community_posts_table")
    def handle_post_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._show_post_text()

    def action_back(self) -> None:
        """ Back to the communities list """
        self.dismiss(200)

    def action_quit(self) -> None:
        """ Back to the main screen """
        self.dismiss(210)

    def action_add_item(self) -> None:
        """ Add a comment if the comments list has focus, otherwise a blog post """
        if self.focused is self.query_one("#community_comments_table", DataTable):
            self.action_add_comment()
        else:
            self.action_new_post()

    # --- blog ----------------------------------------------------------------

    @on(Button.Pressed, "#new_blog_post_btn")
    def handle_new_post_button(self, event: Button.Pressed) -> None:
        self.action_new_post()

    def action_new_post(self) -> None:
        def on_post(post: dict | None) -> None:
            if not post:
                return
            if self.app.add_community_blog_post(self.community_guid, self.community_name,
                                                post["title"], post["text"]):
                self._load_posts()

        self.app.push_screen(NewBlogPostScreen(self.community_name), callback=on_post)

    # --- comments ------------------------------------------------------------

    @on(Button.Pressed, "#add_community_comment_btn")
    def handle_add_comment_button(self, event: Button.Pressed) -> None:
        self.action_add_comment()

    def action_add_comment(self) -> None:
        def on_comment(comment: dict | None) -> None:
            if not comment:
                return
            if self.app.add_community_comment(self.community_guid, comment["text"], comment["comment_type"]):
                self._load_comments()

        self.app.push_screen(AddCommunityCommentScreen(self.community_name), callback=on_comment)

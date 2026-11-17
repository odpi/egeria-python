"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the screen for a single community in My Profile: its members,
   the latest posts on its blog, its resources and the comments attached to it, plus
   the forms to join it, add a blog post or a comment, and to give feedback (comments,
   a like, a star rating) on a blog post or resource.

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


# Egeria's StarRating values, best first, with the number of stars each is worth
STAR_VALUES = {"FIVE_STARS": 5, "FOUR_STARS": 4, "THREE_STARS": 3, "TWO_STARS": 2, "ONE_STAR": 1,
               "NO_RECOMMENDATION": 0}
# Assignment types a user can give themselves when joining. Leaders and administrators are
# assigned by the people who manage the community (https://egeria-project.org/concepts/community/)
JOIN_ASSIGNMENT_TYPES = ["Contributor", "Observer"]


def star_label(star_rating: str) -> str:
    """'FOUR_STARS' -> '★★★★☆'; 'NO_RECOMMENDATION' -> 'No recommendation'"""
    stars = STAR_VALUES.get(star_rating)
    if not stars:
        return "No recommendation" if star_rating == "NO_RECOMMENDATION" else star_rating
    return "★" * stars + "☆" * (5 - stars)


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


class RateElementScreen(ModalScreen):
    """Collect a star rating and an optional review, starting from the user's current rating if any.

    Dismisses with {"star_rating", "review"}, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Rate"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, element_name: str, my_rating: tuple[str, str] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs, id="rate_element_screen")
        self.element_name = element_name
        self.my_rating = my_rating

    def compose(self) -> ComposeResult:
        star_rating, review = self.my_rating or ("FIVE_STARS", "")
        if star_rating not in STAR_VALUES:
            star_rating = "FIVE_STARS"
        yield Header(show_clock=True)
        yield Static("Rate", classes="span-3", id="rate_element_title")
        yield ScrollableContainer(
            Static(f"[b]Rate {self.element_name}[/b]"),
            Static("[dim]Rating again replaces your earlier rating[/dim]" if self.my_rating else ""),
            Static("Stars"),
            Select([(star_label(s), s) for s in STAR_VALUES], value=star_rating, allow_blank=False,
                   id="star_rating_select"),
            Static("Review (optional)"),
            TextArea(review, id="rating_review_text"),
            Horizontal(
                Button("Rate", id="submit_rating_btn", variant="primary"),
                Button("Cancel", id="cancel_rating_btn", variant="warning"),
            ),
            id="rate_element_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Communities - Rate")
        self.query_one("#star_rating_select", Select).focus()

    def action_submit(self) -> None:
        self.dismiss({"star_rating": self.query_one("#star_rating_select", Select).value,
                      "review": self.query_one("#rating_review_text", TextArea).text.strip()})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_rating_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_rating_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class ElementFeedbackScreen(ModalScreen):
    """The feedback on one blog post or resource: its likes, star ratings and comments, with
    actions to like or unlike it, rate it and comment on it.

    The Egeria work is done by the app's CommunitiesMixin (get_element_feedback, like_element,
    unlike_element, rate_element, add_element_comment); this screen only drives it.

    Dismisses with 200 to go back to the community, or 210 to go on to the main screen.
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+l", "toggle_like", "Like / Unlike"),
        ("ctrl+r", "rate", "Rate"),
        ("ctrl+n", "add_comment", "Add Comment"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, element_guid: str, element_name: str, element_kind: str = "", *args, **kwargs):
        super().__init__(id="element_feedback_screen", *args, **kwargs)
        self.element_guid = element_guid
        self.element_name = element_name
        # What the element is, for the heading: "Blog post", "Resource", ...
        self.element_kind = element_kind
        self.feedback: dict = {}

    def compose(self) -> ComposeResult:
        heading = f"{self.element_kind}: {self.element_name}" if self.element_kind else self.element_name
        yield Header(show_clock=True)
        yield Static(f"Feedback - {heading}", classes="span-3", id="element_feedback_title")
        yield ScrollableContainer(
            Static("", id="feedback_summary"),
            Horizontal(
                Button("Like", id="toggle_like_btn", variant="primary"),
                Button("Rate", id="rate_element_btn", variant="primary"),
                Button("Add Comment", id="add_element_comment_btn", variant="primary"),
                id="feedback_buttons",
            ),
            id="feedback_summary_container",
        )
        yield ScrollableContainer(
            Static("[b]Ratings[/b]"),
            DataTable(id="element_ratings_table", zebra_stripes=True, cursor_type="row"),
            id="element_ratings_container",
        )
        yield ScrollableContainer(
            Static("[b]Comments[/b]"),
            DataTable(id="element_comments_table", zebra_stripes=True, cursor_type="row"),
            id="element_comments_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, f"Community - Feedback on {self.element_name}")
        self.query_one("#element_ratings_table", DataTable).add_columns("Stars", "Review", "Rated By", "Rated")
        self.query_one("#element_comments_table", DataTable).add_columns(
            "Comment", "Type", "Author", "Posted", "GUID")
        self._load()

    def _load(self) -> None:
        feedback = self.app.get_element_feedback(self.element_guid)
        if feedback is None:
            return
        self.feedback = feedback
        ratings = self.query_one("#element_ratings_table", DataTable)
        ratings.clear()
        for row in feedback["ratings"]:
            ratings.add_row(*row)
        comments = self.query_one("#element_comments_table", DataTable)
        comments.clear()
        for row in feedback["comments"]:
            comments.add_row(*row, key=row[4])

        likes = feedback["likes"]
        like_text = f"{likes} {'person likes' if likes == 1 else 'people like'} this"
        if feedback["i_like"]:
            like_text += " [dim](including you)[/dim]"
        average = feedback["average"]
        rating_count = len(feedback["ratings"])
        if average is None:
            rating_text = "No star ratings yet" if not rating_count else f"{rating_count} rating(s), no stars given"
        else:
            rating_text = f"Average rating {average:.1f} of 5 from {rating_count} rating(s)"
        self.query_one("#feedback_summary", Static).update(
            f"{like_text}\n{rating_text}\n{len(feedback['comments'])} comment(s)")
        self.query_one("#toggle_like_btn", Button).label = "Unlike" if feedback["i_like"] else "Like"
        self.query_one("#rate_element_btn", Button).label = "Change Rating" if feedback["my_rating"] else "Rate"

    def action_back(self) -> None:
        """ Back to the community """
        self.dismiss(200)

    def action_quit(self) -> None:
        """ Back to the main screen """
        self.dismiss(210)

    # --- likes -----------------------------------------------------------------

    @on(Button.Pressed, "#toggle_like_btn")
    def handle_like_button(self, event: Button.Pressed) -> None:
        self.action_toggle_like()

    def action_toggle_like(self) -> None:
        if self.feedback.get("i_like"):
            done = self.app.unlike_element(self.element_guid)
        else:
            done = self.app.like_element(self.element_guid)
        if done:
            self._load()

    # --- ratings ---------------------------------------------------------------

    @on(Button.Pressed, "#rate_element_btn")
    def handle_rate_button(self, event: Button.Pressed) -> None:
        self.action_rate()

    def action_rate(self) -> None:
        def on_rating(rating: dict | None) -> None:
            if not rating:
                return
            if self.app.rate_element(self.element_guid, rating["star_rating"], rating["review"]):
                self._load()

        self.app.push_screen(RateElementScreen(self.element_name, self.feedback.get("my_rating")),
                             callback=on_rating)

    # --- comments --------------------------------------------------------------

    @on(Button.Pressed, "#add_element_comment_btn")
    def handle_add_comment_button(self, event: Button.Pressed) -> None:
        self.action_add_comment()

    def action_add_comment(self) -> None:
        def on_comment(comment: dict | None) -> None:
            if not comment:
                return
            if self.app.add_element_comment(self.element_guid, comment["text"], comment["comment_type"]):
                self._load()

        self.app.push_screen(AddCommunityCommentScreen(self.element_name), callback=on_comment)


class CommunityScreen(ModalScreen):
    """One community: its members, the latest posts on its blog, its resources and its comments.

    The Egeria work is done by the app's CommunitiesMixin (get_community_members,
    get_community_blog_posts, add_community_blog_post, get_community_resources,
    get_community_comments, add_community_comment, join_community); this screen only drives it.
    Feedback on a blog post or resource opens an ElementFeedbackScreen.

    Dismisses with 200 to go back to the communities list, or 210 to go on to the main screen.
    joined is True once the user has joined the community from this screen.
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+n", "add_item", "New Post / Comment"),
        ("ctrl+o", "feedback", "Feedback on Post / Resource"),
        ("ctrl+w", "join", "Join Community"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_guid: str, community_name: str, *args, **kwargs):
        super().__init__(id="community_screen", *args, **kwargs)
        self.community_guid = community_guid
        self.community_name = community_name
        # Full text of each blog post, by GUID, shown below the posts table
        self.post_text: dict[str, str] = {}
        # Whether the user is a member (directly or through a role); None until the members are read
        self.is_member: bool | None = None
        self.joined = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.community_name, classes="span-3", id="community_title")
        yield ScrollableContainer(
            Static("[b]Latest blog posts[/b]  [dim]ctrl+n adds a post; Enter or ctrl+o gives feedback on one[/dim]"),
            DataTable(id="community_posts_table", zebra_stripes=True, cursor_type="row"),
            Static("", id="community_post_text"),
            Horizontal(
                Button("New Blog Post", id="new_blog_post_btn", variant="primary"),
                Button("Feedback on Post", id="post_feedback_btn", variant="primary"),
                id="community_blog_buttons",
            ),
            id="community_blog_container",
        )
        yield ScrollableContainer(
            Static("[b]Members[/b]  [dim](people linked to the community, directly or through a role they hold)[/dim]"),
            DataTable(id="community_members_table", zebra_stripes=True, cursor_type="row"),
            Static("", id="community_membership_text"),
            Horizontal(
                Select([(t, t) for t in JOIN_ASSIGNMENT_TYPES], value=JOIN_ASSIGNMENT_TYPES[0],
                       allow_blank=False, id="community_join_assignment_type"),
                Button("Join Community", id="community_join_btn", variant="primary"),
                id="community_join_controls",
            ),
            id="community_members_container",
        )
        yield ScrollableContainer(
            Static("[b]Resources[/b]  [dim](elements the community lists or looks after; "
                   "Enter or ctrl+o gives feedback on one)[/dim]"),
            DataTable(id="community_resources_table", zebra_stripes=True, cursor_type="row"),
            Button("Feedback on Resource", id="resource_feedback_btn", variant="primary"),
            id="community_resources_container",
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
        self.query_one("#community_resources_table", DataTable).add_columns(
            "Name", "Type", "Linked As", "Description", "GUID")
        self.query_one("#community_comments_table", DataTable).add_columns(
            "Comment", "Type", "Author", "Posted", "GUID")
        self._load_members()
        self._load_posts()
        self._load_resources()
        self._load_comments()

    def _load_members(self) -> None:
        members = self.app.get_community_members(self.community_guid)
        if members is None:
            # Membership is unknown, so neither offer joining nor claim the user is a member
            self.query_one("#community_join_controls", Horizontal).display = False
            return
        table = self.query_one("#community_members_table", DataTable)
        table.clear()
        for row in members:
            table.add_row(*row)
        user_guid = getattr(self.app, "user_GUID", "")
        self.is_member = bool(user_guid) and any(row[4] == user_guid for row in members)
        self.query_one("#community_join_controls", Horizontal).display = not self.is_member
        self.query_one("#community_membership_text", Static).update(
            "[dim]You are a member[/dim]" if self.is_member
            else "[dim]You are not a member - join as a contributor or an observer[/dim]")

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

    def _load_resources(self) -> None:
        resources = self.app.get_community_resources(self.community_guid)
        if resources is None:
            return
        table = self.query_one("#community_resources_table", DataTable)
        table.clear()
        for row in resources:
            table.add_row(*row, key=row[4])

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

    # --- joining ---------------------------------------------------------------

    @on(Button.Pressed, "#community_join_btn")
    def handle_join_button(self, event: Button.Pressed) -> None:
        self.action_join()

    def action_join(self) -> None:
        """ The user joins this community, with the chosen assignment type """
        if self.is_member:
            self.notify(f"You are already a member of {self.community_name}", timeout=5)
            return
        if self.is_member is None:
            self.notify("Your membership couldn't be checked, so joining isn't offered", timeout=5,
                        severity="warning")
            return
        assignment_type = self.query_one("#community_join_assignment_type", Select).value
        if self.app.join_community(self.community_guid, assignment_type):
            self.joined = True
            self._load_members()

    # --- feedback on posts and resources ---------------------------------------

    def _open_feedback(self, table_id: str, guid_column: int, kind: str) -> None:
        table = self.query_one(table_id, DataTable)
        if table.row_count == 0:
            self.notify(f"There is no {kind.lower()} to give feedback on", timeout=5, severity="warning")
            return
        row = table.get_row_at(table.cursor_row)

        def on_close(result) -> None:
            # q on the feedback screen goes on to the main screen
            if result == 210:
                self.dismiss(210)

        self.app.push_screen(ElementFeedbackScreen(row[guid_column], row[0], kind), callback=on_close)

    def _open_post_feedback(self) -> None:
        self._open_feedback("#community_posts_table", 3, "Blog post")

    def _open_resource_feedback(self) -> None:
        self._open_feedback("#community_resources_table", 4, "Resource")

    def action_feedback(self) -> None:
        """ Feedback on the highlighted resource if the resources list has focus, otherwise on the post """
        if self.focused is self.query_one("#community_resources_table", DataTable):
            self._open_resource_feedback()
        else:
            self._open_post_feedback()

    @on(Button.Pressed, "#post_feedback_btn")
    def handle_post_feedback_button(self, event: Button.Pressed) -> None:
        self._open_post_feedback()

    @on(Button.Pressed, "#resource_feedback_btn")
    def handle_resource_feedback_button(self, event: Button.Pressed) -> None:
        self._open_resource_feedback()

    @on(DataTable.RowSelected, "#community_posts_table")
    def handle_post_selected(self, event: DataTable.RowSelected) -> None:
        self._open_post_feedback()

    @on(DataTable.RowSelected, "#community_resources_table")
    def handle_resource_selected(self, event: DataTable.RowSelected) -> None:
        self._open_resource_feedback()

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

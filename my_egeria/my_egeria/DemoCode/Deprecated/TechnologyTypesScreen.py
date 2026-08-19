"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from pyegeria import load_app_config, settings
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Tree, Header, Static, Button, Footer
from textual.widgets._tree import TreeNode


class TechnologyTypesScreen(ModalScreen):
    """Modal screen to display technology types in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("g", "go_back", "Back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, ttlist, user_name, user_pwd, user_kpts):
        """Initialize the TechnologyTypes screen with a list of technology types."""
        super().__init__()
        self.tech_type_list = ttlist
        self.user_name = user_name
        self.user_password = user_pwd
        self.karma_points = user_kpts
        self.tech_type_tree: Tree[str] = Tree(label="Technology Types", id="technology_types_tree")
        self.tech_type_tree.root.expand()
        self.tech_type_tree.auto_expand = True
        self.selected_t_node = None
        self.selected_t_node_label = None
        self.node_id = None
        self.node_status = "expanded"
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        # config_logging()
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}"
        self.sub_title = "Select a technology type"

    def compose(self) -> ComposeResult:
        """ Compose and display the technology type screen"""
        self.tech_type_tree.refresh()
        if self.tech_type_list:
            self.log(f"Technology types: {self.tech_type_list}, type: {type(self.tech_type_list)}")
            self.render_tech_type_hierarchy_to_tree(self.tech_type_list, self.tech_type_tree)
        else:
            self.tech_type_tree.root.add("No technology types found", expand=True)
        self.tech_type_tree.refresh()
        self.log(f"Technology types tree: {self.tech_type_tree}")

        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Display technology types in Egeria"),
            self.tech_type_tree,
            # Button("Select", id="select_tech_type_btn"),
            id="technology_types_table"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200")

    def action_go_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss("201")

    @on(Tree.NodeSelected)
    def handle_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """ The user has selected a node in the tree. """
        self.log(f"Tree node selected, node: {event.node}")
        self.selected_t_node = event.node
        self.selected_t_node_label = event.node.label
        self.log(f"Selected node: {self.selected_t_node}, label: {self.selected_t_node.label}")
        self.dismiss(str(self.selected_t_node.label))

    @on(Tree.NodeCollapsed)
    def handle_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        # handle the twisty to close a node in the tree
        # logger.debug(f"TreeNodeCollapsed: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "collapsed"

    @on(Tree.NodeExpanded)
    def handle_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        # handle the twisty to open a node in the tree
        # logger.debug(f"TreeNodeExpanded: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "expanded"

    def action_expand(self):
        # handle the hot key to expand/collapse all nodes in the tree (see bindings)
        self.tech_type_tree = self.query_one("#technology_types_tree", Tree)
        if self.node_status == "collapsed":
            self.tech_type_tree.root.expand_all()
        else:
            self.tech_type_tree.root.collapse_all()
        return

    def render_tech_type_hierarchy_to_tree(self,
            data: dict | list[dict],
            tree_or_node: Tree[str] | TreeNode[str],
            label_attr: str = "displayName",
            guid_attr: str = "guid",
            children_attr: str = "subTypes"
    ) -> None:
        """Recursively render a DICT) hierarchy into a Textual Tree.

        Args:
            data: The data structure from pyegeria.get_tech_type_hierarchy.
            tree_or_node: The Tree object or a TreeNode to add children to.
            label_attr: The attribute in the data for the node label.
            guid_attr: The attribute in the data for the node data (GUID).
            children_attr: The attribute in the data containing the list of children.
        """
        if isinstance(data, list):
            for item in data:
                self.render_tech_type_hierarchy_to_tree(item, tree_or_node, label_attr, guid_attr, children_attr)
            return

        if not isinstance(data, dict):
            return

        label = str(data.get(label_attr) or data.get("Display Name") or "Unknown")
        guid = str(data.get(guid_attr) or data.get("GUID") or "")

        # If it's a Tree, we add to root. If it's a TreeNode, we add to it.
        if isinstance(tree_or_node, Tree):
            node = tree_or_node.root.add(label, data=guid, expand=True)
        else:
            node = tree_or_node.add(label, data=guid, expand=True)

        children = data.get(children_attr)
        if children and isinstance(children, list):
            for child in children:
                self.render_tech_type_hierarchy_to_tree(child, node, label_attr, guid_attr, children_attr)

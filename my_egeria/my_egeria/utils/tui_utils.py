from __future__ import annotations
from typing import Any, Optional
from textual.widgets import Tree
from textual.widgets._tree import TreeNode

def render_tech_type_hierarchy_to_tree(
    data: dict | list[dict], 
    tree_or_node: Tree[str] | TreeNode[str], 
    label_attr: str = "displayName", 
    guid_attr: str = "guid", 
    children_attr: str = "children"
) -> None:
    """Recursively render a JSON hierarchy into a Textual Tree.
    
    Args:
        data: The JSON structure from pyegeria.get_tech_type_hierarchy.
        tree_or_node: The Tree object or a TreeNode to add children to.
        label_attr: The attribute in the JSON for the node label.
        guid_attr: The attribute in the JSON for the node data (GUID).
        children_attr: The attribute in the JSON containing the list of children.
    """
    if isinstance(data, list):
        for item in data:
            render_tech_type_hierarchy_to_tree(item, tree_or_node, label_attr, guid_attr, children_attr)
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
            render_tech_type_hierarchy_to_tree(child, node, label_attr, guid_attr, children_attr)

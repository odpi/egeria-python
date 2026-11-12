# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""6.2.38 F-ME1: selecting a node in My Egeria's SelectionOverviewScreen passes the node's GUID (or
qualified name), never the domain tree's whole [type, GUID] list."""
from types import SimpleNamespace

import pytest
from textual.widgets import Tree

from my_egeria.SelectionOverviewScreen import SelectionOverviewScreen, node_identifier

DOMAIN_GUID = "8dc3ff8d-0000-4000-8000-000000000001"


def _select(category, node):
    calls = []
    record = lambda kind: (lambda ident: calls.append((kind, ident)))
    fake = SimpleNamespace(category=category,
                           display_selected_term_details=record("glossary"),
                           display_selected_digital_product=record("catalog"),
                           display_selected_data_dictionary=record("dictionary"),
                           display_selected_business_domain=record("domain"),
                           display_selected_root_collection=record("collection"))
    SelectionOverviewScreen.handle_tree_node_selected(fake, SimpleNamespace(node=node))
    return calls


def test_a_domain_node_passes_its_guid_not_the_list():
    tree = Tree("Domains")            # built as shop_for_data_handler.build_domain_details builds it
    branch = tree.root.add("BusinessCapability::Finance", data=["BusinessCapability", DOMAIN_GUID])
    assert _select("domain", branch) == [("domain", DOMAIN_GUID)]


@pytest.mark.parametrize("category, data, label, expected", [
    ("catalog", "a1b2-guid", "Product summary", "a1b2-guid"),                    # leaf data is the GUID
    ("dictionary", "DataDictionary::Sales::Term", "Summary", "DataDictionary::Sales::Term"),
    ("collection", None, "CollectionFolder::Portal", "CollectionFolder::Portal"),  # no data: its QN label
    ("domain", None, "BusinessCapability::Finance::Payroll", "BusinessCapability::Finance::Payroll"),
    ("glossary", None, "GlossaryTerm::Customer", "GlossaryTerm::Customer"),
])
def test_other_node_kinds(category, data, label, expected):
    tree = Tree("T")
    leaf = tree.root.add_leaf(label, data=data)
    assert _select(category, leaf) == [(category, expected)]


def test_node_identifier():
    assert node_identifier(["BusinessCapability", DOMAIN_GUID]) == DOMAIN_GUID
    assert node_identifier(("x", "")) == "x"
    assert node_identifier(None) is None and node_identifier("") is None

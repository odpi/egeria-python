"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Shop for Data and Catalog explorer handler mixin for My Profile Textual App.
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

from pyegeria import (
    PyegeriaException,
    print_basic_exception,
    exec_report_spec,
    ProductManager,
    Egeria,
)
from textual.widgets import DataTable, Tree
from ShopForDataScreen import ShopForDataScreen
from SearchForTermScreen import SearchForTermScreen
from SelectionOverviewScreen import SelectionOverviewScreen
from CreateSubscriptionRequestScreen import CreateSubscriptionRequestScreen
from StatusScreen import StatusScreen


class ShopForDataMixin:
    """Mixin class providing Catalogs & Shop For Data functionality for MyProfileApp."""

    async def handle_shop_for_data_option(self) -> Any:
        """Push new Screen, Show Glossaries, Digital Product Catalogs, Data Dictionaries and
        Business Domains, allow the user to select from one of the 4 categories and use that selection to
        display a list of available collections of the chosen type and allow the user to subscribe to them.
        """
        # start by gathering the data using Pyegeria to access the Egeria backend servers

        # Glossaries
        glossary_table: DataTable = DataTable(id="glossary_table")
        glossary_table.add_columns("Glossary Name", "Description", "Qualified Name")
        glossary_table.cursor_type = "row"
        glossary_table.zebra_stripes = True
        try:
            self.glossary_data = exec_report_spec(
                format_set_name="Glossaries",
                output_format="DICT",
                params={"search_string": "*"},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving glossary details: {e!s}")
            self.exit(420)
            return 420
        self.log(f"Glossary data returned: {self.glossary_data}")
        self.glossary_data_extract = self.glossary_data.get("data") or []
        self.log(f"Glossary data extracted: {self.glossary_data_extract}")
        if self.glossary_data_extract == []:
            self.log(f"No glossary data found for search string: {getattr(self, 'selected_t_node', '*')}")
            glossary_table.add_row("No glossaries found", "No data returned from Egeria", "")
        else:
            for g in self.glossary_data_extract:
                glossary_table.add_row(g.get("Display Name"), g.get("Description"), g.get("Qualified Name"))

        # Digital Product Catalogs
        digital_product_catalog_table: DataTable = DataTable(id="digital_product_catalog_table")
        digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name")
        digital_product_catalog_table.cursor_type = "row"
        digital_product_catalog_table.zebra_stripes = True
        try:
            self.digital_product_catalog_data = exec_report_spec(
                format_set_name="Digital-Product-Catalog",
                output_format="DICT",
                params={
                    "search_string": "*",
                    "metadata_element_subtypes": ["DigitalProduct", "DigitalProductFamily"],
                },
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            self.log(f"Error retrieving digital product catalog details: {e!s}")
            self.exit(421)
            return 421
        self.log(f"Digital Product Catalog data returned: {self.digital_product_catalog_data}")
        self.digital_product_catalog_data_extract = self.digital_product_catalog_data.get("data") or []
        self.log(f"Digital Product Catalog data extracted: {self.digital_product_catalog_data_extract}")
        if self.digital_product_catalog_data_extract == []:
            self.log(f"No digital product catalog data found for user: {self.user_name}")
            digital_product_catalog_table.add_row("No digital product catalogs found", "No data returned from Egeria", "")
        else:
            for catalog_item in self.digital_product_catalog_data_extract:
                digital_product_catalog_table.add_row(
                    catalog_item["Display Name"],
                    catalog_item["Description"],
                    catalog_item["Qualified Name"],
                )

        # Data Dictionaries
        data_dictionary_table: DataTable = DataTable(id="data_dictionary_table")
        data_dictionary_table.add_columns("Data Dictionary Name", "Description", "Qualified Name")
        data_dictionary_table.cursor_type = "row"
        data_dictionary_table.zebra_stripes = True
        try:
            self.data_dictionary_data = exec_report_spec(
                format_set_name="Data-Dictionaries",
                output_format="DICT",
                params={"search_string": "*"},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            self.log(f"Error retrieving data dictionary details: {e!s}")
            self.exit(422)
            return 422
        self.data_dictionary_data_extract = self.data_dictionary_data.get("data") or []
        if self.data_dictionary_data_extract == []:
            self.log(f"No data dictionary details found for user: {self.user_name}")
            data_dictionary_table.add_row("No data dictionaries found", "No data returned from Egeria", "")
        else:
            self.log(f"Found {self.data_dictionary_data_extract} data dictionaries for user {self.user_name}")
            data_dictionary_table.add_row("Display Name", "Description", "Qualified Name")
            for dictionary in self.data_dictionary_data_extract:
                data_dictionary_table.add_row(
                    dictionary.get("Display Name", ""),
                    dictionary.get("Description", ""),
                    dictionary.get("Qualified Name", ""),
                )

        # Business Domains
        business_domain_table: DataTable = DataTable(id="business_domain_table")
        business_domain_table.add_columns("Business Area Name", "Type Name", "GUID")
        business_domain_table.cursor_type = "row"
        business_domain_table.zebra_stripes = True
        try:
            self.business_domain_data = exec_report_spec(
                format_set_name="BusinessCapabilities",
                output_format="DICT",
                params={"search_string": "*"},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            self.log(f"Error retrieving business domain details: {e!s}")
            self.exit(423)
            return 423
        self.business_domain_data_extract = self.business_domain_data.get("data") or []
        if self.business_domain_data_extract == []:
            self.log(f"No business domains found for user {self.user_name}")
            business_domain_table.add_row("No business domains found", "No data returned from Egeria", "")
        else:
            self.log(f"Found {self.business_domain_data_extract} business domains for user {self.user_name}")
            for domain in self.business_domain_data_extract:
                business_domain_table.add_row(
                    domain.get("Qualified Name", ""),
                    domain.get("Type Name", ""),
                    domain.get("GUID", ""),
                )

        # Root Collections
        self.root_collection_table = DataTable(id="root_collection_table")
        self.root_collection_table.add_columns("Root Collection Name", "Description", "GUID")
        self.root_collection_table.cursor_type = "row"
        self.root_collection_table.zebra_stripes = True

        try:
            self.collections = exec_report_spec(
                format_set_name="BasicCollections",
                output_format="DICT",
                params={"search_string": "RootCollection"},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.collections = "Error retrieving collections: " + str(e)
        self.log(f"Found {len(self.collections)} root collections for user {self.user_name}")
        self.log(f"Root collections: {self.collections}")
        if isinstance(self.collections, str):
            self.root_collection_table.add_row("No root collections found", self.collections, "")
        elif isinstance(self.collections, dict) and self.collections.get("kind") == "json":
            self.collections = self.collections.get("data")
            for collection in self.collections:
                self.root_collection_table.add_row(
                    collection.get("Qualified Name"),
                    collection.get("Type Name"),
                    collection.get("GUID"),
                )
        elif isinstance(self.collections, list):
            for collection in self.collections:
                self.root_collection_table.add_row(
                    collection.get("Qualified Name"),
                    collection.get("Type Name"),
                    collection.get("GUID"),
                )
        else:
            self.log(f"Unexpected data type returned from Egeria: {type(self.collections)}")
            self.root_collection_table.add_row("Invalid data type", "Unexpected data type returned from Egeria", "")

        # hand the data to the Screen for displaying
        await self.push_screen(
            ShopForDataScreen(
                glossary_table,
                digital_product_catalog_table,
                data_dictionary_table,
                business_domain_table,
                self.root_collection_table,
                self.user_name,
                self.user_password,
                self.view_server,
                self.platform_url,
            ),
            callback=self.shop_for_data_callback,
        )

    async def shop_for_data_callback(self, result: Any) -> Any:
        """Callback for Shop For Data screen."""
        self.log(f"Shop For Data screen returned: {result}, type: {type(result)}.")
        if not result:
            self.log("Shop For Data screen returned empty result.")
            self._show_main_screen()
            return 200

        if isinstance(result, int):
            selection_type = result
            selection_parm_1 = None
            selection_parm_2 = None
            selection_parm_3 = None
        elif isinstance(result, (list, tuple)):
            selection_type = result[0]
            selection_parm_1 = result[1] if len(result) > 1 else None
            selection_parm_2 = result[2] if len(result) > 2 else None
            selection_parm_3 = result[3] if len(result) > 3 else None
        else:
            self.log(f"Unexpected result type from Shop For Data screen: {type(result)}")
            self._show_main_screen()
            return 418

        if isinstance(selection_type, int):
            if selection_type == 200:
                self.log("Shop For Data screen returned successfully.")
                self._show_main_screen()
                return 200
            elif selection_type == 201:
                self.log(f"Shop For Data screen returned: {selection_type}, request to search for a term ")
                await self.push_screen(
                    SearchForTermScreen(
                        self.user_name,
                        self.user_password,
                        self.view_server,
                        self.platform_url,
                    ),
                    callback=self.search_for_term_callback,
                )
                return 200
            elif selection_type == 211:
                self.log(f"Shop For Data screen returned: {selection_type}, request to subscribe to data source ")
                return 211
            elif selection_type == 212:
                self.log(f"Shop For Data screen returned: {selection_type}, request to sample data source ")
                self.request_to_sample_data_source(selection_parm_1, selection_parm_2, selection_parm_3)
                return 200
            else:
                self.log(f"Shop For Data screen returned: {selection_type}.")
                self._show_main_screen()
                return selection_type

        if selection_type == "dictionary":
            self.log(f"Selected dictionary with qualified name: {selection_parm_1}")
            self.build_dictionary_details(selection_parm_1, selection_parm_2)
        elif selection_type == "domain":
            self.log(f"Selected business domain with qualified name: {selection_parm_1}")
            self.build_domain_details(selection_parm_1, selection_parm_2)
        elif selection_type == "catalog":
            self.log(f"Selected catalog with qualified name: {selection_parm_1}")
            self.build_catalog_details(selection_parm_1, selection_parm_2)
        elif selection_type == "glossary":
            self.log(f"Selected glossary with qualified name: {selection_parm_2}")
            self.build_glossary_details(selection_parm_1, selection_parm_2)
        elif selection_type == "collection":
            self.log(f"Selected Root Collection with qualified name: {selection_parm_1}")
            self.build_root_collection_details(selection_parm_1, selection_parm_2)
        else:
            self.log(f"Unknown selection type: {selection_type}")
            self.exit(429)

    def build_dictionary_details(self, target_qualified_name: str, target_display_name: str) -> Any:
        """Build the details object for a dictionary details screen."""
        self.log(f"Building dictionary details for qualified name: {target_qualified_name}")
        self.dictionary_qualified_name = target_qualified_name
        self.dictionary_display_name = target_display_name
        build_structure: dict = {}

        try:
            self.dictionary_details = exec_report_spec(
                format_set_name="Data-Dictionaries",
                output_format="DICT",
                params={"search_string": self.dictionary_qualified_name, "filter_string": self.dictionary_qualified_name},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving dictionary details: {e!s}")
            self.exit(420)
            return 420
        self.log(f"Dictionary Details: {self.dictionary_details}")
        if not self.dictionary_details:
            error_category = "Dictionary Details"
            error_message = "No dictionary details found"
            self.log(f"Error retrieving dictionary details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.dictionary_details.get("kind") == "empty":
            dictionary_tree: Tree = Tree(label="Empty Dictionary", id="data_dictionary_tree")
            dictionary_tree.root.expand()
            dictionary_tree.root.content = "No dictionary terms found for this dictionary"
        else:
            dictionary_tree = Tree(label=self.dictionary_display_name, id="data_dictionary_tree")
            dictionary_tree.root.expand()
            dictionary_tree.auto_expand = True
            self.dictionary_details_data = self.dictionary_details.get("data")
            for term in self.dictionary_details_data:
                self.log(f"Dictionary term: {term} being processed")
                term_qualified_name = term.get("Qualified Name") or ""
                term_subject = term.get("Subject Area") or ""
                term_summary = term.get("Summary") or ""
                if term_subject not in build_structure:
                    build_structure[term_subject] = []
                build_structure[term_subject].append({term_qualified_name: term_summary})

            for term_subject, terms in build_structure.items():
                self.log(f"Building tree for subject: {term_subject}, term: {terms}")
                dictionary_branch = dictionary_tree.root.add(term_subject)
                dictionary_branch.expand()
                for term_dict in terms:
                    self.log(f"Adding term to tree: {term_dict}")
                    for term_qualified_name, term_summary in term_dict.items():
                        dictionary_branch.add_leaf(term_summary, data=term_qualified_name)
                dictionary_tree.root.expand()

        self.push_screen(
            SelectionOverviewScreen(
                "dictionary",
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
                data_tree=dictionary_tree,
            ),
            callback=self.overview_callback,
        )

    def build_domain_details(self, target_qualified_name: str, target_type__name: str) -> Any:
        """Build the details object for a business domain details screen."""
        self.log(f"Building domain details for qualified name: {target_qualified_name}")
        self.domain_qualified_name = target_qualified_name
        self.domain_type__name = target_type__name
        build_structure: dict = {}

        try:
            self.domain_details = exec_report_spec(
                format_set_name="BusinessCapabilities",
                output_format="DICT",
                params={"search_string": self.domain_qualified_name, "filter_string": self.domain_qualified_name},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving business domain details: {e!s}")
            self.exit(420)
            return 420
        self.log(f"domain_details: {self.domain_details}")
        if not self.domain_details:
            error_category = "Business Domain Details"
            error_message = "No domain details found"
            self.log(f"Error retrieving business domain details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.domain_details.get("kind") == "empty":
            domain_tree: Tree = Tree(label="Empty Business Domain", id="business_domain_tree")
            domain_tree.root.expand()
            domain_tree.root.content = "No domain details found for this business domain"
        else:
            self.domain_details_data = self.domain_details.get("data")
            self.log(f"domain_details_data: {self.domain_details_data}")
            if isinstance(self.domain_details_data, dict):
                self.domain_display_name = self.domain_details_data.get("Qualified Name") or target_type__name
                domain_items = [self.domain_details_data]
            elif isinstance(self.domain_details_data, list) and len(self.domain_details_data) > 0:
                self.domain_display_name = self.domain_details_data[0].get("Qualified Name") if isinstance(self.domain_details_data[0], dict) else target_type__name
                domain_items = self.domain_details_data
            else:
                self.domain_display_name = target_type__name
                domain_items = []
            domain_tree = Tree(label=self.domain_display_name, id="business_domain_tree")
            domain_tree.root.expand()
            domain_tree.auto_expand = True
            for term in domain_items:
                if term is None:
                    continue
                term_qualified_name = term.get("Qualified Name") or ""
                term_type = term.get("Type Name") or ""
                term_GUID = term.get("GUID") or ""
                term_members = term.get("Containing Members")
                term_memberof = term.get("Member Of")
                build_structure[term_qualified_name] = {
                    "term_type": term_type,
                    "term_GUID": term_GUID,
                    "term_members": term_members,
                    "term_memberof": term_memberof,
                }
            for qualified_name, details in build_structure.items():
                domain_branch = domain_tree.root.add(qualified_name, data=[details["term_type"], details["term_GUID"]])
                if details["term_members"] is not None:
                    domain_branch_members = domain_branch.add("Containing Members")
                    for member in details["term_members"]:
                        domain_branch_members.add_leaf(member)
                if details["term_memberof"] is not None:
                    for member in details["term_memberof"]:
                        domain_branch.add_leaf(member)
                domain_tree.root.expand()

        self.push_screen(
            SelectionOverviewScreen(
                "domain",
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
                data_tree=domain_tree,
            ),
            callback=self.overview_callback,
        )

    def build_catalog_details(self, target_qualified_name: str, target_display_name: str) -> Any:
        """Build the details object for a product catalog details screen."""
        self.log(f"Building product catalog details for qualified name: {target_qualified_name}")
        self.catalog_qualified_name = target_qualified_name
        self.catalog_display_name = target_display_name
        build_structure: dict = {}

        try:
            self.catalog_details = exec_report_spec(
                format_set_name="Digital-Product-Catalog",
                output_format="DICT",
                params={"search_string": self.catalog_qualified_name, "filter_string": self.catalog_qualified_name},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving catalog details: {e!s}")
            self.exit(420)
            return 420
        self.log(f"catalog_details: {self.catalog_details}")
        if not self.catalog_details:
            error_category = "Catalog Details"
            error_message = "No catalog details found"
            self.log(f"Error retrieving catalog details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return
        elif self.catalog_details.get("kind") == "empty":
            catalog_tree: Tree = Tree(label="Empty Catalog", id="digital_product_catalog_tree")
            catalog_tree.root.expand()
            catalog_tree.root.content = "No catalog terms found for this catalog"
            sample_data: list = []
        else:
            catalog_tree = Tree(label=self.catalog_display_name, id="digital_product_catalog_tree")
            catalog_tree.root.expand()
            catalog_tree.auto_expand = True
            self.catalog_details_data = self.catalog_details.get("data")
            self.log(f"catalog_details_data: {self.catalog_details_data}")
            if not self.catalog_details_data:
                error_category = "Catalog Details"
                error_message = "No catalog details found or the data dict entry is missing"
                self.log(f"Error retrieving catalog details: {error_category}, {error_message}")
                self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
                return
            for product in self.catalog_details_data:
                self.log(f"product: {product}")
                term_qualified_name = product.get("Qualified Name") or ""
                term_subject = product.get("Display Name") or ""
                term_summary = product.get("Description") or ""
                if term_subject not in build_structure:
                    build_structure[term_subject] = []
                build_structure[term_subject].append({term_qualified_name: term_summary})
                self.log(f"build_structure: {build_structure}")

            sample_data = []
            for instance, data_prods in build_structure.items():
                catalog_branch = catalog_tree.root.add(instance)
                for data_prod in data_prods:
                    for term_qualified_name, term_summary in data_prod.items():
                        catalog_branch.add_leaf(term_summary, data=term_qualified_name)
                        self.log(f"term_qualified_name: {term_qualified_name}, term summary: {term_summary}")
                catalog_tree.root.expand()

            # get some sample data from the data source for each product
            for product in self.catalog_details_data:
                collection_memberships = product.get("Member Of")
                if collection_memberships:
                    collection_membership_list = collection_memberships.split(",")
                    self.log(f"Membership List for product {product.get('Display Name')}: {collection_membership_list}")
                    for membership_qname in collection_membership_list:
                        self.log(f"Processing collection membership: {membership_qname}")
                        if "DigitalProduct" in membership_qname:
                            self.log(f"Processing dataset: {membership_qname}")
                            try:
                                dclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
                                token = dclient.create_egeria_bearer_token(self.user_name, self.user_password)
                                data_set_metadata = dclient.find_tabular_data_sets(
                                    search_string=membership_qname,
                                    start_from=0,
                                    page_size=1,
                                    output_format="DICT",
                                )
                                self.log(f"Dataset metadata retrieved: {data_set_metadata}")
                                if isinstance(data_set_metadata, list) and len(data_set_metadata) > 0 and data_set_metadata != "No elements found":
                                    data_set_guid = data_set_metadata[0].get("GUID")
                                    if data_set_guid:
                                        data_set_data = dclient.get_tabular_data_set(
                                            tabular_data_set_guid=data_set_guid,
                                            start_from_row=0,
                                            max_row_count=10,
                                            output_format="MD",
                                        )
                                        self.log(f"Dataset data retrieved: {data_set_data}")
                                        sample_data.append(data_set_data)
                                    else:
                                        sample_data.append(f"No GUID found for dataset {membership_qname}")
                                else:
                                    sample_data.append(f"No metadata found for dataset {membership_qname}")
                            except PyegeriaException as e:
                                self.log(f"Error retrieving dataset data: {e}")
                                print_basic_exception(e)
                    self.log(f"Sample data after product {product.get('Display Name')}: {sample_data}")
            self.log(f"Final sample data length: {len(sample_data)}")

        self.push_screen(
            SelectionOverviewScreen(
                "catalog",
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
                data_tree=catalog_tree,
                data_samples=sample_data,
            ),
            callback=self.overview_callback,
        )

    def build_glossary_details(self, target_qualified_name: str, target_display_name: str) -> None:
        """Build the details object for a glossary details screen."""
        self.log(f"Building glossary details for qualified name: {target_qualified_name}")
        self.glossary_qualified_name = target_qualified_name
        self.glossary_display_name = target_display_name

        glossary_tree: Tree = Tree(label=self.glossary_display_name, id="glossary_details_tree")

        for glossary_instance in getattr(self, "glossary_data_extract", []):
            if glossary_instance.get("Qualified Name") == target_qualified_name:
                self.glossary_folders = glossary_instance.get("Folders") or None
                self.log(f"glossary_folders: {self.glossary_folders}")
                if self.glossary_folders is not None:
                    glossary_tree.root.expand()
                    glossary_tree.auto_expand = True

                    folder_entries = [f.strip() for f in self.glossary_folders.split(",")]
                    nodes = {(): glossary_tree.root}
                    prefixes = ["GlossaryCategory", "GlossaryTerm", "CollectionFolder"]

                    for entry in folder_entries:
                        parts = entry.split("::")
                        if len(parts) == 1:
                            parts = entry.split("/")

                        is_leaf = False
                        full_id = ""
                        if any(parts[0].startswith(p) for p in prefixes):
                            type_prefix = parts[0]
                            path_parts = parts[1:]
                            is_leaf = "Term" in type_prefix
                            if is_leaf:
                                full_id = path_parts[-1]
                        else:
                            path_parts = parts

                        current_path = ()
                        for i, part in enumerate(path_parts):
                            parent_path = current_path
                            current_path = current_path + (part,)

                            if current_path not in nodes:
                                parent_node = nodes[parent_path]
                                if is_leaf and i == len(path_parts) - 1:
                                    nodes[current_path] = parent_node.add_leaf(part, data=full_id)
                                else:
                                    new_node = parent_node.add(part, data=part)
                                    new_node.expand()
                                    nodes[current_path] = new_node

                    glossary_tree.refresh()
                else:
                    self.log("No glossary folders found in the glossary data extract")
                    folder_category = "Empty Glossary"
                    category = glossary_tree.root.add(folder_category)
                    folder_term = "No glossary terms found for this glossary"
                    category.add_leaf(folder_term)

        self.push_screen(
            SelectionOverviewScreen(
                "glossary",
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
                data_tree=glossary_tree,
            ),
            callback=self.overview_callback,
        )

    def build_root_collection_details(self, target_qualified_name: str, target_display_name: str) -> None:
        """Build the details object for a root collection details screen."""
        member_tree: Tree = Tree(label="Root Collection", id="root_collection_members_tree")
        member_tree.root.expand()
        member_tree.auto_expand = True

        self.log(f"Building root collection details for qualified name: {target_qualified_name}")
        self.root_collection_qualified_name = target_qualified_name
        collection_branch = member_tree.root.add(self.root_collection_qualified_name, expand=True)
        self.log(f"self_collections: {self.collections}")
        collection = self.collections[0] if isinstance(self.collections, list) and len(self.collections) > 0 else {}
        self.log(f"collection: {collection}")
        if target_qualified_name == collection.get("Qualified Name"):
            root_collection_contains: str = collection.get("Containing Members") or ""
            self.log(f"root_collection_contains: {root_collection_contains}")
            if root_collection_contains:
                folders = str.split(root_collection_contains, ", ")
                for folder in folders:
                    collection_branch.add_leaf(folder)

        self.push_screen(
            SelectionOverviewScreen(
                "collection",
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
                data_tree=member_tree,
            ),
            callback=self.overview_callback,
        )

    def overview_callback(self, r_code: Any) -> None:
        """Callback function for handling overview screen actions."""
        if isinstance(r_code, list):
            self.selected_item = r_code[1]
            self.selected_tree = r_code[2]
            r_code = r_code[0]
        if r_code == 410:
            error_category = "Collection Category"
            error_message = "Unknown collection category returned"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif r_code == 411:
            error_category = "Glossary"
            error_message = "query_one no matches found for glossary tree"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif r_code == 412:
            error_category = "Digital Product Catalog"
            error_message = "query_one no matches found for digital product catalog tree"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif r_code == 413:
            error_category = "Data Dictionary"
            error_message = "query_one no matches found for data dictionary tree"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif r_code == 414:
            error_category = "Business Domain"
            error_message = "query_one no matches fround for business domain tree"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
        elif r_code == 415:
            error_category = "Root Collections"
            error_message = "query_one no matches found for root collections tree"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
        else:
            self.log(f"Overview screen callback, return code : {r_code}")
            if r_code == 211:
                self.log(f"Subscribing to selected item: {self.selected_item} from {self.selected_tree}")
                try:
                    s_client = ProductManager(self.view_server, self.platform_url, self.user_name, self.user_password)
                    s_client.create_egeria_bearer_token(self.user_name, self.user_password)
                    s_client.create_digital_subscription(self.selected_item)
                except PyegeriaException:
                    self.log(f"Error creating digital subscription: {self.selected_item} from {self.selected_tree}")
                    self.notify("Error creating digital subscription")
                    self.push_screen(CreateSubscriptionRequestScreen(), callback=self.create_subscription_callback)
            else:
                self.push_screen(
                    ShopForDataScreen(
                        self.view_server,
                        self.platform_url,
                        self.user_name,
                        self.user_password,
                        self.selected_item,
                        self.selected_tree,
                    ),
                    callback=self.shop_for_data_callback,
                )

    def create_subscription_callback(self, result: Any) -> None:
        """Callback routine for create subscription request screen."""
        if result is None:
            self.log("User cancelled subscription creation")
            return
        self.log(f"Subscription created: {result}")

    def request_to_sample_data_source(self, selection_parm_1: Any, selection_parm_2: Any, selection_parm_3: Any) -> None:
        """The user has requested to see a sample of the data from the selected data source."""
        self.row_highlighted = selection_parm_1
        self.cursor_row_highlighted = selection_parm_2
        self.data_table_highlighted = selection_parm_3
        self.log(f"Data selected: row={selection_parm_1}, cursor_row={selection_parm_2}, data_table={selection_parm_3}")
        selected_item = self.query_one("#" + self.data_table_highlighted, DataTable)
        item_content = selected_item.get_row(self.row_highlighted)

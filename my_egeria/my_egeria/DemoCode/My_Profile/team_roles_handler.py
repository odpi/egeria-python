"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Team and Roles search and term details handler mixin for My Profile Textual App.
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

from textual import on
from textual.widgets import DataTable, Static
from textual.containers import ScrollableContainer
from pyegeria import exec_report_spec, PyegeriaException, print_basic_exception
from MyTeamScreen import MyTeam
from ShopForDataScreen import ShopForDataScreen
from StatusScreen import StatusScreen


class TeamRolesMixin:
    """Mixin class providing Team and Roles interactions for MyProfileApp."""

    @on(DataTable.RowSelected, "#roles_table")
    def handle_roles_table_row_selection(self, event: DataTable.RowSelected) -> Any:
        role_table = event.data_table
        selected_row_key = event.row_key
        selected_row_data = role_table.get_row(selected_row_key)
        selected_role_description = selected_row_data[2]
        selected_role_name = selected_row_data[0]
        selected_role_type = selected_row_data[1]
        selected_role_guid = selected_row_data[3]
        self.log(f"Selected role: {selected_row_data}")
        team_members_list: list = []
        self.team_members = []

        # provide list of team members for team leader or team member
        if (
            "TeamLeader" in selected_role_name
            or "TeamLeader" in selected_role_type
            or "TeamMember" in selected_role_name
            or "TeamMember" in selected_role_type
        ):
            self.log(f"Selected role is a TeamLeader or TeamMember: {selected_role_name}")
            result = self.find_team_members(selected_role_name)
            if not isinstance(result, (tuple, list)) or len(result) != 5:
                return
            team_members_list, team_display_name, team_qualified_name, team_category, team_description = result
        else:
            self.log(f"Selected role is not a TeamLeader or TeamMember: {selected_role_name}")
            return 201

        self.log(f"team_members_list: {team_members_list}")
        # Process team data for display on screen
        team_properties: list = []
        team_properties.append(team_display_name)
        team_properties.append(team_qualified_name)
        team_properties.append(team_category)
        team_properties.append(team_description)
        self.log(f"team_properties: {team_properties}")
        # Process team member data for display on screen
        for team_member in team_members_list:
            if isinstance(team_member, list) and len(team_member) > 0 and "Selection Error" in str(team_member[0]):
                self.log(f"Team member details contain 'Selection Error': {team_member}")
                self.team_members.append(team_member)
                break
            elif isinstance(team_member, dict):
                self.log(f"Processing team member properties: {team_member}")
                team_member_properties = []
                team_member_properties.append(team_member.get("Individual"))
                team_member_properties.append(team_member.get("Assignment Type"))
                team_member_properties.append(team_member.get("Individual GUID"))
                self.log(f"team_member_properties: {team_member_properties}")
                self.team_members.append(team_member_properties)
                self.log(f"team_members: {self.team_members}")

        self.log(f"team_members: {self.team_members}")
        self.log(f"team_properties: {team_properties}")
        self.log(f"User name: {self.user_name}")
        self.push_screen(MyTeam(self.team_members, team_properties, self.user_name), callback=self.my_team_callback)

    def find_team_members(self, role_name: str) -> list[Any]:
        """Common routine for finding team members given a role name.

        Extracts the Department::nnn from the name to use as the search key.
        """
        selected_role_name = role_name
        team_members_list: list = []
        self.team_members = []

        search_key_parts = selected_role_name.split("::")
        role_search_key = "::".join(search_key_parts[1:])
        self.log(f"Role search key: {role_search_key}")
        try:
            team_member_data: dict = exec_report_spec(
                format_set_name="Team-Members",
                output_format="DICT",
                params={"search_string": role_search_key},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving team members: {e!s}")
            self.exit(440)
            return [[], None, None, None, None]

        self.log(f"team_member_data: {team_member_data}")
        if team_member_data.get("kind") != "empty":
            team_members_data_struct = team_member_data.get("data") or []
            self.log(f"team members data extracted: {team_members_data_struct}")
        else:
            self.log(f"No team members found for role: {role_search_key}")
            error_category = "Team Members"
            error_message = "No team members found"
            self.log(f"Error retrieving team members: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return [[], None, None, None, None]

        team_members_list.clear()
        team_display_name: str = ""
        team_qualified_name: str = ""
        team_category: str = ""
        team_description: str = ""
        for team_member in team_members_data_struct:
            team_display_name = team_member.get("Display Name", "")
            team_qualified_name = team_member.get("Qualified Name", "")
            team_category = team_member.get("Category", "")
            team_description = team_member.get("Description", "")
            team_member_structure: list[dict] = team_member.get("Members", [])

            if team_member_structure is not None:
                for entry in team_member_structure:
                    team_members_list.append(entry)

        if not team_members_list and not team_display_name:
            error_category = "Team Member Details"
            error_message = "No team member details found"
            self.log(f"Error retrieving team member details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return [[], None, None, None, None]

        return [team_members_list, team_display_name, team_qualified_name, team_category, team_description]

    def my_team_callback(self, status: Any) -> None:
        self.log(f"Callback received with status: {status}")
        if status == 200:
            self.log("MyTeam screen completed successfully")
        else:
            self.log(f"Error in MyTeam screen: {status}")
        self._show_main_screen()

    def search_for_term_callback(self, status: Any) -> None:
        self.log(f"Callback received with status: {status}")
        if status == 200:
            self.log("Search for term screen completed successfully")
            self._show_main_screen()
        elif status == 201:
            glossary_table = self.query_one("g#glossary_table", DataTable)
            digital_product_catalog_table = self.query_one("d#digital_product_catalog_table", DataTable)
            data_dictionary_table = self.query_one("d#data_dictionary_table", DataTable)
            business_domain_table = self.query_one("b#business_domain_table", DataTable)
            data_specification_table = self.query_one("d#data_specification_table", DataTable)
            self.log("No matches found for search term")
            self.push_screen(
                ShopForDataScreen(
                    glossary_table,
                    digital_product_catalog_table,
                    data_dictionary_table,
                    business_domain_table,
                    data_specification_table,
                    self.user_name,
                    self.user_password,
                    self.view_server,
                    self.platform_url,
                ),
                callback=self.shop_for_data_callback,
            )
        else:
            self.log(f"Error in Search for term screen: {status}")
            error_category = "Search for Term"
            error_message = "Error retrieving Term details"
            self.log(f"Error retrieving team member details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)

    def display_glossary_term_details(self, term: str) -> int:
        """Displays the details of a GlossaryTerm item."""
        self.target_term = term
        try:
            self.term_details = exec_report_spec(
                format_set_name="Glossary-Terms",
                output_format="JSON",
                params={"search_string": self.target_term, "filter_string": self.target_term},
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving term details: {e!s}")
            self.exit(440)
            return 440

        self.log(f"term_details: {self.term_details}")
        if not self.term_details:
            error_category = "Glossary Term Details"
            error_message = "No glossary term details found"
            self.log(f"Error retrieving glossary term details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return 440
        elif self.term_details.get("kind") == "empty":
            self.log(f"No glossary term details found for qualified name: {self.target_term}")
            error_category = "Glossary Term Details"
            error_message = "No glossary term details found"
            self.log(f"Error retrieving glossary term details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return 440

        self.term_details_data = self.term_details.get("data")

        if not self.term_details_data:
            error_category = "Glossary Term Details"
            error_message = "No glossary term details found or the data dict entry is missing"
            self.log(f"Error retrieving glossary term details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return 440
        else:
            self.term_details_container: ScrollableContainer = self.screen.query_one(DataTable)
            if isinstance(self.term_details_data, dict):
                for data_item_key, data_item_value in self.term_details_data.items():
                    self.term_details_container.mount(Static(f"Field: {data_item_key}, Value: {data_item_value}"))
        return 200

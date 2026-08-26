"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Technology Types handler mixin for My Profile Textual App.
"""

import datetime
import json
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

from pyegeria import AutomatedCuration, PyegeriaException, print_basic_exception
from StatusScreen import StatusScreen
from TechnologyTypeScreens import (
    TechnologyTypesScreen,
    TechnologyTypeOptionsScreen,
    TechnologyTypeTemplatesScreen,
    TechnologyTypeProcessesScreen,
)
from profile_utils import clean_structure, bools_to_strings


class TechTypesMixin:
    """Mixin class providing Technology Types functionality for MyProfileApp."""

    async def handle_technology_types_option(self) -> None:
        """Fetch and display technology types screen."""
        self.log("Fetching technology types...")
        await self.fetch_technology_types()
        self.log(f"Tech Type Response: {self.tech_type_response} | {self.tech_type_list}")
        if self.tech_type_response == []:
            self.log("No technology types found.")
            self.exit(200)
        elif len(self.tech_type_response) == 3 and int(self.tech_type_response) >= 400:
            self.log("Error fetching technology types.")
            self.exit(int(self.tech_type_response))
        self.log("Technology types fetched successfully.")
        self.log("Displaying technology types...")
        await self.push_screen(
            TechnologyTypesScreen(
                self.tech_type_list,
                self.user_name,
                self.user_password,
                self.karma_points,
            ),
            callback=self.tech_type_callback,
        )
        self.log("Technology types displayed successfully.")

    async def tech_type_callback(self, result: Any) -> int:
        """Callback for Technology Types screen.

        If the result is int (4xx) it indicates an error in the screen.
        If the result is str it contains the GUID of the selected technology type.
        """
        # clear local data fields
        tech_type_description = ""
        self.tech_type_data = {}
        self.tech_type_data_extracted = {}
        self.tech_type_templates = []
        self.tech_type_processes = []
        # check that we got a valid result from the screen and process accordingly
        if not result or isinstance(result, int):
            self.log(f"Technology Types screen cancelled or failed; return: {result}.")
            self._show_main_screen()
            return result
        self.selected_t_node = str(result)
        self.log(f"Technology Types screen returned: {self.selected_t_node}")
        # Request details for selected tech type
        try:
            p_client = AutomatedCuration(self.view_server, self.platform_url, self.user_name, self.user_password)
            token = p_client.create_egeria_bearer_token(self.user_name, self.user_password)
            self.tech_type_data = p_client.get_tech_type_detail(
                filter_string=self.selected_t_node,
                output_format="JSON",
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            error_category = "Technology Type Process Detail Retrieval"
            error_message = f"Failed to retrieve technology type process details for {getattr(self, 'selected_q_name', self.selected_t_node)}: {str(e)}"
            self.log(f"Error retrieving technology type details: {error_category}, {error_message}")
            await self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)

        self.log(f"Technology Type Data: {self.tech_type_data}, type: {type(self.tech_type_data)}")

        if "specificationMermaidGraph" in self.tech_type_data:
            del self.tech_type_data["specificationMermaidGraph"]
            self.log("Technology Type Mermaid Graph Removed")

        self.tech_type_guid = self.tech_type_data.get("technologyTypeGUID")
        self.tech_type_name = self.tech_type_data.get("displayName")
        self.tech_type_templates = self.tech_type_data.get("catalogTemplates")
        self.tech_type_templates = clean_structure(self.tech_type_templates)
        self.tech_type_templates = bools_to_strings(self.tech_type_templates)
        self.log(f"Templates: {self.tech_type_templates}, type: {type(self.tech_type_templates)}")
        self.tech_type_processes = self.tech_type_data.get("governanceActionProcesses")
        self.tech_type_processes = clean_structure(self.tech_type_processes)
        self.tech_type_processes = bools_to_strings(self.tech_type_processes)
        self.log(f"Processes: {self.tech_type_processes}, type: {type(self.tech_type_processes)}")
        self.tech_type_description = self.tech_type_data.get("description")

        self.log(f"Technology Type GUID: {self.tech_type_guid}")
        self.log(f"Technology Type Name: {self.tech_type_name}")
        self.log(f"Technology Type Description: {self.tech_type_description}")
        self.log(f"Technology Type Templates: {self.tech_type_templates}" or [{"templates": "None"}])
        self.log(f"Technology Type Processes: {self.tech_type_processes}" or [{"processes": "None"}])

        await self.push_screen(
            TechnologyTypeOptionsScreen(
                self.tech_type_guid,
                self.tech_type_name,
                self.tech_type_description,
                self.user_name,
                self.user_password,
                self.karma_points,
                self.tech_type_templates,
                self.tech_type_processes,
            ),
            callback=self.tech_type_options_callback,
        )
        return 200

    async def tech_type_options_callback(self, result: Any) -> int:
        self.log(f"Technology Type Options screen returned: {result}")
        self.selected_t_option = None
        self.selected_t_option_selected = None

        if not result:
            self.log(f"Technology Type Options screen returned no input; return: {result}.")
            self._show_main_screen()
            return 200
        elif isinstance(result, (int, str)):
            if result == "back" or result == "":
                self.log(f"Technology Type Options screen cancelled/failed; return: {result}, exiting.")
                self._show_main_screen()
                return 200
            elif isinstance(result, int) and result == 200:
                self.log("Technology Type Options screen returned successfully.")
                self._show_main_screen()
                return 200
            elif isinstance(result, int) and result != 200:
                self.log(f"Technology Type Options screen cancelled/failed; return: {result}, exiting.")
                self.exit(415)
                return 415
            else:
                self.log(f"Technology Type Options screen returned unexpected result: {result}, type: {type(result)}")
                self._show_main_screen()
                return 200
        elif isinstance(result, (list, tuple)):
            self.log(f"Input is a list: {result}, type: {type(result)}")
            if len(result) == 0:
                self._show_main_screen()
                return 200
            self.log(f"Result 0 = {result[0]}")
            if isinstance(result[0], int):
                if result[0] == 200:
                    self.log("Technology Type Options screen returned successfully.")
                self._show_main_screen()
                return result[0]
            elif result[0] == "back":
                self._show_main_screen()
                return 200
            elif len(result) >= 2:
                self.selected_t_option = str(result[0])
                self.selected_t_option_selected = str(result[1])
                self.log(f"Technology Type Options screen returned: {self.selected_t_option} | {self.selected_t_option_selected}")
            else:
                self.selected_t_option = str(result[0])
                self.selected_t_option_selected = ""
        else:
            self.log(f"Technology Type Options screen cancelled/failed; return: {result}, type: {type(result)}.")
            self._show_main_screen()
            return 200

        self.log(f"Selected: {self.selected_t_option} | {self.selected_t_option_selected}")
        if self.selected_t_option == "template":
            await self.push_screen(
                TechnologyTypeTemplatesScreen(
                    self.user_name,
                    self.karma_points,
                    self.tech_type_name,
                    self.tech_type_description,
                    self.selected_t_option,
                    self.selected_t_option_selected,
                    self.tech_type_templates,
                ),
                callback=self.tech_type_templates_callback,
            )
        elif self.selected_t_option == "process":
            await self.push_screen(
                TechnologyTypeProcessesScreen(
                    self.user_name,
                    self.karma_points,
                    self.tech_type_name,
                    self.tech_type_description,
                    self.selected_t_option,
                    self.selected_t_option_selected,
                    self.tech_type_processes,
                ),
                callback=self.tech_type_processes_callback,
            )
        else:
            self.log(f"Technology Type Options screen returned invalid option: {self.selected_t_option_selected}")
            self.exit(416)
        return 200

    async def fetch_technology_types(self) -> int:
        self.tech_type_list = [{}]
        try:
            self.autoc = AutomatedCuration(self.view_server, self.platform_url, self.user_name, self.user_password)
            self.autoc.create_egeria_bearer_token(self.user_name, self.user_password)
            # retrieve the tech type data
            self.log("Fetching technology type hierarchy for tech_type='*'")
            self.tech_type_response = await self.autoc._async_get_tech_type_hierarchy(filter_string="*")
        except Exception as e:
            self.log(f"Exception in get_tech_type_hierarchy: {e}")
            self.log(print_basic_exception(e))
            self.tech_type_list = [{}]
            self.exit(416)
            return 416

        self.log(f"tech_type_response: {self.tech_type_response}")
        # Copy the data into a working variable for the extraction routine
        self.tech_type_list = self.tech_type_response
        return 200

    def unpack_egeria_data(self) -> int:
        """Unpack the data returned from Egeria."""
        output_data: list[dict] = []
        if isinstance(self.tech_type_data, dict):
            if "data" in self.tech_type_data:
                output_data = self.tech_type_data.get("data")
            else:
                output_data = [self.tech_type_data]
        elif isinstance(self.tech_type_data, list):
            for entry in self.tech_type_data:
                if isinstance(entry, dict):
                    output_data = entry.get("data")
                elif isinstance(entry, list):
                    for subentry in entry:
                        if isinstance(subentry, dict):
                            output_data = [subentry]
                        else:
                            self.log("error unknown data structure for Tech Type data")
                            return 417
                else:
                    self.log("error unknown outer data structure for Tech Type data")
                    return 417
        else:
            self.log("Tech Type data not dict or list")
            return 417

        self.log(f"output_data: {output_data}, {type(output_data)}")
        self.tech_type_list = output_data
        return 200

    def tech_type_templates_callback(self, result: Any) -> Any:
        """Callback for Technology Type Templates screen.

        result contains up to 3 elements:
        [0] = return code or 'input', [1] input data, [2] full template
        """
        self.log(f"Technology Type Templates screen returned: {result}")
        if isinstance(result, int):
            self.log(f"Technology Type Templates screen returned: {result}, exiting.")
            return result
        if not result or not isinstance(result, (list, tuple)) or len(result) < 3 or result[0] != "input":
            self.log(f"Technology Type Templates screen cancelled/failed; return: {result}, exiting.")
            return 418

        if isinstance(result[2], dict):
            self.full_template = result[2]
        else:
            self.full_template = {}

        my_placeholderPropertyValues: dict = {}
        if isinstance(result[1], dict):
            self.placeholder_input = result[1]
        else:
            self.placeholder_input = {}

        if isinstance(self.placeholder_input, dict):
            for input_item, input_value in self.placeholder_input.items():
                self.log(f"input_item: {input_item}, input_value: {input_value}")
                input_fix1 = input_item.replace("_", " ")
                self.log(f"input_item after underscore removal: {input_fix1}")
                input_fix2 = input_fix1.replace(" placeholder input", "")
                self.log(f"input_item after placeholder removal: {input_fix2}")
                self.log(f"fixed input_item: {input_fix2}, {input_value}")
                my_placeholderPropertyValues[input_fix2] = input_value
        else:
            self.log(f"placeholder_input is not a dict: {self.placeholder_input}")
            return 419

        self.log(f"my_placeholderPropertyValues: {my_placeholderPropertyValues}")
        self.log(f"self.placeholder_input: {self.placeholder_input}")
        self.log(f"self.full_template: {self.full_template}")

        request_body: dict = {
            "class": "TemplateRequestBody",
            "externalSourceGUID": self.full_template.get("externalSourceGUID") or "",
            "externalSourceName": self.full_template.get("externalSourceName") or "",
            "typeName": self.full_template.get("typeName") or "",
            "templateGUID": self.full_template.get("Catalog Template GUID"),
            "anchorGUID": self.full_template.get("anchorGUID"),
            "isOwnAnchor": "false",
            "effectiveFrom": "2026-01-01",
            "effectiveTo": "2030-12-31",
            "replacementProperties": self.full_template.get("replacementProperties") or {},
            "placeholderPropertyValues": {},
            "parentGUID": None,
            "parentRelationshipTypeName": None,
            "parentRelationshipProperties": None,
            "parentAtEnd1": self.full_template.get("parentAtEnd1") or True,
            "effectiveTime": self.full_template.get("effectiveTime") or datetime.datetime.now().isoformat(),
        }
        self.log(f"request_body: {request_body}")
        for key, value in my_placeholderPropertyValues.items():
            request_body["placeholderPropertyValues"][key] = value
        self.log(f"request_body after update: {request_body}")

        try:
            tokendata = self.autoc.create_egeria_bearer_token(self.user_name, self.user_password)
            my_md_instance = AutomatedCuration(self.view_server, self.platform_url, self.user_name, self.user_password, tokendata)
            new_guid = my_md_instance.initiate_gov_action_process(body=request_body)
        except Exception as e:
            self.log(f"Exception in create_element_from_template: {e}")
            if isinstance(e, PyegeriaException):
                self.log(print_basic_exception(e))
            else:
                self.log(f"Exception in create_element_from_template: {e}")
            self.push_screen(StatusScreen(f"Error creating element from Template\n{print_basic_exception(e)}"), callback=self.status_callback)
            return 420

        self.log(f"new_guid: {new_guid}")
        self.push_screen(StatusScreen(f"Element created from Template/Metadata element created with GUID: '{new_guid}'"), callback=self.status_callback)

    def tech_type_processes_callback(self, result: Any) -> Any:
        """Callback for Technology Type Processes screen."""
        self.log(f"Technology Type Processes screen returned: {result}")
        if isinstance(result, int):
            self.log(f"Technology Type Processes Screen returned: {result}, exiting.")
            return result

        if not result or not isinstance(result, (list, tuple)) or len(result) < 3 or result[0] != "input":
            self.log(f"Technology Type Processes screen cancelled or failed; return: {result}, exiting.")
            error_category = "Governance Action Process"
            error_message = f"Unknown response from TechnologyTypeProcessesScreen: {result}"
            self.log(f"Error retrieving process details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return 418

        self.type = result[0]
        self.input_data = result[1]
        self.full_process = result[2]
        self.result = result
        self.log(f"Received process type: {self.type}, data: {self.input_data}, full process: {self.full_process}")

        my_process_property_values: list[dict] = []
        if isinstance(self.input_data, dict):
            for input_key, input_value in self.input_data.items():
                self.log(f"Processing input value: {input_key} with value: {input_value}")
                input_fix1 = input_key.replace("_", " ")
                input_fix2 = input_fix1.replace(" placeholder input", "").replace(" process input", "")
                self.log(f"Process input key after cleaning: {input_fix2}")
                my_process_property_values.append({
                    "class": "SupportedRequestParameter",
                    "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
                    "name": input_fix2,
                    "value": input_value,
                    "Description": "",
                    "dataType": "string",
                    "example": "",
                    "required": "False"
                })
        else:
            self.log("No process Request Parameter input data returned, this is possibly valid, but unlikely")
            self.log(f" Input data type: {type(self.input_data)}, data: {self.input_data}")
            self.log("Processing will proceed with no Supported Request Parameters for the process")

        self.log(f"Process property values: {my_process_property_values}")
        self.log(f"Original input: {self.result}")
        self.log(f"full process: {self.full_process}")

        additional_properties = self.full_process.get("additionalProperties", {}) if isinstance(self.full_process, dict) else {}
        template_guid = additional_properties.get("templateGUID") if isinstance(additional_properties, dict) else None

        request_body: dict = {
            "displayName": self.full_process.get("displayName") if isinstance(self.full_process, dict) else None,
            "description": self.full_process.get("description") if isinstance(self.full_process, dict) else None,
            "additionalProperties": {
                "templateGUID": template_guid
            },
            "specification": {
                "supportedRequestParameter": my_process_property_values
            }
        }

    def tech_type_processes_details(self, tech_type: Any, selected_t_option_selected: Any) -> Any:
        """Retrieve process data for Technology Type Processes screen."""
        self.type = None
        self.full_process = None
        self.selected_q_name = None
        required_process = None
        self.type = str(tech_type)
        self.selected_q_name = str(selected_t_option_selected)
        self.log(f"Received process type: {self.type}, selected: {self.selected_q_name}")

        if self.selected_q_name is not None:
            self.log(f"Selected qualified name: {self.selected_q_name}")
            try:
                p_client = AutomatedCuration(self.view_server, self.platform_url, self.user_name, self.user_password)
                token = p_client.create_egeria_bearer_token(self.user_name, self.user_password)
                governance_actions = p_client.get_tech_type_detail(filter_string=self.selected_q_name, output_format="JSON")
            except PyegeriaException as e:
                print_basic_exception(e)
                error_category = "Technology Type Process Detail Retrieval"
                error_message = f"Failed to retrieve technology type process details for {self.selected_q_name}: {str(e)}"
                self.log(f"Error retrieving technology type details: {error_category}, {error_message}")
                self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            self.log(f"Egeria returned: {governance_actions}, type: {type(governance_actions)}")
            if isinstance(governance_actions, str):
                if governance_actions != "No elements found":
                    technology_response = json.loads(governance_actions)
                else:
                    technology_response = None
            else:
                technology_response = governance_actions

            self.log(f"Tech type process data retrieved: {technology_response}")
            self.governance_action_processes = technology_response.get("governanceActionProcesses", []) if technology_response else []
            self.log(f"Retrieved {len(self.governance_action_processes)} governance action processes for {self.selected_q_name}")
            self.log(f"Data: {self.governance_action_processes}")
            for process in self.governance_action_processes:
                self.log(f"Process: {process['name']}, Description: {process['description']}")
                if process['name'] == self.selected_q_name:
                    self.log(f"Found requested process: {process['description']}")
                    required_process = process
                    break
            return required_process
        else:
            self.log(f"selected_q_name in process_details function is None, returnng None to caller: {self.selected_q_name}")
            return None

""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.

    This file is being used to test some display layout options
    This is a test file to explore different ways to display Egeria data
    Author: Peter Coldicott, November 2025

    This version is to test having the user input required parameters to run
    customized reports

"""

import os
import re
import sys

from rich.text import Text

from textual.css.query import NoMatches
from textual.widget import WidgetError, MountError

# Ensure we're using the local pyegeria, not an installed version
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from loguru import logger

from commands.cat.run_report import list_generic
from pydantic import ValidationError
from textual import on
from textual.app import App
from textual.containers import Container, Horizontal, ScrollableContainer, HorizontalScroll
from textual.widgets import Static, Button, DataTable, Header, Footer, Input, Tree, Label


class MyApp(App):
    CSS_PATH = "./my_reports.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctl+e", "expand", "Toggle Twisties"),
        ("r", "report", "Run"),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.selected_report_spec: str = ""
        self.items: list = []
        self.created_inputs: list[Input] = []
        self.inputs_tracker: dict[str, list] = {}
        self.snode_label: str = ""
        # Holds rotated data as column -> list of row values
        self.rotated_table: dict[str, list[str]] = {}
        self.node_status: str = "Expanded"
        self.node_id: str = ""
        self.additional_parameters = {}
        self.selected_name: str = ""

    def compose(self):
        # compose the main screen (_default)
        self.title = "My_Egeria"
        self.sub_title = "Report Specification Details"
        yield Header()
        yield Container(
            Static("Start of report specification list:", id="one_start"),
            Tree(label="Report Specs", id="spec_tree", classes="trees"),
            # Static("End of report specification list:", id="one_end"),
            id="container1", classes="box")
        yield Container(
            Static("Report Specification Details", classes="box", id="two_start"),
            DataTable(id="spec_extracted_datatable"),
            Static("End of Report Specification Details", classes="box", id="two_end"),
            id="container2", classes="box")
        yield ScrollableContainer(
            Static("Report Specs Input Fields", classes="box", id="four_start"),
            Container(id="input_fields"),
            Static("End of Report Specs Input Fields", classes="box", id="four_end"),
            id="container4", classes="box")
        yield ScrollableContainer(
            Static("Report Specification Output)", classes="box", id="three_start"),
            DataTable(id="spec_output_datatable"),
            Static("End of Report Specification Output)", classes="box", id="three_end"),
            id="container3", classes="box")
        yield Footer()

    def on_mount(self):
        # Import the report specifications list function here after path is set
        try:
            from pyegeria.view.base_report_formats import report_spec_list
        except ImportError:
            # If import doesnt work we have a problem!
            raise ImportError("Unable to import report_spec_list from pyegeria.base_report_formats")

        # Find the address of the Tree to hold the structured report specifications
        self.spec_tree = self.query_one("#spec_tree", Tree)
        # Ensure the tree is empty before we load it with values
        self.spec_tree.clear()
        # Provide the data to be associated with the tree root
        root_data = "A categorized list of PyEgeria report specifications"
        self.spec_tree.root.expand()
        # Set the label and data for the tree root
        self.spec_tree.root.label = "Report Specs"
        self.spec_tree.root.data = root_data
        tree_root = self.spec_tree.root
        # self.family is used to track the family (organizing) node that the specs will sit under
        self.family: str = ""
        self.heading = "Report Specs"
        self.subheading = "Select a report spec to execute:"
        self.description = "A list of report specifications, click on one to see its attributes\ns key to run"

        # Attempt to retrieve the report specification list
        try:
            self.report_spec_list: list = report_spec_list(show_family=True, sort_by_family=True, return_kind="dicts")
            logger.debug(f"report_spec_list: {self.report_spec_list}, type: {type(self.report_spec_list)}")
        except Exception as e:
            logger.debug(f"Error getting report_spec_list: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self.report_spec_list = []
        #  find the address of the Tree to hold the structured report specifications
        family_node = self.query_one("#spec_tree", Tree).select_node(tree_root)
        # for each report specification in the list, add it to the tree
        for spec in self.report_spec_list:
            # if this spec is from a new family, create a new family node under the root
            if spec.get("family") != self.family:
                self.family = spec.get("family")
                family_node = tree_root.add_leaf(self.family, data="family_name")
                family_node.expand()
                family_node.add(spec.get("name"), data=spec.get("description"))
                continue
            else:
                # not a new family so just add the spec under the active family node
                family_node.add_leaf(spec.get("name"), spec.get("description"))
                continue
        # make sure everything is visible and showing on the screen
        self.spec_tree.root.expand_all()
        self.spec_tree.refresh()
        return

    # @on(Tree.NodeSelected, "#spec_tree")
    # when the user clicks on a node in the tree
    async def on_tree_node_selected(self, event: Tree.NodeSelected):
        logger.debug(f"Node Selected: {event.node.label} {event.node.data}")
        self.log(f"Node Selected: {event.node.label} {event.node.data}")
        # capture the event data
        snode = event.node
        snode_label: str = event.node.label
        snode_data:str = event.node.data
        self.selected_report_spec = str(event.node.label)
        self.snode_label = snode_label.plain
        logger.debug(f"selected_report_spec: {self.selected_report_spec}")

        # Process the selected node
        if snode_label == "Report Specs":
            # first time through, no node really selected yet, I think this is
            # triggered by the expanding of the tree nodes, not by a user selection
            return

        if not snode_label:
            # error condition, no node data, so we will default to the parent node if possible
            snode = event.node.parent
            self.log(f"snode not found, so set to parent: {snode}, parent data: {event.node.parent}")
            snode_label = event.node.parent.label
            # However if the parent node is the root there is no report spec to process
            if snode_label == "Report Specs":
                # if the parent node is the tree root, we are done,
                # as there are no report specs associated with the tree root node
                return

        logger.debug(f"snode: {snode}", type(snode))
        self.log(f"Selected node: {snode}")
        self.log(f"Selected node data: {snode_data}")
        self.log(f"Selected node label: {snode_label}")

        # address input fields container so we can clear it from prior selections
        try:
            inputs_container = self.query_one("#input_fields", Container)
            # make sure the input data has a report spec name, if not use the data attached instead
            if not snode_label:
                self.log(f"snode.label not found: {snode_label}")
                snode_label = str(snode.data)
                logger.debug(f"snode_label: {snode_label}", type(snode_label))
                # Clear previous rows
                try:
                    self.created_inputs: list[Input] = []
                    # Remove the input_fields container (along with its children) from the DOM
                    # effectively deleting the container and all its children
                    await inputs_container.remove()
                except WidgetError:
                    # assume this is first time through and container is not yet created
                    pass
                except Exception as e:
                    # if this is first time through there is validly no container to clear
                    # but if not trapped by the WidgetError this is likely a program logic error
                    logger.debug(f"Exception clearing inputs container: {e}")
                    raise Exception(f"Exception clearing inputs container: {e}")
        except NoMatches:
            # the inputs_container (input_fields) not found, create it
            logger.debug(f"NoMatches: No inputs container found")
            self.log(f"NoMatches: No inputs container found")
            try:
                # find the container4 which the inputs container will be mounted into
                container4 = self.query_one("#container4", ScrollableContainer)
            except NoMatches:
                # no container4 found, create one, this is most probably due to a logic error
                self.log(f"No container4 found, creating one!")
                container4 = ScrollableContainer(id="container4")
                await container4.mount(after="container2")
            # create the inputs container and mount it into container4
            inputs_container: Container = Container(id="input_fields")
            await container4.mount(inputs_container)

        # Check that we are not dealing with the root node of the tree,
        # The root node has no report specifications associated with it
        self.log(f"inputs_container: {inputs_container}, snode_label: {snode_label}")
        if isinstance(snode_label, Text):
            # sometimes the string variable we get back from pyegeria is actually a rich.text.Text object
            # if so we need to render it as a simple python str variable, using text_variable.plain
            self.log(f"snode_label is Text: {snode_label}, type: {type(snode_label)}")
            snode_label = snode_label.plain
            self.log(f"snode_label is now str: {snode_label}, type: {type(snode_label)}")
        if snode_label == "Report Specs":
           return

        # Get the details of the selected report spec
        await self.get_named_report_spec_details(snode_label)

        # Create user helper to display on the screen for output_format input field
        outlabel = Label("Output Format: DICT to display report on screen, FORM to write to file", id="comment1")

        # only mount the helper if the report spec allows selection of the output format
        try:
            if "DICT" or "FORM" in self.inputs_tracker:
                await inputs_container.mount(outlabel)
        except MountError:
            # if we experience an error, there may already be a helper with the same name,
            # if so remove it and retry the mount
            try:
                comment1 = self.query_one("#comment1", Label)
                await comment1.remove()
                inputs_container.refresh()
                await inputs_container.mount(outlabel)
                inputs_container.refresh()
            except WidgetError as werr:
                # this is just a problem mounting the label so we will log, ignore and continue
                logger.debug(f"WidgetError mounting output label: {werr}")
                pass
        except Exception as e:
            logger.debug(f"Exception mounting output label: {e}")
            # this is just a problem mounting the label so we will log, ignore and continue
            pass

        return

    async def get_named_report_spec_details(self, name):
        """Get the details of a named report spec and render as a flat table."""
        self.spec_name: str = name
        if not self.spec_name:
            # what to do if I get here with no report spec name?
            raise ValueError("Report spec name cannot be empty")
        # Just in time import the select_report_spec function from pyegeria.base_report_formats
        try:
            from pyegeria.view.base_report_formats import select_report_spec
            self.log(f"select_report_spec imported from pyegeria.base_report_formats")
        except NameError:
            # the required import function name isnt recognized
            logger.debug(f"Unable to import select_report_spec from pyegeria.base_report_formats")
            raise NameError("Unable to import select_report_spec from pyegeria.base_report_formats")
        except ImportError:
            # we assume that this is because the imported name is already imported
            pass
        logger.debug(f"get_named_report_spec_details: {self.spec_name} type: {type(self.spec_name)}")
        self.log(f"Getting details for report spec: {self.spec_name}, type: {type(self.spec_name)}")
        # retrieve the report specification selected by the user
        self.selected_report_spec = select_report_spec(self.spec_name, output_type="DICT")
        logger.debug(f"selected_report_spec: {self.selected_report_spec}, type: {type(self.selected_report_spec)}")
        self.log(f"selected_report_spec: {self.selected_report_spec}, type: {type(self.selected_report_spec)}")
        # if a report spec is not returned
        if self.selected_report_spec == None:
            # Set the selected report spec variable to indicate a report spec was not found
            self.selected_report_spec = {"NoDetails": "No details found for selected report spec"}
        # Normalize the shape of the returned spec → always a dict
        # but it may be contained as an element in a higher level construct (", data: ....)
        if isinstance(self.selected_report_spec, dict) and "data" in self.selected_report_spec:
            # retrieve the dict data inside "data"
            self.extracted_report_spec: dict = self.selected_report_spec.get("data") or {}
        elif isinstance(self.selected_report_spec, dict):
            # just use the dictionary or set to empty dict if not found at all
            self.extracted_report_spec: dict = self.selected_report_spec or {}
        else:
            # not a dict, this is an error or perhaps due to a change in pyegeria
            error_text = f"Unknown shape: {self.selected_report_spec}"
            self.extracted_report_spec = {"Error": error_text}

        logger.debug(f"extracted_report_spec: {self.extracted_report_spec}, type: {type(self.extracted_report_spec)}")
        self.log(f"extracted_report_spec: {self.extracted_report_spec}, type: {type(self.extracted_report_spec)}")

        # place into a working structure for local processing
        response_data = self.extracted_report_spec
        # Access the datatable used to display report specification attributes
        self.spec_attribute_datatable = self.query_one("#spec_extracted_datatable", DataTable)
        # Ensure columns exist only once by clearing the datatable and then recreating columns, etc.
        self.spec_attribute_datatable.clear(columns=True)
        self.spec_attribute_datatable.add_columns("Attribute", "Value", "Extended Values")
        self.spec_attribute_datatable.border = True
        self.spec_attribute_datatable.zebra_stripes = True
        self.spec_attribute_datatable.cursor_type = "row"
        self.spec_attribute_datatable.refresh()
        # check the working data has actually got content
        if not response_data:
            response_data = {"NoData": "No data found for selected item"}
        # process the response data and add rows to the datatable for each parameter
        if isinstance(response_data, list):
            # if reponse data contains a list of dicts
            for list_item in response_data:
                # process each list item
                response_data_item: dict = list_item
                logger.debug(f"list_item: {list_item}")
                if isinstance(response_data_item, dict):
                    # if the list item itself contains a dict, process it
                    for key, value in response_data_item.items():
                        logger.debug(f"key: {key}, value: {value}")
                        # check for report spec parms that the use may or has to provide
                        if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                            # if that dict item has parameters that may or must have input, process them
                            logger.debug(f"Executing populate_input_fields for key: {key}")
                            # populate the input fields area of the screen, one name and input area for each parameter
                            await self.populate_input_fields(key, value)
                            logger.debug(f"populate_input_fields completed for key: {key}")
                        logger.debug(f"key: {key}, value: {value}")
                        if isinstance(value, dict):
                            # if the data for that item is a dict, then process it
                            for vkey, vvalue in value.items():
                                if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                                    logger.debug(f"Executing populate_input_fields for key: {vkey}")
                                    await self.populate_input_fields(vkey, vvalue)
                                    logger.debug(f"populate_input_fields completed for key: {vkey}")
                                logger.debug(f"vkey: {vkey}, vvalue: {vvalue}")
                                self.spec_attribute_datatable.add_row(vkey, vvalue)
                                continue
                        elif isinstance(value, list):
                            # if the data for that item is a list, process it
                            for v in value:
                                logger.debug(f"v: {v}")
                                self.spec_attribute_datatable.add_row(key, v)
                                continue
                        elif key == "kind" and value == "empty":
                            # the dict is just saying there is no report specification data available
                            key_str = "No Data"
                            value_str = "For That Asset Type in this repository"
                            logger.debug(f"key_str: {key_str}, value_str: {value_str}")
                            self.spec_attribute_datatable.add_row(key_str, value_str)
                            continue
                        else:
                            # regular item, just process
                            logger.debug(f"else: key {key} value: {value}")
                            self.spec_attribute_datatable.add_row(key, value)
                            continue
        elif isinstance(response_data, dict):
            # if reponse data contains a dict, rather than a list of dicts
            # processing is the same as the previous code segment for list of dicts
            for key, value in response_data.items():
                logger.debug(f"key: {key}, value: {value}")
                if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                    logger.debug(f"Executing populate_input_fields for key: {key}")
                    await self.populate_input_fields(key, value)
                    logger.debug(f"populate_input_fields completed for key: {key}")
                if isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                            logger.debug(f"Executing populate_input_fields for key: {vkey}")
                            await self.populate_input_fields(vkey, vvalue)
                            logger.debug(f"populate_input_fields completed for key: {vkey}")
                        self.spec_attribute_datatable.add_row(vkey, vvalue)
                        continue
                elif isinstance(value, list):
                    for v in value:
                        self.spec_attribute_datatable.add_row(key, v)
                        continue
                elif key == "kind" and value == "empty":
                    key_str = "No Data"
                    value_str = "For That Asset Type in this repository"
                    self.spec_attribute_datatable.add_row(key_str, value_str)
                    continue
                else:
                    self.spec_attribute_datatable.add_row(key, value)
                    continue
        # now the rows are added, refresh the datatable
        self.spec_attribute_datatable.refresh()
        # get the address of the container for the table of parameters
        mount_point = self.query_one("#container2", Container)
        # mount the table into the container
        await mount_point.mount(self.spec_attribute_datatable, before="#two_end")
        return

    async def execute_selected_report_spec(self, selected_name: str, additional_parameters: dict = None):
        """ execute the selected report spec """
        self.log(f"execute_selected_report_spec: {selected_name}, {additional_parameters}")
        try:
            from pyegeria.view.format_set_executor import exec_report_spec
        except NameError:
            self.log(f"Name Error Unable to import exec_report_spec from pyegeria.format_set_executor")
            raise NameError("Unable to import exec_report_spec from pyegeria.format_set_executor")
        except ImportError:
            # I assume that this is because the imported name is already imported
            self.log(f"Import Error Unable to import exec_report_spec from pyegeria.format_set_executor")
            self.log(f" Code assumes that this is because the imported name is already imported")
            self.log(f" If this is not the case, then the run report will fail")
            pass
        # create working variable for the data passed in
        self.selected_name:str = str(selected_name)
        self.additional_parameters = additional_parameters
        # set the default for the output format to DICT, which displays the report on the screen
        output_form = "DICT"
        # check if additional parameters have been provided
        if len(self.additional_parameters) > 0:
            logger.debug(f"additional_parameters: {self.additional_parameters}")
            for key, value in self.additional_parameters.items():
                # check if the values are string True or False, if so convert to boolean
                if value == "True" or value == "False":
                    self.additional_parameters[key] = bool(value)
                if value == "":
                    logger.debug(f"value is empty string, deleting key: {key}")
                    del self.additional_parameters[key]
                continue
            self.log(f"additional_parameters: {self.additional_parameters}")
        else:
            # if no additional parameters have been provided, ensure the table is empty
            logger.debug(f"No additional parameters provided")
            self.additional_parameters = {}
        if self.additional_parameters:
            # where we have additional parameters, check for the output format parameter which is
            # issued separately in the call to pyegeria
            self.log(f"additional_parameters: {self.additional_parameters}")
            if "output_format" in self.additional_parameters:
                output_form: str = str(self.additional_parameters["output_format"], "DICT")
                del self.additional_parameters["output_format"]
            self.log(f"additional_parameters: {self.additional_parameters}, output_form: {output_form}")
            for key, value in self.additional_parameters.items():
                logger.debug(f"key: {key}, value: {value}")
                if not value:
                    logger.debug(f"value is empty, deleting key: {key}")
                    del self.additional_parameters[key]

        # self.additional_parameters.update({"page_size": 23})
        self.log(f"output_form: {output_form}, type: {type(output_form)}, length: {len(output_form)}")
        logger.debug(f"Executing report spec: {self.selected_name} with output format: {output_form}")
        logger.debug(f"additional_parameters: {self.additional_parameters}")

        self.log(f"output form: {output_form}")
        self.log(f"format set name: {self.selected_name}, additional parameters: {self.additional_parameters}")
        self.log(f"view server: {self.view_server}, platform_url: {self.platform_url}")
        self.log(f"user: {self.user}, password: {self.password}")
        if len(output_form) > 0:
            try:
                # run the report spec with the output format specified in the regular parameter list
                response = exec_report_spec(format_set_name=self.selected_name,
                                            output_format=output_form,
                                            params=self.additional_parameters,
                                            view_server=self.view_server,
                                            view_url=self.platform_url,
                                            user=self.user,
                                            user_pass=self.password
                                            )
            except (ValidationError) as e:
                logger.debug(f"ValidationError: {e}")
                response = {"error": f"ValidationError: {e}"}
            except Exception as e:
                logger.debug(f"Exception: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                response = {"error": f"Exception: {e}"}
        else:
            try:
                # run the report spec without the output format specified in the regular parameter list
                response = exec_report_spec(format_set_name=self.selected_name,
                                            params=self.additional_parameters,
                                           view_server=self.view_server,
                                           view_url=self.platform_url,
                                           user=self.user,
                                           user_pass=self.password,
                                           )
                logger.debug(f"Return from exec_report_spec:")
                logger.debug(f"reponse: {response}")
            except (ValidationError) as e:
                logger.debug(f"ValidationError: {e}")
                response = {"error": f"ValidationError: {e}"}
            except Exception as e:
                logger.debug(f"Exception: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                response = {"error": f"Exception: {e}"}
        self.log(f"response: {response}")
        # hand the response from the report spec execution to the display_response function
        await self.display_response(response)
        return

    async def display_response(self, response):
        """ Display the response from executing the selected report spec"""
        # make a working copy of the provided response
        self.response = response
        try:
            # create and/or clear datatable for displaying data
            self.spec_output_datatable = self.query_one("#spec_output_datatable", DataTable)
            self.spec_output_datatable.clear(columns=True)
            logger.debug(f"self.spec_output_datatable : {self.spec_output_datatable} has been created")
            logger.debug(f"self.spec_output_datatable has been assigned an id : {self.spec_output_datatable.id} ")
        except NoMatches:
            logger.debug(f"No datatable found with id 'spec_output_datatable'")
            self.spec_output_datatable = DataTable(id="spec_output_datatable")
            logger.debug(f"self.spec_output_datatable did not exist and has been created")

        # extract data payload from response["data"]. Then populate variables for display
        if isinstance(self.response, dict) and "data" in self.response:
            # the most likely format
            self.response_data = self.response.get("data")
            self.log(f"response_data is dict with data key: {self.response_data}")
        elif isinstance(self.response, dict):
            # just in case the data is not contained in a "data" key
            self.response_data = self.response
            self.log(f"response_data is dict without data key: {self.response_data}")
        elif isinstance(self.response, list):
            # just in case the data is returned as a list of dicts
            self.response_data = self.response
            self.log(f"response_data is list: {self.response_data}")
        else:
            # no data returned, at least in an expected format
            self.response_data = [{"NoData": "No data found for selected item", "Data Content": self.response}]
            self.log(f"response_data is not a dict or list: {self.response_data}")
        # The data will be returned with each set of data in a "vertical" format
        # for display purposes we need to "rotate" it into a horizontal format
        # so we need a table to hold the rotated data
        self.rotated_table.clear()
        # now, depending on which format data we got, process it
        if isinstance(self.response_data, list):
            for list_item in self.response_data:
                # process data in a list
                response_dict = list_item if isinstance(list_item, dict) else {"Value": list_item}
                logger.debug(f"list_item: {list_item}")
                self.log(f"processing list item: {list_item}, type: {type(list_item)}")
                for key, value in response_dict.items():
                    # for each item in the list, process the key and value
                    logger.debug(f"key: {key}, value: {value}")
                    self.log(f"processing key: {key}, value: {value}, type: {type(value)}")
                    if key == "kind" and value == "empty":
                        # this identifies a dict that contains no data
                        key_str: str = "NoData"
                        message: str = "For That Report Type and selected options in this repository"
                        logger.debug(f"key_str: {key_str}, value_str: {message}")
                        # Present a single consolidated message row under NoData
                        self.rotated_table[key_str] = [message]
                        continue
                    elif isinstance(value, dict):
                        # if the value is a dict, process it
                        for vkey, vvalue in value.items():
                            # we use the key to access the rotated table and append the value to that entry
                            logger.debug(f"vkey: {vkey}, vvalue: {vvalue}")
                            self.log(f"processing dict items within list: vkey: {vkey}, vvalue: {vvalue}")
                            self.rotated_table.setdefault(str(vkey), []).append(vvalue)
                            continue
                    elif isinstance(value, list):
                        # if the value is a list, process it
                        for v in value:
                            logger.debug(f"v: {v}")
                            # create an entry for each item in the list with no associated value
                            self.rotated_table.setdefault(str(v), []).append(" ")
                            continue
                    elif key == "kind" and value == "empty":
                        # this identifies a dict that contains no data
                        key_str: str = "NoData"
                        message: str = "For That Asset Type in this repository"
                        logger.debug(f"key_str: {key_str}, value_str: {message}")
                        # Present a single consolidated message row under NoData
                        self.rotated_table[key_str] = [message]
                        continue
                    else:
                        logger.debug(f"else: key {key} value: {value}")
                        # just process the item as a dict and use its key and value to add to the rotated table
                        self.rotated_table.setdefault(str(key), []).append(value)
                        continue
        elif isinstance(self.response_data, dict):
            # process data in a dict, similar option and processing as previous code segment
            for key, value in self.response_data.items():
                logger.debug(f"key: {key}, value: {value}")
                itexists = self.rotated_table.get(str(key), None)
                if itexists != None:
                    itexists = None
                    continue
                if key == "kind":
                    continue
                elif isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        self.rotated_table.setdefault(str(vkey), []).append(vvalue)
                        continue
                elif isinstance(value, list):
                    for v in value:
                        self.rotated_table.setdefault(str(v), []).append(" ")
                        continue
                elif key == "kind" and value == "empty":
                    key_str = "NoData"
                    message = "For That Asset Type in this repository"
                    logger.debug(f"key_str: {key_str}, value_str: {message}")
                    # Present a single consolidated message row under NoData
                    self.rotated_table[key_str] = [message]
                    continue
                else:
                    self.rotated_table.setdefault(str(key), []).append(value)
                    continue
        # now the rotated table is loaded with data, create the datatable
        keys = list(self.rotated_table.keys())
        self.log(f"rotated table keys: {keys}")
        for col_key in keys:
            # use the keys from the rotated table to create columns in the data table
            self.spec_output_datatable.add_column(str(col_key))
            continue
        # calculate the number of rows (columns in the rotated table)
        max_rows: int = max((len(self.rotated_table[k]) for k in keys), default=0)
        # correct the number since index origin starts at zero not one!
        max_rows = max_rows - 1
        for row_idx in range(max_rows):
            # use the values from the rotated table to populate the data table rows
            row = [str(self.rotated_table[k][row_idx]) if row_idx < len(self.rotated_table[k]) else "" for k in keys]
            self.spec_output_datatable.add_row(*row)
            continue
        # Always refresh after populating
        mount_point = self.query_one("#container3", ScrollableContainer)
        await mount_point.mount(self.spec_output_datatable, before="#three_end")
        self.spec_output_datatable.refresh()
        return

    async def populate_input_fields(self, key, value):
        """Create interactive input rows for required/optional params."""
        def safe_id(s: str) -> str:
            # inner function to create a safe id from a string
            return re.sub(r"[^0-9a-zA-Z_-]", "_", s)
        # create working copies of provided variables
        self.key = key
        self.input = value
        # process the provided data
        try:
            # get container address for the input fields
            inputs_container = self.query_one("#input_fields", Container)
            if inputs_container:
                await inputs_container.remove()
                inputs_container: Container = Container(id="input_fields")
                await self.query_one("#container4", ScrollableContainer).mount(inputs_container, before="#four_end")
        except NoMatches:
            # if we dont find the container create one
            logger.debug(f"No container found with id 'input_fields'")
            inputs_container: Container = Container(id="input_fields")
            logger.debug(f"input_fields container has been created")
            # find the outside container for the input fields and mount the new container inside it
            await self.query_one("#container4", ScrollableContainer).mount(inputs_container, before="#four_end")
        # Build rows according to incoming shape
        if isinstance(self.input, dict):
            # some input items have either dicts inside them or lists,
            # here we process the dict versions firstly by making a list of the dict items
            items = list(self.input.items())
            for ikey, ivalue in items:
                # then for each item we create a (safe) row id and use it to create an input "row" using the
                # HorizontalScroll container from Textual so that the Parameter Name and Input field
                # will be aligned beside each other on the screen
                row_id = f"input_row_{safe_id(str(ikey))}"
                row = HorizontalScroll(id=row_id, classes="spaced")
                try:
                    # try and mount the row into the inputs container
                    await inputs_container.mount(row)
                    # mount the parameter name into the row
                    await row.mount(Label(f"{ikey}:"))
                except MountError as e:
                    # if we get mount errors
                    logger.debug(f"MountError: {e}")
                    logger.debug(f"Most likely the user has selected a report spec twice and so we have duplicate rows")
                    # so we check to see if the row id already exists in the inputs container
                    duplicate_rows: HorizontalScroll = self.query_one("#"+row_id, HorizontalScroll)
                    # and remove it (and its children) if it does, then retry mounting the row
                    await duplicate_rows.remove()
                    try:
                        await inputs_container.mount(row)
                        await row.mount(Label(f"{ikey}:", classes="spaced"))
                    except Exception as e:
                        logger.debug(f"Failed to mount row or label into row: {e}")
                        # we will ignore this row and move on to the next one
                        continue
                    continue
                # check for and set up default values for some common parameters
                logger.debug(f"Processing input field: {ikey}")
                if ikey == "search_string":
                    inp_value = "*"
                elif ikey == "page_size":
                    inp_value = '0'
                elif ikey == "start_from":
                    inp_value = '0'
                elif ikey == "starts_with":
                    inp_value = "True"
                elif ikey == "ends_with":
                    inp_value = "False"
                elif ikey == "ignore_case":
                    inp_value = "False"
                elif ikey == "output_format":
                    inp_value = "DICT"
                elif isinstance(ivalue, list):
                    inp_value = ",".join(ivalue)
                else:
                    inp_value = ""
                # add the input field to the row
                inp = Input(value=inp_value, placeholder=str(ivalue), id=f"inp_{safe_id(str(ikey))}", classes="spaced")
                await row.mount(inp)
                self.created_inputs.append(inp)
                # Track by input id so events can update values reliably
                self.inputs_tracker[inp.id] = [str(ikey), ""]
        elif isinstance(self.input, list):
            # process the list type, same essential code as the previous code segment
            # Special-case for types: just display info text, types is a synonym for "output format"
            if key == "types":
                row = Horizontal(id=f"input_row_{safe_id(str(key))}")
                await inputs_container.mount(row)
                await row.mount(Label("Output Format:"))
                await row.mount(Input(value="DICT", placeholder="DICT", id=f"inp_{safe_id(str(key))}", classes="spaced"))
            else:
                for list_item in self.input:
                    label = str(list_item)
                    row_id = f"input_row_{safe_id(label)}"
                    row = Horizontal(id=row_id, classes="spaced")
                    try:
                        await inputs_container.mount(row)
                        await row.mount(Label(f"{label}:"))
                    except MountError as e:
                        logger.debug(f"MountError: {e}")
                        logger.debug(f"we have duplicate rows in the table, error, we will ignore all except the first value provided")
                    logger.debug(f"Processing input field: {label}")
                    if label == "search_string":
                        inp_value = "*"
                    elif label == "page_size":
                        inp_value = '0'
                    elif label == "start_from":
                        inp_value = '0'
                    elif label == "starts_with":
                        inp_value = "True"
                    elif label == "ends_with":
                        inp_value = "False"
                    elif label == "ignore_case":
                        inp_value = "False"
                    elif label == "output_format":
                        inp_value = "DICT"
                    else:
                        inp_value = ""
                    if isinstance(inp_value, list):
                        inp_value = ", ".join(inp_value)
                        logger.debug(f"inp_value: {inp_value}")
                    inp = Input(value=inp_value, placeholder="", id=f"inp_{safe_id(label)}", classes="spaced")
                    await row.mount(inp)
                    self.created_inputs.append(inp)
                    # Track with a reasonable parameter name for list entries
                    self.inputs_tracker[inp.id] = [label, ""]
        else:
            # Unknown shape: show a message
            row = Horizontal(id=f"input_row_{safe_id(str(key))}", classes="spaced")
            await inputs_container.mount(row)
            await row.mount(Label(f"Error, Unknown Shape for {key}: {value}"))

        # Give focus to the first input if any
        if self.created_inputs:
            self.created_inputs[0].focus()
        logger.debug(f"inputs_tracker: {self.inputs_tracker}")

        # Refresh the container
        inputs_container.refresh()
        return

    @on(Input.Changed, "#input_fields Input")
    async def handle_input_changed(self, event: Input.Changed) -> None:
        """ Update the tracker whenever an input changes.

        We key the tracker by the actual Input id and store [param_name, value].
        """
        # make working copies of the input variables
        input_id = event.input.id
        value = event.value or ""
        # Initialize if missing (defensive)
        if input_id not in self.inputs_tracker:
            # Default param name falls back to the visible label-less id
            self.inputs_tracker[input_id] = [input_id, value]
        else:
            self.inputs_tracker[input_id][1] = value
        logger.debug(f"Changed: {input_id} -> {value}")
        return

    @on(Button.Pressed, "#quit")
    def handle_quit(self, event: Button.Pressed) -> None:
        # if quit button exit gracefully, - return code 200 is a good return code in Egeria
        self.exit(200)

    def action_quit(self):
        # if quit hot key (see bindings), exit gracefully, - return code 200 is a good return code in Egeria
        self.exit(200)

    @on(Tree.NodeCollapsed)
    def handle_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        # handle the twisty to close a node in the tree
        logger.debug(f"TreeNodeCollapsed: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "collapsed"

    @on(Tree.NodeExpanded)
    def handle_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        # handle the twisty to open a node in the tree
        logger.debug(f"TreeNodeExpanded: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "expanded"

    def action_expand(self):
        # handle the hot key to expand/collapse all nodes in the tree (see bindings)
        self.spec_tree = self.query_one("#spec_tree", Tree)
        if self.node_status == "collapsed":
            self.spec_tree.root.expand_all()
        else:
            self.spec_tree.root.collapse_all()
        return

    async def action_report(self):
        """ Process the input fields and execute the selected report spec either to the screen or to a file
            DICT means to the Screen, FORM means to a file """
        # clear parameter working vars
        self.new_additional_parameters = {}
        self.additional_parameters = {}
        # if the inputs have been created in a prior selection, remove them
        try:
            previous_inputs = self.query_one("#input_fields", Container)
            logger.debug(f"previous_inputs: {previous_inputs}")
            await previous_inputs.remove()
            logger.debug(f"previous_inputs removed")
        except NoMatches:
            logger.debug(f"No previous inputs found")
        # Build additional parameters from current inputs
        if self.inputs_tracker:
            logger.debug(f"self.inputs_tracker: {self.inputs_tracker}")
            for _, (parm_name, parm_value) in self.inputs_tracker.items():
                if parm_value:
                    self.additional_parameters[parm_name] = parm_value
                    continue
        logger.debug(f"additional_parameters: {self.additional_parameters}")
        # run report when input fields completed
        # iterate and strip the inp_ from the front of the key values if present
        for key, value in self.additional_parameters.items():
            new_key:str = key.removeprefix("inp_")
            self.new_additional_parameters.update({new_key: value})

        self.log (f"new_additional_parameters: {self.new_additional_parameters}")
        self.additional_parameters = self.new_additional_parameters
        logger.debug(f"additional_parameters trimmed: {self.additional_parameters}")
        # Retrieve the output_format value
        output_form = self.additional_parameters.get("output_format", None)
        # if the output format variable isnt present, check to see if types is, if not default to DICT
        if not output_form:
            output_form = self.additional_parameters.get("types", "DICT")
        logger.debug(f"output_format: {output_form}")
        self.log(f"output_format: {output_form}, type: {type(output_form)}")
        # if output_format is FORM, we write the report output to a file
        # if not then we execute the report spec and display the output on the screen
        if output_form == "FORM":
            self.log(f"Writing report to file for format: {output_form}, {self.snode_label}, {self.additional_parameters}")
            await self.report_to_file(self.snode_label, self.additional_parameters)
        else:
            self.log(f"Executing report for format: {output_form}, {self.snode_label}, {self.additional_parameters}")
            await self.execute_selected_report_spec(self.snode_label, self.additional_parameters)
        return

    async def report_to_file(self, selected_name: str = "", additional_parameters: dict = None):
        """ execute the selected report spec """
        my_selected_name = selected_name
        my_additional_parameters: dict = additional_parameters
        # set default value for out put option
        output_form = "DICT"
        # check for additional parameters
        if len(my_additional_parameters) > 0:
            logger.debug(f"additional_parameters: {my_additional_parameters}")
            if "output_format" in my_additional_parameters:
                output_form = my_additional_parameters.get("output_format")
                del my_additional_parameters["output_format"]
            else:
                output_form = "FORM"
        else:
            # no additional parameters found
            logger.debug(f"No additional parameters provided")
            my_additional_parameters = {}
        # run the report with the parameters provided
        logger.debug(f"Executing report spec: {my_selected_name}")
        response = None
        try:
            response = list_generic(report_spec=my_selected_name,
                                   output_format=output_form,
                                   view_server=self.view_server,
                                   view_url=self.platform_url,
                                   user=self.user,
                                   user_pass=self.password,
                                   params=my_additional_parameters,
                                   write_file=True
                                )
            logger.debug(f"Return from exec_report_spec:")
            logger.debug(f"reponse: {response}")
        except (ValidationError) as e:
            logger.debug(f"ValidationError: {e}")
            response = {"error": f"ValidationError: {e}"}
        except Exception as e:
            logger.debug(f"Exception: {e}")
            response = {"error": f"Exception: {e}"}
        # the response is either the report itself or if written to a file, some metadata related to that file
        await self.display_response(response)

# program start up cast this way to enable integration with hey_egeria
def start_exp2():
    app = MyApp()
    app.run()

if __name__ == "__main__":
    start_exp2()
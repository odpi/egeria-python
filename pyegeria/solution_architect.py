"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Solution Architect OMVS module.


"""

import asyncio
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from httpx import Response
from loguru import logger

from pyegeria.models import NewElementRequestBody, TemplateRequestBody, UpdateElementRequestBody, \
    NewRelationshipRequestBody, DeleteRequestBody, UpdateStatusRequestBody, SearchStringRequestBody
from pyegeria.output_formatter import make_preamble, make_md_attribute, generate_output, extract_mermaid_only, \
    extract_basic_dict, MD_SEPARATOR, populate_common_columns
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria import validate_guid
from pyegeria.governance_officer import GovernanceOfficer
from pyegeria._client_new import Client2, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_GUID_RETURNED
from pyegeria.utils import body_slimmer, dynamic_catch
from pyegeria._exceptions import (InvalidParameterException)

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

DEFAULT_BODY_SKELETON = {
    "effective_time": None, "limitResultsByStatus": ["ACTIVE"], "asOfTime": None, "sequencingOrder": None,
    "sequencingProperty": None, "filter": None,
    }



def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


# ("params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to "
# "the query string")


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/metadata-explorer"


class SolutionArchitect(Client2):
    """SolutionArchitect is a class that extends the Client class. The Solution Architect OMVS provides APIs for
      searching for architectural elements such as information supply chains, solution blueprints, solution components,
      and component implementations.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a
            default optionally used by the methods when the user
            doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None


    """

    def __init__(self, view_server: str, platform_url: str, user_id: str = None, user_pwd: str = None,
                 token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.solution_architect_command_root: str = (f"{self.platform_url}/servers/{self.view_server}"
                                                     f"/api/open-metadata/solution-architect")
        Client2.__init__(self, view_server, platform_url, user_id=user_id, user_pwd=user_pwd, token=token, )
        self.url_marker = "solution-architect"
    #
    # Extract properties functions
    #

    def _get_supply_chain_rel_elements(self, guid:str)-> dict | str:
        elements = self.get_info_supply_chain_by_guid(guid)
        return self._get_supply_chain_rel_elements_dict(elements)


    def _get_supply_chain_rel_elements_dict(self, el_struct: dict)-> dict | str:
        """return the lists of objects related to a data field"""

        parent_guids = []
        parent_names = []
        parent_qnames = []

        implemented_by_guids = []
        implemented_by_names = []
        implemented_by_qnames = []

        external_references_guids = []
        external_references_names = []
        external_references_qnames = []

        other_related_elements_guids = []
        other_related_elements_names = []
        other_related_elements_qnames = []


        nested_supply_chains_guids = []
        nested_supply_chains_names = []
        nested_supply_chains_qnames = []

        peer_supply_chains_guids = []
        peer_supply_chains_names = []
        peer_supply_chains_qnames = []
        peer_supply_chain_linl_label = []



        # # extract existing related data structure and data field elements
        # other_related_elements = el_struct.get("otherRelatedElements",None)
        # if other_related_elements:
        #     for rel in other_related_elements:
        #         related_element = rel["relatedElement"]
        #         type = related_element["elementHeader"]["type"]["typeName"]
        #         guid = related_element["elementHeader"]["guid"]
        #         qualified_name = related_element["properties"].get("qualifiedName","") or ""
        #         display_name = related_element["properties"].get("displayName","") or ""
        #         if type == "DataStructure":
        #             implementation_guids.append(guid)
        #             implementation_names.append(display_name)
        #             implementation_qnames.append(qualified_name)
        #
        #         elif type == "DataField":
        #             parent_guids.append(guid)
        #             parent_names.append(display_name)
        #             parent_qnames.append(qualified_name)

        parents = el_struct.get("parents", {})
        if parents:
            for parent in parents:
                parent_guids.append(parent['relatedElement']['elementHeader']["guid"])
                parent_names.append(parent['relatedElement']['properties'].get("displayName",""))
                parent_qnames.append(parent['relatedElement']['properties'].get("qualifiedName",""))

        peer_supply_chains = el_struct.get("links", {})
        if peer_supply_chains:
            for peer in peer_supply_chains:
                peer_supply_chains_guids.append(peer['relatedElement']['elementHeader']['guid'])
                peer_supply_chains_names.append(peer['relatedElement']['properties'].get("displayName",""))
                peer_supply_chains_qnames.append(peer['relatedElement']['properties'].get("qualifiedName",""))
                peer_supply_chain_linl_label.append(peer['relationshipProperties'].get('label',""))

        implemented_by = el_struct.get("implementedByList", {})
        if implemented_by:
            for peer in peer_supply_chains:
                implemented_by_guids.append(peer['relatedElement']['elementHeader']['guid'])
                implemented_by_names.append(peer['relatedElement']['properties'].get("displayName", ""))
                implemented_by_qnames.append(peer['relatedElement']['properties'].get("qualifiedName", ""))



        # nested_supply_chains = el_struct.get("nestedDataClasses", {})
        # for nested_data_class in nested_supply_chains:
        #     nested_supply_chains_guids.append(nested_data_class['relatedElement']["elementHeader"]["guid"])
        #     nested_supply_chains_names.append(nested_data_class['relatedElement']["properties"]["displayName"])
        #     nested_supply_chains_qnames.append(nested_data_class['relatedElement']["properties"]["qualifiedName"])


        mermaid = el_struct.get("mermaidGraph", {})

        return {"parent_guids": parent_guids,
                "parent_names": parent_names,
                "parent_qnames": parent_qnames,

                "implemented_by_guids": implemented_by_guids,
                "implemented_by_names": implemented_by_names,
                "implemented_by_qnames": implemented_by_qnames,

                "peer_supply_chains_guids": peer_supply_chains_guids,
                "peer_supply_chains_names": peer_supply_chains_names,
                "peer_supply_chains_qnames": peer_supply_chains_qnames,

                "nested_data_class_guids": nested_supply_chains_guids,
                "nested_data_class_names": nested_supply_chains_names,
                "nested_data_class_qnames": nested_supply_chains_qnames,

                "external_references_guids": external_references_guids,
                "external_references_names": external_references_names,
                "external_references_qnames": external_references_qnames,

                "mermaid" : mermaid,
            }

    
    def _extract_supply_chain_list(self, element: Union[Dict,List[Dict]])->List[Dict]:
        """
        Normalize supply chain response for a list of dictionaries.
        Args:
            element: Dict or List

        Returns:
            list of Dict

        """
        if isinstance(element, dict):
            return [self._extract_info_supply_chain_properties(element)]
        elif isinstance(element, list):
            comp_list = []
            for i in range(len(element)):
                comp_list.append( self._extract_info_supply_chain_properties(element[i]))
            return comp_list
        else:
            return []

    def _extract_info_supply_chain_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract properties from an information supply chain element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        # Follow common extractor pattern using populate_common_columns
        return populate_common_columns(
            element,
            columns_struct,
            include_header=True,
            include_relationships=True,
            include_subject_area=True,
            mermaid_source_key='mermaidGraph',
            mermaid_dest_key='mermaid'
        )

    def _extract_solution_blueprint_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract properties from a solution blueprint element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        return populate_common_columns(
            element,
            columns_struct,
            include_header=True,
            include_relationships=True,
            include_subject_area=True,
            mermaid_source_key='mermaidGraph',
            mermaid_dest_key='mermaid'
        )

    def _extract_solution_roles_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract properties from a solution role element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        return populate_common_columns(
            element,
            columns_struct,
            include_header=True,
            include_relationships=True,
            include_subject_area=True,
            mermaid_source_key='mermaidGraph',
            mermaid_dest_key='mermaid'
        )





    def _get_component_rel_elements(self, guid:str)-> dict | str:
        elements = self.get_info_supply_chain_by_guid(guid)
        return self._get_supply_chain_rel_elements_dict(elements)


    def _get_component_rel_elements_dict(self, el_struct: dict)-> dict | str:
        """return the lists of objects related to a data field"""

        actor_guids = []
        actor_name_roles = []
        actor_qnames = []
        
        parent_guids = []
        parent_names = []
        parent_qnames = []

        sub_component_guids = []
        sub_component_names = []
        sub_component_qnames = []

        implemented_by_guids = []
        implemented_by_names = []
        implemented_by_qnames = []

        blueprint_guids = []
        blueprint_names = []
        blueprint_qnames = []


        external_references_guids = []
        external_references_names = []
        external_references_qnames = []

        other_related_elements_guids = []
        other_related_elements_names = []
        other_related_elements_qnames = []
        
        owning_info_supply_chain_guids = []
        owning_info_supply_chain_qnames = []
        owning_info_supply_chain_names = []

        wired_to_guids = []
        wired_to_names = []
        wired_to_link_labels = []
        wired_to_qnames = []
        
        wired_from_guids = []
        wired_from_names = []
        wired_from_link_labels = []
        wired_from_qnames = []

        actors = el_struct.get("actors", {})
        if actors:
            for actor in actors:
                actor_guids.append(actor['relatedElement']['elementHeader'].get("guid", None))
                actor_role = actor['relationshipProperties'].get('role',"")      
                actor_name = actor['relatedElement']['properties'].get("displayName", "")
                actor_name_roles.append(f"`{actor_name}` in role `{actor_role}`")
                actor_qnames.append(actor['relatedElement']['properties'].get("qualifiedName", ""))

        wired_to = el_struct.get("wiredToLinks", {})
        if wired_to:
            for wire in wired_to:
                wired_to_link_labels.append(wire['properties'].get("label", ""))
                wired_to_guids.append(wire['linkedElement']['elementHeader']['guid'])
                wired_to_qnames.append(wire['linkedElement']['properties'].get("qualifiedName", ""))
                wired_to_names.append(wire['linkedElement']['properties'].get('displayName', ""))
                
        wired_from = el_struct.get("wiredFromLinks", {})
        if wired_from:
            for wire in wired_from:
                wired_from_link_labels.append(wire['properties'].get("label", ""))
                wired_from_guids.append(wire['linkedElement']['elementHeader']['guid'])
                wired_from_qnames.append(wire['linkedElement']['properties'].get("qualifiedName", ""))
                wired_from_names.append(wire['linkedElement']['properties'].get('displayName', ""))

        blueprints = el_struct.get("blueprints", {})
        if blueprints:
            for bp in blueprints:
                blueprint_guids.append(bp['relatedElement']['elementHeader']['guid'])
                blueprint_qnames.append(bp['relatedElement']['properties'].get("qualifiedName", ""))
                blueprint_names.append(bp['relatedElement']['properties'].get('displayName', ""))

        sub_components = el_struct.get("subComponents", {})
        if sub_components:
            for sub_component in sub_components:
                sub_component_guids.append(sub_component['elementHeader']['guid'])
                sub_component_qnames.append(sub_component['properties'].get("qualifiedName", ""))
                sub_component_names.append(sub_component['properties'].get('displayName', ""))

        context = el_struct.get("context", None)
        if context:
            for c in context:

                parents = c.get("parentComponents", None) if context else None
                if parents:
                    for parent in parents:
                        parent_guids.append(parent['relatedElement']['elementHeader']["guid"])
                        parent_names.append(parent['relatedElement']['properties'].get("displayName",""))
                        parent_qnames.append(parent['relatedElement']['properties'].get("qualifiedName",""))

                owning_isc = c.get("owningInformationSupplyChains", None) if context else None
                if owning_isc:
                    for isc in owning_isc:
                        owning_info_supply_chain_guids.append(isc['relatedElement']['elementHeader']["guid"])
                        owning_info_supply_chain_names.append(isc['relatedElement']['properties'].get("displayName", ""))
                        owning_info_supply_chain_qnames.append(isc['relatedElement']['properties'].get("qualifiedName", ""))



        # implemented_by = el_struct.get("implementedByList", {})
        # if len(implemented_by) > 0:
        #     for peer in peer_supply_chains:
        #         implemented_by_guids.append(peer['relatedElement']['elementHeader']['guid'])
        #         implemented_by_names.append(peer['relatedElement']['properties'].get("displayName", ""))
        #         implemented_by_qnames.append(peer['relatedElement']['properties'].get("qualifiedName", ""))


        mermaid = el_struct.get("mermaidGraph", {})

        return {"parent_guids": parent_guids,
                "parent_names": parent_names,
                "parent_qnames": parent_qnames,

                "actor_guids": actor_guids,
                "actor_name_roles": actor_name_roles,
                "actor_qnames": actor_qnames,

                "sub_component_guids": sub_component_guids,
                "sub_component_names": sub_component_names,
                "sub_component_qnames": sub_component_qnames,

                "blueprint_guids": blueprint_guids,
                "blueprint_names": blueprint_names,
                "blueprint_qnames": blueprint_qnames,

                "owning_info_supply_chain_guids": owning_info_supply_chain_guids,
                "owning_info_supply_chain_names": owning_info_supply_chain_names,
                "owning_info_supply_chain_qnames": owning_info_supply_chain_qnames,

                "implemented_by_guids": implemented_by_guids,
                "implemented_by_names": implemented_by_names,
                "implemented_by_qnames": implemented_by_qnames,

                "wired_from_guids": wired_from_guids,
                "wired_from_names": wired_from_names,
                "wired_from_qnames": wired_from_qnames,
                "wired_from_link_labels": wired_from_link_labels,

                "wired_to_guids": wired_to_guids,
                "wired_to_names": wired_to_names,
                "wired_to_qnames": wired_to_qnames,
                "wired_to_link_labels": wired_to_link_labels,

                "external_references_guids": external_references_guids,
                "external_references_names": external_references_names,
                "external_references_qnames": external_references_qnames,

                "mermaid" : mermaid,
            }

    def _extract_component_list(self, element: Union[Dict,List[Dict]])->List[Dict]:
        """
        Normalize for a list of dictionaries.
        Args:
            element: Dict or List

        Returns:
            list of Dict

        """
        if isinstance(element, dict):
            return [self._extract_solution_components_properties(element)]
        elif isinstance(element, list):
            comp_list = []
            for i in range(len(element)):
                comp_list.append( self._extract_solution_components_properties(element[i]))
            return comp_list
        else:
            return []

    def _extract_solution_components_properties(self, element: Union[Dict,List[Dict]], columns_struct: dict) -> dict:
        """
        Extract properties from a solution component element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """

        return populate_common_columns(
            element,
            columns_struct,
            include_header=True,
            include_relationships=True,
            include_subject_area=True,
            mermaid_source_key='mermaidGraph',
            mermaid_dest_key='mermaid'
        )

    #
    # Markdown output support
    #
    def generate_info_supply_chain_output(self, elements: list | dict, search_string: str, element_type_name: str | None,
                                          output_format: str = 'MD', output_format_set: dict | str = None) -> str | list:
        """Render Information Supply Chains using the shared output pipeline.
        """
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)

        entity_type = "Information Supply Chain"
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set("Information Supply Chains", output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_info_supply_chain_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def generate_solution_blueprint_output(self, elements: list | dict, search_string: str, element_type_name: str | None,
                                           output_format: str = 'MD', output_format_set: dict | str = None) -> str | list:
        """
        Generate output for solution blueprints in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing solution blueprint elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)

        Returns:
            Formatted output as string or list of dictionaries
        """
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)

        entity_type = "Solution Blueprint"
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set("Solution Blueprints", output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_solution_blueprint_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def generate_solution_roles_output(self, elements: list | dict, search_string: str, element_type_name: str | None,
                                       output_format: str = 'MD', output_format_set: dict | str = None) -> str | list:
        """
        Generate output for solution roles in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing solution role elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)

        Returns:
            Formatted output as string or list of dictionaries
        """
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)

        entity_type = "Solution Role"
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set("Solution Roles", output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_solution_roles_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def generate_solution_components_output(self, elements: list | dict, search_string: str, element_type_name: str | None,
                                            output_format: str = 'MD', output_format_set: dict | str = None) -> str | list:
        """
        Generate output for solution components in the specified format.

        Given a set of elements representing solution components (either as a list or a dictionary),
        this function generates output in the specified format. The output includes various 
        attributes of the solution components, such as their names, descriptions, types, and 
        related information like blueprints, parents, and extended properties.

        Args:
            elements: Dictionary or list of dictionaries containing solution component elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)

        Returns:
            Formatted output as string or list of dictionaries
        """
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)

        entity_type = "Solution Component"
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set("Solution Components", output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_solution_components_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    @dynamic_catch
    async def _async_create_info_supply_chain(self, body: dict | NewElementRequestBody) -> str:
        """Create an information supply. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "NewElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
           " class" : "InformationSupplyChainProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
            "estimatedVolumetrics": {},
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains")

        return await self._async_create_element_body_request(url, ["InformationSupplyChainProperties"], body)

    @dynamic_catch
    def create_info_supply_chain(self, body: dict | NewElementRequestBody) -> str:
        """Create an information supply.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "NewElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
           " class" : "InformationSupplyChainProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
             "estimatedVolumetrics": {},
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_info_supply_chain(body))
        return response

    @dynamic_catch
    async def _async_create_info_supply_chain_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new metadata element to represent an information supply chain using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/from-template")

        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create Supply Chain from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_info_supply_chain_from_template(self, body: dict| TemplateRequestBody) -> str:
        """ Create a new metadata element to represent an information supply chain using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_info_supply_chain_from_template(body))
        return response

    @dynamic_catch
    async def _async_update_info_supply_chain(self, guid: str, body: dict | UpdateElementRequestBody,) -> None:
        """ Update the properties of an information supply chain. Async Version.

        Parameters
        ----------
        guid: str
            guid of the information supply chain to update.
        body: dict | UpdateElementRequestBody
            A dictionary containing the updates to the supply chain.


        Returns
        -------

        None

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "UpdateElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "InformationSupplyChainProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/update")

        await self._async_update_element_body_request(url, ["InformationSupplyChainProperties"],body)

    @dynamic_catch
    def update_info_supply_chain(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an information supply chain. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to update.
            body: dict | UpdateElementRequestBody
                A dictionary containing the updates to the supply chain.

            Returns
            -------

            None

            Raises
            ------
            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class" : "UpdateElementRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "properties": {
                "class" : "InformationSupplyChainProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "scope": "add scope of this information supply chain's applicability.",
                "purposes": ["purpose1", "purpose2"],
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_info_supply_chain(guid, body))

    @dynamic_catch
    async def _async_link_peer_info_supply_chains(self, peer1_guid: str, peer2_guid: str, body: dict | NewRelationshipRequestBody = None) -> None:
        """ Connect two peer information supply chains.  The linked elements are of type 'Referenceable' to
        allow significant data stores to be included in the definition of the information supply chain.
        Request body is optional. Async Version.

        Parameters
        ----------
        peer1_guid: str
            guid of the first information supply chain  to link.
        peer2_guid: str
            guid of the second information supply chain to link.
        body: dict | NewRelationshipRequestBody, optional
            The body describing the link between the two chains.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{peer1_guid}/peer-links/{peer2_guid}/attach")

        await self._async_new_relationship_request(url, ["InformationSupplyChainLinkProperties"], body)
        logger.info(f"Linked Supply Chains {peer1_guid} -> {peer2_guid}")

    @dynamic_catch
    def link_peer_info_supply_chains(self, peer1_guid: str, peer2_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Connect two peer information supply chains.  The linked elements are of type 'Referenceable' to
        allow significant data stores to be included in the definition of the information supply chain.
        Request body is optional.

        Parameters
        ----------
        peer1_guid: str
            guid of the first information supply chain  to link.
        peer2_guid: str
            guid of the second information supply chain to link.
        body: dict | NewRelationshipRequestBody, optional
            The body describing the link between the two chains.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
            }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_peer_info_supply_chains(peer1_guid, peer2_guid, body))

    @dynamic_catch
    async def _async_unlink_peer_info_supply_chains(self, peer1_guid: str, peer2_guid: str,
                                                       body: dict | DeleteRequestBody = None) -> None:
        """ Detach two peers in an information supply chain from one another.  The linked elements are of type
           'Referenceable' to allow significant data stores to be included in the definition of the information
           supply chain. Request body is optional. Async Version.

        Parameters
        ----------
        peer1_guid: str
            guid of the first information supply chain to link.
        peer2_guid: str
            guid of the second information supply chain to link.
        body: dict | DeleteRequestBody, optional
            The body describing the link between the two segments.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        validate_guid(peer1_guid)
        validate_guid(peer2_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{peer1_guid}/peer-links/{peer2_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(
            f"Detached supply chains  {peer1_guid} -> {peer2_guid}")

    @dynamic_catch
    def unlink_peer_info_supply_chains(self, peer1_guid: str, peer2_guid: str,
                                                       body: dict = None) -> None:
        """ Detach two peers in an information supply chain from one another.  The linked elements are of type
           'Referenceable' to allow significant data stores to be included in the definition of the information
           supply chain. Request body is optional.

        Parameters
        ----------
        peer1_guid: str
            guid of the first information supply chain to link.
        peer2_guid: str
            guid of the second information supply chain to link.
        body: dict, optional
            The body describing the link between the two segments.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_unlink_peer_info_supply_chains(peer1_guid,peer2_guid, body))

    @dynamic_catch
    async def _async_compose_info_supply_chains(self, chain_guid: str, nested_chain_guid: str,
                                                body: dict | NewRelationshipRequestBody = None) -> None:
        """ Connect a nested information supply chain to its parent. Request body is optional.
            Async Version.

        Parameters
        ----------
        chain_guid: str
            guid of the first information supply chain  to link.
        nested_chain_guid: str
            guid of the second information supply chain to link.
        body: dict | NewRelationshipRequestBody, optional
            The body describing the link between the two chains.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        validate_guid(chain_guid)
        validate_guid(nested_chain_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{chain_guid}/compositions/{nested_chain_guid}/attach")

        await self._async_new_relationship_request(url, ["InformationSupplyChainCompositionProperties"], body)
        logger.info(f"Linked {chain_guid} -> {nested_chain_guid}")

    @dynamic_catch
    def compose_info_supply_chains(self, chain_guid: str, nested_chain_guid: str, body: dict | NewRelationshipRequestBody = None) -> None:
        """ Connect a nested information supply chain to its parent. Request body is optional.

        Parameters
        ----------
        chain_guid: str
            guid of the first information supply chain to link.
        nested_chain_guid: str
            guid of the second information supply chain to link.
        body: dict | NewRelationshipRequestBody, optional
            The body describing the link between the two chains.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
            }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_compose_info_supply_chains(chain_guid, nested_chain_guid, body))


    @dynamic_catch
    async def _async_decompose_info_supply_chains(self, chain_guid: str, nested_chain_guid: str,
                                                       body: dict = None) -> None:
        """ Detach two peers in an information supply chain from one another.  Request body is optional. Async Version.

        Parameters
        ----------
        chain_guid: str
            guid of the first information supply chain to link.
        nested_chain_guid: str
            guid of the second information supply chain to link.
        body: dict, optional
            The body describing the link between the two segments.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        validate_guid(chain_guid)
        validate_guid(nested_chain_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{chain_guid}/compositions/{nested_chain_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(f"Removed composition of {nested_chain_guid} -> {chain_guid}")

    @dynamic_catch
    def decompose_info_supply_chains(self, chain_guid: str, nested_chain_guid: str,
                                                       body: dict | DeleteRequestBody = None) -> None:
        """ Detach two peers in an information supply chain from one another.  Request body is optional.

        Parameters
        ----------
        chain_guid: str
            guid of the first information supply chain to link.
        nested_chain_guid: str
            guid of the second information supply chain to link.
        body: dict | DeleteRequestBody, optional
            The body describing the link between the two segments.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_decompose_info_supply_chains(chain_guid,
                                                                         nested_chain_guid, body))

    @dynamic_catch
    async def _async_delete_info_supply_chain(self, guid: str, body: dict | DeleteRequestBody = None, cascade_delete: bool = False) -> None:
        """Delete an information supply chain. Async Version.

           Parameters
           ----------
           guid: str
               guid of the information supply chain to delete.
           body: dict, optional
               A dictionary containing parameters of the deletion.
           cascade_delete: bool, optional
               If true, the child objects will also be deleted.

           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/delete")

        await self._async_delete_request(url, body, cascade_delete=cascade_delete)
        logger.info(f"Deleted Info Supply Chain  {guid} with cascade {cascade_delete}")

    @dynamic_catch
    def delete_info_supply_chain(self, guid: str, body: dict | DeleteRequestBody= None, cascade_delete: bool = False) -> None:
        """ Delete an information supply chain.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to delete.
            body: dict | DeleteRequestBody, optional
                A dictionary containing parameters of the deletion.
           cascade_delete: bool, optional
               If true, the child objects will also be deleted.
            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_info_supply_chain(guid, body, cascade_delete))

    def find_all_information_supply_chains(self, search_string: str = "*", classification_names: list[str] = None,
                                                    metadata_element_types: list[str] = None,
                                                    starts_with: bool = True, ends_with: bool = False,
                                                    ignore_case: bool = False, start_from: int = 0,
                                                    page_size: int = 0, output_format: str = 'JSON',
                                                    output_format_set: str = None,
                                                    body: dict| SearchStringRequestBody = None) -> (list[dict] | str):
        """ Retrieve a list of all information supply chains
             Parameters
                ----------
                body: dict, optional, default = None
                    - additional optional specifications for the search.
                start_from: int, optional, default = 0
                    page to start from.
                page_size: int, optional, default = max_paging_size
                    number of elements to return.
                output_format: str, default = 'JSON'
                    Type of output to produce:
                        JSON - output standard json
                        MD - output standard markdown with no preamble
                        FORM - output markdown with a preamble for a form
                        REPORT - output markdown with a preamble for a report
                        Mermaid - output markdown with a mermaid graph

                Returns
                -------
                list[dict] | str
                    A list of information supply chain structures or a string if there are no elements found.

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                -----

                {
                  "class" : "FilterRequestBody",
                  "asOfTime" : "{{$isoTimestamp}}",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "forLineage" : false,
                  "forDuplicateProcessing" : false,
                  "limitResultsByStatus" : ["ACTIVE"],
                  "sequencingOrder" : "PROPERTY_ASCENDING",
                  "sequencingProperty" : "qualifiedName"
                }
        """

        return self.find_information_supply_chains("*", classification_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body)

    async def _async_find_information_supply_chains(self, search_string: str = "*", classification_names: list[str] = None,
                                                    metadata_element_types: list[str] = None,
                                                    starts_with: bool = True, ends_with: bool = False,
                                                    ignore_case: bool = False, start_from: int = 0,
                                                    page_size: int = 0, output_format: str = 'JSON',
                                                    output_format_set: str = None,
                                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the list of information supply chain metadata elements that contain the search string.
               https://egeria-project.org/concepts/information-supply-chain
               Async version.

            Parameters
            ----------
            search_filter : str
                - search_filter string to search for.
            add_implementation : bool, [default=True], optional
                - add_implementation flag to include information supply chain implementations details..
            starts_with : bool, [default=False], optional
                Starts with the supplied string.
            ends_with : bool, [default=False], optional
                Ends with the supplied string
            ignore_case : bool, [default=False], optional
                Ignore case when searching
            body: dict, optional, default = None
                - additional optional specifications for the search.
            output_format: str, default = 'JSON'
                Type of output to produce:
                    JSON - output standard json
                    MD - output standard markdown with no preamble
                    FORM - output markdown with a preamble for a form
                    REPORT - output markdown with a preamble for a report
                    Mermaid - output markdown with a mermaid graph

            Returns
            -------
            list[dict] | str
                A list of information supply chain structures or a string if there are no elements found.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----

            {
              "class" : "FilterRequestBody",
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

            """

        url = f"{self.solution_architect_command_root}/information-supply-chains/by-search-string"
        return await self._async_find_request(url, _type="GovernanceDefinition",
                                              _gen_output=self.generate_info_supply_chain_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)



    def find_information_supply_chains(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the list of information supply chain metadata elements that contain the search string.
          https://egeria-project.org/concepts/information-supply-chain

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        add_implementation : bool, [default=True], optional
            - add_implementation flag to include information supply chain implementations details..
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=max_paging_size], optional
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            - additional optional specifications for the search.
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----

            {
              "class" : "SearchStringRequestBody",
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_information_supply_chains(search_string, classification_names, metadata_element_types,
                                                       starts_with, ends_with, ignore_case,
                                                       start_from, page_size,  output_format,
                                                       output_format_set, body))
        return response

    async def _async_get_info_supply_chain_by_name(self, search_filter: str, body: dict = None,
                                                   add_implementation: bool = True, start_from: int = 0,
                                                   page_size: int = max_paging_size,
                                                   output_format: str = "JSON") -> dict | str:
        """ Returns the list of information supply chains with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of information supply chains matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """
        add_impl = str(add_implementation).lower()
        possible_query_params = query_string(
            [("addImplementation", add_impl), ("startFrom", start_from), ("pageSize", page_size)])

        if body is None:
            body = {
                "filter": search_filter,
                }

        url = (f"{self.solution_architect_command_root}/information-supply-chains/by-name"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_info_supply_chain_output(element, None, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_info_supply_chain_by_name(self, search_filter: str, body: dict = None, add_implementation: bool = True,
                                      start_from: int = 0, page_size: int = max_paging_size,
                                      output_format: str = "JSON") -> dict | str:
        """ Returns the list of information supply chains with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of information supply chains matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_info_supply_chain_by_name(search_filter, body, add_implementation, start_from, page_size,
                                                      output_format))
        return response

    async def _async_get_info_supply_chain_by_guid(self, guid: str, body: dict = None, add_implementation: bool = True,
                                                   output_format: str = "JSON") -> dict | str:
        """Return the properties of a specific information supply chain. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }

        """
        validate_guid(guid)
        add_impl = str(add_implementation).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/retrieve?addImplementation={add_impl}")

        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_info_supply_chain_output(element, None, output_format)
        return element

    def get_info_supply_chain_by_guid(self, guid: str, body: dict = None, add_implementation: bool = True,
                                      output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific information supply chain.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_info_supply_chain_by_guid(guid, body, add_implementation, output_format))
        return response

    #
    #  Blueprints
    #

    @dynamic_catch
    async def _async_create_solution_blueprint(self, body: dict | NewElementRequestBody) -> str:
        """ Create a solution blueprint. To set a lifecycle status
            use a NewSolutionElementRequestBody which has a default status of DRAFT. Using a
            NewElementRequestBody sets the status to ACTIVE.
            Async version.

            Parameters
            ----------
            body: dict | NewElementRequestBody
                A dictionary containing the definition of the blueprint to create.

            Returns
            -------
            str - guid of the supply chain created.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "NewElementRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "anchorGUID": "add guid here",
              "isOwnAnchor": false,
              "parentGUID": "add guid here",
              "parentRelationshipTypeName": "add type name here",
              "parentRelationshipProperties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                  "description": {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveValue": "New description"
                  }
                }
              },
              "parentAtEnd1": false,
              "properties": {
                "class" : "SolutionBlueprintProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "versionIdentifier": "add version here",
                "userDefinedStatus" : "add status here",
                "lifecycleStatus": "DRAFT"
                "additionalProperties": {
                  "property1": "propertyValue1",
                  "property2": "propertyValue2"
                },
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
              }
            }

            To set a lifecycle use:

            Set initialStatus which can be DRAFT, PREPARED, PROPPOSED, APPROVED, REJECTED, ACTIVE, DISABLED, DEPRECATED,
            OTHER.  If other is used, set userDefinedStatus.

            {
              "class" : "NewSolutionElementRequestBody",
              "anchorGUID" : "add guid here",
              "isOwnAnchor": false,
              "parentGUID": "add guid here",
              "parentRelationshipTypeName": "add type name here",
              "parentRelationshipProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "description" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveValue" : "New description"
                  }
                }
              },
              "parentAtEnd1": false,
              "properties": {
                "class" : "SolutionBlueprintProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "versionIdentifier": "add version for this blueprint",
                "userDefinedStatus" : "add status here if initialStatus=OTHER",
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              },
              "initialStatus" : "DRAFT",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints")

        return await self._async_create_element_body_request(url, ["SolutionBlueprintProperties"], body)

    @dynamic_catch
    def create_solution_blueprint(self, body: dict | NewElementRequestBody) -> str:
        """ Create a solution blueprint. To set a lifecycle status
            use a NewSolutionElementRequestBody which has a default status of DRAFT. Using a
            NewElementRequestBody sets the status to ACTIVE.

            Parameters
            ----------
            body: dict | NewElementRequestBody
                A dictionary containing the definition of the blueprint to create.

            Returns
            -------
            str - guid of the supply chain created.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "NewElementRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "anchorGUID": "add guid here",
              "isOwnAnchor": false,
              "parentGUID": "add guid here",
              "parentRelationshipTypeName": "add type name here",
              "parentRelationshipProperties": {
                "class": "ElementProperties",
                "propertyValueMap": {
                  "description": {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveValue": "New description"
                  }
                }
              },
              "parentAtEnd1": false,
              "properties": {
                "class" : "SolutionBlueprintProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "versionIdentifier": "add version here",
                "additionalProperties": {
                  "property1": "propertyValue1",
                  "property2": "propertyValue2"
                },
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
              }
            }

            To set a lifecycle use:

            Set initialStatus which can be DRAFT, PREPARED, PROPPOSED, APPROVED, REJECTED, ACTIVE, DISABLED, DEPRECATED,
            OTHER.  If other is used, set userDefinedStatus.

            {
              "class" : "NewSolutionElementRequestBody",
              "anchorGUID" : "add guid here",
              "isOwnAnchor": false,
              "parentGUID": "add guid here",
              "parentRelationshipTypeName": "add type name here",
              "parentRelationshipProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "description" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveValue" : "New description"
                  }
                }
              },
              "parentAtEnd1": false,
              "properties": {
                "class" : "SolutionBlueprintProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "versionIdentifier": "add version for this blueprint",
                "userDefinedStatus" : "add status here if initialStatus=OTHER",
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              },
              "initialStatus" : "DRAFT",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_blueprint(body))
        return response

    @dynamic_catch
    async def _async_create_solution_blueprint_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new solution blueprint using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dictionary containing the definition of the solution blueprint to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/from-template")
        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create Blueprint from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)


    @dynamic_catch
    def create_solution_blueprint_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new solution blueprint using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dictionary containing the definition of the solution blueprint to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }
       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_blueprint_from_template(body))
        return response

    @dynamic_catch
    async def _async_update_solution_blueprint(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update a solution blueprint. Async Version.

        Parameters
        ----------
        guid: str
            guid of the information supply chain to update.
        body: dict | UpdateElementRequestBody
            A dictionary containing the updates to the supply chain.
        Returns
        -------

        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "UpdateElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class" : "SolutionBlueprintProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "versionIdentifier": "add version identifier here",
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
           }
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{guid}/update")

        await self._async_update_element_body_request(url, ["SolutionBlueprintProperties"],body)

    @dynamic_catch
    def update_solution_blueprint(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a solution blueprint. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to update.
            body: dict | UpdateElementRequestBody
                A dictionary containing the updates to the blueprint.

            Returns
            -------

            None

            Raises
            ------
            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "UpdateSElementRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "properties": {
                "class" : "SolutionBlueprintProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "versionIdentifier": "add version identifier here",
                "purposes": ["purpose1", "purpose2"],
                "additionalProperties": {
                  "property1": "propertyValue1",
                  "property2": "propertyValue2"
                },
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
               }
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_solution_blueprint(guid, body))


    @dynamic_catch
    async def _async_delete_solution_blueprint(self, guid: str, body: dict | DeleteRequestBody, cascade: bool = False) -> None:
        """ Delete a solution blueprint. Async Version.
         Parameters
           ----------
           guid: str
               guid of the information supply chain to delete.
           body: dict, optional
               A dictionary containing parameters of the deletion.
           cascade: bool, optional
               If true, the child objects will also be deleted.

           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/delete")

        await self._async_delete_request(url, body, cascade_delete=cascade)
        logger.info(f"Deleted Info Supply Chain  {guid} with cascade {cascade}")

    @dynamic_catch
    def delete_solution_blueprint(self, guid: str, body: dict | DeleteRequestBody = None,
                                 cascade: bool = False) -> None:
        """ Delete an Solution Blueprint.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to delete.
            body: dict | DeleteRequestBody, optional
                A dictionary containing parameters of the deletion.
           cascade: bool, optional
               If true, the child objects will also be deleted.
            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_info_supply_chain(guid, body, cascade))


    @dynamic_catch
    async def _async_link_solution_component_to_blueprint(self, blueprint_guid: str, component_guid: str,
                                                          body: dict | NewRelationshipRequestBody) -> None:
        """ Connect a solution component to a blueprint. Async Version.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to connect to.
        component_guid: str
            guid of the component to link.
        body: dict | NewRelationshipRequestBody
            The body describing the link.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "SolutionBlueprintCompositionProperties",
            "role": "Add role that the component plays in the solution blueprint here",
            "description": "Add description of the solution component in the context of the solution blueprint.",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{blueprint_guid}/solution-components/{component_guid}/attach")

        await self._async_new_relationship_request(url, ["SolutionComponentCompositionProperties"], body)
        logger.info(f"Linked component to blueprint {component_guid} -> {blueprint_guid}")

    @dynamic_catch
    def link_solution_component_to_blueprint(self, blueprint_guid: str, component_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Connect a solution component to a blueprint.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to connect to.
        component_guid: str
            guid of the component to link.
        body: dict | NewRelationshipRequestBody
            The body describing the link.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
         {
          "class" : "RelationshipRequestBody",
          "properties": {
            "class": "SolutionBlueprintCompositionProperties",
            "role": "Add role that the component plays in the solution blueprint here",
            "description": "Add description of the solution component in the context of the solution blueprint.",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_solution_component_to_blueprint(blueprint_guid, component_guid, body))

    @dynamic_catch
    async def _async_detach_solution_component_from_blueprint(self, blueprint_guid: str, component_guid: str,
                                                              body: dict | DeleteRequestBody = None) -> None:
        """ Detach a solution component from a solution blueprint.
            Async Version.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to disconnect from.
        component_guid: str
            guid of the component to disconnect.
        body: dict
            The body describing the request.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{blueprint_guid}/solution-components/{component_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached component from blueprint  {component_guid} -> {blueprint_guid}")

    @dynamic_catch
    def detach_solution_component_from_blueprint(self, blueprint_guid: str, component_guid: str,
                                                 body: dict | DeleteRequestBody = None) -> None:
        """ Detach a solution component from a solution blueprint.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to disconnect from.
        component_guid: str
            guid of the component to disconnect.
        body: dict
            The body describing the request.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_solution_component_from_blueprint(blueprint_guid, component_guid, body))


    @dynamic_catch
    async def _async_delete_solution_blueprint(self, blueprint_guid: str, cascade_delete: bool = False,
                                               body: dict | DeleteRequestBody = None) -> None:
        """Delete a solution blueprint. Async Version.

           Parameters
           ----------
           blueprint_guid: str
               guid of the information supply chain to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict, optional
               A dictionary containing parameters for the deletion.

           Returns
           -------
           None

           Raises
           ------
           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """
        validate_guid(blueprint_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{blueprint_guid}/delete")
        await self._async_delete_request(url, body, cascade_delete=cascade_delete)
        logger.info(f"Deleted Blueprint  {blueprint_guid} with cascade {cascade_delete}")

    @dynamic_catch
    def delete_solution_blueprint(self, blueprint_guid: str, cascade_delete: bool = False, body: dict | DeleteRequestBody = None) -> None:
        """ Delete a solution blueprint.
            Parameters
            ----------
            blueprint_guid: str
                guid of the information supply chain to delete.
            cascade_delete: bool, optional, default: False
                Cascade the delete to dependent objects?
            body: dict, optional
                A dictionary containing parameters of the deletion.

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_solution_blueprint(blueprint_guid, cascade_delete, body))




    async def _async_find_solution_blueprints(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the solution blueprint elements that contain the search string.
           https://egeria-project.org/concepts/solution-blueprint
           Async version.

        Parameters
        ----------
        search_filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of solution blueprint structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        {
          "class" : "FilterRequestBody",
          "filter" : "add name",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }

        """




        url = f"{self.solution_architect_command_root}/solution-blueprints/by-search-string"
        return await self._async_find_request(url, _type="GovernanceDefinition",
                                              _gen_output=self.generate_info_supply_chain_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)


    def find_solution_blueprints(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the list of solution blueprint elements that contain the search string.
           https://egeria-project.org/concepts/solution-blueprint

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=max_paging_size], optional
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            - additional optional specifications for the search.
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        {
          "class" : "FilterRequestBody",
          "filter" : "add name",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_blueprints(search_string, classification_names, metadata_element_types,
                                                  starts_with, ends_with, ignore_case, start_from,
                                                  page_size, output_format, output_format_set, body))
        return response

    def find_all_solution_blueprints(self, classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/solution-blueprint
        """
        return self.find_solution_blueprints("*", classification_names, metadata_element_types,
                                              starts_with, ends_with, ignore_case, start_from,
                                              page_size, output_format, output_format_set, body)


    async def _async_get_solution_blueprint_by_guid(self, guid: str, body: dict = None,
                                                    output_format: str = "JSON") -> dict | str:
        """Return the properties of a specific solution blueprint. Async Version.

            Parameters
            ----------
            guid: str
                guid of the solution blueprint to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        validate_guid(guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{guid}/retrieve")

        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_blueprint_output(element, None, output_format)
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_solution_blueprint_by_guid(self, guid: str, body: dict = None, output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific solution blueprint.

            Parameters
            ----------
            guid: str
                guid of the solution blueprint to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_solution_blueprint_by_guid(guid, body, output_format))
        return response

    async def _async_get_solution_blueprints_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                                     page_size: int = max_paging_size,
                                                     output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution blueprints with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of information supply chains matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-blueprints/by-name"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_blueprint_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_solution_blueprints_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                        page_size: int = max_paging_size, output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution blueprints with a particular name.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of information supply chains matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_solution_blueprints_by_name(search_filter, body, start_from, page_size, output_format))
        return response



    #
    #   Components
    #

    @dynamic_catch
    async def _async_create_solution_component(self, body: dict | NewElementRequestBody) -> str:
        """Create a solution component. To set a lifecycle status
            use a NewSolutionElementRequestBody which has a default status of DRAFT. Using a
            NewElementRequestBody sets the status to ACTIVE.
            Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing parameters of the creation.
            A dictionary containing the definition of the component to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----
        With lifecycle:

        Body structure:
        {
          "class": "NewElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "SolutionComponentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "solutionComponentType": "add optional type for this component",
            "versionIdentifier": "add version for this component",
            "plannedDeployedImplementationType": "add details of the type of implementation for this component",
            "userDefinedStatus" : "Add own status here if initialStatus=OTHER",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "initialStatus" : "DRAFT",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components")

        return await self._async_create_element_body_request(url, ["SolutionComponentProperties"], body)

    @dynamic_catch
    def create_solution_component(self, body: dict | NewElementRequestBody) -> str:
        """Create a solution component. To set a lifecycle status
            use a NewSolutionElementRequestBody which has a default status of DRAFT. Using a
            NewElementRequestBody sets the status to ACTIVE.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the definition of the component to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----
        With lifecycle:

        Body structure:
        {
          "class": "NewElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "SolutionComponentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "solutionComponentType": "add optional type for this component",
            "versionIdentifier": "add version for this component",
            "plannedDeployedImplementationType": "add details of the type of implementation for this component",
            "userDefinedStatus" : "Add own status here if initialStatus=OTHER",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "initialStatus" : "DRAFT",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_component(body))
        return response

    @dynamic_catch
    async def _async_create_solution_component_from_template(self, body: dict| TemplateRequestBody) -> str:
        """ Create a new solution component using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dictionary containing the definition of the solution component to create.

        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/from-template")

        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create Solution Component from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_solution_component_from_template(self, body: dict| TemplateRequestBody) -> str:
        """ Create a new solution component using an existing metadata element
                 as a template.  The template defines additional classifications and relationships that should be
                 added to
                  the new element.


                Parameters
                ----------
                body: dict| TemplateRequestBody
                    A dictionary containing the definition of the solution component to create.

                Returns
                -------

                str - guid of the supply chain created.

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                ----

                Body structure:
                {
                  "class": "TemplateRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": {{isotime}},
                  "forLineage": false,
                  "forDuplicateProcessing": false,
                  "anchorGUID": "add guid here",
                  "isOwnAnchor": false,
                  "parentGUID": "add guid here",
                  "parentRelationshipTypeName": "add type name here",
                  "parentRelationshipProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                      "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "New description"
                      }
                    }
                  },
                  "parentAtEnd1": false,
                  "templateGUID": "add guid here",
                  "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                      "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "New description"
                      }
                    }
                  },
                  "placeholderPropertyValues":  {
                    "placeholder1": "propertyValue1",
                    "placeholder2": "propertyValue2"
                  }
                }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_component_from_template(body))
        return response

    @dynamic_catch
    async def _async_update_solution_component(self, guid: str, body: dict | UpdateElementRequestBody,
                                               ) -> None:
        """ Update the properties of a solution component. Async Version.

        Parameters
        ----------
        guid: str
            guid of the solution component to update.
        body: dict | UpdateElementRequestBody
            A dictionary containing the updates to the component.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "SolutionComponentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "solutionComponentType": "add namespace for this component",
            "plannedDeployedImplementationType": "add details of the type of implementation for this component",
            "versionIdentifier": "add version for this component",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{guid}/update")

        await self._async_update_element_body_request(url, ["SolutionComponentProperties"], body)

    @dynamic_catch
    def update_solution_component(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a solution component. Async Version.

        Parameters
        ----------
        guid: str
            guid of the solution component to update.
        body: dict | UpdateElementRequestBody
            A dictionary containing the updates to the component.
        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "SolutionComponentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "solutionComponentType": "add namespace for this component",
            "plannedDeployedImplementationType": "add details of the type of implementation for this component",
            "versionIdentifier": "add version for this component",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_solution_component(guid, body))

    @dynamic_catch
    async def _async_link_subcomponent(self, component_guid: str, sub_component_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution component. Async Version.

        Parameters
        ----------
        component_guid: str
            guid of the blueprint to connect to.
        sub_component_guid: str
            guid of the component to link.
        body: dict | NewRelationshipRequestBody
            The body describing the link.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component_guid}/subcomponents/{sub_component_guid}/attach")

        await self._async_new_relationship_request(url, ["SolutionCompositionProperties"], body)
        logger.info(f"Linked Subcomponent {component_guid} -> {sub_component_guid}")

    @dynamic_catch
    def link_subcomponent(self, component_guid: str, sub_component_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution component.

                Parameters
                ----------
                component_guid: str
                    guid of the blueprint to connect to.
                sub_component_guid: str
                    guid of the component to link.
                body: dict | NewRelationshipRequestBody
                    The body describing the link.

                Returns
                -------
                None

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                ----

                Body structure:
                {
                  "class" : "NewRelationshipRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "forLineage" : false,
                  "forDuplicateProcessing" : false
                }
                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_subcomponent(component_guid, sub_component_guid, body))
    @dynamic_catch
    async def _async_detach_sub_component(self, parent_component_guid: str, member_component_guid: str,
                                          body: dict |DeleteRequestBody = None) -> None:
        """ Detach a solution component from a solution component.
            Async Version.

        Parameters
        ----------
        parent_component_guid: str
            guid of the parent component to disconnect from.
        member_component_guid: str
            guid of the member (child) component to disconnect.
        body: dict
            The body describing the request.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{parent_component_guid}/subcomponents/{member_component_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached components  {parent_component_guid} -> {member_component_guid}")

    @dynamic_catch
    def detach_sub_component(self, parent_component_guid: str, member_component_guid: str, body: dict| DeleteRequestBody = None) -> None:
        """ Detach a solution component from a solution component.
            Async Version.

        Parameters
        ----------
        parent_component_guid: str
            guid of the parent component to disconnect from.
        member_component_guid: str
            guid of the member (child) component to disconnect.
        body: dict | DeleteRequestBody
            The body describing the request.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_sub_component(parent_component_guid, member_component_guid, body))

    @dynamic_catch
    async def _async_link_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution component as a peer in a solution. Async Version.

        Parameters
        ----------
        component1_guid: str
            GUID of the first component to link.
        component2_guid: str
           GUID of the second component to link.
        body: dict | NewRelationshipRequestBody
            The body describing the link.


        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "properties": {
             "class": "SolutionLinkingWireProperties",
             "label": "",
             "description": "",
             "informationSupplyChainSegmentGUIDs": []
          },
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component1_guid}/wired-to/{component2_guid}/attach")
        await self._async_new_relationship_request(url, ["SolutionLinkingWireProperties"], body)
        logger.info(f"Linked Solution Linking wires between {component1_guid} -> {component2_guid}")

    @dynamic_catch
    def link_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution component as a peer in a solution.

                Parameters
                ----------
                component1_guid: str
                    GUID of the first component to link.
                component2_guid: str
                   GUID of the second component to link.
                body: dict | NewRelationshipRequestBody
                    The body describing the link.

                Returns
                -------
                None

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                ----

                Body structure:
                {
                  "class": "NewRelationshipRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "properties": {
                     "class": "SolutionLinkingWireProperties",
                     "label": "",
                     "description": "",
                     "informationSupplyChainSegmentGUIDs": []
                  },
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }
                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_solution_linking_wire(component1_guid, component2_guid, body))

    @dynamic_catch
    async def _async_detach_solution_linking_wire(self, component1_guid: str, component2_guid: str,
                                                  body: dict | DeleteRequestBody = None) -> None:
        """ Detach a solution component from a peer solution component.
            Async Version.

        Parameters
        ----------
        component1_guid: str
            GUID of the first component to unlink.
        component2_guid: str
            GUID of the second component to unlink.
        body: dict | DeleteRequestBody
            The body describing the request.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component1_guid}/wired-to/{component2_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached solution linking wire between  {component1_guid} -> {component2_guid}")

    @dynamic_catch
    def detach_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict | DeleteRequestBody = None) -> None:
        """ Detach a solution component from a peer solution component.
                    Async Version.

                Parameters
                ----------
                component1_guid: str
                    GUID of the first component to unlink.
                component2_guid: str
                    GUID of the second component to unlink.
                body: dict | DeleteRequestBody
                    The body describing the request.
                    The body describing the request.

                Returns
                -------
                None

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                ----

                Body structure:
                {
                  "class" : "DeleteRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "forLineage" : false,
                  "forDuplicateProcessing" : false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_solution_linking_wire(component1_guid, component2_guid, body))

    @dynamic_catch
    async def _async_delete_solution_component(self, solution_component_guid: str, cascade_delete: bool = False,
                                               body: dict  | DeleteRequestBody= None) -> None:
        """Delete a solution component. Async Version.

           Parameters
           ----------
           solution_component_guid: str
               guid of the component to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict | DeleteRequestBody, optional
               A dictionary containing parameters for the deletion.

           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{solution_component_guid}/delete")
        await self._async_delete_request(url, body, cascade_delete=cascade_delete)
        logger.info(f"Deleted Solution Component  {solution_component_guid} with cascade {cascade_delete}")

    @dynamic_catch
    def delete_solution_component(self, solution_component_guid: str, cascade_delete: bool = False,
                                  body: dict | DeleteRequestBody = None) -> None:
        """Delete a solution component.
           Parameters
           ----------
           solution_component_guid: str
               guid of the component to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict | DeleteRequestBody, optional
               A dictionary containing parameters for the deletion.

           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_solution_component(solution_component_guid, cascade_delete, body))

    async def _async_find_solution_components(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """ Retrieve the solution component elements that contain the search string. The solutions components returned
            include information about consumers, actors, and other solution components that are associated with them.
            https://egeria-project.org/concepts/solution-components
            Async version.

        Parameters
        ----------
        search_filter: str
            - search_filter string to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search - supersedes search filter,
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of solution components or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----
        Body structure:
        {
          "class": "FilterRequestBody",
         "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add name here"
        }
        """



        url = f"{self.solution_architect_command_root}/solution-components/by-search-string"

        return await self._async_find_request(url, _type="GovernanceDefinition",
                                              _gen_output=self.generate_info_supply_chain_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)

    def find_solution_components(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """ Retrieve the solution component elements that contain the search string. The solutions components returned
            include information about consumers, actors, and other solution components that are associated with them.
            https://egeria-project.org/concepts/solution-components

        Parameters
        ----------
        search_filter: str
            - search_filter string to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.- supersedes search filter,
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of solution components or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----
        Body structure:
        {
          "class": "FilterRequestBody",
         "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add name here"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_components(search_string, classification_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body))
        return response

    def find_all_solution_components(self, classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve a list of all solution component elements
        https://egeria-project.org/concepts/solution-components
        """
        return self.find_solution_components("*", classification_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body)

    async def _async_get_solution_components_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                                     page_size: int = 0, output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution components with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval. Filter parameter in body over-rides search-filter.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of solution components matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        if body is None:
            body = {
                "filter": search_filter,
                }

        url = (f"{self.solution_architect_command_root}/solution-components/by-name"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_components_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_solution_components_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                        page_size: int = max_paging_size, output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution components with a particular name.

            Parameters
            ----------
            search_filter: str
                name of the solution component to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval. Filter parameter in body over-rides search-filter.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of solution components matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_solution_components_by_name(search_filter, body, start_from, page_size, output_format))
        return response

    async def _async_get_solution_component_by_guid(self, guid: str, body: dict = None,
                                                    output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific solution component. Async Version.

            Parameters
            ----------
            guid: str
                guid of the solution component to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            dict - details of the solution component

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        validate_guid(guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{guid}/retrieve")

        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_components_output(element, None, output_format)
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_solution_component_by_guid(self, guid: str, body: dict = None, output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific solution component.

            Parameters
            ----------
            guid: str
                guid of the solution component to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            dict - details of the solution component

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_solution_component_by_guid(guid, body, output_format))
        return response



    def get_component_related_elements(self, guid: str) -> dict:
        """ Get related elements about the component"""
        response = self.get_solution_component_by_guid(guid, output_format='JSON')

        if isinstance(response, str):
            return None

        sub_component_guids = []
        actor_guids = []
        blueprint_guids = []
        supply_chain_guids = []
        parent_component_guids = []

        sub_components = response.get("subComponents",{})
        for sub_component in sub_components:
            sub_component_guids.append(sub_component["elementHeader"]["guid"])

        actors = response.get("actors",{})
        for actor in actors:
            actor_guids.append(actor["elementHeader"]["guid"])

        blueprints = response.get("blueprints",{})
        for blueprint in blueprints:
            blueprint_guids.append(blueprint["relatedElement"]['elementHeader']["guid"])

        context = response.get("context",[])
        for c in context:
            supply_chains = c.get("owningInformationSupplyChains", [])
            if supply_chains:
                for chain in supply_chains:
                    supply_chain_guids.append(chain['relatedElement']["elementHeader"]["guid"])

            parent_components = c.get("parentComponents",[])
            if parent_components:
                for parent_component in parent_components:
                    parent_component_guids.append(parent_component["elementHeader"]["guid"])

        return {
            "sub_component_guids": sub_component_guids,
            "actor_guids": actor_guids,
            "blueprint_guids": blueprint_guids,
            "supply_chain_guids": supply_chain_guids,
            "parent_component_guids": parent_component_guids,
            }


    async def _async_get_solution_component_implementations(self, solution_component_guid: str, body: dict = None,
                                                            start_from: int = 0, page_size: int = 0,
                                                            output_format: str = "JSON") -> dict | str:
        """ Retrieve the list of metadata elements that are associated with the solution component via the
            ImplementedBy relationship. Async Version.

            Parameters
            ----------
            solution_component_guid: str
                guid of the solution component to retrieve.
            body: dict, optional
                A dictionary containing parameters for the retrieval.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            dict - details of the solution component implementations.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "limitResultsByStatus": []
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false,
              "sequencingOrder": "",
              "sequencingProperty": ""
            }

        """
        validate_guid(solution_component_guid)

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size), ])

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{solution_component_guid}/implementations{possible_query_params}")

        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_roles_output(element, None, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_solution_component_implementations(self, solution_component_guid: str, body: dict = None,
                                               start_from: int = 0, page_size: int = max_paging_size,
                                               output_format: str = "JSON") -> dict | str:
        """ Retrieve the list of metadata elements that are associated with the solution component via the
            ImplementedBy relationship.

            Parameters
            ----------
            solution_component_guid: str
                guid of the solution component to retrieve.
            body: dict, optional
                A dictionary containing parameters for the retrieval.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            dict - details of the solution component implementations.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "limitResultsByStatus": []
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false,
              "sequencingOrder": "",
              "sequencingProperty": ""
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_solution_component_implementations(solution_component_guid, body, start_from, page_size,
                                                               output_format))
        return response



    #
    #   Roles
    #
    @dynamic_catch
    async def _async_create_solution_role(self, body: dict | NewElementRequestBody) -> str:
        """ Create a solution role. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the properties of the solution role to create.

        Returns
        -------

        str - guid of the role created.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "SolutionRoleProperties",
            "qualifiedName": "add unique name here",
            "name": "add short name here",
            "description": "add description here",
            "scope": "add scope of role here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles")

        return await self._async_create_element_body_request(url, ["SolutionRoleProperties"], body)

    @dynamic_catch
    def create_solution_role(self, body: dict| NewElementRequestBody) -> str:
        """Create a solution role. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A dictionary containing the properties of the solution role to create.

        Returns
        -------

        str - guid of the role created.

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "SolutionRoleProperties",
            "qualifiedName": "add unique name here",
            "name": "add short name here",
            "description": "add description here",
            "scope": "add scope of role here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_role(body))
        return response

    @dynamic_catch
    async def _async_create_solution_role_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new metadata element to represent a solution role using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async Version.


        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dictionary containing the properties of the solution role to create.


        Returns
        -------

        str - guid of the supply chain created.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "anchorGUID": "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
              "description": {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue": "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1": "propertyValue1",
            "placeholder2": "propertyValue2"
          }
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/from-template")
        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create Solution Role from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_solution_role_from_template(self, body: dict |TemplateRequestBody) -> str:
        """ Create a new solution component using an existing metadata element
                 as a template.  The template defines additional classifications and relationships that should be
                 added to
                  the new element.


                Parameters
                ----------
                body: dict | TemplateRequestBody
                    A dictionary containing the properties of the solution role to create.

                Returns
                -------

                str - guid of the supply chain created.

                Raises
                ------
                InvalidParameterException
                    one of the parameters is null or invalid or
                PropertyServerException
                    There is a problem adding the element properties to the metadata repository or
                UserNotAuthorizedException
                    the requesting user is not authorized to issue this request.

                Notes
                ----

                Body structure:
                {
                  "class": "TemplateRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": {{isotime}},
                  "forLineage": false,
                  "forDuplicateProcessing": false,
                  "anchorGUID": "add guid here",
                  "isOwnAnchor": false,
                  "parentGUID": "add guid here",
                  "parentRelationshipTypeName": "add type name here",
                  "parentRelationshipProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                      "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "New description"
                      }
                    }
                  },
                  "parentAtEnd1": false,
                  "templateGUID": "add guid here",
                  "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                      "description": {
                        "class": "PrimitiveTypePropertyValue",
                        "typeName": "string",
                        "primitiveValue": "New description"
                      }
                    }
                  },
                  "placeholderPropertyValues":  {
                    "placeholder1": "propertyValue1",
                    "placeholder2": "propertyValue2"
                  }
                }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_role_from_template(body))
        return response

    @dynamic_catch
    async def _async_update_solution_role(self, guid: str, body: dict |UpdateElementRequestBody) -> None:
        """ Update the properties of a solution role. Async Version.

        Parameters
        ----------
        guid: str
            guid of the solution role to update.
        body: dict
            A dictionary containing the updates to the component.
        replace_all_properties: bool, optional, default is False
            Whether to replace all properties with those provided in the body or to merge with existing properties.

        Returns
        -------

        None

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
         {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "SolutionRoleProperties",
            "qualifiedName": "add unique name here",
            "name": "add short name here",
            "description": "add description here",
            "scope": "add scope of role here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{guid}/update")

        await self._async_update_element_body_request(url, ["SolutionRoleProperties"], body)

    @dynamic_catch
    def update_solution_role(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a solution role.

        Parameters
        ----------
        guid: str
            guid of the solution role to update.
        body: dict | UpdateElementRequestBody
            A dictionary containing the updates to the role.

        Returns
        -------

        None

        Raises
        ------
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "SolutionRoleProperties",
            "qualifiedName": "add unique name here",
            "name": "add short name here",
            "description": "add description here",
            "scope": "add scope of role here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_solution_role(guid, body))

    @dynamic_catch
    async def _async_link_component_to_actor(self, role_guid: str, component_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution role. Async Version.

        Parameters
        ----------
        role_guid: str
            guid of the role to link.
        component_guid: str
            guid of the component to link.
        body: dict | NewRelationshipRequestBody
            A dictionary containing the properties of the relationship to create.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "SolutionComponentActorProperties",
            "role": "Add role here",
            "description": "Add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{role_guid}/solution-roles/{component_guid}/attach")

        await self._async_new_relationship_request(url, ["InformationSupplyChainLinkProperties"], body)
        logger.info(f"Linked Role to Component {role_guid} -> {component_guid}")

    @dynamic_catch
    def link_component_to_actor(self, role_guid: str, component_guid: str, body: dict | NewRelationshipRequestBody) -> None:
        """ Attach a solution component to a solution role.

            Parameters
            ----------
            role_guid: str
                guid of the role to link.
            component_guid: str
                guid of the component to link.
            body: dict | NewRelationshipRequestBody
                A dictionary containing the properties of the relationship to create.

            Returns
            -------
            None

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            ----

            Body structure:
            {
              "class" : "NewRelationshipRequestBody",
              "properties": {
                "class": "SolutionComponentActorProperties",
                "role": "Add role here",
                "description": "Add description here",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }

                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_component_to_actor(role_guid, component_guid, body))

    @dynamic_catch
    async def _async_detach_component_actor(self, role_guid: str, component_guid: str, body: dict | DeleteRequestBody = None) -> None:
        """ Detach a solution role from a solution component.
            Async Version.

        Parameters
        ----------
        role_guid: str
            guid of the role to disconnect from.
        component_guid: str
            guid of the component to disconnect.
        body: dict | DeleteRequestBody, optional
            A dictionary containing the properties of the relationship to create.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{role_guid}/solution-component-actors/{component_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached role from component  {role_guid} -> {component_guid}")

    @dynamic_catch
    def detach_component_actore(self, role_guid: str, component_guid: str, body: dict |DeleteRequestBody = None) -> None:
        """ Detach a solution role from a solution component.

        Parameters
        ----------
        role_guid: str
            guid of the role to disconnect from.
        component_guid: str
            guid of the component to disconnect.
        body: dict | DeleteRequestBody, optional
            A dictionary containing the properties of the relationship to create.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        ----

        Body structure:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_component_actor(role_guid, component_guid, body))

    @dynamic_catch
    async def _async_delete_solution_role(self, guid: str,  body: dict | DeleteRequestBody= None, cascade_delete: bool = False,) -> None:
        """Delete a solution role. Async Version.

           Parameters
           ----------
           guid: str
               guid of the role to delete.
            body: dict | DeleteRequestBody, optional
               A dictionary containing parameters for the deletion.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?


           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{guid}/delete")

        await self._async_delete_request(url, body, cascade_delete=cascade_delete)
        logger.info(f"Delete solution rule  {guid} with cascade {cascade_delete}")

    @dynamic_catch
    def delete_solution_role(self, guid: str, body: dict | DeleteRequestBody = None,cascade_delete: bool = False) -> None:
        """Delete a solution role. Async Version.

           Parameters
           ----------
           guid: str
               guid of the role to delete.
           body: dict | DeleteRequestBody, optional
               A dictionary containing parameters for the deletion.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?

           Returns
           -------
           None

           Raises
           ------
           InvalidParameterException
               one of the parameters is null or invalid or
           PropertyServerException
               There is a problem adding the element properties to the metadata repository or
           UserNotAuthorizedException
               the requesting user is not authorized to issue this request.

           Notes
           ----

           Body structure:
            {
              "class": "DeleteRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_solution_role(guid, cascade_delete, body))

    async def _async_find_solution_roles(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor
           Async version.

        Parameters
        ----------
        search_filter: str
            - search_filter string to search for.
        body: dict, optional, default = None
            - additional optional specifications for the search. Body details, if provided, override search-filter.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching

        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of solution role structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----
        Sample body:
        
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add name here"
        }
        """


        url = f"{self.solution_architect_command_root}/solution-roles/by-search-string"

        return await self._async_find_request(url, _type="GovernanceDefinition",
                                              _gen_output=self.generate_info_supply_chain_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)

    def find_solution_roles(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve the list of solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor

        Parameters
        ----------
        search_filter: str
            - search_filter string to search for.
        body: dict, optional, default = None
            - additional optional specifications for the search.  Body details, if provided, override search-filter.

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=max_paging_size], optional
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            - additional optional specifications for the search.  Body details, if provided, override search-filter.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----
        Sample body:
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add name here"
        }
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_roles(search_string, classification_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body))
        return response

    def find_all_solution_roles(self,  classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str = None,
                                    body: dict| SearchStringRequestBody = None) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/actor
        """
        return self.find_solution_roles("*", classification_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body)


    async def _async_get_solution_roles_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                                page_size: int = max_paging_size,
                                                output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution roles with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the iroles to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of solution roles matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-components/by-name"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_roles_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_solution_roles_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                   page_size: int = max_paging_size, output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution roles with a particular name.

            Parameters
            ----------
            search_filter: str
                name of the solution roles to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=max_paging_size], optional
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of solution roles matching the name.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "FilterRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": "Add name here"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_solution_roles_by_name(search_filter, body, start_from, page_size, output_format))
        return response


    async def _async_get_solution_role_by_guid(self, guid: str, body: dict = None,
                                               output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific solution role. Async Version.

            Parameters
            ----------
            guid: str
                guid of the solution role to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            dict - details of the solution role

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        validate_guid(guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{guid}/retrieve")

        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_roles_output(element, None, output_format)
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_solution_role_by_guid(self, guid: str, body: dict = None, output_format: str = "JSON") -> dict | str:
        """ Return the properties of a specific solution role.

            Parameters
            ----------
            guid: str
                guid of the solution role to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown
            Returns
            -------
            dict - details of the solution role

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.

            Notes
            -----
            Body structure:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": {{isotime}},
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing : false
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_solution_role_by_guid(guid, body, output_format))
        return response



if __name__ == "__main__":
    print("Main-Metadata Explorer")

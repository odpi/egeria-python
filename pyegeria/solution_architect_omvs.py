"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Solution Architect OMVS module.


"""

import asyncio
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from httpx import Response
from pyegeria.output_formatter import make_preamble, make_md_attribute, generate_output, extract_mermaid_only, \
    extract_basic_dict, MD_SEPARATOR, generate_entity_dict
from pyegeria import validate_guid
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND
from pyegeria.utils import body_slimmer

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


class SolutionArchitect(Client):
    """SolutionArchitect is a class that extends the Client class. The Solution Architect OMVS provides APIs for
      searching for architectural elements such as information supply chains, solution blueprints, solution components
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
        Client.__init__(self, view_server, platform_url, user_id=user_id, user_pwd=user_pwd, token=token, )

    #
    # Extract properties functions
    #

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

    def _extract_info_supply_chain_properties(self, element: dict) -> dict:
        """
        Extract properties from an information supply chain element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element['properties']
        qualified_name = properties.get("qualifiedName", None)
        display_name = properties.get("displayName", None)
        description = properties.get("description", None)
        scope = properties.get("scope", None)
        purposes = properties.get("purposes", [])
        purpose_md = ""
        if len(purposes) > 0:
            for purpose in purposes:
                purpose_md += f"{purpose},\n"
        extended_properties = properties.get("extendedProperties", {})
        additional_properties = properties.get("additionalProperties", {})
        mer = f"```mermaid\n\n{element.get('mermaidGraph', None)}\n\n```"

        segments = element.get("segments", [])
        segments_list = []
        if len(segments) > 0:
            for segment in segments:
                segment_dict = {}
                segment_guid = segment['elementHeader'].get("guid", "")
                segment_props = segment['properties']
                segment_qname = segment_props.get("qualifiedName", "")
                segment_display_name = segment_props.get("displayName", "")
                segment_description = segment_props.get("description", "")
                segment_scope = segment_props.get("scope", "")
                segment_integration_style = segment_props.get("integrationStyle", "")
                segment_estimated_volumetrics = segment_props.get("estimatedVolumetrics", "")
                segment_dict["segment_display_name"] = segment_display_name
                segment_dict["segment_qname"] = segment_qname
                segment_dict["segment_guid"] = segment_guid
                segment_dict["segment_description"] =  segment_description
                segment_dict["segment_scope"] = segment_scope
                segment_dict["segment_estimated_volumetrics"] = segment_estimated_volumetrics
                segments_list.append(segment_dict)

        return {
            'GUID': guid,
            'qualified_name': qualified_name,
            'display_name': display_name,
            'description': description,
            'scope': scope,
            'purposes': purpose_md,
            'extended_properties': extended_properties,
            'additional_properties': additional_properties,
            'segments': segments_list,
            'mermaid': mer
        }

    def _extract_solution_blueprint_properties(self, element: dict) -> dict:
        """
        Extract properties from a solution blueprint element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        element_properties = element['properties']
        display_name = element_properties.get("displayName", None)
        description = element_properties.get("description", None)
        version = element_properties.get("version", None)
        qualified_name = element_properties.get("qualifiedName", None)

        solution_components = element.get('solutionComponents', None)
        solution_components_md = ""
        if solution_components:
            for solution_component in solution_components:
                sol_comp_prop = solution_component['solutionComponent']['properties']
                sol_comp_name = sol_comp_prop.get("displayName", None)
                sol_comp_desc = sol_comp_prop.get("description", None)
                solution_components_md += '{' + f" {sol_comp_name}:\t {sol_comp_desc}" + " },\n"
        mer = f"```mermaid\n\n{element.get('mermaidGraph', None)}\n\n```"

        return {
            'GUID': guid,
            'qualified_name': qualified_name,
            'display_name': display_name,
            'description': description,
            'version': version,
            'solution_components': solution_components_md,
            'mermaid': mer
        }

    def _extract_solution_roles_properties(self, element: dict) -> dict:
        """
        Extract properties from a solution role element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        element_properties = element['properties']
        display_name = element_properties.get("title", None)
        role_id = element_properties.get("roleId", None)
        scope = element_properties.get("scope", None)
        description = element_properties.get("description", None)
        domain_identifier = element_properties.get("domainIdentifier", None)
        qualified_name = element_properties.get("qualifiedName", None)

        solution_components = element.get('solutionComponents', None)
        solution_components_md = ""
        if solution_components:
            for solution_component in solution_components:
                sol_comp_prop = solution_component.get('relationshipProperties', None)
                if sol_comp_prop:
                    sol_comp_name = sol_comp_prop.get("role", None)
                    sol_comp_desc = sol_comp_prop.get("description", None)
                    solution_components_md += "{" + f" {sol_comp_name}:\t {sol_comp_desc}" + " },\n"

        return {
            'GUID': guid,
            'qualified_name': qualified_name,
            'display_name': display_name,
            'description': description,
            'role_id': role_id,
            'scope': scope,
            'domain_identifier': domain_identifier,
            'solution_components': solution_components_md
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

    def _extract_solution_components_properties(self, element: Union[Dict,List[Dict]]) -> dict:
        """
        Extract properties from a solution component element.

        Args:
            element: Dictionary containing element data

        Returns:
            Dictionary with extracted properties
        """

        guid = element['elementHeader'].get("guid", None)
        properties = element.get('glossaryCategoryProperties', element.get('properties', {}))
        display_name = properties.get("displayName", None)
        description = properties.get("description", None)
        component_type = properties.get("solutionComponentType", properties.get("componentType", None))
        version = properties.get("version", None)
        qualified_name = properties.get("qualifiedName", None)

        # Extract extended properties
        extended_props = properties.get("extendedProperties", None)
        extended_props_md = ""
        if extended_props:
            for key in extended_props.keys():
                extended_props_md += "{" + f" {key}: {extended_props[key]}" + " }, "

        # Extract additional properties
        additional_props = properties.get("additionalProperties", None)
        additional_props_md = ""
        if additional_props:
            for key in additional_props.keys():
                additional_props_md += "{" + f" {key}: {additional_props[key]}" + " }, "

        # Extract blueprints
        blueprints_md = ""
        blueprints = element.get('blueprints', None)
        if blueprints:
            for blueprint in blueprints:
                if 'relatedElement' in blueprint:
                    bp_q_name = blueprint["relatedElement"]['properties']['qualifiedName']
                    blueprints_md +=  f" {bp_q_name}, \n"
                elif 'blueprint' in blueprint:
                    bp_prop = blueprint['blueprint']['properties']
                    bp_name = bp_prop.get("displayName", None)
                    bp_desc = bp_prop.get("description", None)
                    blueprints_md += "{" + f" {bp_name}:\t {bp_desc}" + " },\n"

        # Extract parent components
        parent_comp_md = ""
        context = element.get("context", None)
        if context:
            parent_components = element.get('parentComponents', None)
            if parent_components:
                for parent_component in parent_components:
                    parent_comp_prop = parent_component['parentComponent']['properties']
                    parent_comp_name = parent_comp_prop.get("name", None)
                    parent_comp_desc = parent_comp_prop.get("description", None)
                    parent_comp_md += f" {parent_comp_name}"

        # Extract sub components
        sub_comp_md = ""
        sub_components = element.get('subComponents', None)
        if sub_components:
            for sub_component in sub_components:
                sub_comp_prop = sub_component['properties']
                sub_comp_name = sub_comp_prop.get("displayName", None)
                sub_comp_desc = sub_comp_prop.get("description", None)
                sub_comp_md +=  f" {sub_comp_name}"

        comp_graph = element.get('mermaidGraph', None)

        return {
            'GUID': guid,
            'qualified_name': qualified_name,
            'display_name': display_name,
            'description': description,
            'component_type': component_type,
            'version': version,
            'blueprints': blueprints_md,
            'parent_components': parent_comp_md,
            'sub_components': sub_comp_md,
            'additional_properties': additional_props_md,
            'extended_properties': extended_props_md,
            'mermaid_graph': comp_graph
        }

    #
    # Markdown output support
    #
    def generate_info_supply_chain_output(self, elements: list | dict, search_string: str,
                                          output_format: str = 'MD') -> str | list:
        """
        Generate output for information supply chains in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing information supply chain elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Handle MERMAID and DICT formats
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)
        elif output_format == "DICT":
            # return extract_basic_dict(elements)
            return self._extract_supply_chain_list(elements)
        # For other formats (MD, FORM, REPORT, LIST), use generate_output
        elif output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [
                {'name': 'Name', 'key': 'display_name'}, 
                {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'Scope', 'key': 'scope'},
                {'name': 'Description', 'key': 'description', 'format': True}
            ]

            return generate_output(
                elements=elements, 
                search_string=search_string, 
                entity_type="Information Supply Chain",
                output_format=output_format, 
                extract_properties_func=self._extract_info_supply_chain_properties,
                columns=columns if output_format == 'LIST' else None
            )

        # Default case
        return None

    def generate_solution_blueprint_output(self, elements: list | dict, search_string: str,
                                           output_format: str = 'MD') -> str | list:
        """
        Generate output for solution blueprints in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing solution blueprint elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Handle MERMAID and DICT formats
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)
        elif output_format == "DICT":
            return extract_basic_dict(elements)

        # For other formats (MD, FORM, REPORT, LIST), use generate_output
        elif output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [
                {'name': 'Blueprint Name', 'key': 'display_name'}, 
                {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'Version', 'key': 'version'},
                {'name': 'Description', 'key': 'description', 'format': True}
            ]

            return generate_output(
                elements=elements, 
                search_string=search_string, 
                entity_type="Solution Blueprint",
                output_format=output_format, 
                extract_properties_func=self._extract_solution_blueprint_properties,
                columns=columns if output_format == 'LIST' else None
            )

        # Default case
        return None

    def generate_solution_roles_output(self, elements: list | dict, search_string: str, output_format: str = 'MD') -> str | list:
        """
        Generate output for solution roles in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing solution role elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Handle MERMAID and DICT formats
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)
        elif output_format == "DICT":
            return extract_basic_dict(elements)

        # For other formats (MD, FORM, REPORT, LIST), use generate_output
        elif output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [
                {'name': 'Role Name', 'key': 'display_name'}, 
                {'name': 'Role ID', 'key': 'role_id'},
                {'name': 'Scope', 'key': 'scope'},
                {'name': 'Domain', 'key': 'domain_identifier'},
                {'name': 'Description', 'key': 'description', 'format': True}
            ]

            return generate_output(
                elements=elements, 
                search_string=search_string, 
                entity_type="Solution Role",
                output_format=output_format, 
                extract_properties_func=self._extract_solution_roles_properties,
                columns=columns if output_format == 'LIST' else None
            )

        # Default case
        return None

    def generate_solution_components_output(self, elements: list | dict, search_string: str,
                                            output_format: str = 'MD') -> str | list:
        """
        Generate output for solution components in the specified format.

        Given a set of elements representing solution components (either as a list or a dictionary),
        this function generates output in the specified format. The output includes various 
        attributes of the solution components, such as their names, descriptions, types, and 
        related information like blueprints, parents, and extended properties.

        Args:
            elements: Dictionary or list of dictionaries containing solution component elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Handle MERMAID and DICT formats
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)
        elif output_format == "DICT":
            return self._extract_component_list(elements)
            # return extract_basic_dict(elements)
            # add more to the body
        # For other formats (MD, FORM, REPORT, LIST), use generate_output
        elif output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [
                {'name': 'Component Name', 'key': 'display_name'}, 
                {'name': 'Component Type', 'key': 'component_type'},
                {'name': 'Version', 'key': 'version'},
                {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'Description', 'key': 'description', 'format': True}
            ]

            return generate_output(
                elements=elements, 
                search_string=search_string, 
                entity_type="Solution Component",
                output_format=output_format, 
                extract_properties_func=self._extract_solution_components_properties,
                columns=columns if output_format == 'LIST' else None
            )

        # Default case
        return None

    async def _async_create_info_supply_chain(self, body: dict) -> str:
        """Create an information supply. Async version.

        Parameters
        ----------
        body: dict
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
          "class": "NewInformationSupplyChainRequestBody",
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
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
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Supply Chain not created")

    def create_info_supply_chain(self, body: dict) -> str:
        """Create an information supply.

        Parameters
        ----------
        body: dict
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
          "class": "NewInformationSupplyChainRequestBody",
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
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
        response = loop.run_until_complete(self._async_create_info_supply_chain(body))
        return response

    async def _async_create_info_supply_chain_from_template(self, body: dict) -> str:
        """ Create a new metadata element to represent an information supply chain using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict
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

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Supply Chain not created")

    def create_info_supply_chain_from_template(self, body: dict) -> str:
        """ Create a new metadata element to represent an information supply chain using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element.

        Parameters
        ----------
        body: dict
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

    async def _async_update_info_supply_chain(self, guid: str, body: dict,
                                              replace_all_properties: bool = False) -> None:
        """ Update the properties of an information supply chain. Async Version.

        Parameters
        ----------
        guid: str
            guid of the information supply chain to update.
        body: dict
            A dictionary containing the updates to the supply chain.
        replace_all_properties: bool, optional
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
          "class": "UpdateInformationSupplyChainRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class" : "InformationSupplyChainProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
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
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/update?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_info_supply_chain(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
        """ Update the properties of an information supply chain. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to update.
            body: dict
                A dictionary containing the updates to the supply chain.
            replace_all_properties: bool, optional
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
              "class": "UpdateInformationSupplyChainRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "properties": {
                "class" : "InformationSupplyChainProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "scope": "add scope of this information supply chain's applicability.",
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
        loop.run_until_complete(self._async_update_info_supply_chain(guid, body, replace_all_properties))

    async def _async_create_info_supply_chain_segment(self, guid: str, body: dict) -> str:
        """Create an information supply chain segment and link it to its owning information supply chain.
         Async version.

        Parameters
        ----------
        guid: str
            guid of the owning information supply chain.
        body: dict
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain segment created.

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
          "class": "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class" : "InformationSupplyChainSegmentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }

       """
        validate_guid(guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/segments")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Supply Chain segment not created")

    def create_info_supply_chain_segment(self, guid: str, body: dict) -> str:
        """Create an information supply chain segment and link it to its owning information supply chain.

        Parameters
        ----------
        guid: str
            The guid of the information supply chain you are adding a segment to.
        body: dict
            A dictionary containing the definition of the supply chain to create.

        Returns
        -------

        str - guid of the supply chain segment created.

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
          "class": "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class" : "InformationSupplyChainSegmentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
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
        response = loop.run_until_complete(self._async_create_info_supply_chain_segment(guid, body))
        return response

    async def _async_update_info_supply_chain_segment(self, guid: str, body: dict,
                                                      replace_all_properties: bool = False) -> None:
        """ Update the properties of an information supply chain segment. Async Version.

        Parameters
        ----------
        guid: str
            guid of the information supply chain segment to update.
        body: dict
            A dictionary containing the updates to the supply chain segment.
        replace_all_properties: bool, optional
            Whether to replace all properties with those provided in the body or to merge with existing properties.

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
          "class": "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class" : "InformationSupplyChainSegmentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/segments/{guid}/update?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_info_supply_chain_segment(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
        """ Update the properties of an information supply chain segment. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain segment to update.
            body: dict
                A dictionary containing the updates to the supply chain segment .
            replace_all_properties: bool, optional
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
              "class": "InformationSupplyChainSegmentRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "properties": {
                "class" : "InformationSupplyChainSegmentProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "scope": "add scope of this information supply chain's applicability.",
                "integrationStyle": "style",
                "estimatedVolumetrics": {
                  "property1": "propertyValue1",
                  "property2": "propertyValue2"
                },
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
        loop.run_until_complete(self._async_update_info_supply_chain_segment(guid, body, replace_all_properties))

    def get_info_supply_chain_segment_by_guid(self, segment_guid: str, supply_chain_guid: str) -> str:
        """ Get information supply chain segment by GUID and return a MD for Dr.Egeria use."""
        info_supply_chain = self.get_info_supply_chain_by_guid(supply_chain_guid)
        segments = info_supply_chain["segments"]
        segment_md = "\n\n# Update Information Supply Chain Segment\n\n"
        for segment in segments:
            if segment["elementHeader"]["guid"] == segment_guid:
                segment_props = segment["properties"]
                segment_md += f"## Display Name\n\n{segment_props.get("displayName","")}\n\n"
                segment_md += f"## Information Supply Chain\n\n{info_supply_chain['properties']['qualifiedName']}\n\n"
                segment_md += f"## Description\n\n{segment_props.get("description","")}\n\n"
                segment_md += f"## Scope\n\n{segment_props.get('scope',"")}\n\n"
                segment_md += f"## Integration Style\n\n{segment_props.get('integrationStyle','')}\n\n"
                segment_md += f"## Estimated Volumetrics\n\n{segment_props.get('estimatedVolumetrics',{})}\n\n"
                segment_md += f"## Extended Properties\n\n{segment_props.get('extendedProperties',{})}\n\n"
                segment_md += f"## Additional Properties\n\n{segment_props.get('additionalProperties',{})}\n\n"
        return segment_md




    async def _async_link_info_supply_chain_segments(self, segment_guid1: str, segment_guid2: str, body: dict) -> None:
        """ Connect the information supply chain segments. Async Version.

        Parameters
        ----------
        segment_guid1: str
            guid of the first information supply chain segment to link.
        segment_guid2: str
            guid of the second information supply chain segment to link.
        body: dict
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
          "class": "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        validate_guid(segment_guid1)
        validate_guid(segment_guid2)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/segments/{segment_guid1}/link-to/{segment_guid2}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_info_supply_chain_segments(self, segment_guid1: str, segment_guid2: str, body: dict) -> None:
        """ Connect the information supply chain segments.

        Parameters
        ----------
        segment_guid1: str
            guid of the first information supply chain segment to link.
        segment_guid2: str
            guid of the second information supply chain segment to link.
        body: dict
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
          "class": "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_info_supply_chain_segments(segment_guid1, segment_guid2, body))

    async def _async_detach_info_supply_chain_segments(self, segment_guid1: str, segment_guid2: str,
                                                       body: dict = None) -> None:
        """ Detach two information supply chain segments from one another. Request body is optional.
            Async Version.

        Parameters
        ----------
        segment_guid1: str
            guid of the first information supply chain segment to link.
        segment_guid2: str
            guid of the second information supply chain segment to link.
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
        validate_guid(segment_guid1)
        validate_guid(segment_guid2)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/segments/{segment_guid1}/link-to{segment_guid2}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_info_supply_chain_segments(self, segment_guid1: str, segment_guid2: str, body: dict = None) -> None:
        """  Detach two information supply chain segments from one another. Request body is optional.

        Parameters
        ----------
        segment_guid1: str
            guid of the first information supply chain segment to link.
        segment_guid2: str
            guid of the second information supply chain segment to link.
        body: dict
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
          "class": "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_info_supply_chain_segments(segment_guid1, segment_guid2, body))

    async def _async_delete_info_supply_chain_segment(self, guid: str, body: dict = None) -> None:
        """Delete an information supply chain segment. Async Version.

           Parameters
           ----------
           guid: str
               guid of the information supply chain segment to delete.
           body: dict, optional
               A dictionary containing parameters of the deletion.

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
        validate_guid(guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/segments/{guid}/delete")

        await self._async_make_request("POST", url, body_slimmer(body))

    def delete_info_supply_chain_segment(self, guid: str, body: dict = None) -> None:
        """ Delete an information supply chain segment. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain segment to delete.
            body: dict, optional
                A dictionary containing parameters of the deletion.

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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_info_supply_chain_segment(guid, body))

    async def _async_delete_info_supply_chain(self, guid: str, body: dict = None) -> None:
        """Delete an information supply chain. Async Version.

           Parameters
           ----------
           guid: str
               guid of the information supply chain to delete.
           body: dict, optional
               A dictionary containing parameters of the deletion.

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
        validate_guid(guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"information-supply-chains/{guid}/delete")

        await self._async_make_request("POST", url, body_slimmer(body))

    def delete_info_supply_chain(self, guid: str, body: dict = None) -> None:
        """ Delete an information supply chain.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to delete.
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
        loop.run_until_complete(self._async_delete_info_supply_chain(guid, body))

    def find_all_information_supply_chains(self, start_from: int = 0, page_size: int = max_paging_size,
                                           output_format: str = "JSON") -> (list[dict] | str):
        """Retrieve a list of all information supply chains
        https://egeria-project.org/concepts/information-supply-chain
        """

        return self.find_information_supply_chains("*", start_from=start_from, page_size=page_size,
                                                   output_format=output_format)

    async def _async_find_information_supply_chains(self, search_filter: str = "*", add_implementation: bool = True,
                                                    starts_with: bool = True, ends_with: bool = False,
                                                    ignore_case: bool = False, start_from: int = 0,
                                                    page_size: int = max_paging_size, body: dict = None,
                                                    output_format: str = 'JSON') -> list[dict] | str:
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

        possible_query_params = query_string(
            [("addImplementation", add_implementation), ("startFrom", start_from), ("pageSize", page_size),
             ("startsWith", starts_with), ("endsWith", ends_with), ("ignoreCase", ignore_case), ])

        if search_filter is None or search_filter == "*":
            search_filter = None

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/information-supply-chains/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_info_supply_chain_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_information_supply_chains(self, filter: str = "*", add_implementation: bool = True,
                                       starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                       start_from: int = 0, page_size: int = max_paging_size, body: dict = None,
                                       output_format: str = 'JSON', ) -> list[dict] | str:
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

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_information_supply_chains(filter, add_implementation, starts_with, ends_with, ignore_case,
                                                       start_from, page_size, body, output_format))
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
        else:
            body["filter"] = search_filter

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

    async def _async_create_solution_blueprint(self, body: dict) -> str:
        """Create a solution blueprint. Async version.

        Parameters
        ----------
        body: dict
            A dictionary containing the definition of the blueprint to create.

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
          "class": "NewSolutionBlueprintRequestBody",
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
            "version": "add version here",
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
               f"solution-blueprints")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Blueprint not created")

    def create_solution_blueprint(self, body: dict) -> str:
        """Create an information supply.

        Parameters
        ----------
        body: dict
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
          "class": "NewSolutionBlueprintRequestBody",
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
            "version": "add version here",
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
        response = loop.run_until_complete(self._async_create_solution_blueprint(body))
        return response

    async def _async_create_solution_blueprint_from_template(self, body: dict) -> str:
        """ Create a new solution blueprint using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict
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

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Blueprint not created")

    def create_solution_blueprint_from_template(self, body: dict) -> str:
        """ Create a new solution blueprint using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element.

        Parameters
        ----------
        body: dict
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

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_solution_blueprint_from_template(body))
        return response

    async def _async_link_solution_component_to_blueprint(self, blueprint_guid: str, component_guid: str,
                                                          body: dict) -> None:
        """ Connect a solution component to a blueprint. Async Version.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to connect to.
        component_guid: str
            guid of the component to link.
        body: dict
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
          "class": "SolutionComponentLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class": "SolutionBlueprintCompositionProperties",
            "role": "add role here",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        validate_guid(blueprint_guid)
        validate_guid(component_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{blueprint_guid}/solution-components/{component_guid}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_solution_component_to_blueprint(self, blueprint_guid: str, component_guid: str, body: dict) -> None:
        """ Connect a solution component to a blueprint.

        Parameters
        ----------
        blueprint_guid: str
            guid of the blueprint to connect to.
        component_guid: str
            guid of the component to link.
        body: dict
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
          "class": "SolutionComponentLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class": "SolutionBlueprintCompositionProperties",
            "role": "add role here",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_solution_component_to_blueprint(blueprint_guid, component_guid, body))

    async def _async_detach_solution_component_from_blueprint(self, blueprint_guid: str, component_guid: str,
                                                              body: dict = None) -> None:
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
        validate_guid(blueprint_guid)
        validate_guid(component_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{blueprint_guid}/solution-components/{component_guid}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_solution_component_from_blueprint(self, blueprint_guid: str, component_guid: str,
                                                 body: dict = None) -> None:
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

    async def _async_delete_solution_blueprint(self, blueprint_guid: str, cascade_delete: bool = False,
                                               body: dict = None) -> None:
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
        if body:
            await self._async_make_request("POST", url, body_slimmer(body))
        else:
            await self._async_make_request("POST", url)

    def delete_solution_blueprint(self, blueprint_guid: str, cascade_delete: bool = False, body: dict = None) -> None:
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

    async def _async_update_solution_blueprint(self, guid: str, body: dict,
                                               replace_all_properties: bool = False) -> None:
        """ Update the properties of a solution blueprint. Async Version.

        Parameters
        ----------
        guid: str
            guid of the information supply chain to update.
        body: dict
            A dictionary containing the updates to the supply chain.
        replace_all_properties: bool, optional
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
          "class": "UpdateSolutionBlueprintRequestBody",
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
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-blueprints/{guid}/update?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_solution_blueprint(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
        """ Update the properties of a solution blueprint. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to update.
            body: dict
                A dictionary containing the updates to the supply chain.
            replace_all_properties: bool, optional
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
              "class": "UpdateSolutionBlueprintRequestBody",
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
        loop.run_until_complete(self._async_update_solution_blueprint(guid, body, replace_all_properties))

    async def _async_find_solution_blueprints(self, search_filter: str = "*", starts_with: bool = True,
                                              ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                              page_size: int = max_paging_size, body: dict = None,
                                              output_format: str = "JSON") -> list[dict] | str:
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

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with), ("endsWith", ends_with),
             ("ignoreCase", ignore_case), ])

        if search_filter is None or search_filter == "*":
            search_filter = None

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-blueprints/by-search-string"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_blueprint_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_blueprints(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
                                 ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size,
                                 body: dict = None, output_format: str = 'JSON') -> list[dict] | str:
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
            self._async_find_solution_blueprints(filter, starts_with, ends_with, ignore_case, start_from, page_size,
                                                 body, output_format))
        return response

    def find_all_solution_blueprints(self, start_from: int = 0, page_size: int = max_paging_size,
                                     output_format: str = "JSON") -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/solution-blueprint
        """
        return self.find_solution_blueprints("*", start_from=start_from, page_size=page_size,
                                             output_format=output_format)

    #
    #   Components
    #

    async def _async_create_solution_component(self, body: dict) -> str:
        """Create a solution component. Async version.

        Parameters
        ----------
        body: dict
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

        Body structure:
        {
          "class": "NewSolutionComponentRequestBody",
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "version": "add version here",
            "solutionComponentType": "type name here",
            "plannedDeployedImplementationType": "type name here",
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
               f"solution-components")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Solution component not created")

    def create_solution_component(self, body: dict) -> str:
        """Create a solution component. Async version.

        Parameters
        ----------
        body: dict
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

        Body structure:
        {
          "class": "NewSolutionComponentRequestBody",
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "version": "add version here",
            "solutionComponentType": "type name here",
            "plannedDeployedImplementationType": "type name here",
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
        response = loop.run_until_complete(self._async_create_solution_component(body))
        return response

    async def _async_create_solution_component_from_template(self, body: dict) -> str:
        """ Create a new solution component using an existing metadata element
         as a template.  The template defines additional classifications and relationships that should be added to
          the new element. Async Version.


        Parameters
        ----------
        body: dict
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

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Component not created")

    def create_solution_component_from_template(self, body: dict) -> str:
        """ Create a new solution component using an existing metadata element
                 as a template.  The template defines additional classifications and relationships that should be
                 added to
                  the new element.


                Parameters
                ----------
                body: dict
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

    async def _async_link_subcomponent(self, component_guid: str, sub_component_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution component. Async Version.

        Parameters
        ----------
        component_guid: str
            guid of the blueprint to connect to.
        sub_component_guid: str
            guid of the component to link.
        body: dict
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
          "class": "SolutionComponentLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "typeName": "string",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        validate_guid(component_guid)
        validate_guid(sub_component_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component_guid}/subcomponents/{sub_component_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body_slimmer(body))
        else:
            await self._async_make_request("POST", url)


    def link_subcomponent(self, component_guid: str, sub_component_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution component.

                Parameters
                ----------
                component_guid: str
                    guid of the blueprint to connect to.
                sub_component_guid: str
                    guid of the component to link.
                body: dict
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
                  "class": "SolutionComponentLinkRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": {{isotime}},
                  "forLineage": false,
                  "forDuplicateProcessing": false,
                  "properties": {
                    "typeName": "string",
                    "description": "add description here",
                    "effectiveFrom": {{isotime}},
                    "effectiveTo": {{isotime}}
                  }
                }
                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_subcomponent(component_guid, sub_component_guid, body))

    async def _async_detach_sub_component(self, parent_component_guid: str, member_component_guid: str,
                                          body: dict = None) -> None:
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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        validate_guid(parent_component_guid)
        validate_guid(member_component_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{parent_component_guid}/subcomponents/{member_component_guid}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_sub_component(self, parent_component_guid: str, member_component_guid: str, body: dict = None) -> None:
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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_sub_component(parent_component_guid, member_component_guid, body))


    async def _async_link_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution component as a peer in a solution. Async Version.

        Parameters
        ----------
        component1_guid: str
            GUID of the first component to link.
        component2_guid: str
           GUID of the second component to link.
        body: dict
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
          "class": "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "properties" : {
             "class" : "SolutionLinkingWireProperties",
             "label" : "",
             "description" : "",
             "informationSupplyChainSegmentGUIDs" : []
          },
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        validate_guid(component1_guid)
        validate_guid(component2_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component1_guid}/wired-to/{component2_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body_slimmer(body))
        else:
            await self._async_make_request("POST", url)


    def link_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution component as a peer in a solution.

                Parameters
                ----------
                component1_guid: str
                    GUID of the first component to link.
                component2_guid: str
                   GUID of the second component to link.
                body: dict
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
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "properties" : {
                     "class" : "SolutionLinkingWireProperties",
                     "label" : "",
                     "description" : "",
                     "informationSupplyChainSegmentGUIDs" : []
                  },
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "forLineage" : false,
                  "forDuplicateProcessing" : false
                }
                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_solution_linking_wire(component1_guid, component2_guid, body))

    async def _async_detach_solution_linking_wire(self, component1_guid: str, component2_guid: str,
                                          body: dict = None) -> None:
        """ Detach a solution component from a peer solution component.
            Async Version.

        Parameters
        ----------
        component1_guid: str
            GUID of the first component to unlink.
        component2_guid: str
            GUID of the second component to unlink.
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
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        validate_guid(component1_guid)
        validate_guid(component2_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{component1_guid}/wired-to/{component2_guid}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_solution_linking_wire(self, component1_guid: str, component2_guid: str, body: dict = None) -> None:
        """ Detach a solution component from a peer solution component.
                    Async Version.

                Parameters
                ----------
                component1_guid: str
                    GUID of the first component to unlink.
                component2_guid: str
                    GUID of the second component to unlink.
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
                  "class" : "MetadataSourceRequestBody",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "forLineage" : false,
                  "forDuplicateProcessing" : false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_solution_linking_wire(component1_guid, component2_guid, body))



    async def _async_update_solution_component(self, guid: str, body: dict,
                                               replace_all_properties: bool = False) -> None:
        """ Update the properties of a solution component. Async Version.

        Parameters
        ----------
        guid: str
            guid of the solution component to update.
        body: dict
            A dictionary containing the updates to the component.
        replace_all_properties: bool, optional
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
          "class": "UpdateSolutionComponentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "version": "add version identifier here",
            "solutionComponentType": "string",
            "plannedDeployedImplementationType": "string",
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
           }
        }
        """
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{guid}/update?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_solution_component(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
        """ Update the properties of a solution component. Async Version.

        Parameters
        ----------
        guid: str
            guid of the solution component to update.
        body: dict
            A dictionary containing the updates to the component.
        replace_all_properties: bool, optional
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
          "class": "UpdateSolutionComponentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "class": "SolutionComponentProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "version": "add version identifier here",
            "solutionComponentType": "string",
            "plannedDeployedImplementationType": "string",
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
        loop.run_until_complete(self._async_update_solution_component(guid, body, replace_all_properties))

    async def _async_delete_solution_component(self, solution_component_guid: str, cascade_delete: bool = False,
                                               body: dict = None) -> None:
        """Delete a solution component. Async Version.

           Parameters
           ----------
           solution_component_guid: str
               guid of the component to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict, optional
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
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """
        validate_guid(solution_component_guid)


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{solution_component_guid}/delete?cascadeDelete={cascade_delete}")
        if body:
            await self._async_make_request("POST", url, body_slimmer(body))
        else:
            await self._async_make_request("POST", url)

    def delete_solution_component(self, solution_component_guid: str, cascade_delete: bool = False,
                                  body: dict = None) -> None:
        """Delete a solution component.
           Parameters
           ----------
           solution_component_guid: str
               guid of the component to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict, optional
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
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_solution_component(solution_component_guid, cascade_delete, body))

    ##### get solution component implementations

    def get_component_related_elements(self, guid: str) -> dict:
        """ Get related elements about the component"""
        response = self.get_solution_component_by_guid(guid, output_format='JSON')

        if isinstance(response, str):
            return None

        sub_component_guids = []
        actor_guids = []
        blueprint_guids = []

        sub_components = response.get("subComponents",{})
        for sub_component in sub_components:
            sub_component_guids.append(sub_component["elementHeader"]["guid"])

        actors = response.get("actors",{})
        for actor in actors:
            actor_guids.append(actor["elementHeader"]["guid"])

        blueprints = response.get("blueprints",{})
        for blueprint in blueprints:
            blueprint_guids.append(blueprint["relatedElement"]['elementHeader']["guid"])

        return {
            "sub_component_guids": sub_component_guids, "actor_guids": actor_guids, "blueprint_guids": blueprint_guids
            }


    async def _async_get_solution_component_implementations(self, solution_component_guid: str, body: dict = None,
                                                            start_from: int = 0, page_size: int = max_paging_size,
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

    async def _async_get_solution_components_by_name(self, search_filter: str, body: dict = None, start_from: int = 0,
                                                     page_size: int = max_paging_size,
                                                     output_format: str = "JSON") -> dict | str:
        """ Returns the list of solution components with a particular name. Async Version.

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
        else:
            body["filter"] = search_filter

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

    async def _async_find_solution_components(self, search_filter: str = "*", starts_with: bool = True,
                                              ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                              page_size: int = max_paging_size, body: dict = None,
                                              output_format: str = "JSON") -> list[dict] | str:
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
            A list of solution components or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with), ("endsWith", ends_with),
             ("ignoreCase", ignore_case), ])

        if search_filter is None or search_filter == "*":
            search_filter = None

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-components/by-search-string"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_components_output(element, filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_components(self, search_filter: str = "*", starts_with: bool = True, ends_with: bool = False,
                                 ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size,
                                 body: dict = None, output_format: str = "JSON") -> list[dict] | str:
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
            A list of solution components or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_components(search_filter, starts_with, ends_with, ignore_case, start_from,
                                                 page_size, body, output_format))
        return response

    def find_all_solution_components(self, start_from: int = 0, page_size: int = max_paging_size,
                                     output_format: str = "JSON") -> list[dict] | str:
        """Retrieve a list of all solution component elements
        https://egeria-project.org/concepts/solution-components
        """
        return self.find_solution_components("*", start_from=start_from, page_size=page_size,
                                             output_format=output_format)

    #
    #   Roles
    #

    async def _async_create_solution_role(self, body: dict) -> str:
        """ Create a solution role. Async version.

        Parameters
        ----------
        body: dict
            A dictionary containing the definition of the role to create.

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
          "class": "NewActorRoleRequestBody",
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
            "class" : "ActorRoleProperties",
            "qualifiedName": "add unique name here",
            "name": "add short name here",
            "description": "add description here",
           ######## is this right?
            "roleID": "string",
            "scope": "string",
            "title": "string",
            "domainIdentifier": "string",
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
               f"solution-roles")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Solution role not created")

    def create_solution_role(self, body: dict) -> str:
        """Create a solution role. Async version.

        Parameters
        ----------
        body: dict
            A dictionary containing the definition of the role to create.

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
          "class": "NewActorRoleRequestBody",
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "version": "add version here",
            "roleID": "string",
            "scope": "string",
            "title": "string",
            "domainIdentifier": "string",
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
        response = loop.run_until_complete(self._async_create_solution_role(body))
        return response

    async def _async_create_solution_role_from_template(self, body: dict) -> str:
        """ Create a new metadata element to represent a solution role using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async Version.


        Parameters
        ----------
        body: dict
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
               f"solution-roles/from-template")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Role not created")

    def create_solution_role_from_template(self, body: dict) -> str:
        """ Create a new solution component using an existing metadata element
                 as a template.  The template defines additional classifications and relationships that should be
                 added to
                  the new element.


                Parameters
                ----------
                body: dict
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
        response = loop.run_until_complete(self._async_create_solution_role_from_template(body))
        return response

    async def _async_link_component_to_role(self, role_guid: str, component_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution role. Async Version.

        Parameters
        ----------
        role_guid: str
            guid of the role to link.
        component_guid: str
            guid of the component to link.
        body: dict
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
          "class": "SolutionComponentLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "typeName": "string",
            "role": "string",
            "description": "add description here",
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
          }
        }
        """
        validate_guid(component_guid)
        validate_guid(role_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{role_guid}/solution-roles/{component_guid}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_component_to_role(self, role_guid: str, component_guid: str, body: dict) -> None:
        """ Attach a solution component to a solution role.

            Parameters
            ----------
            role_guid: str
                guid of the role to link.
            component_guid: str
                guid of the component to link.
            body: dict
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
              "class": "SolutionComponentLinkRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false,
              "properties": {
                "typeName": "string",
                "role": "string",
                "description": "add description here",
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
              }
            }
                """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_component_to_role(role_guid, component_guid, body))

    async def _async_detach_component_from_role(self, role_guid: str, component_guid: str, body: dict = None) -> None:
        """ Detach a solution role from a solution component.
            Async Version.

        Parameters
        ----------
        role_guid: str
            guid of the role to disconnect from.
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
        validate_guid(role_guid)
        validate_guid(component_guid)
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-components/{role_guid}/solution-component-actors/{component_guid}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_component_from_role(self, role_guid: str, component_guid: str, body: dict = None) -> None:
        """ Detach a solution role from a solution component.

        Parameters
        ----------
        role_guid: str
            guid of the role to disconnect from.
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
        loop.run_until_complete(self._async_detach_component_from_role(role_guid, component_guid, body))

    async def _async_update_solution_role(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
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
          "class": "UpdateSolutionComponentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "qualifiedName": "add unique name here",
            "roleId": "string",
            "title": "string",
            "description": "add description here",
            "domainIdentifier": Int,
            "solutionComponentType": "string",
            "plannedDeployedImplementationType": "string",
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "effectiveFrom": {{isotime}},
            "effectiveTo": {{isotime}}
           }
        }
        """
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{guid}/update?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_solution_role(self, guid: str, body: dict, replace_all_properties: bool = False) -> None:
        """ Update the properties of a solution role.

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
          "class": "UpdateSolutionComponentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": {{isotime}},
          "forLineage": false,
          "forDuplicateProcessing": false,
          "properties": {
            "qualifiedName": "add unique name here",
            "roleId": "string",
            "title": "string",
            "description": "add description here",
            "domainIdentifier": Int,
            "solutionComponentType": "string",
            "plannedDeployedImplementationType": "string",
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
        loop.run_until_complete(self._async_update_solution_role(guid, body, replace_all_properties))

    async def _async_delete_solution_role(self, guid: str, cascade_delete: bool = False, body: dict = None) -> None:
        """Delete a solution role. Async Version.

           Parameters
           ----------
           guid: str
               guid of the role to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict, optional
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
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
           """
        validate_guid(guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/solution-architect/"
               f"solution-roles/{guid}/delete")

        await self._async_make_request("POST", url, body_slimmer(body))

    def delete_solution_role(self, guid: str, cascade_delete: bool = False, body: dict = None) -> None:
        """Delete a solution role. Async Version.

           Parameters
           ----------
           guid: str
               guid of the role to delete.
           cascade_delete: bool, optional, default: False
               Cascade the delete to dependent objects?
           body: dict, optional
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
              "class": "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": {{isotime}},
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_solution_role(guid, cascade_delete, body))

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

    async def _async_find_solution_roles(self, search_filter: str = "*", starts_with: bool = True,
                                         ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                         page_size: int = max_paging_size, body: dict = None,
                                         output_format: str = "JSON", ) -> list[dict] | str:
        """Retrieve the solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor
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
            A list of solution role structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with), ("endsWith", ends_with),
             ("ignoreCase", ignore_case), ])

        if search_filter is None or search_filter == "*":
            search_filter = None

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-roles/by-search-string"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_solution_roles_output(element, filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_roles(self, search_filter: str = "*", starts_with: bool = True, ends_with: bool = False,
                            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size,
                            body: dict = None, output_format: str = "JSON", ) -> list[dict] | str:
        """Retrieve the list of solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor

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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_roles(search_filter, starts_with, ends_with, ignore_case, start_from, page_size,
                                            body, output_format=output_format, ))
        return response

    def find_all_solution_roles(self, start_from: int = 0, page_size: int = max_paging_size,
                                output_format: str = "JSON") -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/actor
        """
        return self.find_solution_roles("*", start_from=start_from, page_size=page_size, output_format=output_format)


if __name__ == "__main__":
    print("Main-Metadata Explorer")

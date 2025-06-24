"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Governance Officer OMVS module.


"""

import asyncio
import os
import sys
from typing import Dict, List, Union

from httpx import Response

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


class GovernanceOfficer(Client):
    """GovernanceOfficer is a class that extends the Client class. The Governance Officer OMVS provides APIs for
      defining and managing governance definitions.

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

        Client.__init__(self, view_server, platform_url, user_id=user_id, user_pwd=user_pwd, token=token, )

    #
    # Extract properties functions
    #

    def _extract_supply_chain_list(self, element: Union[Dict, List[Dict]]) -> List[Dict]:
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
                comp_list.append(self._extract_info_supply_chain_properties(element[i]))
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
                segment_dict["segment_description"] = segment_description
                segment_dict["segment_scope"] = segment_scope
                segment_dict["segment_estimated_volumetrics"] = segment_estimated_volumetrics
                segments_list.append(segment_dict)

        return {
            'guid': guid, 'qualified_name': qualified_name, 'display_name': display_name, 'description': description,
            'scope': scope, 'purposes': purpose_md, 'extended_properties': extended_properties,
            'additional_properties': additional_properties, 'segments': segments_list
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

        return {
            'guid': guid, 'qualified_name': qualified_name, 'display_name': display_name, 'description': description,
            'version': version, 'solution_components': solution_components_md
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
            'guid': guid, 'qualified_name': qualified_name, 'display_name': display_name, 'description': description,
            'role_id': role_id, 'scope': scope, 'domain_identifier': domain_identifier,
            'solution_components': solution_components_md
            }

    def _extract_component_list(self, element: Union[Dict, List[Dict]]) -> List[Dict]:
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
                comp_list.append(self._extract_solution_components_properties(element[i]))
            return comp_list
        else:
            return []

    def _extract_solution_components_properties(self, element: Union[Dict, List[Dict]]) -> dict:
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
                    blueprints_md += f" {bp_q_name}, \n"
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
                sub_comp_md += f" {sub_comp_name}"

        comp_graph = element.get('mermaidGraph', None)

        return {
            'guid': guid, 'qualified_name': qualified_name, 'display_name': display_name, 'description': description,
            'component_type': component_type, 'version': version, 'blueprints': blueprints_md,
            'parent_components': parent_comp_md, 'sub_components': sub_comp_md,
            'additional_properties': additional_props_md, 'extended_properties': extended_props_md,
            'mermaid_graph': comp_graph
            }

    #
    # Markdown output support
    #

    async def _async_create_governance_definition(self, url_marker: str, body: dict) -> str:
        """Create an information supply. Async version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.

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
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-12T21:00:52.332Z",
          "anchorGUID": "string",
          "isOwnAnchor": true,
          "anchorScopeGUID": "string",
          "parentGUID": "string",
          "parentRelationshipTypeName": "string",
          "parentRelationshipProperties": {
            "propertyValueMap": {
              "additionalProp1": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              },
              "additionalProp2": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              },
              "additionalProp3": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              }
            },
            "propertyCount": 0,
            "propertiesAsStrings": {
              "additionalProp1": "string",
              "additionalProp2": "string",
              "additionalProp3": "string"
            },
            "propertyNames": {}
          },
          "parentAtEnd1": true,
          "properties": {
            "effectiveFrom": "2025-06-12T21:00:52.332Z",
            "effectiveTo": "2025-06-12T21:00:52.332Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "documentIdentifier": "string",
            "additionalProperties": {
              "additionalProp1": "string",
              "additionalProp2": "string",
              "additionalProp3": "string"
            },
            "title": "string",
            "summary": "string",
            "description": "string",
            "scope": "string",
            "domainIdentifier": 0,
            "importance": "string",
            "implications": [
              "string"
            ],
            "outcomes": [
              "string"
            ],
            "results": [
              "string"
            ],
            "class": "string"
          },
          "initialStatus": "GovernanceDefinitionStatus : Draft"
        }

       """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance_definitions"

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return response.json().get("guid", "Supply Chain not created")

    def create_governance_definition(self, url_marker: str, body: dict) -> str:
        """Create a governance definition.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.

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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-12T21:00:52.332Z",
          "anchorGUID": "string",
          "isOwnAnchor": true,
          "anchorScopeGUID": "string",
          "parentGUID": "string",
          "parentRelationshipTypeName": "string",
          "parentRelationshipProperties": {
            "propertyValueMap": {
              "additionalProp1": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              },
              "additionalProp2": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              },
              "additionalProp3": {
                "typeName": "string",
                "class": "string",
                "arrayCount": 0,
                "arrayValues": "string"
              }
            },
            "propertyCount": 0,
            "propertiesAsStrings": {
              "additionalProp1": "string",
              "additionalProp2": "string",
              "additionalProp3": "string"
            },
            "propertyNames": {}
          },
          "parentAtEnd1": true,
          "properties": {
            "effectiveFrom": "2025-06-12T21:00:52.332Z",
            "effectiveTo": "2025-06-12T21:00:52.332Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "documentIdentifier": "string",
            "additionalProperties": {
              "additionalProp1": "string",
              "additionalProp2": "string",
              "additionalProp3": "string"
            },
            "title": "string",
            "summary": "string",
            "description": "string",
            "scope": "string",
            "domainIdentifier": 0,
            "importance": "string",
            "implications": [
              "string"
            ],
            "outcomes": [
              "string"
            ],
            "results": [
              "string"
            ],
            "class": "string"
          },
          "initialStatus": "GovernanceDefinitionStatus : Draft"
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_governance_definition(url_marker, body))
        return response

    async def _async_delete_governance_definition(self, guid: str, url_marker: str, body: dict) -> str:
        """ Delete an information supply. Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to delete.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.

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
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "class": "",
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T01:45:46.235Z"
        }
       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"{url_marker}/governance_definitions/delete")

        response = await self._async_make_request("POST", url, body_slimmer(body))

        return

    def create_delete_governance_definition(self, guid: str, url_marker: str, body: dict) -> str:
        """ Delete an information supply. Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to delete.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.

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
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "class": "",
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T01:45:46.235Z"
        }
       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_delete_governance_definition(guid, url_marker, body))
        return

    async def _async_get_gov_def_in_context(self, guid: str, url_marker: str, body: dict, output_format: str,
                                            start_from: int = 0, page_size: int = max_paging_size) -> list[dict] | str:

        """ Get governance definition in context.
            Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.
        output_format: str
            The output format to use.
        start_from: int, default= 0
            Indicates the start of the page range.
        page_size: int, default = max_paging_size
            The page size to use.

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
        ----
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T14:12:44.896Z",
          "limitResultsByStatus": [
            "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}"
          ],
          "asOfTime": "2025-06-13T14:12:44.896Z",
          "sequencingOrder": "SequencingOrder{Any Order}",
          "sequencingProperty": "string"
        }

       """
        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance_definitions/"
               f"in-context{possible_query_params}")

        if body:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response = await self._async_make_request("POST", url)

        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_gov_def_output(element, guid, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_gov_def_in_context(self, guid: str, url_marker: str, body: dict, output_format: str, start_from: int = 0,
                               page_size: int = max_paging_size) -> list[dict] | str:

        """ Get governance definition in context.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.
        output_format: str
            The output format to use.
        start_from: int, default= 0
            Indicates the start of the page range.
        page_size: int, default = max_paging_size
            The page size to use.

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
        ----
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T14:12:44.896Z",
          "limitResultsByStatus": [
            "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}"
          ],
          "asOfTime": "2025-06-13T14:12:44.896Z",
          "sequencingOrder": "SequencingOrder{Any Order}",
          "sequencingProperty": "string"
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_def_in_context(guid, url_marker, body, output_format, start_from, page_size))
        return response

    async def _async_get_gov_def_by_guid(self, guid: str, url_marker: str, body: dict, output_format: str,
                                         start_from: int = 0, page_size: int = max_paging_size) -> dict | str:

        """ Get governance definition by guid.
            Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.
        output_format: str
            The output format to use.

        Returns
        -------

        dict | str
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
        ----
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "effectiveTime": "2025-06-13T14:43:32.194Z",
          "asOfTime": "2025-06-13T14:43:32.194Z",
          "forLineage": true,
          "forDuplicateProcessing": true
        }

       """
        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance_definitions/"
               f"retrieve")

        if body:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response = await self._async_make_request("POST", url)

        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_gov_def_output(element, guid, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_gov_def_by_guid(self, guid: str, url_marker: str, body: dict, output_format: str) -> dict | str:

        """ Get governance definition by guid.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
        url_marker: str
            Indicates which service should be used to create the governance definition.
        body: dict
            A dictionary containing the definition of the supply chain to create.
        output_format: str
            The output format to use.

        Returns
        -------

        dict | str
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
        ----
        https://egeria-project.org/concepts/governance-definition

        Body structure:
        {
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T14:12:44.896Z",
          "limitResultsByStatus": [
            "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}"
          ],
          "asOfTime": "2025-06-13T14:12:44.896Z",
          "sequencingOrder": "SequencingOrder{Any Order}",
          "sequencingProperty": "string"
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_gov_def_by_guid(guid, url_marker, body, output_format))
        return response

    async def _async_update_governance_definition_status(self, guid: str, url_marker: str, body: dict,
                                                         replace_all_properties: bool = False) -> None:
        """ Update the status of a governance definition. Async Version.

        Parameters
        ----------
        guid: str
            guid of the governance definition to update.
        url_marker: str
            Indicates which service should be used to update the governance definition.
        body: dict
            A dictionary containing the updates to the governance definition.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T14:57:32.040Z",
          "status": "GovernanceDefinitionStatus : Draft"
        }
        """
        validate_guid(guid)
        replace_all_properties_s = str(replace_all_properties).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-defnitions/"
               f"{guid}/update-status?replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_governance_definition_status(self, guid: str, url_marker: str, body: dict,
                                            replace_all_properties: bool = False) -> None:
        """ Update the status of a governance definition.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to update.
            url_marker: str
                Indicates which service should be used to update the governance definition.
            body: dict
                A dictionary containing the updates to the supply chain.
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
              "externalSourceGUID": "string",
              "externalSourceName": "string",
              "forLineage": true,
              "forDuplicateProcessing": true,
              "effectiveTime": "2025-06-13T14:57:32.040Z",
              "status": "GovernanceDefinitionStatus : Draft"
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_governance_definition_status(guid, url_marker, body, replace_all_properties))

    async def _async_link_peer_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                           definition_guid2: str, body: dict) -> None:
        """ Attach two peer governance definitions. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:03:28.505Z",
          "properties": {
            "effectiveFrom": "2025-06-13T15:03:28.505Z",
            "effectiveTo": "2025-06-13T15:03:28.505Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "description": "string"
          }
        }
        """
        validate_guid(definition_guid1)
        validate_guid(definition_guid2)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{definition_guid1}/peer-definitions/{relationship_type}/{definition_guid2}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_peer_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                              definition_guid2: str, body: dict) -> None:
        """ Attach two peer governance definitions. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:03:28.505Z",
          "properties": {
            "effectiveFrom": "2025-06-13T15:03:28.505Z",
            "effectiveTo": "2025-06-13T15:03:28.505Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "description": "string"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_peer_definitions(url_marker, definition_guid1, relationship_type, definition_guid2, body))

    async def _async_detach_peer_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                             definition_guid2: str, body: dict) -> None:
        """ Detach two peer governance definitions. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        validate_guid(definition_guid1)
        validate_guid(definition_guid2)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{definition_guid1}/peer-definitions/{relationship_type}/{definition_guid2}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_peer_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                definition_guid2: str, body: dict) -> None:
        """ Detach two peer governance definitions.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_peer_definitions(url_marker, definition_guid1, relationship_type, definition_guid2,
                                                body))

    async def _async_link_supporting_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                                 definition_guid2: str, body: dict) -> None:
        """ Attach a supporting governance definition. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T18:04:45.117Z",
          "properties": {
            "effectiveFrom": "2025-06-13T18:04:45.117Z",
            "effectiveTo": "2025-06-13T18:04:45.117Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "rationale": "string"
          }
        }
        """
        validate_guid(definition_guid1)
        validate_guid(definition_guid2)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{definition_guid1}/supporting-definitions/{relationship_type}/{definition_guid2}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_supporting_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                    definition_guid2: str, body: dict) -> None:
        """ Attach a supporting governance definition.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T18:04:45.117Z",
          "properties": {
            "effectiveFrom": "2025-06-13T18:04:45.117Z",
            "effectiveTo": "2025-06-13T18:04:45.117Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "rationale": "string"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_supporting_definitions(url_marker, definition_guid1, relationship_type, definition_guid2,
                                                    body))

    async def _async_detach_supporting_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                                   definition_guid2: str, body: dict) -> None:
        """ Detach a governance definition from a supporting governance definition. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to unlink.
        definition_guid2: str
            guid of the second governance definition to unlink.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        validate_guid(definition_guid1)
        validate_guid(definition_guid2)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{definition_guid1}/supporting-definitions/{relationship_type}/{definition_guid2}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_supporting_definitions(self, url_marker: str, definition_guid1: str, relationship_type: str,
                                      definition_guid2: str, body: dict) -> None:
        """ Detach a governance definition from a supporting governance definition.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        definition_guid1: str
            guid of the first governance definition to unlink.
        definition_guid2: str
            guid of the second governance definition to unlink.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_supporting_definitions(url_marker, definition_guid1, relationship_type, definition_guid2,
                                                      body))

    async def _async_link_definition_implementation(self, url_marker: str, technical_control_guid: str,
                                                    relationship_type: str, implementation_guid: str,
                                                    body: dict) -> None:
        """ Attach a governance definition to its implementation. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        technical_control_guid: str
            guid of the technical control to link.
        relationship_type: str
            Relationship type name linking the governance definitions.
        implementation_guid: str
            guid of the implementation definition to link.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T18:04:45.117Z",
          "properties": {
            "effectiveFrom": "2025-06-13T18:04:45.117Z",
            "effectiveTo": "2025-06-13T18:04:45.117Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "notes": "string"
          }
        }
        """
        validate_guid(technical_control_guid)
        validate_guid(implementation_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{technical_control_guid}/governance-implementation/{relationship_type}/{implementation_guid}/attach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def link_definition_implementation(self, url_marker: str, technical_control_guid: str, relationship_type: str,
                                       implementation_guid: str, body: dict) -> None:
        """ Attach a governance definition to its implementation.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        technical_control_guid: str
            guid of the technical control to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
        implementation_guid: str
            guid of the implementation definition to link.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T18:04:45.117Z",
          "properties": {
            "effectiveFrom": "2025-06-13T18:04:45.117Z",
            "effectiveTo": "2025-06-13T18:04:45.117Z",
            "typeName": "string",
            "extendedProperties": {
              "additionalProp1": {},
              "additionalProp2": {},
              "additionalProp3": {}
            },
            "class": "string",
            "notes": "string"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_definition_implementation(url_marker, technical_control_guid, relationship_type,
                                                       implementation_guid, body))

    async def _async_detach_definition_implementation(self, url_marker: str, technical_control_guid: str,
                                                      relationship_type: str, implementation_guid: str,
                                                      body: dict) -> None:
        """ Detach a governance definition from its implementation. Async Version.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to unlink the governance definition.
        technical_control_guid: str
            guid of the technical control to link.
        relationship_type: str
            Relationship type name linking the governance definitions.
        implementation_guid: str
            guid of the implementation definition to unlink.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        validate_guid(technical_control_guid)
        validate_guid(implementation_guid)

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"{technical_control_guid}/governance-implementation/{relationship_type}/{implementation_guid}/detach")

        await self._async_make_request("POST", url, body_slimmer(body))

    def detach_definition_implementation(self, url_marker: str, technical_control_guid: str, relationship_type: str,
                                         implementation_guid: str, body: dict) -> None:
        """ Detach a governance definition from its implementation.

        Parameters
        ----------
        url_marker: str
            Indicates which service should be used to link the governance definition.
        technical_control_guid: str
            guid of the technical control to unlink.
        relationship_type: str
            Relationship type name linking the governance definitions..
        implementation_guid: str
            guid of the implementation definition to unlink.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_definition_implementation(url_marker, technical_control_guid, relationship_type,
                                                         implementation_guid, body))

    async def _async_get_governance_definitions_by_name(self, url_marker: str, search_filter: str, body: dict = None,
                                                        start_from: int = 0, page_size: int = max_paging_size,
                                                        output_format: str = "JSON") -> dict | str:
        """ Returns the list of governance definitions with a particular name. Async Version.

            Parameters
            ----------
            url_marker: str
                Indicates which service should be used.
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
              "filter": "Add name here",
              "templateFilter": "NO_TEMPLATES"
            }

        """
        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"by-name{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_governance_definition_output(element, None, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_governance_definitions_by_name(self, url_marker: str, search_filter: str, body: dict = None,
                                           start_from: int = 0, page_size: int = max_paging_size,
                                           output_format: str = "JSON") -> dict | str:
        """ Returns the list of information supply chains with a particular name. Async Version.

            Parameters
            ----------
            url_marker: str
                Indicates which service should be used.
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
              "filter": "Add name here",
              "templateFilter": "NO_TEMPLATES"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_governance_definitions_by_name(url_marker, search_filter, body, start_from, page_size,
                                                           output_format))
        return response

    async def _async_find_governance_definitions(self, url_marker: str, search_filter: str = "*",
                                                 starts_with: bool = True, ends_with: bool = False,
                                                 ignore_case: bool = False, start_from: int = 0,
                                                 page_size: int = max_paging_size, body: dict = None,
                                                 output_format: str = 'JSON') -> list[dict] | str:
        """ Retrieve the list of governance definition metadata elements that contain the search string.
            Async version.

            Parameters
            ----------
            url_marker: str
                Indicates which service should be used.
            search_filter : str
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
              "filter": "Add name here",
              "templateFilter": "NO_TEMPLATES"
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

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{url_marker}/governance-definitions/"
               f"by-search-string{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_info_supply_chain_output(element, search_filter, output_format)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_information_supply_chains(self, url_marker: str, search_filter: str = "*", starts_with: bool = True,
                                       ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                       page_size: int = max_paging_size, body: dict = None,
                                       output_format: str = 'JSON', ) -> list[dict] | str:
        """ Retrieve the list of governance definition metadata elements that contain the search string.

            Parameters
            ----------
            url_marker: str
                Indicates which service should be used.
            search_filter : str
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
              "filter": "Add name here",
              "templateFilter": "NO_TEMPLATES"
            }
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_governance_definitions(url_marker, filter, starts_with, ends_with, ignore_case, start_from,
                                                    page_size, body, output_format))
        return response


async def _async_create_governance_definition_from_template(self, url_marker: str, body: dict) -> str:
    """ Create a new metadata element to represent a governance definition using an existing metadata element
        as a template. The template defines additional classifications and relationships that should be added to
        the new element. Async version.

    Parameters
    ----------
    url_marker: str
        Indicates which service should be used to create the governance definition.
    body: dict
        A dictionary containing the definition of the supply chain to create.

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
    https://egeria-project.org/concepts/governance-definition

    Body structure:
     {
      "externalSourceGUID": "string",
      "externalSourceName": "string",
      "forLineage": true,
      "forDuplicateProcessing": true,
      "effectiveTime": "2025-06-13T19:06:56.874Z",
      "typeName": "string",
      "initialStatus": "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}",
      "initialClassifications": {
        "additionalProp1": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        },
        "additionalProp2": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        },
        "additionalProp3": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        }
      },
      "anchorGUID": "string",
      "isOwnAnchor": true,
      "anchorScopeGUID": "string",
      "allowRetrieve": true,
      "effectiveFrom": "2025-06-13T19:06:56.874Z",
      "effectiveTo": "2025-06-13T19:06:56.874Z",
      "templateGUID": "string",
      "replacementProperties": {
        "propertyValueMap": {
          "additionalProp1": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp2": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp3": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          }
        },
        "propertyCount": 0,
        "propertiesAsStrings": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "propertyNames": {}
      },
      "placeholderPropertyValues": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      },
      "parentGUID": "string",
      "parentRelationshipTypeName": "string",
      "parentRelationshipProperties": {
        "propertyValueMap": {
          "additionalProp1": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp2": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp3": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          }
        },
        "propertyCount": 0,
        "propertiesAsStrings": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "propertyNames": {}
      },
      "parentAtEnd1": true
    }

   """
    url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
           f"{url_marker}/governance_definitions/from-template")

    response = await self._async_make_request("POST", url, body_slimmer(body))

    return response.json().get("guid", "Governance definition not created")


def create_governance_definition_from_template(self, url_marker: str, body: dict) -> str:
    """ Create a new metadata element to represent a governance definition using an existing metadata element
        as a template. The template defines additional classifications and relationships that should be added to
        the new element.

    Parameters
    ----------
    url_marker: str
        Indicates which service should be used to create the governance definition.
    body: dict
        A dictionary containing the definition of the supply chain to create.

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
    https://egeria-project.org/concepts/governance-definition

    Body structure:
     {
      "externalSourceGUID": "string",
      "externalSourceName": "string",
      "forLineage": true,
      "forDuplicateProcessing": true,
      "effectiveTime": "2025-06-13T19:06:56.874Z",
      "typeName": "string",
      "initialStatus": "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}",
      "initialClassifications": {
        "additionalProp1": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        },
        "additionalProp2": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        },
        "additionalProp3": {
          "propertyValueMap": {
            "additionalProp1": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp2": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            },
            "additionalProp3": {
              "typeName": "string",
              "class": "string",
              "arrayCount": 0,
              "arrayValues": "string"
            }
          },
          "propertyCount": 0,
          "propertiesAsStrings": {
            "additionalProp1": "string",
            "additionalProp2": "string",
            "additionalProp3": "string"
          },
          "propertyNames": {}
        }
      },
      "anchorGUID": "string",
      "isOwnAnchor": true,
      "anchorScopeGUID": "string",
      "allowRetrieve": true,
      "effectiveFrom": "2025-06-13T19:06:56.874Z",
      "effectiveTo": "2025-06-13T19:06:56.874Z",
      "templateGUID": "string",
      "replacementProperties": {
        "propertyValueMap": {
          "additionalProp1": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp2": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp3": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          }
        },
        "propertyCount": 0,
        "propertiesAsStrings": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "propertyNames": {}
      },
      "placeholderPropertyValues": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
      },
      "parentGUID": "string",
      "parentRelationshipTypeName": "string",
      "parentRelationshipProperties": {
        "propertyValueMap": {
          "additionalProp1": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp2": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          },
          "additionalProp3": {
            "typeName": "string",
            "class": "string",
            "arrayCount": 0,
            "arrayValues": "string"
          }
        },
        "propertyCount": 0,
        "propertiesAsStrings": {
          "additionalProp1": "string",
          "additionalProp2": "string",
          "additionalProp3": "string"
        },
        "propertyNames": {}
      },
      "parentAtEnd1": true
    }

   """

    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(self._async_create_governance_definition_from_template(url_marker, body))
    return response


if __name__ == "__main__":
    print("Main-Metadata Explorer")

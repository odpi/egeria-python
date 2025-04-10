"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the metadata-explorer OMVS module.

https://egeria-project.org/concepts/information-supply-chain

"""

import asyncio
import os
import sys
from datetime import datetime

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

MD_SEPERATOR = "\n---\n\n"

def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


#("params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to "
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
    # Markdown output support
    #
    def generate_info_supply_chain_md(self, elements: list | dict, search_string: str,
                                      output_format: str = 'MD', include_mermaid: bool = True
                                      ) -> str:
        """Generate markdown for information supply chains."""
        elements_md, elements_action = self.make_preamble(obj_type="Information Supply Chain",
                                                          search_string=search_string,
                                                          output_format=output_format)
        if isinstance(elements, dict):
            elements = [elements]

        for element in elements:
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
                    purpose_md += f"* {purpose}\n"
            mermaid = element.get('mermaidGraph', None)

            if output_format in ['FORM', 'MD']:
                elements_md += f"# {elements_action}\n\n"
                elements_md += f"## Information Supply Chain Name \n\n{display_name}\n\n"

            elif output_format == 'REPORT':
                elements_md += f"# Information Supply Chain Name: {display_name}\n\n"
            else:
                elements_md += f"## Information Supply Chain Name \n\n{display_name}\n\n"

            elements_md += self.make_md_attribute("description", description, output_format)
            elements_md += self.make_md_attribute("scope", scope, output_format)
            elements_md += self.make_md_attribute("purposes", purpose_md, output_format)

            elements_md += self.make_md_attribute("qualified name", qualified_name, output_format)
            elements_md += self.make_md_attribute("GUID", guid, output_format)
            if include_mermaid and output_format == 'REPORT':
                elements_md += f"\n```mermaid\n{mermaid}\n```\n"
            elements_md += MD_SEPERATOR
        return elements_md

    def generate_solution_blueprint_md(self, elements: list | dict, search_string: str,
                                       output_format: str = 'MD', include_mermaid: bool = True) -> str:
        elements_md, elements_action = self.make_preamble(obj_type="Solution Blueprint", search_string=search_string,
                                                          output_format=output_format)
        if isinstance(elements, dict):
            elements = [elements]

        for element in elements:
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
                    solution_components_md += f"* {sol_comp_name}:\t {sol_comp_desc}\n"
            bp_graph = element.get('mermaidGraph', None)

            if output_format in ['FORM', 'MD']:
                elements_md += f"# {elements_action}\n\n"
                elements_md += f"## Blueprint Name \n\n{display_name}\n\n"
            elif output_format == 'REPORT':
                elements_md += f"# Blueprint Name: {display_name}\n\n"
            else:
                elements_md += f"## Blueprint Name \n\n{display_name}\n\n"

            elements_md += self.make_md_attribute("description", description, output_format)
            elements_md += self.make_md_attribute("version", version, output_format)
            if output_format == 'REPORT':
                elements_md += self.make_md_attribute("solution components", solution_components_md, output_format)
            elements_md += self.make_md_attribute("qualified name", qualified_name, output_format)
            elements_md += self.make_md_attribute("GUID", guid, output_format)
            if include_mermaid and output_format == 'REPORT':
                elements_md += f"\n```mermaid\n{bp_graph}\n```\n"
            elements_md += MD_SEPERATOR

        return elements_md

    def generate_solution_roles_md(self, elements: list | dict, search_string: str,
                                   output_format: str = 'MD', include_mermaid: bool = True) -> str:
        elements_md, elements_action = self.make_preamble(obj_type="Categories", search_string=search_string,
                                                          output_format=output_format)
        if isinstance(elements, dict):
            elements = [elements]

        for element in elements:
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
                    sol_comp_prop = solution_component.get('relationshipProperties',None)
                    if sol_comp_prop:
                        sol_comp_name = sol_comp_prop.get("role", None)
                        sol_comp_desc = sol_comp_prop.get("description", None)
                        solution_components_md += f"* {sol_comp_name}:\t {sol_comp_desc}\n"
            solution_roles_graph = element.get('mermaidGraph', None)

            if output_format in ['FORM', 'MD']:
                elements_md += f"# {elements_action}\n\n"
                elements_md += f"## Blueprint Name \n\n{display_name}\n\n"
            elif output_format == 'REPORT':
                elements_md += f"# Blueprint Name: {display_name}\n\n"
            else:
                elements_md += f"## Blueprint Name \n\n{display_name}\n\n"
            elements_md += self.make_md_attribute("role id", role_id, output_format)
            elements_md += self.make_md_attribute("scope", scope, output_format)
            elements_md += self.make_md_attribute("description", description, output_format)
            elements_md += self.make_md_attribute("domain identifier", domain_identifier, output_format)
            if output_format == 'REPORT':
                elements_md += self.make_md_attribute("solution components", solution_components_md, output_format)
            elements_md += self.make_md_attribute("qualified name", qualified_name, output_format)
            elements_md += self.make_md_attribute("GUID", guid, output_format)
            if include_mermaid and output_format == 'REPORT':
                elements_md += f"\n```mermaid\n{solution_roles_graph}\n```\n"
            elements_md += MD_SEPERATOR

        return elements_md

    def generate_solution_components_md(self, elements: list | dict, search_string: str,
                                        output_format: str = 'MD', include_mermaid: bool = True) -> str:
        """
        Generates a Markdown (MD) or formatted document representation for solution components.

        Given a set of elements representing solution components (either as a list or a dictionary),
        this function generates a detailed output string compliant with a specified format. The
        resulting output includes various attributes of the solution components, such as their
        names, descriptions, types, and related information like blueprints, parents, and extended
        properties. Optionally, it can include Mermaid graphs for further visualization when needed.

        Args:
            elements (list | dict): A collection of elements, each representing a solution component.
                Elements can be provided as a list of dictionaries or a single dictionary. Each
                dictionary should contain the required keys, including "elementHeader" and "glossaryCategoryProperties".
            search_string (str): A string to be used for preamble generation or context identification.
            output_format (str, optional): The format of the resulting output string. Defaults to 'MD'.
                Valid values include 'MD', 'FORM', and 'REPORT'.
            include_mermaid (bool, optional): Determines whether Mermaid graphs should be included
                in the output. Defaults to True.

        Returns:
            str: A string containing the formatted details of solution components in the specified format.
        """
        elements_md, elements_action = self.make_preamble(obj_type="Categories", search_string=search_string,
                                                          output_format=output_format)

        if isinstance(elements, dict):
            elements = [elements]

        for element in elements:
            guid = element['elementHeader'].get("guid", None)
            properties = element['glossaryCategoryProperties']
            display_name = properties.get("displayName", None)
            description = properties.get("description", None)
            version = properties.get("version", None)
            component_type = properties.get("solutionComponentType", None)
            qualified_name = properties.get("qualifiedName", None)

            extended_props = properties.get("extendedProperties", None)
            extended_props_md = ""
            if extended_props:
                for key in extended_props.keys():
                    extended_props_md += f"* {key}:\t {extended_props[key]}\n"

            blueprints_md = ""
            blueprints = element.get('blueprints', None)
            if blueprints:
                for blueprint in blueprints:
                    bp_q_name = blueprint["relatedElement"]['properties']['qualifiedName']
                    blueprints_md += f"* {bp_q_name}\n"

            parent_comp_md = ""
            context = element["context"]
            if context:
                for parent in context:
                    parent_comp_md += f"* {parent['name']}\n"
                    # Todo - This is incomplete - discuss with Mandy
            comp_graph = element.get('mermaidGraph', None)

            if output_format in ['FORM', 'MD']:
                elements_md += f"# {elements_action}\n\n"
                elements_md += f"## Solution Component Name \n\n{display_name}\n\n"

            elif output_format == 'REPORT':
                elements_md += f"# Solution Component Name: {display_name}\n\n"
            else:
                elements_md += f"## Solution Component Name \n\n{display_name}\n\n"

            elements_md += self.make_md_attribute("description", description, output_format)
            elements_md += self.make_md_attribute("component type", component_type, output_format)
            elements_md += self.make_md_attribute("version", version, output_format)
            elements_md += self.make_md_attribute("qualified name/GUID", f"{qualified_name}\n---\n{guid}", output_format)
            elements_md += self.make_md_attribute("blueprints", blueprints_md, output_format)
            elements_md += self.make_md_attribute("parent components", parent_comp_md, output_format)
            elements_md += self.make_md_attribute("extended properties", extended_props_md, output_format)
            if include_mermaid and output_format == 'REPORT':
                elements_md += f"\n```mermaid\n{comp_graph}\n```\n"
            elements_md += MD_SEPERATOR

        return elements_md

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
          "class" : "NewInformationSupplyChainRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
          "class" : "NewInformationSupplyChainRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
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
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
          "class" : "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
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
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
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
          "class" : "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
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
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
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
          "class" : "UpdateInformationSupplyChainRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "purposes": ["purpose1", "purpose2"],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
              "class" : "UpdateInformationSupplyChainRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "properties": {
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "scope": "add scope of this information supply chain's applicability.",
                "purposes": ["purpose1", "purpose2"],
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
               }
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_info_supply_chain(guid, body, replace_all_properties))

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
              "class" : "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
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
              "class" : "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_info_supply_chain(guid, body))

    async def _async_get_info_supply_chain_by_guid(self, guid: str, body: dict = None,
                                                   add_implementation: bool = True) -> dict | str:
        """Return the properties of a specific information supply chain. Async Version.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.

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
              "class" : "AnyTimeRequestBody",
              "asOfTime" : {{isotime}},
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
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
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_info_supply_chain_by_guid(self, guid: str, body: dict = None,
                                      add_implementation: bool = True) -> dict | str:
        """ Return the properties of a specific information supply chain.

            Parameters
            ----------
            guid: str
                guid of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.

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
              "class" : "AnyTimeRequestBody",
              "asOfTime" : {{isotime}},
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_info_supply_chain_by_guid(guid, body, add_implementation))
        return response

    async def _async_get_info_supply_chain_by_name(self, search_filter: str, body: dict = None,
                                                   add_implementation: bool = True, start_from: int = 0,
                                                   page_size: int = max_paging_size) -> dict | str:
        """ Returns the list of information supply chains with a particular name. Async Version.

            Parameters
            ----------
            search_filter: str
                name of the information supply chain to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.

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
              "class" : "FilterRequestBody",
              "asOfTime" : {{isotime}},
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName",
              "filter" : "Add name here"
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
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_info_supply_chain_by_name(self, search_filter: str, body: dict = None, add_implementation: bool = True,
                                      start_from: int = 0, page_size: int = max_paging_size) -> dict | str:
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
              "class" : "FilterRequestBody",
              "asOfTime" : {{isotime}},
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName",
              "filter" : "Add name here"
            }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_info_supply_chain_by_name(search_filter, body, add_implementation, start_from, page_size))
        return response

    async def _async_find_information_supply_chains(self, filter: str = "*", add_implementation: bool = True,
            starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
            page_size: int = max_paging_size, body: dict = None,
            output_format: str = 'JSON', include_mermaid: bool = False ) -> list[dict] | str:
        """Retrieve the list of information supply chain metadata elements that contain the search string.
               https://egeria-project.org/concepts/information-supply-chain
               Async version.

            Parameters
            ----------
            filter : str
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
            include_mermaid: bool, default = False
                Include mermaid diagrams?

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

        possible_query_params = query_string(
            [("addImplementation", add_implementation), ("startFrom", start_from), ("pageSize", page_size),
                ("startsWith", starts_with), ("endsWith", ends_with), ("ignoreCase", ignore_case), ])

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

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
            return self.generate_info_supply_chain_md(element, filter, output_format, include_mermaid)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_information_supply_chains(self, filter: str = "*", add_implementation: bool = True, starts_with: bool = True,
            ends_with: bool = False, ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size,
            body: dict = None, output_format: str = 'JSON', include_mermaid: bool = False ) -> list[dict] | str:
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
            self._async_find_information_supply_chains(filter, add_implementation, starts_with, ends_with, ignore_case,
                start_from, page_size, body, output_format, include_mermaid ))
        return response


    def find_all_information_supply_chains(self, start_from: int = 0, page_size: int = max_paging_size) -> list[dict] | str:
        """Retrieve a list of all information supply chains
        https://egeria-project.org/concepts/information-supply-chain
        """

        return self.find_information_supply_chains("*", start_from=start_from, page_size=page_size)


    #
    # Segments
    #
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
          "class" : "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
          "class" : "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
          "class" : "InformationSupplyChainSegmentRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope": "add scope of this information supply chain's applicability.",
            "integrationStyle": "style",
            "estimatedVolumetrics": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
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
              "class" : "InformationSupplyChainSegmentRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "properties": {
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "scope": "add scope of this information supply chain's applicability.",
                "integrationStyle": "style",
                "estimatedVolumetrics": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": {{isotime}},
                "effectiveTo": {{isotime}}
              }
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_info_supply_chain_segment(guid, body, replace_all_properties))


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
              "class" : "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
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
              "class" : "MetadataSourceRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : {{isotime}},
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_info_supply_chain_segment(guid, body))


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
          "class" : "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
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
               f"information-supply-chains/segments/{segment_guid1}/link-to{segment_guid2}/attach")

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
          "class" : "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
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
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false
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
          "class" : "InformationSupplyChainLinkRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : {{isotime}},
          "forLineage" : false,
          "forDuplicateProcessing" : false,
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


    #
    #  Blueprints
    #


    async def _async_find_solution_blueprints(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None,
                                              output_format: str = "JSON", include_mermaid: bool = False) -> list[
                                                                                                                          dict] | str:
        """Retrieve the solution blueprint elements that contain the search string.
           https://egeria-project.org/concepts/solution-blueprint
           Async version.

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
        body: dict, optional, default = None
            - additional optional specifications for the search.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        include_mermaid: bool, default = False
            Include mermaid diagrams?

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
        """

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with), ("endsWith", ends_with),
                ("ignoreCase", ignore_case), ])

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

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
            return self.generate_solution_blueprint_md(element, filter, output_format, include_mermaid)
        return response.json().get("elements", NO_ELEMENTS_FOUND)


    def find_solution_blueprints(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None,
                                 output_format: str = 'JSON', include_mermaid: bool= False) -> list[dict] | str:
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
        include_mermaid: bool, default = False
            Include mermaid diagrams?

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
            self._async_find_solution_blueprints(filter, starts_with, ends_with, ignore_case,
                                                 start_from, page_size, body,
                                                 output_format, include_mermaid)
           )
        return response


    def find_all_solution_blueprints(self, start_from: int = 0, page_size: int = max_paging_size) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/solution-blueprint
        """
        return self.find_solution_blueprints("*", start_from=start_from, page_size=page_size)


    #
    #   Roles
    #

    async def _async_find_solution_roles(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None,
                                         output_format: str = "JSON", include_mermaid: bool = False) -> list[
                                                                                                                          dict] | str:
        """Retrieve the solutio nrole elements that contain the search string.
           https://egeria-project.org/concepts/actor
           Async version.

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
        body: dict, optional, default = None
            - additional optional specifications for the search.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        include_mermaid: bool, default = False
            Include mermaid diagrams?

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

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

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
            return self.generate_solution_roles_md(element, filter, output_format, include_mermaid)
        return response.json().get("elements", NO_ELEMENTS_FOUND)


    def find_solution_roles(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
                        ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None,
                        output_format: str = "JSON", include_mermaid: bool = False) -> list[dict] | str:
        """Retrieve the list of solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor

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
        include_mermaid: bool, default = False
            Include mermaid diagrams?

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
            self._async_find_solution_roles(filter, starts_with, ends_with, ignore_case,
                                            start_from, page_size, body,
                                            output_format=output_format, include_mermaid=include_mermaid )
            )
        return response


    def find_all_solution_roles(self, start_from: int = 0, page_size: int = max_paging_size) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/actor
        """
        return self.find_solution_roles("*", start_from=start_from, page_size=page_size)


    #
    #   Components
    #
    async def _async_find_solution_components(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None, ) -> list[
                                                                                                                          dict] | str:
        """Retrieve the solution component elements that contain the search string.
           https://egeria-project.org/concepts/solution-components
           Async version.

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
        body: dict, optional, default = None
            - additional optional specifications for the search.

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
        """

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with), ("endsWith", ends_with),
                ("ignoreCase", ignore_case), ])

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

        if body is None:
            body = {
                "filter": search_filter,
                }
        else:
            body["filter"] = search_filter

        url = (f"{self.solution_architect_command_root}/solution-components/by-search-string"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("elements", NO_ELEMENTS_FOUND)


    def find_solution_components(self, filter: str = "*", starts_with: bool = True, ends_with: bool = False,
            ignore_case: bool = False, start_from: int = 0, page_size: int = max_paging_size, body: dict = None, ) -> list[
                                                                                                                          dict] | str:
        """Retrieve the list of solution component elements that contain the search string.
           https://egeria-project.org/concepts/solution-components

        Parameters
        ----------
        filter : str
            - filter string to search for.
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
            self._async_find_solution_components(filter, starts_with, ends_with, ignore_case, start_from, page_size,
                body, ))
        return response


    def find_all_solution_components(self, start_from: int = 0, page_size: int = max_paging_size) -> list[dict] | str:
        """Retrieve a list of all solution component elements
        https://egeria-project.org/concepts/solution-components
        """
        return self.find_solution_components("*", start_from=start_from, page_size=page_size)


    async def _async_get_solution_component_implementations(self, guid: str, body: dict = None, start_from: int = 0,
            page_size: int = max_paging_size, ) -> list[dict] | str:
        """ Retrieve the list of metadata elements that are associated with the solution component via
            the ImplementedBy relationship.
            Async version.

            Parameters
            ----------
            guid: str
                - identifier of the solution component to retrieve the implementations for.
            body: dict, optional, default = None
                - additional optional specifications for the search.
            start_from : int, default = 0
            page_size : int, default = max_paging_size

            Returns
            -------
            list[dict] | str
                A list of implementation elements or a string if there are no elements found.

            Raises
            ------
            InvalidParameterException
                one of the parameters is null or invalid or
            PropertyServerException
                There is a problem adding the element properties to the metadata repository or
            UserNotAuthorizedException
                the requesting user is not authorized to issue this request.
            """

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])

        validate_guid(guid)

        url = (f"{self.solution_architect_command_root}/solution-components/{guid}/implementations"
               f"{possible_query_params}")
        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("elementList", NO_ELEMENTS_FOUND)


    def get_solution_component_implementations(self, guid: str, body: dict = None, start_from: int = 0,
            page_size: int = max_paging_size, ) -> list[dict] | str:
        """Retrieve the list of metadata elements that are associated with the solution component via
            the ImplementedBy relationship.
            Async version.

            Parameters
            ----------
            guid: str
                - identifier of the solution component to retrieve the implementations for.
            body: dict, optional, default = None
                - additional optional specifications for the search.
            start_from : int, default = 0
            page_size : int, default = max_paging_size

            Returns
            -------
            list[dict] | str
                A list of implementation elements or a string if there are no elements found.

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
            self._async_get_solution_component_implementations(guid, body, start_from, page_size))
        return response


if __name__ == "__main__":
    print("Main-Metadata Explorer")

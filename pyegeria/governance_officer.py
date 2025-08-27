"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Governance Officer OMVS module.


"""

import asyncio
import os
import sys
from typing import Annotated, Literal, Union
from typing import Dict, List

from loguru import logger
from pydantic import Field

from pyegeria._client_new import Client2
from pyegeria.output_formatter import (
    extract_mermaid_only,
    generate_output,
    _extract_referenceable_properties,
    populate_columns_from_properties,
    get_required_relationships,
)
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from pyegeria._exceptions_new import PyegeriaInvalidParameterException
from pyegeria._globals import NO_GUID_RETURNED
from pyegeria.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, NewElementRequestBody,
                             ReferenceableProperties, TemplateRequestBody,
                             UpdateElementRequestBody, UpdateStatusRequestBody, NewRelationshipRequestBody,
                             DeleteRequestBody)
from pyegeria.utils import dynamic_catch

GOV_DEF_PROPERTIES_LIST = ["GovernanceDefinitionProperties", "GovernanceStrategyProperties", "RegulationProperties",
                           "GovernanceControlProperties", "SecurityGroupProperties", "NamingStandardRuleProperties",
                           "CertificationTypeProperties", "LicenseTypeProperties", "GovernanceApproachProperties",
                           "GovernanceStrategyProperties", "GovernanceProcessingPurposeProperties",
                           "BusinessImperativeProperties", "RegulationArticleProperties", "ThreatProperties",]

GOV_BASIC_TYPES = ["BusinessImperative", "RegulationArticle", "Threat", "GovernancePrinciple", "GovernanceObligation",
                   "GovernanceApproach", "GovernanceProcessingPurpose"]



EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
DEFAULT_BODY_SKELETON = {
    "effective_time": None, "limitResultsByStatus": ["ACTIVE"], "asOfTime": None, "sequencingOrder": None,
    "sequencingProperty": None, "filter": None,
    }


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/governance-officer/api/open-metadata/metadata-explorer"


class GovernanceDefinitionProperties(ReferenceableProperties):
    class_: Annotated[Literal["GovernanceDefinitionProperties"], Field(alias="class")]
    identifier: str | None = None
    domainIdentifier: int | None = None
    summary: str | None = None
    scope: str | None = None
    usage: str | None = None
    importance: str | None = None
    implications: list[str] | None = None
    outcomes: list[str] | None = None
    results: list[str] | None = None
    userDefinedStatus: str | None = None


class GovernanceOfficer(Client2):
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

        Client2.__init__(self, view_server, platform_url, user_id=user_id, user_pwd=user_pwd, token=token)
        self.url_marker = "governance-officer"

    #
    # Extract properties functions
    #
    def _generate_governance_definition_output(self, elements: list | dict, search_string: str, element_type_name: str = None,
                                               output_format: str = 'DICT', output_format_set: dict | str = None
                                               ) -> str | list:
        """
        Generate output for governance definitions in the specified format, using output format sets.

        Args:
            elements: Dictionary or list of dictionaries containing governance definition elements
            search_string: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
            output_format_set: Optional format set name or structure to control columns

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Ensure elements handled consistently for MERMAID
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)

        entity_type = element_type_name if element_type_name else "Governance Definition"
        # Resolve columns_struct via output format sets
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            # Default to the Governance Definitions format set
            output_formats = select_output_format_set("Governance Definitions", output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        logger.trace(f"Executing generate_governance_definition_output: {output_formats}")
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_gov_def_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    #
    #
    #

    def _extract_gov_def_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract and populate governance definition properties into columns_struct.

        This follows the columns_struct pattern: fill from element.properties (camelCase), overlay header
        attributes, and derive any relationship-based columns that are explicitly requested.

        Args:
            element: The governance definition element
            columns_struct: The columns structure to populate

        Returns:
            dict: columns_struct with populated 'value' fields
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])

        # Header-derived values (GUID, type_name, etc.)
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')

        # Populate requested relationship-based columns generically
        col_data = get_required_relationships(element, col_data)

        # Mermaid graph if requested
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = element.get('mermaidGraph', '') or ''
                break

        return col_data

    def _extract_gov_def_list(self, element: Union[Dict, List[Dict]]) -> List[Dict]:
        """
        Normalize for a list of dictionaries.
        Args:
            element: Dict or List

        Returns:
            list of Dict

        """
        if isinstance(element, dict):
            return [self._extract_gov_def_properties(element)]
        elif isinstance(element, list):
            def_list = []
            for i in range(len(element)):
                def_list.append(self._extract_gov_def_properties(element[i]))
            return def_list
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
    @dynamic_catch
    async def _async_create_governance_definition(self, body: dict | NewElementRequestBody) -> str:
        """ Create a governance definition. There are many kinds of governance definition and
            while the overall body structure is the same, many will have different property
            structures nested within them. A list is shown in the notes below.

        It may be of type:
            * BusinessImperative
            * RegulationArticle
            * Threat
            * GovernancePrinciple
            * GovernanceObligation
            * GovernanceApproach
            * GovernanceProcessingPurpose
            The type is added to the "typeName" property.

            Async Version.

        Parameters
        ----------
        body: dict
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the definition created.

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
        Governance definitions can be simple or anchored to a parent element -  Both are shown below. depending on
        which structure is used for the body.

        Many kinds of governance definition have additional properties added. Details are described in the UML diagrams
        on the website and summarized in the table below which shows the property class name and which types
        of governance definitions use it. The test_governance_officer module offers some usage examples.

        Property Class Name     |       Definition Types
        ===================================================================================
        GovernanceDefinitionProperties | BusinessImperative, RegulationArticle, Threat, GovernanceProcessingPurpose,
                                       | GovernancePrinciple, GovernanceObligation, GovernanceApproach
        GovernanceStrategyProperties   | GovernanceStrategy
        RegulationProperties           | Regulation
        GovernanceControlProperties    | GovernanceControl
        SecurityGroupProperties        | SecurityGroup
        NamingStandardRuleProperties   | NamingStandardRule
        CertificationTypeProperties    | CertificationType
        LicenseTyoeProperties          | LicenseType
        GovernanceApproachProperties   | GovernanceApproach


        Generic simple governance body structure:
        {
          "class": "NewElementRequestBody",
          "properties": {
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "enter the type of the governance definition",
            "domainIdentifier": 0,
            "documentIdentifier": "add unique name here",
            "title": "add short name here",
            "summary": "add summary here",
            "description": "add description here",
            "scope": "add scope of effect for this definition",
            "importance": "add importance for this definition",
            "implications": [],
            "outcomes": [],
            "results": [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "initialStatus": "DRAFT"
        }

        Generic governance Body structure with Parent:
        {
          "class" : "NewGovernanceDefinitionRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
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
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "enter the type of the governance definition",
            "domainIdentifier": 0,
            "documentIdentifier": "add unique name here",
            "title": "add short name here",
            "summary": "add summary here",
            "description": "add description here",
            "scope": "add scope of effect for this definition",
            "importance": "add importance for this definition",
            "implications": [],
            "outcomes": [],
            "results": [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "initialStatus": "DRAFT"
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"{self.url_marker}/governance-definitions")
        return await self._async_create_element_body_request(url, GOV_DEF_PROPERTIES_LIST, body)

    @dynamic_catch
    def create_governance_definition(self, body: dict | NewElementRequestBody) -> str:
        """ Create a governance definition. It may be of type:
            * BusinessImperative
            * RegulationArticle
            * Threat
            * GovernancePrinciple
            * GovernanceObligation
            * GovernanceApproach
            * GovernanceProcessingPurpose
            The type is added to the "typeName" property.

        Parameters
        ----------
 
        body: dict
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the definition created.

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
       Governance definitions can be simple or anchored to a parent element -  Both are shown below. depending on
        which structure is used for the body.

        Many kinds of governance definition have additional properties added. Details are described in the UML diagrams
        on the website and summarized in the table below which shows the property class name and which types
        of governance definitions use it. The test_governance_officer module offers some usage examples.

        Property Class Name     |       Definition Types
        ===================================================================================
        GovernanceDefinitionProperties | BusinessImperative, RegulationArticle, Threat, GovernanceProcessingPurpose,
                                       | GovernancePrinciple, GovernanceObligation, GovernanceApproach
        GovernanceStrategyProperties   | GovernanceStrategy
        RegulationProperties           | Regulation
        GovernanceControlProperties    | GovernanceControl
        SecurityGroupProperties        | SecurityGroup
        NamingStandardRuleProperties   | NamingStandardRule
        CertificationTypeProperties    | CertificationType
        LicenseTyoeProperties          | LicenseType
        GovernanceApproachProperties   | GovernanceApproach

        Simple body structure:
        {
          "class": "NewElementRequestBody",
          "properties": {
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "enter the type of the governance definition",
            "domainIdentifier": 0,
            "documentIdentifier": "add unique name here",
            "title": "add short name here",
            "summary": "add summary here",
            "description": "add description here",
            "scope": "add scope of effect for this definition",
            "importance": "add importance for this definition",
            "implications": [],
            "outcomes": [],
            "results": [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "initialStatus": "DRAFT"
        }

        Body structure with Parent:
        {
          "class" : "NewGovernanceDefinitionRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
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
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "enter the type of the governance definition",
            "domainIdentifier": 0,
            "documentIdentifier": "add unique name here",
            "title": "add short name here",
            "summary": "add summary here",
            "description": "add description here",
            "scope": "add scope of effect for this definition",
            "importance": "add importance for this definition",
            "implications": [],
            "outcomes": [],
            "results": [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "initialStatus": "DRAFT"
        }


       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_governance_definition(body))
        return response

    @dynamic_catch
    async def _async_create_governance_definition_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new metadata element to represent a governance definition using an existing metadata element
            as a template. The template defines additional classifications and relationships that should be added to
            the new element. Async version.

        Parameters
        ----------
 
        body: dict
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the governance definition created.

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
          "class" : "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
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
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"{self.url_marker}/governance-definitions/from-template")

        if isinstance(body, TemplateRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)
        else:
            raise PyegeriaInvalidParameterException(
                additional_info={"reason": "body must be a dict or TemplateRequestBody"})

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Created governance definition from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_governance_definition_from_template(self, body: dict | TemplateRequestBody) -> str:
        """ Create a new metadata element to represent a governance definition using an existing metadata element
            as a template. The template defines additional classifications and relationships that should be added to
            the new element.

        Parameters
        ----------
 
        body: dict
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the governance definition created.

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
          "class" : "TemplateRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
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
        response = loop.run_until_complete(self._async_create_governance_definition_from_template(body))
        return response

    @dynamic_catch
    async def _async_update_governance_definition(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a governance definition. Async Version.

        Parameters
        ----------
        guid: str
            guid of the governance definition to update.
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
          "class" : "UpdateElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "Add type name here",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add namespace for this structure",
            "versionIdentifier": "add version for this structure",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"{guid}/update")
        await self._async_update_element_body_request(url, GOV_DEF_PROPERTIES_LIST, body)

    @dynamic_catch
    async def _async_update_governance_definition(self, guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update a governance definition. Async Version."""

    def update_governance_definition(self, guid: str, body: dict | UpdateStatusRequestBody) -> None:
        """ Update the properties of a governance definition.

        Parameters
        ----------
        guid: str
            guid of the governance definition to update.
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
          "class" : "UpdateElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "Add type name here",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add namespace for this structure",
            "versionIdentifier": "add version for this structure",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_governance_definition(guid, body))

    @dynamic_catch
    async def _async_update_governance_definition_status(self, guid: str, status: str = None,
                                                         body: dict | UpdateStatusRequestBody = None) -> None:
        """ Update the status of a governance definition. Async Version.

        Parameters
        ----------
        guid: str
            guid of the governance definition to update.
        status: str, optional, default is None
            The status to update the governance definition to. Superseded by the body definition if present.
        body: dict
            A dictionary containing the updates to the governance definition.

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
          "class": "UpdateGovernanceDefinitionRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "status": "ACTIVE"
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{self.url_marker}/governance-defnitions/"
            f"{guid}/update-status")

        await self._async_update_status_request(url, status, body)

    def update_governance_definition_status(self, guid: str, status: str = None,
                                            body: dict | UpdateStatusRequestBody = None) -> None:
        """ Update the status of a governance definition.

            Parameters
            ----------
            guid: str
                guid of the information governance definition to update.
            status: str, optional, default is None
                The status to update the governance definition to. Superseded by the body definition if present.
            body: dict
                A dictionary containing the updates to the governance definition.

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
              "class" : "UpdateGovernanceDefinitionRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "status": "ACTIVE"
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_governance_definition_status(guid, status, body))

    @dynamic_catch
    async def _async_delete_governance_definition(self, definition_guid: str,
                                                  body: dict | DeleteRequestBody = None,
                                                  cascade: bool = False) -> None:
        """ Delete a governance definition. Async Version.

        Parameters
        ----------
        definition_guid: str
            The guid of the governance definition to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict DeleteRequestBodyt, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        ValidationException
          Raised by pydantic when the request body is invalid.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = (
            f"{self.platform_url}/s"
            f"ervers/{self.view_server}/api/open-metadata/governance-officer/governance-definitions/"
            f"{definition_guid}/delete")
        await self._async_delete_request(url, body, cascade)
        logger.info(f"Deleted collection {definition_guid} with cascade {cascade}")

    def delete_governance_definition(self, definition_guid: str, body: dict | DeleteRequestBody = None,
                                     cascade: bool = False) -> None:
        """Delete a governance definition.

        Parameters
        ----------
        definition_guid: str
            The guid of the governance definition to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict DeleteRequestBodyt, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        ValidationException
          Raised by pydantic when the request body is invalid.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_delete_governance_definition(definition_guid, body, cascade))

    @dynamic_catch
    async def _async_link_peer_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                                           body: dict = None | NewRelationshipRequestBody) -> None:
        """ Attach two peer governance definitions. Request body is optional. Async Version.

        Parameters
        ----------
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
        The relationshipTypeNme can be:
        * GovernanceDriverLink between governance drivers (GovernanceStrategy, BusinessImperative, Regulation,
        RegulationArticle, Threat).
        * GovernancePolicyLink between governance policies (GovernancePrinciple, GovernanceObligation,
        GovernanceApproach).
        * GovernanceControlLink between governance controls (GovernanceRule, GovernanceProcess,
        GovernanceResponsibility, GovernanceProcedure, SecurityAccessControl, SecurityGroup).

        Body structure:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "PeerDefinitionProperties",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (
            f"{self.platform_url}/s"
            f"ervers/{self.view_server}/api/open-metadata/governance-officer/governance-definitions/"
            f"{definition_guid1}/peer-definitions/{relationship_type}/{definition_guid2}/attach")

        await self._async_new_relationship_request(url, "PeerDefinitionProperties", body)
        logger.info(f"Linked {definition_guid1} -> {definition_guid2}")

    @dynamic_catch
    def link_peer_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                              body: dict | NewElementRequestBody = None) -> None:
        """ Attach two peer governance definitions. Async Version.

        Parameters
        ----------
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
        The relationshipTypeNme can be:
        * GovernanceDriverLink between governance drivers (GovernanceStrategy, BusinessImperitive, Regulation,
        RegulationArticle, Threat).
        * GovernancePolicyLink between governance policies (GovernancePrinciple, GovernanceObligation,
        GovernanceApproach).
        * GovernanceControlLink between governance controls (GovernanceRule, GovernanceProcess,
        GovernanceResponsibility, GovernanceProcedure, SecurityAccessControl, SecurityGroup).

        Body structure:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "PeerDefinitionProperties",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_peer_definitions(definition_guid1, relationship_type, definition_guid2, body))

    @dynamic_catch
    async def _async_detach_peer_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                                             body: dict | DeleteRequestBody = None) -> None:
        """ Detach two peer governance definitions. Request body is optional. Async Version.

        Parameters
        ----------
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"{definition_guid1}/peer-definitions/{relationship_type}/{definition_guid2}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached peer definitions: {definition_guid1} -> {definition_guid2}")

    @dynamic_catch
    def detach_peer_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                                body: dict = None | DeleteRequestBody) -> None:
        """ Detach two peer governance definitions. Request body is optional.

        Parameters
        ----------
        definition_guid1: str
            guid of the first governance definition to link.
        definition_guid2: str
            guid of the second governance definition to link.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_peer_definitions(definition_guid1, relationship_type, definition_guid2, body))

    @dynamic_catch
    async def _async_attach_supporting_definitions(self, definition_guid1: str, relationship_type: str,
                                                   definition_guid2: str,
                                                   body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a supporting governance definition. Request body is optional.
            The relationshipTypeNme can be:
            * GovernanceResponse between governance drivers (GovernanceStrategy, BusinessImperative, Regulation,
            RegulationArticle, Threat) and governance policies (GovernancePrinciple, GovernanceObligation,
            GovernanceApproach).
            * GovernanceImplementation between governance policies (GovernancePrinciple, GovernanceObligation,
            GovernanceApproach) and governance controls (GovernanceRule, GovernanceProcess, GovernanceResponsibility,
            GovernanceProcedure, SecurityAccessControl, SecurityGroup).

        Async Version.

        Parameters
        ----------
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "SupportingDefinitionProperties",
            "rationale": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"{definition_guid1}/supporting-definitions/{relationship_type}/{definition_guid2}/attach")
        await self._async_new_relationship_request(url, "SupportingDefinitionProperties", body)
        logger.info(f"Linked {definition_guid1} -> {definition_guid2}")

    @dynamic_catch
    def attach_supporting_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                                      body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a supporting governance definition. Request body is optional.
            The relationshipTypeNme can be:
            * GovernanceResponse between governance drivers (GovernanceStrategy, BusinessImperative, Regulation,
            RegulationArticle, Threat) and governance policies (GovernancePrinciple, GovernanceObligation,
            GovernanceApproach).
            * GovernanceImplementation between governance policies (GovernancePrinciple, GovernanceObligation,
            GovernanceApproach) and governance controls (GovernanceRule, GovernanceProcess, GovernanceResponsibility,
            GovernanceProcedure, SecurityAccessControl, SecurityGroup).

        Parameters
        ----------
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "SupportingDefinitionProperties",
            "rationale": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_attach_supporting_definitions(definition_guid1, relationship_type, definition_guid2, body))

    @dynamic_catch
    async def _async_detach_supporting_definitions(self, definition_guid1: str, relationship_type: str,
                                                   definition_guid2: str,
                                                   body: dict | DeleteRequestBody = None) -> None:
        """ Detach a governance definition from a supporting governance definition.
            Request body is optional. Async Version.

        Parameters
        ----------
        definition_guid1: str
            guid of the first governance definition to unlink.
        definition_guid2: str
            guid of the second governance definition to unlink.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"{definition_guid1}/supporting-definitions/{relationship_type}/{definition_guid2}/detach"
        )
        await self._async_delete_request(url, body)
        logger.info(f"Detached digital supporting definitions: {definition_guid1} -> {definition_guid2}")

    @dynamic_catch
    def detach_supporting_definitions(self, definition_guid1: str, relationship_type: str, definition_guid2: str,
                                      body: dict | DeleteRequestBody = None) -> None:
        """ Detach a governance definition from a supporting governance definition.
            Request body is optional.

        Parameters
        ----------
        definition_guid1: str
            guid of the first governance definition to unlink.
        definition_guid2: str
            guid of the second governance definition to unlink.
        relationship_type: str
            Relationship type name linking the governance definitions..
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
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_supporting_definitions(definition_guid1, relationship_type, definition_guid2, body))

    @dynamic_catch
    async def _async_delete_governance_definition(self, guid: str, body: dict | DeleteRequestBody = None) -> None:
        """ Delete an information supply. Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to delete.
 
        body: dict, optional
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the governance definition created.

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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

       """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"{self.url_marker}/governance-definitions/{guid}/delete")
        await self._async_delete_request(url, body)
        logger.info(f"Deleted governance definition: {guid} ")

    @dynamic_catch
    def delete_governance_definition(self, guid: str, body: dict | DeleteRequestBody = None) -> None:
        """ Delete an information supply. Request body is optional. Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to delete.
 
        body: dict, optionl
            A dictionary containing the definition of the governance definition to create.

        Returns
        -------

        str - guid of the governance definition created.

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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

       """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_governance_definition(guid, body))

    @dynamic_catch
    async def _async_find_governance_definitions(self, search_string: str = "*", classification_names: list[str] = None,
                                                 metadata_element_types: list[str] = None,
                                                 starts_with: bool = True,
                                                 ends_with: bool = False, ignore_case: bool = False,
                                                 start_from: int = 0, page_size: int = 0,
                                                 output_format: str = 'JSON', output_format_set: dict = None,
                                                 body: dict | SearchStringRequestBody = None,
                                                 ) -> list | str:
        """ Retrieve the list of governance definition metadata elements that contain the search string.
            Async version.

            Parameters
            ----------
            search_string : str
                - string to search for.
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
                A list of information governance definition structures or a string if there are no elements found.

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
            If a body is provided it overrides the filter_string parameter.
            
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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"by-search-string")
        return await self._async_find_request(url, _type="GovernanceDefinition",
                                              _gen_output=self._generate_governance_definition_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)

    @dynamic_catch
    def find_governance_definitions(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_types: list[str] = None,
                                    starts_with: bool = True, ends_with: bool = False,
                                    ignore_case: bool = False, start_from: int = 0, page_size: int = 0,
                                    output_format: str = 'JSON', output_format_set: dict = None,
                                    body: dict | SearchStringRequestBody = None, ) -> list | str:
        """ Retrieve the list of governance definition metadata elements that contain the search string.

            Parameters
            ----------
            search_string : str
                - filter_string string to search for.
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
                A list of information governance definition structures or a string if there are no elements found.

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
            If a body is provided it overrides the filter_string parameter.

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
            self._async_find_governance_definitions(search_string, classification_names, metadata_element_types,
                                                    starts_with, ends_with, ignore_case, start_from,
                                                    page_size, output_format, output_format_set, body))
        return response

    @dynamic_catch
    async def _async_get_governance_definitions_by_name(self, filter_string: str,
                                                        classification_names: list[str] = None,
                                                        body: dict | FilterRequestBody = None,
                                                        start_from: int = 0, page_size: int = 0,
                                                        output_format: str = "JSON",
                                                        output_format_set: dict = None) -> list | str:
        """ Returns the list of governance definitions with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str
                name of the information governance definition to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            output_format: str, default = 'JSON'
                Type of output to produce include:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                MERMAID - output mermaid markdown

            Returns
            -------
            [dict] | str
                A list of information governance definitions matching the name.

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
            If a body is provided it overrides the filter_string parameter.
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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/by-name")
        response = await self._async_get_name_request(url, _type="GovernanceDefinition",
                                                      _gen_output=self._generate_governance_definition_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_governance_definitions_by_name(self, filter_string: str, classification_names: list[str] = None,
                                           body: dict | FilterRequestBody = None,
                                           start_from: int = 0, page_size: int = 0,
                                           output_format: str = "JSON",
                                           output_format_set: dict = None) -> list | str:
        """ Returns the list of governance definitions with a particular name."""

        """ Returns the list of information governance definitions with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str
                name of the information governance definition to retrieve.
            body: dict, optional
                A dictionary containing parameters of the retrieval.
            add_implementation: bool, optional
                Whether to add the implementation details to the response.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=0], optional
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
                A list of information governance definitions matching the name.

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
            self._async_get_governance_definitions_by_name(filter_string, classification_names, body,
                                                           start_from, page_size, output_format, output_format_set))
        return response

    @dynamic_catch
    async def _async_get_governance_definition_by_guid(self, guid: str, element_type: str = None,
                                                       body: dict | FilterRequestBody = None,
                                                       output_format: str = "JSON",
                                                       output_format_set: dict = None) -> dict | str:

        """ Get governance definition by guid.
            Async version.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
 
        body: dict, optional
            A dictionary containing the definition of the governance definition to create.
        output_format: str
            The output format to use.

        Returns
        -------

        dict | str
                A list of information governance definition structures or a string if there are no elements found.


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
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

       """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
            f"{self.url_marker}/governance-definitions/"
            f"{guid}/retrieve")
        type = element_type if element_type else "GovernanceDefinition"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_governance_definition_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_governance_definition_by_guid(self, guid: str, element_type: str = None, body: dict = None,
                                          output_format: str = "JSON",
                                          output_format_set: dict = None) -> dict | str:

        """ Get governance definition by guid.

        Parameters
        ----------
        guid: str
            GUID of the governance definition to get.
 
        body: dict, optional
            A dictionary containing the definition of the governance definition to create.
        output_format: str, default = "JSON"
            The output format to use.

        Returns
        -------

        dict | str
                A list of information governance definition structures or a string if there are no elements found.


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
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

       """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_governance_definition_by_guid(guid, element_type, body,
                                                                                         output_format,
                                                                                         output_format_set))
        return response

    @dynamic_catch
    async def _async_link_design_to_implementation(self, design_desc_guid: str, implementation_guid: str,
                                                   body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a design object such as a solution component or governance definition to its implementation via the
            ImplementedBy relationship. Request body is optional. Async Version.
            https://egeria-project.org/types/7/0737-Solution-Implementation/

        Parameters
        ----------
        design_desc_guid: str
            guid of the design element to link.
        implementation_guid: str
            guid of the implementation definition to link.
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ImplementedByProperties",
            "designStep": "",
            "role": "",
            "transformation": "",
            "description": "",
            "iscQualifiedName": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{self.url_marker}/designs/"
               f"{design_desc_guid}/implementations/{implementation_guid}/attach")
        await self._async_new_relationship_request(url, "ImplementedByProperties", body)
        logger.info(f"Linked design to implementation: {design_desc_guid} -> {implementation_guid}")

    @dynamic_catch
    def link_design_to_implementation(self, design_desc_guid: str, implementation_guid: str,
                                      body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a design object such as a solution component or governance definition to its implementation via the
            ImplementedBy relationship. Request body is optional.
            https://egeria-project.org/types/7/0737-Solution-Implementation/

        Parameters
        ----------
        design_desc_guid: str
            guid of the design element to link.
        implementation_guid: str
            guid of the implementation definition to link.
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ImplementedByProperties",
            "designStep": "",
            "role": "",
            "transformation": "",
            "description": "",
            "iscQualifiedName": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_design_to_implementation(design_desc_guid, implementation_guid, body))

    @dynamic_catch
    async def _async_detach_design_from_implementation(self, design_desc_guid: str, implementation_guid: str,
                                                       body: dict | DeleteRequestBody = None) -> None:
        """ Detach a governance definition from its implementation. Async Version.

        Parameters
        ----------
        design_desc_guid: str
            guid of the technical control to link.
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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{self.url_marker}/designs/"
               f"{design_desc_guid}/implementations/{implementation_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(
            f"Detached design from implementation: {design_desc_guid} -> {implementation_guid}")

    @dynamic_catch
    def detach_design_from_implementation(self, design_desc_guid: str, implementation_guid: str,
                                          body: dict | DeleteRequestBody = None) -> None:
        """ Detach a governance definition from its implementation. Request body is optional.

        Parameters
        ----------
        design_descl_guid: str
            guid of the technical control to unlink.
        implementation_guid: str
            guid of the implementation definition to unlink.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_design_from_implementation(design_desc_guid, implementation_guid, body))

    @dynamic_catch
    async def _async_link_implementation_resource(self, design_desc_guid: str, implementation_guid: str,
                                                  body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a design object such as a solution component or governance definition to one of its implementation
            resource via the ImplementationResource relationship. Request body is optional.
            https://egeria-project.org/types/7/0737-Solution-Implementation/

        Parameters
        ----------
        design_desc_guid: str
            guid of the design element to link.
        implementation_guid: str
            guid of the implementation definition to link.
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ImplementedByProperties",
            "designStep": "",
            "role": "",
            "transformation": "",
            "description": "",
            "iscQualifiedName": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{self.url_marker}/designs/"
               f"{design_desc_guid}/implementation-resources/{implementation_guid}/attach")
        await self._async_new_relationship_request(url, "ImplementationResourceProperties", body)
        logger.info(f"Linked design to implementation resource: {design_desc_guid} -> {implementation_guid}")

    @dynamic_catch
    def link_implementation_resource(self, design_desc_guid: str, implementation_guid: str,
                                     body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a design object such as a solution component or governance definition to its implementation via the
            ImplementedBy relationship. Request body is optional.
            https://egeria-project.org/types/7/0737-Solution-Implementation/

        Parameters
        ----------
        design_desc_guid: str
            guid of the design element to link.
        implementation_guid: str
            guid of the implementation definition to link.
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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ImplementedByProperties",
            "designStep": "",
            "role": "",
            "transformation": "",
            "description": "",
            "iscQualifiedName": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_implementation_resource(design_desc_guid, implementation_guid, body))

    @dynamic_catch
    async def _async_detach_implementation_resource(self, design_desc_guid: str, implementation_guid: str,
                                                    body: dict | DeleteRequestBody = None) -> None:
        """ Detach a design object such as a solution component or governance definition from one of its implementation
            resources. Request body is optional. Async version.

        Parameters
        ----------
        design_desc_guid: str
            guid of the technical control to link.
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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/{self.url_marker}/designs/"
               f"{design_desc_guid}/implementation-resources/{implementation_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(
            f"Detached design from implementation resource: {design_desc_guid} -> {implementation_guid}")

    def detach_implementation_resource(self, design_desc_guid: str, implementation_guid: str,
                                       body: dict | DeleteRequestBody = None) -> None:
        """ Detach a design object such as a solution component or governance definition from one of its implementation
            resources. Request body is optional.

        Parameters
        ----------
        design_desc_guid: str
            guid of the technical control to link.
        implementation_guid: str
            guid of the implementation definition to unlink.
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
          "externalSourceGUID": "string",
          "externalSourceName": "string",
          "forLineage": true,
          "forDuplicateProcessing": true,
          "effectiveTime": "2025-06-13T15:13:31.339Z"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_implementation_resource(design_desc_guid, implementation_guid, body))

    # async def _async_get_gov_def_in_context(self, guid: str, body: dict = None, output_format: str = "JSON",
    # start_from: int = 0,
    #                                         page_size: int = 0) -> list[dict] | str:
    #     """ Get governance definition in context. Brings back the graph.
    #         Async version.
    #
    #         Parameters
    #         ----------
    #         guid: str
    #             GUID of the governance definition to get.
    #
    #         body: dict
    #             A dictionary containing the definition of the governance definition to get.
    #         output_format: str
    #             The output format to use.
    #         start_from: int, default= 0
    #             Indicates the start of the page range.
    #         page_size: int, default = 0
    #             The page size to use.
    #
    #         Returns
    #         -------
    #
    #         list[dict] | str
    #                 A list of information governance definition structures or a string if there are no elements found.
    #
    #
    #         Raises
    #         ------
    #         InvalidParameterException
    #             one of the parameters is null or invalid or
    #         PropertyServerException
    #             There is a problem adding the element properties to the metadata repository or
    #         UserNotAuthorizedException
    #             the requesting user is not authorized to issue this request.
    #
    #         Notes
    #         ----
    #         https://egeria-project.org/concepts/governance-definition
    #
    #         Body structure:
    #         {
    #           "forLineage": true,
    #           "forDuplicateProcessing": true,
    #           "effectiveTime": "2025-06-13T14:12:44.896Z",
    #           "limitResultsByStatus": [
    #             "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}"
    #           ],
    #           "asOfTime": "2025-06-13T14:12:44.896Z",
    #           "sequencingOrder": "SequencingOrder{Any Order}",
    #           "sequencingProperty": "string"
    #         }
    #
    #        """
    #     possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size)])
    #
    #     url = (
    #         f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
    #         f"{self.url_marker}/governance-definitions/"
    #         f"{guid}/in-context{possible_query_params}")
    #
    #     if body:
    #         response = await self._async_make_request("POST", url, body_slimmer(body))
    #     else:
    #         response = await self._async_make_request("POST", url)
    #
    #     element = response.json().get("element", NO_ELEMENTS_FOUND)
    #     if output_format != 'JSON':  # return a simplified markdown representation
    #         return self.generate_governance_definition_output(element, "", output_format)
    #     return response.json().get("element", NO_ELEMENTS_FOUND)
    #
    # def get_gov_def_in_context(self, guid: str, body: dict = None, output_format: str = "JSON", start_from: int = 0,
    #                            page_size: int = 0) -> list[dict] | str:
    #     """ Get governance definition in context. Brings back the graph.
    #
    #         Parameters
    #         ----------
    #         guid: str
    #             GUID of the governance definition to get.
    #
    #         body: dict
    #             A dictionary containing the definition of the governance definition to get.
    #         output_format: str
    #             The output format to use.
    #         start_from: int, default= 0
    #             Indicates the start of the page range.
    #         page_size: int, default = 0
    #             The page size to use.
    #
    #         Returns
    #         -------
    #
    #         list[dict] | str
    #                 A list of information governance definition structures or a string if there are no elements found.
    #
    #
    #         Raises
    #         ------
    #         InvalidParameterException
    #             one of the parameters is null or invalid or
    #         PropertyServerException
    #             There is a problem adding the element properties to the metadata repository or
    #         UserNotAuthorizedException
    #             the requesting user is not authorized to issue this request.
    #
    #         Notes
    #         ----
    #         https://egeria-project.org/concepts/governance-definition
    #
    #         Body structure:
    #         {
    #           "forLineage": true,
    #           "forDuplicateProcessing": true,
    #           "effectiveTime": "2025-06-13T14:12:44.896Z",
    #           "limitResultsByStatus": [
    #             "InstanceStatus{ordinal=0, name='<Unknown>', description='Unknown instance status.'}"
    #           ],
    #           "asOfTime": "2025-06-13T14:12:44.896Z",
    #           "sequencingOrder": "SequencingOrder{Any Order}",
    #           "sequencingProperty": "string"
    #         }
    #
    #        """
    #
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(
    #         self._async_get_gov_def_in_context(guid, body, output_format, start_from, page_size))
    #     return response


if __name__ == "__main__":
    print("Main-Metadata Explorer")

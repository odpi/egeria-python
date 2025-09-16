"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain reference data.
    https://egeria-project.org/concepts/project

"""

import asyncio

from pyegeria._output_formats import select_output_format_set
from pyegeria._client_new import Client2
from pyegeria._output_formats import get_output_format_type_match
from pyegeria.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, DeleteRequestBody, UpdateElementRequestBody,
                             NewRelationshipRequestBody, DeleteElementRequestBody, DeleteRelationshipRequestBody)
from pyegeria.output_formatter import generate_output, populate_columns_from_properties, \
    _extract_referenceable_properties, get_required_relationships, populate_common_columns, overlay_additional_values
from pyegeria.utils import body_slimmer, dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from loguru import logger


class ReferenceDataManager(Client2):
    """
    Manage Reference Data in Egeria..

    This client provides asynchronous and synchronous helpers to create, update, search,
    and relate Project elements and their subtypes (Campaign, StudyProject, Task, PersonalProject).

    References


    Parameters
    -----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        Default user identity for calls (can be overridden per call).
    user_pwd : str, optional
        Password for the user_id. If a token is supplied, this may be None.

    Notes
    -----
    - Most high-level list/report methods accept an `output_format` and an optional `output_format_set` and
      delegate rendering to `pyegeria.output_formatter.generate_output` along with shared helpers such as
      `populate_common_columns`.
    - Private extractor methods follow the convention: `_extract_<entity>_properties(element, columns_struct)` and
      must return the same `columns_struct` with per-column `value` fields populated.
    """

    def __init__(
            self,
            view_server: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.ref_data_command_base: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/reference-data"
        )
        self.url_marker = 'reference-data'
        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _extract_additional_valid_value_definition_properties(self, element: dict, columns_struct: dict)-> dict:


        roles_required = any(column.get('key') == 'project_roles'
                             for column in columns_struct.get('formats', {}).get('columns', []))
        project_props = {}

        if roles_required:
            project_roles = element['elementHeader'].get('projectRoles', [])
            project_roles_list = []
            for project_role in project_roles:
                project_roles_list.append(project_role.get('classificationName', ""))
            project_roles_md = (", \n".join(project_roles_list)).rstrip(',') if project_roles_list else ''
            project_props = {
                'project_roles': project_roles_md,
            }
        return project_props




    def _extract_valid_value_definition_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Common population pipeline
        col_data = populate_common_columns(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])
        # Overlay extras (project roles) only where empty

        # extra = self._extract_additional_project_properties(element, columns_struct)

        # col_data = overlay_additional_values(col_data, extra)
        return col_data


    def _generate_vv_def_output(self, elements: dict | list[dict], search_string: str,
                                 element_type_name: str | None,
                                 output_format: str = 'DICT',
                                 output_format_set: dict | str = None) -> str | list[dict]:
        entity_type = 'ValidValueDefinition'
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_valid_value_definition_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #


    @dynamic_catch
    async def _async_find_valid_value_definitions(
            self,
            search_string: str, classification_names: list[str] = None, metadata_element_types: list[str] = None,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,
            body: dict | SearchStringRequestBody = None
    ) -> list | str:
        """ Returns the list of valid value definitions matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith,and ignoreCase can be used to allow a fuzzy search.
            Async version.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects matching the search string. Returns a string if none found.

        Raises
        ------

        PyegeriaException
        ValidationError

        """

        url = f"{self.ref_data_command_base}/valid-value-definitions/by-search-string"

        response = await self._async_find_request(url, _type="ValidValuesDefinition",
                                                  _gen_output=self._generate_vv_def_output,
                                                  search_string=search_string,
                                                  classification_names=classification_names,
                                                  metadata_element_types=metadata_element_types,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response

    @dynamic_catch
    def find_valid_value_definitions(
            self,
            search_string: str, classification_names: list[str] = None, metadata_element_types: list[str] = None,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,
            body: dict | SearchStringRequestBody = None
    ) -> list | str:

        """ Returns the list of valid value definitions matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects matching the search string. Returns a string if none found.

        Raises
        ------

        PyegeriaException
        ValidationError

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_find_valid_value_definitions(
                search_string,
                classification_names,
                metadata_element_types,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                output_format_set,
                body,
            )
        )

        return resp

    @dynamic_catch
    async def _async_get_valid_value_definitions_by_name(
            self, filter_string: str = None, classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None) -> list | str:
        url = f"{self.ref_data_command_base}/valid-value-definitions/by-name"

        response = await self._async_get_name_request(url, _type="ValidValuesDefinition",
                                                      _gen_output=self._generate_vv_def_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_valid_value_definitions_by_name(
            self, filter_string: str = None, classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None) -> list | str:

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_valid_value_definitions_by_name(
                filter_string,
                classification_names,
                body,
                start_from,
                page_size,
                output_format,
                output_format_set,
            )
        )
        return resp

    @dynamic_catch
    async def _async_get_valid_value_definition_by_guid(self, vv_def_guid: str, element_type: str = None,
                                         body: dict | GetRequestBody = None,
                                         output_format: str = 'JSON',
                                         output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific project. Async version.

            Parameters
            ----------
            vv_def_guid: str,
                unique identifier of the collection.
            element_type: str, default = None, optional
                type of valid value
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------
            PyegeriaException
            ValidationError

            Notes
            ----
            Body sample:
            {
              "class": "GetRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """

        url = f"{self.ref_data_command_base}/valid-value-definitions/{vv_def_guid}/retrieve"
        type = element_type if element_type else "ValidValuesDefinition"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_vv_def_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_valid_value_definition_by_guid(self, vv_def_guid: str, element_type: str = None,
                            body: dict | GetRequestBody = None,
                            output_format: str = 'JSON',
                            output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific project.

            Parameters
            ----------
            vv_def_guid: str,
                unique identifier of the collection.
            element_type: str, default = None, optional
                type of collection - Collection, DataSpec, Agreement, etc.
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            ----
            Body sample:
            {
              "class": "GetRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_valid_value_definition_by_guid(vv_def_guid, element_type, body, output_format, output_format_set)
        )

        return resp

    #
    #   Create Valid Value Definition methods
    #
    @dynamic_catch
    async def _async_create_valid_value_definition(self, body: dict | NewElementRequestBody) -> str:
        """Create Valid Value definition. Async version.

        Parameters
        ----------.
        body: dict
            A dict representing the details of the valid value definition to create. .

        Returns
        -------
        str - the guid of the created valid value definition.

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        -----

        Body structure like:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "initialClassifications" : {
            "ZoneMembership" : { "class" :  "ZoneMembershipProperties" ,
              "zoneMembership" : ["QuarantineZone", "Production"]}
             },
          "properties": {
            "class" : "ValidValueDefinitionProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add description here",
            "namespace" : "add namespace here",
            "userDefinedStatus" : "add status here",
            "usage": "add usage here",
            "dataType" : "add data type here",
            "scope" : "add scope here",
            "preferredValue" : "add preferred value here",
            "isCaseSensitive" : false,
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
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = f"{self.ref_data_command_base}/valid-value-definitions"

        return await self._async_create_element_body_request(url, ["ValidValueDefinitionProperties"], body)

    @dynamic_catch
    def create_valid_value_definition(self, body: dict | NewElementRequestBody) -> str:
        """Create Valid Value definition. Async version.

        Parameters
        ----------.
        body: dict
            A dict representing the details of the valid value definition to create. .

        Returns
        -------
        str - the guid of the created valid value definition.

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        -----

        Body structure like:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "initialClassifications" : {
            "ZoneMembership" : { "class" :  "ZoneMembershipProperties" ,
              "zoneMembership" : ["QuarantineZone", "Production"]}
             },
          "properties": {
            "class" : "ValidValueDefinitionProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add description here",
            "namespace" : "add namespace here",
            "userDefinedStatus" : "add status here",
            "usage": "add usage here",
            "dataType" : "add data type here",
            "scope" : "add scope here",
            "preferredValue" : "add preferred value here",
            "isCaseSensitive" : false,
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
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_create_valid_value_definition(body)
        )
        return resp

    @dynamic_catch
    async def _async_create_valid_value_definition_from_template(
            self,
            body: dict | TemplateRequestBody,
    ) -> str:
        """ Create a new metadata element to represent a valid value definition using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Request body provides properties that override the template
            Async version.

        Parameters
        ----------

        body: dict
            A dict representing the details of the valid value definition to create and the over-rides to the template..

        Returns
        -------
        str - the guid of the created valid value definition.

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        -----
        JSON Structure looks like:

        {
          "class" : "TemplateRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
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
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = f"{self.ref_data_command_base}/valid-value-definitions/from-template"
        return await self._async_create_element_from_template(url, body)

    @dynamic_catch
    def create_valid_value_definition_from_template(
            self,
            body: dict | TemplateRequestBody,
    ) -> str:
        """ Create a new metadata element to represent a valid value definition using an existing metadata element as a template.
           The template defines additional classifications and relationships that should be added to the new element.
           Request body provides properties that override the template

           Parameters
           ----------

           body: dict
               A dict representing the details of the valid value definition to create and the over-rides to the template..

           Returns
           -------
           str - the guid of the created valid value definition.

           Raises
           ------
           PyegeriaException
           ValidationError

           Notes
           -----
           JSON Structure looks like:

           {
             "class" : "TemplateRequestBody",
             "anchorGUID" : "add guid here",
             "isOwnAnchor": false,
             "parentGUID": "add guid here",
             "parentRelationshipTypeName": "add type name here",
             "parentRelationshipProperties": {
               "class": "RelationshipElementProperties",
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
             },
             "externalSourceGUID": "add guid here",
             "externalSourceName": "add qualified name here",
             "effectiveTime" : "{{$isoTimestamp}}",
             "forLineage" : false,
             "forDuplicateProcessing" : false
           }

           """

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_valid_value_definition_from_template(body))
        return resp

    #
    #
    #

    @dynamic_catch
    async def _async_update_valid_value_definition(
            self,
            vv_def_guid: str,
            body: dict | UpdateElementRequestBody
    ) -> None:
        """Update the properties of a valid value definition. Async Version.

        Parameters
        ----------
        vv_def_guid: str
            Unique identifier for the valid value definition.
        body: dict | UpdateElementRequestBody
            A dict representing the details of the valid value definition to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        _____
        Sample body:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ValidValueDefinitionProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add description here",
            "namespace" : "add namespace here",
            "userDefinedStatus" : "add status here",
            "usage": "add usage here",
            "dataType" : "add data type here",
            "scope" : "add scope here",
            "preferredValue" : "add preferred value here",
            "isCaseSensitive" : false,
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
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = f"{self.ref_data_command_base}/valid-value-definitions/{vv_def_guid}/update"

        await self._async_update_element_body_request(url, ["ValidValueDefinitionProperties"], body)
        logger.info(f"Updated valid value definition {vv_def_guid}")

    @dynamic_catch
    def update_valid_value_definition(
            self,
            vv_def_guid: str,
            body: dict | UpdateElementRequestBody
    ) -> None:
        """Update the properties of a valid value definition.

        Parameters
        ----------
        vv_def_guid: str
            Unique identifier for the valid value definition.
        body: dict | UpdateElementRequestBody
            A dict representing the details of the valid value definition to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        _____
        Sample body:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ValidValueDefinitionProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add description here",
            "namespace" : "add namespace here",
            "userDefinedStatus" : "add status here",
            "usage": "add usage here",
            "dataType" : "add data type here",
            "scope" : "add scope here",
            "preferredValue" : "add preferred value here",
            "isCaseSensitive" : false,
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
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_valid_value_definition(vv_def_guid, body))

    @dynamic_catch
    async def _async_link_valid_value_member(self, vv_set_guid:str, vv_member_guid: str, body: dict | NewRelationshipRequestBody):
        """ Link a valid value definition to another valid value definition. Async version.

        Parameters
        __________
        vv_set_guid: str
            Unique identifier for the valid value definition set in the role of parent.
        vv_member_guid: str
            Unique identifier for the valid value definition member.(Child)
        body: dict | NewRelationshipRequestBody
            A dict representing the details of the relationship.

        Returns
        ______
        None

        Raises
        ______
        PyegeriaException
        ValidationError

        Notes
        -----
        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": false,
            "label": "",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        url = f"{self.ref_data_command_base}/valid-values/{vv_set_guid}/members/{vv_member_guid}/attach"
        await self._async_create_element_body_request(url, ["ValidValueMemberProperties"], body)
        logger.info(f"Linked valid value definition {vv_set_guid} to {vv_member_guid}")

    @dynamic_catch
    def link_valid_value_definition(
            self,
            vv_set_guid: str, vv_member_guid: str, body: dict | NewRelationshipRequestBody = None) -> None:
        """ Link a valid value definition to another valid value definition.

        Parameters
        __________
        vv_set_guid: str
            Unique identifier for the valid value definition set in the role of parent.
        vv_member_guid: str
            Unique identifier for the valid value definition member.(Child)
        body: dict | NewRelationshipRequestBody
            A dict representing the details of the relationship.

        Returns
        ______
        None

        Raises
        ______
        PyegeriaException
        ValidationError

        Notes
        -----
        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": false,
            "label": "",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_valid_value_member(vv_set_guid, vv_member_guid, body))

    @dynamic_catch
    async def _async_detach_valid_value_member(self, vv_set_guid: str, vv_member_guid: str,
                                             body: dict | DeleteRelationshipRequestBody):
        """ Link a valid value definition to another valid value definition. Async version.

        Parameters
        __________
        vv_set_guid: str
            Unique identifier for the valid value definition set in the role of parent.
        vv_member_guid: str
            Unique identifier for the valid value definition member.(Child)
        body: dict | NewRelationshipRequestBody
            A dict representing the details of the relationship.

        Returns
        ______
        None

        Raises
        ______
        PyegeriaException
        ValidationError

        Notes
        -----
        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": false,
            "label": "",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        url = f"{self.ref_data_command_base}/valid-values/{vv_set_guid}/members/{vv_member_guid}/attach"
        await self._async_create_element_body_request(url, ["ValidValueMemberProperties"], body)
        logger.info(f"Linked valid value definition {vv_set_guid} to {vv_member_guid}")

    @dynamic_catch
    def detach_valid_value_definition(
            self,
            vv_set_guid: str, vv_member_guid: str, body: dict | DeleteRelationshipRequestBody = None) -> None:
        """ Detach a valid value definition from another valid value definition.

        Parameters
        __________
        vv_set_guid: str
            Unique identifier for the valid value definition set in the role of parent.
        vv_member_guid: str
            Unique identifier for the valid value definition member.(Child)
        body: dict | NewRelationshipRequestBody
            A dict representing the details of the relationship.

        Returns
        ______
        None

        Raises
        ______
        PyegeriaException
        ValidationError

        Notes
        -----
        Sample body:

        {
          "class": "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_valid_value_member(vv_set_guid, vv_member_guid, body))

    @dynamic_catch
    async def _async_delete_valid_value_definition(
            self,
            vv_def_guid: str, cascade_delete: bool = False, body: dict | DeleteElementRequestBody = None) -> None:
        """Delete a valid value definition.  Async version

        Parameters
        ----------
        vv_def_guid: str
            The guid of the valid value definition to delete.
        cascade_delete: bool, optional, default = False
            If true, delete all elements anchored to this definition.
        body: dict | DeleteElementRequestBody, optional
            A dict representing the details of the valid value definition to delete.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        _____
        Sample body:
        {
          "class" : "DeleteElementRequestBody",
          "cascadeDelete" : false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = f"{self.ref_data_command_base}/valid-value-definitions/{vv_def_guid}/delete"

        await self._async_delete_request(url, body, cascade_delete)
        logger.info(f"Deleted valid value definition {vv_def_guid} with cascade {cascade_delete}")

    @dynamic_catch
    def delete_valid_value_definition(
            self,
            vv_def_guid: str, cascade_delete: bool = False, body: dict | DeleteElementRequestBody = None) -> None:
        """Delete a valid value definition.

            Parameters
            ----------
            vv_def_guid: str
                The guid of the valid value definition to delete.
            cascade_delete: bool, optional, default = False
                If true, delete all elements anchored to this definition.
            body: dict | DeleteElementRequestBody, optional
                A dict representing the details of the valid value definition to delete.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
            ValidationError

            Notes
            _____
            Sample body:
            {
              "class": "DeleteElementRequestBody",
              "cascadeDelete": false,
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_valid_value_definition(vv_def_guid, cascade_delete, body))




if __name__ == "__main__":
    print("Main-Project Manager")

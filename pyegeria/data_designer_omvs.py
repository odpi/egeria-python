"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the data-designer OMVS module.

[data-designer](https://egeria-project.org/services/omvs/data-designer/overview)

"""

import asyncio

from httpx import Response

from pyegeria._client import Client, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND
from pyegeria.output_formatter import (extract_mermaid_only, extract_basic_dict, generate_output)
from pyegeria.utils import body_slimmer


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
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/data-designer"


class DataDesigner(Client):
    """DataDesigner is a class that extends the Client class. The Data Designer OMVS provides APIs for
      building specifications for data. This includes common data fields in a data dictionary, data specifications
      for a project and data classes for data quality validation.
    """

    def __init__(self, view_server_name: str, platform_url: str, user_id: str = None, user_pwd: str = None,
                 token: str = None, ):
        self.view_server = view_server_name
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.metadata_explorer_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-designer")
        Client.__init__(self, view_server_name, platform_url, user_id=user_id, user_pwd=user_pwd, token=token, )

    #
    #    Data Structures
    #

    async def _async_create_data_structure(self, name: str, description: str, qualified_name: str = None,
                                           namespace: str = None, version_id: str = None) -> str:
        """
        Create a new data structure from a provided dict body. Async version.

        Parameters
        ----------
        name : str
            - unique name to search for
        description : str
            - description of the data structure
        qualified_name : str, optional
            - unique name of the data structure, if not provided, one will be generated from the name.
        namespace : str
            - a namespace for the data structure
        version_id : str, optional
            - a version identifier for the data structure

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if version_id is None:
            qualified_name = qualified_name or f"DataStructure::{name}"
        else:
            qualified_name = qualified_name or f"DataStructure::{name}::{version_id}"
        if namespace:
            qualified_name = f"{namespace}::{qualified_name}"

        body = {
            "properties": {
                "class": "DataStructureProperties", "qualifiedName": qualified_name, "displayName": name,
                "description": description, "namespace": namespace, "versionIdentifier": version_id
                }
            }

        url = f"{base_path(self, self.view_server)}/data-structures"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure(self, name: str, description: str, qualified_name: str = None, namespace: str = None,
                              version_id: str = None) -> str:
        """
        Create a new data structure from a provided dict body.

        Parameters
        ----------
        name : str
            - unique name to search for
        description : str
            - description of the data structure
        qualified_name : str, optional
            - unique name of the data structure, if not provided, one will be generated from the name.
        namespace : str
            - a namespace for the data structure
        version_id : str, optional
            - a version identifier for the data structure

        Returns
        -------
        str
            The GUID of the element - or "No element found"

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
            self._async_create_data_structure(name, description, qualified_name, namespace, version_id, ))
        return response

    async def _async_create_data_structure_w_body(self, body: dict) -> str:
        """
        Create a new data structure with basic parameters. Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data structure to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        Full sample body:

            {
              "class" : "NewDataStructureRequestBody",
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
                "class" : "DataStructureProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "namespace": "add namespace for this structure",
                "versionIdentifier": "add version for this structure",
                "additionalProperties": {
                  "property1" : "propertyValue1",
                  "property2" : "propertyValue2"
                },
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }

        """

        url = f"{base_path(self, self.view_server)}/data-structures"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure_w_body(self, body: dict) -> str:
        """
        Create a new data structure with basic parameters.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data structure to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        Full sample body:

            {
              "class" : "NewDataStructureRequestBody",
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
                "class" : "DataStructureProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "namespace": "add namespace for this structure",
                "versionIdentifier": "add version for this structure",
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
        response = loop.run_until_complete(self._async_create_data_structure_w_body(body, ))
        return response

    async def _async_create_data_structure_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data structure using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data structure to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        Full sample body:

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

        url = f"{base_path(self, self.view_server)}/data-structures/from-template"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data structure using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data structure to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        Full sample body:

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
        response = loop.run_until_complete(self._async_create_data_structure_from_template(body, ))
        return response

    async def _async_update_data_structure_w_body(self, data_struct_guid: str, body: dict,
                                                  replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data structure. Async version.

        Parameters
        ----------
        data_struct_guid: str
            - the GUID of the data structure to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
        replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
             will be replaced.
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

        Note
        ----

        Full sample body:

        {
          "class" : "UpdateDataStructureRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataStructureProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add namespace for this structure",
            "versionIdentifier": "add version for this structure",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        replace_all_properties_s = str(replace_all_properties).lower()

        url = (f"{base_path(self, self.view_server)}/data-structures/{data_struct_guid}/update?"
               f"replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_data_structure_w_body(self, data_struct_guid: str, body: dict.get,
                                     replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data structure.

        Parameters
        ----------
        data_struct_guid: str
            - the GUID of the data structure to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
r       replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
              will be replaced.
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

        Note
        ----

        Full sample body:

                    {
          "class" : "UpdateDataStructureRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataStructureProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add namespace for this structure",
            "versionIdentifier": "add version for this structure",
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
        loop.run_until_complete(
            self._async_update_data_structure_w_body(data_struct_guid, body, replace_all_properties))

    async def _async_link_member_data_field(self, parent_data_struct_guid: str, member_data_field_guid: str,
                                            body: dict = None) -> None:
        """
        Connect a data structure to a data field. Async version.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data class will be connected to.
        member_data_field_guid: str
            - the GUID of the data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

        {
          "class" : "MemberDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "MemberDataFieldProperties",
            "dataFieldPosition": 0,
            "minCardinality": 0,
            "maxCardinality": 0,
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-structures/{parent_data_struct_guid}"
               f"/member-data-fields/{member_data_field_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_member_data_field(self, parent_data_struct_guid: str, member_data_field_guid: str,
                               body: dict = None) -> None:
        """
        Connect a data structure to a data field.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data class will be connected to.
        member_data_field_guid: str
            - the GUID of the data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

        {
          "class" : "MemberDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "MemberDataFieldProperties",
            "dataFieldPosition": 0,
            "minCardinality": 0,
            "maxCardinality": 0,
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_member_data_field(parent_data_struct_guid, member_data_field_guid, body))

    async def _async_detach_member_data_field(self, parent_data_struct_guid: str, member_data_field_guid: str,
                                              body: dict = None) -> None:
        """
        Detach a data class from a data structure. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data class will be detached from..
        member_data_field_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-structures/{parent_data_struct_guid}"
               f"/member-data-fields/{member_data_field_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_member_data_field(self, parent_data_struct_guid: str, member_data_field_guid: str,
                                 body: dict = None) -> None:
        """
        Detach a data class from a data structure. Request body is optional.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data class will be detached fromo.
        member_data_field_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

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
            self._async_detach_member_data_field(parent_data_struct_guid, member_data_field_guid, body))

    async def _async_delete_data_structure(self, data_struct_guid: str, body: dict = None, cascade: bool=False) -> None:
        """
        Delete a data structure. Request body is optional. Async version.

        Parameters
        ----------
       data_struct_guid: str
            - the GUID of the parent data structure to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then all child data structures will be deleted as well. Otherwise, only the data structure

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

        Note
        ----

        Full sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """
        cascaded_s = str(cascade).lower()
        url = f"{base_path(self, self.view_server)}/data-structures/{data_struct_guid}/delete?cascadedDelete={cascaded_s}"

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def delete_data_structure(self, data_struct_guid: str, body: dict = None, cascade: bool = False) -> None:
        """
        Delete a data structure. Request body is optional.

        Parameters
        ----------
        data_struct_guid: str
            - the GUID of the data structure to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then all child data structures will be deleted as well. Otherwise, only the data structure


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

        Note
        ----

        Full sample body:

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
        loop.run_until_complete(self._async_delete_data_field(data_struct_guid, body, cascade))

    async def _async_find_all_data_structures(self, start_from: int = 0, page_size: int = max_paging_size,
                                              output_format: str = "DICT") -> list | str:
        """Returns a list of all known data structures. Async version.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict of elements with the results.

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
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", 'false'), ("endsWith", 'false'),
             ("ignoreCase", 'true')])

        url = (f"{base_path(self, self.view_server)}/data-structures/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_structure_output(elements, filter, output_format)
        return elements

    def find_all_data_structures(self, start_from: int = 0, page_size: int = max_paging_size,
                                 output_format: str = "DICT") -> list | str:
        """ Returns a list of all known data structures.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  elements with the results.

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
        response = loop.run_until_complete(self._async_find_all_data_structures(start_from, page_size, output_format))
        return response

    async def _async_find_data_structures_w_body(self, body: dict, start_from: int = 0,
                                                 page_size: int = max_paging_size, starts_with: bool = True,
                                                 ends_with: bool = False, ignore_case: bool = True,
                                                 output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data structure metadata elements that contain the search string.
            Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", 'REPORT', 'FORM', "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

        """
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with_s),
             ("endsWith", ends_with_s), ("ignoreCase", ignore_case_s), ])

        url = (f"{base_path(self, self.view_server)}/data-structures/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_structure_output(elements, filter, output_format)
        return elements

    def find_data_structures_w_body(self, body: dict, start_from: int = 0, page_size: int = max_paging_size,
                                    starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                    output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data structure metadata elements that contain the search string.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing : false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_data_structures_w_body(body, start_from, page_size, starts_with, ends_with, ignore_case,
                                                    output_format))
        return response

    async def _async_find_data_structures(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                                          starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                          output_format: str = "DICT") -> list | str:
        """ Find the list of data structure metadata elements that contain the search string.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - one of "DICT", "MERMAID" or "JSON"

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        """

        body = {"filter": filter}

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", str(starts_with).lower),
             ("endsWith", str(ends_with).lower()), ("ignoreCase", str(ignore_case).lower()), ])

        url = (f"{base_path(self, self.view_server)}/data-structures/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            return self.generate_data_structure_output(elements, filter, output_format)
        return elements

    def find_data_structures(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                             starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                             output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data structure metadata elements that contain the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            output_format: str, default = "DICT"
            -  one of "DICT", "MERMAID" or "JSON"
        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
            self._async_find_data_structures(filter, start_from, page_size, starts_with, ends_with, ignore_case,
                                             output_format))
        return response

    async def _async_get_data_structures_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                                 page_size: int = max_paging_size,
                                                 output_format: str = "DICT") -> list | str:
        """ Get the list of data structure metadata elements with a matching name to the search string filter.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties for the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - one of "DICT", "MERMAID" or "JSON"
        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
        if body is None:
            body = {"filter": filter}

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size), ])

        url = (f"{base_path(self, self.view_server)}/data-structures/by-name"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_structure_output(elements, filter, output_format)
        return elements

    def get_data_structures_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                    page_size: int = max_paging_size, output_format: str = "DICT") -> list | str:
        """ Get the list of data structure metadata elements with a matching name to the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties for the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
         - one of "DICT", "MERMAID" or "JSON"

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
            self._async_get_data_structures_by_name(filter, body, start_from, page_size, output_format))
        return response

    async def _async_get_data_structures_by_guid(self, guid: str, body: dict = None,
                                                 output_format: str = "DICT") -> list | str:
        """ Get the  data structure metadata elements for the specified GUID.
            Async version.

        Parameters
        ----------
        guid: str
            - unique identifier of the data structure metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
         - one of "DICT", "MERMAID" or "JSON"
        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-structures/{guid}/retrieve")
        if body:
            response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response: Response = await self._async_make_request("POST", url)

        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(element) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_structure_output(element, filter, output_format)
        return element

    def get_data_structures_by_guid(self, guid: str, body: str = None, output_format: str = "DICT") -> list | str:
        """ Get the data structure metadata element with the specified unique identifier..

        Parameters
        ----------
        guid: str
            - unique identifier of the data structure metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
         - one of "DICT", "MERMAID" or "JSON"
        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_data_structures_by_guid(guid, body, output_format))
        return response

    #
    # Work with Data Fields
    # https://egeria-project.org/concepts/data-class
    #
    async def _async_create_data_field(self, body: dict) -> str:
        """
        Create a new data class with parameters defined in the body. Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
        Sample bodies:

        {
          "class" : "NewDataFieldRequestBody",
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
            "class" : "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": ["alias1", "alias2"],
            "isDeprecated": false,
            "isNullable" : false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
    or
       {
          "properties": {
            "class": "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": [
              "alias1",
              "alias2"
            ],
            "namePatterns": [],
            "isDeprecated": false,
            "isNullable": false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            }
          }
        }


        """

        url = f"{base_path(self, self.view_server)}/data-fields"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_field(self, body: dict) -> str:
        """
        Create a new data class with parameters defined in the body..

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        Sample bodies:

        {
          "class" : "NewDataFieldRequestBody",
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
            "class" : "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": ["alias1", "alias2"],
            "isDeprecated": false,
            "isNullable" : false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
    or
       {
          "properties": {
            "class": "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": [
              "alias1",
              "alias2"
            ],
            "namePatterns": [],
            "isDeprecated": false,
            "isNullable": false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            }
          }
        }


        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_data_field(body))
        return response

    async def _async_create_data_field_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data class using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
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

        url = f"{base_path(self, self.view_server)}/data-fields/from-template"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_field_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data class using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
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
        response = loop.run_until_complete(self._async_create_data_field_from_template(body))
        return response

    async def _async_update_data_field(self, data_field_guid: str, body: dict,
                                       replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data class. Async version.

        Parameters
        ----------
        data_field_guid: str
            - the GUID of the data class to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
        replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
             will be replaced.
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

        Note
        ----

        Full sample body:

       {
          "class" : "UpdateDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": ["alias1", "alias2"],
            "namePatterns": [],
            "isDeprecated": false,
            "isNullable" : false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        replace_all_properties_s = str(replace_all_properties).lower()

        url = (f"{base_path(self, self.view_server)}/data-fields/{data_field_guid}/update?"
               f"replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_data_field(self, data_field_guid: str, body: dict.get, replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data class.

        Parameters
        ----------
        data_field_guid: str
            - the GUID of the data class to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
        replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
              will be replaced.
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

        Note
        ----

        Full sample body:

       {
          "class" : "UpdateDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataFieldProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "namespace": "",
            "description": "add description here",
            "versionIdentifier": "add version",
            "aliases": ["alias1", "alias2"],
            "namePatterns": [],
            "isDeprecated": false,
            "isNullable" : false,
            "defaultValue": "",
            "dataType": "",
            "minimumLength": 0,
            "length": 0,
            "precision": 0,
            "orderedValues": false,
            "sortOrder": "UNSORTED",
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
        loop.run_until_complete(self._async_update_data_field(data_field_guid, body, replace_all_properties))

    async def _async_link_nested_data_field(self, parent_data_field_guid: str, nested_data_field_guid: str,
                                            body: dict = None) -> None:
        """
        Connect a nested data field to a data field. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_field_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        nested_data_field_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

        {
          "class" : "MemberDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "MemberDataFieldProperties",
            "dataFieldPosition": 0,
            "minCardinality": 0,
            "maxCardinality": 0,
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-fields/{parent_data_field_guid}"
               f"/nested-data-fields/{nested_data_field_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_nested_data_field(self, parent_data_field_guid: str, nested_data_field_guid: str,
                               body: dict = None) -> None:
        """
        Connect a nested data class to a data class. Request body is optional.

        Parameters
        ----------
        parent_data_field_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        nested_data_field_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

        {
          "class" : "MemberDataFieldRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "MemberDataFieldProperties",
            "dataFieldPosition": 0,
            "minCardinality": 0,
            "maxCardinality": 0,
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_nested_data_field(parent_data_field_guid, nested_data_field_guid, body))

    async def _async_detach_nested_data_field(self, parent_data_field_guid: str, nested_data_field_guid: str,
                                              body: dict = None) -> None:
        """
        Detach a nested data class from a data class. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_field_guid: str
            - the GUID of the parent data class the data class will be detached from..
        nested_data_field_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-fields/{parent_data_field_guid}"
               f"/member-data-fields/{nested_data_field_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_nested_data_field(self, parent_data_field_guid: str, nested_data_field_guid: str,
                                 body: dict = None) -> None:
        """
        Detach a nested data class from a data class. Request body is optional.

        Parameters
        ----------
        parent_data_field_guid: str
            - the GUID of the parent data structure the data class will be detached fromo.
        nested_data_field_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

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
            self._async_detach_nested_data_field(parent_data_field_guid, nested_data_field_guid, body))

    async def _async_delete_data_field(self, data_field_guid: str, body: dict = None, cascade:bool = False) -> None:
        """
        Delete a data class. Request body is optional. Async version.

        Parameters
        ----------
        data_field_guid: str
            - the GUID of the data class to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then all child data fields will be deleted as well.


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

        Note
        ----

        Full sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """
        cascade_s = str(cascade).lower()
        url = f"{base_path(self, self.view_server)}/data-fields/{data_field_guid}/delete?cascadedDelete={cascade_s}"

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def delete_data_field(self, data_field_guid: str, body: dict = None, cascade:bool = False) -> None:
        """
        Delete a data class. Request body is optional.

        Parameters
        ----------
        data_field_guid: str
            - the GUID of the data class the data class to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then all child data fields will be deleted as well.


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

        Note
        ----

        Full sample body:

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
        loop.run_until_complete(self._async_delete_data_field(data_field_guid, body, cascade))

    async def _async_find_all_data_fields(self, start_from: int = 0, page_size: int = max_paging_size,
                                          output_format: str = "DICT") -> list | str:
        """Returns a list of all known data fields. Async version.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict elements with the results.

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
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", 'false'), ("endsWith", 'false'),
             ("ignoreCase", 'true')])

        url = (f"{base_path(self, self.view_server)}/data-fields/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_field_output(elements, filter, output_format)
        return elements

    def find_all_data_fields(self, start_from: int = 0, page_size: int = max_paging_size,
                             output_format: str = "DICT") -> list | str:
        """ Returns a list of all known data fields.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict elements with the results.

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
        response = loop.run_until_complete(self._async_find_all_data_fields(start_from, page_size, output_format))
        return response

    async def _async_find_data_fields_w_body(self, body: dict, start_from: int = 0, page_size: int = max_paging_size,
                                             starts_with: bool = True, ends_with: bool = False,
                                             ignore_case: bool = True, output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data class metadata elements that contain the search string.
            Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing : false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

        """
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with_s),
             ("endsWith", ends_with_s), ("ignoreCase", ignore_case_s), ])

        url = (f"{base_path(self, self.view_server)}/data-fields/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_field_output(elements, filter, output_format)
        return elements

    def find_data_fields_w_body(self, body: dict, start_from: int = 0, page_size: int = max_paging_size,
                                starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data class metadata elements that contain the search string.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing : false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_data_fields_w_body(body, start_from, page_size, starts_with, ends_with, ignore_case,
                                                output_format))
        return response

    async def _async_find_data_fields(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                                      starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                      output_format: str = "DICT") -> list | str:
        """ Find the list of data class elements that contain the search string.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        """

        body = {"filter": filter}

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", str(starts_with).lower),
             ("endsWith", str(ends_with).lower()), ("ignoreCase", str(ignore_case).lower()), ])

        url = (f"{base_path(self, self.view_server)}/data-fields/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_field_output(elements, filter, output_format)
        return elements

    def find_data_fields(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                         starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                         output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data fields elements that contain the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
            self._async_find_data_fields(filter, start_from, page_size, starts_with, ends_with, ignore_case,
                                         output_format))
        return response

    async def _async_get_data_fields_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                             page_size: int = max_paging_size,
                                             output_format: str = "DICT") -> list | str:
        """ Get the list of data class metadata elements with a matching name to the search string filter.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties to use in the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
        if body is None:
            body = {"filter": filter}

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size), ])

        url = (f"{base_path(self, self.view_server)}/data-fields/by-name"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_field_output(elements, filter, output_format)
        return elements

    def get_data_fields_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                page_size: int = max_paging_size, output_format: str = "DICT") -> list | str:
        """ Get the list of data class elements with a matching name to the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties to use in the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
            self._async_get_data_fields_by_name(filter, body, start_from, page_size, output_format))
        return response

    async def _async_get_data_field_by_guid(self, guid: str, body: dict = None,
                                            output_format: str = "DICT") -> list | str:
        """ Get the  data class elements for the specified GUID.
            Async version.

        Parameters
        ----------
        guid: str
            - unique identifier of the data class metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-fields/{guid}/retrieve")
        if body:
            response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response: Response = await self._async_make_request("POST", url)

        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_field_output(elements, filter, output_format)
        return elements

    def get_data_field_by_guid(self, guid: str, body: str = None, output_format: str = "DICT") -> list | str:
        """ Get the  data structure metadata element with the specified unique identifier..

        Parameters
        ----------
        guid: str
            - unique identifier of the data structure metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_data_field_by_guid(guid, body, output_format))
        return response

    ###
    # =====================================================================================================================
    # Work with Data Classes
    # https://egeria-project.org/concepts/data-class
    #
    #
    async def _async_create_data_class(self, body: dict) -> str:
        """
        Create a new data class with parameters defined in the body. Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
        Sample bodies:

        {
          "class" : "NewDataClassRequestBody",
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
            "class" : "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": ["name1", "name2"],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns" : [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        or
        {
          "properties": {
            "class": "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": [
              "name1",
              "name2"
            ],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns": [],
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            }
          }
        }

        """

        url = f"{base_path(self, self.view_server)}/data-classes"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_class(self, body: dict) -> str:
        """
        Create a new data class with parameters defined in the body..

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----

        {
          "class" : "NewDataClassRequestBody",
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
            "class" : "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": ["name1", "name2"],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns" : [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        or
        {
          "properties": {
            "class": "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": [
              "name1",
              "name2"
            ],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns": [],
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            }
          }
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_data_class(body))
        return response

    async def _async_create_data_class_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data class using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
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

        url = f"{base_path(self, self.view_server)}/data-classes/from-template"

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_class_from_template(self, body: dict) -> str:
        """
        Create a new metadata element to represent a data class using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict
            - a dictionary containing the properties of the data class to be created.

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note
        ----
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
        response = loop.run_until_complete(self._async_create_data_class_from_template(body))
        return response

    async def _async_update_data_class(self, data_class_guid: str, body: dict,
                                       replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data class. Async version.

        Parameters
        ----------
        data_class_guid: str
            - the GUID of the data class to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
        replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
             will be replaced.
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

        Note
        ----
        Full sample body:
        {
          "class" : "UpdateDataClassRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": ["name1", "name2"],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns" : [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        replace_all_properties_s = str(replace_all_properties).lower()

        url = (f"{base_path(self, self.view_server)}/data-class/{data_class_guid}/update?"
               f"replaceAllProperties={replace_all_properties_s}")

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_data_class(self, data_class_guid: str, body: dict.get, replace_all_properties: bool = False) -> None:
        """
        Update the properties of a data class.

        Parameters
        ----------
        data_class_guid: str
            - the GUID of the data class to be updated.
        body: dict
            - a dictionary containing the properties of the data structure to be created.
        replace_all_properties: bool, default = False
            - if true, then all properties will be replaced with the new ones. Otherwise, only the specified ones
              will be replaced.
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

        Note
        ----

        {
          "class" : "UpdateDataClassRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class" : "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": ["name1", "name2"],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": true,
            "isNullable": false,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns" : [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_data_class(data_class_guid, body, replace_all_properties))

    async def _async_link_nested_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                            body: dict = None) -> None:
        """
        Connect two data classes to show that one is used by the other when it is validating (typically a complex
        data item). Request body is optional. Async version.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        child_data_class_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-classes/{parent_data_class_guid}"
               f"/nested-data-classes/{child_data_class_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_nested_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                               body: dict = None) -> None:
        """
        Connect a nested data class to a data class. Request body is optional.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        child_data_class_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
        loop.run_until_complete(self._async_link_nested_data_class(parent_data_class_guid, child_data_class_guid, body))

    async def _async_detach_nested_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                              body: dict = None) -> None:
        """
        Detach two nested data classes from each other. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the data class will be detached from..
        child_data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-classes/{parent_data_class_guid}"
               f"/member-data-classes/{child_data_class_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_nested_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                 body: dict = None) -> None:
        """
        Detach two nested data classes from each other. Request body is optional.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data structure the data class will be detached fromo.
        child_data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

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
            self._async_detach_nested_data_class(parent_data_class_guid, child_data_class_guid, body))

    async def _async_link_specialist_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                                body: dict = None) -> None:
        """
        Connect two data classes to show that one provides a more specialist evaluation. Request body is optional.
        Async version.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        child_data_class_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-classes/{parent_data_class_guid}"
               f"/specialist-data-classes/{child_data_class_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_specialist_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                   body: dict = None) -> None:
        """
        Connect two data classes to show that one provides a more specialist evaluation. Request body is optional.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the nested data class will be connected to.
        child_data_class_guid: str
            - the GUID of the nested data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
            self._async_link_specialist_data_class(parent_data_class_guid, child_data_class_guid, body))

    async def _async_detach_specialist_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                                  body: dict = None) -> None:
        """
        Detach two data classes from each other. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data class the data class will be detached from..
        child_data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-classes/{parent_data_class_guid}"
               f"/specialist-data-classes/{child_data_class_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_specialist_data_class(self, parent_data_class_guid: str, child_data_class_guid: str,
                                     body: dict = None) -> None:
        """
        Detach two data classes from each other. Request body is optional.

        Parameters
        ----------
        parent_data_class_guid: str
            - the GUID of the parent data structure the data class will be detached from.
        child_data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Full sample body:

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
            self._async_detach_specialist_data_class(parent_data_class_guid, child_data_class_guid, body))

    async def _async_delete_data_class(self, data_class_guid: str, body: dict = None, cascade:bool= False) -> None:
        """
        Delete a data class. Request body is optional. Async version.

        Parameters
        ----------
        data_class_guid: str
            - the GUID of the data class to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then the delete cascades to dependents


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

        Note
        ----

        Full sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """
        cascade_s = str(cascade).lower()
        url = f"{base_path(self, self.view_server)}/data-classes/{data_class_guid}/delete?cascadedDelete={cascade_s}"

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def delete_data_class(self, data_class_guid: str, body: dict = None, cascade:bool= False) -> None:
        """
        Delete a data class. Request body is optional.

        Parameters
        ----------
        data_class_guid: str
            - the GUID of the data class the data class to delete.
        body: dict, optional
            - a dictionary containing additional properties.
        cascade: bool, optional
            - if True, then the delete cascades to dependents


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

        Note
        ----

        Full sample body:

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
        loop.run_until_complete(self._async_delete_data_class(data_class_guid, body, cascade))

    async def _async_find_all_data_classes(self, start_from: int = 0, page_size: int = max_paging_size,
                                           output_format: str = "DICT") -> list | str:
        """ Returns a list of all data classes. Async version.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict elements with the results.

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
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", 'false'), ("endsWith", 'false'),
             ("ignoreCase", 'true')])

        url = (f"{base_path(self, self.view_server)}/data-classes/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_class_output(elements, filter, output_format)
        return elements

    def find_all_data_classes(self, start_from: int = 0, page_size: int = max_paging_size,
                              output_format: str = "DICT") -> list | str:
        """ Returns a list of all data classes.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict elements with the results.

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
        response = loop.run_until_complete(self._async_find_all_data_classes(start_from, page_size, output_format))
        return response

    async def _async_find_data_classes_w_body(self, body: dict, start_from: int = 0, page_size: int = max_paging_size,
                                              starts_with: bool = True, ends_with: bool = False,
                                              ignore_case: bool = True, output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data class metadata elements that contain the search string.
            Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing : false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

        """
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", starts_with_s),
             ("endsWith", ends_with_s), ("ignoreCase", ignore_case_s), ])

        url = (f"{base_path(self, self.view_server)}/data-classes/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_class_output(elements, filter, output_format)
        return elements

    def find_data_classes_w_body(self, body: dict, start_from: int = 0, page_size: int = max_paging_size,
                                 starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                 output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data class metadata elements that contain the search string.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
              "class": "FilterRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing : false,
              "limitResultsByStatus": ["ACTIVE"],
              "sequencingOrder": "PROPERTY_ASCENDING",
              "sequencingProperty": "qualifiedName",
              "filter": ""
            }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_data_classes_w_body(body, start_from, page_size, starts_with, ends_with, ignore_case,
                                                 output_format))
        return response

    async def _async_find_data_classes(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                                       starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                                       output_format: str = "DICT") -> list | str:
        """ Find the list of data class elements that contain the search string.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        """

        body = {"filter": filter}

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ("startsWith", str(starts_with).lower),
             ("endsWith", str(ends_with).lower()), ("ignoreCase", str(ignore_case).lower()), ])

        url = (f"{base_path(self, self.view_server)}/data-classes/by-search-string"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_class_output(elements, filter, output_format)
        return elements

    def find_data_classes(self, filter: str, start_from: int = 0, page_size: int = max_paging_size,
                          starts_with: bool = True, ends_with: bool = False, ignore_case: bool = True,
                          output_format: str = "DICT") -> list | str:
        """ Retrieve the list of data fields elements that contain the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        starts_with: bool, default = True
            - if True, the search string filters from the beginning of the string.
        ends_with: bool, default = False
            - if True, the search string filters from the end of the string.
        ignore_case: bool, default = True
            - If True, the case of the search string is ignored.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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
            self._async_find_data_classes(filter, start_from, page_size, starts_with, ends_with, ignore_case,
                                          output_format))
        return response

    async def _async_get_data_classes_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                              page_size: int = max_paging_size,
                                              output_format: str = "DICT") -> list | str:
        """ Get the list of data class metadata elements with a matching name to the search string filter.
            Async version.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties to use in the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
        if body is None:
            body = {"filter": filter}

        possible_query_params = query_string([("startFrom", start_from), ("pageSize", page_size), ])

        url = (f"{base_path(self, self.view_server)}/data-classes/by-name"
               f"{possible_query_params}")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_class_output(elements, filter, output_format)
        return elements

    def get_data_classes_by_name(self, filter: str, body: dict = None, start_from: int = 0,
                                 page_size: int = max_paging_size, output_format: str = "DICT") -> list | str:
        """ Get the list of data class elements with a matching name to the search string filter.

        Parameters
        ----------
        filter: str
            - search string to filter on.
        body: dict, optional
            - a dictionary containing additional properties to use in the request.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".


        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict with the results.

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
            self._async_get_data_classes_by_name(filter, body, start_from, page_size, output_format))
        return response

    async def _async_get_data_class_by_guid(self, guid: str, body: dict = None,
                                            output_format: str = "DICT") -> list | str:
        """ Get the  data class elements for the specified GUID.
            Async version.

        Parameters
        ----------
        guid: str
            - unique identifier of the data class metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-classes/{guid}/retrieve")
        if body:
            response: Response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response: Response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return other representations
            return self.generate_data_class_output(elements, filter, output_format)
        return elements

    def get_data_class_by_guid(self, guid: str, body: str = None, output_format: str = "DICT") -> list | str:
        """ Get the  data structure metadata element with the specified unique identifier..

        Parameters
        ----------
        guid: str
            - unique identifier of the data structure metadata element.
        body: dict, optional
            - optional request body.
        output_format: str, default = "DICT"
            - output format of the data structure. Possible values: "DICT", "JSON", "MERMAID".

        Returns
        -------
        [dict] | str
            Returns a string if no elements are found and a list of dict  with the results.

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

        Optional request body:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

    """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_data_class_by_guid(guid, body, output_format))
        return response

    ###
    # =====================================================================================================================
    # Assembling a data specification
    # https://egeria-project.org/concepts/data-specification
    #
    async def _async_link_data_class_definition(self, data_definition_guid: str, data_class_guid: str,
                                                body: dict = None) -> None:
        """
         Connect an element that is part of a data design to a data class to show that the data class should be used as
         the specification for the data values when interpreting the data definition. Request body is optional.
         Async version
        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition to link.
        data_class_guid: str
            - the GUID of the data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-definitions/{data_definition_guid}"
               f"/data-class-definition/{data_class_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_data_class_definition(self, data_definition_guid: str, data_class_guid: str, body: dict = None) -> None:
        """
         Connect an element that is part of a data design to a data class to show that the data class should be used as
         the specification for the data values when interpreting the data definition. Request body is optional.
         Async version
        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition to link.
        data_class_guid: str
            - the GUID of the data class to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
        loop.run_until_complete(self._async_link_data_class_definition(data_definition_guid, data_class_guid, body))

    async def _async_detach_data_class_definition(self, data_definition_guid: str, data_class_guid: str,
                                                  body: dict = None) -> None:
        """
        Detach a data definition from a data class. Request body is optional. Async version.

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition.
        data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-definitions/{data_definition_guid}"
               f"/data-class-definition/{data_class_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_data_class_definition(self, data_definition_guid: str, data_class_guid: str, body: dict = None) -> None:
        """
        Detach a data definition from a data class. Request body is optional.

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition.
        data_class_guid: str
            - the GUID of the data class to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
        loop.run_until_complete(self._async_detach_data_class_definition(data_definition_guid, data_class_guid, body))

    async def _async_link_semantic_definition(self, data_definition_guid: str, glossary_term_guid: str,
                                              body: dict = None) -> None:
        """
        Connect an element that is part of a data design to a glossary term to show that the term should be used as
        the semantic definition for the data values when interpreting the data definition. Request body is optional.
        Async version

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition to link.
        glossary_term_guid: str
            - the GUID of the glossary term to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/data-definitions/{data_definition_guid}"
               f"/semantic-definition/{glossary_term_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_semantic_definition(self, data_definition_guid: str, glossary_term_guid: str, body: dict = None) -> None:
        """
        Connect an element that is part of a data design to a glossary term to show that the term should be used as
        the semantic definition for the data values when interpreting the data definition. Request body is optional.
        Async version

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition to link.
        glossary_term_guid: str
            - the GUID of the glossary term to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
        loop.run_until_complete(self._async_link_semantic_definition(data_definition_guid, glossary_term_guid, body))

    async def _async_detach_semantic_definition(self, data_definition_guid: str, glossary_term_guid: str,
                                                body: dict = None) -> None:
        """
        Detach a data definition from a glossary term. Request body is optional. Async version.

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition.
        glossary_term_guid: str
            - the GUID of the glossary term to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

       {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """

        url = (f"{base_path(self, self.view_server)}/data-definitions/{data_definition_guid}"
               f"/semantic-definition/{glossary_term_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_semantic_definition(self, data_definition_guid: str, glossary_term_guid: str, body: dict = None) -> None:
        """
        Detach a data definition from a glossary term. Request body is optional.

        Parameters
        ----------
        data_definition_guid: str
            - the GUID of the data class definition.
        glossary_term_guid: str
            - the GUID of the glossary term to be disconnected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
        loop.run_until_complete(self._async_detach_semantic_definition(data_definition_guid, glossary_term_guid, body))

    async def _async_link_certification_type_to_data_structure(self, certification_type_guid: str,
                                                               data_structure_guid: str, body: dict = None) -> None:
        """
         Connect a certification type to a data structure to guide the survey action service (that checks the data
         quality of a data resource as part of certifying it with the supplied certification type) to the definition
         of the data structure to use as a specification of how the data should be both structured and (if data
        classes are attached to the associated data fields using the DataClassDefinition relationship) contain the
        valid values. Request body is optional.
         Async version

        Parameters
        ----------
        certification_type_guid: str
            - the GUID of the certification type to link.
        data_structure_guid: str
            - the GUID of the data structure to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/certification-types/{certification_type_guid}"
               f"/data-structure-definition/{data_structure_guid}/attach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def link_certification_type_to_data_structure(self, certification_type_guid: str, data_structure_guid: str,
                                                  body: dict = None) -> None:
        """
        Connect a certification type to a data structure to guide the survey action service (that checks the data
         quality of a data resource as part of certifying it with the supplied certification type) to the definition
         of the data structure to use as a specification of how the data should be both structured and (if data
        classes are attached to the associated data fields using the DataClassDefinition relationship) contain the
        valid values. Request body is optional.

        Parameters
        ----------
        certification_type_guid: str
            - the GUID of the certification type to link.
        data_structure_guid: str
            - the GUID of the data structure to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
            self._async_link_certification_type_to_data_structure(certification_type_guid, data_structure_guid, body))

    async def _async_detach_certification_type_from_data_structure(self, certification_type_guid: str,
                                                                   data_structure_guid: str, body: dict = None) -> None:
        """
        Detach a data structure from a certification type. Request body is optional. Async version.

        Parameters
        ----------
        certification_type_guid: str
            - the GUID of the certification type to link.
        data_structure_guid: str
            - the GUID of the data structure to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (f"{base_path(self, self.view_server)}/certification-stypes/{certification_type_guid}"
               f"/data-structure-definition/{data_structure_guid}/detach")

        if body is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_slimmer(body))

    def detach_certification_type_from_data_structure(self, certification_type_guid: str, data_structure_guid: str,
                                                      body: dict = None) -> None:
        """
        Detach a data structure from a certification type. Request body is optional.

        Parameters
        ----------
        certification_type_guid: str
            - the GUID of the certification type to link.
        data_structure_guid: str
            - the GUID of the data structure to be connected.
        body: dict, optional
            - a dictionary containing additional properties.

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

        Note
        ----

        Sample body:

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
            self._async_detach_certification_type_from_data_structure(certification_type_guid, data_structure_guid,
                                                                      body))

    def _extract_data_structure_properties(self, element: dict) -> dict:
        """
        Extract common properties from a data structure element.

        Args:
            element (dict): The data structure element

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element.get('properties', {})
        display_name = properties.get("displayName", "") or ""
        description = properties.get("description", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""
        namespace = properties.get("namespace", "") or ""
        version_id = properties.get("versionIdentifier", "") or ""

        return {
            'guid': guid, 'properties': properties, 'display_name': display_name, 'description': description,
            'qualified_name': qualified_name, 'namespace': namespace, 'version_identifier': version_id
            }

    def _extract_data_class_properties(self, element: dict) -> dict:
        """
        Extract common properties from a data class element.

        Args:
            element (dict): The data class element

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element.get('properties', {})
        display_name = properties.get("displayName", "") or ""
        description = properties.get("description", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""

        return {
            'guid': guid, 'properties': properties, 'display_name': display_name, 'description': description,
            'qualified_name': qualified_name
            }

    def _extract_data_field_properties(self, element: dict) -> dict:
        """
        Extract common properties from a data field element.

        Args:
            element (dict): The data field element

        Returns:
            dict: Dictionary of extracted properties
        """
        guid = element['elementHeader'].get("guid", None)
        properties = element.get('properties', {})
        display_name = properties.get("displayName", "") or ""
        description = properties.get("description", "") or ""
        qualified_name = properties.get("qualifiedName", "") or ""

        # Get data type from extendedProperties if available
        extended_properties = properties.get("extendedProperties", {})
        data_type = extended_properties.get("dataType", "")

        return {
            'guid': guid, 'properties': properties, 'display_name': display_name, 'description': description,
            'qualified_name': qualified_name, 'data_type': data_type
            }

    def generate_basic_structured_output(self, elements, filter, output_format) -> str | list:
        """
        Generate output in the specified format for the given elements.

        Args:
            elements: Dictionary or list of dictionaries containing element data
            filter: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        # Handle MERMAID and DICT formats using existing methods
        if output_format == "MERMAID":
            return extract_mermaid_only(elements)
        elif output_format == "DICT":
            return extract_basic_dict(elements)

        # For other formats (MD, FORM, REPORT, LIST), use generate_output
        elif output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [{'name': 'Name', 'key': 'display_name'}, {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'Description', 'key': 'description', 'format': True}]

            return generate_output(elements=elements, search_string=filter, entity_type="Data Element",
                output_format=output_format, extract_properties_func=self._extract_data_structure_properties,
                columns=columns if output_format == 'LIST' else None)

        # Default case
        return None

    def generate_data_structure_output(self, elements, filter, output_format) -> str | list:
        """
        Generate output for data structures in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing data structure elements
            filter: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        if output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [{'name': 'Structure Name', 'key': 'display_name'},
                {'name': 'Qualified Name', 'key': 'qualified_name'}, {'name': 'Namespace', 'key': 'namespace'},
                {'name': 'Version', 'key': 'version_identifier'},
                {'name': 'Description', 'key': 'description', 'format': True}]

            return generate_output(elements=elements, search_string=filter, entity_type="Data Structure",
                output_format=output_format, extract_properties_func=self._extract_data_structure_properties,
                columns=columns if output_format == 'LIST' else None)
        else:
            return self.generate_basic_structured_output(elements, filter, output_format)

    def generate_data_class_output(self, elements, filter, output_format) -> str | list:
        """
        Generate output for data classes in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing data class elements
            filter: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as string or list of dictionaries
        """
        if output_format in ["MD", "FORM", "REPORT", "LIST"]:
            # Define columns for LIST format
            columns = [{'name': 'Class Name', 'key': 'display_name'},
                {'name': 'Qualified Name', 'key': 'qualified_name'},
                {'name': 'Description', 'key': 'description', 'format': True}]

            return generate_output(elements=elements, search_string=filter, entity_type="Data Class",
                output_format=output_format, extract_properties_func=self._extract_data_class_properties,
                columns=columns if output_format == 'LIST' else None)
        else:
            return self.generate_basic_structured_output(elements, filter, output_format)

    def generate_data_field_output(self, elements, filter, output_format) -> str | list:
        """
        Generate output for data fields in the specified format.

        Args:
            elements: Dictionary or list of dictionaries containing data field elements
            filter: The search string used to find the elements
            output_format: The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID)

        Returns:
            Formatted output as a string or list of dictionaries
        """
        if output_format in ["MD", "FORM", "REPORT", "LIST", "DICT"]:
            # Define columns for LIST format
            columns = [{'name': 'Field Name', 'key': 'display_name'},
                {'name': 'Qualified Name', 'key': 'qualified_name'}, {'name': 'Data Type', 'key': 'data_type'},
                {'name': 'Description', 'key': 'description', 'format': True}]

            return generate_output(elements=elements, search_string=filter, entity_type="Data Field",
                output_format=output_format, extract_properties_func=self._extract_data_field_properties,
                columns=columns if output_format == 'LIST' else None)
        else:
            return self.generate_basic_structured_output(elements, filter, output_format)


if __name__ == "__main__":
    print("Data Designer")

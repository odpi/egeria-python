"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the data-designer OMVS module.

[data-designer](https://egeria-project.org/services/omvs/data-designer/overview)

"""

import asyncio

from httpx import Response

from pyegeria.utils import body_slimmer
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import default_time_out, NO_ELEMENTS_FOUND



def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


"params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to the query string"


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/data-designer"


def process_related_element_list(
    response: Response, mermaid_only: bool, relationship_list: bool = False
) -> str | dict:
    """Process the result payload

    Parameters
    ----------
    response: Response
        - the response payload from the API call
    mermaid_only: bool
        - if true, only return the Mermaid graph
    relationship_list: bool
        - if True, look for "relationshipList" otherwise look for "relatedElementList"

    Returns
    -------

    """
    if relationship_list:
        elements = response.json().get("relationshipList", "No relationship list found")
    else:
        elements = response.json().get("relatedElementList", NO_ELEMENTS_FOUND)

    if isinstance(elements, str):
        return NO_ELEMENTS_FOUND
    if mermaid_only:
        return elements.get("mermaidGraph", "No mermaid graph found")

    el_list = elements.get("elementList", NO_ELEMENTS_FOUND)
    if isinstance(el_list, str):
        return el_list

    if len(el_list) == 0:
        return "No elements returned"
    return elements


class DataDesigner(Client):
    """DataDesigner is a class that extends the Client class. The Data Designer OMVS provides APIs for
      building specifications for data. This includes common data fields in a data dictionary, data specifications
      for a project and data classes for data quality validation.

    Attributes:

        view_server_name: str
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

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.metadata_explorer_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-designer"
        )
        Client.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )

    #
    #    Data Structures
    #

    async def _async_create_data_structure(
        self,
        name: str,
        description: str,
        qualified_name: str = None,
        namespace: str = None,
        version_id: str = None) -> str:
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
            "class" : "DataStructureProperties",
            "qualifiedName": qualified_name,
            "displayName": name,
            "description": description,
            "namespace": namespace,
            "versionIdentifier": version_id
          }
        }


        url = f"{base_path(self, self.view_server)}/data-structures"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure(
            self,
            name: str,
            description: str,
            qualified_name: str = None,
            namespace: str = None,
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
            self._async_create_data_structure(
                name,
                description,
                qualified_name,
                namespace,
                version_id,
            )
        )
        return response

    async def _async_create_data_structure_w_body(
            self,
            body: dict) -> str:
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

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
            )
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure_w_body(
            self,
            body: dict) -> str:
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
        response = loop.run_until_complete(
            self._async_create_data_structure_w_body(
                body,
                )
            )
        return response

    async def _async_create_data_structure_from_template(
            self,
            body: dict) -> str:
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

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
            )
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def create_data_structure_from_template(
            self,
            body: dict) -> str:
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
        response = loop.run_until_complete(
            self._async_create_data_structure_from_template(
                body,
                )
            )
        return response

    async def _async_update_data_structure_w_body(
            self,
            data_struct_guid: str,
            body: dict,
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

        await self._async_make_request(
            "POST", url, body_slimmer(body)
            )

    def update_data_structure_w_body(
            self,
            data_struct_guid: str,
            body: dict.get,
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
            self._async_update_data_structure_w_body(
                data_struct_guid,
                body,
                replace_all_properties
                )
            )

    async def _async_link_member_data_field(
            self,
            parent_data_struct_guid: str,
            member_data_field_guid: str,
            body: dict = None) -> None:
        """
        Connect a data structure to a data field. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data field will be connected to.
        member_data_field_guid: str
            - the GUID of the data field to be connected.
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
            await self._async_make_request(
                "POST", url
                )
        else:
            await self._async_make_request(
                "POST", url, body_slimmer(body)
                )

    def link_member_data_field(
            self,
            parent_data_struct_guid: str,
            member_data_field_guid: str,
            body: dict = None) -> None:
        """
        Connect a data structure to a data field. Request body is optional.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data field will be connected to.
        member_data_field_guid: str
            - the GUID of the data field to be connected.
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
            self._async_link_member_data_field(
                parent_data_struct_guid,
                member_data_field_guid,
                body
                )
            )

    async def _async_detach_member_data_field(
            self,
            parent_data_struct_guid: str,
            member_data_field_guid: str,
            body: dict = None) -> None:
        """
        Detach a data field from a data structure. Request body is optional. Async version.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data field will be detached from..
        member_data_field_guid: str
            - the GUID of the data field to be disconnected.
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
            await self._async_make_request(
                "POST", url
                )
        else:
            await self._async_make_request(
                "POST", url, body_slimmer(body)
                )

    def detach_member_data_field(
            self,
            parent_data_struct_guid: str,
            member_data_field_guid: str,
            body: dict = None) -> None:
        """
        Detach a data field from a data structure. Request body is optional.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data field will be detached fromo.
        member_data_field_guid: str
            - the GUID of the data field to be disconnected.
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
            self._async_detach_member_data_field(
                parent_data_struct_guid,
                member_data_field_guid,
                body
                )
            )

    async def _async_delete_data_structure(
            self,
            data_struct_guid: str,
            body: dict = None) -> None:
        """
        Delete a data structure. Request body is optional. Async version.

        Parameters
        ----------
       data_struct_guid: str
            - the GUID of the parent data structure to delete.
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

        url = f"{base_path(self, self.view_server)}/data-structures/{data_struct_guid}/delete"


        if body is None:
            await self._async_make_request(
                "POST", url
                )
        else:
            await self._async_make_request(
                "POST", url, body_slimmer(body)
                )


    def delete_data_structure(
            self,
            parent_data_struct_guid: str,
            member_data_field_guid: str,
            body: dict = None) -> None:
        """
        Delete a data structure. Request body is optional.

        Parameters
        ----------
        parent_data_struct_guid: str
            - the GUID of the parent data structure the data field will be detached fromo.
        member_data_field_guid: str
            - the GUID of the data field to be disconnected.
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
            self._async_detach_member_data_field(
                parent_data_struct_guid,
                member_data_field_guid,
                body
                )
            )


    async def _async_find_all_data_structures(
        self,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Returns a list of all known data structures. Async version.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.

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
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", 'false'),
                ("endsWith", 'false'),
                ("ignoreCase", 'true')
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/data-structures/by-search-string"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def find_all_data_structures(
            self,
            start_from: int = 0,
            page_size: int = max_paging_size,
            ) -> list | str:
        """ Returns a list of all known data structures.

        Parameters
        ----------
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.

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

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_all_data_structures(
               start_from,
               page_size
                )
            )
        return response


    async def _async_find_data_structures_w_body(
        self,
        body: dict,
        start_from: int = 0,
        page_size: int = max_paging_size,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True
    ) -> list | str:
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
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with_s),
                ("endsWith", ends_with_s),
                ("ignoreCase", ignore_case_s),
                ]
            )

        url = (
            f"{base_path(self, self.view_server)}/data-structures/by-search-string"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements


    def find_data_structures_w_body(
            self,
            body: dict,
            start_from: int = 0,
            page_size: int = max_paging_size,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True
            ) -> list | str:
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
            self._async_find_data_structures_w_body(
                body,
               start_from,
               page_size,
                starts_with,
                ends_with,
                ignore_case
                )
            )
        return response

    async def _async_find_data_structures(
            self,
            filter: str,
            start_from: int = 0,
            page_size: int = max_paging_size,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True
            ) -> list | str:
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

        body = { "filter": filter }
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with_s),
                ("endsWith", ends_with_s),
                ("ignoreCase", ignore_case_s),
                ]
            )

        url = (
            f"{base_path(self, self.view_server)}/data-structures/by-search-string"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
            )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def find_data_structures(
            self,
            filter: str,
            start_from: int = 0,
            page_size: int = max_paging_size,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True
            ) -> list | str:
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
            self._async_find_data_structures(
                filter,
                start_from,
                page_size,
                starts_with,
                ends_with,
                ignore_case
                )
            )
        return response




if __name__ == "__main__":
    print("Data Designer")

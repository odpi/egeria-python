"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage locations in Egeria.

"""

import asyncio
from typing import Optional

from pyegeria._server_client import ServerClient
from pyegeria.base_report_formats import get_report_spec_match
from pyegeria.base_report_formats import select_report_spec
from pyegeria.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, UpdateElementRequestBody,
                             NewRelationshipRequestBody, DeleteElementRequestBody, DeleteRelationshipRequestBody)
from pyegeria.output_formatter import generate_output, populate_columns_from_properties, \
    _extract_referenceable_properties, get_required_relationships
from pyegeria.utils import dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from loguru import logger


class Location(ServerClient):
    """
    Manage Locations in Egeria..

    This client provides asynchronous and synchronous helpers to create, update, search,
    and relate Location elements and their subtypes (Campaign, StudyProject, Task, PersonalProject).

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
    - Most high-level list/report methods accept an `output_format` and an optional `report_spec` and
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
        self.ref_location_command_base: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/location-arena"
        )
        self.url_marker = 'locations'
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    @dynamic_catch
    async def _async_create_location(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new Location. Async version.

        Parameters
        ----------

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the Location to create.
        Returns
        -------
        str - the guid of the created Location

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example body:
        {
          "class" : "NewElementRequestBody",
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
          "properties": {
            "class" : "LocationProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add category here",
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

        url = f"{self.ref_location_command_base}/locations"
        return await self._async_create_element_body_request(url, ["LocationProperties"], body)

    @dynamic_catch
    def create_location(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new Location.

        Parameters
        ----------

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the Location to create.
        Returns
        -------
        str - the guid of the created Location

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example body:
        {
          "class" : "NewElementRequestBody",
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
          "properties": {
            "class" : "LocationProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add category here",
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

        return asyncio.get_event_loop().run_until_complete(self._async_create_location(body))

    #######

    @dynamic_catch
    async def _async_create_location_from_template(self, body: TemplateRequestBody | dict) -> str:
        """ Create a new metadata element to represent a Location using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async version.
    
        Parameters
        ----------
        body: dict
            A dict representing the details of the Location to create.
    
        Returns
        -------
        str - the guid of the created Location
    
        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        PyegeriaUnAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    
        Notes
        -----
        JSON Structure looks like:
    
        {
          "class": "TemplateRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "templateGUID": "template GUID",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "propertyName" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                "primitiveValue" : "value of property"
              }
            }
          },
          "placeholderPropertyValues" : {
            "placeholderProperty1Name" : "property1Value",
            "placeholderProperty2Name" : "property2Value"
          }
        }
    
        """
        url = f"{self.ref_location_command_base}/locations/from-template"

        return await self._async_create_element_from_template("POST", url, body)

    @dynamic_catch
    def create_location_from_template(self, body: dict) -> str:
        """ Create a new metadata element to represent a Location using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict
            A dict representing the details of the Location to create.

        Returns
        -------
        str - the guid of the created Location

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        PyegeriaUnAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:

        {
          "class": "TemplateRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "templateGUID": "template GUID",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "propertyName" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                "primitiveValue" : "value of property"
              }
            }
          },
          "placeholderPropertyValues" : {
            "placeholderProperty1Name" : "property1Value",
            "placeholderProperty2Name" : "property2Value"
          }
        }

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_location_from_template(body))
        return resp

    @dynamic_catch
    async def _async_update_location(self, location_guid: str,
                                     body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an Location.
            Collections: https://egeria-project.org/concepts/location
    
            Async version.
        Parameters
        ----------
        location_guid: str
            The guid of the Location to update.
    
        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the Location to create.

        Returns
        -------
        None
    
        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaUnAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    
        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "LocationProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "category": "add category here",
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

        url = f"{self.ref_location_command_base}/locations/{location_guid}/update"
        await self._async_update_element_body_request(url, ["LocationProperties"], body)

    @dynamic_catch
    def update_location(self, location_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an Location.
            Collections: https://egeria-project.org/concepts/location

        Parameters
        ----------
        location_guid: str
            The guid of the Location to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the Location to create.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaUnAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the Location here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_location(location_guid, body))

    @dynamic_catch
    async def _async_link_peer_locations(self, location1_guid: str, location2_guid: str,
                                         body: dict | NewRelationshipRequestBody = None) -> None:
        """ Link Peer Locations.
            Async version.
    
        Parameters
        ----------
        location1_guid: str
            The unique identifier of the first location.
        location2_guid: str
            The unique identifier of the second location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
        Returns
        -------
        Nothing
    
        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    
        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "AdjacentLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = f"{self.ref_location_command_base}/locations/{location1_guid}/adjacent-locations/{location2_guid}/attach"
        await self._async_new_relationship_request(url, ["AdjacentLocationProperties"], body)
        logger.info(f"Linking location {location1_guid} to location {location2_guid}")

    @dynamic_catch
    def link_peer_locations(self, location1_guid: str, location2_guid: str,
                            body: dict | NewRelationshipRequestBody = None):
        """ Link Peer Locations.

        Parameters
        ----------
        location1_guid: str
            The unique identifier of the first location.
        location2_guid: str
            The unique identifier of the second location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "AdjacentLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_peer_locations(location1_guid, location2_guid, body))

    @dynamic_catch
    async def _async_detach_peer_locations(self, location1_guid: str, location2_guid: str,
                                           body: dict | DeleteRelationshipRequestBody = None) -> None:
        """ Unlink peer locations. Async version.
    
        Parameters
        ----------
        location1_guid: str
            The unique identifier of the subscriber.
        location2_guid: str
            The unique identifier of the subscription.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
        Returns
        -------
        Nothing
    
        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    
        Notes
        -----
        JSON Structure looks like:
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
        url = (f"{self.command_root}/elements/{location1_guid}/locations/{location2_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.info(f"Unlink {location1_guid} from location {location2_guid}")

    def detach_peer_locations(self, location1_guid: str, location2_guid: str,
                              body: dict | DeleteRelationshipRequestBody = None):
        """ Unlink peer locations.

        Parameters
        ----------
        location1_guid: str
            The unique identifier of the subscriber.
        location2_guid: str
            The unique identifier of the subscription.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_peer_locations(location1_guid, location2_guid, body))

    @dynamic_catch
    async def _async_link_nested_location(self, location_guid: str, nested_location_guid: str,
                                          body: dict | NewRelationshipRequestBody = None) -> None:
        """ AAttach a super location to a nested location.
            Async version.

        Parameters
        ----------
        location_guid: str
            The unique identifier of the location.
        nested_location_guid: str
            The identifier of the nested location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "NestedLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = f"{self.ref_location_command_base}/locations/{location_guid}/nested-locations/{nested_location_guid}/attach"
        await self._async_new_relationship_request(url, ["NestedLocationProperties"], body)
        logger.info(f"Linking element {location_guid} to nested location  {nested_location_guid}")

    @dynamic_catch
    def link_nested_location(self, location_guid: str, nested_location_guid: str,
                             body: dict | NewRelationshipRequestBody = None):
        """ AAttach a super location to a nested location.

        Parameters
        ----------
        location_guid: str
            The unique identifier of the location.
        nested_location_guid: str
            The identifier of the nested location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "NestedLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_nested_location(location_guid, nested_location_guid, body))

    @dynamic_catch
    async def _async_detach_nested_location(self, location_guid: str, nested_location_guid: str,
                                            body: dict | DeleteRelationshipRequestBody = None) -> None:
        """ Detach a nested location from a location. Async version.

        Parameters
        ----------
        location_guid: str
            The unique identifier of the location.
        nested_location_guid: str
            The unique identifier of the nested location.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
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
        url = (
            f"{self.ref_location_command_base}/locations{location_guid}/nested-locations/{nested_location_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.info(f"Detached location {location_guid} from nested location {nested_location_guid}")

    def detach_nested_location(self, location_guid: str, nested_location_guid: str,
                               body: dict | DeleteRelationshipRequestBody = None):
        """ Detach a nested location from a location.

        Parameters
        ----------
        location_guid: str
            The unique identifier of the location.
        nested_location_guid: str
            The unique identifier of the nested location.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_nested_location(location_guid, nested_location_guid, body))

    @dynamic_catch
    async def _async_link_known_location(self, element_guid: str, location_guid: str,
                                         body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an element to its location.
            Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        location_guid: str
            The identifier of the location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "KnownLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = f"{self.ref_location_command_base}elements/{element_guid}/known-locations/{location_guid}/attach"
        await self._async_new_relationship_request(url, ["KnownLocationProperties"], body)
        logger.info(f"Linking element {element_guid} to location {location_guid}")

    @dynamic_catch
    def link_known_location(self, element_guid: str, location_guid: str,
                            body: dict | NewRelationshipRequestBody = None):
        """ Attach an element to its location.
            Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        location_guid: str
            The identifier of the location.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "KnownLocationProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_known_location(element_guid, location_guid, body))

    @dynamic_catch
    async def _async_detach_known_location(self, element_guid: str, location_guid: str,
                                           body: dict | DeleteRelationshipRequestBody = None) -> None:
        """ Detach an element from an known location. Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        location_guid: str
            The unique identifier of the location.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
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
        url = (f"{self.command_root}/location_arena/elements/{element_guid}/known-locations/{location_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.info(f"Detached element {element_guid} from location {location_guid}")

    def detach_known_location(self, element_guid: str, location_guid: str,
                              body: dict | DeleteRelationshipRequestBody = None):
        """ Detach an element from an known location. Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        location_guid: str
            The unique identifier of the location.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_known_location(element_guid, location_guid, body))

    @dynamic_catch
    async def _async_delete_location(self, location_guid: str,
                                     body: dict | DeleteRelationshipRequestBody = None,
                                     cascade: bool = False) -> None:
        """ Delete a location. Async Version.
    
        Parameters
        ----------
        location_guid: str
            The guid of the location to delete.
    
        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.
    
        body: dict DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
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
          "class": "DeleteRelationshipRequestBody",
          "cascadeDelete": false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.ref_location_command_base}/locations/{location_guid}/delete"

        await self._async_delete_element_request(url, body, cascade)
        logger.info(f"Deleted location {location_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_location(self, location_guid: str, body: dict | DeleteElementRequestBody = None,
                        cascade: bool = False) -> None:
        """ Delete a location.

        Parameters
        ----------
        location_guid: str
            The guid of the location to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRelationshipRequestBody",
          "cascadeDelete": false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_location(location_guid, body, cascade))

    @dynamic_catch
    async def _async_find_locations(self, search_string: str = "*", classification_names: list[str] = None,
                                    metadata_element_subtypes: list[str] = None, starts_with: bool = True,
                                    ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                    page_size: int = 0, output_format: str = 'JSON',
                                    report_spec: str | dict = "Referenceable",
                                    body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of location metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all locations (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all metadata element types are returned.
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
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.ref_location_command_base}/locations/by-search-string"
        response = await self._async_find_request(url, _type="Location", _gen_output=self._generate_location_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    @dynamic_catch
    def find_locations(self, search_string: str = '*', classification_names: str = None,
                       metadata_element_subtypes: list[str] = None, starts_with: bool = True,
                       ends_with: bool = False, ignore_case: bool = False,
                       start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                       report_spec: str | dict = "ExternalReference",
                       body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of location metadata elements that contain the search string.

          Parameters
          ----------
          search_string: str
              Search string to match against - None or '*' indicate match against all locations (may be filtered by
              classification).
          classification_names: list[str], optional, default=None
              A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
              then all classifications are returned.
          metadata_element_subtypes: list[str], optional, default=None
              A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
              then all metadata element types are returned.
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
          output_format: str, default = "JSON"
              - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
          report_spec: str | dict , optional, default = None
              - The desired output columns/fields to include.
          body: dict | SearchStringRequestBody, optional, default = None
              - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

          Returns
          -------
          List | str

          Output depends on the output format specified.

          Raises
          ------

          ValidationError
            If the client passes incorrect parameters on the request that don't conform to the data model.
          PyegeriaException
            Issues raised in communicating or server side processing.
          NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

          """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_locations(search_string, classification_names, metadata_element_subtypes, starts_with,
                                       ends_with, ignore_case, start_from, page_size, output_format, report_spec, body))

    @dynamic_catch
    async def _async_get_locations_by_name(self, filter_string: str = None,
                                           classification_names: list[str] = None,
                                           body: dict | FilterRequestBody = None,
                                           start_from: int = 0, page_size: int = 0,
                                           output_format: str = 'JSON',
                                           report_spec: str | dict = "Locations") -> list | str:
        """ Returns the list of Locations with a particular name. Async version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching locations.
            classification_names: list[str], optional, default = None
                type of collection to filter by - e.g., DataDict, Folder, Root
            body: dict, optional, default = None
                Provides, a full request body. If specified, the body supercedes the name parameter.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            report_spec: dict , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A list of collections match matching the name. Returns a string if none found.

            Raises
            ------

            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
        """
        url = f"{self.ref_location_command_base}/locations/by-name"
        response = await self._async_get_name_request(url, _type="ExternalReference",
                                                      _gen_output=self._generate_location_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    def get_locations_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                              body: dict | FilterRequestBody = None,
                              start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                              report_spec: str | dict = "Locations") -> list | str:
        """ Returns the list of Locations with a particular name.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching locations.
            classification_names: list[str], optional, default = None
                type of collection to filter by - e.g., DataDict, Folder, Root
            body: dict, optional, default = None
                Provides, a full request body. If specified, the body supercedes the name parameter.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            report_spec: dict , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A list of collections match matching the name. Returns a string if none found.

            Raises
            ------

            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_locations_by_name(filter_string, classification_names, body, start_from, page_size,
                                              output_format, report_spec))

    @dynamic_catch
    async def _async_get_location_by_guid(self, location_guid: str, element_type: str = None,
                                          body: dict | GetRequestBody = None, output_format: str = 'JSON',
                                          report_spec: str | dict = "Locations") -> dict | str:
        """Return the properties of a specific location. Async version.

        Parameters
        ----------
        location_guid: str,
            unique identifier of the location to retrieve.
        element_type: str, default = None, optional
             type of element, etc.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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

        url = f"{self.ref_location_command_base}/locations/{location_guid}/retrieve"
        type = element_type if element_type else "Location"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_location_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_location_by_guid(self, location_guid: str, element_type: str = None, body: dict | GetRequestBody = None,
                             output_format: str = 'JSON', report_spec: str | dict = "Locations") -> dict | str:
        """Return the properties of a specific location. Async version.

        Parameters
        ----------
        location_guid: str,
            unique identifier of the location to retrieve.
        element_type: str, default = None, optional
             type of element, etc.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        ----
        Body sample:
        {
          "class": "FilterRequestBody",
          "filter": "Add name here",
          "startFrom": 0,
          "pageSize": 10,
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName"
        }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_location_by_guid(location_guid, element_type, body, output_format, report_spec))

    @dynamic_catch
    def _extract_location_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a location element and populate into the provided columns_struct.

        Args:
            element (dict): The location element
            columns_struct (dict): The columns structure to populate

        Returns:
            dict: columns_struct with column 'value' fields populated
        """
        # First, populate from element.properties using the utility
        col_data = populate_columns_from_properties(element, columns_struct)

        columns_list = col_data.get("formats", {}).get("attributes", [])

        # Populate header-derived values
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')

        # Derived/computed fields
        # locationCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("locationCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break

        # Populate requested relationship-based columns generically from top-level keys
        col_data = get_required_relationships(element, col_data)

        # Subject area classification
        subject_area = element.get('elementHeader', {}).get("subjectArea", "") or ""
        subj_val = ""
        if isinstance(subject_area, dict):
            subj_val = subject_area.get("classificationProperties", {}).get("subjectAreaName", "")
        for column in columns_list:
            if column.get('key') == 'subject_area':
                column['value'] = subj_val
                break

        # Mermaid graph
        mermaid_val = element.get('mermaidGraph', "") or ""
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = mermaid_val
                break

        logger.trace(f"Extracted/Populated columns: {col_data}")

        return col_data

    @dynamic_catch
    def _generate_location_output(self, elements: dict | list[dict], filter: Optional[str],
                                  element_type_name: Optional[str], output_format: str = "DICT",
                                  report_spec: dict | str = None) -> str | list[dict]:
        """ Generate output for locations in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of location
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if element_type_name is None:
            entity_type = "Locations"
        else:
            entity_type = element_type_name
        # First see if the user has specified an report_spec - either a label or a dict
        get_additional_props_func = None
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            elif isinstance(report_spec, dict):
                output_formats = get_report_spec_match(report_spec, output_format)

        # If no output_format was set, then use the element_type_name to lookup the output format
        elif element_type_name:
            output_formats = select_report_spec(element_type_name, output_format)
        else:
            # fallback to locations or entity type
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        if output_formats:
            get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
            if isinstance(get_additional_props_name, str):
                class_name, method_name = get_additional_props_name.split(".")
                if hasattr(self, method_name):
                    get_additional_props_func = getattr(self, method_name)

        logger.trace(f"Executing generate_location_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_location_properties,
            get_additional_props_func,
            output_formats,
        )

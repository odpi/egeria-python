"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage actor profiles, roles, and organizational structures.

"""

import asyncio
from typing import Optional, Any

from loguru import logger
from pydantic import HttpUrl

from pyegeria.view.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, NewAttachmentRequestBody,
                             UpdateElementRequestBody, NewRelationshipRequestBody,
                             DeleteElementRequestBody, DeleteRelationshipRequestBody, NewClassificationRequestBody,
                             DeleteClassificationRequestBody)
from pyegeria.view.output_formatter import (_extract_referenceable_properties, populate_columns_from_properties,
                                            get_required_relationships, materialize_egeria_summary)
from pyegeria.core.utils import dynamic_catch

ACTOR_PROFILE = ["ActorProfile", "PersonRole", "TeamRole", "Organization",
                 "UserIdentity","ITProfile"]

ACTOR_PROFILE_PROPERTIES_LIST = ["ActorProfileProperties", "PersonProperties", "TeamProperties",
                                 "OrganizationProperties", "ITProfileProperties"]

# ACTOR = ["Actor", "PersonRole", "TeamRole", "ITProfileRole"]
ACTOR_ROLE = ["ActorRole", "PersonRole", "TeamRole", "ITProfileRole", "TeamMember", "TeamLeader"]

ACTOR_ROLE_PROPERTIES_LIST = ["ActorRoleProperties", "PersonRoleProperties", "TeamRoleProperties",
                              "ITProfileRoleProperties", "GovernanceRoleProperties","SolutionActorRoleProperties"]

from pyegeria.core._server_client import ServerClient


class ActorManager(ServerClient):
    def _handle_optional_param(self, param: Any, default: Any) -> Any:
        """Handle Optional parameters by providing a default value if None."""
        return param if param is not None else default

    def _handle_optional_list(self, param: Optional[list[str]]) -> list[str]:
        """Handle Optional list parameters by providing an empty list if None."""
        return param if param is not None else []

    def _handle_optional_str(self, param: Optional[str]) -> str:
        """Handle Optional string parameters by providing an empty string if None."""
        return param if param is not None else ""

    def _handle_optional_dict(self, param: Optional[dict]) -> dict:
        """Handle Optional dict parameters by providing an empty dict if None."""
        return param if param is not None else {}
    """
    Create and manage actor profiles.

    Review the documentation on the website for more details.
    
    Attributes:

        server_name: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str
            An optional bearer token

    """

    def __init__(self, view_server: str = None, platform_url: str = None, user_id: str = None, user_pwd: Optional[str] = None, token: Optional[str] = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        # Handle Optional parameters for parent class
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/actor-manager")

    @dynamic_catch
    async def _async_create_actor_profile(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new actor profile. Async version.

        Parameters
        ----------

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor profile to create.
        Returns
        -------
        str - the guid of the created actor profile

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "effectiveFrom": "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "properties": {
            "class" : "ActorProfileProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
        }

    """

        url = f"{self.command_root}/actor-profiles"
        # Handle Optional body parameter
        body_to_use = body if body is not None else {}
        return await self._async_create_element_body_request(url, ACTOR_PROFILE_PROPERTIES_LIST, body_to_use)

    @dynamic_catch
    def create_actor_profile(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new actor profile.

               Parameters
               ----------
               body: dict | NewElementRequestBody, optional
                   A dict or NewElementRequestBody representing the details of the actor profile to create.
               Returns
               -------
               str - the guid of the created actor profile

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
               example:
               {
                 "class": "NewElementRequestBody",
                 "isOwnAnchor": true,
                 "effectiveFrom": "{{$isoTimestamp}}",
                 "effectiveTo": "{{$isoTimestamp}}",
                 "properties": {
                   "class" : "ActorProfileProperties",
                   "typeName" : "enter the type of the element",
                   "qualifiedName": "add unique name here",
                   "displayName": "add short name here",
                   "description": "add description here",
                   "additionalProperties": {
                     "property1" : "propertyValue1",
                     "property2" : "propertyValue2"
                   },
                   "extendedProperties": {
                     "property1" : "propertyValue1",
                     "property2" : "propertyValue2"
                   },
               }

           """

        return asyncio.get_event_loop().run_until_complete(self._async_create_actor_profile(body))

    #######

    @dynamic_catch
    async def _async_create_actor_profile_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent an actor profile using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async version.
    
        Parameters
        ----------
        body: dict
            A dict representing the details of the actor profile to create.
    
        Returns
        -------
        str - the guid of the created actor profile
    
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
        url = f"{self.command_root}/actor-profiles/from-template"

        # Handle Optional body parameter
        body_to_use = body if body is not None else {}
        return await self._async_create_element_from_template("POST", url, body_to_use)

    @dynamic_catch
    def create_actor_profile_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent an actor profile using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict
            A dict representing the details of the actor profile to create.

        Returns
        -------
        str - the guid of the created actor profile

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
        resp = loop.run_until_complete(self._async_create_actor_profile_from_template(body))
        return resp

    @dynamic_catch
    async def _async_update_actor_profile(self, actor_profile_guid: str,
                                          body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an actor profile.  Async version.
        
        Parameters
        ----------
        actor_profile_guid: str
            The guid of the actor profile to update.
    
        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor profile to create.

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
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ActorProfileProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
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

        url = (f"{self.command_root}/actor-profiles/{actor_profile_guid}/update")
        await self._async_update_element_body_request(url, ACTOR_PROFILE_PROPERTIES_LIST, body)

    @dynamic_catch
    def update_actor_profile(self, actor_profile_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an actor profile.

        Parameters
        ----------
        actor_profile_guid: str
            The guid of the actor profile to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor profile to create.

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
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ActorProfileProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
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

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_actor_profile(actor_profile_guid, body))

    @dynamic_catch
    async def _async_link_asset_to_profile(self, asset_guid: str, it_profile_guid: str,
                                           body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach an asset to an IT Profile. Async version.
    
        Parameters
        ----------
        asset_guid: str
            The unique identifier of the asset.
        it_profile_guid: str
            The identifier of the IT profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
        Returns
        -------
        Nothing
    
        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "RelationshipProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = url = (f"{self.command_root}/assets/{asset_guid}/it-profiles/{it_profile_guid}/attach")
        await self._async_new_relationship_request(url, ["RelationshipProperties"], body)
        logger.debug(f"Linking element {asset_guid} to IT Profile  {it_profile_guid}")

    @dynamic_catch
    def link_asset_to_profile(self, asset_guid: str, it_profile_guid: str,
                              body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach an asset to an IT Profile.
            Parameters
            ----------
            asset_guid: str
                The unique identifier of the asset.
            it_profile_guid: str
                The identifier of the IT profile.
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
                "class": "RelationshipProperties",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_asset_to_profile(asset_guid, it_profile_guid, body))

    @dynamic_catch
    async def _async_detach_asset_from_profile(self, asset_guid: str, it_profile_guid: str,
                                               body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach an asset from an IT Profile. Async version.
    
        Parameters
        ----------
        asset_guid: str
            The unique identifier of the asset.
        it_profile_guid: str
            The unique identifier of the IT profile.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
        url = (f"{self.command_root}/assets/{asset_guid}/it_profiles/{it_profile_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.debug(f"Detached asset {asset_guid} from it profile {it_profile_guid}")

    def detach_asset_from_profile(self, asset_guid: str, it_profile_guid: str,
                                  body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach an asset from an IT Profile. Async version.

            Parameters
            ----------
            asset_guid: str
                The unique identifier of the asset.
            it_profile_guid: str
                The unique identifier of the IT profile.
            body: dict | DeleteRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
        loop.run_until_complete(self._async_detach_asset_from_profile(asset_guid, it_profile_guid, body))

    @dynamic_catch
    async def _async_delete_actor_profile(self, actor_profile_guid: str,
                                          body: Optional[dict | DeleteElementRequestBody] = None,
                                          cascade: bool = False) -> None:
        """ Delete an actor profile. Async Version.
    
        Parameters
        ----------
        actor_profile_guid: str
            The guid of the actor profile to delete.
    
        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.
    
        body: dict | DeleteElementRequestBody, optional, default = None
            A structure representing the details of the relationship.
    
        Returns
        -------
        Nothing
    
        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        Notes
        _____
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.command_root}/actor-profiles/{actor_profile_guid}/delete"

        await self._async_delete_element_request(url, body, cascade)
        logger.debug(f"Deleted Actor Profile {actor_profile_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_actor_profile(self, actor_profile_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                             cascade: bool = False) -> None:
        """ Delete an actor profile. Async Version.

         Parameters
         ----------
         actor_profile_guid: str
             The guid of the actor profile to delete.

         cascade: bool, optional, defaults to True
             If true, a cascade delete is performed.

         body: dict | DeleteElementRequestBody, optional, default = None
             A structure representing the details of the relationship.

         Returns
         -------
         Nothing

         Raises
         ------
         PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

         Notes
         _____
         JSON Structure looks like:
         {
           "class": "DeleteRelationshipRequestBody",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime": "{{$isoTimestamp}}",
           "forLineage": false,
           "forDuplicateProcessing": false
         }
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_actor_profile(actor_profile_guid, body, cascade))

    @dynamic_catch
    async def _async_find_actor_profiles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ActorProfile",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor profile metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all profiles.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-profiles/by-search-string"))

        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        response = await self._async_find_request(
            url,
            _type="ActorProfile",
            _gen_output=self._generate_actor_profile_output,
            **params,
        )
        return response

    def find_actor_profiles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ActorProfile",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor profile metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str, default "*"
            Search string to match against - None or '*' indicate match against all profiles.
        starts_with : bool, default True
            Starts with the supplied string.
        ends_with : bool, default False
            Ends with the supplied string.
        ignore_case : bool, default True
            Ignore case when searching.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The subtypes to filter by.
        include_only_relationships : list[str], optional
            Only include these relationships.
        skip_relationships : list[str], optional
            Relationships to skip in the graph.
        graph_query_depth : int, optional
            The query depth for relationships.
        as_of_time : str, optional
            Historical time for the query.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 100.
        sequencing_order : str, optional
            Order for sequencing results.
        sequencing_property : str, optional
            Property to sequence by.
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        body : dict, optional
            Request body for additional parameters.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_actor_profiles(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_actor_profiles_by_name(
        self,
        name: str,
        metadata_element_type_name: str | None = "ActorProfile",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor profile metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str
            name to use to find matching profiles.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Profiles"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-profiles/by-name"))
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="ActorProfile",
            _gen_output=self._generate_actor_profile_output,
            **params,
        )

    def get_actor_profiles_by_name(
        self,
        name: str,
        metadata_element_type_name: str | None = "ActorProfile",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor profile metadata elements with a particular name.

        Parameters
        ----------
        name: str
            name to use to find matching profiles.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Profiles"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actor_profiles_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_actor_profile_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific actor profile. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the actor profile to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Profiles"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-profiles/{guid}/retrieve"))
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="ActorProfile",
            _gen_output=self._generate_actor_profile_output,
            **params,
        )

    def get_actor_profile_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Profiles",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific actor profile.

        Parameters
        ----------
        guid: str
            unique identifier of the actor profile to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Profiles"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actor_profile_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    def _extract_actor_profile_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a actor_profile element and populate into the provided columns_struct.

        Args:
            element (dict): The actor_profile element
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
        # actor_profileCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("actor_profileCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break

        # Handle assignedActors specifically for nested Team reports if present
        assigned_actors = element.get('assignedActors')
        if assigned_actors:
            for column in columns_list:
                if column.get('key') == 'assigned_actors' and column.get('detail_spec'):
                    # We want to provide a list of dicts for the detail spec
                    # Each dict should have role info and person info
                    flattened_actors = []
                    for aa in assigned_actors:
                        m_aa = materialize_egeria_summary(aa)
                        # aa might have sideLinks. Let's pull the first one's name out.
                        side_links = m_aa.get('sideLinks', [])
                        if side_links and len(side_links) > 0:
                            person = side_links[0]
                            m_aa['individual_name'] = person.get('name')
                            m_aa['individual_guid'] = person.get('guid')
                            m_aa['individual_type'] = person.get('type')
                            # Also copy some common props if they are not there
                            if not m_aa.get('displayName') and person.get('displayName'):
                                m_aa['displayName'] = person.get('displayName')
                        flattened_actors.append(m_aa)
                    column['value'] = flattened_actors
                    break

        # Handle sideLinks specifically for nested reports if present at root
        side_links = element.get('sideLinks')
        if side_links:
            for column in columns_list:
                if column.get('key') == 'side_links' and column.get('detail_spec'):
                    materialized = [materialize_egeria_summary(sl) for sl in side_links]
                    column['value'] = materialized
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

    def _generate_actor_profile_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                       element_type_name: Optional[str] = None, output_format: str = "DICT",
                                       report_spec: dict | str = "Actor-Profiles", **kwargs) -> str | list[dict]:
        """ Generate output for actor_profiles in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter_string (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of actor_profile
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.
                **kwargs: Additional arguments.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "ActorProfile",
            output_format=output_format,
            extract_properties_func=self._extract_actor_profile_properties,
            report_spec=report_spec,
            **kwargs
        )

    #
    # Actor Role
    #

    @dynamic_catch
    async def _async_create_actor_role(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new actor role. There are GovernanceRole, PersonRole, ITProfileRole, SolutionActorRole. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor role to create.
        Returns
        -------
        str - the guid of the created actor role

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
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "effectiveFrom": "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "properties": {
            "class" : "ActorRoleProperties",
            "typeName" : "enter the type of the element",
            "actorProfileGroups" : ["group1", "group2"],
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "scope" : "add scope here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
          }
        }

    """

        url = f"{self.command_root}/actor-roles"
        return await self._async_create_element_body_request(url, ACTOR_ROLE_PROPERTIES_LIST, body)

    @dynamic_catch
    def create_actor_role(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new actor role. There are GovernanceRole, PersonRole, ITProfileRole, SolutionActorRole.

           Parameters
           ----------
           body: dict | NewElementRequestBody, optional
               A dict or NewElementRequestBody representing the details of the actor role to create.
           Returns
           -------
           str - the guid of the created actor role

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
           example:
           {
             "class": "NewElementRequestBody",
             "isOwnAnchor": true,
             "effectiveFrom": "{{$isoTimestamp}}",
             "effectiveTo": "{{$isoTimestamp}}",
             "properties": {
               "class" : "ActorRoleProperties",
               "typeName" : "enter the type of the element",
               "actorProfileGroups" : ["group1", "group2"],
               "qualifiedName": "add unique name here",
               "displayName": "add short name here",
               "description": "add description here",
               "scope" : "add scope here",
               "additionalProperties": {
                 "property1" : "propertyValue1",
                 "property2" : "propertyValue2"
               },
               "extendedProperties": {
                 "property1" : "propertyValue1",
                 "property2" : "propertyValue2"
               },
             }
           }

           """

        return asyncio.get_event_loop().run_until_complete(self._async_create_actor_role(body))

    @dynamic_catch
    async def _async_create_actor_role_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent an actor role using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async version.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dict or TemplateRequestBody representing the details of the actor role to create.

        Returns
        -------
        str - the guid of the created actor role

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
        url = f"{self.command_root}/actor-roles/from-template"

        # Handle Optional body parameter
        body_to_use = body if body is not None else {}
        return await self._async_create_element_from_template("POST", url, body_to_use)

    @dynamic_catch
    def create_actor_role_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent an actor role using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dict or TemplateRequestBody representing the details of the actor role to create.

        Returns
        -------
            str - the guid of the created actor role

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
        resp = loop.run_until_complete(self._async_create_actor_role_from_template(body))
        return resp

    @dynamic_catch
    async def _async_update_actor_role(self, actor_role_guid: str,
                                       body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an actor role.
            Async version.
        Parameters
        ----------
        actor_role_guid: str
            The guid of the actor role to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor role to create.

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
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ActorRoleProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
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

        url = (f"{self.command_root}/actor-roles/{actor_role_guid}/update")
        await self._async_update_element_body_request(url, ACTOR_ROLE_PROPERTIES_LIST, body)

    @dynamic_catch
    def update_actor_role(self, actor_role_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an actor role.

        Parameters
        ----------
        actor_role_guid: str
            The guid of the actor role to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the actor role to create.

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
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ActorRoleProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
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

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_actor_role(actor_role_guid, body))

    @dynamic_catch
    async def _async_link_person_role_to_profile(self, person_role_guid: str, person_profile_guid: str,
                                                 body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach a person role to a person profile. Async version.

        Parameters
        ----------
        person_role_guid: str
            The unique identifier of the person role.
        person_profile_guid: str
            The identifier of the person profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "PersonRoleAppointmentProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = url = (
            f"{self.command_root}/actor-roles/{person_role_guid}/person-role-appointments/{person_profile_guid}/attach")
        await self._async_new_relationship_request(url, ["PersonAppointmentProperties"], body)
        logger.debug(f"Linking person role {person_role_guid} to Person Profile  {person_profile_guid}")

    @dynamic_catch
    def link_person_role_to_profile(self, person_role_guid: str, person_profile_guid: str,
                                    body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach a person role to a person profile.
            Parameters
            ----------
            person_role_guid: str
                The unique identifier of the person role.
            person_profile_guid: str
                The identifier of the person profile.
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
                "class": "PersonRoleAppointmentProperties",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_person_role_to_profile(person_role_guid, person_profile_guid, body))

    @dynamic_catch
    async def _async_detach_person_role_from_profile(self, person_role_guid: str, person_profile_guid: str,
                                                     body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach a person role from a person profile. Async version.

        Parameters
        ----------
        person_role_guid: str
            The unique identifier of the person role.
        person_profile_guid: str
            The unique identifier of the person profile.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            f"{self.command_root}/actor-roles/{person_role_guid}/person-role-appointments/{person_profile_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.debug(f"Detached Person Rolet {person_role_guid} from Person Profile {person_profile_guid}")

    def detach_person_role_from_profile(self, person_role_guid: str, person_profile_guid: str,
                                        body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach a person role from a person profile. Async version.

            Parameters
            ----------
            person_role_guid: str
                The unique identifier of the person role.
            person_profile_guid: str
                The unique identifier of the person profile.
            body: dict | DeleteRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
        loop.run_until_complete(
            self._async_detach_person_role_from_profile(person_role_guid, person_profile_guid, body))

    #
    @dynamic_catch
    async def _async_link_team_role_to_profile(self, team_role_guid: str, team_profile_guid: str,
                                               body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach a team role to a team profile. Async version.

        Parameters
        ----------
        team_role_guid: str
            The unique identifier of the team role.
        team_profile_guid: str
            The identifier of the team profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "TeamRoleAppointmentProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = url = (
            f"{self.command_root}/actor-roles/{team_role_guid}/team-role-appointments/{team_profile_guid}/attach")
        await self._async_new_relationship_request(url, ["TeamAppointmentProperties"], body)
        logger.debug(f"Linking team role {team_role_guid} to Team Profile  {team_profile_guid}")

    @dynamic_catch
    def link_team_role_to_profile(self, team_role_guid: str, team_profile_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach a team role to a team profile.
            Parameters
            ----------
            team_role_guid: str
                The unique identifier of the team role.
            team_profile_guid: str
                The identifier of the team profile.
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
                "class": "TeamRoleAppointmentProperties",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_team_role_to_profile(team_role_guid, team_profile_guid, body))

    @dynamic_catch
    async def _async_detach_team_role_from_profile(self, team_role_guid: str, team_profile_guid: str,
                                                   body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach a person role from a person profile. Async version.

        Parameters
        ----------
        team_role_guid: str
            The unique identifier of the team role.
        team_profile_guid: str
            The unique identifier of the team profile.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
        url = (f"{self.command_root}/actor-roles/{team_role_guid}/team-role-appointments/{team_profile_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.debug(f"Detached Team Role {team_role_guid} from Team Profile {team_profile_guid}")

    def detach_team_role_from_profile(self, team_role_guid: str, team_profile_guid: str,
                                      body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach a person role from a person profile. Async version.

            Parameters
            ----------
            team_role_guid: str
                The unique identifier of the team role.
            team_profile_guid: str
                The unique identifier of the team profile.
            body: dict | DeleteRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
        loop.run_until_complete(self._async_detach_team_role_from_profile(team_role_guid, team_profile_guid, body))

    #
    @dynamic_catch
    async def _async_link_it_profile_role_to_it_profile(self, it_profile_role_guid: str, it_profile_guid: str,
                                                        body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach an IT profile role to an IT profile. Async version.

        Parameters
        ----------
        it_profile_role_guid: str
            The unique identifier of the IT profile role.
        it_profile_guid: str
            The identifier of the IT profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "ITProfileRoleAppointmentProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = url = (
            f"{self.command_root}/actor-roles/{it_profile_role_guid}/it-profile-role-appointments/{it_profile_guid}/attach")
        await self._async_new_relationship_request(url, ["ITProfileAppointmentProperties"], body)
        logger.debug(f"Linking IT Profile role {it_profile_role_guid} to IT Profile  {it_profile_guid}")

    @dynamic_catch
    def link_it_profile_role_to_it_profile(self, it_profile_role_guid: str, it_profile_guid: str,
                                           body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach a person role to a person profile.
            Parameters
            ----------
            it_profile_role_guid: str
                The unique identifier of the IT Profile role.
            it_profile_guid: str
                The identifier of the IT profile.
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
                "class": "ITProfileRoleAppointmentProperties",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_it_profile_role_to_it_profile(it_profile_role_guid, it_profile_guid, body))

    @dynamic_catch
    async def _async_detach_it_profile_role_from_it_profile(self, it_profile_role_guid: str, it_profile_guid: str,
                                                            body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach an IT profile role from an IT profile. Async version.

        Parameters
        ----------
        it_profile_role_guid: str
            The unique identifier of the IT profile role.
        it_profile_guid: str
            The unique identifier of the IT profile.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            f"{self.command_root}/actor-roles/{it_profile_role_guid}/it-profile-role-appointments/{it_profile_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.debug(f"Detached IT Profile Role {it_profile_role_guid} from IT Profile {it_profile_guid}")

    def detach_it_profile_role_from_it_profile(self, it_profile_role_guid: str, it_profile_guid: str,
                                               body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach an IT profile role from an IT profile.

            Parameters
            ----------
            it_profile_role_guid: str
                The unique identifier of the IT profile role.
            it_profile_guid: str
                The unique identifier of the IT profile.
            body: dict | DeleteRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
        loop.run_until_complete(
            self._async_detach_it_profile_role_from_it_profile(it_profile_role_guid, it_profile_guid, body))

    #

    @dynamic_catch
    async def _async_delete_actor_role(self, actor_role_guid: str,
                                       body: Optional[dict | DeleteElementRequestBody] = None,
                                       cascade: bool = False) -> None:
        """ Delete an actor role. Async Version.

        Parameters
        ----------
        actor_role_guid: str
            The guid of the actor role to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict | DeleteElementRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.command_root}/actor-roles/{actor_role_guid}/delete"

        await self._async_delete_element_request(url, body, cascade)
        logger.debug(f"Deleted actor role {actor_role_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_actor_role(self, actor_role_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                          cascade: bool = False) -> None:
        """ Delete an actor role. Async Version.

         Parameters
         ----------
         actor_role_guid: str
             The guid of the actor role to delete.

         cascade: bool, optional, defaults to True
             If true, a cascade delete is performed.

         body: dict | DeleteRelationshipRequestBody, optional, default = None
             A structure representing the details of the relationship.

         Returns
         -------
         Nothing

         Raises
         ------
         PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

         Notes
         _____
         JSON Structure looks like:
         {
           "class": "DeleteRelationshipRequestBody",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime": "{{$isoTimestamp}}",
           "forLineage": false,
           "forDuplicateProcessing": false
         }
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_actor_role(actor_role_guid, body, cascade))

    @dynamic_catch
    async def _async_find_actor_roles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ActorRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor role metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all roles.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-roles/by-search-string"))

        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        response = await self._async_find_request(
            url,
            _type="ActorRole",
            _gen_output=self._generate_actor_role_output,
            **params,
        )
        return response

    def find_actor_roles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ActorRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor role metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str, default "*"
            Search string to match against - None or '*' indicate match against all roles.
        starts_with : bool, default True
            Starts with the supplied string.
        ends_with : bool, default False
            Ends with the supplied string.
        ignore_case : bool, default True
            Ignore case when searching.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The subtypes to filter by.
        include_only_relationships : list[str], optional
            Only include these relationships.
        skip_relationships : list[str], optional
            Relationships to skip in the graph.
        graph_query_depth : int, optional
            The query depth for relationships.
        as_of_time : str, optional
            Historical time for the query.
        start_from : int, optional
            Starting index for pagination. Defaults to 0.
        page_size : int, optional
            Number of results per page. Defaults to 100.
        sequencing_order : str, optional
            Order for sequencing results.
        sequencing_property : str, optional
            Property to sequence by.
        output_format : str, optional
            Format for output. Defaults to "JSON".
        report_spec : str | dict, optional
            Report specification for formatting.
        body : dict, optional
            Request body for additional parameters.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_actor_roles(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_actor_roles_by_name(
        self,
        name: str,
        metadata_element_type_name: str | None = "ActorRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor role metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str
            name to use to find matching roles.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Roles"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-roles/by-name"))
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="ActorRole",
            _gen_output=self._generate_actor_role_output,
            **params,
        )

    def get_actor_roles_by_name(
        self,
        name: str,
        metadata_element_type_name: str | None = "ActorRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of actor role metadata elements with a particular name.

        Parameters
        ----------
        name: str
            name to use to find matching roles.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=0]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Roles"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actor_roles_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_actor_role_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific actor role. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the actor role to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Roles"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = str(HttpUrl(f"{self.command_root}/actor-roles/{guid}/retrieve"))
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="ActorRole",
            _gen_output=self._generate_actor_role_output,
            **params,
        )

    def get_actor_role_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Actor-Roles",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific actor role.

        Parameters
        ----------
        guid: str
            unique identifier of the actor role to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Actor-Roles"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actor_role_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    def _extract_actor_role_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a actor_role element and populate into the provided columns_struct.

        Args:
            element (dict): The actor_role element
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
        # actor_roleCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("actor_roleCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break

        # Handle sideLinks specifically for nested reports if present at root
        side_links = element.get('sideLinks')
        if side_links:
            for column in columns_list:
                if column.get('key') == 'side_links' and column.get('detail_spec'):
                    materialized = [materialize_egeria_summary(sl) for sl in side_links]
                    column['value'] = materialized
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

    def _generate_actor_role_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                    element_type_name: Optional[str] = None, output_format: str = "DICT",
                                    report_spec: dict | str = "Actor-Roles", **kwargs) -> str | list[dict]:
        """ Generate output for actor_roles in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter_string (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of actor_role
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.
                **kwargs: Additional arguments.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "ActorRole",
            output_format=output_format,
            extract_properties_func=self._extract_actor_role_properties,
            report_spec=report_spec,
            **kwargs
        )

    #
    # User Identity
    #

    @dynamic_catch
    async def _async_create_user_identity(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new user identity. Async version.

        Parameters
        ----------

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the user identity to create.
        Returns
        -------
        str - the guid of the created user identity

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
        simple:

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
            "class" : "UserIdentityProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "userId":"add name here",
            "distinguishedName": "add name here",
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

        url = f"{self.command_root}/user-identities"
        return await self._async_create_element_body_request(url, ["ActorProfileProperties"], body)

    @dynamic_catch
    def create_user_identity(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new user identity.

               Parameters
               ----------
               body: dict | NewElementRequestBody, optional
                   A dict or NewElementRequestBody representing the details of the user identity to create.
               Returns
               -------
               str - the guid of the created user identity

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
               example:

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
                    "class" : "UserIdentityProperties",
                    "typeName" : "enter the type of the element",
                    "qualifiedName": "add unique name here",
                    "userId":"add name here",
                    "distinguishedName": "add name here",
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

        return asyncio.get_event_loop().run_until_complete(self._async_create_user_identity(body))

    @dynamic_catch
    async def _async_create_user_identity_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent a user identity using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.
            Async version.

        Parameters
        ----------
        body: TemplateRequestBody | dict
            A dict representing the details of the user identity to create.

        Returns
        -------
        str - the guid of the created user identity

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
        url = f"{self.command_root}/user-identities/from-template"

        return await self._async_create_element_from_template("POST", url, body)

    @dynamic_catch
    def create_user_identity_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new metadata element to represent an user identity using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dict or TemplateRequestBody representing the details of the user identity to create.

        Returns
        -------
        str - the guid of the created user identity

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
        resp = loop.run_until_complete(self._async_create_user_identity_from_template(body))
        return resp

    @dynamic_catch
    async def _async_update_user_identity(self, user_identity_guid: str,
                                          body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an user identity.
            Collections: https://egeria-project.org/concepts/user_identity

            Async version.
        Parameters
        ----------
        user_identity_guid: str
            The guid of the user identity to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the user identity to create.

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
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "UserIdentityProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "userId":"add name here",
            "distinguishedName": "add name here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = (f"{self.command_root}/user-identities/{user_identity_guid}/update")
        await self._async_update_element_body_request(url, ["UserIdentityProperties"], body)

    @dynamic_catch
    def update_user_identity(self, user_identity_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an user identity.
            Collections: https://egeria-project.org/concepts/user_identity

        Parameters
        ----------
        user_identity_guid: str
            The guid of the user identity to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the user identity to create.

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
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "UserIdentityProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "userId":"add name here",
            "distinguishedName": "add name here",
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

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_user_identity(user_identity_guid, body))

    @dynamic_catch
    async def _async_link_identity_to_profile(self, user_identity_guid: str, actor_profile_guid: str,
                                              body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach an actor profile to a user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        actor_profile_guid: str
            The identifier of the actor profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "ProfileIdentityProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = url = (
            f"{self.command_root}/user-identities/{user_identity_guid}/profile-identity/{actor_profile_guid}/attach")
        await self._async_new_relationship_request(url, ["ProfileIdentityProperties"], body)
        logger.debug(f"Linking User Identity {user_identity_guid} to Actor Profile  {actor_profile_guid}")

    @dynamic_catch
    def link_identity_to_profile(self, user_identity_guid: str, actor_profile_guid: str,
                                 body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach an actor profile to a user identity.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        actor_profile_guid: str
            The identifier of the actor profile.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "ProfileIdentityProperties",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_identity_to_profile(user_identity_guid, actor_profile_guid, body))

    @dynamic_catch
    async def _async_detach_identity_from_profile(self, user_identity_guid: str, actor_profile_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach an actor profile from a user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        actor_profile_guid: str
            The unique identifier of the actor profile.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
        url = (f"{self.command_root}/user-identities/{user_identity_guid}/profile-identity/{actor_profile_guid}/detach")

        await self._async_delete_element_request(url, body)
        logger.debug(f"Detached User Identity {user_identity_guid} from it a actor profile {actor_profile_guid}")

    @dynamic_catch
    def detach_identity_from_profile(self, user_identity_guid: str, actor_profile_guid: str,
                                     body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach an actor profile from a user identity.

            Parameters
            ----------
            user_identity_guid: str
                The unique identifier of the user identity.
            actor_profile_guid: str
                The unique identifier of the actor profile.
            body: dict | DeleteRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
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
        loop.run_until_complete(self._async_detach_identity_from_profile(user_identity_guid, actor_profile_guid, body))

    @dynamic_catch
    async def _async_link_assignment_scope(self, scope_element_guid: str, actor_guid: str,
                                           body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach an actor to an element that describes its scope. Async version.

        Parameters
        ----------
        scope_element_guid: str
            The unique identifier of the element that describes the scope.
        actor_guid: str
            The unique identifier of the actor.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "AssignmentScopeProperties",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = f"{self.command_root}/elements/{scope_element_guid}/actors/{actor_guid}/attach"
        await self._async_new_relationship_request(url, ["AssignmentScopeProperties"], body)
        logger.debug(f"Linking actor {actor_guid} to assignment scope {scope_element_guid}")

    @dynamic_catch
    def link_assignment_scope(self, scope_element_guid: str, actor_guid: str,
                              body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach an actor to an element that describes its scope.

        Parameters
        ----------
        scope_element_guid: str
            The unique identifier of the element that describes the scope.
        actor_guid: str
            The unique identifier of the actor.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
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
            "class": "AssignmentScopeProperties",
            "description": "",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_assignment_scope(scope_element_guid, actor_guid, body))

    @dynamic_catch
    async def _async_detach_assignment_scope(self, scope_element_guid: str, actor_guid: str,
                                             body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach an actor from the element that describes its scope. Async version.

        Parameters
        ----------
        scope_element_guid: str
            The unique identifier of the element that describes the scope.
        actor_guid: str
            The unique identifier of the actor.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/elements/{scope_element_guid}/actors/{actor_guid}/detach"

        await self._async_delete_relationship_request(url, body)
        logger.debug(f"Detached actor {actor_guid} from assignment scope {scope_element_guid}")

    @dynamic_catch
    def detach_assignment_scope(self, scope_element_guid: str, actor_guid: str,
                                body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach an actor from the element that describes its scope.

        Parameters
        ----------
        scope_element_guid: str
            The unique identifier of the element that describes the scope.
        actor_guid: str
            The unique identifier of the actor.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_assignment_scope(scope_element_guid, actor_guid, body))

    @dynamic_catch
    async def _async_add_security_group_membership(self, user_identity_guid: str, security_groups: list[str] = [""],
                                                   body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """ Add the SecurityGroupMembership classification to the user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        security_groups: list[str], optional, default = [""]
            The list of security groups to add to the user identity.
        body: dict | NewClassificationRequestBody, optional, default = None
            A structure representing the details of the classification.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewClassificationRequestBody",
          "properties": {
            "class": "SecurityGroupMembershipProperties",
            "groups": [""],
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

        url = url = (f"{self.command_root}/user-identities/{user_identity_guid}/security-group-membership/classify")
        await self._async_new_classification_request(url, ["SecurityGroupMembershipProperties"], body)
        logger.debug(f"Classifying User Identity {user_identity_guid} with Security Groups  {security_groups}")

    @dynamic_catch
    def add_security_group_membership(self, user_identity_guid: str, security_groups: list[str] = [""],
                                      body: Optional[dict | NewClassificationRequestBody] = None):
        """ Add the SecurityGroupMembership classification to the user identity.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        security_groups: list[str], optional, default = [""]
            The list of security groups to add to the user identity.
        body: dict | NewClassificationRequestBody, optional, default = None
            A structure representing the details of the classification.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewClassificationRequestBody",
          "properties": {
            "class": "SecurityGroupMembershipProperties",
            "groups": [""],
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
        loop.run_until_complete(self._async_add_security_group_membership(user_identity_guid, security_groups, body))

    @dynamic_catch
    async def _async_update_security_group_membership(self, user_identity_guid: str,
                                                      body: dict = None) -> None:
        """ Update the SecurityGroupMembership classification. Async version.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        body: dict, optional, default = None
            A structure representing the details of the classification.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "UpdateClassificationRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class": "SecurityGroupMembershipProperties",
            "groups": [""],
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
        url = (f"{self.command_root}/user-identities/{user_identity_guid}/security-group-membership/reclassify")

        await self._async_make_request("POST", url, body)
        logger.debug(f"Updated security classifications for {user_identity_guid}")

    @dynamic_catch
    def update_security_group_membership(self, user_identity_guid: str,
                                         body: dict = None):
        """ Update the SecurityGroupMembership classification.

            Parameters
            ----------
            user_identity_guid: str
                The unique identifier of the user identity.
            body: dict, optional, default = None
                A structure representing the details of the classification.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
                The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            JSON Structure looks like:
            {
              "class" : "UpdateClassificationRequestBody",
              "mergeUpdate" : true,
              "properties": {
                "class": "SecurityGroupMembershipProperties",
                "groups": [""],
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
        loop.run_until_complete(self._async_update_security_group_membership(user_identity_guid, body))

    @dynamic_catch
    async def _async_remove_all_security_group_memberships(self, user_identity_guid: str,
                                                           body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """ Remove all security group classifications from a user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str
            The unique identifier of the user identity.
        body: dict | DeleteClassificationRequestBody, optional, default = None
            A structure representing the details of the classification.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteClassificationRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (f"{self.command_root}/user-identities/{user_identity_guid}/security-group-memberships/declassify")

        await self._async_delete_classification_request(url, body)
        logger.debug(f"Declassified User Identity {user_identity_guid} from its security groups")

    @dynamic_catch
    def remove_all_security_group_memberships(self, user_identity_guid: str,
                                              body: Optional[dict | DeleteClassificationRequestBody] = None):
        """ Remove all security group classifications from a user identity.

            Parameters
            ----------
            user_identity_guid: str
                The unique identifier of the user identity.
            body: dict | DeleteClassificationRequestBody, optional, default = None
                A structure representing the details of the classification.

            Returns
            -------
            Nothing

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
                The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            JSON Structure looks like:
            {
              "class": "DeleteClassificationRequestBody",
              "deleteMethod": "LOOK_FOR_LINEAGE",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_identity_from_profile(user_identity_guid, body))

    #
    # do deletes etc
    #
    @dynamic_catch
    async def _async_delete_user_identity(self, user_identity_guid: str,
                                          body: Optional[dict | DeleteElementRequestBody] = None,
                                          cascade: bool = False) -> None:
        """ Delete an user identity. Async Version.

        Parameters
        ----------
        user_identity_guid: str
            The guid of the user identity to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict | DeleteElementRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
        {
          "class": "DeleteElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.command_root}/user-identities/{user_identity_guid}/delete"

        await self._async_delete_element_request(url, body, cascade)
        logger.debug(f"Deleted user identity {user_identity_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_user_identity(self, user_identity_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                             cascade: bool = False) -> None:
        """ Delete an user identity. Async Version.

         Parameters
         ----------
         user_identity_guid: str
             The guid of the user identity to delete.

         cascade: bool, optional, defaults to True
             If true, a cascade delete is performed.

         body: dict | DeleteElementRequestBody, optional, default = None
             A structure representing the details of the relationship.

         Returns
         -------
         Nothing

         Raises
         ------
         PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

         Notes
         _____
         JSON Structure looks like:
         {
           "class": "DeleteElementRequestBody",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime": "{{$isoTimestamp}}",
           "forLineage": false,
           "forDuplicateProcessing": false
         }
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_user_identity(user_identity_guid, body, cascade))

    @dynamic_catch
    async def _async_find_user_identities(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "UserIdentity",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of user identity metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all user identities.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/user-identities/by-search-string"))
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        response = await self._async_find_request(
            url,
            _type="UserIdentity",
            _gen_output=self._generate_user_identity_output,
            **params,
        )
        return response

    @dynamic_catch
    def find_user_identities(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "UserIdentity",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of user identity metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all user identities.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_user_identities(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_user_identities_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "UserIdentity",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of user identity metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching user identities.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "User-Identities"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = str(HttpUrl(f"{self.command_root}/user-identities/by-name"))
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="UserIdentity",
            _gen_output=self._generate_user_identity_output,
            **params,
        )

    @dynamic_catch
    def get_user_identities_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "UserIdentity",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of user identity metadata elements with a particular name.

        Parameters
        ----------
        name: str, optional
            name to use to find matching user identities.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "User-Identities"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_user_identities_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_user_identity_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific user identity. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the user identity to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "User-Identities"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = str(HttpUrl(f"{self.command_root}/user-identities/{guid}/retrieve"))
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="UserIdentity",
            _gen_output=self._generate_user_identity_output,
            **params,
        )

    @dynamic_catch
    def get_user_identity_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "User-Identities",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Retrieve the properties of a specific user identity.

        Parameters
        ----------
        guid: str
            unique identifier of the user identity to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "User-Identities"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_user_identity_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    def _extract_user_identity_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a user_identity element and populate into the provided columns_struct.

        Args:
            element (dict): The user_identity element
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
        # user_identityCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("user_identityCategories", [])
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

    def _generate_user_identity_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                       element_type_name: Optional[str] = None, output_format: str = "DICT",
                                       report_spec: dict | str = "User-Identities", **kwargs) -> str | list[dict]:
        """ Generate output for user_identitys in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter_string (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of user_identity
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.
                **kwargs: Additional arguments.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "UserIdentity",
            output_format=output_format,
            extract_properties_func=self._extract_user_identity_properties,
            report_spec=report_spec,
            **kwargs
        )


    @dynamic_catch
    async def _async_create_contribution_record(self, actor_profile_guid: str, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """ Create a new contribution record. Async version.

        Parameters
        ----------
        actor_profile_guid: str
            The guid of the actor profile to associate the contribution record with.
        body: dict | NewAttachmentRequestBody, optional
            A dict or NewElementRequestBody representing the details of the contribution record to create.

        Returns
        -------
        str - the guid of the created contribution record

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
        example:
        {
          "class" : "NewAttachmentRequestBody",
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
            "class" : "ContributionRecordProperties",
            "qualifiedName": "add unique name here",
            "displayName":"add name here",
            "identifier": "add name here",
            "description": "add description here",
            "category": "add category here",
            "url": "add url here",
            "karmaPoints" : 0,
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
        url = f"{self.command_root}/actor-profiles/{actor_profile_guid}/contribution-records"
        return await self._async_create_attachment_body_request(url, ["ContributionRecordProperties"], body)

    @dynamic_catch
    def create_contribution_record(self, actor_profile_guid: str, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """ Create a new contribution record.

        Parameters
        ----------
        actor_profile_guid: str
            The guid of the actor profile to associate the contribution record with.
        body: dict | NewAttachmentRequestBody, optional
            A dict or NewElementRequestBody representing the details of the contribution record to create.

        Returns
        -------
        str - the guid of the created contribution record

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
        example:
        {
          "class" : "NewAttachmentRequestBody",
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
            "class" : "ContributionRecordProperties",
            "qualifiedName": "add unique name here",
            "displayName":"add name here",
            "identifier": "add name here",
            "description": "add description here",
            "category": "add category here",
            "url": "add url here",
            "karmaPoints" : 0,
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
        return asyncio.run(self._async_create_contribution_record(actor_profile_guid, body))

    @dynamic_catch
    async def _async_update_contribution_record(self, contribution_record_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a contribution record. Async version.

        Parameters
        ----------
        contribution_record_guid: str
            The unique identifier of the contribution record to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContributionRecordProperties",
            "qualifiedName": "add unique name here",
            "displayName":"add name here",
            "identifier": "add name here",
            "description": "add description here",
            "category": "add category here",
            "url": "add url here",
            "karmaPoints" : 0,
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
        url = f"{self.command_root}/contribution-records/{contribution_record_guid}"
        await self._async_update_element_body_request(url, ["ContributionRecordProperties"], body)

    @dynamic_catch
    def update_contribution_record(self, contribution_record_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a contribution record.

        Parameters
        ----------
        contribution_record_guid: str
            The unique identifier of the contribution record to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContributionRecordProperties",
            "qualifiedName": "add unique name here",
            "displayName":"add name here",
            "identifier": "add name here",
            "description": "add description here",
            "category": "add category here",
            "url": "add url here",
            "karmaPoints" : 0,
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
        return asyncio.run(self._async_update_contribution_record(contribution_record_guid, body))

    @dynamic_catch
    async def _async_delete_contribution_record(self, contribution_record_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Delete a contribution record. Async version.

        Parameters
        ----------
        contribution_record_guid: str
            The unique identifier of the contribution record to delete.
        body: dict | DeleteRelationshipRequestBody, optional
            A dict or DeleteRelationshipRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteRelationshipRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadeDelete" : false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/contribution-records/{contribution_record_guid}/delete"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def delete_contribution_record(self, contribution_record_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Delete a contribution record.

        Parameters
        ----------
        contribution_record_guid: str
            The unique identifier of the contribution record to delete.
        body: dict | DeleteRelationshipRequestBody, optional
            A dict or DeleteRelationshipRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteRelationshipRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadeDelete" : false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return asyncio.run(self._async_delete_contribution_record(contribution_record_guid, body))

    @dynamic_catch
    async def _async_get_contribution_records_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "ContributionRecord",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contribution record metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching contribution records.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contribution-Records"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = f"{self.command_root}/contribution-records/by-name"
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="ContributionRecord",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_contribution_records_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "ContributionRecord",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contribution record metadata elements with a particular name.

        Parameters
        ----------
        name: str, optional
            name to use to find matching contribution records.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contribution-Records"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_contribution_records_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_contribution_records(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ContributionRecord",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contribution record metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all contribution records.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = f"{self.command_root}/contribution-records/by-search-string"
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="ContributionRecord",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def find_contribution_records(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ContributionRecord",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contribution record metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all contribution records.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_contribution_records(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_contribution_record_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific contribution record. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the contribution record to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contribution-Records"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = f"{self.command_root}/contribution-records/{guid}/retrieve"
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="ContributionRecord",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_contribution_record_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contribution-Records",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific contribution record.

        Parameters
        ----------
        guid: str
            unique identifier of the contribution record to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contribution-Records"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_contribution_record_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_create_contact_details(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new contact details. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the contact details to create.

        Returns
        -------
        str - the guid of the created contact details

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
        example:
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
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL",
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
        url = f"{self.command_root}/contact-details"
        return await self._async_create_element_body_request(url, ["ContactDetailsProperties"], body)

    @dynamic_catch
    def create_contact_details(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new contact details.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the contact details to create.

        Returns
        -------
        str - the guid of the created contact details

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
        example:
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
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL",
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
        return asyncio.run(self._async_create_contact_details(body))

    @dynamic_catch
    async def _async_create_contact_details_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new contact details from a template. Async version.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created contact details

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
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
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL"
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
          }
        }
        """
        url = f"{self.command_root}/contact-details/from-template"
        return await self._async_create_element_body_request(url, ["ContactDetailsProperties"], body)

    @dynamic_catch
    def create_contact_details_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new contact details from a template.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created contact details

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
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
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL"
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
          }
        }
        """
        return asyncio.run(self._async_create_contact_details_from_template(body))

    @dynamic_catch
    async def _async_update_contact_details(self, contact_details_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a contact details. Async version.

        Parameters
        ----------
        contact_details_guid: str
            The unique identifier of the contact details to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL",
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
        url = f"{self.command_root}/contact-details/{contact_details_guid}/update"
        await self._async_update_element_body_request(url, ["ContactDetailsProperties"], body)

    @dynamic_catch
    def update_contact_details(self, contact_details_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a contact details.

        Parameters
        ----------
        contact_details_guid: str
            The unique identifier of the contact details to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContactDetailsProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "contactType" : "add contact type",
            "contactMethodService" : "",
            "contactMethodValue" : "",
            "contactMethodType" : "EMAIL",
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
        return asyncio.run(self._async_update_contact_details(contact_details_guid, body))

    @dynamic_catch
    async def _async_delete_contact_details(self, contact_details_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a contact details. Async version.

        Parameters
        ----------
        contact_details_guid: str
            The unique identifier of the contact details to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
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
        url = f"{self.command_root}/contact-details/{contact_details_guid}/delete"
        await self._async_delete_element_request(url, body)

    @dynamic_catch
    def delete_contact_details(self, contact_details_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a contact details.

        Parameters
        ----------
        contact_details_guid: str
            The unique identifier of the contact details to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
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
        return asyncio.run(self._async_delete_contact_details(contact_details_guid, body))

    @dynamic_catch
    async def _async_link_contact_details(self, element_guid: str, contact_details_guid: str,
                                          body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """ Attach an element to its contact details. Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the parent element.
        contact_details_guid: str
            The unique identifier of the contact details.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "ContactThroughProperties",
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

        url = f"{self.command_root}/elements/{element_guid}/contact-details/{contact_details_guid}/attach"
        await self._async_new_relationship_request(url, ["ContactThroughProperties"], body)
        logger.debug(f"Linking element {element_guid} to contact details {contact_details_guid}")

    @dynamic_catch
    def link_contact_details(self, element_guid: str, contact_details_guid: str,
                             body: Optional[dict | NewRelationshipRequestBody] = None):
        """ Attach an element to its contact details.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the parent element.
        contact_details_guid: str
            The unique identifier of the contact details.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "ContactThroughProperties",
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
        loop.run_until_complete(self._async_link_contact_details(element_guid, contact_details_guid, body))

    @dynamic_catch
    async def _async_detach_contact_details(self, element_guid: str, contact_details_guid: str,
                                            body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Detach an element from its contact details. Async version.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the parent element.
        contact_details_guid: str
            The unique identifier of the contact details.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/elements/{element_guid}/contact-details/{contact_details_guid}/detach"

        await self._async_delete_relationship_request(url, body)
        logger.debug(f"Detached element {element_guid} from contact details {contact_details_guid}")

    @dynamic_catch
    def detach_contact_details(self, element_guid: str, contact_details_guid: str,
                               body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Detach an element from its contact details.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the parent element.
        contact_details_guid: str
            The unique identifier of the contact details.
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_contact_details(element_guid, contact_details_guid, body))

    @dynamic_catch
    async def _async_get_contact_details_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "ContactDetails",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contact details metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching contact details.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contact-Details"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = f"{self.command_root}/contact-details/by-name"
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="ContactDetails",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_contact_details_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "ContactDetails",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contact details metadata elements with a particular name.

        Parameters
        ----------
        name: str, optional
            name to use to find matching contact details.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contact-Details"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_contact_details_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_contact_details(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ContactDetails",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contact details metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all contact details.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = f"{self.command_root}/contact-details/by-search-string"
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="ContactDetails",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def find_contact_details(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "ContactDetails",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of contact details metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all contact details.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_contact_details(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_contact_details_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific contact details. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the contact details to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contact-Details"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = f"{self.command_root}/contact-details/{guid}/retrieve"
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="ContactDetails",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_contact_details_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Contact-Details",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific contact details.

        Parameters
        ----------
        guid: str
            unique identifier of the contact details to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Contact-Details"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_contact_details_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    # =====================================================================================================================
    # Work with Perspectives
    # https://egeria-project.org/concepts/perspective

    @dynamic_catch
    async def _async_create_perspective(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new perspective. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the perspective to create.

        Returns
        -------
        str - the guid of the created perspective

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
        example:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "PerspectiveProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        url = f"{self.command_root}/perspectives"
        body_to_use = body if body is not None else {}
        return await self._async_create_element_body_request(url, ["PerspectiveProperties"], body_to_use)

    @dynamic_catch
    def create_perspective(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new perspective.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the perspective to create.

        Returns
        -------
        str - the guid of the created perspective

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
        example:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "PerspectiveProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        return asyncio.run(self._async_create_perspective(body))

    @dynamic_catch
    async def _async_create_perspective_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new perspective from a template. Async version.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created perspective

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "TemplateRequestBody",
          "isOwnAnchor": false,
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
        url = f"{self.command_root}/perspectives/from-template"
        body_to_use = body if body is not None else {}
        return await self._async_create_element_body_request(url, ["PerspectiveProperties"], body_to_use)

    @dynamic_catch
    def create_perspective_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new perspective from a template.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created perspective

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "TemplateRequestBody",
          "isOwnAnchor": false,
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
        return asyncio.run(self._async_create_perspective_from_template(body))

    @dynamic_catch
    async def _async_update_perspective(self, perspective_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a perspective. Async version.

        Parameters
        ----------
        perspective_guid: str
            The unique identifier of the perspective to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "PerspectiveProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        url = f"{self.command_root}/perspectives/{perspective_guid}/update"
        await self._async_update_element_body_request(url, ["PerspectiveProperties"], body)

    @dynamic_catch
    def update_perspective(self, perspective_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a perspective.

        Parameters
        ----------
        perspective_guid: str
            The unique identifier of the perspective to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "PerspectiveProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        return asyncio.run(self._async_update_perspective(perspective_guid, body))

    @dynamic_catch
    async def _async_delete_perspective(self, perspective_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a perspective. Async version.

        Parameters
        ----------
        perspective_guid: str
            The unique identifier of the perspective to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteElementRequestBody",
          "cascadeDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00Z",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/perspectives/{perspective_guid}/delete"
        await self._async_delete_element_request(url, body)

    @dynamic_catch
    def delete_perspective(self, perspective_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a perspective.

        Parameters
        ----------
        perspective_guid: str
            The unique identifier of the perspective to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteElementRequestBody",
          "cascadeDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00Z",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return asyncio.run(self._async_delete_perspective(perspective_guid, body))

    @dynamic_catch
    async def _async_get_perspectives_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "Perspective",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of perspective metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching perspectives.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Perspectives"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = str(HttpUrl(f"{self.command_root}/perspectives/by-name"))
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="Perspective",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_perspectives_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "Perspective",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of perspective metadata elements with a particular name.

        Parameters
        ----------
        name: str, optional
            name to use to find matching perspectives.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Perspectives"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_perspectives_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_perspectives(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "Perspective",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of perspective metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all perspectives.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/perspectives/by-search-string"))
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="Perspective",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def find_perspectives(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "Perspective",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of perspective metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all perspectives.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_perspectives(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_perspective_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific perspective. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the perspective to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Perspectives"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = f"{self.command_root}/perspectives/{guid}/retrieve"
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="Perspective",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_perspective_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Perspectives",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific perspective.

        Parameters
        ----------
        guid: str
            unique identifier of the perspective to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Perspectives"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_perspective_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    # =====================================================================================================================
    # Work with Skills
    # https://egeria-project.org/concepts/skill

    @dynamic_catch
    async def _async_create_skill(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new skill. Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the skill to create.

        Returns
        -------
        str - the guid of the created skill

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
        example:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "SkillProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        url = f"{self.command_root}/skills"
        body_to_use = body if body is not None else {}
        return await self._async_create_element_body_request(url, ["SkillProperties"], body_to_use)

    @dynamic_catch
    def create_skill(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """ Create a new skill.

        Parameters
        ----------
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the skill to create.

        Returns
        -------
        str - the guid of the created skill

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
        example:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "SkillProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        return asyncio.run(self._async_create_skill(body))

    @dynamic_catch
    async def _async_create_skill_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new skill from a template. Async version.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created skill

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "TemplateRequestBody",
          "isOwnAnchor": false,
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
        url = f"{self.command_root}/skills/from-template"
        body_to_use = body if body is not None else {}
        return await self._async_create_element_body_request(url, ["SkillProperties"], body_to_use)

    @dynamic_catch
    def create_skill_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """ Create a new skill from a template.

        Parameters
        ----------
        body: dict | TemplateRequestBody, optional
            A dict or TemplateRequestBody representing the template and replacement properties.

        Returns
        -------
        str - the guid of the created skill

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "TemplateRequestBody",
          "isOwnAnchor": false,
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
        return asyncio.run(self._async_create_skill_from_template(body))

    @dynamic_catch
    async def _async_update_skill(self, skill_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a skill. Async version.

        Parameters
        ----------
        skill_guid: str
            The unique identifier of the skill to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "SkillProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        url = f"{self.command_root}/skills/{skill_guid}/update"
        await self._async_update_element_body_request(url, ["SkillProperties"], body)

    @dynamic_catch
    def update_skill(self, skill_guid: str, body: Optional[dict | UpdateElementRequestBody] = None) -> None:
        """ Update a skill.

        Parameters
        ----------
        skill_guid: str
            The unique identifier of the skill to update.
        body: dict | UpdateElementRequestBody, optional
            A dict or UpdateElementRequestBody representing the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate" : true,
          "properties": {
            "class" : "SkillProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          }
        }
        """
        return asyncio.run(self._async_update_skill(skill_guid, body))

    @dynamic_catch
    async def _async_delete_skill(self, skill_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a skill. Async version.

        Parameters
        ----------
        skill_guid: str
            The unique identifier of the skill to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteElementRequestBody",
          "cascadeDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00Z",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/skills/{skill_guid}/delete"
        await self._async_delete_element_request(url, body)

    @dynamic_catch
    def delete_skill(self, skill_guid: str, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
        """ Delete a skill.

        Parameters
        ----------
        skill_guid: str
            The unique identifier of the skill to delete.
        body: dict | DeleteElementRequestBody, optional
            A dict or DeleteElementRequestBody representing the delete options.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the DeleteElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        example:
        {
          "class" : "DeleteElementRequestBody",
          "cascadeDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00Z",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return asyncio.run(self._async_delete_skill(skill_guid, body))

    @dynamic_catch
    async def _async_get_skills_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "Skill",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of skill metadata elements with a particular name. Async Version.

        Parameters
        ----------
        name: str, optional
            name to use to find matching skills.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Skills"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        # Handle backward-compatible positional or keyword args
        if name is not None and not isinstance(name, str):
            body = name
            name = None

        if name is None:
            name = kwargs.pop("filter_string", None)

        if name is None and body is None:
            name = "*"

        url = str(HttpUrl(f"{self.command_root}/skills/by-name"))
        params = {
            "filter_string": name,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "start_from": start_from,
            "page_size": page_size,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "filter_string"}

        return await self._async_get_name_request(
            url,
            _type="Skill",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_skills_by_name(
        self,
        name: str = None,
        metadata_element_type_name: str | None = "Skill",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of skill metadata elements with a particular name.

        Parameters
        ----------
        name: str, optional
            name to use to find matching skills.
        metadata_element_type_name : str, optional
            The type of metadata element.
        metadata_element_subtypes : list[str], optional
            The list of subtypes to filter by.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Skills"
            The desired output columns/fields to include.
        body: dict, optional
            Provides a full request body. If specified, the body supercedes other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_skills_by_name(
                name=name,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_skills(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "Skill",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of skill metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all skills.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        url = str(HttpUrl(f"{self.command_root}/skills/by-search-string"))
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="Skill",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def find_skills(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "Skill",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Retrieve the list of skill metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all skills.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=True], optional
            Ignore case when searching
        metadata_element_type_name: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        as_of_time: str, optional
            The time to search as of.
        start_from: int, [default=0], optional
            When paged results are available, the starting index.
        page_size: int, [default=100]
            The number of items to return.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict, optional
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional
            - if provided, the search parameters in the body will supercede other attributes.

        Returns
        -------
        list | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_skills(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_skill_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific skill. Async version.

        Parameters
        ----------
        guid: str
            unique identifier of the skill to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Skills"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        url = f"{self.command_root}/skills/{guid}/retrieve"
        params = {
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None}

        return await self._async_get_guid_request(
            url,
            _type="Skill",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    @dynamic_catch
    def get_skill_by_guid(
        self,
        guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "Skills",
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return the properties of a specific skill.

        Parameters
        ----------
        guid: str
            unique identifier of the skill to retrieve.
        include_only_relationships : list[str], optional
            The list of relationship type names to include.
        skip_relationships : list[str], optional
            The list of relationship type names to skip.
        graph_query_depth : int, optional
            The query depth for relationships.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict, optional, default = "Skills"
            The desired output columns/fields to include.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
        dict | str
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_skill_by_guid(
                guid=guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

from typing import Union, Dict, List, Optional

if __name__ == "__main__":
    print("Main-Actor Manager")

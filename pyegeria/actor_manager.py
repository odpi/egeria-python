"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage external references to a variety of artifacts.

"""

import asyncio
from typing import Optional

from loguru import logger
from pydantic import HttpUrl

from pyegeria.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.config import settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody,
                             UpdateElementRequestBody, NewRelationshipRequestBody,
                             DeleteElementRequestBody, DeleteRelationshipRequestBody, NewClassificationRequestBody,
                             DeleteClassificationRequestBody)
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import dynamic_catch

app_settings = settings
EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
ACTOR_PROFILE = ["ActorProfile", "Person", "Team",
                 "UserIdentity",
                 "ITProfile", "Person"]

# ACTOR = ["Actor", "PersonRole", "TeamRole", "ITProfileRole"]
ACTOR_ROLE = ["ActorRole", "PersonRole", "TeamRole", "ITProfileRole", "TeamMember", "TeamLeader"]

from pyegeria._server_client import ServerClient


class ActorManager(ServerClient):
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

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        result = self.get_platform_origin()
        logger.debug(f"{self.__class__} initialized, platform origin is: {result} ")
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/actor-manager")

    @dynamic_catch
    async def _async_create_actor_profile(self, body: dict | NewElementRequestBody = None) -> str:
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
        return await self._async_create_element_body_request(url, ["ActorProfileProperties"], body)

    @dynamic_catch
    def create_actor_profile(self, body: dict | NewElementRequestBody = None) -> str:
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
    async def _async_create_actor_profile_from_template(self, body: TemplateRequestBody | dict) -> str:
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

        return await self._async_create_element_from_template("POST", url, body)

    @dynamic_catch
    def create_actor_profile_from_template(self, body: dict) -> str:
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
        await self._async_update_element_body_request(url, ["ActorProfileProperties"], body)

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
                                           body: dict | NewRelationshipRequestBody = None) -> None:
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
                              body: dict | NewRelationshipRequestBody = None):
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
                                               body: dict | DeleteRelationshipRequestBody = None) -> None:
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
                                  body: dict | DeleteRelationshipRequestBody = None):
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
                                          body: dict | DeleteElementRequestBody = None,
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
    def delete_actor_profile(self, actor_profile_guid: str, body: dict | DeleteElementRequestBody = None,
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
    async def _async_find_actor_profiles(self, search_string: str = "*", classification_names: list[str] = None,
                                         metadata_element_subtypes: list[str] = ACTOR_PROFILE,
                                         starts_with: bool = True, ends_with: bool = False,
                                         ignore_case: bool = False,
                                         start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                         report_spec: str | dict = "Actor-Profiles",
                                         body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of actor profile metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all profiles (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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

        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        """
        url = str(HttpUrl(f"{self.command_root}/actor-profiles/by-search-string"))
        response = await self._async_find_request(url, _type="ActorProfile",
                                                  _gen_output=self._generate_actor_profile_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    @dynamic_catch
    def find_actor_profiles(self, search_string: str = '*', classification_names: str = None,
                            metadata_element_subtypes: list[str] = ACTOR_PROFILE, starts_with: bool = True,
                            ends_with: bool = False, ignore_case: bool = False,
                            start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                            report_spec: str | dict = "Actor-Profiles",
                            body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of actor profile metadata elements that contain the search string. Async Version.

          Parameters
          ----------
          search_string: str
              Search string to match against - None or '*' indicate match against all profiles (may be filtered by
              classification).
          classification_names: list[str], optional, default=None
              A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
              then all classifications are returned.
          metadata_element_subtypes: list[str], optional, default=None
              A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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

          PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
          ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
          PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

          """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_actor_profiles(search_string, classification_names, metadata_element_subtypes, starts_with,
                                            ends_with, ignore_case, start_from, page_size, output_format, report_spec,
                                            body))

    @dynamic_catch
    async def _async_get_actor_profiles_by_name(self, filter_string: str = None,
                                                classification_names: list[str] = None,
                                                body: dict | FilterRequestBody = None,
                                                start_from: int = 0, page_size: int = 0,
                                                output_format: str = 'JSON',
                                                report_spec: str | dict = "Actor-Profiles") -> list | str:
        """ Retrieve the list of actor profile metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching profiles.
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

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        url = str(HttpUrl(f"{self.command_root}/actor-profiles/by-name"))
        response = await self._async_get_name_request(url, _type="ACTOR_PROFILES",
                                                      _gen_output=self._generate_actor_profile_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    def get_actor_profiles_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                   body: dict | FilterRequestBody = None,
                                   start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                   report_spec: str | dict = "Actor-Profiles") -> list | str:
        """ Retrieve the list of actor profile metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching profiles.
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

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_actor_profiles_by_name(filter_string, classification_names, body, start_from,
                                                   page_size,
                                                   output_format, report_spec))

    @dynamic_catch
    async def _async_get_actor_profile_by_guid(self, actor_profile_guid: str, element_type: str = None,
                                               body: dict | GetRequestBody = None,
                                               output_format: str = 'JSON',
                                               report_spec: dict = "Actor-Profiles") -> dict | str:
        """ Retrieve the properties of a specific actor profile. Async version.

        Parameters
        ----------
        actor_profile_guid: str,
            unique identifier of the actor profile to retrieve.
        element_type: str, default = None, optional
            type of actor profile to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified actor profile. Returns a string if none found.

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

        url = str(HttpUrl(f"{self.command_root}/actor-profiles/{actor_profile_guid}/retrieve"))
        type = element_type if element_type else "ActorProfile"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_actor_profile_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_actor_profile_by_guid(self, actor_profile_guid: str, element_type: str = None,
                                  body: dict | GetRequestBody = None,
                                  output_format: str = 'JSON',
                                  report_spec: dict = "Actor-Profiles") -> dict | str:
        """ Retrieve the properties of a specific actor profile.

        Parameters
        ----------
        actor_profile_guid: str,
            unique identifier of the actor profile to retrieve.
        element_type: str, default = None, optional
            type of actor profile to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified actor profile. Returns a string if none found.

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
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_actor_profile_by_guid(actor_profile_guid, element_type, body,
                                                  output_format, report_spec))

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

    def _generate_actor_profile_output(self, elements: dict | list[dict], filter: Optional[str],
                                       element_type_name: Optional[str], output_format: str = "DICT",
                                       report_spec: dict | str = "Actor-Profiles") -> str | list[dict]:
        """ Generate output for actor_profiles in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of actor_profile
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if element_type_name is None:
            entity_type = "ActorProfile"
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
            # fallback to actor_profiles or entity type
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        if output_formats:
            get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
            if isinstance(get_additional_props_name, str):
                class_name, method_name = get_additional_props_name.split(".")
                if hasattr(self, method_name):
                    get_additional_props_func = getattr(self, method_name)

        logger.trace(f"Executing generate_actor_profile_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_actor_profile_properties,
            get_additional_props_func,
            output_formats,
        )

    #
    # Actor Role
    #

    @dynamic_catch
    async def _async_create_actor_role(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new actor role. Async version.

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
        return await self._async_create_element_body_request(url, ["ActorRoleProperties"], body)

    @dynamic_catch
    def create_actor_role(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new actor role.

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
    async def _async_create_actor_role_from_template(self, body: TemplateRequestBody | dict) -> str:
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

        return await self._async_create_element_from_template("POST", url, body)

    @dynamic_catch
    def create_actor_role_from_template(self, body: dict | TemplateRequestBody) -> str:
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

        url = (f"{self.command_root}/actor-roles/{actor_role_guid}/update")
        await self._async_update_element_body_request(url, ["ActorRoleProperties"], body)

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
                                                 body: dict | NewRelationshipRequestBody = None) -> None:
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
                                    body: dict | NewRelationshipRequestBody = None):
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
                                                     body: dict | DeleteRelationshipRequestBody = None) -> None:
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
                                        body: dict | DeleteRelationshipRequestBody = None):
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
                                               body: dict | NewRelationshipRequestBody = None) -> None:
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
                                  body: dict | NewRelationshipRequestBody = None):
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
                                                   body: dict | DeleteRelationshipRequestBody = None) -> None:
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
                                      body: dict | DeleteRelationshipRequestBody = None):
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
                                                        body: dict | NewRelationshipRequestBody = None) -> None:
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
                                           body: dict | NewRelationshipRequestBody = None):
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
                                                            body: dict | DeleteRelationshipRequestBody = None) -> None:
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
                                               body: dict | DeleteRelationshipRequestBody = None):
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
                                       body: dict | DeleteElementRequestBody = None,
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
        url = f"{self.command_root}/actor-profiles/{actor_role_guid}/delete"

        await self._async_delete_element_request(url, body, cascade)
        logger.debug(f"Deleted actor role {actor_role_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_actor_role(self, actor_role_guid: str, body: dict | DeleteElementRequestBody = None,
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
    async def _async_find_actor_roles(self, search_string: str = "*", classification_names: list[str] = None,
                                      metadata_element_subtypes: list[str] = ACTOR_ROLE,
                                      starts_with: bool = True, ends_with: bool = False,
                                      ignore_case: bool = False,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      report_spec: str | dict = "Actor-Roles",
                                      body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of actor role metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all roles (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["ActorRoles"], for an actor role. If none,
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

        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action

        """
        url = str(HttpUrl(f"{self.command_root}/actor-roles/by-search-string"))
        response = await self._async_find_request(url, _type="ActorRole", _gen_output=self._generate_actor_role_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    @dynamic_catch
    def find_actor_roles(self, search_string: str = '*', classification_names: str = None,
                         metadata_element_subtypes: list[str] = ACTOR_ROLE, starts_with: bool = True,
                         ends_with: bool = False, ignore_case: bool = False,
                         start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                         report_spec: str | dict = "Actor-Roles",
                         body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of actor role metadata elements that contain the search string. Async Version.

          Parameters
          ----------
          search_string: str
              Search string to match against - None or '*' indicate match against all roles (may be filtered by
              classification).
          classification_names: list[str], optional, default=None
              A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
              then all classifications are returned.
          metadata_element_subtypes: list[str], optional, default=None
              A list of metadata element types to filter on - for example, ["ActorRole"], for actor role. If none,
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

             PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            PyegeriaNotAuthorizedException
                The principle specified by the user_id does not have authorization for the requested action

          """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_actor_roles(search_string, classification_names, metadata_element_subtypes, starts_with,
                                         ends_with, ignore_case, start_from, page_size, output_format, report_spec,
                                         body))

    @dynamic_catch
    async def _async_get_actor_roles_by_name(self, filter_string: str = None,
                                             classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             report_spec: str | dict = "Actor-Roles") -> list | str:
        """ Retrieve the list of actor role metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching roles.
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

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        url = str(HttpUrl(f"{self.command_root}/actor-roles/by-name"))
        response = await self._async_get_name_request(url, _type="ActorRole",
                                                      _gen_output=self._generate_actor_role_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    def get_actor_roles_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                body: dict | FilterRequestBody = None,
                                start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                report_spec: str | dict = "Actor-Roles") -> list | str:
        """ Retrieve the list of actor role metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching roles.
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

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_actor_roles_by_name(filter_string, classification_names, body, start_from,
                                                page_size,
                                                output_format, report_spec))

    @dynamic_catch
    async def _async_get_actor_role_by_guid(self, actor_role_guid: str, element_type: str = None,
                                            body: dict | GetRequestBody = None,
                                            output_format: str = 'JSON',
                                            report_spec: dict = "Actor-Roles") -> dict | str:
        """ Retrieve the properties of a specific actor role. Async version.

        Parameters
        ----------
        actor_role_guid: str,
            unique identifier of the actor role to retrieve.
        element_type: str, default = None, optional
            type of actor role to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified actor role. Returns a string if none found.

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

        url = str(HttpUrl(f"{self.command_root}/actor-roles/{actor_role_guid}/retrieve"))
        type = element_type if element_type else "ActorRole"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_actor_role_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_actor_role_by_guid(self, actor_role_guid: str, element_type: str = None,
                               body: dict | GetRequestBody = None,
                               output_format: str = 'JSON',
                               report_spec: dict = "Actor-Roles") -> dict | str:
        """ Retrieve the properties of a specific actor role. Async version.

        Parameters
        ----------
        actor_role_guid: str,
            unique identifier of the actor role to retrieve.
        element_type: str, default = None, optional
            type of actor role to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict , optional, default = None
            The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified actor role. Returns a string if none found.

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
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_actor_role_by_guid(actor_role_guid, element_type, body,
                                               output_format, report_spec))

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

    def _generate_actor_role_output(self, elements: dict | list[dict], filter: Optional[str],
                                    element_type_name: Optional[str], output_format: str = "DICT",
                                    report_spec: dict | str = "Actor-Roles") -> str | list[dict]:
        """ Generate output for actor_roles in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of actor_role
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if element_type_name is None:
            entity_type = "ActorRole"
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
            # fallback to actor_roles or entity type
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        if output_formats:
            get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
            if isinstance(get_additional_props_name, str):
                class_name, method_name = get_additional_props_name.split(".")
                if hasattr(self, method_name):
                    get_additional_props_func = getattr(self, method_name)

        logger.trace(f"Executing generate_actor_role_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_actor_role_properties,
            get_additional_props_func,
            output_formats,
        )

    #
    # User Identity
    #

    @dynamic_catch
    async def _async_create_user_identity(self, body: dict | NewElementRequestBody = None) -> str:
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
    def create_user_identity(self, body: dict | NewElementRequestBody = None) -> str:
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
    async def _async_create_user_identity_from_template(self, body: TemplateRequestBody | dict) -> str:
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
    def create_user_identity_from_template(self, body: dict | TemplateRequestBody) -> str:
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
                                              body: dict | NewRelationshipRequestBody = None) -> None:
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
                                 body: dict | NewRelationshipRequestBody = None):
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
                                                  body: dict | DeleteRelationshipRequestBody = None) -> None:
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
                                     body: dict | DeleteRelationshipRequestBody = None):
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
    async def _async_add_security_group_membership(self, user_identity_guid: str, security_groups: list[str] = [""],
                                                   body: dict | NewClassificationRequestBody = None) -> None:
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
                                      body: dict | NewClassificationRequestBody = None):
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
                                                           body: dict | DeleteClassificationRequestBody = None) -> None:
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
                                              body: dict | DeleteClassificationRequestBody = None):
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
                                          body: dict | DeleteElementRequestBody = None,
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
    def delete_user_identity(self, user_identity_guid: str, body: dict | DeleteElementRequestBody = None,
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
    async def _async_find_user_identities(self, search_string: str = "*", classification_names: list[str] = None,
                                          metadata_element_subtypes: list[str] = ["UserIdentity"],
                                          starts_with: bool = True, ends_with: bool = False,
                                          ignore_case: bool = False,
                                          start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                          report_spec: str | dict = "User-Identities",
                                          body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of user identity metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all profiles (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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

        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = str(HttpUrl(f"{self.command_root}/user-identities/by-search-string"))
        response = await self._async_find_request(url, _type="UserIdentity",
                                                  _gen_output=self._generate_user_identity_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    @dynamic_catch
    def find_user_identities(self, search_string: str = '*', classification_names: str = None,
                             metadata_element_subtypes: list[str] = ["UserIdentity"], starts_with: bool = True,
                             ends_with: bool = False, ignore_case: bool = False,
                             start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                             report_spec: str | dict = "User-Identities",
                             body: dict | SearchStringRequestBody = None) -> list | str:
        """ Retrieve the list of user identity metadata elements that contain the search string. Async Version.

          Parameters
          ----------
          search_string: str
              Search string to match against - None or '*' indicate match against all profiles (may be filtered by
              classification).
          classification_names: list[str], optional, default=None
              A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
              then all classifications are returned.
          metadata_element_subtypes: list[str], optional, default=None
              A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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

          PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

          """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_user_identities(search_string, classification_names, metadata_element_subtypes, starts_with,
                                             ends_with, ignore_case, start_from, page_size, output_format, report_spec,
                                             body))

    @dynamic_catch
    async def _async_get_user_identities_by_name(self, filter_string: str = None,
                                                 classification_names: list[str] = None,
                                                 body: dict | FilterRequestBody = None,
                                                 start_from: int = 0, page_size: int = 0,
                                                 output_format: str = 'JSON',
                                                 report_spec: str | dict = "User-Identities") -> list | str:
        """ Retrieve the list of user identity metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str,
                name to use to find matching profiles.
            classification_names: list[str], optional, default = None
                type of collection to filter by - e.g., DataDict, Folder, Root
            body: dict | FilterRequestBody, optional, default = None
                Provides, a full request body. If specified, the body supercedes the name parameter.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            report_spec: str | dict , optional, default = User-Identities
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        url = str(HttpUrl(f"{self.command_root}/user-identities/by-name"))
        response = await self._async_get_name_request(url, _type="UserIdentity",
                                                      _gen_output=self._generate_user_identity_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    def get_user_identities_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                    body: dict | FilterRequestBody = None,
                                    start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                    report_spec: str | dict = "User-Identities") -> list | str:
        """ Retrieve the list of user identity metadata elements with a particular name. Async Version.

            Parameters
            ----------
            filter_string: str, optional, default = None
                name to use to find matching profiles.
            classification_names: list[str], optional, default = None
                type of collection to filter by - e.g., DataDict, Folder, Root
            body: dict | FilterRequestBody, optional, default = None
                Provides, a full request body. If specified, the body supercedes the name parameter.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            report_spec: dict , optional, default = User-Identities
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A list of profiles matching the name. Returns a string if none found.

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
            {
              "class" : "SearchStringRequestBody",
              "searchString": "xxx",
              "startsWith" : false,
              "endsWith" : false,
              "ignoreCase" : true,
              "startFrom" : 0,
              "pageSize": 0,
              "asOfTime" : "{{$isoTimestamp}}",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "limitResultsByStatus" : ["ACTIVE"],
              "sequencingOrder" : "PROPERTY_ASCENDING",
              "sequencingProperty" : "qualifiedName"
            }

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_user_identities_by_name(filter_string, classification_names, body, start_from,
                                                    page_size,
                                                    output_format, report_spec))

    @dynamic_catch
    async def _async_get_user_identity_by_guid(self, user_identity_guid: str, element_type: str = None,
                                               body: dict | GetRequestBody = None,
                                               output_format: str = 'JSON',
                                               report_spec: dict = "User-Identities") -> dict | str:
        """ Retrieve the properties of a specific user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str,
            unique identifier of the user identity to retrieve.
        element_type: str, default = None, optional
            type of user identity to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: dict , optional, default = User-Identities
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified user identity. Returns a string if none found.

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

        url = str(HttpUrl(f"{self.command_root}/user-identities/{user_identity_guid}/retrieve"))
        type = element_type if element_type else "UserIdentity"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_user_identity_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_user_identity_by_guid(self, user_identity_guid: str, element_type: str = None,
                                  body: dict | GetRequestBody = None,
                                  output_format: str = 'JSON',
                                  report_spec: dict = "User-Identities") -> dict | str:
        """ Retrieve the properties of a specific user identity. Async version.

        Parameters
        ----------
        user_identity_guid: str,
            unique identifier of the user identity to retrieve.
        element_type: str, default = None, optional
            type of user identity to retrieve.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict , optional, default = User-Identities
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified user identity. Returns a string if none found.

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
        ----
        Body sample:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        Args:
            report_spec ():
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_user_identity_by_guid(user_identity_guid, element_type, body, output_format, report_spec))

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

    def _generate_user_identity_output(self, elements: dict | list[dict], filter: Optional[str],
                                       element_type_name: Optional[str], output_format: str = "DICT",
                                       report_spec: dict | str = "User-Identities") -> str | list[dict]:
        """ Generate output for user_identitys in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of user_identity
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if element_type_name is None:
            entity_type = "UserIdentity"
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
            # fallback to user_identitys or entity type
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        if output_formats:
            get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
            if isinstance(get_additional_props_name, str):
                class_name, method_name = get_additional_props_name.split(".")
                if hasattr(self, method_name):
                    get_additional_props_func = getattr(self, method_name)

        logger.trace(f"Executing generate_user_identity_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_user_identity_properties,
            get_additional_props_func,
            output_formats,
        )


from typing import Union, Dict, List, Optional

if __name__ == "__main__":
    print("Main-Actor Manager")

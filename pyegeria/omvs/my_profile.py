"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the MyProfile class and its methods.

"""
import json

from loguru import logger
from typing import Any, Optional
from pyegeria.core._server_client import ServerClient
from pyegeria.core._validators import validate_name
from pyegeria.core.utils import dynamic_catch
from pyegeria.models import (
    GetRequestBody,
    NewElementRequestBody,
    SearchStringRequestBody,
    UpdateElementRequestBody,
)
import asyncio


class MyProfile(ServerClient):
    """A class representing the profile of a user.

    This class provides methods for retrieving and managing the profile details
    of a user associated with a token.

    Parameters
    ----------
    view_server : str
        The name of the view server to configure.
    platform_url : str
        The URL of the platform.
    token : str, optional
        The token associated with the user. Default is None.
    user_id : str, optional
        The user ID. Default is None.
    user_pwd : str, optional
        The user password. Default is None.
    """

    def __init__(self, view_server: str, platform_url: str, user_id: str | None = None, user_pwd: str|None = None,
                 token: str|None = None):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )
        self.my_profile_command_root: str = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/my-profile"

    @dynamic_catch
    async def _async_get_my_profile(
        self, output_format: str = "JSON", report_spec: str | dict = None
    ) -> dict | str:
        """Retrieve the profile details of the user associated with the token. Async version.

        Parameters
        ----------
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Returns
        -------
        dict | str
            A dictionary containing the profile details or formatted output.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        """
        url = self.my_profile_command_root
        response = await self._async_make_request("GET",url)
        if type(response) == str:
            return "No Profile Found"

        elements = response.json().get("element", "No Profile Found")
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return super()._generate_referenceable_output(elements, self.user_id, "Person",
                               output_format, report_spec)
        return elements

    @dynamic_catch
    def get_my_profile(
        self, output_format: str = "JSON", report_spec: str | dict = None
    ) -> dict | str:
        """Retrieve the profile details of the user associated with the token.

        Parameters
        ----------
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Returns
        -------
        dict | str
            A dictionary containing the profile details or formatted output.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_profile(output_format, report_spec)
        )

    @dynamic_catch
    async def _async_add_my_profile(
        self, body: dict | NewElementRequestBody
    ) -> str:
        """Add a profile for the user. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            A dictionary or NewElementRequestBody containing the profile properties.

        Returns
        -------
        str
            The GUID of the created profile.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Example body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "PersonProperties",
            "qualifiedName": "puddy1",
            "displayName": "Puddy",
            "courtesyTitle" : "Miss",
            "initials" : "",
            "givenNames" : "Hey You",
            "surname" : "Cat",
            "fullName" : "Puddy",
            "pronouns" : "",
            "jobTitle" : "Troublemaker",
            "employeeNumber" : "",
            "employeeType" : "",
            "preferredLanguage" : "",
            "residentCountry" : "",
            "timeZone" : "",
            "description": "Wanderer",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        url = f"{self.my_profile_command_root}"
        return await self._async_create_element_body_request(url, ["PersonProperties"], body)

    @dynamic_catch
    def add_my_profile(self, body: dict | NewElementRequestBody) -> str:
        """Add a profile for the user.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            A dictionary or NewElementRequestBody containing the profile properties.

        Returns
        -------
        str
            The GUID of the created profile.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Example body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "PersonProperties",
            "qualifiedName": "puddy1",
            "displayName": "Puddy",
            "courtesyTitle" : "Miss",
            "initials" : "",
            "givenNames" : "Hey You",
            "surname" : "Cat",
            "fullName" : "Puddy",
            "pronouns" : "",
            "jobTitle" : "Troublemaker",
            "employeeNumber" : "",
            "employeeType" : "",
            "preferredLanguage" : "",
            "residentCountry" : "",
            "timeZone" : "",
            "description": "Wanderer",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(self._async_add_my_profile(body))

    @dynamic_catch
    async def _async_get_my_actors(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of actors linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors"
        return await self._async_get_request_body_request(
            url,
            _type="ActorProfile",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_actors(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of actors linked to the user's profile.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_actors(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_user_identities(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of user identities linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors/user-identities"
        return await self._async_get_request_body_request(
            url,
            _type="UserIdentity",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_user_identities(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of user identities linked to the user's profile.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_user_identities(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_roles(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned roles linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors/assigned-roles"
        return await self._async_get_request_body_request(
            url,
            _type="GovernanceRole",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_roles(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned roles linked to the user's profile.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_roles(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_resources(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned resources linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        url = f"{self.my_profile_command_root}/assigned-resources"
        return await self._async_get_request_body_request(
            url,
            _type="Resource",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_resources(
        self,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned resources linked to the user's profile.

        Parameters
        ----------
        body : dict | GetRequestBody, optional
            A dict or GetRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_resources(body, output_format, report_spec)
        )



    # async def _async_get_assigned_actions(
    #     self,
    #     actor_guid: str,
    #     status: str = "OPEN",
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    # ) -> list | str:
    #     """Get assigned actions for the actor. Async version.
    #
    #     Parameters
    #     ----------
    #     actor_guid: str
    #         The GUID of the actor whose assigned actions are to be retrieved.
    #     status: str
    #         The status of teh action to filter on. Default value is "OPEN".
    #
    #     start_from: int, optional
    #         The index from which to start retrieving the assigned actions. Default is 0.
    #     page_size: int, optional
    #         The number of assigned actions to retrieve per page. Default is 100.
    #
    #     Returns
    #     -------
    #     list or str
    #         A list of assigned actions is returned. If there aren't any, a string is returned indicating that.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #       If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #       Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #       The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     if page_size is None:
    #         page_size = self.page_size
    #
    #     body = {"status": status}
    #
    #     url = (
    #         f"{self.my_profile_command_root}/actors/{actor_guid}"
    #         f"/assigned/to-dos?startFrom={start_from}&pageSize={page_size}"
    #     )
    #
    #     response = await self._async_make_request("POST", url, body)
    #
    #     elements = response.json().get("elements", "No entries found")
    #     if output_format != "JSON" and not isinstance(elements, str):
    #         return self._generate_referenceable_output(
    #             elements, actor_guid, "ToDo", output_format, report_spec
    #         )
    #     return elements
    #
    # def get_assigned_actions(
    #     self,
    #     actor_guid: str,
    #     status: str = "OPEN",
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    # ) -> list | str:
    #     """Get assigned actions for the actor.
    #     Parameters
    #     ----------
    #     actor_guid: str
    #         The GUID of the actor whose assigned actions are to be retrieved.
    #     status: str
    #         The status of teh action to filter on. Default value is "OPEN".
    #
    #     start_from: int, optional
    #         The index from which to start retrieving the assigned actions. Default is 0.
    #     page_size: int, optional
    #         The number of assigned actions to retrieve per page. Default is 100.
    #
    #     Returns
    #     -------
    #     list or str
    #         A list of assigned actions is returned. If there aren't any, a string is returned indicating that.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #       If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #       Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #       The principle specified by the user_id does not have authorization for the requested action
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(
    #         self._async_get_assigned_actions(
    #             actor_guid, status, start_from, page_size, output_format, report_spec
    #         )
    #     )
    #
    #     return response
    #
    # async def _async_get_actions_for_action_target(
    #     self,
    #     element_guid: str,
    #     status: str = "OPEN",
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    #     ) -> list | str:
    #     """Get actions assigned to the action target. Async version.
    #
    #     Parameters
    #     ----------
    #     element_guid: str
    #         The GUID of the target whose assigned actions are to be retrieved.
    #     status: str
    #         The status of teh action to filter on. Default value is "OPEN".
    #
    #     start_from: int, optional
    #         The index from which to start retrieving the assigned actions. Default is 0.
    #     page_size: int, optional
    #         The number of assigned actions to retrieve per page. Default is 100.
    #
    #     Returns
    #     -------
    #     list or str
    #         A list of assigned actions is returned. If there aren't any, a string is returned indicating that.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #       If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #       Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #       The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     validate_name(element_guid)
    #
    #     body = {"status": status}
    #
    #     url = (
    #         f"{self.my_profile_command_root}/elements/{element_guid}"
    #         f"/action-targets/to-dos?startFrom={start_from}&pageSize={page_size}"
    #     )
    #
    #     response = await self._async_make_request("POST", url, body)
    #     elements = response.json() if response is not None else "No Results"
    #     if output_format != "JSON" and not isinstance(elements, str):
    #         return self._generate_referenceable_output(
    #             elements, element_guid, "ToDo", output_format, report_spec
    #         )
    #     return elements
    #
    # def get_actions_for_action_target(
    #     self,
    #     element_guid: str,
    #     status: str = "OPEN",
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    # ) -> list | str:
    #     """Get actions assigned to the action target.
    #
    #     Parameters
    #     ----------
    #     element_guid: str
    #         The GUID of the target whose assigned actions are to be retrieved.
    #     status: str
    #         The status of teh action to filter on. Default value is "OPEN"
    #
    #     start_from: int, optional
    #         The index from which to start retrieving the assigned actions. Default is 0.
    #     page_size: int, optional
    #         The number of assigned actions to retrieve per page. Default is 100.
    #
    #     Returns
    #     -------
    #     list or str
    #         A list of assigned actions is returned. If there aren't any, a string is returned indicating that.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #       If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #       Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #       The principle specified by the user_id does not have authorization for the requested action
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(
    #         self._async_get_actions_for_action_target(
    #             element_guid, status, start_from, page_size, output_format, report_spec
    #         )
    #     )
    #
    #     return response

    #
    # Lifecycle
    #
    # async def _async_create_person_action(self, body: dict) -> str:
    #     """Create a person action (Meeting, ToDo, Notification, Review). Async version.
    #
    #     Parameters
    #     ----------
    #     body : dict
    #         The dictionary containing the details of the action.
    #
    #     Returns
    #     -------
    #     GUID
    #         GUID of the person action
    #
    #     Raises
    #     ------
    #     PyegeriaException
    #
    #     ValidationError
    #
    #     Notes
    #     _____
    #
    #     This method can be used to create a person action. The type of person action depends on the "Class" element
    #     in the body. Here are brief examples of bodies:
    #
    #     {
    #       "class" : "NewElementRequestBody",
    #       "isOwnAnchor": true,
    #       "properties": {
    #         "class" : "Meeting",
    #         "qualifiedName": "add unique name here",
    #         "displayName": "add short name here",
    #         "description": "add description here",
    #         "situation": "add situation here",
    #         "objective": "add objective here",
    #         "minutes": "add minutes here",
    #         "decisions": "add decisions here"
    #         }
    #     }
    #
    #     {
    #       "class" : "NewElementRequestBody",
    #       "isOwnAnchor": true,
    #       "properties": {
    #         "class" : "ToDo",
    #         "qualifiedName": "add unique name here",
    #         "displayName": "add short name here",
    #         "description": "add description here",
    #         "situation": "add situation here"
    #         }
    #     }
    #
    #     {
    #       "class" : "NewElementRequestBody",
    #       "isOwnAnchor": true,
    #       "properties": {
    #         "class" : "Notification",
    #         "qualifiedName": "add unique name here",
    #         "displayName": "add short name here",
    #         "description": "add description here",
    #         "situation": "add situation here"
    #         }
    #     }
    #
    #     {
    #       "class" : "NewElementRequestBody",
    #       "isOwnAnchor": true,
    #       "properties": {
    #         "class" : "Review",
    #         "qualifiedName": "add unique name here",
    #         "displayName": "add short name here",
    #         "description": "add description here",
    #         "situation": "add situation here",
    #         "reviewDate": "add date here",
    #         "comment": "add comment here"
    #         }
    #     }
    #     """
    #
    #     response = await super().create_asset(["Meeting","Todo","Notification","Review"], body)
    #     return response.json().get("guid", "No guid returned")
    #
    # def create_person_action(self, body: dict) -> str:
    #     """Create a person action (Meeting, ToDo, Notification, Review).
    #         Parameters
    #         ----------
    #         body : dict
    #             The dictionary containing the details of the to-do item.
    #
    #         Returns
    #         -------
    #         None
    #             This method does not return any value.
    #
    #         Raises
    #         ------
    #         PyegeriaInvalidParameterException
    #           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #         PyegeriaAPIException
    #           Raised by the server when an issue arises in processing a valid request
    #         NotAuthorizedException
    #           The principle specified by the user_id does not have authorization for the requested action
    #
    #         Notes
    #         -----
    #
    #         {
    #           "class" : "NewElementRequestBody",
    #           "isOwnAnchor": true,
    #           "properties": {
    #             "class" : "Meeting",
    #             "qualifiedName": "add unique name here",
    #             "displayName": "add short name here",
    #             "description": "add description here",
    #             "situation": "add situation here",
    #             "objective": "add objective here",
    #             "minutes": "add minutes here",
    #             "decisions": "add decisions here"
    #             }
    #         }
    #
    #         {
    #           "class" : "NewElementRequestBody",
    #           "isOwnAnchor": true,
    #           "properties": {
    #             "class" : "ToDo",
    #             "qualifiedName": "add unique name here",
    #             "displayName": "add short name here",
    #             "description": "add description here",
    #             "situation": "add situation here"
    #             }
    #         }
    #
    #         {
    #           "class" : "NewElementRequestBody",
    #           "isOwnAnchor": true,
    #           "properties": {
    #             "class" : "Notification",
    #             "qualifiedName": "add unique name here",
    #             "displayName": "add short name here",
    #             "description": "add description here",
    #             "situation": "add situation here"
    #             }
    #         }
    #
    #         {
    #           "class" : "NewElementRequestBody",
    #           "isOwnAnchor": true,
    #           "properties": {
    #             "class" : "Review",
    #             "qualifiedName": "add unique name here",
    #             "displayName": "add short name here",
    #             "description": "add description here",
    #             "situation": "add situation here",
    #             "reviewDate": "add date here",
    #             "comment": "add comment here"
    #             }
    #         }
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_create_person_action(body))
    #     return response
    #
    #
    # async def _async_update_person_action(self, action_guid: str, body: dict | UpdateElementRequestBody) -> None:
    #     """Update a person action.  Note that this is a facade over update_asset. Async version.
    #     Parameters
    #     ----------
    #     action_guid: str
    #       Identifier of the person action.
    #     body: dict | UpdateElementRequestBody
    #         The details to update the person action with.
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #         One of the parameters is null or invalid (for example, bad URL or invalid values).
    #     PyegeriaAPIException
    #         The server reported an error while processing a valid request.
    #     PyegeriaUnauthorizedException
    #         The requesting user is not authorized to issue this request.
    #     """
    #
    #     validate_name(action_guid)
    #
    #     await self._async_make_request("POST", url, body)
    #     return
    #
    # def update_to_do(
    #     self,
    #     todo_guid: str,
    #     body: dict,
    #     is_merge_update: bool = True,
    # ) -> None:
    #     """Update a To-Do item.
    #     Parameters
    #     ----------
    #     todo_guid: str
    #       Identifier of the To-Do item.
    #     body: str
    #         The details to update the to-do item with.
    #     is_merge_update: bool [default: True]
    #         If true then merges the updated information, otherwise replace the existing information.
    #
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(
    #         self._async_update_person_action(todo_guid, body)
    #     )
    #     return
    #
    # async def _async_delete_to_do(self, todo_guid: str) -> None:
    #     """Delete a To-Do item. Async version.
    #     Parameters
    #     ----------
    #     todo_guid: str
    #       Identifier of the To-Do item.
    #
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     validate_name(todo_guid)
    #
    #     url = f"{self.my_profile_command_root}/to-dos/{todo_guid}/delete"
    #
    #     await self._async_make_request("POST", url)
    #     return
    #
    # def delete_to_do(self, todo_guid: str) -> None:
    #     """Delete a To-Do item.
    #     Parameters
    #     ----------
    #     todo_guid: str
    #       Identifier of the To-Do item.
    #
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self._async_delete_to_do(todo_guid))
    #     return
    #
    # async def _async_reassign_to_do(
    #     self,
    #     todo_guid: str,
    #     actor_guid: str,
    #     status: str = "OPEN",
    # ) -> None:
    #     """Reassign a To-Do item. Async version.
    #     Parameters
    #     ----------
    #      todo_guid: str
    #          Identifier of the To-Do item.
    #      actor_guid: str
    #          The actor to receive the reassigned to-do item.
    #      status: str [default = "OPEN"]
    #          Filter items to match this status.
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     validate_name(todo_guid)
    #     validate_name(actor_guid)
    #     body = {"status": status}
    #
    #     url = (
    #         f"{self.my_profile_command_root}/to-dos/{todo_guid}/reassign/{actor_guid}"
    #     )
    #
    #     await self._async_make_request("POST", url, body)
    #     return
    #
    # def reassign_to_do(
    #     self,
    #     todo_guid: str,
    #     actor_guid: str,
    #     status: str = "OPEN",
    # ) -> None:
    #     """Reassign a To-Do item.
    #     Parameters
    #     ----------
    #      todo_guid: str
    #          Identifier of the To-Do item.
    #      actor_guid: str
    #          The actor to receive the reassigned to-do item.
    #      status: str [default = "OPEN"]
    #          Filter items to match this status.
    #
    #     Returns
    #     -------
    #     None
    #      This method does not return any value.
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(
    #         self._async_reassign_to_do(todo_guid, actor_guid, status)
    #     )
    #     return

    # async def _async_find_to_do(
    #     self,
    #     search_string: str = "*",
    #     starts_with: bool = False,
    #     ends_with: bool = False,
    #     ignore_case: bool = True,
    #     anchor_domain: Optional[str] = None,
    #     metadata_element_type: Optional[str] = None,
    #     metadata_element_subtypes: list[str] = ["ToDo", "Notification", "Review", "Meeting"],
    #     skip_relationships: Optional[list[str]] = None,
    #     include_only_relationships: Optional[list[str]] = None,
    #     skip_classified_elements: Optional[list[str]] = None,
    #     include_only_classified_elements: Optional[list[str]] = None,
    #     graph_query_depth: int = 3,
    #     governance_zone_filter: Optional[list[str]] = None,
    #     as_of_time: Optional[str] = None,
    #     effective_time: Optional[str] = None,
    #     relationship_page_size: int = 0,
    #     limit_results_by_status: Optional[list[str]] = None,
    #     sequencing_order: Optional[str] = None,
    #     sequencing_property: Optional[str] = None,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     property_names: Optional[list[str]] = None,
    #     body: Optional[dict | SearchStringRequestBody] = None,
    # ) -> list | str:
    #     """find To-Do items. Async version.
    #     Parameters
    #     ----------
    #       search_string: str
    #          String to search against. If '*' then all to-do items will match.
    #       starts_with : bool, [default=False], optional
    #          Starts with the supplied string.
    #       ends_with : bool, [default=False], optional
    #              Ends with the supplied string
    #       ignore_case : bool, [default=False], optional
    #              Ignore case when searching
    #     Returns
    #     -------
    #     None
    #      List of To-Do items that match the criteria
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #
    #     url = f"{self.my_profile_command_root}/to-dos/find-by-search-string"
    #
    #     return await self._async_find_request(
    #         url,
    #         _type="ToDo",
    #         _gen_output=self._generate_referenceable_output,
    #         search_string=search_string,
    #         starts_with=starts_with,
    #         ends_with=ends_with,
    #         ignore_case=ignore_case,
    #         anchor_domain=anchor_domain,
    #         metadata_element_type=metadata_element_type,
    #         metadata_element_subtypes=metadata_element_subtypes,
    #         skip_relationships=skip_relationships,
    #         include_only_relationships=include_only_relationships,
    #         skip_classified_elements=skip_classified_elements,
    #         include_only_classified_elements=include_only_classified_elements,
    #         graph_query_depth=graph_query_depth,
    #         governance_zone_filter=governance_zone_filter,
    #         as_of_time=as_of_time,
    #         effective_time=effective_time,
    #         relationship_page_size=relationship_page_size,
    #         limit_results_by_status=limit_results_by_status,
    #         sequencing_order=sequencing_order,
    #         sequencing_property=sequencing_property,
    #         output_format=output_format,
    #         report_spec=report_spec,
    #         start_from=start_from,
    #         page_size=page_size,
    #         property_names=property_names,
    #         body=body,
    #     )
    #
    # def find_to_do(
    #     self,
    #     search_string: str = "*",
    #     starts_with: bool = False,
    #     ends_with: bool = False,
    #     ignore_case: bool = True,
    #     anchor_domain: Optional[str] = None,
    #     metadata_element_type: Optional[str] = None,
    #     metadata_element_subtypes: list[str] = ["ToDo", "Notification", "Review", "Meeting"],
    #     skip_relationships: Optional[list[str]] = None,
    #     include_only_relationships: Optional[list[str]] = None,
    #     skip_classified_elements: Optional[list[str]] = None,
    #     include_only_classified_elements: Optional[list[str]] = None,
    #     graph_query_depth: int = 3,
    #     governance_zone_filter: Optional[list[str]] = None,
    #     as_of_time: Optional[str] = None,
    #     effective_time: Optional[str] = None,
    #     relationship_page_size: int = 0,
    #     limit_results_by_status: Optional[list[str]] = None,
    #     sequencing_order: Optional[str] = None,
    #     sequencing_property: Optional[str] = None,
    #     output_format: str = "JSON",
    #     report_spec: str | dict = None,
    #     start_from: int = 0,
    #     page_size: int = 100,
    #     property_names: Optional[list[str]] = None,
    #     body: Optional[dict | SearchStringRequestBody] = None,
    # ) -> list | str:
    #     """find To-Do items.
    #        Parameters
    #        ----------
    #       search_string: str
    #          String to search against. If '*' then all to-do items will match.
    #       starts_with : bool, [default=False], optional
    #          Starts with the supplied string.
    #       ends_with : bool, [default=False], optional
    #              Ends with the supplied string
    #       ignore_case : bool, [default=False], optional
    #              Ignore case when searching
    #        start_from: int, [default=0], optional
    #            When multiple pages of results are available, the page number to start from.
    #        page_size: int, [default=100]
    #            The number of items to return in a single page.
    #     Returns
    #     -------
    #     None
    #      List of To-Do items that match the criteria
    #
    #     Raises
    #     ------
    #     PyegeriaInvalidParameterException
    #     If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PyegeriaAPIException
    #     Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException
    #     The principle specified by the user_id does not have authorization for the requested action
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(
    #         self._async_find_to_do(
    #             search_string=search_string,
    #             starts_with=starts_with,
    #             ends_with=ends_with,
    #             ignore_case=ignore_case,
    #             anchor_domain=anchor_domain,
    #             metadata_element_type=metadata_element_type,
    #             metadata_element_subtypes=metadata_element_subtypes,
    #             skip_relationships=skip_relationships,
    #             include_only_relationships=include_only_relationships,
    #             skip_classified_elements=skip_classified_elements,
    #             include_only_classified_elements=include_only_classified_elements,
    #             graph_query_depth=graph_query_depth,
    #             governance_zone_filter=governance_zone_filter,
    #             as_of_time=as_of_time,
    #             effective_time=effective_time,
    #             relationship_page_size=relationship_page_size,
    #             limit_results_by_status=limit_results_by_status,
    #             sequencing_order=sequencing_order,
    #             sequencing_property=sequencing_property,
    #             output_format=output_format,
    #             report_spec=report_spec,
    #             start_from=start_from,
    #             page_size=page_size,
    #             property_names=property_names,
    #             body=body,
    #         )
    #     )
    #     return response
    #






if __name__ == "__main__":
    print("Main-My Profile")

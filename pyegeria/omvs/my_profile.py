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
from pyegeria.view.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.view.output_formatter import (populate_common_columns, resolve_output_formats, materialize_egeria_summary, select_report_format)
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

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str | None = None,
        user_pwd: str | None = None,
        token: str | None = None,
        aggregation_depth: int = 3,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.aggregation_depth = aggregation_depth
        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )
        self.my_profile_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/my-profile"
        )

    def _find_nested_elements(
        self,
        summary_list: list,
        target_type: str,
        spec: dict,
        max_depth: int = 3,
        current_depth: int = 0,
        seen_guids: Optional[set] = None,
    ) -> list:
        """
        Recursively find nested elements of a specific type within a list of summaries.
        Deduplicates by GUID. Checks both type name and supertype names.
        """
        if seen_guids is None:
            seen_guids = set()

        found = []
        if current_depth >= max_depth:
            return found

        for s in summary_list:
            if not isinstance(s, dict):
                continue

            rel_el = s.get("relatedElement") or {}
            header = rel_el.get("elementHeader") or {}
            guid = header.get("guid")

            header_type = header.get("type") or {}
            type_name = header_type.get("typeName")
            super_types = header_type.get("superTypeNames") or []

            # 1. Check this element
            if type_name == target_type or target_type in super_types:
                if not guid or guid not in seen_guids:
                    found.append(materialize_egeria_summary(s, spec))
                    if guid:
                        seen_guids.add(guid)

            # 2. Recurse into nested elements
            nested = s.get("nestedElements") or []
            if isinstance(nested, list) and nested:
                found.extend(
                    self._find_nested_elements(
                        nested,
                        target_type,
                        spec,
                        max_depth,
                        current_depth + 1,
                        seen_guids,
                    )
                )

        return found

    def _extract_my_profile_properties(self, element: dict, columns_struct: dict) -> dict:
        """Extractor for My Profile (Person) elements."""
        col_data = populate_common_columns(element, columns_struct)

        # Pre-fetch collections once to avoid redundant work
        performs_roles = element.get("performsRoles") or []
        contact_details = element.get("contactDetails") or []
        user_identities = element.get("userIdentities") or []

        try:
            formats = col_data.get("formats")
            if isinstance(formats, dict):
                attributes = formats.get("attributes", [])
            elif isinstance(formats, list):
                attributes = formats[0].get("attributes", []) if formats else []
            else:
                attributes = []

            for column in attributes:
                key = column.get("key")
                if not key:
                    continue

                try:
                    if key == "user_id":
                        if user_identities and isinstance(user_identities, list):
                            props = (user_identities[0].get("relatedElement") or {}).get("properties") or {}
                            column["value"] = props.get("userId")

                    elif key == "contact_methods":
                        if isinstance(contact_details, list):
                            # Resolve the spec for this column to enable generic promotion (DICT -> LIST -> REPORT -> ALL)
                            ds_name = column.get("detail_spec")
                            spec = None
                            if ds_name:
                                spec = (
                                    select_report_format(ds_name, "DICT")
                                    or select_report_format(ds_name, "LIST")
                                    or select_report_format(ds_name, "REPORT")
                                    or select_report_format(ds_name, "ALL")
                                )
                            # Use recursive finder with max_depth=1 for top-level collections to benefit from deduplication
                            if spec and spec.get("target_type"):
                                column["value"] = self._find_nested_elements(
                                    contact_details, spec.get("target_type"), spec, max_depth=1
                                )
                            else:
                                column["value"] = [
                                    materialize_egeria_summary(c, spec) for c in contact_details
                                ]

                    elif key == "roles":
                        if isinstance(performs_roles, list):
                            ds_name = column.get("detail_spec")
                            spec = None
                            if ds_name:
                                spec = (
                                    select_report_format(ds_name, "DICT")
                                    or select_report_format(ds_name, "LIST")
                                    or select_report_format(ds_name, "REPORT")
                                    or select_report_format(ds_name, "ALL")
                                )
                            # Deduplicate roles using recursion depth 1
                            if spec and spec.get("target_type"):
                                column["value"] = self._find_nested_elements(
                                    performs_roles, spec.get("target_type"), spec, max_depth=1
                                )
                            else:
                                column["value"] = [
                                    materialize_egeria_summary(r, spec) for r in performs_roles
                                ]

                    # Generic handler for elements nested within roles (e.g., teams, communities, projects)
                    elif column.get("detail_spec") and column.get("value") in (None, "", []):
                        ds_name = column.get("detail_spec")
                        spec = (
                            select_report_format(ds_name, "DICT")
                            or select_report_format(ds_name, "LIST")
                            or select_report_format(ds_name, "REPORT")
                            or select_report_format(ds_name, "ALL")
                        )

                        if spec and spec.get("target_type"):
                            target_type = spec.get("target_type")
                            found_elements = self._find_nested_elements(
                                performs_roles,
                                target_type,
                                spec,
                                max_depth=self.aggregation_depth,
                            )
                            if found_elements:
                                column["value"] = found_elements
                except Exception as e:
                    logger.error(f"Error processing profile column '{key}': {e}")

        except Exception as e:
            logger.error(f"Critical error in _extract_my_profile_properties: {e}")

        return col_data



    def _generate_my_profile_output(
            self,
            elements: dict | list[dict],
            filter_string: Optional[str] = "My",
            element_type_name: Optional[str] = "Actor",
            output_format: str = "JSON",
            report_spec: dict | str | None = "My-User-MD",
            **kwargs,
    ) -> str | list[dict]:
        """ Generate output for my_profile in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """

        entity_type = element_type_name if element_type_name else "Actor"
        logger.trace(f"Executing generate_actor_role_output for {entity_type}")
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            element_type_name=entity_type,
            output_format=output_format,
            report_spec=report_spec,
            extract_properties_func=self._extract_my_profile_properties,
            **kwargs,
        )


    @dynamic_catch
    async def _async_get_my_profile(
            self, body: dict | GetRequestBody | None = None, output_format: str = "JSON",
            report_spec: str | dict = "My-User-MD"
    ) -> dict | str:
        """Retrieve the profile details of the user associated with the token. Async version.

        Parameters
        ----------
        body: dict | GetRequestBody | None
            - details of the request body, including filters and options for the profile retrieval.
        output_format: str, default = "JSON"
            - specifying the format of the response (JSON, DICT, REPORT, LIST, FORM, MERMAID).
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
        response = await self._async_get_request_body_request(url=url, _type="Actor",
                                                              _gen_output=self._generate_my_profile_output,
                                                              output_format=output_format, report_spec=report_spec,
                                                              body=body)

        return response

    @dynamic_catch
    def get_my_profile(
        self, body: dict | GetRequestBody | None = None, output_format: str = "JSON", report_spec: str | dict = "My-User-MD"
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
            self._async_get_my_profile(body, output_format, report_spec)
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
        return await self._async_get_request_body_request(url, _type="ActorProfile",
                                                          _gen_output=self._generate_my_profile_output,
                                                          output_format=output_format, report_spec=report_spec,
                                                          body=body)

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
        return await self._async_get_request_body_request(url, _type="UserIdentity",
                                                          _gen_output=self._generate_my_profile_output,
                                                          output_format=output_format, report_spec=report_spec,
                                                          body=body)

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
        return await self._async_get_request_body_request(url, _type="GovernanceRole",
                                                          _gen_output=self._generate_my_profile_output,
                                                          output_format=output_format, report_spec=report_spec,
                                                          body=body)

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
        return await self._async_get_request_body_request(url, _type="Resource",
                                                          _gen_output=self._generate_my_profile_output,
                                                          output_format=output_format, report_spec=report_spec,
                                                          body=body)

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

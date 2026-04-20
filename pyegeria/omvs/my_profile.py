"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the MyProfile class and its methods.

"""
import json
import time

from loguru import logger
from typing import Any, Optional

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.core._validators import validate_name
from pyegeria.core.utils import dynamic_catch, body_slimmer
from pyegeria.models import (
    GetRequestBody,
    NewElementRequestBody,
    SearchStringRequestBody,
    UpdateElementRequestBody, ActionRequestBody,
    ActivityStatusRequestBody,
    NewAttachmentRequestBody,
    ResultsRequestBody,
)
from pyegeria.view.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.view.output_formatter import (populate_common_columns, resolve_output_formats, materialize_egeria_summary, select_report_format)
import asyncio


class MyProfile(AssetMaker):
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
        view_server: str = None,
        platform_url: str = None,
        user_id: str | None = None,
        user_pwd: str | None = None,
        token: str | None = None,
        aggregation_depth: int = 3,
    ):
        AssetMaker.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )
        self.view_server = self.server_name
        self.platform_url = self.platform_url
        self.user_id = self.user_id
        self.user_pwd = self.user_pwd
        self.aggregation_depth = aggregation_depth
        self.my_profile_guid: str | None = None


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

    def _extract_entry(self, el_summary: dict) -> Optional[dict]:
        """Extract properties and time from an entry summary."""
        rel_el = el_summary.get("relatedElement")
        if not rel_el:
            return None

        header = rel_el.get("elementHeader")
        if not header:
            return None

        type_info = header.get("type")
        if not type_info:
            return None

        type_name = type_info.get("typeName")
        super_types = type_info.get("superTypeNames") or []

        if type_name != "Notification" and "Notification" not in super_types:
            return None

        properties = rel_el.get("properties") or {}
        versions = header.get("versions")
        create_time = versions.get("createTime") if versions else None

        res = properties.copy()
        res["time"] = create_time

        # Ensure title and text are populated from fallbacks if needed
        if res.get("title") is None:
            res["title"] = res.get("displayName")
        if res.get("text") is None:
            res["text"] = res.get("description")

        return res

    def _extract_note_log_entries(self, note_logs: list, type_suffix: str = None) -> list[dict]:
        """Extract entries from note logs, optionally filtered by qualifiedName suffix."""
        entries = []
        for nl in note_logs:
            nl_rel = nl.get("relatedElement") or {}
            nl_props = nl_rel.get("properties") or {}
            nl_qn = nl_props.get("qualifiedName", "")

            if type_suffix and not nl_qn.endswith(type_suffix):
                continue

            nested = nl.get("nestedElements") or []
            for n in nested:
                entry = self._extract_entry(n)
                if entry:
                    entries.append(entry)
        return entries

    def _extract_my_profile_properties(self, element: dict, columns_struct: dict) -> dict:
        """Extractor for My Profile (Person) elements."""
        contribution_record = element.get("contributionRecord") or []
        col_data = populate_common_columns(element, columns_struct)

        # Pre-fetch collections once to avoid redundant work
        performs_roles = element.get("performsRoles") or []
        contact_details = element.get("contactDetails") or []
        user_identities = element.get("userIdentities") or []
        note_logs = element.get("noteLogs") or []

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
                    elif key == "contribution_record":
                        if isinstance(contribution_record, list):
                            ds_name = column.get("detail_spec")
                            spec = select_report_format(ds_name, "DICT")  # or other formats
                            if spec and spec.get("target_type"):
                                column["value"] = self._find_nested_elements(
                                    contribution_record, spec.get("target_type"), spec, max_depth=1
                                )
                            else:
                                column["value"] = [materialize_egeria_summary(c, spec) for c in contribution_record]

                    elif key == "note_logs":
                        column["value"] = self._extract_note_log_entries(note_logs)

                    elif key == "activity_entries":
                        column["value"] = self._extract_note_log_entries(note_logs, "::MyActivity")

                    elif key == "blog_entries":
                        column["value"] = self._extract_note_log_entries(note_logs, "::MyBlog")

                    elif key == "journal_entries":
                        column["value"] = self._extract_note_log_entries(note_logs, "::MyJournal")

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
            report_spec: str | dict = "My-User-MD",**kwargs
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
        # response = await self._async_get_request_body_request(url=url, _type="Actor",
        #                                                       _gen_output=self._generate_my_profile_output,
        #                                                       output_format=output_format, report_spec=report_spec,
        #                                                       body=body,**kwargs)
        if body is None:
            response = await self._async_make_request("POST", url)
        else:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if isinstance(elements, dict):
            self.my_profile_guid = elements.get("elementHeader", {}).get("guid")
        else:
            self.my_profile_guid = None
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_my_profile_output(elements, "My", "MyProfile", output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_get_my_entries(self) -> list[dict]:
        """Retrieve all activity entries (journal, blog, log) for the user. Async version.

        This method extracts entries from 'noteLogs' (via 'nestedElements') and 'requestedActions'.
        It focuses on elements of type 'Notification'.

        Returns
        -------
        list[dict]
            A list of dictionaries, each containing 'properties' and 'time' for an entry.
        """
        profile = await self._async_get_my_profile(output_format="JSON")
        if profile == NO_ELEMENTS_FOUND:
            return []

        entries = []

        # 1. Extract from requestedActions
        requested_actions = profile.get("requestedActions") or []
        for action in requested_actions:
            entry = self._extract_entry(action)
            if entry:
                entries.append(entry)

        # 2. Extract from noteLogs -> nestedElements
        note_logs = profile.get("noteLogs") or []
        entries.extend(self._extract_note_log_entries(note_logs))

        return entries

    @dynamic_catch
    def get_my_entries(self) -> list[dict]:
        """Retrieve all activity entries (journal, blog, log) for the user.

        Returns
        -------
        list[dict]
            A list of dictionaries, each containing 'properties' and 'time' for an entry.
        """
        return asyncio.get_event_loop().run_until_complete(self._async_get_my_entries())

    @dynamic_catch
    def get_my_profile(
        self, body: dict | GetRequestBody | None = None, output_format: str = "JSON",
            report_spec: str | dict = "My-User-MD",**kwargs
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
            self._async_get_my_profile(body, output_format, report_spec,**kwargs)
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
        url = f"{self.my_profile_command_root}/new"
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
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of actors linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors"
        return await self._async_get_results_body_request(
            url,
            _type="ActorProfile",
            _gen_output=self._generate_my_profile_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_actors(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of actors linked to the user's profile.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_actors(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_user_identities(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of user identities linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors/user-identities"
        return await self._async_get_results_body_request(
            url,
            _type="UserIdentity",
            _gen_output=self._generate_my_profile_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_user_identities(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of user identities linked to the user's profile.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_user_identities(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_roles(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned roles linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        url = f"{self.my_profile_command_root}/actors/assigned-roles"
        return await self._async_get_results_body_request(
            url,
            _type="GovernanceRole",
            _gen_output=self._generate_my_profile_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_roles(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned roles linked to the user's profile.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_roles(body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_my_resources(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned resources linked to the user's profile. Async version.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        ```
        """
        url = f"{self.my_profile_command_root}/assigned-resources?includeUserIds=true&includeRoles=true"
        return await self._async_get_results_body_request(
            url,
            _type="Resource",
            _gen_output=self._generate_my_profile_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_my_resources(
        self,
        body: dict | ResultsRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | str:
        """Return the list of assigned resources linked to the user's profile.

        Parameters
        ----------
        body : dict | ResultsRequestBody, optional
            A dict or ResultsRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "ResultsRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "startFrom": 0,
          "pageSize": 0
        }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_my_resources(body, output_format, report_spec)
        )



    @dynamic_catch
    async def _async_get_my_assigned_actions(
        self,
        metadata_element_type: Optional[str] = "Action",
        metadata_element_subtypes: Optional[list[str]] = [],
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get assigned actions for the user profile. Async version.

        Parameters
        ----------
        metadata_element_type : str, default = "Action"

        metadtata_element_subtypes : list[str], default = []
            The subtypes of the metadata element to filter on.
        activity_status_list: list[str], default = ["REQUESTED", "WAITING", "IN_PROGRESS"]
            The status of the action to filter on.
        start_from: int, default = 0
            The index from which to start retrieving the actions.
        page_size: int, default = 0
            The number of actions to retrieve per page.
        body: dict | ActivityStatusRequestBody, optional
            A dict or ActivityStatusRequestBody representing the request options.
        output_format: str, default = "JSON"
            - one of "DICT", "JSON"
        report_spec: str | dict, optional, default = None
            - The desired output columns/field options.

        Returns
        -------
        list or str
            A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

        """
        url = f"{self.my_profile_command_root}/assigned-actions?includeUserIds=true&includeRoles=true"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            metadata_element_type=metadata_element_type,
            metadtata_element_subtypes=metadata_element_subtypes,
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def get_my_assigned_actions(
        self,
        metadata_element_type: Optional[str] = "Action",
        metadata_element_subtypes: list[str] = [],
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get assigned actions for the user profile.

        Args:
            metadata_element_subtypes ():
            metadata_element_type ():
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_my_assigned_actions(metadata_element_type=metadata_element_type,
                                                metadata_element_subtypes=metadata_element_subtypes,
                                                activity_status_list=activity_status_list, start_from=start_from,
                                                page_size=page_size, limit_results_by_status=limit_results_by_status,
                                                sequencing_order=sequencing_order,
                                                sequencing_property=sequencing_property, body=body,
                                                output_format=output_format, report_spec=report_spec, **kwargs)
        )

    @dynamic_catch
    async def _async_get_my_sponsored_actions(
        self,
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get actions sponsored by the user profile. Async version."""
        url = f"{self.my_profile_command_root}/sponsored-actions?includeUserIds=true&includeRoles=true"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def get_my_sponsored_actions(
        self,
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get actions sponsored by the user profile."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_my_sponsored_actions(
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_my_requested_actions(
        self,
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get actions requested by the user profile. Async version."""
        url = f"{self.my_profile_command_root}/requested-actions?includeUserIds=true&includeRoles=true"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def get_my_requested_actions(
        self,
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs,
    ) -> list | str:
        """Get actions requested by the user profile."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_my_requested_actions(
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_log_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's activity log. Async version."""
        url = f"{self.my_profile_command_root}/log-my-activity"
        return await self._async_create_attachment_body_request(url, ["NotificationProperties"], body)

    @dynamic_catch
    def log_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's activity log."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_log_my_activity(body))

    @dynamic_catch
    async def _async_journal_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's journal. Async version."""
        url = f"{self.my_profile_command_root}/journal-my-activity"
        return await self._async_create_attachment_body_request(url, ["NotificationProperties"], body)

    @dynamic_catch
    def journal_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's journal."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_journal_my_activity(body))

    @dynamic_catch
    async def _async_blog_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's blog. Async version."""
        url = f"{self.my_profile_command_root}/blog-my-activity"
        return await self._async_create_attachment_body_request(url, ["NotificationProperties"], body)

    @dynamic_catch
    def blog_my_activity(self, body: Optional[dict | NewAttachmentRequestBody] = None) -> str:
        """Add a notification to the user's blog."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_blog_my_activity(body))

    #
    # Lifecycle
    #

    async def _async_create_my_todo(self, todo_name: str, activity_status: str = "REQUESTED",
                                    description:Optional[str]=None, situation: Optional[str]=None,priority:Optional[int]=0) -> str:
        """Create a person action (Meeting, ToDo, Notification, Review). Async version.

        Parameters
        ----------
        todo_name : str
            The name of the action to be created.
        activity_status : str, optional
            The status of the action, by default "REQUESTED"
        description : Optional[str], optional
            The description of the action, by default None
        situation : Optional[str], optional
            The situation of the action, by default None
        priority : Optional[int], optional
            The priority of the action, by default 0
        Returns
        -------
        GUID
            GUID of the person action

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        -----
        This method can be used to create a person action. The type of person action depends on the "Class" element
        in the body. Here are brief examples of bodies:

        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "ToDo",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "situation": "add situation here"
            }
        }
        """
        qualified_name = self.__create_qualified_name__("Todo", todo_name)+f"-{int(time.time())}"
        if not self.my_profile_guid:
            me = self.get_my_profile()
            self.my_profile_guid = me['elementHeader']["guid"]

        body = {
            "class": "ActionRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "ToDoProperties",
                "qualifiedName": qualified_name,
                "displayName": todo_name,
                "description": description,
                "situation": situation,
                "priority": priority,
                "activityStatus": activity_status,
                "originatorGUID": self.my_profile_guid,
                "assignToActorGUID": self.my_profile_guid
            }
        }
        response = await super()._async_create_action(body)
        return response

    def create_my_todo(self, todo_name: str, activity_status: str = "REQUESTED",
                    description:Optional[str]=None, situation: Optional[str]=None,priority:Optional[int]=0) -> str:
        """Create a person action (Meeting, ToDo, Notification, Review). Async version.

        Parameters
        ----------
        todo_name : str
            The name of the action to be created.
        activity_status : str, optional
            The status of the action, by default "REQUESTED"
        description : Optional[str], optional
            The description of the action, by default None
        situation : Optional[str], optional
            The situation of the action, by default None
        priority : Optional[int], optional
            The priority of the action, by default 0
        Returns
        -------
        GUID
            GUID of the person action

        Raises
        ------
        PyegeriaException
        ValidationError

        Notes
        -----
        This method can be used to create a person action. The type of person action depends on the "Class" element
        in the body. Here are brief examples of bodies:

        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class" : "ToDo",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "situation": "add situation here"
            }
        }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_my_todo(todo_name, activity_status,
                                                                      description, situation, priority))
        return response


    @dynamic_catch
    async def _async_get_my_to_dos(
            self,
        activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
        metadata_element_type: Optional[str] = "Action",
        metadata_element_subtypes: list[str] = ["ToDo"],

        output_format: str = "JSON",
        report_spec: str | dict = None,
        start_from: int = 0,
        page_size: int = 0,

    ) -> list | str:
        """find To-Do items. Async version.
        Parameters
        ----------
          starts_with : bool, [default=False], optional
             Starts with the supplied string.
          ends_with : bool, [default=False], optional
                 Ends with the supplied string
          ignore_case : bool, [default=False], optional
                 Ignore case when searching
        Returns
        -------
        None
         List of To-Do items that match the criteria

        Raises
        ------
        PyegeriaInvalidParameterException
        If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
        Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
        The principle specified by the user_id does not have authorization for the requested action
        """


        return await self._async_get_my_assigned_actions(metadata_element_type, metadata_element_subtypes,
                                                    activity_status_list,
                                                    start_from, page_size, output_format=output_format,
                                                    report_spec=report_spec)


    @dynamic_catch

    def get_my_to_dos(self,

                      activity_status_list: list[str] = ["REQUESTED", "WAITING", "IN_PROGRESS"],
                      metadata_element_type: Optional[str] = "Action",
                      metadata_element_subtypes: list[str] = ["ToDo"],

                      output_format: str = "JSON",
                      report_spec: str | dict = None,
                      start_from: int = 0,
                      page_size: int = 0,

                      ) -> list | str:
        """find To-Do items. Async version.
        Parameters
        ----------
          search_string: str
             String to search against. If '*' then all to-do items will match.
          starts_with : bool, [default=False], optional
             Starts with the supplied string.
          ends_with : bool, [default=False], optional
                 Ends with the supplied string
          ignore_case : bool, [default=False], optional
                 Ignore case when searching
        Returns
        -------
        None
         List of To-Do items that match the criteria

        Raises
        ------
        PyegeriaInvalidParameterException
        If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
        Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
        The principle specified by the user_id does not have authorization for the requested action
        """

        return self.get_my_assigned_actions(metadata_element_type, metadata_element_subtypes,
                                                         activity_status_list,
                                                         start_from, page_size, output_format=output_format,
                                                         report_spec=report_spec)


#






if __name__ == "__main__":
    print("Main-My Profile")

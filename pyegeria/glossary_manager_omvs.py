"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_manager omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""
import asyncio
import os
import time
import csv
from datetime import datetime
from typing import List

from pyegeria import InvalidParameterException

# import json
from pyegeria._client import Client
from pyegeria._validators import (
    validate_name,
    validate_guid,
    validate_search_string,
)
from pyegeria.glossary_browser_omvs import GlossaryBrowser
from pyegeria.utils import body_slimmer


class GlossaryManager(GlossaryBrowser):
    """
    GlossaryManager is a class that extends the Client class. It provides methods to create and manage glossaries,
    terms and categories.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None


    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.gl_mgr_command_root: str
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    #
    #       Get Valid Values for Enumerations
    #

    def __validate_term_status__(self, status: str) -> bool:
        """Return True if the status is a legal glossary term status"""
        recognized_term_status = self.get_glossary_term_statuses()
        return status in recognized_term_status

    async def _async_create_glossary(
        self,
        display_name: str,
        description: str,
        language: str = "English",
        usage: str = None,
    ) -> str:
        """Create a new glossary. Async version.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        language: str, optional, default = "English"
            The language the used for the glossary
        usage: str, optional, default = None
            How the glossary is intended to be used


        Returns
        -------
        str
            The GUID of the created glossary.

        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries"
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryProperties",
                "qualifiedName": f"Glossary:{display_name}",
                "displayName": display_name,
                "description": description,
                "language": language,
                "usage": usage,
            },
        }
        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", None)

    def create_glossary(
        self,
        display_name: str,
        description: str,
        language: str = "English",
        usage: str = None,
    ) -> str:
        """Create a new glossary.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        language: str, optional, default = "English"
            The language the used for the glossary
        usage: str, optional, default = None
            How the glossary is intended to be used


        Returns
        -------
        str
            The GUID of the created glossary.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary(display_name, description, language, usage)
        )
        return response

    async def _async_delete_glossary(self, glossary_guid: str) -> None:
        """Delete glossary. Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.


        Returns
        -------
        None

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/remove"
        )

        await self._async_make_request("POST", url)
        return

    def delete_glossary(self, glossary_guid: str) -> None:
        """Create a new glossary.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.


        Returns
        -------
        None

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_delete_glossary(glossary_guid))
        return response

    async def _async_update_glossary(
        self,
        glossary_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> None:
        """Update Glossary.

        Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to update.
        body: dict
            A dict containing the properties to update.
        is_merge_update: bool, optional, default = True
            If true, then only those properties specified in the body will be updated. If false, then all the
            properties of the glossary will be replaced with those of the body.
        for_lineage: bool, optional, default = False
            Normally false. Used when we want to retrieve elements that have been delete but have a Memento entry.
        for_duplicate_processing: bool, optional, default = False
            Normally false. Set true when Egeria is told to skip deduplication because another system will do it.


        Returns
        -------
        None

        Notes
        -----

        Sample body:

            {
                "class" : "ReferenceableRequestBody",
                "elementProperties" :
                    {
                        "class" : "GlossaryProperties",
                        "qualifiedName" : "MyGlossary",
                        "displayName" : "My Glossary",
                        "description" : "This is an example glossary"
                    }
            }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/update?isMergeUpdate={is_merge_update}&forLineage={for_lineage}&"
            f"forDuplicateProcessing={for_duplicate_processing}"
        )

        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_glossary(
        self,
        glossary_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> None:
        """Update Glossary.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to update.
        body: dict
            A dict containing the properties to update.
        is_merge_update: bool, optional, default = True
            If true, then only those properties specified in the body will be updated. If false, then all the
            properties of the glossary will be replaced with those of the body.
        for_lineage: bool, optional, default = False
            Normally false. Used when we want to retrieve elements that have been delete but have a Memento entry.
        for_duplicate_processing: bool, optional, default = False
            Normally false. Set true when Egeria is told to skip deduplication because another system will do it.


        Returns
        -------
        None

        Notes
        -----

        Sample body:

            {
                "class" : "ReferenceableRequestBody",
                "elementProperties" :
                    {
                        "class" : "GlossaryProperties",
                        "qualifiedName" : "MyGlossary",
                        "displayName" : "My Glossary",
                        "description" : "This is an example glossary"
                    }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_glossary(
                glossary_guid,
                body,
                is_merge_update,
                for_lineage,
                for_duplicate_processing,
            )
        )
        return

    #
    #       Glossaries
    #

    async def _async_find_glossaries(
        self,
        search_string: str,
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary metadata elements that contain the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        validate_search_string(search_string)

        if search_string == "*":
            search_string = None

        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string,
            "effectiveTime": effective_time,
            "typeName": type_name,
        }
        body = body_slimmer(body)
        # print(f"\n\nBody is: \n{body}")

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
            f"forDuplicateProcessing={for_duplicate_processing_s}"
        )

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No Glossaries found")

    def find_glossaries(
        self,
        search_string: str,
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary metadata elements that contain the search string.
                The search string is located in the request body and is interpreted as a plain string.
                The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional
             Indicates the search is for lineage.
        for_duplicate_processing : bool, [default=False], optional
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
         start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
         page_size: int, [default=None]
             The number of items to return in a single page. If not specified, the default will be taken from
             the class instance.
        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossaries(
                search_string,
                effective_time,
                starts_with,
                ends_with,
                ignore_case,
                for_lineage,
                for_duplicate_processing,
                type_name,
                start_from,
                page_size,
            )
        )

        return response

    async def _async_get_glossaries_by_name(
        self,
        glossary_name: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        None

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        if page_size is None:
            page_size = self.page_size
        validate_name(glossary_name)

        if effective_time is None:
            body = {"name": glossary_name}
        else:
            body = {"name": glossary_name, "effectiveTime": effective_time}

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
            f"by-name?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No glossaries found")

    def get_glossaries_by_name(
        self,
        glossary_name: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.

        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            he class instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossaries_by_name(
                glossary_name, effective_time, start_from, page_size
            )
        )
        return response

    #
    # Glossary Categories
    #
    async def _async_create_category(
        self,
        glossary_guid: str,
        display_name: str,
        description: str,
    ) -> str:
        """Create a new category within the specified glossary. Async Version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.


        Returns
        -------
        A string with the GUID of the new category..

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/categories"
        )
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryCategoryProperties",
                "qualifiedName": f"GlossaryCategory-{display_name}-{time.asctime()}",
                "displayName": display_name,
                "description": description,
            },
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", None)

    def create_category(
        self,
        glossary_guid: str,
        display_name: str,
        description: str,
    ) -> str:
        """Create a new category within the specified glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.


        Returns
        -------
        A string with the GUID of the new category..

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_category(glossary_guid, display_name, description)
        )
        return response

    async def _async_get_glossary_for_category(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> dict | str:
        """Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        Returns
        -------
        A dict structure with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time,
        }

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"for-category/{glossary_category_guid}/retrieve"
        )

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def get_glossary_for_category(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> dict | str:
        """Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        Returns
        -------
        A dict structure with the glossary metadata element for the requested category.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_for_category(
                glossary_category_guid, effective_time
            )
        )
        return response

    async def _async_find_glossary_categories(
        self,
        search_string: str,
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary category metadata elements that contain the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
            Async version.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

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

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        validate_search_string(search_string)

        if search_string == "*":
            search_string = None

        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string,
            "effectiveTime": effective_time,
        }
        body = body_slimmer(body)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No Categories found")

    def find_glossary_categories(
        self,
        search_string: str,
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary category metadata elements that contain the search string.
         The search string is located in the request body and is interpreted as a plain string.
         The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

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

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_categories(
                search_string,
                effective_time,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
            )
        )

        return response

    async def _async_get_categories_for_glossary(
        self,
        glossary_guid: str,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Return the list of categories associated with a glossary.
            Async version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_for_glossary(
        self,
        glossary_guid: str,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Return the list of categories associated with a glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_for_glossary(
                glossary_guid, start_from, page_size
            )
        )
        return response

    async def _async_get_categories_for_term(
        self,
        glossary_term_guid: str,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Return the list of categories associated with a glossary term.
            Async version.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary term.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
            f"{glossary_term_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_for_term(
        self,
        glossary_term_guid: str,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Return the list of categories associated with a glossary term.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories associated with a glossary term.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_for_term(
                glossary_term_guid, start_from, page_size
            )
        )
        return response

    async def _async_get_categories_by_name(
        self,
        name: str,
        glossary_guid: str = None,
        status: [str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary category metadata elements that either have the requested qualified name or display name.
            The name to search for is located in the request body and is interpreted as a plain string.
            The request body also supports the specification of a glossaryGUID to restrict the search to within a single glossary.

            Async version.

        Parameters
        ----------
        name: str,
            category name to search for.
        glossary_guid: str, optional
            The identity of the glossary to search. If not specified, all glossaries will be searched.
        status: [str], optional
            A list of statuses to optionally restrict results. Default is Active

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories with the corresponding display name or qualified name.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size
        validate_name(name)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"by-name?startFrom={start_from}&pageSize={page_size}"
        )

        body = {
            "class": "GlossaryNameRequestBody",
            "name": name,
            "glossaryGUID": glossary_guid,
            "limitResultsByStatus": status,
        }

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_by_name(
        self,
        name: str,
        glossary_guid: str = None,
        status: [str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary category metadata elements that either have the requested qualified name or display name.
            The name to search for is located in the request body and is interpreted as a plain string.
            The request body also supports the specification of a glossaryGUID to restrict the search to within a single glossary.

        Parameters
        ----------
        name: str,
            category name to search for.
        glossary_guid: str, optional
            The identity of the glossary to search. If not specified, all glossaries will be searched.
        status: [str], optional
            A list of statuses to optionally restrict results. Default is Active

        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of categories with the corresponding display name or qualified name.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_by_name(
                name, glossary_guid, status, start_from, page_size
            )
        )
        return response

    async def _async_get_categories_by_guid(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> list | str:
        """Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Async version.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time: str, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        Returns
        -------
        List | str

        Details for the category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"{glossary_category_guid}/retrieve"
        )

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time,
        }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No Category found")

    def get_categories_by_guid(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> list | str:
        """Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time, datetime, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        Returns
        -------
        List | str

        Details for the category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_categories_by_guid(glossary_category_guid, effective_time)
        )
        return response

    async def _async_get_category_parent(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> list | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
            element for the glossary category with the supplied unique identifier.  If the requested category
            does not have a parent category, null is returned.  The optional request body contain an effective time
            for the query.

        Async version.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time, datetime, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        Returns
        -------
        List | str

        Details for the parent category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/categories/"
            f"{glossary_category_guid}/parent/retrieve"
        )

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time,
        }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No Parent Category found")

    def get_category_parent(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
    ) -> list | str:
        """Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
            element for the glossary category with the supplied unique identifier.  If the requested category
            does not have a parent category, null is returned.  The optional request body contain an effective time
            for the query.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time, datetime, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).


        Returns
        -------
        List | str

        Details for the parent category with the glossary category GUID.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_category_parent(glossary_category_guid, effective_time)
        )
        return response

    #
    #  Terms
    #
    async def _async_create_controlled_glossary_term(
        self, glossary_guid: str, body: dict
    ) -> str:
        """Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        Sample body like:
        {
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm: term name : {$isoTimestamp}",
                    "displayName" : "term name",
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "GT",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "publishVersionIdentifier" : "V1.0",
                    "additionalProperties" :
                    {
                       "propertyName1" : "xxxx",
                       "propertyName2" : "xxxx"
                    }
                },
            "initialStatus" : "DRAFT"
        }

        """

        validate_guid(glossary_guid)
        if self.__validate_term_status__(body["initialStatus"]) is False:
            raise InvalidParameterException("Bad status value")

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/terms/new-controlled"
        )

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_controlled_glossary_term(self, glossary_guid: str, body: dict) -> str:
        """Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        Sample body like:
        {
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm: term name : {$isoTimestamp}",
                    "displayName" : "term name",
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "GT",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "publishVersionIdentifier" : "V1.0",
                    "additionalProperties" :
                    {
                       "propertyName1" : "xxxx",
                       "propertyName2" : "xxxx"
                    }
                },
            "initialStatus" : "DRAFT"
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_controlled_glossary_term(glossary_guid, body)
        )

        return response

    def load_terms_from_file(
        self,
        glossary_name: str,
        filename: str,
        upsert: bool = True,
        verbose: bool = True,
    ) -> List[dict] | None:
        """This method loads glossary terms into the specified glossary from the indicated file.

        Parameters
        ----------
            glossary_name : str
                Name of the glossary to import terms into.
            filename: str
                Path to the file to import terms from. File is assumed to be in CSV format. The path
                is relative to where the python method is being called from.
            upsert: bool, default = True
                If true, terms from the file are inserted into the glossary if no qualified name is specified;
                if a qualified name is specified in the file, then the file values for this term will over-ride the
                values in the glossary. If false, the row in the file will be appended to the glossary, possibly
                resulting in duplicate term names - which is legal (since the qualified names will be unique).

            verbose: bool, default = True
                If true, a JSON structure will be returned indicating the import status of each row.


        Returns
        -------
        [dict]:
            If verbose is True, import status for each row
        None:
            If verbose is False

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
            Keep in mind that the file path is relative to where the python method is being called from -
            not relative to the Egeria platform.

        """

        # Check that glossary exists and get guid
        glossaries = self.get_glossaries_by_name(glossary_name)
        if type(glossaries) is not list:
            return "Unknown glossary"
        if len(glossaries) > 1:
            glossary_error = (
                "Multiple glossaries found - please use a qualified name from below\n"
            )
            for g in glossaries:
                glossary_error += (
                    f"Display Name: {g['glossaryProperties']['displayName']}\tQualified Name:"
                    f" {g['glossaryProperties']['qualifiedName']}\n"
                )
            raise Exception(glossary_error)
            sys.exit(1)

        # Now we know we have a single glossary so we can get the guid
        glossary_guid = glossaries[0]["elementHeader"]["guid"]

        term_properties = {
            "Term Name",
            "Qualified Name",
            "Abbreviation",
            "Summary",
            "Description",
            "Examples",
            "Usage",
            "Version Identifier",
            "Status",
        }
        # process file
        with open(filename, mode="r") as file:
            # Create a CSV reader object
            csv_reader = csv.DictReader(file)
            headers = csv_reader.fieldnames
            term_info = []
            # check that the column headers are known
            if all(header in term_properties for header in headers) is False:
                raise InvalidParameterException("Invalid headers in CSV File")
                sys.exit(1)

            # process each row and validate values
            for row in csv_reader:
                # Parse the file. When the value '---' is encountered, make the value None.git+https:
                term_name = row.get("Term Name", " ")
                if len(term_name) < 2:
                    term_info.append(
                        {
                            "term_name": "---",
                            "qualified_name": "---",
                            "term_guid": "---",
                            "error": "missing or invalid term names - skipping",
                        }
                    )
                    continue
                qualified_name = row.get("Qualified Name", None)
                abbrev_in = row.get("Abbreviation", None)
                abbrev = None if abbrev_in == "---" else abbrev_in

                summary_in = row.get("Summary", None)
                summary = None if summary_in == "---" else summary_in

                description_in = row.get("Description", None)
                description = None if description_in == "---" else description_in

                examples_in = row.get("Examples", None)
                examples = None if examples_in == "---" else examples_in

                usage_in = row.get("Usage", None)
                usage = None if usage_in == "---" else usage_in

                version = row.get("Version Identifier", "1.0")
                status = row.get("Status", "DRAFT").upper()
                if self.__validate_term_status__(status) is False:
                    term_info.append(
                        {
                            "term_name": "---",
                            "qualified_name": "---",
                            "term_guid": "---",
                            "error": "invalid term status",
                        }
                    )
                    continue

                if upsert:
                    # If upsert is set we need to see if it can be done (there must be a valid qualified name) and then
                    # do the update for the row - if there is no qualified name we will treat the row as an insert.
                    if qualified_name:
                        term_stuff = self.get_terms_by_name(
                            qualified_name, glossary_guid
                        )
                        if type(term_stuff) is str:
                            # An existing term was not found with that qualified name
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "error": "Matching term not found - skipping",
                                }
                            )
                            continue
                        elif len(term_stuff) > 1:
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "error": "Multiple matching terms - skipping",
                                }
                            )
                            continue
                        else:
                            # An existing term was found - so update it! Get the existing values and overlay
                            # values from file when present

                            body = {
                                "class": "ReferenceableRequestBody",
                                "elementProperties": {
                                    "class": "GlossaryTermProperties",
                                    "qualifiedName": qualified_name,
                                    "displayName": term_name,
                                    "summary": summary,
                                    "description": description,
                                    "abbreviation": abbrev,
                                    "examples": examples,
                                    "usage": usage,
                                    "publishVersionIdentifier": version,
                                },
                                "updateDescription": "Update from file import via upsert",
                            }
                            term_guid = term_stuff[0]["elementHeader"]["guid"]
                            self.update_term(
                                term_guid, body_slimmer(body), is_merge_update=True
                            )
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "term_guid": term_guid,
                                    "updated": "the term was updated",
                                }
                            )
                            continue

                # Add the term
                term_qualified_name = (
                    f"GlossaryTerm: {term_name} - {datetime.now().isoformat()}"
                )
                body = {
                    "class": "ReferenceableRequestBody",
                    "elementProperties": {
                        "class": "GlossaryTermProperties",
                        "qualifiedName": term_qualified_name,
                        "displayName": term_name,
                        "summary": summary,
                        "description": description,
                        "abbreviation": abbrev,
                        "examples": examples,
                        "usage": usage,
                        "publishVersionIdentifier": version,
                    },
                    "initialStatus": status,
                }

                # Add the term
                term_guid = self.create_controlled_glossary_term(
                    glossary_guid, body_slimmer(body)
                )
                term_info.append(
                    {
                        "term_name": term_name,
                        "qualified_name": term_qualified_name,
                        "term_guid": term_guid,
                    }
                )
        if verbose:
            return term_info
        else:
            return

    async def _async_export_glossary_to_csv(
        self, glossary_guid: str, target_file: str
    ) -> int:
        """Export all the terms in a glossary to a CSV file. Async version

        Parameters:
        -----------
        glossary_guid: str
            Identity of the glossary to export.
        target_file: str
            Complete file name with path and extension to export to.

        Returns:
            int: Number of rows exported.
        """

        term_list = await self._async_get_terms_for_glossary(glossary_guid)

        header = [
            "Term Name",
            "Qualified Name",
            "Abbreviation",
            "Summary",
            "Description",
            "Examples",
            "Usage",
            "Version Identifier",
            "Status",
        ]

        with open(target_file, mode="w") as file:
            csv_writer = csv.DictWriter(file, fieldnames=header)
            csv_writer.writeheader()
            count = 0
            for term in term_list:
                term_name = term["glossaryTermProperties"]["displayName"]
                qualified_name = term["glossaryTermProperties"]["qualifiedName"]
                abbrev = term["glossaryTermProperties"].get("abbreviation", "---")
                summary = term["glossaryTermProperties"].get("summary", "---")
                description = term["glossaryTermProperties"].get("description", "---")
                examples = term["glossaryTermProperties"].get("examples", "---")
                usage = term["glossaryTermProperties"].get("usage", "---")
                version = term["glossaryTermProperties"].get(
                    "publishVersionIdentifier", "---"
                )
                status = term["elementHeader"]["status"]

                csv_writer.writerow(
                    {
                        "Term Name": term_name,
                        "Qualified Name": qualified_name,
                        "Abbreviation": abbrev,
                        "Summary": summary,
                        "Description": description,
                        "Examples": examples,
                        "Usage": usage,
                        "Version Identifier": version,
                        "Status": status,
                    }
                )

                count += 1
        return count

    def export_glossary_to_csv(self, glossary_guid: str, target_file: str) -> int:
        """Export all the terms in a glossary to a CSV file.

        Parameters:
        -----------
        glossary_guid: str
            Identity of the glossary to export.
        target_file: str
            Complete file name with path and extension to export to.

        Returns:
            int: Number of rows exported.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_export_glossary_to_csv(glossary_guid, target_file)
        )

        return response

    async def _async_create_term_copy(
        self,
        glossary_guid: str,
        glossary_term_guid: str,
        new_display_name: str,
        version_id: str,
        term_status: str = "PROPOSED",
    ) -> str:
        """Create a new term from an existing term.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_named: str
                The display name of the new term.
            version_id: str
                The version identifier of the new term.
            term_status: str, optional, default = "PROPOSED"
                The status of the term


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        """

        validate_guid(glossary_guid)
        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/terms/from-template/{glossary_term_guid}"
        )

        body = {
            "class": "GlossaryTemplateRequestBody",
            "elementProperties": {
                "class": "TemplateProperties",
                "qualifiedName": f"Term-{new_display_name}-{time.asctime()}",
                "displayName": new_display_name,
                "versionIdentifier": version_id,
            },
            "glossaryTermStatus": term_status,
        }

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_term_copy(
        self,
        glossary_guid: str,
        glossary_term_guid: str,
        new_display_name: str,
        version_id: str,
        term_status: str = "PROPOSED",
    ) -> str:
        """Create a new term from an existing term.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_named: str
                The display name of the new term.
            version_id: str
                The version identifier of the new term.
            term_status: str, optional, default = "PROPOSED"
                The status of the term


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_term_copy(
                glossary_guid,
                glossary_term_guid,
                new_display_name,
                version_id,
                term_status,
            )
        )

        return response

    async def _async_add_data_field_to_term(
        self, glossary_term_guid: str, body: dict
    ) -> None:
        """Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        Body is of the structure:

        {
            "class" : "ClassificationRequestBody",
            "properties" :
                {
                    "class" : "DataFieldValuesProperties",
                    "defaultValue" : "Add default value here",
                    "sampleValues" : [ "Sample Value 1", "Sample Value 2"],
                    "dataPattern" : ["add data pattern here"],
                    "namePattern" : ["add column pattern here"]
                }
        }
        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{glossary_term_guid}/is-data-field"
        )

        await self._async_make_request("POST", url, body)
        return

    def add_data_field_to_term(self, glossary_term_guid: str, body: dict) -> None:
        """Add the data field values classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        Body is of the structure:

        {
            "class" : "ClassificationRequestBody",
            "properties" :
                {
                    "class" : "DataFieldValuesProperties",
                    "defaultValue" : "Add default value here",
                    "sampleValues" : [ "Sample Value 1", "Sample Value 2"],
                    "dataPattern" : ["add data pattern here"],
                    "namePattern" : ["add column pattern here"]
                }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_data_field_to_term(glossary_term_guid, body)
        )

        return

    async def _async_add_confidentiality_to_term(
        self,
        glossary_term_guid: str,
        confidentiality_level: int,
    ) -> None:
        """Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/elements/"
            f"{glossary_term_guid}/confidentiality"
        )

        body = {
            "class": "ClassificationRequestBody",
            "properties": {
                "class": "GovernanceClassificationProperties",
                "levelIdentifier": confidentiality_level,
            },
        }

        await self._async_make_request("POST", url, body)
        return

    def add_confidentiality_to_term(
        self,
        glossary_term_guid: str,
        confidentiality_level: int,
    ) -> str:
        """Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_confidentiality_to_term(
                glossary_term_guid, confidentiality_level
            )
        )

        return

    async def _async_add_subject_area_to_term(
        self, glossary_term_guid: str, subject_area: str
    ) -> None:
        """Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/elements/"
            f"{glossary_term_guid}/subject-area-member"
        )

        body = {
            "class": "ClassificationRequestBody",
            "properties": {
                "class": "SubjectAreaMemberProperties",
                "subjectAreaName": subject_area,
            },
        }

        await self._async_make_request("POST", url, body)
        return

    def add_subject_area_to_term(
        self, glossary_term_guid: str, subject_area: str
    ) -> None:
        """Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_subject_area_to_term(glossary_term_guid, subject_area)
        )

        return

    async def _async_update_term(
        self,
        glossary_term_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processig: bool = False,
    ) -> None:
        """Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            is_merge_update: bool, optional, default = True
                Whether the data field values should be merged with existing definition or replace it.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        An example body is:

        {
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "description" : "This is the long description of the term. And this is some more text."
                },
                "updateDescription" : "Final updates based on in-house review comments."
        }

        """

        validate_guid(glossary_term_guid)
        is_merge_update_s = str(is_merge_update).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processig).lower()

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate={is_merge_update_s}&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}"
        )

        await self._async_make_request("POST", url, body)
        return

    def update_term(
        self,
        glossary_term_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processig: bool = False,
    ) -> None:
        """Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            is_merge_update: bool, optional, default = True
                Whether the data field values should be merged with existing definition or replace it.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        An example body is:

        {
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "description" : "This is the long description of the term. And this is some more text."
                },
                "updateDescription" : "Final updates based on in-house review comments."
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_term(
                glossary_term_guid,
                body,
                is_merge_update,
                for_lineage,
                for_duplicate_processig,
            )
        )

        return

    async def _async_update_term_version_id(
        self,
        glossary_term_guid: str,
        new_version_identifier: str,
    ) -> None:
        """Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        This is a useful example of a term update, specifying a new version identifier.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate=true"
        )

        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryTermProperties",
                "publishVersionIdentifier": new_version_identifier,
            },
        }
        await self._async_make_request("POST", url, body)
        return

    def update_term_version_id(
        self,
        glossary_term_guid: str,
        new_version_identifier: str,
    ) -> None:
        """Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.


        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        This is a useful example of a term update, specifying a new version identifier.

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_term_version_id(
                glossary_term_guid, new_version_identifier
            )
        )

        return

    async def _async_get_terms_for_category(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            effective_time : str, optional
                If specified, the terms are returned if they are active at the `effective_time
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(glossary_category_guid)

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
            f"{glossary_category_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}"
        )

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_category(
        self,
        glossary_category_guid: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            effective_time : str, optional
                If specified, the terms are returned if they are active at the `effective_time.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)`.
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_for_category(
                glossary_category_guid,
                effective_time,
                start_from,
                page_size,
            )
        )

        return response

    async def _async_delete_term(
        self,
        term_guid: str,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> list | str:
        """Delete the glossary terms associated with the specified glossary. Async version.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.
            for_lineage: bool, opt, default = False
                Set true for lineage processing - generally false.
            for_duplicate_processing: bool, opt, default = False
                Set true if duplicate processing handled externally - generally set False.

        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/remove?forLineage={for_lineage}&forDuplicateProcessing={for_duplicate_processing}"
        )

        await self._async_make_request("POST", url)
        return

    def delete_term(
        self,
        term_guid: str,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> list | str:
        """Delete the glossary terms associated with the specified glossary.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.
            for_lineage: bool, opt, default = False
                Set true for lineage processing - generally false.
            for_duplicate_processing: bool, opt, default = False
                Set true if duplicate processing handled externally - generally set False.

        Returns
        -------
        None

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_term(term_guid, for_lineage, for_duplicate_processing)
        )

        return

    async def _async_get_term_relationships(
        self,
        term_guid: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship..
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term
            effective_time : str, optional
                If specified, term relationships are included if they are active at the `effective_time`.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
            f"{term_guid}/related-terms?startFrom={start_from}&pageSize={page_size}"
        )

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_term_relationships(
        self,
        term_guid: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship..
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term
            effective_time : str, optional
                If specified, term relationships are included if they are active at the `effective_time`.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_term_relationships(
                term_guid, effective_time, start_from, page_size
            )
        )

        return response

    async def _async_get_glossary_for_term(
        self, term_guid: str, effective_time: str = None
    ) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to specify
            that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time,
        }
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
            f"for-term/{term_guid}/retrieve"
        )

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No glossary found")

    def get_glossary_for_term(
        self, term_guid: str, effective_time: str = None
    ) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to specify
            that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            TIf specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_for_term(term_guid, effective_time)
        )
        return response

    async def _async_get_terms_by_name(
        self,
        term: str,
        glossary_guid: str = None,
        status_filter: list = [],
        effective_time: str = None,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list:
        """Retrieve glossary terms by display name or qualified name. Async Version.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found, it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """

        if page_size is None:
            page_size = self.page_size

        validate_name(term)

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "GlossaryNameRequestBody",
            "glossaryGUID": glossary_guid,
            "name": term,
            "effectiveTime": effective_time,
            "limitResultsByStatus": status_filter,
        }
        # body = body_slimmer(body)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
            f"terms/by-name?startFrom={start_from}&pageSize={page_size}&"
            f"&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}"
        )

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")

    def get_terms_by_name(
        self,
        term: str,
        glossary_guid: str = None,
        status_filter: list = [],
        effective_time: str = None,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list:
        """Retrieve glossary terms by display name or qualified name.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
             Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found,
            it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_by_name(
                term,
                glossary_guid,
                status_filter,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
            )
        )
        return response

    async def _async_get_terms_by_guid(self, term_guid: str) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
            f"{term_guid}/retrieve"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("element", "No term found")

    def get_terms_by_guid(self, term_guid: str) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.

        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_terms_by_guid(term_guid))

        return response

    async def _async_get_terms_versions(
        self,
        term_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the versions of a glossary term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
            f"{term_guid}/history?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("element", "No term found")

    def get_terms_versions(
        self,
        term_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the versions of a glossary term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_versions(term_guid, start_from, page_size)
        )

        return response

    async def _async_get_term_revision_logs(
        self,
        term_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the revision log history for a term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision log history. If no term is found, the string
            "No log found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/elements/"
            f"{term_guid}/notes/retrieve?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No log found")

    def get_term_revision_logs(
        self,
        term_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the revision log history for a term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision log history. If no term is found, the string
            "No log found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_term_revision_logs(term_guid, start_from, page_size)
        )

        return response

    async def _async_get_term_revision_history(
        self,
        term_revision_log_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the revision history for a glossary term. Async version.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision history.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.


        Notes
        -----
        This revision history is created automatically.  The text is supplied on the update request.
        If no text is supplied, the value "None" is show.
        """

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_revision_log_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/note-logs/"
            f"{term_revision_log_guid}/notes/retrieve?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No logs found")

    def get_term_revision_history(
        self,
        term_revision_log_guid: str,
        start_from: int = 0,
        page_size=None,
    ) -> dict | str:
        """Retrieve the revision history for a glossary term.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        Returns
        -------
        dict | str
            A dict detailing the glossary term revision history.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.


        Notes
        -----
        This revision history is created automatically.  The text is supplied on the update request.
        If no text is supplied, the value "None" is show.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_term_revision_history(
                term_revision_log_guid, start_from, page_size
            )
        )

        return response

    async def _async_find_glossary_terms(
        self,
        search_string: str,
        glossary_guid: str = None,
        status_filter: list = [],
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a single glossary.
        """

        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == "*":
            search_string = None

        # validate_search_string(search_string)

        body = {
            "class": "GlossarySearchStringRequestBody",
            "glossaryGUID": glossary_guid,
            "searchString": search_string,
            "effectiveTime": effective_time,
            "limitResultsByStatus": status_filter,
        }
        # body = body_slimmer(body)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
            f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
            f"forDuplicateProcessing={for_duplicate_processing_s}"
        )

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get(
            "elementList", "No terms found"
        )  # return response.text

    def find_glossary_terms(
        self,
        search_string: str,
        glossary_guid: str = None,
        status_filter: list = [],
        effective_time: str = None,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a single glossary.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_terms(
                search_string,
                glossary_guid,
                status_filter,
                effective_time,
                starts_with,
                ends_with,
                ignore_case,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
            )
        )

        return response


if __name__ == "__main__":
    print("Main-Glossary Manager")

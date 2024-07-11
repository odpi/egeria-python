"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_manager omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""
import asyncio
from datetime import datetime, time

# import json
from pyegeria._client import Client
from pyegeria._globals import enable_ssl_check
from pyegeria._validators import (validate_name, validate_guid, validate_search_string, )
from pyegeria.glossary_browser_omvs import GlossaryBrowser
from pyegeria.utils import body_slimmer


class GlossaryManager(GlossaryBrowser):
    """
    GlossaryManager is a class that extends the Client class. It provides methods to create and manage glossaries,
    terms and categories.

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
        verify_flag: bool
            Flag to indicate if SSL Certificates should be verified in the HTTP requests.
            Defaults to False.

     """

    def __init__(self, server_name: str, platform_url: str, token: str = None, user_id: str = None,
                 user_pwd: str = None, verify_flag: bool = enable_ssl_check, sync_mode: bool = True):
        self.admin_command_root: str
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)

    #
    #       Get Valid Values for Enumerations
    #

    async def _async_create_glossary(self, display_name: str, description: str, server_name: str = None) -> str:
        """ Create a new glossary. Async version.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        server_name : str, optional
            The name of the server to query. If not provided, the server name associated with the instance is used.

        Returns
        -------
        str
            The GUID of the created glossary.

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-manager/glossaries/"
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties":
                {
                    "class": "GlossaryProperties",
                    "qualifiedName": f"Glossary-{display_name}-{time.asctime()}",
                    "displayName": display_name,
                    "description": description
                }
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", None)

    def create_glossary(self, display_name: str, description: str, server_name: str = None) -> str:
        """ Create a new glossary.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        server_name : str, optional
            The name of the server to query. If not provided, the server name associated with the instance is used.

        Returns
        -------
        str
            The GUID of the created glossary.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_create_glossary(display_name, description, server_name))
        return response

    async def _async_delete_glossary(self, glossary_guid: str, server_name: str = None) -> None:
        """ Delete glossary. Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.
        server_name : str, optional
            The name of the server to query. If not provided, the server name associated with the instance is used.

        Returns
        -------
        None

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-manager/glossaries/"
               f"{glossary_guid}/remove")

        await self._async_make_request("POST", url)
        return

    def delete_glossary(self, glossary_guid: str, server_name: str = None) -> None:
        """ Create a new glossary.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.
        server_name : str, optional
            The name of the server to query. If not provided, the server name associated with the instance is used.

        Returns
        -------
        None

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_delete_glossary(glossary_guid, server_name))
        return response

    #
    #       Glossaries
    #

    async def _async_find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                                     for_duplicate_processing: bool = False, type_name: str = None,
                                     server_name: str = None, start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        validate_search_string(search_string)

        if search_string == '*':
            search_string = None

        body = {"class": "SearchStringRequestBody", "searchString": search_string, "effectiveTime": effective_time,
                "typeName": type_name}
        body = body_slimmer(body)
        # print(f"\n\nBody is: \n{body}")

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No Glossaries found")

    def find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                        ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                        for_duplicate_processing: bool = False, type_name: str = None, server_name: str = None,
                        start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string.
                   The search string is located in the request body and is interpreted as a plain string.
                   The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

           Parameters
           ----------
           search_string: str,
               Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

           effective_time: str, [default=None], optional
               Effective time of the query. If not specified will default to any time. Time format is
               "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
           server_name : str, optional
               The name of the server to  configure.
               If not provided, the server name associated with the instance is used.
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
            self._async_find_glossaries(search_string, effective_time, starts_with, ends_with, ignore_case, for_lineage,
                                        for_duplicate_processing, type_name, server_name, start_from, page_size))

        return response

    async def _async_get_glossary_by_guid(self, glossary_guid: str, server_name: str = None,
                                          effective_time: str = None) -> dict:
        """ Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time. Time format is
                "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)

        body = {"class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/retrieve")
        print(url)
        response = await self._async_make_request("POST", url, payload=body)
        return response.json()

    def get_glossary_by_guid(self, glossary_guid: str, server_name: str = None) -> dict:
        """ Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
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
        response = loop.run_until_complete(self._async_get_glossary_by_guid(glossary_guid, server_name))
        return response

    async def _async_get_glossaries_by_name(self, glossary_name: str, effective_time: str = None,
                                            server_name: str = None, start_from: int = 0,
                                            page_size: int = None) -> dict | str:
        """ Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        validate_name(glossary_name)

        if effective_time is None:
            body = {"name": glossary_name}
        else:
            body = {"name": glossary_name, "effectiveTime": effective_time}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def get_glossaries_by_name(self, glossary_name: str, effective_time: str = None, server_name: str = None,
                               start_from: int = 0, page_size: int = None) -> dict | str:
        """ Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
            self._async_get_glossaries_by_name(glossary_name, effective_time, server_name, start_from, page_size))
        return response

    #
    # Glossary Categories
    #
    async def _async_create_category(self, glossary_guid: str, display_name: str, description: str,
                                     server_name: str = None) -> str:
        """ Create a new category within the specified glossary. Async Version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/categories")
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties":
                {
                    "class": "GlossaryCategoryProperties",
                    "qualifiedName": f"GlossaryCategory-{display_name}-{time.asctime()}",
                    "displayName": display_name,
                    "description": description
                }
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", None)

    def create_category(self, glossary_guid: str, display_name: str, description: str,
                        server_name: str = None) -> str:
        """ Create a new category within the specified glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
            self._async_create_category(glossary_guid, display_name, description, server_name))
        return response

    async def _async_get_glossary_for_category(self, glossary_category_guid: str, effective_time: str = None,
                                               server_name: str = None) -> dict | str:
        """ Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        body = {"class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"for-category/{glossary_category_guid}/retrieve")

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def get_glossary_for_category(self, glossary_category_guid: str, effective_time: str = None,
                                  server_name: str = None) -> dict | str:
        """ Retrieve the glossary metadata element for the requested category.  The optional request body allows you to
        specify that the glossary element should only be returned if it was effective at a particular time.

        Parameters
        ----------
        glossary_category_guid: str,
            Unique identifier for the glossary category.
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
            self._async_get_glossary_fpr_category(glossary_category_guid, effective_time, server_name))
        return response

    async def _async_find_glossary_categories(self, search_string: str, effective_time: str = None,
                                              starts_with: bool = False, ends_with: bool = False,
                                              ignore_case: bool = False, server_name: str = None, start_from: int = 0,
                                              page_size: int = None) -> list | str:
        """ Retrieve the list of glossary category metadata elements that contain the search string.
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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        validate_search_string(search_string)

        if search_string == '*':
            search_string = None

        body = {"class": "SearchStringRequestBody", "searchString": search_string, "effectiveTime": effective_time}
        body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"categories/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No Categories found")

    def find_glossary_categories(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                 ends_with: bool = False, ignore_case: bool = False, server_name: str = None,
                                 start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary category metadata elements that contain the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

           Parameters
           ----------
           search_string: str,
               Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

           effective_time: str, [default=None], optional
               Effective time of the query. If not specified will default to any time. Time format is
               "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
           server_name : str, optional
               The name of the server to  configure.
               If not provided, the server name associated with the instance is used.
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
            self._async_find_glossary_categories(search_string, effective_time, starts_with, ends_with, ignore_case,
                                                 server_name, start_from, page_size))

        return response

    async def _async_get_categories_for_glossary(self, glossary_guid: str, server_name: str = None, start_from: int = 0,
                                                 page_size: int = None) -> list | str:
        """ Return the list of categories associated with a glossary.
            Async version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_for_glossary(self, glossary_guid: str, server_name: str = None, start_from: int = 0,
                                    page_size: int = None) -> list | str:
        """ Return the list of categories associated with a glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identity of the glossary
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
            self._async_get_categories_for_glossary(glossary_guid, server_name, start_from, page_size))
        return response

    async def _async_get_categories_for_term(self, glossary_term_guid: str, server_name: str = None,
                                             start_from: int = 0, page_size: int = None) -> list | str:
        """ Return the list of categories associated with a glossary term.
            Async version.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term
        server_name : str, optional
            The name of the server to use.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{glossary_term_guid}/categories/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_for_term(self, glossary_term_guid: str, server_name: str = None, start_from: int = 0,
                                page_size: int = None) -> list | str:
        """ Return the list of categories associated with a glossary term.

        Parameters
        ----------
        glossary_term_guid: str,
            Unique identity of a glossary term
        server_name : str, optional
            The name of the server to use.
            If not provided, the server name associated with the instance is used.
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
            self._async_get_categories_for_term(glossary_term_guid, server_name, start_from, page_size))
        return response

    async def _async_get_categories_by_name(self, name: str, glossary_guid: str = None, status: [str] = ["ACTIVE"],
                                            server_name: str = None, start_from: int = 0,
                                            page_size: int = None) -> list | str:
        """ Retrieve the list of glossary category metadata elements that either have the requested qualified name or display name.
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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        validate_name(name)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/categories/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        body = {"class": "GlossaryNameRequestBody", "name": name, "glossaryGUID": glossary_guid,
                "limitResultsByStatus": status}

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No Categories found")

    def get_categories_by_name(self, name: str, glossary_guid: str = None, status: [str] = ["ACTIVE"],
                               server_name: str = None, start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary category metadata elements that either have the requested qualified name or display name.
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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
            self._async_get_categories_by_name(name, glossary_guid, status, server_name, start_from, page_size))
        return response

    async def _async_get_categories_by_guid(self, glossary_category_guid: str, effective_time: str = None,
                                            server_name: str = None) -> list | str:
        """  Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Async version.

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time, datetime, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/categories/"
               f"{glossary_category_guid}/retrieve")

        body = {"class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No Category found")

    def get_categories_by_guid(self, glossary_category_guid: str, effective_time: str = None,
                               server_name: str = None) -> list | str:
        """  Retrieve the requested glossary category metadata element.  The optional request body contain an effective
        time for the query..

        Parameters
        ----------
        glossary_category_guid: str
            The identity of the glossary category to search.
        effective_time, datetime, optional
            If specified, the category should only be returned if it was effective at the specified time.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
            self._async_get_categories_by_guid(glossary_category_guid, effective_time, server_name))
        return response

    async def _async_get_category_parent(self, glossary_category_guid: str, effective_time: str = None,
                                         server_name: str = None) -> list | str:
        """ Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/categories/"
               f"{glossary_category_guid}/parent/retrieve")

        body = {"class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No Parent Category found")

    def get_category_parent(self, glossary_category_guid: str, effective_time: str = None,
                            server_name: str = None) -> list | str:
        """ Glossary categories can be organized in a hierarchy. Retrieve the parent glossary category metadata
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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
            self._async_get_category_parent(glossary_category_guid, effective_time, server_name))
        return response

    #
    #  Terms
    #
    async def _async_create_controlled_glossary_term(self, glossary_guid: str, body: dict,
                                                     server_name: str = None) -> str:
        """ Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/terms/new-controlled"
               )

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_controlled_glossary_term(self, glossary_guid: str, body: dict, server_name: str = None) -> str:
        """ Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_create_controlled_glossary_term(glossary_guid, body, server_name))

        return response

    async def _async_create_term_copy(self, glossary_guid: str, glossary_term_guid: str, new_display_name: str,
                                      version_id: str, term_status: str = "PROPOSED", server_name: str = None) -> str:
        """ Create a new term from an existing term.

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
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)
        validate_guid(glossary_term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/terms/from-template/{glossary_term_guid}"
               )

        body = {
            "class": "GlossaryTemplateRequestBody",
            "elementProperties":
                {
                    "class": "TemplateProperties",
                    "qualifiedName": f"Term-{new_display_name}-{time.asctime()}",
                    "displayName": new_display_name,
                    "versionIdentifier": version_id
                },
            "glossaryTermStatus": term_status
        }

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_term_copy(self, glossary_guid: str, glossary_term_guid: str, new_display_name: str,
                         version_id: str, term_status: str = "PROPOSED", server_name: str = None) -> str:
        """ Create a new term from an existing term.

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
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_create_term_copy(glossary_guid, glossary_term_guid, new_display_name,
                                         version_id, term_status, server_name))

        return response

    async def _async_add_data_field_to_term(self, glossary_term_guid: str, body: dict,
                                            server_name: str = None) -> None:
        """ Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/{glossary_term_guid}/is-data-field"
               )

        await self._async_make_request("POST", url, body)
        return

    def add_data_field_to_term(self, glossary_term_guid: str, body: dict, server_name: str = None) -> None:
        """ Add the data field values classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_add_data_field_to_term(glossary_term_guid, body, server_name))

        return

    async def _async_add_confidentiality_to_term(self, glossary_term_guid: str,
                                                 confidentiality_level: int, server_name: str = None) -> None:
        """ Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/elements/"
               f"{glossary_term_guid}/confidentiality"
               )

        body = {
            "class": "ClassificationRequestBody",
            "properties":
                {
                    "class": "GovernanceClassificationProperties",
                    "levelIdentifier": confidentiality_level
                }
        }

        await self._async_make_request("POST", url, body)
        return

    def add_confidentiality_to_term(self, glossary_term_guid: str,
                                    confidentiality_level: int, server_name: str = None) -> str:
        """ Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_add_confidentiality_to_term(glossary_term_guid, confidentiality_level,
                                                    server_name))

        return

    async def _async_add_subject_area_to_term(self, glossary_term_guid: str, subject_area: str,
                                              server_name: str = None) -> None:
        """ Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/elements/"
               f"{glossary_term_guid}/subject-area-member"
               )

        body = {
            "class": "ClassificationRequestBody",
            "properties":
                {
                    "class": "SubjectAreaMemberProperties",
                    "subjectAreaName": subject_area
                }
        }

        await self._async_make_request("POST", url, body)
        return

    def add_subject_area_to_term(self, glossary_term_guid: str, subject_area: str, server_name: str = None) -> None:
        """ Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_add_subject_area_to_term(glossary_term_guid, subject_area,
                                                 server_name))

        return

    async def _async_update_term(self, glossary_term_guid: str, body: dict, is_merge_update: bool,
                                 server_name: str = None) -> None:
        """ Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            is_merge_update: bool
                Whether the data field values should be merged with existing definition or replace it.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_term_guid)
        is_merge_update_s = str(is_merge_update).lower()

        url = (
            f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate={is_merge_update_s}"
            )

        await self._async_make_request("POST", url, body)
        return

    def update_term(self, glossary_term_guid: str, body: dict, is_merge_update: bool,
                    server_name: str = None) -> None:
        """ Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            is_merge_update: bool
                Whether the data field values should be merged with existing definition or replace it.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_update_term(glossary_term_guid, body, is_merge_update, server_name))

        return

    async def _async_update_term_version_id(self, glossary_term_guid: str, new_version_identifier: str,
                                            server_name: str = None) -> None:
        """ Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate=true"
            )

        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties":
                {
                    "class": "GlossaryTermProperties",
                    "publishVersionIdentifier": new_version_identifier
                }
        }
        await self._async_make_request("POST", url, body)
        return

    def update_term_version_id(self, glossary_term_guid: str, new_version_identifier: str,
                               server_name: str = None) -> None:
        """ Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.

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
            self._async_update_term_version_id(glossary_term_guid, new_version_identifier, server_name))

        return

    async def _async_get_terms_for_category(self, glossary_category_guid: str, server_name: str = None,
                                            effective_time: str = None, start_from: int = 0,
                                            page_size: int = None) -> list | str:
        """ Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_category_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{glossary_category_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_category(self, glossary_category_guid: str, server_name: str = None,
                               effective_time: str = None, start_from: int = 0,
                               page_size: int = None) -> list | str:
        """ Retrieve ALL the glossary terms in a category.
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_category_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
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
            self._async_get_terms_for_category(glossary_category_guid, server_name, effective_time, start_from,
                                               page_size))

        return response

    async def _async_get_terms_for_glossary(self, glossary_guid: str, server_name: str = None,
                                            effective_time: str = None, start_from: int = 0,
                                            page_size: int = None) -> list | str:
        """ Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time : str, optional
                If specified, terms are potentially included if they are active at the`effective_time.
                Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)`
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

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_glossary(self, glossary_guid: str, server_name: str = None, effective_time: str = None,
                               start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time : str, optional
                If specified, terms are potentially returned if they are active at the `effective_time`
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
            self._async_get_terms_for_glossary(glossary_guid, server_name, effective_time, start_from, page_size))

        return response

    async def _async_get_term_relationships(self, term_guid: str, server_name: str = None,
                                            effective_time: str = None, start_from: int = 0,
                                            page_size: int = None) -> list | str:

        """ This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship..
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
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

        if server_name is None:
            server_name = self.server_name
        validate_guid(term_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/related-terms?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_term_relationships(self, term_guid: str, server_name: str = None, effective_time: str = None,
                               start_from: int = 0, page_size: int = None) -> list | str:

        """ This call retrieves details of the glossary terms linked to this glossary term.
        Notice the original org 1 glossary term is linked via the "SourcedFrom" relationship..
        Parameters
        ----------
            term_guid : str
                Unique identifier for the glossary term
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
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
            self._async_get_term_relationships(term_guid, server_name, effective_time, start_from, page_size))

        return response

    async def _async_get_glossary_for_term(self, term_guid: str, server_name: str = None,
                                           effective_time: str = None) -> dict | str:
        """ Retrieve the glossary metadata element for the requested term.  The optional request body allows you to specify
            that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.
        server_name : str, optional
            The name of the server. If not specified, the default server name will be used.
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
        if server_name is None:
            server_name = self.server_name
        validate_guid(term_guid)

        body = {"class": "EffectiveTimeQueryRequestBody", "effectiveTime": effective_time}
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"for-term/{term_guid}/retrieve")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "No glossary found")

    def get_glossary_for_term(self, term_guid: str, server_name: str = None,
                              effective_time: str = None) -> dict | str:
        """ Retrieve the glossary metadata element for the requested term.  The optional request body allows you to specify
            that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.
        server_name : str, optional
            The name of the server. If not specified, the default server name will be used.
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
        response = loop.run_until_complete(self._async_get_glossary_for_term(term_guid, server_name, effective_time))
        return response

    async def _async_get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [],
                                       server_name: str = None, effective_time: str = None,
                                       for_lineage: bool = False, for_duplicate_processing: bool = False,
                                       start_from: int = 0, page_size: int = None) -> list:
        """ Retrieve glossary terms by display name or qualified name. Async Version.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.
        server_name : str, optional
            The name of the server where the glossaries reside. If not provided, it will use the default server name.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size

        validate_name(term)

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {"class": "GlossaryNameRequestBody", "glossaryGUID": glossary_guid, "name": term,
                "effectiveTime": effective_time, "limitResultsByStatus": status_filter}
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-name?startFrom={start_from}&pageSize={page_size}&"
               f"&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")

    def get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [], server_name: str = None,
                          effective_time: str = None, for_lineage: bool = False,
                          for_duplicate_processing: bool = False, start_from: int = 0, page_size: int = None) -> list:
        """ Retrieve glossary terms by display name or qualified name.

           Parameters
           ----------
           term : str
               The term to search for in the glossaries.
           glossary_guid : str, optional
               The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
           status_filter : list, optional
               A list of status values to filter the search results. Default is an empty list, which means no filtering.
           server_name : str, optional
               The name of the server where the glossaries reside. If not provided, it will use the default server name.
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
            self._async_get_terms_by_name(term, glossary_guid, status_filter, server_name, effective_time, for_lineage,
                                          for_duplicate_processing, start_from, page_size))
        return response

    async def _async_get_terms_by_guid(self, term_guid: str, server_name: str = None) -> dict | str:
        """ Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.

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
        if server_name is None:
            server_name = self.server_name

        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/retrieve")

        response = await self._async_make_request("POST", url)
        return response.json().get("element", "No term found")

    def get_terms_by_guid(self, term_guid: str, server_name: str = None) -> dict | str:
        """ Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.

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
        response = loop.run_until_complete(self._async_get_terms_by_guid(term_guid, server_name))

        return response

    async def _async_get_terms_versions(self, term_guid: str, server_name: str = None, start_from: int = 0,
                                        page_size=None) -> dict | str:
        """ Retrieve the versions of a glossary term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
        if server_name is None:
            server_name = self.server_name

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/history?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("element", "No term found")

    def get_terms_versions(self, term_guid: str, server_name: str = None, start_from: int = 0,
                           page_size=None) -> dict | str:
        """ Retrieve the versions of a glossary term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
            self._async_get_terms_versions(term_guid, server_name, start_from, page_size))

        return response

    async def _async_get_term_revision_logs(self, term_guid: str, server_name: str = None, start_from: int = 0,
                                            page_size=None) -> dict | str:
        """ Retrieve the revision log history for a term. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
        if server_name is None:
            server_name = self.server_name

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/elements/"
               f"{term_guid}/notes/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No log found")

    def get_term_revision_logs(self, term_guid: str, server_name: str = None, start_from: int = 0,
                               page_size=None) -> dict | str:
        """ Retrieve the revision log history for a term.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
            self._async_get_term_revision_logs(term_guid, server_name, start_from, page_size))

        return response

    async def _async_get_term_revision_history(self, term_revision_log_guid: str, server_name: str = None,
                                               start_from: int = 0, page_size=None) -> dict | str:
        """ Retrieve the revision history for a glossary term. Async version.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
        if server_name is None:
            server_name = self.server_name

        if page_size is None:
            page_size = self.page_size

        validate_guid(term_revision_log_guid)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/note-logs/"
               f"{term_revision_log_guid}/notes/retrieve?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url)
        return response.json().get("elementList", "No logs found")

    def get_term_revision_history(self, term_revision_log_guid: str, server_name: str = None, start_from: int = 0,
                                  page_size=None) -> dict | str:
        """ Retrieve the revision history for a glossary term.

        Parameters
        ----------
        term_revision_log_guid : str
            The GUID of the glossary term revision log to retrieve.
        server_name : str, optional
            The name of the server to connect to. If not provided, the default server name will be used.
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
            self._async_get_term_revision_history(term_revision_log_guid, server_name, start_from, page_size))

        return response

    async def _async_find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                         effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                                         ignore_case: bool = False, for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, server_name: str = None,
                                         start_from: int = 0, page_size: int = None) -> list | str:

        """ Retrieve the list of glossary term metadata elements that contain the search string.

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
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == '*':
            search_string = None

        # validate_search_string(search_string)

        body = {"class": "GlossarySearchStringRequestBody", "glossaryGUID": glossary_guid,
                "searchString": search_string, "effectiveTime": effective_time, "limitResultsByStatus": status_filter}
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")  # return response.text

    def find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                            effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                            ignore_case: bool = False, for_lineage: bool = False,
                            for_duplicate_processing: bool = False, server_name: str = None, start_from: int = 0,
                            page_size: int = None) -> list | str:
        """ Retrieve the list of glossary term metadata elements that contain the search string.

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
               server_name : str, optional
                   The name of the server to  configure.
                   If not provided, the server name associated with the instance is used.
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
            self._async_find_glossary_terms(search_string, glossary_guid, status_filter, effective_time, starts_with,
                                            ends_with, ignore_case, for_lineage, for_duplicate_processing, server_name,
                                            start_from, page_size))

        return response

    #
    #   Feedback
    #
    async def _async_get_comment(self, commemtGUID: str, effective_time: str, server_name: str = None,
                                 for_lineage: bool = False, for_duplicate_processing: bool = False) -> dict | list:
        """ Retrieve the comment specified by the comment GUID """
        if server_name is None:
            server_name = self.server_name

        validate_guid(commemtGUID)

        if effective_time is None:
            effective_time = datetime.now().isoformat()

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {"effective_time": effective_time}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commemtGUID}?forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json()

    async def _async_add_comment_reply(self, commentGUID: str, is_public: bool, comment_type: str, comment_text: str,
                                       server_name: str = None, for_lineage: bool = False,
                                       for_duplicate_processing: bool = False) -> str:
        """ Reply to a comment """

        if server_name is None:
            server_name = self.server_name

        validate_guid(commentGUID)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {"class": "CommentRequestBody", "commentType": comment_type, "commentText": comment_text,
                "isPublic": is_public}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commentGUID}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response

    async def _async_update_comment(self, commentGUID: str, is_public: bool, comment_type: str, comment_text: str,
                                    server_name: str = None, is_merge_update: bool = False, for_lineage: bool = False,
                                    for_duplicate_processing: bool = False) -> str:
        """ Update the specified comment"""
        if server_name is None:
            server_name = self.server_name

        validate_guid(commentGUID)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {"class": "CommentRequestBody", "commentType": comment_type, "commentText": comment_text,
                "isPublic": is_public}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commentGUID}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response

    async def _async_find_comment(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                  effective_time: str = None, starts_with: bool = False, ends_with: bool = False,
                                  ignore_case: bool = False, for_lineage: bool = False,
                                  for_duplicate_processing: bool = False, server_name: str = None, start_from: int = 0,
                                  page_size: int = None):
        """Find comments by search string"""
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == '*':
            search_string = None

        # validate_search_string(search_string)

        body = {"class": "GlossarySearchStringRequestBody", "glossaryGUID": glossary_guid,
                "searchString": search_string, "effectiveTime": effective_time, "limitResultsByStatus": status_filter}
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")

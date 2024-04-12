"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""
import asyncio
import json
from datetime import datetime

# import json
from pyegeria._client import Client
from pyegeria._globals import enable_ssl_check
from pyegeria._validators import (
    validate_name,
    validate_guid,
    validate_search_string,
)
from pyegeria.utils import body_slimmer


class CollectionManager(Client):
    """
    Maintain and explore the contents of nested collections. These collections can be used to represent digital
    products, or collections of resources for a particular project or team. They can be used to organize assets and
    other resources into logical groups.

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

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            verify_flag: bool = enable_ssl_check,
            sync_mode: bool = True
    ):
        self.command_base: str = f"/api/open-metadata/collection-manager/collections"
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)

    #
    #       Retrieving Collections - https://egeria-project.org/concepts/collection
    #
    async def _async_get_linked_collections(self, parent_guid: str, server_name: str = None,
                                            start_from: int = 0, page_size: int = None) -> list | str:
        """  Returns the list of collections that are linked off of the supplied element. Async version.

        Parameters
        ----------
        parent_guid: str
            The list of collections linked off the parent guid.
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

        A list of collections linked off of the supplied element.

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

        body = {
            "string": parent_guid
        }

        url = f"{self.platform_url}/server/{server_name}{self.command_base}?startFrom={start_from}&pageSize={page_size}"

        resp = await self._async_make_request("POST", url, body)
        return resp

    def get_linked_collections(self, parent_guid: str, server_name: str = None,
                               start_from: int = 0, page_size: int = None) -> list | str:
        """  Returns the list of collections that are linked off of the supplied element.

        Parameters
        ----------
        parent_guid: str
            The list of collections linked off the parent guid.
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

        A list of collections linked off of the supplied element.

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
        resp = loop.run_until_complete(self._async_get_linked_collections(parent_guid, server_name,
                                                                              start_from, page_size)),
        return resp

    async def _async_get_classified_collections(self, classification: str, server_name: str = None,
                                                start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular classification. Async version.

        Parameters
        ----------
        classification: str
            The classification of the collection to inspect.
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
        list | str
            The list of collections (if found) with the specified classification. Returns a string if none found.

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
        if page_size is None:
            page_size = self.page_size

        body = {
            "string": classification
        }

        url = (f"{self.platform_url}/server/{server_name}{self.command_base}/by-classifications?"
               f"startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body)
        return resp

    def get_classified_collections(self, classification: str, server_name: str = None,
                                   start_from: int = 0, page_size: int = None) -> list | str:
        """  Returns the list of collections that are linked off of the supplied element.

        Parameters
        ----------
        classification: str
            The classification of the collection to inspect.
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

        A list of collections linked off of the supplied element.

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
        resp = loop.run_until_complete(self._async_classified_collections(classification, server_name,
                                                                          start_from, page_size)),
        return resp

    async def _async_find_collections(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                      ends_with: bool = False, ignore_case: bool = False,
                                      server_name: str = None,
                                      start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the search string. Returns a string if none found.

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

        body = {
            "string" : search_string
        }

        url = (f"{self.platform_url}/server/{server_name}{self.command_base}/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        resp = await self._async_make_request("POST", url, body)
        return resp

    def find_collections(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                         ends_with: bool = False, ignore_case: bool = False, server_name: str = None,
                         start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_find_collections(search_string, effective_time, starts_with,
                                        ends_with, ignore_case,
                                        server_name,start_from, page_size))

        return resp

    async def _async_get_collections_by_name(self, name: str, effective_time: str = None,
                                             server_name: str = None,
                                             start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular name.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the name. Returns a string if none found.

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

        validate_search_string(name)

        body = {
            "string": name
        }

        url = (f"{self.platform_url}/server/{server_name}{self.command_base}/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body)
        return resp

    def get_collections_by_name(self, name: str, effective_time: str = None, server_name: str = None,
                                start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_find_collections(name, effective_time,
                             server_name,start_from, page_size))

        return resp

    async def _async_get_collections_by_type(self, collection_type: str, effective_time: str = None,
                                      server_name: str = None,
                                      start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular collectionType. This is an optional text field in the
            collection element.

        Parameters
        ----------
        collection_type: str,
            collection_type to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the name. Returns a string if none found.

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

        validate_search_string(collection_type)

        body = {
            "string" : collection_type
        }

        url = (f"{self.platform_url}/server/{server_name}{self.command_base}/"
               f"by-collection-type?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body)
        return resp

    def get_collections_by_type(self, collection_type: str, effective_time: str = None, server_name: str = None,
                         start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_get_collections_by_type(collection_type, effective_time,
                             server_name,start_from, page_size))

        return resp

    async def _async_get_collection(self, collection_guid: str, effective_time: str = None,
                                     server_name: str = None,
                                     start_from: int = 0, page_size: int = None) -> dict | str:
        """ Return the properties of a specific collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

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

        validate_guid(collection_guid)

        url = f"{self.platform_url}/server/{server_name}{self.command_base}/{collection_guid}"

        resp = await self._async_make_request("POST", url)
        return resp

    def get_collection(self, collection_guid: str, effective_time: str = None, server_name: str = None,
                                start_from: int = 0, page_size: int = None) -> dict | str:
        """ Return the properties of a specific collection.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_get_collection(collection_guid, effective_time,
                                                       server_name, start_from, page_size))

        return resp


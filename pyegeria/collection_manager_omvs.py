"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""

import asyncio
from typing import Dict, Union, List, Optional

from loguru import logger

from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria._client import Client
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_GUID_RETURNED, NO_MEMBERS_FOUND
from pyegeria._validators import validate_guid, validate_search_string
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties)
from pyegeria.utils import body_slimmer, dynamic_catch



def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


# ("params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to "
# "the query string")


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result

from pyegeria._client_new import Client2

class CollectionManager(Client2):
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
        token: str
            An optional bearer token

    """


    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd


        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        result = self.get_platform_origin()
        logger.info(f"CollectionManager initialized, platform origin is: {result}")
        self.collection_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections")
        #
        #       Retrieving Collections - https://egeria-project.org/concepts/collection
        #


    @dynamic_catch
    async def _async_get_attached_collections(self, parent_guid: str, start_from: int = 0, page_size: int = 0,
                                              body: dict = None, output_format: str = "JSON",
                                              output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections that are linked off of the supplied element using the ResourceList
           relationship. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            If supplied, adds addition request details - for instance, to filter the results on collectionType
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict = None), optional, default = None
            The desired output columns/fields to include.

        Returns
        -------
        List

        A list of collections linked off of the supplied element.

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
        Sample body:
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collectionType value here"
        }

        """
        if body is None:
            body = {}

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/"
               f"metadata-elements/{parent_guid}/collections?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, None, output_format,
                                                    output_format_set=output_format_set)
        return elements


    def get_attached_collections(self, parent_guid: str, start_from: int = 0, page_size: int = 0, body: dict = None,
                                 output_format: str = "JSON", output_format_set: str | dict = None) -> list:
        """Returns the list of collections that are linked off of the supplied element using the ResourceList
           relationship. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            If supplied, adds addition request details - for instance, to filter the results on collectionType
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict = None), optional, default = None
                The desired output columns/fields to include.


        Returns
        -------
        List

        A list of collections linked off of the supplied element.

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
        Sample body:
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collectionType value here"
        }

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_attached_collections(parent_guid, start_from, page_size,
                                                 body, output_format, output_format_set))


    # @dynamic_catch
    async def _async_find_collections_w_body(self, body: dict, classification_name: str = None,
                                             starts_with: bool = True, ends_with: bool = False,
                                             ignore_case: bool = False, start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            The search string is located in the request body and is interpreted as a plain string. The full
            body allows complete control including status, asOfTime and effectiveTime.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        body: dict
            Details of the search request - see the notes below for details.
        classification_name: str, optional, default=None
            A classification name to filter on - for example, DataSpec for data specifications. If none,
            then all classifications are returned.
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
         output_format_set: str | dict , optional, default = None
            - The desired output columns/field options.
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

        Notes
        -----

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Data Product Development Journey"
        }

        """

        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        if classification_name in ["*", "Collections", "Collection"]:
            classification_name = None

        body_s = body_slimmer(body)
        url = (f"{self.collection_command_root}/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        if classification_name:
            url += f"&classificationName={classification_name}"

        response = await self._async_make_request("POST", url, body_s)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            # logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, classification_name,
                                                    output_format, output_format_set)
        return elements


    def find_collections_w_body(self, body: dict, classification_name: str = None, starts_with: bool = True,
                                ends_with: bool = False, ignore_case: bool = False, start_from: int = 0,
                                page_size: int = 0, output_format: str = 'JSON',
                                output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            The search string is located in the request body and is interpreted as a plain string. The full
            body allows complete control including status, asOfTime and effectiveTime.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        body: dict
            Details of the search request - see the notes below for details.
        classification_name: str, optional, default=None
            A classification name to filter on - for example, DataSpec for data specifications. If none,
            then all classifications are returned.
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
         output_format_set: str | dict , optional, default = None
                The desired output columns.
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

        Notes
        -----

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Data Product Development Journey"
        }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_collections_w_body(body, classification_name, starts_with, ends_with, ignore_case,
                                                start_from, page_size, output_format, output_format_set))


    @dynamic_catch
    async def _async_find_collections(self, search_string: str = '*', classification_name: str = None,
                                      starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            The search string is located in the request body and is interpreted as a plain string. The full
            body allows complete control including status, asOfTime and effectiveTime.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all collections (may be filtered by
            classification).
        classification_name: str, optional, default=None
            A classification name to filter on - for example, DataSpec for data specifications. If none,
            then all classifications are returned.
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
         output_format_set: str | dict , optional, default = None
            - The desired output columns/fields to include.
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

        body = {
            "class": "FilterRequestBody", "filter": search_string
            }

        resp = await self._async_find_collections_w_body(body, classification_name, starts_with, ends_with, ignore_case,
                                                         start_from, page_size, output_format, output_format_set)
        return resp

    @dynamic_catch
    def find_collections(self, search_string: str = '*', classification_name: str = None, starts_with: bool = True,
                         ends_with: bool = False, ignore_case: bool = False,
                         start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                         output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            The search string is located in the request body and is interpreted as a plain string. The full
            body allows complete control including status, asOfTime and effectiveTime.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str
            String to match against - None or '*' indicate match against all collections (may be filtered
        classification_name: str, optional, default=None
            A classification name to filter on - for example, DataSpec for data specifications. If none,
            then all classifications are returned.
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
         output_format_set: str | dict , optional, default = None
            - The desired output columns/fields to include.
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
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_collections(search_string, classification_name, starts_with, ends_with, ignore_case,
                                         start_from, page_size, output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collections_by_name(self, name: str, classification_name: str = None, body: dict = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections with a particular name.

            Parameters
            ----------
            name: str,
                name to use to find matching collections.
            classification_name: str, optional, default = None
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
         output_format_set: dict , optional, default = None
                The desired output columns/fields to include.

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

        if body is None:
            validate_search_string(name)
            body = {
                "class": "FilterRequestBody", "filter": name
                }

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ('classificationName', classification_name)])

        url = f"{self.collection_command_root}/by-name{possible_query_params}"

        response = await self._async_make_request("POST", url, body_slimmer(body))
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, filter, classification_name,
                                                    output_format, output_format_set)
        return elements


    def get_collections_by_name(self, name: str, classification_name: str = None, body: dict = None,
                                start_from: int = 0, page_size: int = None, output_format: str = 'JSON',
                                output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        classification_name: str, optional, default = None
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
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

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

        Args:
            as_of_time ():

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collections_by_name(name, classification_name, body, start_from, page_size,
                                                output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collections_by_type(self, collection_type: str, classification_name: str = None,
                                             body: dict = None, start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections with a particular collectionType. This is an optional text field in the
            collection element.

        Parameters
        ----------
        collection_type: str
            collection_type to use to find matching collections.
        classification_name: str, optional
            An optional filter on the search,  e.g., DataSpec
        body: dict, optional, default = None
            Provides, a full request body. If specified, the body filter parameter supercedes the collection_type
            parameter.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections matching the collection type. Returns a string if none found.

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
        Body sample:

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collection type here"
        }

        """

        if classification_name:
            classification_name = None if classification_name == '*' else classification_name

        if body is None:
            body = {
                "class": "FilterRequestBody", "filter": collection_type,
                }
        body_s = body_slimmer(body)

        possible_query_params = query_string(
            [("startFrom", start_from), ("pageSize", page_size), ('classificationName', classification_name)])

        url = f"{self.collection_command_root}/by-collection-type{possible_query_params}"

        response = await self._async_make_request("POST", url, body_s)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, filter, collection_type,
                                                    output_format, output_format_set)
        return elements


    def get_collections_by_type(self, collection_type: str, classification_name: str = None, body: dict = None,
                                start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections with a particular collectionType. This is an optional text field in the
            collection element.

        Parameters
        ----------
        collection_type: str
            collection_type to use to find matching collections.
        classification_name: str, optional
            An optional filter on the search, e.g., DataSpec
        body: dict, optional, default = None
            Provides, a full request body. If specified, the body filter parameter supersedes the collection_type
            parameter.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections of the specified collection type. Returns a string if none found.

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
        Body sample:

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collection type here"
        }

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collections_by_type(collection_type, classification_name, body, start_from, page_size,
                                                output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collection_by_guid(self, collection_guid: str, collection_type: str = None, body: dict = None,
                                            output_format: str = 'JSON',
                                            output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        collection_type: str, default = None, optional
            type of collection - Data Dictionary, Data Spec, Data Product, etc.
        body: dict, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

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

        Notes
        ----
        Body sample:
        {
          "class": "AnyTimeRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        validate_guid(collection_guid)

        url = f"{self.collection_command_root}/{collection_guid}"

        if body:
            response = await self._async_make_request("GET", url, body_slimmer(body))
        else:
            response = await self._async_make_request("GET", url)
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, collection_type,
                                                    output_format, output_format_set)
        return elements


    def get_collection_by_guid(self, collection_guid: str, collection_type: str = None, body: dict = None,
                               output_format: str = 'JSON', output_format_set: str | dict = None) -> dict | str:
        """ Return the properties of a specific collection. Async version.

            Parameters
            ----------
            collection_guid: str,
                unique identifier of the collection.
            collection_type: str, default = None, optional
                type of collection - Data Dictionary, Data Spec, Data Product, etc.
            body: dict, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
         output_format_set: dict , optional, default = None
                The desired output columns/fields to include.


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

            Notes
            ----
            Body sample:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collection_by_guid(collection_guid, collection_type, body,
                                               output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collection_members(self, collection_guid: str = None, collection_name: str = None,
                                            collection_qname: str = None, body: dict = None, start_from: int = 0,
                                            page_size: int = 0, output_format: str = "JSON",
                                            output_format_set: str | dict = None) -> list | str:
        """Return a list of elements that are a member of a collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        collection_name: str,
            display the name of the collection to return members for. If none, collection_guid
            or collection_qname are used.
        collection_qname: str,
            qualified name of the collection to return members for. If none, collection_guid
            or collection_name are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collection members in the collection.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        Body sample:
        {
          "class": "ResultsRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "limitResultsByStatus": ["ACTIVE"],
          "asOfTime": "{{$isoTimestamp}}",
          "sequencingOrder": "CREATION_DATE_RECENT",
          "sequencingProperty": ""
        }

        """

        if collection_guid is None:
            collection_guid = self.__get_guid__(collection_guid, collection_name, "name",
                                                collection_qname, None, )

        url = (f"{self.collection_command_root}/{collection_guid}/"
               f"members?startFrom={start_from}&pageSize={page_size}")

        if body:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_MEMBERS_FOUND)
        if type(elements) is str:
            logger.trace(f"No elements found for collection {collection_guid}")
            return NO_MEMBERS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.debug(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, None,
                                                    output_format, output_format_set)
        return elements


    def get_collection_members(self, collection_guid: str = None, collection_name: str = None,
                               collection_qname: str = None, body: dict = None, start_from: int = 0,
                               page_size: int = 0,
                               output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Return a list of elements that are a member of a collection.
        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        collection_name: str,
            display the name of the collection to return members for. If none, collection_guid
            or collection_qname are used.
        collection_qname: str,
            qualified name of the collection to return members for. If none, collection_guid
            or collection_name are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collection members in the collection.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        Body sample:
        {
          "class": "ResultsRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "limitResultsByStatus": ["ACTIVE"],
          "asOfTime": "{{$isoTimestamp}}",
          "sequencingOrder": "CREATION_DATE_RECENT",
          "sequencingProperty": ""
        }

    """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_collection_members(collection_guid, collection_name, collection_qname, body, start_from,
                                               page_size, output_format, output_format_set))

        return resp


    @dynamic_catch
    async def _async_get_collection_graph(self, collection_guid: str, body: dict = None, start_from: int = 0,
                                          page_size: int = 0, output_format: str = "JSON",
                                          output_format_set: str | dict = None) -> list | str:
        """ Return a graph of elements that are the nested members of a collection along
                with elements immediately connected to the starting collection.  The result
                includes a mermaid graph of the returned elements. Async version.

            Parameters
            ----------
            collection_guid: str,
                identity of the collection to return members for. If none, collection_name or
                collection_qname are used.
            body: dict, optional, default = None
                Providing the body allows full control of the request and replaces filter parameters.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: dict , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A graph anchored in the collection.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes:
            -----
                Body sample:
                {
                  "class": "ResultsRequestBody",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "limitResultsByStatus": ["ACTIVE"],
                  "asOfTime": "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }
            """

        url = (f"{self.collection_command_root}/{collection_guid}/"
               f"graph?startFrom={start_from}&pageSize={page_size}")

        if body:
            response = await self._async_make_request("POST", url, body_slimmer(body))
        else:
            response = await self._async_make_request("POST", url)

        elements = response.json().get("graph", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, None,
                                                    output_format, output_format_set)
        return elements


    def get_collection_graph(self, collection_guid: str = None, body: dict = None, start_from: int = 0,
                             page_size: int = 0, output_format: str = "JSON",
                             output_format_set: str | dict = None) -> list | str:
        """ Return a graph of elements that are the nested members of a collection along
            with elements immediately connected to the starting collection.  The result
            includes a mermaid graph of the returned elements.

        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A graph anchored in the collection.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
            Body sample:
            {
              "class": "ResultsRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collection_graph(collection_guid, body, start_from, page_size,
                                             output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collection_graph_w_body(self, collection_guid: str, body: dict = None, start_from: int = 0,
                                                 page_size: int = None, output_format: str = "JSON",
                                                 output_format_set: str | dict = None) -> list | str:
        """ Return a graph of elements that are the nested members of a collection along
            with elements immediately connected to the starting collection.  The result
            includes a mermaid graph of the returned elements. Async version.

            Parameters
            ----------
            collection_guid: str,
                identity of the collection to return members for.
            body: dict
                A dictionary containing the body of the request. See Note.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
    output_format_set: dict , optional, default = None

            Returns
            -------
            List | str

            A list of collection members in the collection.

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Note
            ____
            {
              "class": "ResultsRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }

        """

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.collection_command_root}/{collection_guid}/"
               f"graph?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("GET", url, body_slimmer(body))
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, None,
                                                    output_format, output_format_set)
        return elements


    def get_collection_graph_w_body(self, collection_guid: str, body: dict = None, start_from: int = 0,
                                    page_size: int = None, output_format: str = "JSON",
                                    output_format_set: str | dict = None) -> list | str:
        """ Return a graph of elements that are the nested members of a collection along
            with elements immediately connected to the starting collection.  The result
            includes a mermaid graph of the returned elements.

            Parameters
            ----------
            collection_guid: str,
               identity of the collection to return members for.
            body: dict
               A dictionary containing the body of the request. See Note.
            start_from: int, [default=0], optional
                       When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
               The number of items to return in a single page. If not specified, the default will be taken from
               the class instance.
            output_format: str, default = "JSON"
               - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
             output_format_set: str | dict  , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

            A list of collection members in the collection.

            Raises
            ------
            InvalidParameterException
               If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
               Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Note
            ____
            {
              "class": "ResultsRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }

       """

        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collection_graph_w_body(collection_guid, body, start_from,
                                                    page_size, output_format, output_format_set))

        #
        #   Create collection methods
        #

        ###
        # =====================================================================================================================
        # Create Collections: https://egeria-project.org/concepts/collection
        # These requests use the following parameters:
        #
        # anchorGUID - the unique identifier of the element that should be the anchor for the new element. Set to
        # null if
        # no anchor,
        # or if this collection is to be its own anchor.
        #
        # isOwnAnchor -this element should be classified as its own anchor or not.  The default is false.
        #
        # parentGUID - the optional unique identifier for an element that should be connected to the newly
        # created element.
        # If this property is specified, parentRelationshipTypeName must also be specified
        #
        # parentRelationshipTypeName - the name of the relationship, if any, that should be established between
        # the new
        # element and the parent element.
        # Examples could be "ResourceList" or "DigitalServiceProduct".
        #
        # parentAtEnd1 -identifies which end any parent entity sits on the relationship.
        #


    @dynamic_catch
    async def _async_create_collection_w_body(self, body: dict, classification_name: str = None) -> str:
        """ Create a new generic collection.
            Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.
        classification_name: str, optional, default=None
            Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----

        Sample body:
        {
        "class": "NewElementRequestBody",
          "isOwnAnchor" : true,
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "collectionType": "Add appropriate valid value for type"
          }
        }


        or
        {
          "class": "NewElementRequestBody",
          "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor" : False,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName" : "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "collectionType": "Add appropriate valid value for type"
          }
        }
        """
        possible_query_params = query_string([("classificationName", classification_name)])
        url = f"{self.collection_command_root}{possible_query_params}"

        resp = await self._async_make_request("POST", url, body)
        logger.info(f"Create collection with GUID: {resp.json().get['guid']}")
        return resp.json().get("guid", NO_GUID_RETURNED)


    def create_collection_w_body(self, body: dict, classification_name: str = None, ) -> str:
        """ Create a new generic collection.
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.
        classification_name: str, optional, default=None
            Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----

        Sample body:
        {
        "class": "NewElementRequestBody",
          "isOwnAnchor" : true,
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "collectionType": "Add appropriate valid value for type"
          }
        }
        or
        {
          "class": "NewElementRequestBody",
          "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor" : False,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName" : "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "collectionType": "Add appropriate valid value for type"
          }
        }
        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection_w_body(body, classification_name))


    @dynamic_catch
    async def _async_create_collection(self, display_name: str, description: str, is_own_anchor: bool = True,
                                       classification_name: str = None, anchor_guid: str = None,
                                       parent_guid: str = None, parent_relationship_type_name: str = None,
                                       parent_at_end1: bool = True, collection_type: str = None,
                                       anchor_scope_guid: str = None, additional_properties: dict = None,
                                       extended_properties: dict = None) -> str:
        """ Create a new generic collection.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        classification_name: str
            Type of collection to create; e.g RootCollection, Folder, ResultsSet, DigitalProduct, HomeCollection,
            RecentAccess, WorkItemList, etc.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        is_own_anchor_s = str(is_own_anchor).lower()
        parent_at_end1_s = str(parent_at_end1).lower()

        possible_query_params = query_string([("classificationName", classification_name)])

        url = f"{self.collection_command_root}{possible_query_params}"
        if classification_name is not None:
            qualified_name = self.__create_qualified_name__(classification_name, display_name)
        else:
            qualified_name = self.__create_qualified_name__("Collection", display_name)

        body = {
            "class": "NewElementRequestBody", "anchorGUID": anchor_guid, "anchorScopeGUID": anchor_scope_guid,
            "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
            "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1_s,
            "properties": {
                "class": "CollectionProperties", "qualifiedName": qualified_name, "name": display_name,
                "description": description, "collectionType": collection_type,
                "additionalProperties": additional_properties, "extendedProperties": extended_properties
                },
            }

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        return resp.json().get("guid", NO_GUID_RETURNED)


    def create_collection(self, display_name: str, description: str, is_own_anchor: bool = True,
                          classification_name: str = None, anchor_guid: str = None, parent_guid: str = None,
                          parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                          collection_type: str = None, anchor_scope_guid: str = None,
                          additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new generic collection.
            Create Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        classification_name: str
            Type of collection to create; e.g RootCollection, Folder, ResultsSet, DigitalProduct, HomeCollection,
            RecentAccess, WorkItemList, etc.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name, description, is_own_anchor, classification_name,
                                          anchor_guid,
                                          parent_guid, parent_relationship_type_name, parent_at_end1,
                                          collection_type,
                                          anchor_scope_guid, additional_properties, extended_properties))


    @dynamic_catch
    async def _async_create_generic_collection(self, display_name: str, description: str,
                                               qualified_name: str = None,
                                               is_own_anchor: bool = True, url_item=None,
                                               classification_name: str = None, anchor_guid: str = None,
                                               parent_guid: str = None, parent_relationship_type_name: str = None,
                                               parent_at_end1: bool = True, collection_type: str = None,
                                               anchor_scope_guid: str = None, additional_properties: dict = None,
                                               extended_properties: dict = None) -> str:
        """ Create a new generic collection.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        classification_name: str
            Type of collection to create; e.g RootCollection, Folder, ResultsSet, DigitalProduct, HomeCollection,
            RecentAccess, WorkItemList, etc.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Args:
            url_item ():
            qualified_name ():

        """

        is_own_anchor_s = str(is_own_anchor).lower()
        parent_at_end1_s = str(parent_at_end1).lower()

        url = f"{self.collection_command_root}/{url_item}"
        if qualified_name is None:
            if classification_name is not None:
                qualified_name = self.__create_qualified_name__(classification_name, display_name)
            else:
                qualified_name = self.__create_qualified_name__("Collection", display_name)

        body = {
            "class": "NewElementRequestBody", "anchorGUID": anchor_guid, "anchorScopeGUID": anchor_scope_guid,
            "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
            "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1_s,
            "properties": {
                "class": "CollectionProperties", "qualifiedName": qualified_name, "name": display_name,
                "description": description, "collectionType": collection_type,
                "additionalProperties": additional_properties, "extendedProperties": extended_properties
                },
            }

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    @dynamic_catch
    async def _async_create_root_collection(self, display_name: str, description: str, qualified_name: str = None,
                                            is_own_anchor: bool = True, anchor_guid: str = None,
                                            parent_guid: str = None, parent_relationship_type_name: str = None,
                                            parent_at_end1: bool = True, collection_type: str = None,
                                            anchor_scope_guid: str = None,

                                            additional_properties: dict = None,
                                            extended_properties: dict = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
        collection
        hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor, url_item="root-collection",
                                                           classification_name="RootCollection",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_root_collection(self, display_name: str, description: str, qualified_name: str = None,
                               is_own_anchor: bool = True, anchor_guid: str = None, parent_guid: str = None,
                               parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                               collection_type: str = None, anchor_scope_guid: str = None,

                               additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new collection with the RootCollection classification.
            Used to identify the top of a collection hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_root_collection(display_name, description, qualified_name, is_own_anchor,
                                               anchor_guid,
                                               parent_guid, parent_relationship_type_name, parent_at_end1,
                                               collection_type, anchor_scope_guid, additional_properties,
                                               extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_data_spec_collection(self, display_name: str, description: str,
                                                 qualified_name: str = None,
                                                 is_own_anchor: bool = True, anchor_guid: str = None,
                                                 parent_guid: str = None, parent_relationship_type_name: str = None,
                                                 parent_at_end1: bool = True, collection_type: str = None,
                                                 anchor_scope_guid: str = None, additional_properties: dict = None,
                                                 extended_properties: dict = None) -> str:
        """ Create a new collection with the DataSpec classification.  Used to identify a collection of data
        structures and
            data fields used to define data requirements for a project or initiative.
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="data-spec-collection",
                                                           classification_name="DataSpec", anchor_guid=anchor_guid,
                                                           parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_data_spec_collection(self, display_name: str, description: str, qualified_name: str = None,
                                    is_own_anchor: bool = True, anchor_guid: str = None, parent_guid: str = None,
                                    parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                    collection_type: str = None, anchor_scope_guid: str = None,

                                    additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new collection with the DataSpec classification.  Used to identify a collection of data
        structures and
            data fields used to define data requirements for a project or initiative.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_data_spec_collection(display_name, description, qualified_name, is_own_anchor,
                                                    anchor_guid, parent_guid, parent_relationship_type_name,
                                                    parent_at_end1, collection_type, anchor_scope_guid,
                                                    additional_properties, extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_data_dictionary_collection(self, display_name: str, description: str,
                                                       qualified_name: str = None, is_own_anchor: bool = True,
                                                       anchor_guid: str = None, parent_guid: str = None,
                                                       parent_relationship_type_name: str = None,
                                                       parent_at_end1: bool = True, collection_type: str = None,
                                                       anchor_scope_guid: str = None,
                                                       additional_properties: dict = None,
                                                       extended_properties: dict = None) -> str:
        """ Create a new collection with the DataDictionary classification.  Used to identify a collection of data
        structures and
            data fields used to define data requirements for a project or initiative.
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="data-dictionary-collection",
                                                           classification_name="DataDictionary",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_data_dictionary_collection(self, display_name: str, description: str, qualified_name: str = None,
                                          is_own_anchor: bool = True, anchor_guid: str = None,
                                          parent_guid: str = None,
                                          parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                          collection_type: str = None, anchor_scope_guid: str = None,

                                          additional_properties: dict = None,
                                          extended_properties: dict = None) -> str:
        """ Create a new collection with the DataSpec classification.  Used to identify a collection of data
        structures and
            data fields used to define data requirements for a project or initiative.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_data_dictionary_collection(display_name, description, qualified_name, is_own_anchor,
                                                          anchor_guid, parent_guid, parent_relationship_type_name,
                                                          parent_at_end1, collection_type, anchor_scope_guid,
                                                          additional_properties, extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_folder_collection(self, display_name: str, description: str, qualified_name: str = None,
                                              is_own_anchor: bool = True, anchor_guid: str = None,
                                              parent_guid: str = None, parent_relationship_type_name: str = None,
                                              parent_at_end1: bool = True, collection_type: str = None,
                                              anchor_scope_guid: str = None,

                                              additional_properties: dict = None,
                                              extended_properties: dict = None) -> str:
        """ Create a new collection with the Folder classification.  This is used to identify the organizing
        collections
            in a collection hierarchy.
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor, url_item="folder",
                                                           classification_name="Folder", anchor_guid=anchor_guid,
                                                           parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_folder_collection(self, display_name: str, description: str, qualified_name: str = None,
                                 is_own_anchor: bool = True, anchor_guid: str = None, parent_guid: str = None,
                                 parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                 collection_type: str = None, anchor_scope_guid: str = None,

                                 additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new collection with the Folder classification.  This is used to identify the organizing
        collections
            in a collection hierarchy.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_folder_collection(display_name, description, qualified_name, is_own_anchor,
                                                 anchor_guid,
                                                 parent_guid, parent_relationship_type_name, parent_at_end1,
                                                 collection_type, anchor_scope_guid, additional_properties,
                                                 extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_context_event_collection(self, display_name: str, description: str,
                                                     qualified_name: str = None, is_own_anchor: bool = True,
                                                     anchor_guid: str = None, parent_guid: str = None,
                                                     parent_relationship_type_name: str = None,
                                                     parent_at_end1: bool = True, collection_type: str = None,
                                                     anchor_scope_guid: str = None,
                                                     additional_properties: dict = None,
                                                     extended_properties: dict = None) -> str:
        """ Create a new collection with the ContextEventCollection classification.  This is used to group context
        events together.
            For example, the collection may be a series of events that affect a set of resources.
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="context-event-collection",
                                                           classification_name="CtxEventCollection",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_context_event_collection(self, display_name: str, description: str, qualified_name: str = None,
                                        is_own_anchor: bool = True, anchor_guid: str = None,
                                        parent_guid: str = None,
                                        parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                        collection_type: str = None, anchor_scope_guid: str = None,

                                        additional_properties: dict = None,
                                        extended_properties: dict = None) -> str:
        """ Create a new collection with the ContextEventCollection classification.  This is used to group context
        events together.
            For example, the collection may be a series of events that affect a set of resources.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_context_event_collection(display_name, description, qualified_name, is_own_anchor,
                                                        anchor_guid, parent_guid, parent_relationship_type_name,
                                                        parent_at_end1, collection_type, anchor_scope_guid,
                                                        additional_properties, extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_name_space_collection(self, display_name: str, description: str,
                                                  qualified_name: str = None,
                                                  is_own_anchor: bool = True, anchor_guid: str = None,
                                                  parent_guid: str = None,
                                                  parent_relationship_type_name: str = None,
                                                  parent_at_end1: bool = True, collection_type: str = None,
                                                  anchor_scope_guid: str = None, additional_properties: dict = None,
                                                  extended_properties: dict = None) -> str:
        """ Create a new collection with the Namespace classification.  This is used to group elements that
        belong to
        the same namespace.
         For example, the collection may be a series of processes that are recording OpenLineage under a single
         namespace.
            Async version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="namespace-collection",
                                                           classification_name="NamespaceCollection",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_name_space_collection(self, display_name: str, description: str, qualified_name: str = None,
                                     is_own_anchor: bool = True, anchor_guid: str = None, parent_guid: str = None,
                                     parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                     collection_type: str = None, anchor_scope_guid: str = None,
                                     additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new collection with the Namespace classification.  This is used to group elements that
        belong to
        the same namespace.
         For example, the collection may be a series of processes that are recording OpenLineage under a single
         namespace.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_name_space_collection(display_name, description, qualified_name, is_own_anchor,
                                                     anchor_guid, parent_guid, parent_relationship_type_name,
                                                     parent_at_end1, collection_type, anchor_scope_guid))
        return resp


    @dynamic_catch
    async def _async_create_event_set_collection(self, display_name: str, description: str,
                                                 qualified_name: str = None,
                                                 is_own_anchor: bool = True, anchor_guid: str = None,
                                                 parent_guid: str = None, parent_relationship_type_name: str = None,
                                                 parent_at_end1: bool = True, collection_type: str = None,
                                                 anchor_scope_guid: str = None,

                                                 additional_properties: dict = None,
                                                 extended_properties: dict = None) -> str:
        """ Create a new collection with the EventSet classification.  This is used to group event schemas together.
            For example, the collection may describe a set of events emitted by a specific system or to disseminate
            information about a certain situation.
            Async Version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="event-set-collection",
                                                           classification_name="EventSetCollection",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_event_set_collection(self, display_name: str, description: str, qualified_name: str = None,
                                    is_own_anchor: bool = True, anchor_guid: str = None, parent_guid: str = None,
                                    parent_relationship_type_name: str = None, parent_at_end1: bool = True,
                                    collection_type: str = None, anchor_scope_guid: str = None,

                                    additional_properties: dict = None, extended_properties: dict = None) -> str:
        """ Create a new collection with the EventSet classification.  This is used to group event schemas together.
            For example, the collection may describe a set of events emitted by a specific system or to disseminate
            information about a certain situation.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_event_set_collection(display_name, description, qualified_name, is_own_anchor,
                                                    anchor_guid, parent_guid, parent_relationship_type_name,
                                                    parent_at_end1, collection_type, anchor_scope_guid,
                                                    additional_properties, extended_properties))
        return resp


    @dynamic_catch
    async def _async_create_naming_standard_ruleset_collection(self, display_name: str, description: str,
                                                               qualified_name: str = None,
                                                               is_own_anchor: bool = True,
                                                               anchor_guid: str = None, parent_guid: str = None,
                                                               parent_relationship_type_name: str = None,
                                                               parent_at_end1: bool = True,
                                                               collection_type: str = None,
                                                               anchor_scope_guid: str = None,
                                                               additional_properties: dict = None,
                                                               extended_properties: dict = None) -> str:
        """ Create a new collection with the NamingStandardRuleSet classification.  This is used to group naming
        standard rule
            governance definitions together.
            Async Version.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        resp = await self._async_create_generic_collection(display_name, description, qualified_name,
                                                           is_own_anchor=is_own_anchor,
                                                           url_item="naming-standard-rule-set-collection",
                                                           classification_name="NamingRulesCollection",
                                                           anchor_guid=anchor_guid, parent_guid=parent_guid,
                                                           parent_relationship_type_name=parent_relationship_type_name,
                                                           parent_at_end1=parent_at_end1,
                                                           collection_type=collection_type,
                                                           anchor_scope_guid=anchor_scope_guid,
                                                           additional_properties=additional_properties,
                                                           extended_properties=extended_properties)

        return resp


    def create_naming_standard_ruleset_collection(self, display_name: str, description: str,
                                                  qualified_name: str = None,
                                                  is_own_anchor: bool = True, anchor_guid: str = None,
                                                  parent_guid: str = None,
                                                  parent_relationship_type_name: str = None,
                                                  parent_at_end1: bool = True, collection_type: str = None,
                                                  anchor_scope_guid: str = None, additional_properties: dict = None,
                                                  extended_properties: dict = None) -> str:
        """ Create a new collection with the NamingStandardRuleSet classification.  This is used to group naming
        standard rule
            governance definitions together.

        Parameters
        ----------
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        qualified_name: str, optional, defaults to None
            Allows user to specify a qualified name of the collection.
        is_own_anchor: bool, optional, defaults to True
            Indicates if the collection should be classified as its own anchor or not.
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element. Set to null if no
            anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool, defaults to True
            Identifies which end any parent entity sits on the relationship.
        collection_type: str
            Adds an user supplied valid value for the collection type.
        anchor_scope_guid: str, optional, defaults to None
            optional GUID of search scope
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(
            self._async_create_naming_standard_ruleset_collection(display_name, description, qualified_name,
                                                                  is_own_anchor, anchor_guid, parent_guid,
                                                                  parent_relationship_type_name, parent_at_end1,
                                                                  collection_type, anchor_scope_guid))
        return resp

        #
        #
        #


    @dynamic_catch
    async def _async_create_collection_from_template(self, body: dict) -> str:
        """Create a new metadata element to represent a collection using an existing metadata element as a template.
        The template defines additional classifications and relationships that are added to the new collection.
        Async version.

        Parameters
        ----------

        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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

        url = f"{self.collection_command_root}/from-template"

        resp = await self._async_make_request("POST", url, body)
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    def create_collection_from_template(self, body: dict) -> str:
        """Create a new metadata element to represent a collection using an existing metadata element as a template.
        The template defines additional classifications and relationships that are added to the new collection.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        resp = loop.run_until_complete(self._async_create_collection_from_template(body))
        return resp

        #
        # Manage collections
        #


    @dynamic_catch
    async def _async_update_collection(self, collection_guid: str, qualified_name: str = None,
                                       display_name: str = None,
                                       description: str = None, collection_type: str = None,

                                       additional_properties: dict = None, extended_properties: dict = None,
                                       replace_all_props: bool = False) -> None:
        """Update the properties of a collection.  Async version.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        qualified_name: str, optional, defaults to None
            The qualified name of the collection to update.
        display_name: str, optional, defaults to None
           The display name of the element. Will also be used as the basis of the qualified_name.
        description: str, optional, defaults to None
           A description of the collection.
        collection_type: str, optional, defaults to None
           Add appropriate valid value for the collection type.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
         If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
         Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
         The principle specified by the user_id does not have authorization for the requested action
        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.collection_command_root}/{collection_guid}/update?"
               f"replaceAllProperties={replace_all_props_s}")

        body = {
            "class": "UpdateElementRequestBody", "properties": {
                "class": "CollectionProperties", "qualifiedName": qualified_name, "name": display_name,
                "description": description, "collectionType": collection_type,
                "additionalProperties": additional_properties, "extendedProperties": extended_properties
                }
            }
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        logger.info(f"Successfully updated {collection_guid}")


    def update_collection(self, collection_guid, qualified_name: str = None, display_name: str = None,
                          description: str = None, collection_type: str = None, additional_properties: dict = None,
                          extended_properties: dict = None, replace_all_props: bool = False) -> None:
        """Update the properties of a collection.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        qualified_name: str
            The qualified name of the collection to update.
        display_name: str
           The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
           A description of the collection.
        collection_type: str
           Add appropriate valid value for the collection type.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.
        additional_properties: dict, optional, defaults to None
            User specified Additional properties to add to the collection definition.
        extended_properties: dict, optional, defaults to None
            Properties defined by extensions to Egeria types to add to the collection definition.


        Returns
        -------
        Nothing

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
        loop.run_until_complete(
            self._async_update_collection(collection_guid, qualified_name, display_name, description,
                                          collection_type,

                                          additional_properties, extended_properties, replace_all_props))


    @dynamic_catch
    async def _async_update_collection_w_body(self, collection_guid: str, body: dict,
                                              replace_all_props: bool = False) -> None:
        """Update the properties of a collection.  Async version.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        body: dict
            The body of the request containing the details.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.

        Returns
        -------
        Nothing

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
           {
              "class" : "UpdateElementRequestBody",
              "properties": {
                "class" : "CollectionProperties",
                "qualifiedName": "Must provide a unique name here",
                "name" : "Add display name here",
                "description" : "Add description of the collection here",
                "collectionType": "Add appropriate valid value for type"
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.collection_command_root}/{collection_guid}/update?"
               f"replaceAllProperties={replace_all_props_s}")

        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        logger.info(f"Updated properties of collection {collection_guid}")


    def update_collection_w_body(self, collection_guid: str, body: dict, replace_all_props: bool = False) -> None:
        """Update the properties of a collection.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        body: dict
            The body of the request containing the details.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.

        Returns
        -------
        Nothing

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
           {
              "class" : "UpdateElementRequestBody",
              "properties": {
                "class" : "CollectionProperties",
                "qualifiedName": "Must provide a unique name here",
                "name" : "Add display name here",
                "description" : "Add description of the collection here",
                "collectionType": "Add appropriate valid value for type"
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }


        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_collection_w_body(collection_guid, body, replace_all_props))

        #
        #   Digital Products
        #


    @dynamic_catch
    async def _async_create_digital_product(self, body: dict) -> str:
        """ Create a new collection that represents a digital product. To set a lifecycle status
            use a NewDigitalProductRequestBody which has a default status of DRAFT. Using a
            NewElementRequestBody sets the status to ACTIVE.
            Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:

        Without lifecycle status:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor" : false,
          "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName" : "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "collectionType": "Add appropriate valid value for type",
            "collectionOrder" : "OTHER",
            "orderByPropertyName" : "Add property name if 'collectionOrder' is OTHER"
          },
          "digitalProductProperties" : {
            "class" : "DigitalProductProperties",
            "productStatus" : "ACTIVE",
            "productName" : "Add name here",
            "productType" : "Add valid value here",
            "description" : "Add description here",
            "introductionDate" : "date",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "currentVersion": "V1.0",
            "nextVersion": "V1.1",
            "withdrawDate": "date",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          }
        }

        With a lifecycle, the body is:
        {
          "class" : "NewDigitalProductRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct:Add product name here",
            "userDefinedStatus" : "Optional value here - used when initial status is OTHER",
            "name" : "Product display name",
            "description" : "Add description of product and its expected usage here",
            "identifier" : "Add product identifier here",
            "productName" : "Add product name here",
            "productType" : "Periodic Delta",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "introductionDate" : "date",
            "nextVersionDate": "date",
            "withdrawDate": "date",
            "currentVersion": "V0.1",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "initialStatus" : "DRAFT",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
        UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
        OTHER.  If using OTHER, set the userDefinedStatus with the status value you want.
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    def create_digital_product(self, body: dict) -> str:
        """ Create a new collection that represents a digital product. To set a lifecycle status
               use a NewDigitalProductRequestBody which has a default status of DRAFT. Using a
               NewElementRequestBody sets the status to ACTIVE.

           Parameters
           ----------
           body: dict
               A dict representing the details of the collection to create.

           Returns
           -------
           str - the guid of the created collection

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
           Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
           be valid dates if specified, otherwise you will get a 400 error response.

           JSON Structure looks like:

           Without lifecycle status:
           {
             "class" : "NewElementRequestBody",
             "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
             "isOwnAnchor" : false,
             "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
             "parentRelationshipTypeName" : "open metadata type name",
             "parentAtEnd1": true,
             "properties": {
               "class" : "CollectionProperties",
               "qualifiedName": "Must provide a unique name here",
               "name" : "Add display name here",
               "description" : "Add description of the collection here",
               "collectionType": "Add appropriate valid value for type",
               "collectionOrder" : "OTHER",
               "orderByPropertyName" : "Add property name if 'collectionOrder' is OTHER"
             },
             "digitalProductProperties" : {
               "class" : "DigitalProductProperties",
               "productStatus" : "ACTIVE",
               "productName" : "Add name here",
               "productType" : "Add valid value here",
               "description" : "Add description here",
               "introductionDate" : "date",
               "maturity" : "Add valid value here",
               "serviceLife" : "Add the estimated lifetime of the product",
               "currentVersion": "V1.0",
               "nextVersion": "V1.1",
               "withdrawDate": "date",
               "additionalProperties": {
                 "property1Name" : "property1Value",
                 "property2Name" : "property2Value"
               }
             }
           }

           With a lifecycle, the body is:
           {
             "class" : "NewDigitalProductRequestBody",
             "isOwnAnchor" : true,
             "anchorScopeGUID" : "optional GUID of search scope",
             "parentGUID" : "xxx",
             "parentRelationshipTypeName" : "CollectionMembership",
             "parentAtEnd1": true,
             "properties": {
               "class" : "DigitalProductProperties",
               "qualifiedName": "DigitalProduct:Add product name here",
               "userDefinedStatus" : "Optional value here - used when initial status is OTHER",
               "name" : "Product display name",
               "description" : "Add description of product and its expected usage here",
               "identifier" : "Add product identifier here",
               "productName" : "Add product name here",
               "productType" : "Periodic Delta",
               "maturity" : "Add valid value here",
               "serviceLife" : "Add the estimated lifetime of the product",
               "introductionDate" : "date",
               "nextVersionDate": "date",
               "withdrawDate": "date",
               "currentVersion": "V0.1",
               "additionalProperties": {
                 "property1Name" : "property1Value",
                 "property2Name" : "property2Value"
               }
             },
             "initialStatus" : "DRAFT",
             "externalSourceGUID": "add guid here",
             "externalSourceName": "add qualified name here",
             "effectiveTime" : "{{$isoTimestamp}}",
             "forLineage" : false,
             "forDuplicateProcessing" : false
           }

           The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
           UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
           OTHER.  If using OTHER, set the userDefinedStatus with the status value you want.
           """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_digital_product(body))
        return resp


    @dynamic_catch
    async def _async_update_digital_product(self, collection_guid: str, body: dict,
                                            replace_all_props: bool = False, ):
        """Update the properties of the DigitalProduct classification attached to a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {"class": "UpdateElementRequestBody",
        "properties": {
              "class" : "DigitalProductProperties",
              "productName" : "Add name here",
              "productType" : "Add valid value here",
              "description" : "Add description here",
              "introductionDate" : "date",
              "maturity" : "Add valid value here",
              "serviceLife" : "Add the estimated lifetime of the product",
              "currentVersion": "V1.0",
              "nextVersion": "V1.1",
              "withdrawDate": "date",
              "additionalProperties": {
                "property1Name" : "property1Value",
                "property2Name" : "property2Value"
              }
            }
         }
        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"{collection_guid}/update?replaceAllProperties={replace_all_props_s}")

        await self._async_make_request("POST", url, body)
        logger.info(f'Updated properties of DigitalProduct: {collection_guid}')


    def update_digital_product(self, collection_guid: str, body: dict, replace_all_props: bool = False, ):
        """Update the properties of the DigitalProduct classification attached to a collection.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "DigitalProductProperties",
          "productStatus" : "ACTIVE",
          "productName" : "Add name here",
          "productType" : "Add valid value here",
          "description" : "Add description here",
          "introductionDate" : "date",
          "maturity" : "Add valid value here",
          "serviceLife" : "Add the estimated lifetime of the product",
          "currentVersion": "V1.0",
          "nextVersion": "V1.1",
          "withdrawDate": "date",
          "additionalProperties": {
            "property1Name" : "property1Value",
            "property2Name" : "property2Value"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_product(collection_guid, body, replace_all_props))


    @dynamic_catch
    async def _async_update_digital_product_status(self, digital_prod_guid: str, body: dict):
        """Update the status of a DigitalProduct collection. Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product collection to update.
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
           {
              "class": "DigitalProductStatusRequestBody",
              "status": "APPROVED",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{digital_prod_guid}/update=status")

        await self._async_make_request("POST", url, body)
        logger.info(f'Updated status of DigitalProduct: {digital_prod_guid}')


    def update_digital_product_status(self, digital_prod_guid: str, body: dict):
        """Update the status of a DigitalProduct collection. Async version.

            Parameters
            ----------
            digital_prod_guid: str
                The guid of the digital product collection to update.
            body: dict
                A dict representing the details of the collection to create.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
               {
                  "class": "DigitalProductStatusRequestBody",
                  "status": "APPROVED",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_product_status(digital_prod_guid, body))


    @dynamic_catch
    async def _async_link_digital_product_dependency(self, upstream_digital_prod_guid: str,
                                                     downstream_digital_prod_guid: str, body: dict = None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional. Async version.

        Parameters
        ----------
        upstream_digital_prod_guid: str
            The guid of the first digital product
        downstream_digital_prod_guid: str
            The guid of the downstream digital product
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Linked {upstream_digital_prod_guid} -> {downstream_digital_prod_guid}")


    def link_digital_product_dependency(self, upstream_digital_prod_guid: str, downstream_digital_prod_guid: str,
                                        body: dict = None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional.

            Parameters
            ----------
            upstream_digital_prod_guid: str
                The guid of the first digital product
            downstream_digital_prod_guid: str
                The guid of the downstream digital product
            body: dict, optional, default = None
                A dict representing the details of the relationship.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
            {
              "class" : "RelationshipRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "properties": {
                "class": "InformationSupplyChainLinkProperties",
                "label": "add label here",
                "description": "add description here",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_digital_product_dependency(upstream_digital_prod_guid, downstream_digital_prod_guid,
                                                        body))


    @dynamic_catch
    async def _async_detach_digital_product_dependency(self, upstream_digital_prod_guid: str,
                                                       downstream_digital_prod_guid: str, body: dict = None):
        """ Unlink two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional. Async version.

        Parameters
        ----------
        upstream_digital_prod_guid: str
            The guid of the first digital product
        downstream_digital_prod_guid: str
            The guid of the downstream digital product
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/detach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached digital product dependency {upstream_digital_prod_guid}, {downstream_digital_prod_guid}")


    @dynamic_catch
    async def _async_link_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str,
                                          body: dict = None) -> None:
        """ Attach a product manager to a digital product. Request body is optional.
            Request body is optional. Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product
        digital_prod_manager_guid: str
            The guid of the digital_product_manager
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{digital_prod_guid}/product-managers/{digital_prod_manager_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Attached digital product manager {digital_prod_manager_guid} to {digital_prod_guid}")


    def link_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str, body: dict = None):
        """ Link a product manager to a digital product.
            Request body is optional.

            Parameters
            ----------
            digital_prod_guid: str
                The guid of the digital product
            digital_prod_manager_guid: str
                The guid of the product manager
            body: dict, optional, default = None
                A dict representing the details of the relationship.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
            {
              "class": "RelationshipRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_product_manager(digital_prod_guid, digital_prod_manager_guid, body))


    @dynamic_catch
    async def _async_detach_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str,
                                            body: dict = None):
        """ Detach a product manager from a digital product. Request body is optional.
            Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product
        digital_prod_manager_guid: str
            The guid of the product manager
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{digital_prod_guid}/product-managers/{digital_prod_manager_guid}/detach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f'Detached product manager {digital_prod_manager_guid} from {digital_prod_guid}')


    def detach_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str, body: dict = None):
        """ Detach a product manager from a digital product. Request body is optional.

            Parameters
            ----------
            digital_prod_guid: str
                The guid of the digital product
            digital_prod_manager_guid: str
                The guid of the product manager
            body: dict, optional, default = None
                A dict representing the details of the relationship.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
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
            self._async_detach_product_manager(digital_prod_guid, digital_prod_manager_guid, body))

        #
        # Agreements
        #


    @dynamic_catch
    async def _async_create_agreement(self, body: dict) -> str:
        """Create a new collection that represents am agreement. Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        With a lifecycle, the body is:
        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "NEW",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "initialStatus" : "OTHER",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, ACTIVE, DISABLED,
        DEPRECATED,
        OTHER.  If using OTHER, set the userDefinedStatus with the status value you want.
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    def create_agreement(self, body: dict) -> str:
        """Create a new collection that represents am agreement. Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        With a lifecycle, the body is:
        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "NEW",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "initialStatus" : "OTHER",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, ACTIVE, DISABLED,
        DEPRECATED,
        OTHER.  If using OTHER, set the userDefinedStatus with the status value you want.
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_agreement(body))
        return resp


    @dynamic_catch
    async def _async_create_data_sharing_agreement(self, body: dict) -> str:
        """ Create a new collection with the DataSharingAgreement classification.  The collection is typically
            an agreement which may use the NewElementRequestBody, or the NewAgreementRequestBody if the
            initial status needs to be set. Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "NEW",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "initialStatus" : "OTHER",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/data"
            f"-sharing-agreement")

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    def create_data_sharing_agreement(self, body: dict) -> str:
        """ Create a new collection with the DataSharingAgreement classification.  The collection is typically
            an agreement which may use the NewElementRequestBody, or the NewAgreementRequestBody if the
            initial status needs to be set.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "NEW",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "initialStatus" : "OTHER",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_data_sharing_agreement(body))
        return resp


    @dynamic_catch
    async def _async_update_agreement(self, agreement_guid: str, body: dict, replace_all_props: bool = False, ):
        """Update the properties of the agreement collection. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"{agreement_guid}/update?replaceAllProperties={replace_all_props_s}")

        await self._async_make_request("POST", url, body)
        logger.info(f"Updated properties for agreement {agreement_guid}")


    def update_agreement(self, agreement_guid: str, body: dict, replace_all_props: bool = False, ):
        """Update the properties of the DigitalProduct classification attached to a collection.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
         {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_product(agreement_guid, body, replace_all_props))


    @dynamic_catch
    async def _async_update_agreement_status(self, agreement_guid: str, body: dict):
        """Update the status of an agreement collection. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the digital product collection to update.
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
           {
              "class": "AgreementStatusRequestBody",
              "status": "APPROVED",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{agreement_guid}/update-status")

        await self._async_make_request("POST", url, body)
        logger.info(f"Updated status for agreement {agreement_guid}")


    def update_agreement_status(self, agreement_guid: str, body: dict):
        """Update the status of an agreement collection. Async version.

            Parameters
            ----------
            agreement_guid: str
                The guid of the digital product collection to update.
            body: dict
                A dict representing the details of the collection to create.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
               {
                  "class": "AgreementStatusRequestBody",
                  "status": "APPROVED",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_agreement_status(agreement_guid, body))


    @dynamic_catch
    async def _async_link_agreement_actor(self, agreement_guid: str, actor_guid: str, body: dict = None):
        """ Attach an actor to an agreement.  The actor element may be an actor profile (person, team or IT
        profile);
            actor role (person role, team role or IT profile role); or user identity. Request body is optional.
            Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement.
        actor_guid: str
            The guid of the actor assigned.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
           "properties": {
            "class": "AgreementActorProperties",
            "actorName": "add name of actor used in agreement text",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{agreement_guid}/agreement-actors/{actor_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Attached actor {actor_guid} to agreement {agreement_guid}")


    def link_agreement_actor(self, agreement_guid: str, actor_guid: str, body: dict = None):
        """ Attach an actor to an agreement.  The actor element may be an actor profile (person, team or IT
        profile);
            actor role (person role, team role or IT profile role); or user identity. Request body is optional.


        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement.
        actor_guid: str
            The guid of the actor assigned.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
           "properties": {
            "class": "AgreementActorProperties",
            "actorName": "add name of actor used in agreement text",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_agreement_actor(agreement_guid, actor_guid, body))


    @dynamic_catch
    async def _async_detach_agreement_actor(self, agreement_guid: str, actor_guid: str, body: dict = None):
        """ Unlink an actor from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the first digital product
        actor_guid: str
            The guid of the downstream digital product
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{agreement_guid}/agreement-actors/{actor_guid}/detach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached agreement actor {actor_guid} from {agreement_guid}")


    def detach_agreement_actor(self, agreement_guid: str, actor_guid: str, body: dict = None):
        """ Unlink an actor from an agreement. Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the first digital product
        actor_guid: str
            The guid of the downstream digital product
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_agreement_actor(agreement_guid, actor_guid, body))


    @dynamic_catch
    async def _async_link_agreement_item(self, agreement_guid: str, agreement_item_guid: str,
                                         body: dict = None) -> None:
        """ Attach an agreement to an element referenced in its definition. The agreement item element is of type
           'Referenceable' to allow the agreement to refer to many things. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____

        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "AgreementItemProperties",
            "agreementItemId": "add label here",
            "agreementStart": "{{$isoTimestamp}}",
            "agreementEnd": "{{$isoTimestamp}}",
            "restrictions": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "obligations" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "usageMeasurements" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"agreements/{agreement_guid}/agreement-items/{agreement_item_guid}/attach")

        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Attached agreement item {agreement_item_guid} to {agreement_guid}")


    def link_agreement_item(self, agreement_guid: str, agreement_item_guid: str, body: dict = None) -> None:
        """ Attach an agreement to an element referenced in its definition. The agreement item element is of type
                  'Referenceable' to allow the agreement to refer to many things. Request body is optional.

               Parameters
               ----------
               agreement_guid: str
                   The guid of the agreement to update.
               agreement_item_guid: str
                   The guid of the element to attach.
               body: dict, optional, default = None
                   A dict representing the details of the relationship.

               Returns
               -------
               Nothing

               Raises
               ------
               InvalidParameterException
                 If the client passes incorrect parameters on the request - such as bad URLs or invalid values
               PropertyServerException
                 Raised by the server when an issue arises in processing a valid request
               NotAuthorizedException
                 The principle specified by the user_id does not have authorization for the requested action

               Notes
               _____

               {
                 "class" : "RelationshipRequestBody",
                 "externalSourceGUID": "add guid here",
                 "externalSourceName": "add qualified name here",
                 "effectiveTime" : "{{$isoTimestamp}}",
                 "forLineage" : false,
                 "forDuplicateProcessing" : false,
                 "properties": {
                   "class": "AgreementItemProperties",
                   "agreementItemId": "add label here",
                   "agreementStart": "{{$isoTimestamp}}",
                   "agreementEnd": "{{$isoTimestamp}}",
                   "restrictions": {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "obligations" : {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "usageMeasurements" : {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "effectiveFrom": "{{$isoTimestamp}}",
                   "effectiveTo": "{{$isoTimestamp}}"
                 }
               }

               """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_agreement_item(agreement_guid, agreement_item_guid, body))


    @dynamic_catch
    async def _async_detach_agreement_item(self, agreement_guid: str, agreement_item_guid: str,
                                           body: dict = None) -> None:
        """Detach an agreement item from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements"
            f"{agreement_guid}/agreement-items/{agreement_item_guid}/detach")

        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached agreement item {agreement_item_guid} from {agreement_guid}")


    def detach_agreement_item(self, agreement_guid: str, agreement_item_guid: str, body: dict = None) -> None:
        """Detach an agreement item from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_agreement_item(agreement_guid, agreement_item_guid, body))


    @dynamic_catch
    async def _async_link_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """ Attach an agreement to an external reference element that describes the location of the contract
        documents.
            Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        external_ref_guid: str
            The guid of the external reference to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____

        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ContractLinkProperties",
            "contractId": "add id here",
            "contractLiaison": "add identifier of actor here",
            "contractLiaisonTypeName": "add type of actor here",
            "contractLiaisonPropertyName": "add property of actor's identifier here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"agreements/{agreement_guid}/contract-links/{external_ref_guid}/attach")

        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Attached agreemenbt {agreement_guid} to contract {external_ref_guid}")


    def link_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """ Attach an agreement to an external reference element that describes the location of the contract
        documents.
            Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        external_ref_guid: str
            The guid of the external reference to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____

        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ContractLinkProperties",
            "contractId": "add id here",
            "contractLiaison": "add identifier of actor here",
            "contractLiaisonTypeName": "add type of actor here",
            "contractLiaisonPropertyName": "add property of actor's identifier here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_contract(agreement_guid, external_ref_guid, body))


    @dynamic_catch
    async def _async_detach_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """Detach an external reference to a contract, from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        external_ref_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements"
            f"{agreement_guid}/contract-links/{external_ref_guid}/detach")

        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached contract: {external_ref_guid} from {agreement_guid}")


    def detach_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """Detach an external reference to a contract, from an agreement. Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        external_ref_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_contract(agreement_guid, external_ref_guid, body))

        #
        # Digital Subscriptions
        #


    @dynamic_catch
    async def _async_create_digital_subscription(self, body: dict) -> str:
        """Create a new collection that represents a type of agreement called a digital_subscription. Async version.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }

        With a lifecycle, the body is:

        The DigitalSubscription is a type of Agreement and so can have lifecycle states.
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must be valid dates if specified,
        otherwise you will get a 400 error response.
        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED
        ACTIVE, DEPRECATED, OTHER.  If using OTHER, set the userDefinedStatus with the statu value you want.

        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "initialStatus" : "OTHER",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"

        resp = await self._async_make_request("POST", url, body_slimmer(body))
        guid = resp.json().get('guid', NO_GUID_RETURNED)
        logger.info(f"Create collection with GUID: {guid}")
        return guid


    def create_digital_subscription(self, body: dict) -> str:
        """Create a new collection that represents a type of agreement called a digital_subscription.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        str - the guid of the created collection

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        With a lifecycle, the body is:

        The DigitalSubscription is a type of Agreement and so can have lifecycle states.
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must be valid dates if specified,
        otherwise you will get a 400 error response.
        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED
        ACTIVE, DEPRECATED, OTHER.  If using OTHER, set the userDefinedStatus with the statu value you want.

        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "initialStatus" : "OTHER",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_digital_subscription(body))
        return resp


    @dynamic_catch
    async def _async_update_digital_subscription(self, digital_subscription_guid: str, body: dict,
                                                 replace_all_props: bool = False, ):
        """Update the properties of the digital_subscription collection. Async version.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital_subscription to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"{digital_subscription_guid}/update?replaceAllProperties={replace_all_props_s}")

        await self._async_make_request("POST", url, body)
        logger.info(f"Updated digital subscription {digital_subscription_guid}")


    def update_digital_subscription(self, digital_subscription_guid: str, body: dict,
                                    replace_all_props: bool = False, ):
        """Update the properties of the DigitalProduct classification attached to a collection.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital_subscription to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
         {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add digital_subscription name here",
            "name" : "display name",
            "description" : "Add description of the digital_subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add digital_subscription identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_digital_subscription(digital_subscription_guid, body, replace_all_props))


    @dynamic_catch
    async def _async_update_digital_subscription_status(self, digital_subscription_guid: str, body: dict):
        """Update the status of an digital_subscription collection. Async version.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital product collection to update.
        body: dict
            A dict representing the details of the collection to create.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
           {
              "class": "AgreementStatusRequestBody",
              "status": "APPROVED",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{digital_subscription_guid}/update-status")

        await self._async_make_request("POST", url, body)
        logger.info(f"Updated status for DigitalProduct {digital_subscription_guid}")


    def update_digital_subscription_status(self, digital_subscription_guid: str, body: dict):
        """Update the status of an digital_subscription collection. Async version.

            Parameters
            ----------
            digital_subscription_guid: str
                The guid of the digital product collection to update.
            body: dict
                A dict representing the details of the collection to create.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
               {
                  "class": "AgreementStatusRequestBody",
                  "status": "APPROVED",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_subscription_status(digital_subscription_guid, body))


    @dynamic_catch
    async def _async_link_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict = None):
        """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
            products, team or business capabilities to be the subscriber. The subscription is an element of type
            DigitalSubscription.
            Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "DigitalSubscriberProperties",
            "subscriberId": "add id here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/subscribers/"
            f"{subscriber_guid}/subscriptions/{subscription_guid}/attach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Linking subscriber {subscriber_guid} to subscription {subscription_guid}")


    def link_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict = None):
        """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
            products, team or business capabilities to be the subscriber. The subscription is an element of type
            DigitalSubscription.
            Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "DigitalSubscriberProperties",
            "subscriberId": "add id here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_subscriber(subscriber_guid, subscription_guid, body))


    @dynamic_catch
    async def _async_detach_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict = None):
        """ Detach a subscriber from a subscription Request body is optional. Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The unique identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{subscriber_guid}/agreement-actors/{subscription_guid}/detach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached subscriber {subscriber_guid} from subscription {subscription_guid}")


    def detach_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict = None):
        """ Detach a subscriber from a subscription. Request body is optional.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The unique identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_subscriber(subscriber_guid, subscription_guid, body))

        #
        #
        #


    @dynamic_catch
    async def _async_attach_collection(self, parent_guid: str, collection_guid: str, body: dict = None,
                                       make_anchor: bool = False):
        """ Connect an existing collection to an element using the ResourceList relationship (0019).
            Async version.

        Parameters
        ----------
        parent_guid: str
            The unique identifier of the parent to attach to.
        collection_guid: str
            The identifier of the collection being attached.
        body: dict, optional, default = None
            A dict representing the details of the relationship.
        make_anchor: bool, optional, default = False
            Indicates if the collection should be anchored to the element.

        Returns
        -------
        Nothing

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
        JSON Structure looks like:

        {
          "class" : "RelationshipRequestBody",
          "properties": {
            "class": "ResourceListProperties",
            "resourceUse": "Add valid value here",
            "resourceUseDescription": "Add description here",
            "watchResource": false,
            "resourceUseProperties": {
              "property1Name": "property1Value",
              "property2Name": "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/metadata-elements/"
            f"{parent_guid}/collections/{collection_guid}/attach?makeAchor={make_anchor}")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Attached {collection_guid} to {parent_guid}")


    def attach_collection(self, parent_guid: str, collection_guid: str, body: dict = None,
                          make_anchor: bool = False):
        """ Connect an existing collection to an element using the ResourceList relationship (0019).

            Parameters
            ----------
            parent_guid: str
                The unique identifier of the parent to attach to.
            collection_guid: str
                The identifier of the collection being attached.
            body: dict, optional, default = None
                A dict representing the details of the relationship.
            make_anchor: bool, optional, default = False
                Indicates if the collection should be anchored to the element.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:

            {
              "class" : "RelationshipRequestBody",
              "properties": {
                "class": "ResourceListProperties",
                "resourceUse": "Add valid value here",
                "resourceUseDescription": "Add description here",
                "watchResource": false,
                "resourceUseProperties": {
                  "property1Name": "property1Value",
                  "property2Name": "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_attach_collection(parent_guid, collection_guid, body, make_anchor))


    @dynamic_catch
    async def _async_detach_collection(self, parent_guid: str, collection_guid: str, body: dict = None):
        """ Detach an existing collection from an element. If the collection is anchored to the element,
        it is delete.
            Async version.

        Parameters
        ----------
        parent_guid: str
                The unique identifier of the parent to detach from.
        collection_guid: str
                The identifier of the collection being detached.
        body: dict, optional, default = None
            A dict representing the details of the relationship.


        Returns
        -------
        Nothing

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
        JSON Structure looks like:
        {
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/metadata-elements/"
            f"{parent_guid}/collections/{collection_guid}/detach")
        if body:
            await self._async_make_request("POST", url, body)
        else:
            await self._async_make_request("POST", url)
        logger.info(f"Detached collection {collection_guid} from {parent_guid}")


    def detach_collection(self, parent_guid: str, collection_guid: str, body: dict = None):
        """ Detach an existing collection from an element. If the collection is anchored to the element,
        it is delete.

          Parameters
          ----------
          parent_guid: str
                  The unique identifier of the parent to detach from.
          collection_guid: str
                 The identifier of the collection being detached.
          body: dict, optional, default = None
              A dict representing the details of the relationship.

          Returns
          -------
          Nothing

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
          JSON Structure looks like:
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
        loop.run_until_complete(self._async_detach_collection(parent_guid, collection_guid, body))


    @dynamic_catch
    async def _async_delete_collection(self, collection_guid: str, body: dict = None,
                                       cascade: bool = False) -> None:
        """Delete a collection.  It is detected from all parent elements.  If members are anchored to the collection
        then they are also deleted. Async version


        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


        """
        cascade_s = str(cascade).lower()
        url = f"{self.collection_command_root}/{collection_guid}/delete?cascadedDelete={cascade_s}"
        if body is None:
            body = {"class": "NullRequestBody"}

        await self._async_make_request("POST", url, body)
        logger.info(f"Deleted collection {collection_guid} with cascade {cascade}")


    def delete_collection(self, collection_guid: str, body: dict = None, cascade: bool = False) -> None:
        """Delete a collection.  It is detected from all parent elements.  If members are anchored to the collection
        then they are also deleted.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict, optional, default = None
            A dict representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        _____
        JSON Structure looks like:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_collection(collection_guid, body, cascade))


    @dynamic_catch
    async def _async_add_to_collection(self, collection_guid: str, element_guid: str, body: dict = None, ) -> None:
        """Add an element to a collection.  The request body is optional. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

            The name of the server to use.


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

        Notes
        -----
        Example body:
        { "class": "RelationshipRequestBody",
           "properties" : {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
              },
              },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/attach")
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        logger.info(f"Added {element_guid} to {collection_guid}")


    def add_to_collection(self, collection_guid: str, element_guid: str, body: dict = None, ) -> None:
        """Add an element to a collection.  The request body is optional.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

            The name of the server to use.


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

        Notes
        -----
        Example body:
         { "class": "RelationshipRequestBody",
           "properties" : {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
              },
              },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_to_collection(collection_guid, element_guid, body))


    @dynamic_catch
    async def _async_update_collection_membership(self, collection_guid: str, element_guid: str, body: dict = None,
                                                  replace_all_props: bool = False, ) -> None:
        """Update an element's membership to a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.
        replace_all_props: bool, optional, defaults to False
            Replace all properties or just update ones specified in body.

            The name of the server to use.


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

        Notes
        -----
        Example body:
        {
          "class" : "RelationshipRequestBody",
          "properties" : {
            "class": "CollectionMembershipProperties",
            "membershipRationale": "xxx",
            "createdBy": "user id here",
            "expression": "expression that described why the element is a part of this collection",
            "confidence": 100,
            "membershipStatus": "PROPOSED",
            "userDefinedStatus": "Add valid value here",
            "steward": "identifier of steward that validated this member",
            "stewardTypeName": "type name of element identifying the steward",
            "stewardPropertyName": "property name if the steward's identifier",
            "source": "source of the member",
            "notes": "Add notes here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/update?replaceAllProperties={replace_all_props_s}")
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        logger.info(f"Updated membership for collection {collection_guid}")


    def update_collection_membership(self, collection_guid: str, element_guid: str, body: dict = None,
                                     replace_all_props: bool = False, ) -> None:
        """Update an element's membership to a collection.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.
        replace_all_props: bool, optional, defaults to False
            Replace all properties or just update ones specified in body.

            The name of the server to use.


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

        Notes
        -----
        Example body:
        {
          "class" : "RelationshipRequestBody",
          "properties" : {
            "class": "CollectionMembershipProperties",
            "membershipRationale": "xxx",
            "createdBy": "user id here",
            "expression": "expression that described why the element is a part of this collection",
            "confidence": 100,
            "membershipStatus": "PROPOSED",
            "userDefinedStatus": "Add valid value here",
            "steward": "identifier of steward that validated this member",
            "stewardTypeName": "type name of element identifying the steward",
            "stewardPropertyName": "property name if the steward's identifier",
            "source": "source of the member",
            "notes": "Add notes here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_collection_membership(collection_guid, element_guid, body, replace_all_props))


    @dynamic_catch
    async def _async_remove_from_collection(self, collection_guid: str, element_guid: str,
                                            body: dict = None) -> None:
        """Remove an element from a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

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

        Notes
        -----
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/detach")
        if body is None:
            body = {"class": "NullRequestBody"}
        await self._async_make_request("POST", url, body)
        logger.info(f"Removed member {element_guid} from collection {collection_guid}")


    def remove_from_collection(self, collection_guid: str, element_guid: str, body: dict = None) -> None:
        """Remove an element from a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

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

        Notes
        -----
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_from_collection(collection_guid, element_guid, body))

        #
        #
        #


    @dynamic_catch
    async def _async_get_member_list(self, collection_guid: str = None, collection_name: str = None,
                                     collection_qname: str = None, ) -> list | str:
        """Get the member list for the collection - async version.
        Parameters
        ----------
        collection_guid: str,
           identity of the collection to return members for. If none, collection_name or
           collection_qname are used.
        collection_name: str,
           display name of the collection to return members for. If none, collection_guid
           or collection_qname are used.
        collection_qname: str,
           qualified name of the collection to return members for. If none, collection_guid
           or collection_name are used.

        Returns
        -------
        list | str
            The list of member information if successful, otherwise the string "No members found"

        Raises
        ------
        InvalidParameterException
            If the root_collection_name does not have exactly one root collection.

        """

        # first find the guid for the collection we are using as root

        # now find the members of the collection
        member_list = []
        members = await self._async_get_collection_members(collection_guid, collection_name, collection_qname)
        if (type(members) is str) or (len(members) == 0):
            logger.trace(f"No members found for collection {collection_guid}")
            return "No members found"
        # finally, construct a list of  member information
        for member_rel in members:
            member_guid = member_rel["elementHeader"]["guid"]
            member = await self._async_get_element_by_guid_(member_guid)
            if isinstance(member, dict):
                member_instance = {
                    "name": member["properties"].get('displayName', ''),
                    "qualifiedName": member["properties"]["qualifiedName"], "guid": member["elementHeader"]["guid"],
                    "description": member["properties"].get("description", ''),
                    "type": member["elementHeader"]["type"]['typeName'],
                    }
                member_list.append(member_instance)
        logger.debug(f"Member list for collection {collection_guid}: {member_list}")
        return member_list if len(member_list) > 0 else "No members found"


    def get_member_list(self, collection_guid: str = None, collection_name: str = None,
                        collection_qname: str = None, ) -> list | bool:
        """Get the member list for a collection - async version.
        Parameters
        ----------
        collection_guid: str,
           identity of the collection to return members for. If none, collection_name or
           collection_qname are used.
        collection_name: str,
           display name of the collection to return members for. If none, collection_guid
           or collection_qname are used.
        collection_qname: str,
           qualified name of the collection to return members for. If none, collection_guid
           or collection_name are used.
        Returns
        -------
        list | bool
            The list of member information if successful, otherwise False.

        Raises
        ------
        InvalidParameterException
            If the root_collection_name does not have exactly one root collection.

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_member_list(collection_guid, collection_name, collection_qname))
        return resp


    def _extract_collection_properties(self, element: dict) -> dict:
        """
        Extract common properties from a collection element.

        Args:
            element (dict): The collection element

        Returns:
            dict: Dictionary of extracted properties
        """

        props = _extract_referenceable_properties(element)
        classification_names = ""
        # classifications = element['elementHeader'].get("classifications", [])
        for classification in props['classifications']:
            classification_names += f"{classification['classificationName']}, "
        props["classifications"] = classification_names[:-2]  # why?

        props['mermaid'] = element.get('mermaidGraph', "") or ""

        member_names = ""
        members = self.get_member_list(collection_guid=props["GUID"])
        if isinstance(members, list):
            for member in members:
                member_names += f"{member['qualifiedName']}, "
            props['members'] = member_names[:-2]
        logger.trace(f"Extracted properties: {props}")
        return props


    def _generate_collection_output(self, elements: dict|list[dict], filter: Optional[str],
                                    classification_name: Optional[str], output_format: str = "DICT",
                                    output_format_set: dict | str = None) -> str| list[dict]:
        """ Generate output for collections in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                classification_name (Optional[str]): The type of collection
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                output_format_set (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if classification_name is None:
            entity_type = "Collections"
        else:
            entity_type = classification_name
        # First see if the user has specified an output_format_set - either a label or a dict
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            if isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        # If no output_format was set, then use the classification_name to lookup the output format
        elif classification_name:
            output_formats = select_output_format_set(classification_name, output_format)
        else:
            # fallback to collections or entity type
            output_formats = select_output_format_set(entity_type,output_format)

        logger.trace(f"Executing generate_collection_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_collection_properties,
            None,
            output_formats,
            )


from typing import Union, Dict, List, Optional

if __name__ == "__main__":
    print("Main-Collection Manager")

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the metadata-explorer OMVS module.

[metadata-explorer](https://egeria-project.org/services/omvs/metadata-explorer/overview/)

"""

import asyncio

from httpx import Response

from pyegeria import body_slimmer


from pyegeria._client import Client, max_paging_size
from pyegeria._globals import default_time_out

NO_ELEMENTS_FOUND = "No_elements_found"


def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


"params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to the query string"


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/metadata-explorer"


def process_related_element_list(
    response: Response, mermaid_only: bool, relationship_list: bool = False
) -> str | dict:
    """Process the result payload

    Parameters
    ----------
    response: Response
        - the response payload from the API call
    mermaid_only: bool
        - if true, only return the Mermaid graph
    relationship_list: bool
        - if True, look for "relationshipList" otherwise look for "relatedElementList"

    Returns
    -------

    """
    if relationship_list:
        elements = response.json().get("relationshipList", "No relationship list found")
    else:
        elements = response.json().get("relatedElementList", NO_ELEMENTS_FOUND)

    if isinstance(elements, str):
        return NO_ELEMENTS_FOUND
    if mermaid_only:
        return elements.get("mermaidGraph", "No mermaid graph found")

    el_list = elements.get("elementList", NO_ELEMENTS_FOUND)
    if isinstance(el_list, str):
        return el_list

    if len(el_list) == 0:
        return "No elements returned"
    return elements


class MetadataExplorer(Client):
    """MetadataExplorer is a class that extends the Client class. The Metadata Explorer OMVS provides APIs for
      supporting the search, query and retrieval of open metadata. It is an advanced API for users that understands
      the Open Metadata Types.

    Attributes:

        view_server_name: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a
            default optionally used by the methods when the user
            doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None


    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.metadata_explorer_command_root: str = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/metadata-explorer"
        Client.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )

    #
    #   Get
    #

    async def _async_get_metadata_guid_by_unique_name(
        self,
        name: str,
        property_name: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> str:
        """
        Retrieve the metadata element GUID using its unique name (typically the qualified name, but it is possible to
        specify a different property name in the request body as long as it is unique).
        If multiple matching instances are found, an exception is thrown. Async version.

        Parameters
        ----------
        name : str
            - unique name to search for
        property_name: str
            - property name to search in (typically the qualified name)
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "NameRequestBody",
            "name": name,
            "namePropertyName": property_name,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/guid-by-unique-name"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def get_metadata_guid_by_unique_name(
        self,
        name: str,
        property_name: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> str:
        """
        Retrieve the metadata element GUID using its unique name (typically the qualified name, but it is possible to
        specify a different property name in the request body as long as it is unique).
        If multiple matching instances are found, an exception is thrown.

        Parameters
        ----------
        name : str
            - unique name to search for
        property_name: str
            - property name to search in (typically the qualified name)
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        str
            The GUID of the element - or "No element found"

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_guid_by_unique_name(
                name,
                property_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
            )
        )
        return response

    async def _async_get_metadata_element_by_guid(
        self,
        guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> dict | str:
        """
        Retrieve the metadata element using its unique identifier. Async version.

        Parameters
        ----------
        guid : str
            - unique identifier of the element to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
            - Query the element as of this time. If None, then use current time.
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
            If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "AnyTimeRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_metadata_element_by_guid(
        self,
        guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> dict | str:
        """
        Retrieve the metadata element using its unique identifier.

        Parameters
        ----------
        guid : str
            - unique identifier of the element to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
            - Query the element as of this time. If None, then use current time.
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
            If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_by_guid(
                guid, effective_time, for_lineage, for_duplicate_processing
            )
        )
        return response

    async def _async_get_anchored_metadata_element_graph(
        self,
        guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        mermaid_only: bool = False,
    ) -> dict | str:
        """
        Retrieve the metadata element and all of its anchored elements using its unique identifier. Async version.

        Parameters
        ----------
        guid : str
            - unique identifier of the element to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
            - Query the element as of this time. If None, then use current time.
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        dict | str
            If the element is found, and mermaid_only is False, a dict of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "AnyTimeRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}/with-anchored-elements"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        # if mermaid_only:
        #     return response.json()["elementGraph"].get(
        #         "mermaidGraph", NO_ELEMENTS_FOUND
        #     )
        # else:
        #     return response.json().get("elementGraph", NO_ELEMENTS_FOUND)
        if isinstance(response, str):
            return NO_ELEMENTS_FOUND
        el_list = response.json().get("elementGraph", NO_ELEMENTS_FOUND)
        if isinstance(el_list, str):
            return el_list
        if mermaid_only:
            return el_list.get("mermaidGraph", "No mermaid graph found")
        if len(el_list) == 0:
            return "No elements returned"
        return el_list

    def get_anchored_metadata_element_graph(
        self,
        guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        mermaid_only: bool = False,
    ) -> dict | str:
        """
        Retrieve the metadata element and all of its anchored elements using its unique identifier. Async version.

        Parameters
        ----------
        guid : str
            - unique identifier of the element to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
            - Query the element as of this time. If None, then use current time.
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        dict | str
            If the element is found, and mermaid_only is False, a dict of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_anchored_metadata_element_graph(
                guid,
                effective_time,
                as_of_time,
                for_lineage,
                for_duplicate_processing,
                mermaid_only,
            )
        )
        return response

    # def get_metadata_element_mermaid_graph(
    #     self,
    #     guid: str,
    #     effective_time: str = None,
    #     as_of_time: str = None,
    #     for_lineage: bool = None,
    #     for_duplicate_processing: bool = None,
    # ) -> dict | str:
    #     """
    #     Retrieve the metadata element using its unique identifier.
    #
    #     Parameters
    #     ----------
    #     guid : str
    #         - unique identifier of the element to retrieve
    #     effective_time: str, default = None
    #         - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
    #     as_of_time: str, default = None
    #         - Query the element as of this time. If None, then use current time.
    #     for_lineage: bool, default is set by server
    #         - determines if elements classified as Memento should be returned - normally false
    #     for_duplicate_processing: bool, default is set by server
    #         - Normally false. Set true when the caller is part of a deduplication function
    #
    #     Returns
    #     -------
    #     dict | str
    #         If the element is found, a dict of the element details is returned. Otherwise the string "No element found".
    #
    #     Raises
    #     ------
    #     InvalidParameterException
    #         one of the parameters is null or invalid or
    #     PropertyServerException
    #         There is a problem adding the element properties to the metadata repository or
    #     UserNotAuthorizedException
    #         the requesting user is not authorized to issue this request.
    #     """
    #
    #     response = self.get_metadata_element_graph(
    #         guid, effective_time, as_of_time, for_lineage, for_duplicate_processing
    #     )
    #     return response.get("mermaidGraph", NO_ELEMENTS_FOUND)

    async def _async_get_metadata_element_by_unique_name(
        self,
        name: str,
        property_name: str = "qualifiedName",
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> dict | str:
        """
        Retrieve the metadata element using its unique name (typically the *qualifiedName* attribute but other attributes
        can be used if they are unique - such as *pathName* for a file). Async version.

        Parameters
        ----------
        name : str
            - unique name to search for
        property_name: str, default = "qualifiedName"
            - property name to search in (typically the qualified name)
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
                If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "NameRequestBody",
            "name": name,
            "namePropertyName": property_name,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-unique-name"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_metadata_element_by_unique_name(
        self,
        name: str,
        property_name: str = "qualifiedName",
        effective_time: str = None,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> str:
        """
        Retrieve the metadata element using its unique name (typically the *qualifiedName* attribute but other attributes
        can be used if they are unique - such as *pathName* for a file).

        Parameters
        ----------
        name : str
            - unique name to search for
        property_name: str, default = "qualifiedName"
            - property name to search in (typically the qualified name)
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
                If the element is found, a dict of the element details is returned. Otherwise the string "No element found".


        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_by_unique_name(
                name,
                property_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
            )
        )
        return response

    async def _async_get_metadata_element_history(
        self,
        guid: str,
        effective_time: str = None,
        oldest_first: bool = False,
        from_time: str = None,
        to_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve all the versions of a metadata element. Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("oldestFirst", oldest_first),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}/history"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elementList", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def get_metadata_element_history(
        self,
        guid: str,
        effective_time: str = None,
        oldest_first: bool = False,
        from_time: str = None,
        to_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve all the versions of a metadata element.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_history(
                guid,
                effective_time,
                oldest_first,
                from_time,
                to_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_find_metadata_elements_with_string(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Return a list of metadata elements that match the supplied criteria. The results can be returned over many pages.
        Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "SearchStringRequestBody",
                  "searchString" : "Egeria",
                  "typeName" : "ValidValueDefinition",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }

        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-string"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elementList", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def find_metadata_elements_with_string(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Return a list of metadata elements that match the supplied criteria. The results can be returned over many pages.
        Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "SearchStringRequestBody",
                  "searchString" : "Egeria",
                  "typeName" : "ValidValueDefinition",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_metadata_elements_with_string(
                body,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_all_related_metadata_elements(
        self,
        guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the metadata elements connected to the supplied element.
        Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned


        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".
        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """

        possible_query_params = query_string(
            [
                ("startingAtEnd", starting_at_end),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/related-elements/{guid}/any-type"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        return process_related_element_list(response, mermaid_only)

    def get_all_related_metadata_elements(
        self,
        guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the metadata elements connected to the supplied element.

        Parameters
        ----------
        guid: str
            - unique identity of element
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned


        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_all_related_metadata_elements(
                guid,
                body,
                for_lineage,
                for_duplicate_processing,
                starting_at_end,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_get_related_metadata_elements(
        self,
        guid: str,
        relationship_type: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the metadata elements connected to the supplied element.
        Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        relationship_type: str
            - name of relationship type to retrieve relationships of
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """

        possible_query_params = query_string(
            [
                ("startingAtEnd", starting_at_end),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/related-elements/{guid}/type/{relationship_type}"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return process_related_element_list(response, mermaid_only)

    def get_related_metadata_elements(
        self,
        guid: str,
        relationship_type: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the metadata elements connected to the supplied element.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        relationship_type: str
            - name of relationship type to retrieve relationships of
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_metadata_elements(
                guid,
                relationship_type,
                body,
                for_lineage,
                for_duplicate_processing,
                starting_at_end,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_get_all_metadata_element_relationships(
        self,
        end1_guid: str,
        end2_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the relationships linking the supplied elements.
        Async version.

        Parameters
        ----------
        end1_guid: str
            - Unique identity of the metadata element at end1 of a relationship.
        end2_guid: str
            - Unique identity of the metadata element at end2 of a relationship.
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned


        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """

        possible_query_params = query_string(
            [
                ("startingAtEnd", starting_at_end),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{end1_guid}/linked-by-any-type/"
            f"to-elements/{end2_guid}"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return process_related_element_list(response, mermaid_only)

    def get_all_metadata_element_relationships(
        self,
        end1_guid: str,
        end2_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the relationships linking the supplied elements.

        Parameters
        ----------
        end1_guid: str
            - Unique identity of the metadata element at end1 of a relationship.
        end2_guid: str
            - Unique identity of the metadata element at end2 of a relationship.
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_all_metadata_element_relationships(
                end1_guid,
                end2_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                starting_at_end,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_get_metadata_element_relationships(
        self,
        end1_guid: str,
        end2_guid: str,
        relationship_type: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the relationships linking the supplied elements.
        Async version.

        Parameters
        ----------
        end1_guid: str
            - Unique identity of the metadata element at end1 of a relationship.
        end2_guid: str
            - Unique identity of the metadata element at end2 of a relationship.
        relationship_type: str
            - name of relationship type to retrieve relationships of
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """

        possible_query_params = query_string(
            [
                ("startingAtEnd", starting_at_end),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{end1_guid}/linked-by-type/"
            f"{relationship_type}/to-elements/{end2_guid}"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return process_related_element_list(response, mermaid_only)

    def get_metadata_element_relationships(
        self,
        end1_guid: str,
        end2_guid: str,
        relationship_type: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        starting_at_end: int = 0,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve the relationships linking the supplied elements.

        Parameters
        ----------
        end1_guid: str
            - Unique identity of the metadata element at end1 of a relationship.
        end2_guid: str
            - Unique identity of the metadata element at end2 of a relationship.
        relationship_type: str
            - name of relationship type to retrieve relationships of
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        starting_at_end: int, default = 0
            - Relationship end to start from.
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned


        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "ResultsRequestBody",
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "PROPERTY_ASCENDING",
                  "sequencingProperty": "fileName"
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_relationships(
                end1_guid,
                end2_guid,
                relationship_type,
                body,
                for_lineage,
                for_duplicate_processing,
                starting_at_end,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_find_metadata_elements(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """Return a list of metadata elements that match the supplied criteria.
        The results can be returned over many pages. Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "FindRequestBody",
                  "metadataElementTypeName": "add typeName here",
                  "metadataElementSubtypeNames": [],
                  "searchProperties": {
                     "class" : "SearchProperties",
                     "conditions": [ {
                         "nestedConditions": {
                               "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "matchClassifications": {
                     "class" : "SearchClassifications",
                     "conditions": [{
                         "name" : "add classification name here",
                         "searchProperties": {
                            "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-conditions"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elementList", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def find_metadata_elements(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve the relationships linking the supplied elements.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "FindRequestBody",
                  "metadataElementTypeName": "add typeName here",
                  "metadataElementSubtypeNames": [],
                  "searchProperties": {
                     "class" : "SearchProperties",
                     "conditions": [ {
                         "nestedConditions": {
                               "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "matchClassifications": {
                     "class" : "SearchClassifications",
                     "conditions": [{
                         "name" : "add classification name here",
                         "searchProperties": {
                            "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_metadata_elements(
                body,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_find_relationships_between_elements(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """Return a list of relationships that match the requested conditions.
            The results can be received as a series of pages. Async version.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "FindRelationshipRequestBody",
                  "relationshipTypeName": "add typeName here",
                  "searchProperties": {
                     "class" : "SearchProperties",
                     "conditions": [ {
                         "nestedConditions": {
                               "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/relationships/by-search-conditions"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return process_related_element_list(
            response, mermaid_only, relationship_list=True
        )

    def find_relationships_between_elements(
        self,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """Return a list of relationships that match the requested conditions.
            The results can be received as a series of pages.

        Parameters
        ----------
        body: dict
            - A structure containing the search criteria. (example below)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes:

            Sample body:
                {
                  "class" : "FindRelationshipRequestBody",
                  "relationshipTypeName": "add typeName here",
                  "searchProperties": {
                     "class" : "SearchProperties",
                     "conditions": [ {
                         "nestedConditions": {
                               "class" : "SearchProperties",
                               "conditions": [
                               {
                                   "property" : "add name of property here",
                                   "operator": "EQ",
                                   "value": {
                                      "class" : "PrimitiveTypePropertyValue",
                                      "typeName" : "string",
                                      "primitiveValue" : "Add value here"
                                   }
                               }],
                               "matchCriteria": "ALL"
                         }
                     }],
                     "matchCriteria": "ANY"
                  },
                  "effectiveTime" : "{{$isoTimestamp}}",
                  "limitResultsByStatus" : ["ACTIVE"],
                  "asOfTime" : "{{$isoTimestamp}}",
                  "sequencingOrder": "CREATION_DATE_RECENT",
                  "sequencingProperty": ""
                }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_relationships_between_elements(
                body,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response

    async def _async_get_relationship_by_guid(
        self,
        guid: str,
        effective_time: str = None,
        as_of_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> dict | str:
        """
        Retrieve the relationship using its unique identifier. Async version.

        Parameters
        ----------
        guid : str
            - unique identifier of the relationship to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
            If the relationship is found, a dict of the relationship details is returned. Otherwise, the string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "AnyTimeRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/by-guid/{guid}"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_relationship_by_guid(
        self,
        guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
    ) -> dict | str:
        """
        Retrieve the relationship using its unique identifier.

        Parameters
        ----------
        guid : str
            - unique identifier of the relationship to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        dict | str
            If the relationship is found, a dict of the relationship details is returned. Otherwise, the string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationship_by_guid(
                guid, effective_time, for_lineage, for_duplicate_processing
            )
        )
        return response

    async def _async_get_relationship_history(
        self,
        guid: str,
        effective_time: str = None,
        oldest_first: bool = False,
        from_time: str = None,
        to_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve all the versions of a relationship. Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of element to retrieve.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

        Returns
        -------
        [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("oldestFirst", oldest_first),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/{guid}/history"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rel = response.json().get("relationshipList", NO_ELEMENTS_FOUND)
        if isinstance(rel, (list, dict)):
            return rel.get("elementList", NO_ELEMENTS_FOUND)
        else:
            return rel

    def get_relationship_history(
        self,
        guid: str,
        effective_time: str = None,
        oldest_first: bool = False,
        from_time: str = None,
        to_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
        mermaid_only: bool = False,
    ) -> list | str:
        """
        Retrieve all the versions of a relationship.

         Parameters
         ----------
         guid: str
             - Unique identity of element to retrieve.
         effective_time: str, default = None
             - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
         oldest_first: bool, default = False
         from_time: str, default = None
             Time to begin returning history
         to_time: str, default = None
             Time to end returning history
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         start_from: int, default = 0
             - index of the list to start from (0 for start).
         page_size
             - maximum number of elements to return.
         time_out: int, default = default_time_out
             - http request timeout for this request
         mermaid_only: bool, default is False
            - if true only a string representing the mermaid graph will be returned

         Returns
         -------
         [dict] | str
            If the element is found, and mermaid_only is False, a [dict] of the element details is returned.
            If mermaid_only is True, a string representing the mermaid graph will be returned.
            If no elements found, string "No element found".

         Raises
         ------
         InvalidParameterException
             one of the parameters is null or invalid or
         PropertyServerException
             There is a problem adding the element properties to the metadata repository or
         UserNotAuthorizedException
             the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationship_history(
                guid,
                effective_time,
                oldest_first,
                from_time,
                to_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
                mermaid_only,
            )
        )
        return response


if __name__ == "__main__":
    print("Main-Metadata Explorer")

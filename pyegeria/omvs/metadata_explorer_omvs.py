"""SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the metadata-explorer OMVS module.

[metadata-explorer](https://egeria-project.org/services/omvs/metadata-explorer/overview/)

"""

import asyncio

from httpx import Response
from loguru import logger
from typing import Any, Optional
from pyegeria.models import SearchStringRequestBody, FilterRequestBody, GetRequestBody, ResultsRequestBody
from pyegeria.core.utils import body_slimmer, dynamic_catch
from pyegeria.core._server_client import ServerClient, max_paging_size
from pyegeria.core._globals import default_time_out, NO_ELEMENTS_FOUND


def base_path(client: ServerClient, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/metadata-explorer"


@dynamic_catch
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


class MetadataExplorer(ServerClient):
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
        user_id: Optional[str] = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.metadata_explorer_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/metadata-explorer"
        )
        ServerClient.__init__(
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
    @dynamic_catch
    async def _async_get_metadata_guid_by_unique_name(
        self,
        name: str,
        property_name: str,
            as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
            body: Optional[dict | FilterRequestBody] = None
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
            as_of_time: str, default = None
                - The Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            effective_time: str, default = None
                - The Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            body: dict | FilterRequestBody, default = None
                - details of the request supersede parameters.

            Returns
            -------
            str
                The GUID of the element - or "No element found"

            Raises
            ------
            PyegeriaInvalidParameterException
                One of the parameters is null or invalid (for example, bad URL or invalid values).
            PyegeriaAPIException
                The server reported an error while processing a valid request.
            PyegeriaUnauthorizedException
                The requesting user is not authorized to issue this request.

            Notes
            -----
            Sample Body:
            {
              "class": "UniqueNameRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "as_of_time": "{{$isoTimestamp}}",
              "name": "active-metadata-store",
              "namePropertyName": "displayName"
            }


        """
        if body is None:
            body = {
                "class": "UniqueNameRequestBody",
                "effectiveTime": effective_time,
                "as_of_time": as_of_time,
            "name": name,
            "namePropertyName": property_name,
        }

        url = f"{base_path(self, self.view_server)}/metadata-elements/guid-by-unique-name"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("guid", NO_ELEMENTS_FOUND)

    @dynamic_catch
    def get_metadata_guid_by_unique_name(
        self,
        name: str,
        property_name: str,
            as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
            body: Optional[dict | FilterRequestBody] = None,
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
            as_of_time: str, default = None
                - The Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            effective_time: str, default = None
                - The Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            body: dict | FilterRequestBody, default = None
                - details of the request supersede parameters.

            Returns
            -------
            str
                The GUID of the element - or "No element found"

            Raises
            ------
            PyegeriaInvalidParameterException
                One of the parameters is null or invalid (for example, bad URL or invalid values).
            PyegeriaAPIException
                The server reported an error while processing a valid request.
            PyegeriaUnauthorizedException
                The requesting user is not authorized to issue this request.

            Notes
            -----
            Sample Body:
            {
              "class": "UniqueNameRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "as_of_time": "{{$isoTimestamp}}",
              "name": "active-metadata-store",
              "namePropertyName": "displayName"
            }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_guid_by_unique_name(name, property_name, as_of_time=as_of_time,
                                                         effective_time=effective_time, body=body)
        )
        return response

    @dynamic_catch
    async def _async_get_metadata_element_by_guid(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
            body: Optional[dict | GetRequestBody] = None,
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
        body: dict | GetRequestBody, default = None
            - details of the request supersede parameters. Body, if present overrides parameters.

        Returns
        -------
        dict | str
            If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----
        Sample Body:
        {
          "class": "GetRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "asOfTime": "{{$isoTimestamp}}"
        }

        """

        if body is None:
            body = {
                "class": "GetRequestBody",
                "effectiveTime": effective_time,
                "asOfTime": as_of_time,
            }

        url = f"{base_path(self, self.view_server)}/metadata-elements/{guid}"
        response = await self._async_get_guid_request(url=url, _type="Referenceable",
                                                      _gen_output=self._generate_referenceable_output,
                                                      output_format="JSON",
                                                      report_spec=None, body=body)
        return response

    @dynamic_catch
    def get_metadata_element_by_guid(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
            body: Optional[dict | GetRequestBody] = None,
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
        body: dict | GetRequestBody, default = None
            - details of the request supersede parameters. Body, if present overrides parameters.

        Returns
        -------
        dict | str
            If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_by_guid(guid, effective_time, as_of_time, body)
        )
        return response

    @dynamic_catch
    async def _async_get_anchored_element_graph(self, guid: str, effective_time: Optional[str] = None, as_of_time: Optional[str] = None,
                                                mermaid_only: bool = False,
                                                body: Optional[dict | GetRequestBody] = None) -> dict | str:
        """
        Retrieve the metadata element and all of its anchored elements using its unique identifier. Async version.

        Parameters
        ----------
        guid : str
            - unique identifier of the element to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
            - Query the element as of this time. If None, current time is used.
        body: dict | GetRequestBody, default = None
        - details of the request supersede parameters. Body, if present, overrides parameters.

        Returns
        -------
        dict | str
            If the element is found, a dict of the element details is returned.
            If no elements are found, string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        -----
        sample body:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}"
          "effectiveTime": "{{$isoTimestamp}}"
        }


        """

        if body is None:
            body = {
                "class": "GetRequestBody",
                "effectiveTime": effective_time,
                "asOfTime": as_of_time,
            }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}/with-anchored-elements"
        )
        response = await self._async_get_guid_request(
            url=url, _type="Referenceable", _gen_output=self._generate_referenceable_output,
            output_format="JSON", report_spec=None, body=body
        )
        if mermaid_only:
            return response.get("mermaidGraph", "No Mermaid Graph Found")
        return response

    @dynamic_catch
    def get_anchored_element_graph(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
            mermaid_only: bool = False,
            body: Optional[dict | GetRequestBody] = None
    ) -> dict | str:
        """
            Retrieve the metadata element and all of its anchored elements using its unique identifier.

            Parameters
            ----------
            guid : str
                - unique identifier of the element to retrieve
            effective_time: str, default = None
                - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            as_of_time: str, default = None
                - Query the element as of this time. If None, current time is used.
            body: dict | GetRequestBody, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.

            Returns
            -------
            dict | str
                If the element is found, a dict of the element details is returned.
                If no elements are found, string "No element found".

            Raises
            ------
            PyegeriaInvalidParameterException
                one of the parameters is null or invalid or
            PyegeriaAPIException
                There is a problem adding the element properties to the metadata repository or
            PyegeriaUnauthorizedException
                the requesting user is not authorized to issue this request.

            Notes:
            -----
            sample body:
            {
              "class": "GetRequestBody",
              "asOfTime": "{{$isoTimestamp}}"
              "effectiveTime": "{{$isoTimestamp}}"
            }

            Args:
                mermaid_only ():


            """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_anchored_element_graph(guid, effective_time, as_of_time, mermaid_only, body)
        )
        return response

    @dynamic_catch
    async def _async_get_metadata_element_by_unique_name(
        self,
        name: str,
        property_name: str = "qualifiedName",
        effective_time: Optional[str] = None,
            body: dict = None
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
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.
        Returns
        -------
        dict | str
                If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        -----
        sample body:
        {
          "class": "UniqueNameRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "asOfTime": "{{$isoTimestamp}},
          "name": "active-metadata-store",
          "namePropertyName": "displayName"
        }

        """

        if body is None:
            body = {
                "class": "UniqueNameRequestBody",
                "name": name,
                "namePropertyName": property_name,
                "effectiveTime": effective_time,
                "asOfTime": effective_time,
            }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-unique-name"

        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        return elements

    @dynamic_catch
    def get_metadata_element_by_unique_name(
        self,
        name: str,
        property_name: str = "qualifiedName",
        effective_time: Optional[str] = None,
            body: dict = None
    ) -> str:
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
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.
        Returns
        -------
        dict | str
                If the element is found, a dict of the element details is returned. Otherwise the string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        -----
        sample body:
        {
          "class": "UniqueNameRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "asOfTime": "{{$isoTimestamp}},
          "name": "active-metadata-store",
          "namePropertyName": "displayName"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_metadata_element_by_unique_name(name, property_name, effective_time, body)
        )
        return response

    @dynamic_catch
    async def _async_get_element_history(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        oldest_first: bool = False,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        start_from: int = 0,
            page_size: int = 0,
            body: dict = None
    ) -> list | str:
        """
        Retrieve all the versions of a metadata element. Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of an element to retrieve.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.

        Returns
        -------
        [dict] | str
            If the element is found, a [dict] of the element details is returned.
            If no there are elements found, string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        _____
        Sample body:
        {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
            "oldestFirst": oldest_first,
            "AsOfTime": "{{$isoTimestamp}}",
            "GraphQueryDepth": 5,
            "IncludeOnlyRelationships": ["relationships"]
        }
        """

        if body is None:
            body = {
                "class": "HistoryRequestBody",
                "effectiveTime": effective_time,
                "fromTime": from_time,
                "toTime": to_time,
                "oldestFirst": oldest_first,
                "startFrom": start_from,
                "pageSize": page_size
            }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}/history"

        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body),
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        return elements

    @dynamic_catch
    def get_element_history(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        oldest_first: bool = False,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
            body: dict = None

    ) -> list | str:
        """
        Retrieve all the versions of a metadata element.

        Parameters
        ----------
        guid: str
            - Unique identity of an element to retrieve.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = max_paging_size
            - maximum number of elements to return.
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.
        Returns
        -------
        [dict] | str
            If the element is found, a [dict] of the element details is returned.
            If no there are elements found, string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        _____
        Sample body:
        {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
            "oldestFirst": oldest_first,
            "AsOfTime": "{{$isoTimestamp}}",
            "GraphQueryDepth": 5,
            "IncludeOnlyRelationships": ["relationships"]
        }

        Args:
            body ():
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_element_history(guid, effective_time, oldest_first, from_time, to_time, start_from,
                                            page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_get_classification_history(
        self,
            guid: str,
            classification_name: str,
            effective_time: Optional[str] = None,
            oldest_first: bool = False,
            from_time: Optional[str] = None,
            to_time: Optional[str] = None,
        start_from: int = 0,
            page_size: int = 0,
            body: dict = None
    ) -> list | str:
        """
        Retrieve all the versions of a metadata element. Async version.

        Parameters
        ----------
        guid: str
            - Unique identity of an element to retrieve.
        classification_name: str
            - Name of the classification to retrieve history for.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.

        Returns
        -------
        [dict] | str
            If the element is found, a [dict] of the element details is returned.
            If no there are elements found, string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        _____
        Sample body:
        {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
            "oldestFirst": oldest_first,
            "AsOfTime": "{{$isoTimestamp}}",
            "GraphQueryDepth": 5,
            "IncludeOnlyRelationships": ["relationships"]
        }

        Args:
            classification_name ():
        """

        if body is None:
            body = {
                "class": "HistoryRequestBody",
                "effectiveTime": effective_time,
                "fromTime": from_time,
                "toTime": to_time,
                "oldestFirst": oldest_first,
                "startFrom": start_from,
                "pageSize": page_size
            }

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{guid}/classifications/"
            f"{classification_name}/history"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body),
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        return elements

    @dynamic_catch
    def get_classification_history(
        self,
            guid: str,
            classification_name: str,
            effective_time: Optional[str] = None,
            oldest_first: bool = False,
            from_time: Optional[str] = None,
            to_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
            body: dict = None

    ) -> list | str:
        """
        Retrieve all the versions of a metadata element.

        Parameters
        ----------
        guid: str
            - Unique identity of an element to retrieve.
        classification_name: str
            - Name of the classification to retrieve history for.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        oldest_first: bool, default = False
        from_time: str, default = None
            Time to begin returning history
        to_time: str, default = None
            Time to end returning history
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = max_paging_size
            - maximum number of elements to return.
        body: dict, default = None
            - details of the request supersede parameters. Body, if present, overrides parameters.

        Returns
        -------
        [dict] | str
            If the element is found, a [dict] of the element details is returned.
            If no there are elements found, string "No element found".

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        _____
        Sample body:
        {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
            "oldestFirst": oldest_first,
            "AsOfTime": "{{$isoTimestamp}}",
            "GraphQueryDepth": 5,
            "IncludeOnlyRelationships": ["relationships"]
        }
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_classification_history(guid, classification_name, effective_time, oldest_first, from_time,
                                                   to_time, start_from, page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_find_metadata_elements_with_string(self, search_string: str = "*", starts_with: bool = True,
                                                        ends_with: bool = False, ignore_case: bool = False,
                                                        anchor_domain: Optional[str] = None,
                                                        zone_filter=None, metadata_element_type: Optional[str] = None,
                                                        metadata_element_sub_type=None, skip_relationships=None,
                                                        include_only_relationships=None,
                                                        relationship_page_size: int = 10,
                                                        skip_classified_elements=None,
                                                        include_only_classified_elements: Optional[list[str]] = None,
                                                        graph_query_depth: int = 5,
                                                        as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                                        limit_results_by_status: Optional[list[str]] = None,
                                                        sequencing_order: str = "PROPERTY_ASCENDING",
                                                        sequencing_property: str = "qualifiedName",
                                                        start_from: int = 0, page_size: int = 0,
                                                        body: SearchStringRequestBody | dict = None) -> list | str:
        """ Searches for metadata elements based on a string pattern with a comprehensive filtering
        mechanism. This method allows for advanced keyword searches with various parameters including string
        matching rules, filtering by type, relationships, classifications, and querying depth.

        Args:

            search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                restrictions on the search string.
            starts_with (bool): If set to True, the search string should match only elements that start
                with the specified query. Defaults to True.
            ends_with (bool): If set to True, the search string should match only elements that end with
                the specified query. Defaults to False.
            ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
            anchor_domain (str): Restricts search results to elements within this specified domain.
                Defaults to None, indicating no specific domain.
            zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                those associated with the given zones. Defaults to None.
            metadata_element_type (str | None): Filters the search to elements of a specific metadata
                type. Defaults to None.
            metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                Defaults to None.
            skip_relationships (bool | None): If set to True, relationships associated with metadata
                elements are excluded from the search result. Defaults to None.
            include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                to be included exclusively in the search result. Defaults to None.
            relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                to 10.
            skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                are excluded from the search result. Defaults to None.
            include_only_classified_elements (list[str] | None): A list of classification names to restrict
                the search to metadata elements with these classifications exclusively. Defaults to None.
            graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                metadata elements. Defaults to 5.
            as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
            effective_time (str | None): Timestamp to filter metadata elements based on their effective
                state. Defaults to None.
            limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                with the specified statuses. Defaults to None.
            sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
            sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                "qualifiedName".
            start_from (int): The starting index for paginated results. Defaults to 0.
            page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                Defaults to 0.
            body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                or overrides. Defaults to None.

        Returns:
            list | str: Returns the search results as a list of metadata elements, or as a string in cases
                where the output is serialized in text format.
        """

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-string"
        )

        response = await self._async_find_request(url=url, _type="Referenceable",
                                                  _gen_output=self._generate_referenceable_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case,
                                                  anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_sub_type,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=zone_filter, as_of_time=as_of_time,
                                                  effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property, output_format="JSON",
                                                  report_spec=None, start_from=start_from, page_size=page_size,
                                                  body=body)
        return response

    @dynamic_catch
    def find_metadata_elements_with_string(self, search_string: str = "*", starts_with: bool = True,
                                           ends_with: bool = False, ignore_case: bool = False,
                                           anchor_domain: Optional[str] = None,
                                           zone_filter=None, metadata_element_type: Optional[str] = None,
                                           metadata_element_sub_type=None, skip_relationships=None,
                                           include_only_relationships=None, relationship_page_size: int = 10,
                                           skip_classified_elements=None,
                                           include_only_classified_elements: Optional[list[str]] = None,
                                           graph_query_depth: int = 5,
                                           as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                           limit_results_by_status: Optional[list[str]] = None,
                                           sequencing_order: str = "PROPERTY_ASCENDING",
                                           sequencing_property: str = "qualifiedName",
                                           start_from: int = 0, page_size: int = 0,
                                           body: SearchStringRequestBody | dict = None) -> list | str:
        """
        Asynchronously searches for metadata elements based on a string pattern with a comprehensive filtering
        mechanism. This method allows for advanced keyword searches with various parameters including string
        matching rules, filtering by type, relationships, classifications, and querying depth.

        Args:
            search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                restrictions on the search string.
            starts_with (bool): If set to True, the search string should match only elements that start
                with the specified query. Defaults to True.
            ends_with (bool): If set to True, the search string should match only elements that end with
                the specified query. Defaults to False.
            ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
            anchor_domain (str): Restricts search results to elements within this specified domain.
                Defaults to None, indicating no specific domain.
            zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                those associated with the given zones. Defaults to None.
            metadata_element_type (str | None): Filters the search to elements of a specific metadata
                type. Defaults to None.
            metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                Defaults to None.
            skip_relationships (bool | None): If set to True, relationships associated with metadata
                elements are excluded from the search result. Defaults to None.
            include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                to be included exclusively in the search result. Defaults to None.
            relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                to 10.
            skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                are excluded from the search result. Defaults to None.
            include_only_classified_elements (list[str] | None): A list of classification names to restrict
                the search to metadata elements with these classifications exclusively. Defaults to None.
            graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                metadata elements. Defaults to 5.
            as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
            effective_time (str | None): Timestamp to filter metadata elements based on their effective
                state. Defaults to None.
            limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                with the specified statuses. Defaults to None.
            sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
            sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                "qualifiedName".
            start_from (int): The starting index for paginated results. Defaults to 0.
            page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                Defaults to 0.
            body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                or overrides. Defaults to None.

        Returns:
            list | str: Returns the search results as a list of metadata elements, or as a string in cases
                where the output is serialized in text format.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_metadata_elements_with_string(search_string, starts_with, ends_with,
                                                           ignore_case, anchor_domain, zone_filter,
                                                           metadata_element_type, metadata_element_sub_type,
                                                           skip_relationships, include_only_relationships,
                                                           relationship_page_size, skip_classified_elements,
                                                           include_only_classified_elements,
                                                           graph_query_depth, as_of_time, effective_time,
                                                           limit_results_by_status, sequencing_order,
                                                           sequencing_property, start_from, page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_find_elements_for_anchor(self, anchor_guid: str, search_string: str = "*",
                                              starts_with: bool = True,
                                              ends_with: bool = False, ignore_case: bool = False,
                                              anchor_domain: Optional[str] = None,
                                              zone_filter=None, metadata_element_type: Optional[str] = None,
                                              metadata_element_sub_type=None, skip_relationships=None,
                                              include_only_relationships=None, relationship_page_size: int = 10,
                                              skip_classified_elements=None,
                                              include_only_classified_elements: Optional[list[str]] = None,
                                              graph_query_depth: int = 5,
                                              as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                              limit_results_by_status: Optional[list[str]] = None,
                                              sequencing_order: str = "PROPERTY_ASCENDING",
                                              sequencing_property: str = "qualifiedName",
                                              start_from: int = 0, page_size: int = 0,
                                              body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
        title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
        The breadth of the search is determined by the supplied anchorGUID. Async Version.

        Args:
            anchor_guid (str): The GUID of the metadata element to anchor the search from.
            search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                restrictions on the search string.
            starts_with (bool): If set to True, the search string should match only elements that start
                with the specified query. Defaults to True.
            ends_with (bool): If set to True, the search string should match only elements that end with
                the specified query. Defaults to False.
            ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
            anchor_domain (str): Restricts search results to elements within this specified domain.
                Defaults to None, indicating no specific domain.
            zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                those associated with the given zones. Defaults to None.
            metadata_element_type (str | None): Filters the search to elements of a specific metadata
                type. Defaults to None.
            metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                Defaults to None.
            skip_relationships (bool | None): If set to True, relationships associated with metadata
                elements are excluded from the search result. Defaults to None.
            include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                to be included exclusively in the search result. Defaults to None.
            relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                to 10.
            skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                are excluded from the search result. Defaults to None.
            include_only_classified_elements (list[str] | None): A list of classification names to restrict
                the search to metadata elements with these classifications exclusively. Defaults to None.
            graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                metadata elements. Defaults to 5.
            as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
            effective_time (str | None): Timestamp to filter metadata elements based on their effective
                state. Defaults to None.
            limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                with the specified statuses. Defaults to None.
            sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
            sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                "qualifiedName".
            start_from (int): The starting index for paginated results. Defaults to 0.
            page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                Defaults to 0.
            body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                or overrides. Defaults to None.

        Returns:
            list | str: Returns the search results as a list of metadata elements, or as a string in cases
                where the output is serialized in text format.
        """

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-string/for-anchor/{anchor_guid}"
        )

        response = await self._async_find_request(url=url, _type="Referenceable",
                                                  _gen_output=self._generate_referenceable_output,
                                                  search_string=search_string, anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_sub_type,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=zone_filter, as_of_time=as_of_time,
                                                  effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property, output_format="JSON",
                                                  report_spec=None, start_from=start_from, page_size=page_size,
                                                  body=body)
        return response

    @dynamic_catch
    def find_elements_for_anchor(self, anchor_guid: str, search_string: str = "*", starts_with: bool = True,
                                 ends_with: bool = False, ignore_case: bool = False, anchor_domain: Optional[str] = None,
                                 zone_filter=None, metadata_element_type: Optional[str] = None,
                                 metadata_element_sub_type=None, skip_relationships=None,
                                 include_only_relationships=None, relationship_page_size: int = 10,
                                 skip_classified_elements=None,
                                 include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 5,
                                 as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                 limit_results_by_status: Optional[list[str]] = None,
                                 sequencing_order: str = "PROPERTY_ASCENDING",
                                 sequencing_property: str = "qualifiedName",
                                 start_from: int = 0, page_size: int = 0,
                                 body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
            title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
            The breadth of the search is determined by the supplied anchorGUID.

            Args:
                anchor_guid (str): The GUID of the metadata element to anchor the search from.
                search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                    restrictions on the search string.
                starts_with (bool): If set to True, the search string should match only elements that start
                    with the specified query. Defaults to True.
                ends_with (bool): If set to True, the search string should match only elements that end with
                    the specified query. Defaults to False.
                ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
                anchor_domain (str): Restricts search results to elements within this specified domain.
                    Defaults to None, indicating no specific domain.
                zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                    those associated with the given zones. Defaults to None.
                metadata_element_type (str | None): Filters the search to elements of a specific metadata
                    type. Defaults to None.
                metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                    Defaults to None.
                skip_relationships (bool | None): If set to True, relationships associated with metadata
                    elements are excluded from the search result. Defaults to None.
                include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                    to be included exclusively in the search result. Defaults to None.
                relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                    to 10.
                skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                    are excluded from the search result. Defaults to None.
                include_only_classified_elements (list[str] | None): A list of classification names to restrict
                    the search to metadata elements with these classifications exclusively. Defaults to None.
                graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                    metadata elements. Defaults to 5.
                as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
                effective_time (str | None): Timestamp to filter metadata elements based on their effective
                    state. Defaults to None.
                limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                    with the specified statuses. Defaults to None.
                sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
                sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                    "qualifiedName".
                start_from (int): The starting index for paginated results. Defaults to 0.
                page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                    Defaults to 0.
                body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                    or overrides. Defaults to None.

            Returns:
                    list | str: Returns the search results as a list of metadata elements, or as a string in cases
                        where the output is serialized in text format.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_for_anchor(anchor_guid, search_string, starts_with, ends_with,
                                                 ignore_case, anchor_domain, zone_filter,
                                                 metadata_element_type, metadata_element_sub_type,
                                                 skip_relationships, include_only_relationships,
                                                 relationship_page_size, skip_classified_elements,
                                                 include_only_classified_elements,
                                                 graph_query_depth, as_of_time, effective_time,
                                                 limit_results_by_status, sequencing_order,
                                                 sequencing_property, start_from, page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_find_elements_in_anchor_domain(self, search_string: str = "*",
                                                    starts_with: bool = True,
                                                    ends_with: bool = False, ignore_case: bool = False,
                                                    anchor_domain: Optional[str] = None,
                                                    zone_filter=None, metadata_element_type: Optional[str] = None,
                                                    metadata_element_sub_type=None, skip_relationships=None,
                                                    include_only_relationships=None, relationship_page_size: int = 10,
                                                    skip_classified_elements=None,
                                                    include_only_classified_elements: Optional[list[str]] = None,
                                                    graph_query_depth: int = 5,
                                                    as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                                    limit_results_by_status: Optional[list[str]] = None,
                                                    sequencing_order: str = "PROPERTY_ASCENDING",
                                                    sequencing_property: str = "qualifiedName",
                                                    start_from: int = 0, page_size: int = 0,
                                                    body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
        title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
        The breadth of the search is determined by the supplied anchorGUID. Async Version.

        Args:
            search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                restrictions on the search string.
            starts_with (bool): If set to True, the search string should match only elements that start
                with the specified query. Defaults to True.
            ends_with (bool): If set to True, the search string should match only elements that end with
                the specified query. Defaults to False.
            ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
            anchor_domain (str): Restricts search results to elements within this specified domain.
                Defaults to None, indicating no specific domain.
            zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                those associated with the given zones. Defaults to None.
            metadata_element_type (str | None): Filters the search to elements of a specific metadata
                type. Defaults to None.
            metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                Defaults to None.
            skip_relationships (bool | None): If set to True, relationships associated with metadata
                elements are excluded from the search result. Defaults to None.
            include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                to be included exclusively in the search result. Defaults to None.
            relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                to 10.
            skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                are excluded from the search result. Defaults to None.
            include_only_classified_elements (list[str] | None): A list of classification names to restrict
                the search to metadata elements with these classifications exclusively. Defaults to None.
            graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                metadata elements. Defaults to 5.
            as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
            effective_time (str | None): Timestamp to filter metadata elements based on their effective
                state. Defaults to None.
            limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                with the specified statuses. Defaults to None.
            sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
            sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                "qualifiedName".
            start_from (int): The starting index for paginated results. Defaults to 0.
            page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                Defaults to 0.
            body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                or overrides. Defaults to None.

        Returns:
            list | str: Returns the search results as a list of metadata elements, or as a string in cases
                where the output is serialized in text format.
        """

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-string/"
            f"in-anchor-domain/{anchor_domain}"
        )

        response = await self._async_find_request(url=url, _type="Referenceable",
                                                  _gen_output=self._generate_referenceable_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case,
                                                  anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_sub_type,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=zone_filter, as_of_time=as_of_time,
                                                  effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property, output_format="JSON",
                                                  report_spec=None, start_from=start_from, page_size=page_size,
                                                  body=body)
        return response

    @dynamic_catch
    def find_elements_in_anchor_domain(self, search_string: str = "*", starts_with: bool = True,
                                       ends_with: bool = False, ignore_case: bool = False, anchor_domain: Optional[str] = None,
                                       zone_filter=None, metadata_element_type: Optional[str] = None,
                                       metadata_element_sub_type=None, skip_relationships=None,
                                       include_only_relationships=None, relationship_page_size: int = 10,
                                       skip_classified_elements=None,
                                       include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 5,
                                       as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                       limit_results_by_status: Optional[list[str]] = None,
                                       sequencing_order: str = "PROPERTY_ASCENDING",
                                       sequencing_property: str = "qualifiedName",
                                       start_from: int = 0, page_size: int = 0,
                                       body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
            title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
            The breadth of the search is determined by the supplied anchorGUID.

            Args:
                search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                    restrictions on the search string.
                starts_with (bool): If set to True, the search string should match only elements that start
                    with the specified query. Defaults to True.
                ends_with (bool): If set to True, the search string should match only elements that end with
                    the specified query. Defaults to False.
                ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
                anchor_domain (str): Restricts search results to elements within this specified domain.
                    Defaults to None, indicating no specific domain.
                zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                    those associated with the given zones. Defaults to None.
                metadata_element_type (str | None): Filters the search to elements of a specific metadata
                    type. Defaults to None.
                metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                    Defaults to None.
                skip_relationships (bool | None): If set to True, relationships associated with metadata
                    elements are excluded from the search result. Defaults to None.
                include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                    to be included exclusively in the search result. Defaults to None.
                relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                    to 10.
                skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                    are excluded from the search result. Defaults to None.
                include_only_classified_elements (list[str] | None): A list of classification names to restrict
                    the search to metadata elements with these classifications exclusively. Defaults to None.
                graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                    metadata elements. Defaults to 5.
                as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                    state as of the given time. Defaults to None.
                effective_time (str | None): Timestamp to filter metadata elements based on their effective
                    state. Defaults to None.
                limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                    with the specified statuses. Defaults to None.
                sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
                sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                    "qualifiedName".
                start_from (int): The starting index for paginated results. Defaults to 0.
                page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                    Defaults to 0.
                body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                    or overrides. Defaults to None.

            Returns:
                    list | str: Returns the search results as a list of metadata elements, or as a string in cases
                        where the output is serialized in text format.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_in_anchor_domain(search_string, starts_with, ends_with, ignore_case,
                                                       anchor_domain, zone_filter,
                                                       metadata_element_type, metadata_element_sub_type,
                                                       skip_relationships, include_only_relationships,
                                                       relationship_page_size, skip_classified_elements,
                                                       include_only_classified_elements, graph_query_depth, as_of_time,
                                                       effective_time, limit_results_by_status, sequencing_order,
                                                       sequencing_property, start_from,
                                                       page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_find_elements_in_anchor_scope(self, anchor_scope_guid: str, search_string: str = "*",
                                                   starts_with: bool = True,
                                                   ends_with: bool = False, ignore_case: bool = False,
                                                   anchor_domain: Optional[str] = None,
                                                   zone_filter=None, metadata_element_type: Optional[str] = None,
                                                   metadata_element_sub_type=None, skip_relationships=None,
                                                   include_only_relationships=None, relationship_page_size: int = 10,
                                                   skip_classified_elements=None,
                                                   include_only_classified_elements: Optional[list[str]] = None,
                                                   graph_query_depth: int = 5,
                                                   as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                                   limit_results_by_status: Optional[list[str]] = None,
                                                   sequencing_order: str = "PROPERTY_ASCENDING",
                                                   sequencing_property: str = "qualifiedName",
                                                   start_from: int = 0, page_size: int = 0,
                                                   body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
            title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
            The breadth of the search is determined by the supplied scope guid. The results are organized by anchor element.
            Async Version.

        Args:
            anchor_scope_guid (str): The guid of the scope to search within. Required.
            search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                restrictions on the search string.
            starts_with (bool): If set to True, the search string should match only elements that start
                with the specified query. Defaults to True.
            ends_with (bool): If set to True, the search string should match only elements that end with
                the specified query. Defaults to False.
            ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
            anchor_domain (str): Restricts search results to elements within this specified domain.
                Defaults to None, indicating no specific domain.
            zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                those associated with the given zones. Defaults to None.
            metadata_element_type (str | None): Filters the search to elements of a specific metadata
                type. Defaults to None.
            metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                Defaults to None.
            skip_relationships (bool | None): If set to True, relationships associated with metadata
                elements are excluded from the search result. Defaults to None.
            include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                to be included exclusively in the search result. Defaults to None.
            relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                to 10.
            skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                are excluded from the search result. Defaults to None.
            include_only_classified_elements (list[str] | None): A list of classification names to restrict
                the search to metadata elements with these classifications exclusively. Defaults to None.
            graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                metadata elements. Defaults to 5.
            as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
            effective_time (str | None): Timestamp to filter metadata elements based on their effective
                state. Defaults to None.
            limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                with the specified statuses. Defaults to None.
            sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
            sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                "qualifiedName".
            start_from (int): The starting index for paginated results. Defaults to 0.
            page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                Defaults to 0.
            body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                or overrides. Defaults to None.

        Returns:
            list | str: Returns the search results as a list of metadata elements, or as a string in cases
                where the output is serialized in text format.
        """

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-string/"
            f"in-anchor-scope/{anchor_scope_guid}"
        )

        response = await self._async_find_request(url=url, _type="Referenceable",
                                                  _gen_output=self._generate_referenceable_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case,
                                                  anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_sub_type,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=zone_filter, as_of_time=as_of_time,
                                                  effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property, output_format="JSON",
                                                  report_spec=None, start_from=start_from, page_size=page_size,
                                                  body=body)
        return response

    @dynamic_catch
    def find_elements_in_anchor_scope(self, anchor_scope_guid: str, search_string: str = "*", starts_with: bool = True,
                                      ends_with: bool = False, ignore_case: bool = False, anchor_domain: Optional[str] = None,
                                      zone_filter=None, metadata_element_type: Optional[str] = None,
                                      metadata_element_sub_type=None, skip_relationships=None,
                                      include_only_relationships=None, relationship_page_size: int = 10,
                                      skip_classified_elements=None,
                                      include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 5,
                                      as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                                      limit_results_by_status: Optional[list[str]] = None,
                                      sequencing_order: str = "PROPERTY_ASCENDING",
                                      sequencing_property: str = "qualifiedName",
                                      start_from: int = 0, page_size: int = 0,
                                      body: SearchStringRequestBody | dict = None) -> list | str:
        """ Return a list of elements with the requested search string in their (display, resource) name, qualified name,
            title, text, summary, identifier, or description.  The search string is interpreted as a regular expression (RegEx).
            The breadth of the search is determined by the supplied scope guid. The results are organized by anchor element.

            Args:
                anchor_scope_guid (str): The guid of the scope to search within. Required.
                search_string (str): The string pattern to search for. Defaults to "*", which indicates no
                    restrictions on the search string.
                starts_with (bool): If set to True, the search string should match only elements that start
                    with the specified query. Defaults to True.
                ends_with (bool): If set to True, the search string should match only elements that end with
                    the specified query. Defaults to False.
                ignore_case (bool): Flags whether the search should be case-insensitive. Defaults to False.
                anchor_domain (str): Restricts search results to elements within this specified domain.
                    Defaults to None, indicating no specific domain.
                zone_filter (list[str] | None): A list of zone names to filter the metadata elements to
                    those associated with the given zones. Defaults to None.
                metadata_element_type (str | None): Filters the search to elements of a specific metadata
                    type. Defaults to None.
                metadata_element_sub_type (str | None): Filters the search to elements of a specific subtype.
                    Defaults to None.
                skip_relationships (bool | None): If set to True, relationships associated with metadata
                    elements are excluded from the search result. Defaults to None.
                include_only_relationships (list[str] | None): A list specifying identifiers of relationships
                    to be included exclusively in the search result. Defaults to None.
                relationship_page_size (int): The maximum number of relationships retrieved per page. Defaults
                    to 10.
                skip_classified_elements (bool | None): If set to True, metadata elements with classifications
                    are excluded from the search result. Defaults to None.
                include_only_classified_elements (list[str] | None): A list of classification names to restrict
                    the search to metadata elements with these classifications exclusively. Defaults to None.
                graph_query_depth (int): Specifies the depth for graph queries, useful for deeply connected
                    metadata elements. Defaults to 5.
                as_of_time (str | None): Timestamp to filter metadata elements based on their historical
                state as of the given time. Defaults to None.
                effective_time (str | None): Timestamp to filter metadata elements based on their effective
                    state. Defaults to None.
                limit_results_by_status (list[str] | None): Filters to return only metadata elements associated
                    with the specified statuses. Defaults to None.
                sequencing_order (str): Determines the sequencing order of results. Defaults to "PROPERTY_ASCENDING".
                sequencing_property (str): The property used for sequencing metadata elements. Defaults to
                    "qualifiedName".
                start_from (int): The starting index for paginated results. Defaults to 0.
                page_size (int): The number of metadata elements to return per page. A value of 0 implies no pagination.
                    Defaults to 0.
                body (SearchStringRequestBody | dict | None): A payload containing additional search parameters
                    or overrides. Defaults to None.

            Returns:
                    list | str: Returns the search results as a list of metadata elements, or as a string in cases
                        where the output is serialized in text format.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_in_anchor_scope(anchor_scope_guid, search_string, starts_with, ends_with,
                                                      ignore_case, anchor_domain, zone_filter,
                                                      metadata_element_type, metadata_element_sub_type,
                                                      skip_relationships, include_only_relationships,
                                                      relationship_page_size, skip_classified_elements,
                                                      include_only_classified_elements, graph_query_depth, as_of_time,
                                                      effective_time, limit_results_by_status, sequencing_order,
                                                      sequencing_property, start_from,
                                                      page_size, body)
        )
        return response

    @dynamic_catch
    async def _async_get_all_related_elements(
        self,
            element_guid: str,
        starting_at_end: int = 0,
        start_from: int = 0,
            page_size: int = 0,
            graph_query_depth: int = 5,
            relationships_page_size: int = 0,
            body: Optional[dict | ResultsRequestBody] = None,
    ) -> list | str:
        """ Retrieve the metadata elements connected to the supplied element. Async Version.

        Args:
            element_guid (str): The identifier of the element whose related metadata
                elements are to be fetched.
            starting_at_end (int): Indicator for starting fetch operation from the
                end of the result list. Defaults to 0.
            start_from (int): The starting index for fetching results. Defaults to 0.
            page_size (int): The maximum number of metadata elements to retrieve per
                page. Defaults to the constant max_paging_size.
            graph_query_depth (int): The depth level of the query in the metadata graph
                to traverse to fetch related elements. Defaults to 5.
            relationships_page_size (int): The page size for traversing relationships.
                Defaults to 0 (no limit).
            body (dict | ResultsRequestBody): The request body containing additional
                filtering or query parameters specific to the request. This can either
                be a dictionary or an object of class ResultsRequestBody.

        Returns:
            list | str: The related metadata elements, either in list format or as a
                string based on the specified output format.
        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Notes:
        -----
            Sample body:
            {
              "class": "ResultsRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }
        """
        if body is None:
            body = {
                "class": "ResultsRequestBody",
                "startFrom": start_from,
                "pageSize": page_size,
                "graphQueryDepth": graph_query_depth,
                "relationshipsPageSize": relationships_page_size,
            }
        url = (
            f"{base_path(self, self.view_server)}/related-elements/{element_guid}/"
            f"any-type?startingAtEnd={starting_at_end}"

        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        rel_list = process_related_element_list(response, False)
        return rel_list

    def get_all_related_elements(
            self,
            element_guid: str,
            starting_at_end: int = 0,
            start_from: int = 0,
            page_size: int = max_paging_size,
            graph_query_depth: int = 5,
            relationships_page_size: int = 0,
            body: Optional[dict | ResultsRequestBody] = None,
    ) -> list | str:
        """ Retrieve the metadata elements connected to the supplied element.

        Args:
            element_guid (str): The identifier of the element whose related metadata
                elements are to be fetched.
            starting_at_end (int): Indicator for starting fetch operation from the
                end of the result list. Defaults to 0.
            start_from (int): The starting index for fetching results. Defaults to 0.
            page_size (int): The maximum number of metadata elements to retrieve per
                page. Defaults to the constant max_paging_size.
            graph_query_depth (int): The depth level of the query in the metadata graph
                to traverse to fetch related elements. Defaults to 5.
            relationships_page_size (int): The page size for traversing relationships.
                Defaults to 0 (no limit).
            body (dict | ResultsRequestBody): The request body containing additional
                filtering or query parameters specific to the request. This can either
                be a dictionary or an object of class ResultsRequestBody.

        Returns:
            list | str: The related metadata elements, either in list format or as a
                string based on the specified output format.
        Raises
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        Notes:
            Sample body:
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
        response = loop.run_until_complete(
            self._async_get_all_related_elements(element_guid, starting_at_end, start_from, page_size,
                                                 graph_query_depth, relationships_page_size,
                                                 body=body)
        )
        return response

    async def _async_get_related_metadata_elements(
            self,
            element_guid: str,
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
                - Unique identity of the element to retrieve.
            relationship_type: str
                - name of the relationship type to retrieve relationships of
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
                The related metadata elements.

            Raises
            ------
            PyegeriaInvalidParameterException
                one of the parameters is null or invalid or
            PyegeriaAPIException
                There is a problem adding the element properties to the metadata repository or
            PyegeriaUnauthorizedException
                the requesting user is not authorized to issue this request.

            Notes:

                Sample body:
                    {
                      "class": "ResultsRequestBody",
                      "effectiveTime": "{{$isoTimestamp}}",
                      "limitResultsByStatus": ["ACTIVE"],
                      "asOfTime": "{{$isoTimestamp}}",
                      "sequencingOrder": "PROPERTY_ASCENDING",
                      "sequencingProperty": "fileName"
                    }

            """

        url = (
            f"{base_path(self, self.view_server)}/related-elements/{element_guid}/type/{relationship_type}"

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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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

        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{end1_guid}/linked-by-any-type/"
            f"to-elements/{end2_guid}"
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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


        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/{end1_guid}/linked-by-type/"
            f"{relationship_type}/to-elements/{end2_guid}"
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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


        url = (
            f"{base_path(self, self.view_server)}/metadata-elements/by-search-conditions"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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

        url = (
            f"{base_path(self, self.view_server)}/relationships/by-search-conditions"
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        effective_time: Optional[str] = None,
        as_of_time: Optional[str] = None,
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        """


        body = {
            "class": "AnyTimeRequestBody",
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/by-guid/{guid}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("element", NO_ELEMENTS_FOUND)

    def get_relationship_by_guid(
        self,
        guid: str,
        effective_time: Optional[str] = None,
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        effective_time: Optional[str] = None,
        oldest_first: bool = False,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        """


        body = {
            "class": "HistoryRequestBody",
            "effectiveTime": effective_time,
            "fromTime": from_time,
            "toTime": to_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/{guid}/history"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rel = response.json().get("relationshipList", NO_ELEMENTS_FOUND)
        if isinstance(rel, (list, dict)):
            return rel.get("elements", NO_ELEMENTS_FOUND)
        else:
            return rel

    def get_relationship_history(
        self,
        guid: str,
        effective_time: Optional[str] = None,
        oldest_first: bool = False,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
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
         PyegeriaInvalidParameterException
             one of the parameters is null or invalid or
         PyegeriaAPIException
             There is a problem adding the element properties to the metadata repository or
         PyegeriaUnauthorizedException
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

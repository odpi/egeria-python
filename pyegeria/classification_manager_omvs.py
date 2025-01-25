"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the classification_manager_omvs module.

"""

import asyncio

from httpx import Response

from pyegeria import body_slimmer

# import json
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import default_time_out


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
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/classification-manager"


class ClassificationManager(Client):
    """ClassificationManager is a class that extends the Client class. It
    provides methods to CRUD annotations and to query elements and relationships. Async version.

    Attributes:

        server_name: str
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
        self.classification_command_root: str = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/classification-manager"
        Client.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )

    #
    #   Get elements
    #

    async def _async_get_elements(
        self,
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements of the requested type name. If no type name is specified, then any type of element may
        be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/by-type{possible_query_params}"
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_elements(
        self,
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements of the requested type name. If no type name is specified, then any type of element may
        be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements(
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/by-exact-property-value{possible_query_params}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_property_value(
                property_value,
                property_names,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_find_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified. The value must only be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict the
        results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/by-property-value-search{possible_query_params}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def find_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified. The value must only be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict the
        results.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_by_property_value(
                property_value,
                property_names,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_element_by_guid(
        self,
        element_guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> dict | str:
        """
        Retrieve element by its unique identifier.  Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
           - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
           - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        dict | str
            Returns a string if no elements found; otherwise a dict of the element.

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
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}{possible_query_params}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("element", "No elements found")

        return elements

    def get_element_by_guid(
        self,
        element_guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> dict | str:
        """
        Retrieve element by its unique identifier.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
           - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
           - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        dict | str
            Returns a string if no elements found; otherwise a dict of the element.

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
            self._async_get_element_by_guid(
                element_guid,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )
        return response

    def get_actor_for_guid(self, guid: str) -> str:
        """Get the name of the actor from the supplied guid."""
        details = self.get_element_by_guid(guid)
        if type(details) is str:
            return details
        if details["elementHeader"]["type"]["typeName"] != "UserIdentity":
            return "GUID does not represent a UserIdentity"
        return details["properties"]["userId"]

    async def _async_get_element_by_unique_name(
        self,
        name: str,
        property_name: str = None,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve the metadata element using the supplied unique element name (typically the qualifiedName,
        but it is possible to specify a different property name in the request body as long as its unique.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional
            - optional name of property to search. If not specified, defaults to qualifiedName
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        property_name = "qualifiedName" if property_name is None else property_name

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
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/by-unique-name{possible_query_params}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return response.json().get("element", "No elements found")

    def get_element_by_unique_name(
        self,
        name: str,
        property_name: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve the metadata element using the supplied unique element name (typically the qualifiedName,
        but it is possible to specify a different property name in the request body as long as its unique.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional
            - optional name of property to search. If not specified, defaults to qualifiedName
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

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
            self._async_get_element_by_unique_name(
                name,
                property_name,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )
        return response

    async def _async_get_element_guid_by_unique_name(
        self,
        name: str,
        property_name: str = 'qualifiedName',
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied unique element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional, default = "qualifiedName"
            - optional name of property to search. If not specified, defaults to qualifiedName
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        property_name = "qualifiedName" if property_name is None else property_name

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
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/guid-by-unique-name{possible_query_params}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        return response.json().get("guid", "No elements found")

    def get_element_guid_by_unique_name(
        self,
        name: str,
        property_name: str = "qualifiedName",
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied unique element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional, default = "qualifiedName"
            - optional name of property to search. If not specified, defaults to qualifiedName
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

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
            self._async_get_element_guid_by_unique_name(
                name,
                property_name,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )
        return response

    async def _async_get_guid_for_name(
        self, name: str, time_out: int = default_time_out
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        property_name = ["name", "displayName", "title"]
        elements = await self._async_get_elements_by_property_value(
            name, property_name, None
        )

        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
            elif len(elements) > 1:
                raise Exception("Multiple elements found for supplied name!")
            elif len(elements) == 1:
                return elements[0]["elementHeader"]["guid"]
        return elements

    def get_guid_for_name(
        self, name: str, time_out: int = default_time_out
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        str
            Returns the guid of the element.

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
            self._async_get_guid_for_name(name, time_out)
        )
        return response

    async def _async_find_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict
        the results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/elements/by-property-value-search{possible_query_params}"
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def find_elements_by_property_value(
        self,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict
        the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_by_property_value(
                property_value,
                property_names,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    #
    # Elements by classification
    #
    async def _async_get_elements_by_classification(
        self,
        classification_name: str,
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
         Retrieve elements with the requested classification name. It is also possible to limit the results
        by specifying a type name for the elements that should be returned. If no type name is specified then
        any type of element may be returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DD THH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}"
            f"{possible_query_params}"
        )
        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_elements_by_classification(
        self,
        classification_name: str,
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name. It is also possible to limit the results
        by specifying a type name for the elements that should be returned. If no type name is specified then
        any type of element may be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_classification(
                classification_name,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_elements_by_classification_with_property_value(
        self,
        classification_name: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested a value found in one of the
        classification's properties specified.  The value must match exactly. An open metadata type name may be supplied
        to restrict the types of elements returned. Async version.

         https://egeria-project.org/types/

         Parameters
         ----------
         classification_name: str
             - the classification name to retrieve elements for.
         property_value: str
             - property value to be searched.
         property_names: [str]
             - property names to search in.
         open_metadata_type_name : str, default = None
             - open metadata type to be used to restrict the search
         effective_time: str, default = None
             - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}/"
            f"with-exact-property-value{possible_query_params}"
        )
        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_elements_by_classification_with_property_value(
        self,
        classification_name: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_classification_with_property_value(
                classification_name,
                property_value,
                property_names,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_find_elements_by_classification_with_property_value(
        self,
        classification_name: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested value found in
        one of the classification's properties specified.  The value must only be contained in the
        properties rather than needing to be an exact match.
        An open metadata type name may be supplied to restrict the results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}/"
            f"with-property-value-search{possible_query_params}"
        )
        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def find_elements_by_classification_with_property_value(
        self,
        classification_name: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested a value found in
        one of the classification's properties specified.  The value must only be contained in the
        properties rather than needing to be an exact match.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_by_classification_with_property_value(
                classification_name,
                property_value,
                property_names,
                open_metadata_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    #
    #   related elements
    #

    async def _async_get_related_elements(
        self,
        element_guid: str,
        relationship_type: str = None,
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked by relationship type name. If the relationship type is None, then all related elements
        will be returned. It is also possible to limit the results by specifying a type name for the elements that
        should be returned. If no type name is specified then any type of element may be returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str, optional, default = None
            - the type of relationship to navigate to related elements.
              If None, then all related elements will be returned.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ("startAtEnd", start_at_end),
            ]
        )

        body = {
            "class": "FindProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "effectiveTime": effective_time,
        }

        if relationship_type is None:
            url = (
                f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship"
                f"{possible_query_params}"
            )
        else:
            url = (
                f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
                f"{relationship_type}{possible_query_params}"
            )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_related_elements(
        self,
        element_guid: str,
        relationship_type: str = None,
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked by relationship type name. If the relationship type is None, then all related elements
        will be returned. It is also possible to limit the results by specifying a type name for the elements that
        should be returned. If no type name is specified then any type of element may be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_elements(
                element_guid,
                relationship_type,
                open_metadata_type_name,
                start_at_end,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_related_elements_with_property_value(
        self,
        element_guid: str,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must match exactly. An open metadata type name may be
        supplied to restrict the types of elements returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - restrict search to elements of this open metadata type
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ("startAtEnd", start_at_end),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
            f"{relationship_type}/with-exact-property-value{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def get_related_elements_with_property_value(
        self,
        element_guid: str,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must match exactly. An open metadata type name may be
        supplied to restrict the types of elements returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_elements_with_property_value(
                element_guid,
                relationship_type,
                property_value,
                property_names,
                open_metadata_type_name,
                start_at_end,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_find_related_elements_with_property_value(
        self,
        element_guid: str,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match An open metadata type name may be supplied to restrict the types of elements
        returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - restrict search to elements of this open metadata type
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ("startAtEnd", start_at_end),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataTypeName": open_metadata_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
            f"{relationship_type}/with-property-value-search{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", "No elements found")
        if type(elements) is list:
            if len(elements) == 0:
                return "No elements found"
        return elements

    def find_related_elements_with_property_value(
        self,
        element_guid: str,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        open_metadata_type_name: str = None,
        start_at_end: int = 1,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match An open metadata type name may be supplied to restrict the types of elements
        returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        open_metadata_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_related_elements_with_property_value(
                element_guid,
                relationship_type,
                property_value,
                property_names,
                open_metadata_type_name,
                start_at_end,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    #
    #   relationships

    async def _async_get_relationships(
        self,
        relationship_type: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name. Async version.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {"class": "FindProperties", "effectiveTime": effective_time}

        url = (
            f"{base_path(self, self.view_server)}/relationships/{relationship_type}"
            f"{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rels = response.json().get("relationships", "No relationships found")

        if type(rels) is list:
            if len(rels) == 0:
                return "No elements found"
        return rels

    def get_relationships(
        self,
        relationship_type: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationships(
                relationship_type,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_get_relationships_with_property_value(
        self,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in
        one of the relationship's properties specified.  The value must match exactly. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/{relationship_type}/"
            f"with-exact-property-value{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rels = response.json().get("relationships", "No elements found")
        if type(rels) is list:
            if len(rels) == 0:
                return "No elements found"
        return rels

    def get_relationships_with_property_value(
        self,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in
        one of the relationship's properties specified.  The value must match exactly.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationships_with_property_value(
                relationship_type,
                property_value,
                property_names,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def _async_find_relationships_with_property_value(
        self,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in one of
        the relationship's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match. Async version.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindPropertyNamesProperties",
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/"
            f"{relationship_type}/with-property-value-search{possible_query_params}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        rels = response.json().get("relationships", "No elements found")
        if type(rels) is list:
            if len(rels) == 0:
                return "No elements found"
        return rels

    def find_relationships_with_property_value(
        self,
        relationship_type: str,
        property_value: str,
        property_names: [str],
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        time_out: int = default_time_out,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in one of
        the relationship's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match..

        https://egeria-project.org/types/

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: [str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_relationships_with_property_value(
                relationship_type,
                property_value,
                property_names,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    #
    #  guid
    #

    async def _async_retrieve_instance_for_guid(
        self,
        guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
         Retrieve the header for the instance identified by the supplied unique identifier.
         It may be an element (entity) or a relationship between elements. Async version.

        Parameters
        ----------
        guid: str
            - the identity of the instance to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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
        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        body = {
            "class": "FindProperties",
            "effectiveTime": effective_time,
        }

        url = f"{base_path(self, self.view_server)}/guids/{guid}{possible_query_params}"
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        element = response.json().get("element", "No elements found")
        return element

    def retrieve_instance_for_guid(
        self,
        guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> list | str:
        """
         Retrieve the header for the instance identified by the supplied unique identifier.
         It may be an element (entity) or a relationship between elements.

        Parameters
        ----------
        guid: str
            - the identity of the instance to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_retrieve_instance_for_guid(
                guid,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )
        return response

    #
    #   Classification CRUD
    #

    async def _async_set_confidence_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate the level of confidence that the organization
        has that the data is complete, accurate and up-to-date.  The level of confidence is expressed by the
        levelIdentifier property. Async version.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidence" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidence"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_confidence_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate the level of confidence that the organization
        has that the data is complete, accurate and up-to-date.  The level of confidence is expressed by the
        levelIdentifier property.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidence" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_confidence_classification(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_confidence_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidence classification from the element.  This normally occurs when the organization has lost
        track of the level of confidence to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidence/remove"
            f"{possible_query_params}"
        )
        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_confidence_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidence classification from the element.  This normally occurs when the organization has lost
        track of the level of confidence to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_confidence_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_confidentiality_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of confidentiality that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of confidentiality is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property. Async version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidentiality" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidentiality"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_confidentiality_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of confidentiality that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of confidentiality is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidentiality" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_confidentiality_classification(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_confidentiality_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidentiality classification from the element.  This normally occurs when the organization has lost
        track of the level of confidentiality to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidentiality/remove"
            f"{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_confidentiality_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidentiality classification from the element.  This normally occurs when the organization has lost
        track of the level of confidentiality to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_confidentiality_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_criticality_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how critical the element (or
        associated resource) is to the organization.  The level of criticality is expressed by the levelIdentifier
        property. Async version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "criticality" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/criticality"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_criticality_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how critical the element (or
        associated resource) is to the organization.  The level of criticality is expressed by the levelIdentifier
        property.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an-isoTimestamp",
           "properties" : {
               "class" : "GovernanceClassificationProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "criticality" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_criticality_classification(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_criticality_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the criticality classification from the element.  This normally occurs when the organization has lost
        track of the level of criticality to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/criticality/remove"
            f"{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_criticality_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the criticality classification from the element.  This normally occurs when the organization has lost
        track of the level of criticality to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_criticality_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_add_gov_definition_to_element(
        self,
        definition_guid: str,
        element_guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Link a governance definition to an element using the GovernedBy relationship. Async version.

        Governance Definitions: https://egeria-project.org/types/4/0401-Governance-Definitions/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        effective_time: str, default is None
            - None means ignore, otherwise the time that the element must be effective
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

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

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governed-by/definition/{definition_guid}"
            f"{possible_query_params}"
        )

        body = {"class": "RelationshipRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_gov_definition_to_element(
        self,
        definition_guid: str,
        element_guid: str,
        effective_time: str = None,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Link a governance definition to an element using the GovernedBy relationship.

        Governance Definition: https://egeria-project.org/types/4/0401-Governance-Definitions/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        effective_time: str, default is None
            - None means ignore, otherwise the time that the element must be effective
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

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
        loop.run_until_complete(
            self._async_add_gov_definition_to_element(
                definition_guid,
                element_guid,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_gov_definition_from_element(
        self,
        definition_guid,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the GovernedBy relationship between a governance definition and an element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governed-by/definition/"
            f"{definition_guid}/remove{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_gov_definition_from_element(
        self,
        definition_guid,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the GovernedBy relationship between a governance definition and an element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_criticality_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_add_ownership_to_element(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the ownership classification for an element. Async version.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - structure containing ownership information - see Notes
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "OwnerProperties",
               "owner" : "Add value here",
               "ownerTypeName" : "Add value here",
               "ownerPropertyName" : "Add value here"
           }
        }

        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/ownership"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_ownership_to_element(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the ownership classification for an element.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - structure containing ownership information - see Notes
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Notes
        -----

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "OwnerProperties",
               "owner" : "Add value here",
               "ownerTypeName" : "Add value here",
               "ownerPropertyName" : "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_ownership_to_element(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_ownership_from_element(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the ownership classification from an element. Async version.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

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

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/ownership/remove"
            f"{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_ownership_from_element(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the ownership classification from an element.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

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
        loop.run_until_complete(
            self._async_clear_ownership_from_element(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_retention_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how long the element (or associated resource)
        is to be retained by the organization.  The policy to apply to the element/resource is captured by the retentionBasis
        property.  The dates after which the element/resource is archived and then deleted are specified in the archiveAfter and deleteAfter
        properties respectively. Async version

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "RetentionClassificationProperties",
               "retentionBasis" : 0,
               "status" : 0,
               "confidence" : 0,
               "associatedGUID" : "Add value here",
               "archiveAfter" : "{{$isoTimestamp}}",
               "deleteAfter" : "{{$isoTimestamp}}",
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/retention"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_retention_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how long the element (or associated resource)
        is to be retained by the organization.  The policy to apply to the element/resource is captured by the retentionBasis
        property.  The dates after which the element/resource is archived and then deleted are specified in the archiveAfter and deleteAfter
        properties respectively. Async version

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "RetentionClassificationProperties",
               "retentionBasis" : 0,
               "status" : 0,
               "confidence" : 0,
               "associatedGUID" : "Add value here",
               "archiveAfter" : "{{$isoTimestamp}}",
               "deleteAfter" : "{{$isoTimestamp}}",
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_retention_classification(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_retention_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the retention classification from the element.  This normally occurs when the organization has lost
        track of the level of retention to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/retention/remove"
            f"{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_retention_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the retention classification from the element.  This normally occurs when the organization has lost
        track of the level of retention to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


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


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_retention_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_security_tags_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the security tags for an element. Async version,

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "SecurityTagsProperties",
               "securityLabels" : [ "Label1", "Label2" ],
               "securityProperties" : {
                   "propertyName1" : "add property value here",
                   "propertyName2" : "add property value here"
               },
               "accessGroups" : {
                   "groupName1" : [ "operation1", "operation2" ],
                   "groupName2" : [ "operation1", "operation3" ]
               }
           }
        }


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/security-tags"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_security_tags_classification(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the security tags for an element. Async versuib,

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


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

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "SecurityTagsProperties",
               "securityLabels" : [ "Label1", "Label2" ],
               "securityProperties" : {
                   "propertyName1" : "add property value here",
                   "propertyName2" : "add property value here"
               },
               "accessGroups" : {
                   "groupName1" : [ "operation1", "operation2" ],
                   "groupName2" : [ "operation1", "operation3" ]
               }
           }
        }


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_security_tags_classification(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_security_tags_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the security-tags classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

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

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/security-tags/remove"
            f"{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_security_tags_classification(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the security-tags classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

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
        loop.run_until_complete(
            self._async_clear_security_tags_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_setup_semantic_assignment(
        self,
        glossary_term_guid: str,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Create a semantic assignment relationship between a glossary term and an element (normally a schema attribute,
        data field or asset). This relationship indicates that the data associated with the element meaning matches
        the description in the glossary term. Async version

        Semantic Assignments: https://egeria-project.org/types/3/0370-Semantic-Assignment/

        Parameters
        ----------
        glossary_term_guid: str
            - identity of glossary to assign
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note:

        A sample dict structure is:

        {
          "class" : "RelationshipRequestBody",
          "effectiveTime" : "an isoTimestamp",
          "relationshipProperties" : {
            "class": "SemanticAssignmentProperties",
            "expression" : "add value here",
            "description" : "add value here",
            "status" : "VALIDATED",
            "confidence" : 100,
            "createdBy" : "add value here",
            "steward" : "add value here",
            "source" : "add value here"
          }
        }


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/semantic-assignment/terms"
            f"/{glossary_term_guid}{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def setup_semantic_assignment(
        self,
        glossary_term_guid: str,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Create a semantic assignment relationship between a glossary term and an element (normally a schema attribute,
        data field or asset). This relationship indicates that the data associated with the element meaning matches
        the description in the glossary term.

        Semantic Assignments: https://egeria-project.org/types/3/0370-Semantic-Assignment/

        Parameters
        ----------
        glossary_term_guid: str
            - identity of glossary to assign
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note:

        A sample dict structure is:

        {
          "class" : "RelationshipRequestBody",
          "effectiveTime" : "an isoTimestamp",
          "relationshipProperties" : {
            "class": "SemanticAssignmentProperties",
            "expression" : "add value here",
            "description" : "add value here",
            "status" : "VALIDATED",
            "confidence" : 100,
            "createdBy" : "add value here",
            "steward" : "add value here",
            "source" : "add value here"
          }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_semantic_assignment(
                glossary_term_guid,
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_semantic_assignment_classification(
        self,
        glossary_term_guid: str,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the semantic_assignment classification from the element. Async version.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        glossary_term_guid: str
           - identity of glossary to remove
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

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

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/semantic-assignment/terms/"
            f"{glossary_term_guid}/remove{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_semantic_assignment_classification(
        self,
        glossary_term_guid: str,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the semantic_assignment classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        glossary_term_guid: str
           - identity of glossary to remove
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

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
        loop.run_until_complete(
            self._async_clear_semantic_assignment_classification(
                glossary_term_guid,
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_add_element_to_subject_area(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify the element to assert that the definitions it represents are part of a subject area definition. Async

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "SubjectAreaMemberProperties",
               "subjectAreaName" : "Add value here"
           }
        }


        """

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
            ]
        )

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/subject-area-member"
            f"{possible_query_params}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_element_to_subject_area(
        self,
        element_guid: str,
        body: dict,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Classify the element to assert that the definitions it represents are part of a subject area definition. Async

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Note:

        A sample dict structure is:

        {
           "class" : "ClassificationRequestBody",
           "effectiveTime" : "an isoTimestamp",
           "properties" : {
               "class" : "SubjectAreaMemberProperties",
               "subjectAreaName" : "Add value here"
           }
        }


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_element_to_subject_area(
                element_guid,
                body,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_remove_element_from_subject_area(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the subject area designation from the identified element. Async version.

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

         Parameters
         ----------
         element_guid: str
             - the identity of the element to update
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
            None

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

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/subject-area-member"
            f"/remove{possible_query_params}"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def remove_element_from_subject_area(
        self,
        element_guid: str,
        for_lineage: bool = None,
        for_duplicate_processing: bool = None,
        effective_time: str = None,
        time_out: int = default_time_out,
    ) -> None:
        """
        Remove the subject area designation from the identified element.

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

         Parameters
         ----------
         element_guid: str
             - the identity of the element to update
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
            None

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
        loop.run_until_complete(
            self._async_remove_element_from_subject_area(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )


if __name__ == "__main__":
    print("Main-Classification Manager")

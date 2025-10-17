"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is a simple class to create and manage a connection to an Egeria backend. It is the Superclass for the
different client capabilities. It also provides the common methods used to make restful self.session to Egeria.

"""

import asyncio
import os
import re
import time
from collections.abc import Callable
from typing import Any

from httpx import Response
# from venv import logger
from loguru import logger
from pydantic import TypeAdapter

from pyegeria._base_client import BaseClient
from pyegeria._exceptions_new import (
    PyegeriaConnectionException, PyegeriaInvalidParameterException
)
from pyegeria._globals import max_paging_size, NO_ELEMENTS_FOUND, default_time_out
from pyegeria._output_formats import get_output_format_type_match
from pyegeria._output_formats import select_output_format_set
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, UpdateStatusRequestBody, UpdateElementRequestBody,
                             NewRelationshipRequestBody,
                             DeleteRequestBody, UpdateRelationshipRequestBody, ResultsRequestBody,
                             NewClassificationRequestBody,
                             DeleteElementRequestBody, DeleteRelationshipRequestBody, DeleteClassificationRequestBody,
                             LevelIdentifierQueryBody)
from pyegeria.output_formatter import populate_common_columns, resolve_output_formats, generate_output
from pyegeria.utils import body_slimmer, dynamic_catch

...


class Client2(BaseClient):
    """
    An abstract class used to establish connectivity for an Egeria Client
    for a particular server, platform and user.

    Attributes
    ----------
        server_name : str (required)
            Name of the OMAG server to use
        platform_url : str (required)
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd : str
            The password used to authenticate the server identity

    Methods
    -------
        create_egeria_bearer_token(user_Id: str, password: str = None) -> str
           Create a bearer token using the simple Egeria token service - store the bearer token in the object instance.

        refresh_egeria_bearer_token()-> None
            Refresh the bearer token using the attributes of the object instance.

        set_bearer_token(token: str) -> None
            Set the bearer token attribute in the object instance - used when the token is generated
            by an external service.

        get_token() -> str
            Retrieve the bearer token.

        make_request(request_type: str, endpoint: str, payload: str | dict = None,
                    time_out: int = 30) -> Response
            Make an HTTP Restful request and handle potential errors and exceptions.

    """

    json_header = {"Content-Type": "application/json"}

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str = None,
            user_pwd: str = None,
            token: str = None,
            token_src: str = None,
            api_key: str = None,
            page_size: int = max_paging_size,
    ):
        # self.server_name = validate_server_name(server_name)
        # self.platform_url = validate_url(platform_url)
        # self.user_id = user_id
        # self.user_pwd = user_pwd
        # self.page_size = page_size
        # self.token_src = token_src
        # self.token = token
        # self.exc_type = None
        # self.exc_value = None
        # self.exc_tb = None
        # self.url_marker = "MetadataExpert"

        #
        #           I'm commenting this out since you should only have to use tokens if you want - just have to
        #           create or set the token with the appropriate methods as desired.
        # if token is None:
        #     token = os.environ.get("Egeria_Bearer_Token", None)
        #     if token is None: # No token found - so make one
        #         self.create_egeria_bearer_token(self.user_id, self.user_pwd)
        #     else:
        #         self.token = token

        # if api_key is None:
        #     api_key = os.environ.get("API_KEY", None)
        # self.api_key = api_key
        #
        # self.headers = {
        #     "Content-Type": "application/json",
        # }
        # self.text_headers = {
        #     "Content-Type": "text/plain",
        # }
        # if self.api_key is not None:
        #     self.headers["X-Api-Key"] = self.api_key
        #     self.text_headers["X-Api-Key"] = self.api_key
        #
        # if token is not None:
        #     self.headers["Authorization"] = f"Bearer {token}"
        #     self.text_headers["Authorization"] = f"Bearer {token}"
        #
        # v_url = validate_url(platform_url)
        #
        # if v_url:
        #     self.platform_url = platform_url
        #     if validate_server_name(server_name):
        #         self.server_name = server_name
        #     self.session = AsyncClient(verify=enable_ssl_check)

        super().__init__(server_name, platform_url, user_id, user_pwd, token, 
                         token_src, api_key, page_size)

        self.command_root: str = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/"
        self._search_string_request_adapter = TypeAdapter(SearchStringRequestBody)
        self._filter_request_adapter = TypeAdapter(FilterRequestBody)
        self._get_request_adapter = TypeAdapter(GetRequestBody)
        self._new_element_request_adapter = TypeAdapter(NewElementRequestBody)
        self._update_element_request_adapter = TypeAdapter(UpdateElementRequestBody)
        self._update_status_request_adapter = TypeAdapter(UpdateStatusRequestBody)
        self._new_relationship_request_adapter = TypeAdapter(NewRelationshipRequestBody)
        self._new_classification_request_adapter = TypeAdapter(NewClassificationRequestBody)
        self._delete_request_adapter = TypeAdapter(DeleteRequestBody)
        self._delete_element_request_adapter = TypeAdapter(DeleteElementRequestBody)
        self._delete_relationship_request_adapter = TypeAdapter(DeleteRelationshipRequestBody)
        self._delete_classification_request_adapter = TypeAdapter(DeleteClassificationRequestBody)
        self._template_request_adapter = TypeAdapter(TemplateRequestBody)
        self._update_relationship_request_adapter = TypeAdapter(UpdateRelationshipRequestBody)
        self._results_request_adapter = TypeAdapter(ResultsRequestBody)
        self._level_identifier_query_body = TypeAdapter(LevelIdentifierQueryBody)

        try:
            result = self.check_connection()
            logger.debug(f"client initialized, platform origin is: {result}")
        except PyegeriaConnectionException as e:
            raise

    # @logger.catch
    async def __async_get_guid__(
            self,
            guid: str = None,
            display_name: str = None,
            property_name: str = "qualifiedName",
            qualified_name: str = None,
            tech_type: str = None,
    ) -> str:
        """Helper function to return a server_guid - one of server_guid, qualified_name or display_name should
        contain information. If all are None, an exception will be thrown. If all contain
        values, server_guid will be used first, followed by qualified_name.  If the tech_type is supplied and the
        property_name is qualifiedName then the display_name will be pre-pended with the tech_type name to form a
        qualifiedName.

        An InvalidParameter Exception is thrown if multiple matches
        are found for the given property name. If this occurs, use a qualified name for the property name.
        Async version.
        """

        if guid:
            return guid

        if qualified_name:
            body = {
                "class": "NameRequestBody",
                "name": qualified_name,
                "namePropertyName": "qualifiedName",
                "forLineage": False,
                "forDuplicateProcessing": False,
                "effectiveTime": None,
            }
            url = (
                f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/classification-manager/"
                f"elements/guid-by-unique-name"
            )

            result = await self._async_make_request("POST", url, body_slimmer(body))
            return result.json().get("guid", NO_ELEMENTS_FOUND)

        try:
            view_server = self.view_server
        except AttributeError:
            view_server = os.environ.get("EGERIA_VIEW_SERVER", "view-server")

        if (not qualified_name) and display_name:
            if (tech_type) and (property_name == "qualifiedName"):
                name = f"{tech_type}::{display_name}"
                body = {
                    "class": "NameRequestBody",
                    "displayName": name,
                    "namePropertyName": property_name,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "effectiveTime": None,
                }
                url = (
                    f"{self.platform_url}/servers/{view_server}/api/open-metadata/classification-manager/"
                    f"elements/guid-by-unique-name?forLineage=false&forDuplicateProcessing=false"
                )

                result = await self._async_make_request("POST", url, body_slimmer(body))
                return result.json().get("guid", NO_ELEMENTS_FOUND)
            else:
                body = {
                    "class": "NameRequestBody",
                    "name": display_name,
                    "namePropertyName": property_name,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "effectiveTime": None,
                }
                url = (
                    f"{self.platform_url}/servers/{view_server}/api/open-metadata/classification-manager/"
                    f"elements/guid-by-unique-name?forLineage=false&forDuplicateProcessing=false"
                )

                result = await self._async_make_request("POST", url, body_slimmer(body))
                return result.json().get("guid", NO_ELEMENTS_FOUND)
        else:
            additional_info = {
                "reason": "Neither server_guid nor server_name were provided - please provide.",
                "parameters": (f"GUID={guid}, display_name={display_name}, property_name={property_name},"
                               f"qualified_name={qualified_name}, tech_type={tech_type}")
            }
            raise PyegeriaInvalidParameterException(None, None, additional_info)
    #
    # Include basic functions for finding elements and relationships.
    #

    def __get_guid__(
            self,
            guid: str = None,
            display_name: str = None,
            property_name: str = "qualifiedName",
            qualified_name: str = None,
            tech_type: str = None,
    ) -> str:
        """Helper function to return a server_guid - one of server_guid, qualified_name or display_name should
        contain information. If all are None, an exception will be thrown. If all contain
        values, server_guid will be used first, followed by qualified_name.  If the tech_type is supplied and the
        property_name is qualifiedName then the display_name will be pre-pended with the tech_type name to form a
        qualifiedName.

        An InvalidParameter Exception is thrown if multiple matches
        are found for the given property name. If this occurs, use a qualified name for the property name.
        Async version.
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.__async_get_guid__(
                guid, display_name, property_name, qualified_name, tech_type
            )
        )
        return result


    def __create_qualified_name__(self, type: str, display_name: str, local_qualifier: str = None,
                                  version_identifier: str = None) -> str:
        """Helper function to create a qualified name for a given type and display name.
           If present, the local qualifier will be prepended to the qualified name."""
        EGERIA_LOCAL_QUALIFIER = os.environ.get("EGERIA_LOCAL_QUALIFIER", local_qualifier)
        display_name = re.sub(r'\s', '-', display_name.strip())  # This changes spaces between words to -; removing
        if display_name is None:
            additional_info = {"reason": "Display name is missing - please provide.", }
            raise PyegeriaInvalidParameterException(additional_info=additional_info)
        q_name = f"{type}::{display_name}"
        if EGERIA_LOCAL_QUALIFIER:
            q_name = f"{EGERIA_LOCAL_QUALIFIER}::{q_name}"
        if version_identifier:
            q_name = f"{q_name}::{version_identifier}"
        return q_name

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



        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataType": relationship_type,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
        }

        url = (
            f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/classification-manager/relationships/"
            f"with-exact-property-value"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rels = response.json().get("relationships", NO_ELEMENTS_FOUND)
        if type(rels) is list:
            if len(rels) == 0:
                return NO_ELEMENTS_FOUND
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


    async def async_get_elements_by_property_value(
            self,
            property_value: str,
            property_names: [str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
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
        metadata_element_type_name : str, default = None
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
        PyegeriaException
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "startFrom": start_from,
            "pageSize": page_size,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing
        }

        url = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/classification-explorer/elements/by-exact-property-value"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

    def get_elements_by_property_value(
            self,
            property_value: str,
            property_names: [str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            output_format_set: dict | str = None,
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
        metadata_element_type_name : str, default = None
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
        output_format: str, default = "JSON"
            - Type of output to return.
        output_format_set: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_get_elements_by_property_value(
                property_value,
                property_names,
                metadata_element_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
            )
        )
        return response

    async def async_get_guid_for_name(
            self, name: str, property_name: [str] = ["qualifiedName","displayName"], type_name: str = "ValidMetadataValue"

    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: [str], default = ["qualifiedName","displayName"]
            - propertys to search in.
        type_name: str, default = "ValidMetadataValue"
            - metadata element type name to be used to restrict the search
        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
        """

        elements = await self.async_get_elements_by_property_value(
            name, property_name, type_name
        )

        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
            elif len(elements) > 1:
                raise Exception("Multiple elements found for supplied name!")
            elif len(elements) == 1:
                return elements[0]["elementHeader"]["guid"]
        return elements

    def get_guid_for_name(
            self, name: str, property_name: [str] = ["qualifiedName","displayName"], type_name: str = "ValidMetadataValue"
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: [str], default = ["qualifiedName","displayName"]
            - propertys to search in.
        type_name: str, default = "ValidMetadataValue"
            - metadata element type name to be used to restrict the search
        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaExeception
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_get_guid_for_name(name, property_name, type_name)
        )
        return response


    async def async_get_element_by_guid_(self, element_guid: str) -> dict | str:
        """
            Simplified, internal version of get_element_by_guid found in Classification Manager.
            Retrieve an element by its guid.  Async version.

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element

        Returns
        -------
        dict | str
            Returns a string if no element found; otherwise a dict of the element.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": None,
        }

        url = (f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/classification-manager/elements/"
               f"{element_guid}?forLineage=false&forDuplicateProcessing=false")

        response: Response = await self._async_make_request("POST", url, body_slimmer(body))

        elements = response.json().get("element", NO_ELEMENTS_FOUND)

        return elements

    async def async_get_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: [str],
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
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
        metadata_element_type_name : str, default = None
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
        PyegeriaException
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = (
             f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/classification-explorer/elements/{element_guid}"
             f"/by-relationship/{relationship_type}/with-exact-property-value?startAtEnd={start_at_end}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        return elements

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

    async def async_get_connector_guid(self, connector_name: str) -> str:
        """Get the guid of a connector. Async version.
            Parameters:
                connector_name (str): The name of the connector to retrieve the guid for.
            Returns:
                str: The guid of the connector.
        """
        rel = await self._async_get_relationships_with_property_value(relationship_type="RegisteredIntegrationConnector",
                                                             property_names=["connectorName"],
                                                             property_value=connector_name,
                                                             )
        if rel == "No elements found":
            logger.error(f"\n\n===> No connector found with name '{connector_name}'\n\n")
            return "No connector found"
        connector_guid = rel[0]['end2']['guid']

        if connector_guid is None:
            logger.error(f"\n\n===> No connector found with name '{connector_name}'\n\n")
            return "No connector found"

        return connector_guid


    def get_connector_guid(self, connector_name: str) -> str:
        """Get the guid of a connector.
            Parameters:
                connector_name (str): The name of the connector to retrieve the guid for.
            Returns:
                str: The guid of the connector.
        """

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.async_get_connector_guid(
                connector_name
            )
        )
        return result


    #
    #   Common feedback commands
    #
    

    def make_feedback_qn(self, feedback_type, src_guid) -> str:
        timestamp = int(time.time())
        return f"{feedback_type}::{src_guid}::{self.user_id}::{timestamp}"

    async def async_add_comment_reply(
        self,
        element_guid: str,
        comment_guid: str,
        comment: str,
        comment_type: str = "STANDARD_COMMENT",
        body: dict = None,
    ) -> str:
        """
        Adds a reply to a comment. Async Version

        Parameters
        ----------
        element_guid
            - String - unique id for the anchor element.
        comment_guid
            - String - unique id for an existing comment. Used to add a reply to a comment.
        comment
            - String - the text of the comment.
        comment_type
            - String - the type of comment, default is STANDARD_COMMENT.
        body
            - containing type of comment enum and the text of the comment.  Body overrides other parameters if present.

        Returns
        -------
        ElementGUID

        Raises
        ------
        PyEgeriaException

        """
        if body is None:
            body = {
                "class": "NewFeedbackRequestBody",
                "properties": {
                    "class": "CommentProperties",
                    "qualifiedName": self.make_feedback_qn("Reply", comment_guid),
                    "desription": comment,
                    "commentType": comment_type
                }
            }
        url = f"{self.command_root}feedback-manager/{element_guid}/comments/{comment_guid}/replies"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_comment_reply(
        self,
        element_guid: str,
        comment_guid: str,
        comment: str,
        comment_type: str = "STANDARD_COMMENT",
        body: dict = None,

    ) -> str:
        """
        Adds a reply to a comment.

        Parameters
        ----------
        element_guid
            - String - unique id for the anchor element.
        comment_guid
            - String - unique id for an existing comment. Used to add a reply to a comment.
        comment
            - String - the text of the comment.
        comment_type
            - String - the type of comment, default is STANDARD_COMMENT.
        body
            - containing type of comment enum and the text of the comment. Body overrides other parameters if present.

        Returns
        -------
        ElementGUID

        Raises
        ------
        PyEgeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_add_comment_reply(element_guid, comment_guid, comment, comment_type, body)
        )
        return response


    async def async_add_comment_to_element(
        self,
        element_guid: str,
        comment: str=None,
        comment_type: str = "STANDARD_COMMENT",
        body: dict = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------

        element_guid: str
            - unique id for the element.
        comment: str
            - The text of the comment.

        comment_type: str
            - the type of comment, default is STANDARD_COMMENT.
        body
            - containing type of comment enum and the text of the comment. Body overrides other parameters if present.
        Returns
        -------
        ElementGUID

        Raises
        ------
        PyEgeriaException

        """
        if body is None:
            body = {
                "class": "NewFeedbackRequestBody",
                "properties": {
                    "class": "CommentProperties",
                    "qualifiedName": self.make_feedback_qn("Comment", element_guid),
                    "description": comment,
                    "commentType": comment_type
                }
            }
        url = f"{self.command_root}feedback-manager/elements/{element_guid}/comments"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "NO_GUID_RETURNED")


    def add_comment_to_element(
        self,
        element_guid: str,
        comment: str = None,
        comment_type: str = "STANDARD_COMMENT",
        body: dict = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        comment: str
            - The text of the comment.
        comment_type
            - String - the type of comment, default is STANDARD_COMMENT.
        body
            - containing type of comment enum and the text of the comment. Body overrides other parameters if present.

        Returns
        -------
        ElementGUID

        Raises
        ------
        PyEgeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_add_comment_to_element(element_guid, comment, comment_type, body)
        )
        return response


    async def async_update_comment(
        self,
        comment_guid: str,
        comment: str=None,
        comment_type: str = "STANDARD_COMMENT",
        body: dict | UpdateElementRequestBody= None,
        merge_update: bool = True,
    ) -> None:
        """
        Updates a comment.

        Parameters
        ----------

        comment_guid: str
            - unique id for the comment.
        comment: str
            - The text of the comment.

        comment_type: str
            - the type of comment, default is STANDARD_COMMENT.
        body: dict | UpdateElementRequestBody
            - containing type of comment enum and the text of the comment. Body overrides other parameters if present.
        merge_update: bool
        - Whether to merge the updated attributes or replace them.

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException

        """
        if body is None:
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": {
                    "class": "CommentProperties",
                    "description": comment,
                    "commentType": comment_type
                }
            }
        url = f"{self.command_root}feedback-manager/comments{comment_guid}/update"
        response = await self._async_update_element_body_request(body, url, ["Comment"])
        return response


    def update_comment(
        self,
        element_guid: str,
        comment: str = None,
        comment_type: str = "STANDARD_COMMENT",
        body: dict | UpdateElementRequestBody = None,
        merge_update: bool = True,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------

        comment_guid
            - String - unique id for the comment.
        comment: str
            - The text of the comment.
        comment_type
            - String - the type of comment, default is STANDARD_COMMENT.
        body
            - containing type of comment enum and the text of the comment. Body overrides other parameters if present.
        merge_update: bool
            - Whether to merge the updated attributes or replace them.
        Returns
        -------
        ElementGUID

        Raises
        ------
        PyEgeriaException

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_update_comment(element_guid, comment, comment_type, body, merge_update)
        )
        return response


    async def async_setup_accepted_answer(
        self,
        question_comment_guid: str,
        answer_comment_guid: str,

    ) -> None:
        """
        Link a comment that contains the best answer to a question posed in another comment. Async version.

        Parameters
        ----------

        question_comment_guid: str
            - unique id for the question comment.
        answer_comment_guid: str
            - unique id for the answer comment.

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException

        """

        url = f"{self.command_root}feedback-manager/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}"
        await self._async_make_request( "POST",url)


    def setup_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,

    ) -> None:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------

        question_comment_guid: str
            - unique id for the question comment.
        answer_comment_guid: str
            - unique id for the answer comment.

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.async_setup_accepted_answer(question_comment_guid, answer_comment_guid)
        )

    async def async_clear_accepted_answer(
        self,
        question_comment_guid: str,
        answer_comment_guid: str,

    ) -> None:
        """
        Link a comment that contains the best answer to a question posed in another comment. Async version.

        Parameters
        ----------

        question_comment_guid: str
            - unique id for the question comment.
        answer_comment_guid: str
            - unique id for the answer comment.

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException

        """

        url = f"{self.command_root}feedback-manager/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}/remove"
        await self._async_make_request( "POST",url)


    def setup_clear_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,

    ) -> None:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------

        question_comment_guid: str
            - unique id for the question comment.
        answer_comment_guid: str
            - unique id for the answer comment.

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.async_clear_accepted_answer(question_comment_guid, answer_comment_guid)
        )

    async def async_remove_comment_from_element(
        self,
        element_guid:str,
        comment_guid: str,
        body: dict | DeleteRequestBody = None,
        cascade_delete: bool = False,
    ) -> None:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        comment_guid
            - String - unique id for the comment object
        server_name
            - name of the server instances for this request

        body
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        VoidResponse

        Raises
        ------
        PyegeriaException

        Args:
            cascade_delete ():
        """

        url = f"{self.command_root}feedback-manager/elements/{element_guid}/comments/{comment_guid}/remove"
        await self._async_delete_element_request(url,body,cascade_delete)


    def remove_comment_from_element(
        self,
        element_guid: str,
        comment_guid: str,
        body: dict | DeleteRequestBody = None,
        cascade_delete: bool = False,

    ) -> None:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        comment_guid
            - String - unique id for the comment object
        body
            - containing type of comment enum and the text of the comment.
        cascade_delete: bool = False


        Returns
        -------
        VoidResponse

        Raises
        ------
        PyEgeriaException
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.async_remove_comment_from_element(element_guid,comment_guid, body,cascade_delete=cascade_delete)
        )




    async def async_get_comment_by_guid(
        self,
        comment_guid: str, element_type: str = "Comment",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        output_format_set: str | dict = None
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        comment_guid
            - unique identifier for the comment object.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
            - optional effective time

        Returns
        -------
        comment properties

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            output_format_set ():
        """


        url = f"{self.command_root}feedback-manager/comments/{comment_guid}/comments/retrieve"
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_comment_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    def get_comment_by_guid(
        self,
        comment_guid: str, element_type: str = "Comment",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        output_format_set: str | dict = None
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        comment_guid
            - unique identifier for the comment object.
        server_name
            - name of the server instances for this request
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
            - optional effective time

        Returns
        -------
        comment properties

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            output_format_set ():
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_get_comment_by_guid(comment_guid, element_type,body,output_format, output_format_set)
        )
        return response

    async def async_get_attached_comments(
            self,
            element_guid: str,
            element_type: str = "Comment",
            body: dict = {},
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            output_format_set: str | dict = None

    ) -> dict | str:
        """
        Return the comments attached to an element.

        Parameters
        ----------
        element_guid
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.


        Returns
        -------
        list of comments

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/elements/{element_guid}/comments/retrieve"
        response = await self._async_make_request("POST", url, body)
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self._generate_comment_output(element, None, output_format, output_format_set)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_attached_comments(
            self, element_guid: str,
            element_type: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            output_format_set: str | dict = None
    ) -> dict | str:
        """
        Return the comments attached to an element.

        Parameters
        ----------
        element_guid
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of comments

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            output_format_set ():
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_get_attached_comments(element_guid, element_type, body, start_from, page_size, output_format,
                                             output_format_set)
        )
        return response

    def _extract_comment_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Common population pipeline
        col_data = populate_common_columns(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])
        # Overlay extras (project roles) only where empty
        # extra = self._extract_additional_project_properties(element, columns_struct)
        # col_data = overlay_additional_values(col_data, extra)
        return col_data



    async def async_find_comments(
        self,
        search_string: str,
        classification_names: list[str] = None,
        metadata_element_types: list[str] = ["Comment"],
        starts_with: bool = None,
        ends_with: bool = None,
        ignore_case: bool = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        output_format_set: str | dict = None,
        body: dict | SearchStringRequestBody = None
    ) -> dict | str:

        """
        Return the list of comments containing the supplied string. Async Version.

        Parameters
        ----------
        search_string
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format
            - output format for the response
        output_format_set
            - output format set for the response
        body
            - body of the request. Details of the body overrides other parameters if present.

        Returns
        -------
        list of comment objects

        Raises
        ------
        PyegeriaException

        Args:
            classification_names ():
            metadata_element_types ():


        """

        url = f"{self.command_root}feedback-manager/comments/by-search-string"
        response = await self._async_find_request(url, _type="Comment",
                                                  _gen_output=self._generate_comment_output,
                                                  search_string=search_string,
                                                  classification_names=classification_names,
                                                  metadata_element_types=metadata_element_types,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response

    def find_comments(
            self,
            search_string: str,
            classification_names: list[str] = None, metadata_element_types: list[str]=["Comment"],
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = max_paging_size,
            output_format: str = "JSON", output_format_set: str | dict = None,
            body: dict | SearchStringRequestBody = None
    ) -> dict | str:
        """
        Return the list of comments containing the supplied string. Async Version.

        Parameters
        ----------
        search_string
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format
            - output format for the response
        output_format_set
            - output format set for the response
        body
            - body of the request. Details of the body overrides other parameters if present.

        Returns
        -------
        list of comment objects

        Raises
        ------
        PyegeriaException

        Args:
            classification_names ():
            metadata_element_types ():


        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self.async_find_comments(
                search_string,
                classification_names,
                metadata_element_types,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                output_format_set,
                body,
            )
        )

        return resp




    def _generate_comment_output(self, elements: dict | list[dict], search_string: str,
                                 element_type_name: str | None,
                                 output_format: str = 'DICT',
                                 output_format_set: dict | str = None) -> str | list[dict]:
        entity_type = 'Comment'
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_comment_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )
    #
    # Helper functions for requests
    #


    def validate_new_element_request(self, body: dict | NewElementRequestBody,
                                     prop: list[str]) -> NewElementRequestBody | None:
        if isinstance(body, NewElementRequestBody):
            # if body.properties.class_ in prop:
            validated_body = body
            # else:
            #     raise PyegeriaInvalidParameterException(additional_info=
            #                                             {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            # if body.get("properties", {}).get("class", "") == prop:
            validated_body = self._new_element_request_adapter.validate_python(body)
            # else:
            #     raise PyegeriaInvalidParameterException(additional_info=
            #                                             {"reason": "unexpected property class name"})
        else:
            return None
        return validated_body

    def validate_new_element_from_template_request(self, body: dict | TemplateRequestBody
                                                   ) -> NewElementRequestBody | None:
        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            # if body.get("properties", {}).get("class", "") == prop:
            validated_body = self._template_request_adapter.validate_python(body)
        else:
            return None
        return validated_body

    def validate_new_relationship_request(self, body: dict | NewRelationshipRequestBody,
                                          prop: str = None) -> NewRelationshipRequestBody | None:
        if isinstance(body, NewRelationshipRequestBody):
            if (prop and body.properties.class_ == prop) or (prop is None):
                validated_body = body
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            if body.get("properties", {}).get("class", "") == prop:
                validated_body = self._new_relationship_request_adapter.validate_python(body)
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})
        else:
            return None

        return validated_body

    def validate_new_classification_request(self, body: dict | NewClassificationRequestBody,
                                            prop: str = None) -> NewClassificationRequestBody | None:
        if isinstance(body, NewClassificationRequestBody):
            if (prop and body.properties.class_ == prop) or (prop is None):
                validated_body = body
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            if body.get("properties", {}).get("class", "") == prop:
                validated_body = self._new_classification_request_adapter.validate_python(body)
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})
        else:
            return None

        return validated_body

    def validate_delete_request(self, body: dict | DeleteRequestBody,
                                cascade_delete: bool = False) -> DeleteRequestBody | None:
        if isinstance(body, DeleteRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._delete_request_adapter.validate_python(body)
        else:  # handle case where body not provided
            body = {
                "class": "DeleteRequestBody",
                "cascadeDelete": cascade_delete
            }
            validated_body = DeleteRequestBody.model_validate(body)
        return validated_body
    def validate_delete_element_request(self, body: dict | DeleteElementRequestBody,
                                cascade_delete: bool = False) -> DeleteElementRequestBody | None:
        if isinstance(body, DeleteElementRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._delete_element_request_adapter.validate_python(body)
        else:  # handle case where body not provided
            body = {
                "class": "DeleteElementRequestBody",
                "cascadeDelete": cascade_delete
            }
            validated_body = DeleteElementRequestBody.model_validate(body)
        return validated_body

    def validate_delete_relationship_request(self, body: dict | DeleteRelationshipRequestBody,
                                cascade_delete: bool = False) -> DeleteRelationshipRequestBody | None:
        if isinstance(body, DeleteRelationshipRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._delete_relationship_request_adapter.validate_python(body)
        else:  # handle case where body not provided
            body = {
                "class": "DeleteRelationshipRequestBody",
                "cascadeDelete": cascade_delete
            }
            validated_body = DeleteRelationshipRequestBody.model_validate(body)
        return validated_body

    def validate_delete_classification_request(self, body: dict | DeleteClassificationRequestBody,
                                cascade_delete: bool = False) -> DeleteClassificationRequestBody | None:
        if isinstance(body, DeleteClassificationRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._delete_classification_request_adapter.validate_python(body)
        else:  # handle case where body not provided
            body = {
                "class": "DeleteClassificationRequestBody",
                "cascadeDelete": cascade_delete
            }
            validated_body = DeleteClassificationRequestBody.model_validate(body)
        return validated_body


    def validate_update_element_request(self, body: dict | UpdateElementRequestBody,
                                        prop: list[str]) -> UpdateElementRequestBody | None:
        if isinstance(body, UpdateElementRequestBody):
            if body.properties.class_ in prop:
                validated_body = body
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            # if body.get("properties", {}).get("class", "") in prop:
            validated_body = self._update_element_request_adapter.validate_python(body)
            # else:
            #     raise PyegeriaInvalidParameterException(additional_info=
            #                                             {"reason": "unexpected property class name"})
        else:
            validated_body = None
        return validated_body

    def validate_update_status_request(self, status: str = None, body: dict | UpdateStatusRequestBody = None,
                                       prop: list[str] = None) -> UpdateStatusRequestBody | None:
        if isinstance(body, UpdateStatusRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._update_element_request_adapter.validate_python(body)

        elif status:
            body = {
                "class": "UpdateStatusRequestBody",
                "newStatus": status
            }
            validated_body = UpdateStatusRequestBody.model_validate(body)
        else:
            raise PyegeriaInvalidParameterException(additional_info={"reason": "invalid parameters"})

        return validated_body

    def validate_update_relationship_request(self, body: dict | UpdateRelationshipRequestBody,
                                             prop: [str]) -> UpdateRelationshipRequestBody | None:
        if isinstance(body, UpdateRelationshipRequestBody):
            # if body.properties.class_ == prop:
            validated_body = body
            # else:
            #     raise PyegeriaInvalidParameterException(additional_info=
            #                                             {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            # if body.get("properties", {}).get("class", "") == prop:
            validated_body = self._update_relationship_request_adapter.validate_python(body)
            # else:
            #     raise PyegeriaInvalidParameterException(additional_info=
            #                                             {"reason": "unexpected property class name"})
        else:
            validated_body = None
        return validated_body

    async def _async_find_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                  search_string: str = '*', classification_names: list[str] = None,
                                  metadata_element_types: list[str] = None,
                                  starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                  start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                  output_format_set: str | dict = None,
                                  body: dict | SearchStringRequestBody = None) -> Any:

        if isinstance(body, SearchStringRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._search_string_request_adapter.validate_python(body)
        else:
            search_string = None if search_string == "*" else search_string
            body = {
                "class": "SearchStringRequestBody",
                "search_string": search_string,
                "starts_with": starts_with,
                "ends_with": ends_with,
                "ignore_case": ignore_case,
                "start_from": start_from,
                "page_size": page_size,
                "include_only_classified_elements": classification_names,
                "metadata_element_subtype_names": metadata_element_types,
            }
            validated_body = SearchStringRequestBody.model_validate(body)

        # classification_names = validated_body.include_only_classified_elements
        # element_type_name = classification_names[0] if classification_names else _type

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            # logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return _gen_output(elements, search_string, _type,
                               output_format, output_format_set)
        return elements

    async def _async_get_name_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                      filter_string: str, classification_names: list[str] = None,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      output_format_set: str | dict = None,
                                      body: dict | FilterRequestBody = None) -> Any:

        if isinstance(body, FilterRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._filter_request_adapter.validate_python(body)
        else:
            filter_string = None if filter_string == "*" else filter_string
            classification_names = None if classification_names == [] else classification_names
            body = {
                "class": "FilterRequestBody",
                "filter": filter_string,
                "start_from": start_from,
                "page_size": page_size,
                "include_only_classified_elements": classification_names,
            }
            validated_body = FilterRequestBody.model_validate(body)

        # classification_names = validated_body.include_only_classified_elements
        # element_type_name = classification_names[0] if classification_names else _type

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return _gen_output(elements, filter_string, _type,
                               output_format, output_format_set)
        return elements

    async def _async_get_guid_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                      output_format: str = 'JSON', output_format_set: str | dict = None,
                                      body: dict | GetRequestBody = None) -> Any:

        if isinstance(body, GetRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._get_request_adapter.validate_python(body)
        else:
            body = {
                "class": "GetRequestBody",
                "metadataElementTypeName": _type
            }
            validated_body = GetRequestBody.model_validate(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body)
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return _gen_output(elements, "GUID", _type, output_format, output_format_set)
        return elements

    async def _async_get_results_body_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                              start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                              output_format_set: str | dict = None,
                                              body: dict | ResultsRequestBody = None) -> Any:
        if isinstance(body, ResultsRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._results_request_adapter.validate_python(body)
        else:
            body = {
                "class": "ResultsRequestBody",
                "start_from": start_from,
                "page_size": page_size,
            }
            validated_body = ResultsRequestBody.model_validate(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body)
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return _gen_output(elements, "Members", _type,
                               output_format, output_format_set)
        return elements

    async def _async_get_level_identifier_query_body_request(self, url: str, _gen_output: Callable[..., Any],
                                              output_format: str = 'JSON',
                                              output_format_set: str | dict = None,
                                              body: dict | ResultsRequestBody = None) -> Any:
        if isinstance(body, LevelIdentifierQueryBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._level_identifier_query_body.validate_python(body)
        else:
            return None

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body)
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and output_format_set: {output_format_set}")
            return _gen_output(elements, "", "Referenceable",
                               output_format, output_format_set)
        return elements


    async def _async_create_element_body_request(self, url: str, prop: list[str],
                                                 body: dict | NewElementRequestBody = None) -> str:
        validated_body = self.validate_new_element_request(body, prop)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())
        return response.json().get("guid", "NO_GUID_RETURNED")

    async def _async_create_element_from_template(self, url: str, body: dict | TemplateRequestBody = None) -> str:
        validated_body = self.validate_new_element_from_template_request(body)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(response.json())
        return response.json().get("guid", "NO_GUID_RETURNED")

    async def _async_update_element_body_request(self, url: str, prop: list[str],
                                                 body: dict | UpdateElementRequestBody = None) -> None:
        validated_body = self.validate_update_element_request(body, prop)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())

    async def _async_update_status_request(self, url: str, status: str = None,
                                           body: dict | UpdateStatusRequestBody = None) -> None:
        validated_body = self.validate_update_status_request(status, body)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())

    async def _async_new_relationship_request(self, url: str, prop: list[str],
                                              body: dict | NewRelationshipRequestBody = None) -> None:
        validated_body = self.validate_new_relationship_request(body, prop)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_new_classification_request(self, url: str, prop: str,
                                                body: dict | NewRelationshipRequestBody = None) -> None:
        validated_body = self.validate_new_classification_request(body, prop)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_delete_request(self, url: str, body: dict | DeleteRequestBody = None,
                                    cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_delete_element_request(self, url: str, body: dict | DeleteElementRequestBody = None,
                                            cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_element_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_delete_relationship_request(self, url: str, body: dict | DeleteRelationshipRequestBody = None,
                                      cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_relationshp_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_delete_classification_request(self, url: str, body: dict | DeleteClassificationRequestBody = None,
                                                 cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_classification_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    async def _async_update_relationship_request(self, url: str, prop: str,
                                                 body: dict | UpdateRelationshipRequestBody = None) -> None:
        validated_body = self.validate_update_relationship_request(body, prop)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_update_element_status(self, guid: str, status: str = None,
                                           body: dict | UpdateStatusRequestBody = None) -> None:
        """ Update the status of an element. Async version.

           Parameters
           ----------
           guid: str
               The guid of the element to update.
           status: str, optional
               The new lifecycle status for the element. Ignored, if the body is provided.
           body: dict | UpdateStatusRequestBody, optional
               A structure representing the details of the element status to update. If supplied, these details
               supersede the status parameter provided.

           Returns
           -------
           Nothing

           Raises
           ------
           PyegeriaException
           ValidationError

           Notes
           -----
           JSON Structure looks like:
            {
             "class": "UpdateStatusRequestBody",
             "newStatus": "APPROVED",
             "externalSourceGUID": "add guid here",
             "externalSourceName": "add qualified name here",
             "effectiveTime": "{{$isoTimestamp}}",
             "forLineage": false,
             "forDuplicateProcessing": false
           }
           """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"{self.url_marker}/metadata-elements/{guid}/update-status")
        await self._async_update_status_request(url, status, body)

    @dynamic_catch
    def update_element_status(self, guid: str, status: str = None,
                              body: dict | UpdateStatusRequestBody = None) -> None:
        """ Update the status of an element. Async version.

           Parameters
           ----------
           guid: str
               The guid of the element to update.
           status: str, optional
               The new lifecycle status for the element. Ignored, if the body is provided.
           body: dict | UpdateStatusRequestBody, optional
               A structure representing the details of the element status to update. If supplied, these details
               supersede the status parameter provided.

           Returns
           -------
           Nothing

           Raises
           ------
           PyegeriaException
           ValidationError

           Notes
           -----
           JSON Structure looks like:
            {
             "class": "UpdateStatusRequestBody",
             "newStatus": "APPROVED",
             "externalSourceGUID": "add guid here",
             "externalSourceName": "add qualified name here",
             "effectiveTime": "{{$isoTimestamp}}",
             "forLineage": false,
             "forDuplicateProcessing": false
           }
           """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_element_status(guid, status, body))

    @dynamic_catch
    async def _async_update_element_effectivity(self, guid: str, effectivity_time: str = None, body: dict = None) -> None:
        """ Update the status of an element. Async version.

           Parameters
           ----------
           guid: str
               The guid of the element to update.
           effectivity_time: str, optional
               The new effectivity time for the element.
           body: dict, optional
               A structure representing the details of the effectivity time to update. If supplied, these details
                supersede the effectivity time parameter provided.

           Returns
           -------
           Nothing

           Raises
           ------
           PyegeriaException
           ValidationError

           Notes
           -----
           JSON Structure looks like:
            {
              "class" : "UpdateEffectivityDatesRequestBody",
              "externalSourceGUID" :  "",
              "externalSourceName" : "",
              "effectiveFrom" : "{{$isoTimestamp}}",
              "effectiveTo": "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "effectiveTime" : "{{$isoTimestamp}}"
            }
           """

        url = f"{self.command_root}/metadata-elements/{guid}/update-effectivity"
        if body is None:
            body = {
                "class": "UpdateEffectivityRequestBody",
                "effectiveTime": effectivity_time
            }
        logger.info(body)
        await self._async_make_request("POST", url, body)



    @dynamic_catch
    def update_element_effectivity(self, guid: str, status: str = None,
                              body: dict = None) -> None:
        """ Update the status of an element. Async version.

           Parameters
           ----------
           guid: str
               The guid of the element to update.
           effectivity_time: str, optional
               The new effectivity time for the element.
           body: dict, optional
               A structure representing the details of the effectivity time to update. If supplied, these details
                supersede the effectivity time parameter provided.

           Returns
           -------
           Nothing

           Raises
           ------
           PyegeriaException
           ValidationError

           Notes
           -----
           JSON Structure looks like:
            {
              "class" : "UpdateEffectivityDatesRequestBody",
              "externalSourceGUID" :  "",
              "externalSourceName" : "",
              "effectiveFrom" : "{{$isoTimestamp}}",
              "effectiveTo": "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "effectiveTime" : "{{$isoTimestamp}}"
            }
           """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_element_status(guid, status, body))
    #
    # @dynamic_catch
    # async def _async_classify_element(self, guid: str, status: str = None,
    #                                        body: dict | UpdateStatusRequestBody = None) -> None:
    #     """ Update the status of an element. Async version.
    #
    #        Parameters
    #        ----------
    #        guid: str
    #            The guid of the element to update.
    #        status: str, optional
    #            The new lifecycle status for the element. Ignored, if the body is provided.
    #        body: dict | UpdateStatusRequestBody, optional
    #            A structure representing the details of the element status to update. If supplied, these details
    #            supersede the status parameter provided.
    #
    #        Returns
    #        -------
    #        Nothing
    #
    #        Raises
    #        ------
    #        PyegeriaException
    #        ValidationError
    #
    #        Notes
    #        -----
    #        JSON Structure looks like:
    #         {
    #          "class": "UpdateStatusRequestBody",
    #          "newStatus": "APPROVED",
    #          "externalSourceGUID": "add guid here",
    #          "externalSourceName": "add qualified name here",
    #          "effectiveTime": "{{$isoTimestamp}}",
    #          "forLineage": false,
    #          "forDuplicateProcessing": false
    #        }
    #        """
    #
    #     url = f"{self.command_root}/metadata-elements/{guid}/update-status"
    #     await self._async_update_status_request(url, status, body)
    #
    # @dynamic_catch
    # def classify_element(self, guid: str, status: str = None,
    #                           body: dict | UpdateStatusRequestBody = None) -> None:
    #     """ Update the status of an element. Async version.
    #
    #        Parameters
    #        ----------
    #        guid: str
    #            The guid of the element to update.
    #        status: str, optional
    #            The new lifecycle status for the element. Ignored, if the body is provided.
    #        body: dict | UpdateStatusRequestBody, optional
    #            A structure representing the details of the element status to update. If supplied, these details
    #            supersede the status parameter provided.
    #
    #        Returns
    #        -------
    #        Nothing
    #
    #        Raises
    #        ------
    #        PyegeriaException
    #        ValidationError
    #
    #        Notes
    #        -----
    #        JSON Structure looks like:
    #         {
    #          "class": "UpdateStatusRequestBody",
    #          "newStatus": "APPROVED",
    #          "externalSourceGUID": "add guid here",
    #          "externalSourceName": "add qualified name here",
    #          "effectiveTime": "{{$isoTimestamp}}",
    #          "forLineage": false,
    #          "forDuplicateProcessing": false
    #        }
    #        """
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self._async_update_element_status(guid, status, body))
    #
    # @dynamic_catch
    # async def _async_reclassify_element(self, guid: str, effectivity_time: str = None,
    #                                             body: dict = None) -> None:
    #     """ Update the status of an element. Async version.
    #
    #        Parameters
    #        ----------
    #        guid: str
    #            The guid of the element to update.
    #        effectivity_time: str, optional
    #            The new effectivity time for the element.
    #        body: dict, optional
    #            A structure representing the details of the effectivity time to update. If supplied, these details
    #             supersede the effectivity time parameter provided.
    #
    #        Returns
    #        -------
    #        Nothing
    #
    #        Raises
    #        ------
    #        PyegeriaException
    #        ValidationError
    #
    #        Notes
    #        -----
    #        JSON Structure looks like:
    #         {
    #           "class" : "UpdateEffectivityDatesRequestBody",
    #           "externalSourceGUID" :  "",
    #           "externalSourceName" : "",
    #           "effectiveFrom" : "{{$isoTimestamp}}",
    #           "effectiveTo": "{{$isoTimestamp}}",
    #           "forLineage" : false,
    #           "forDuplicateProcessing" : false,
    #           "effectiveTime" : "{{$isoTimestamp}}"
    #         }
    #        """
    #
    #     url = f"{self.command_root}/metadata-elements/{guid}/update-effectivity"
    #     if body is None:
    #         body = {
    #             "class": "UpdateEffectivityRequestBody",
    #             "effectiveTime": effectivity_time
    #         }
    #     logger.info(body)
    #     await self._async_make_request("POST", url, body)
    #
    # @dynamic_catch
    # def reclassify_element(self, guid: str, status: str = None,
    #                                body: dict = None) -> None:
    #     """ Update the status of an element. Async version.
    #
    #        Parameters
    #        ----------
    #        guid: str
    #            The guid of the element to update.
    #        effectivity_time: str, optional
    #            The new effectivity time for the element.
    #        body: dict, optional
    #            A structure representing the details of the effectivity time to update. If supplied, these details
    #             supersede the effectivity time parameter provided.
    #
    #        Returns
    #        -------
    #        Nothing
    #
    #        Raises
    #        ------
    #        PyegeriaException
    #        ValidationError
    #
    #        Notes
    #        -----
    #        JSON Structure looks like:
    #         {
    #           "class" : "UpdateEffectivityDatesRequestBody",
    #           "externalSourceGUID" :  "",
    #           "externalSourceName" : "",
    #           "effectiveFrom" : "{{$isoTimestamp}}",
    #           "effectiveTo": "{{$isoTimestamp}}",
    #           "forLineage" : false,
    #           "forDuplicateProcessing" : false,
    #           "effectiveTime" : "{{$isoTimestamp}}"
    #         }
    #        """
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(self._async_update_element_status(guid, status, body))
    #
    #     @dynamic_catch
    #     async def _async_declassify_element(self, guid: str, effectivity_time: str = None,
    #                                         body: dict = None) -> None:
    #         """ Update the status of an element. Async version.
    #
    #            Parameters
    #            ----------
    #            guid: str
    #                The guid of the element to update.
    #            effectivity_time: str, optional
    #                The new effectivity time for the element.
    #            body: dict, optional
    #                A structure representing the details of the effectivity time to update. If supplied, these details
    #                 supersede the effectivity time parameter provided.
    #
    #            Returns
    #            -------
    #            Nothing
    #
    #            Raises
    #            ------
    #            PyegeriaException
    #            ValidationError
    #
    #            Notes
    #            -----
    #            JSON Structure looks like:
    #             {
    #               "class" : "UpdateEffectivityDatesRequestBody",
    #               "externalSourceGUID" :  "",
    #               "externalSourceName" : "",
    #               "effectiveFrom" : "{{$isoTimestamp}}",
    #               "effectiveTo": "{{$isoTimestamp}}",
    #               "forLineage" : false,
    #               "forDuplicateProcessing" : false,
    #               "effectiveTime" : "{{$isoTimestamp}}"
    #             }
    #            """
    #
    #         url = f"{self.command_root}/metadata-elements/{guid}/update-effectivity"
    #         if body is None:
    #             body = {
    #                 "class": "UpdateEffectivityRequestBody",
    #                 "effectiveTime": effectivity_time
    #             }
    #         logger.info(body)
    #         await self._async_make_request("POST", url, body)
    #
    #     @dynamic_catch
    #     def declassify_element(self, guid: str, status: str = None,
    #                            body: dict = None) -> None:
    #         """ Update the status of an element. Async version.
    #
    #            Parameters
    #            ----------
    #            guid: str
    #                The guid of the element to update.
    #            effectivity_time: str, optional
    #                The new effectivity time for the element.
    #            body: dict, optional
    #                A structure representing the details of the effectivity time to update. If supplied, these details
    #                 supersede the effectivity time parameter provided.
    #
    #            Returns
    #            -------
    #            Nothing
    #
    #            Raises
    #            ------
    #            PyegeriaException
    #            ValidationError
    #
    #            Notes
    #            -----
    #            JSON Structure looks like:
    #             {
    #               "class" : "UpdateEffectivityDatesRequestBody",
    #               "externalSourceGUID" :  "",
    #               "externalSourceName" : "",
    #               "effectiveFrom" : "{{$isoTimestamp}}",
    #               "effectiveTo": "{{$isoTimestamp}}",
    #               "forLineage" : false,
    #               "forDuplicateProcessing" : false,
    #               "effectiveTime" : "{{$isoTimestamp}}"
    #             }
    #            """
    #         loop = asyncio.get_event_loop()
    #         loop.run_until_complete(self._async_update_element_status(guid, status, body))

    @dynamic_catch
    def _extract_referenceable_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate default Referenceable columns for output using common population pipeline."""
        return populate_common_columns(element, columns_struct)

    @dynamic_catch
    def _generate_referenceable_output(self, elements: dict | list[dict], search_string: str | None,
                                       element_type_name: str | None,
                                       output_format: str = "JSON",
                                       output_format_set: dict | str = None) -> str | list[dict]:
        """Generate formatted output for generic Referenceable elements.

        If output_format is 'JSON', returns elements unchanged. Otherwise, resolves an
        output format set and delegates to generate_output with a standard extractor.
        """
        if output_format == "JSON":
            return elements
        entity_type = element_type_name or "Referenceable"
        output_formats = resolve_output_formats(entity_type, output_format, output_format_set, default_label=entity_type)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

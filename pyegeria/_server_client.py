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
from datetime import datetime
from typing import Any

from httpx import Response
from loguru import logger
from pydantic import TypeAdapter

from pyegeria._base_server_client import BaseServerClient
from pyegeria._exceptions import (
    PyegeriaConnectionException, PyegeriaInvalidParameterException, PyegeriaException, PyegeriaErrorCode
)
from pyegeria._globals import max_paging_size, NO_ELEMENTS_FOUND, default_time_out, COMMENT_TYPES
from pyegeria.base_report_formats import get_report_spec_match
from pyegeria.base_report_formats import select_report_spec
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, UpdateStatusRequestBody, UpdateElementRequestBody,
                             NewRelationshipRequestBody,
                             UpdateRelationshipRequestBody, ResultsRequestBody,
                             NewClassificationRequestBody,
                             DeleteElementRequestBody, DeleteRelationshipRequestBody, DeleteClassificationRequestBody,
                             LevelIdentifierQueryBody)
from pyegeria.output_formatter import populate_common_columns, resolve_output_formats, generate_output, \
    overlay_additional_values
from pyegeria.utils import body_slimmer, dynamic_catch

...


class ServerClient(BaseServerClient):
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
            raise PyegeriaConnectionException(e)

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
        try:
            view_server = self.server_name
        except AttributeError:
            view_server = os.environ.get("EGERIA_VIEW_SERVER", "view-server")

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
                f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/classification-manager/"
                f"elements/guid-by-unique-name"
            )

            result = await self._async_make_request("POST", url, body_slimmer(body))
            return result.json().get("guid", NO_ELEMENTS_FOUND)

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
                    f"elements/guid-by-unique-name"
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

        if display_name is None:
            additional_info = {"reason": "Display name is missing - please provide.", }
            raise PyegeriaInvalidParameterException(additional_info=additional_info)
        display_name = re.sub(r'\s', '-', display_name.strip())  # This changes spaces between words to -; removing
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
            property_names: list[str],
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
        PyegeriaInvalidParameterException
            One of the parameters is null or invalid (for example, bad URL or invalid values).
        PyegeriaAPIException
            The server reported an error while processing a valid request.
        PyegeriaUnauthorizedException
            The requesting user is not authorized to issue this request.
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataType": relationship_type,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size,
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
            property_names: list[str],
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
        PyegeriaInvalidParameterException
            One of the parameters is null or invalid (for example, bad URL or invalid values).
        PyegeriaAPIException
            The server reported an error while processing a valid request.
        PyegeriaUnauthorizedException
            The requesting user is not authorized to issue this request.
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

    async def _async_get_elements_by_property_value(
            self,
            property_value: str,
            property_names: list[str],
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
            property_names: list[str],
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
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request

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
            self._async_get_elements_by_property_value(property_value, property_names, metadata_element_type_name,
                                                       effective_time, for_lineage, for_duplicate_processing,
                                                       start_from, page_size, time_out)
        )
        return response

    async def _async_get_guid_for_name(
            self, name: str, property_name: list[str] = ["qualifiedName", "displayName"],
            type_name: str = None

    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: [str], default = ["qualifiedName","displayName"]
            - properties to search in.
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

        elements = await self._async_get_elements_by_property_value(name, property_name, type_name)

        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
            elif len(elements) > 1:
                raise PyegeriaException(context={"issue": "Multiple elements found for supplied name!"})
            elif len(elements) == 1:
                return elements[0]["elementHeader"]["guid"]
        else:
            return NO_ELEMENTS_FOUND
        return elements

    def get_guid_for_name(
            self, name: str, property_name: list[str] = ["qualifiedName", "displayName"],
            type_name: str = "ValidMetadataValue"
    ) -> list | str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: [str], default = ["qualifiedName","displayName"]
            - properties to search in.
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

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_guid_for_name(name, property_name, type_name)
        )
        return response

    async def _async_get_element_by_guid_(self, element_guid: str) -> dict | str:
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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

    def _get_element_by_guid_(self, element_guid: str) -> dict | str:
        """
            Simplified, internal version of get_element_by_guid found in Classification Manager.
            Retrieve an element by its guid.

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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self._async_get_element_by_guid_(
                element_guid
            )
        )
        return result


    async def _async_get_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
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

    async def _async_get_connector_guid(self, connector_name: str) -> str:
        """Get the guid of a connector. Async version.
            Parameters:
                connector_name (str): The name of the connector to retrieve the guid for.
            Returns:
                str: The guid of the connector.
        """
        rel = await self._async_get_relationships_with_property_value(
            relationship_type="RegisteredIntegrationConnector",
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
            self._async_get_connector_guid(
                connector_name
            )
        )
        return result

    async def _async_add_archive_file(
            self,
            archive_file: str,
            server_guid: str = None,
            display_name: str = None,
            qualified_name: str = None,
            time_out: int = 120,
    ) -> None:
        """Add a new open metadata archive to running OMAG Server's repository.
            An open metadata archive contains metadata types and instances.  This operation loads an open metadata archive
            that is stored in the named file.  It can be used with OMAG servers that are of type Open Metadata Store.
            Async version.

            https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        archive_file: str
            Open metadata archive file to load.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        time_out: int, optional
           Time out for the rest call.

        Returns
        -------
        Response
          None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid,
            display_name,
            "displayName",
            qualified_name,
            "Metadata Access Server",
        )

        url = f"{self.command_root}runtime-manager/omag-servers/{server_guid}/instance/load/open-metadata-archives/file"

        await self._async_make_request(
            "POST-DATA", url, archive_file, time_out=time_out
        )
        return

    def add_archive_file(
            self,
            archive_file: str,
            server_guid: str = None,
            display_name: str = None,
            qualified_name: str = None,
            time_out: int = 120,
    ) -> None:
        """Add a new open metadata archive to running OMAG Server's repository.
            An open metadata archive contains metadata types and instances.  This operation loads an open metadata archive
            that is stored in the named file.  It can be used with OMAG servers that are of type Open Metadata Store.

            https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        archive_file: str
            Open metadata archive file to load.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        time_out: int, optional, default = 60 seconds

        Returns
        -------
        Response
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_archive_file(
                archive_file, server_guid, display_name, qualified_name, time_out
            )
        )
        return

    #
    #   Common feedback commands
    #

    def make_feedback_qn(self, feedback_type, src_guid, display_name=None) -> str:
        timestamp = int(time.time())
        if display_name is None:
            return f"{feedback_type}::{src_guid}::{self.user_id}::{timestamp}"
        else:
            return f"{feedback_type}::{src_guid}::{self.user_id}::{display_name}::{timestamp}"


    async def _async_add_comment_to_element(
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
            if comment_type not in COMMENT_TYPES:
                context = {"issue": "Invalid comment type"}
                raise PyegeriaInvalidParameterException(context=context)
            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "CommentProperties",
                    "qualifiedName": self.make_feedback_qn("Comment", element_guid),
                    "description": comment,
                    "commentType": comment_type
                }
            }
        elif body is None and comment is None:
            context = {"issue": "Invalid comment and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

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
            self._async_add_comment_to_element(element_guid, comment, comment_type, body)
        )
        return response

    async def _async_update_comment(
            self,
            comment_guid: str,
            comment: str = None,
            comment_type: str = "STANDARD_COMMENT",
            body: dict | UpdateElementRequestBody = None,
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
        if body is None and comment:
            if comment_type not in COMMENT_TYPES:
                context = {"issue": "Invalid comment type"}
                raise PyegeriaInvalidParameterException(context=context)
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": {
                    "class": "CommentProperties",
                    "description": comment,
                    "commentType": comment_type
                }
            }
        elif body is None and comment is None:
            context = {"issue": "Invalid comment and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

        url = f"{self.command_root}feedback-manager/comments{comment_guid}/update"
        await self._async_update_element_body_request(url, ["Comment"], body)

    def update_comment(
            self,
            comment_guid: str,
            comment: str = None,
            comment_type: str = "STANDARD_COMMENT",
            body: dict | UpdateElementRequestBody = None,
            merge_update: bool = True,
    ) -> None:
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
        loop.run_until_complete(
            self._async_update_comment(comment_guid, comment, comment_type, body, merge_update)
        )

    async def _async_setup_accepted_answer(
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
        await self._async_make_request("POST", url)

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
            self._async_setup_accepted_answer(question_comment_guid, answer_comment_guid)
        )

    async def _async_clear_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,

    ) -> None:
        """
        Remove the accepted-answer link between a question comment and its answer. Async version.

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
        await self._async_make_request("POST", url)

    def setup_clear_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,

    ) -> None:
        """
        Remove the accepted-answer link between a question comment and its answer.

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
            self._async_clear_accepted_answer(question_comment_guid, answer_comment_guid)
        )

    async def _async_remove_comment_from_element(
            self,
            comment_guid: str,
            body: dict | DeleteElementRequestBody = None,
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
        None

        Raises
        ------
        PyegeriaException

        Args:
            cascade_delete ():
        """

        url = f"{self.command_root}feedback-manager/comments/{comment_guid}/remove"
        await self._async_delete_element_request(url, body, cascade_delete)

    def remove_comment_from_element(
            self,
            comment_guid: str,
            body: dict | DeleteElementRequestBody = None,
            cascade_delete: bool = False,

    ) -> None:
        """
        Remove a comment from an element added by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        comment_guid: str
            - unique id for the comment object
        body: dict | DeleteElementRequestBody, optional
            - contains comment type and text
        cascade_delete: bool, default = False
            - whether to cascade delete

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_comment_from_element(comment_guid, body, cascade_delete=cascade_delete)
        )

    async def _async_get_comment_by_guid(
            self,
            comment_guid: str, element_type: str = "Comment",
            body: dict | GetRequestBody = None,
            output_format: str = "JSON",
            report_spec: str | dict = None
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        comment_guid
            - unique identifier for the comment object.
        body
            - optional effective time

        Returns
        -------
        comment properties

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        """

        url = f"{self.command_root}feedback-manager/comments/{comment_guid}/retrieve"
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_comment_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    def get_comment_by_guid(
            self,
            comment_guid: str, element_type: str = "Comment",
            body: dict | GetRequestBody = None,
            output_format: str = "JSON",
            report_spec: str | dict = None
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            report_spec ():
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_comment_by_guid(comment_guid, element_type, body, output_format, report_spec)
        )
        return response

    async def _async_get_attached_comments(
            self,
            element_guid: str,
            element_type: str = "Comment",
            body: dict = {},
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = None

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
            return self._generate_comment_output(element, None, output_format, report_spec)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def get_attached_comments(
            self, element_guid: str,
            element_type: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = None
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            report_spec ():
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_attached_comments(element_guid, element_type, body, start_from, page_size, output_format,
                                              report_spec)
        )
        return response

    async def _async_find_comments(
            self,
            search_string: str = None,
            classification_names: list[str] = None,
            metadata_element_subtypes: list[str] = ["Comment"],
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            output_format: str = "JSON",
            report_spec: str | dict = None,
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
        report_spec
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
            metadata_element_subtypes ():


        """

        url = f"{self.command_root}feedback-manager/comments/by-search-string"
        response = await self._async_find_request(url, _type="Comment", _gen_output=self._generate_comment_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    def find_comments(
            self,
            search_string: str = None,
            classification_names: list[str] = None, metadata_element_subtypes: list[str] = ["Comment"],
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = max_paging_size,
            output_format: str = "JSON",
            report_spec: str | dict = None,
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
        report_spec
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
            metadata_element_subtypes ():


        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_find_comments(search_string, classification_names, metadata_element_subtypes, starts_with,
                                      ends_with, ignore_case, start_from, page_size, output_format, report_spec, body)
        )

        return resp

    def _generate_comment_output(self, elements: dict | list[dict], search_string: str,
                                 element_type_name: str | None,
                                 output_format: str = 'DICT',
                                 report_spec: dict | str = None) -> str | list[dict]:
        entity_type = 'Comment'
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            elif isinstance(report_spec, dict):
                output_formats = get_report_spec_match(report_spec, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec('Default', output_format)
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
    # Note log
    #

    @dynamic_catch
    async def _async_create_note_log(
            self,
            element_guid: str = None,
            display_name: str = None,
            description: str = None,
            body: dict = None,
    ) -> str:
        """
        Creates a new noteLog and returns the unique identifier for it. Async Version.

        Parameters
        ----------
        element_guid: str, optional
            - unique identifier of the element where the note log is attached
        display_name: str, optional
            - name of the note log
        description: str, optional
            - text of the note log
        body
            - contains the name of the log and text. If present, the contents overrides
              the supplied parameters. If no element is provided, the property class must be "NewElementRequestBody".

        Returns
        -------
        ElementGUID

        Raises
        ------
        PyegeriaException
        Notes:
        ------
        Sample Body (simple version attaching to an associated element):

        {
            "class" : "NewAttachmentRequestBody",
            "initialClassifications": {
              "ZoneMembership" : {
                "class" : "ZoneMembershipProperties",
                "zoneMembership" : [ "erinoverview", "peterprofile" ]
              }
            },
            "properties": {
              "class": "NoteLogProperties",
              "qualifiedName": "Add unique name here",
              "displayName": "Add name here",
              "description": "Add description here",
              "additionalProperties": {
                "propertyName 1": "property value 1",
                "propertyName 2": "property value 2"
              }
            }
        }

        Full feature version allowing optional standalone use or attachment to an additional element:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class": "NoteLogProperties",
            "qualifiedName": "Add unique name here",
            "displayName": "Add name here",
            "description": "Add description here",
            "additionalProperties": {
              "propertyName 1": "property value 1",
              "propertyName 2": "property value 2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }


        """
        if body is None and element_guid:
            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "NoteLogProperties",
                    "typeName": "NoteLog",
                    "displayName": display_name,
                    "qualifiedName": self.make_feedback_qn("NoteLog", element_guid, display_name),
                    "description": description,
                }
            }
        elif body is None and not element_guid:
            body = {
                "class": "NewAElementRequestBody",
                "properties": {
                    "class": "NoteLogProperties",
                    "typeName": "NoteLog",
                    "displayName": display_name,
                    "qualifiedName": self.make_feedback_qn("NoteLog", element_guid, display_name),
                    "description": description,
                }
            }

        elif body is None and display_name is None:
            context = {"issue": "Invalid display name and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

        if element_guid:
            url = f"{self.command_root}feedback-manager/elements/{element_guid}/note-logs"
        else:
            url = f"{self.command_root}feedback-manager/note-logs"
        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json()

    @dynamic_catch
    def create_note_log(
            self,
            element_guid: str = None,
            display_name: str = None,
            description: str = None,
            body: dict = None,
    ) -> str:
        """
        Creates a new noteLog and returns the unique identifier for it.

        Parameters
        ----------
        element_guid, str, optional
            - unique identifier of the element where the note log is attached
        display_name: str, optional
            - name of the note log
        description: str, optional
            - text of the note log
        body
            - contains the name of the tag and (optional) description of the tag. If present, the contents overridee
              the supplied parameters.

        Returns
        -------
        ElementGUID

        Raises
        ------
        PyegeriaException
        Notes:
        ------
        Sample Body:

        {
            "class" : "NewAttachmentRequestBody",
            "initialClassifications": {
              "ZoneMembership" : {
                "class" : "ZoneMembershipProperties",
                "zoneMembership" : [ "erinoverview", "peterprofile" ]
              }
            },
            "properties": {
              "class": "NoteLogProperties",
              "qualifiedName": "Add unique name here",
              "displayName": "Add name here",
              "description": "Add description here",
              "additionalProperties": {
                "propertyName 1": "property value 1",
                "propertyName 2": "property value 2"
              }
            }
        }

        Full feature version allowing optional standalone use or attachment to an additional element:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class": "NoteLogProperties",
            "qualifiedName": "Add unique name here",
            "displayName": "Add name here",
            "description": "Add description here",
            "additionalProperties": {
              "propertyName 1": "property value 1",
              "propertyName 2": "property value 2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_note_log(element_guid, display_name, description, body)
        )
        return response

    @dynamic_catch
    async def _async_update_note_log(
            self,
            note_log_guid: str,
            display_name: str = None,
            description: str = None,
            body: dict = None,
            merge_update: bool = True,
    ) -> None:
        """
        Update an existing note log. Async Version.

        Parameters
        ----------
        note_log_guid
            - a unique identifier for the note log to change.
        display_name: str, optional
            - name of the note log
        description: str, optional
            - text of the note log
        body: dict, optional
            - details of the update - supersedes the other parameters.
        merge_update: bool, optional
            - whether to merge the new attributes with the existing note log attributes.

        Returns
        -------
        Void

        Raises
        ------
        PyegeriaExecption

        Notes:
        ______
        Sample body:

        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties" : {
            "class" : "NoteLogProperties",
            "qualifiedName" : "Add unique name here",
            "displayName" : "Add name here",
            "description" : "Add description here",
            "additionalProperties" : {
              "propertyName 1" : "property value 1",
              "propertyName 2" : "property value 2"
            }
          }
        }

        Args:
            display_name ():
            description ():

        """
        if body is None:
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": {
                    "class": "NoteLogProperties",
                    "description": description,
                    "displayName": display_name
                }
            }
        elif body is None and display_name is None:
            context = {"issue": "Invalid display name and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

        url = f"{self.command_root}feedback-manager/note-logs/note-logs/{note_log_guid}"
        await self._async_make_request("POST", url, body_slimmer(body))

    @dynamic_catch
    def update_note_log(
            self,
            note_log_guid: str,
            display_name: str = None,
            description: str = None,
            body: dict = None,
            merge_update: bool = True,
    ) -> None:
        """
        Update an existing note log.

        Parameters
        ----------
        note_log_guid
            - a unique identifier for the note log to change.
        display_name: str, optional
            - name of the note log
        description: str, optional
            - text of the note log
        body: dict, optional
            - details of the update - supersedes the other parameters.
        merge_update: bool, optional
            - whether to merge the new attributes with the existing note log attributes.
        Returns
        -------
        Void

        Raises
        ------
        PyegeriaExecption

        Notes:
        ______
        Sample body:

        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties" : {
            "class" : "NoteLogProperties",
            "qualifiedName" : "Add unique name here",
            "displayName" : "Add name here",
            "description" : "Add description here",
            "additionalProperties" : {
              "propertyName 1" : "property value 1",
              "propertyName 2" : "property value 2"
            }
          }
        }

        Args:
            display_name ():
            description ():

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.update_note_log(note_log_guid, display_name, description, body, merge_update)
        )
        return response

    @dynamic_catch
    async def _async_remove_note_log(
            self,
            note_log_guid: str,
            body: dict | DeleteElementRequestBody = None,
            cascade_delete: bool = False,
    ) -> None:
        """
        Removes a Note Log from the repository. All the relationships to referenceables are lost. Async Version..

        Parameters
        ----------
        note_log_guid: str
            - String - unique id for the note log.
        body: dict | DeleteElementRequestBody, optional
            - containing type of comment enum and the text of the comment.
        cascade_delete: bool, optional
            - If True, deletes all comments and replies associated with the note log.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/note-logs/{note_log_guid}/remove"
        await self._async_delete_element_request(url, body, cascade_delete)

    @dynamic_catch
    def remove_note_log(
            self,
            note_log_guid: str,
            body: dict | DeleteElementRequestBody = None,
            cascade_delete: bool = False,

    ) -> None:
        """
        Remove a note log from the repository. All relationships to referenceables are lost.

        Parameters
        ----------
        note_log_guid: str
            - unique id for the note log
        body: dict | DeleteElementRequestBody, optional
            - request body details (if provided, supersedes other parameters)
        cascade_delete: bool, default = False
            - if True, deletes all comments and replies associated with the note log

        Returns
        -------
        None

        Raises
        ------
        PyEgeriaException
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_note_log(note_log_guid, body, cascade_delete)
        )

    @dynamic_catch
    async def _async_find_note_logs(
            self,
            search_string: str,
            classification_names: list[str] = None,
            metadata_element_subtypes: list[str] = ["NoteLog"],
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            output_format: str = "JSON",
            report_spec: str | dict = None,
            body: dict | SearchStringRequestBody = None
    ) -> dict | str:

        """
        Return the list of note logs containing the supplied string. Async Version.

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
        report_spec
            - output format set for the response
        body
            - body of the request. Details of the body overrides other parameters if present.

        Returns
        -------
        list of note log objects

        Raises
        ------
        PyegeriaException

        Notes:

        Sample body:

        {
          "class" : "SearchStringRequestBody",
          "searchString" : "Add value here",
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 10,
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """

        url = f"{self.command_root}feedback-manager/note-logs/by-search-string"
        response = await self._async_find_request(url, _type="NoteLog", _gen_output=self._generate_feedback_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response

    @dynamic_catch
    def find_note_logs(
            self,
            search_string: str,
            classification_names: list[str] = None, metadata_element_subtypes: list[str] = ["NoteLog"],
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = max_paging_size,
            output_format: str = "JSON", report_spec: str | dict = None,
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
        report_spec
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
            metadata_element_subtypes ():


        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_find_note_logs(search_string, classification_names, metadata_element_subtypes, starts_with,
                                       ends_with, ignore_case, start_from, page_size, output_format, report_spec, body)
        )

        return resp

    @dynamic_catch
    async def _async_get_note_logs_by_name(
            self, filter: str,
            element_type: str = "NoteLog",
            body: dict | FilterRequestBody = None,
            output_format: str = "JSON",
            report_spec: str | dict = None,
            start_from: int = 0, page_size: int = 0
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements with an exact matching qualifiedName or name. Asymc Version.

        Parameters
        ----------
        filter: str
            - the name to filter on.
        element_type: str
            - NoteLog element type.
        body: dict | FilterRequestBody
            - optional effective time. If present, values supercede other parameters.

        Returns
        -------
        Note logproperties

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/note-logs/by-name"
        response = await self._async_get_name_request(url, _type=element_type, filter=filter,
                                                      _gen_output=self._generate_feedback_output, start_from=start_from,
                                                      page_size=page_size, output_format=output_format,
                                                      report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_note_logs_by_name(
            self, filter: str,
            element_type: str = "NoteLog",
            body: dict | FilterRequestBody = None,
            output_format: str = "JSON",
            report_spec: str | dict = None,
            start_from: int = 0, page_size: int = 0
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements with an exact matching qualifiedName or name.

        Parameters
        ----------
        filter: str
            - the name to filter on.
        element_type: str
            - NoteLog element type.
        body: dict | FilterRequestBody
            - optional effective time. If present, values supercede other parameters.

        Returns
        -------
        Note logproperties

        Raises
        ------
        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_note_logs_by_name(filter, element_type, body, output_format, report_spec, start_from,
                                             page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_attached_note_logs(
            self,
            element_guid: str,
            element_type: str = "NoteLog",
            body: dict = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = None

    ) -> dict | str:
        """
        Return the note logs attached to an element. Async version.

        Parameters
        ----------
        element_guid
            - a unique identifier for the element that the note logs are connected to (maybe a comment too).
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

        url = f"{self.command_root}feedback-manager/elements/{element_guid}/note-logs/retrieve"
        response = await self._async_make_request("POST", url, body)
        element = response.json().get("elements", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            return self._generate_feedback_output(element, None, output_format, report_spec)
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    @dynamic_catch
    def get_attached_note_logs(
            self, element_guid: str,
            element_type: str = None,
            body: dict = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = None
    ) -> dict | str:
        """
        Return the Note Logs attached to an element.

        Parameters
        ----------
        element_guid
            - a unique identifier for the element that the note logs are connected to (maybe a comment too).
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.

        Args:
            element_type ():
            output_format ():
            report_spec ():
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_attached_comments(element_guid, element_type, body, start_from, page_size, output_format,
                                              report_spec)
        )
        return response

    @dynamic_catch
    async def _async_create_note(self, note_log_guid: str, display_name: str = None, description: str = None,
                                 associated_element: str = None, body: dict | NewElementRequestBody = None) -> str:
        """
        Creates a new note for a note log and returns the unique identifier for it. Async version.

        Parameters
        ----------
        note_log_guid
            - unique identifier of the note log
        display_name
            - optional display name for the note
        description
            - optional description for the note
        associated_element: str, default is None
            - guid of the element to associate with the note - if provided, the note will be anchored to this element.
        body
            - optional body for the note

        Returns
        -------
        Guid for the note

        Raises
        ------
        PyegeriaException

        Notes
        _____

        Sample body (a note is an asset)
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "{{noteLogGUID}}",
          "isOwnAnchor": false,
          "parentGUID": "{{noteLogGUID}}",
          "parentRelationshipTypeName": "AttachedNoteLogEntry",
          "parentAtEnd1": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        if body is None and display_name:
            body = {
                "class": "NewElementRequestBody",
                "anchorGUID": associated_element if associated_element else note_log_guid,
                "isOwnAnchor": False,
                "parentGUID": note_log_guid,
                "parentRelationshipTypeName": "AttachedNoteLogEntry",
                "parentAtEnd1": True,
                "properties": {
                    "class": "NotificationProperties",
                    "typeName": "Notification",
                    "qualifiedName": self.make_feedback_qn("Note", note_log_guid, display_name),
                    "displayName": display_name,
                    "description": description,
                },
                "forLineage": False,
                "forDuplicateProcessing": False
            }

        elif body is None and display_name is None:
            context = {"issue": "Invalid display name and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

        url = f"{self.command_root}feedback-manager/assets"
        response = await self._async_create_element_body_request(url, ['Notification'], body)
        return response

    @dynamic_catch
    def create_note(
            self, note_log_guid:
            str, display_name: str = None, description: str = None,
            body: dict | NewElementRequestBody = None) -> str:
        """
        Creates a new note for a note log and returns the unique identifier for it.
    
        Parameters
        ----------
        note_log_guid
            - unique identifier of the note log
        display_name
            - optional display name for the note
        description
            - optional description for the note
        body
            - optional body for the note
    
        Returns
        -------
        Guid for the note
    
        Raises
        ------
        PyegeriaException
    
        Notes
        _____
    
        Sample body (a note is an asset)
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "{{noteLogGUID}}",
          "isOwnAnchor": false,
          "parentGUID": "{{noteLogGUID}}",
          "parentRelationshipTypeName": "AttachedNoteLogEntry",
          "parentAtEnd1": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
    
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_note(note_log_guid, display_name, body)
        )
        return response

    @dynamic_catch
    async def _async_add_journal_entry(self, note_log_qn: str = None, element_qn: str =  None,
                                       note_log_display_name: str = None, journal_entry_display_name: str = None,
                                       note_entry: str = None,
                                       body: dict | NewElementRequestBody = None) -> str:
        """
        Creates a new journal entry for a note log and returns the unique identifier for it. The note_log will be
        created if it does not exist. Async version.

        Parameters
        ----------
        note_log_qn: str = None
            - If provided, the journal entry will be attached to this note log. If not provided, a new note_log will be created.
        element_qn: str = None
            - If provided, and note log needs to be created, this will be used to define the new note log and attach it
             to the specified element.
        note_log_display_name: str = None
            - optional note log display name
        journal_entry_display_name: str = None
            - optional journal entry display name
        note_entry: str = None
            - the journal entry text

        body
            - optional body for the note - if provided, details here will supercede other parameters.

        Returns
        -------
        GUID for the journal entry (note).

        Raises
        ------
        PyegeriaException

        Notes
        _____

        Sample body (a note is an asset)
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "{{noteLogGUID}}",
          "isOwnAnchor": false,
          "parentGUID": "{{noteLogGUID}}",
          "parentRelationshipTypeName": "AttachedNoteLogEntry",
          "parentAtEnd1": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        note_log_guid = None
        element_guid = None
        # If a note_log_qn has been provided, look up its GUID
        if note_log_qn:
            note_log_guid = await self._async_get_guid_for_name(note_log_qn, ["qualifiedName"],'NoteLog' ) if note_log_qn else None

        # If we need to create a new note_log, then use the qualified name from the element_qn parameter, if provided.
        if note_log_guid is None or note_log_guid == NO_ELEMENTS_FOUND:
            if element_qn is None:
                if note_log_display_name is None:
                    note_log_display_name = f"NoteLog-{datetime.now().strftime('%Y-%m-%d %H:%M')}"

            else:
                element_guid = await self._async_get_guid_for_name(element_qn, ["qualifiedName"])
                if element_guid is None or element_guid == NO_ELEMENTS_FOUND:
                    context = { "reason" : "The specified associated element was not found"}
                    raise PyegeriaException(error_code = PyegeriaErrorCode.VALIDATION_ERROR, context = context)

            note_log = await self._async_create_note_log(element_guid = element_guid, display_name = note_log_display_name)
            note_log_guid = note_log["guid"]

        # Create the Journal Entry (Note)
        if journal_entry_display_name is None:
            journal_entry_display_name = f"Note-{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        journal_entry_guid = await self._async_create_note(note_log_guid, journal_entry_display_name,
                                                           note_entry, body)

        return journal_entry_guid

    @dynamic_catch
    def add_journal_entry(self, note_log_qn: str = None, element_qn: str = None,
                           note_log_display_name: str = None, journal_entry_display_name: str = None,
                          note_entry: str = None,
                           body: dict | NewElementRequestBody = None) -> str:
        """
        Creates a new journal entry for a note log and returns the unique identifier for it. The note_log will be
        created if it does not exist.

        Parameters
        ----------
        note_log_qn: str = None
            - If provided, the journal entry will be attached to this note log. If not provided, a new note_log will be created.
        element_qn: str = None
            - If provided, and note log needs to be created, this will be used to define the new note log and attach it
             to the specified element.
        note_log_display_name: str = None
            - optional note log display name
        journal_entry_display_name: str = None
            - optional journal entry display name
        note_entry: str = None
            - the journal entry text

        body
            - optional body for the note - if provided, details here will supercede other parameters.

        Returns
        -------
        GUID for the journal entry (note).

        Raises
        ------
        PyegeriaException

        Notes
        _____

        Sample body (a note is an asset)
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "{{noteLogGUID}}",
          "isOwnAnchor": false,
          "parentGUID": "{{noteLogGUID}}",
          "parentRelationshipTypeName": "AttachedNoteLogEntry",
          "parentAtEnd1": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_journal_entry(note_log_qn, element_qn, note_log_display_name, journal_entry_display_name, note_entry, body)
        )
        return response


    @dynamic_catch
    async def _async_update_note(self, note_guid: str, display_name: str = None, description: str = None,
                                 body: dict | UpdateElementRequestBody = None, merge_update: bool = True) -> None:
        """
        Update a note for a note log and returns the unique identifier for it. Async Version.

        Parameters
        ----------
        note_guid
            - unique identifier of the note log
        display_name
            - optional display name for the note
        description
            - optional description for the note
        body
            - optional body for the note. If provided, supercedes other parameters.
        merge_update
            - optional flag to merge the update with existing properties. Default is True.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        _____

        Sample body (a note is an asset)
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
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

        Args:
            merge_update ():

        """
        if body is None and display_name:
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": {
                    "class": "NotificationProperties",
                    "displayName": display_name,
                    "description": description,
                }
            }

        elif body is None and display_name is None:
            context = {"issue": "Invalid display name and body not provided"}
            raise PyegeriaInvalidParameterException(context=context)

        url = f"{self.command_root}feedback-manager/notes/{note_guid}"
        await self._async_update_element_body_request(url, ['Notification'], body)

    @dynamic_catch
    def update_note(
            self, note_guid: str, display_name: str = None, description: str = None,
            body: dict | UpdateElementRequestBody = None, merge_update: bool = True) -> None:
        """
        Update a note for a note log and returns the unique identifier for it. Async Version.

        Parameters
        ----------
        note_guid
            - unique identifier of the note log
        display_name
            - optional display name for the note
        description
            - optional description for the note
        body
            - optional body for the note. If provided, supercedes other parameters.
        merge_update
            - optional flag to merge the update with existing properties. Default is True.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        _____

        Sample body (a note is an asset)
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "NotificationProperties",
            "typeName" : "Notification",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "systemAction" : "add optional system action that occurred as part of this notification processing",
            "userResponse" : "add optional action that the reader should take",
            "priority" : 1,
            "activityStatus" : "FOR_INFO",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
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

        Args:
            merge_update ():

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_note(note_guid, display_name, description, body, merge_update)
        )

    @dynamic_catch
    async def _async_remove_note(
            self,
            note_guid: str,
            body: dict | DeleteElementRequestBody = None,

    ) -> None:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------

        note_guid
            - unique id for the note.

        body: dict | DeleteElementRequestBody
           - optional body for the note deletion.

        Returns
        -------
        VoidResponse

        Raises
        ------
        PyegeriaException
        """
        url = f"{self.command_root}feedback-manager/assets/{note_guid}/delete"
        await self._async_delete_element_request(url, body)

    @dynamic_catch
    def remove_note(
            self,
            note_guid: str,
            body: dict = None,
    ) -> None:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        note_guid
            - unique id for the note .

        body: dict | DeleteElementRequestBody
           - optional body for the note deletion.

        Returns
        -------
        VoidResponse

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_note(
                note_guid,
                body
            )
        )

    @dynamic_catch
    async def _async_find_notes(
            self,
            search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str = None
    ) -> dict | str:
        """
        Retrieve the list of note metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str, optional = None
            - optional search string to search for. If none, all elements are returned.
        body
            - search string and effective time.

        starts_with
            - Does the value start with the supplied string?
        ends_with
            - Does the value end with the supplied string?
        ignore_case
            - Should the search ignore case?
        start_from
            - Index of the list to start from (0 for start).
        page_size
            -Maximum number of elements to return.
        output_format: str, optional = "JSON"
            - Format of the returned output - includes JSON, MD, MERMAID, REPORT, LIST...
        report_spec: str, optional = None
            - Report specification for the returned output

        Returns
        -------
        list of matching metadata elements

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/assets/by-search-string"
        response = await self._async_find_request(url, "Notification", self._generate_feedback_output, search_string,
                                                  None, metadata_element_subtypes=["Notification"],
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def find_notes(
            self, search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str = None
    ) -> dict | str:
        """
        Retrieve the list of note metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str, optional = None
            - optional search string to search for. If none, all elements are returned.
        body
            - search string and effective time.

        starts_with
            - Does the value start with the supplied string?
        ends_with
            - Does the value end with the supplied string?
        ignore_case
            - Should the search ignore case?
        start_from
            - Index of the list to start from (0 for start).
        page_size
            -Maximum number of elements to return.

        Returns
        -------
        list of matching metadata elements

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():


        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_notes(search_string, body, starts_with, ends_with, ignore_case,
                                   start_from, page_size, output_format, report_spec)
        )
        return response

    @dynamic_catch
    async def _async_get_note_by_guid(
            self,
            note_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = "JSON",
            report_spec: str = None,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        note_guid
             - unique identifier of the requested metadata element
        body: dict | GetRequestBody
            - optional details of the request.
        O=output_format: str, default = "JSON"
            - output type - JSON, MD, MERMAID, REPORT, LIST...
        report_spec: str, optional = None
            - Report specification for the returned output
         Returns
         -------
         matching metadata element

         Raises
         ------
         PyegeriaException
        """

        url = f"{self.command_root}feedback-manager/assets/{note_guid}/retrieve"
        response = await self._async_get_guid_request(url, "Notification", self._generate_feedback_output,
                                                      output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_note_by_guid(
            self,
            note_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = "JSON",
            report_spec: str = None,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        note_guid
             - unique identifier of the requested metadata element
        body: dict | GetRequestBody
            - optional details of the request.
        output_format: str, default = "JSON"
            - output type - JSON, MD, MERMAID, REPORT, LIST...
        report_spec: str, optional = None
            - Report specification for the returned output
         Returns
         -------
         matching metadata element

         Raises
         ------
         PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_note_by_guid(note_guid, body, output_format, report_spec)
        )
        return response

    @dynamic_catch
    async def _async_get_notes_for_note_log(
            self,
            note_log_guid: str,
            body: dict | ResultsRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str = None,
    ) -> dict | str:
        """
        Retrieve the notes for the note_name.

        Parameters
        ----------
        note_log_guid
             - id of the note log to retrieve notes for.
        body: dict | ResultsRequestBody
            - optional details of the request.
        O=output_format: str, default = "JSON"
            - output type - JSON, MD, MERMAID, REPORT, LIST...
        report_spec: str, optional = None
            - Report specification for the returned output
         Returns
         -------
         matching metadata element

         Raises
         ------
         PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/note-logs/{note_log_guid}/retrieve"
        response = await self._async_get_results_body_request(url, "Notification", self._generate_feedback_output,
                                                              0, 0, output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_notes_for_note_log(
            self,
            note_log_guid: str,
            body: dict | ResultsRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str = None,
    ) -> dict | str:
        """
         Retrieve the notes for the note_name.

         Parameters
         ----------
         note_log_guid
              - note_log id to find notes for.
         body: dict | ResultsRequestBody
             - optional details of the request.
         O=output_format: str, default = "JSON"
             - output type - JSON, MD, MERMAID, REPORT, LIST...
         report_spec: str, optional = None
             - Report specification for the returned output
          Returns
          -------
          matching metadata element

          Raises
          ------
          PyegeriaException

         """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_notes_for_note_log(note_log_guid, body, start_from, page_size,
                                               output_format, report_spec)
        )
        return response

    #
    # Tags
    #
    @dynamic_catch
    async def _async_create_informal_tag(
            self,
            display_name: str,
            description: str,
            qualified_name: str = None
    ) -> str:
        """
        Creates a new informal tag and returns the unique identifier for it. Async Version.

        Parameters
        ----------

        display_name: str
            - The name of the informal tag.
        description: str
            - The description of the informal tag.
        qualified_name: str, optional
            - The qualified name of the informal tag. If not provided, it will be generated.

        Returns
        -------
        new element_guid

        Raises
        ------
        PyegeriaException
        """
        url = f"{self.command_root}feedback-manager/tags"
        if display_name is None:
            raise PyegeriaInvalidParameterException(context={"reason": "display_name is required"})
        if qualified_name is None:
            qualified_name = self.make_feedback_qn("InformalTag", None, display_name)
        body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "InformalTagProperties",
                "displayName": display_name,
                "qualifiedName" : qualified_name,
                "description": description
            }
        }
        response = await self._async_create_element_body_request(url, ["InformalTagProperties"], body)
        return response

    @dynamic_catch
    def create_informal_tag(
            self,
            display_name: str,
            description: str,
            qualified_name: str = None
    ) -> str:
        """
        Creates a new informal tag and returns the unique identifier for it.

        Parameters
        ----------

        display_name: str
            - The name of the informal tag.
        description: str
            - The description of the informal tag.
        qualified_name: str, optional
            - The qualified name of the informal tag. If not provided, it will be created automatically.

        Returns
        -------
        new element_guid

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_informal_tag(display_name, description, qualified_name)
        )
        return response

    @dynamic_catch
    async def _async_update_tag_description(
            self,
            tag_guid: str,
            description: str,

    ) -> None:
        """
        Updates the description of an existing tag. Async version.

        Parameters
        ----------

        tag_guid
            - unique id for the tag
        description: str
            - description of the tag

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
        """
        body = {
            "class": "InformalTagUpdateRequestBody",
            "description": description
        }

        url = f"{self.command_root}feedback-manager/tags/{tag_guid}/update"

        await self._async_make_request("POST", url, body)

    @dynamic_catch
    def update_tag_description(
            self,
            tag_guid: str,
            description: str,

    ) -> None:
        """
        Update the description of an existing tag.

        Parameters
        ----------
        tag_guid: str
            - unique id for the tag
        description: str
            - description of the tag

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_update_tag_description(tag_guid, description)
        )
        return response

    @dynamic_catch
    async def _async_delete_tag(
            self,
            tag_guid: str

    ) -> None:
        """
        Removes an informal tag from the repository.

        All the tagging relationships to this informal tag are lost. A
        private tag can be deleted by its creator and all the
        references are lost; a public tag can be deleted by anyone,
        but only if it is not attached to any referenceable.

        Parameters
        ----------

        tag_guid
            - String - unique id for the tag.
        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
        """

        url = f"{self.command_root}feedback-manager/tags/{tag_guid}/remove"
        await self._async_make_request("POST", url)

    @dynamic_catch
    def delete_tag(
            self,
            tag_guid: str
    ) -> None:
        """
         Removes an informal tag from the repository.

         All the tagging relationships to this informal tag are lost. A
         private tag can be deleted by its creator and all the
         references are lost; a public tag can be deleted by anyone,
         but only if it is not attached to any referenceable.

         Parameters
         ----------

         tag_guid
             - String - unique id for the tag.
         Returns
         -------
         VOIDResponse

         Raises
         ------
         PyegeriaException
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_tag(tag_guid)
        )

    @dynamic_catch
    async def _async_get_tag_by_guid(
            self,
            tag_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = "json",
            report_spec: str = None) -> dict | str:
        """
        Return the informal tag for the supplied unique identifier (tag_guid).

        Parameters
        ----------

        tag_guid
            - unique identifier of the meaning.
        body: dict | GetRequestBody, Optional
            - details of the request.
        output_format: str, Optional, default = "JSON"
            - format of the response
        report_spec: str, Optional
            - specification for the report

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException

        Args:
            body ():
            output_format ():
            report_spec ():
        """

        url = f"{self.command_root}feedback-manager/tags/{tag_guid}/retrieve"

        response = await self._async_get_guid_request(url, "InformalTag", self._generate_feedback_output,
                                                      output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_tag_by_guid(
            self,
            tag_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = "json",
            report_spec: str = None,
    ) -> dict | str:
        """
                Return the informal tag for the supplied unique identifier (tag_guid).

                Parameters
                ----------
                tag_guid
                    - unique identifier of the meaning.
                body: dict | GetRequestBody, Optional
                    - details of the request.
                output_format: str, Optional, default = "JSON"
                    - format of the response
                report_spec: str, Optional
                    - specification for the report

                Returns
                -------
                list of tag objects

                Raises
                ------
                PyegeriaException
            """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tag_by_guid(tag_guid, body, output_format, report_spec)
        )
        return response

    @dynamic_catch
    async def _async_get_tags_by_name(
            self,
            tag_name: str,
            body: dict | FilterRequestBody = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json",
            report_spec: str = None,
    ) -> dict | str:
        """
        Return the tags exactly matching the supplied name. Async Version.

        Parameters
        ----------
        tag_name: str
            - name of the informal tag to filter on.
        body
            - name of tag.
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException
        """

        url = f"{self.command_root}feedback-manager/tags/by-name"

        response = await self._async_get_name_request(url, self._generate_feedback_output, tag_name,
                                                      None,start_from, page_size, output_format, report_spec
                                                     )
        return response

    @dynamic_catch
    def get_tags_by_name(
            self,
            tag_name: str,
            body: dict | FilterRequestBody = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json",
            report_spec: str = None,
    ) -> dict | str:
        """
        Return the tags exactly matching the supplied name.

        Parameters
        ----------
        tag_name: str
            - name of the informal tag to filter on.
        body
            - name of tag.
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tags_by_name(
                tag_name, body,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )
        return response

    @dynamic_catch
    async def _async_find_tags(
            self,
            search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = max_paging_size, output_format: str = "json", report_spec: str = None,

    ) -> dict | str:
        """
        Return the list of informal tags containing the supplied string in their name or description. The search string
        is located in the request body and is interpreted as a plain string.  The request parameters,
        startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.  The request body also supports the
        specification of an effective time to restrict the search to element that are/were effective at a particular time.

        Parameters
        ----------
        search_string: str
            - string to search for.
        body: dict | SearchStringRequestBody
            - details of the request.
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

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}feedback-manager/tags/by-search-string"
        response = await self._async_find_request(url, "InformalTag", self._generate_feedback_output, search_string,
                                                  None, metadata_element_subtypes=None, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def find_tags(
            self,
            search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = max_paging_size, output_format: str = "json", report_spec: str = None,
    ) -> dict | str:
        """
        Return the list of informal tags containing the supplied string in their name or description. The search string
        is located in the request body and is interpreted as a plain string.  The request parameters,
        startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.  The request body also supports the
        specification of an effective time to restrict the search to element that are/were effective at a particular time.

        Parameters
        ----------
        search_string: str
            - string to search for.
        body: dict | SearchStringRequestBody
            - details of the request.
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

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException

"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_tags(search_string, body, starts_with, ends_with, ignore_case,
                                  start_from, page_size, output_format, report_spec)
        )
        return response

    async def _async_find_my_tags(
            self,
            search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,

    ) -> dict | str:
        """
        Return the list of the calling user's private tags containing the supplied string in either the name or description.

        Parameters
        ----------
        search_string: str
        - string to search for.
        body: dict | SearchStringRequestBody
        - details of the request. Supersedes other parameters if present.
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

        Returns
        -------
        list of tag objects

        Raises
        ------
        PyegeriaException
        """

        url = f"{self.command_root}feedback-manager/tags/update"
        response = await self._async_make_request("POST", url, body)
        return response

    def find_my_tags(
            self,
            search_string: str = None,
            body: dict | SearchStringRequestBody = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,

    ) -> dict | str:
        """
        Return the list of the calling user's private tags containing the supplied string in either the name or description.

        Parameters
        ----------
        search_string: str
        body: dict | SearchStringRequestBody
            - detailed request - supersedes other parameters.
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


        Returns
        -------
        list of tag objects

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
            self._async_find_my_tags(
                search_string,
                body,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,

            )
        )
        return response

    @dynamic_catch
    async def _async_add_tag_to_element(
            self,
            element_guid: str,
            tag_guid: str,
            is_public: bool = False,
            body: dict | NewRelationshipRequestBody = None,

    ) -> None:
        """
        Adds an informal tag (either private of public) to an element. Async Version.

        Parameters
        ----------

        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        body: dict | NewRelationshipRequestBody
            - optional detailed information for the request.

        Returns
        -------
        Void

        Raises
        ------
        PyegeriaException
        """
        is_public_s = str(is_public).lower()

        url = f"{self.command_root}feedback-manager/elements/{element_guid}/tags/{tag_guid}?isPublic={is_public_s}"
        await self._async_new_relationship_request(url, 'InformalTag', body)

    @dynamic_catch
    def add_tag_to_element(
            self,
            element_guid: str,
            tag_guid: str,
            is_public: bool = False,
            body: dict | NewRelationshipRequestBody = None,

    ) -> dict | str:
        """
        Adds an informal tag (either private of public) to an element. Async Version.

        Parameters
        ----------

        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        body: dict | NewRelationshipRequestBody
            - optional detailed information for the request.

        Returns
        -------
        Void

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_tag_to_element(
                element_guid,
                tag_guid,
                is_public,
                body
            )
        )

    @dynamic_catch
    async def _async_get_elements_by_tag(
            self,
            tag_guid: str,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,

    ) -> dict | str:
        """
        Return the list of unique identifiers for elements that are linked to a specific tag either directly, or via one of its schema elements.

        Parameters
        ----------
        tag_guid
            - unique identifier of tag.
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.

        Returns
        -------
        element stubs list

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        """
        # Todo - fix the output format here when ready
        url = f"{self.command_root}feedback-manager/elements/by-tag/{tag_guid}?startFrom={start_from}&pageSize={page_size}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    @dynamic_catch
    def get_elements_by_tag(
            self,
            tag_guid: str,
            body: dict = {},
            start_from: int = 0,
            page_size: int = 0,

    ) -> dict | str:
        """
        Return the list of unique identifiers for elements that are linked to a specific tag either directly, or via one of its schema elements.

        Parameters
        ----------
        tag_guid
            - unique identifier of tag.
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.

        Returns
        -------
        element stubs list

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
            self._async_get_elements_by_tag(tag_guid, body, start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_attached_tags(
            self,
            element_guid: str,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,

    ) -> dict | str:
        """
        Return the informal tags attached to an element.

        Parameters
        ----------
        element_guid
            - unique identifier for the element that the ratings are connected to

        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.

        Returns
        -------
        List of InformalTags (InformalTagsResponse)

        Raises
        ------
        PyegeriaException
        """
        # Todo clean up and add output format stuff when ready
        url = f"{self.command_root}feedback-manager/elements/{element_guid}/tags/retrieve"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    @dynamic_catch
    def get_attached_tags(
            self,
            element_guid: str,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,

    ) -> dict | str:
        """
        Return the informal tags attached to an element.

        Parameters
        ----------
        element_guid
            - unique identifier for the element that the ratings are connected to

        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.

        Returns
        -------
        List of InformalTags (InformalTagsResponse)

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
            self._async_get_attached_tags(
                element_guid,
                body,
                start_from,
                page_size,
            )
        )
        return response

    async def _async_remove_tag_from_element(
            self,
            element_guid: str,
            tag_guid: str,
            body: dict = {},

    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------

        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        body
            - null request body needed for correct protocol exchange.

        Returns
        -------
        Void

        Raises
        ------
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
            the requesting user is not authorized to issue this request.
        """

        url = f"{self.command_root}feedback-manager/elements/{element_guid}/tags/{tag_guid}/remove"
        await self._async_make_request("POST", url, body)

    def remove_tag_from_element(
            self,
            element_guid: str,
            tag_guid: str,
            body: dict = {},

    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------
        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
            - null request body needed for correct protocol exchange.

        Returns
        -------
        Void

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
            self._async_remove_tag_from_element(
                element_guid,
                tag_guid,
                body
            )
        )
        return response

    #
    # Search Tags
    #
    @dynamic_catch
    async def _async_add_search_keyword_to_element(
            self,
            element_guid: str,
            keyword: str = None,
            body: dict = None
    ) -> str:
        """
        Creates a search keyword and attaches it to an element.
        The GUID returned is the identifier of the relationship. Async Version.

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        keyword: str = None
            - the name of the search keyword to add
        body: dict, optional
            - structure containing search string information - see Notes

        Returns
        -------
        Guid of the search keyword.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
          "class" : "NewAttachmentRequestBody",
          "properties" : {
            "class" : "SearchKeywordProperties",
            "keyword" : "myKeyword",
            "description" : "Add search keyword text here"
          }
        }

        """
        if body is None and keyword:
            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "SearchKeywordProperties",
                    "keyword": keyword
                }
            }
        elif body is None:
            raise PyegeriaInvalidParameterException(context={"reason": "keyword or body is required"})

        url = f"{self.command_root}classification-manager/elements/{element_guid}/search-keywords"

        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get('guid', 'Search keyword was not created')

    @dynamic_catch
    def add_search_keyword_to_element(
            self,
            element_guid: str,
            keyword: str = None,
            body: dict = None,
    ) -> str:
        """
        Creates a search keyword and attaches it to an element.
        The GUID returned is the identifier of the relationship.

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        keyword: str = None
            - the name of the search keyword to add
        body: dict, optional
            - structure containing search string information - see Notes

        Returns
        -------
        Guid of the search keyword.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
          "class" : "NewAttachmentRequestBody",
          "properties" : {
            "class" : "SearchKeywordProperties",
            "keyword" : "myKeyword",
            "description" : "Add search keyword text here"
          }
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_search_keyword_to_element(element_guid, keyword, body)
        )
        return response


    @dynamic_catch
    async def _async_update_search_keyword(
            self,
            keyword_guid: str,
            body: dict | UpdateElementRequestBody = None,
    ) -> str:
        """
       Update the properties of a search keyword. Async Version.

        Parameters
        ----------
        keyword_guid: str
            - identity of the keyword to update
        body: dict | UpdateElementRequestBody, optional
            - structure containing keyword information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties" : {
            "class" : "SearchKeywordProperties",
            "keyword" : "myKeyword",
            "description" : "Add search keyword text here"
          }
        }

        """

        url = f"{self.command_root}classification-manager/search-keywords/{keyword_guid}/update"
        await self._async_update_relationship_request(url, None, body_slimmer(body))

    @dynamic_catch
    def update_search_keyword(
            self,
            keyword_guid: str,
            body: dict | UpdateElementRequestBody = None,
    ) -> None:
        """
        Update the properties of a search keyword.

         Parameters
         ----------
         keyword_guid: str
             - identity of the keyword to update
         body: dict | UpdateElementRequestBody, optional
             - structure containing keyword information - see Notes

         Returns
         -------
         None

         Raises
         ------
         PyegeriaException

         Notes
         -----
         Sample body:
         {
           "class" : "UpdateElementRequestBody",
           "mergeUpdate": true,
           "properties" : {
             "class" : "SearchKeywordProperties",
             "keyword" : "myKeyword",
             "description" : "Add search keyword text here"
           }
         }

         """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_search_keyword(keyword_guid, body)
        )

    @dynamic_catch
    async def _async_remove_search_keyword(
            self,
            keyword_guid: str
    ) -> None:
        """
        Remove the search keyword for an element. Async Version.

        Parameters
        ----------
        keyword_guid: str
            - identity of the search keyword to remove.

        Returns
        -------

        Raises
        ------
        PyegeriaException


        """

        url = f"{self.command_root}classification-manager/search-keywords/{keyword_guid}/remove"
        await self._async_delete_relationship_request(url = url, body = None, cascade_delete = False)

    @dynamic_catch
    def remove_search_keyword(
            self,
            keyword_guid,
    ) -> None:
        """
        Remove the search keyword for an element.

        Parameters
        ----------
        license_guid: str
            - identity of the license to remove

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_search_keyword(keyword_guid )
        )

    @dynamic_catch
    async def _async_get_search_keyword_by_guid(
            self,
            keyword_guid: str,
            output_format: str | None = "JSON",
            report_spec: dict | str = None
    ) -> dict | str:
        """
        Return information about the specified search keyword.

        Parameters
        ----------
        keyword_guid: str
            - unique identifier of tag.
        output_format: str, default "JSON"
            - output format for the response
        report_spec: str | dict, default None
            - report specification

        Returns
        -------
        Details of the search keyword in the requested format.

        Raises
        ------
        PyegeriaException

        """

        url = f"{self.command_root}classification-manager/search-keywords/{keyword_guid}"
        response = await self._async_get_guid_request(url, "SearchKeyword", self._generate_feedback_output,
                                                      output_format, report_spec)
        return response

    @dynamic_catch
    def get_search_keyword_by_guid(
            self,
            keyword_guid: str,
            output_format: str | None = "JSON",
            report_spec: dict | str = None

    ) -> dict | str:
        """
               Return information about the specified search keyword.

               Parameters
               ----------
               keyword_guid: str
                   - unique identifier of tag.
               output_format: str, default "JSON"
                   - output format for the response
               report_spec: str | dict, default None
                   - report specification

               Returns
               -------
               Details of the search keyword in the requested format.

               Raises
               ------
               PyegeriaException

               """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_search_keyword_by_guid(keyword_guid, output_format, report_spec)
        )
        return response

    @dynamic_catch
    async def _async_get_search_keyword_by_keyword(
            self,
            keyword: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str | None = "JSON",
            report_spec: dict | str = None,
            body: dict | FilterRequestBody = None
    ) -> dict | str:
        """
        Return information about the specified search keyword. Async Version.

        Parameters
        ----------
        keyword : str
            - keyword to search for.
        start_from: int, default 0
            - start index of the search keyword
        page size
            - output_format: str, default "JSON
        output_format: str, default "JSON"
            - output format for the response
        report_spec: str | dict, default None
            - report specification
        body: dict | FilterRequestBody, optional
            - structure containing detailed request information.

        Returns
        -------
        Details of the search keyword in the requested format.

        Raises
        ------
        PyegeriaException

        """
        if body is None and keyword:
            body = {
                "class": "FilterRequestBody",
                "filter": filter,
                "startFrom": start_from,
                "pageSize": page_size
            }
        url = f"{self.command_root}classification-manager/search-keywords/by-keyword"
        response = await self._async_get_name_request(url, "SearchKeyword", self._generate_feedback_output,
                                                      keyword, None, None, start_from,
                                                      page_size, output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_search_keyword_by_keyword(
            self,
            keyword: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str | None = "JSON",
            report_spec: dict | str = None,
            body: dict | FilterRequestBody = None
    ) -> dict | str:
        """
        Return information about the specified search keyword.

        Parameters
        ----------
        keyword : str
            - keyword to search for.
        start_from: int, default 0
            - start index of the search keyword
        page size
            - output_format: str, default "JSON
        output_format: str, default "JSON"
            - output format for the response
        report_spec: str | dict, default None
            - report specification
        body: dict | FilterRequestBody, optional
            - structure containing detailed request information.

        Returns
        -------
        Details of the search keyword in the requested format.

        Raises
        ------
        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_search_keywords(keyword, start_from, page_size, output_format, report_spec, body)
        )
        return response

    async def _async_find_search_keywords(
            self,
            search_string: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str | None = "JSON",
            report_spec: dict | str = None,
            body: dict | SearchStringRequestBody = None
    ) -> dict | str:
        """
        Return the list of search keywords containing the supplied string. The search string is located in the request
         body and is interpreted as a plain string.  The request parameters, startsWith, endsWith and ignoreCase can
         be used to allow a fuzzy search.  The request body also supports the specification of an effective time to
         restrict the search to element that are/were effective at a particular time. Async Version.

        Parameters
        ----------
        search_string : str
            - keyword to search for.
        start_from: int, default 0
            - start index of the search keyword
        page size
            - output_format: str, default "JSON
        output_format: str, default "JSON"
            - output format for the response
        report_spec: str | dict, default None
            - report specification
        body: dict | SearchStringRequestBody, optional
            - structure containing detailed request information.

        Returns
        -------
        Details of the search keyword in the requested format.

        Raises
        ------
        PyegeriaException

        """
        if body is None and search_string:
            body = {
                "class": "SearchStringRequestBody",
                "filter": filter,
                "startFrom": start_from,
                "pageSize": page_size
            }
        url = f"{self.command_root}classification-manager/search-keywords/by-search-string"
        response = await self._async_find_request(url, "SearchKeyword", self._generate_feedback_output, search_string,
                                                  None, metadata_element_subtypes=None, starts_with=True,
                                                  ends_with=False, ignore_case=False, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def find_search_keywords(
            self,
            search_string: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str | None = "JSON",
            report_spec: dict | str = None,
            body: dict | SearchStringRequestBody = None
    ) -> dict | str:
        """
        Return the list of search keywords containing the supplied string. The search string is located in the request
         body and is interpreted as a plain string.  The request parameters, startsWith, endsWith and ignoreCase can
         be used to allow a fuzzy search.  The request body also supports the specification of an effective time to
         restrict the search to element that are/were effective at a particular time. Async Version.

        Parameters
        ----------
        search_string : str
            - keyword to search for.
        start_from: int, default 0
            - start index of the search keyword
        page size
            - output_format: str, default "JSON
        output_format: str, default "JSON"
            - output format for the response
        report_spec: str | dict, default None
            - report specification
        body: dict | SearchStringRequestBody, optional
            - structure containing detailed request information.

        Returns
        -------
        Details of the search keyword in the requested format.

        Raises
        ------
        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_search_keywords(search_string, start_from, page_size, output_format, report_spec, body)
        )
        return response

    @dynamic_catch
    def _extract_comment_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Common population pipeline
        col_data = populate_common_columns(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('attributes', [])
        # Overlay extras (project roles) only where empty
        # extra = self._extract_additional_project_properties(element, columns_struct)
        # col_data = overlay_additional_values(col_data, extra)
        return col_data

    def _extract_element_properties_for_keyword(self, element: dict, columns_struct: dict) -> dict:
        keyword_elements = None
        keyword_elements = element["keywordElements"]
        out_body = {}
        keyword = element["properties"].get('keyword', '')
        for el in keyword_elements:
            element = el.get("relatedElement", {})
            element_guid = element['elementHeader']['guid']
            element_type = element['elementHeader']['type']['typeName']
            element_display_name = element['properties'].get('displayName',"")
            element_description = element['properties'].get('description',"")
            element_category = element['properties'].get('category',"")
            out_body = {
                "element_display_name": element_display_name,
                "element_description": element_description,
                "element_category": element_category,
                "element_type": element_type,
                "element_guid": element_guid,
                "keyword": keyword
            }
        return out_body

    @dynamic_catch
    def _extract_feedback_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Common population pipeline
        col_data = populate_common_columns(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('attributes', [])
        # Overlay extras (project roles) only where empty
        keyword_elements = element.get("keywordElements", [])

        if keyword_elements != [] and isinstance(element['keywordElements'], list):
            extra = self._extract_element_properties_for_keyword(element, columns_struct)
            col_data = overlay_additional_values(col_data, extra)

        note_logs = element.get("presentInNoteLogs", [])
        if note_logs != []:
            extra = self._extract_element_properties_for_notes( element, columns_struct)
            col_data = overlay_additional_values(col_data, extra)

        return col_data

    @dynamic_catch
    def _generate_feedback_output(self, elements: dict | list[dict], search_string: str,
                                  element_type_name: str | None,
                                  output_format: str = 'DICT',
                                  report_spec: dict | str = None) -> str | list[dict]:
        entity_type = element_type_name
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            elif isinstance(report_spec, dict):
                output_formats = get_report_spec_match(report_spec, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec('Default', output_format)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_feedback_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )


    #
    # Helper functions for requests
    #

    @dynamic_catch
    def validate_new_element_request(self, body: dict | NewElementRequestBody,
                                     prop: list[str] = None) -> NewElementRequestBody | None:
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

    @dynamic_catch
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

    @dynamic_catch
    def validate_new_relationship_request(self, body: dict | NewRelationshipRequestBody,
                                          prop: list[str] = None) -> NewRelationshipRequestBody | None:
        if isinstance(body, NewRelationshipRequestBody):
            if (prop and body.properties.class_ in prop) or (prop is None):
                validated_body = body
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})
        elif isinstance(body, dict):
            if prop is None or body.get("properties", {}).get("class", "") in prop:
                validated_body = self._new_relationship_request_adapter.validate_python(body)
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})
        else:
            return None
        return validated_body

    @dynamic_catch
    def validate_new_classification_request(self, body: dict | NewClassificationRequestBody,
                                            prop: str = None) -> NewClassificationRequestBody | None:
        if isinstance(body, NewClassificationRequestBody):
            if (prop and body.properties.class_ in prop) or (prop is None):
                validated_body = body
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})

        elif isinstance(body, dict):
            if prop is None or body.get("properties", {}).get("class", "") == prop:
                validated_body = self._new_classification_request_adapter.validate_python(body)
            else:
                raise PyegeriaInvalidParameterException(additional_info=
                                                        {"reason": "unexpected property class name"})
        else:
            return None

        return validated_body

    @dynamic_catch
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

    @dynamic_catch
    def validate_delete_relationship_request(self, body: dict | DeleteRelationshipRequestBody,
                                             cascade_delete: bool = False) -> DeleteRelationshipRequestBody | None:
        if isinstance(body, DeleteRelationshipRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._delete_relationship_request_adapter.validate_python(body)
        else:  # handle case where body not provided
            # body = {
            #     "class": "DeleteRelationshipRequestBody",
            #     "cascadeDelete": cascade_delete
            # }
            # validated_body = DeleteRelationshipRequestBody.model_validate(body)
            return None
        return validated_body

    @dynamic_catch
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

    @dynamic_catch
    def validate_update_element_request(self, body: dict | UpdateElementRequestBody,
                                        prop: list[str] = None) -> UpdateElementRequestBody | None:
        if isinstance(body, UpdateElementRequestBody):
            if prop is None or body.properties.class_ in prop:
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

    @dynamic_catch
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

    @dynamic_catch
    def validate_update_relationship_request(self, body: dict | UpdateRelationshipRequestBody,
                                             prop: [str] = None) -> UpdateRelationshipRequestBody | None:
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

    @dynamic_catch
    async def _async_find_request(self, url: str, _type: str, _gen_output: Callable[..., Any], search_string: str = '*',
                                  include_only_classification_names: list[str] = None,
                                  metadata_element_type: str = None, metadata_element_subtypes: list[str] = None,
                                  starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                  start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                  report_spec: str | dict = None, skip_relationships: list[str] = None,
                                  include_only_relatiohsips: list[str] = None,
                                  skip_classified_elements: list[str] = None, graph_query_depth: int = 3,
                                  governance_zone_filter: list[str] = None, as_of_time: str = None,
                                  effective_time: str = None, relationship_page_size: int = 0,
                                  body: dict | SearchStringRequestBody = None) -> Any:

        if isinstance(body, SearchStringRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._search_string_request_adapter.validate_python(body)
        else:
            search_string = None if search_string == "*" else search_string
            body = {
                "class": "SearchStringRequestBody",
                "include_only_classified_elements": include_only_classification_names,
                "metadata_element_type": metadata_element_type,
                "metadata_element_subtype_names": metadata_element_subtypes,
                "skip_classified_elements": skip_classified_elements,
                "skip_relationships": skip_relationships,
                "include_only_relatiohsips": include_only_relatiohsips,
                "graph_query_depth": graph_query_depth,
                "governance_zone_filter": governance_zone_filter,
                "as_of_time": as_of_time,
                "effective_time": effective_time,
                "relationship_page_size": relationship_page_size,
                "search_string": search_string,
                "starts_with": starts_with,
                "ends_with": ends_with,
                "ignore_case": ignore_case,
                "start_from": start_from,
                "page_size": page_size,

            }
            validated_body = SearchStringRequestBody.model_validate(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)

        response = await self._async_make_request("POST", url, json_body, time_out = 90)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            # logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return _gen_output(elements, search_string, _type,
                               output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_get_name_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                      filter_string: str, classification_names: list[str] = None,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      report_spec: str | dict = None,
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
        if type(elements) is str or len(elements) == 0:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return _gen_output(elements, filter_string, _type,
                               output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_get_guid_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                      output_format: str = 'JSON', report_spec: str | dict = None,
                                      body: dict | GetRequestBody = None) -> Any:

        if isinstance(body, GetRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._get_request_adapter.validate_python(body)
        else:
            _type = _type.replace(" ", "")
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
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return _gen_output(elements, "GUID", _type, output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_get_results_body_request(self, url: str, _type: str, _gen_output: Callable[..., Any],
                                              start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                              report_spec: str | dict = None,
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

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return _gen_output(elements, "Members", _type,
                               output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_get_level_identifier_query_body_request(self, url: str, _gen_output: Callable[..., Any],
                                                             output_format: str = 'JSON',
                                                             report_spec: str | dict = None,
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
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return _gen_output(elements, "", "Referenceable",
                               output_format, report_spec)
        return elements

    @dynamic_catch
    async def _async_create_element_body_request(self, url: str, prop: list[str] = None,
                                                 body: dict | NewElementRequestBody = None) -> str:
        validated_body = self.validate_new_element_request(body, prop)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())
        return response.json().get("guid", "NO_GUID_RETURNED")

    @dynamic_catch
    async def _async_create_element_from_template(self, url: str, body: dict | TemplateRequestBody = None) -> str:
        validated_body = self.validate_new_element_from_template_request(body)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(response.json())
        return response.json().get("guid", "NO_GUID_RETURNED")

    @dynamic_catch
    async def _async_update_element_body_request(self, url: str, prop: list[str] = None,
                                                 body: dict | UpdateElementRequestBody = None) -> None:
        validated_body = self.validate_update_element_request(body, prop)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())

    @dynamic_catch
    async def _async_update_status_request(self, url: str, status: str = None,
                                           body: dict | UpdateStatusRequestBody = None) -> None:
        validated_body = self.validate_update_status_request(status, body)
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        response = await self._async_make_request("POST", url, json_body)
        logger.info(response.json())

    @dynamic_catch
    async def _async_new_relationship_request(self, url: str, prop: list[str] = None,
                                              body: dict | NewRelationshipRequestBody = None) -> None:
        validated_body = self.validate_new_relationship_request(body, prop)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_new_classification_request(self, url: str, prop: list[str] = None,
                                                body: dict | NewClassificationRequestBody = None) -> None:
        validated_body = self.validate_new_classification_request(body, prop)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_delete_element_request(self, url: str, body: dict | DeleteElementRequestBody = None,
                                            cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_element_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_delete_relationship_request(self, url: str, body: dict | DeleteRelationshipRequestBody = None,
                                                 cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_relationship_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_delete_classification_request(self, url: str, body: dict | DeleteClassificationRequestBody = None,
                                                   cascade_delete: bool = False) -> None:
        validated_body = self.validate_delete_classification_request(body, cascade_delete)
        if validated_body:
            json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
            logger.info(json_body)
            await self._async_make_request("POST", url, json_body)
        else:
            await self._async_make_request("POST", url)

    @dynamic_catch
    async def _async_update_relationship_request(self, url: str, prop: list[str] = None,
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
    async def _async_update_element_effectivity(self, guid: str, effectivity_time: str = None,
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


    @dynamic_catch
    def _extract_referenceable_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate default Referenceable columns for output using common population pipeline."""
        return populate_common_columns(element, columns_struct)

    @dynamic_catch
    def _generate_referenceable_output(self, elements: dict | list[dict], search_string: str | None,
                                       element_type_name: str | None,
                                       output_format: str = "JSON",
                                       report_spec: dict | str = None) -> str | list[dict]:
        """Generate formatted output for generic Referenceable elements.

        If output_format is 'JSON', returns elements unchanged. Otherwise, resolves an
        output format set and delegates to generate_output with a standard extractor.
        """
        if output_format == "JSON":
            return elements
        entity_type = element_type_name or "Referenceable"
        output_formats = resolve_output_formats(entity_type, output_format, report_spec, default_label=entity_type)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def _extract_element_properties_for_keyword(self, element: dict, columns_struct: dict) -> dict:
        keyword_elements = None
        keyword_elements = element["keywordElements"]
        out_body = {}
        keyword = element["properties"].get('keyword', '')
        for el in keyword_elements:
            element = el.get("relatedElement", {})
            element_guid = element['elementHeader']['guid']
            element_type = element['elementHeader']['type']['typeName']
            element_display_name = element['properties'].get('displayName',"")
            element_description = element['properties'].get('description',"")
            element_category = element['properties'].get('category',"")
            out_body = {
                "element_display_name": element_display_name,
                "element_description": element_description,
                "element_category": element_category,
                "element_type": element_type,
                "element_guid": element_guid,
                "keyword": keyword
            }
        return out_body

    def _extract_element_properties_for_notes(self, element: dict, columns_struct: dict):
        note_log_qualified_name = None
        note_log_guid = None
        note_log_display_name = None
        note_log_description = None

        note_log_el = element.get("presentInNoteLogs",{})[0].get("relatedElement",None)
        if note_log_el:
            note_log_guid = note_log_el['elementHeader']['guid']
            note_log_display_name = note_log_el['properties'].get('displayName',"")
            note_log_qualified_name = note_log_el['properties']['qualifiedName']
            note_log_description = note_log_el['properties'].get('description',"")

        return {
            "note_log_name": note_log_display_name,
            "note_log_description": note_log_description,
            "note_log_qualified_name": note_log_qualified_name,
            "note_log_guid": note_log_guid,
        }

    def _extract_element_properties_for_note_logs(self, element: dict, columns_struct: dict):
        note_log_qualified_name = None
        note_log_guid = None
        note_log_display_name = None
        note_log_description = None

        note_log_el = element.get("presentInNoteLogs",{})[0].get("relatedElement",None)
        if note_log_el:
            note_log_guid = note_log_el['elementHeader']['guid']
            note_log_display_name = note_log_el['properties'].get('displayName',"")
            note_log_qualified_name = note_log_el['properties']['qualifiedName']
            note_log_description = note_log_el['properties'].get('description',"")

        return {
            "note_log_name": note_log_display_name,
            "note_log_description": note_log_description,
            "note_log_qualified_name": note_log_qualified_name,
            "note_log_guid": note_log_guid,
        }
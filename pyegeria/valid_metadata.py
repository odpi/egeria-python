"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""

import asyncio

from pyegeria._server_client import ServerClient
from pyegeria.models import SearchStringRequestBody, ResultsRequestBody, FilterRequestBody, GetRequestBody, \
    DeleteElementRequestBody
from pyegeria.utils import dict_to_markdown_list, dynamic_catch, body_slimmer
from pyegeria._exceptions import (PyegeriaException)
from pyegeria._globals import max_paging_size, NO_ELEMENTS_FOUND
from pyegeria.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.output_formatter import (
    generate_output,
    _extract_referenceable_properties,
    populate_columns_from_properties,
    get_required_relationships,
)


class ValidMetadataManager(ServerClient):
    """The Valid Metadata OMVS provides APIs for retrieving and updating lists of valid metadata values.
        For more details see: https://egeria-project.org/guides/planning/valid-values/overview/

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
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        self.valid_m_command_base: str = f"/api/open-metadata/valid-metadata"
        self.page_size = max_paging_size
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)

        # Default entity label used by output formatter when a specific type is not supplied
        self.REFERENCEABLE_LABEL = "Referenceable"

    # ---------------------------
    # Output formatting helpers
    # ---------------------------
    def _extract_referenceable_output_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate requested columns from a generic Referenceable element.
        Mirrors the approach used in other managers so report specs work consistently.
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])

        # Header-derived fields (GUID, qualifiedName, displayName, etc.)
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")

        # Relationships (generic handler fills requested relationship-driven columns if present)
        col_data = get_required_relationships(element, col_data)

        # Mermaid graph support if present
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaid":
                col["value"] = mermaid_val
                break

        return col_data

    def _generate_referenceable_output(
        self,
        elements: dict | list[dict],
        filter: str | None,
        element_type_name: str | None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> str | list[dict]:
        """Resolve format set and generate output for Referenceable-derived elements.

        This aligns with the formatting workflow used by classification_manager and automated_curation.
        """
        entity_type = element_type_name or self.REFERENCEABLE_LABEL

        # Resolve output format set
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_spec(element_type_name, output_format)
        else:
            output_formats = select_report_spec(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_referenceable_output_properties,
            None,
            output_formats,
        )

    def _extract_valid_value_output_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate requested columns for valid value metadata. """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])

        # if isinstance(element, dict):
        #     element = [element]

        category = element.get("category", "---")
        display_name = element.get("displayName", "---")
        description = element.get("description", "---")
        preferred_value = element.get("preferredValue", "---")
        data_type = element.get("dataType", "---")
        is_case_sensitive = element.get("isCaseSensitive", "---")
        additional_properties = element.get("additionalProperties", "---")
        property_name = element.get("propertyName", "---")
        map_name = element.get("mapName", "---")
        type_name = element.get("typeName", "---")


        for column in columns_list:
            key = column.get("key")
            match key:
                case 'category':
                    column["value"] = element.get("category", "---")
                case 'display_name':
                    column["value"] = element.get("displayName", "---")
                case 'description':
                    column["value"] = element.get("description", "---")
                case 'preferred_value':
                    column["value"] = element.get("preferredValue", "---")
                case 'data_type':
                    column["value"] = element.get("dataType", "---")
                case 'is_case_sensitive':
                    column["value"] = element.get("isCaseSensitive", "---")
                case 'property_name':
                    column["value"] = element.get("propertyName", "---")
                case 'additional_properties':
                    additional_properties = element.get("additionalProperties", "---")
                    if isinstance(additional_properties, dict):
                        column["value"] = dict_to_markdown_list(additional_properties)
                    else:
                        column["value"] = additional_properties

        return col_data

    def _generate_valid_value_output(
        self,
        elements: dict | list[dict],
        filter: str | None,
        element_type_name: str | None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Resolve format set and generate output for Referenceable-derived elements.

        This aligns with the formatting workflow used by classification_manager and automated_curation.
        """
        entity_type = element_type_name or self.REFERENCEABLE_LABEL

        # Resolve output format set
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_spec(element_type_name, output_format)
        else:
            output_formats = select_report_spec(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            # self._extract_valid_value_output_properties,
            populate_columns_from_properties,
            None,
            output_formats,
        )

    def _extract_entity_output_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate requested columns from a generic Referenceable element.
        Mirrors the approach used in other managers so report specs work consistently.
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])

        # Header-derived fields (GUID, qualifiedName, displayName, etc.)
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")

        # Relationships (generic handler fills requested relationship-driven columns if present)
        col_data = get_required_relationships(element, col_data)

        # Mermaid graph support if present
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaidGraph":
                col["value"] = mermaid_val
                break

        return col_data

    def _generate_entity_output(
        self,
        elements: dict | list[dict],
        filter: str | None,
        element_type_name: str | None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Resolve format set and generate output for Referenceable-derived elements.

        This aligns with the formatting workflow used by classification_manager and automated_curation.
        """
        entity_type = element_type_name if element_type_name is not None else self.REFERENCEABLE_LABEL
        # Remove a layer of nesting in the JSON if the output_format is not MERMAID
        if output_format != "MERMAID":
            elements = elements["typeDefs"] if output_format != "MERMAID" else elements

        # Resolve output format set
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_spec(element_type_name, output_format)
        else:
            output_formats = select_report_spec(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_entity_output_properties,
            None,
            output_formats,
        )

    async def _async_setup_valid_metadata_value(
        self, property_name: str, type_name: str, body: dict
    ):
        """Create or update the valid value for a particular open metadata property name. If the typeName is null,
        this valid value applies to properties of this name from all types. The valid value is stored in the
        preferredValue property. If a valid value is already set up for this property (with overlapping effective dates)
        then the valid value is updated. Async Version.

        Parameters
        ----------
        property_name : str
            The name of the property for which the valid metadata value is being set up.
        type_name : str
            The name of the type for the valid metadata value.
        body : dict
            The body of the request containing the details of the valid metadata value.


        Returns
        -------
        No value is returned.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        Notes
        -----

        Payload structure similar to:
        {
          "displayName": "",
          "description": "",
          "preferredValue": "",
          "dataType": "",
          "isCaseSensitive": false,
          "isDeprecated" : false,
          "effectiveFrom" : "2024-09-30T20:00:00.000Z",
          "effectiveTo" : "2025-09-30T20:00:00.000Z",
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/setup-value/{property_name}?"
            f"typeName={type_name}"
        )

        await self._async_make_request("POST", url, body)
        return

    def setup_valid_metadata_value(
        self, property_name: str, type_name: str, body: dict
    ):
        """Create or update the valid value for a particular open metadata property name. If the typeName is null,
        this valid value applies to properties of this name from all types. The valid value is stored in the
        preferredValue property. If a valid value is already set up for this property (with overlapping effective dates)
        then the valid value is updated.

        Parameters
        ----------
        property_name : str
            The name of the property for which the valid metadata value is being set up.
        type_name : str
            The name of the type for the valid metadata value.
        body : dict
            The body of the request containing the details of the valid metadata value.


        Returns
        -------
        None - this method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        Payload structure similar to:
        {
          "displayName": "",
          "description": "",
          "preferredValue": "",
          "dataType": "",
          "isCaseSensitive": false,
          "isDeprecated" : false,
          "additionalProperties": {
            "colour": "purple"
            }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_valid_metadata_value(property_name, type_name, body)
        )
        return

    async def _async_setup_valid_metadata_map_name(
        self, property_name: str, type_name: str, body: dict
    ):
        """Create or update the valid value for a name that can be stored in a particular open metadata property name.
        This property is of type map from name to string. The mapName is stored in the preferredValue property of
        validMetadataValue. If the typeName is null, this valid value applies to properties of this name from any
        open metadata type. If a valid value is already set up for this property (with overlapping effective dates)
        then the valid value is updated. Async Version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        body : dict
            The metadata map setup data.


        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        Notes
        -----

        Body strycture similar to:

        {
          "displayName": "",
          "description": "",
          "preferredValue": "put mapName value here",
          "dataType": "",
          "isCaseSensitive": false,
          "isDeprecated" : false,
          "effectiveFrom" : "2024-09-30T20:00:00.000Z",
          "effectiveTo" : "2025-09-30T20:00:00.000Z"
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/setup-map-name/{property_name}?"
            f"typeName={type_name}"
        )

        await self._async_make_request("POST", url, body)
        return

    def setup_valid_metadata_map_name(
        self, property_name: str, type_name: str, body: dict
    ):
        """Create or update the valid value for a name that can be stored in a particular open metadata property name.
        This property is of type map from name to string. The mapName is stored in the preferredValue property of
        validMetadataValue. If the typeName is null, this valid value applies to properties of this name from any
        open metadata type. If a valid value is already set up for this property (with overlapping effective dates)
        then the valid value is updated.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        body : dict
            The metadata map setup data.


        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        Notes
        -----

        Body strycture similar to:

        {
          "displayName": "",
          "description": "",
          "preferredValue": "put mapName value here",
          "dataType": "",
          "isCaseSensitive": false,
          "isDeprecated" : false
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_valid_metadata_map_name(property_name, type_name, body)
        )
        return

    async def _async_setup_valid_metadata_map_value(
        self, property_name: str,  map_name: str, type_name: str, body: dict
    ) -> None:
        """Create or update the valid value for a name that can be stored in a particular open metadata property name.
        This property is of type map from name to string.
        The valid value is stored in the preferredValue property of validMetadataValue.
        If the typeName is null, this valid value applies to properties of this name from any open metadata type.
        If a valid value is already set up for this property (with overlapping effective dates) then the valid value
        is updated.  Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map we associate a value with.
        body : dict
            The metadata map setup data.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        Notes
        -----

        Body strycture similar to:

        {
          "displayName": "",
          "description": "",
          "preferredValue": "put mapName value here",
          "dataType": "",
          "isCaseSensitive": false,
          "effectiveFrom" : "2024-09-30T20:00:00.000Z",
          "effectiveTo" : "2025-09-30T20:00:00.000Z"
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/setup-map-value/"
            f"{property_name}/{map_name}?typeName={type_name}"
        )

        await self._async_make_request("POST", url, body)
        return

    def setup_valid_metadata_map_value(
        self, property_name: str,  map_name: str, type_name: str, body: dict
    ) -> None:
        """Create or update the valid value for a name that can be stored in a particular open metadata property name.
        This property is of type map from name to string.
        The valid value is stored in the preferredValue property of validMetadataValue.
        If the typeName is null, this valid value applies to properties of this name from any open metadata type.
        If a valid value is already set up for this property (with overlapping effective dates) then the valid value
        is updated.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map we associate a value with.
        body : dict
            The metadata map setup data.


        Returns
        -------
        None
            This method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        Notes
        -----

        Body structure similar to:

        {
          "displayName": "",
          "description": "",
          "preferredValue": "put mapName value here",
          "dataType": "",
          "isCaseSensitive": false,
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_valid_metadata_map_value(
                property_name, map_name, type_name, body
            )
        )
        return

    async def _async_clear_valid_metadata_value(
        self, property_name: str, type_name: str, preferred_value: str
    ) -> None:
        """Remove a valid value for a property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The reference valye to remove.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/clear-value/"
            f"{property_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        await self._async_make_request("POST", url)
        return

    def clear_valid_metadata_value(
        self, property_name: str, type_name: str, preferred_value: str
    ) -> None:
        """Remove a valid value for a property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The reference valye to remove.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action


        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_valid_metadata_value(
                property_name, type_name, preferred_value
            )
        )
        return

    async def _async_clear_valid_metadata_map_name(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
    ):
        """Remove a valid map name value for a property. The match is done on MapName name. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map we associate a value with.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/clear-map-name/"
            f"{property_name}?typeName={type_name}&mapName={map_name}"
        )

        await self._async_make_request("POST", url)
        return

    def clear_valid_metadata_map_name(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
    ):
        """Remove a valid map name value for a property. The match is done on MapName name.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map we associate a value with.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_valid_metadata_map_name(
                property_name, type_name, map_name
            )
        )
        return

    async def _async_clear_valid_metadata_map_value(
        self, property_name: str, type_name: str, map_name: str, preferred_value: str
    ):
        """Remove a valid map name value for a property.  The match is done on preferred name. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of the map to remove.
        preferred_value: str
            The value to remove.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaServerException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/clear-map-value/"
            f"{property_name}/{map_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        await self._async_make_request("POST", url)
        return

    def clear_valid_metadata_map_value(
        self, property_name: str, type_name: str, map_name:str, preferred_value: str
    ):
        """Remove a valid map name value for a property.  The match is done on preferred name.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of the map to remove.
        preferred_value: str
            The value to remove.

        Returns
        -------
        None - This method does not return a value.

        Raises
        ------
        PyegeriaServerException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_valid_metadata_map_value(
                property_name, type_name, map_name, preferred_value
            )
        )
        return

    async def _async_validate_metadata_value(
        self, property_name: str, type_name: str, actual_value: str
    ) -> bool | str:
        """Validate whether the value found in an open metadata property is valid. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        actual_value: str
            The value to validate.

        Returns
        -------
        Bool - True, if validated.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/validate-value/"
            f"{property_name}?typeName={type_name}&actualValue={actual_value}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("flag", "No flag found")

    def validate_metadata_value(
        self, property_name: str, type_name: str, actual_value: str
    ) -> bool | str:
        """Validate whether the value found in an open metadata property is valid.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        actual_value: str
            The value to validate.

        Returns
        -------
        Bool - True, if validated.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_validate_metadata_value(
                property_name, type_name, actual_value
            )
        )
        return response

    async def _async_validate_metadata_map_name(
        self, property_name: str, type_name: str, map_name: str
    ) -> bool | str:
        """Validate whether the name found in an open metadata map property is valid. Async version.

         Parameters
         ----------
         property_name : str
             The name of the property to setup metadata map.
         type_name : str
             The type name of the property.
        map_name: str
             The name of a map to validate.

         Returns
         -------
         Bool - True, if validated.

         Raises
         ------
         PyegeriaInvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
         PyegeriaAPIException
           Raised by the server when an issue arises in processing a valid request
         NotAuthorizedException
           The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/validate-map-name/"
            f"{property_name}?typeName={type_name}&mapName={map_name}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("flag", "No flag found")

    def validate_metadata_map_name(
        self, property_name: str, type_name: str, map_name: str
    ) -> bool | str:
        """Validate whether the name found in an open metadata map property is valid.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map to validate.

        Returns
        -------
        Bool - True, if validated.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_validate_metadata_map_name(property_name, type_name, map_name)
        )
        return response

    async def _async_validate_metadata_map_value(
        self, property_name: str, type_name: str, map_name: str, actual_value: str
    ) -> bool | str:
        """Validate whether the name found in an open metadata map property is valid. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map to validate.
        actual_value: str
            The actual value associated with the map to validate.

        Returns
        -------
        Bool - True, if validated.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/validate-map-value/"
            f"{property_name}/{map_name}?typeName={type_name}&actualValue={actual_value}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("flag", "No flag found")

    def validate_metadata_map_value(
        self, property_name: str, type_name: str, map_name: str, actual_value: str
    ) -> bool | str:
        """Validate whether the name found in an open metadata map property is valid.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            The name of a map to validate.
        actual_value: str
             The actual value associated with the map to validate.

        Returns
        -------
        Bool - True, if validated.

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_validate_metadata_map_value(
                property_name, type_name, map_name, actual_value
            )
        )
        return response

    async def _async_get_valid_metadata_value(
        self,
        property_name: str,
        type_name: str,
        preferred_value: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid value for a property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The preferred value of the property.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-value/"
            f"{property_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        response = await self._async_make_request("GET", url)
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_valid_value_output(element, preferred_value, "ValidMetadataValue",
                                                       output_format, report_spec)
        return element

    def get_valid_metadata_value(
        self,
        property_name: str,
        type_name: str,
        preferred_value: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid value for a property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The preferred value of the property.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_valid_metadata_value(
                property_name, type_name, preferred_value, output_format=output_format, report_spec=report_spec
            )
        )
        return response

    async def _async_get_valid_metadata_map_name(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid name for a map property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            Map to return details of.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-map-name/"
            f"{property_name}?typeName={type_name}&mapName={map_name}"
        )

        response = await self._async_make_request("GET", url)
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_valid_value_output(element, map_name, "ValidMetadataValue",
                                                       output_format, report_spec)
        return element

    def get_valid_metadata_map_name(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid name for a map property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            Map to return details of.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_valid_metadata_map_name(property_name, type_name, map_name,
                                                    output_format=output_format, report_spec=report_spec)
        )
        return response

    async def _async_get_valid_metadata_map_value(
        self,
        property_name: str,
        type_name: str,
        preferred_value: str,
        map_name: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid value for a map property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            Preferred value to return details of.
        map_name: str
            Map to return details of.
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        Args:
            map_name ():

        """

        url = (
            f'{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-map-value/'
            f'{property_name}/{map_name}'
            # f'?typeName={type_name}&preferredValue={preferred_value}'
        )
        params = { "typeName": type_name , "preferredValue": preferred_value }
        response = await self._async_make_request("GET", url, params = params)
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_referenceable_output(element, preferred_value, "ValidMetadataValue",
                                                       output_format, report_spec)
        return element

    def get_valid_metadata_map_value(
        self,
        property_name: str,
        type_name: str,
        preferred_value: str,
        map_name: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | str | list[dict]:
        """Retrieve details of a specific valid value for a map property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            Preferred value to return details of.
        map_name: str
            Map to return details of.

        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

        Raises
        ------
        PyegeriaException

        Args:
            map_name ():

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_valid_metadata_map_value(property_name, type_name, preferred_value, map_name,
                                                     output_format=output_format, report_spec=report_spec)
        )
        return response

    async def _async_get_valid_metadata_values(
        self,
        property_name: str,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | list | str:
        """Retrieve list of values for the property. Async version.

        Parameters
        ----------
        property_name: str
            The property to query.
        type_name: str, opt
            The Open Metadata type to get the property values for. If not specified then all property values
            will be returned.
        start_from: int, opt
            Page to start from.
        page_size: int, opt
             Number of elements to return per page - if None, then default for class will be used.


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

        A list of collections linked off of the supplied element.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/get-valid-metadata-values/{property_name}"
            f"?typeName={type_name}&startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("elements", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_valid_value_output(elements, property_name, "ValidMetadataValue",
                                                       output_format, report_spec)
        return elements

    def get_valid_metadata_values(
        self,
        property_name: str,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> dict | list | str:
        """Retrieve list of values for the property.

        Parameters
        ----------
        property_name: str
            The property to query.
        type_name: str, opt
            The Open Metadata type to get the property values for. If not specified then all property values
            will be returned.
        start_from: int, opt
            Page to start from.
        page_size: int, opt
             Number of elements to return per page - if None, then default for class will be used.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

        A list of collections linked off of the supplied element.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_valid_metadata_values(
                property_name, type_name, start_from, page_size, output_format=output_format, report_spec=report_spec
            )
        )
        return resp

    async def _async_get_consistent_metadata_values(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
        preferred_value: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> list | str:
        """Retrieve all the consistent valid values for the requested property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve the valid values for.
        type_name : str
            The open metadata type that the property is associated with.
        map_name : str
            A valid map name that associates a property with a value.
        preferred_value : str
            Preferred value to return details of.
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        params = {
            "typeName": type_name,
            "mapName": map_name,
            "preferredValue": preferred_value,
            "startFrom": str(start_from),
            "pageSize": str(page_size)
        }
        params_s = body_slimmer(params)
        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/{property_name}/"
            f"consistent-metadata-values"
        )

        resp = await self._async_make_request("GET", url, params=params_s)
        elements = resp.json().get("elements", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_referenceable_output(elements, preferred_value, "ValidMetadataValue",
                                                       output_format, report_spec)
        return elements

    def get_consistent_metadata_values(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
        preferred_value: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
    ) -> list | str:
        """Retrieve all the consistent valid values for the requested property.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve the valid values for.
        type_name : str
            The open metadata type that the property is associated with.
        map_name : str
            A valid map name that associates a property with a value.
        preferred_value : str


        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

        A list of collections linked off of the supplied element.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_consistent_metadata_values(
                property_name,
                type_name,
                map_name,
                preferred_value,
                start_from,
                page_size,
                output_format=output_format,
                report_spec=report_spec,
            )
        )
        return resp

    async def _async_set_consistent_metadata_values(
        self,
        property_name1: str,
        type_name1: str,
        map_name1: str ,
        preferred_value1: str,
        property_name2: str,
        type_name2: str ,
        map_name2: str,
        preferred_value2: str,
    ) -> None:
        """Set up consistent metadata values relationship between the two property values. Async version.

        Parameters
        ----------
        property_name1 : str
            The name of the first property.
        property_name2 : str
            The name of the second property.
        type_name1 : str
            The open metadata type that property1 is associated with.
        map_name1 : str
            First valid map name.
        preferred_value1 : str
            First preferred value.
        type_name2 : str
            The open metadata type that property2 is associated with.
        map_name2 : str
            Second valid map name.
        preferred_value2 : str
            Second preferred value.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        params = {
           "typeName1": type_name1,
           "typeName2": type_name2,
           "mapName1": map_name1,
           "mapName2": map_name2,
           "preferredValue1": preferred_value1,
           "preferredValue2": preferred_value2,
       }
        params_s = body_slimmer(params)

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/{property_name1}/"
            f"consistent-metadata-values/{property_name2}"
        )

        await self._async_make_request("POST", url, params=params_s)
        return

    def set_consistent_metadata_values(
        self,
        property_name1: str,
        type_name1: str,
        map_name1: str,
        preferred_value1: str,
        property_name2: str,
        type_name2: str,
        map_name2: str,
        preferred_value2: str,
    ) -> None:
        """Set up consistent metadata values relationship between the two property values.

        Parameters
        ----------
        property_name1 : str
            The name of the first property.
        property_name2 : str
            The name of the second property.
        type_name1 : str
            The open metadata type that property1 is associated with.
        map_name1 : str
            First valid map name.
        preferred_value1 : str
            First preferred value.
        type_name2 : str
            The open metadata type that property2 is associated with.
        map_name2 : str
            Second valid map name.
        preferred_value2 : str
            Second preferred value.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_consistent_metadata_values(property_name1, type_name1, map_name1, preferred_value1,
                                                       property_name2, type_name2, map_name2, preferred_value2)
        )
        return

    #
    # Get all ...
    #
    async def _async_get_all_entity_types(self,
                                          output_format: str = "JSON",
                                          report_spec: dict | str | None = None) -> dict | list | str:
        """Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types"

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefs", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            # Treat returned structure generically as TypeDef listing
            return self._generate_entity_output(elements, None, "TypeDef", output_format, report_spec)
        return elements

    def get_all_entity_types(self,
                             output_format: str = "JSON",
                             report_spec: dict | str | None = None) -> dict | list | str:
        """Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_all_entity_types(output_format=output_format,
                                                                        report_spec=report_spec))
        return resp

    async def _async_get_all_entity_defs(self,
                                         output_format: str = "JSON",
                                         report_spec: dict | str | None = None) -> dict | list | str:
        """GReturns all the entity type definitions. Async version.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/entity-defs"

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, None, "TypeDef", output_format, report_spec)
        return elements

    def get_all_entity_defs(self,
                            output_format: str = "JSON",
                            report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the entity type definitions.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_all_entity_defs(output_format=output_format,
                                                                       report_spec=report_spec))
        return resp

    async def _async_get_all_relationship_defs(self,
                                               output_format: str = "JSON",
                                               report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the relationship type definitions. Async version.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/relationship-defs"

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, None, "TypeDef", output_format, report_spec)
        return elements

    def get_all_relationship_defs(self,
                                  output_format: str = "JSON",
                                  report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the relationship type definitions.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_all_relationship_defs(output_format=output_format,
                                                                             report_spec=report_spec))
        return resp

    async def _async_get_all_classification_defs(self,
                                                 output_format: str = "JSON",
                                                 report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the classification type definitions. Async version.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/classification-defs"

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, None, "TypeDef", output_format, report_spec)
        return elements

    def get_all_classification_defs(self,
                                    output_format: str = "JSON",
                                    report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the classification type definitions.

        Parameters
        ----------


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_all_classification_defs(output_format=output_format,
                                                                               report_spec=report_spec))
        return resp

    #
    # Get valid ...
    #

    async def _async_get_sub_types(self, type_name: str,
                                   output_format: str = "JSON",
                                   report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the TypeDefs for a specific subtype.  If a null result is returned it means the
            type has no subtypes. Async version.

        Parameters
        ----------
        type_name : str
            Type name to retrieve the sub-types for.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified type.

        Raises
        ------

        PyegeriaException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/sub-types/"
            f"{type_name}"
        )

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, type_name, "TypeDef", output_format, report_spec)
        return elements

    def get_sub_types(self, type_name: str,
                      output_format: str = "JSON",
                      report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the TypeDefs for a specific subtype.  If a null result is returned it means the
            type has no subtypes.

        Parameters
        ----------
        type_name : str
            Type name to retrieve the sub-types for.

        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified type.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_sub_types(type_name, output_format=output_format, report_spec=report_spec)
        )
        return resp

    async def _async_get_valid_relationship_types(self, entity_type: str,
                                                  output_format: str = "JSON",
                                                  report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the TypeDefs for relationships that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the valid relationships for.


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified entity type.

        Raises
        ------

        PyegeriaException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/{entity_type}/"
            f"attached-relationships"
        )

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, entity_type, "TypeDef", output_format, report_spec)
        return elements

    def get_valid_relationship_types(self, entity_type: str,
                                     output_format: str = "JSON",
                                     report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the TypeDefs for relationships that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                 The name of the entity type to retrieve the valid relationships for.
             : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.

            Parameters
            ----------
            output_format: str, default = "JSON"
                Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
            report_spec: dict | str | None
                Output format set to use. If None, the default output format set is used.

            Returns
            -------
            List | str

                A list of TypeDefs that can be attached to the specified entity type.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_valid_relationship_types(entity_type, output_format=output_format, report_spec=report_spec)
        )
        return resp

    async def _async_get_valid_classification_types(
        self, entity_type: str,
        output_format: str = "JSON",
        report_spec: dict | str | None = None
    ) -> dict | list | str:
        """Returns all the TypeDefs for classifications that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the classifications for.


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        List | str

            A list of classifications that can be attached to the specified entity type.

        Raises
        ------

        PyegeriaException

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/{entity_type}/"
            f"attached-classifications"
        )

        resp = await self._async_make_request("GET", url)
        elements = resp.json().get("typeDefList", NO_ELEMENTS_FOUND)
        if elements == NO_ELEMENTS_FOUND or elements is None or elements == []:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(elements, entity_type, "TypeDef", output_format, report_spec)
        return elements

    def get_valid_classification_types(self, entity_type: str,
                                       output_format: str = "JSON",
                                       report_spec: dict | str | None = None) -> dict | list | str:
        """Returns all the TypeDefs for classifications that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                The name of the entity type to retrieve the classifications for.
             : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.

            Parameters
            ----------
            output_format: str, default = "JSON"
                Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
            report_spec: dict | str | None
                Output format set to use. If None, the default output format set is used.

            Returns
            -------
            List | str

                A list of classifications that can be attached to the specified entity type.

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_valid_classification_types(entity_type, output_format=output_format,
                                                       report_spec=report_spec)
        )
        return resp

    async def _async_get_typedef_by_name(self, entity_type: str,
                                         output_format: str = "JSON",
                                         report_spec: dict | str | None = None) -> dict | str | list[dict]:
        """Return the TypeDef identified by the unique name.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        dict | str

            The typedef associated with the type name

        Raises
        ------

        PyegeriaException

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/name/{entity_type}"

        resp = await self._async_make_request("GET", url)
        element = resp.json().get("typeDef", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND or element is None:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(element, entity_type, "TypeDef", output_format, report_spec)
        return element

    def get_typedef_by_name(self, entity_type: str,
                            output_format: str = "JSON",
                            report_spec: dict | str | None = None) -> dict | str | list[dict]:
        """Return the TypeDef identified by the unique name.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.


        Parameters
        ----------
        output_format: str, default = "JSON"
            Type of output to return. For example: "JSON", "DICT", "MD", "MD_TABLE", etc.
        report_spec: dict | str | None
            Output format set to use. If None, the default output format set is used.

        Returns
        -------
        dict | str

            The typedef associated with the type name

        Raises
        ------

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_typedef_by_name(entity_type,
                                                                       output_format=output_format,
                                                                       report_spec=report_spec))
        return resp


    #
    #  Specification Properties
    #

    async def _async_setup_specification_property(
        self, element_guid: str,  body: dict
    ):
        """Create a replacementAttribute specification property and attach it to an element.
           There are several different payloads to support setting up different use cases.
           see https://egeria-project.org/services/omvs/valid-metadata/overview/?h=valid#maintaining-specification-properties
           Async Version.

        Parameters
        ----------
        element_guid : str
            Element to attach the property to.
        body : dict
            The definition of the specification property to attach.

        Returns
        -------
        No value is returned.

        Raises
        ------
        PyegeriaException


        Notes
        -----

        Example payload structures for element:
        {
          "class" : "ReplacementAttribute",
          "name": "replacement attribute name",
          "description": "replacement attribute description",
          "datatype": "data type of the attribute, eg string",
          "example": "this is an example - often it is the default value for an optional replacement attribute.",
          "required": false,
          "otherPropertyValues": {
            "property1" : "propertyValue1",
            "property2" : "propertyValue2"
          }
        }

        for Template:
            {
              "class" : "SupportedTemplate",
              "name": "template name",
              "description": "template description",
              "openMetadataTypeName": "open metadata type of the element produced by the template",
              "required": false,
              "otherPropertyValues": {
                "property1" : "propertyValue1",
                "property2" : "propertyValue2"
              }
            }
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/elements/{element_guid}/specification-properties"

        await self._async_make_request("POST", url, body)
        return

    def setup_specification_property(self, element_guid: str, body: dict):
        """ Create a replacementAttribute specification property and attach it to an element.
            There are several different payloads to support setting up different use cases.
            see https://egeria-project.org/services/omvs/valid-metadata/overview/?h=valid#maintaining-specification-properties
            Async Version.
            Parameters
            ----------
            element_guid : str
                Element to attach the property to.
            body : dict
                The definition of the specification property to attach.

            Returns
            -------
            No value is returned.

            Raises
            ------
            PyegeriaException

            Notes
            -----
                Example payload structures for element:
                {
                  "class" : "ReplacementAttribute",
                  "name": "replacement attribute name",
                  "description": "replacement attribute description",
                  "datatype": "data type of the attribute, eg string",
                  "example": "this is an example - often it is the default value for an optional replacement attribute.",
                  "required": false,
                  "otherPropertyValues": {
                    "property1" : "propertyValue1",
                    "property2" : "propertyValue2"
                  }
                }

            for Template:
            {
              "class" : "SupportedTemplate",
              "name": "template name",
              "description": "template description",
              "openMetadataTypeName": "open metadata type of the element produced by the template",
              "required": false,
              "otherPropertyValues": {
                "property1" : "propertyValue1",
                "property2" : "propertyValue2"
              }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_specification_property(element_guid, body)
        )

    async def _async_delete_specification_property(
        self, spec_property_guid: str,  body: dict | DeleteElementRequestBody = None, cascade: bool = False)->None:
        """Create a replacementAttribute specification property and attach it to an element.
           There are several different payloads to support setting up different use cases.
           see https://egeria-project.org/services/omvs/valid-metadata/overview/?h=valid#maintaining-specification-properties
           Async Version.

        Parameters
        ----------
        spec_property_guid : str
            Element to delete.
        body : dict | DeleteElementRequestBody
            Finer control over the delete.
        cascade: bool
            Delete all elements that depend on this element.
        Returns
        -------
        No value is returned.

        Raises
        ------
        PyegeriaException


        Notes
        -----

        Example payload structures:
        {
          "class": "DeleteElementRequestBody",
          "cascadeDelete": false,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/{spec_property_guid}/delete")

        await self._async_delete_element_request(url, body, cascade)


    def delete_specification_property(self, spec_property_guid: str, body: dict | DeleteElementRequestBody, cascade: bool = False)->None:
        """ Create a replacementAttribute specification property and attach it to an element.
            There are several different payloads to support setting up different use cases.
            see https://egeria-project.org/services/omvs/valid-metadata/overview/?h=valid#maintaining-specification-properties
            Async Version.
            Parameters
            ----------
            spec_property_guid : str
                Element to delete.
            body : dict | DeleteElementRequestBody
                Finer control over the delete.
            cascade: bool
                Delete all elements that depend on this element.

            Returns
            -------
            No value is returned.

            Raises
            ------
            PyegeriaException

            Notes
            -----
                Example payload structures:
                {
                  "class": "DeleteElementRequestBody",
                  "cascadeDelete": false,
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_specification_property(spec_property_guid, body, cascade)
        )

    async def _async_find_specification_property(self, search_string: str = "*", classification_names: list[str] = None,
                                      metadata_element_subtypes: list[str] = None,
                                      starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      report_spec: str | dict = None,
                                      body: dict | SearchStringRequestBody = None) -> list | str:
        """ Return the list of specification properties containing the supplied string.
            This method can either be used with a body, allowing full control, or with the individual parameters.
            If the body is provided it will be used and the search_string will be ignored. Async version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all collections (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------
            PyegeriaException
        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/by-search-string")
        response = await self._async_find_request(url, _type="SpecificationPropertyValue",
                                                  _gen_output=self._generate_valid_value_output,
                                                  search_string=search_string,
                                                  include_only_classification_names=classification_names,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response


    def find_specification_property(self, search_string: str = "*", classification_names: list[str] = None,
                                          metadata_element_subtypes: list[str] = None,
                                          starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                          start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                          report_spec: str | dict = None,
                                          body: dict | SearchStringRequestBody = None) -> list | str:
        """ Return the list of specification properties containing the supplied string.
            This method can either be used with a body, allowing full control, or with the individual parameters.
            If the body is provided it will be used and the search_string will be ignored. Async version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all collections (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_subtypes: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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
        report_spec: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------
            PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
                self._async_find_specification_property(search_string,classification_names,
                                                        metadata_element_subtypes,starts_with,
                                                        ends_with,ignore_case,start_from,
                                                        page_size,output_format,report_spec,
                                                        body)
            )
        return response

    @dynamic_catch
    async def _async_get_specification_property_by_type(self, spec_property_type: str, body: dict | ResultsRequestBody = None,
                                              start_from: int = 0,
                                              page_size: int = 0, output_format: str = "JSON",
                                              report_spec: str | dict = None) -> list | str:
        """ Return the list of specification properties containing the supplied type. Async version.

            Parameters
            ----------
            spec_property_type: str,
                identity of the specification property type to return members for.
            body: dict | ResultsRequestBody, optional, default = None
                Providing the body allows full control of the request and replaces filter parameters.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
            report_spec: dict , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

           Results based on the output format.

            Raises
            ------
                PyegeriaException
            Notes:
            -----
                Body sample:
            {
              "class": "ResultsRequestBody",
              "startFrom": 0,
              "pageSize": 0,
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }
            """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/by-type?specificationPropertyType={spec_property_type}")
        response = await self._async_get_results_body_request(url, _type="SpecificationPropertyValue",
                                                              _gen_output=self._generate_valid_value_output,
                                                              start_from=start_from, page_size=page_size,
                                                              output_format=output_format,
                                                              report_spec=report_spec,
                                                              body=body)

        return response

    def get_specification_property_by_type(self, spec_property_type:str, body: dict | ResultsRequestBody = None,
                                 start_from: int = 0,
                                 page_size: int = 0, output_format: str = "JSON",
                                 report_spec: str | dict = None) -> list | str:
        """ Return the list of specification properties containing the supplied type.


        Parameters
        ----------
        spec_property_type: str,
            identity of the specification property type to return members for.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         report_spec: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A graph anchored in the collection.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
            self._async_get_specification_property_by_type(spec_property_type, body, start_from, page_size,
                                                 output_format, report_spec))
    @dynamic_catch
    async def _async_get_specification_property_by_name(self, name: str, start_from: int = 0, page_size: int = 0,
                                              category: str = None, classification_names: list[str]= None,
                                              body: dict | FilterRequestBody = None, output_format: str = "JSON",
                                              report_spec: str | dict = None) -> list | str:
        """ Return the list of specification properties containing the supplied name. Async version.

        Parameters
        ----------
        name: str
            The name of the specification property to retrieve.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            If supplied, adds addition request details - for instance, to filter the results on collectionType
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict = None), optional, default = None
            The desired output columns/fields to include.

        Returns
        -------
        List

        A list of specification properties containing the supplied name.

        Raises
        ------
        PyegeriaAPIException

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

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/by-name")
        response = await self._async_get_name_request(url, _type="SpecificationPropertyValue",
                                                      _gen_output=self._generate_valid_value_output,
                                                      filter_string=name,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response


    def get_specification_property_by_name(self, name: str, start_from: int = 0, page_size: int = 0,
                                              category: str = None, classification_names: list[str]= None,
                                              body: dict | FilterRequestBody = None, output_format: str = "JSON",
                                              report_spec: str | dict = None) -> list:
        """ Return the list of specification properties containing the supplied name.

            Parameters
            ----------
            name: str
                The name of the specification property to retrieive.
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            body: dict, optional, default = None
                If supplied, adds addition request details - for instance, to filter the results on collectionType
            output_format: str, default = "JSON"
                - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
            report_spec: str | dict = None), optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List

            A list of specification properties containing the supplied name.

            Raises
            ------
            PyegeriaAPIException

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

        Args:
            classification_names ():

            """

        return asyncio.get_event_loop().run_until_complete(
            self._async_get_specification_property_by_name(name, start_from, page_size,
                                                           category, classification_names,
                                                           body,output_format,report_spec)
        )

    @dynamic_catch
    async def _async_get_specification_property_by_guid(self, spec_property_guid: str, element_type: str = None,
                                            body: dict | GetRequestBody = None,
                                            output_format: str = 'JSON',
                                            report_spec: str | dict = None) -> dict | str:
        """Return the properties of a specific collection. Async version.

        Parameters
        ----------
        spec_property_guid: str,
            unique identifier of the property.
        element_type: str, default = None, optional
            type of collection - Collection, DataSpec, Agreement, etc.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the specified property. Returns a string if none found.

        Raises
        ------
        PyegeriaException

        Notes
        ----
        Body sample:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        type = element_type if element_type else "SpecificationPropertyValue"
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/{spec_property_guid}/retrieve")
        response = await self._async_get_guid_request(url, _type=type,
                                                  _gen_output=self._generate_valid_value_output,
                                                  output_format=output_format, report_spec=report_spec,
                                                  body=body)

        return response

    @dynamic_catch
    def get_specification_property_by_guid(self, spec_property_guid: str, element_type: str = None, body: dict | GetRequestBody= None,
                               output_format: str = 'JSON', report_spec: str | dict = None) -> dict | str:
        """ Return the properties of a specific collection. Async version.

            Parameters
            ----------
            spec_property_guid: str,
                unique identifier of the property.
            element_type: str, default = None, optional
                type of element - Collection, DataSpec, Agreement, etc.
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            report_spec: dict , optional, default = None
                The desired output columns/fields to include.


            Returns
            -------
            dict | str

            A JSON dict representing the specified property. Returns a string if none found.

            Raises
            ------
            PyegeriaException

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
            self._async_get_specification_property_by_guid(spec_property_guid, element_type, body,
                                               output_format, report_spec))


    @dynamic_catch
    async def _async_get_specification_property_types(self, output_format: str = 'JSON',
                                                               report_spec: str | dict = None) -> dict | str | list[dict]:
        """Return the list of specification property types. Async version.

        Parameters
        ----------
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         report_spec: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        dict | str

        A JSON dict representing the list of properties.

        Raises
        ------
        PyegeriaException

        Notes
        ----
        Body sample:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/"
               f"specification-properties/type-names")
        resp = await self._async_make_request("GET", url)
        element = resp.json().get("stringMap", NO_ELEMENTS_FOUND)
        if element == NO_ELEMENTS_FOUND or element is None:
            return NO_ELEMENTS_FOUND
        if output_format != "JSON":
            return self._generate_entity_output(element, "ALL", "SpecificationPropertyValues",
                                                output_format, report_spec)
        return element

        return response

    @dynamic_catch
    def get_specification_property_types(self, output_format: str = 'JSON', report_spec: str | dict = None) -> dict | str | list[dict]:
        """Return the list of specification property types.

             Parameters
             ----------
             output_format: str, default = "JSON"
                 - one of "DICT", "MERMAID" or "JSON"
              report_spec: str | dict, optional, default = None
                     The desired output columns/fields to include.

             Returns
             -------
             dict | str

             A JSON dict representing the list of properties.

             Raises
             ------
             PyegeriaException

             Notes
             ----
             Body sample:
             {
               "class": "GetRequestBody",
               "asOfTime": "{{$isoTimestamp}}",
               "effectiveTime": "{{$isoTimestamp}}",
               "forLineage": false,
               "forDuplicateProcessing": false
             }
             """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_specification_property_types(output_format, report_spec))




if __name__ == "__main__":
    print("Main-Valid Metadata Manager")

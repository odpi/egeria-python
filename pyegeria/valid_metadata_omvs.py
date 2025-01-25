"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""
import asyncio

# import json
from pyegeria._client import Client
from pyegeria._globals import max_paging_size


class ValidMetadataManager(Client):
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
        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)

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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        self, property_name: str, type_name: str, map_name: str, body: dict
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        self, property_name: str, type_name: str, map_name: str, body: dict
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
                property_name, type_name, map_name, body
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        self, property_name: str, type_name: str, preferred_value: str
    ):
        """Remove a valid map name value for a property.  The match is done on preferred name. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The value to remove.

        Returns
        -------
        None - This method does not return a value.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/clear-map-value/"
            f"{property_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        await self._async_make_request("POST", url)
        return

    def clear_valid_metadata_map_value(
        self, property_name: str, type_name: str, preferred_value: str
    ):
        """Remove a valid map name value for a property.  The match is done on preferred name.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The value to remove.

        Returns
        -------
        None - This method does not return a value.

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
            self._async_clear_valid_metadata_map_value(
                property_name, type_name, preferred_value
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_clear_valid_metadata_map_value(
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
         InvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
         PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
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
        self, property_name: str, type_name: str, preferred_value: str
    ) -> dict | str:
        """Retrieve details of a specific valid value for a property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The preferred value of the property.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-value/"
            f"{property_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "No value found")

    def get_valid_metadata_value(
        self, property_name: str, type_name: str, preferred_value: str
    ) -> dict | str:
        """Retrieve details of a specific valid value for a property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            The preferred value of the property.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            self._async_get_valid_metadata_value(
                property_name, type_name, preferred_value
            )
        )
        return response

    async def _async_get_valid_metadata_map_name(
        self, property_name: str, type_name: str, map_name: str
    ) -> dict | str:
        """Retrieve details of a specific valid name for a map property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            Map to return details of.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-map-name/"
            f"{property_name}?typeName={type_name}&mapName={map_name}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "No value found")

    def get_valid_metadata_map_name(
        self, property_name: str, type_name: str, map_name: str
    ) -> dict | str:
        """Retrieve details of a specific valid name for a map property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        map_name: str
            Map to return details of.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            self._async_get_valid_metadata_map_name(property_name, type_name, map_name)
        )
        return response

    async def _async_get_valid_metadata_map_value(
        self, property_name: str, type_name: str, preferred_value: str
    ) -> dict | str:
        """Retrieve details of a specific valid value for a map property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            Preferred value to return details of.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/valid-metadata/get-map-value/"
            f"{property_name}?typeName={type_name}&preferredValue={preferred_value}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "No value found")

    def get_valid_metadata_map_value(
        self, property_name: str, type_name: str, preferred_value: str
    ) -> dict | str:
        """Retrieve details of a specific valid value for a map property.

        Parameters
        ----------
        property_name : str
            The name of the property to setup metadata map.
        type_name : str
            The type name of the property.
        preferred_value: str
            Preferred value to return details of.

        Returns
        -------
        Dict if the value is found, otherwise an str indicating the value wasn't found.

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
            self._async_get_valid_metadata_map_value(
                property_name, type_name, preferred_value
            )
        )
        return response

    async def _async_get_valid_metadata_values(
        self,
        property_name: str,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
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

        if page_size is None:
            page_size = self.page_size

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/get-valid-metadata-values/{property_name}"
            f"?typeName={type_name}&startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("GET", url)
        return resp.json().get("elementList", "No elements found")

    def get_valid_metadata_values(
        self,
        property_name: str,
        type_name: str = None,
        start_from: int = 0,
        page_size: int = None,
    ) -> list | str:
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
        resp = loop.run_until_complete(
            self._async_get_valid_metadata_values(
                property_name, type_name, start_from, page_size
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
        page_size: int = None,
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
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/{property_name}/"
            f"consistent-metadata-values?typeName={type_name}&mapName={map_name}&preferredValue={preferred_value}"
            f"&startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("GET", url)
        return resp.json().get("elementList", "No elements found")

    def get_consistent_metadata_values(
        self,
        property_name: str,
        type_name: str,
        map_name: str,
        preferred_value: str,
        start_from: int = 0,
        page_size: int = None,
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
        resp = loop.run_until_complete(
            self._async_get_consistent_metadata_values(
                property_name,
                type_name,
                map_name,
                preferred_value,
                start_from,
                page_size,
            )
        )
        return resp

    async def _async_set_consistent_metadata_values(
        self,
        property_name1: str,
        property_name2: str,
        type_name1: str,
        map_name1: str,
        preferred_value1: str,
        type_name2: str,
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/{property_name1}/"
            f"consistent-metadata-values/{property_name2}?"
            f"typeName1={type_name1}&mapName1={map_name1}&preferredValue1={preferred_value1}&"
            f"typeName1={type_name2}&mapName2={map_name2}&preferredValue2={preferred_value2}"
        )

        await self._async_make_request("POST", url)
        return

    def set_consistent_metadata_values(
        self,
        property_name1: str,
        property_name2: str,
        type_name1: str,
        map_name1: str,
        preferred_value1: str,
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
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_consistent_metadata_values(
                property_name1,
                property_name2,
                type_name1,
                map_name1,
                preferred_value1,
                type_name2,
                map_name2,
                preferred_value2,
            )
        )
        return

    #
    # Get all ...
    #
    async def _async_get_all_entity_types(self) -> list | str:
        """Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types"

        resp = await self._async_make_request("GET", url)
        return resp.json()

    def get_all_entity_types(self) -> list | str:
        """Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

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
        resp = loop.run_until_complete(self._async_get_all_entity_types())
        return resp

    async def _async_get_all_entity_defs(self) -> list | str:
        """GReturns all the entity type definitions. Async version.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/entity-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_entity_defs(self) -> list | str:
        """Returns all the entity type definitions.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

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
        resp = loop.run_until_complete(self._async_get_all_entity_defs())
        return resp

    async def _async_get_all_relationship_defs(self) -> list | str:
        """Returns all the relationship type definitions. Async version.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/relationship-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_relationship_defs(self) -> list | str:
        """Returns all the relationship type definitions.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

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
        resp = loop.run_until_complete(self._async_get_all_relationship_defs())
        return resp

    async def _async_get_all_classification_defs(self) -> list | str:
        """Returns all the classification type definitions. Async version.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/classification-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_classification_defs(self) -> list | str:
        """Returns all the classification type definitions.

        Parameters
        ----------


        Returns
        -------
        List | str

            A list of all entity types.

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
        resp = loop.run_until_complete(self._async_get_all_classification_defs())
        return resp

    #
    # Get valid ...
    #

    async def _async_get_sub_types(self, type_name: str) -> list | str:
        """Returns all the TypeDefs for a specific subtype.  If a null result is returned it means the
            type has no subtypes. Async version.

        Parameters
        ----------
        type_name : str
            Type name to retrieve the sub-types for.

        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified type.

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
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/sub-types/"
            f"{type_name}"
        )

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_sub_types(self, type_name: str) -> list | str:
        """Returns all the TypeDefs for a specific subtype.  If a null result is returned it means the
            type has no subtypes.

        Parameters
        ----------
        type_name : str
            Type name to retrieve the sub-types for.

        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified type.

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
            self._async_get_valid_relationship_types(type_name)
        )
        return resp

    async def _async_get_valid_relationship_types(self, entity_type: str) -> list | str:
        """Returns all the TypeDefs for relationships that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the valid relationships for.


        Returns
        -------
        List | str

            A list of TypeDefs that can be attached to the specified entity type.

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
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/{entity_type}/"
            f"attached-relationships"
        )

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_valid_relationship_types(self, entity_type: str) -> list | str:
        """Returns all the TypeDefs for relationships that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                 The name of the entity type to retrieve the valid relationships for.
             : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.

            Returns
            -------
            List | str

                A list of TypeDefs that can be attached to the specified entity type.

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
            self._async_get_valid_relationship_types(entity_type)
        )
        return resp

    async def _async_get_valid_classification_types(
        self, entity_type: str
    ) -> list | str:
        """Returns all the TypeDefs for classifications that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the classifications for.


        Returns
        -------
        List | str

            A list of classifications that can be attached to the specified entity type.

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
            f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/{entity_type}/"
            f"attached-classifications"
        )

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_valid_classification_types(self, entity_type: str) -> list | str:
        """Returns all the TypeDefs for classifications that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                The name of the entity type to retrieve the classifications for.
             : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.

            Returns
            -------
            List | str

                A list of classifications that can be attached to the specified entity type.

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
            self._async_get_valid_classification_types(entity_type)
        )
        return resp

    async def _async_get_typedef_by_name(self, entity_type: str) -> dict | str:
        """Return the TypeDef identified by the unique name.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.


        Returns
        -------
        dict | str

            The typedef associated with the type name

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = f"{self.platform_url}/servers/{self.view_server}{self.valid_m_command_base}/open-metadata-types/name/{entity_type}"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDef", "No TypeDefs Found")

    def get_typedef_by_name(self, entity_type: str) -> dict | str:
        """Return the TypeDef identified by the unique name.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.


        Returns
        -------
        dict | str

            The typedef associated with the type name

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
        resp = loop.run_until_complete(self._async_get_typedef_by_name(entity_type))
        return resp


if __name__ == "__main__":
    print("Main-Valid Metadata Manager")

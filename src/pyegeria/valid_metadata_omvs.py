"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""
import asyncio

# import json
from pyegeria._client import Client
from pyegeria._globals import enable_ssl_check, max_paging_size


class ValidMetadataManager(Client):
    """ The Valid Metadata OMVS provides APIs for retrieving and updating lists of valid metadata values.
        For more details see: https://egeria-project.org/guides/planning/valid-values/overview/

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

     """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            verify_flag: bool = enable_ssl_check,
    ):
        self.command_base: str = f"/api/open-metadata/valid-metadata"
        self.page_size = max_paging_size
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token)

    async def _async_setup_valid_metadata_value(self, property_name: str, type_name: str, body: dict,
                                                server: str = None):
        """ Create or update the valid value for a particular open metadata property name. If the typeName is null,
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
        server : str, optional
            The name of the server where the valid metadata value is being set up.
            If not provided, the default server name will be used.

        Returns
        -------

        Notes
        -----

        Payload structure similar to:
        {
          "displayName": "",
          "description": "",
          "preferredValue": "",
          "dataType": "",
          "isCaseSensitive": false,
          "isDeprecated" : false
        }
        """
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/valid-metadata/setup-value/{property_name}?"
               f"typeName={type_name}")

        await self._async_make_request("POST", url, body)
        return

    def setup_valid_metadata_value(self, property_name: str, type_name: str, body: dict,
                                   server: str = None):
        """ Create or update the valid value for a particular open metadata property name. If the typeName is null,
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
        server : str, optional
            The name of the server where the valid metadata value is being set up.
            If not provided, the default server name will be used.

        Returns
        -------
        str
            The GUID of the valid metadata value if it was successfully set up, or "GUID failed to be returned"
            if the GUID was not returned in the response.

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
        loop.run_until_complete(self._async_setup_valid_metadata_value(property_name, type_name,
                                                                       body, server))
        return

    async def _async_setup_valid_metadata_map_name(self, property_name: str, type_name: str, body: dict,
                                                   server: str = None):
        """ Create or update the valid value for a name that can be stored in a particular open metadata property name.
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
            server : str, optional
                The name of the server to setup the metadata map. If not provided, the default server name will be used.

            Returns
            -------
            None
                This method does not return any value.

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
        server = self.server_name if server is None else server

        url = (f"{self.platform_url}/servers/{server}/api/open-metadata/valid-metadata/setup-map-name/{property_name}?"
               f"typeName={type_name}")

        await self._async_make_request("POST", url, body)
        return

    async def _async_setup_valid_metadata_type_value(self, property_name: str, type_name: str, map_name: str,
                                                     server: str = None):
        pass

    async def _async_clear_valid_metadata_value(self, property_name: str, type_name: str, map_name: str,
                                                server: str = None):
        pass

    async def _async_clear_valid_metadata_map_value(self, property_name: str, type_name: str, map_name: str,
                                                    preferred_value: str, server: str = None):
        pass

    async def _async_validate_metadata_value(self, property_name: str, type_name: str, actual_value: str,
                                             server: str = None):
        pass

    async def _async_validate_metadata_map_name(self, property_name: str, type_name: str, map_name: str,
                                                server: str = None):
        pass

    async def _async_validate_metadata_map_value(self, property_name: str, type_name: str, actual_value: str,
                                                 server: str = None):
        pass

    async def _async_validate_metadata_map_name(self, property_name: str, type_name: str, map_name: str,
                                                server: str = None):
        pass

    async def _async_get_valid_metadata_value(self, property_name: str, type_name: str, preferred_value: str,
                                              server: str = None):
        pass

    async def _async_get_valid_metadata_map_name(self, property_name: str, type_name: str, map_name: str,
                                                 server: str = None):
        pass

    async def _async_get_valid_metadata_map_value(self, property_name: str, type_name: str, map_name: str,
                                                  preferred_value: str, server: str = None):
        pass

    async def _async_get_valid_metadata_values(self, property_name: str, type_name: str = None,
                                               server_name: str = None,
                                               start_value: int = 0, page_size: int = None) -> list | str:
        """ Retrieve list of values for the property. Async version.

            Parameters
            ----------
            property_name: str
                The property to query.
            type_name: str, opt
                The Open Metadata type to get the property values for. If not specified then all property values
                will be returned.
            server_name : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.

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

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/get-valid-metadata-values/{property_name}"
               f"?typeName={type_name}&startFrom={start_value}&pageSize={page_size}")

        resp = await self._async_make_request("GET", url)
        return resp.json().get("elementList", "No elements found")

    def get_valid_metadata_values(self, property_name: str, type_name: str = None,
                                  server_name: str = None) -> list | str:
        """  Retrieve list of values for the property.

        Parameters
        ----------
        property_name: str
            The property to query.
        type_name: str, opt
            The Open Metadata type to get the property values for. If not specified then all property values
            will be returned.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(self._async_get_valid_metadata_values(property_name, type_name,
                                                                             server_name))
        return resp

    async def _async_get_valid_metadata_value(self, property_name: str, type_name: str, preferred_value: str,
                                              server_name: str = None) -> list | str:
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/get-value/{property_name}"
               f"?typeName={type_name}&preferredValue={preferred_value}")

        resp = await self._async_make_request("GET", url)
        return resp.json()

    def get_valid_metadata_value(self, property_name: str, type_name: str, preferred_value: str,
                                 server_name: str = None) -> list | str:
        """  Retrieve details of a specific valid value for a property.

        Parameters
        ----------
        property_name: str
            The property name of the valid metadata value to retrieve
        type_name: str
            Type of the metadata value to retrieve
        preferred_value: str
            The preferred value of the valid metadata value to retrieve
        server_name : str, opt
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(self._async_get_valid_metadata_value(property_name, type_name,
                                                                            preferred_value, server_name)),
        return resp

    async def _async_get_consistent_metadata_values(self, property_name: str, type_name: str, map_name: str,
                                                    preferred_value: str, server_name: str = None,
                                                    start_from: int = 0, page_size: int = None) -> list | str:
        """  Retrieve all the consistent valid values for the requested property. Async version.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve the valid values for.
        type_name : str
            The open metadata type that the property is associated with.
        map_name : str
            A valid map name that associates a property with a value.
        preferred_value : str

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

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{property_name}/"
               f"consistent-metadata-values?typeName={type_name}&mapName={map_name}&preferredValue={preferred_value}"
               f"&startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("GET", url)
        return resp.json()

    def get_consistent_metadata_values(self, property_name: str, type_name: str, map_name: str,
                                       preferred_value: str, server_name: str = None,
                                       start_from: int = 0, page_size: int = None) -> list | str:
        """  Retrieve all the consistent valid values for the requested property.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve the valid values for.
        type_name : str
            The open metadata type that the property is associated with.
        map_name : str
            A valid map name that associates a property with a value.
        preferred_value : str

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
        resp = loop.run_until_complete(
            self._async_get_consistent_metadata_values(property_name, type_name,
                                                       map_name, preferred_value,
                                                       server_name, start_from, page_size)
        )
        return resp

    #
    # Get all ...
    #
    async def _async_get_all_entity_types(self, server_name: str = None) -> list | str:
        """ Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_entity_types(self, server_name: str = None) -> list | str:
        """ Returns the list of different types of metadata organized into two groups.  The first are the
            attribute type definitions (AttributeTypeDefs).  These provide types for attributes in full
            type definitions.  Full type definitions (TypeDefs) describe types for entities, relationships
            and classifications. Async version.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(
            self._async_get_all_entity_types(server_name))
        return resp

    async def _async_get_all_entity_defs(self, server_name: str = None) -> list | str:
        """ GReturns all the entity type definitions. Async version.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/entity-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_entity_defs(self, server_name: str = None) -> list | str:
        """ Returns all the entity type definitions.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(
            self._async_get_all_entity_defs(server_name))
        return resp

    async def _async_get_all_relationship_defs(self, server_name: str = None) -> list | str:
        """ Returns all the relationship type definitions. Async version.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/relationship-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_relationship_defs(self, server_name: str = None) -> list | str:
        """ Returns all the relationship type definitions.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(
            self._async_get_all_relationship_defs(server_name))
        return resp

    async def _async_get_all_classification_defs(self, server_name: str = None) -> list | str:
        """ Returns all the classification type definitions. Async version.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/classification-defs"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_all_classification_defs(self, server_name: str = None) -> list | str:
        """ Returns all the classification type definitions.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(
            self._async_get_all_classification_defs(server_name))
        return resp

    #
    # Get valid ...
    #
    async def _async_get_valid_relationship_types(self, entity_type: str, server_name: str = None) -> list | str:
        """  Returns all the TypeDefs for relationships that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the valid relationships for.
        server_name : str, optional
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
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/{entity_type}/"
               f"attached-relationships")

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_valid_relationship_types(self, entity_type: str, server_name: str = None) -> list | str:
        """  Returns all the TypeDefs for relationships that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                 The name of the entity type to retrieve the valid relationships for.
            server_name : str, optional
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
            self._async_get_valid_relationship_types(entity_type,
                                                     server_name)
        )
        return resp

    async def _async_get_valid_classification_types(self, entity_type: str, server_name: str = None) -> list | str:
        """ Returns all the TypeDefs for classifications that can be attached to the requested entity type.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the classifications for.
        server_name : str, optional
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
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/{entity_type}/"
               f"attached-classifications")

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDefs", "No TypeDefs Found")

    def get_valid_classification_types(self, entity_type: str, server_name: str = None) -> list | str:
        """  Returns all the TypeDefs for relationships that can be attached to the requested entity type.
                    Async version.

            Parameters
            ----------
            entity_type : str
                The name of the entity type to retrieve the classifications for.
            server_name : str, optional
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
            self._async_get_valid_classification_types(entity_type,
                                                       server_name)
        )
        return resp

    async def _async_get_typedef_by_name(self, entity_type: str, server_name: str = None) -> dict | str:
        """ Return the TypeDef identified by the unique name.
            Async version.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/open-metadata-types/name/{entity_type}"

        resp = await self._async_make_request("GET", url)
        return resp.json().get("typeDef", "No TypeDefs Found")

    def get_typedef_by_name(self, entity_type: str, server_name: str = None) -> dict | str:
        """ Return the TypeDef identified by the unique name.

        Parameters
        ----------
        entity_type : str
            The name of the entity type to retrieve the typedef for.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        resp = loop.run_until_complete(
            self._async_get_typedef_by_name(entity_type, server_name))
        return resp

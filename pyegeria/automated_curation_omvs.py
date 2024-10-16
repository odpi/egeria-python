"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Automated Curation View Service Methods

"""
import asyncio
import datetime

from httpx import Response

from pyegeria import Client, max_paging_size, body_slimmer, TEMPLATE_GUIDS
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from ._validators import validate_name, validate_guid, validate_search_string


class AutomatedCuration(Client):
    """Set up and maintain automation services in Egeria.

    Attributes:
        view_server : str
            The name of the View Server to use.
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
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.curation_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/automated-curation"

    async def _async_create_element_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
            The json body used to instantiate the template.

        Returns
        -------
        Response
           The guid of the resulting element

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        See also: https://egeria-project.org/features/templated-cataloguing/overview/
        The full description of the body is shown below:
           {
             "typeName" : "",
             "initialStatus" : "",
             "initialClassifications" : "",
             "anchorGUID" : "",
             "isOwnAnchor" : "",
             "effectiveFrom" : "",
             "effectiveTo" : "",
             "templateGUID" : "",
             "templateProperties" : {},
             "placeholderPropertyValues" : {
               "placeholderPropertyName1" : "placeholderPropertyValue1",
               "placeholderPropertyName2" : "placeholderPropertyValue2"
             },
             "parentGUID" : "",
             "parentRelationshipTypeName" : "",
             "parentRelationshipProperties" : "",
             "parentAtEnd1" : "",
             "effectiveTime" : ""
           }
        """

        url = f"{self.curation_command_root}/catalog-templates/new-element"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "GUID failed to be returned")

    def create_element_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
             The json body used to instantiate the template.


        Returns
        -------
        Response
            The guid of the resulting element

         Raises
         ------
         InvalidParameterException
         PropertyServerException
         UserNotAuthorizedException

         Notes
         -----
         See also: https://egeria-project.org/features/templated-cataloguing/overview/
         The full description of the body is shown below:
             {
               "typeName" : "",
               "initialStatus" : "",
               "initialClassifications" : "",
               "anchorGUID" : "",
               "isOwnAnchor" : "",
               "effectiveFrom" : "",
               "effectiveTo" : "",
               "templateGUID" : "",
               "templateProperties" : {},
               "placeholderPropertyValues" : {
                 "placeholderPropertyName1" : "placeholderPropertyValue1",
                 "placeholderPropertyName2" : "placeholderPropertyValue2"
               },
               "parentGUID" : "",
               "parentRelationshipTypeName" : "",
               "parentRelationshipProperties" : "",
               "parentAtEnd1" : "",
               "effectiveTime" : ""
             }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_element_from_template(body)
        )
        return response

    async def _async_create_kafka_server_element_from_template(
        self,
        kafka_server: str,
        host_name: str,
        port: str,
        description: str = None,
    ) -> str:
        """Create a Kafka server element from a template. Async version.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        description: str, opt
            A description of the Kafka server.



        Returns
        -------
        str
            The GUID of the Kafka server element.
        """

        body = {
            "templateGUID": TEMPLATE_GUIDS["Apache Kafka Server"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": kafka_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_kafka_server_element_from_template(
        self,
        kafka_server: str,
        host_name: str,
        port: str,
        description: str = None,
    ) -> str:
        """Create a Kafka server element from a template.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        description: str, opt
            A description of the Kafka server.



        Returns
        -------
        str
            The GUID of the Kafka server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_kafka_server_element_from_template(
                kafka_server, host_name, port, description
            )
        )
        return response

    async def _async_create_postgres_server_element_from_template(
        self,
        postgres_server: str,
        host_name: str,
        port: str,
        db_user: str,
        db_pwd: str,
        description: str = None,
    ) -> str:
        """Create a Postgres server element from a template. Async version.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        description: str, opt
            A description of the element.



        Returns
        -------
        str
            The GUID of the Postgres server element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["PostgreSQL Server"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": postgres_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "databaseUserId": db_user,
                "description": description,
                "databasePassword": db_pwd,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_postgres_server_element_from_template(
        self,
        postgres_server: str,
        host_name: str,
        port: str,
        db_user: str,
        db_pwd: str,
        description: str = None,
    ) -> str:
        """Create a Postgres server element from a template.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.



        description: str, opt
            A description of the elementr.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        Returns
        -------
        str
            The GUID of the Postgres server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_postgres_server_element_from_template(
                postgres_server, host_name, port, db_user, db_pwd, description
            )
        )
        return response

    async def _async_create_postgres_database_element_from_template(
        self,
        postgres_database: str,
        server_name: str,
        host_identifier: str,
        port: str,
        db_user: str,
        db_pwd: str,
        description: str = None,
    ) -> str:
        """Create a Postgres database element from a template. Async version.

        Parameters
        ----------
        postgres_database : str
            The name of the Postgres database.
        server_name : str
            The server name of the Postgres server.
        host_identifier: str
            The host IP address or domain name.
        port : str
            The port number of the Postgres server.
        db_user: str
            User name to connect to the database
        db_pwd: str
            User password to connect to the database
        description: str, opt
            A description of the element.

        Returns
        -------
        str
            The GUID of the Postgres database element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["PostgreSQL Relational Database"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "databaseName": postgres_database,
                "serverName": server_name,
                "hostIdentifier": host_identifier,
                "portNumber": port,
                "databaseUserId": db_user,
                "description": description,
                "databasePassword": db_pwd,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_postgres_database_element_from_template(
        self,
        postgres_database: str,
        server_name: str,
        host_identifier: str,
        port: str,
        db_user: str,
        db_pwd: str,
        description: str = None,
    ) -> str:
        """Create a Postgres database element from a template. Async version.

        Parameters
        ----------
        postgres_database : str
            The name of the Postgres database.
        server_name : str
            The server name of the Postgres server.
        host_identifier: str
            The host IP address or domain name.
        port : str
            The port number of the Postgres server.
        db_user: str
            User name to connect to the database
        db_pwd: str
            User password to connect to the database
        description: str, opt
            A description of the element.

        Returns
        -------
        str
            The GUID of the Postgres database element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_postgres_database_element_from_template(
                postgres_database,
                server_name,
                host_identifier,
                port,
                db_user,
                db_pwd,
                description,
            )
        )
        return response

    async def _async_create_folder_element_from_template(
        self,
        path_name: str,
        folder_name: str,
        file_system: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a File folder element from a template.
        Async version.

        Parameters
        ----------
        path_name : str
            The path including the folder..

        folder_name : str
            The name of the folder to create.

        file_system : str
            The unique name for the file system that the folder belongs to. It may be a machine name or URL to a
            remote file store.

        description: str, opt
            A description of the element.

        version: str, opt
            version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["File System Directory"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "directoryPathName": path_name,
                "directoryName": folder_name,
                "versionIdentifier": version,
                "fileSystemName": file_system,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_folder_element_from_template(
        self,
        path_name: str,
        folder_name: str,
        file_system: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a File folder element from a template.

        Parameters
        ----------
        path_name : str
            The path including the folder..

        folder_name : str
            The name of the folder to create.

        file_system : str
            The unique name for the file system that the folder belongs to. It may be a machine name or URL to a
            remote file store.

        description: str, opt
            A description of the element.

        version: str, opt
            version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_folder_element_from_template(
                path_name, folder_name, file_system, description, version
            )
        )
        return response

    async def _async_create_uc_server_element_from_template(
        self,
        server_name: str,
        host_url: str,
        port: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog Server element from a template. Async version.

        Parameters
        ----------
        server_name : str
            The name of the Unity Catalog server we are configuring.

        host_url : str
            The URL of the server.

        port : str
            The port number of the server.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Server"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": server_name,
                "hostURL": host_url,
                "versionIdentifier": version,
                "portNumber": port,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_server_element_from_template(
        self,
        server_name: str,
        host_url: str,
        port: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog Server element from a template. Async version.

        Parameters
        ----------
        server_name : str
            The name of the Unity Catalog server we are configuring.

        host_url : str
            The URL of the server.

        port : str
            The port number of the server.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_server_element_from_template(
                server_name, host_url, port, description, version
            )
        )
        return response

    async def _async_create_uc_catalog_element_from_template(
        self,
        uc_catalog: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog Catalog element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Catalog"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_catalog_element_from_template(
        self,
        uc_catalog: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog Catalog element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_catalog_element_from_template(
                uc_catalog, network_address, description, version
            )
        )
        return response

    async def _async_create_uc_schema_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog schema element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Schema"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_schema_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog schema element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_schema_element_from_template(
                uc_catalog, uc_schema, network_address, description, version
            )
        )
        return response

    async def _async_create_uc_table_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_table: str,
        uc_table_type: str,
        uc_storage_loc: str,
        uc_data_source_format: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog table element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_table: str
            The name of the UC table we are configuring.
        uc_table_type: str
            The type of table - expect either Managed or External.
        uc_storage_loc: str
            The location where the data associated with this element is stored.
        uc_data_source_format: str
            The format of the data source - currently DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Table"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucTableName": uc_table,
                "ucTableType": uc_table_type,
                "ucStorageLocation": uc_storage_loc,
                "ucDataSourceFormat": uc_data_source_format,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_table_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_table: str,
        uc_table_type: str,
        uc_storage_loc: str,
        uc_data_source_format: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog table element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_table: str
            The name of the UC table we are configuring.
        uc_table_type: str
            The type of table - expect either Managed or External.
        uc_storage_loc: str
            The location where the data associated with this element is stored.
        uc_data_source_format: str
            The format of the data source - currently DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_table_element_from_template(
                uc_catalog,
                uc_schema,
                uc_table,
                uc_table_type,
                uc_storage_loc,
                uc_data_source_format,
                network_address,
                description,
                version,
            )
        )
        return response

    async def _async_create_uc_function_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_function: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog function element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_function: str
            The name of the UC function we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Function"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucFunctionName": uc_function,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_function_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_function: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog function element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_function: str
            The name of the UC function we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_function_element_from_template(
                uc_catalog,
                uc_schema,
                uc_function,
                network_address,
                description,
                version,
            )
        )
        return response

    async def _async_create_uc_volume_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_volume: str,
        uc_vol_type: str,
        uc_storage_loc: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog volume element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_volume: str
            The name of the UC volume we are configuring.

        uc_vol_type: str
            The volume type of the UC volume we are configuring. Currently Managed or External.
        uc_storage_loc: str
            The location with the data associated with this element is stored.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        body = {
            "templateGUID": TEMPLATE_GUIDS["Unity Catalog Volume"],
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucVolumeName": uc_volume,
                "ucVolumeType": uc_vol_type,
                "ucStorageLocation": uc_storage_loc,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_element_from_template(body_s)
        return str(response)

    def create_uc_volume_element_from_template(
        self,
        uc_catalog: str,
        uc_schema: str,
        uc_volume: str,
        uc_vol_type: str,
        uc_storage_loc: str,
        network_address: str,
        description: str = None,
        version: str = None,
    ) -> str:
        """Create a Unity Catalog volume element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_volume: str
            The name of the UC volume we are configuring.

        uc_vol_type: str
            The volume type of the UC volume we are configuring. Currently Managed or External.

        uc_storage_loc: str
            The location with the data associated with this element is stored.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_volume_element_from_template(
                uc_catalog,
                uc_schema,
                uc_volume,
                uc_vol_type,
                uc_storage_loc,
                network_address,
                description,
                version,
            )
        )
        return response

    #
    # Engine Actions
    #
    async def _async_get_engine_actions(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list:
        """Retrieve the engine actions that are known to the server. Async version.
        Parameters
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
        [dict]
            A list of engine action descriptions as JSON.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        url = (
            f"{self.curation_command_root}/engine-actions?"
            f"startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "No elements")

    def get_engine_actions(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list:
        """Retrieve the engine actions that are known to the server.
        Parameters
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
        [dict]
            A list of engine action descriptions as JSON.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_engine_actions(start_from, page_size)
        )
        return response

    async def _async_get_engine_action(self, engine_action_guid: str) -> dict:
        """Request the status and properties of an executing engine action request. Async version.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        url = f"{self.curation_command_root}/engine-actions/" f"{engine_action_guid}"

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "No element found")

    def get_engine_action(self, engine_action_guid: str) -> dict:
        """Request the status and properties of an executing engine action request.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_engine_action(engine_action_guid)
        )
        return response

    async def _async_cancel_engine_action(self, engine_action_guid: str) -> None:
        """Request that an engine action request is cancelled and any running governance service is stopped. Async Ver.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        validate_guid(engine_action_guid)

        url = (
            f"{self.curation_command_root}/engine-actions/"
            f"{engine_action_guid}/cancel"
        )

        await self._async_make_request("POST", url)

    def cancel_engine_action(self, engine_action_guid: str) -> None:
        """Request that an engine action request is cancelled and any running governance service is stopped.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_cancel_engine_action(engine_action_guid))
        return

    async def _async_get_active_engine_actions(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list | str:
        """Retrieve the engine actions that are still in process. Async Version.

        Parameters:
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns:
        -------
            List[dict]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """

        url = (
            f"{self.curation_command_root}/engine-actions/active?"
            f"startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "no actions")

    def get_active_engine_actions(
        self, start_from: int = 0, page_size: int = 0
    ) -> list | str:
        """Retrieve the engine actions that are still in process.

        Parameters:
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
            List[dict]: A list of JSON representations of governance action processes matching the provided name.

        Raises
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_active_engine_actions(start_from, page_size)
        )
        return response

    async def _async_get_engine_actions_by_name(
        self,
        name: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request. Async Version.
        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
            maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
             found with the given name.
        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """

        validate_name(name)

        url = (
            f"{self.curation_command_root}/engine-actions/by-name?"
            f"startFrom={start_from}&pageSize={page_size}"
        )
        body = {"filter": name}
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_engine_actions_by_name(
        self,
        name: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request.

        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
             maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
            found with the given name.
        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_engine_actions_by_name(name, start_from, page_size)
        )
        return response

    async def _async_find_engine_actions(
        self,
        search_string: str,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements that contain the search string. Async Version.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (
            f"{self.curation_command_root}/engine-actions/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )
        body = {"class": "SearchStringRequestBody", "name": search_string}
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def find_engine_actions(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements that contain the search string.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_engine_actions(
                search_string,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
            )
        )
        return response

    #
    # Governance action processes
    #

    async def _async_get_governance_action_process_by_guid(
        self, process_guid: str
    ) -> dict | str:
        """Retrieve the governance action process metadata element with the supplied unique identifier. Async Version.

        Parameters:
        ----------
            process_guid: str
              The GUID (Globally Unique Identifier) of the governance action process.


        Returns:
        -------
            dict: The JSON representation of the governance action process element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        validate_guid(process_guid)

        url = (
            f"{self.curation_command_root}/"
            f"governance-action-processes/{process_guid}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_governance_action_process_by_guid(self, process_guid: str) -> dict | str:
        """Retrieve the governance action process metadata element with the supplied unique identifier.

        Parameters:
        ----------
            process_guid: str
              The GUID (Globally Unique Identifier) of the governance action process.

        Returns:
        -------
            dict: The JSON representation of the governance action process element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_governance_action_process_by_guid(process_guid)
        )
        return response

    async def _async_get_gov_action_process_graph(
        self, process_guid: str
    ) -> dict | str:
        """Retrieve the governance action process metadata element with the supplied unique
            identifier along with the flow definition describing its implementation. Async Version.
        Parameters
        ----------
        process_guid : str
            The process GUID to retrieve the graph for.

        Returns
        -------
        dict or str
            A dictionary representing the graph of the governance action process, or the string "no actions"
            if no actions are found.
        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

        """

        validate_guid(process_guid)

        url = (
            f"{self.curation_command_root}/"
            f"governance-action-processes/{process_guid}/graph"
        )

        response = await self._async_make_request("POST", url)
        return response.json().get("element", "no actions")

    def get_gov_action_process_graph(self, process_guid: str) -> dict | str:
        """Retrieve the governance action process metadata element with the supplied unique
         identifier along with the flow definition describing its implementation.
        Parameters
        ----------
        process_guid : str
            The process GUID to retrieve the graph for.

        Returns
        -------
        dict or str
            A dictionary representing the graph of the governance action process, or the string "no actions"
            if no actions are found.
        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_process_graph(process_guid)
        )
        return response

    async def _async_get_gov_action_processes_by_name(
        self,
        name: str,
        start_from: int = None,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action process metadata elements with a matching qualified or display name.
         There are no wildcards supported on this request. Async Version.

        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default
            global maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions,
            or "no actions" if no engine actions were found with the given name.
        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """

        validate_name(name)

        url = (
            f"{self.curation_command_root}/governance-action-processes/"
            f"by-name?startFrom={start_from}&pageSize={page_size}"
        )
        body = {"filter": name}
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_gov_action_processes_by_name(
        self,
        name: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action process metadata elements with a matching qualified or display name.
         There are no wildcards supported on this request.

        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
             maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions,
            or "no actions" if no engine actions were found with the given name.
        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_processes_by_name(name, start_from, page_size)
        )
        return response

    async def _async_find_gov_action_processes(
        self,
        search_string: str,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action process metadata elements that contain the search string. Async ver.

        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the governance action processes found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """

        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (
            f"{self.curation_command_root}/governance-action-processes/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )

        if search_string:
            body = {"filter": search_string}
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elements", "no actions")

    def find_gov_action_processes(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action process metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the governance action processes found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_gov_action_processes(
                search_string,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
            )
        )
        return response

    async def _async_initiate_gov_action_process(
        self,
        action_type_qualified_name: str,
        request_source_guids: [str] = None,
        action_targets: list = None,
        start_time: datetime = None,
        request_parameters: dict = None,
        orig_service_name: str = None,
        orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action process as a template, initiate a chain of engine actions. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str], optional
            - request source elements for the resulting governance action service
        action_targets: [str], optional
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, optional
            - time to start the process
        request_parameters: [str], optional
            - parameters passed into the process
        orig_service_name: str, optional
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str, optional
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        start_time: datetime = (
            datetime.datetime.now() if start_time is None else start_time
        )

        url = f"{self.curation_command_root}/governance-action-processes/" f"initiate"
        body = {
            "class": "GovernanceActionProcessRequestBody",
            "processQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startTime": int(start_time.timestamp() * 1000),
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_gov_action_process(
        self,
        action_type_qualified_name: str,
        request_source_guids: [str] = None,
        action_targets: [str] = None,
        start_time: datetime = None,
        request_parameters: dict = None,
        orig_service_name: str = None,
        orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action process as a template, initiate a chain of engine actions.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str], optional
            - request source elements for the resulting governance action service
        action_targets: [str], optional
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, optional
            - time to start the process
        request_parameters: [str], optional
            - parameters passed into the process
        orig_service_name: str, optional
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str, optional
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_process(
                action_type_qualified_name,
                request_source_guids,
                action_targets,
                start_time,
                request_parameters,
                orig_service_name,
                orig_engine_name,
            )
        )
        return response

    async def _async_get_gov_action_types_by_guid(
        self, gov_action_type_guid: str
    ) -> dict | str:
        """Retrieve the governance action type metadata element with the supplied unique identifier. Async version.

        Parameters:
        ----------
            gov_action_type_guid: str
              The GUID (Globally Unique Identifier) of the governance action type to retrieve.

        Returns:
        -------
            dict: The JSON representation of the governance action type element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        validate_guid(gov_action_type_guid)

        url = (
            f"{self.curation_command_root}/"
            f"governance-action-types/{gov_action_type_guid}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_gov_action_types_by_guid(self, gov_action_type_guid: str) -> dict | str:
        """Retrieve the governance action type metadata element with the supplied unique identifier.

        Parameters:
        ----------
            gov_action_type_guid: str
              The GUID (Globally Unique Identifier) of the governance action type to retrieve.

        Returns:
        -------
            dict: The JSON representation of the governance action type element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_types_by_guid(gov_action_type_guid)
        )
        return response

    async def _async_get_gov_action_types_by_name(
        self,
        action_type_name,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action type metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request. Async version.

            Parameters:
            ----------
                action_type_name: str
                  The name of the governance action type to retrieve.

            Returns:
            -------
                dict: The JSON representation of the governance action type element.

            Raises:
            ------
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                                           this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:
        """

        validate_name(action_type_name)

        url = (
            f"{self.curation_command_root}/"
            f"governance-action-types/by-name?startFrom={start_from}&pageSize={page_size}"
        )

        body = {"filter": action_type_name}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_gov_action_types_by_name(
        self,
        action_type_name,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action type metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request. Async version.

        Parameters:
        ----------
            action_type_name: str
              The name of the governance action type to retrieve.

        Returns:
        -------
            dict: The JSON representation of the governance action type element.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_gov_action_types_by_name(
                action_type_name, start_from, page_size
            )
        )
        return response

    async def _async_find_gov_action_types(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action type metadata elements that contain the search string.
         Async Version.

        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the governance action types found based on the search query.
            If no actions are found, returns the string "no action types".

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        validate_search_string(search_string)
        if search_string == "*":
            search_string = None
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        url = (
            f"{self.curation_command_root}/governance-action-types/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )
        body = {"filter": search_string}
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no action types")

    def find_gov_action_types(
        self,
        search_string: str = "*",
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of governance action type metadata elements that contain the search string.

        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.


        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the governance action types found based on the search query.
            If no actions are found, returns the string "no action types".

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_gov_action_types(
                search_string,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
            )
        )
        return response

    async def _async_initiate_gov_action_type(
        self,
        action_type_qualified_name: str,
        request_source_guids: [str],
        action_targets: list,
        start_time: datetime = None,
        request_parameters: dict = None,
        orig_service_name: str = None,
        orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action type as a template, initiate an engine action. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, default = None
            - time to start the process, no earlier than start time. None means now.
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.curation_command_root}/governance-action-types/" f"initiate"
        start = int(start_time.timestamp() * 1000) if start_time else None
        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startDate": start,
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_gov_action_type(
        self,
        action_type_qualified_name: str,
        request_source_guids: [str],
        action_targets: list,
        start_time: datetime = None,
        request_parameters: dict = None,
        orig_service_name: str = None,
        orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action type as a template, initiate an engine action.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, default = None
            - time to start the process, no earlier than start time. None means now.
        request_parameters: [str]
            - parameters passed into the process
        orig_service_name: str
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_type(
                action_type_qualified_name,
                request_source_guids,
                action_targets,
                start_time,
                request_parameters,
                orig_service_name,
                orig_engine_name,
            )
        )
        return response

    #
    #   Initiate surveys
    #

    async def _async_initiate_survey(self, survey_name: str, resource_guid: str) -> str:
        """Initiate a survey of the survey_name on the target resource. Async Version.

        Parameters
        ----------
        survey_name: str
            The name of the survey to initiate.
        resource_guid : str
            The GUID of the resource to be surveyed.

        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """

        url = f"{self.curation_command_root}/governance-action-types/initiate"

        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": survey_name,
            "actionTargets": [
                {
                    "class": "NewActionTarget",
                    "actionTargetName": "serverToSurvey",
                    "actionTargetGUID": resource_guid,
                }
            ],
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "Action not initiated")

    def initiate_postgres_database_survey(self, postgres_database_guid: str) -> str:
        """Initiate a postgres database survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "PostgreSQLSurveys:survey-postgres-database", postgres_database_guid
            )
        )
        return response

    def initiate_postgres_server_survey(self, postgres_server_guid: str) -> str:
        """Initiate a postgres server survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "PostgreSQLSurveys:survey-postgres-server", postgres_server_guid
            )
        )
        return response

    def initiate_file_folder_survey(
        self,
        file_folder_guid: str,
        survey_name: str = "FileSurveys:survey-folder",
    ) -> str:
        """Initiate a file folder survey - async version

        Parameters:
        ----------
            file_folder_guid: str
                The GUID of the File Folder that we wish to survey.
            survey_name: str, optional
                The unique name of the survey routine to execute. Default surveys all folders.

        Returns:
        -------
            str:
                The guid of the survey being run.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:

        Notes:
            There are multiple kinds of file folder surveys available, each with their own purpose. They are described
            in the Core Content Brain.

            File Folder Survey Names currently include::
            - Egeria:GovernanceActionType:AssetSurvey:survey-folders
            - Egeria:GovernanceActionType:AssetSurvey:survey-folder-and-files
            - Egeria:GovernanceActionType:AssetSurvey:survey-all-folders
            - Egeria:GovernanceActionType:AssetSurvey:survey-all-folders-and-files


        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                survey_name,
                file_folder_guid,
            )
        )
        return response

    def initiate_file_survey(self, file_guid: str) -> str:
        """Initiate a file survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey("FileSurveys:survey-data-file", file_guid)
        )
        return response

    def initiate_kafka_server_survey(self, kafka_server_guid: str) -> str:
        """Initiate survey of a kafka server.
        Parameters
        ----------
        kafka_server_guid : str
            The GUID of the Kafka server to be surveyed.


        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "ApacheKafkaSurveys:survey-kafka-server", kafka_server_guid
            )
        )
        return response

    def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
        """Initiate survey of a Unity Catalog server. Async Version.
        Parameters
        ----------
        uc_server_guid : str
            The GUID of the Kafka server to be surveyed.


        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "UnityCatalogSurveys:survey-unity-catalog-server", uc_server_guid
            )
        )
        return response

    def initiate_uc_schema_survey(self, uc_schema_guid: str) -> str:
        """Initiate survey of a Unity Catalog schema. Async Version.
        Parameters
        ----------
        uc_schema_guid : str
            The GUID of the Kafka server to be surveyed.



        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "UnityCatalogSurveys:survey-unity-catalog-schema", uc_schema_guid
            )
        )
        return response

    # async def _async_initiate_uc_function_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_function_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response
    #
    # async def _async_initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response
    #
    # async def _async_initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response

    #
    #   Initiate general engine action
    #

    async def _async_initiate_engine_action(
        self,
        qualified_name: str,
        domain_identifier: int,
        display_name: str,
        description: str,
        request_source_guids: str,
        action_targets: str,
        received_guards: [str],
        start_time: datetime,
        request_type: str,
        request_parameters: dict,
        process_name: str,
        request_src_name: str = None,
        originator_svc_name: str = None,
        originator_eng_name: str = None,
    ) -> str:
        """Create an engine action in the metadata store that will trigger the governance service associated with
        the supplied request type. The engine action remains to act as a record of the actions taken for auditing.
        Async version.

        Parameters
        ----------
            qualified_name (str): The qualified name of the governance action.
            domain_identifier (int): The domain identifier for the governance action.
            display_name (str): The display name of the governance action.
            description (str): The description of the governance action.
            request_source_guids (str): GUIDs of the sources initiating the request.
            action_targets (str): Targets of the governance action.
            received_guards (List[str]): List of guards received for the action.
            start_time (datetime): The start time for the governance action.
            request_type (str): The type of the governance action request.
            request_parameters (dict): Additional parameters for the governance action.
            process_name (str): The name of the associated governance action process.
            request_src_name (str, optional): The name of the request source. Defaults to None.
            originator_svc_name (str, optional): The name of the originator service. Defaults to None.
            originator_eng_name (str, optional): The name of the originator engine. Defaults to None.

        Returns
        -------
            str: The GUID (Globally Unique Identifier) of the initiated governance action.

        Raises
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note
        ----
            The `start_time` parameter should be a `datetime` object representing the start time of the
            governance action.


        """

        url = (
            f"{self.curation_command_root}/governance-engines/"
            f"engine-actions/initiate"
        )
        body = {
            "class": "GovernanceActionRequestBody",
            "qualifiedName": qualified_name + str(int(start_time.timestamp())),
            "domainIdentifier": domain_identifier,
            "displayName": display_name,
            "description": description,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "receivedGuards": received_guards,
            "startTime": int(start_time.timestamp() * 1000),
            "requestType": request_type,
            "requestParameters": request_parameters,
            "processName": process_name,
            "requestSourceName": request_src_name,
            "originatorServiceName": originator_svc_name,
            "originatorEngineName": originator_eng_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_engine_action(
        self,
        qualified_name: str,
        domain_identifier: int,
        display_name: str,
        description: str,
        request_source_guids: str,
        action_targets: str,
        received_guards: [str],
        start_time: datetime,
        request_type: str,
        request_parameters: dict,
        process_name: str,
        request_src_name: str = None,
        originator_svc_name: str = None,
        originator_eng_name: str = None,
    ) -> str:
        """Create an engine action in the metadata store that will trigger the governance service associated with
        the supplied request type. The engine action remains to act as a record of the actions taken for auditing.

        Parameters
        ----------
            qualified_name (str): The qualified name of the governance action.
            domain_identifier (int): The domain identifier for the governance action.
            display_name (str): The display name of the governance action.
            description (str): The description of the governance action.
            request_source_guids (str): GUIDs of the sources initiating the request.
            action_targets (str): Targets of the governance action.
            received_guards (List[str]): List of guards received for the action.
            start_time (datetime): The start time for the governance action.
            gov_engine_name (str): The name of the governance engine associated with the action.
            request_type (str): The type of the governance action request.
            request_parameters (dict): Additional parameters for the governance action.
            process_name (str): The name of the associated governance action process.
            request_src_name (str, optional): The name of the request source. Defaults to None.
            originator_svc_name (str, optional): The name of the originator service. Defaults to None.
            originator_eng_name (str, optional): The name of the originator engine. Defaults to None.

        Returns
        -------
            str: The GUID (Globally Unique Identifier) of the initiated governance action.

        Raises
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note
        ----
            The `start_time` parameter should be a `datetime` object representing the start time of the
            governance action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_engine_action(
                qualified_name,
                domain_identifier,
                display_name,
                description,
                request_source_guids,
                action_targets,
                received_guards,
                start_time,
                request_type,
                request_parameters,
                process_name,
                request_src_name,
                originator_svc_name,
                originator_eng_name,
            )
        )
        return response

    async def _async_get_catalog_targets(
        self,
        integ_connector_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.
        Async version.

        Parameters:
        ----------
            integ_connector_guid: str
              The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        Returns:
        -------
            [dict]: The list of catalog targets JSON objects.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        validate_guid(integ_connector_guid)

        url = (
            f"{self.curation_command_root}/integration-connectors/"
            f"{integ_connector_guid}/catalog-targets?startFrom={start_from}&pageSize={page_size}"
        )

        response = await self._async_make_request("GET", url)
        return response.json().get("elements", "no targets")

    def get_catalog_targets(
        self,
        integ_connector_guid: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.

        Parameters:
        ----------
            integ_connector_guid: str
              The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        Returns:
        -------
            [dict]: The list of catalog targets JSON objects.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_targets(integ_connector_guid, start_from, page_size)
        )
        return response

    async def _async_get_catalog_target(self, relationship_guid: str) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector. Further Information:
        https://egeria-project.org/concepts/integration-connector/ .    Async version.

        Parameters:
        ----------
            relationship_guid: str
                The GUID (Globally Unique Identifier) identifying the catalog targets for an integration connector.

        Returns:
        -------
            dict: JSON structure of the catalog target.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        validate_guid(relationship_guid)

        url = f"{self.curation_command_root}/catalog-targets/" f"{relationship_guid}"

        response = await self._async_make_request("GET", url)
        return response.json().get("element", "no actions")

    def get_catalog_target(self, relationship_guid: str) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector.  Further Information:
        https://egeria-project.org/concepts/integration-connector/ .

        Parameters:
        ----------
            relationship_guid: str
                The GUID (Globally Unique Identifier) identifying the catalog targets for an integration connector.

        Returns:
        -------
            dict: JSON structure of the catalog target.

        Raises:
        ------
            InvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PropertyServerException: If the API response indicates a server side error.
            UserNotAuthorizedException:
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_target(relationship_guid)
        )
        return response

    async def _async_add_catalog_target(
        self,
        integ_connector_guid: str,
        metadata_element_guid: str,
        catalog_target_name: str,
        connection_name: str = None,
        metadata_src_qual_name: str = None,
        config_properties: dict = None,
        template_properties: dict = None,
        permitted_sync: str = "BOTH_DIRECTIONS",
        delete_method: str = "ARCHIVE",
    ) -> str:
        """Add a catalog target to an integration connector and .
        Async version.

        Parameters:
        ----------
        integ_connector_guid: str
            The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        metadata_element_guid: str
            The specific metadata element target we want to retrieve.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
                Returns:
        -------
            Relationship GUID for the catalog target,

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:
        """

        validate_guid(integ_connector_guid)
        validate_guid(metadata_element_guid)

        url = (
            f"{self.curation_command_root}/integration-connectors/"
            f"{integ_connector_guid}/catalog-targets/{metadata_element_guid}"
        )
        body = {
            "catalogTargetName": catalog_target_name,
            "metadataSourceQualifiedName": metadata_src_qual_name,
            "configProperties": config_properties,
            "templateProperties": template_properties,
            "connectionName": connection_name,
            "permittedSynchronization": permitted_sync,
            "deleteMethod": delete_method,
        }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "No Guid returned")

    def add_catalog_target(
        self,
        integ_connector_guid: str,
        metadata_element_guid: str,
        catalog_target_name: str,
        connection_name: str = None,
        metadata_src_qual_name: str = None,
        config_properties: dict = None,
        template_properties: dict = None,
        permitted_sync: str = "BOTH_DIRECTIONS",
        delete_method: str = "ARCHIVE",
    ) -> str:
        """Add a catalog target to an integration connector and .

        Parameters:
        ----------
        integ_connector_guid: str
            The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        metadata_element_guid: str
            The specific metadata element target we want to retrieve.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
                Returns:
        -------
            Relationship GUID for the catalog target,

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_catalog_target(
                integ_connector_guid,
                metadata_element_guid,
                catalog_target_name,
                connection_name,
                metadata_src_qual_name,
                config_properties,
                template_properties,
                permitted_sync,
                delete_method,
            )
        )
        return response

    async def _async_update_catalog_target(
        self,
        relationship_guid: str,
        catalog_target_name: str,
        connection_name: str = None,
        metadata_src_qual_name: str = None,
        config_properties: dict = None,
        template_properties: dict = None,
        permitted_sync: str = "BOTH_DIRECTIONS",
        delete_method: str = "ARCHIVE",
    ) -> None:
        """Update a catalog target to an integration connector.
        Async version.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) of the relationship used to retrieve catalog targets.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
        Returns:
        -------
            None

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:
        """

        validate_guid(relationship_guid)

        url = (
            f"{self.curation_command_root}/catalog-targets/"
            f"{relationship_guid}/update"
        )
        body = {
            "catalogTargetName": catalog_target_name,
            "metadataSourceQualifiedName": metadata_src_qual_name,
            "configProperties": config_properties,
            "templateProperties": template_properties,
            "connectionName": connection_name,
            "permittedSynchronization": permitted_sync,
            "deleteMethod": delete_method,
        }
        await self._async_make_request("POST", url, body)
        return

    def update_catalog_target(
        self,
        relationship_guid: str,
        catalog_target_name: str,
        connection_name: str = None,
        metadata_src_qual_name: str = None,
        config_properties: dict = None,
        template_properties: dict = None,
        permitted_sync: str = "BOTH_DIRECTIONS",
        delete_method: str = "ARCHIVE",
    ) -> None:
        """Update a catalog target to an integration connector.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) of the relationship used to retrieve catalog targets.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
        server: str, optional
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_catalog_target(
                relationship_guid,
                catalog_target_name,
                connection_name,
                metadata_src_qual_name,
                config_properties,
                template_properties,
                permitted_sync,
                delete_method,
            )
        )
        return

    async def _async_remove_catalog_target(self, relationship_guid: str) -> None:
        """Remove a catalog target to an integration connector. Async version.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) identifying the catalog target relationship.

        Returns:
        -------
            None

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:
        """

        validate_guid(relationship_guid)

        url = (
            f"{self.curation_command_root}/catalog-targets/"
            f"{relationship_guid}/remove"
        )

        await self._async_make_request("POST", url)
        return

    def remove_catalog_target(self, relationship_guid: str) -> None:
        """Remove a catalog target to an integration connector.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) identifying the catalog target relationship.

        Returns:
        -------
            None

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_catalog_target(relationship_guid))
        return

    #
    #   Get information about technologies
    #

    async def _async_get_tech_types_for_open_metadata_type(
        self,
        type_name: str,
        tech_name: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of deployed implementation type metadata elements linked to a particular
        open metadata type.. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        tech_name: str
            The technology name we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/types
        """

        # validate_name(type_name)
        url = (
            f"{self.curation_command_root}/open-metadata-types/"
            f"{type_name}/technology-types?startFrom={start_from}&pageSize={page_size}"
        )
        body = {"filter": tech_name}

        response = await self._async_make_request("GET", url, body)
        return response.json().get("elements", "no tech found")

    def get_tech_types_for_open_metadata_type(
        self,
        type_name: str,
        tech_name: str,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> list | str:
        """Retrieve the list of deployed implementation type metadata elements linked to a particular
        open metadata type.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        tech_name: str
            The technology name we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/types
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tech_types_for_open_metadata_type(
                type_name, tech_name, start_from, page_size
            )
        )
        return response

    async def _async_get_technology_type_detail(self, type_name: str) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
            and contain no wild cards. Async version.
        Parameters
        ----------
        type_name : str
            The name of the technology type to retrieve detailed information for.


        Returns
        -------
        list[dict] | str
            A list of dictionaries containing the detailed information for the specified technology type.
            If the technology type is not found, returns the string "no type found".
        Raises
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        """

        # validate_name(type_name)
        url = f"{self.curation_command_root}/technology-types/by-name"

        body = {"filter": type_name}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("element", "no type found")

    def get_technology_type_detail(self, type_name: str) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
        and contain no wild cards.
        Parameters
        ----------
        type_name : str
            The name of the technology type to retrieve detailed information for.

        Returns
        -------
        list[dict] | str
            A list of dictionaries containing the detailed information for the specified technology type.
            If the technology type is not found, returns the string "no type found".
        Raises
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_technology_type_detail(type_name)
        )
        return response

    async def _async_find_technology_types(
        self,
        search_string: str = "*",
        start_from: int = 0,
        page_size: int = max_paging_size,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        starts_with : bool, optional
           Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
           Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
           Whether to ignore case while searching engine actions. Default is True.

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        validate_name(search_string)
        if search_string == "*":
            search_string = ""

        url = (
            f"{self.curation_command_root}/technology-types/"
            f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
            f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}"
        )
        body = {"filter": search_string}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no tech found")

    def find_technology_types(
        self,
        search_string: str = "*",
        start_from: int = 0,
        page_size: int = max_paging_size,
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_technology_types(
                search_string,
                start_from,
                page_size,
                starts_with,
                ends_with,
                ignore_case,
            )
        )
        return response

    async def _async_get_all_technology_types(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list | str:
        """Get all technology types - async version"""
        return await self._async_find_technology_types("*", start_from, page_size)

    def get_all_technology_types(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list | str:
        """Get all technology types"""
        return self.find_technology_types("*", start_from, page_size)

    def print_engine_action_summary(self, governance_action: dict):
        """print_governance_action_summary

        Print all the governance actions with their status, in the server.

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        if governance_action:
            name = governance_action.get("displayName")
            if not name:
                name = governance_action.get("qualifiedName")
            action_status = governance_action.get("action_status")
            if governance_action.get("completion_guards"):
                completion_guards = governance_action.get("completion_guards")
            else:
                completion_guards = "\t"
            if governance_action.get("process_name"):
                process_name = governance_action.get("process_name")
            else:
                process_name = "\t"
            if governance_action.get("completion_message"):
                completion_message = governance_action.get("completion_message")
            else:
                completion_message = ""
            print(
                action_status
                + "\n\t| "
                + name
                + "\t| "
                + process_name
                + "\t| "
                + "%s" % ", ".join(map(str, completion_guards))
                + "\t| "
                + completion_message
            )

    def print_engine_actions(self):
        """print_governance_actions

        Print all the governance actions with their status, in the server.

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        governance_actions = self.get_engine_actions()
        if governance_actions is not None:
            for x in range(len(governance_actions)):
                self.print_engine_action_summary(governance_actions[x])

    async def _async_get_technology_type_elements(
        self,
        filter: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        get_templates: bool = False,
    ) -> list | str:
        """Retrieve the elements for the requested deployed implementation type. There are no wildcards allowed
        in the name. Async version.

        Parameters:
        ----------
        filter: str
            The name of the deployed technology implementation type to retrieve elements for.
                effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        get_templates_s = str(get_templates).lower()
        validate_name(filter)

        url = (
            f"{self.curation_command_root}/technology-types/elements?"
            f"startFrom={start_from}&pageSize={page_size}&getTemplates={get_templates_s}"
        )
        body = {"filter": filter, "effective_time": effective_time}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no tech found")

    def get_technology_type_elements(
        self,
        filter: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        get_templates: bool = False,
    ) -> list | str:
        """Retrieve the elements for the requested deployed implementation type. There are no wildcards allowed
        in the name.

        Parameters:
        ----------
        filter: str
            The name of the deployed technology implementation type to retrieve elements for.
                effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        InvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PropertyServerException: If the API response indicates a server side error.
        UserNotAuthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_technology_type_elements(
                filter, effective_time, start_from, page_size, get_templates
            )
        )
        return response


if __name__ == "__main__":
    print("Main-Automated Curation")

"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""

import asyncio

from loguru import logger
from requests import Response
from pyegeria.core.utils import body_slimmer, dynamic_catch
from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import max_paging_size, default_time_out, NO_ELEMENTS_FOUND
from typing import Any, Optional
from pyegeria.view.base_report_formats import get_report_spec_match
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.models import (
    SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
    TemplateRequestBody, UpdateElementRequestBody, NewRelationshipRequestBody,
    DeleteElementRequestBody, DeleteRelationshipRequestBody,
    ArchiveRequestBody, NewOpenMetadataElementRequestBody, FindRequestBody
)
from pyegeria.view.output_formatter import populate_columns_from_properties, \
    _extract_referenceable_properties, get_required_relationships

class RuntimeManager(ServerClient):
    """
    Client to issue Runtime status requests.

    Attributes:

        view_server : str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str, optional
            Bearer token

    Methods:

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
        time_out: int = default_time_out,
    ):
        self.view_server = view_server
        self.time_out = time_out
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.runtime_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/runtime-manager"
        # self.platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"  # this is platform @ 9443 from the core content archive
        self.platform_guid = None
        self.default_platform_name = (
            "Default Local OMAG Server Platform"  # this from the core content archive
        )


    #
    #   Integration Connector Methods
    #
    @dynamic_catch
    async def _async_get_integration_connector_config_properties(
        self,
        connector_name: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "IntegrationConnector",
        body: Optional[dict | GetRequestBody] = None,
    ) -> dict | str:
        """Retrieve the configuration properties of the named integration connector running in the integration daemon.
            Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        connector_name : str
            Name of the integration connector to retrieve properties for.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "IntegrationConnector".

        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           Dict of the connector configuration properties.

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
            "Integration Daemon",
        )
        url = (
            f"{self.runtime_command_root}/integration-daemon/"
            f"{server_guid}/integration-connectors/{connector_name}/configuration-properties"
        )
        response = await self._async_make_request("GET", url)
        props = response.json().get("properties", {})
        
        if output_format.upper() in ["DICT", "JSON"]:
            return props
            
        # Convert to Key/Value list for other formats
        elements = [{"Property": k, "Value": v} for k, v in props.items()] if props else []
        
        # Use a simple dynamic report spec for properties
        columns_struct = {
            "formats": {
                "attributes": [
                    {"key": "Property", "label": "Property", "value": ""},
                    {"key": "Value", "label": "Value", "value": ""}
                ]
            }
        }
        
        def extract_kv(elem, cols):
            c_data = populate_columns_from_properties(elem, cols)
            c_list = c_data.get("formats", {}).get("attributes", [])
            for c in c_list:
                c['value'] = elem.get(c['key'])
            return c_data

        return self._generate_formatted_output(
            elements=elements,
            query_string=connector_name,
            entity_type="Properties",
            output_format=output_format,
            extract_properties_func=extract_kv,
            report_spec=columns_struct
        )

    def get_integration_connector_config_properties(
        self,
        connector_name: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "IntegrationConnector",
        body: Optional[dict | GetRequestBody] = None,
    ) -> dict | str:
        """Retrieve the configuration properties of the named integration connector running in the integration daemon.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        connector_name : str
            Name of the integration connector to retrieve properties for.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "IntegrationConnector".

        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           Dict of the connector configuration properties.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_integration_connector_config_properties(
                connector_name, server_guid, display_name, qualified_name, output_format, report_spec, body
            )
        )
        return response

    async def _async_update_connector_configuration(
        self,
        connector_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        merge_update: bool = True,
        config_properties: dict = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Update the configuration properties of the integration connectors, or specific integration connector
            if a connector name is supplied.  This update is in memory and will not persist over a server restart.
            Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        connector_name : str, default = None
            Name of the integration connector to update properties for. If none, all connectors will be updated.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.

        merge_update : bool, optional, default = False
            Specifies whether properties should be over-written or completely replace existing properties. If False
            the values will be replaced; if True, they will be merged.
        config_properties : dict, optional, default = None
            A dict of Property Name, Property Value pairs.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Integration Daemon",
        )
        url = (
            f"{self.runtime_command_root}/integration-daemon/"
            f"{server_guid}/integration-connectors/configuration-properties"
        )

        if body is None:
            body = {
                "class": "ConnectorConfigPropertiesRequestBody",
                "connectorName": connector_name,
                "mergeUpdate": merge_update,
                "configurationProperties": config_properties,
            }
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_connector_configuration(
        self,
        connector_name: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        merge_update: bool = False,
        config_properties: dict = None,
        body: Optional[dict] = None,
    ) -> None:
        """Update the configuration properties of the integration connectors, or specific integration connector
            if a connector name is supplied.  This update is in memory and will not persist over a server restart.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        merge_update : bool, optional, default = False
            Specifies whether properties should be over-written or completely replace existing properties. If False
            the values will be replaced; if True, they will be merged.
        config_properties : dict, optional, default = None
            A dict of Property Name, Property Value pairs.

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_connector_configuration(
                connector_name,
                server_guid,
                display_name,
                qualified_name,
                merge_update,
                config_properties,
                body,
            )
        )
        return

    async def _async_update_endpoint_address(
        self,
        connector_name: str,
        endpoint_address: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> None:
        """Update the endpoint network address for a specific integration connector.  Typically used for discovery.
            This update is in memory and will not persist over a server restart. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        endpoint_address : str
            Specifies the new network endpoint address. This is the full address string - can include protocol,
            port, operation, etc.

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, display_name, "qualifiedName", qualified_name, "Connection"
        )
        url = (
            f"{self.runtime_command_root}/integration-daemon/"
            f"{server_guid}/integration-connectors/{connector_name}/endpoint-network-address"
        )

        if body is None:
            body = {
                "class": "StringRequestBody",
                "string": endpoint_address,
            }
        await self._async_make_request("POST", url, body)
        return

    def update_endpoint_address(
        self,
        connector_name: str,
        endpoint_address: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> None:
        """Update the endpoint network address for a specific integration connector.  Typically used for discovery.
            This update is in memory and will not persist over a server restart. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        endpoint_address : str
            Specifies the new network endpoint address. This is the full address string - can include protocol,
            port, operation, etc.

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_endpoint_address(
                connector_name,
                endpoint_address,
                server_guid,
                display_name,
                qualified_name,
                body,
            )
        )
        return

    async def _async_stop_connector(
        self,
        connector_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Stop the named integration connector OR all connectors if connector name is None.  Async version.

        Parameters
        ----------
        connector_name : str, default = None
            Name of the integration connector to stop. If none, all connectors will be stopped.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Integration Daemon",
        )

        if connector_name is None:
            url = (
                f"{self.runtime_command_root}/integration-daemon/"
                f"{server_guid}/integration-connectors/stop"
            )
        else:
            url = (
                f"{self.runtime_command_root}/integration-daemon/"
                f"{server_guid}/integration-connectors/{connector_name}/stop"
            )

        await self._async_make_request("GET", url, body=body)
        return

    def stop_connector(
        self,
        connector_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Stop the named integration connector OR all connectors if connector name is None.

        Parameters
        ----------
        connector_name : str, default = None
            Name of the integration connector to stop. If none, all connectors will be stopped.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_stop_connector(
                connector_name, server_guid, display_name, qualified_name, body
            )
        )
        return

    async def _async_start_connector(
        self,
        connector_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Start the named integration connector OR all connectors if connector name is None.  Async version.

        Parameters
        ----------
        connector_name : str, default = None
            Name of the integration connector to start. If none, all connectors will be started.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Integration Daemon",
        )

        if connector_name is None:
            url = (
                f"{self.runtime_command_root}/integration-daemon/"
                f"{server_guid}/integration-connectors/start"
            )
        else:
            url = (
                f"{self.runtime_command_root}/integration-daemon/"
                f"{server_guid}/integration-connectors/{connector_name}/start"
            )

        await self._async_make_request("GET", url, body=body)
        return

    def start_connector(
        self,
        connector_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Start the named integration connector OR all connectors if connector name is None.

        Parameters
        ----------
        connector_name : str, default = None
            Name of the integration connector to start. If none, all connectors will be started.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_start_connector(
                connector_name, server_guid, display_name, qualified_name, body
            )
        )
        return

    async def _async_connect_to_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to register with the named cohort.  Async version.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, server_name, "resourceName", tech_type="OMAG Server"
        )
        url = (
            f"{self.runtime_command_root}/omag-servers/"
            f"{server_guid}/cohorts/{cohort_name}"
        )
        await self._async_make_request("POST", url, body=body)
        return

    def connect_to_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to register with the named cohort.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_connect_to_cohort(cohort_name, server_guid, server_name, body)
        )
        return

    async def _async_disconnect_from_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to disconnect from the named cohort. Async version.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, server_name, "resourceName", tech_type="OMAG Server"
        )
        url = (
            f"{self.runtime_command_root}/omag-servers/"
            f"{server_guid}/cohorts/{cohort_name}"
        )
        await self._async_make_request("DELETE", url, body=body)
        return

    def disconnect_from_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to disconnect from the named cohort.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_disconnect_from_cohort(cohort_name, server_guid, server_name, body)
        )
        return

    async def _async_unregister_from_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to unregister from the named cohort. Async version.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, server_name, "resourceName", tech_type="OMAG Server"
        )
        url = (
            f"{self.runtime_command_root}/omag-servers/"
            f"{server_guid}/cohorts/{cohort_name}/unregister"
        )
        await self._async_make_request("POST", url, body=body)
        return

    def unregister_from_cohort(
        self, cohort_name: str, server_guid: str = None, server_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Request the named OMAG server to unregister from the named cohort.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to register with.
        server_guid : str, opt
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, opt
            Name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_unregister_from_cohort(cohort_name, server_guid, server_name, body)
        )
        return

    async def _async_refresh_gov_eng_config(
        self,
        gov_engine_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Request that the governance engine refresh its configuration by calling the metadata server. This request is
            useful if the metadata server has an outage, particularly while the governance server is initializing.
            This request just ensures that the latest configuration is in use. If gov_engine_name is None, all engines
            will be refreshed. Async version.

            https://egeria-project.org/concepts/governance-engine-definition/

        Parameters
        ----------
        gov_engine_name: str, default = None
            If None, then all engines will be refreshed - this is the normal case. If an engine is specified only this
            engine will be refreshed.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or display_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, opt, default is None.
                        Identity of the server to act on. Either the server_guid , qualified_name, or server_name must
                        be provided.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Governance Engine",
        )

        if gov_engine_name is None:
            url = (
                f"{self.runtime_command_root}/governance-engines/"
                f"{server_guid}/refresh-config"
            )
        else:
            url = (
                f"{self.runtime_command_root}/governance-engines/"
                f"{server_guid}/governance-engines/{gov_engine_name}/refresh-config"
            )

        await self._async_make_request("GET", url, body=body)
        return

    async def _async_refresh_integ_group_config(
        self,
        integ_group_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Request that the integration group refresh its configuration by calling the metadata access server.
            Changes to the connector configuration will result in the affected connectors being restarted.
            This request is useful if the metadata access server has an outage, particularly while the integration
            daemon is initializing. This request just ensures that the latest configuration is in use. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        integ_group_name : str, opt, default = None

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Integration Daemon",
        )
        url = (
            f"{self.runtime_command_root}/integration-daemon/"
            f"{server_guid}/integration-groups/{integ_group_name}/refresh-config"
        )

        await self._async_make_request("GET", url, body=body)
        return

    def refresh_integ_group_config(
        self,
        integ_group_name: Optional[str] = None,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict] = None,
    ) -> None:
        """Request that the integration group refresh its configuration by calling the metadata access server.
            Changes to the connector configuration will result in the affected connectors being restarted.
            This request is useful if the metadata access server has an outage, particularly while the integration
            daemon is initializing. This request just ensures that the latest configuration is in use.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        integ_group_name : str, opt, default = None
            Name of the integration group to refresh. If None, all groups are refreshed.

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_refresh_integ_group_config(
                integ_group_name, server_guid, display_name, qualified_name, body
            )
        )
        return

    #
    # Open Lineage & Archives
    #
    async def _async_publish_open_lineage_event(
        self,
        ol_event: dict,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Send an Open Lineage event to the integration daemon. It will pass it on to the integration connectors that
            have registered a listener for open lineage events. Async version.

            https://egeria-project.org/features/lineage-management/overview/#the-openlineage-standard

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        ol_event : dict
            Dict containing the user specified Open Lineage event.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "resourceName",
            qualified_name,
        )
        url = (
            f"{self.runtime_command_root}/integration-daemons/{server_guid}/open-lineage-events/publish-event-string"
        )

        payload = body if body else ol_event
        await self._async_make_request("POST", url, payload)

    def publish_open_lineage_event(
        self,
        ol_event: dict,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Send an Open Lineage event to the integration daemon. It will pass it on to the integration connectors that
            have registered a listener for open lineage events.

            https://egeria-project.org/features/lineage-management/overview/#the-openlineage-standard

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        ol_event : dict
            Dict containing the user specified Open Lineage event.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_publish_open_lineage_event(ol_event, server_guid, display_name, qualified_name, body)
        )


    async def _async_add_archive_content(
        self,
        archive_content: dict,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        time_out: int = 60,
        body: Optional[dict | ArchiveRequestBody] = None,
    ) -> None:
        """An open metadata archive contains metadata types and instances.
            This operation loads the supplied open metadata archive into the local repository. It can be used with OMAG
            servers that are of type Open Metadata Store. Async version.

                https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        archive_content : dict
            A dict containing the content of the archive to load.
        time_out : int, optional, default = 60 seconds
            Timeout for the REST call.

        body : dict | ArchiveRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
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
            "qualifiedName",
            qualified_name,
            "Metadata Access Server",
        )
        url = (
            f"{self.runtime_command_root}/metadata-access-stores/{server_guid}/instance/load/open-metadata-archives/"
            f"archive-content"
        )

        payload = body if body else archive_content
        await self._async_make_request("POST", url, payload, time_out=time_out)
        return

    def add_archive_content(
        self,
        archive_content: dict,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        time_out: int = 60,
        body: Optional[dict | ArchiveRequestBody] = None,
    ) -> None:
        """An open metadata archive contains metadata types and instances.
            This operation loads the supplied open metadata archive into the local repository. It can be used with OMAG
            servers that are of type Open Metadata Store.

                https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        archive_content : dict
            A dict containing the content of the archive to load.
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid or server_name must be.
        time_out : int, optional, default = 60 seconds
            Timeout for the REST call.

        body : dict | ArchiveRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_archive_content(
                archive_content, server_guid, display_name, qualified_name, time_out, body
            )
        )
        return

    async def _async_add_archive_file(
        self,
        archive_file: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        time_out: int = 120,
        body: Optional[dict | ArchiveRequestBody] = None,
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

        body : dict | ArchiveRequestBody, optional
            Request body to pass directly to the API.

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
            "resourceName",
            qualified_name,
            "Metadata Access Server",
        )
        url = f"{self.runtime_command_root}/metadata-access-stores/{server_guid}/instance/load/open-metadata-archives/file"

        payload = body if body else archive_file
        await self._async_make_request(
            "POST-DATA", url, payload, time_out=time_out
        )
        return

    def add_archive_file(
        self,
        archive_file: str,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        time_out: int = 120,
        body: Optional[dict | ArchiveRequestBody] = None,
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

        body : dict | ArchiveRequestBody, optional
            Request body to pass directly to the API.

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
                archive_file, server_guid, display_name, qualified_name, time_out, body
            )
        )
        return

    #
    # Server & Platform admin
    #
    async def _async_shutdown_and_unregister_server(
        self,
        server_guid: Optional[str] = None,
        qualified_name: Optional[str] = None,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Shutdown the named OMAG server. The server will also be removed from any open metadata repository cohorts
            it has registered with.  Async version.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name  must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid  must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

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
            server_guid, property_name="qualifiedName", qualified_name=qualified_name
        )
        url = f"{self.runtime_command_root}/omag-servers/{server_guid}"

        await self._async_make_request("DELETE", url, body=body)

        return

    def shutdown_and_unregister_server(
        self, server_guid: Optional[str] = None, qualified_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Shutdown the named OMAG server. The server will also be removed from any open metadata repository cohorts
            it has registered with.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name  must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid  must be.
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

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
            self._async_shutdown_and_unregister_server(server_guid, qualified_name, body)
        )
        return

    async def _async_activate_server_with_stored_config(
        self,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        timeout: int = 240,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Activate the named OMAG server using the appropriate configuration document found in the
            configuration store. Async version.

        https://egeria-project.org/concepts/configuration-document

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name or server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid or qualified_name must be.
        qualified_name: str, default = None
            Unique name of server to act on. If not specified, server_guid  must be.
        timeout: int, optional, default = 240 seconds

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, display_name, "resourceName", qualified_name
        )

        url = f"{self.runtime_command_root}/omag-servers/{server_guid}/instance"

        await self._async_make_request("POST", url, body=body, time_out=timeout)
        return

    def activate_server_with_stored_config(
        self,
        server_guid: Optional[str] = None,
        display_name: Optional[str] = None,
        qualified_name: Optional[str] = None,
        timeout: int = 240,
        body: Optional[dict | FilterRequestBody] = None,
    ) -> None:
        """Activate the named OMAG server using the appropriate configuration document found in the
            configuration store.

        https://egeria-project.org/concepts/configuration-document

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, server_name must be.
        display_name: str, default = None
            Name of server to act on. If not specified, server_guid must be.
        timeout: int, optional, default = 240 seconds

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           None

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_activate_server_with_stored_config(
                server_guid, display_name, qualified_name, timeout, body
            )
        )
        return

    async def _async_shutdown_server(
        self, server_guid: Optional[str] = None, qualified_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Temporarily shutdown the named OMAG server. This server can be restarted as a later time.  Async version.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name must be.
        qualified_name: str, default = None
            Qualified name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

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
            server_guid, None, "qualifiedName", qualified_name
        )
        url = f"{self.runtime_command_root}/omag-servers/{server_guid}/instance"

        await self._async_make_request("DELETE", url, body=body)

        return

    def shutdown_server(
        self, server_guid: Optional[str] = None, qualified_name: str = None, body: Optional[dict | FilterRequestBody] = None
    ) -> None:
        """Temporarily shutdown the named OMAG server. This server can be restarted as a later time.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, qualified_name must be.
        qualified_name: str, default = None
            Qualified name of server to act on. If not specified, server_guid must be.

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

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
            self._async_shutdown_server(server_guid, qualified_name, body)
        )
        return

    def get_platforms_by_name(
        self,
        filter_string: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: str | dict = "Platforms",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of platforms with a particular name. The name is specified in the filter.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the display name or qualified name of the platforms to return information for. If the
            value is None, we will default to the default_platform_name that comes from the core content pack.
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platforms".

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        Response
           A list of JSONdict with the platform reports.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platforms_by_name(
                filter_string, start_from, page_size, output_format, report_spec, body
            )
        )
        return response

    @dynamic_catch
    async def _async_get_platforms_by_name(
        self,
        filter_string: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Platforms",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of platforms with a particular name. The name is specified in the filter.  Async version.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the display name or qualified name of the platforms to return information for. If the
            value is None, we will default to the default_platform_name that comes from the core content pack.

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platforms".

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        Response
           A list of JSONdict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        if filter_string is None:
            filter_string = self.default_platform_name

        url = (
            f"{self.runtime_command_root}/platforms/by-name"
        )

        return await self._async_get_name_request(url, _type="Platforms", _gen_output=self._generate_platform_output,
                                                  filter_string=filter_string, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)

    @dynamic_catch
    async def _async_get_platforms_by_type(
        self,
        filter_string: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: str | dict = "Platforms",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.  Async version.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platforms".

        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        Response
           A list of JSONdict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        if filter_string is None:
            filter_string = "OMAG Server Platform"

        url = (
            f"{self.runtime_command_root}/platforms/by-deployed-implementation-type"
        )

        return await self._async_get_name_request(url, _type="Platforms", _gen_output=self._generate_platform_output,
                                                  filter_string=filter_string, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)

    def get_platforms_by_type(
        self,
        filter_string: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: str | dict = "Platforms",
        body: Optional[dict | GetRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platforms".

        body : dict, optional
            Request body to pass directly to the API.

        Returns
        -------
           A list of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_platforms_by_type(
                filter_string, start_from, page_size, output_format, report_spec, body
            )
        )

    async def _async_get_platform_templates_by_type(
        self,
        filter_string: Optional[str] = None,
        effective_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON", report_spec: str | dict = "Platforms",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list:
        """Returns the list of platform templates for a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.
            Async version.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The specification of the report to generate. Default is "Platforms".
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        if filter_string is None:
            filter_string = "OMAG Server Platform"

        url = (
            f"{self.runtime_command_root}/platforms/by-deployed-implementation-type"
        )


        return await self._async_get_name_request(url, _type="Platforms", _gen_output=self._generate_platform_output,
                                                  filter_string=filter_string, classification_names=["Template"],
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

    def get_platform_templates_by_type(
        self,
        filter_string: Optional[str] = None,
        effective_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON", report_spec: str | dict = "Platforms",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list:
        """Returns the list of platform templates with a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The specification of the report to generate. Default is "Platforms".
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platform_templates_by_type(filter_string, effective_time, start_from, page_size, body=body)
        )
        return response

    @dynamic_catch
    async def _async_get_platform_report(
        self, 
        platform_guid: Optional[str] = None, 
        platform_name: str = None,
        output_format: str = "JSON",
        report_spec: str | dict = "Platform-Report"
    ) -> str | list | dict:
        """Returns details about the running platform. Async version.

        Parameters
        ----------
        platform_guid : str
            The unique identifier for the platform. If not specified, platform_name must be.
        platform_name: str, default = None
            Name of server to act on. If not specified, platform_guid must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platform-Report".

        Returns
        -------
        Response
           A JSONdict with the platform report.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        platform_guid = await self.__async_get_guid__(guid=platform_guid, display_name= platform_name, property_name="displayName")
        url = f"{self.runtime_command_root}/platforms/{platform_guid}/report"

        response =  await self._async_make_request("GET",url)
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            elements = response.json().get("elementGraph", NO_ELEMENTS_FOUND)
            if type(elements) is str:
                logger.info(NO_ELEMENTS_FOUND)
                return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_platform_report_output(elements, "None", "Platform-Report", output_format, report_spec)
        return elements

    def get_platform_report(
        self, 
        platform_guid: Optional[str] = None, 
        platform_name: str = None,
        output_format: str = "JSON",
        report_spec: str | dict = "Platform-Report",
    ) -> str | list | dict:
        """Returns details about the running platform.

        Parameters
        ----------
        platform_guid : str
            The unique identifier for the platform. If not specified, platform_name must be.
        platform_name: str, default = None
            Name of server to act on. If not specified, platform_guid must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "Platform-Report".

        Returns
        -------
        Response
           A JSONdict with the platform report.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_platform_report(platform_guid, platform_name, output_format, report_spec)
        )

    async def _async_get_platform_by_guid(
        self,
        platform_guid: str,
        output_format: str = "JSON",
        report_spec: str | dict = "Platforms",
        body: Optional[dict | GetRequestBody] = None
    ) -> str | list:
        """Returns details about the platform's catalog entry (asset). Async version.

        Parameters
        ----------
        platform_guid : str
            Unique id of the platform to return details of.
        output_format: str, optional
            - The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            - The specification of the report to generate. Default is "Platforms".
        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        Response
           A list of JSONdict with the platform reports.

        """

        url = f"{self.runtime_command_root}/platforms/{platform_guid}"
            
        response = await self._async_get_guid_request(
            url=url,
            _type="SoftwareServerPlatform",
            _gen_output=self._generate_platform_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body
        )
        return response

    def get_platform_by_guid(
        self,
        platform_guid: str,
        output_format: str = "JSON", report_spec: str | dict = "Platforms",
        body: Optional[dict | GetRequestBody] = None,
    ) -> str | list:
        """Returns details about the platform's catalog entry (asset).

        Parameters
        ----------
        platform_guid : str, opt
            Identity of the platform to return details about.
        output_format: str, optional
        - The format of the output. Default is "JSON".
        report_spec: str | dict, optional
        - The specification of the report to generate. Default is "Platforms".

        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platform_by_guid(platform_guid, output_format, report_spec, body)
        )
        return response

    @dynamic_catch
    async def _async_get_server_by_guid(
        self,
        server_guid: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
        body: Optional[dict | GetRequestBody] = None,
    ) -> str | dict:
        """Returns details about the server's catalog entry (asset). Async version.

        Parameters
        ----------
        server_guid : str
            The unique identifier for the platform.
        output_format: str, optional
        - The format of the output. Default is "JSON".
        report_spec: str | dict, optional
        - The specification of the report to generate. Default is "OMAGServers".
        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException
        """

        url = f"{self.runtime_command_root}/software-servers/{server_guid}"
        response = await self._async_get_guid_request(
            url=url,
            _type="SoftwareServer",
            _gen_output=self._generate_omag_server_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body
        )
        return response


    @dynamic_catch
    def get_server_by_guid(
        self,
        server_guid: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
        body: Optional[dict | GetRequestBody] = None,
    ) -> str | dict:
        """Returns details about the platform's catalog entry (asset).

        Parameters
        ----------
        server_guid : str
            The unique identifier for the platform.
        output_format: str, optional
        - The format of the output. Default is "JSON".
        report_spec: str | dict, optional
        - The specification of the report to generate. Default is "OMAGServers".
        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_server_by_guid(server_guid, output_format=output_format,
                                           report_spec=report_spec, body=body)
        )
        return response

    @dynamic_catch
    async def _async_get_servers_by_name(
        self,
        filter_string: Optional[str] = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of servers with a particular name.  The name is specified in the filter. Async version.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "OMAGServers".

        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSON dict with the server reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        url = f"{self.runtime_command_root}/software-servers/by-name"

        
        return await self._async_get_name_request(url, _type="SoftwareServer",
                                                  _gen_output=self._generate_omag_server_output,
                                                  filter_string=filter_string, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)

    @dynamic_catch
    def get_servers_by_name(
        self, 
        filter_string: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
        body: Optional[dict | SearchStringRequestBody] = None,
    ) -> str | list | dict:
        """Returns the list of servers with a particular name.  The name is specified in the filter.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "OMAGServers".

        body : dict | SearchStringRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           List of JSON dict with the server reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_servers_by_name(
                filter_string, start_from, page_size, output_format, report_spec, body
            )
        )
        return response

    @dynamic_catch
    async def _async_get_servers_by_dep_impl_type(self, filter_string: str,
                                                  start_from: int = 0, page_size: int = 0, output_format:str="JSON",
                                                  report_spec: str = "OMAGServers",
                                                  body: Optional[dict | FilterRequestBody] = None) -> str | list:
        """Returns the list of servers with a particular deployed implementation type. The value is specified
            in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
           List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        if filter_string == "*":
            filter_string = None

        url = f"{self.runtime_command_root}/software-servers/by-deployed-implementation-type"

        return await self._async_get_name_request(url, _type="OMAGServers",
                                                  _gen_output=self._generate_omag_server_output,
                                                  filter_string=filter_string, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, body=body)


    @dynamic_catch
    def get_servers_by_dep_impl_type(self, search_string: str = "*", effective_time: Optional[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = "JSON", report_spec: str | dict = "OMAGServers",
                                     body: Optional[dict | FilterRequestBody] = None) -> str | list:
        """Returns the list of servers with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

        Parameters
        ----------
        search_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        body : dict | GetRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        Response
           A lit of JSONdict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        Args:
            output_format ():
            report_spec ():

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_servers_by_dep_impl_type(search_string, start_from,page_size,
                                                     output_format, report_spec, body)
        )
        return response

    async def _async_get_server_templates_by_dep_impl_type(
        self,
        filter_string : str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON", report_spec: dict = "OMAGServers",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list:
        """Returns the list of server templates with a particular deployed implementation type.   The value is
            specified in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

        Parameters
        ----------
        filter_string : str, optional
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: dict, optional
            The specification of the report to generate. Default is "OMAGServers".
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSONdict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """

        url = (
            f"{self.runtime_command_root}/software-servers/"
            f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}&getTemplates=true"
        )

        return await self._async_get_name_request(url, _type="OMAGServers",
                                                  _gen_output=self._generate_omag_server_output,
                                                  filter_string=filter_string, classification_names=["Template"],
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)


    def get_server_templates_by_dep_impl_type(
        self,
        filter_string : str,
        start_from: int = 0,
        page_size: int = max_paging_size,
        output_format: str = "JSON", report_spec: dict = "OMAGServers",
        body: Optional[dict | FilterRequestBody] = None,
    ) -> str | list:
        """Returns the list of server templates with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

        Parameters
        ----------
        filter_string : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: dict, optional
            The specification of the report to generate. Default is "OMAGServers".
        body : dict | FilterRequestBody, optional
            Request body to pass directly to the API.

        Returns
        -------
        List of JSON dict with the platform reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_server_templates_by_dep_impl_type(
                filter_string, start_from, page_size, output_format,report_spec,body
            )
        )
        return response

    @dynamic_catch
    async def _async_get_server_report(
        self, 
        server_guid: Optional[str] = None, 
        server_name: str = None,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
    ) -> str | list | dict:
        """Returns details about the running server. Async version.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, default = None
            Name of server to act on. If not specified, server_guid must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "OMAGServers".


        Returns
        -------
           List of JSON dict with the server reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        server_guid = self.__get_guid__(
            server_guid, server_name, "resourceName", tech_type="Integration Daemon"
        )
        url = f"{self.runtime_command_root}/omag-servers/{server_guid}/instance/report"

        response = await self._async_make_request("GET",url)
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            elements = response.json().get("elementGraph", NO_ELEMENTS_FOUND)
            if type(elements) is str:
                logger.info(NO_ELEMENTS_FOUND)
                return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_server_report_output(elements, "None", "Server-Report", output_format, report_spec)
        return elements

    def get_server_report(
        self, 
        server_guid: Optional[str] = None, 
        server_name: str = None,
        output_format: str = "JSON",
        report_spec: str | dict = "OMAGServers",
    ) -> str | list | dict:
        """Returns details about the running server.

        Parameters
        ----------
        server_guid : str, default = None
            Identity of the server to act on. If not specified, server_name must be.
        server_name: str, default = None
            Name of server to act on. If not specified, server_guid must be.
        output_format: str, optional
            The format of the output. Default is "JSON".
        report_spec: str | dict, optional
            The report specification to use. Default is "OMAGServers".

        Returns
        -------
           List of JSON dict with the server reports.

        Raises
        ------
        PyegeriaInvalidParameterException
        PyegeriaAPIException
        PyegeriaUnauthorizedException

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_server_report(server_guid, server_name, output_format, report_spec)
        )

    def _extract_platform_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a Platform element.
        """
        # First, populate from element.properties using the utility
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])

        if "platformUrlRoot" in element:
             for column in columns_list:
                key = column.get('key')
                if key == 'platform_url_root':
                    column['value'] = element.get('platformUrlRoot')
                elif key == 'version':
                    column['value'] = element.get('version')
                elif key == 'platform_origin':
                    column['value'] = element.get('platformOrigin')
                elif key == 'platform_start_time':
                    column['value'] = element.get('startTime')
                elif key == 'platform_build_properties':
                    column['value'] = element.get('platformBuildProperties')
                elif key == 'omagservers':
                    column['value'] = element.get('omagservers', element.get('omagServers'))
                elif key == 'guid':
                    column['value'] = element.get('guid', element.get('elementHeader', {}).get('guid', ''))
        else:
            header_props = _extract_referenceable_properties(element)
            for column in columns_list:
                key = column.get('key')
                if key in header_props:
                    column['value'] = header_props.get(key)
                elif key == 'guid':
                    column['value'] = header_props.get('GUID')
        
        return col_data

    @dynamic_catch
    def _generate_platform_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                  element_type_name: Optional[str] = None, output_format: str = "DICT",
                                  report_spec: dict | str = None, **kwargs) -> str | list[dict]:
        """ Generate output for Platform elements. """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "Platforms",
            output_format=output_format,
            extract_properties_func=self._extract_platform_properties,
            report_spec=report_spec,
            **kwargs
        )

    def _generate_platform_report_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                  element_type_name: Optional[str] = None, output_format: str = "DICT",
                                  report_spec: dict | str = None, **kwargs) -> str | list[dict]:
        """ Generate output for Platform Report elements. """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "SoftwareServerPlatform",
            output_format=output_format,
            extract_properties_func=self._extract_platform_properties,
            report_spec=report_spec,
            **kwargs
        )

    def _extract_omag_server_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from an OMAG Server element.
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        
        if "serverName" in element:
             for column in columns_list:
                key = column.get('key')
                if key == 'server_name':
                    column['value'] = element.get('serverName')
                elif key == 'server_type':
                    column['value'] = element.get('serverType')
                elif key == 'server_active_status':
                    column['value'] = element.get('serverActiveStatus')
                elif key == 'server_configuration':
                    column['value'] = str(element.get('serverConfiguration', ''))
                elif key == 'guid':
                     column['value'] = element.get('guid', '') 
        else:
            header_props = _extract_referenceable_properties(element)
            for column in columns_list:
                key = column.get('key')
                if key in header_props:
                    column['value'] = header_props.get(key)
                elif key == 'guid':
                    column['value'] = header_props.get('GUID')

        return col_data

    @dynamic_catch
    def _generate_omag_server_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                  element_type_name: Optional[str] = None, output_format: str = "DICT",
                                  report_spec: dict | str = None, **kwargs) -> str | list[dict]:
        """ Generate output for OMAGServer elements. """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "OMAGServers",
            output_format=output_format,
            extract_properties_func=self._extract_omag_server_properties,
            report_spec=report_spec,
            **kwargs
        )

    def _generate_server_report_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                     element_type_name: Optional[str] = None, output_format: str = "DICT",
                                     report_spec: dict | str = None, **kwargs) -> str | list[dict]:
        """ Generate output for OMAGServer elements. """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "OMAGServerReport",
            output_format=output_format,
            extract_properties_func=self._extract_omag_server_properties,
            report_spec=report_spec,
            **kwargs
        )

    def _extract_integration_connector_properties(self, element: dict, columns_struct: dict) -> dict:
        """ Extract common properties from an Integration Connector element. """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        
        if "connectorName" in element:
             for column in columns_list:
                key = column.get('key')
                if key == 'connector_name':
                    column['value'] = element.get('connectorName')
                elif key == 'connector_type':
                    column['value'] = element.get('connectorType', {}).get('displayName', '')
                elif key == 'metadata_source_qualified_name':
                    column['value'] = element.get('metadataSourceQualifiedName')
                elif key == 'status':
                    column['value'] = element.get('status')
                elif key == 'last_status_change':
                    column['value'] = element.get('lastStatusChange')
                elif key == 'guid':
                    column['value'] = element.get('guid', '')
        
        return col_data

    @dynamic_catch
    def _generate_integration_connector_output(self, elements: dict | list[dict], filter_string: Optional[str] = None,
                                  element_type_name: Optional[str] = None, output_format: str = "DICT",
                                  report_spec: dict | str = None, **kwargs) -> str | list[dict]:
        """ Generate output for IntegrationConnector elements. """
        return self._generate_formatted_output(
            elements=elements,
            query_string=filter_string,
            entity_type=element_type_name or "IntegrationConnectors",
            output_format=output_format,
            extract_properties_func=self._extract_integration_connector_properties,
            report_spec=report_spec,
            **kwargs
        )


if __name__ == "__main__":
    print("Main-Runtime Manager")

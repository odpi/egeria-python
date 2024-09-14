"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""
import asyncio

from requests import Response

from pyegeria import Client, max_paging_size, body_slimmer


class RuntimeManager(Client):
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
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.cur_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/runtime-manager"
        self.platform_guid = "44bf319f-1e41-4da1-b771-2753b92b631a"  # this is platform @ 9443 from the core content archive
        self.default_platform_name = (
            "Default Local OMAG Server Platform"  # this from the core content archive
        )

    #
    #   Cohorts
    #
    async def _async_connect_to_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """A new server needs to register the metadataCollectionId for its metadata repository with the other servers
            in the open metadata repository. It only needs to do this once and uses a timestamp to record that the
            registration event has been sent. If the server has already registered in the past, it sends a
            reregistration request.  Async version.

        https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        cohort_name : str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/cohort-members/"
            f"{server_guid}/cohorts/{cohort_name}/connect"
        )
        await self._async_make_request("GET", url)
        return

    def connect_to_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """A new server needs to register the metadataCollectionId for its metadata repository with the other servers
            in the open metadata repository. It only needs to do this once and uses a timestamp to record that the
            registration event has been sent. If the server has already registered in the past, it sends a
            reregistration request.

        https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid: str
           Identity of the server to act on.
        cohort_name: str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_connect_to_cohort(server_guid, cohort_name))
        return

    async def _async_disconnect_from_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """Disconnect communications from a specific cohort.  Async version.

            https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        cohort_name : str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/cohort-members/"
            f"{server_guid}/cohorts/{cohort_name}/disconnect"
        )
        await self._async_make_request("GET", url)
        return

    def disconnect_from_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """Disconnect communications from a specific cohort.

            https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid: str
           Identity of the server to act on.
        cohort_name: str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_disconnect_from_cohort(server_guid, cohort_name)
        )
        return

    async def _async_unregister_from_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """Unregister from a specific cohort and disconnect from cohort communications.  Async version.

            https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        cohort_name : str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/cohort-members/"
            f"{server_guid}/cohorts/{cohort_name}/unregister"
        )
        await self._async_make_request("GET", url)
        return

    def unregister_from_cohort(
        self,
        server_guid: str,
        cohort_name: str,
    ) -> None:
        """Unregister from a specific cohort and disconnect from cohort communications.
            https://egeria-project.org/concepts/cohort-member/

        Parameters
        ----------
        server_guid: str
           Identity of the server to act on.
        cohort_name: str
            Name of the cohort to join

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_disconnect_from_cohort(server_guid, cohort_name)
        )
        return

    #
    #   Governance Engines
    #

    async def _async_refresh_gov_eng_config(
        self,
        server_guid: str,
        gov_engine_name: str = None,
    ) -> None:
        """Request that the governance engine refresh its configuration by calling the metadata server. This request is
            useful if the metadata server has an outage, particularly while the governance server is initializing.
            This request just ensures that the latest configuration is in use.  Async version.

            https://egeria-project.org/concepts/governance-engine-definition/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        gov_engine_name : str, Opt
            Name of the governance engine to refresh. If None, then all governance engines will be refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/engine-hosts/"
            f"{server_guid}/governance_engines/{gov_engine_name}/refresh-config"
        )
        await self._async_make_request("GET", url)
        return

    def refresh_gov_eng_config(
        self,
        server_guid: str,
        gov_engine_name: str = None,
    ) -> None:
        """Request that the governance engine refresh its configuration by calling the metadata server. This request is
            useful if the metadata server has an outage, particularly while the governance server is initializing.
            This request just ensures that the latest configuration is in use.

            https://egeria-project.org/concepts/governance-engine-definition/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        gov_engine_name : str
            Name of the governance engine to refresh. If None, then all governance engines will be refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_refresh_gov_eng_config(server_guid, gov_engine_name)
        )
        return

    #
    #   Integration Connector Methods
    #
    async def _async_get_integ_connector_config_properties(
        self,
        server_guid: str,
        connector_name: str,
    ) -> dict | str:
        """Retrieve the configuration properties of the named integration connector running in the integration daemon.
            Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.

        Returns
        -------
           Dict of the connector configuration properties.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-connectors/{connector_name}/configuration-properties"
        )
        response = await self._async_make_request("GET", url)
        return response.json().get("properties", "No pproperties found")

    def get_integ_connector_config_properties(
        self,
        server_guid: str,
        connector_name: str,
    ) -> dict | str:
        """Retrieve the configuration properties of the named integration connector running in the integration daemon.
            Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_integ_connector_config_properties(
                server_guid, connector_name
            )
        )
        return response

    async def _async_update_connector_connection(
        self,
        server_guid: str,
        connector_name: str,
        merge_update: bool = False,
        config_properties: dict = None,
    ) -> None:
        """Update the configuration properties of the integration connectors, or specific integration connector
            if a connector name is supplied.  This update is in memory and will not persist over a server restart.
            Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        merge_update : bool, optional, default = False
            Specifies whether properties should be over-written or completely replace existing properties. If False
            the values will be replaced; if True, they will be merged.
        config_properties : dict, optional, default = None
            A dict of Property Name, Property Value pairs.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-connectors/{connector_name}/configuration-properties"
        )

        body = {
            "class": "ConnectorConfigPropertiesRequestBody",
            "connectorName": connector_name,
            "mergeUpdate": merge_update,
            "configurationProperties": config_properties,
        }
        await self._async_make_request("POST", url, body)
        return

    def update_connector_connection(
        self,
        server_guid: str,
        connector_name: str,
        merge_update: bool = False,
        config_properties: dict = None,
    ) -> None:
        """Update the configuration properties of the integration connectors, or specific integration connector
            if a connector name is supplied.  This update is in memory and will not persist over a server restart.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        merge_update : bool, optional, default = False
            Specifies whether properties should be over-written or completely replace existing properties. If False
            the values will be replaced; if True, they will be merged.
        config_properties : dict, optional, default = None
            A dict of Property Name, Property Value pairs.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_connector_connection(
                server_guid, connector_name, merge_update, config_properties
            )
        )
        return

    async def _async_update_endpoint_address(
        self, server_guid: str, connector_name: str, endpoint_address: str
    ) -> None:
        """Update the endpoint network address for a specific integration connector.  Typically used for discovery.
            This update is in memory and will not persist over a server restart. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        endpoint_address : str
            Specifies the new network endpoint address. This is the full address string - can include protocol,
            port, operation, etc.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-connectors/{connector_name}/endpoint-network-address"
        )

        body = {
            "class": "StringRequestBody",
            "string": endpoint_address,
        }
        await self._async_make_request("POST", url, body)
        return

    def update_endpoint_address(
        self, server_guid: str, connector_name: str, endpoint_address: str
    ) -> None:
        """Update the endpoint network address for a specific integration connector.  Typically used for discovery.
            This update is in memory and will not persist over a server restart. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str
            Name of the integration connector to retrieve properties for.
        endpoint_address : str
            Specifies the new network endpoint address. This is the full address string - can include protocol,
            port, operation, etc.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_endpoint_address(
                server_guid, connector_name, endpoint_address
            )
        )
        return

    async def _async_refresh_integration_connectors(
        self, server_guid: str, connector_name: str = None
    ) -> None:
        """Issue a refresh() request on all connectors running in the integration daemon, or a specific connector if
            the connector name is specified. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str, opt
            Name of the integration connector to retrieve properties for. If None, all connectors refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-connectors/refresh"
        )

        body = {
            "class": "NameRequestBody",
            "string": connector_name,
        }
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def refresh_integration_connectors(
        self, server_guid: str, connector_name: str = None
    ) -> None:
        """Issue a refresh() request on all connectors running in the integration daemon, or a specific connector if
            the connector name is specified.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str, opt
            Name of the integration connector to retrieve properties for. If None, all connectors refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_refresh_integration_connectors(server_guid, connector_name)
        )
        return

    async def _async_restart_integration_connectors(
        self, server_guid: str, connector_name: str = None
    ) -> None:
        """Issue a restart() request on all connectors running in the integration daemon, or a specific connector if
            the connector name is specified. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str, opt
            Name of the integration connector to retrieve properties for. If None, all connectors restarted.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-connectors/restart"
        )

        body = {
            "class": "NameRequestBody",
            "string": connector_name,
        }
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def restart_integration_connectors(
        self, server_guid: str, connector_name: str = None
    ) -> None:
        """Issue a restart() request on all connectors running in the integration daemon, or a specific connector if
            the connector name is specified.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        connector_name : str, opt
            Name of the integration connector to retrieve properties for. If None, all connectors restarted.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_restart_integration_connectors(server_guid, connector_name)
        )
        return

    async def _async_refresh_integ_group_config(
        self, server_guid: str, integ_group_name: str = None
    ) -> None:
        """Request that the integration group refresh its configuration by calling the metadata access server.
            Changes to the connector configuration will result in the affected connectors being restarted.
            This request is useful if the metadata access server has an outage, particularly while the integration
            daemon is initializing. This request just ensures that the latest configuration is in use. Async version.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        integ_group_name : str, opt, default = None
            Name of the integration group to refresh. If None, all groups are refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-groups/{integ_group_name}/refresh-config"
        )

        await self._async_make_request("GET", url)
        return

    def refresh_integ_group_config(
        self, server_guid: str, integ_group_name: str = None
    ) -> None:
        """Request that the integration group refresh its configuration by calling the metadata access server.
            Changes to the connector configuration will result in the affected connectors being restarted.
            This request is useful if the metadata access server has an outage, particularly while the integration
            daemon is initializing. This request just ensures that the latest configuration is in use.

            https://egeria-project.org/concepts/integration-connector/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        integ_group_name : str, opt, default = None
            Name of the integration group to refresh. If None, all groups are refreshed.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_refresh_integ_group_config(server_guid, integ_group_name)
        )
        return

    #
    # Open Lineage & Archives
    #
    async def _async_publish_open_lineage_event(
        self, server_guid: str, ol_event: dict
    ) -> None:
        """Send an Open Lineage event to the integration daemon. It will pass it on to the integration connectors that
            have registered a listener for open lineage events. Async version.

            https://egeria-project.org/features/lineage-management/overview/#the-openlineage-standard

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        ol_event : dict
            Dict containing the user specified Open Lineage event.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/integration-daemons/"
            f"{server_guid}/integration-daemons/{server_guid}/open-lineage-events/publish"
        )

        await self._async_make_request("POST", url, ol_event)
        return

    def publish_open_lineage_event(self, server_guid: str, ol_event: dict) -> None:
        """Send an Open Lineage event to the integration daemon. It will pass it on to the integration connectors that
            have registered a listener for open lineage events.

            https://egeria-project.org/features/lineage-management/overview/#the-openlineage-standard

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        ol_event : dict
            Dict containing the user specified Open Lineage event.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_publish_open_lineage_event(server_guid, ol_event)
        )
        return

    async def _async_add_archive_content(
        self, server_guid: str, archive_content: dict, time_out: int = 60
    ) -> None:
        """An open metadata archive contains metadata types and instances.
            This operation loads the supplied open metadata archive into the local repository. It can be used with OMAG
            servers that are of type Open Metadata Store. Async version.

                https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        archive_content : dict
            A dict containing the content of the archive to load.
        time_out : int, optional, default = 60 seconds
            Timeout for the REST call.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/metadata-access-stores/{server_guid}/instance/load/open-metadata-archives/"
            f"archive-content"
        )

        await self._async_make_request("POST", url, archive_content, time_out=time_out)
        return

    def add_archive_content(
        self, server_guid: str, archive_content: dict, time_out: int = 60
    ) -> None:
        """An open metadata archive contains metadata types and instances.
            This operation loads the supplied open metadata archive into the local repository. It can be used with OMAG
            servers that are of type Open Metadata Store.

                https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.
        archive_content : dict
            A dict containing the content of the archive to load.
        time_out : int, optional, default = 60 seconds
            Timeout for the REST call.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_archive_content(
                server_guid, archive_content, time_out=time_out
            )
        )
        return

    async def _async_add_archive_file(
        self,
        archive_file: str,
        server_guid: str,
        time_out: int = 60,
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
        server_guid: str
            GUID of the server to load the file into.
        time_out: int, optional
           Time out for the rest call.

        Returns
        -------
        Response
          None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/metadata-access-stores/{server_guid}/instance/load/open-metadata-archives/file"

        await self._async_make_request(
            "POST-DATA", url, archive_file, time_out=time_out
        )
        return

    def add_archive_file(
        self,
        archive_file: str,
        server_guid: str,
        time_out: int = 60,
    ) -> None:
        """Add a new open metadata archive to running OMAG Server's repository.
            An open metadata archive contains metadata types and instances.  This operation loads an open metadata archive
            that is stored in the named file.  It can be used with OMAG servers that are of type Open Metadata Store.

            https://egeria-project.org/concepts/open-metadata-archives/

        Parameters
        ----------
        archive_file: str
            Open metadata archive file to load.
        server_guid: str
            GUID of the server to load the file into.
        time_out: int, optional, default = 60 seconds

        Returns
        -------
        Response
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_archive_file(archive_file, server_guid, time_out)
        )
        return

    #
    # Server & Platform admin
    #
    async def _async_shutdown_and_unregister_server(self, server_guid: str) -> None:
        """Shutdown the named OMAG server. The server will also be removed from any open metadata repository cohorts
            it has registered with.  Async version.

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
        Response
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/omag-servers/{server_guid}"

        await self._async_make_request("DELETE", url)

        return

    def shutdown_and_unregister_server(self, server_guid: str) -> None:
        """Shutdown the named OMAG server. The server will also be removed from any open metadata repository cohorts
            it has registered with.

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
        Response
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_and_unregister_server(server_guid))
        return

    async def _async_activate_server_with_stored_config(self, server_guid: str) -> None:
        """Activate the named OMAG server using the appropriate configuration document found in the
            configuration store. Async version.

        https://egeria-project.org/concepts/configuration-document

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/omag-servers/{server_guid}/instance"

        await self._async_make_request("POST", url)
        return

    def activate_server_with_stored_config(self, server_guid: str) -> None:
        """Activate the named OMAG server using the appropriate configuration document found in the
            configuration store.

        https://egeria-project.org/concepts/configuration-document

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_activate_server_with_stored_config(server_guid)
        )
        return

    async def _async_shutdown_server(self, server_guid: str) -> None:
        """Temporarily shutdown the named OMAG server. This server can be restarted as a later time.  Async version.

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
        Response
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/omag-servers/{server_guid}/instance"

        await self._async_make_request("DELETE", url)

        return

    def shutdown_server(self, server_guid: str) -> None:
        """Temporarily shutdown the named OMAG server. This server can be restarted as a later time.

        Parameters
        ----------
        server_guid : str
            Identity of the server to act on.

        Returns
        -------
        Response
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_shutdown_server(server_guid))
        return

    def get_platforms_by_name(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platforms with a particular name. The name is specified in the filter.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the display name or qualified name of the platforms to return information for. If the
            value is None, we will default to the default_platform_name that comes from the core content pack.
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platforms_by_name(
                filter, effective_time, start_from, page_size
            )
        )
        return response

    async def _async_get_platforms_by_name(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platforms with a particular name. The name is specified in the filter.  Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the display name or qualified name of the platforms to return information for. If the
            value is None, we will default to the default_platform_name that comes from the core content pack.
        effective_time: str, optional
           Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        if filter is None:
            filter = self.default_platform_name

        url = (
            f"{self.cur_command_root}/platforms/by-name?"
            f"startFrom={start_from}&pageSize={page_size}"
        )
        if effective_time is not None:
            body = {"filter": filter, "effectiveTime": effective_time}
        else:
            body = {"filter": filter}

        response = await self._async_make_request("POST", url, body)

        return response.json().get("elements", "No platforms found")

    async def _async_get_platforms_by_type(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.  Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        if filter is None:
            filter = "OMAG Server Platform"

        url = (
            f"{self.cur_command_root}/platforms/"
            f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}"
        )

        if effective_time is not None:
            body = {"filter": filter, "effectiveTime": effective_time}
        else:
            body = {"filter": filter}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "No platforms found")

    def get_platforms_by_type(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platforms with a particular deployed implementation type.  The value is specified in
            the filter. If it is null, or no request body is supplied, all platforms are returned.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platforms_by_type(
                filter, effective_time, start_from, page_size
            )
        )
        return response

    async def _async_get_platform_templates_by_type(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platform templates for a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.
            Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
               The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        if filter is None:
            filter = "OMAG Server Platform"

        url = (
            f"{self.cur_command_root}/platforms/"
            f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}&getTemplates=true"
        )

        if effective_time is not None:
            body = {"filter": filter, "effectiveTime": effective_time}
        else:
            body = {"filter": filter}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "No platforms found")

    def get_platform_templates_by_type(
        self,
        filter: str = None,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of platform templates with a particular deployed implementation type.  The value is
            specified in the filter. If it is null, or no request body is supplied, all platforms are returned.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platforms_by_type(
                filter, effective_time, start_from, page_size
            )
        )
        return response

    async def _async_get_platform_report(self, platform_guid: str = None) -> str | list:
        """Returns details about the running platform. Async version.

        Parameters
        ----------
        platform_guid : str
            The unique identifier for the platform.

        Returns
        -------
        Response
           A json dict with the platform report.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/platforms/{platform_guid}/report"

        response = await self._async_make_request("GET", url)

        return response.json().get("element", "No platforms found")

    def get_platform_report(self, platform_guid: str = None) -> str | list:
        """Returns details about the running platform.

        Parameters
        ----------
        platform_guid : str
            The unique identifier for the platform.

        Returns
        -------
        Response
           A json dict with the platform report.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platform_report(platform_guid)
        )
        return response

    async def _async_get_platform_by_guid(
        self,
        platform_guid: str,
        effective_time: str = None,
    ) -> str | list:
        """Returns details about the platform's catalog entry (asset). Async version.

        Parameters
        ----------
        platform_guid : str
            Unique id of the platform to return details of.
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).


        Returns
        -------
        Response
           A list of json dict with the platform reports.

        """

        url = f"{self.cur_command_root}/platforms/{platform_guid}"

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)

        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elements", "No platforms found")

    def get_platform_by_guid(
        self,
        platform_guid: str,
        effective_time: str = None,
    ) -> str | list:
        """Returns details about the platform's catalog entry (asset).

        Parameters
        ----------
        platform_guid : str, opt
            Identity of the platform to return details about.
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_platform_by_guid(platform_guid, effective_time)
        )
        return response

    async def _async_get_server_by_guid(
        self, server_guid: str, effective_time: str = None
    ) -> str | dict:
        """Returns details about the server's catalog entry (asset). Async version.

        Parameters
        ----------
        server_guid : str
            The unique identifier for the platform.
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/software-servers/{server_guid}"

        if effective_time is not None:
            body = {"effectiveTime": effective_time}
            response = await self._async_make_request("POST", url, body)

        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elements", "No server found")

    def get_server_by_guid(
        self, server_guid: str, effective_time: str = None
    ) -> str | dict:
        """Returns details about the platform's catalog entry (asset).

        Parameters
        ----------
        server_guid : str
            The unique identifier for the platform.
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_server_by_guid(server_guid, effective_time)
        )
        return response

    async def _async_get_servers_by_name(
        self,
        filter: str,
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of servers with a particular name.  The name is specified in the filter. Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = (
            f"{self.cur_command_root}/software-servers/by-name?"
            f"startFrom={start_from}&pageSize={page_size}"
        )

        if effective_time is None:
            body = {"filter": filter}
        else:
            body = {"filter": filter, "effective_time": effective_time}
        response = await self._async_make_request("POST", url, body)

        return response.json().get("elements", "No platforms found")

    def get_servers_by_name(
        self, filter: str, effective_time: str = None
    ) -> str | list:
        """Returns the list of servers with a particular name.  The name is specified in the filter.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_servers_by_name(filter, effective_time)
        )
        return response

    async def _async_get_servers_by_dep_impl_type(
        self,
        filter: str = "*",
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of servers with a particular deployed implementation type. The value is specified
            in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        if filter == "*":
            filter = None

        url = (
            f"{self.cur_command_root}/software-servers/"
            f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}"
        )

        body = body_slimmer({"filter": filter, "effective_time": effective_time})

        response = await self._async_make_request("POST", url, body)

        return response.json().get("elements", "No servers found")

    def get_servers_by_dep_impl_type(
        self,
        filter: str = "*",
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of servers with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_servers_by_dep_impl_type(
                filter, effective_time, start_from, page_size
            )
        )
        return response

    async def _async_get_server_templates_by_dep_impl_type(
        self,
        filter: str = "*",
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of server templates with a particular deployed implementation type.   The value is
            specified in the filter. If it is null, or no request body is supplied, all servers are returned.
            Async version.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        if filter == "*":
            filter = None

        url = (
            f"{self.cur_command_root}/software-servers/"
            f"by-deployed-implementation-type?startFrom={start_from}&pageSize={page_size}&getTemplates=true"
        )

        body = body_slimmer({"filter": filter, "effective_time": effective_time})

        response = await self._async_make_request("POST", url, body)

        return response.json().get("elements", "No platforms found")

    def get_server_templates_by_dep_impl_type(
        self,
        filter: str = "*",
        effective_time: str = None,
        start_from: int = 0,
        page_size: int = max_paging_size,
    ) -> str | list:
        """Returns the list of server templates with a particular deployed implementation type.
            The value is specified in the filter. If it is null, or no request body is supplied,
            all servers are returned.

        Parameters
        ----------
        filter : str, opt
            Filter specifies the kind of deployed implementation type of the platforms to return information for.
            If the value is None, we will default to the "OMAG Server Platform".
        effective_time: str, optional
            Timeframe to return information for. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.
        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `max_paging_size`.

        Returns
        -------
        Response
           A lit of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_server_templates_by_dep_impl_type(
                filter, effective_time, start_from, page_size
            )
        )
        return response

    async def _async_get_server_report(self, server_guid: str = None) -> str | list:
        """Returns details about the running server. Async version.

        Parameters
        ----------
        server_guid: str
            Identity of the server to report on.

        Returns
        -------
        Response
           A list of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}/omag-servers/{server_guid}/instance/report"

        response = await self._async_make_request("GET", url)

        return response.json().get("element", "No server found")

    def get_server_report(self, server_guid: str = None) -> str | list:
        """Returns details about the running server.

        Parameters
        ----------
        server_guid: str
            Identity of the server to report on.

        Returns
        -------
        Response
           A list of json dict with the platform reports.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_server_report(server_guid))
        return response


if __name__ == "__main__":
    print("Main-Runtime Manager")

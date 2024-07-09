"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This module contains the core OMAG configuration class and its methods. These methods are used
to create and update OMAG server configuration documents. Configuration documents must be subsequently
deployed to take effect.

"""

import json

# import json
from pyegeria._client import Client
from pyegeria._globals import enable_ssl_check
from pyegeria._validators import (
    validate_name,
    validate_guid,
    validate_url
)


class CoreServerConfig(Client):
    """
    CoreServerConfig is a class that extends the Client class. It provides methods to configure and interact with access
    services in the OMAG server.

    Attributes:

        server_name: str
            The name of the OMAG server to configure.
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
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = enable_ssl_check,
    ):
        self.admin_command_root: str
        Client.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.admin_command_root = (
                self.platform_url
                + "/open-metadata/admin-services/users/"
                + user_id
        )

    #
    #       Configure Access Services
    #
    def get_stored_configuration(self, server_name: str = None) -> dict:
        """ Retrieves all the configuration documents for a server
        Parameters
        ----------
            self :
                the implicit instance of the class
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
        Returns
        -------
        dict
            The stored configurations for the given server as a JSON dict.

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        If a server name doesn't currently exist, the method will return a starter configuration body with some of the
        key elements filled in that can serve as a starter for a valid server configuration using the fine-grained
        methods in the full OMAG Server Configuration API.

        More details on the OMAG Server Configuration at: https://egeria-project.org/guides/admin/servers/
        """

        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/configuration"
        response = self.make_request("GET", url)
        return response.json().get("omagserverConfig", "No configuration found")

    def is_server_configured(self, server_name: str = None) -> bool:
        """ Check if the server has a stored configuration

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, it uses the default server_name from the instance.

        Returns
        -------
        bool
            Returns True if the server has a stored configuration, False otherwise.
        """
        if server_name is None:
            server_name = self.server_name

        response = self.get_stored_configuration(server_name=server_name)

        if 'auditTrail' in response:
            return True
        else:
            return False

    def get_configured_access_services(self, server_name: str = None) -> list | str:
        """ Return the list of access services that are configured for this server.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to get the configured access services for.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        list | str
            A JSON list of configured access services for the specified server. If either no services or the server
            isn't found, then an explanatory string is returned.

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

        url = f"{self.admin_command_root}/servers/{server_name}/access-services"
        response = self.make_request("GET", url)
        return response.json().get("services", "No access services found")

    def configure_all_access_services(self, server_name: str = None) -> None:
        """ Enable all access services that are registered with this server platform.
            The access services will send notifications if it is part of its implementation.
        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/access-services"
        self.make_request("POST", url)

    def configure_all_access_services_no_topics(self, server_name: str = None) -> None:
        """ Configure all access services for the specified server with no cohort/Event Bus.
        Parameters
        ----------
        server_name : str, optional
            The name of the server to configure.
            If not provided, the server name associated with the instance is used.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/access-services/no-topics"
        self.make_request("POST", url)

    def clear_all_access_services(self, server_name: str = None) -> None:
        """ Disable the access services. This removes all configuration for the access services and disables the
            enterprise repository services.
        Parameters
        ----------
        server_name : str, optional
            The name of the server to clear all access services for.
            If not provided, the server name associated with the instance is used.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/access-services"
        self.make_request("DELETE", url)

    def get_access_service_config(self, access_service_name: str, server_name: str = None) -> dict:
        """ Retrieve the config for an access service.

        Parameters
        ----------
        access_service_name : str
            The name of the access service.

        server_name : str, optional
            The name of the server to get the configured access services for.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        dict
            The access service configuration as a JSON dictionary.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
       """
        if server_name is None:
            server_name = self.server_name
        validate_name(access_service_name)

        url = f"{self.admin_command_root}/servers/{server_name}/access-services/{access_service_name}"
        response = self.make_request("GET", url)
        return response.json().get("config", "Access service not found")

    def configure_access_service(self, access_service_name: str, access_service_options: dict = None,
                                 server_name: str = None) -> None:
        """ Enable a single access service. This access service will send notifications if it is part
            of its implementation.

        Parameters
        ----------
        access_service_name : str
            The name of the access service to be configured.

        access_service_options : dict, optional
            Optional configuration for the access service. For, instance, this can be used to
            set the zones that an access service has access to.

        server_name : str, optional
            The name of the server to configure access services for.
            If not provided, the server name associated with the instance is used.
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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.

        Notes
        -----
        This method configures the given access service for the specified server. If the server name is not provided,
        the default server name will be used.
        """
        if server_name is None:
            server_name = self.server_name
        validate_name(access_service_name)
        url = f"{self.admin_command_root}/servers/{server_name}/access-services/{access_service_name}"
        self.make_request("POST", url, access_service_options)

    def configure_access_service_no_topics(self, access_service_name: str, access_service_options: dict = None,
                                           server_name: str = None) -> None:
        """ Enable a single access service. Notifications, if supported, are disabled.

        Parameters
        ----------
        access_service_name : str
            The name of the access service to be configured.

        access_service_options : dict, optional
            Optional configuration for the access service. For, instance, this can be used to
            set the zones that an access service has access to.

        server_name : str, optional
            The name of the server to configure access services for.
            If not provided, the server name associated with the instance is used.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.

        Notes
        -----
        This method configures the given access service for the specified server. If the server name is not provided,
        the default server name will be used. Notifications, if supported, are disabled.
        """
        if server_name is None:
            server_name = self.server_name
        validate_name(access_service_name)

        url = f"{self.admin_command_root}/servers/{server_name}/access-services/{access_service_name}/no-topics"
        self.make_request("POST", url, access_service_options)

    def clear_access_service(self, access_service_name: str, server_name: str = None) -> None:
        """ Remove the config for an access service.

        Parameters
        ----------
        access_service_name : str
            The name of the access service to be cleared.

        server_name : str, optional
            The name of the server where the access service is located. If not provided, the server name from the class
            instance will be used.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        if server_name is None:
            server_name = self.server_name
        validate_name(access_service_name)

        url = f"{self.admin_command_root}/servers/{server_name}/access-services/{access_service_name}"
        self.make_request("DELETE", url)

    def get_access_services_configuration(self, server_name: str = None) -> list:
        """ Return the detailed configuration for the access services in this server.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to retrieve access service configurations from.
            If not provided, the server name from the class instance will be used.

        Returns
        -------
        list
            The access services configuration for the specified server, returned as a JSON list.

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/access-services/configuration"
        response = self.make_request("GET", url)

        return response.json().get("services", "No access services configured")

    #
    #       Configure Event Bus
    #
    def get_event_bus(self, server_name: str = None) -> dict:
        """ Returns the event bus configuration for the specified server

        Parameters
        ----------
        server_name: str, optional
            The name of the server to retrieve the event bus configuration from. If not provided, the default
            server name specified in the class instance will be used.

        Returns
        -------
            The event bus configuration as a JSON dictionary

        Raises
        ------
        InvalidParameterException
            If the response status code is not 200 and the related HTTP code is also not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/event-bus"

        response = self.make_request("GET", url)
        return response.json().get("config", "No event bus configured")

    def set_event_bus(self, event_bus_config: dict, server_name: str = None) -> None:
        """ Sets the event bus configuration for the server.

        Parameters
        ----------

        event_bus_config : dict
            A JSON dictionary containing the Event Bus configuration

        server_name : str, optional
            The name of the server to retrieve the event bus configuration from. If not provided, the default server
            name specified in the class instance will be used.

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

        Description
        -----------
        Set up the default event bus for embedding in event-driven connector.
        The resulting connector will be used for example, in the OMRS Topic Connector for each cohort,
        the in and out topics for each Access Service and possibly the local repository's event mapper.
        When the event bus is configured, it is used only on future configuration.
        It does not affect existing configuration.

        """

        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/event-bus"
        self.make_request("POST", url, event_bus_config)

    def clear_event_bus(self, server_name: str = None) -> None:
        """ Delete the event bus configuration for the given server.

        Parameters
        ----------

        server_name : str, optional
            The name of the server to retrieve the event bus configuration from. If not provided, the default server
            name specified in the class instance will be used.

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

        Description
        -----------
        Delete the current configuration for the event bus. This does not impact that existing configuration for the
        server, only future configuration requests.
        """

        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/event-bus"
        self.make_request("DELETE", url)

    #
    #       Configure Audit Logs
    #
    def get_audit_log_destinations(self, server_name: str = None) -> dict:
        """ Get the destinations for a servers audit log

         Parameters
         ----------
         server_name : str, optional
         The name of the server to retrieve the audit configuration for. If no value is provided will pull
         the default from the class definition.

         Returns
         -------
         Returns json string containing the audit log destinations configuration.

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

        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations"
        response = self.make_request("GET", url)
        return response.json().get("connections", "No audit log destinations configured")

    def clear_audit_log_destinations(self, server_name: str = None) -> None:
        """ Clears the audit log destination configuration for the specified server

        Parameters
        ----------
        server_name : str
            Name of the server to clear audit log destination

        Returns
        -------

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
            Raised when configuration parameters passed on earlier calls turn out to be
            invalid or make the new call invalid.

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations"
        self.make_request("DELETE", url)

    def clear_a_log_destination(self, dest_name: str, server_name: str = None) -> None:
        """  Clears audit log destinations for a server

        Parameters
        ----------

        dest_name : str
            Qualified name of the log destination to clear.
        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

        Raises
        ------

        InvalidParameterException:
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(dest_name)
        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/connection/{dest_name}"
        self.make_request("DELETE", url)

    def add_console_log_destinations(self, severities: [str], server_name: str = None) -> None:
        """ Adds a console log destination to a server

        Parameters
        ----------
        severities : [str]
            List of severities to send to this log destination.
        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

        Raises
        ------

        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
            Raised when configuration parameters passed on earlier calls turn out to be
            invalid or make the new call invalid.

        """
        if server_name is None:
            server_name = self.server_name
        if severities is None:
            severities = []
        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/console"
        self.make_request("POST", url, severities)

    def add_default_log_destinations(self, server_name: str = None) -> None:
        """ Adds the default log destination to a server

        Parameters
        ----------

        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

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
        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/default"
        self.make_request("POST", url)

    def add_event_topic_log_destinations(self, topic_name: str, severities: [str], server_name: str = None) -> None:
        """ Adds an event topic log destination to a server

        Parameters
        ----------

        topic_name : str
            Name of the event topic to send audit logs to.
        severities : [str], optional
            List of severities to send to the Topic

        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

        Raises
        ------

        InvalidParameterException:
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException:
            Raised when configuration parameters passed on earlier calls turn out to be
            invalid or make the new call invalid.

        """
        if server_name is None:
            server_name = self.server_name

        validate_name(topic_name)

        if severities is None:
            severities = []

        url = (f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/event-topic?topicName="
               f"{topic_name}")
        self.make_request("POST", url, severities)

    def add_file_log_destinations(self, directory_name: str, severities=None,
                                  server_name: str = None) -> None:
        """ Adds a file log destination to a server. Each message is a separate file in the directory
            indicated by the directory name.

        Parameters
        ----------
        directory_name : str
            Path to the audit files.
        severities : [str], optional
            List of severities to send to this destination.
        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

        Raises
        ------

        InvalidParameterException:
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException:
            Raised when configuration parameters passed on earlier calls turn out to be
            invalid or make the new call invalid.

        """
        if severities is None:
            severities = ["Error", "Exception"]
        if server_name is None:
            server_name = self.server_name

        validate_name(directory_name)

        if severities is None:
            severities = []
        url = (f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/files?directoryName="
               f"{directory_name}")
        self.make_request("POST", url, severities)

    def add_slf4j_log_destination(self, severities: [str] = None, server_name: str = None) -> None:
        """ Adds an SLF4J log destination to a server

        Parameters
        ----------
        severities: str
            List of severities to send to the destination.
        server_name : str
            Name of the server to update.

        Returns
        -------
        Void

        Raises
        ------

        InvalidParameterException:
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name
        if severities is None:
            severities = []
        url = f"{self.admin_command_root}/servers/{server_name}/audit-log-destinations/slf4j"
        self.make_request("POST", url, severities)

    #
    #   Basic Repository Configuration
    #
    def set_no_repository_mode(self, server_name: str = None) -> None:
        """ Disable the local repository for this server

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the method uses the value stored in `self.server_name`.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository"
        self.make_request("DELETE", url)

    def get_local_repository_config(self, server_name: str = None) -> dict:
        """ Retrieve the local repository configuration as a JSON dictionary

        Parameters
        ----------
        server_name : str, optional
            The name of the server for which to retrieve the local repository configuration. If not specified,
            the default server name will be used.

        Returns
        -------
        dict
            The local repository configuration for the specified server as a JSON dictionary.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = self.admin_command_root + "/servers/" + server_name + "/local-repository/configuration"
        response = self.make_request("GET", url)

        # return response.json().get("config")

        return response.json().get("config", "No configuration found")

    def clear_local_repository_config(self, server_name: str = None) -> None:
        """ Clear the configuration of the local repository

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not specified, the default server name will be used.

        Returns
        -------
        None
            This method does not return anything.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = self.admin_command_root + "/servers/" + server_name + "/local-repository/configuration"
        self.make_request("DELETE", url)

    def set_local_metadata_collection_id(self, metadata_collection_id: str, server_name: str = None) -> None:
        """ set the metadata collection id of the local repository

        Parameters
        ----------
        metadata_collection_id : str
            The unique identifier of the metadata collection to set.
        server_name : str, optional
            The name of the server. If not provided, defaults to the server name associated with the instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        validate_guid(metadata_collection_id)

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/metadata-collection-id"
        self.make_request("POST", url, metadata_collection_id)

    def get_local_metadata_collection_id(self, server_name: str = None) -> str:
        """ get the local metadata collection id
        Parameters
        ----------
                server_name : str, optional
            The name of the server. If not provided, defaults to the server name associated with the instance.

        Returns
        -------
        Metadata collection id

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The server repository must have already been activated.
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/metadata-collection-id"
        response = self.make_request("GET", url, )
        return response.json().get('guid', "No ID found")

    def get_local_metadata_collection_name(self, server_name: str = None) -> str:
        """ get the local metadata collection name
        Parameters
        ----------
                server_name : str, optional
            The name of the server. If not provided, defaults to the server name associated with the instance.

        Returns
        -------
        Metadata collection id

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The server repository must have already been activated.
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/metadata-collection-name"
        response = self.make_request("GET", url, )
        return response.json().get("resultString", "No name found")

    def set_local_metadata_collection_name(self, metadata_collection_name: str, server_name: str = None) -> None:
        """ Set local metadata collection name

        Parameters
        ----------
        metadata_collection_name : str
            The name of the metadata collection to be set.

        server_name : str, optional
            The name of the server where the metadata collection should be set.
            If not provided, the server name defaults to the instance's server name.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(metadata_collection_name)

        url = (f"{self.admin_command_root}/servers/{server_name}/local-repository/"
               f"metadata-collection-name/{metadata_collection_name}")
        self.make_request("POST", url)

    def set_in_mem_local_repository(self, server_name: str = None) -> None:
        """  Sets the local repository to use the native in-memory repository

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the method uses the default server name from the object.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/in-memory-repository"
        self.make_request("POST", url)

    def set_graph_local_repository(self, server_name: str = None) -> None:
        """ Sets the local repository to use JanusGraph file based repository

        Parameters
        ----------
        server_name : str, optional
            The name of the server to set as the graph local repository.
            If not provided, the current server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/local-graph-repository"
        self.make_request("POST", url)

    def set_read_only_local_repository(self, server_name: str = None) -> None:
        """ Sets the local repository to be read-only

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the default server name of the instance will be used.

        Returns
        -------
        None
            This method does not return anything.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/read-only-repository"
        self.make_request("POST", url)

    def set_repository_proxy_details(self, connector_provider: str, server_name: str = None) -> None:
        """ Sets the local repository to use the proxy repository specified by the connection.

        Parameters
        ----------
        connector_provider: str
            Specifies the class of the proxy connector provider.
        server_name : str, optional
            The name of the server. If not provided, the default server name of the instance will be used.

        Returns
        -------
        None
            This method does not return anything.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        validate_name(connector_provider)

        url = (f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/repository-proxy/"
               f"details?connectorProvider={connector_provider}")
        self.make_request("POST", url)

    def set_plug_in_repository(self, config_body: dict, server_name: str = None) -> None:
        """ Configure the metadata repository using a full repository connection body.

        Parameters
        ----------
        config_body : dict
            The configuration body for the plug-in repository. This should contain the necessary parameters for
            connecting to the repository.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        None
            This method does not return anything.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/plugin-repository/connection"
        self.make_request("POST", url, config_body)

    def set_xtdb_in_mem_repository(self, server_name: str = None) -> None:
        """ Set xtdb local repository connection to be XTDB with an in memory repository

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the method will use the default server name.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/xtdb-in-memory-repository"
        self.make_request("POST", url)

    def set_xtdb_local_kv_repository(self, server_name: str = None) -> None:
        """ Set xtdb local repository connection to be XTDB with a local file based key-value store

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the method will use the default server name.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action


        Description
        -----------
        This method is used to set the local key-value repository mode to XTDB local KV repository for a given server.
         The server name can be optionally specified, otherwise, the default server

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/xtdb-local-kv-repository"
        self.make_request("POST", url)

    def set_xtdb_local_repository(self, xtdb_config_body: dict, server_name: str = None) -> None:
        """ Set the local repository connection to be XTDB with a potentially complex XTDB configuration

        Parameters
        ----------
        xtdb_config_body : dict
            The XTDB configuration body as a json dict.

        server_name : str, optional
            The name of the server. If not provided, it uses the default server name specified in the instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        See https://egeria-project.org/connectors/repository/xtdb for more information

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/xtdb-local-repository"
        self.make_request("POST", url, xtdb_config_body)

    def set_xtdb_pg_repository(self, host: str, pg_user: str, pg_pwd: str, server_name: str = None) -> None:
        """ Set the local repository connection to be XTDB using PostgresSQL Server, passing in basic parameters

        Parameters
        ----------
        host : str
            the full hostname and port of the postgres server

        pg_user : str
            postgresql user name

        pg_pwd : str
            postgresql user password

        server_name : str, optional
            The name of the server. If not provided, it uses the default server name specified in the instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        Current convention is to use the server name as the database name. Currently, the database is assumed
        to already exist at the specified server.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(pg_pwd)
        validate_name(pg_user)
        validate_name(host)
        pg_db = server_name.lower()

        jdbc_url = f'"jdbc:postgresql://{host}/{pg_db}?user={pg_user}&password={pg_pwd}"'
        index_dir = f'"data/servers/{server_name}/repository/xtdb/rdb-index"'
        lucene_dir = f'"data/servers/{server_name}/repository/xtdb/lucene"'

        index_str = '{:xtdb/index-store {:kv-store {:xtdb/module xtdb.rocksdb/->kv-store :db-dir '
        index_str2 = index_str + index_dir + '}}'

        lucene_str = ':xtdb.lucene/lucene-store {:db-dir ' + lucene_dir
        lucene_str2 = lucene_str + ' :indexer {:xtdb/module xtdb.lucene.egeria/->egeria-indexer} '
        lucene_str3 = lucene_str2 + ':analyzer {:xtdb/module xtdb.lucene.egeria/->ci-analyzer}} '

        conn_pool_str = ':xtdb.jdbc/connection-pool {:dialect {:xtdb/module xtdb.jdbc.psql/->dialect} '
        conn_pool_str2 = f'{conn_pool_str} :db-spec {{:jdbcUrl {jdbc_url} }} }}'

        tx_str = ':xtdb/tx-log {:xtdb/module xtdb.jdbc/->tx-log :connection-pool '
        tx_str2 = tx_str + ':xtdb.jdbc/connection-pool :poll-sleep-duration "PT1S"}'

        doc_str = ':xtdb/document-store {:xtdb/module xtdb.jdbc/->document-store :connection-pool'
        doc_str2 = doc_str + ' :xtdb.jdbc/connection-pool}}'

        edn = f"{index_str2} {lucene_str3} {conn_pool_str2} {tx_str2} {doc_str2}"
        body = {
            "xtdbConfigEDN": edn,
        }

        print(json.dumps(body, indent=4))
        url = f'{self.admin_command_root}/servers/{server_name}/local-repository/mode/xtdb-local-repository'
        self.make_request("POST", url, body)

    def get_open_metadata_archives(self, server_name: str = None) -> dict:
        """ Return the list of open metadata archives configured to load on startup.

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        dict
            A JSON dictionary of the open metadata archives configured to load on startup.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/open-metadata-archives"
        response = self.make_request("GET", url)

        return response.json().get("connections", "No archives found")

    def clear_open_metadata_archives(self, server_name: str = None) -> None:
        """ Clear open metadata archives from being loaded at startup

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, uses the default server name assigned to the instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/open-metadata-archives"
        self.make_request("DELETE", url)

    def add_startup_open_metadata_archive_file(self, archive_file: str, server_name: str = None) -> None:
        """ Add a metadata archive file to be loaded on startup
        Parameters
        ----------

        archive_file : str
            The file path of the metadata archive file.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(archive_file)

        url = f"{self.admin_command_root}/servers/{server_name}/open-metadata-archives/file"
        self.make_request("POST", url, archive_file)

    #
    #   Basic settings and security
    #
    def set_basic_server_properties(self, local_server_description: str, organization_name: str,
                                    local_server_url: str, local_server_user_id: str, local_server_password: str,
                                    max_page_size: int = 0, server_name: str = None):
        """ Sets the basic server properties.
        Parameters
        ----------
        local_server_description : str
            Description of the defined server.
        organization_name : str
            Name of the organization.
        local_server_url : str
            URL of the defined server.
        local_server_user_id : str
            User ID of the defined server.
        local_server_password : str
            Password of the defined server.
        max_page_size : int, optional
            Maximum page size for server response (default is 0).
        server_name : str, optional
            Name of the server being defined (default is None).

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        validate_name(local_server_user_id)
        validate_url(local_server_url)
        validate_name(local_server_password)

        basic_props = {
            "localServerDescription": local_server_description,
            "organizationName": organization_name,
            "localServerURL": local_server_url,
            "localServerUserId": local_server_user_id,
            "localServerPassword": local_server_password,
            "maxPageSize": max_page_size
        }
        url = self.admin_command_root + "/servers/" + server_name + "/server-properties"

        self.make_request("POST", url, basic_props)

    def get_basic_server_properties(self, server_name: str = None) -> dict | str:
        """ Retrieve the basic properties associated with this server

        Parameters
        ----------
        server_name : str, optional
            The name of the server to retrieve the local metadata collection ID from. If not provided, the current
            server name associated with the instance of the class will be used.

        Returns
        -------
        dict
            A JSON structure of the basic server properties.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = self.admin_command_root + "/servers/" + server_name + "/server-properties"
        response = self.make_request("GET", url)

        return response.json().get("basicServerProperties", "No server properties found")

    def get_server_type_classification(self, server_name: str = None) -> dict | str:
        """ Clears the server type for the given server

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If None, the default server name will be used.

        Returns
        -------
        str:
            The server type for the given server.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-type-classification"
        response = self.make_request("GET", url)

        return response.json().get("serverTypeClassification", "No server type found")

    def get_server_security_connection(self, server_name: str = None) -> dict | str:
        """ Retrieve the security connection configuration for a server.

        Parameters
        ----------
        server_name : str, optional
            The name of the server for which the security connection information is requested.
            If not provided, the method will use the default server name.

        Returns
        -------
        dict
            A dictionary with the connection information for the server's security.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/security/connection"
        response = self.make_request("GET", url)
        return response.json()

    def set_server_security_connection(self, security_connection_body: dict, server_name: str = None) -> None:
        """ Set the server security configuration

        Parameters
        ----------
        security_connection_body : str
            The JSON body containing the configuration details for setting up the server security connection.

        server_name : str (optional)
            The name of the server for which the security connection should be set.
            If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/security/connection"
        self.make_request("POST", url, security_connection_body)

    def clear_server_security_connection(self, server_name: str = None) -> None:
        """ Clears the server security configuration

                Parameters
                ----------

                server_name : str (optional)
                    The name of the server for which the security connection should be set.
                    If not provided, the default server name will be used.

                Returns
                -------
                None

                Raises
                ------
                InvalidParameterException
                    If the response code is not 200.
                PropertyServerException:
                    Raised by the server when an issue arises in processing a valid request
                NotAuthorizedException:
                    The principle specified by the user_id does not have authorization for the requested action

                """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/security/connection"
        self.make_request("DELETE", url)

    def get_server_classification(self, server_name: str = None) -> dict:
        """ Get server classification

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the value from `self.server_name` will be used.

        Returns
        -------
        str
            The server type classification.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-type-classification"
        response = self.make_request("GET", url)

        return response.json().get("serverTypeClassification")

    #
    # View Services
    #

    def get_configured_view_svcs(self, server_name: str = None) -> dict:
        """ Get the list of view services configured for the specified server

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        dict
            A JSON list containing the configured view services for the specified server.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/view-services"
        response = self.make_request("GET", url)

        return response.json().get("services", "No view services found")

    def config_all_view_services(self, mdr_server_name: str,
                                   mdr_server_platform_root_url: str, server_name: str = None) -> None:
        """ Enable all view services that are registered with this OMAG server platform.

        Parameters
        ----------

        mdr_server_name : str
            the name of the paired OMAG server.

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        mdr_server_platform_root_url : str
            The platform URL root where the metadata access server is running.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        To configure a view service specifying the complete configuration body you can use the
        full_omag_config module.
        """

        if server_name is None:
            server_name = self.server_name

        validate_name(mdr_server_name)
        validate_name(mdr_server_platform_root_url)

        view_service_body = {
            "class": "ViewServiceRequestBody",
            "omagserverName": mdr_server_name,
            "omagserverPlatformRootURL": mdr_server_platform_root_url
        }

        url = f"{self.admin_command_root}/servers/{server_name}/view-services"
        self.make_request("POST", url, view_service_body)

    def config_all_view_services_w_body(self, view_services_request_body, server_name: str = None) -> None:
        """ Configure all view services for the specified view server with a simple configuration.

        Parameters
        ----------
        view_services_request_body: dict
            a valid JSON viewServicesRequestBody object

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----


        """

        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/view-services"
        self.make_request("POST", url, view_services_request_body)

    def clear_all_view_services(self, server_name: str = None) -> None:
        """ Clears all the view services for the given server

        Parameters
        ----------
        server_name : str, optional
            The name of the server. If None, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/view-services"
        self.make_request("DELETE", url)

    def get_view_svc_config(self, service_url_marker: str, server_name: str = None) -> dict | str:
        """ Retrieves the view service configuration for the given view server.
        Parameters
        ----------
        service_url_marker : str
            The service URL marker. A list can be retrieved through the `list_registered_view_svcs` of the
            `registered_info` module.

        server_name : str, optional
            The server name. If not provided, the default server name will be used.

        Returns
        -------
        dict | str
            The configuration of the view service if found, or the message "No view services found" if not found.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        Details on view services configuration can be found at:
         https://egeria-project.org/guides/admin/servers/configuring-the-view-services/?h=view#integration-view-services

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(service_url_marker)

        url = f"{self.admin_command_root}/servers/{server_name}/view-services/{service_url_marker}"
        response = self.make_request("GET", url)
        return response.json().get("config", "No view services found")

    def config_view_service(self, service_url_marker: str, mdr_server_name: str,
                            mdr_server_platform_root_url: str, server_name: str = None) -> None:
        """ Configure a view service specified by the service_url_marker with basic properties.

        Parameters
        ----------
        service_url_marker : str
            The service URL marker. A list can be retrieved through the `list_registered_view_svcs` of the
            `registered_info` module.

        mdr_server_name : str
            the name of the paired OMAG server.

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        mdr_server_platform_root_url : str
            The platform URL root where the metadata access server is running.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        To configure a view service specifying the complete configuration body you can use the
        extended_omag_config module.
        """

        if server_name is None:
            server_name = self.server_name
        validate_name(service_url_marker)
        validate_name(mdr_server_name)
        validate_name(mdr_server_platform_root_url)

        view_service_body = {
            "class": "ViewServiceRequestBody",
            "omagserverName": mdr_server_name,
            "omagserverPlatformRootURL": mdr_server_platform_root_url
        }

        url = f"{self.admin_command_root}/servers/{server_name}/view-services/{service_url_marker}"
        self.make_request("POST", url, view_service_body)

    def clear_view_service(self, service_url_marker: str, server_name: str = None) -> None:
        """ Remove the view service specified by the service_url_marker.

        Parameters
        ----------
        service_url_marker : str
            The service URL marker. A list can be retrieved through the `list_registered_view_svcs` of the
            `registered_info` module.

        server_name : str, optional
            The name of the server where the service resides. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        Details on view services configuration can be found at:
         https://egeria-project.org/guides/admin/servers/configuring-the-view-services/?h=view#integration-view-services

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(service_url_marker)

        url = f"{self.admin_command_root}/servers/{server_name}/view-services/{service_url_marker}"
        self.make_request("DELETE", url)

    def get_view_svcs_config(self, server_name: str = None) -> str | list:
        """ Retrieves the view services configuration for the specified view server.
        Parameters
        ----------
        server_name : str, optional
            The name of the server for which the view services configuration is retrieved.
            If not provided, the default server name will be used.

        Returns
        -------
        str
            The JSON representation of the view services configuration.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        Details on view services configuration can be found at:
         https://egeria-project.org/guides/admin/servers/configuring-the-view-services/?h=view#integration-view-services

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/view-services/configuration"
        response = self.make_request("GET", url)

        return response.json().get("services", "No services found")

    #
    #   Cohort Configuration, etc.
    #
    def add_cohort_registration(self, cohort_name: str, server_name: str = None) -> None:
        """ Enable registration of server to an open metadata repository cohort using the default topic structure
            (DEDICATED_TOPICS). A cohort is a group of open metadata repositories that are sharing metadata.
            An OMAG server can connect to zero, one or more cohorts. Each cohort needs a unique name.
            The members of the cohort use a shared topic to exchange registration information and events
            related to the changes in their supported metadata types and instances. They are also able to query
            each other's metadata directly through REST calls.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to be registered.

        server_name : str, optional
            Name of the server to which the cohort should be added. Defaults to None.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200 after making the POST request.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)

        url = f"{self.admin_command_root}/servers/{server_name}/cohorts/{cohort_name}"
        self.make_request("POST", url)

    def get_cohort_config(self, cohort_name: str, server_name: str = None) -> dict:
        """ Get the cohort configuration for the given cohort.

        Parameters
        ----------
        cohort_name : str
            Name of the cohort to get the configuration for.
        server_name : str, optional
            The name of the server. If None, the default server name will be used.

        Returns
        -------
        Dictionary containing the JSON structure of the cohort configuration.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        validate_name(cohort_name)

        url = self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name
        response = self.make_request("GET", url)

        return response.json().get("config", "No cohort configuration found")

    def deploy_server_config(self, target_platform_body: dict, server_name: str = None) -> None:
        """ Add a metadata archive file to be loaded on startup
        Parameters
        ----------

        target_platform_body : dict
            The target platform URL in a JSON dict defining where to deploy the configuration to.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/configuration/deploy"
        self.make_request("POST", url, target_platform_body)

    #
    #   Integration Groups
    #
    def clear_all_integration_groups(self, server_name: str = None) -> None:
        """ Remove all the integration groups associated with the server.

        Parameters
        ----------

        server_name : str, optional
            The name of the server where the service resides. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----


        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/integration-groups"
        self.make_request("DELETE", url)

    def clear_an_integration_group(self, group_qualified_name: str, server_name: str = None) -> None:
        """ Remove the integration group specified by the group_qualified_name parameter.

        Parameters
        ----------
        group_qualified_name : str
            The name of the integration group to remove.

        server_name : str, optional
            The name of the server where the service resides. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(group_qualified_name)

        url = f"{self.admin_command_root}/servers/{server_name}/view-services/{group_qualified_name}"
        self.make_request("DELETE", url)

    def get_integration_groups_config(self, server_name: str = None) -> list | str:
        """ Get the Integration Groups configuration server specified by the server_name parameter.

        Parameters
        ----------

        server_name : str, optional
            The name of the server. If None, the default server name will be used.

        Returns
        -------
        Dictionary containing the JSON structure of the Integration Groups configuration.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        url = self.admin_command_root + "/servers/" + server_name + "/integration-groups/configuration"
        response = self.make_request("GET", url)

        return response.json().get("groups", "No Integration Group configuration found")

    def config_integration_group(self, omag_server_name: str, omag_server_platform_root_url: str,
                                 qualified_name: str, server_name: str = None) -> None:
        """ Add configuration for a single integration group to the server's config document.

        Parameters
        ----------

        omag_server_name : str
            the name of the paired OMAG server.

        qualified_name : str
            The unique name of teh integration group.

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        omag_server_platform_root_url : str
            The platform URL root where the metadata access server is running.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        See https://egeria-project.org/concepts/integration-group/ for more information.

        """

        if server_name is None:
            server_name = self.server_name
        validate_name(omag_server_name)
        validate_url(omag_server_platform_root_url)
        validate_name(qualified_name)

        integration_group_service_body = {
            "class": "IntegrationGroupConfig",
            "omagserverName": omag_server_name,
            "omagserverPlatformRootURL": omag_server_platform_root_url,
            "integrationGroupQualifiedName": qualified_name
        }

        url = f"{self.admin_command_root}/servers/{server_name}/integration-groups/configuration"
        self.make_request("POST", url, integration_group_service_body)

    #
    #   Engine Host Config
    #

    def clear_engine_definitions_client_config(self, server_name: str = None) -> None:
        """ Remove the configuration for the Governance Engine OMAS Engine client configuration in a single call.
        This overrides the current values.

        Parameters
        ----------

        server_name : str, optional
            The name of the server where the service resides. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        see also https://egeria-project.org/services/omes/
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/engine-definitions/client-config"
        self.make_request("DELETE", url)

    def set_engine_definitions_client_config(self, mdr_server_name: str, mdr_server_platform_root_url: str,
                                             server_name: str = None) -> None:
        """ Set up the name and platform URL root for the metadata server running the Governance Engine OMAS that
         provides the governance engine definitions used by the engine services.

        Parameters
        ----------

        mdr_server_name : str
            the name of the paired OMAG server.

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        mdr_server_platform_root_url : str
            The platform URL root where the metadata access server is running.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        See https://egeria-project.org/services/omes/ for more information.

        """

        if server_name is None:
            server_name = self.server_name
        validate_name(mdr_server_name)
        validate_url(mdr_server_platform_root_url)

        body = {
            "class": "OMAGServerClientConfig",
            "omagserverName": mdr_server_name,
            "omagserverPlatformRootURL": mdr_server_platform_root_url,
        }

        url = f"{self.admin_command_root}/servers/{server_name}/engine-definitions/client-config"
        self.make_request("POST", url, body)

    def clear_engine_list(self, server_name: str = None) -> None:
        """ Remove the configuration for the Governance Engine OMAS Engine client configuration in a single call.
        This overrides the current values.

        Parameters
        ----------

        server_name : str, optional
            The name of the server where the service resides. If not provided, the default server name will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----

        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/engine-list"
        self.make_request("DELETE", url)

    def set_engine_list(self, engine_list: [dict], server_name: str = None) -> None:
        """ Set up the list of governance engine that will use the metadata from the same metadata access server
         as the engine host uses for retrieving the engine configuration.

        Parameters
        ----------

        engine_list: [dict]
            a JSON dict containing a list of tuples for the engine - see below for structure.

        server_name : str, optional
            The name of the metadata access server that is to provide the metadata services to the view service.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        See https://egeria-project.org/concepts/governance-engine/ for more information.

        engine_list structure is:

        [
            {
                "class" : "EngineConfig",
                # engineId is optional - one is automatically created if needed
                "engineId": "string",
                "engineQualifiedName": "string",
                "engineUserId": "string"
            }
        ]

        """

        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/engine-list"
        self.make_request("POST", url, engine_list)

    def get_engine_host_services_config(self, server_name: str = None) -> dict | str:
        """ Return the configuration for the complete engine host services in this server.

        Parameters
        ----------

        server_name : str, optional
            The name of the server. If None, the default server name will be used.

        Returns
        -------
        List containing the JSON structure of the Integration Groups configuration.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if server_name is None:
            server_name = self.server_name

        url = self.admin_command_root + "/servers/" + server_name + "/engine-host-services/configuration"
        response = self.make_request("GET", url)

        # return response.json().get("config", "No engine definitions client configuration found")
        return response.json().get("services", "No engine host services")

    def get_placeholder_variables(self) -> dict:
        """ get placeholder variables

        Get the placeholder variables from the platform.

        Returns:
            dict: A dictionary containing the placeholder variables.

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action



        """
        url = self.admin_command_root + "/stores/placeholder-variables"
        response = self.make_request("GET", url)

        return response.json().get("stringMap")

    def set_placeholder_variables(self, placeholder_variables: dict) -> None:
        """ Set placeholder variables - replaces previous placeholders with the new list

        Parameters
        ----------
        placeholder_variables : dict
            A dictionary containing the placeholder variables.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.admin_command_root}/stores/placeholder-variables"
        self.make_request("POST", url, placeholder_variables)

    def clear_placeholder_variables(self) -> None:
        """
        Clears the placeholder variables for a store.

        Parameters:
        - self: The instance of the class.

        Returns:
        - None

        Raises
        ------
        InvalidParameterException
            If the response code is not 200.
        PropertyServerException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.admin_command_root}/stores/placeholder-variables"
        self.make_request("DELETE", url)

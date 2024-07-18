"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Server configuration functions.  These functions add definitions to an OMAG server's configuration document.
 This class encompasses the full set of configuration methods.
"""

import json

from pyegeria import Client
from pyegeria import (InvalidParameterException)
from pyegeria._globals import enable_ssl_check
from pyegeria._validators import validate_name, validate_url
from .core_omag_server_config import CoreServerConfig


class FullServerConfig(CoreServerConfig):
    """
    This class represents a client for configuring the OMAG Server.

    Parameters
    ----------
    server_name : str
        The name of the server to connect to.
    platform_url : str
        The URL of the platform where the server is running.
    user_id : str
        The user ID for authentication.
    user_pwd : str, optional
        The password for authentication (default: None).
    verify_flag : bool, optional
        Flag to enable/disable SSL certificate verification (default: enable_ssl_check).

    """

    def __init__(self, server_name: str, platform_url: str, user_id: str, user_pwd: str = None,
            verify_flag: bool = enable_ssl_check, ):
        self.admin_command_root: str
        Client.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.admin_command_root = (self.platform_url + "/open-metadata/admin-services/users/" + user_id)

    def get_access_services_topic_names(self, access_service_name: str, server_name: str = None) -> list[str]:
        """ Retrieve the topic names for this access service.
        Parameters
        ----------
        access_service_name : str
            The name of the access service.

        server_name : str, optional
            The name of the server. If not provided, the server name of the instance is used.

        Returns
        -------
        list[str]
            A list of topic names associated with the specified access service.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(access_service_name)
        url = (
                    self.admin_command_root + "/servers/" + server_name + "/access-services/" + access_service_name +
                    "/topic-names")
        response = self.make_request("GET", url)

        return response.json()  # todo fix

    def get_all_access_services_topic_names(self, server_name: str = None) -> list:
        """ Retrieve the topic names for all access services.
        Parameters
        ----------
        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        list
            The JSON response containing the access services topic names.

        """
        if server_name is None:
            server_name = self.server_name

        url = (self.admin_command_root + "/servers/" + server_name + "/access-services/topic-names")
        response = self.make_request("GET", url)

        return response.json()  # todo fix

    def set_access_services_configuration(self, access_services_body: str, server_name: str = None) -> None:
        """ Set up the configuration for selected open metadata access services (OMASs).
        This overrides the current configured values.

        Parameters
        ----------
        access_services_body: str
            The body of the access services configuration. This should be a string representation of the desired
            configuration.

        server_name: str, optional
            The name of the server. If not provided, the default server will be used.

        Returns
        -------
        None

        """
        if server_name is None:
            server_name = self.server_name

        url = self.admin_command_root + "/servers/" + server_name + "/access-services/configuration"
        self.make_request("POST", url, access_services_body)
        return

    def override_access_service_in_topic_name(self, access_service_name: str, new_topic_name: str,
                                              server_name: str = None) -> None:
        """override the in topic for the access service"""
        if server_name is None:
            server_name = self.server_name

        url = (
                    self.admin_command_root + "/servers/" + server_name + "/access-services/" + access_service_name +
                    "/topic-names/in-topic")
        self.make_request("POST", url, new_topic_name)
        return

    def override_access_service_out_topic_name(self, access_service_name: str, new_topic_name: str,
                                               server_name: str = None) -> None:
        """ override the out topic for the access service"""
        if server_name is None:
            server_name = self.server_name

        url = (
                    self.admin_command_root + "/servers/" + server_name + "/access-services/" + access_service_name +
                    "/topic-names/out-topic")
        self.make_request("POST", url, new_topic_name)
        return

    def set_audit_log_destinations(self, audit_dest_body: str, server_name: str = None) -> None:
        """ Sets the audit log destinations for a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations

        Parameters
        ----------
        audit_dest_body : str
            A JSON document describing the audit destinations for this server.

        server_name : str
            Name of the server to update.

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
        if server_name is None:
            server_name = self.server_name

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations"
        self.make_request("POST", url, audit_dest_body)
        return

    def update_audit_log_destination(self, connection_name: str, audit_dest_body: str, server_name: str = None) -> None:
        """ Update an audit log destination that is identified with the supplied destination name
            with the supplied connection object.
        Parameters
        ----------
        connection_name : str
            The name of the connection for the audit log destination.
        audit_dest_body : str
            The body of the audit log destination.
        server_name : str, optional
            The name of the server. If not provided, the server name associated with the instance will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response status code is not 200 and the related HTTP code is not 200.

        """
        if server_name is None:
            server_name = self.server_name

        url = (self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/connection/" +
               connection_name)
        self.make_request("POST", url, audit_dest_body)
        return

    def add_audit_log_destination(self, connection_body: str, server_name: str = None) -> None:
        """ Adds an audit log destination to a server.

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/connection

        Parameters
        ----------
        connection_body : str
            JSON string containing the connection properties for the audit log destination.
        server_name : str
            Name of the server to update.

        Returns
        -------
        None

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

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/connection"
        self.make_request("POST", url, connection_body)
        return

    def set_cohort_config(self, cohort_name: str, cohort_config_body: str, server_name: str = None) -> None:
        """ Set up the configuration properties for a cohort. This may reconfigure an existing cohort or
            create a cohort. Use setCohortMode to delete a cohort.
        Parameters
        ----------
        cohort_name : str
            The name of the cohort for which the configuration is being set.
        cohort_config_body : str
            The body of the cohort configuration.
        server_name : str, optional
            The name of the server. If not provided, the method will use the server name that is already set.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the cohort_config_body is None.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)
        if cohort_config_body is None:
            raise InvalidParameterException(cohort_config_body)

        url = self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name + "/configuration"
        self.make_request("POST", url, cohort_config_body)
        return

    def clear_cohort_configuration(self, cohort_name: str, server_name: str = None) -> None:
        """ Retrieves the stored configurations for a server
        Parameters
        ----------
        cohort_name : str

        server_name : str, optional

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

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/cohorts/{cohort_name}"
        validate_name(cohort_name)

        self.make_request("DELETE", url)

    def get_dedicated_cohort_topic_names(self, cohort_name: str, server_name: str = None) -> list:
        """ Retrieve the current topic name for the cohort. This call can only be made once the cohort is set up with
            add_cohort_registration().

        Parameters
        ----------
        cohort_name : str
            The name of the cohort for which to retrieve the dedicated topic names.

        server_name : str, optional
            The name of the server on which the cohort resides. If not provided, the default server name will be used.

        Returns
        -------
        list
            A list of topic names that are dedicated to the specified cohort.

        """
        if server_name is None:
            server_name = self.server_name

        validate_name(cohort_name)

        url = self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name + "/dedicated-topic-names"
        response = self.make_request("POST", url)
        return response.json().get("topicNames")

    def get_cohort_topic_name(self, cohort_name: str, server_name: str = None) -> str:
        """ Retrieve the current topic name for the cohort. This call can only be made once the
            cohort is set up with add_cohort_registration().
        Parameters
        ----------
        cohort_name : str
            The name of the cohort for which to retrieve the topic name.
        server_name : str, optional
            The name of the server on which the cohort is located. If not provided, the default server name will be used.

        Returns
        -------
        str
            The topic name associated with the specified cohort.

        Raises
        ------
        InvalidParameterException
            If the request to retrieve the topic name fails or returns an invalid parameter code.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)

        url = f"{self.admin_command_root}/servers/{server_name}/cohorts/{cohort_name}/topic-name"
        response = self.make_request("GET", url)
        return response.json().get("topicName")

    def override_cohort_topic_name(self, cohort_name: str, topic_override: str, server_name: str = None) -> None:
        """ Override the current name for the single topic for the cohort. This call can only be made once the
            cohort is set up with add_cohort_registration().
        Parameters
        ----------
        cohort_name : str
            The name of the cohort for which the topic name is to be overridden.

        topic_override : str
            The new topic name to override the original topic name.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)
        validate_name(topic_override)

        url = self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name + "/topic-name-override"
        self.make_request("POST", url, topic_override)
        return

    def override_instances_cohort_topic_name(self, cohort_name: str, topic_override: str,
                                             server_name: str = None) -> None:
        """ Override the current name for the "instances" topic for the cohort. This call can only be made once
            the cohort is set up with add_cohort_registration().
        Parameters
        ----------
        cohort_name : str
            The name of the cohort to override the topic name for.

        topic_override : str
            The new topic name to override for the cohort.

        server_name : str, optional
            The name of the server where the cohort is located. If not specified,
            the default server name will be used.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)
        validate_name(topic_override)

        url = (self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name +
               "/topic-name-override/instances")
        self.make_request("POST", url, topic_override)
        return

    def override_registration_cohort_topic_name(self, cohort_name: str, topic_override: str,
                                                server_name: str = None) -> None:
        """ Override the current name for the registration topic for the cohort. This call can only be made once
            the cohort is set up with add_cohort_registration().
        Parameters
        ----------
        cohort_name : str
            Name of the cohort to override the topic name for.
        topic_override : str
            The overriding topic name for the cohort.
        server_name : str, optional
            Name of the server. If not provided, the default server name will be used.

        Returns
        -------
        None
            This method does not return any value.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)
        validate_name(topic_override)

        url = (self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name +
               "/topic-name-override/registration")
        self.make_request("POST", url, topic_override)
        return

    def override_types_cohort_topic_name(self, cohort_name: str, topic_override: str, server_name: str = None) -> None:
        """ Override the current name for the "types" topic for the cohort. This call can only be made once
            the cohort is set up with add_cohort_registration().
        Parameters
        ----------
        cohort_name : str
            The name of the cohort.
        topic_override : str
            The topic override to be set for the cohort.
        server_name : str, optional
            The name of the server. If not provided, it will use the default server name from the class.

        Raises
        ------
        InvalidParameterException
            If the response from the server has a relatedHTTPCode other than 200.

        """
        if server_name is None:
            server_name = self.server_name
        validate_name(cohort_name)
        validate_name(topic_override)

        url = (self.admin_command_root + "/servers/" + server_name + "/cohorts/" + cohort_name +
               "/topic-name-override/types")
        self.make_request("POST", url, topic_override)
        return

    def add_full_cohort_registration(self, cohort_name: str, topic_structure: str, server_name: str = None) -> None:
        """  add a full cohort registration

            Parameters
            ----------
            cohort_name : str
                Name of the cohort to be registered.
            topic_structure : str
                Topic structure for the cohort. This is a string from an enumerated list.
                'Dedicated Cohort Topics', description='The cohort members use three topics to exchange information.
                One for registration requests, one for type validation and one for exchange of instances stored by the
                cohort members.
                    This is the preferred and optimal approach
                 'Single Topic', description='All asynchronous communication between cohort members is via a single topic.
                    This is the original design and may still be used when communicating with back level cohort members.
                'Both Single and Dedicated Topics', description='Both the single cohort topic and the dedicated topics are
                    set up and used. This is necessary when the cohort has members with different capabilities.
                     This configuration may cause some events to be processed twice.'
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

        url = f"{self.admin_command_root}/servers/{server_name}/cohorts/{cohort_name}/topic-structure/{topic_structure}"
        self.make_request("POST", url)

    def set_server_configuration(self, config_body: str, server_name: str = None) -> None | str:
        """ Sets the configurations for a server
        Parameters
        ----------

        Returns
        -------
        str
            The stored configurations for the given server.

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
        url = self.admin_command_root + "/servers/" + server_name + "/configuration"
        response = self.make_request("POST", url, config_body)
        if response.status_code != 200:
            return str(response.status_code)  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return
        else:
            raise InvalidParameterException(response.content)

    def clear_stored_configuration(self, server_name: str = None) -> None | str:
        """ Retrieves the stored configurations for a server
        Parameters
        ----------

        Returns
        -------
        str
            The stored configurations for the given server.

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
        url = self.admin_command_root + "/servers/" + server_name + "/configuration"
        response = self.make_request("DELETE", url)
        if response.status_code != 200:
            return str(response.status_code)  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return
        else:
            raise InvalidParameterException(response.content)

    def deploy_stored_configurations(self, target_url_root: str, server_name: str = None) -> None:
        """ Push the configuration for the server to another OMAG Server Platform.
        Parameters
        ----------
        target_url_root : str
            The target URL root where the configurations will be deployed.
        server_name : str, optional
            The name of the server to which the configurations will be deployed.
            If not provided, the default server name will be used.

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

        url = f"{self.admin_command_root}/servers/{server_name}/configuration/deploy"

        self.make_request("POST", url, target_url_root)

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
        return response.json().get("config")

    def set_event_bus_detailed(self, connector_provider: str, topic_url_root: str, server_name: str = None) -> None:
        """
        Parameters
        ----------

        connector_provider : str
            Name of the connector provider

        topic_url_root : str
            URL for the topic

        server_name : str, optional
            The name of the server to retrieve the event bus configuration from. If not provided, the default server
            name specified in the class instance will be used.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
            If the response status code is not 200 and the related HTTP code is also not 200.

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

        url = (f"{self.admin_command_root}/servers/{server_name}/event-bus?connectorProvider="
               f"{connector_provider}&topicURLRoot={topic_url_root}")
        self.make_request("POST", url)

    def delete_event_bus(self, server_name: str = None) -> None:
        """ Delete the event bus configuration for the given server.

        Parameters
        ----------

        server_name : str, optional
            The name of the server to retrieve the event bus configuration from. If not provided, the default server
            name specified in the class instance will be used.

        Returns
        -------

        Raises
        ------
        InvalidParameterException
            If the response status code is not 200 and the related HTTP code is also not 200.

        Description
        -----------
        Delete the current configuration for the event bus. This does not impact that existing configuration for the
        server, only future configuration requests.
        """

        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/event-bus"
        self.make_request("DELETE", url)

    def set_server_url_root(self, url_root: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-url-root-for-caller"
        body = {"urlRoot": url_root}
        response = self.make_request("POST", url, payload=body)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_max_page_size(self, max_page_size: int, server_name: str = None) -> None:
        """
            Set the maximum page size for a server.

        Parameters
        ----------
        max_page_size : int
            The maximum page size to set.
        server_name : str, optional
            The name of the server for which to set the maximum page size. If not specified, the default server name
            will be used.

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
        url = f"{self.admin_command_root}/servers/{server_name}/max-page-size?limit={max_page_size}"
        self.make_request("POST", url)

    def set_server_user_id(self, server_user_id: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-user-id?id={server_user_id}"
        response = self.make_request("POST", url)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_server_user_password(self, server_user_pwd: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-user-password?password={server_user_pwd}"
        response = self.make_request("POST", url)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_organization_name(self, org_name: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/organization-name?name={org_name}"
        response = self.make_request("POST", url)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_local_repository_config(self, repository_body: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = self.admin_command_root + "/servers/" + server_name + "/local-repository/configuration"
        response = self.make_request("POST", url, payload=repository_body)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_plug_in_repository_connection(self, repository_connection_body: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/plugin-repository/connection"
        self.make_request("POST", url, payload=repository_connection_body)

    def set_plug_in_repository_connection_provider(self, repository_connection_provider: str,
                                                   server_name: str = None) -> None:
        """ Set the local repository connection with a user specified connection provider

        Parameters
        ----------
        repository_connection_provider : str
            The name of the connection provider for the plugin repository.

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
        url = (f"{self.admin_command_root}/servers/{server_name}/local-repository/mode/plugin-repository/"
               f"details?connectionProvider={repository_connection_provider}")
        self.make_request("POST", url)

    def set_open_metadata_archives(self, archives_list_body: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/open-metadata-archives"
        response = self.make_request("POST", url, payload=archives_list_body)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_descriptive_server_type(self, type_name: str, server_name: str = None) -> None:
        """ Set descriptiveServerType for this OMAG server

            Parameters
            ----------
            type_name : str
                The name of the descriptive server type to set.

            server_name : str, optional
                The name of the server for which the descriptive server type is being set. If not provided, the
                default server name associated with the object is used.

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
        url = f"{self.admin_command_root}/servers/{server_name}/server-type?typeName={type_name}"
        self.make_request("POST", url)

    def set_server_description(self, server_desc: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/server-description"
        response = self.make_request("POST", url, server_desc)
        related_code = response.json().get("relatedHTTPCode")
        if related_code != 200:
            raise InvalidParameterException(response.content)
        else:
            return

    def set_server_type(self, server_type: str, server_name: str = None) -> None:
        """ Sets the server type for the given server

        Parameters
        ----------
        server_type : str
            The type of server to set

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

        Notes
        -----

        See https://egeria-project.org/concepts/omag-server/#server-name for details.

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.admin_command_root}/servers/{server_name}/"
               f"server-type?typename={server_type}")
        self.make_request("POST", url)

        def clear_server_type(self, server_name: str = None) -> None:
            """ Clears the server type for the given server

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
            url = f"{self.admin_command_root}/servers/{server_name}/server-type?typeName="
            self.make_request("POST", url)

    def config_view_service(self, service_url_marker: str, view_service_body: dict, server_name: str = None) -> None:
        """ Configure a the view service specified by the service_url_marker using the view_service_body.

        Parameters
        ----------
        service_url_marker : str
            The service URL marker. A list can be retrieved through the `list_registered_view_svcs` of the
            `registered_info` module.

        view_service_body : dict
            The body of the view service request.

        server_name : str, optional
            The name of the server. If not provided, the value of `self.server_name` will be used.

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
        self.make_request("POST", url, view_service_body)

    # todo - this may not be used anymore - old
    def set_view_svcs_config(self, view_svcs_config_body: dict, server_name: str = None) -> None:
        """ Set up the configuration for all the open metadata integration groups. This overrides the current values.

        Parameters
        ----------
        view_svcs_config_body : dict
            The configuration body for the view services.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

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

        Notes
        -----

        Details on view services configuration can be found at:
         https://egeria-project.org/guides/admin/servers/configuring-the-view-services/?h=view#integration-view-services

        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/view-services/configuration"
        self.make_request("POST", url, view_svcs_config_body)

    def set_integration_groups_config(self, integration_groups_config_body: dict, server_name: str = None) -> None:
        """ Set up the configuration for all the open metadata integration groups. This overrides the current values.
        Parameters
        ----------
        integration_groups_config_body : dict
            The configuration body for the integration groups.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

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

        Notes
        -----

        Details on integration group configuration can be found at:
         https://egeria-project.org/concepts/integration-group/

        body format is:
        [
          {
            "integrationGroupQualifiedName": "string",
            "omagserverPlatformRootURL": "string",
            "omagserverName": "string"
          }
        ]
        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.admin_command_root}/servers/{server_name}/integration-groups/configuration/all"
        self.make_request("POST", url, integration_groups_config_body)

    def set_engine_host_services(self):
        # handles an array of engine list - pass in JSON

        pass

    def set_integration_daemon_services_configuration(self):
        # pass a json list
        pass

    def config_integration_service(self, remote_omag_server: str, remote_omag_platform_url: str,
                                   service_url_marker: str, integration_service_options: dict, connector_configs: list,
                                   server_name: str = None) -> None:

        if server_name is None:
            server_name = self.server_name

        if not isinstance(connector_configs, list):
            exc_msg = ' ==> connector_configs must be a list of dictionaries'
            raise Exception(exc_msg)

        validate_name(remote_omag_server)
        validate_url(remote_omag_platform_url)

        validate_name(service_url_marker)

        request_body = {"class": "IntegrationServiceRequestBody", "omagserverPlatformRootURL": remote_omag_platform_url,
            "omagserverName": remote_omag_server, "integrationServiceOptions": integration_service_options,
            "integrationConnectorConfigs": connector_configs}

        url = f"{self.admin_command_root}/servers/{server_name}/integration-services/{service_url_marker}"
        # print(f"URL is : {url}")
        # print(f"body is : \n{json.dumps(request_body, indent=4)}")

        self.make_request("POST", url, request_body)
        return

    def config_all_integration_services(self, remote_omag_server: str, remote_omag_platform_url: str,
                                        integration_service_options: dict, connector_configs: dict,
                                        server_name: str = None) -> None:

        if server_name is None:
            server_name = self.server_name
        validate_name(remote_omag_server)
        validate_url(remote_omag_platform_url)

        request_body = {"IntegrationConnectorConfigs": [
            {"class": "IntegrationServiceRequestBody", "omagserverPlatformRootURL": remote_omag_platform_url,
                "omagserverName": remote_omag_server, "integrationServiceOptions": integration_service_options,
                "integrationConnectorConfigs": connector_configs}]}

        url = f"{self.admin_command_root}/servers/{server_name}/integration-services"
        print(f"URL is : {url}")
        print(f"body is : \n{json.dumps(request_body, indent=4)}")

        self.make_request("POST", url, request_body)

    def clear_integration_service(self, service_url_marker: str, server_name: str = None) -> None:
        if server_name is None:
            server_name = self.server_name
        validate_name(service_url_marker)

        url = f"{self.admin_command_root}/servers/{server_name}/integration-services/{service_url_marker}"
        self.make_request("DELETE", url)

    def get_integration_service_config(self, service_url_marker: str, server_name: str = None) -> dict | str:
        if server_name is None:
            server_name = self.server_name
        validate_name(service_url_marker)
        url = f"{self.admin_command_root}/servers/{server_name}/integration-services/{service_url_marker}/configuration"
        response = self.make_request("GET", url)
        return response.json().get("config", "No configuration found")

    def get_integration_services_configs(self, server_name: str = None) -> dict | str:
        if server_name is None:
            server_name = self.server_name

        url = f"{self.admin_command_root}/servers/{server_name}/integration-services/configuration"
        response = self.make_request("GET", url)
        return response.json().get("services", "No configuration found")

    def set_lineage_warehouse_services(self, body: dict, lineage_server: str) -> None:
        url = f"{self.admin_command_root}/servers/{lineage_server}/lineage-warehouse/configuration"
        self.make_request("POST", url, body)

    def remove_lineage_warehouse_services(self, lineage_server: str = None) -> None:
        url = f"{self.admin_command_root}/servers/{lineage_server}/lineage-warehouse/configuration"
        self.make_request("DELETE", url)
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 OMAG Server configuration functions.  These functions add definitions to an OMAG server's configuration document
"""


from .client import Client
from .config import enable_ssl_check, is_debug


from .util_exp import (
    OMAGCommonErrorCode,
    EgeriaException,
    InvalidParameterException,
    OMAGServerInstanceErrorCode,
    PropertyServerException,
    UserNotAuthorizedException, validate_name
)

class OMAGServerConfigClient(Client):
    """
       Client to configure commmon server properties, audit log, server security and default event bus.

       Attributes:
           server_name: str
                Name of the server to configure.
           platform_url : str
               URL of the server platform to connect to
           user_id : str
               The identity of the user calling the method - this sets a default optionally used by the methods
               when the user doesn't pass the user_id on a method call.
           user_pwd: str
                The password associated with the user
           verify_flag: bool = enable_ssl_check
                Set true for SSL verification to be enabled, false for disabled. Default behaviour set by the
                enable_ssl_check attribute from config.py

       Methods:
           __init__(self,
                    platform_url: str,
                    end_user_id: str,
                    )
            Initializes the connection - throwing an exception if there is a problem

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

    def get_audit_log_destinations(self, server_name:str = None) -> str:

        """ Add a destination for the audit log

         /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations

         Parameters
         ----------
         server_name : str
         The name of the server to retrieve the audit configuration for.

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
         ConfigurationErrorException
             Raised when configuration parameters passed on earlier calls turn out to be
             invalid or make the new call invalid.

         """
        if server_name is None:
            server_name = self.server_name

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations"
        response = self.make_request("GET", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return response.json()
        else:
            raise InvalidParameterException(response.content)

    def set_audit_log_destinations(self, audit_dest_body: str, server_name:str = None) -> str:
        """ Sets the audit log destination for a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations

        Parameters
        ----------

        audit_dest_body : str
            A JSON document describing the audit destinations for this server.

        server_name : str
            Name of the server to update.

        Returns
        -------
        JSON string containing the status of the request.

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

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations"
        response = self.make_request("POST", url, audit_dest_body )
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def clear_audit_log_destinations(self, server_name:str = None):

        """ Clears the audit log destination configuration for the specified server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations

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

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations"
        response = self.make_request("DELETE", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return
        else:
            raise InvalidParameterException(response.content)

    def add_console_log_destinations(self, severities: [str],server_name: str = None) -> bool:
        """ Adds a log destination to a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/console

        Parameters
        ----------

        server_name : str
            Name of the server to update.

        Returns
        -------
        True if successful, False otherwise

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

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/console"
        response = self.make_request("POST", url, severities)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def add_default_log_destinations(self, server_name: str = None) -> str:
        """ Adds a log destination to a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/default

        Parameters
        ----------

        server_name : str
            Name of the server to update.

        Returns
        -------
        JSON string containing the status of the request.

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

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/default"
        response = self.make_request("POST", url)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def add_topic_log_destinations(self, topic_name: str, severities: [str], server_name: str = None) -> str:
        """ Adds a log destination to a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/event-topic

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
        JSON string containing the status of the request.

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

        url = (self.admin_command_root + "/servers/" + server_name +
               "/audit-log-destinations/event-topic?topicName=" + topic_name)
        response = self.make_request("POST", url, severities)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def add_file_log_destinations(self, directory_name:str, severities: [str] = None, server_name: str = None ) -> str:
        """ Adds a file log destination to a server. Each message is a seperate file in the directory
            indicated by the directory name.

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/files

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
        JSON string containing the status of the request.

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

        if severities is None:
            severities = []

        url = (self.admin_command_root + "/servers/" + server_name +
               "/audit-log-destinations/files?directoryName=" + directory_name)
        response = self.make_request("POST", url, severities)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    def add_SLF4J_log_destination(self, severities: [str] = None, server_name: str = None) -> str:
        """ Adds an SLF4J log destination to a server

        /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/slf4j

        Parameters
        ----------

        severities: str
            List of severities to send to the destination.
        server_name : str
            Name of the server to update.

        Returns
        -------
        JSON string containing the status of the request.

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
        if severities is None:
            severities = []

        url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/slf4j"
        response = self.make_request("POST", url, severities)
        if response.status_code != 200:
            return response.json()  # should never get here?

        related_code = response.json().get("relatedHTTPCode")
        if related_code == 200:
            return True
        else:
            raise InvalidParameterException(response.content)

    # def clear_a_log_destination(self, dest_name: str, server_name: str = None) -> bool:
    #     """  Clears audit log destinations for a server
    #
    #     /open-metadata/admin-services/users/{userId}/servers/{serverName}/audit-log-destinations/{{dest_name}}
    #
    #     Parameters
    #     ----------
    #
    #     dest_name : str
    #         Qualified name of the log destination to clear.
    #     server_name : str
    #         Name of the server to update.
    #
    #     Returns
    #     -------
    #     JSON string containing the status of the request.
    #
    #     Raises
    #     ------
    #
    #     InvalidParameterException:
    #         If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     PropertyServerException:
    #         Raised by the server when an issue arises in processing a valid request
    #     NotAuthorizedException:
    #         The principle specified by the user_id does not have authorization for the requested action
    #     ConfigurationErrorException:
    #         Raised when configuration parameters passed on earlier calls turn out to be
    #         invalid or make the new call invalid.
    #
    #     """
    #     if server_name is None:
    #         server_name = self.server_name
    #
    #     url = self.admin_command_root + "/servers/" + server_name + "/audit-log-destinations/" + dest_name
    #     response = self.make_request("DELETE", url)
    #     if response.status_code != 200:
    #         return response.json()  # should never get here?
    #
    #     related_code = response.json().get("relatedHTTPCode")
    #     if related_code == 200:
    #         return True
    #     else:
    #         raise InvalidParameterException(response.content)



class CohortMemberConfigClient(OMAGServerConfigClient):
    def __init__(self,
                 server_name: str,
                 platform_url:str,
                 user_id: str,
                 user_pwd: str = None,
                 verify_flag: bool = False,
                 ):
        OMAGServerConfigClient.__init__( self, server_name, platform_url, user_id, user_pwd, verify_flag)


class MetadataAccessServerConfigClient(CohortMemberConfigClient):
    def __init__(self,
                 server_name: str,
                 platform_url: str,
                 user_id: str,
                 user_pwd: str = None,
                 verify_flag: bool = False,
                 ):
       CohortMemberConfigClient.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)


class MetadataAccessStoreConfigClient(MetadataAccessServerConfigClient):
    def __init__(self,
                 server_name: str,
                 platform_url: str,
                 user_id: str,
                 user_pwd: str = None,
                 verify_flag: bool = False,
                 ):
        CohortMemberConfigClient.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)

# def configurePlatformURL(self):
#     self.admin_command_root = (
#         self.platform_url
#         + "/open-metadata/platform-services/users/"
#         + self.user_id
#         + "/server-platform"
#     )
#     # print("   ... configuring the platform the server will run on...")
#     url = (
#         self.admin_command_root
#         + serverName
#         + "/server-url-root?url="
#         + serverPlatform
#     )
#     issuePostNoBody(url)


# def configureMaxPageSize(admin_platform_url, adminUserId, serverName, maxPageSize):
#     adminCommandURLRoot = (
#         admin_platform_url
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the maximum page size...")
#     url = adminCommandURLRoot + serverName + "/max-page-size?limit=" + maxPageSize
#     issuePostNoBody(url)
#
#
# def configureServerType(admin_platform_url, adminUserId, serverName, serverType):
#     adminCommandURLRoot = (
#         admin_platform_url
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the server's type...")
#     url = adminCommandURLRoot + serverName + "/server-type?typeName=" + serverType
#     issuePostNoBody(url)
#
#
# def clearServerType(adminPlatformURL, adminUserId, serverName):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... clearing the server's type...")
#     url = adminCommandURLRoot + serverName + "/server-type?typeName="
#     issuePostNoBody(url)
#
#
# def configureOwningOrganization(
#     adminPlatformURL, adminUserId, serverName, organizationName
# ):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the server's owning organization...")
#     url = (
#         adminCommandURLRoot + serverName + "/organization-name?name=" + organizationName
#     )
#     issuePostNoBody(url)
#
#
# def configureUserId(adminPlatformURL, adminUserId, serverName, userId):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the server's userId...")
#     url = adminCommandURLRoot + serverName + "/server-user-id?id=" + userId
#     issuePostNoBody(url)
#
#
# def configurePassword(adminPlatformURL, adminUserId, serverName, password):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the server's password (optional)...")
#     url = (
#         adminCommandURLRoot + serverName + "/server-user-password?password=" + password
#     )
#     issuePostNoBody(url)
#
#
# def configureSecurityConnection(
#     adminPlatformURL, adminUserId, serverName, securityBody
# ):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the server's security connection...")
#     url = adminCommandURLRoot + serverName + "/security/connection"
#     issuePost(url, securityBody)
#
#
# def configureDefaultAuditLog(adminPlatformURL, adminUserId, serverName):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the default audit log...")
#     url = adminCommandURLRoot + serverName + "/audit-log-destinations/default"
#     issuePostNoBody(url)
#
#
# def configureEventBus(adminPlatformURL, adminUserId, serverName, busBody):
#     adminCommandURLRoot = (
#         adminPlatformURL
#         + "/open-metadata/admin-services/users/"
#         + adminUserId
#         + "/servers/"
#     )
#     print("   ... configuring the event bus for this server...")
#     url = adminCommandURLRoot + serverName + "/event-bus"
#     issuePost(url, busBody)

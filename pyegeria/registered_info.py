"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module allows users to query the available (registered) capabilities of Egeria. Detailed information is returned
to provide both insight and understanding in how to use these capabilities. For example, when configuring an Egeria
integration service, it is import registered_info.pyant to know what companion service it depends on so that you can
make sure the companion service is also configured and running.

"""

from pyegeria._client import Client


class RegisteredInfo(Client):
    """ Client to discover Egeria services and capabilities

    Parameters:
    ----------
        server_name: str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        verify_flag: bool
            Flag to indicate if SSL Certificates should be verified in the HTTP requests.
            Defaults to False.

    Methods:
    -------
        list_registered_svcs(self, kind: str = None, fmt: str = 'json', skinny: bool = True, wrap_len: int = 30)
            -> list | str
            Returns information about the different kinds of services as either JSON or a printable table.

        list_severity_definitions(self, fmt: str = 'json', skinny: bool = True, wrap_len: int = 30) -> list | str
            Returns a list of severity definitions for an OMAG Server used by the audit services.

        list_asset_types(self, server: str = None) -> list | str
            Lists the defined asset types.
    """

    admin_command_root: str

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
    ):
        if server_name is None:
            server_name = "NA"
        Client.__init__(self, server_name, platform_url,
                        user_id, user_pwd, verify_flag)
        self.admin_command_root = (f"{self.platform_url}/open-metadata/platform-services/users/"
                                   f"{self.user_id}/server-platform/registered-services")

    def list_registered_svcs(self, kind: str = None) -> list | str:
        """ Get the registered services for the OMAG Server Platform

           Parameters
           ----------
            kind: str, optional
                The kind of service to return information for. If None, then provide back a list of service kinds.

           Returns
           -------
           dict | str
               Returns JSON dict of the requested information or a help string if input is 'help'.
           Raises
           ------
           InvalidParameterException
               If the response code is not 200.
           PropertyServerException:
               Raised by the server when an issue arises in processing a valid request
           NotAuthorizedException:
               The principle specified by the user_id does not have authorization for the requested action

           """
        if kind is None or kind == "help":
            return ("""
            The kinds of services that you can get more information include:
                all.....................lists all registered services
                access-services.........lists all registered access services
                common-services.........lists all registered common services
                engine-services.........lists all registered engine services
                governance-services.....lists all registered governance services
                integration-services....lists all registered integration services
                view-services...........lists all registered view services

                Pass in a parameter from the left-hand column into the function to 
                get more details on the specified service category.
            """)
        if kind == "all":
            url = f"{self.admin_command_root}"
        else:
            url = f"{self.admin_command_root}/{kind}"
        response = self.make_request("GET", url)

        return response.json().get("services", "No services found")

    def list_severity_definitions(self) -> list | str:
        """ Get the registered severities for the OMAG Server

          Parameters
          ----------

          Returns
          -------
          dict | str
              Return a dictionary containing the registered services for the specified platform.
          Raises
          ------
          InvalidParameterException
              If the response code is not 200.
          PropertyServerException:
              Raised by the server when an issue arises in processing a valid request
          NotAuthorizedException:
              The principle specified by the user_id does not have authorization for the requested action

        """
        url = (f"{self.platform_url}/servers/{self.server_name}/open-metadata/repository-services"
               f"/users/{self.user_id}/audit-log/severity-definitions"
               )
        response = self.make_request("GET", url)
        return response.json().get("severities", "No severities found")

    def list_asset_types(self, server: str = None) -> list | str:
        """ Get the registered severities for the OMAG Server

          Parameters
          ----------
           server: str, optional, default = None

          Returns
          -------
          dict | str
              Returns a list of the asset types.

          Raises
          ------
          InvalidParameterException
              If the response code is not 200.
          PropertyServerException:
              Raised by the server when an issue arises in processing a valid request
          NotAuthorizedException:
              The principle specified by the user_id does not have authorization for the requested action

        """
        server = self.server_name if server is None else server
        url = f"{self.platform_url}/servers/{server}/api/open-metadata/asset-catalog/assets/types"

        response = self.make_request("GET", url)
        return response.json().get('types', 'no types found')

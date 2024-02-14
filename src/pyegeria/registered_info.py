"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module allows users to query the available (registered) capabilities of Egeria. Detailed information is returned
to provide both insight and understanding in how to use these capabilities. For example, when configuring an Egeria
integration service, it is important to know what companion service it depends on so that you can make sure the
companion service is also configured and running.

"""
import pandas as pd
from tabulate import tabulate

from .utils import wrap_text

from ._client import Client


class RegisteredInfo(Client):
    """ Client to discover Egeria services and capabilities

    Attributes:

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
        __init__(self,platform_url: str, end_user_id: str)
         Initializes the connection - throwing an exception if there is a problem

        list_registered_svcs(self, kind: str = None, fmt: str = 'json', skinny: bool = True, wrap_len: int = 30)
            -> list | str
        Returns information about the different kinds of services as either JSON or a printable table.

    """

    admin_command_root: str

    def __init__(
            self,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
            server_name: str = None
    ):
        if server_name is None:
            server_name = "NA"
        Client.__init__(self, server_name, platform_url,
                        user_id, user_pwd, verify_flag)
        self.admin_command_root = (f"{self.platform_url}/open-metadata/platform-services/users/"
                                   f"{self.user_id}/server-platform/registered-services")

    def list_registered_svcs(self, kind: str = None, fmt: str = 'json', skinny: bool = True,
                             wrap_len: int = 30) -> list | str:
        """ Get the registered services for the OMAG Server Platform

           Parameters
           ----------
            kind: str, optional
                The kind of service to return information for. If None, then provide back a list of service kinds.
            fmt: str, optional, default = 'json'
                If fmt is 'json', then return the result as a JSON string. If fmt is 'table', then
                return the result as a nicely formatted table string.
            skinny: bool, optional, default = True
                If a table is being created and `skinny` is true, then return a subset of the information,
                if false return all columns.
            wrap_len: int, optional, default = 30
                If a table is being created, the width of the column to wrap text to.
           Returns
           -------
           dict | str
               If fmt is 'JSON' then return a dictionary containing the registered services for the specified
                platform. If fmt is 'table' then return the result as a nicely formatted printable table string.

           Raises
           ------
           InvalidParameterException
               If the response code is not 200.
           PropertyServerException:
               Raised by the server when an issue arises in processing a valid request
           NotAuthorizedException:
               The principle specified by the user_id does not have authorization for the requested action

           """
        if kind is None or kind is "help":
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
        if kind is "all":
            url = f"{self.admin_command_root}"
        else:
            url = f"{self.admin_command_root}/{kind}"
        response = self.make_request("GET", url)

        if fmt is 'json':
            return response.json().get("services", "No services found")
        elif fmt is 'table':
            df = pd.DataFrame(response.json().get("services", []))
            if skinny:
                df = df.drop(columns=['serviceId', 'serviceDevelopmentStatus'])
            return tabulate(wrap_text(df, wrap_len=wrap_len), headers='keys', tablefmt='psql')

    def list_severity_definitions(self, fmt: str = 'json', skinny: bool = True, wrap_len: int = 30) -> list | str:
        """ Get the registered severities for the OMAG Server

          Parameters
          ----------
           fmt: str, optional, default = 'json'
               If fmt is 'json', then return the result as a JSON string. If fmt is 'table', then
               return the result as a nicely formatted table string.
           skinny: bool, optional, default = True
               If a table is being created and `skinny` is true, then return a subset of the information,
               if false return all columns.
           wrap_len: int, optional, default = 30
               If a table is being created, the width of the column to wrap text to.

          Returns
          -------
          dict | str
              If fmt is 'JSON' then return a dictionary containing the registered services for the specified
               platform. If fmt is 'table' then return the result as a nicely formatted printable table string.

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
        if fmt is 'json':
            return response.json().get("severities", "No severities found")
        elif fmt is 'table':
            df = pd.DataFrame(response.json().get("severities", []))
            if skinny:
                df = df.drop(columns=['ordinal'])
            return tabulate(wrap_text(df, wrap_len=wrap_len), headers='keys', tablefmt='psql')

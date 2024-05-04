"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module allows users to query the available (registered) capabilities of Egeria. Detailed information is returned
to provide both insight and understanding in how to use these capabilities. For example, when configuring an Egeria
integration service, it is importregistered_info.pyant to know what companion service it depends on so that you can make sure the
companion service is also configured and running.

"""

import pandas as pd
from tabulate import tabulate

from pyegeria._client import Client
from pyegeria.utils import wrap_text


class LoadedResources(Client):
    """ Client to search and retrieve currently loaded information about connectors, templates, governance actions,
        etc.

    Attributes:
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

    def get_all_templates(self, server: str = None, start_from: int = 0, page_size: int = 0) -> list | str:
        """ Get Loaded templates for the Server.

           Parameters
           ----------

           Returns
           -------
           dict | str
              A dictionary containing a simplified list of key template attributes.

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
        url = (f"{self.platform_url}/servers/{server}/open-metadata/framework-services/asset-owner/open-metadata-store/"
               f"users/{self.user_id}/metadata-elements/by-search-string?startFrom=start_from&pageSize=page_size")
        body = {
                  "class" : "SearchStringRequestBody",
                  "searchString" : ".*Template.*"
                }
        response = self.make_request("POST", url, body)
        return response.json().get("elementList", "No elements")

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
        if fmt == 'json':
            return response.json().get("severities", "No severities found")
        elif fmt == 'table':
            df = pd.DataFrame(response.json().get("severities", []))
            if skinny:
                df = df.drop(columns=['ordinal'])
            return tabulate(wrap_text(df, wrap_len=wrap_len), headers='keys', tablefmt='psql')

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
        url = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/asset-catalog/assets/types"

        response = self.make_request("GET", url)
        return response.json().get('types', 'no types found')

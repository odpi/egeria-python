"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Governance Engine functions.  These functions initiate and manage Governance Actions and Processes

 This module is deprecated - please use Automated Curation.
"""

from datetime import datetime

from ._client import Client
from ._globals import enable_ssl_check


def body_slimmer(body: dict) -> dict:
    """ body_slimmer is a little function to remove unused keys from a dict

    Parameters
    ----------
    body : the dictionary that you want to slim

    Returns
    -------
    dict:
        a slimmed body
    """
    slimmed = {key: value for key, value in body.items() if value}
    return slimmed


class GovEng(Client):
    """
       Client to initiate and manage governance actions and processes.

       Attributes:
           server_name: str
                Name of the server to use.
           platform_url : str
               URL of the server platform to connect to
           user_id : str
               The identity of the user calling the method - this sets a default optionally used by the methods
               when the user doesn't pass the user_id on a method call.
           user_pwd: str = None
                The password associated with the user
           verify_flag: bool = enable_ssl_check
                Set true for SSL verification to be enabled, false for disabled. Default behaviour set by the
                enable_ssl_check attribute from _globals.py

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
        Client.__init__(self, server_name, platform_url, user_id,
                        user_pwd, verify_flag)
        self.engine_command_root = (
                self.platform_url
                + "/servers/" + server_name
                + "/open-metadata/framework-services/governance-engine/open-governance-service/users/"
                + user_id
        )

    def get_engine_actions(self, start_from: int = 0, page_size: int = 0) -> [dict]:
        """ Get engine actions associated deployed on the server.

        Args:
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.

        """
        url = (self.engine_command_root + "/engine-actions?startFrom=" +
               str(start_from) + "&pageSize=" + str(page_size))
        response = self.make_request("GET", url)

        governance_elements = response.json().get('elements')
        return governance_elements

    def get_engine_action(self, engine_action_guid: str) -> str:
        """ Return the governance action associated with the supplied guid

        Parameters
        ----------
        engine_action_guid : str
            The unique identifier of the engine action to retrieve.
        Returns
        -------
        JSON string of the governance action associated with the guid

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException
        """

        url = self.engine_command_root + "/engine-actions/" + engine_action_guid
        response = self.make_request("GET", url)

        governance_element = response.json().get('element')
        return governance_element

    def get_active_engine_actions(self, start_from: int = 0, page_size: int = 0) -> [str]:
        """ Get active governance actions associated on the server.

        Args:
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.
        """
        url = (self.engine_command_root + "/engine-actions/active?startFrom=" +
               str(start_from) + "&pageSize=" + str(page_size))

        response = self.make_request("GET", url)
        governance_elements = response.json().get('elements')
        return governance_elements
        
    def get_engine_actions_by_name(self, name: str, start_from: int = 0, page_size: int = 0) -> str:
        """ Retrieve engine actions matching the name string.
        Args:
            name (str): The qualified name or display name of the governance action to get.
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.

        """
        url = (self.engine_command_root + "/engine-actions/by-name?startFrom=" +
               str(start_from) + "&pageSize=" + str(page_size))
        body = {
            "class": "NameRequestBody",
            "name": name
        }
        response = self.make_request("POST", url, body)

        governance_elements = response.json().get('elements')
        return governance_elements

    def find_engine_actions(self, search_string: str, start_from: int = 0, page_size: int = 0) -> [str]:
        """ Search for engine actions matching the search string.

        Args:
            search_string (str): The search string to query for.
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.
       """
        url = (self.engine_command_root + "/engine-actions/by-search-string?startFrom=" +
               str(start_from) + "&pageSize=" + str(page_size))
        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string
        }
        response = self.make_request("POST", url, body)

        governance_elements = response.json().get('elements')
        return governance_elements

    def get_governance_action_process_by_guid(self, gov_process_guid: str) -> str:
        """
            Retrieves information about a governance action process based on its GUID.

            Args:
                gov_process_guid (str): The GUID (Globally Unique Identifier) of the governance action process.

            Returns:
                str: The JSON representation of the governance action process element.

            Raises:
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.
                PropertyServerException: If the API response indicates a server side error.
                UserNotAuthorizedException:

            Note:
                This method assumes that the provided GUID is valid and corresponds to an existing
                governance action process in the system.

            """
        url = self.engine_command_root + "/governance-action-processes/" + gov_process_guid
        response = self.make_request("GET", url)
        governance_element = response.json().get('element')
        return governance_element

    def get_governance_action_processes_by_name(self, name: str, start_from: int = 0, page_size: int = 0) -> [str]:
        """
        Retrieves governance action processes based on their name only (no wildcards).

        Args:
            name (str): The qualified name or display name of the governance action to get.
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.

        """
        url = (self.engine_command_root + "/governance-action-processes/by-name?startFrom=" + str(start_from)
               + "&pageSize=" + str(page_size))
        body = {
            "class":          "NameRequestBody",
            "name":           name
        }
        response = self.make_request("POST", url, body)
        governance_elements = response.json().get('elements')
        return governance_elements
        
    def find_governance_action_processes(self, search_string: str, start_from: int = 0, page_size: int = 0) -> [str]:
        """ Return governance action processes that match the search string (with regex).

        Args:
            search_string (str): The search string to query for.
            start_from (int, optional): The index to start retrieving processes from. Defaults to 0.
            page_size (int, optional): The number of processes to retrieve per page. Defaults to 0 (no pagination).

        Returns:
            List[str]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
            InvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note:
            Pagination of 0 defaults to server default.

        """
        url = (self.engine_command_root + "/governance-action-processes/by-search-string?startFrom=" + str(start_from)
               + "&pageSize=" + str(page_size))
        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string
        }
        response = self.make_request("POST", url, body)

        governance_elements = response.json().get('elements')
        return governance_elements
        
    def initiate_governance_action_process(self, qualified_name: str, request_source_guids: [str],
                                           action_targets: [str], start_time: datetime, request_parameters: dict,
                                           orig_service_name: str, orig_engine_name: str) -> str:
        """ initiate_gov_action_process

        This method starts a governance action process using the supplied parameters.

        Parameters
        ----------
        qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime
            - time to start the process
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
        url = self.engine_command_root + "/governance-action-processes/initiate"
        body = {
            "class":                     "GovernanceActionProcessRequestBody",
            "processQualifiedName":       qualified_name,
            "requestSourceGUIDs":         request_source_guids,
            "actionTargets":              action_targets,
            "startTime":                  int(start_time.timestamp() * 1000),
            "requestParameters":          request_parameters,
            "originatorServiceName":      orig_service_name,
            "originatorEngineName":       orig_engine_name
        }
        new_body = body_slimmer(body)
        response = self.make_request("POST", url, new_body)

        return response.json().get('guid')
        
    def initiate_engine_action(self, qualified_name: str, domain_identifier: int, display_name: str,
                               description: str, request_source_guids: str, action_targets: str,
                               received_guards: [str], start_time: datetime, gov_engine_name: str,
                               request_type: str, request_parameters: dict, process_name: str,
                               request_src_name: str = None, originator_svc_name: str = None,
                               originator_eng_name: str = None) -> str:
        """
            Initiates an engine action with the specified parameters.

            Args:
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

            Returns:
                str: The GUID (Globally Unique Identifier) of the initiated governance action.

            Raises:
                InvalidParameterException: If the API response indicates an error (non-200 status code),
                this exception is raised with details from the response content.

            Note:
                The `start_time` parameter should be a `datetime` object representing the start 
                time of the governance action.


            """
        url = self.engine_command_root + ("/governance-engines/" + gov_engine_name +
                                          "/engine-actions/initiate")

        body = {
            "class":                      "GovernanceActionRequestBody",
            "qualifiedName":              qualified_name + str(int(start_time.timestamp())),
            "domainIdentifier":           domain_identifier,
            "displayName":                display_name,
            "description":                description,
            "requestSourceGUIDs":         request_source_guids,
            "actionTargets":              action_targets,
            "receivedGuards":             received_guards,
            "startTime":                  int(start_time.timestamp()*1000),
            "requestType":                request_type,
            "requestParameters":          request_parameters,
            "process_name":                process_name,
            "requestSourceName":          request_src_name,
            "originatorServiceName":      originator_svc_name,
            "originatorEngineName":       originator_eng_name
        }
        new_body = body_slimmer(body)
        response = self.make_request("POST", url, new_body)
        return response.json().get('guid')


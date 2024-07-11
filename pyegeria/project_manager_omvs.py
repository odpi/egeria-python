"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain and explore projects.
    https://egeria-project.org/concepts/project

"""
import asyncio
import time

# import json
from pyegeria._client import Client
from pyegeria._validators import (
    validate_guid,
    validate_search_string,
)
from pyegeria.utils import body_slimmer


class ProjectManager(Client):
    """
    Create and manage projects. Projects may be organized in a hierarchy.
    See https://egeria-project.org/types/1/0130-Projects

    Attributes:

        server_name: str
            The name of the View Server to connect to.
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
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            sync_mode: bool = True
    ):
        self.command_base: str = f"/api/open-metadata/project-manager/metadata-elements"
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)

    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #
    async def _async_get_linked_projects(self, parent_guid: str, project_status: str = None, effective_time: str = None,
                                         server_name: str = None, start_from: int = 0, page_size: int = None) \
            -> list | str:
        """  Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked projects from.
        project_status: str, optional
            Optionally, filter results by project status.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects linked off of the supplied element filtered by project status and effective time.

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
        if page_size is None:
            page_size = self.page_size

        body = {
            "filter": project_status,
            "effectiveTime": effective_time,
        }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/"
               f"metadata-elements/{parent_guid}/projects?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json()

    def get_linked_projects(self, parent_guid: str, project_status: str = None, effective_time: str = None,
                            server_name: str = None, start_from: int = 0, page_size: int = None) -> list | str:
        """  Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status.

        Parameters
        ----------
        parent_guid: str
             The identity of the parent to find linked projects from
        project_status: str, optional
            Optionally, filter results by project status.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects linked off of the supplied element filtered by project status and effective time.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_linked_projects(parent_guid, project_status,
                                                                       effective_time, server_name,
                                                                       start_from, page_size))
        return resp

    async def _async_get_classified_projects(self, project_classification: str, effective_time: str = None,
                                             server_name: str = None, start_from: int = 0, page_size: int = None) \
            -> list | str:
        """ Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign or Task. There is also GlossaryProject and GovernanceProject. Async version.

        Parameters
        ----------
        project_classification: str
            The project classification to search for.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects filtered by project classification, and effective time.

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
        if page_size is None:
            page_size = self.page_size

        body = {
            "filter": project_classification,
            "effectiveTime": effective_time,
        }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/"
               f"projects/by-classifications?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json()

    def get_classified_projects(self, project_classification: str, effective_time: str = None, server_name: str = None,
                                start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign or Task. There is also GlossaryProject and GovernanceProject.

        Parameters
        ----------
        project_classification: str
            The project classification to search for.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects filtered by project classification, and effective time.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_classified_projects(project_classification,
                                                                           effective_time, server_name,
                                                                           start_from, page_size))
        return resp

    async def _async_get_project_team(self, project_guid: str, team_role: str = None, effective_time: str = None,
                                      server_name: str = None, start_from: int = 0,
                                      page_size: int = None) -> list | str:
        """ Returns the list of actors that are linked off of the project. This includes the project managers.
            The optional request body allows a teamRole to be specified as a filter. To filter out the project managers,
            specify ProjectManagement as the team role. See https://egeria-project.org/concepts/project for details.
            Async version.

        Parameters
        ----------
        project_guid: str
            The identity of the project to return team information about.
        team_role: str, optional
            team role to filter on. Project managers would be "ProjectManagement".
        effective_time: str, optional
            Time at which to query the team role. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        list | str
            The list of actors linked off the project, including project managers Returns a string if none found.

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
        """
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size

        body = {
            effective_time: effective_time,
            "filter": team_role
        }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/"
               f"{project_guid}/team?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)

        result = resp.json().get('elements', 'No elements found')
        return result

    def get_project_team(self, project_guid: str, team_role: str = None, effective_time: str = None,
                         server_name: str = None, start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of actors that are linked off of the project. This includes the project managers.
            The optional request body allows a teamRole to be specified as a filter. To filter out the project managers,
            specify ProjectManagement as the team role. See https://egeria-project.org/concepts/project for details.
            Async version.

        Parameters
        ----------
        project_guid: str
            The identity of the project to return team information about.
        team_role: str, optional
            team role to filter on. Project managers would be "ProjectManagement".
        effective_time: str, optional
            Time at which to query the team role. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        list | str
            The list of actors linked off the project, including project managers Returns a string if none found.

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
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_project_team(project_guid, team_role, effective_time,
                                                                    server_name, start_from, page_size))
        return resp

    async def _async_find_projects(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                   ends_with: bool = False, ignore_case: bool = False,
                                   server_name: str = None,
                                   start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of projects matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
            Async version.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects matching the search string. Returns a string if none found.

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
        if page_size is None:
            page_size = self.page_size
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        validate_search_string(search_string)

        if search_string == '*':
            search_string = None

        body = {
            "filter": search_string,
            "effective_time": effective_time,
        }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No elements found")

    def find_projects(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                      ends_with: bool = False, ignore_case: bool = False, server_name: str = None,
                      start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of projects matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of projects matching the search string. Returns a string if none found.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_find_projects(search_string, effective_time, starts_with,
                                                                 ends_with, ignore_case,
                                                                 server_name, start_from, page_size))

        return resp

    async def _async_get_projects_by_name(self, name: str, effective_time: str = None,
                                          server_name: str = None,
                                          start_from: int = 0, page_size: int = None) -> list | str:

        """ Returns the list of projects with a particular name. Async version.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. ISO 8601 format.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of collections match matching the name. Returns a string if none found.

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
        if page_size is None:
            page_size = self.page_size

        validate_search_string(name)

        body = {
            "filter": name,
            "effective_time": effective_time,
        }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No elements found")

    def get_projects_by_name(self, name: str, effective_time: str = None, server_name: str = None,
                             start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of projects with a particular name.

            Parameters
            ----------
            name: str,
                name to use to find matching collections.
            effective_time: str, [default=None], optional
                Effective time of the query. If not specified will default to any time. ISO 8601 format.
            server_name : str, optional
                The name of the server to  configure.
                If not provided, the server name associated with the instance is used.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            Returns
            -------
            List | str

            A list of collections match matching the name. Returns a string if none found.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_projects_by_name(name, effective_time,
                                                                        server_name, start_from, page_size))

        return resp

    async def _async_get_project(self, project_guid: str, effective_time: str = None,
                                 server_name: str = None) -> dict | str:
        """ Return the properties of a specific project. Async version.

        Parameters
        ----------
        project_guid: str,
            unique identifier of the project.
        effective_time: str, [default=None], optional
             Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        dict | str

        A JSON dict representing the specified project. Returns a string if none found.

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

        validate_guid(project_guid)
        body = {
            "effective_time": effective_time,
        }
        url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}"

        resp = await self._async_make_request("GET", url, body)
        return resp.json()

    def get_project(self, project_guid: str, server_name: str = None) -> dict | str:
        """ Return the properties of a specific project.

        Parameters
        ----------
        project_guid: str,
            unique identifier of the project.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        dict | str

        A JSON dict representing the specified project. Returns a string if none found.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_project(project_guid, server_name))

        return resp

    #
    #   Create project methods
    #
    async def _async_create_project_w_body(self, body: dict, classification: str = None,
                                           server_name: str = None) -> str:
        """  Create project: https://egeria-project.org/concepts/project Async version.

            Parameters
            ----------.
            body: dict
                A dict representing the details of the project to create.
            classification: str, optional
                An optional project classification. See https://egeria-project.org/types/1/0130-Projects for values.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            str - the guid of the created project

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
            Notes
            -----

            Body structure like:
            {
              "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor" : False,
              "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName" : "open metadata type name",
              "parentAtEnd1": True,
              "projectProperties": {
                "class" : "ProjectProperties",
                "qualifiedName": "Must provide a unique name here",
                "identifier" : "Add business identifier",
                "name" : "Add display name here",
                "description" : "Add description of the project here",
                "projectStatus": "Add appropriate valid value for type",
                "projectPhase" : "Add appropriate valid value for phase",
                "projectHealth" : "Add appropriate valid value for health",
                "startDate" : "date/time",
                "plannedEndDate" : "date/time"
              }
            }

    """
        if server_name is None:
            server_name = self.server_name
        if classification is None:
            url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects"
        else:
            url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects?"
                   f"classificationName={classification}")
        body_s = body_slimmer(body)
        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("guid", "No GUID returned")

    def create_project_w_body(self, body: dict, classification: str = None, server_name: str = None) -> str:
        """  Create project: https://egeria-project.org/concepts/project

            Parameters
            ----------.
            body: dict
                A dict representing the details of the project to create.
            classification: str, optional
                An optional project classification. See https://egeria-project.org/types/1/0130-Projects for values.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance
                 is used.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            Body structure like:
            {
              "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor" : False,
              "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName" : "open metadata type name",
              "parentAtEnd1": True,
              "projectProperties": {
                "class" : "ProjectProperties",
                "qualifiedName": "Must provide a unique name here",
                "identifier" : "Add business identifier",
                "name" : "Add display name here",
                "description" : "Add description of the project here",
                "projectStatus": "Add appropriate valid value for type",
                "projectPhase" : "Add appropriate valid value for phase",
                "projectHealth" : "Add appropriate valid value for health",
                "startDate" : "date/time",
                "plannedEndDate" : "date/time"
              }
            }

    """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_project_w_body(body, classification, server_name))
        return resp

    async def _async_create_project(self, anchor_guid: str, parent_guid: str,
                                    parent_relationship_type_name: str, parent_at_end1: bool, display_name: str,
                                    description: str, classification_name: str = None, identifier: str = None,
                                    is_own_anchor: bool = False, project_status: str = None, project_phase: str = None,
                                    project_health: str = None, start_date: str = None,
                                    planned_end_date: str = None, server_name: str = None) -> str:
        """ Create Project: https://egeria-project.org/concepts/project Async version.

            Parameters
            ----------
            classification_name: str, optional
                Type of project to create; "PersonalProject", "Campaign", etc. If not provided, project will not
                be classified.
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element. Set to null if no
                anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            identifier: str
                A project identifier.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should be classified as its own anchor or not.
            project_status: str, optional
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.

            Returns
            -------
            str - the guid of the created project

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

        if parent_guid is None:
            is_own_anchor = False

        if classification_name is None:
            url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects"
        else:
            url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects?"
                   f"classificationName={classification_name}")

        body = {
            "anchorGUID": anchor_guid,
            "isOwnAnchor": str(is_own_anchor).lower(),
            "parentGUID": parent_guid,
            "parentRelationshipTypeName": parent_relationship_type_name,
            "parentAtEnd1": str(parent_at_end1).lower(),
            "projectProperties": {
                "class": "ProjectProperties",
                "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                "identifier": identifier,
                "name": display_name,
                "description": description,
                "projectStatus": project_status,
                "projectPhase": project_phase,
                "projectHealth": project_health,
                "startDate": start_date,
                "plannedEndDate": planned_end_date
            }
        }
        body_s = body_slimmer(body)
        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("guid", "No GUID returned")

    def create_project(self, anchor_guid: str, parent_guid: str,
                       parent_relationship_type_name: str, parent_at_end1: bool, display_name: str,
                       description: str, classification_name: str, identifier: str = None, is_own_anchor: bool = False,
                       project_status: str = None, project_phase: str = None, project_health: str = None,
                       start_date: str = None, planned_end_date: str = None, server_name: str = None) -> str:
        """ Create Project: https://egeria-project.org/concepts/project

            Parameters
            ----------
            classification_name: str
                Type of project to create; "PersonalProject", "Campaign", etc. If not provided, the project will not
                have a project classification.
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element. Set to null if no
                anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            identifier: str
                A project identifier.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should be classified as its own anchor or not.
            project_status: str, optional
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.

            Returns
            -------
            str - the guid of the created project

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_project(anchor_guid, parent_guid,
                                                                  parent_relationship_type_name, parent_at_end1,
                                                                  display_name, description,
                                                                  classification_name, identifier, is_own_anchor,
                                                                  project_status, project_phase, project_health,
                                                                  start_date, planned_end_date, server_name))
        return resp

    async def _async_create_project_task(self, project_guid: str, display_name: str, identifier: str = None,
                                         description: str = None, project_status: str = None, project_phase: str = None,
                                         project_health: str = None, start_date: str = None,
                                         planned_end_date: str = None, server_name: str = None) -> str:
        """ Create a new project with the Task classification and link it to a project. Async version.

            Parameters
            ----------
            project_guid: str
                The unique identifier of the project to create the task for  (the parent).
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            identifier: str
                A project identifier.
            description: str
                A description of the collection.
            project_status: str, optional, defaults to "OTHER"
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.
            Returns
            -------
            str - the guid of the created project task

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

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/"
               f"{project_guid}/task")

        body = {
            "class": "ProjectProperties",
            "qualifiedName": f"task-{display_name}-{time.asctime()}",
            "identifier": identifier,
            "name": display_name,
            "description": description,
            "projectStatus": project_status,
            "projectPhase": project_phase,
            "projectHealth": project_health,
            "startDate": start_date,
            "plannedEndDate": planned_end_date
        }
        body_s = body_slimmer(body)
        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("guid", "No GUID Returned")

    def create_project_task(self, project_guid: str, display_name: str, identifier: str = None,
                            description: str = None, project_status: str = None, project_phase: str = None,
                            project_health: str = None,
                            start_date: str = None, planned_end_date: str = None, server_name: str = None) -> str:
        """ Create a new project with the Task classification and link it to a project.

            Parameters
            ----------
            project_guid: str
                The unique identifier of the project to create the task for.The parent.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            identifier: str
                A project identifier.
            description: str
                A description of the collection.
            project_status: str, optional, defaults to "OTHER"
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.
            Returns
            -------
            str - the guid of the created project task

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_project_task(project_guid, display_name,
                                                                       identifier, description, project_status,
                                                                       project_phase, project_health, start_date,
                                                                       planned_end_date,
                                                                       server_name))
        return resp

    async def _async_create_project_from_template(self, body: dict, server_name: str = None) -> str:
        """ Create a new metadata element to represent a project using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new project.
            Async version.

            Parameters
            ----------

            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance
                 is used.

            Returns
            -------
            str - the guid of the created project.

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            JSON Structure looks like:
            {
              "class": "TemplateRequestBody",
              "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor": false,
              "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName": "open metadata type name",
              "parentAtEnd1": true,
              "templateGUID": "template GUID",
              "replacementProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "propertyName" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                    "primitiveValue" : "value of property"
                  }
                }
              },
              "placeholderPropertyValues" : {
                "placeholderProperty1Name" : "property1Value",
                "placeholderProperty2Name" : "property2Value"
              }
            }


    """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/from-template"
        body_s = body_slimmer(body)
        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("guid", "No GUID Returned")

    def create_project_from_template(self, body: dict, server_name: str = None) -> str:
        """ Create a new metadata element to represent a project using an existing metadata element as a template.
            The template defines additional classifications and relationships that should be added to the new project.

            Parameters
            ----------

            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance
                 is used.

            Returns
            -------
            str - the guid of the created project.

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            JSON Structure looks like:
            {
              "class": "TemplateRequestBody",
              "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor": false,
              "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName": "open metadata type name",
              "parentAtEnd1": true,
              "templateGUID": "template GUID",
              "replacementProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "propertyName" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                    "primitiveValue" : "value of property"
                  }
                }
              },
              "placeholderPropertyValues" : {
                "placeholderProperty1Name" : "property1Value",
                "placeholderProperty2Name" : "property2Value"
              }
            }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_project_from_template(body, server_name))
        return resp

    async def _async_update_project(self, project_guid: str, qualified_name: str = None, identifier: str = None,
                                    display_name: str = None, description: str = None,
                                    project_status: str = None, project_phase: str = None, project_health: str = None,
                                    start_date: str = None, planned_end_date: str = None,
                                    replace_all_props: bool = False, server_name: str = None) -> None:
        """ Update the properties of a project. Async Version.

            Parameters
            ----------
            project_guid: str
                Unique identifier for the project.
            qualified_name: str, optional, defaults to None
                The unique identifier of the project.
            identifier: str
                A project identifier.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            project_status: str, optional
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            replace_all_props: bool, optional, defaults to False
                If True, then all the properties of the project will be replaced with the specified properties.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.
            Returns
            -------
            str - the guid of the created project task

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
        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}/"
               f"update?replaceAllProperties={replace_all_props_s}")

        body = {
            "class": "ProjectProperties",
            "qualifiedName": qualified_name,
            "identifier": identifier,
            "name": display_name,
            "description": description,
            "projectStatus": project_status,
            "projectPhase": project_phase,
            "projectHealth": project_health,
            "startDate": start_date,
            "plannedEndDate": planned_end_date
        }
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        return

    def update_project(self, project_guid: str, qualified_name: str = None, identifier: str = None,
                       display_name: str = None, description: str = None, project_status: str = None,
                       project_phase: str = None, project_health: str = None, start_date: str = None,
                       planned_end_date: str = None, replace_all_props: bool = False, server_name: str = None) -> None:
        """ Update the properties of a project.

            Parameters
            ----------
            project_guid: str
                Unique identifier for the project.
            qualified_name: str, optional, defaults to None
                The unique identifier of the project.
            identifier: str
                A project identifier.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            project_status: str, optional
                The project status
            project_phase: str, optional
                Project phase as defined in valid values
            project_health: str, optional
                Project health as defined in valid values
            start_date: str, optional, defaults to None
                Start date of the project in ISO 8601 string format.
            planned_end_date: str, optional, defaults to None
                Planned completion date in ISO 8601 string format.
            replace_all_props: bool, optional, defaults to False
                If True, then all the properties of the project will be replaced with the specified properties.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.
            Returns
            -------
            str - the guid of the created project task

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_project(project_guid, qualified_name, identifier,
                                                           display_name, description, project_status,
                                                           project_phase, project_health, start_date,
                                                           planned_end_date,
                                                           replace_all_props, server_name))
        return

    async def _async_delete_project(self, project_guid: str, server_name: str = None) -> None:
        """ Delete a project.  It is detected from all parent elements. Async version

            Parameters
            ----------
            project_guid: str
                The guid of the project to update.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance
                 is used.

            Returns
            -------
            Nothing

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

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/"
               f"{project_guid}/delete")

        body = {
            "class": "NullRequestBody"
        }

        await self._async_make_request("POST", url, body)
        return

    def delete_project(self, project_guid: str, server_name: str = None) -> None:
        """ Delete a project.  It is detected from all parent elements.

            Parameters
            ----------
            project_guid: str
                The guid of the collection to update.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance
                 is used.

            Returns
            -------
            Nothing

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_project(project_guid, server_name))
        return

    async def _async_add_to_project_team(self, project_guid: str, actor_guid: str, team_role: str = None,
                                         effective_from: str = None, effective_to: str = None,
                                         server_name: str = None) -> None:
        """ Add an actor to a project. The request body is optional.  If supplied, it contains the name of the role that
            the actor plays in the project. Async version.

            Parameters
            ----------
            project_guid: str
                identity of the project to update.
            actor_guid: str
                identity of the actor to add.
            team_role: str, optional, defaults to None
                Name of the role the actor plays in the project.
            effective_from: str, optional, defaults to None
                Date at which the actor becomes active in the project. Date format is ISO 8601 string format.
            effective_to: str, optional, defaults to None
                Date at which the actor is no longer active in the project. Date format is ISO 8601 string format.
            server_name : str, optional
                The name of the server to use.
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

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}/"
               f"members/{actor_guid}/attach")
        body = {
            "class": "ProjectTeamProperties",
            "teamRole": team_role,
            "effectiveFrom": effective_from,
            "effectiveTo": effective_to
        }
        body_s = body_slimmer(body)
        if body_s is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_s)
        return

    def add_to_project_team(self, project_guid: str, actor_guid: str, team_role: str = None,
                            effective_from: str = None, effective_to: str = None,
                            server_name: str = None) -> None:
        """ Add an actor to a project. The request body is optional.  If supplied, it contains the name of the role that
            the actor plays in the project.

            Parameters
            ----------
            project_guid: str
                identity of the project to update.
            actor_guid: str
                identity of the actor to add.
            team_role: str, optional, defaults to None
                Name of the role the actor plays in the project.
            effective_from: str, optional, defaults to None
                Date at which the actor becomes active in the project. Date format is ISO 8601 string format.
            effective_to: str, optional, defaults to None
                Date at which the actor is no longer active in the project. Date format is ISO 8601 string format.
            server_name : str, optional
                The name of the server to use.
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

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_to_project_team(project_guid, actor_guid,
                                                                team_role, effective_from,
                                                                effective_to, server_name))
        return

    async def _async_remove_from_project_team(self, project_guid: str, actor_guid: str,
                                              server_name: str = None) -> None:
        """ Remove an actor from a project. Async version.

            Parameters
            ----------
            project_guid: str
                identity of the project to remove members from.
            actor_guid: str
                identity of the actor to remove.
            server_name : str, optional
                The name of the server to use.
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

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}/"
               f"members/{actor_guid}/detach")

        body = {
            "class": "NullRequestBody"
        }
        await self._async_make_request("POST", url, body)
        return

    def remove_from_project_team(self, project_guid: str, actor_guid: str,
                                 server_name: str = None) -> None:
        """ Remove an actor from a project.

            Parameters
            ----------
            project_guid: str
                identity of the project.
            actor_guid: str
                identity of the actor to remove.
            server_name : str, optional
                The name of the server to use.
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

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_from_project_team(project_guid, actor_guid,
                                                                     server_name))
        return

    async def _async_setup_project_management_role(self, project_guid: str, project_role_guid: str,
                                                   server_name: str = None) -> None:
        """ Create a ProjectManagement relationship between a project and a person role to show that anyone appointed to
            the role is a member of the project. Async version.

            Parameters
            ----------
            project_guid: str
                identity of the project.
            project_role_guid: str
                guid of the role to assign to the project.
            server_name : str, optional
                The name of the server to use.
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

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}/"
               f"project-management-roles/{project_role_guid}/attach")

        body = {
            "class": "NullRequestBody"
        }
        await self._async_make_request("POST", url, body)
        return

    def setup_project_management_role(self, project_guid: str, project_role_guid: str,
                                      server_name: str = None) -> None:
        """ Create a ProjectManagement relationship between a project and a person role to show that anyone appointed to
        the role is a member of the project. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.
        server_name : str, optional
            The name of the server to use.
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

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_setup_project_management_role(project_guid, project_role_guid,
                                                                          server_name))
        return

    async def _async_clear_project_management_role(self, project_guid: str, project_role_guid: str,
                                                   server_name: str = None) -> None:
        """ Remove a ProjectManagement relationship between a project and a person role. Async version.

            Parameters
            ----------
            project_guid: str
                identity of the project.
            project_role_guid: str
                guid of the role to assign to the project.
            server_name : str, optional
                The name of the server to use.
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

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/project-manager/projects/{project_guid}/"
               f"project-management-roles/{project_role_guid}/detach")

        body = {
            "class": "NullRequestBody"
        }
        await self._async_make_request("POST", url, body)
        return

    def clear_project_management_role(self, project_guid: str, project_role_guid: str,
                                      server_name: str = None) -> None:
        """ Clear a ProjectManagement relationship between a project and a person role.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.
        server_name : str, optional
            The name of the server to use.
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

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_clear_project_management_role(project_guid, project_role_guid,
                                                                          server_name))
        return

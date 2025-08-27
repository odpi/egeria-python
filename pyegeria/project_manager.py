"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain and explore projects.
    https://egeria-project.org/concepts/project

"""

import asyncio

from pyegeria._client_new import Client2
from pyegeria.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody)
from pyegeria.utils import body_slimmer, dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND

PROJECT_TYPES = ["Project", "Campaign", "StudyProject", "Task", "PersonalProject"]

class ProjectManager(Client2):
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
            view_server: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            token: str = None,
            ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.project_command_base: str = (
            f"/api/open-metadata/project-manager/projects"
        )
        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)


    def _generate_project_output(self):
        pass
    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #
    async def _async_get_linked_projects(
            self,
            parent_guid: str,
            project_status: str = None,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked projects from.
        project_status: str, optional
            Optionally, filter results by project status.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

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

        if page_size is None:
            page_size = self.page_size

        body = {
            "filter": project_status,
            "effectiveTime": effective_time,
            }
        body_s = body_slimmer(body)
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"metadata-elements/{parent_guid}/projects?startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No linked projects found")

    def get_linked_projects(
            self,
            parent_guid: str,
            project_status: str = None,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status.

        Parameters
        ----------
        parent_guid: str
             The identity of the parent to find linked projects from
        project_status: str, optional
            Optionally, filter results by project status.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

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
        resp = loop.run_until_complete(
            self._async_get_linked_projects(
                parent_guid,
                project_status,
                effective_time,
                start_from,
                page_size,
                )
            )
        return resp

    async def _async_get_classified_projects(
            self,
            project_classification: str,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign or Task. There is also GlossaryProject and GovernanceProject. Async version.

        Parameters
        ----------
        project_classification: str
            The project classification to search for.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

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

        if page_size is None:
            page_size = self.page_size

        body = {
            "filter": project_classification,
            "effectiveTime": effective_time,
            }
        body_s = body_slimmer(body)
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/by-classifications?startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json()

    def get_classified_projects(
            self,
            project_classification: str,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign or Task. There is also GlossaryProject and GovernanceProject.

        Parameters
        ----------
        project_classification: str
            The project classification to search for.
        effective_time: str, optional
            Time at which to query for projects. Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

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
        resp = loop.run_until_complete(
            self._async_get_classified_projects(
                project_classification,
                effective_time,
                start_from,
                page_size,
                )
            )
        return resp

    async def _async_get_project_team(
            self,
            project_guid: str,
            team_role: str = None,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of actors that are linked off of the project. This includes the project managers.
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

        if page_size is None:
            page_size = self.page_size

        body = {effective_time: effective_time, "filter": team_role}
        body_s = body_slimmer(body)
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"{project_guid}/team?startFrom={start_from}&pageSize={page_size}"
        )

        resp = await self._async_make_request("POST", url, body_s)

        result = resp.json().get("elements", NO_ELEMENTS_FOUND)
        return result

    def get_project_team(
            self,
            project_guid: str,
            team_role: str = None,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = None,
            ) -> list | str:
        """Returns the list of actors that are linked off of the project. This includes the project managers.
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
        resp = loop.run_until_complete(
            self._async_get_project_team(
                project_guid,
                team_role,
                effective_time,
                start_from,
                page_size,
                )
            )
        return resp

    @dynamic_catch
    async def _async_find_projects(
            self,
            search_string: str, classification_names: list[str] = None, metadata_element_types: list[str] = None,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,
            body: dict | SearchStringRequestBody = None
            ) -> list | str:
        """Returns the list of projects matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
            Async version.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.

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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"by-search-string"
        )

        response = await self._async_find_request(url, _type="Project",
                                                  _gen_output=self._generate_project_output,
                                                  search_string=search_string,
                                                  classification_names=classification_names,
                                                  metadata_element_types=metadata_element_types,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response

    @dynamic_catch
    def find_projects(
            self,
            search_string: str, classification_names: list[str] = None, metadata_element_types: list[str] = None,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,
            body: dict | SearchStringRequestBody = None
            ) -> list | str:

        """Returns the list of projects matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching projects. If the search string is '*' then all projects returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.

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
        resp = loop.run_until_complete(
            self._async_find_projects(
                search_string,
                classification_names,
                metadata_element_types,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                output_format_set,
                body,
                )
            )

        return resp

    @dynamic_catch
    async def _async_get_projects_by_name(
            self,  filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
            url = f"{self.project_command_base}/by-name"

            response = await self._async_get_name_request(url, _type="Projects",
                                                  _gen_output=self._generate_projects_output,
                                                  filter_string=filter_string,
                                                  classification_names=classification_names,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

            return response

    @dynamic_catch
    def get_projects_by_name(
            self, filter_string: str = None, classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None) -> list | str:

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_projects_by_name(
                filter_string,
                classification_names,
                body,
                start_from,
                page_size,
                output_format,
                output_format_set,
                )
            )
        return resp

    @dynamic_catch
    async def _async_get_project_by_guid(self, project_guid: str, element_type: str = None,
                                            body: dict | GetRequestBody = None,
                                            output_format: str = 'JSON',
                                            output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific project. Async version.

            Parameters
            ----------
            project_guid: str,
                unique identifier of the collection.
            element_type: str, default = None, optional
                type of collection - Collection, DataSpec, Agreement, etc.
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            ----
            Body sample:
            {
              "class": "GetRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
               f"{project_guid}")
        type = element_type if element_type else "Collection"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_collection_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_project_by_guid(self, project_guid: str, element_type: str = None,
                                            body: dict | GetRequestBody = None,
                                            output_format: str = 'JSON',
                                            output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific project.

            Parameters
            ----------
            project_guid: str,
                unique identifier of the collection.
            element_type: str, default = None, optional
                type of collection - Collection, DataSpec, Agreement, etc.
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            ----
            Body sample:
            {
              "class": "GetRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
            """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_project_by_guid(project_guid, element_type, body, output_format, output_format_set )
            )

        return resp

    @dynamic_catch
    async def _async_get_project_graph(
            self,
            project_guid: str,
            element_type: str = None,
            body: dict | GetRequestBody = None,
            output_format: str = 'JSON',
            output_format_set: str | dict = None,
            ) -> dict | str:
        """Return the mermaid graph of a specific project. Async version.

        Parameters
        ----------
        project_guid: str,
            unique identifier of the project.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
         str

            A mermaid markdown string representing the graph of the project.
        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/pr"
               f"ojects/{project_guid}/graph")

        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_project_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_project_graph(
            self,
            project_guid: str,
            element_type: str = None,
            body: dict | GetRequestBody = None,
            output_format: str = 'JSON',
            output_format_set: str | dict = None,
            ) -> dict | str:
        """Return the mermaid graph of a specific project. Async version.

        Parameters
        ----------
        project_guid: str,
            unique identifier of the project.
        body: dict | GetRequestBody, optional, default = None
            full request body.

        Returns
        -------
         str

            A mermaid markdown string representing the graph of the project.
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
        resp = loop.run_until_complete(
            self._async_get_project_graph(project_guid, element_type, body, output_format, output_format_set)
            )

        return resp

    #
    #   Create project methods
    #
    @dynamic_catch
    async def _async_create_project(
            self,
            body: dict | NewElementRequestBody,
            ) -> str:
        """Create project: https://egeria-project.org/concepts/project Async version.

        Parameters
        ----------.
        body: dict
            A dict representing the details of the project to create. To create different kinds of projects,
            set the initial_classifications in the body to be, for instance, "PersonalProject" or "Campaign".


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
          "class": "NewElementRequestBody",
          "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor" : False,
          "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName" : "open metadata type name",
          "parentAtEnd1": True,
          "initialClassifications" : {
                "Folder" : {
                  "class": "FolderProperties"
                }
              },
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


        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects"

        return await self._async_create_element_body_request(body, ["ProjectProperties"], body)

    @dynamic_catch
    def create_project(
            self,
            body: dict | NewElementRequestBody,
            ) -> str:
        """Create project: https://egeria-project.org/concepts/project

        Parameters
        ----------.
        body: dict
            A dict representing the details of the project to create.

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
        resp = loop.run_until_complete(
            self._async_create_project(body)
            )
        return resp

    @dynamic_catch
    async def _async_create_project_from_template(
            self,
            body: dict | TemplateRequestBody,
            ) -> str:
        """Create a new metadata element to represent a project using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new project.
        Async version.

        Parameters
        ----------

        body: dict
            A dict representing the details of the collection to create.


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

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/from-template"
        return await self._async_create_element_from_template(url, body)

    @dynamic_catch
    def create_project_from_template(
            self,
            body: dict,
            ) -> str:
        """Create a new metadata element to represent a project using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new project.

        Parameters
        ----------

        body: dict
            A dict representing the details of the collection to create.


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
        resp = loop.run_until_complete(self._async_create_project_from_template(body))
        return resp

    #
    #
    #

    async def _async_update_project(
            self,
            project_guid: str,
            qualified_name: str = None,
            identifier: str = None,
            display_name: str = None,
            description: str = None,
            project_status: str = None,
            project_phase: str = None,
            project_health: str = None,
            start_date: str = None,
            planned_end_date: str = None,
            replace_all_props: bool = False,
            ) -> None:
        """Update the properties of a project. Async Version.

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

        replace_all_props_s = str(replace_all_props).lower()
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"update?replaceAllProperties={replace_all_props_s}"
        )

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
            "plannedEndDate": planned_end_date,
            }
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        return

    def update_project(
            self,
            project_guid: str,
            qualified_name: str = None,
            identifier: str = None,
            display_name: str = None,
            description: str = None,
            project_status: str = None,
            project_phase: str = None,
            project_health: str = None,
            start_date: str = None,
            planned_end_date: str = None,
            replace_all_props: bool = False,
            ) -> None:
        """Update the properties of a project.

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
        loop.run_until_complete(
            self._async_update_project(
                project_guid,
                qualified_name,
                identifier,
                display_name,
                description,
                project_status,
                project_phase,
                project_health,
                start_date,
                planned_end_date,
                replace_all_props,
                )
            )
        return

    async def _async_delete_project(
            self,
            project_guid: str, cascade: bool = False
            ) -> None:
        """Delete a project.  It is detected from all parent elements. Async version

        Parameters
        ----------
        project_guid: str
            The guid of the project to update.
        cascade: bool, optional, defaults to False
            If true, then all anchored elements will be deleted.

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
        cascade_s = str(cascade).lower()
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"{project_guid}/delete?cascadedDelete={cascade_s}"
        )

        body = {"class": "NullRequestBody"}

        await self._async_make_request("POST", url, body)
        return

    def delete_project(
            self,
            project_guid: str, cascade: bool = False
            ) -> None:
        """Delete a project.  It is detected from all parent elements.

        Parameters
        ----------
        project_guid: str
            The guid of the collection to update.
        cascade: bool, optional, defaults to False
            If true, then all anchored elements will be deleted.


        cascade: bool, optional, defaults to False
            If true, then all anchored elements will be deleted.
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
        loop.run_until_complete(self._async_delete_project(project_guid, cascade))
        return

    async def _async_add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            team_role: str = None,
            effective_from: str = None,
            effective_to: str = None,
            ) -> None:
        """Add an actor to a project. The request body is optional.  If supplied, it contains the name of the role that
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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"members/{actor_guid}/attach"
        )
        body = {
            "class": "ProjectTeamProperties",
            "teamRole": team_role,
            "effectiveFrom": effective_from,
            "effectiveTo": effective_to,
            }
        body_s = body_slimmer(body)
        if body_s is None:
            await self._async_make_request("POST", url)
        else:
            await self._async_make_request("POST", url, body_s)
        return

    def add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            team_role: str = None,
            effective_from: str = None,
            effective_to: str = None,
            ) -> None:
        """Add an actor to a project. The request body is optional.  If supplied, it contains the name of the role that
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
        loop.run_until_complete(
            self._async_add_to_project_team(
                project_guid,
                actor_guid,
                team_role,
                effective_from,
                effective_to,
                )
            )
        return

    async def _async_remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            ) -> None:
        """Remove an actor from a project. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project to remove members from.
        actor_guid: str
            identity of the actor to remove.

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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"members/{actor_guid}/detach"
        )

        body = {"class": "NullRequestBody"}
        await self._async_make_request("POST", url, body)
        return

    def remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            ) -> None:
        """Remove an actor from a project.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        actor_guid: str
            identity of the actor to remove.

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
        loop.run_until_complete(
            self._async_remove_from_project_team(project_guid, actor_guid)
            )
        return

    async def _async_setup_project_management_role(
            self,
            project_guid: str,
            project_role_guid: str,
            ) -> None:
        """Create a ProjectManagement relationship between a project and a person role to show that anyone appointed to
        the role is a member of the project. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.


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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"project-management-roles/{project_role_guid}/attach"
        )

        body = {"class": "NullRequestBody"}
        await self._async_make_request("POST", url, body)
        return

    def setup_project_management_role(
            self,
            project_guid: str,
            project_role_guid: str,
            ) -> None:
        """Create a ProjectManagement relationship between a project and a person role to show that anyone appointed to
        the role is a member of the project. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.


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
        loop.run_until_complete(
            self._async_setup_project_management_role(project_guid, project_role_guid)
            )
        return

    async def _async_clear_project_management_role(
            self,
            project_guid: str,
            project_role_guid: str,
            ) -> None:
        """Remove a ProjectManagement relationship between a project and a person role. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.


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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"project-management-roles/{project_role_guid}/detach"
        )

        body = {"class": "NullRequestBody"}
        await self._async_make_request("POST", url, body)
        return

    def clear_project_management_role(
            self,
            project_guid: str,
            project_role_guid: str,
            ) -> None:
        """Clear a ProjectManagement relationship between a project and a person role.

        Parameters
        ----------
        project_guid: str
            identity of the project.
        project_role_guid: str
            guid of the role to assign to the project.


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
        loop.run_until_complete(
            self._async_clear_project_management_role(project_guid, project_role_guid)
            )
        return


if __name__ == "__main__":
    print("Main-Project Manager")

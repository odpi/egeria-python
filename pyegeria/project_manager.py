"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain and explore projects.
    https://egeria-project.org/concepts/project

"""

import asyncio

from loguru import logger

from pyegeria._client_new import Client2
from pyegeria.load_config import get_app_config
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, UpdateElementRequestBody, DeleteRequestBody,
                             NewRelationshipRequestBody)
from pyegeria.utils import body_slimmer, dynamic_catch
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties,
                                       populate_columns_from_properties,
                                       get_required_relationships)

app_settings = get_app_config()
EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND

PROJECT_TYPES = ["Project", "Campaign", "StudyProject", "Task", "PersonalProject"]
PROJECT_PROPERTIES_LIST = ["ProjectProperties", "CampaignProperties", "StudyProjectProperties", "TaskProperties",
                           "PersonalProjectProperties"]

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


    def _extract_project_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Populate columns_struct values for a Project element using the standardized approach from collection_manager.
        - Populate from element.properties
        - Overlay header-derived values
        - Derive classifications list
        - Populate relationship-based columns generically
        - Include mermaid graph if requested
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("columns", [])

        # Header-derived values
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')

        # Classifications
        cl_names = []
        for c in element.get('elementHeader', {}).get('classifications', []) or []:
            nm = c.get('classificationName')
            if nm:
                cl_names.append(nm)
        if cl_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = ", ".join(cl_names)
                    break

        # Relationships
        col_data = get_required_relationships(element, col_data)

        # Mermaid
        mermaid_val = element.get('mermaidGraph', "") or ""
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = mermaid_val
                break

        return col_data

    def _generate_project_output(self, elements: dict | list[dict], filter: str = None,
                                 element_type_name: str | None = None,
                                 output_format: str = 'DICT',
                                 output_format_set: str | dict = None) -> str | list[dict]:
        """
        Generate output for projects using selectable output format sets.
        """
        entity_type = element_type_name or 'Project'

        # Resolve output formats
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
        elif element_type_name:
            output_formats = select_output_format_set(element_type_name, output_format)
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_project_properties,
            None,
            output_formats,
        )
    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #
    async def _async_get_linked_projects(
            self,
            parent_guid: str,
            filter_string: str = None,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = None,
            output_format: str = "json", output_format_set: str | dict = None,
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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"metadata-elements/{parent_guid}/projects"
        )

        response = await self._async_get_name_request(url, _type="Project",
                                                      _gen_output=self._generate_project_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    def get_linked_projects(
            self,
            parent_guid: str,
            filter_string: str = None,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = None,
            output_format: str = "json", output_format_set: str | dict = None,
            ) -> list | str:
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_linked_projects(parent_guid, filter_string, classification_names,
                                            body, start_from,page_size,output_format, output_format_set)
            )

        return resp






    async def _async_get_classified_projects(
            self,
            project_classification: str,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,

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


        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/by-classifications"
        )
        response = await self._async_get_name_request(url, _type="Project",
                                                      _gen_output=self._generate_project_output,
                                                      filter_string=project_classification,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response


    def get_classified_projects(
            self,
            project_classification: str,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = "json", output_format_set: str | dict = None,

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
                classification_names,
                body,   start_from,
                page_size,
                output_format,
                output_format_set,
                )
            )
        return resp

    async def _async_get_project_team(
            self,
            project_guid: str,
            team_role: str = None,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = None,
            output_format: str = "json", output_format_set: str | dict = None,
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


        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"{project_guid}/team"
        )
        response = await self._async_get_name_request(url, _type="Project",
                                                      _gen_output=self._generate_project_output,
                                                      filter_string=team_role,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    def get_project_team(
            self,
            project_guid: str,
            team_role: str = None,
            classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = None,
            output_format: str = "json", output_format_set: str | dict = None,
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
                classification_names,
                body,   start_from,
                page_size,
                output_format,
                output_format_set,
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

            response = await self._async_get_name_request(url, _type="Project",
                                                  _gen_output=self._generate_project_output,
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
            project_guid: str
                Unique identifier of the project to retrieve.
            element_type: str, optional, default = None
                Metadata element type name to guide output formatting (defaults to "Project").
            body: dict | GetRequestBody, optional, default = None
                Full request body for advanced options (effective time, lineage, etc.).
            output_format: str, optional, default = "JSON"
                One of "DICT", "LIST", "MD", "FORM", "REPORT", "MERMAID" or "JSON".
            output_format_set: str | dict, optional, default = None
                The desired output columns/fields definition or a label referring to a predefined set.

            Returns
            -------
            dict | str
                JSON dict representing the specified project when output_format == "JSON";
                otherwise a formatted string (or list) according to output_format.

            Raises
            ------
            InvalidParameterException
                If the client passes incorrect parameters on the request (bad URLs/values)
            PropertyServerException
                Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
                The requesting user is not authorized to issue this request

            Notes
            -----
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
        type = element_type if element_type else "Project"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_project_output,
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
            project_guid: str
                Unique identifier of the project to retrieve.
            element_type: str, optional, default = None
                Metadata element type name to guide output formatting (defaults to "Project").
            body: dict | GetRequestBody, optional, default = None
                Full request body for advanced options (effective time, lineage, etc.).
            output_format: str, optional, default = "JSON"
                One of "DICT", "LIST", "MD", "FORM", "REPORT", "MERMAID" or "JSON".
            output_format_set: str | dict, optional, default = None
                The desired output columns/fields definition or a label referring to a predefined set.

            Returns
            -------
            dict | str
                JSON dict representing the specified project when output_format == "JSON";
                otherwise a formatted string (or list) according to output_format.

            Raises
            ------
            InvalidParameterException
                If the client passes incorrect parameters on the request (bad URLs/values)
            PropertyServerException
                Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
                The requesting user is not authorized to issue this request

            Notes
            -----
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
        """Return the mermaid graph or formatted details of a specific project. Async version.

        Parameters
        ----------
        project_guid: str
            Unique identifier of the project.
        element_type: str, optional, default = None
            Metadata element type name to guide output formatting (defaults to "Project").
        body: dict | GetRequestBody, optional, default = None
            Full request body for advanced options (effective time, lineage, etc.).
        output_format: str, optional, default = "JSON"
            One of "DICT", "LIST", "MD", "FORM", "REPORT", "MERMAID" or "JSON".
        output_format_set: str | dict, optional, default = None
            The desired output columns/fields definition or a label referring to a predefined set.

        Returns
        -------
        dict | str
            JSON dict when output_format == "JSON"; otherwise a formatted string according to output_format
            (for example, a Mermaid markdown string when output_format == "MERMAID").

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request (bad URLs/values)
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
            The requesting user is not authorized to issue this request

        """


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/pr"
               f"ojects/{project_guid}/graph")

        response = await self._async_get_guid_request(url, _type=element_type or 'Project',
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
        """Return the mermaid graph or formatted details of a specific project.

        Parameters
        ----------
        project_guid: str
            Unique identifier of the project.
        element_type: str, optional, default = None
            Metadata element type name to guide output formatting (defaults to "Project").
        body: dict | GetRequestBody, optional, default = None
            Full request body for advanced options (effective time, lineage, etc.).
        output_format: str, optional, default = "JSON"
            One of "DICT", "LIST", "MD", "FORM", "REPORT", "MERMAID" or "JSON".
        output_format_set: str | dict, optional, default = None
            The desired output columns/fields definition or a label referring to a predefined set.

        Returns
        -------
        dict | str
            JSON dict when output_format == "JSON"; otherwise a formatted string according to output_format
            (for example, a Mermaid markdown string when output_format == "MERMAID").

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request (bad URLs/values)
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
            The requesting user is not authorized to issue this request

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
        ----------
        body: dict | NewElementRequestBody
            A dict or NewElementRequestBody representing the details of the project to create.

        Returns
        -------
        str
            The GUID of the created project.

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
            body: dict | UpdateElementRequestBody,
            ) -> None:
        """Update the properties of a project. Async version.

        Parameters
        ----------
        project_guid: str
            Unique identifier of the project to update.
        body: dict | UpdateElementRequestBody
            The update payload specifying properties to change.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/update"
        )

        await self._async_update_element_body_request(url, PROJECT_PROPERTIES_LIST, body)

    def update_project(
            self,
            project_guid: str,
            body: dict | UpdateElementRequestBody            ) -> None:
        """Update the properties of a project.

        Parameters
        ----------
        project_guid: str
            Unique identifier of the project to update.
        body: dict | UpdateElementRequestBody
            The update payload specifying properties to change.

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
            self._async_update_project(
                project_guid,
                body
                )
            )
        return

    async def _async_delete_project(
            self,
            project_guid: str, cascade_delete: bool = False,
            body: dict | DeleteRequestBody = None
            ) -> None:
        """Delete a project. Async version.

        Parameters
        ----------
        project_guid: str
            The GUID of the project to delete.
        cascade_delete: bool, optional, default = False
            If True, then all anchored elements will be deleted.
        body: dict | DeleteRequestBody, optional, default = None
            Request body for additional options.

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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"{project_guid}/delete"
        )
        await self._async_delete_request(url, body, cascade_delete)
        logger.info(f"Deleted project {project_guid} with cascade {cascade_delete}")

    def delete_project(
            self,
            project_guid: str, cascade_delete: bool = False,
            body: dict |DeleteRequestBody  = None
            ) -> None:
        """Delete a project.

        Parameters
        ----------
        project_guid: str
            The GUID of the project to delete.
        cascade_delete: bool, optional, default = False
            If True, then all anchored elements will be deleted.
        body: dict | DeleteRequestBody, optional, default = None
            Request body for additional options.

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
        loop.run_until_complete(self._async_delete_project(project_guid, cascade_delete, body))


    async def _async_add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Add an actor to a project. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the project to update.
        actor_guid: str
            Identity of the actor to add.
        body: dict | NewRelationshipRequestBody, optional, default = None
            Optional relationship properties (for example, role name, effective times).

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
        await self._async_new_relationship_request(url, "AssignmentScopeProperties", body)
        logger.info(f"Added actor {actor_guid} to project {project_guid}")

    def add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Add an actor to a project.

        Parameters
        ----------
        project_guid: str
            Identity of the project to update.
        actor_guid: str
            Identity of the actor to add.
        body: dict | NewRelationshipRequestBody, optional, default = None
            Optional relationship properties (for example, role name, effective times).

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
                body
                )
            )


    async def _async_remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False,
            ) -> None:
        """Remove an actor from a project. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the project to remove members from.
        actor_guid: str
            Identity of the actor to remove.
        body: dict | DeleteRequestBody, optional, default = None
            Optional relationship properties.
        cascade_delete: bool, optional, default = False
            If True, deletes related anchored elements as applicable.

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
        await self._async_delete_request(url, body, cascade_delete)
        logger.info(f"Removed actor {actor_guid} from project {project_guid}")


    def remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False,
            ) -> None:
        """Remove an actor from a project.

        Parameters
        ----------
        project_guid: str
            Identity of the project.
        actor_guid: str
            Identity of the actor to remove.
        body: dict | DeleteRequestBody, optional, default = None
            Optional relationship properties.
        cascade_delete: bool, optional, default = False
            If True, deletes related anchored elements as applicable.

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
            self._async_remove_from_project_team(project_guid, actor_guid, body, cascade_delete)
            )


    async def _async_setup_project_dependency(
            self,
            project_guid: str,
            depends_on_project_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Create a project dependency link from one project to another. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the project that has the dependency.
        depends_on_project_guid: str
            GUID of the project that the first project depends on.


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
            f"project-dependencies/{depends_on_project_guid}/attach"
        )
        await self._async_new_relationship_request(url, "ProjectDependencyProperties", body)
        logger.info(f"Added dependency between project  {project_guid} depending on project {depends_on_project_guid}")


    def setup_project_dependency(
            self,
            project_guid: str,
            depends_on_project_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Create a project dependency link from one project to another.

        Parameters
        ----------
        project_guid: str
            Identity of the project that has the dependency.
        depends_on_project_guid: str
            GUID of the project that the first project depends on.


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
            self._async_setup_project_dependency(   project_guid, depends_on_project_guid, body)
            )
        return

    async def _async_clear_project_dependency(
            self,
            project_guid: str,
            depends_on_project_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False
            ) -> None:
        """Remove a project dependency link between two projects. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the project that previously had the dependency.
        depends_on_project_guid: str
            GUID of the project that was depended on.


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
            f"project-dependencies/{depends_on_project_guid}/detach"
        )
        await self._async_delete_request(url, body, cascade_delete)
        logger.info(f"Removed project dependency between project  {project_guid} and project {depends_on_project_guid}")


    def clear_project_dependency(
            self,
            project_guid: str,
            depends_on_project_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False
            ) -> None:
        """Clear a project dependency link between two projects.

        Parameters
        ----------
        project_guid: str
            Identity of the project that previously had the dependency.
        depends_on_project_guid: str
            GUID of the project that was depended on.


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
            self._async_clear_project_dependency(project_guid, depends_on_project_guid,
                                                 body, cascade_delete)
            )
        return

    async def _async_setup_project_hierarchy(
            self,
            project_guid: str,
            managed_project_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Create a project hierarchy link from a project to a managed (child) project. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the parent (managing) project.
        managed_project_guid: str
            GUID of the managed (child) project.


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
            f"project-hierarchies/{managed_project_guid}/attach"
        )
        await self._async_new_relationship_request(url, "ProjectHierarchyProperties", body)
        logger.info(f"Added hierarchy between project  {project_guid} abd project {managed_project_guid}")


    def setup_project_hierarchy(
            self,
            project_guid: str,
            managed_project_guid: str,
            body: dict | NewRelationshipRequestBody = None,
            ) -> None:
        """Create a project hierarchy link from a project to a managed (child) project.

        Parameters
        ----------
        project_guid: str
            Identity of the parent (managing) project.
        managed_project_guid: str
            GUID of the managed (child) project.


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
            self._async_setup_project_dependency(   project_guid, managed_project_guid, body)
            )
        return

    async def _async_clear_project_hierarchy(
            self,
            project_guid: str,
            managed_project_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False
            ) -> None:
        """Remove a project hierarchy link between two projects. Async version.

        Parameters
        ----------
        project_guid: str
            Identity of the parent (managing) project.
        managed_project_guid: str
            GUID of the managed (child) project.


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
            f"project-hierarchies/{managed_project_guid}/detach"
        )
        await self._async_delete_request(url, body, cascade_delete)
        logger.info(f"Removed project hierarchy link between project  {project_guid} and project {managed_project_guid}")


    def clear_project_hierarchy(
            self,
            project_guid: str,
            managed_project_guid: str,
            body: dict | DeleteRequestBody = None,
            cascade_delete: bool = False
            ) -> None:
        """Clear a project hierarchy link between two projects.

        Parameters
        ----------
        project_guid: str
            Identity of the parent (managing) project.
        managed_project_guid: str
            GUID of the managed (child) project.


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
            self._async_clear_project_hierarchy(project_guid, managed_project_guid,
                                                 body, cascade_delete)
            )
        return


if __name__ == "__main__":
    print("Main-Project Manager")


# Automatically apply @dynamic_catch to all methods of ProjectManager (excluding dunder methods)
try:
    for _name, _attr in list(ProjectManager.__dict__.items()):
        if callable(_attr) and not _name.startswith("__"):
            # Avoid double-wrapping if already decorated
            if not getattr(_attr, "__wrapped__", None):
                setattr(ProjectManager, _name, dynamic_catch(_attr))
except Exception as _e:
    # Be resilient; if anything goes wrong, leave methods as-is
    logger.debug(f"dynamic_catch auto-wrap skipped due to: {_e}")

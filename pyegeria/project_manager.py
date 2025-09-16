"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain and explore projects.
    https://egeria-project.org/concepts/project

"""

import asyncio

from pyegeria._output_formats import select_output_format_set
from pyegeria._client_new import Client2
from pyegeria._output_formats import get_output_format_type_match
from pyegeria.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, DeleteRequestBody, UpdateElementRequestBody,
                             NewRelationshipRequestBody)
from pyegeria.output_formatter import generate_output, populate_columns_from_properties, \
    _extract_referenceable_properties, get_required_relationships, populate_common_columns, overlay_additional_values
from pyegeria.utils import body_slimmer, dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from loguru import logger

PROJECT_TYPES = ["Project", "Campaign", "StudyProject", "Task", "PersonalProject"]


class ProjectManager(Client2):
    """
    Manage Open Metadata Projects via the Project Manager OMVS.

    This client provides asynchronous and synchronous helpers to create, update, search,
    and relate Project elements and their subtypes (Campaign, StudyProject, Task, PersonalProject).

    References
    - Egeria concept: https://egeria-project.org/concepts/project
    - Type lineage: https://egeria-project.org/types/1/0130-Projects

    Parameters
    -----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        Default user identity for calls (can be overridden per call).
    user_pwd : str, optional
        Password for the user_id. If a token is supplied, this may be None.

    Notes
    -----
    - Most high-level list/report methods accept an `output_format` and an optional `output_format_set` and
      delegate rendering to `pyegeria.output_formatter.generate_output` along with shared helpers such as
      `populate_common_columns`.
    - Private extractor methods follow the convention: `_extract_<entity>_properties(element, columns_struct)` and
      must return the same `columns_struct` with per-column `value` fields populated.
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
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects"
        )
        self.url_marker = 'project-manager'
        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _extract_additional_project_properties(self, element: dict, columns_struct: dict)-> dict:


        roles_required = any(column.get('key') == 'project_roles'
                             for column in columns_struct.get('formats', {}).get('columns', []))
        project_props = {}

        if roles_required:
            project_roles = element['elementHeader'].get('projectRoles', [])
            project_roles_list = []
            for project_role in project_roles:
                project_roles_list.append(project_role.get('classificationName', ""))
            project_roles_md = (", \n".join(project_roles_list)).rstrip(',') if project_roles_list else ''
            project_props = {
                'project_roles': project_roles_md,
            }
        return project_props




    def _extract_project_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Common population pipeline
        col_data = populate_common_columns(element, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])
        # Overlay extras (project roles) only where empty
        extra = self._extract_additional_project_properties(element, columns_struct)
        col_data = overlay_additional_values(col_data, extra)
        return col_data


    def _generate_project_output(self, elements: dict | list[dict], search_string: str,
                                 element_type_name: str | None,
                                 output_format: str = 'DICT',
                                 output_format_set: dict | str = None) -> str | list[dict]:
        entity_type = 'Project'
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_project_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #
    @dynamic_catch
    async def _async_get_linked_projects(
            self,
            parent_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = 'JSON',
            output_format_set: str | dict = None,
    ) -> list | str:
        """Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked projects from.
        project_status: str, optional
            Optionally, filter results by project status.

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

        response = await self._async_get_guid_request(url, "Project", self._extract_project_properties,
                                                      body=body,
                                                      output_format=output_format,
                                                      output_format_set=output_format_set)
        return response

    @dynamic_catch
    def get_linked_projects(
            self,
            parent_guid: str,
            body: dict | GetRequestBody = None,
            output_format: str = 'JSON',
            output_format_set: str | dict = None) -> str | dict:

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
                body,
                output_format,
                output_format_set
            )
        )
        return resp

    @dynamic_catch
    async def _async_get_classified_projects(
            self,
            project_classification: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None,
            body: dict | GetRequestBody = None,) -> str | dict:

        """Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign or Task. There is also GlossaryProject and GovernanceProject. Async version.

        Parameters
        ----------
        project_classification: str
            The project classification to search for.
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
        response = await self._async_get_name_request(url, "Project", self._extract_project_properties,
                                                      filter_string = project_classification, start_from=start_from,
                                                      page_size=page_size, body=body,
                                                      output_format=output_format,
                                                      output_format_set=output_format_set)
        return response

    @dynamic_catch
    def get_classified_projects(
            self,
            project_classification: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None,
            body: dict | GetRequestBody = None,
    ) -> str | dict:
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
            self._async_get_classified_projects(project_classification,
                start_from,page_size,

                output_format,
                output_format_set,
                body
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
            self, filter_string: str = None, classification_names: list[str] = None,
            body: dict | FilterRequestBody = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            output_format_set: str | dict = None) -> list | str:
        url = f"{self.project_command_base}/by-name"

        response = await self._async_get_name_request(url, _type="Projects",
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
            self._async_get_project_by_guid(project_guid, element_type, body, output_format, output_format_set)
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

        return await self._async_create_element_body_request(url, ["ProjectProperties"], body)

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

    @dynamic_catch
    async def _async_update_project(
            self,
            project_guid: str,
            body: dict | UpdateElementRequestBody
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

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"update"
        )

        await self._async_update_element_body_request(url, ["ProjectProperties"], body)
        logger.info(f"Updated digital subscription {project_guid}")

    @dynamic_catch
    def update_project(
            self,
            project_guid: str,
            body: dict | UpdateElementRequestBody,
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
            self._async_update_project(project_guid, body))

    @dynamic_catch
    async def _async_delete_project(
            self,
            project_guid: str, cascade: bool = False, body: dict | DeleteRequestBody = None) -> None:
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
            f"{project_guid}/delete"
        )

        await self._async_delete_request(url, body, cascade)
        logger.info(f"Deleted project {project_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_project(
            self,
            project_guid: str, cascade: bool = False, body: dict | DeleteRequestBody = None) -> None:
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
        loop.run_until_complete(self._async_delete_project(project_guid, cascade, body))

    @dynamic_catch
    async def _async_set_project_dependency(self, project_guid: str,
                                            upstream_project_guid: str,
                                            body: dict | NewRelationshipRequestBody = None):
        """ A project depends on an upstream project.
            Request body is optional. Async version.

        Parameters
        ----------
        upstream_project_guid: str
            The guid of the project depended on.
        project_guid: str
            The guid of the dependent project
        body: dict | NewRelationshipRequestBody, optional, default = None
            A dict representing the details of the relationship.

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

        Notes
        -----

        """
        url = (
            f"{self.project_command_base}/{project_guid}/project-dependencies/{upstream_project_guid}/attach"
        )
        await self._async_new_relationship_request(url, "ProjectDependencyProperties", body)
        logger.info(f"Project {project_guid} depends on -> {upstream_project_guid}")

    @dynamic_catch
    def set_project_dependency(self, project_guid: str,
                                            upstream_project_guid: str,
                                            body: dict | NewRelationshipRequestBody = None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional.

            Parameters
            ----------
            upstream_digital_prod_guid: str
                The guid of the first digital product
            downstream_digital_prod_guid: str
                The guid of the downstream digital product
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

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

            Notes
            -----

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_project_dependency(project_guid, upstream_project_guid,
                                               body))

    @dynamic_catch
    async def _async_clear_project_dependency(self, project_guid: str,
                                              upstream_project_guid: str,
                                              body: dict | DeleteRequestBody = None) -> None:
        """ Unlink two dependent projects.  Request body is optional. Async version.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        upstream_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = "{self.project_command_base}/{project_guid}/project-dependencies/{upstream_project_guid}/detach"

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached project {project_guid} from -> {upstream_project_guid}")

    @dynamic_catch
    def clear_project_dependency(self, project_guid: str, upstream_project_guid: str,
                                 body: dict | DeleteRequestBody = None):
        """ Unlink two dependent projects.  Request body is optional.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        upstream_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_project_dependency(project_guid, upstream_project_guid, body))

    @dynamic_catch
    async def _async_set_project_hierarchy(self, project_guid: str,
                                           parent_project_guid: str,
                                           body: dict | NewRelationshipRequestBody = None):
        """ Set a hierarchy relationship between two projects.
            Request body is optional. Async version.


        Parameters
        ----------
        parent_project_guid: str
            The guid of the project depended on.
        project_guid: str
            The guid of the dependent project
        body: dict | NewRelationshipRequestBody, optional, default = None
            A dict representing the details of the relationship.

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

        Notes
        -----

        """
        url = (
            f"{self.project_command_base}/{parent_project_guid}/project-dependencies/{project_guid}/attach"
        )
        await self._async_new_relationship_request(url, ["ProjectHierarchyProperties"], body)
        logger.info(f"Project {project_guid} managed by -> {parent_project_guid}")

    @dynamic_catch
    def set_project_hierarchy(self, project_guid: str,
                              parent_project_guid: str,
                              body: dict | NewRelationshipRequestBody = None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional.

            Parameters
            ----------
            upstream_digital_prod_guid: str
                The guid of the first digital product
            downstream_digital_prod_guid: str
                The guid of the downstream digital product
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

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

            Notes
            -----

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_project_hierarchy(project_guid, parent_project_guid,
                                              body))

    @dynamic_catch
    async def _async_clear_project_hierarchy(self, project_guid: str,
                                             parent_project_guid: str,
                                             body: dict | DeleteRequestBody = None) -> None:
        """ Unlink hierarchy relationship.  Request body is optional. Async version.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        parent_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = "{self.project_command_base}/{parent_project_guid}/project-dependencies/{project_guid}/detach"

        await self._async_delete_request(url, body)
        logger.info(
            f"Detached project {project_guid} from -> {parent_project_guid}")

    @dynamic_catch
    def clear_project_hierarchy(self, project_guid: str, parent_project_guid: str,
                                body: dict | DeleteRequestBody = None):
        """ Unlink two dependent projects.  Request body is optional.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        parent_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_project_hierarchy(project_guid, parent_project_guid, body))

    @dynamic_catch
    async def _async_add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            assignment_type: str = None,
            description: str = None,
            body: dict | NewRelationshipRequestBody = None
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
        if body is None:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "AssignmentScopeProperties",
                    "description": description,
                    "assignmentType": assignment_type,
                }
            }
            body_s = body_slimmer(body)

        await self._async_new_relationship_request(url, ["AssignmentScopeRelationship"], body)
        logger.info(f"Added member {actor_guid} to project {project_guid}")

    @dynamic_catch
    def add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            assignment_type: str = None,
            description: str = None,
            body: dict | NewRelationshipRequestBody = None
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
                assignment_type,
                description,
                body,
            )
        )

    @dynamic_catch
    async def _async_remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | DeleteRequestBody = None
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

        await self._async_delete_request(url, body)
        logger.info(f"Removed member {actor_guid} from project {project_guid}")

    @dynamic_catch
    def remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: dict | DeleteRequestBody = None
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
            self._async_remove_from_project_team(project_guid, actor_guid, body)
        )

    @dynamic_catch
    async def _async_create_task_for_project(
            self,
            project_guid: str,
            body: dict | NewElementRequestBody
    ) -> str:
        """Create a new task for a project.  Async version."""

        url = f"{self.project_command_base}/{project_guid}/task"
        response = await self._async_new_element_request(url, body)
        logger.info(f"Created task for project {project_guid}")
        return response

    @dynamic_catch
    def create_task_for_project(
            self,
            project_guid: str,
            body: dict | NewElementRequestBody
    ) -> str:
        """Create a new task for a project.  """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_create_task_for_project(project_guid, body)
        )
        return resp


if __name__ == "__main__":
    print("Main-Project Manager")

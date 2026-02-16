"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Create, maintain and explore projects.
    https://egeria-project.org/concepts/project

"""

import asyncio
from typing import Any, Optional

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.core._server_client import ServerClient
from pyegeria.view.base_report_formats import get_report_spec_match
from pyegeria.core.config import settings as app_settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody, DeleteElementRequestBody, DeleteRelationshipRequestBody,
                             UpdateElementRequestBody,
                             NewRelationshipRequestBody, NewClassificationRequestBody, DeleteClassificationRequestBody)
from pyegeria.view.output_formatter import generate_output, populate_common_columns, overlay_additional_values, materialize_egeria_summary
from pyegeria.core.utils import body_slimmer, dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
from loguru import logger

PROJECT_TYPES = ["Project", "Campaign", "StudyProject", "Task", "PersonalProject"]


class ProjectManager(ServerClient):
    """
    Client for the Project Manager View Service.

    The Project Manager View Service provides methods to manage projects,
    including project links, classification, and teams.

    Attributes
    ----------
    view_server : str
        The name of the View Server to use.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
            self,
            view_server: str,
            platform_url: str,
            user_id: str,
            user_pwd: Optional[str] = None,
            token: Optional[str] = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.project_command_base: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects"
        )
        self.url_marker = 'project-manager'
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)


    def _extract_project_properties(self, element: dict, columns_struct: dict) -> dict:
        """Extract properties from a project element, materializing header fields generically."""
        # Materialize the element to flatten header properties (like projectRoles)
        flat_element = materialize_egeria_summary(element, columns_struct)

        # Common population pipeline
        col_data = populate_common_columns(flat_element, columns_struct)
        return col_data


    def _generate_project_output(self, elements: dict | list[dict], search_string: str,
                                 element_type_name: str | None,
                                 output_format: str = 'DICT',
                                 report_spec: dict | str = None,
                                 **kwargs) -> str | list[dict]:
        entity_type = 'Project'
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            elif isinstance(report_spec, dict):
                output_formats = get_report_spec_match(report_spec, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_report_spec(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_spec('Default', output_format)
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_project_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
            **kwargs
        )

    #
    #       Retrieving Projects= Information - https://egeria-project.org/concepts/project
    #
    @dynamic_catch
    async def _async_get_linked_projects(
            self,
            parent_guid: str,
            body: Optional[dict | GetRequestBody] = None,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
    ) -> list | str:
        """Returns the list of projects that are linked off of the supplied element. Any relationship will do.
             The request body is optional, but if supplied acts as a filter on project status. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked projects from.
        project_status: str, optional
            Optionally, filter results by project status.
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"metadata-elements/{parent_guid}/projects"
        )

        response = await self._async_get_guid_request(url, "Project", self._generate_project_output,
                                                      body=body,
                                                      output_format=output_format,
                                                      report_spec=report_spec)
        return response

    @dynamic_catch
    def get_linked_projects(
            self,
            parent_guid: str,
            body: Optional[dict | GetRequestBody] = None,
            output_format: str = 'JSON',
            report_spec: str | dict = None) -> str | dict:

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
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
                report_spec
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
            report_spec: str | dict = None,
            body: Optional[dict | GetRequestBody] = None,) -> str | dict:

        """Returns the list of projects with a particular classification. The name of the classification is
            supplied in the request body. Examples of these classifications include StudyProject, PersonalProject,
            Campaign, or Task. There is also GlossaryProject and GovernanceProject. Async version.

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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
                                                      report_spec=report_spec)
        return response

    @dynamic_catch
    def get_classified_projects(
            self,
            project_classification: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
            body: Optional[dict | GetRequestBody] = None,
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_classified_projects(project_classification,
                start_from,page_size,

                output_format,
                report_spec,
                body
            )
        )
        return resp

    @dynamic_catch
    async def _async_add_project_classification(
            self, project_guid: str, body: dict | NewClassificationRequestBody
    )-> None:

        """Classify the project to indicate the approach and style of the project based on its intended outcome. Async version.

        Parameters
        ----------
        project_guid: str
            The project to classify.
        body: dict | NewClassificationRequestBody
            Details of the new classification to add.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Note
        ____
        Sample body:
        {
          "class": "NewClassificationRequestBody",
          "properties": {
            "class": "ProjectClassificationProperties",
            "approach": "Regulated Clinical Trial",
            "managementStyle": "Regulated Project",
            "ResultsUsage": "Business Critical"
          }
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/{project_guid}/classification-properties/classify"
        )
        response = await self._async_new_classification_request(url, ["ProjectClassificationProperties"],
                                                                body=body)
        return response

    @dynamic_catch
    def add_project_classification(
            self,
            project_guid: str,
            body: dict | NewClassificationRequestBody,

    ) -> None:
        """Classify the project to indicate the approach and style of the project based on its intended outcome.

         Parameters
         ----------
         project_guid: str
             The project to classify.
         body: dict | NewClassificationRequestBody
             Details of the new classification to add.

         Returns
         -------
         None

         Raises
         ------
         PyegeriaInvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
         PyegeriaAPIException
           Raised by the server when an issue arises in processing a valid request
         NotAuthorizedException
           The principle specified by the user_id does not have authorization for the requested action

         Note
         ____
         Sample body:
         {
           "class": "NewClassificationRequestBody",
           "properties": {
             "class": "ProjectClassificationProperties",
             "approach": "Regulated Clinical Trial",
             "managementStyle": "Regulated Project",
             "ResultsUsage": "Business Critical"
           }
         }
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_project_classification(project_guid = project_guid,
                                                body=body
                                                )
        )

    @dynamic_catch
    async def _async_clear_project_classification(
            self, project_guid: str, body: dict | DeleteClassificationRequestBody | None = None
    )-> None:

        """Clear the classification the ProjectClassification classification from the project. Async version.

        Parameters
        ----------
        project_guid: str
            The project to declassify.
        body: dict | DeleteClassificationRequestBody | None
            Request details of the classification to remove.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Note
        ____
        Sample body:
        {
          "class": "DeleteClassificationRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/{project_guid}/classification-properties/declassify"
        )
        response = await self._async_new_classification_request(url, ["ProjectClassificationProperties"],
                                                                body=body)
        return response

    @dynamic_catch
    def clear_project_classification(
            self,
            project_guid: str,
            body: dict | DeleteClassificationRequestBody | None = None,

    ) -> None:
        """Clear the classification the ProjectClassification classification from the project.

         Parameters
         ----------
         project_guid: str
             The project to declassify.
         body: dict | DeleteClassificationRequestBody | None
             Request details of the classification to remove.

         Returns
         -------
         None

         Raises
         ------
         PyegeriaInvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
         PyegeriaAPIException
           Raised by the server when an issue arises in processing a valid request
         NotAuthorizedException
           The principle specified by the user_id does not have authorization for the requested action

         Note
         ____
         Sample body:
         {
          "class": "DeleteClassificationRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
         }
         """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_project_classification(project_guid = project_guid,
                                                body=body
                                                )
        )



    @dynamic_catch
    async def _async_get_projects_by_classification_properties(
            self, approach: str = None, management_style: str = None, results_usage: str = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
            body: Optional[dict | None] = None,) -> str | dict:

        """ Returns the list of project with a ProjectClassification classification and with matching properties.
         Async version.

        Parameters
        ----------
        approach: str, [default=None]
            The approach to filter by.  If None, will be treated as any.
        management_style: str, [default=None]
            The management style to filter by.  If None, will be treated as any.
        results_usage: str, [default=None]
            The results usage to filter by.  If None, will be treated as any.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, [default='JSON'], optional
            The format of the response.
        report_spec: str, [default=None]
            The report specification to use.  If None, the default will be used.
        Returns
        -------
        List | str

        A list of projects filtered by project classification, and effective time.

        Raises
        ------
        PyegeriaException

        Notes
        _____
        sample body:
        {
          "class" : "FindProjectClassificationProperties",
          "approach" : "",
          "managementStyle" : "",
          "resultsUsage" : ""
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/by-classification-properties"
        )
        if body is None:
            body = {
                "class" : "FindProjectClassificationProperties",
                "approach" : approach,
                "managementStyle" : management_style,
                "resultsUsage" : results_usage,
                "startFrom" : start_from,
                "pageSize" : page_size,
            }
        response = await self._async_make_request("POST", url, body)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str or len(elements) == 0:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_project_output(elements, "ProjectClassification",
                                                 "Project",
                                                 output_format, report_spec)
        return elements

    @dynamic_catch
    def get_projects_by_classification_properties(
            self, approach: str = None, management_style: str = None, results_usage: str = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
            body: Optional[dict | None] = None,) -> str | dict:

        """ Returns the list of project with a ProjectClassification classification and with matching properties.

        Parameters
        ----------
        approach: str, [default=None]
            The approach to filter by.  If None, will be treated as any.
        management_style: str, [default=None]
            The management style to filter by.  If None, will be treated as any.
        results_usage: str, [default=None]
            The results usage to filter by.  If None, will be treated as any.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, [default='JSON'], optional
            The format of the response.
        report_spec: str, [default=None]
            The report specification to use.  If None, the default will be used.
        Returns
        -------
        List | str

        A list of projects filtered by project classification, and effective time.

        Raises
        ------
        PyegeriaException

        Notes
        _____
        sample body:
        {
          "class": "FindProjectClassificationProperties",
          "approach": "",
          "managementStyle": "",
          "resultsUsage": ""
        }
        """

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_projects_by_classification_properties( approach, management_style, results_usage,
                                         start_from, page_size,
                                         output_format, report_spec, body)
        )
        return resp


    async def _async_get_project_team(
            self,
            project_guid: str,
            team_role: Optional[str] = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
            body: Optional[dict | FilterRequestBody] = None,) -> str | dict:

        """Returns the list of actors that are linked off of the project.  This includes the project managers.
           The optional request body allows a teamRole to be specified as a filter.  To filter out the project managers,
           specify "ProjectManagement" as the team role. Async version.

        Parameters
        ----------
        project_guid: str
            Identifier of the project to return information for.
        team_role: str, [default=None]
            The team role to filter by.  If None, all team members will be returned.
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

        PyegeriaException

        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/"
            f"projects/{project_guid}/team"
        )
        if body is None and (team_role is not None and team_role != "*"):
            body = { "filter" : team_role }
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str or len(elements) == 0:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_project_output(elements, team_role, "Project Team",
                                                 output_format, report_spec)
        return elements

    @dynamic_catch
    def get_project_team(
            self,
            project_guid: str,
            team_role: Optional[str] = None,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
            body: Optional[dict | FilterRequestBody] = None,
    ) -> str | dict:
        """Returns the list of actors that are linked off of the project.  This includes the project managers.
           The optional request body allows a teamRole to be specified as a filter.  To filter out the project managers,
           specify "ProjectManagement" as the team perspective.

        Parameters
        ----------
        project_guid: str
            Identifier of the project to return information for.
        team_role: str, [default=None]
            The team perspective to filter by.  If None, all team members will be returned.
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

        PyegeriaException

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_project_team(project_guid, team_role, start_from, page_size,
                                         output_format,report_spec, body  )
        )
        return resp

    @dynamic_catch
    async def _async_find_projects(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs
    ) -> list | str:
        """ Retrieve the list of project metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all projects.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = "Referenceable"
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/by-search-string"
        
        # Merge explicit parameters with kwargs
        params = {
            'search_string': search_string,
            'body': body,
            'starts_with': starts_with,
            'ends_with': ends_with,
            'ignore_case': ignore_case,
            'start_from': start_from,
            'page_size': page_size,
            'output_format': output_format,
            'report_spec': report_spec
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(
            url,
            _type="Project",
            _gen_output=self._generate_project_output,
            **params
        )

        return response

    @dynamic_catch
    def find_projects(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs
    ) -> list | str:
        """ Retrieve the list of project metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all projects.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = "Referenceable"
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
-------
        List | str

        Output depends on the output format specified.

        Raises
-------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_projects(
                search_string=search_string,
                body=body,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                **kwargs
            )
        )

    @dynamic_catch
    async def _async_get_projects_by_name(
            self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
            body: Optional[dict | FilterRequestBody] = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None) -> list | str:
        url = f"{self.project_command_base}/by-name"

        response = await self._async_get_name_request(url, _type="Projects",
                                                      _gen_output=self._generate_project_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_projects_by_name(
            self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
            body: Optional[dict | FilterRequestBody] = None,
            start_from: int = 0, page_size: int = 0,
            output_format: str = 'JSON',
            report_spec: str | dict = None) -> list | str:

        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_projects_by_name(
                filter_string,
                classification_names,
                body,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )
        return resp

    @dynamic_catch
    async def _async_get_project_by_guid(self, project_guid: str, element_type: Optional[str] = None,
                                         body: Optional[dict | GetRequestBody] = None,
                                         output_format: str = 'JSON',
                                         report_spec: str | dict = None) -> dict | str:
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
            report_spec: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------

            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
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
        type = element_type if element_type else "Project"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_project_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_project_by_guid(self, project_guid: str, element_type: Optional[str] = None,
                            body: Optional[dict | GetRequestBody] = None,
                            output_format: str = 'JSON',
                            report_spec: str | dict = None) -> dict | str:
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
            report_spec: str | dict, optional, default = None
                    The desired output columns/fields to include.

            Returns
            -------
            dict | str

            A JSON dict representing the specified collection. Returns a string if none found.

            Raises
            ------

            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
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
            self._async_get_project_by_guid(project_guid, element_type, body, output_format, report_spec)
        )

        return resp

    @dynamic_catch
    async def _async_get_project_graph(
            self,
            project_guid: str,
            element_type: Optional[str] = None,
            body: Optional[dict | GetRequestBody] = None,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
               f"{project_guid}/graph")
        element_type = element_type if element_type else "Project"
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_project_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)

        return response

    @dynamic_catch
    def get_project_graph(
            self,
            project_guid: str,
            element_type: Optional[str] = None,
            body: Optional[dict | GetRequestBody] = None,
            output_format: str = 'JSON',
            report_spec: str | dict = None,
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_project_graph(project_guid, element_type, body, output_format, report_spec)
        )

        return resp

    #
    #   Create project methods
    #
    @dynamic_catch
    async def _async_create_project(
            self,
            anchor_guid: Optional[str] = None,
            parent_guid: Optional[str] = None,
            parent_relationship_type_name: Optional[str] = None,
            parent_at_end1: bool = False,
            display_name: Optional[str] = None,
            description: Optional[str] = None,
            classification_name: str = "Project",
            identifier: Optional[str] = None,
            is_own_anchor: bool = True,
            status: Optional[str] = None,
            phase: Optional[str] = None,
            health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create project: https://egeria-project.org/concepts/project Async version.

        Parameters
        ----------.
        anchor_guid: str, optional
            The identity of the anchor element for the project.
        parent_guid: str, optional
            The identity of the parent element for the project.
        parent_relationship_type_name: str, optional
            The type of relationship to the parent element.
        parent_at_end1: bool, optional
            True if the parent is at end 1 of the relationship.
        display_name: str, optional
            The display name of the project.
        description: str, optional
            A description of the project.
        classification_name: str, optional
            The type of project - Campaign, StudyProject, Task, PersonalProject or Project.
        identifier: str, optional
            A business identifier for the project.
        is_own_anchor: bool, optional
            True if the project is its own anchor.
        status: str, optional
            The project status.
        phase: str, optional
            The project phase.
        health: str, optional
            The project health.
        start_date: str, optional
            The start date of the project.
        planned_end_date: str, optional
            The planned completion date of the project.
        body: dict
            A dict representing the details of the project to create. To create different kinds of projects,
            set the initial_classifications in the body to be, for instance, "PersonalProject" or "Campaign".


        Returns
        -------
        str - the guid of the created project

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
          "properties": {
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
        if body is None:
            import time
            body = {
                "class": "NewElementRequestBody",
                "anchorGUID": anchor_guid,
                "isOwnAnchor": is_own_anchor,
                "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name,
                "parentAtEnd1": parent_at_end1,
                "initialClassifications": {
                    classification_name: {
                        "class": f"{classification_name}Properties"
                    }
                } if classification_name and classification_name != "Project" else None,
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                    "identifier": identifier,
                    "name": display_name,
                    "description": description,
                    "projectStatus": status,
                    "projectPhase": phase,
                    "projectHealth": health,
                    "startDate": start_date,
                    "plannedEndDate": planned_end_date,
                }
            }

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects"

        return await self._async_create_element_body_request(url, ["ProjectProperties"], body)

    @dynamic_catch
    def create_project(
            self,
            anchor_guid: Optional[str] = None,
            parent_guid: Optional[str] = None,
            parent_relationship_type_name: Optional[str] = None,
            parent_at_end1: bool = False,
            display_name: Optional[str] = None,
            description: Optional[str] = None,
            classification_name: str = "Project",
            identifier: Optional[str] = None,
            is_own_anchor: bool = True,
            status: Optional[str] = None,
            phase: Optional[str] = None,
            health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create project: https://egeria-project.org/concepts/project

        Parameters
        ----------.
        anchor_guid: str, optional
            The identity of the anchor element for the project.
        parent_guid: str, optional
            The identity of the parent element for the project.
        parent_relationship_type_name: str, optional
            The type of relationship to the parent element.
        parent_at_end1: bool, optional
            True if the parent is at end 1 of the relationship.
        display_name: str, optional
            The display name of the project.
        description: str, optional
            A description of the project.
        classification_name: str, optional
            The type of project - Campaign, StudyProject, Task, PersonalProject or Project.
        identifier: str, optional
            A business identifier for the project.
        is_own_anchor: bool, optional
            True if the project is its own anchor.
        status: str, optional
            The project status.
        phase: str, optional
            The project phase.
        health: str, optional
            The project health.
        start_date: str, optional
            The start date of the project.
        planned_end_date: str, optional
            The planned completion date of the project.
        body: dict
            A dict representing the details of the project to create.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
            self._async_create_project(anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                                       display_name, description, classification_name, identifier,
                                       is_own_anchor, status, phase, health, start_date, planned_end_date, body)
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
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
            qualified_name: Optional[str] = None,
            identifier: Optional[str] = None,
            display_name: Optional[str] = None,
            description: Optional[str] = None,
            project_status: Optional[str] = None,
            project_phase: Optional[str] = None,
            project_health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            merge_update: bool = True,
            body: Optional[dict | UpdateElementRequestBody] = None,
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
        merge_update: bool, optional, defaults to False
            If True, then all the properties of the project will be replaced with the specified properties.
        body: dict, optional
            Full request body. If provided, other parameters are ignored.

        Returns
        -------
        str - the guid of the created project task

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        if body is None:
            body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": merge_update,
                "properties": {
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
            }

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
            qualified_name: Optional[str] = None,
            identifier: Optional[str] = None,
            display_name: Optional[str] = None,
            description: Optional[str] = None,
            project_status: Optional[str] = None,
            project_phase: Optional[str] = None,
            project_health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            merge_update: bool = True,
            body: Optional[dict | UpdateElementRequestBody] = None,
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
        merge_update: bool, optional, defaults to False
            If True, then all the properties of the project will be replaced with the specified properties.
        body: dict, optional
            Full request body. If provided, other parameters are ignored.

        Returns
        -------
        str - the guid of the created project task

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_project(project_guid, qualified_name, identifier, display_name, description,
                                       project_status, project_phase, project_health, start_date, planned_end_date,
                                       merge_update, body))

    @dynamic_catch
    async def _async_delete_project(
            self,
            project_guid: str, cascade: bool = False, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
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
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        cascade_s = str(cascade).lower()
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/"
            f"{project_guid}/delete"
        )

        await self._async_delete_element_request(url, body, cascade)
        logger.info(f"Deleted project {project_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_project(
            self,
            project_guid: str, cascade: bool = False, body: Optional[dict | DeleteElementRequestBody] = None) -> None:
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_project(project_guid, cascade, body))

    @dynamic_catch
    async def _async_set_project_dependency(self, project_guid: str,
                                            upstream_project_guid: str,
                                            body: Optional[dict | NewRelationshipRequestBody] = None):
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
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
                                            body: Optional[dict | NewRelationshipRequestBody] = None):
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
            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
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
                                              body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Unlink two dependent projects.  Request body is optional. Async version.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        upstream_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = "{self.project_command_base}/{project_guid}/project-dependencies/{upstream_project_guid}/detach"

        await self._async_delete_relationship_request(url, body)
        logger.info(
            f"Detached project {project_guid} from -> {upstream_project_guid}")

    @dynamic_catch
    def clear_project_dependency(self, project_guid: str, upstream_project_guid: str,
                                 body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Unlink two dependent projects.  Request body is optional.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        upstream_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
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
                                           body: Optional[dict | NewRelationshipRequestBody] = None):
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
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
                              body: Optional[dict | NewRelationshipRequestBody] = None):
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
            PyegeriaInvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PyegeriaAPIException
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
                                             body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """ Unlink hierarchy relationship.  Request body is optional. Async version.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        parent_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = "{self.project_command_base}/{parent_project_guid}/project-dependencies/{project_guid}/detach"

        await self._async_delete_relationship_request(url, body)
        logger.info(
            f"Detached project {project_guid} from -> {parent_project_guid}")

    @dynamic_catch
    def clear_project_hierarchy(self, project_guid: str, parent_project_guid: str,
                                body: Optional[dict | DeleteRelationshipRequestBody] = None):
        """ Unlink two dependent projects.  Request body is optional.

        Parameters
        ----------
        project_guid: str
            The guid of the dependent project.
        parent_project_guid: str
            The guid of the upstream digital project
        body: dict | DeleteRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
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
            assignment_type: Optional[str] = None,
            description: Optional[str] = None,
            body: Optional[dict | NewRelationshipRequestBody] = None
    ) -> None:
        """Add an actor to a project. The request body is optional.  If supplied, it contains the name of the perspective that
        the actor plays in the project. Async version.

        Parameters
        ----------
        project_guid: str
            identity of the project to update.
        actor_guid: str
            identity of the actor to add.
        team_role: str, optional, defaults to None
            Name of the perspective the actor plays in the project.
        effective_from: str, optional, defaults to None
            Date at which the actor becomes active in the project. Date format is ISO 8601 string format.
        effective_to: str, optional, defaults to None
            Date at which the actor is no longer active in the project. Date format is ISO 8601 string format.

        Returns
        -------
        None

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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

        await self._async_new_relationship_request(url, ["AssignmentScopeProperties"], body)
        logger.info(f"Added member {actor_guid} to project {project_guid}")

    @dynamic_catch
    def add_to_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            assignment_type: Optional[str] = None,
            description: Optional[str] = None,
            body: Optional[dict | NewRelationshipRequestBody] = None
    ) -> None:
        """Add an actor to a project. The request body is optional.  If supplied, it contains the name of the perspective that
        the actor plays in the project.

        Parameters
        ----------
        project_guid: str
            identity of the project to update.
        actor_guid: str
            identity of the actor to add.
        team_role: str, optional, defaults to None
            Name of the perspective the actor plays in the project.
        effective_from: str, optional, defaults to None
            Date at which the actor becomes active in the project. Date format is ISO 8601 string format.
        effective_to: str, optional, defaults to None
            Date at which the actor is no longer active in the project. Date format is ISO 8601 string format.

        Returns
        -------
        None

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
            body: Optional[dict | DeleteRelationshipRequestBody] = None
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/project-manager/projects/{project_guid}/"
            f"members/{actor_guid}/detach"
        )

        await self._async_delete_relationship_request(url, body)
        logger.info(f"Removed member {actor_guid} from project {project_guid}")

    @dynamic_catch
    def remove_from_project_team(
            self,
            project_guid: str,
            actor_guid: str,
            body: Optional[dict | DeleteRelationshipRequestBody] = None
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

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_from_project_team(project_guid, actor_guid, body)
        )

    @dynamic_catch
    async def _async_create_project_task(
            self,
            project_guid: str,
            display_name: Optional[str] = None,
            identifier: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            phase: Optional[str] = None,
            health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            body: Optional[dict | NewElementRequestBody] = None
    ) -> str:
        """Create a new task for a project.  Async version."""
        if body is None:
            import time
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Task-{display_name}-{time.asctime()}",
                    "identifier": identifier,
                    "name": display_name,
                    "description": description,
                    "projectStatus": status,
                    "projectPhase": phase,
                    "projectHealth": health,
                    "startDate": start_date,
                    "plannedEndDate": planned_end_date,
                }
            }

        url = f"{self.project_command_base}/{project_guid}/task"
        response = await self._async_new_element_request(url, body)
        logger.info(f"Created task for project {project_guid}")
        return response

    @dynamic_catch
    def create_project_task(
            self,
            project_guid: str,
            display_name: Optional[str] = None,
            identifier: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            phase: Optional[str] = None,
            health: Optional[str] = None,
            start_date: Optional[str] = None,
            planned_end_date: Optional[str] = None,
            body: Optional[dict | NewElementRequestBody] = None
    ) -> str:
        """Create a new task for a project.  """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_create_project_task(project_guid, display_name, identifier, description, status, phase, health,
                                            start_date, planned_end_date, body)
        )
        return resp


if __name__ == "__main__":
    print("Main-Project Manager")

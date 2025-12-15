"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Automated Curation View Service Methods

"""

import asyncio
import datetime

from httpx import Response
from loguru import logger
from pydantic import HttpUrl
from pyegeria._globals import NO_ELEMENTS_FOUND
from pyegeria._server_client import ServerClient
from pyegeria._validators import validate_guid, validate_name, validate_search_string
# from pyegeria._exceptions import (
#     PyegeriaInvalidParameterException,
#     PyegeriaAPIException,
#     PyegeriaUnauthorizedException,
# )
from pyegeria.models import GetRequestBody, FilterRequestBody, SearchStringRequestBody
from pyegeria.utils import body_slimmer
from pyegeria.config import settings
from pyegeria.base_report_formats import select_report_format, get_report_spec_match
from pyegeria.output_formatter import (
    generate_output,
    _extract_referenceable_properties,
    populate_columns_from_properties,
    get_required_relationships,
)
settings.Logging.console_logging_level = "ERROR"


class AutomatedCuration(ServerClient):
    """Set up and maintain automation services in Egeria.

    Attributes:
        view_server : str
            The name of the View Server to use.
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
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.curation_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/automated-curation"

        # Default entity label used by the output formatter for Technology Types
        self.TECH_TYPE_ENTITY_LABEL = "TechType"
        self.GOV_ACTION_TYPE_LABEL = "GovActionType"
        self.CATALOG_TARGET_LABEL = "CatalogTarget"
        self.ENGINE_ACTION_LABEL = "EngineAction"
        self.GOV_ACTION_PROCESS_LABEL = "GovActionProcess"


    def _extract_tech_type_element_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract properties from a technology type element and populate the provided columns_struct.
        Tolerant to missing fields.
        """
        # Populate direct properties first
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("columns", [])

        # Referenceable header extraction (GUID, qualifiedName, displayName, etc.)
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get("key")
            if key in header_props:
                column["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                column["value"] = header_props.get("GUID")
            elif key == "mermaidGraph":
                column["value"] = element.get("mermaidGraph","")
            elif key == "specificationMermaidGraph":
                column["value"] = element.get("specificationMermaidGraph","")

        return col_data
        # return columns_struct

    def _extract_tech_type_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract properties from a technology type element and populate the provided columns_struct.
        Tolerant to missing fields.
        """
        # # Populate direct properties first
        # col_data = populate_columns_from_properties(element, columns_struct)
        # columns_list = col_data.get("formats", {}).get("columns", [])
        #
        # # Referenceable header extraction (GUID, qualifiedName, displayName, etc.)
        # header_props = _extract_referenceable_properties(element)
        # for column in columns_list:
        #     key = column.get("key")
        #     if key in header_props:
        #         column["value"] = header_props.get(key)
        #     elif isinstance(key, str) and key.lower() == "guid":
        #         column["value"] = header_props.get("GUID")
        #
        # # Try common category/type fields
        # category = (
        #     element.get("properties", {}).get("category")
        #     or element.get("elementProperties", {}).get("category")
        #     or element.get("elementType", {}).get("typeName")
        #     or ""
        # )
        columns_list = columns_struct.get("formats", {}).get("attributes", [])

        guid = element.get('technologyTypeGUID',None)
        qualified_name = element.get('qualifiedName',None)
        display_name = element.get('displayName',None)
        description = element.get('description',None)
        catalog_templates = element.get('catalogTemplates',None)
        governance_processes = element.get('governanceActionProcesses',None)
        external_references = element.get('externalReferences',None)
        url = element.get('url',None)


        # Mermaid graph support if present
        mermaid_val = element.get("mermaidGraph", "") or ""
        for column in columns_list:
            if column.get("key") == "mermaidGraph":
                column["value"] = mermaid_val
                break
            elif column.get("key") == "catalog_template_specs":
                specs = ""
                for template in catalog_templates:
                    for placeholder in template['specification']['placeholderProperty']:
                        specs += (f"* Placeholder Property: {placeholder.get('name','')}\n\t"
                                  f"Type: {placeholder.get('dataType',"")}\n\t"
                                  f"Description:  {placeholder.get('description',"")}\n\t"
                                  f"Required: {placeholder.get("required","")}\n\t"
                                  f"Example: {placeholder.get("example","")}\n\n")
                column["value"] = specs
            elif column.get("key") == "catalog_templates":
                column["value"] =catalog_templates
            elif column.get("key") == "governance_processes":
                procs = ""
                specs = ""
                if governance_processes:
                    for proc in governance_processes:
                        proc_props = proc['relatedElement'].get("properties", {})
                        proc_qn = proc_props.get("qualifiedName","")
                        proc_dn = proc_props.get("displayName","")
                        proc_description = proc_props.get("description","")

                        proc_specs = proc.get("specification",{}).get("supportedRequestParameter",{})
                        for spec in proc_specs:
                            name = spec.get("name","")
                            description = spec.get("description","")
                            data_type = spec.get("dataType","")
                            example = spec.get("example","")
                            required = str(spec.get("required",""))
                            specs += (f"* Name: {name}\n"
                                      f"* Description: {description}\n"
                                      f"* Data Type: {data_type}\n"
                                      f"* Example: {example}\n"
                                      f"* Required: {required}\n\t---------\n"
                                      )

                        procs += (f"* Display Name: {proc_dn}\n"
                                  f"* Resource Use: {proc.get("resourceUse", "")}\n"
                                  f"* Description: {proc_description}\n"
                                  f"* Qualified Name: {proc_qn}\n"
                                  f"* Parameters:\n\t---------\n{specs}\n\t==========\n\n"
                                  )
                column['value'] = procs
            elif column.get("key") == "governance_processes_d":
                processes = []

                if governance_processes:
                    for proc in governance_processes:
                        procs = {}
                        proc_props = proc['relatedElement'].get("properties", {})
                        procs['proc_qualified_name'] = proc_props.get("qualifiedName", "")
                        procs['proc_display_name'] = proc_props.get("displayName", "")
                        procs['proc_description'] = proc_props.get("description", "")
                        procs['proc_params'] = proc.get("specification",{}).get("supportedRequestParameter",{})
                        processes.append(procs)
                column['value'] = processes
            elif column.get("key") == "guid":
                column["value"] = guid
            elif column.get("key") == "qualified_name":
                column["value"] = qualified_name
            elif column.get("key") == "display_name":
                column["value"] = display_name
            elif column.get("key") == "description":
                column["value"] = description
            elif column.get("key") == "external_references":
                column["value"] = external_references
            elif column.get("key") == "ref_url":
                if isinstance(external_references, dict):
                    column["value"] = external_references[0]['relatedElement']['properties'].get('url',"")
            elif column.get("key") == "url":
                column["value"] = url
        columns_struct["formats"]["attributes"] = columns_list
        return columns_struct

    def _generate_tech_type_output(
        self,
        elements: dict | list[dict],
        filter: str | None,
        element_type_name: str | None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
        **kwargs,
    ) -> str | list[dict]:
        """Generate output for technology types in the specified format."""
        entity_type = element_type_name or self.TECH_TYPE_ENTITY_LABEL

        # Resolve report format (with backward-compatible legacy kwarg)
        get_additional_props_func = None
        if report_spec is None and isinstance(kwargs, dict) and 'report_spec' in kwargs:
            report_spec = kwargs.get('report_spec')
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_format(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_format("Default", output_format)

        # Optional hook for extra server calls to enrich rows
        get_additional_props_name = (
            output_formats.get("get_additional_props", {}).get("function") if output_formats else None
        )
        if isinstance(get_additional_props_name, str):
            parts = get_additional_props_name.split(".")
            method_name = parts[-1] if parts else None
            if method_name and hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_tech_type_properties,
            get_additional_props_func,
            output_formats,
        )

    def _generate_tech_type_element_output(
        self,
        elements: dict | list[dict],
        filter: str | None,
        element_type_name: str | None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
        **kwargs,
    ) -> str | list[dict]:
        """Generate output for technology type elements in the specified format."""
        entity_type = element_type_name or self.TECH_TYPE_ENTITY_LABEL

        # Resolve report format (with backward-compatible legacy kwarg)
        get_additional_props_func = None
        if report_spec is None and isinstance(kwargs, dict) and 'report_spec' in kwargs:
            report_spec = kwargs.get('report_spec')
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_format(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_format("Default", output_format)

        # Optional hook for extra server calls to enrich rows
        get_additional_props_name = (
            output_formats.get("get_additional_props", {}).get("function") if output_formats else None
        )
        if isinstance(get_additional_props_name, str):
            parts = get_additional_props_name.split(".")
            method_name = parts[-1] if parts else None
            if method_name and hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_tech_type_element_properties,
            get_additional_props_func,
            output_formats,
        )

    def _extract_gov_action_type_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get("key")
            if key in header_props:
                column["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                column["value"] = header_props.get("GUID")
        col_data = get_required_relationships(element, col_data)
        mermaid_val = element.get("mermaidGraph", "") or ""
        for column in columns_list:
            if column.get("key") == "mermaid":
                column["value"] = mermaid_val
                break
        return col_data

    def _generate_gov_action_type_output(self, elements: dict | list[dict], filter: str | None,
                                         element_type_name: str | None, output_format: str = "DICT",
                                         report_format: dict | str | None = None,
                                         **kwargs) -> str | list[dict]:
        entity_type = element_type_name or self.GOV_ACTION_TYPE_LABEL
        get_additional_props_func = None
        if report_format is None and isinstance(kwargs, dict) and 'report_spec' in kwargs:
            report_format = kwargs.get('report_spec')
        if report_format:
            if isinstance(report_format, str):
                output_formats = select_report_format(report_format, output_format)
            else:
                output_formats = get_report_spec_match(report_format, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_format("Default", output_format)
        get_additional_props_name = (
            output_formats.get("get_additional_props", {}).get("function") if output_formats else None
        )
        if isinstance(get_additional_props_name, str):
            method_name = get_additional_props_name.split(".")[-1]
            if hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_gov_action_type_properties,
            get_additional_props_func,
            output_formats,
        )

    def _extract_catalog_target_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get("key")
            if key in header_props:
                column["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                column["value"] = header_props.get("GUID")
        col_data = get_required_relationships(element, col_data)
        mermaid_val = element.get("mermaidGraph", "") or ""
        for column in columns_list:
            if column.get("key") == "mermaid":
                column["value"] = mermaid_val
                break
        return col_data

    def _generate_catalog_target_output(self, elements: dict | list[dict], filter: str | None,
                                        element_type_name: str | None, output_format: str = "DICT",
                                        report_format: dict | str | None = None,
                                        **kwargs) -> str | list[dict]:
        entity_type = element_type_name or self.CATALOG_TARGET_LABEL
        get_additional_props_func = None
        if report_format is None and isinstance(kwargs, dict) and 'report_spec' in kwargs:
            report_format = kwargs.get('report_spec')
        if report_format:
            if isinstance(report_format, str):
                output_formats = select_report_format(report_format, output_format)
            else:
                output_formats = get_report_spec_match(report_format, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_format("Default", output_format)
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_catalog_target_properties,
            None,
            output_formats,
        )

    def _extract_engine_action_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")
        # EngineAction specifics: status, process_name, received_guards, completion_guards, request_type
        status = (
            element.get("properties", {}).get("status")
            or element.get("elementProperties", {}).get("status")
            or element.get("status")
        )
        process_name = (
            element.get("properties", {}).get("processName")
            or element.get("elementProperties", {}).get("processName")
            or element.get("processName")
        )
        req_type = (
            element.get("properties", {}).get("requestType")
            or element.get("elementProperties", {}).get("requestType")
            or element.get("requestType")
        )
        rec_guards = element.get("receivedGuards") or element.get("received_guards") or []
        comp_guards = element.get("completionGuards") or element.get("completion_guards") or []
        # assign to columns if present
        for col in columns_list:
            key = col.get("key")
            if key == "status":
                col["value"] = status
            elif key in ("process_name", "processName"):
                col["value"] = process_name
            elif key in ("request_type", "requestType"):
                col["value"] = req_type
            elif key in ("received_guards", "receivedGuards"):
                col["value"] = ", ".join(map(str, rec_guards)) if isinstance(rec_guards, list) else rec_guards
            elif key in ("completion_guards", "completionGuards"):
                col["value"] = ", ".join(map(str, comp_guards)) if isinstance(comp_guards, list) else comp_guards
        col_data = get_required_relationships(element, col_data)
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaid":
                col["value"] = mermaid_val
                break
        return col_data

    def _generate_engine_action_output(self, elements: dict | list[dict], filter: str | None,
                                       element_type_name: str | None, output_format: str = "DICT",
                                       report_spec: dict | str | None = None) -> str | list[dict]:
        entity_type = element_type_name or self.ENGINE_ACTION_LABEL
        get_additional_props_func = None
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_format(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_format("Default", output_format)
        get_additional_props_name = (
            output_formats.get("get_additional_props", {}).get("function") if output_formats else None
        )
        if isinstance(get_additional_props_name, str):
            method_name = get_additional_props_name.split(".")[-1]
            if hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_engine_action_properties,
            get_additional_props_func,
            output_formats,
        )

    def _extract_gov_action_process_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")
        # GAP specifics: processStatus, elementTypeName, stepCount
        proc_status = (
            element.get("properties", {}).get("processStatus")
            or element.get("elementProperties", {}).get("processStatus")
            or element.get("processStatus")
        )
        step_count = (
            element.get("properties", {}).get("stepCount")
            or element.get("elementProperties", {}).get("stepCount")
            or element.get("stepCount")
        )
        for col in columns_list:
            key = col.get("key")
            if key in ("process_status", "processStatus"):
                col["value"] = proc_status
            elif key == "stepCount":
                col["value"] = step_count
        col_data = get_required_relationships(element, col_data)
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaid":
                col["value"] = mermaid_val
                break
        return col_data

    def _generate_gov_action_process_output(self, elements: dict | list[dict], filter: str | None,
                                            element_type_name: str | None, output_format: str = "DICT",
                                            report_spec: dict | str | None = None) -> str | list[dict]:
        entity_type = element_type_name or self.GOV_ACTION_PROCESS_LABEL
        get_additional_props_func = None
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_format(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_format(element_type_name, output_format)
        else:
            output_formats = select_report_format(entity_type, output_format)
        if output_formats is None:
            output_formats = select_report_format("Default", output_format)
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_gov_action_process_properties,
            None,
            output_formats,
        )

    async def _async_create_elem_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
            The json body used to instantiate the template.

        Returns
        -------
        Response
           The guid of the resulting element

        Raises
        ------
        PyegeriaException
        Notes
        -----
        See also: https://egeria-project.org/features/templated-cataloguing/overview/
        The full description of the body is shown below:
           {
             "typeName" : "",
             "initialStatus" : "",
             "initialClassifications" : "",
             "anchorGUID" : "",
             "isOwnAnchor" : "",
             "effectiveFrom" : "",
             "effectiveTo" : "",
             "templateGUID" : "",
             "templateProperties" : {},
             "placeholderPropertyValues" : {
               "placeholderPropertyName1" : "placeholderPropertyValue1",
               "placeholderPropertyName2" : "placeholderPropertyValue2"
             },
             "parentGUID" : "",
             "parentRelationshipTypeName" : "",
             "parentRelationshipProperties" : "",
             "parentAtEnd1" : "",
             "effectiveTime" : ""
           }
        """

        url = f"{self.curation_command_root}/catalog-templates/new-element"
        return await self._async_create_element_from_template(url, body)

    def create_elem_from_template(self, body: dict) -> str:
        """Create a new metadata element from a template.  Async version.
        Parameters
        ----------
        body : str
             The json body used to instantiate the template.


        Returns
        -------
        Response
            The guid of the resulting element

         Raises
         ------
         PyegeriaInvalidParameterException
         PyegeriaAPIException
         PyegeriaUnauthorizedException

         Notes
         -----
         See also: https://egeria-project.org/features/templated-cataloguing/overview/
         The full description of the body is shown below:
             {
               "typeName" : "",
               "initialStatus" : "",
               "initialClassifications" : "",
               "anchorGUID" : "",
               "isOwnAnchor" : "",
               "effectiveFrom" : "",
               "effectiveTo" : "",
               "templateGUID" : "",
               "templateProperties" : {},
               "placeholderPropertyValues" : {
                 "placeholderPropertyName1" : "placeholderPropertyValue1",
                 "placeholderPropertyName2" : "placeholderPropertyValue2"
               },
               "parentGUID" : "",
               "parentRelationshipTypeName" : "",
               "parentRelationshipProperties" : "",
               "parentAtEnd1" : "",
               "effectiveTime" : ""
             }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_elem_from_template(body)
        )
        return response

    async def _async_create_kafka_server_element_from_template(
            self,
            kafka_server: str,
            host_name: str,
            port: str,
            description: str = None,
    ) -> str:
        """Create a Kafka server element from a template. Async version.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        description: str, opt
            A description of the Kafka server.



        Returns
        -------
        str
            The GUID of the Kafka server element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Apache Kafka Server")
        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": kafka_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        return await self._async_create_elem_from_template(body_s)

    def create_kafka_server_element_from_template(
            self,
            kafka_server: str,
            host_name: str,
            port: str,
            description: str = None,
    ) -> str:
        """Create a Kafka server element from a template.

        Parameters
        ----------
        kafka_server : str
            The name of the Kafka server.

        host_name : str
            The host name of the Kafka server.

        port : str
            The port number of the Kafka server.

        description: str, opt
            A description of the Kafka server.



        Returns
        -------
        str
            The GUID of the Kafka server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_kafka_server_element_from_template(
                kafka_server, host_name, port, description
            )
        )
        return response

    async def _async_create_csv_data_file_element_from_template(
            self,
            file_name: str,
            file_type: str,
            file_path_name: str,
            version_identifier: str,
            file_encoding: str = "UTF-8",
            file_extension: str = "csv",
            file_system_name: str = None,
            description: str = None,
    ) -> str:
        """Create a CSV file element from a template. Async version.

        Parameters
        ----------
        file_name : str
            The name of the Kafka server.
        file_type : str
            The host name of the Kafka server.
        file_path_name : str
            The port number of the Kafka server.
        version_identifier : str
            The version identifier of the CSV file..
        file_encoding: str, opt, default UTF-8
            The encoding of the CSV file.
        file_extension: str, opt, default is CSV
            File extension of the CSV file.
        file_system_name: str, opt
            Name of the file system the CSV file is hosted on.
        description: str, opt
            A description of the CSV file..


        Returns
        -------
        str
            The GUID of the CSV File element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("CSV Data File")
        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "fileName": file_name,
                "fileType": file_type,
                "filePathName": file_path_name,
                "versionIdentifier": version_identifier,
                "fileEncoding": file_encoding,
                "fileExtension": file_extension,
                "fileSystemName": file_system_name,
                "description": description
            },
        }
        body_s = body_slimmer(body)
        return await self._async_create_elem_from_template(body_s)

    def create_csv_data_file_element_from_template(
            self,
            file_name: str,
            file_type: str,
            file_path_name: str,
            version_identifier: str,
            file_encoding: str = "UTF-8",
            file_extension: str = "csv",
            file_system_name: str = None,
            description: str = None,
    ) -> str:
        """Create a CSV file element from a template. Async version.

        Parameters
        ----------
        file_name : str
            The name of the Kafka server.
        file_type : str
            The host name of the Kafka server.
        file_path_name : str
            The port number of the Kafka server.
        version_identifier : str
            The version identifier of the CSV file..
        file_encoding: str, opt, default UTF-8
            The encoding of the CSV file.
        file_extension: str, opt, default is CSV
            File extension of the CSV file.
        file_system_name: str, opt
            Name of the file system the CSV file is hosted on.
        description: str, opt
            A description of the CSV file..

        Returns
        -------
        str
            The GUID of the CSV File element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_csv_data_file_element_from_template(
                file_name, file_type, file_path_name, version_identifier,
                file_encoding, file_extension, file_system_name, description
            )
        )
        return response

    async def _async_get_create_csv_data_file_element_from_template(
            self,
            file_name: str,
            file_type: str,
            file_path_name: str,
            version_identifier: str,
            file_encoding: str = "UTF-8",
            file_extension: str = "csv",
            file_system_name: str = None,
            description: str = None,
    ) -> str:
        """Create a CSV file element from a template if it doesn't exist. If it does exist,
           the guid will be returned. Async version.

        Parameters
        ----------
        file_name : str
            The name of the Kafka server.
        file_type : str
            The host name of the Kafka server.
        file_path_name : str
            The port number of the Kafka server.
        version_identifier : str
            The version identifier of the CSV file..
        file_encoding: str, opt, default UTF-8
            The encoding of the CSV file.
        file_extension: str, opt, default is CSV
            File extension of the CSV file.
        file_system_name: str, opt
            Name of the file system the CSV file is hosted on.
        description: str, opt
            A description of the CSV file..


        Returns
        -------
        str
            The GUID of the CSV File element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("CSV Data File")
        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": True,
            "allowRetrieve": True,
            "placeholderPropertyValues": {
                "fileName": file_name,
                "fileType": file_type,
                "filePathName": file_path_name,
                "versionIdentifier": version_identifier,
                "fileEncoding": file_encoding,
                "fileExtension": file_extension,
                "fileSystemName": file_system_name,
                "description": description
            },
        }
        body_s = body_slimmer(body)
        return await self._async_create_elem_from_template(body_s)

    def get_create_csv_data_file_element_from_template(
            self,
            file_name: str,
            file_type: str,
            file_path_name: str,
            version_identifier: str,
            file_encoding: str = "UTF-8",
            file_extension: str = "csv",
            file_system_name: str = None,
            description: str = None,
    ) -> str:
        """Create a CSV file element from a template if it doesn't exist. If it does exist,
           the guid will be returned.

        Parameters
        ----------
        file_name : str
            The name of the Kafka server.
        file_type : str
            The host name of the Kafka server.
        file_path_name : str
            The port number of the Kafka server.
        version_identifier : str
            The version identifier of the CSV file..
        file_encoding: str, opt, default UTF-8
            The encoding of the CSV file.
        file_extension: str, opt, default is CSV
            File extension of the CSV file.
        file_system_name: str, opt
            Name of the file system the CSV file is hosted on.
        description: str, opt
            A description of the CSV file..

        Returns
        -------
        str
            The GUID of the CSV File element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_create_csv_data_file_element_from_template(
                file_name, file_type, file_path_name, version_identifier,
                file_encoding, file_extension, file_system_name, description
            )
        )
        return response

    async def _async_create_postgres_server_element_from_template(
            self,
            postgres_server: str,
            host_name: str,
            port: str,
            db_user: str,
            db_pwd: str,
            description: str = None,
    ) -> str:
        """Create a Postgres server element from a template. Async version.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        description: str, opt
            A description of the element.



        Returns
        -------
        str
            The GUID of the Postgres server element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("PostgreSQL Server")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": postgres_server,
                "hostIdentifier": host_name,
                "portNumber": port,
                "databaseUserId": db_user,
                "description": description,
                "databasePassword": db_pwd,
            },
        }
        body_s = body_slimmer(body)
        return await self._async_create_elem_from_template(body_s)

    def create_postgres_server_element_from_template(
            self,
            postgres_server: str,
            host_name: str,
            port: str,
            db_user: str,
            db_pwd: str,
            description: str = None,
    ) -> str:
        """Create a Postgres server element from a template.

        Parameters
        ----------
        postgres_server : str
            The name of the Postgres server.

        host_name : str
            The host name of the Postgres server.

        port : str
            The port number of the Postgres server.



        description: str, opt
            A description of the elementr.

        db_user: str
            User name to connect to the database

        db_pwd: str
            User password to connect to the database

        Returns
        -------
        str
            The GUID of the Postgres server element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_postgres_server_element_from_template(
                postgres_server, host_name, port, db_user, db_pwd, description
            )
        )
        return response

    async def _async_create_postgres_database_element_from_template(
            self,
            postgres_database: str,
            server_name: str,
            host_identifier: str,
            port: str,
            db_user: str,
            db_pwd: str,
            description: str = None,
    ) -> str:
        """Create a Postgres database element from a template. Async version.

        Parameters
        ----------
        postgres_database : str
            The name of the Postgres database.
        server_name : str
            The server name of the Postgres server.
        host_identifier: str
            The host IP address or domain name.
        port : str
            The port number of the Postgres server.
        db_user: str
            User name to connect to the database
        db_pwd: str
            User password to connect to the database
        description: str, opt
            A description of the element.

        Returns
        -------
        str
            The GUID of the Postgres database element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("PostgreSQL Relational Database")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "databaseName": postgres_database,
                "serverName": server_name,
                "hostIdentifier": host_identifier,
                "portNumber": port,
                "databaseUserId": db_user,
                "description": description,
                "databasePassword": db_pwd,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_postgres_database_element_from_template(
            self,
            postgres_database: str,
            server_name: str,
            host_identifier: str,
            port: str,
            db_user: str,
            db_pwd: str,
            description: str = None,
    ) -> str:
        """Create a Postgres database element from a template. Async version.

        Parameters
        ----------
        postgres_database : str
            The name of the Postgres database.
        server_name : str
            The server name of the Postgres server.
        host_identifier: str
            The host IP address or domain name.
        port : str
            The port number of the Postgres server.
        db_user: str
            User name to connect to the database
        db_pwd: str
            User password to connect to the database
        description: str, opt
            A description of the element.

        Returns
        -------
        str
            The GUID of the Postgres database element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_postgres_database_element_from_template(
                postgres_database,
                server_name,
                host_identifier,
                port,
                db_user,
                db_pwd,
                description,
            )
        )
        return response

    async def _async_create_folder_element_from_template(
            self,
            path_name: str,
            folder_name: str,
            file_system: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a File folder element from a template.
        Async version.

        Parameters
        ----------
        path_name : str
            The path including the folder..

        folder_name : str
            The name of the folder to create.

        file_system : str
            The unique name for the file system that the folder belongs to. It may be a machine name or URL to a
            remote file store.

        description: str, opt
            A description of the element.

        version: str, opt
            version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("File System Directory")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "directoryPathName": path_name,
                "directoryName": folder_name,
                "versionIdentifier": version,
                "fileSystemName": file_system,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_folder_element_from_template(
            self,
            path_name: str,
            folder_name: str,
            file_system: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a File folder element from a template.

        Parameters
        ----------
        path_name : str
            The path including the folder..

        folder_name : str
            The name of the folder to create.

        file_system : str
            The unique name for the file system that the folder belongs to. It may be a machine name or URL to a
            remote file store.

        description: str, opt
            A description of the element.

        version: str, opt
            version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_folder_element_from_template(
                path_name, folder_name, file_system, description, version
            )
        )
        return response

    async def _async_create_uc_server_element_from_template(
            self,
            server_name: str,
            host_url: str,
            port: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog Server element from a template. Async version.

        Parameters
        ----------
        server_name : str
            The name of the Unity Catalog server we are configuring.

        host_url : str
            The URL of the server.

        port : str
            The port number of the server.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Server")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "serverName": server_name,
                "hostURL": host_url,
                "versionIdentifier": version,
                "portNumber": port,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_server_element_from_template(
            self,
            server_name: str,
            host_url: str,
            port: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog Server element from a template. Async version.

        Parameters
        ----------
        server_name : str
            The name of the Unity Catalog server we are configuring.

        host_url : str
            The URL of the server.

        port : str
            The port number of the server.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_server_element_from_template(
                server_name, host_url, port, description, version
            )
        )
        return response

    async def _async_create_uc_catalog_element_from_template(
            self,
            uc_catalog: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog Catalog element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Catalog")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_catalog_element_from_template(
            self,
            uc_catalog: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog Catalog element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_catalog_element_from_template(
                uc_catalog, network_address, description, version
            )
        )
        return response

    async def _async_create_uc_schema_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog schema element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Schema")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_schema_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog schema element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_schema_element_from_template(
                uc_catalog, uc_schema, network_address, description, version
            )
        )
        return response

    async def _async_create_uc_table_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_table: str,
            uc_table_type: str,
            uc_storage_loc: str,
            uc_data_source_format: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog table element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_table: str
            The name of the UC table we are configuring.
        uc_table_type: str
            The type of table - expect either Managed or External.
        uc_storage_loc: str
            The location where the data associated with this element is stored.
        uc_data_source_format: str
            The format of the data source - currently DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Table")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucTableName": uc_table,
                "ucTableType": uc_table_type,
                "ucStorageLocation": uc_storage_loc,
                "ucDataSourceFormat": uc_data_source_format,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_table_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_table: str,
            uc_table_type: str,
            uc_storage_loc: str,
            uc_data_source_format: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog table element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_table: str
            The name of the UC table we are configuring.
        uc_table_type: str
            The type of table - expect either Managed or External.
        uc_storage_loc: str
            The location where the data associated with this element is stored.
        uc_data_source_format: str
            The format of the data source - currently DELTA, CSV, JSON, AVRO, PARQUET, ORC, TEXT.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_table_element_from_template(
                uc_catalog,
                uc_schema,
                uc_table,
                uc_table_type,
                uc_storage_loc,
                uc_data_source_format,
                network_address,
                description,
                version,
            )
        )
        return response

    async def _async_create_uc_function_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_function: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog function element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_function: str
            The name of the UC function we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Function")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucFunctionName": uc_function,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_function_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_function: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog function element from a template.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_function: str
            The name of the UC function we are configuring.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_function_element_from_template(
                uc_catalog,
                uc_schema,
                uc_function,
                network_address,
                description,
                version,
            )
        )
        return response

    async def _async_create_uc_volume_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_volume: str,
            uc_vol_type: str,
            uc_storage_loc: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog volume element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_volume: str
            The name of the UC volume we are configuring.

        uc_vol_type: str
            The volume type of the UC volume we are configuring. Currently Managed or External.
        uc_storage_loc: str
            The location with the data associated with this element is stored.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        template_guid = await self._async_get_template_guid_for_technology_type("Unity Catalog Volume")

        body = {
            "class": "TemplateRequestBody",
            "templateGUID": template_guid,
            "isOwnAnchor": "true",
            "placeholderPropertyValues": {
                "ucCatalogName": uc_catalog,
                "ucSchemaName": uc_schema,
                "ucVolumeName": uc_volume,
                "ucVolumeType": uc_vol_type,
                "ucStorageLocation": uc_storage_loc,
                "serverNetworkAddress": network_address,
                "versionIdentifier": version,
                "description": description,
            },
        }
        body_s = body_slimmer(body)
        response = await self._async_create_elem_from_template(body_s)
        return str(response)

    def create_uc_volume_element_from_template(
            self,
            uc_catalog: str,
            uc_schema: str,
            uc_volume: str,
            uc_vol_type: str,
            uc_storage_loc: str,
            network_address: str,
            description: str = None,
            version: str = None,
    ) -> str:
        """Create a Unity Catalog volume element from a template. Async version.

        Parameters
        ----------
        uc_catalog : str
            The name of the UC catalog we are configuring.

        uc_schema: str
            The name of the UC schema we are configuring.

        uc_volume: str
            The name of the UC volume we are configuring.

        uc_vol_type: str
            The volume type of the UC volume we are configuring. Currently Managed or External.

        uc_storage_loc: str
            The location with the data associated with this element is stored.

        network_address : str
            The endpoint of the catalog.

        description: str, opt
                A description of the server.

        version: str, opt
                version of the element - typically of the form x.y.z



        Returns
        -------
        str
            The GUID of the File Folder element.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_uc_volume_element_from_template(
                uc_catalog,
                uc_schema,
                uc_volume,
                uc_vol_type,
                uc_storage_loc,
                network_address,
                description,
                version,
            )
        )
        return response

    #
    # Engine Actions
    #

    async def _async_cancel_engine_action(self, engine_action_guid: str) -> None:
        """Request that an engine action request is cancelled and any running governance service is stopped. Async Ver.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        validate_guid(engine_action_guid)

        url = (
            f"{self.curation_command_root}/engine-actions/"
            f"{engine_action_guid}/cancel"
        )

        await self._async_make_request("POST", url)

    def cancel_engine_action(self, engine_action_guid: str) -> None:
        """Request that an engine action request is cancelled and any running governance service is stopped.
        Parameters
        ----------
        engine_action_guid : str
            The GUID of the engine action to retrieve.



        Returns
        -------
        dict
            The JSON representation of the engine action.

        Raises
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_cancel_engine_action(engine_action_guid))
        return

    async def _async_get_active_engine_actions(
            self, start_from: int = 0, page_size: int = 0,
            output_format: str = "JSON", report_spec: str | dict = "Engine-Actions") -> list | str:
        """Retrieve the engine actions that are still in process. Async Version.

        Parameters:
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns:
        -------
            List[dict]: A list of JSON representations of governance action processes matching the provided name.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """

        url = (
            f"{self.curation_command_root}/engine-actions/active"
        )

        response = await self._async_make_request("GET", url)
        elements = response.json().get("elements", "No actions found")
        if type(elements) is str:
            logger.info("No Actions Found")
            return "No Actions Found"

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            # logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_engine_action_output(elements, None, "EngineAction",
                               output_format, report_spec)
        return elements

    def get_active_engine_actions(
            self, start_from: int = 0, page_size: int = 0,
            output_format: str = "JSON", report_spec: str | dict = "EngineAction",
    ) -> list | str:
        """Retrieve the engine actions that are still in process.

        Parameters:
        ----------

        start_from : int, optional
            The starting index of the actions to retrieve. Default is 0.
        page_size : int, optional
            The maximum number of actions to retrieve per page. Default is the global maximum paging size.

        Returns
        -------
            List[dict]: A list of JSON representations of governance action processes matching the provided name.

        Raises
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_active_engine_actions(start_from, page_size, output_format=output_format,
                                                  report_spec=report_spec)
        )
        return response

    async def _async_get_engine_actions_by_name(
            self,
            name: str,
            start_from: int = 0,
            page_size: int = 0,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request. Async Version.
        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
            maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
             found with the given name.
        Raises:
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """

        validate_name(name)

        url = (
            f"{self.curation_command_root}/engine-actions/by-name"
        )
        body = {"filter": name}
        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no actions")

    def get_engine_actions_by_name(
            self,
            name: str,
            start_from: int = 0,
            page_size: int = 0,
    ) -> list | str:
        """Retrieve the list of engine action metadata elements with a matching qualified or display name.
        There are no wildcards supported on this request.

        Parameters
        ----------
        name : str
            The name of the engine action to retrieve.

        start_from : int, optional
            The index to start retrieving engine actions from. If not provided, the default value will be used.
        page_size : int, optional
            The maximum number of engine actions to retrieve in a single request. If not provided, the default global
             maximum paging size will be used.

        Returns
        -------
        list of dict | str
            A list of dictionaries representing the retrieved engine actions, or "no actions" if no engine actions were
            found with the given name.
        Raises:
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_engine_actions_by_name(name, start_from, page_size)
        )
        return response

    async def _async_find_engine_actions(
            self,
            search_string: str,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = "EngineAction",
    ) -> list | str:
        """Retrieve the list of engine action metadata elements that contain the search string. Async Version.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `0`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        validate_search_string(search_string)
        if search_string == "*":
            search_string = None

        url = str(HttpUrl(f"{self.curation_command_root}/assets/by-search-string"))
        return await self._async_find_request(url, _type=self.ENGINE_ACTION_LABEL,
                                              _gen_output=self._generate_engine_action_output,
                                              search_string=search_string, include_only_classification_names=None,
                                              metadata_element_subtypes=["EngineAction"], starts_with=starts_with,
                                              ends_with=ends_with, ignore_case=ignore_case, start_from=start_from,
                                              page_size=page_size, output_format=output_format, report_spec=report_spec,
                                              body=None)

    def find_engine_actions(
            self,
            search_string: str = "*",
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = False,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = "EngineAction",
    ) -> list | str:
        """Retrieve the list of engine action metadata elements that contain the search string.
        Parameters
        ----------
        search_string : str
            The string used for searching engine actions by name.



        starts_with : bool, optional
            Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
            Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
            Whether to ignore case while searching engine actions. Default is False.

        start_from : int, optional
            The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
            The maximum number of engine actions to fetch in a single request. Default is `0`.

        Returns
        -------
        List[dict] or str
            A list of dictionaries representing the engine actions found based on the search query.
            If no actions are found, returns the string "no actions".

        Raises:
        ------
        PyegeriaException
        Notes
        -----
        For more information see: https://egeria-project.org/concepts/engine-action
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_engine_actions(
                search_string,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format=output_format,
                report_spec=report_spec,
            )
        )
        return response

    #
    # Governance action processes
    #


    async def _async_initiate_gov_action_process(
            self,
            action_type_qualified_name: str,
            request_source_guids: [str] = None,
            action_targets: list = None,
            start_time: datetime = None,
            request_parameters: dict = None,
            orig_service_name: str = None,
            orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action process as a template, initiate a chain of engine actions. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str], optional
            - request source elements for the resulting governance action service
        action_targets: [str], optional
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, optional
            - time to start the process
        request_parameters: [str], optional
            - parameters passed into the process
        orig_service_name: str, optional
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str, optional
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        PyegeriaException
        """

        start_time: datetime = (
            datetime.datetime.now() if start_time is None else start_time
        )

        url = f"{self.curation_command_root}/governance-action-processes/initiate"
        body = {
            "class": "GovernanceActionProcessRequestBody",
            "processQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startTime": int(start_time.timestamp() * 1000),
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_gov_action_process(
            self,
            action_type_qualified_name: str,
            request_source_guids: [str] = None,
            action_targets: [str] = None,
            start_time: datetime = None,
            request_parameters: dict = None,
            orig_service_name: str = None,
            orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action process as a template, initiate a chain of engine actions.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str], optional
            - request source elements for the resulting governance action service
        action_targets: [str], optional
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, optional
            - time to start the process
        request_parameters: [str], optional
            - parameters passed into the process
        orig_service_name: str, optional
            - unique name of the requesting governance service (if initiated by a governance engine)
        orig_engine_name: str, optional
            - optional unique name of the governance engine (if initiated by a governance engine).

        Returns
        -------
        Unique id (guid) of the newly started governance engine process

        Raises
        ------
        PyegeriaException
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_process(
                action_type_qualified_name,
                request_source_guids,
                action_targets,
                start_time,
                request_parameters,
                orig_service_name,
                orig_engine_name,
            )
        )
        return response



    async def _async_initiate_gov_action_type(
            self,
            action_type_qualified_name: str,
            request_source_guids: [str],
            action_targets: list,
            start_time: datetime = None,
            request_parameters: dict = None,
            orig_service_name: str = None,
            orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action type as a template, initiate an engine action. Async version.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, default = None
            - time to start the process, no earlier than start time. None means now.
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
        PyegeriaException
        """

        url = f"{self.curation_command_root}/governance-action-types/initiate"
        start = int(start_time.timestamp() * 1000) if start_time else None
        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": action_type_qualified_name,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "startDate": start,
            "requestParameters": request_parameters,
            "originatorServiceName": orig_service_name,
            "originatorEngineName": orig_engine_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_gov_action_type(
            self,
            action_type_qualified_name: str,
            request_source_guids: [str],
            action_targets: list,
            start_time: datetime = None,
            request_parameters: dict = None,
            orig_service_name: str = None,
            orig_engine_name: str = None,
    ) -> str:
        """Using the named governance action type as a template, initiate an engine action.

        Parameters
        ----------
        action_type_qualified_name: str
            - unique name for the governance process
        request_source_guids: [str]
            - request source elements for the resulting governance action service
        action_targets: [str]
            -list of action target names to GUIDs for the resulting governance action service
        start_time: datetime, default = None
            - time to start the process, no earlier than start time. None means now.
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
        PyegeriaException        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_gov_action_type(
                action_type_qualified_name,
                request_source_guids,
                action_targets,
                start_time,
                request_parameters,
                orig_service_name,
                orig_engine_name,
            )
        )
        return response

    #
    #   Initiate surveys
    #

    async def _async_initiate_survey(self, survey_name: str, resource_guid: str) -> str:
        """Initiate a survey of the survey_name on the target resource. Async Version.

        Parameters
        ----------
        survey_name: str
            The name of the survey to initiate.
        resource_guid : str
            The GUID of the resource to be surveyed.

        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """

        url = f"{self.curation_command_root}/governance-action-types/initiate"

        body = {
            "class": "InitiateGovernanceActionTypeRequestBody",
            "governanceActionTypeQualifiedName": survey_name,
            "actionTargets": [
                {
                    "class": "NewActionTarget",
                    "actionTargetName": "serverToSurvey",
                    "actionTargetGUID": resource_guid.strip(),
                }
            ],
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "Action not initiated")

    def initiate_postgres_database_survey(self, postgres_database_guid: str) -> str:
        """Initiate a postgres database survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "PostgreSQLSurvey:survey-postgres-database", postgres_database_guid
            )
        )
        return response

    def initiate_postgres_server_survey(self, postgres_server_guid: str) -> str:
        """Initiate a postgres server survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "PostgreSQLSurvey:survey-postgres-server", postgres_server_guid
            )
        )
        return response

    def initiate_file_folder_survey(
            self,
            file_folder_guid: str,
            survey_name: str = "FileSurveys:survey-folder",
    ) -> str:
        """Initiate a file folder survey - async version

        Parameters:
        ----------
            file_folder_guid: str
                The GUID of the File Folder that we wish to survey.
            survey_name: str, optional
                The unique name of the survey routine to execute. Default surveys all folders.

        Returns:
        -------
            str:
                The guid of the survey being run.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PyegeriaAPIException: If the API response indicates a server side error.
            PyegeriaUnauthorizedException:

        Notes:
            There are multiple kinds of file folder surveys available, each with their own purpose. They are described
            in the Core Content Brain.

            File Folder Survey Names currently include::
            - Egeria:GovernanceActionType:AssetSurvey:survey-folders
            - Egeria:GovernanceActionType:AssetSurvey:survey-folder-and-files
            - Egeria:GovernanceActionType:AssetSurvey:survey-all-folders
            - Egeria:GovernanceActionType:AssetSurvey:survey-all-folders-and-files


        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                survey_name,
                file_folder_guid,
            )
        )
        return response

    def initiate_file_survey(self, file_guid: str) -> str:
        """Initiate a file survey"""
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey("FileSurveys:survey-data-file", file_guid)
        )
        return response

    def initiate_kafka_server_survey(self, kafka_server_guid: str) -> str:
        """Initiate survey of a kafka server.
        Parameters
        ----------
        kafka_server_guid : str
            The GUID of the Kafka server to be surveyed.


        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "ApacheKafkaSurveys:survey-kafka-server", kafka_server_guid
            )
        )
        return response

    def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
        """Initiate survey of a Unity Catalog server. Async Version.
        Parameters
        ----------
        uc_server_guid : str
            The GUID of the Kafka server to be surveyed.


        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "UnityCatalogSurveys:survey-unity-catalog-server", uc_server_guid
            )
        )
        return response

    def initiate_uc_schema_survey(self, uc_schema_guid: str) -> str:
        """Initiate survey of a Unity Catalog schema. Async Version.
        Parameters
        ----------
        uc_schema_guid : str
            The GUID of the Kafka server to be surveyed.



        Returns
        -------
        str
            The GUID of the initiated action or "Action not initiated" if the action was not initiated.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_survey(
                "UnityCatalogSurveys:survey-unity-catalog-schema", uc_schema_guid
            )
        )
        return response

    # async def _async_initiate_uc_function_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_function_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response
    #
    # async def _async_initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response
    #
    # async def _async_initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     server = self.view_server if server is None else server
    #     url = (f"{self.curation_command_root}/governance-action-types/"
    #            f"initiate")
    #
    #     body = {"class": "InitiateGovernanceActionTypeRequestBody",
    #             "governanceActionTypeQualifiedName": "AssetSurvey:survey-unity-catalog-server", "actionTargets": [
    #             {"class": "NewActionTarget", "actionTargetName": "serverToSurvey", "actionTargetGUID": uc_server_guid}]}
    #     response = await self._async_make_request("POST", url, body)
    #     return response.json().get("guid", "Action not initiated")
    #
    # def initiate_uc_server_survey(self, uc_server_guid: str) -> str:
    #     """ Initiate survey of a Unity Catalog server. Async Version.
    #     Parameters
    #     ----------
    #     Unity Catalog_server_guid : str
    #         The GUID of the Kafka server to be surveyed.
    #
    #     server : str, optional
    #         The name of the server. If not provided, the default server name is used.
    #
    #     Returns
    #     -------
    #     str
    #         The GUID of the initiated action or "Action not initiated" if the action was not initiated.
    #
    #     """
    #     loop = asyncio.get_event_loop()
    #     response = loop.run_until_complete(self._async_initiate_uc_server_survey(uc_server_guid))
    #     return response

    #
    #   Initiate general engine action
    #

    async def _async_initiate_engine_action(
            self,
            qualified_name: str,
            domain_identifier: int,
            display_name: str,
            description: str,
            request_source_guids: str,
            action_targets: str,
            received_guards: [str],
            start_time: datetime,
            request_type: str,
            request_parameters: dict,
            process_name: str,
            request_src_name: str = None,
            originator_svc_name: str = None,
            originator_eng_name: str = None,
    ) -> str:
        """Create an engine action in the metadata store that will trigger the governance service associated with
        the supplied request type. The engine action remains to act as a record of the actions taken for auditing.
        Async version.

        Parameters
        ----------
            qualified_name (str): The qualified name of the governance action.
            domain_identifier (int): The domain identifier for the governance action.
            display_name (str): The display name of the governance action.
            description (str): The description of the governance action.
            request_source_guids (str): GUIDs of the sources initiating the request.
            action_targets (str): Targets of the governance action.
            received_guards (List[str]): List of guards received for the action.
            start_time (datetime): The start time for the governance action.
            request_type (str): The type of the governance action request.
            request_parameters (dict): Additional parameters for the governance action.
            process_name (str): The name of the associated governance action process.
            request_src_name (str, optional): The name of the request source. Defaults to None.
            originator_svc_name (str, optional): The name of the originator service. Defaults to None.
            originator_eng_name (str, optional): The name of the originator engine. Defaults to None.

        Returns
        -------
            str: The GUID (Globally Unique Identifier) of the initiated governance action.

        Raises
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note
        ----
            The `start_time` parameter should be a `datetime` object representing the start time of the
            governance action.


        """

        url = (
            f"{self.curation_command_root}/governance-engines/"
            f"engine-actions/initiate"
        )
        body = {
            "class": "GovernanceActionRequestBody",
            "qualifiedName": qualified_name + str(int(start_time.timestamp())),
            "domainIdentifier": domain_identifier,
            "displayName": display_name,
            "description": description,
            "requestSourceGUIDs": request_source_guids,
            "actionTargets": action_targets,
            "receivedGuards": received_guards,
            "startTime": int(start_time.timestamp() * 1000),
            "requestType": request_type,
            "requestParameters": request_parameters,
            "processName": process_name,
            "requestSourceName": request_src_name,
            "originatorServiceName": originator_svc_name,
            "originatorEngineName": originator_eng_name,
        }
        new_body = body_slimmer(body)
        response = await self._async_make_request("POST", url, new_body)
        return response.json().get("guid", "Action not initiated")

    def initiate_engine_action(
            self,
            qualified_name: str,
            domain_identifier: int,
            display_name: str,
            description: str,
            request_source_guids: str,
            action_targets: str,
            received_guards: [str],
            start_time: datetime,
            request_type: str,
            request_parameters: dict,
            process_name: str,
            request_src_name: str = None,
            originator_svc_name: str = None,
            originator_eng_name: str = None,
    ) -> str:
        """Create an engine action in the metadata store that will trigger the governance service associated with
        the supplied request type. The engine action remains to act as a record of the actions taken for auditing.

        Parameters
        ----------
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

        Returns
        -------
            str: The GUID (Globally Unique Identifier) of the initiated governance action.

        Raises
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
            this exception is raised with details from the response content.

        Note
        ----
            The `start_time` parameter should be a `datetime` object representing the start time of the
            governance action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_initiate_engine_action(
                qualified_name,
                domain_identifier,
                display_name,
                description,
                request_source_guids,
                action_targets,
                received_guards,
                start_time,
                request_type,
                request_parameters,
                process_name,
                request_src_name,
                originator_svc_name,
                originator_eng_name,
            )
        )
        return response

    async def _async_get_catalog_targets(
            self,
            integ_connector_guid: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = "CatalogTarget",
    ) -> list | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.
        Async version.

        Parameters:
        ----------
            integ_connector_guid: str
              The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        Returns:
        -------
            [dict]: The list of catalog targets JSON objects.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PyegeriaAPIException: If the API response indicates a server side error.
            PyegeriaUnauthorizedException:
        """

        validate_guid(integ_connector_guid)

        url = f"{self.curation_command_root}/integration-connectors/{integ_connector_guid}/catalog-targets"


        response = await self._async_make_request("GET", url)
        elements = response.json().get("elements", "no targets")
        if isinstance(elements, str):
            logger.info("No catalog targets found for this integration connector.")
            return elements
        if output_format != "JSON":
            logger.info(f"Found targets, output_format: {output_format}, and report_spec: {report_spec}")
            return self._generate_catalog_target_output(elements, None, self.CATALOG_TARGET_LABEL,
                                                    output_format=output_format,report_spec=report_spec)
        return elements

    def get_catalog_targets(
            self,
            integ_connector_guid: str,
            start_from: int = 0,
            page_size: int = 0,
            output_format: str = "JSON",
            report_spec: str | dict = "CatalogTarget",
    ) -> list | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.

        Parameters:
        ----------
            integ_connector_guid: str
              The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        Returns:
        -------
            [dict]: The list of catalog targets JSON objects.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PyegeriaAPIException: If the API response indicates a server side error.
            PyegeriaUnauthorizedException:
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_targets(integ_connector_guid, start_from, page_size,
                                            output_format=output_format,
                                            report_spec=report_spec)
        )
        return response

    async def _async_get_catalog_target(self, relationship_guid: str,
                                        output_format: str = "JSON",
                                        report_spec: str | dict = "CatalogTarget",
                                        body: dict | GetRequestBody = None) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector. Further Information:
        https://egeria-project.org/concepts/integration-connector/ .    Async version.

        Parameters:
        ----------
            relationship_guid: str
                The GUID (Globally Unique Identifier) identifying the catalog targets for an integration connector.

        Returns:
        -------
            dict: JSON structure of the catalog target.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PyegeriaAPIException: If the API response indicates a server side error.
            PyegeriaUnauthorizedException:
        """

        validate_guid(relationship_guid)

        url = str(HttpUrl(f"{self.curation_command_root}/catalog-targets/{relationship_guid}"))
        response = await self._async_get_guid_request(
            url,
            _type=self.CATALOG_TARGET_LABEL,
            _gen_output=self._generate_catalog_target_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )
        return response

    def get_catalog_target(self, relationship_guid: str,
                           output_format: str = "JSON",
                           report_spec: str | dict = "CatalogTarget",
                           body: dict | GetRequestBody = None) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector.  Further Information:
        https://egeria-project.org/concepts/integration-connector/ .

        Parameters:
        ----------
            relationship_guid: str
                The GUID (Globally Unique Identifier) identifying the catalog targets for an integration connector.

        Returns:
        -------
            dict: JSON structure of the catalog target.

        Raises:
        ------
            PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                       this exception is raised with details from the response content.
            PyegeriaAPIException: If the API response indicates a server side error.
            PyegeriaUnauthorizedException:
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_catalog_target(relationship_guid,
                                           output_format=output_format,
                                           report_spec=report_spec,
                                           body=body)
        )
        return response

    async def _async_add_catalog_target(
            self,
            integ_connector_guid: str,
            metadata_element_guid: str,
            catalog_target_name: str,
            connection_name: str = None,
            metadata_src_qual_name: str = None,
            config_properties: dict = None,
            template_properties: dict = None,
            permitted_sync: str = "BOTH_DIRECTIONS",
            delete_method: str = "ARCHIVE",
    ) -> str:
        """Add a catalog target to an integration connector and .
        Async version.

        Parameters:
        ----------
        integ_connector_guid: str
            The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        metadata_element_guid: str
            The specific metadata element target we want to retrieve.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
                Returns:
        -------
            Relationship GUID for the catalog target,

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:
        """

        validate_guid(integ_connector_guid)
        validate_guid(metadata_element_guid)

        url = (
            f"{self.curation_command_root}/integration-connectors/"
            f"{integ_connector_guid}/catalog-targets/{metadata_element_guid}"
        )
        body = {
            "catalogTargetName": catalog_target_name,
            "metadataSourceQualifiedName": metadata_src_qual_name,
            "configProperties": config_properties,
            "templateProperties": template_properties,
            "connectionName": connection_name,
            "permittedSynchronization": permitted_sync,
            "deleteMethod": delete_method,
        }

        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "No Guid returned")

    def add_catalog_target(
            self,
            integ_connector_guid: str,
            metadata_element_guid: str,
            catalog_target_name: str,
            connection_name: str = None,
            metadata_src_qual_name: str = None,
            config_properties: dict = None,
            template_properties: dict = None,
            permitted_sync: str = "BOTH_DIRECTIONS",
            delete_method: str = "ARCHIVE",
    ) -> str:
        """Add a catalog target to an integration connector and .

        Parameters:
        ----------
        integ_connector_guid: str
            The GUID (Globally Unique Identifier) of the integration connector used to retrieve catalog targets.
        metadata_element_guid: str
            The specific metadata element target we want to retrieve.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
                Returns:
        -------
            Relationship GUID for the catalog target,

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_catalog_target(
                integ_connector_guid,
                metadata_element_guid,
                catalog_target_name,
                connection_name,
                metadata_src_qual_name,
                config_properties,
                template_properties,
                permitted_sync,
                delete_method,
            )
        )
        return response

    async def _async_update_catalog_target(
            self,
            relationship_guid: str,
            catalog_target_name: str,
            connection_name: str = None,
            metadata_src_qual_name: str = None,
            config_properties: dict = None,
            template_properties: dict = None,
            permitted_sync: str = "BOTH_DIRECTIONS",
            delete_method: str = "ARCHIVE",
    ) -> None:
        """Update a catalog target to an integration connector.
        Async version.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) of the relationship used to retrieve catalog targets.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
        Returns:
        -------
            None

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:
        """

        validate_guid(relationship_guid)

        url = (
            f"{self.curation_command_root}/catalog-targets/"
            f"{relationship_guid}/update"
        )
        body = {
            "catalogTargetName": catalog_target_name,
            "metadataSourceQualifiedName": metadata_src_qual_name,
            "configProperties": config_properties,
            "templateProperties": template_properties,
            "connectionName": connection_name,
            "permittedSynchronization": permitted_sync,
            "deleteMethod": delete_method,
        }
        await self._async_make_request("POST", url, body)
        return

    def update_catalog_target(
            self,
            relationship_guid: str,
            catalog_target_name: str,
            connection_name: str = None,
            metadata_src_qual_name: str = None,
            config_properties: dict = None,
            template_properties: dict = None,
            permitted_sync: str = "BOTH_DIRECTIONS",
            delete_method: str = "ARCHIVE",
    ) -> None:
        """Update a catalog target to an integration connector.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) of the relationship used to retrieve catalog targets.
        catalog_target_name : dict
            Name of the catalog target to add.
        connection_name: str, default = None
            Optional name of connection to use for this catalog target when multiple connections defined.
        metadata_src_qual_name: str
            The qualified name of the metadata source for the catalog target
        config_properties: dict
            Configuration properties for the catalog target
        template_properties: dict
            Template properties to pass
        permitted_sync: str, default = BOTH_DIRECTIONS
            Direction the metadata is allowed to flow (BOTH_DIRECTIONS, FROM_THIRD_PARTH, TO_THIRD_PARTY
        delete_method: str, default = ARCHIVE
            Controls the type of delete. Use ARCHIVE for lineage considerations. Alternative is SOFT_DELETE.
        server: str, optional
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_catalog_target(
                relationship_guid,
                catalog_target_name,
                connection_name,
                metadata_src_qual_name,
                config_properties,
                template_properties,
                permitted_sync,
                delete_method,
            )
        )
        return

    async def _async_remove_catalog_target(self, relationship_guid: str) -> None:
        """Remove a catalog target to an integration connector. Async version.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) identifying the catalog target relationship.

        Returns:
        -------
            None

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:
        """

        validate_guid(relationship_guid)

        url = (
            f"{self.curation_command_root}/catalog-targets/"
            f"{relationship_guid}/remove"
        )

        await self._async_make_request("POST", url)
        return

    def remove_catalog_target(self, relationship_guid: str) -> None:
        """Remove a catalog target to an integration connector.

        Parameters:
        ----------
        relationship_guid: str
            The GUID (Globally Unique Identifier) identifying the catalog target relationship.

        Returns:
        -------
            None

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_catalog_target(relationship_guid))
        return

    #
    #   Get information about technologies
    #

    async def _async_get_tech_types_for_open_metadata_type(
            self,
            type_name: str,
            tech_name: str,
            start_from: int = 0,
            page_size: int = 0,
    ) -> list | str:
        """Retrieve the list of deployed implementation type metadata elements linked to a particular
        open metadata type.. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        tech_name: str
            The technology name we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/types
        """

        # validate_name(type_name)
        url = (
            f"{self.curation_command_root}/open-metadata-types/"
            f"{type_name}/technology-types"
        )
        body = {"filter": tech_name}

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elements", "no tech found")

    def get_tech_types_for_open_metadata_type(
            self,
            type_name: str,
            tech_name: str,
            start_from: int = 0,
            page_size: int = 0,
    ) -> list | str:
        """Retrieve the list of deployed implementation type metadata elements linked to a particular
        open metadata type.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        tech_name: str
            The technology name we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        More information can be found at: https://egeria-project.org/types
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tech_types_for_open_metadata_type(
                type_name, tech_name, start_from, page_size
            )
        )
        return response

    async def _async_get_tech_type_detail(self, filter: str = None, body: dict | FilterRequestBody = None,
                                          output_format: str = "JSON", report_spec: str | dict = "TechType",
                                          **kwargs) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
            and contain no wild cards. Async version.
        Parameters
        ----------
        filter : str
            The name of the technology type to retrieve detailed information for.
        body: dict | FilterRequestBody
            If provided, the information in the body supersedes the other parameters and allows more advanced requests.

        Returns
        -------
        list[dict] | str
            A list of dictionaries containing the detailed information for the specified technology type.
            If the technology type is not found, returns the string "no type found".
        Raises
        ------
                PyegeriaException
        ValidationError

        Notes
        -----
        More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        Sample body:
        {
          "class" : "FilterRequestBody",
          "filter" : "Root Technology Type",
          "startFrom": 0,
          "pageSize": 10,
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "includeOnlyClassifiedElements" : ["Template"]
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """

        # validate_name(type_name)
        url = str(HttpUrl(f"{self.curation_command_root}/technology-types/by-name"))
        if body is None:
            body = {
                "class": "FilterRequestBody",
                "filter": filter
            }

        response = await self._async_make_request("POST", url, body)
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(element) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_tech_type_output(element, filter, "ValidMetadataValue",
                                                   output_format, report_spec)
        return element

    def get_tech_type_detail(self, filter: str = None, body: dict | FilterRequestBody = None,
                             output_format: str = "JSON", report_spec: str | dict = "TechType", **kwargs) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
                 and contain no wild cards.
             Parameters
             ----------
             filter : str
                 The name of the technology type to retrieve detailed information for.
             body: dict | FilterRequestBody
                 If provided, the information in the body supersedes the other parameters and allows more advanced requests.

             Returns
             -------
             list[dict] | str
                 A list of dictionaries containing the detailed information for the specified technology type.
                 If the technology type is not found, returns the string "no type found".
             Raises
             ------
                     PyegeriaException
             ValidationError

             Notes
             -----
             More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
             Sample body:
             {
               "class" : "FilterRequestBody",
               "filter" : "Root Technology Type",
               "startFrom": 0,
               "pageSize": 10,
               "asOfTime" : "{{$isoTimestamp}}",
               "effectiveTime" : "{{$isoTimestamp}}",
               "includeOnlyClassifiedElements" : ["Template"]
               "forLineage" : false,
               "forDuplicateProcessing" : false,
               "limitResultsByStatus" : ["ACTIVE"],
               "sequencingOrder" : "PROPERTY_ASCENDING",
               "sequencingProperty" : "qualifiedName"
             }
             """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tech_type_detail(filter, body=body, output_format=output_format, report_spec=report_spec)
        )
        return response


    async def _async_get_tech_type_hierarchy(self, filter: str = None, body: dict | FilterRequestBody = None,
                                          output_format: str = "JSON", report_spec: str | dict = "TechType",
                                          **kwargs) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
            and contain no wild cards. Async version.
        Parameters
        ----------
        filter : str
            The name of the technology type to retrieve detailed information for.
        body: dict | FilterRequestBody
            If provided, the information in the body supersedes the other parameters and allows more advanced requests.

        Returns
        -------
        list[dict] | str
            A list of dictionaries containing the detailed information for the specified technology type.
            If the technology type is not found, returns the string "no type found".
        Raises
        ------
                PyegeriaException
        ValidationError

        Notes
        -----
        More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
        Sample body:
        {
          "class" : "FilterRequestBody",
          "filter" : "Root Technology Type",
          "startFrom": 0,
          "pageSize": 10,
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "includeOnlyClassifiedElements" : ["Template"]
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """

        # validate_name(type_name)
        if filter == "*":
            filter = "Root Technology Type"

        url = str(HttpUrl(f"{self.curation_command_root}/technology-types/hierarchy"))
        if body is None:
            body = {
                "class": "FilterRequestBody",
                "filter": filter
            }
        body_s = body_slimmer(body)
        response = await self._async_make_request("POST", url, body_s)
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(element) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_tech_type_output(element, filter, "ValidMetadataValue",
                                                   output_format, report_spec)
        return element

    def get_tech_type_hierarchy(self, filter: str = None, body: dict | FilterRequestBody = None,
                             output_format: str = "JSON", report_spec: str | dict = "TechType", **kwargs) -> list | str:
        """Retrieve the details of the named technology type. This name should be the name of the technology type
                 and contain no wild cards.
             Parameters
             ----------
             filter : str
                 The name of the technology type to retrieve detailed information for.
             body: dict | FilterRequestBody
                 If provided, the information in the body supersedes the other parameters and allows more advanced requests.

             Returns
             -------
             list[dict] | str
                 A list of dictionaries containing the detailed information for the specified technology type.
                 If the technology type is not found, returns the string "no type found".
             Raises
             ------
                     PyegeriaException
             ValidationError

             Notes
             -----
             More information can be found at: https://egeria-project.org/concepts/deployed-implementation-type
             Sample body:
             {
               "class" : "FilterRequestBody",
               "filter" : "Root Technology Type",
               "startFrom": 0,
               "pageSize": 10,
               "asOfTime" : "{{$isoTimestamp}}",
               "effectiveTime" : "{{$isoTimestamp}}",
               "includeOnlyClassifiedElements" : ["Template"]
               "forLineage" : false,
               "forDuplicateProcessing" : false,
               "limitResultsByStatus" : ["ACTIVE"],
               "sequencingOrder" : "PROPERTY_ASCENDING",
               "sequencingProperty" : "qualifiedName"
             }
             """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tech_type_hierarchy(filter, body=body, output_format=output_format, report_spec=report_spec)
        )
        return response





    async def _async_get_template_guid_for_technology_type(self, type_name: str) -> str:
        details = await self._async_get_tech_type_detail(type_name)
        if isinstance(details, dict):
            return details.get("catalogTemplates", {})[0].get("relatedElement", {}).get("elementHeader", {}).get("guid",
                                                                                                                 None)
        else:
            return None

    def get_template_guid_for_technology_type(self, type_name: str) -> str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_template_guid_for_technology_type(type_name)
        )
        return response

    async def async_find_technology_types(
            self,
            search_string: str = "*",
            start_from: int = 0,
            page_size: int = 0,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = True,
            output_format: str = "JSON",
            report_spec: str | dict = "TechType"
    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        starts_with : bool, optional
           Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
           Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
           Whether to ignore case while searching engine actions. Default is True.

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `0`.
        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        if search_string == "*":
            search_string = None

        url = (
            f"{self.curation_command_root}/technology-types/"
            f"by-search-string"
        )
        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string,
            "startsWith": starts_with,
            "endsWith": ends_with,
            "ignoreCase": ignore_case,
            "startFrom": start_from,
            "pageSize": page_size,
            "limitResultsByStatus": ["ACTIVE"],
            "sequencingOrder": "PROPERTY_ASCENDING",
            "sequencingProperty": "qualifiedName"
        }

        response = await self._async_make_request("POST", url, body)
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format.upper() != 'JSON':  # return a simplified markdown representation
            # logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_tech_type_output(elements, search_string, "TechType",
                                                   output_format, report_spec)
        return elements


    def find_technology_types(
            self,
            search_string: str = "*",
            start_from: int = 0,
            page_size: int = 0,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = True,
            output_format: str = "JSON",
            report_spec: str | dict = "TechType",
    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_find_technology_types(
                search_string,
                start_from,
                page_size,
                starts_with,
                ends_with,
                ignore_case,
                output_format,
                report_spec
            )
        )
        return response

    async def async_find_technology_types_body(
            self,
            search_string: str = "*",
            start_from: int = 0,
            page_size: int = 0,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = True,
            output_format: str = "JSON",
            report_spec: str | dict = "TechType",
            body: dict | SearchStringRequestBody = None
    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
        ----------
        type_name: str
            The technology type we are looking for.
        starts_with : bool, optional
           Whether to search engine actions that start with the given search string. Default is False.

        ends_with : bool, optional
           Whether to search engine actions that end with the given search string. Default is False.

        ignore_case : bool, optional
           Whether to ignore case while searching engine actions. Default is True.

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `0`.
        body: dict | SearchStringRequestBody, optional
            Full request body, if provided, overrides other parameters.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        if search_string == "*":
            search_string = None

        url = str(HttpUrl(f"{self.curation_command_root}/technology-types/by-search-string"))
        response = await self._async_find_request(url, _type="TechType", _gen_output=self._generate_tech_type_output,
                                                  search_string=search_string, include_only_classification_names=None,
                                                  metadata_element_subtypes='ValidMetadataValue',
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec, body=body)

        return response


    def find_technology_types_body(
            self,
            search_string: str = "*",
            start_from: int = 0,
            page_size: int = 0,
            starts_with: bool = False,
            ends_with: bool = False,
            ignore_case: bool = True,
            output_format: str = "JSON",
            report_spec: str = "TechType",
            body: dict | SearchStringRequestBody = None

    ) -> list | str:
        """Retrieve the list of technology types that contain the search string. Async version.

        Parameters:
            output_format ():
            report_spec ():
            body ():
        ----------
        type_name: str
            The technology type we are looking for.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.async_find_technology_types_body(
                search_string,
                start_from,
                page_size,
                starts_with,
                ends_with,
                ignore_case,
                output_format,
                report_spec,
                body
            )
        )
        return response

    async def _async_get_all_technology_types(
            self, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str = "TechType"
    ) -> list | str:
        """Get all technology types - async version"""
        return await self._async_find_technology_types(search_string = "*", start_from = start_from,
                                                       page_size = page_size, output_format = output_format,
                                                       report_spec = report_spec)

    def get_all_technology_types(
            self, start_from: int = 0, page_size: int = 0, output_format: str = "JSON", report_spec: str = "TechType"
    ) -> list | str:
        """Get all technology types"""
        return self.find_technology_types(search_string = "*", start_from = start_from, page_size = page_size,
                                          output_format = output_format, report_spec = report_spec)

    def print_engine_action_summary(self, governance_action: dict):
        """print_governance_action_summary

        Print all the governance actions with their status, in the server.

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        PyegeriaException        """
        if governance_action:
            name = governance_action.get("displayName")
            if not name:
                name = governance_action.get("qualifiedName")
            action_status = governance_action.get("action_status")
            if governance_action.get("completion_guards"):
                completion_guards = governance_action.get("completion_guards")
            else:
                completion_guards = "\t"
            if governance_action.get("process_name"):
                process_name = governance_action.get("process_name")
            else:
                process_name = "\t"
            if governance_action.get("completion_message"):
                completion_message = governance_action.get("completion_message")
            else:
                completion_message = ""
            print(
                action_status
                + "\n\t| "
                + name
                + "\t| "
                + process_name
                + "\t| "
                + "%s" % ", ".join(map(str, completion_guards))
                + "\t| "
                + completion_message
            )

    def print_engine_actions(self):
        """print_governance_actions

        Print all the governance actions with their status, in the server.

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        PyegeriaException
        """
        governance_actions = self.get_engine_actions()
        if governance_actions is not None:
            for x in range(len(governance_actions)):
                self.print_engine_action_summary(governance_actions[x])

    async def _async_get_technology_type_elements(
            self,
            filter: str,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = 0,
            get_templates: bool = False,
            output_format: str = "JSON", report_spec: str = "Tech-Type-Elements",
            body: dict | FilterRequestBody = None,
    ) -> list | str:
        """Retrieve the elements for the requested deployed implementation type. There are no wildcards allowed
        in the name. Async version.

        Parameters:
            output_format ():
            report_spec ():
            body ():
        ----------
        filter: str
            The name of the deployed technology implementation type to retrieve elements for.
                effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `0`.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        skip_templates = "Template" if not get_templates else ""
        validate_name(filter)

        url = (
            f"{self.curation_command_root}/technology-types/elements"
        )
        if body is None:
            body = {
                    "class" : "FilterRequestBody",
                    "filter": filter,
                    "effective_time": effective_time,
                    "skipClassifiedElements": [skip_templates],
                    "startFrom": start_from,
                    "pageSize": page_size
                    }

        response = await self._async_get_name_request(url, "TechTypeElement",  self._generate_tech_type_element_output, filter, None, start_from, page_size, output_format, report_spec, body)
        return response


    def get_technology_type_elements(
            self,
            filter: str,
            effective_time: str = None,
            start_from: int = 0,
            page_size: int = 0,
            get_templates: bool = False,
            output_format: str = "JSON", report_spec: str = "Tech-Type-Elements",
            body: dict | FilterRequestBody = None,
    ) -> list | str:
        """Retrieve the elements for the requested deployed implementation type. There are no wildcards allowed
        in the name.

        Parameters:
            output_format ():
            report_spec ():
            body ():
        ----------
        filter: str
            The name of the deployed technology implementation type to retrieve elements for.
                effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        start_from : int, optional
           The index from which to start fetching the engine actions. Default is 0.

        page_size : int, optional
           The maximum number of engine actions to fetch in a single request. Default is `0`.

        Returns:
        -------
            [dict] | str: List of elements describing the technology - or "no tech found" if not found.

        Raises:
        ------
        PyegeriaInvalidParameterException: If the API response indicates an error (non-200 status code),
                                   this exception is raised with details from the response content.
        PyegeriaAPIException: If the API response indicates a server side error.
        PyegeriaUnauthorizedException:

        Notes
        -----
        For more information see: https://egeria-project.org/concepts/deployed-implementation-type
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_technology_type_elements(filter, effective_time, start_from, page_size, get_templates, output_format,
                                                     report_spec, body)
        )
        return response


if __name__ == "__main__":
    print("Main-Automated Curation")

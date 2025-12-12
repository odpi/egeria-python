"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module allows users to query the available (registered) capabilities of Egeria. Detailed information is returned
to provide both insight and understanding in how to use these capabilities. For example, when configuring an Egeria
integration service, it is import registered_info.pyant to know what companion service it depends on so that you can
make sure the companion service is also configured and running.

"""

from typing import Optional

from pyegeria._server_client import ServerClient
from pyegeria.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.output_formatter import (
    generate_output,
    populate_columns_from_properties,
)


class RegisteredInfo(ServerClient):
    """Client to discover Egeria services and capabilities

    Parameters:
    ----------
        view_server: str
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

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        if view_server is None:
            server_name = "NA"
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.reg_command_root = (
            f"{self.platform_url}/open-metadata/platform-services/users/"
            f"{self.user_id}/server-platform/registered-services"
        )

    def list_registered_svcs(
        self,
        kind: str = None,
        *,
        output_format: str = "DICT",
        report_spec: str | dict = None,
    ) -> list | str:
        """Get the registered services for the OMAG Server Platform

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
        PyegeriaInvalidParameterException
            If the response code is not 200.
        PyegeriaAPIException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        if kind is None or kind == "help":
            return """
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
            """
        if kind == "all":
            url = f"{self.reg_command_root}"
        else:
            url = f"{self.reg_command_root}/{kind}"
        response = self.make_request("GET", url)
        elements = response.json().get("services", [])
        # Fallback to raw if no elements or output not requested
        if output_format in (None, "JSON") and report_spec is None:
            return elements or "No services found"

        # Choose a report spec
        columns_struct = None
        if isinstance(report_spec, str):
            columns_struct = select_report_spec(report_spec, output_format)
        elif isinstance(report_spec, dict):
            columns_struct = get_report_spec_match(report_spec, output_format)
        else:
            columns_struct = select_report_spec("Registered-Services", output_format)
        if columns_struct is None:
            columns_struct = select_report_spec("Default", output_format)

        return self._generate_registered_info_output(
            elements=elements,
            filter=kind,
            entity_type_name="Registered-Services",
            output_format=output_format,
            report_spec=columns_struct,
            extract_func=self._extract_registered_service_properties,
        )

    def list_severity_definitions(
        self,
        *,
        output_format: str = "DICT",
        report_spec: str | dict = None,
    ) -> list | str:
        """Get the registered severities for the OMAG Server

        Parameters
        ----------

        Returns
        -------
        dict | str
            Return a dictionary containing the registered services for the specified platform.
        Raises
        ------
        PyegeriaInvalidParameterException
            If the response code is not 200.
        PyegeriaAPIException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/open-metadata/repository-services"
            f"/users/{self.user_id}/audit-log/severity-definitions"
        )
        response = self.make_request("GET", url)
        elements = response.json().get("severities", [])

        if output_format in (None, "JSON") and report_spec is None:
            return elements or "No severities found"

        columns_struct = None
        if isinstance(report_spec, str):
            columns_struct = select_report_spec(report_spec, output_format)
        elif isinstance(report_spec, dict):
            columns_struct = get_report_spec_match(report_spec, output_format)
        else:
            columns_struct = select_report_spec("Severity-Definitions", output_format)
        if columns_struct is None:
            columns_struct = select_report_spec("Default", output_format)

        return self._generate_registered_info_output(
            elements=elements,
            filter=None,
            entity_type_name="Severity-Definitions",
            output_format=output_format,
            report_spec=columns_struct,
            extract_func=self._extract_severity_properties,
        )

    def list_asset_types(
        self,
        *,
        output_format: str = "DICT",
        report_spec: str | dict = None,
    ) -> list | str:
        """Get the registered severities for the OMAG Server

        Parameters
        ----------

        Returns
        -------
        dict | str
            Returns a list of the asset types.

        Raises
        ------
        PyegeriaInvalidParameterException
            If the response code is not 200.
        PyegeriaAPIException:
            Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException:
            The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-catalog/assets/types"

        response = self.make_request("GET", url)
        elements = response.json().get("types", [])

        if output_format in (None, "JSON") and report_spec is None:
            return elements or "no types found"

        columns_struct = None
        if isinstance(report_spec, str):
            columns_struct = select_report_spec(report_spec, output_format)
        elif isinstance(report_spec, dict):
            columns_struct = get_report_spec_match(report_spec, output_format)
        else:
            columns_struct = select_report_spec("Asset-Types", output_format)
        if columns_struct is None:
            columns_struct = select_report_spec("Default", output_format)

        return self._generate_registered_info_output(
            elements=elements,
            filter=None,
            entity_type_name="Asset-Types",
            output_format=output_format,
            report_spec=columns_struct,
            extract_func=self._extract_asset_type_properties,
        )

    # -------------------------------
    # Helpers for report generation
    # -------------------------------
    def _extract_registered_service_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate values for a registered service element using the column spec keys.

        The registered services payload is typically a flat dict of camelCase keys, so we can
        rely on populate_columns_from_properties which maps our snake_case keys to camelCase.
        """
        return populate_columns_from_properties(element, columns_struct)

    def _extract_severity_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate values for a severity definition element."""
        return populate_columns_from_properties(element, columns_struct)

    def _extract_asset_type_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate values for an asset type listing element."""
        # API may return simple strings (type names) or dicts; support both
        if isinstance(element, str):
            # Ensure the first attribute key named 'type_name' (snake) is populated
            formats = columns_struct.get('formats') or {}
            cols = formats.get('attributes') or []
            for col in cols:
                if isinstance(col, dict) and col.get('key') == 'type_name':
                    col['value'] = element
            return columns_struct
        return populate_columns_from_properties(element, columns_struct)

    def _generate_registered_info_output(
        self,
        *,
        elements: list[dict] | dict,
        filter: Optional[str],
        entity_type_name: Optional[str],
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
        extract_func=None,
    ) -> str | list[dict]:
        """Generate output for RegisteredInfo endpoints using the common formatter.

        Args:
            elements: list or dict of items returned from the endpoint
            filter: optional filter string used in the request (for headings)
            entity_type_name: logical report spec target name
            output_format: desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
            report_spec: a FormatSet dict or name resolved beforehand
            extract_func: callable used to map element -> columns_struct values
        """
        if entity_type_name is None:
            entity_type = "Referenceable"
        else:
            entity_type = entity_type_name

        columns_struct = None
        if isinstance(report_spec, dict):
            columns_struct = report_spec
        elif isinstance(report_spec, str):
            columns_struct = select_report_spec(report_spec, output_format)
        else:
            columns_struct = select_report_spec(entity_type, output_format)

        if columns_struct is None:
            columns_struct = select_report_spec("Default", output_format)

        # Default extract function just maps columns by key
        if extract_func is None:
            extract_func = populate_columns_from_properties

        return generate_output(
            elements=elements,
            search_string=filter or "All",
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=lambda e, cs=columns_struct: extract_func(e, cs),
            get_additional_props_func=None,
            columns_struct=columns_struct,
        )


if __name__ == "__main__":
    print("Main-Registered Info")

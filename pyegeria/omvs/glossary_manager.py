"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_manager module.

"""

import asyncio
import csv
import os
from typing import List, Annotated, Literal, Optional

from loguru import logger
from pydantic import Field

from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core._globals import NO_GUID_RETURNED
from pyegeria.core._validators import validate_guid
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.models import (NewElementRequestBody, DeleteElementRequestBody, DeleteRelationshipRequestBody,
                             ReferenceableProperties, UpdateElementRequestBody, TemplateRequestBody,
                             NewRelationshipRequestBody, UpdateRelationshipRequestBody, NewClassificationRequestBody,
                             FilterRequestBody, GetRequestBody, SearchStringRequestBody,
                             DeleteClassificationRequestBody)
from pyegeria.view.output_formatter import (_extract_referenceable_properties, populate_common_columns,
                                            overlay_additional_values, resolve_output_formats)
from pyegeria.core.utils import body_slimmer, dynamic_catch

class GlossaryProperties(ReferenceableProperties):
    class_: Annotated[Literal["GlossaryProperties"], Field(alias="class")]
    language: str = "English"
    usage: str = None


class GlossaryTermProperties(ReferenceableProperties):
    class_: Annotated[Literal["GlossaryTermProperties"], Field(alias="class")]
    summary: str = None
    description: str = None
    abbreviation: str = None
    examples: str = None
    usage: str = None
    user_defined_status: str = None
    publishVersionIdentifier: str = None


class GlossaryManager(CollectionManager):
    """
    Client for the Glossary Manager View Service.

    The Glossary Manager View Service provides methods to create and manage glossaries,
    terms, and categories.

    Attributes
    ----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
            self,
            view_server: str = None,
            platform_url: str = None,
            user_id: str = None,
            user_pwd: Optional[str] = None,
            token: Optional[str] = None,
            ):
        CollectionManager.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        self.view_server = self.server_name
        self.platform_url = self.platform_url
        self.user_id = self.user_id
        self.user_pwd = self.user_pwd
        self.url_marker = "glossary-manager"


        self.glossary_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager"
    #
    #       Get Valid Values for Enumerations
    #
    @dynamic_catch
    def __validate_term_status__(self, status: str) -> bool:
        """Return True if the status is a legal glossary term status"""
        recognized_term_status = self.get_glossary_term_statuses()
        return status in recognized_term_status

    #
    #       Glossaries
    #



    @dynamic_catch
    async def _async_create_glossary(self, display_name: str, description: Optional[str] = None, language: str = "English", usage: Optional[str] = None,
                        category: Optional[str] = None, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """Create a new glossary. Async version.

        Parameters
        ----------
        display_name : str
            The name of the glossary.
        description : str, optional
            The description of the glossary.
        language : str, optional
            The language of the glossary (default is "English").
        usage : str, optional
            The usage information for the glossary.
        category : str, optional
            The category for the glossary.
        body : dict | NewElementRequestBody, optional
            If provided, the request body for creating the glossary.

        Returns
        -------
        str
            The GUID of the newly created glossary.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        if body is None:
            if isinstance(display_name, (dict, NewElementRequestBody)):
                body = display_name
            else:
                qualified_name = self.__create_qualified_name__("Glossary", display_name)
                body = {
                    "class": "NewElementRequestBody",
                    "is_own_anchor": True,
                    "properties": {
                        "class": "GlossaryProperties",
                        "displayName": display_name,
                        "qualifiedName": qualified_name,
                        "description": description,
                        "language": language,
                        "usage": usage,
                        "category": category
                        },
                    }
        response = await self._async_create_collection(body=body)
        return response

    @dynamic_catch
    def create_glossary(self, display_name: str, description: Optional[str] = None, language: str = "English",
                               usage: Optional[str] = None,
                               category: Optional[str] = None, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """Create a new glossary.

        Parameters
        ----------
        display_name : str
            The name of the glossary.
        description : str, optional
            The description of the glossary.
        language : str, optional
            The language of the glossary (default is "English").
        usage : str, optional
            The usage information for the glossary.
        category : str, optional
            The category for the glossary.
        body : dict | NewElementRequestBody, optional
            If provided, the request body for creating the glossary.

        Returns
        -------
        str
            The GUID of the newly created glossary.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary(display_name, description, language, usage, category, body)
            )
        return response

    @dynamic_catch
    async def _async_delete_glossary(self, glossary_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                                     cascade: bool = False) -> None:
        """Delete glossary. Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.
        cascade: bool, optional, default = False
            If true, then delete all terms and categories in the glossary as well.

        Returns
        -------
        None

        """

        await self._async_delete_collection(glossary_guid, body, cascade)

        logger.info(f"Deleted glossary {glossary_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_glossary(self, glossary_guid: str, body: Optional[dict | DeleteElementRequestBody] = None, cascade: bool = False) -> None:
        """Delete a new glossary.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to delete.
        cascade: bool, optional, default = False
            If true, then delete all terms and categories in the glossary as well.


        Returns
        -------
        None

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_glossary(glossary_guid, body, cascade))

    @dynamic_catch
    async def _async_update_glossary(
            self,
            glossary_guid: str,
            body: dict | UpdateElementRequestBody,
            merge_update: bool = True,
            ) -> None:
        """Update Glossary.

        Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to update.
        body: dict
            A dict containing the properties to update.

        Returns
        -------
        None

        Notes
        -----

        Sample body:

        """



        await self._async_update_collection(glossary_guid, body)
        logger.info(f"Updated glossary {glossary_guid}")

    @dynamic_catch
    def update_glossary(
            self,
            glossary_guid: str,
            body: dict | UpdateElementRequestBody,
            merge_update: bool = True,
            ) -> None:
        """Update Glossary.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to update.
        body: dict
            A dict containing the properties to update.
        is_merge_update: bool, optional, default = True
            If true, then only those properties specified in the body will be updated. If false, then all the
            properties of the glossary will be replaced with those of the body.


        Returns
        -------
        None

        Notes
        -----

        Sample body:


        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_glossary(
                glossary_guid,
                body, merge_update
                )
            )

    #
    #   add glossary classifications? is-canonical, is editing, is staging, is taxonomy?
    #   Not all show up in UML



    #
    #  Terms
    #
    @dynamic_catch
    async def _async_create_glossary_term(
            self, body: dict | NewElementRequestBody
            ) -> str:
        """Create a term for a glossary. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The request body for creating the glossary term.

        Returns
        -------
        str
            The unique GUID for the created term.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms"
        )
        return await self._async_create_element_body_request(url, "GlossaryTermProperties", body)

    @dynamic_catch
    def create_glossary_term(self, body: dict | NewElementRequestBody) -> str:
        """Create a term for a glossary.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The request body for creating the glossary term.

        Returns
        -------
        str
            The unique GUID for the created term.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary_term(body)
            )

        return response

    @dynamic_catch
    async def _async_import_glossary_terms_from_csv(
            self,
            glossary_name: str,
            filename: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            upsert: bool = True,
            verbose: bool = True,
            ) -> List[dict] | None:
        """Import glossary terms from a CSV file into the specified glossary. Async version.

        Parameters
        ----------
        glossary_name : str
            Name of the glossary to import terms into.
        filename : str
            Name of the CSV file to import terms from.
        file_path : str, optional
            Directory path to prepend to ``filename``.  Defaults to the
            ``EGERIA_GLOSSARY_PATH`` environment variable, or ``None``.
        upsert : bool, default True
            When True and a row contains a ``Qualified Name`` that matches an
            existing term, that term is updated with the row values.  When False
            (or when no qualified name is supplied) the row is always inserted as
            a new term.
        verbose : bool, default True
            When True, return a list of per-row status dicts.

        Returns
        -------
        list[dict] | None
            Per-row import status when ``verbose`` is True, otherwise None.

        Raises
        ------
        FileNotFoundError
            If the resolved file path does not exist.
        PyegeriaInvalidParameterException
            If the CSV contains unrecognised column headers.
        PyegeriaAPIException
            Raised by the server when an issue arises in processing a valid request.

        Notes
        -----
        The CSV must use the column headers exported by
        :meth:`export_glossary_to_csv`:
        ``Term Name``, ``Qualified Name``, ``Abbreviation``, ``Summary``,
        ``Description``, ``Examples``, ``Usage``, ``Version Identifier``,
        ``Status``.

        The file path is relative to the caller, not the Egeria platform.
        """
        # Check that the glossary exists and retrieve its GUID
        glossaries = self.get_glossaries_by_name(glossary_name)
        if not isinstance(glossaries, list) or len(glossaries) == 0:
            raise ValueError(f"Glossary '{glossary_name}' not found.")
        if len(glossaries) > 1:
            props_key = "properties"
            glossary_error = (
                "Multiple glossaries found - please use a qualified name from below\n"
            )
            for g in glossaries:
                g_props = g.get(props_key, g.get("glossaryProperties", {}))
                glossary_error += (
                    f"Display Name: {g_props.get('displayName', '---')}\t"
                    f"Qualified Name: {g_props.get('qualifiedName', '---')}\n"
                )
            raise ValueError(glossary_error)

        glossary_guid = glossaries[0]["elementHeader"]["guid"]

        valid_term_properties = {
            "Term Name",
            "Qualified Name",
            "Abbreviation",
            "Summary",
            "Description",
            "Examples",
            "Usage",
            "Version Identifier",
            "Status",
            }

        full_file_path = os.path.join(file_path, filename) if file_path else filename
        if not os.path.isfile(full_file_path):
            raise FileNotFoundError(
                f"CSV file not found: {full_file_path}"
                )

        create_url = (
            f"{self.platform_url}/servers/{self.view_server}"
            f"/api/open-metadata/glossary-manager/glossaries/terms"
        )

        with open(full_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            headers = csv_reader.fieldnames or []
            term_info = []

            if not all(h in valid_term_properties for h in headers):
                raise PyegeriaInvalidParameterException(
                    None,
                    context={"caller_method": "import_glossary_terms_from_csv"},
                    additional_info={"reason": "Unrecognised column headers in CSV file"},
                )

            for row in csv_reader:
                term_name = row.get("Term Name", "").strip()
                if len(term_name) < 2:
                    term_info.append(
                        {
                            "term_name": "---",
                            "qualified_name": "---",
                            "term_guid": "---",
                            "error": "Missing or too-short term name — row skipped",
                            }
                        )
                    continue

                qualified_name = row.get("Qualified Name") or None
                abbrev = row.get("Abbreviation") or None
                if abbrev == "---":
                    abbrev = None
                summary = row.get("Summary") or None
                if summary == "---":
                    summary = None
                description = row.get("Description") or None
                if description == "---":
                    description = None
                examples = row.get("Examples") or None
                if examples == "---":
                    examples = None
                usage = row.get("Usage") or None
                if usage == "---":
                    usage = None
                version = row.get("Version Identifier") or "1.0"
                status = (row.get("Status") or "DRAFT").upper()

                if not self.__validate_term_status__(status):
                    term_info.append(
                        {
                            "term_name": term_name,
                            "qualified_name": qualified_name or "---",
                            "term_guid": "---",
                            "error": f"Invalid term status '{status}' — row skipped",
                            }
                        )
                    continue

                if upsert and qualified_name:
                    # Try to find an existing term by qualified name
                    term_stuff = self.get_terms_by_name(filter_string=qualified_name)
                    if isinstance(term_stuff, str):
                        # Not found — treat as a new insert
                        pass
                    elif len(term_stuff) > 1:
                        term_info.append(
                            {
                                "term_name": term_name,
                                "qualified_name": qualified_name,
                                "error": "Multiple matching terms found — row skipped",
                                }
                            )
                        continue
                    elif len(term_stuff) == 1:
                        # Existing term found — perform a merge update
                        term_guid = term_stuff[0]["elementHeader"]["guid"]
                        update_body = body_slimmer({
                            "class": "UpdateElementRequestBody",
                            "mergeUpdate": True,
                            "properties": {
                                "class": "GlossaryTermProperties",
                                "qualifiedName": qualified_name,
                                "displayName": term_name,
                                "summary": summary,
                                "description": description,
                                "abbreviation": abbrev,
                                "examples": examples,
                                "usage": usage,
                                "publishVersionIdentifier": version,
                                },
                            })
                        await self._async_update_glossary_term(term_guid, update_body)
                        term_info.append(
                            {
                                "term_name": term_name,
                                "qualified_name": qualified_name,
                                "term_guid": term_guid,
                                "action": "updated",
                                }
                            )
                        continue

                # Insert as a new term
                term_qualified_name = qualified_name or self.__create_qualified_name__("Term", term_name)
                create_body = body_slimmer({
                    "class": "NewElementRequestBody",
                    "parentGUID": glossary_guid,
                    "parentRelationshipTypeName": "CollectionMembership",
                    "isOwnAnchor": True,
                    "parentAtEnd1": True,
                    "properties": {
                        "class": "GlossaryTermProperties",
                        "qualifiedName": term_qualified_name,
                        "displayName": term_name,
                        "summary": summary,
                        "description": description,
                        "abbreviation": abbrev,
                        "examples": examples,
                        "usage": usage,
                        "publishVersionIdentifier": version,
                        },
                    "initialStatus": status,
                    })
                resp = await self._async_make_request("POST", create_url, create_body)
                term_guid = resp.json().get("guid", NO_GUID_RETURNED)
                term_info.append(
                    {
                        "term_name": term_name,
                        "qualified_name": term_qualified_name,
                        "term_guid": term_guid,
                        "action": "created",
                        }
                    )

        return term_info if verbose else None

    @dynamic_catch
    def import_glossary_terms_from_csv(
            self,
            glossary_name: str,
            filename: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            upsert: bool = True,
            verbose: bool = True,
            ) -> List[dict] | None:
        """Import glossary terms from a CSV file into the specified glossary.

        Parameters
        ----------
        glossary_name : str
            Name of the glossary to import terms into.
        filename : str
            Name of the CSV file to import terms from.
        file_path : str, optional
            Directory path to prepend to ``filename``.  Defaults to the
            ``EGERIA_GLOSSARY_PATH`` environment variable, or ``None``.
        upsert : bool, default True
            When True and a row contains a ``Qualified Name`` that matches an
            existing term, that term is updated with the row values.  When False
            (or when no qualified name is supplied) the row is always inserted as
            a new term.
        verbose : bool, default True
            When True, return a list of per-row status dicts.

        Returns
        -------
        list[dict] | None
            Per-row import status when ``verbose`` is True, otherwise None.

        Raises
        ------
        FileNotFoundError
            If the resolved file path does not exist.
        PyegeriaInvalidParameterException
            If the CSV contains unrecognised column headers.
        PyegeriaAPIException
            Raised by the server when an issue arises in processing a valid request.

        Notes
        -----
        The CSV must use the column headers exported by
        :meth:`export_glossary_to_csv`:
        ``Term Name``, ``Qualified Name``, ``Abbreviation``, ``Summary``,
        ``Description``, ``Examples``, ``Usage``, ``Version Identifier``,
        ``Status``.

        The file path is relative to the caller, not the Egeria platform.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_import_glossary_terms_from_csv(
                glossary_name, filename, file_path, upsert, verbose
                )
            )

    def load_terms_from_csv_file(
            self,
            glossary_name: str,
            filename: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            upsert: bool = True,
            verbose: bool = True,
            ) -> List[dict] | None:
        """Backward-compatible alias for :meth:`import_glossary_terms_from_csv`."""
        return self.import_glossary_terms_from_csv(
            glossary_name, filename, file_path, upsert, verbose
            )

    @dynamic_catch
    async def _async_export_glossary_to_csv(
            self,
            glossary_guid: str,
            target_file: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            ) -> int:
        """Export all terms in a glossary to a CSV file. Async version.

        Parameters
        ----------
        glossary_guid : str
            GUID of the glossary whose terms are to be exported.
        target_file : str
            Output file name (without directory).
        file_path : str, optional
            Directory in which to write ``target_file``.  Defaults to the
            ``EGERIA_GLOSSARY_PATH`` environment variable, or the current
            working directory when not set.

        Returns
        -------
        int
            Number of term rows written to the CSV.

        Notes
        -----
        The output CSV uses the same column headers expected by
        :meth:`import_glossary_terms_from_csv` so a round-trip
        export → edit → import is straightforward.
        """
        # Retrieve all terms belonging to this glossary.
        # anchor_scope_guid scopes the search to the specific glossary.
        term_list = await self._async_find_glossary_terms(
            search_string="*",
            anchor_scope_guid=glossary_guid,
            output_format="JSON",
            page_size=0,
            )
        if isinstance(term_list, str):
            # No terms found
            term_list = []

        header = [
            "Term Name",
            "Qualified Name",
            "Abbreviation",
            "Summary",
            "Description",
            "Examples",
            "Usage",
            "Version Identifier",
            "Status",
            ]

        full_file_path = os.path.join(file_path, target_file) if file_path else target_file
        target_dir = os.path.dirname(os.path.abspath(full_file_path))
        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError as exc:
            # The configured path (e.g. /home/jovyan from EGERIA_GLOSSARY_PATH) may not
            # be accessible on this OS.  Fall back to writing in the current directory
            # and let the caller know.
            import warnings
            warnings.warn(
                f"Cannot create directory '{target_dir}' ({exc}); "
                f"writing '{target_file}' to the current working directory instead.",
                RuntimeWarning,
                stacklevel=2,
            )
            full_file_path = target_file

        with open(full_file_path, mode="w", newline="", encoding="utf-8") as file:
            csv_writer = csv.DictWriter(file, fieldnames=header)
            csv_writer.writeheader()
            count = 0
            for term in term_list:
                # The REST API returns term attributes under "properties" (not the
                # legacy "glossaryTermProperties" key used by older Egeria clients).
                props = term.get("properties") or term.get("glossaryTermProperties", {})
                term_name = props.get("displayName", "---")
                qualified_name = props.get("qualifiedName", "---")
                abbrev = props.get("abbreviation", "---") or "---"
                summary = props.get("summary", "---") or "---"
                description = props.get("description", "---") or "---"
                examples = props.get("examples", "---") or "---"
                usage = props.get("usage", "---") or "---"
                version = props.get("publishVersionIdentifier", "---") or "---"
                status = term.get("elementHeader", {}).get("status", "DRAFT")

                csv_writer.writerow(
                    {
                        "Term Name": term_name,
                        "Qualified Name": qualified_name,
                        "Abbreviation": abbrev,
                        "Summary": summary,
                        "Description": description,
                        "Examples": examples,
                        "Usage": usage,
                        "Version Identifier": version,
                        "Status": status,
                        }
                    )
                count += 1

        return count

    @dynamic_catch
    def export_glossary_to_csv(
            self,
            glossary_guid: str,
            target_file: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            ) -> int:
        """Export all terms in a glossary to a CSV file.

        Parameters
        ----------
        glossary_guid : str
            GUID of the glossary whose terms are to be exported.
        target_file : str
            Output file name (without directory).
        file_path : str, optional
            Directory in which to write ``target_file``.  Defaults to the
            ``EGERIA_GLOSSARY_PATH`` environment variable, or the current
            working directory when not set.

        Returns
        -------
        int
            Number of term rows written to the CSV.

        Notes
        -----
        The output CSV uses the same column headers expected by
        :meth:`import_glossary_terms_from_csv` so a round-trip
        export → edit → import is straightforward.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_export_glossary_to_csv(glossary_guid, target_file, file_path)
            )


    @dynamic_catch
    async def _async_create_term_copy(
            self,
            glossary_guid: str,
            glossary_term_guid: str,
            new_display_name: str,
            version_id: Optional[str] = None,
            term_status: str = "PROPOSED",
            body: Optional[dict | TemplateRequestBody] = None,
            ) -> str:
        """Create a new term from an existing term.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_name: str
                The display name of the new term.
            version_id: str
                The version identifier of the new term.
            term_status: str, optional, default = "PROPOSED"
                The status of the term


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        """

        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)
        else:
            qualified_name = self.__create_qualified_name__("Term", new_display_name)
            body = {
                "class" : "TemplateRequestBody",
                "templateGUID": glossary_term_guid,
                "parentGuid": glossary_guid,
                "parentAtEnd1": True,

                "replacementProperties": {
                    "class": "GlossaryTermProperties",
                        "qualifiedName": qualified_name,
                        "displayName":  new_display_name,
                        "status": term_status,
                        "versionIdentifier": version_id
                    },
                }
            validated_body = self._template_request_adapter.validate_python(body)
            validated_body._templateGUID = glossary_term_guid
        v_body = body_slimmer(validated_body.model_dump(exclude_none=True, by_alias=True))
        logger.info(v_body)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/from-template/{glossary_term_guid}"
        )

        resp = await self._async_make_request("POST", url, v_body)
        guid = resp.json().get("guid", NO_GUID_RETURNED)
        logger.info(f"Create Term from template with GUID: {guid}")
        return guid

    @dynamic_catch
    def create_term_copy(
            self,
            glossary_guid: str,
            glossary_term_guid: str,
            new_display_name: str,
            version_id: Optional[str] = None,
            term_status: str = "PROPOSED",
            body: Optional[dict | TemplateRequestBody] = None,
            ) -> str:
        """Create a new term from an existing term.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_name: str
                The display name of the new term.
            version_id: str
                The version identifier of the new term.
            term_status: str, optional, default = "PROPOSED"
                The status of the term


        Returns
        -------
        str:
            The unique guid for the created term.

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_term_copy(
                glossary_guid,
                glossary_term_guid,
                new_display_name,
                version_id,
                term_status,
                body,
                )
            )

        return response

    @dynamic_catch
    async def _async_update_glossary_term(
            self,
            glossary_term_guid: str,
            body: dict | UpdateElementRequestBody,
            ) -> None:
        """Update a term. Async version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
            f"{glossary_term_guid}/"
            f"update"
        )
        await self._async_update_element_body_request(url, ["GlossaryTermProperties"], body)
        logger.info(f"Updated digital subscription {glossary_term_guid}")
    @dynamic_catch
    def update_glossary_term(
            self,
            glossary_term_guid: str,
            body: dict | UpdateElementRequestBody,

            ) -> None:
        """Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            body: dict
                Body containing information about the data field to add
            is_merge_update: bool, optional, default = True
                Whether the data field values should be merged with existing definition or replace it.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        An example body is:

        {
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "description" : "This is the long description of the term. And this is some more text."
                },
                "updateDescription" : "Final updates based on in-house review comments."
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_glossary_term(
                glossary_term_guid,
                body,
                )
            )

    @dynamic_catch
    async def _async_update_glossary_term_status(
            self,
            glossary_term_guid: str,
            term_status: str = "ACTIVE",
            body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the status of a term. Async version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            term_status: str
                new status of the term.
            body: dict | UpdateElementRequestBody
                Body containing information about the status change. Supersedes other parameters.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaException

        """

        validate_guid(glossary_term_guid)

        if body is None:
            body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "GlossaryTermProperties",
                    "contentStatus": term_status,
                },
                "mergeUpdate": True,
            }
        await self._async_update_glossary_term( glossary_term_guid, body)
        logger.info(f"Updated term status {glossary_term_guid}")


    @dynamic_catch
    def update_glossary_term_status(
            self,
            glossary_term_guid: str, term_status: str = "ACTIVE",
            body: Optional[dict | UpdateElementRequestBody] = None,
            ) -> None:
        """Add the data field values classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            term_status: str
                new status of the term.
            body: dict | UpdateStatusRequestBody
                Body containing information about the status change. Supersedes other parameters.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthoclearizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        An example body is:

        {
            "class" : "UpdateStatusRequestBody",
            "newStatus" : "DRAFT"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_glossary_term_status(
                glossary_term_guid,
                term_status,
                body,
                )
            )

    @dynamic_catch
    async def _async_delete_term(
            self,
            term_guid: str,
            cascade: bool = False,
            body: Optional[dict | DeleteElementRequestBody] = None
            ) -> None:
        """Delete the glossary terms associated with the specified glossary. Async version.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.
            for_lineage: bool, opt, default = False
                Set true for lineage processing - generally false.
            for_duplicate_processing: bool, opt, default = False
                Set true if duplicate processing handled externally - generally set False.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/delete"
        )
        await self._async_delete_element_request(url, body, cascade)
        logger.info(f"Deleted collection {term_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_term(
            self,
            term_guid: str,
            cascade: bool = False,
            body: Optional[dict | DeleteElementRequestBody] = None
            ) -> None:
        """Delete the glossary terms associated with the specified glossary.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.
            for_lineage: bool, opt, default = False
                Set true for lineage processing - generally false.
            for_duplicate_processing: bool, opt, default = False
                Set true if duplicate processing handled externally - generally set False.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_term(term_guid, cascade, body)
            )

    @dynamic_catch
    async def _async_move_term(
            self,
            term_guid: str,
            glossary_guid: str,
            body: Optional[dict | DeleteRelationshipRequestBody] = None
            ) -> None:
        """Move the glossary terms to the specified glossary. Async version.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        validate_guid(term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/move-to/{glossary_guid}"
        )
        await self._async_delete_relationship_request(url, body)
        logger.info(f"Moved collection {term_guid} to glossary {glossary_guid}")

    @dynamic_catch
    def move_term(
            self,
            term_guid: str,
            glossary_guid: str,
            body: Optional[dict | DeleteRelationshipRequestBody] = None
            ) -> None:
        """Move the glossary terms to the specified glossary.

        Parameters
        ----------
            term_guid : str,
                The unique identifier for the term to delete.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_move_term(term_guid, glossary_guid, body)
            )



    #
    #   Categories are just Folders in collection manager
    #




    #
    #   From glossary browser
    #

    @dynamic_catch
    async def _async_add_is_abstract_concepts(
            self, term_guid: str, body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-abstract-concept"
        )
        if body is None:
            body = {
                "class": "NewClassificationRequestBody",
                "properties":
                    {
                        "class": "AbstractConceptProperties"
                    }
                }

        await self._async_new_classification_request(url, "AbstractConceptProperties", body)
        logger.info(f"Added AbstractConcept classification to {term_guid}")

    @dynamic_catch
    def add_is_abstract_concept(
            self, term_guid: str,  body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_is_abstract_concepts(term_guid, body)
            )

    @dynamic_catch
    async def _async_remove_is_abstract_concepts(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-abstract-concept/remove"
        )
        await self._async_delete_classification_request(url, body)
        logger.info(f"Removed AbstractConcept classification to {term_guid}")

    @dynamic_catch
    def remove_is_abstract_concept(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_is_abstract_concepts(term_guid, body)
            )

    @dynamic_catch
    async def _async_add_is_context_definition(
            self, term_guid: str, body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-context-definition"
        )
        if body is None:
            body = {
                "class": "NewClassificationRequestBody",
                "properties":
                    {
                        "class": "ContextDefinitionProperties"
                    }
                }

        await self._async_new_classification_request(url, "ContextDefinitionProperties", body)
        logger.info(f"Added AbstractConcept classification to {term_guid}")

    @dynamic_catch
    def add_is_context_definition(
            self, term_guid: str,  body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_is_context_definition(term_guid, body)
            )

    @dynamic_catch
    async def _async_remove_is_context_definition(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-context-definition/remove"
        )
        await self._async_delete_classification_request(url, body)
        logger.info(f"Removed ContextDefinition classification to {term_guid}")

    @dynamic_catch
    def remove_is_context_definition(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_is_context_definition(term_guid, body)
            )

    @dynamic_catch
    async def _async_add_is_data_value(
            self, term_guid: str, body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-data-value"
        )
        if body is None:
            body = {
                "class": "NewClassificationRequestBody",
                "properties":
                    {
                        "class": "DataValueProperties"
                    }
                }

        await self._async_new_classification_request(url, "DataValueProperties", body)
        logger.info(f"Added DataValue classification to {term_guid}")

    @dynamic_catch
    def add_is_data_value(
            self, term_guid: str,  body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_is_data_value(term_guid, body)
            )

    @dynamic_catch
    async def _async_remove_is_data_value(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-data-value/remove"
        )
        await self._async_delete_classification_request(url, body)
        logger.info(f"Removed DataValue classification to {term_guid}")

    @dynamic_catch
    def remove_is_data_value(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_is_data_value(term_guid, body)
            )

    @dynamic_catch
    async def _async_add_activity_description(
            self, term_guid: str, activity_type: int = None, body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        if body is None:
            body = {
                "class": "NewClassificationRequestBody",
                "properties": {
                    "class": "ActivityDescriptionProperties",
                    "type": activity_type,
                    }
                }

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-activity"
        )
        await self._async_new_classification_request(url, "ActivityDescriptionProperties", body)
        logger.info(f"Added DataValue classification to {term_guid}")

    @dynamic_catch
    def add_activity_description(
            self, term_guid: str,  activity_type: int = None, body: Optional[dict | NewClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_activity_description(term_guid, activity_type, body)
            )

    @dynamic_catch
    async def _async_remove_activity_description(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewClassificationRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",

                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term_guid}/is-activity/remove"
        )
        await self._async_delete_classification_request(url, body)
        logger.info(f"Removed ActivityDescription classification to {term_guid}")

    @dynamic_catch
    def remove_activity_description(
            self, term_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_activity_description(term_guid, body)
            )

    #
    #   Term - Term Relationships
    #

    @dynamic_catch
    async def _async_add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | NewRelationshipRequestBody] = None,
            ) -> None:
        """Add a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        body: dict, optional, default = None
            Further optional details for the relationship.


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "NewRelationshipRequestBody",
             "effectiveTime" : {{@isoTimestamp}},
             "properties" : {
                "class" : "GlossaryTermRelationship",
                "expression" : "",
                "confidence"  : 0,
                "description" : "",
                "status"   : "",
                "steward"  : "",
                "source" : "",
                "effectiveFrom" : "{{@isoTimestamp}}",
                "effectiveTo" : "{{@isoTimestamp}}",
                "extendedProperties" : {
                }
             }
        }
        """

        validate_guid(term1_guid)
        validate_guid(term2_guid)

        if body is None:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties":
                    {"class": "GlossaryTermRelationshipProperties",
                     "confidence": 100}
                }

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}"
        )
        await self._async_new_relationship_request(url, ["GlossaryTermRelationshipProperties"],body)
        logger.info(f"Added relationship between {term1_guid} and {term2_guid} of type {relationship_type}")

    @dynamic_catch
    def add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | NewRelationshipRequestBody] = None,
            ) -> None:
        """Add a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add. A list of relationship types can be found using get_term_relationship_types().
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "NewRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_relationship_between_terms(term1_guid, term2_guid, relationship_type,
                                                       body)
            )

    @dynamic_catch
    async def _async_update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | UpdateRelationshipRequestBody] = None
            ) -> None:

        """Update a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to update.
        body: dict, optional, default = None
            Further optional details for the relationship.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
         "class" : "UpdateRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """

        validate_guid(term1_guid)
        validate_guid(term2_guid)



        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}/update")

        await self._async_update_relationship_request(url, "GlossaryTermRelationship", body)
        logger.info(f"Updated relationship between {term1_guid} and {term2_guid} of type {relationship_type}")

    @dynamic_catch
    def update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | UpdateRelationshipRequestBody] = None
            ) -> None:
        """Update a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to update. A list of relationship types can be found using
            get_term_relationship_types().
        body: dict
            Details of the relationship to update.

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
         "class" : "UpdateRelationshipRequestBody",
         "effectiveTime" : {{@isoTimestamp}},
         "properties" : {
            "class" : "GlossaryTermRelationship",
            "expression" : "",
            "confidence"  : 0,
            "description" : "",
            "status"   : "",
            "steward"  : "",
            "source" : "",
            "effectiveFrom" : "{{@isoTimestamp}}",
            "effectiveTo" : "{{@isoTimestamp}}",
            "extendedProperties" : {
            }
         }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_relationship_between_terms(term1_guid, term2_guid, relationship_type,
                                                          body)
            )

    @dynamic_catch
    async def _async_remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | DeleteRelationshipRequestBody] = None,
            ) -> None:
        """Remove a relationship between terms. Async Version.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to add.
        effective_time: str, optional, default = None
            Effective time to remove the relationship.
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function

        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.


        """

        validate_guid(term1_guid)
        validate_guid(term2_guid)


        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}/remove"
        )

        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:

        """Remove a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to remove. A list of relationship types can be found using
            get_term_relationship_types().


        Returns
        -------
        None

        Raises
        ------
         PyegeriaInvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PyegeriaAPIException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_relationship_between_terms(term1_guid, term2_guid, relationship_type,
                                                          body)
            )

    #
    # Integrated Glossary Browser methods
    #
    @dynamic_catch
    def _extract_glossary_properties(self, element: dict, columns_struct: dict) -> dict:
        """Extract glossary columns for rendering.

        This extractor uses `populate_common_columns` for standard fields (properties, header, relationships,
        subject area, mermaid). It then overlays glossary-specific values such as:
        - categories_names: comma/newline separated Display Names of categories in the glossary
        - categories_qualified_names: comma/newline separated Qualified Names of categories in the glossary

        Parameters
        ----------
        element : dict
            Raw element as returned by the OMVS.
        columns_struct : dict
            The selected output format structure (from _output_formats), whose columns' `value` fields will be filled.

        Returns
        -------
        dict
            The same columns_struct with values populated. Non-empty values are not overwritten.
        """
        # Common population first
        col_data = populate_common_columns(element, columns_struct)
        # Overlay glossary-specific extras: categories lists
        header_props = _extract_referenceable_properties(element)
        guid = header_props.get('GUID')
        extra: dict = {}
        if guid:
            try:
                categories = self.get_categories_for_glossary(guid)
            except Exception:
                categories = None
            if isinstance(categories, list):
                cat_display_list = []
                cat_qn_list = []
                for category in categories:
                    gcp = category.get('glossaryCategoryProperties', {})
                    dn = (gcp.get('displayName') or '')
                    qn = (gcp.get('qualifiedName') or '')
                    if dn:
                        cat_display_list.append(dn)
                    if qn:
                        cat_qn_list.append(qn)
                if cat_display_list:
                    extra['categories_names'] = ", \n".join(cat_display_list)
                if cat_qn_list:
                    extra['categories_qualified_names'] = ", \n".join(cat_qn_list)
        return overlay_additional_values(col_data, extra)

    @dynamic_catch
    def _extract_term_properties(self, element: dict, columns_struct: dict) -> dict:
        """Extract glossary term columns for rendering.

        Populates standard columns via `populate_common_columns`, and if requested by the
        selected columns, derives a classifications string (from `elementHeader.collectionCategories`)
        into the `classifications` column.

        Parameters
        ----------
        element : dict
            Raw term element returned by the OMVS.
        columns_struct : dict
            The chosen format-set structure whose column `value`s will be set.

        Returns
        -------
        dict
            The same `columns_struct` with values populated.
        """
        # Use centralized population
        col_data = populate_common_columns(element, columns_struct)
        # Term-specific classifications (collectionCategories) to 'classifications' column
        columns_list = col_data.get('formats', {}).get('attributes', [])
        try:
            classification_names = ""
            classifications = element.get('elementHeader', {}).get("collectionCategories", [])
            for classification in classifications:
                nm = classification.get('classificationName')
                if nm:
                    classification_names += f"{nm}, "
            if classification_names:
                for column in columns_list:
                    if column.get('key') == 'classifications' and column.get('value') in (None, ""):
                        column['value'] = classification_names[:-2]
                        break
        except Exception:
            pass
        return col_data

    @dynamic_catch
    def _get_term_additional_properties(self, element: dict, term_guid: str, output_format: str = None) -> dict:
        additional: dict = {}
        try:
            classifications = element.get('elementHeader', {}).get('otherClassifications', [])
            glossary_name = ''
            if classifications:
                cls_props = classifications[0].get('classificationProperties', {}) or {}
                g_guid = cls_props.get('anchorScopeGUID')
                if g_guid and hasattr(self, 'get_glossary_by_guid'):
                    try:
                        gl = self.get_glossary_by_guid(g_guid)
                        if isinstance(gl, dict):
                            if output_format == 'REPORT':
                                glossary_name = gl.get('glossaryProperties', {}).get('displayName', '')
                            else:
                                glossary_name = gl.get('glossaryProperties', {}).get('qualifiedName', '')
                    except Exception:
                        pass
            if glossary_name:
                additional['in_glossary'] = glossary_name
        except Exception:
            pass
        try:
            if hasattr(self, 'get_categories_for_term') and term_guid:
                cats = self.get_categories_for_term(term_guid)
                names = []
                if isinstance(cats, list):
                    for c in cats:
                        gcp = c.get('glossaryCategoryProperties', {})
                        val = gcp.get('displayName') if output_format in ['REPORT', 'LIST'] else gcp.get('qualifiedName')
                        if val:
                            names.append(val)
                if names:
                    additional['categories'] = ", \n".join(names)
        except Exception:
            pass
        return additional

    @dynamic_catch
    def _generate_glossary_output(self, elements: dict | list[dict], search_string: Optional[str] = None,
                                  element_type_name: Optional[str] = None,
                                  output_format: str = 'DICT',
                                  report_spec: dict | str = None,
                                  **kwargs) -> str | list[dict]:
        return self._generate_formatted_output(
            elements=elements,
            query_string=search_string,
            entity_type='Glossary',
            output_format=output_format,
            extract_properties_func=self._extract_glossary_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    def _generate_term_output(self, elements: dict | list[dict], search_string: Optional[str] = None,
                               element_type_name: Optional[str] = None,
                               output_format: str = 'DICT',
                               report_spec: dict | str = None,
                               **kwargs) -> str | list[dict]:
        return self._generate_formatted_output(
            elements=elements,
            query_string=search_string,
            entity_type='GlossaryTerm',
            output_format=output_format,
            extract_properties_func=self._extract_term_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    async def _async_get_glossary_term_statuses(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/status-list")
        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    @dynamic_catch
    def get_glossary_term_statuses(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    @dynamic_catch
    async def _async_get_glossary_term_rel_statuses(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/status-list")
        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    @dynamic_catch
    def get_glossary_term_rel_statuses(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_rel_statuses())
        return response

    @dynamic_catch
    async def _async_get_glossary_term_activity_types(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/activity-types")
        response = await self._async_make_request("GET", url)
        return response.json().get("types", [])

    @dynamic_catch
    def get_glossary_term_activity_types(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_activity_types())
        return response

    @dynamic_catch
    async def _async_get_term_relationship_types(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/type-names")
        response = await self._async_make_request("GET", url)
        return response.json().get("names", [])

    @dynamic_catch
    def get_term_relationship_types(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_relationship_types())
        return response

    @dynamic_catch
    async def _async_find_glossaries(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        **kwargs
    ) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all glossaries.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional, [default="Glossary"]
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
        report_spec: str | dict , optional, default = None
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
        response = await self._async_find_collections(
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
        return response

    @dynamic_catch
    def find_glossaries(self, search_string: str = "*",
                        starts_with: bool = True, ends_with: bool = False,
                        ignore_case: bool = False,
                        anchor_domain: Optional[str] = None,
                        metadata_element_type: str = "Glossary",
                        metadata_element_subtypes: Optional[list[str]] = None,
                        skip_relationships: Optional[list[str]] = None,
                        include_only_relationships: Optional[list[str]] = None,
                        skip_classified_elements: Optional[list[str]] = None,
                        include_only_classified_elements: Optional[list[str]] = None,
                        graph_query_depth: int = 3,
                        governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                        effective_time: Optional[str] = None, relationship_page_size: int = 0,
                        limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                        sequencing_property: Optional[str] = None,
                        output_format: str = "JSON",
                        report_spec: str | dict = None,
                        start_from: int = 0, page_size: int = 100,
                        property_names: Optional[list[str]] = None,
                        body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all glossaries.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional, [default="Glossary"]
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
        report_spec: str | dict , optional, default = None
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
        return loop.run_until_complete(self._async_find_glossaries(search_string=search_string,
                                                                  starts_with=starts_with,
                                                                  ends_with=ends_with,
                                                                  ignore_case=ignore_case,
                                                                  anchor_domain=anchor_domain,
                                                                  metadata_element_type=metadata_element_type,
                                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                                  skip_relationships=skip_relationships,
                                                                  include_only_relationships=include_only_relationships,
                                                                  skip_classified_elements=skip_classified_elements,
                                                                  include_only_classified_elements=include_only_classified_elements,
                                                                  graph_query_depth=graph_query_depth,
                                                                  governance_zone_filter=governance_zone_filter,
                                                                  as_of_time=as_of_time,
                                                                  effective_time=effective_time,
                                                                  relationship_page_size=relationship_page_size,
                                                                  limit_results_by_status=limit_results_by_status,
                                                                  sequencing_order=sequencing_order,
                                                                  sequencing_property=sequencing_property,
                                                                  output_format=output_format,
                                                                  report_spec=report_spec,
                                                                  start_from=start_from,
                                                                  page_size=page_size,
                                                                  property_names=property_names,
                                                                  body=body))

    @dynamic_catch
    async def _async_get_glossaries_by_name(self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
                                             body: Optional[dict | FilterRequestBody] = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             report_spec: str | dict = None) -> dict | str:
        return await self._async_get_collections_by_name(filter_string, classification_names, body, start_from, page_size, output_format, report_spec)

    @dynamic_catch
    def get_glossaries_by_name(self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
                                             body: Optional[dict | FilterRequestBody] = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             report_spec: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossaries_by_name(filter_string, classification_names, body,start_from, page_size,
                                               output_format, report_spec))
        return response

    @dynamic_catch
    async def _async_get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: Optional[dict | GetRequestBody] = None,
                                          output_format: str = "JSON", report_spec: str | dict = None) -> dict | str:

        return await self._async_get_collection_by_guid(glossary_guid, element_type, body, output_format, report_spec)

    @dynamic_catch
    def get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", report_spec: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_by_guid(glossary_guid, element_type, body,output_format, report_spec))
        return response

    @dynamic_catch
    async def _async_get_terms_by_name(self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
                                             body: Optional[dict | FilterRequestBody] = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             report_spec: str | dict = None) -> list:
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
               f"terms/by-name")
        response = await self._async_get_name_request(url, _type="GlossaryTerm", _gen_output=self._generate_term_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names, start_from=start_from,
                                                      page_size=page_size, output_format=output_format,
                                                      report_spec=report_spec, body=body)
        return response

    @dynamic_catch
    def get_terms_by_name(self, filter_string: Optional[str] = None, classification_names: Optional[list[str]] = None,
                                             body: Optional[dict | FilterRequestBody] = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             report_spec: str | dict = None) -> list:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_by_name(filter_string, classification_names, body,start_from, page_size,
                                           output_format, report_spec))
        return response

    @dynamic_catch
    async def _async_get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", report_spec: str | dict = None) -> dict | str:
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
               f"{term_guid}")
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_term_output,
                                                      output_format=output_format, report_spec=report_spec,
                                                      body=body)
        return response

    @dynamic_catch
    def get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", report_spec: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_by_guid(term_guid, element_type, body,  output_format, report_spec))
        return response

    @dynamic_catch
    async def _async_find_glossary_terms(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        output_format: str = "JSON",
        report_spec: str | dict = "Glossary-Term-DrE",
        **kwargs
    ) -> list | str:
        """ Retrieve the list of glossary term metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all glossary terms.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional, [default="GlossaryTerm"]
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
        report_spec: str | dict , optional, default = "Glossary-Term-DrE"
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
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
               f"by-search-string")
        
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
        
        # Get metadata_element_type from kwargs or use default
        metadata_element_type = kwargs.get('metadata_element_type', 'GlossaryTerm')
        
        response = await self._async_find_request(url, _type=metadata_element_type,
                                                  _gen_output=self._generate_term_output, **params)

        return response

    @dynamic_catch
    def find_glossary_terms(self, search_string: str = "*",
                            starts_with: bool = True, ends_with: bool = False,
                            ignore_case: bool = False,
                            anchor_domain: Optional[str] = None,
                            metadata_element_type: str = "GlossaryTerm",
                            metadata_element_subtypes: Optional[list[str]] = None,
                            skip_relationships: Optional[list[str]] = None,
                            include_only_relationships: Optional[list[str]] = None,
                            skip_classified_elements: Optional[list[str]] = None,
                            include_only_classified_elements: Optional[list[str]] = None,
                            graph_query_depth: int = 3,
                            governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                            effective_time: Optional[str] = None, relationship_page_size: int = 0,
                            limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                            sequencing_property: Optional[str] = None,
                            output_format: str = "JSON",
                            report_spec: str | dict = "Glossary-Term-DrE",
                            start_from: int = 0, page_size: int = 100,
                            property_names: Optional[list[str]] = None,
                            body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
        """ Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all glossary terms.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional, [default="GlossaryTerm"]
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
        report_spec: str | dict , optional, default = "Glossary-Term-DrE"
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
        return loop.run_until_complete(self._async_find_glossary_terms(search_string=search_string,
                                                                      starts_with=starts_with,
                                                                      ends_with=ends_with,
                                                                      ignore_case=ignore_case,
                                                                      anchor_domain=anchor_domain,
                                                                      metadata_element_type=metadata_element_type,
                                                                      metadata_element_subtypes=metadata_element_subtypes,
                                                                      skip_relationships=skip_relationships,
                                                                      include_only_relationships=include_only_relationships,
                                                                      skip_classified_elements=skip_classified_elements,
                                                                      include_only_classified_elements=include_only_classified_elements,
                                                                      graph_query_depth=graph_query_depth,
                                                                      governance_zone_filter=governance_zone_filter,
                                                                      as_of_time=as_of_time,
                                                                      effective_time=effective_time,
                                                                      relationship_page_size=relationship_page_size,
                                                                      limit_results_by_status=limit_results_by_status,
                                                                      sequencing_order=sequencing_order,
                                                                      sequencing_property=sequencing_property,
                                                                      output_format=output_format,
                                                                      report_spec=report_spec,
                                                                      start_from=start_from,
                                                                      page_size=page_size,
                                                                      property_names=property_names,
                                                                      body=body))


if __name__ == "__main__":
    print("Main-Glossary Manager")

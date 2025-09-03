"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_manager omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""

import asyncio
import csv
import os
import time
from typing import List, Annotated, Literal

from loguru import logger
from pydantic import Field

from pyegeria._client_new import Client2
from pyegeria._exceptions import InvalidParameterException
from pyegeria._exceptions_new import PyegeriaInvalidParameterException
from pyegeria._globals import NO_GUID_RETURNED
from pyegeria._validators import validate_guid
from pyegeria.collection_manager import CollectionManager
from pyegeria.config import settings as app_settings
from pyegeria.models import (NewElementRequestBody,
                             ReferenceableProperties, UpdateElementRequestBody, DeleteRequestBody, TemplateRequestBody,
                             NewRelationshipRequestBody, UpdateRelationshipRequestBody, NewClassificationRequestBody,
                             FilterRequestBody, GetRequestBody, SearchStringRequestBody, UpdateStatusRequestBody)
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import body_slimmer, dynamic_catch

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


("params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to "
 "the query string")




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
    GlossaryManager is a class that extends the Client class. It provides methods to create and manage glossaries,
    terms and categories.

    Attributes:

        view_server: str
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
        self.gl_mgr_command_root: str
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        CollectionManager.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        result = self.get_platform_origin()
        logger.info(f"GlossaryManager initialized, platform origin is: {result}")
    #
    #       Get Valid Values for Enumerations
    #

    def __validate_term_status__(self, status: str) -> bool:
        """Return True if the status is a legal glossary term status"""
        recognized_term_status = self.get_glossary_term_statuses()
        return status in recognized_term_status

    #
    #       Glossaries
    #



    @dynamic_catch
    async def _async_create_glossary(self, display_name: str, description: str = None, language: str = "English", usage: str = None,
                        category: str = None, body: dict | NewElementRequestBody = None) -> str:
        """Create a new glossary with optional classification. """
        if body is None:
            qualified_name = self.__create_qualified_name__("Glossary", display_name, EGERIA_LOCAL_QUALIFIER)
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

    def create_glossary(self, display_name: str, description: str = None, language: str = "English",
                               usage: str = None,
                               category: str = None, body: dict | NewElementRequestBody = None) -> str:
        """Create a new glossary with optional classification. """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary(display_name, description, language, usage, category, body)
            )
        return response

    async def _async_delete_glossary(self, glossary_guid: str, body: dict | DeleteRequestBody = None,
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

    def delete_glossary(self, glossary_guid: str, body: dict | DeleteRequestBody = None, cascade: bool = False) -> None:
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



        await self._async_update_collection(glossary_guid, body, is_merge_update=merge_update)
        logger.info(f"Updated digital subscription {glossary_guid}")

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
    async def _async_create_glossary_term(
            self, body: dict | NewElementRequestBody
            ) -> str:
        """Create a term for a  glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            body: dict | NewElementRequestBody
                The dictionary to create glossary term for. Example below.


        Returns
        -------
        str:
            The unique guid for the created term.

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

        Sample body like:
        {
            "class" : "NewElementRequestBody",
            "parentGUID" : "Glossary GUID here",
            "isOwnAnchor" : true,
            "anchorScopeGUID" : "Glossary GUID here",
            "parentRelationshipTypeName" : "ParentGlossary",
            "parentAtEnd1": true,
            "properties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm::term name",
                    "displayName" : "term name",
                    "aliases": []
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "aabrev",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "versionIdentifier" : "V1.0",
                    "category" : "A user defined category",
                    "additionalProperties" :
                    {
                       "propertyName1" : "xxxx",
                       "propertyName2" : "xxxx"
                    }
                },
            "initialStatus" : "DRAFT"
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms"
        )
        return await self._async_create_element_body_request(url, "GlossaryTermProperties", body)

    def create_glossary_term(self, body: dict | NewElementRequestBody) -> str:
        """Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

        Parameters
        ----------

            body: dict
                The dictionary to create glossary term for. Example below.


        Returns
        -------
        str:
            The unique guid for the created term.

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

        Sample body like:
         {
            "class" : "NewElementRequestBody",
            "parentGUID" : "Glossary GUID here",
            "isOwnAnchor" : true,
            "anchorScopeGUID" : "Glossary GUID here",
            "parentRelationshipTypeName" : "ParentGlossary",
            "parentAtEnd1": true,
            "properties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm::term name",
                    "displayName" : "term name",
                    "aliases": []
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "aabrev",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "versionIdentifier" : "V1.0",
                    "category" : "A user defined category",
                    "additionalProperties" :
                    {
                       "propertyName1" : "xxxx",
                       "propertyName2" : "xxxx"
                    }
                },
            "initialStatus" : "DRAFT"
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary_term(body)
            )

        return response

    def load_terms_from_csv_file(
            self,
            glossary_name: str,
            filename: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            upsert: bool = True,
            verbose: bool = True,
            ) -> List[dict] | None:
        """This method loads glossary terms into the specified glossary from the indicated file.

        Parameters
        ----------
            glossary_name : str
                Name of the glossary to import terms into.
            file_path: str, default is EGERIA_GLOSSARY_PATH if specified or None
                If EGERIA_GLOSSARY_PATH environment variable is set, then it will be used in forming the
                prepended to the filename parameter to form the full path to the file.
            filename: str
                Path to the file to import terms from. File is assumed to be in CSV format. The path
                is relative to where the python method is being called from.
            upsert: bool, default = True
                If true, terms from the file are inserted into the glossary if no qualified name is specified;
                if a qualified name is specified in the file, then the file values for this term will over-ride the
                values in the glossary. If false, the row in the file will be appended to the glossary, possibly
                resulting in duplicate term names - which is legal (since the qualified names will be unique).

            verbose: bool, default = True
                If true, a JSON structure will be returned indicating the import status of each row.


        Returns
        -------
        [dict]:
            If verbose is True, import status for each row
        None:
            If verbose is False

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
            Keep in mind that the file path is relative to where the python method is being called from -
            not relative to the Egeria platform.

        """

        # Check that glossary exists and get guid
        glossaries = self.get_glossaries_by_name(glossary_name)
        if type(glossaries) is not list:
            return "Unknown glossary"
        if len(glossaries) > 1:
            glossary_error = (
                "Multiple glossaries found - please use a qualified name from below\n"
            )
            for g in glossaries:
                glossary_error += (
                    f"Display Name: {g['glossaryProperties']['displayName']}\tQualified Name:"
                    f" {g['glossaryProperties']['qualifiedName']}\n"
                )
            raise Exception(glossary_error)
            sys.exit(1)

        # Now we know we have a single glossary so we can get the guid
        glossary_guid = glossaries[0]["elementHeader"]["guid"]

        term_properties = {
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

        if file_path:
            full_file_path = os.path.join(file_path, filename)
        else:
            full_file_path = filename

        if not os.path.isfile(full_file_path):
            raise FileNotFoundError(
                f"Did not find file with path {file_path} and name {filename}"
                )
        # process file
        with open(full_file_path, mode="r") as file:
            # Create a CSV reader object
            csv_reader = csv.DictReader(file)
            headers = csv_reader.fieldnames
            term_info = []
            # check that the column headers are known
            if all(header in term_properties for header in headers) is False:
                raise InvalidParameterException("Invalid headers in CSV File")

            # process each row and validate values
            for row in csv_reader:
                # Parse the file. When the value '---' is encountered, make the value None.git+https:
                term_name = row.get("Term Name", " ")
                if len(term_name) < 2:
                    term_info.append(
                        {
                            "term_name": "---",
                            "qualified_name": "---",
                            "term_guid": "---",
                            "error": "missing or invalid term names - skipping",
                            }
                        )
                    continue
                qualified_name = row.get("Qualified Name", None)
                abbrev_in = row.get("Abbreviation", None)
                abbrev = None if abbrev_in == "---" else abbrev_in

                summary_in = row.get("Summary", None)
                summary = None if summary_in == "---" else summary_in

                description_in = row.get("Description", None)
                description = None if description_in == "---" else description_in

                examples_in = row.get("Examples", None)
                examples = None if examples_in == "---" else examples_in

                usage_in = row.get("Usage", None)
                usage = None if usage_in == "---" else usage_in

                version = row.get("Version Identifier", "1.0")
                status = row.get("Status", "DRAFT").upper()
                if self.__validate_term_status__(status) is False:
                    term_info.append(
                        {
                            "term_name": "---",
                            "qualified_name": "---",
                            "term_guid": "---",
                            "error": "invalid term status",
                            }
                        )
                    continue

                if upsert:
                    # If upsert is set we need to see if it can be done (there must be a valid qualified name) and then
                    # do the update for the row - if there is no qualified name we will treat the row as an insert.
                    if qualified_name:
                        term_stuff = self.get_terms_by_name(
                            qualified_name, glossary_guid
                            )
                        if type(term_stuff) is str:
                            # An existing term was not found with that qualified name
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "error": "Matching term not found - skipping",
                                    }
                                )
                            continue
                        elif len(term_stuff) > 1:
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "error": "Multiple matching terms - skipping",
                                    }
                                )
                            continue
                        else:
                            # An existing term was found - so update it! Get the existing values and overlay
                            # values from file when present

                            body = {
                                "class": "ReferenceableRequestBody",
                                "elementProperties": {
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
                                "updateDescription": "Update from file import via upsert",
                                }
                            term_guid = term_stuff[0]["elementHeader"]["guid"]
                            self.update_term(
                                term_guid, body_slimmer(body), is_merge_update=True
                                )
                            term_info.append(
                                {
                                    "term_name": term_name,
                                    "qualified_name": qualified_name,
                                    "term_guid": term_guid,
                                    "updated": "the term was updated",
                                    }
                                )
                            continue

                # Add the term
                term_qualified_name = self.__create_qualified_name__("Term", term_name)

                body = {
                    "class": "ReferenceableRequestBody",
                    "elementProperties": {
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
                    }

                # Add the term
                term_guid = self.create_controlled_glossary_term(
                    glossary_guid, body_slimmer(body)
                    )
                term_info.append(
                    {
                        "term_name": term_name,
                        "qualified_name": term_qualified_name,
                        "term_guid": term_guid,
                        }
                    )
        if verbose:
            return term_info
        else:
            return

    async def _async_export_glossary_to_csv(
            self,
            glossary_guid: str,
            target_file: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            ) -> int:
        """Export all the terms in a glossary to a CSV file. Async version

        Parameters:
        -----------
        glossary_guid: str
            Identity of the glossary to export.
        target_file: str
            Complete file name with path and extension to export to.
        input_file: str, default is EGERIA_GLOSSARY_PATH if specified or None
                If EGERIA_GLOSSARY_PATH environment variable is set, then it will be used in forming the
                prepended to the filename parameter to form the full path to the file.

        Returns:
            int: Number of rows exported.
        """

        term_list = await self._async_get_terms_for_glossary(glossary_guid)

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
        if file_path:
            full_file_path = os.path.join(file_path, target_file)
        else:
            full_file_path = target_file

        with open(full_file_path, mode="w") as file:
            csv_writer = csv.DictWriter(file, fieldnames=header)
            csv_writer.writeheader()
            count = 0
            for term in term_list:
                term_name = term["glossaryTermProperties"]["displayName"]
                qualified_name = term["glossaryTermProperties"]["qualifiedName"]
                abbrev = term["glossaryTermProperties"].get("abbreviation", "---")
                summary = term["glossaryTermProperties"].get("summary", "---")
                description = term["glossaryTermProperties"].get("description", "---")
                examples = term["glossaryTermProperties"].get("examples", "---")
                usage = term["glossaryTermProperties"].get("usage", "---")
                version = term["glossaryTermProperties"].get(
                    "publishVersionIdentifier", "---"
                    )
                status = term["elementHeader"]["status"]

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

    def export_glossary_to_csv(
            self,
            glossary_guid: str,
            target_file: str,
            file_path: str = os.environ.get("EGERIA_GLOSSARY_PATH", None),
            ) -> int:
        """Export all the terms in a glossary to a CSV file.

        Parameters:
        -----------
        glossary_guid: str
            Identity of the glossary to export.
        target_file: str
            Complete file name with path and extension to export to.
        input_file: str, default is EGERIA_GLOSSARY_PATH if specified or None
                If EGERIA_GLOSSARY_PATH environment variable is set, then it will be used in forming the
                prepended to the filename parameter to form the full path to the file.

        Returns:
            int: Number of rows exported.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_export_glossary_to_csv(glossary_guid, target_file, file_path)
            )

        return response

    async def _async_create_term_copy(
            self,
            glossary_guid: str,
            glossary_term_guid: str,
            new_display_name: str,
            version_id: str = None,
            term_status: str = "PROPOSED",
            body: dict | TemplateRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
            qualified_name = self.__create_qualified_name__("Term", new_display_name, EGERIA_LOCAL_QUALIFIER)
            body = {
                "class" : "TemplateRequestBody",
                "templateGUID": glossary_term_guid,
                "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": qualified_name,
                            },

                        "displayName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": new_display_name,
                            },

                        # "publishVersionIdentifier": {
                        #     "class": "PrimitiveTypePropertyValue",
                        #     "typeName": "string",
                        #     "primitiveValue": version_id,
                        #     },

                        }
                    },
                "initialStatus": term_status,
                }
            validated_body = self._template_request_adapter.validate_python(body)

        v_body = body_slimmer(validated_body.model_dump(exclude_none=True))
        logger.info(v_body)


        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/from-template/{glossary_term_guid}"
        )

        resp = await self._async_make_request("POST", url, v_body)
        guid = resp.json().get("guid", NO_GUID_RETURNED)
        logger.info(f"Create Term from template with GUID: {guid}")
        return guid

    def create_term_copy(
            self,
            glossary_guid: str,
            glossary_term_guid: str,
            new_display_name: str,
            version_id: str = None,
            term_status: str = "PROPOSED",
            body: dict | TemplateRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
    async def _async_update_term_status(self, term_guid: str, status: str = None,
                                              body: dict | UpdateStatusRequestBody = None):
        """Update the status of a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the collection. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody, optional
            A structure representing the details of the collection to create. If supplied, these details
            supersede the status parameter provided.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/metadata-elements/{term_guid}/update-status"
        await self._async_update_status_request(url, status, body)
        logger.info(f"Updated status for term {term_guid}")

    @dynamic_catch
    def update_term_status(self, term_guid: str, status: str = None,
                                 body: dict | UpdateStatusRequestBody = None):
        """Update the status of a DigitalProduct collection.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the digital product. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody, optional
            A structure representing the details of the collection to create. If supplied, these details
            supersede the status parameter provided.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_collection_status(term_guid, status, body))


    async def _async_delete_term(
            self,
            term_guid: str,
            cascade: bool = False,
            body: dict | DeleteRequestBody = None
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body, cascade)
        logger.info(f"Deleted collection {term_guid} with cascade {cascade}")


    def delete_term(
            self,
            term_guid: str,
            cascade: bool = False,
            body: dict | DeleteRequestBody = None
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
        loop.run_until_complete(
            self._async_delete_term(term_guid, cascade, body)
            )

    async def _async_move_term(
            self,
            term_guid: str,
            glossary_guid: str,
            body: dict | DeleteRequestBody = None
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body)
        logger.info(f"Moved collection {term_guid} to glossary {glossary_guid}")


    def move_term(
            self,
            term_guid: str,
            glossary_guid: str,
            body: dict | DeleteRequestBody = None
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
        loop.run_until_complete(
            self._async_move_term(term_guid, glossary_guid, body)
            )



    #
    #   Categories are just Folders in collection manager
    #




    #
    #   From glossary browser
    #



    async def _async_add_is_abstract_concepts(
            self, term_guid: str, body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

        await self._async_new_classification_request(url, "AbstractConceptProperties",body)
        logger.info(f"Added AbstractConcept classification to {term_guid}")


    def add_is_abstract_concept(
            self, term_guid: str,  body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_remove_is_abstract_concepts(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body)
        logger.info(f"Removed AbstractConcept classification to {term_guid}")

    def remove_is_abstract_concept(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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


    async def _async_add_is_context_definition(
            self, term_guid: str, body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

        await self._async_new_classification_request(url, "ContextDefinitionProperties",body)
        logger.info(f"Added AbstractConcept classification to {term_guid}")



    def add_is_context_definition(
            self, term_guid: str,  body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_remove_is_context_definition(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body)
        logger.info(f"Removed ContextDefinition classification to {term_guid}")

    def remove_is_context_definition(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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


    async def _async_add_is_data_value(
            self, term_guid: str, body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

        await self._async_new_classification_request(url, "DataValueProperties",body)
        logger.info(f"Added DataValue classification to {term_guid}")



    def add_is_data_value(
            self, term_guid: str,  body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_remove_is_data_value(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body)
        logger.info(f"Removed DataValue classification to {term_guid}")

    def remove_is_data_value(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        
        
    async def _async_add_activity_description(
            self, term_guid: str, activity_type: int = None, body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_new_classification_request(url, "ActivityDescriptionProperties",body)
        logger.info(f"Added DataValue classification to {term_guid}")



    def add_activity_description(
            self, term_guid: str,  activity_type: int = None, body: dict | NewClassificationRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_remove_activity_description(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
        await self._async_delete_request(url, body)
        logger.info(f"Removed ActivityDescription classification to {term_guid}")

    def remove_activity_description(
            self, term_guid: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | NewRelationshipRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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
                    {"class": "GlossaryTermRelationship" }
                }



        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}"
        )
        await self._async_new_relationship_request(url, ["GlossaryTermRelationship"],body)
        logger.info(f"Added relationship between {term1_guid} and {term2_guid} of type {relationship_type}")

    def add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | NewRelationshipRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | UpdateRelationshipRequestBody = None
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    def update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | UpdateRelationshipRequestBody = None
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    async def _async_remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | DeleteRequestBody = None,
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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

        await self._async_delete_request(url, body)

    def remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict | DeleteRequestBody = None) -> None:

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
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
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

    def _extract_glossary_properties(self, element: dict, columns_struct: dict) -> dict:
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        col_data = populate_columns_from_properties(normalized, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])
        header_props = _extract_referenceable_properties(element)
        guid = header_props.get('GUID')
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = guid
        if guid:
            categories = None
            try:
                categories = self.get_categories_for_glossary(guid)
            except Exception:
                categories = None
            cat_display_list = []
            cat_qn_list = []
            if isinstance(categories, list):
                for category in categories:
                    gcp = category.get('glossaryCategoryProperties', {})
                    dn = gcp.get('displayName', '') or ''
                    qn = gcp.get('qualifiedName', '') or ''
                    if dn:
                        cat_display_list.append(dn)
                    if qn:
                        cat_qn_list.append(qn)
            cat_names_md = (", \n".join(cat_display_list)).rstrip(',') if cat_display_list else ''
            cat_qn_md = (", \n".join(cat_qn_list)).rstrip(',') if cat_qn_list else ''
            for column in columns_list:
                if column.get('key') == 'categories_names' and not column.get('value'):
                    column['value'] = cat_names_md
                if column.get('key') == 'categories_qualified_names' and not column.get('value'):
                    column['value'] = cat_qn_md
        for column in columns_list:
            if column.get('key') == 'mermaid' and not column.get('value'):
                column['value'] = element.get('mermaidGraph', '') or ''
                break
        return col_data

    def _extract_term_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("columns", [])
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("collectionCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break
        col_data = get_required_relationships(element, col_data)
        subject_area = element.get('elementHeader', {}).get("subjectArea", "") or ""
        subj_val = ""
        if isinstance(subject_area, dict):
            subj_val = subject_area.get("classificationProperties", {}).get("subjectAreaName", "")
        for column in columns_list:
            if column.get('key') == 'subject_area':
                column['value'] = subj_val
                break
        mermaid_val = element.get('mermaidGraph', "") or ""
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = mermaid_val
                break
        return col_data

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

    def _generate_glossary_output(self, elements: dict | list[dict], search_string: str,
                                  element_type_name: str | None,
                                  output_format: str = 'DICT',
                                  output_format_set: dict | str = None) -> str | list[dict]:
        entity_type = 'Glossary'
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
            extract_properties_func=self._extract_glossary_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def _generate_term_output(self, elements: dict | list[dict], search_string: str,
                               element_type_name: str | None,
                               output_format: str = 'DICT',
                               output_format_set: dict | str = None) -> str | list[dict]:
        entity_type = 'GlossaryTerm'
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
            extract_properties_func=self._extract_term_properties,
            get_additional_props_func=self._get_term_additional_properties,
            columns_struct=output_formats,
        )

    async def _async_get_glossary_term_statuses(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/status-list")
        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_statuses(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_glossary_term_rel_statuses(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/status-list")
        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_rel_statuses(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_rel_statuses())
        return response

    async def _async_get_glossary_term_activity_types(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/activity-types")
        response = await self._async_make_request("GET", url)
        return response.json().get("types", [])

    def get_glossary_term_activity_types(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_term_relationship_types(self) -> [str]:
        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/type-names")
        response = await self._async_make_request("GET", url)
        return response.json().get("names", [])

    def get_term_relationship_types(self) -> [str]:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_relationship_types())
        return response

    async def _async_find_glossaries(self, search_string: str = "*", classificaton_names: list[str] = None,
                                     metadata_element_types: list[str] = ["Glossary"],
                                     starts_with: bool = False, ends_with: bool = False, ignore_case: bool = False,
                                     start_from: int = 0,page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict  = None,
                                     body: dict | SearchStringRequestBody = None) -> list | str:

        response = await self._async_find_collections(search_string, classificaton_names,
                                                      metadata_element_types, starts_with, ends_with, ignore_case,
                                                      start_from, page_size, output_format, output_format_set, body)
        return response

    def find_glossaries(self, search_string: str = "*", classificaton_names: list[str] = None,
                                     metadata_element_types: list[str] = ["Glossary"],
                                     starts_with: bool = False, ends_with: bool = False, ignore_case: bool = False,
                                     start_from: int = 0,page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict  = None,
                                     body: dict | SearchStringRequestBody = None) -> list | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
                    self._async_find_glossaries(search_string,  classificaton_names, metadata_element_types, starts_with, ends_with, ignore_case, start_from, page_size, output_format, output_format_set, body))
        return response

    async def _async_get_glossaries_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> dict | str:
        return await self._async_get_collections_by_name(filter_string, classification_names, body, start_from, page_size, output_format, output_format_set)


    def get_glossaries_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossaries_by_name(filter_string, classification_names, body,start_from, page_size,
                                               output_format, output_format_set))
        return response

    async def _async_get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: dict | GetRequestBody = None,
                                          output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:

        return await self._async_get_collection_by_guid(glossary_guid, element_type, body, output_format, output_format_set)



    def get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_by_guid(glossary_guid, element_type, body,output_format, output_format_set))
        return response



    async def _async_get_terms_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list:
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
               f"terms/by-name")
        response = await self._async_get_name_request(url, _type="GlossaryTerm",
                                                      _gen_output=self._generate_term_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)
        return response

    def get_terms_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_by_name(filter_string, classification_names, body,start_from, page_size,
                                           output_format, output_format_set))
        return response

    async def _async_get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
               f"{term_guid}")
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_term_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)
        return response

    def get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_by_guid(term_guid, element_type, body,  output_format, output_format_set))
        return response

    async def _async_find_glossary_terms(self, search_string: str, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, type_name: str = "GlossaryTerm",
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
               f"by-search-string")
        response = await self._async_find_request(url, _type= type_name,
                                                  _gen_output=self._generate_term_output,
                                                  search_string = search_string, classification_names = classification_names,
                                                  metadata_element_types = ["GlossaryTerm"],
                                                  starts_with = starts_with, ends_with = ends_with, ignore_case = ignore_case,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)
        return response

    def find_glossary_terms(self, search_string: str, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, type_name: str = "GlossaryTerm",
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_terms(search_string, starts_with,
                                            ends_with, ignore_case, type_name,classification_names,
                                            start_from,
                                            page_size, output_format, output_format_set, body))
        return response


if __name__ == "__main__":
    print("Main-Glossary Manager")

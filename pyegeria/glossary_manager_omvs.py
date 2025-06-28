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
from datetime import datetime
from typing import List

from pyegeria._client import Client
from pyegeria._exceptions import InvalidParameterException
from pyegeria._globals import NO_TERMS_FOUND
from pyegeria._validators import validate_guid, validate_name
from pyegeria.glossary_browser_omvs import GlossaryBrowser
from pyegeria.utils import body_slimmer

def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


"params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to the query string"


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/classification-manager"


class GlossaryManager(GlossaryBrowser):
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

        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    #
    #       Get Valid Values for Enumerations
    #

    def __validate_term_status__(self, status: str) -> bool:
        """Return True if the status is a legal glossary term status"""
        recognized_term_status = self.get_glossary_term_statuses()
        return status in recognized_term_status

    async def _async_create_glossary(
        self,
        display_name: str,
        description: str,
        language: str = "English",
        usage: str = None,
    ) -> str:
        """Create a new glossary. Async version.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        language: str, optional, default = "English"
            The language the used for the glossary
        usage: str, optional, default = None
            How the glossary is intended to be used


        Returns
        -------
        str
            The GUID of the created glossary.

        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries"
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryProperties",
                "qualifiedName": self.__create_qualified_name__("Glossary", display_name),
                "displayName": display_name,
                "description": description,
                "language": language,
                "usage": usage,
            },
        }
        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", None)

    def create_glossary(
        self,
        display_name: str,
        description: str,
        language: str = "English",
        usage: str = None,
    ) -> str:
        """Create a new glossary.

        Parameters
        ----------
        display_name: str
            The name of the new glossary. This will be used to produce a unique qualified name for the glossary.
        description: str
            A description of the glossary.
        language: str, optional, default = "English"
            The language the used for the glossary
        usage: str, optional, default = None
            How the glossary is intended to be used


        Returns
        -------
        str
            The GUID of the created glossary.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_glossary(display_name, description, language, usage)
        )
        return response

    async def _async_delete_glossary(self, glossary_guid: str, cascade:bool = False) -> None:
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
        cascade_str = str(cascade).lower()
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/remove?cascadedDelete={cascade_str}"
        )

        await self._async_make_request("POST", url)

    def delete_glossary(self, glossary_guid: str, cascade: bool = False) -> None:
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
        loop.run_until_complete(self._async_delete_glossary(glossary_guid, cascade))

    async def _async_update_glossary(
        self,
        glossary_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> None:
        """Update Glossary.

        Async version.

        Parameters
        ----------
        glossary_guid: str
            The ID of the glossary to update.
        body: dict
            A dict containing the properties to update.
        is_merge_update: bool, optional, default = True
            If true, then only those properties specified in the body will be updated. If false, then all the
            properties of the glossary will be replaced with those of the body.
        for_lineage: bool, optional, default = False
            Normally false. Used when we want to retrieve elements that have been delete but have a Memento entry.
        for_duplicate_processing: bool, optional, default = False
            Normally false. Set true when Egeria is told to skip deduplication because another system will do it.


        Returns
        -------
        None

        Notes
        -----

        Sample body:

            {
                "class" : "ReferenceableRequestBody",
                "elementProperties" :
                    {
                        "class" : "GlossaryProperties",
                        "qualifiedName" : "MyGlossary",
                        "displayName" : "My Glossary",
                        "description" : "This is an example glossary"
                    }
            }
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/update?isMergeUpdate={is_merge_update}&forLineage={for_lineage}&"
            f"forDuplicateProcessing={for_duplicate_processing}"
        )

        await self._async_make_request("POST", url, body_slimmer(body))

    def update_glossary(
        self,
        glossary_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
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
        for_lineage: bool, optional, default = False
            Normally false. Used when we want to retrieve elements that have been delete but have a Memento entry.
        for_duplicate_processing: bool, optional, default = False
            Normally false. Set true when Egeria is told to skip deduplication because another system will do it.


        Returns
        -------
        None

        Notes
        -----

        Sample body:

            {
                "class" : "ReferenceableRequestBody",
                "elementProperties" :
                    {
                        "class" : "GlossaryProperties",
                        "qualifiedName" : "MyGlossary",
                        "displayName" : "My Glossary",
                        "description" : "This is an example glossary"
                    }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_glossary(
                glossary_guid,
                body,
                is_merge_update,
                for_lineage,
                for_duplicate_processing,
            )
        )

    #
    #       Glossaries
    #




    #
    # Glossary Categories
    #
    async def _async_create_category(
        self,
        glossary_guid: str,
        display_name: str,
        description: str,
        is_root_category: bool = False,
    ) -> str:
        """Create a new category within the specified glossary. Async Version.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        is_root_category: bool, [default=False], optional
            Is this category a root category?


        Returns
        -------
        A string with the GUID of the new category..

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/categories?isRootCategory={is_root_category}"
        )
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryCategoryProperties",
                "qualifiedName": self.__create_qualified_name__("Category", display_name),
                "displayName": display_name,
                "description": description,
            },
        }
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", None)

    def create_category(
        self,
        glossary_guid: str,
        display_name: str,
        description: str,
        is_root_category: bool = False,
    ) -> str:
        """Create a new category within the specified glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        is_root_category: bool, [default=False], optional
            Is this category a root category?

        Returns
        -------
        A string with the GUID of the new category..

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_category(glossary_guid, display_name, description, is_root_category)
        )
        return response

    async def _async_update_category(
        self,
        category_guid: str,
        display_name: str,
        description: str,
        qualified_name: str = None,
        effective_time: str = None,
        update_description: str = None,
        is_merge_update: bool = True,
    ) :
        """Create a new category within the specified glossary. Async Version.

        Parameters
        ----------
        category_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        qualified_name: str, [default=None], optional
            Unique identifier for the glossary category. Must be specified if not a merge update.
        effective_time: datetime, [default=None], optional
            Time when the category becomes effective.
        update_description: str, [default=None], optional
            Description of the update to the category.
        is_merge_update: bool, [default=True], optional
            Should this be a merge or a replace?


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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        if (not is_merge_update and qualified_name is None):
            raise ValueError('qualified_name must be specified for a replace update')
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{category_guid}/update?isMergeUpdate={is_merge_update}"
        )
        body = {
            "class": "ReferenceableUpdateRequestBody",
            "effectiveTime": effective_time,
            "updateDescription": update_description,
            "elementProperties": {
                "class": "GlossaryCategoryProperties",
                "qualifiedName": qualified_name ,
                "displayName": display_name,
                "description": description
            },
        }
        response = await self._async_make_request("POST", url, body_slimmer(body))
        return response.json().get("guid", None)

    def update_category(
        self,
        glossary_guid: str,
        display_name: str,
        description: str,
        qualified_name: str = None,
        effective_time: str = None,
        update_description: str = None,
        is_merge_update: bool = True,
    ) -> str:
        """Create a new category within the specified glossary.

        Parameters
        ----------
        glossary_guid: str,
            Unique identifier for the glossary.
        display_name: str,
            Display name for the glossary category. Will be used as the base for a constructed unique qualified name.
        description: str,
            Description for the category.
        qualified_name: str, [default=None], optional
            Unique identifier for the glossary category. Must be specified if not a merge update.
        effective_time: datetime, [default=None], optional
            Time when the category becomes effective.
        update_description: str, [default=None], optional
            Description of the update to the category.
        is_merge_update: bool, [default=True], optional
            Should this be a merge or a replace?


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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_update_category(glossary_guid, display_name, description,
                                        qualified_name, effective_time, update_description, is_merge_update)
        )
        return response


    async def _async_delete_category(
        self,
        category_guid: str,
    ) -> None:
        """Delete a category. Async Version.

        Parameters
        ----------
        category_guid: str,
            Unique identifier for the category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{category_guid}/remove"
        )

        await self._async_make_request("POST", url)


    def delete_category(
        self,
        category_guid: str,
    ) -> None:
        """Delete a category.

        Parameters
        ----------
        category_guid: str,
            Unique identifier for the category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_category(category_guid)
        )

    async def _async_set_parent_category(
        self,
        parent_category_guid: str, child_category_guid: str) -> None:
        """Set parent category Async Version.

        Parameters
        ----------
        parent_category_guid: str,
            Unique identifier for the parent category.
        child_category_guid: str,
            Unique identifier for the child category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{parent_category_guid}/subcategories/{child_category_guid}"
        )

        await self._async_make_request("POST", url)

    def set_parent_category(self, parent_category_guid: str, child_category_guid: str) -> None:
        """Set parent category

        Parameters
        ----------
        parent_category_guid: str,
            Unique identifier for the parent category.
        child_category_guid: str,
            Unique identifier for the child category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_parent_category(parent_category_guid,child_category_guid)
        )

    async def _async_remove_parent_category(
            self,
            parent_category_guid: str, child_category_guid: str) -> None:
        """Remove parent category relationship. Async Version.

        Parameters
        ----------
        parent_category_guid: str,
            Unique identifier for the parent category.
        child_category_guid: str,
            Unique identifier for the child category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{parent_category_guid}/subcategories/{child_category_guid}/remove"
        )

        await self._async_make_request("POST", url)

    def remove_parent_category(self, parent_category_guid: str, child_category_guid: str) -> None:
        """Remove parent category relationship.

        Parameters
        ----------
        parent_category_guid: str,
            Unique identifier for the parent category.
        child_category_guid: str,
            Unique identifier for the child category.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_parent_category(parent_category_guid, child_category_guid)
            )

    #
    #  Terms
    #
    async def _async_create_controlled_glossary_term(
        self, glossary_guid: str, body: dict
    ) -> str:
        """Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.


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
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm: term name : {$isoTimestamp}",
                    "displayName" : "term name",
                    "aliases": []
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "GT",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "publishVersionIdentifier" : "V1.0",
                    "additionalProperties" :
                    {
                       "propertyName1" : "xxxx",
                       "propertyName2" : "xxxx"
                    }
                },
            "initialStatus" : "DRAFT"
        }

        """

        validate_guid(glossary_guid)
        if self.__validate_term_status__(body["initialStatus"]) is False:
            raise InvalidParameterException("Bad status value")

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/terms/new-controlled"
        )

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_controlled_glossary_term(self, glossary_guid: str, body: dict) -> str:
        """Create a term for a controlled glossary.
            See also: https://egeria-project.org/types/3/0385-Controlled-Glossary-Development/?h=controlled
            The request body also supports the specification of an effective time for the query.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            body: dict
                The dictionary to create te controlled glossary term for. Example below.


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
            "class" : "ReferenceableRequestBody",
            "elementProperties" :
                {
                    "class" : "GlossaryTermProperties",
                    "qualifiedName" : "GlossaryTerm: term name : {$isoTimestamp}",
                    "displayName" : "term name",
                    "aliases": []
                    "summary" : "This is the short description.",
                    "description" : "This is the long description of the term.",
                    "abbreviation" : "GT",
                    "examples" : "Add examples and descriptions here.",
                    "usage" : "This is how the concept described by the glossary term is used.",
                    "publishVersionIdentifier" : "V1.0",
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
            self._async_create_controlled_glossary_term(glossary_guid, body)
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
        version_id: str,
        term_status: str = "PROPOSED",
    ) -> str:
        """Create a new term from an existing term.

            Async Version.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_named: str
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

        validate_guid(glossary_guid)
        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"{glossary_guid}/terms/from-template/{glossary_term_guid}"
        )

        body = {
            "class": "GlossaryTemplateRequestBody",
            "elementProperties": {
                "class": "TemplateProperties",
                "qualifiedName": f"Term-{new_display_name}-{time.asctime()}",
                "displayName": new_display_name,
                "versionIdentifier": version_id,
            },
            "glossaryTermStatus": term_status,
        }

        response = await self._async_make_request("POST", url, body)

        return response.json().get("guid", "Term not created")

    def create_term_copy(
        self,
        glossary_guid: str,
        glossary_term_guid: str,
        new_display_name: str,
        version_id: str,
        term_status: str = "PROPOSED",
    ) -> str:
        """Create a new term from an existing term.

        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary category to retrieve terms from.
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_display_named: str
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
            )
        )

        return response


    async def _async_add_term_to_category(
            self, glossary_term_guid: str, glossary_category_guid: str
            ) -> None:
        """Add the term to the specified category. Async Version.

        Parameters
        ----------
            glossary_term_guid : str
                Unique identifier for the glossary term to assign.
            glossary_category_guid: str
                Unique identifier for the category the term will be assigned to.

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

        validate_guid(glossary_term_guid)
        validate_guid(glossary_category_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{glossary_category_guid}/terms/{glossary_term_guid}"
        )
        body = {
            "class": "RelationshipRequestBody",
            "properties": {
                "class": "GlossaryTermCategorization"

                }
            }

        await self._async_make_request("POST", url, body)


    def add_term_to_category(self, glossary_term_guid: str, glossary_category_guid: str) -> None:
        """Add the term to the specified category.

        Parameters
        ----------
            glossary_term_guid : str
                Unique identifier for the glossary term to assign.
            glossary_category_guid: str
                Unique identifier for the category the term will be assigned to.

        Returns
        -------

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
            self._async_add_term_to_category(glossary_term_guid, glossary_category_guid)
            )

    async def _async_remove_term_from_category(
            self, glossary_term_guid: str, glossary_category_guid: str
            ) -> None:
        """Remove the term from the specified category. Async Version.

        Parameters
        ----------
            glossary_term_guid : str
                Unique identifier for the glossary term to assign.
            glossary_category_guid: str
                Unique identifier for the category the term will be assigned to.

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

        validate_guid(glossary_term_guid)
        validate_guid(glossary_category_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"categories/{glossary_category_guid}/terms/{glossary_term_guid}/remove"
        )
        await self._async_make_request("POST", url)


    def remove_term_from_category(self, glossary_term_guid: str, glossary_category_guid: str) -> None:
        """Remove the term from the specified category.

        Parameters
        ----------
            glossary_term_guid : str
                Unique identifier for the glossary term to assign.
            glossary_category_guid: str
                Unique identifier for the category the term will be assigned to.

        Returns
        -------

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
            self._async_remove_term_from_category(glossary_term_guid, glossary_category_guid)
            )

    async def _async_add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict = None,
            for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:
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

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
             "class" : "RelationshipRequestBody",
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
            body = {"class": "RelationshipRequestBody",
                    "properties":
                        {"class": "GlossaryTermRelationship",}
                }

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ]
            )

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}{possible_query_params}"
        )

        await self._async_make_request("POST", url, body_slimmer(body))


    def add_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict = None,
            for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:
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

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

        {
         "class" : "RelationshipRequestBody",
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
                                                       body, for_lineage, for_duplicate_processing)
            )


    async def _async_update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict = None,
        for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:

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

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
         "class" : "RelationshipRequestBody",
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

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ]
            )

        if body is None:
            body = {"properties": {"class": "RelationshipRequestBody"}}

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}/update{possible_query_params}"
        )

        await self._async_make_request("POST", url, body_slimmer(body))


    def update_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, body: dict,
            for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:
        """Update a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to update. A list of relationship types can be found using get_term_relationship_types().
        body: dict
            Details of the relationship to update.
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

        Notes
        ----
        Body is currently required but can be empty except for class. Basic structure is:

            {
         "class" : "RelationshipRequestBody",
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
                                                          body,for_lineage,for_duplicate_processing)
            )

    async def _async_remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str, effective_time: str = None,
            for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:
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

        possible_query_params = query_string(
            [
                ("forLineage", for_lineage),
                ("forDuplicateProcessing", for_duplicate_processing),
                ]
            )

        body = {"properties": {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time
            }
        }

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/"
            f"terms/{term1_guid}/relationships/{relationship_type}/terms/{term2_guid}/remove{possible_query_params}"
        )

        await self._async_make_request("POST", url, body_slimmer(body))


    def remove_relationship_between_terms(
            self, term1_guid: str, term2_guid: str, relationship_type: str,  effective_time: str = None,
            for_lineage: bool = False, for_duplicate_processing: bool = False) -> None:
        """Remove a relationship between terms.

        Parameters
        ----------
        term1_guid : str
            Unique identifier of the first glossary term in relationship.
        term2_guid : str
            Unique identifier of the second glossary term in relationship.
        relationship_type: str
            Type of relationship to remove. A list of relationship types can be found using get_term_relationship_types().
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
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_relationship_between_terms(term1_guid, term2_guid, relationship_type,
                                                          effective_time, for_lineage, for_duplicate_processing)
            )



    async def _async_add_confidentiality_to_term(
        self,
        glossary_term_guid: str,
        confidentiality_level: int,
    ) -> None:
        """Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.


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
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/elements/"
            f"{glossary_term_guid}/confidentiality"
        )

        body = {
            "class": "ClassificationRequestBody",
            "properties": {
                "class": "GovernanceClassificationProperties",
                "levelIdentifier": confidentiality_level,
            },
        }

        await self._async_make_request("POST", url, body)
        return

    def add_confidentiality_to_term(
        self,
        glossary_term_guid: str,
        confidentiality_level: int,
    ) -> str:
        """Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            confidentiality_level: int
                The level of confidentiality to classify the term with.


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
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_confidentiality_to_term(
                glossary_term_guid, confidentiality_level
            )
        )

        return

    async def _async_add_subject_area_to_term(
        self, glossary_term_guid: str, subject_area: str
    ) -> None:
        """Add the confidentiality classification to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.


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
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/elements/"
            f"{glossary_term_guid}/subject-area-member"
        )

        body = {
            "class": "ClassificationRequestBody",
            "properties": {
                "class": "SubjectAreaMemberProperties",
                "subjectAreaName": subject_area,
            },
        }

        await self._async_make_request("POST", url, body)
        return

    def add_subject_area_to_term(
        self, glossary_term_guid: str, subject_area: str
    ) -> None:
        """Add the confidentiality classification to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            subject_area: str
                The subject area to classify the term with.


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
        See https://egeria-project.org/types/4/0421-Governance-Classification-Levels/?h=confidential#governance-classification-levels
        for a list of default confidentiality levels.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_subject_area_to_term(glossary_term_guid, subject_area)
        )

        return

    async def _async_update_term(
        self,
        glossary_term_guid: str,
        body: dict,
        is_merge_update: bool = False,
        for_lineage: bool = False,
        for_duplicate_processig: bool = False,
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

        validate_guid(glossary_term_guid)
        is_merge_update_s = str(is_merge_update).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processig).lower()

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate={is_merge_update_s}&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}"
        )

        await self._async_make_request("POST", url, body)
        return

    def update_term(
        self,
        glossary_term_guid: str,
        body: dict,
        is_merge_update: bool = True,
        for_lineage: bool = False,
        for_duplicate_processig: bool = False,
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
            self._async_update_term(
                glossary_term_guid,
                body,
                is_merge_update,
                for_lineage,
                for_duplicate_processig,
            )
        )

        return

    async def _async_update_term_version_id(
        self,
        glossary_term_guid: str,
        new_version_identifier: str,
    ) -> None:
        """Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.


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
        This is a useful example of a term update, specifying a new version identifier.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/terms/{glossary_term_guid}/"
            f"update?isMergeUpdate=true"
        )

        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryTermProperties",
                "publishVersionIdentifier": new_version_identifier,
            },
        }
        await self._async_make_request("POST", url, body)
        return

    def update_term_version_id(
        self,
        glossary_term_guid: str,
        new_version_identifier: str,
    ) -> None:
        """Update a glossary term's version identifier

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.
            new_version_identifier: str
                The new version identifier to update the term with.


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
        This is a useful example of a term update, specifying a new version identifier.

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_term_version_id(
                glossary_term_guid, new_version_identifier
            )
        )

    async def _async_undo_term_update(self, glossary_term_guid: str) -> None:
        """Undo an update to a glossary term

            Async Version.

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.

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
        This creates a new version with the state of the term before the last update.

        """

        validate_guid(glossary_term_guid)

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-manager/glossaries/terms/"
            f"{glossary_term_guid}/undo"
        )

        await self._async_make_request("POST", url)

    def undo_term_update(self, glossary_term_guid: str) -> None:
        """Undo an update to a glossary term

        Parameters
        ----------
            glossary_term_guid: str
                Unique identifier for the source glossary term.

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
        This creates a new version with the state of the term before the last update.

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_undo_term_update(glossary_term_guid))



    async def _async_delete_term(
        self,
        term_guid: str,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> list | str:
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
            f"terms/{term_guid}/remove?forLineage={for_lineage}&forDuplicateProcessing={for_duplicate_processing}"
        )

        await self._async_make_request("POST", url)
        return

    def delete_term(
        self,
        term_guid: str,
        for_lineage: bool = False,
        for_duplicate_processing: bool = False,
    ) -> list | str:
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
            self._async_delete_term(term_guid, for_lineage, for_duplicate_processing)
        )

        return

    async def _async_relate_terms(self, term1_guid: str, term2_guid: str, relationship: str) -> None:
        pass


if __name__ == "__main__":
    print("Main-Glossary Manager")

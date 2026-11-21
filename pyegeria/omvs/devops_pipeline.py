"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Devops Pipeline View Service client.

    Egeria 6.4 (odpi/egeria#9463) adds the Branch classification (model 0280): it marks an element as
    holding the files for one branch of a source code repository. This client wraps the two requests that
    set and clear it. The other devops-pipeline requests (storage volumes and so on) are not wrapped yet.

    Every URL path comes from pyegeria.core.egeria_6_4_names, so a rename is one edit there.
"""

from typing import Optional

from loguru import logger
from pyegeria.core import egeria_6_4_names as e64
from pyegeria.core.egeria_6_4_bodies import checked_body, e64_url, refuse
from pyegeria.core._server_client import ServerClient
from pyegeria.core.async_runner import run_sync
from pyegeria.core.utils import dynamic_catch
from pyegeria.models import (
    DeleteRelationshipRequestBody,
    MetadataSourceRequestBody,
    NewClassificationRequestBody,
    NewRelationshipRequestBody,
)

class DevopsPipeline(ServerClient):
    """
    Client for the Devops Pipeline View Service.

    Today it sets and clears the Branch classification, which needs Egeria 6.4 (odpi/egeria#9463).

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
    token : str, optional
        Supply a token instead of using userId/password discovery.
    timeout : int, optional
        An optional timeout for requests.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = None):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
        self.url_marker = e64.DEVOPS_PIPELINE
        self.open_metadata_root = f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/"
        self.devops_pipeline_command_root = self.open_metadata_root + e64.DEVOPS_PIPELINE

    #
    # Branch classification (model 0280)
    #

    @dynamic_catch
    async def _async_set_element_as_branch(self, element_guid: str,
                                           body: Optional[dict | NewClassificationRequestBody] = None,
                                           display_name: Optional[str] = None, scope: Optional[str] = None,
                                           purpose: Optional[str] = None, url: Optional[str] = None) -> None:
        """Classify an element as holding the files for one branch of a source code repository. Async version.

        Needs Egeria 6.4 (odpi/egeria#9463); an older Egeria does not have this request.

        Parameters
        ----------
        element_guid: str
            The element to classify, for example a SourceControlLibrary.
        body: dict | NewClassificationRequestBody, optional
            A NewClassificationRequestBody whose properties are BranchProperties: displayName, scope,
            purpose and url. BranchProperties has no label or description. Leave it out to classify with no
            properties, or use the keywords instead.
        display_name, scope, purpose, url: str, optional
            The BranchProperties, as a convenience instead of `body`. Not with `body`.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
            Refused locally, before Egeria: `body` and keywords together; a body class other than
            NewClassificationRequestBody; properties of a class other than BranchProperties, or with no
            class; keys BranchProperties does not read, such as label or description.
        PyegeriaAPIException
            Raised by the server when an issue arises in processing a valid request.
        PyegeriaNotAuthorizedException
            The principal does not have authorization for the requested action.

        Example
        -------
        ``{"class": "NewClassificationRequestBody", "properties": {"class": "BranchProperties",
        "displayName": "main", "scope": "repository", "purpose": "default branch", "url": "https://..."}}``
        """
        method = "set_element_as_branch"
        keywords = {"displayName": display_name, "scope": scope, "purpose": purpose, "url": url}
        keywords = {k: v for k, v in keywords.items() if v is not None}
        if keywords:
            if body is not None:
                refuse(method, f"{method} takes either a body or the Branch keywords, not both.")
            body = {"class": "NewClassificationRequestBody",
                    "properties": {"class": e64.BRANCH_PROPERTIES, **keywords}}
        payload = checked_body(body, method, request_class="NewClassificationRequestBody",
                               properties_classes={e64.BRANCH_PROPERTIES})
        request_url = e64_url(self.platform_url, self.server_name, e64.BRANCH_SET, elementGUID=element_guid)
        await self._async_make_request("POST", request_url, payload)
        logger.info(f"Classified {element_guid} as a Branch.")

    @dynamic_catch
    def set_element_as_branch(self, element_guid: str, body: Optional[dict | NewClassificationRequestBody] = None,
                              display_name: Optional[str] = None, scope: Optional[str] = None,
                              purpose: Optional[str] = None, url: Optional[str] = None) -> None:
        """Classify an element as holding the files for one branch of a source code repository.

        Needs Egeria 6.4 (odpi/egeria#9463). See `_async_set_element_as_branch` for the parameters: a
        NewClassificationRequestBody with BranchProperties (displayName, scope, purpose, url; no label or
        description), or those four as keywords.
        """
        return run_sync(self._async_set_element_as_branch(element_guid, body, display_name, scope, purpose, url))

    @dynamic_catch
    async def _async_clear_element_as_branch(self, element_guid: str,
                                             body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """Remove the Branch classification from an element. Async version.

        Needs Egeria 6.4 (odpi/egeria#9463); an older Egeria does not have this request.

        Parameters
        ----------
        element_guid: str
            The element to declassify.
        body: dict | MetadataSourceRequestBody, optional
            A MetadataSourceRequestBody (externalSourceGUID/Name, effectiveTime, forLineage,
            forDuplicateProcessing). Left out, a bare MetadataSourceRequestBody is sent. Its "class" may be
            left out; any other class is refused.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
            A body class other than MetadataSourceRequestBody, refused locally.
        PyegeriaAPIException
            Raised by the server when an issue arises in processing a valid request.
        PyegeriaNotAuthorizedException
            The principal does not have authorization for the requested action.
        """
        payload = checked_body(body, "clear_element_as_branch", request_class="MetadataSourceRequestBody",
                               default_body={"class": "MetadataSourceRequestBody"})
        request_url = e64_url(self.platform_url, self.server_name, e64.BRANCH_REMOVE, elementGUID=element_guid)
        await self._async_make_request("POST", request_url, payload)
        logger.info(f"Removed the Branch classification from {element_guid}.")

    @dynamic_catch
    def clear_element_as_branch(self, element_guid: str,
                                body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """Remove the Branch classification from an element.

        Needs Egeria 6.4 (odpi/egeria#9463). Sends a MetadataSourceRequestBody (a bare one when `body` is left
        out). See `_async_clear_element_as_branch`.
        """
        return run_sync(self._async_clear_element_as_branch(element_guid, body))


if __name__ == "__main__":
    print("Devops Pipeline")

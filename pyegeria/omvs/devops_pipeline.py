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
from pydantic import BaseModel, ValidationError

from pyegeria.core import egeria_6_4_names as e64
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core._server_client import ServerClient
from pyegeria.core.async_runner import run_sync
from pyegeria.core.utils import dynamic_catch
from pyegeria.models import (
    DeleteRelationshipRequestBody,
    MetadataSourceRequestBody,
    NewClassificationRequestBody,
    NewRelationshipRequestBody,
)

_BODY_MODELS = {
    "NewRelationshipRequestBody": NewRelationshipRequestBody,
    "DeleteRelationshipRequestBody": DeleteRelationshipRequestBody,
    "NewClassificationRequestBody": NewClassificationRequestBody,
    "MetadataSourceRequestBody": MetadataSourceRequestBody,
}


def _refuse(method: str, reason: str) -> None:
    raise PyegeriaInvalidParameterException(None, context={"caller_method": method},
                                            additional_info={"reason": reason})


def _checked_6_4_body(body: Optional[dict | BaseModel], request_class: str, properties_class: Optional[str],
                      method: str, default_body: bool = False) -> Optional[str]:
    """The JSON to send for an Egeria 6.4 request, or None to send no body.

    Shared by the A3 wrappers (ProjectManager, SchemaMaker, DevopsPipeline). Refuses locally, with words,
    what Egeria would reject or silently drop:

    - a request body of another class than `request_class`;
    - properties of another class than `properties_class`, or with no class (6.4 rejects a wrong class; a
      parent class passes Egeria's check and loses the subclass's fields, the TR-89 case);
    - property keys the class does not read (Egeria ignores them silently), per PROPERTIES_CLASS_FIELDS.

    The body is sent as given: only the keys the caller set, so it equals the `.http` sample it came from.
    With no body, nothing is sent, unless `default_body` asks for a bare body of `request_class`.
    """
    if body is None:
        if not default_body:
            return None
        body = {"class": request_class}
    if isinstance(body, BaseModel):
        data = body.model_dump(mode="json", by_alias=True, exclude_unset=True, exclude_none=True)
    elif isinstance(body, dict):
        data = dict(body)
    else:
        _refuse(method, f"{method} takes a dict or a {request_class}, not a {type(body).__name__}.")
    sent_class = data.setdefault("class", request_class)
    if sent_class != request_class:
        _refuse(method, f"{method} sends a {request_class}; the body is a {sent_class}.")

    props = data.get("properties")
    if properties_class and props is not None:
        if not isinstance(props, dict):
            _refuse(method, f"{method}: properties must be a dict of {properties_class}.")
        props_class = props.get("class")
        if props_class != properties_class:
            named = f"names {props_class}" if props_class else "names no class"
            _refuse(method, f"{method} needs properties of class {properties_class}; the body {named}.")
        from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
        known = PROPERTIES_CLASS_FIELDS.get(properties_class)
        if known:
            unread = sorted(set(props) - {"class"} - set(known[1]))
            if unread:
                _refuse(method, f"{properties_class} does not read {', '.join(unread)}; Egeria would drop "
                                f"{'it' if len(unread) == 1 else 'them'} silently.")

    try:
        validated = _BODY_MODELS[request_class].model_validate(data)
    except ValidationError as error:
        _refuse(method, f"{method}: the body is not a valid {request_class}: {error}")
    return validated.model_dump_json(by_alias=True, exclude_none=True, exclude_unset=True)


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
                _refuse(method, f"{method} takes either a body or the Branch keywords, not both.")
            body = {"class": "NewClassificationRequestBody",
                    "properties": {"class": e64.BRANCH_PROPERTIES, **keywords}}
        payload = _checked_6_4_body(body, "NewClassificationRequestBody", e64.BRANCH_PROPERTIES, method)
        request_url = self.open_metadata_root + e64.BRANCH_SET.format(elementGUID=element_guid)
        if payload:
            await self._async_make_request("POST", request_url, payload)
        else:
            await self._async_make_request("POST", request_url)
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
        payload = _checked_6_4_body(body, "MetadataSourceRequestBody", None, "clear_element_as_branch",
                                    default_body=True)
        request_url = self.open_metadata_root + e64.BRANCH_REMOVE.format(elementGUID=element_guid)
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

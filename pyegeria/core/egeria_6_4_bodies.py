# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The one request-body checker for the Egeria 6.4 wrappers (odpi/egeria#9463).

Every 6.4 wrapper (GovernanceOfficer, DataEngineer, ProjectManager, SchemaMaker, DevopsPipeline) builds its
URL and checks its body here, so the five modules follow one rule:

1. **Writes** (create, update, delete, link, detach, set, clear) send the caller's body exactly as given,
   after the checks. A dict is never re-dumped through a pyegeria model: the models are ``extra='ignore'``
   (models.py), so a dump would drop keys the model lacks and reformat timestamps. A model the caller built
   is sent as its own JSON dump (by alias, without None). With no body, attach and detach send none; a
   request that needs a body (create, update) is refused with words.
2. **Reads** are not checked here; they use the shared ServerClient helpers, whose added defaults equal
   Egeria's.
3. **The class check** takes a set of accepted Properties classes (for example DataValueProperties or
   LiteralDataValueProperties) and refuses, before sending, a properties object of any other class or of
   none, naming the accepted classes.
4. **Unread keys are refused**, naming the class and the keys it reads, using the generated
   PROPERTIES_CLASS_FIELDS (public setters through the whole superclass chain, as Jackson binds). Egeria
   would ignore them silently. A class that is not in the table at all is only warned about.
5. The URL builder joins a path from pyegeria.core.egeria_6_4_names to the view server's open-metadata root.

The generated table lives in md_processing (the same wheel); it is imported lazily, here and only here.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel, ValidationError

from pyegeria.core._exceptions import PyegeriaInvalidParameterException


def e64_url(platform_url: str, view_server: str, path: str, **guids: str) -> str:
    """The full URL of a 6.4 request whose path (from egeria_6_4_names) is relative to open-metadata/."""
    return f"{platform_url}/servers/{view_server}/api/open-metadata/{path.format(**guids)}"


def refuse(method: str, reason: str) -> None:
    """Raise the local refusal every check uses: nothing reaches Egeria."""
    raise PyegeriaInvalidParameterException(None, context={"caller_method": method},
                                            additional_info={"reason": reason})


def properties_class_fields() -> dict[str, tuple[str, tuple[str, ...]]]:
    """The generated PROPERTIES_CLASS_FIELDS table (class -> (kind, keys it reads))."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    return PROPERTIES_CLASS_FIELDS


def _accepted(classes: str | Iterable[str]) -> tuple[str, ...]:
    return (classes,) if isinstance(classes, str) else tuple(classes)


def _named(classes: tuple[str, ...]) -> str:
    return " or ".join(classes)


def require_body(body: Any, method: str) -> None:
    """Refuse a request that needs a body (create, update) sent with none."""
    if body is None:
        refuse(method, f"{method} needs a request body: Egeria 6.4 refuses this request without one, and an "
                       f"update with no body changes nothing.")


def check_properties_class(properties: Any, accepted: str | Iterable[str], method: str) -> str:
    """Refuse a properties object whose class is not one of `accepted`; return the class it names."""
    accepted = _accepted(accepted)
    if not isinstance(properties, dict):
        refuse(method, f"{method}: properties must be an object of class {_named(accepted)}, "
                       f"not a {type(properties).__name__}.")
    sent = properties.get("class")
    if sent not in accepted:
        named = f"names class {sent}" if sent else "names no class"
        refuse(method, f"{method}: the properties object {named}; this request accepts {_named(accepted)}. "
                       f"Egeria rejects a properties object of the wrong class, and a parent class would lose "
                       f"the subclass's fields.")
    return sent


def check_unread_keys(properties: dict, properties_class: str, method: str) -> None:
    """Refuse property keys `properties_class` does not read (Egeria would drop them silently)."""
    known = properties_class_fields().get(properties_class)
    if known is None:
        logger.warning(f"{method}: {properties_class} is not in PROPERTIES_CLASS_FIELDS, so its keys are not "
                       f"checked; regenerate the table (scripts/gen_properties_class_fields.py).")
        return
    reads = known[1]
    unread = sorted(set(properties) - {"class"} - set(reads))
    if unread:
        refuse(method, f"{method}: {properties_class} does not read {', '.join(unread)}; Egeria would drop "
                       f"{'it' if len(unread) == 1 else 'them'} silently. {properties_class} reads: "
                       f"{', '.join(reads)}.")


def _request_model(request_class: str):
    import pyegeria.models as models
    return getattr(models, request_class, None)


def checked_body(body: Optional[dict | BaseModel], method: str, *, request_class: Optional[str] = None,
                 properties_classes: Optional[str | Iterable[str]] = None, required: bool = False,
                 default_body: Optional[dict] = None, int_keys: Iterable[str] = ()) -> Optional[str]:
    """Check a 6.4 write body locally and return the JSON to send, or None to send no body.

    Parameters
    ----------
    body : dict | BaseModel | None
        The caller's body. A dict is sent exactly as given; a model is sent as its own dump.
    method : str
        The wrapper's name, used in every refusal.
    request_class : str, optional
        The request-body class the endpoint takes (for example NewRelationshipRequestBody). A body naming
        another class is refused. A body naming no class is given this one: the only key ever added, since
        Egeria cannot read a body without it. The body is also validated against that pyegeria model (the
        result is discarded, never sent).
    properties_classes : str | iterable of str, optional
        The Properties classes accepted. When given and the body has properties, they must name one of them
        and carry only keys that class reads.
    required : bool, default False
        Refuse a missing body (create and update).
    default_body : dict, optional
        Sent when no body is given (delete sends ``{"class": "DeleteElementRequestBody", "cascadedDelete": ...}``).
    int_keys : iterable of str
        Property keys that must be an int when present (``position``: 0 means unset).
    """
    if body is None:
        if required:
            require_body(body, method)
        if default_body is None:
            return None
        body = default_body

    if isinstance(body, BaseModel):
        data = body.model_dump(mode="json", by_alias=True, exclude_none=True)
    elif isinstance(body, dict):
        data = body
    else:
        refuse(method, f"{method} takes a dict or a {request_class or 'request-body model'}, "
                       f"not a {type(body).__name__}.")

    if request_class:
        sent_class = data.get("class")
        if sent_class is None:
            data = {"class": request_class, **data}
        elif sent_class != request_class:
            refuse(method, f"{method} sends a {request_class}; the body is a {sent_class}.")

    props = data.get("properties")
    if properties_classes and props is not None:
        props_class = check_properties_class(props, properties_classes, method)
        check_unread_keys(props, props_class, method)
        for key in int_keys:
            value = props.get(key)
            if value is not None and type(value) is not int:
                refuse(method, f"{method}: {key} must be an int (0 means unset), not "
                               f"{type(value).__name__} {value!r}.")

    model = _request_model(request_class) if request_class else None
    if model is not None:
        try:
            model.model_validate(data)
        except ValidationError as error:
            refuse(method, f"{method}: the body is not a valid {request_class}: "
                           f"{error.errors(include_url=False)}")

    return json.dumps(data)

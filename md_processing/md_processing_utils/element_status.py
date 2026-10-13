# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Map Dr.Egeria's status attributes onto the status property an element type actually has.

Egeria no longer accepts `initialStatus` on new-element requests (removed 2025-12-15).
Each type carries its own kind of status in its properties instead: `contentStatus`
(authored content -- glossary terms, collections, data structures, ...),
`activityStatus` (actions and processes -- notes, to-dos, meetings, ...),
`deploymentStatus` (infrastructure, solution components, capabilities, ...), or
none at all (actors, plain assets, comments). See ISSUE-113.
"""
from __future__ import annotations

from loguru import logger

from md_processing.md_processing_utils.element_status_fields import STATUS_FIELDS_BY_PROPERTIES_CLASS

# Dr.Egeria attribute -> Egeria property, for the type-specific status attributes.
EXPLICIT_STATUS_ATTRIBUTES = {
    "Content Status": "contentStatus",
    "Activity Status": "activityStatus",
    "Deployment Status": "deploymentStatus",
}

# Valid values of each status enum (ContentStatus, ActivityStatus, DeploymentStatus).
VALID_STATUS_VALUES = {
    "contentStatus": {"DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", "ACTIVE", "DEPRECATED",
                      "OBSOLETE", "OTHER"},
    "activityStatus": {"REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED", "FOR_INFO",
                       "COMPLETED", "INVALID", "IGNORED", "FAILED", "CANCELLED", "ABANDONED", "OTHER"},
    "deploymentStatus": {"PROPOSED", "UNDER_DEVELOPMENT", "DEVELOPMENT_COMPLETE", "APPROVED_FOR_DEPLOYMENT",
                         "REJECTED", "STANDBY", "ACTIVE", "DISABLED", "FAILED", "OTHER"},
}

# Where a written `Status` value fits more than one of a type's fields, the first wins.
_PREFERENCE = ("contentStatus", "activityStatus", "deploymentStatus")


def _value(attributes: dict, name: str):
    value = (attributes.get(name) or {}).get("value")
    return value if value not in (None, "") else None


def _is_default(attributes: dict, name: str) -> bool:
    return bool((attributes.get(name) or {}).get("is_default"))


def element_status_properties(properties_class: str, attributes: dict) -> dict:
    """Return the status properties to put in a `properties_class` body.

    Values the user wrote come first; values the parser filled in from spec
    defaults only fill a property nothing written has set.

    1. A written `Content Status` / `Activity Status` / `Deployment Status` is sent
       when the type has that property, and dropped with a warning when it does not.
    2. A written `Status` goes to the first of the type's status properties not yet
       set whose enum accepts the value.
    3. Defaulted type-specific attributes fill their property if it is still unset.
    4. A defaulted `Status` only ever fills `contentStatus`, as before, so a default
       never starts overwriting an activity or deployment status (an upsert re-run
       would otherwise reset it).

    A properties class this table does not know keeps the old behaviour: the
    type-specific attributes pass through and `Status` goes to `contentStatus`.
    """
    known = properties_class in STATUS_FIELDS_BY_PROPERTIES_CLASS
    supported = STATUS_FIELDS_BY_PROPERTIES_CLASS.get(properties_class, ())
    has = (lambda field: field in supported) if known else (lambda field: True)
    result: dict = {}

    def explicit(defaults: bool):
        for attr, field in EXPLICIT_STATUS_ATTRIBUTES.items():
            value = _value(attributes, attr)
            if value is None or _is_default(attributes, attr) != defaults or field in result:
                continue
            if not has(field):
                if not defaults:
                    logger.warning(f"'{attr}' ignored: {properties_class} has no {field} property.")
                continue
            result[field] = value

    explicit(defaults=False)

    status = _value(attributes, "Status")
    status_is_default = _is_default(attributes, "Status")
    if status is not None and not status_is_default:
        upper = str(status).strip().upper()
        candidates = [f for f in _PREFERENCE if f in supported] if known else ["contentStatus"]
        placed = False
        for field in candidates:
            if field not in result and upper in VALID_STATUS_VALUES[field]:
                result[field] = upper
                placed = True
                break
        if not placed and known:
            if not supported:
                logger.warning(f"'Status' ignored: {properties_class} has no status property.")
            elif not any(f in result for f in candidates):
                logger.warning(f"'Status' value '{status}' ignored: not valid for {properties_class}'s "
                               f"{' / '.join(supported)}.")

    explicit(defaults=True)

    if status is not None and status_is_default and "contentStatus" not in result and has("contentStatus"):
        upper = str(status).strip().upper()
        if upper in VALID_STATUS_VALUES["contentStatus"]:
            result["contentStatus"] = upper
    return result

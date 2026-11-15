# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The element statuses Egeria accepts in a `limitResultsByStatus` filter, and the check that keeps others out.

`limitResultsByStatus` filters on an element's *header* status, Egeria's `ElementStatus` enum. It is not one of
the status *properties* some types carry (contentStatus, deploymentStatus, ...). A value from one of those (DRAFT,
APPROVED, UNDER_DEVELOPMENT, ...) used to reach Egeria and come back as a 400 ("Cannot deserialize value of type
ElementStatus from String "DRAFT""), seen 2026-11-13 from a find whose caller meant "draft governance
definitions". pyegeria now refuses it before sending, and says which status property the value belongs to and
where that property lives.

Everything here is offline. Egeria's valid metadata values for these properties are declared per property (the
typeName makes no difference) and equal the Java enums, so a server read would give the same words with a new
way to fail (STATUS-VALID-VALUES-LAZ-2026-11-13).

This module imports nothing from pyegeria, so the request-body models can use it without an import cycle.
"""
from __future__ import annotations

import warnings
from typing import Iterable, List, NamedTuple, Optional

#: Egeria's ElementStatus values, from ElementStatus.java at odpi/egeria 3c8970b656 (2026-09-21), the enum
#: in the build laz runs (002a3ef1, 2026-11-13). Older Egerias (5.x) accepted more (DRAFT, PROPOSED,
#: APPROVED, ...): when Egeria's enum changes, change this set and name the new source.
ELEMENT_STATUSES = frozenset({"UNKNOWN", "ACTIVE", "INVALID", "DELETED", "OTHER"})
ELEMENT_STATUS_SOURCE = "ElementStatus.java @ odpi/egeria 3c8970b656"

#: Element statuses no element can hold: every one of the 676 types on laz (2026-11-13) has
#: validElementStatusList [ACTIVE, DELETED]. They pass the check (Egeria accepts them) but match nothing.
UNHELD_ELEMENT_STATUSES = frozenset({"UNKNOWN", "INVALID", "OTHER"})


class StatusProperty(NamedTuple):
    """A status property some types carry, the values its enum allows, and where it lives."""
    name: str            # the property, e.g. contentStatus
    enum: str            # the Java enum its values come from
    where: str           # where the property lives, for the hint
    on_elements: bool    # declared on an entity or classification (so a find can filter on it); else relationships
    values: frozenset


#: The status properties a misplaced `limitResultsByStatus` value most likely belongs to. Values: the Java enums
#: in open-metadata-framework .../frameworks/openmetadata/enums (odpi/egeria 8de9572c4d), equal to laz's
#: get_valid_metadata_values and to the enums at bae9bcb1 (Architect, 2026-11-13). Where: the types that declare
#: each property (subtypes inherit), from laz's type system. Element-carried properties first.
STATUS_PROPERTIES = (
    StatusProperty("contentStatus", "ContentStatus", "AuthoredReferenceable, DataAsset", True, frozenset({
        "DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "OBSOLETE", "OTHER"})),
    StatusProperty("deploymentStatus", "DeploymentStatus",
                   "DigitalProduct, Infrastructure, SoftwareCapability, SolutionComponent, the Promise classification",
                   True, frozenset({
        "PROPOSED", "UNDER_DEVELOPMENT", "DEVELOPMENT_COMPLETE", "APPROVED_FOR_DEPLOYMENT", "REJECTED", "STANDBY",
        "ACTIVE", "DISABLED", "FAILED", "OTHER"})),
    StatusProperty("activityStatus", "ActivityStatus", "Process; ActionTarget and NotificationSubscriber relationships",
                   True, frozenset({
        "REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED", "FOR_INFO", "COMPLETED", "INVALID",
        "IGNORED", "FAILED", "CANCELLED", "ABANDONED", "OTHER"})),
    StatusProperty("membershipStatus", "CollectionMemberStatus", "collection memberships", False, frozenset({
        "UNKNOWN", "DISCOVERED", "PROPOSED", "IMPORTED", "VALIDATED", "DEPRECATED", "OBSOLETE", "OTHER"})),
    StatusProperty("termRelationshipStatus", "TermRelationshipStatus", "term relationships", False, frozenset({
        "DRAFT", "ACTIVE", "DEPRECATED", "OBSOLETE", "OTHER"})),
    StatusProperty("termAssignmentStatus", "TermAssignmentStatus", "semantic assignments", False, frozenset({
        "DISCOVERED", "PROPOSED", "IMPORTED", "VALIDATED", "DEPRECATED", "OBSOLETE", "OTHER"})),
)


class InvalidElementStatus(ValueError):
    """A `limitResultsByStatus` value that isn't one of Egeria's element statuses. A ValueError, so a pydantic
    validator reports it as a field error (which pyegeria turns into PyegeriaInvalidParameterException)."""


class UnheldElementStatusWarning(UserWarning):
    """A `limitResultsByStatus` value Egeria accepts but no element can hold (UNKNOWN, INVALID, OTHER)."""


def _phrase(prop: StatusProperty, first: bool) -> str:
    if prop.on_elements:
        return f"{'a ' if first else 'or '}{prop.name}{' value' if first else ''} ({prop.where})"
    return f"{'a ' if first else 'or '}{prop.name}{' value' if first else ''} on {prop.where}"


def _why(value: str) -> str:
    props = [p for p in STATUS_PROPERTIES if value in p.values]
    if not props:
        return f"{value} is not an element status, nor a value of any status property"
    words = f"{value} is " + ", ".join(_phrase(p, i == 0) for i, p in enumerate(props)) + ", not an element status"
    filterable = [p.name for p in props if p.on_elements]
    return words + (f"; filter on {' or '.join(filterable)} instead" if filterable else "")


def check_element_statuses(values: Optional[Iterable[str]], *, field: str = "limit_results_by_status"
                           ) -> Optional[List[str]]:
    """`values` upper-cased, or InvalidElementStatus naming each value that isn't an element status, the status
    property it belongs to and where that lives. None and an empty list pass through unchanged (no status
    filter). A lone string counts as one value. UNKNOWN, INVALID and OTHER pass, with an UnheldElementStatusWarning:
    Egeria accepts them, but no element can hold them.

    Under ``-W error`` (or a ``filterwarnings = error`` test setting) that warning becomes an exception. Raised in
    the request-body validator, it is not a ValueError, so pydantic doesn't wrap it: it propagates raw as
    UnheldElementStatusWarning, not as a ValidationError / PyegeriaInvalidParameterException."""
    if values is None:
        return None
    if isinstance(values, str):
        values = [values]
    out: List[str] = []
    bad: List[str] = []
    for v in values:
        s = str(v).strip().upper()
        if s in ELEMENT_STATUSES:
            out.append(s)
        else:
            bad.append(_why(s or repr(v)))
    if bad:
        raise InvalidElementStatus(
            f"{field}: {'; '.join(bad)}. Element statuses are {', '.join(sorted(ELEMENT_STATUSES))} "
            f"({ELEMENT_STATUS_SOURCE}).")
    unheld = [s for s in out if s in UNHELD_ELEMENT_STATUSES]
    if unheld:
        warnings.warn(
            f"{field}: {', '.join(unheld)} {'is an element status' if len(unheld) == 1 else 'are element statuses'}"
            f" Egeria accepts, but no type lets an element hold {'it' if len(unheld) == 1 else 'them'} (every "
            f"type's validElementStatusList is ACTIVE, DELETED), so {'it matches' if len(unheld) == 1 else 'they match'}"
            f" nothing.", UnheldElementStatusWarning, stacklevel=2)
    return out

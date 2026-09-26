"""
Find-then-update for Dr.Egeria `Link` commands on MULTI_LINK relationship types.

Egeria never rejects or merges a second instance of a MULTI_LINK relationship
between the same two elements, so a `Link` command that always creates would
add a duplicate every time a markdown file is re-run. Each caller names the
properties that identify "the same" instance for its type (e.g. label +
iscQualifiedName for lineage), and this updates that instance instead.
"""
from typing import Any, Awaitable, Callable, Optional, Tuple

from loguru import logger

from pyegeria.core.relationship_multiplicity import async_find_matching_relationship


def update_body(properties: dict) -> dict:
    return {"class": "UpdateRelationshipRequestBody", "properties": properties, "mergeUpdate": True}


async def async_link_or_update(
    client,
    relationship_type: str,
    end1_guid: Optional[str],
    end2_guid: Optional[str],
    match_properties: dict[str, Any],
    create: Callable[[], Awaitable[Optional[str]]],
    update: Optional[Callable[[str], Awaitable[Any]]] = None,
    explicit_guid: Optional[str] = None,
) -> Tuple[Optional[str], bool]:
    """Update the relationship this command describes if it exists, else create it.

    `end1_guid`/`end2_guid` must be in the relationship type's own end order.
    `explicit_guid` (a relationship GUID the user supplied) skips the lookup.
    With no `update`, an existing match is reused unchanged -- for types with no
    update endpoint. Returns `(relationship_guid, created)`.
    """
    rel_guid = explicit_guid
    if not rel_guid:
        try:
            rel_guid = await async_find_matching_relationship(
                client, relationship_type, end1_guid, end2_guid, match_properties)
        except Exception as e:  # noqa: BLE001 -- a failed lookup must not block the link itself
            logger.warning(f"Could not look up existing {relationship_type} between {end1_guid} and "
                           f"{end2_guid}; creating a new one: {e}")

    if rel_guid:
        if update:
            await update(rel_guid)
            logger.success(f"Updated existing {relationship_type} {rel_guid} ({match_properties})")
        else:
            logger.info(f"{relationship_type} {rel_guid} already exists ({match_properties}); reusing it")
        return rel_guid, False

    return await create(), True

# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 4: Create ToDo / Meeting / Review for a user with no personal profile.

get_my_profile() returns the string "No elements found" when the user has no personal profile, and
_async_create_my_todo/_meeting/_review indexed it as a dict: Dr.Egeria's Create ToDo, Create Meeting and
Create Review failed with "string indices must be integers, not 'str'" on the round-trip probe (scratch
platform, demo user with no profile). They now stop with a sentence that names the user and what's missing,
before any request is sent.
"""
import pytest

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.omvs.my_profile import MyProfile


def _client(profile_response, sent):
    client = object.__new__(MyProfile)  # no constructor: no connection check, no server
    client.user_id = "garygeeke"
    client.my_profile_guid = None

    async def get_my_profile(*args, **kwargs):
        if isinstance(profile_response, dict):
            client.my_profile_guid = profile_response["elementHeader"]["guid"]
        return profile_response

    async def make_request(*args, **kwargs):
        sent.append(args)
        raise AssertionError("no create request may be sent without a profile")

    client._async_get_my_profile = get_my_profile
    client._async_make_request = make_request
    client.__create_qualified_name__ = lambda kind, name: f"{kind}::{name}"
    client._MyProfile__create_qualified_name__ = client.__create_qualified_name__
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("method, what", [
    ("_async_create_my_todo", "create a to-do"),
    ("_async_create_meeting", "create a meeting"),
    ("_async_create_review", "create a review"),
])
async def test_no_profile_is_a_sentence_not_a_type_error(method, what):
    sent = []
    client = _client(NO_ELEMENTS_FOUND, sent)
    with pytest.raises(ValueError) as exc:
        await getattr(client, method)("RTP name", qualified_name="RTP::QN")
    assert str(exc.value) == (f"User garygeeke has no personal profile in Egeria, so it can't {what}; "
                              "create the user's profile first")
    assert sent == []


@pytest.mark.asyncio
async def test_profile_guid_is_looked_up_once_and_reused():
    client = _client({"elementHeader": {"guid": "Person-1"}}, [])
    assert await client._async_require_my_profile_guid("create a to-do") == "Person-1"
    client._async_get_my_profile = None  # a second lookup would fail
    assert await client._async_require_my_profile_guid("create a review") == "Person-1"

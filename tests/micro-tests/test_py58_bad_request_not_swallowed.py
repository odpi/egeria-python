"""PY-58 read-back: an Egeria 400 is not read as "the collection is absent"."""
import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from pyegeria import PyegeriaBadRequestException, PyegeriaInvalidParameterException, PyegeriaNotFoundException
from pyegeria.omvs.collection_manager import CollectionManager

BODY_400 = {"class": "VoidResponse", "relatedHTTPCode": 400,
            "exceptionErrorMessage": "The name passed on the name parameter of the getAssetsByName operation is null",
            "exceptionErrorMessageId": "OPEN-METADATA-400-004"}


def _manager(error):
    m = CollectionManager.__new__(CollectionManager)
    m.__async_get_guid__ = AsyncMock(side_effect=error)
    setattr(m, "_CollectionManager__async_get_guid__", m.__async_get_guid__)
    return m


def _bad_request():
    response = httpx.Response(200, json=BODY_400, request=httpx.Request("POST", "https://egeria/x"))
    return PyegeriaBadRequestException(response, {"caller": "t"}, additional_info=BODY_400)


def test_a_400_from_the_qualified_name_lookup_is_raised_not_swallowed():
    m = _manager(_bad_request())
    with pytest.raises(PyegeriaBadRequestException):
        asyncio.run(CollectionManager._resolve_collection_guid(m, collection_qname="Coll::1"))


def test_a_plain_not_found_still_falls_through_to_not_found():
    m = _manager(PyegeriaInvalidParameterException(None, None, {"reason": "not found"}))
    m.__async_get_guid__ = m.__async_get_guid__
    with pytest.raises(PyegeriaNotFoundException):
        asyncio.run(CollectionManager._resolve_collection_guid(m, collection_qname="Coll::1"))

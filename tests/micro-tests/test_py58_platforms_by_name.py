"""PY-58: get_platforms_by_name("*") and the label of an Egeria 400."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from pyegeria import PyegeriaAPIException, PyegeriaInvalidParameterException
from pyegeria.core._base_server_client import BaseServerClient
from pyegeria.omvs.runtime_manager import RuntimeManager

# the real answer of laz 6.4 (read-only, 2026-11-23) to POST /runtime-manager/platforms/by-name with no filter
BODY_400 = {
    "class": "VoidResponse",
    "relatedHTTPCode": 400,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.InvalidParameterException",
    "actionDescription": "getPlatformsByName",
    "exceptionErrorMessage": "The name passed on the name parameter of the getAssetsByName operation is null",
    "exceptionErrorMessageId": "OPEN-METADATA-400-004",
    "exceptionErrorMessageParameters": ["name", "getAssetsByName"],
    "exceptionSystemAction": "The system is unable to process the request.",
    "exceptionUserAction": "Correct the code in the caller to provide the name.",
}


def _response(body):
    return httpx.Response(200, json=body, request=httpx.Request("POST", "https://egeria/by-name"))


def _client():
    c = BaseServerClient.__new__(BaseServerClient)
    c.user_id = "u"
    c.user_pwd = None
    c.token = "t"
    import threading
    c._thread_local = threading.local()
    return c


# ── fix 2: the 400 is an invalid-parameter error, with Egeria's own words ──
def test_a_related_400_is_an_invalid_parameter_exception_not_a_server_error():
    from pyegeria.core._base_server_client import PyegeriaBadRequestException
    exc = PyegeriaBadRequestException(_response(BODY_400), {"caller": "t"}, additional_info=BODY_400)
    assert isinstance(exc, PyegeriaInvalidParameterException)
    assert "SERVER_ERROR_500" not in str(exc)


def test_the_400_message_shows_egeria_message_and_id():
    from pyegeria.core._base_server_client import PyegeriaBadRequestException
    exc = PyegeriaBadRequestException(_response(BODY_400), {"caller": "t"}, additional_info=BODY_400)
    text = str(exc)
    assert "OPEN-METADATA-400-004" in text and "The name passed on the name parameter" in text
    assert exc.response_egeria_msg_id == "OPEN-METADATA-400-004" and exc.related_http_code == 400


def test_the_400_is_still_caught_by_a_handler_for_the_old_class():
    from pyegeria.core._base_server_client import PyegeriaBadRequestException
    assert issubclass(PyegeriaBadRequestException, PyegeriaAPIException)


def test_make_request_raises_it_for_a_200_wrapping_a_400():
    client = _client()
    client.timeout = 10
    client.headers = {}
    client.text_headers = {}
    session = MagicMock()
    session.post = AsyncMock(return_value=_response(BODY_400))
    client.session = session
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        asyncio.run(BaseServerClient._async_make_request(client, "POST", "https://egeria/by-name", {"class": "FilterRequestBody"}))
    assert "OPEN-METADATA-400-004" in str(info.value)
    assert "SERVER_ERROR_500" not in str(info.value)


def test_404_401_and_403_keep_their_classes():
    from pyegeria import PyegeriaNotFoundException
    assert issubclass(PyegeriaNotFoundException, PyegeriaAPIException)
    assert not issubclass(PyegeriaNotFoundException, PyegeriaInvalidParameterException)


# ── fix 1: "*" means all platforms ──
def _manager():
    m = RuntimeManager.__new__(RuntimeManager)
    m.default_platform_name = "Default Local OMAG Server Platform"
    m.runtime_command_root = "http://x/runtime-manager"
    m._async_get_name_request = AsyncMock(return_value=["by-name"])
    m._async_get_platforms_by_type = AsyncMock(return_value=["by-type"])
    return m


def test_star_is_all_platforms_through_the_by_type_lookup():
    m = _manager()
    out = asyncio.run(RuntimeManager._async_get_platforms_by_name(m, "*"))
    assert out == ["by-type"]
    assert m._async_get_platforms_by_type.call_args.kwargs["filter_string"] is None
    m._async_get_name_request.assert_not_called()


def test_no_name_and_no_default_is_all_platforms():
    m = _manager()
    m.default_platform_name = ""
    assert asyncio.run(RuntimeManager._async_get_platforms_by_name(m, None)) == ["by-type"]


def test_a_real_name_still_goes_to_by_name():
    m = _manager()
    assert asyncio.run(RuntimeManager._async_get_platforms_by_name(m, "My Platform")) == ["by-name"]
    assert m._async_get_name_request.call_args.kwargs["filter_string"] == "My Platform"
    m._async_get_platforms_by_type.assert_not_called()


def test_no_name_with_a_default_still_uses_the_default_name():
    m = _manager()
    asyncio.run(RuntimeManager._async_get_platforms_by_name(m, None))
    assert m._async_get_name_request.call_args.kwargs["filter_string"] == "Default Local OMAG Server Platform"

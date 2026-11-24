"""PY-24: a caller can say WHY a read failed when Egeria hides the element from them."""
import httpx
import pytest

from pyegeria import (PyegeriaAPIException, PyegeriaBadRequestException, PyegeriaNotFoundException,
                      PyegeriaUnauthorizedException)
from pyegeria.view.egeria_folders import is_gone_error

BODY_400_010 = {
    "class": "VoidResponse", "relatedHTTPCode": 400,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.InvalidParameterException",
    "exceptionErrorMessageId": "OMAG-REPOSITORY-HANDLER-400-010",
    "exceptionErrorMessage": "OMAG-REPOSITORY-HANDLER-400-010 The element with guid 1234 is not visible to the caller "
                             "because it is anchored to or classified with [Anchors, Promise]",
}
BODY_403_007 = {
    "class": "VoidResponse", "relatedHTTPCode": 403,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.UserNotAuthorizedException",
    "exceptionErrorMessageId": "OPEN-METADATA-SECURITY-403-007",
    "exceptionErrorMessage": "OPEN-METADATA-SECURITY-403-007 User erin is not authorized to access the anchor of 1234",
}
BODY_400_004 = {
    "class": "VoidResponse", "relatedHTTPCode": 400,
    "exceptionErrorMessageId": "OPEN-METADATA-400-004",
    "exceptionErrorMessage": "The name passed on the name parameter of the getAssetsByName operation is null",
}
BODY_NOT_FOUND = {"class": "VoidResponse", "relatedHTTPCode": 404,
                  "exceptionErrorMessageId": "OMAG-REPOSITORY-HANDLER-404-002",
                  "exceptionErrorMessage": "The element was not found"}


def _response(body):
    return httpx.Response(200, json=body, request=httpx.Request("POST", "https://egeria/x"))


def _bad_request(body):
    return PyegeriaBadRequestException(_response(body), {"caller": "t"}, additional_info=body)


def _unauthorized(body):
    return PyegeriaUnauthorizedException(_response(body), {"caller": "t"}, additional_info=body)


def test_a_400_010_body_reads_not_visible():
    assert _bad_request(BODY_400_010).not_visible is True


def test_a_403_007_body_reads_not_visible():
    assert _unauthorized(BODY_403_007).not_visible is True


def test_an_ordinary_400_004_reads_not_visible_false():
    assert _bad_request(BODY_400_004).not_visible is False


def test_not_found_and_a_bare_token_failure_are_not_not_visible():
    nf = PyegeriaNotFoundException(_response(BODY_NOT_FOUND), {"caller": "t"}, additional_info=BODY_NOT_FOUND)
    assert nf.not_visible is False
    bare = PyegeriaUnauthorizedException(httpx.Response(401, request=httpx.Request("POST", "https://e/x")),
                                         {"caller": "t"}, additional_info={"userid": "u"})
    assert bare.not_visible is False


@pytest.mark.parametrize("make,body", [(_bad_request, BODY_400_010), (_bad_request, BODY_400_004),
                                       (_unauthorized, BODY_403_007)])
def test_the_exception_carries_egeria_message_id(make, body):
    assert make(body).egeria_message_id == body["exceptionErrorMessageId"]


def test_a_plain_api_exception_carries_egeria_message_id():
    body = {"class": "VoidResponse", "relatedHTTPCode": 500, "exceptionErrorMessageId": "OMAG-COMMON-500-001",
            "exceptionErrorMessage": "boom"}
    assert PyegeriaAPIException(_response(body), {"caller": "t"}, additional_info=body).egeria_message_id == \
        "OMAG-COMMON-500-001"


def test_is_gone_error_still_true_for_its_existing_cases_and_now_for_the_new_ids():
    old = {"class": "VoidResponse", "relatedHTTPCode": 403,
           "exceptionClassName": "org.x.UserNotAuthorizedException",
           "exceptionErrorMessageId": "OPEN-METADATA-SECURITY-403-020",
           "exceptionErrorMessage": "User is not authorized to issue an operation read"}
    assert is_gone_error(_unauthorized(old)) is True
    nf = PyegeriaNotFoundException(_response(BODY_NOT_FOUND), {"caller": "t"}, additional_info=BODY_NOT_FOUND)
    assert is_gone_error(nf) is True
    assert is_gone_error(_bad_request(BODY_400_004)) is False
    assert is_gone_error(ConnectionError("down")) is False
    assert is_gone_error(_bad_request(BODY_400_010)) is True and is_gone_error(_unauthorized(BODY_403_007)) is True

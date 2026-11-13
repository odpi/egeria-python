# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 6: a failed command always says what failed.

str(PyegeriaException) is a multi-line report that starts with a newline, so the Dr.Egeria summary row
built from f"Execution failed: {str(e)}" read just "Execution failed:" (round-trip probe 2026-11-12:
Schema Maker, Blog/Journal/Activity Entry, nine Asset Maker technology-type creates). Every failure path
now prints the exception type and message on one line, with Egeria's message id when there is one.
"""
import json

from pyegeria import PyegeriaException
from pyegeria.core._exceptions import PyegeriaClientException

from md_processing.v2.processors import describe_exception


class _Response:
    def __init__(self, payload, status=400):
        self._payload = payload
        self.status_code = status
        self.url = "https://localhost:19443/servers/view-server/api/open-metadata/schema-maker/schema-types"
        self.reason_phrase = json.dumps(payload)
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


def test_pyegeria_exception_with_a_text_response_is_one_line():
    e = PyegeriaException(response="No catalog template is registered for technology type 'Kafka Topic' on "
                                   "this Egeria server.", context={"type_name": "Kafka Topic"})
    assert str(e).startswith("\n")  # the reason the summary row used to be empty
    assert describe_exception(e) == ("PyegeriaException: No catalog template is registered for technology "
                                     "type 'Kafka Topic' on this Egeria server.")


def test_egeria_message_and_id_are_used_when_the_response_has_them():
    payload = {"class": "GUIDResponse", "relatedHTTPCode": 400,
               "exceptionErrorMessageId": "OMAG-REPOSITORY-HANDLER-400-001",
               "exceptionErrorMessage": "OMAG-REPOSITORY-HANDLER-400-001 An unsupported property named newProperties "
                                        "was passed to the repository services"}
    e = PyegeriaClientException(_Response(payload), context={"caller method": "x"})
    text = describe_exception(e)
    assert text.startswith("PyegeriaClientException: OMAG-REPOSITORY-HANDLER-400-001 An unsupported property")
    assert "\n" not in text
    assert text.count("OMAG-REPOSITORY-HANDLER-400-001") == 1  # not repeated when the message already has it


def test_message_id_is_appended_when_the_message_lacks_it():
    payload = {"exceptionErrorMessageId": "OMVS-MY-PROFILE-400-002",
               "exceptionErrorMessage": "The personal profile for user garygeeke does not exist"}
    e = PyegeriaClientException(_Response(payload), context={})
    assert describe_exception(e).endswith("does not exist [OMVS-MY-PROFILE-400-002]")


def test_jackson_400_without_an_id():
    payload = {"exceptionClassName": "com.fasterxml.jackson.databind.exc.InvalidTypeIdException",
               "exceptionErrorMessage": "Could not resolve subtype of : missing type id property 'class'\n at x"}
    text = describe_exception(PyegeriaClientException(_Response(payload), context={}))
    assert text == ("PyegeriaClientException: Could not resolve subtype of : missing type id property 'class' "
                    "at x")


def test_plain_exceptions_never_come_out_empty():
    assert describe_exception(ValueError("boom")) == "ValueError: boom"
    assert describe_exception(KeyError()) == "KeyError: KeyError()"
    assert describe_exception(RuntimeError("  two\n lines ")) == "RuntimeError: two lines"

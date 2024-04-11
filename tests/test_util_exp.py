"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.

"""

from contextlib import nullcontext as does_not_raise
from json import JSONDecodeError

import pytest

from pyegeria import (
    validate_user_id,
    validate_server_name,
    validate_guid,
    validate_name,
    validate_search_string,
    validate_public,
    validate_url,
    InvalidParameterException,
    print_exception_response,
    is_json,
)


#
#  Test field validators
#
class TestValidators:
    """
    A class to test all the base field validators using Pytest.
    These validators do not require a connection to Egeria.

    Attributes:


    Methods:
        test_validate_user_id(user_id,method_name)
            check for null or empty string

        test_validate_server_name()

        test_validate_public()

        test_validate_url(url, class_name, method_name)

        test_validate_server()

    """

    @pytest.mark.parametrize("user_id, result", [("foo", True), ("", False)])
    def test_validate_user_id(self, user_id, result):
        """
        Test the validator for user_id

        Parameters
        ----------
        user_id : the string to validate
        result :  the expected outcome

        """
        try:
            id_check = validate_user_id(user_id)
            assert id_check == result, "Invalid user id"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize("server_name, result", [("cocoMDS1", True), ("", False)])
    def test_validate_server_name(self, server_name, result):
        """
        Test the validator for a server name

        Parameters
        ----------
        server_name : the string to validate
        result :  the expected outcome

        """
        try:
            assert validate_server_name(server_name) == result, "Invalid Server Name"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize("guid, result", [("12341234-1234213", True), ("", False)])
    def test_validate_guid(self, guid, result):
        """
        Test the validator for a GUID

        Parameters
        ----------
        guid : the string to validate
        result :  the expected outcome

        """
        try:
            assert validate_guid(guid) == result, "Invalid GUID"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize("name, result", [("garygeeke", True), ("", False)])
    def test_validate_name(self, name, result):
        """
        Test the validator for a name

        Parameters
        ----------
        name : the string to validate
        result :  the expected outcome

        """
        try:
            assert validate_name(name) == result, "Invalid Name"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize(
        "search_string, result", [("sustainability", True), ("", False)]
    )
    def test_validate_search_string(self, search_string, result):
        """
        Test the validator for a search_string

        Parameters
        ----------
        search_string : the string to validate
        result :  the expected outcome

        """
        try:
            assert (
                validate_search_string(search_string) == result
            ), "Invalid search string"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize("is_public, result", [(True, True), (None, False)])
    def test_validate_public(self, is_public, result):
        """
        Test the validator for public flag

        Parameters
        ----------
        is_public : the string to validate
        result :  the expected outcome

        """
        try:
            assert validate_public(is_public) == result, "Invalid public flag"

        except InvalidParameterException as e:
            print_exception_response(e)

    @pytest.mark.parametrize(
        "url, result, expectation",
        [
            ("https://google.com", True, does_not_raise()),
            (
                "https://127.0.0.1:9443/open-metadata/platform-services/users/garygeeke/server-platform/servers/active-metadata-store/instance",
                True,
                does_not_raise(),
            ),
            (
                "https://localhost.local:9443/open-metadata/platform-services/users/garygeeke/server-platform/servers/active-metadata-store/instance",
                True,
                does_not_raise(),
            ),
            ("", False, pytest.raises(InvalidParameterException)),
            ("http://localhost:9444", False, pytest.raises(InvalidParameterException)),
        ],
    )
    def test_validate_url(self, url, result, expectation):
        """
        Test the url validator

        Parameters
        ----------
        url : the url string to check
        result : the expected outcome

        """

        with expectation as e:
            res = validate_url(url)
            assert res == result, "Invalid URL"
        if e:
            print_exception_response(e.value)

    def test_is_json(self):
        txt1 = '{"class": "ServerStatusResponse","relatedHTTPCode": 200}'

        txt2 = "<asdfasdf>"
        try:
            out1 = is_json(txt1)
            print(f"\n\nOutput 1 is:{out1}")
            assert out1, "Expected JSON to be there"
            out2 = is_json(txt2)
            print(f"\n\nOutput 2 is {out2}")
            assert not out2, "Expected this not to be a JSON string"
            return
        except JSONDecodeError as e:
            print("didn't expect to be here in is_json")
            print(e)


if __name__ == "__main__":
    print("something")

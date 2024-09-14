"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""

from pyegeria._exceptions import (
    InvalidParameterException,
)
from pyegeria import max_paging_size, body_slimmer, MyProfile, FeedbackManager


class EgeriaMy(MyProfile, FeedbackManager):
    """
    Client to issue Runtime status requests.

    Attributes:

        server_name: str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None


    Methods:
        Inherits from MyProfile, FeedbackManager
    """

    def __init__(
        self,
        server_name: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        MyProfile.__init__(self, server_name, platform_url, user_id, user_pwd, token)
        FeedbackManager.__init__(
            self, server_name, platform_url, user_id, user_pwd, token
        )


if __name__ == "__main__":
    print("Main-Egeria My Client")

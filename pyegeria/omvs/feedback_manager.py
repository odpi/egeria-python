"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module is a facade for the feedback_manager view service.
The methods are inherited from the ServerClient class and provide a simplified interface for interacting
with the feedback_manager view service.
"""

import asyncio
import json
import time
from typing import Any, Optional

from pyegeria.core._server_client import ServerClient


class FeedbackManager(ServerClient):
    """FeedbackManager is a class that extends the Client class. It
    provides methods to CRUD tags, comments and likes for managed
    elements.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a
            default optionally used by the methods when the user
            doesn't pass the user_id on a method call.
         user_pwd: str
            The password associated with the user_id. Defaults to None

         token: str, optional
            bearer token

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.admin_command_root: str = f"{platform_url}/servers/{view_server}api/open-metadata/feedback-manager/"
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id,
            user_pwd,
            token=token,
        )




if __name__ == "__main__":
    print("Main-Feedback Manager")

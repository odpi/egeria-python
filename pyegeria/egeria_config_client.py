"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Client to configure the Egeria platform and servers

"""

from pyegeria.full_omag_server_config import FullServerConfig
from pyegeria.server_operations import  ServerOps


class EgeriaConfig:
    """
    Client for configuring the Egeria Platform and Servers using composition.

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
        Methods are provided by composed sub-clients via delegation.
    """

    def __init__(
        self, server_name: str, platform_url: str, user_id: str, user_pwd: str = None
    ):
        self.server_name = server_name
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        self._config = FullServerConfig(server_name, platform_url, user_id, user_pwd)
        self._ops = ServerOps(server_name, platform_url, user_id, user_pwd)
        self._subclients = [self._config, self._ops]

    def __getattr__(self, name):
        for sub in self._subclients:
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        token_val = None
        for sub in self._subclients:
            token_val = sub.create_egeria_bearer_token(user_id, user_pwd)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        for sub in self._subclients:
            sub.set_bearer_token(token)

    def get_token(self) -> str:
        for sub in self._subclients:
            if hasattr(sub, "get_token"):
                return sub.get_token()
        return None

    def close_session(self) -> None:
        for sub in self._subclients:
            if hasattr(sub, "close_session"):
                try:
                    sub.close_session()
                except Exception:
                    pass


if __name__ == "__main__":
    print("Main-Config Client")

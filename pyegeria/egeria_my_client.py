"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Runtime manager is a view service that supports user interaction with the running platforms.

"""
from pyegeria.feedback_manager_omvs import FeedbackManager
from pyegeria.my_profile_omvs import MyProfile
from pyegeria.utils import body_slimmer

from pyegeria._exceptions import InvalidParameterException


class EgeriaMy:
    """
    Client to issue Runtime status requests using composition of MyProfile and FeedbackManager.

    Attributes:
        view_server: str
            Name of the view server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str, optional
            Bearer token used for authentication.

    Methods:
        Methods are provided by composed sub-clients (MyProfile, FeedbackManager) via delegation.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        # Compose sub-clients
        self._my_profile = MyProfile(view_server, platform_url, user_id, user_pwd, token)
        self._feedback = FeedbackManager(view_server, platform_url, user_id, user_pwd, token)
        # Keep an ordered list for delegation lookups and bulk operations
        self._subclients = [self._my_profile, self._feedback]

    # Delegation: route unknown attributes to first sub-client that has it
    def __getattr__(self, name):
        for sub in self._subclients:
            if hasattr(sub, name):
                return getattr(sub, name)
        raise AttributeError(f"{self.__class__.__name__!s} object has no attribute {name!r}")

    # Token management across subclients
    def create_egeria_bearer_token(self, user_id: str = None, user_pwd: str = None):
        token_val = None
        for sub in self._subclients:
            token_val = sub.create_egeria_bearer_token(user_id, user_pwd)
        return token_val

    def set_bearer_token(self, token: str) -> None:
        for sub in self._subclients:
            sub.set_bearer_token(token)

    def get_token(self) -> str:
        # Return token from the first sub-client that provides it
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
                    # Best-effort close; ignore individual errors
                    pass


if __name__ == "__main__":
    print("Main-Egeria My Client")

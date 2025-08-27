"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This class is meant to be a client for catalog users and currently inherits from
AssetCatalog, CollectionManager, GlossaryManager, and ProjectManager.

"""
from pyegeria.egeria_my_client import EgeriaMy
from pyegeria.asset_catalog_omvs import AssetCatalog
# from pyegeria.collection_manager import CollectionManager
from pyegeria.glossary_manager import GlossaryManager
from pyegeria.project_manager import ProjectManager


class EgeriaCat:
    """
    Catalog-oriented client using composition of AssetCatalog, EgeriaMy, GlossaryManager, and ProjectManager.

    Attributes:
        view_server: str
            Name of the view server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str
            An optional bearer token

    Methods:
        Methods are provided by composed sub-clients via delegation.
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
        self._asset_catalog = AssetCatalog(view_server, platform_url, user_id, user_pwd, token)
        self._my = EgeriaMy(view_server, platform_url, user_id, user_pwd, token)
        self._glossary = GlossaryManager(view_server, platform_url, user_id, user_pwd, token)
        self._projects = ProjectManager(view_server, platform_url, user_id, user_pwd, token)
        self._subclients = [
            self._asset_catalog,
            self._my,
            self._glossary,
            self._projects,
        ]

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
    print("Egeria Cat Client")

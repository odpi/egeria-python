"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Client to configure the Egeria platform and servers

"""
from pyegeria.omvs.core_omag_server_config import CoreServerConfig
from pyegeria.omvs.full_omag_server_config import FullServerConfig
from pyegeria.omvs.server_operations import  ServerOps


class EgeriaConfig:
    """
    Client for managing Egeria configuration using lazy loading.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.token = token

        self._subclient_map = {
            "core_config": CoreServerConfig,
            "full_config": FullServerConfig,
        }
        self._instantiated_clients = {}

    def _get_subclient(self, attr_name: str):
        if attr_name not in self._instantiated_clients:
            client_cls = self._subclient_map[attr_name]
            self._instantiated_clients[attr_name] = client_cls(
                self.view_server, self.platform_url, self.user_id, self.user_pwd, self.token
            )
        return self._instantiated_clients[attr_name]

    def __getattr__(self, name):
        """Resolves attribute via instantiated or mapped subclients"""
        for inst in self._instantiated_clients.values():
            if hasattr(inst, name):
                return getattr(inst, name)
        for attr_name, client_cls in self._subclient_map.items():
            if hasattr(client_cls, name):
                return getattr(self._get_subclient(attr_name), name)
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

    def set_bearer_token(self, token: str) -> None:
        self.token = token
        for sub in self._instantiated_clients.values():
            sub.set_bearer_token(token)

    def close_session(self) -> None:
        for sub in self._instantiated_clients.values():
            if hasattr(sub, "close_session"):
                try: sub.close_session()
                except Exception: pass
        self._instantiated_clients.clear()


if __name__ == "__main__":
    print("Main-Config Client")

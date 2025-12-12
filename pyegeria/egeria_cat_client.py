"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

EgeriaCat: Catalog-oriented client using multiple inheritance.

This client combines methods from:
- AssetCatalog (asset_catalog_omvs)
- GlossaryManager (glossary_manager)
- ProjectManager (project_manager)
- MyProfile (my_profile_omvs)

to provide a single, convenient surface for catalog users.
"""
from pyegeria.asset_catalog import AssetCatalog
from pyegeria.glossary_manager import GlossaryManager
from pyegeria.project_manager import ProjectManager
from pyegeria.my_profile_omvs import MyProfile


class EgeriaCat(ProjectManager, GlossaryManager, AssetCatalog, MyProfile):
    """
    Catalog-oriented client that exposes the combined methods of
    ProjectManager, GlossaryManager, AssetCatalog, and MyProfile via inheritance.

    Notes:
    - ProjectManager is listed first to prefer the BaseServerClient (ServerClient) token/session
      implementations in method resolution order.
    - Each parent class is explicitly initialized to ensure its internal state
      (URLs, roots, etc.) is set up.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        # Initialize each parent explicitly (do not rely on cooperative super)
        ProjectManager.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        GlossaryManager.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        AssetCatalog.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        MyProfile.__init__(self, view_server, platform_url, user_id, user_pwd, token)


if __name__ == "__main__":
    print("Egeria Cat Client")

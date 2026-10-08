"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides a browser for the Product Manager related functions of my_egeria module.


"""

# from textual.geometry import Coordinate  # remove unused/unsupported import
from my_egeria.screens.base_screen import BaseScreen
from my_egeria.services.product_manager_service import ProductManagerService
# from .collection_details import CollectionDetailsScreen
# from .add_collection import AddCollectionScreen
# from .delete_collection import DeleteCollectionScreen
# import asyncio

class ProductManagerBrowser(BaseScreen):

    def __init__(self, product_manager_service: ProductManagerService):
        super().__init__()
        self.product_manager_service = product_manager_service
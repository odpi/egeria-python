"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the browser for the Project MNanager related functions of my_egeria module.


"""
# from textual.geometry import Coordinate  # remove unused/unsupported import
from ..base_screen import BaseScreen
from my_egeria.services.project_manager_service import ProjectManagerService
# from .collection_details import CollectionDetailsScreen
# from .add_collection import AddCollectionScreen
# from .delete_collection import DeleteCollectionScreen
# import asyncio

class ProductManagerBrowser(BaseScreen):

    def __init__(self, product_manager_service: ProjectManagerService):
        super().__init__()
        self.product_manager_service = product_manager_service
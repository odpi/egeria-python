"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Product Catalog OMVS module.

The Product Catalog view service supports browsing digital product catalogs. Egeria
serves it through the generic collection endpoints under the "product-catalog" URL
marker, so it inherits CollectionManager; the methods here use that marker.
"""
import asyncio
from typing import Optional

from typing import Unpack
from pyegeria.core.request_filters import deprecated_names
from pyegeria.core.request_filters import SearchFilters
from pyegeria.core.utils import dynamic_catch
from pyegeria.models import SearchStringRequestBody
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.core.async_runner import run_sync


class ProductCatalog(CollectionManager):
    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
        timeout: int = None):
        CollectionManager.__init__(self, view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
        # Only the methods below use this root; inherited CollectionManager methods keep their
        # own collection-manager root, so they behave exactly as on CollectionManager.
        self.product_catalog_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-catalog"
        )

    @deprecated_names(metadata_element_type_name="metadata_element_type")
    @dynamic_catch
    async def _async_find_digital_product_catalogs(
            self,
            search_string: str = "*",
            metadata_element_type: str = "DigitalProductCatalog",
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True,
            start_from: int = 0,
            page_size: int = 100,
            output_format: str = "JSON",
            report_spec: Optional[str | dict] = None,
            body: Optional[dict | SearchStringRequestBody] = None,
            **kwargs,
    ) -> list | str:
        """Find digital product catalogs, or the products in them, through the product-catalog
        view service. Async version.

        Parameters
        ----------
        search_string : str, default "*"
            String to match; "*" matches every element of the requested type.
        metadata_element_type : str, default "DigitalProductCatalog"
            Type to search for; use "DigitalProduct" to find products.
        starts_with, ends_with, ignore_case : bool
            How the search string is matched.
        start_from, page_size : int
            Paging.
        output_format : str, default "JSON"
            JSON, DICT, LIST, MD, REPORT, ...
        report_spec : str | dict, optional
            Report spec for non-JSON output.
        body : dict | SearchStringRequestBody, optional
            A full request body, used instead of the arguments above.

        Accepts the standard search filters as keyword arguments (see ``SearchFilters``
        in ``pyegeria.core.request_filters``), e.g. ``metadata_element_subtypes=[...]``.

        Returns
        -------
        list | str
            The matching elements, or NO_ELEMENTS_FOUND.

        Notes
        -----
        Sample body:
        {
          "class" : "SearchStringRequestBody",
          "searchString" : "Open Metadata Digital Product Catalog",
          "metadataElementTypeName" : "DigitalProductCatalog"
        }
        """
        url = f"{self.product_catalog_command_root}/collections/by-search-string"
        return await self._async_find_request(
            url, _type=metadata_element_type, _gen_output=self._generate_collection_output,
            search_string=search_string, starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
            start_from=start_from, page_size=page_size,
            output_format=output_format, report_spec=report_spec, body=body, **{"metadata_element_type": metadata_element_type, **kwargs})

    @deprecated_names(metadata_element_type_name="metadata_element_type")
    @dynamic_catch
    def find_digital_product_catalogs(
            self,
            search_string: str = "*",
            metadata_element_type: str = "DigitalProductCatalog",
            starts_with: bool = True,
            ends_with: bool = False,
            ignore_case: bool = True,
            start_from: int = 0,
            page_size: int = 100,
            output_format: str = "JSON",
            report_spec: Optional[str | dict] = None,
            body: Optional[dict | SearchStringRequestBody] = None,
            **kwargs,
    ) -> list | str:
        """Find digital product catalogs, or the products in them ("DigitalProduct"), through the
        product-catalog view service. See _async_find_digital_product_catalogs for the parameters.

        Accepts the standard search filters as keyword arguments (see ``SearchFilters``
        in ``pyegeria.core.request_filters``), e.g. ``metadata_element_subtypes=[...]``.
        """
        return run_sync(self._async_find_digital_product_catalogs(
            search_string, metadata_element_type, starts_with, ends_with, ignore_case,
            start_from, page_size, output_format, report_spec, body, **kwargs))

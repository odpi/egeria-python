# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""
import asyncio
from typing import Any, Dict, List, Optional
from .base_service import BaseService
from my_egeria.utils.config import EgeriaConfig

class CollectionService(BaseService):
    """Wrapper around pyegeria collection functions with token-managed client."""

    def __init__(self, config: Optional[EgeriaConfig] = None, manager=None):
        super().__init__(config=config, manager=manager)

    # ------------------ synchronous API ------------------

    def list_collections(self, search: str = "*") -> List[Dict[str, Any]]:
        """
        Use pyegeria.find_collections with a DICT response.
        """
        res = self._invoke("find_collections", args=(search,), kwargs={"output_format": "DICT"})
        return self._ensure_list_like(res, keys=("collections", "elements", "results", "items"))

    def get_collection_details(self, collection_guid: str) -> Dict[str, Any]:
        if not collection_guid:
            raise ValueError("collection_guid is required")
        res = self._invoke("get_collection", args=(collection_guid,), kwargs={"output_format": "DICT"})
        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        raise ConnectionError(
            "Failed to retrieve collection details (unexpected response shape)."
        )

    def get_collection_members(
        self, collection_guid: str, search: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Synchronous path for completeness (search is ignored by API).
        """
        if not collection_guid:
            raise ValueError("collection_guid is required")
        res = self._invoke(
            "get_member_list",
            args=(),
            kwargs={"collection_guid": collection_guid, "collection_name": None, "collection_qname": None},
        )
        return self._ensure_list_like(res, keys=("members", "elements", "results", "items"))

    def add_collection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a collection via:
          create_collection(display_name, description, category, initial_classifications)
        """
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        display_name = payload.get("display_name") or payload.get("name")
        description = payload.get("description") or payload.get("summary")
        category = payload.get("category") or payload.get("collection_type")
        initial_classifications = payload.get("initial_classifications")  # list[str] or None

        missing = []
        if not display_name:
            missing.append("display_name")
        if not description:
            missing.append("description")
        if not category:
            missing.append("category")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        res = self._invoke(
            "create_collection",
            args=(display_name, description, category, initial_classifications),
            kwargs={},
        )
        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    def delete_collection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a collection via:
          delete_collection(guid)
        """
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        guid = payload.get("guid") or payload.get("collection_guid")
        display_name = payload.get("display_name") or payload.get("name")
        description = payload.get("description") or payload.get("summary")

        missing = []
        if not guid:
            missing.append("guid")
        if not display_name:
            missing.append("display_name")
        if not description:
            missing.append("description")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        res = self._invoke(
            "delete_collection",
            args=(guid),
            kwargs={},
        )
        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}


    # ------------------ async API (robust, non-blocking) ------------------

    async def list_collections_async(self, search: str = "*") -> List[Dict[str, Any]]:
        """
        Prefer native async; if it is not awaitable or stalls, fall back to sync in a worker thread.
        """
        try:
            res = self._invoke("_async_find_collections", args=(search,), kwargs={"output_format": "DICT"})
        except Exception:
            return await asyncio.to_thread(self.list_collections, search)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.list_collections, search)
        except Exception:
            return await asyncio.to_thread(self.list_collections, search)

        return self._ensure_list_like(res, keys=("collections", "elements", "results", "items"))

    async def get_collection_details_async(self, collection_guid: str) -> Dict[str, Any]:
        if not collection_guid:
            raise ValueError("collection_guid is required")
        try:
            res = self._invoke("_async_get_collection", args=(collection_guid,), kwargs={"output_format": "DICT"})
        except Exception:
            return await asyncio.to_thread(self.get_collection_details, collection_guid)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.get_collection_details, collection_guid)
        except Exception:
            return await asyncio.to_thread(self.get_collection_details, collection_guid)

        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        raise ConnectionError(
            "Failed to retrieve collection details (unexpected response shape)."
        )

    async def get_collection_members_async(
        self, collection_guid: str, search: str = ""
    ) -> List[Dict[str, Any]]:
        if not collection_guid:
            raise ValueError("collection_guid is required")
        try:
            res = self._invoke(
                "_async_get_member_list",
                args=(),
                kwargs={"collection_guid": collection_guid, "collection_name": None, "collection_qname": None},
            )
        except Exception:
            return await asyncio.to_thread(self.get_collection_members, collection_guid, search)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.get_collection_members, collection_guid, search)
        except Exception:
            return await asyncio.to_thread(self.get_collection_members, collection_guid, search)

        return self._ensure_list_like(res, keys=("members", "elements", "results", "items"))

    async def add_collection_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        display_name = payload.get("display_name") or payload.get("name")
        description = payload.get("description") or payload.get("summary")
        category = payload.get("category") or payload.get("collection_type")
        initial_classifications = payload.get("initial_classifications")

        missing = []
        if not display_name:
            missing.append("display_name")
        if not description:
            missing.append("description")
        if not category:
            missing.append("category")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        try:
            res = self._invoke(
                "_async_create_collection",
                args=(display_name, description, category, initial_classifications),
                kwargs={},
            )
        except Exception:
            return await asyncio.to_thread(self.add_collection, payload)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.add_collection, payload)
        except Exception:
            return await asyncio.to_thread(self.add_collection, payload)

        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    async def delete_collection_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        guid = payload.get("guid") or payload.get("collection_guid")

        missing = []
        if not guid:
            missing.append("guid")

        try:
            res = self._invoke(
                "_async_delete_collection",
                args=(guid),
                kwargs={},
            )
        except Exception:
            return await asyncio.to_thread(self.delete_collection, guid)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.delete_collection, payload)
        except Exception:
            return await asyncio.to_thread(self.delete_collection, payload)

        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    # ------------------ small helpers ------------------

    def _ensure_list_like(self, res: Any, keys: tuple[str, ...]) -> List[Dict[str, Any]]:
        """
        Normalize various possible list-like shapes to a list[dict].
        """
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            for k in keys:
                v = res.get(k)
                if isinstance(v, list):
                    return v
        # Fallback: wrap non-list truthy into a list
        return [] if res is None else ([res] if res else [])

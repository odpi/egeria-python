# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the functions of my_egeria module.


"""

import os
import sys
import importlib
import logging
import asyncio
from typing import Any, Dict, List, Optional
from .base_service import BaseService
from my_egeria.utils.config import EgeriaConfig


# Hook for tests to inject a mock client
GlossaryAuthorView = None


class GlossaryService(BaseService):
    """Wrapper around pyegeria's glossary/term functions with token-managed client."""

    def __init__(self, config: Optional[EgeriaConfig] = None, manager=None):
        super().__init__(config=config, manager=manager)

        # Logger for traceability
        self._log = logging.getLogger(__name__)
        if not self._log.handlers:
            logging.basicConfig(level=logging.INFO)

        # Legacy envs are optional; tests may rely on them, but prod code should not hard-fail
        self._legacy_url = os.getenv("EGERIA_SERVER_URL", "")
        self._legacy_name = os.getenv("EGERIA_SERVER_NAME", "")
        self._gav_factory: Optional[Any] = None
        self._gclient: Optional[Any] = None

        mod = sys.modules.get("my_egeria.services.glossary_service")
        GAV = getattr(mod, "GlossaryAuthorView", None) if mod else None

        if GAV is None:
            try:
                mod = importlib.import_module("my_egeria.services.glossary_service")
                GAV = getattr(mod, "GlossaryAuthorView", None)
            except Exception:
                GAV = None

        if callable(GAV):
            self._gav_factory = GAV
            self._log.info("GlossaryService: GAV factory registered (lazy construction)")
        else:
            self._log.info("GlossaryService: No GAV factory detected; will use token-managed client fallback")

    def _ensure_gclient(self) -> Optional[Any]:
        """Lazily construct the monkeypatched client if a factory exists."""
        if self._gclient is not None:
            return self._gclient
        if not callable(self._gav_factory):
            return None

        args_matrix = [
            (self._legacy_name, self._legacy_url),
            (
                self._legacy_name,
                self._legacy_url,
                os.getenv("EGERIA_USER", ""),
                os.getenv("EGERIA_USER_PASSWORD", ""),
            ),
        ]
        for args in args_matrix:
            try:
                self._gclient = self._gav_factory(*args)
                return self._gclient
            except Exception:
                continue
        try:
            self._gclient = self._gav_factory()
            return self._gclient
        except Exception:
            return None

    # --------- sync API ---------

    def list_glossaries(self, search: str = "*") -> List[Dict[str, Any]]:
        """
        find_glossaries(search_string='*', ..., output_format='DICT')
        Prefer the monkeypatched GlossaryAuthorView client if present to avoid network latency.
        """
        client = self._ensure_gclient()
        if client and hasattr(client, "find_glossaries"):
            try:
                # If the client supports output_format, request DICT; otherwise call with just search
                return self._ensure_list_like(
                    client.find_glossaries(search, output_format="DICT"),
                    keys=("glossaries", "elements", "results", "items")
                )
            except TypeError:
                return self._ensure_list_like(
                    client.find_glossaries(search),
                    keys=("glossaries", "elements", "results", "items")
                )

        # Fallback to token-managed client
        res = self._invoke("find_glossaries", args=(search,), kwargs={"output_format": "DICT"})
        return self._ensure_list_like(res, keys=("glossaries", "elements", "results", "items"))


    def add_glossary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        create_glossary(display_name, description, language='English', usage=None)
        """
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        display_name = payload.get("display_name") or payload.get("name")
        description = payload.get("description")
        language = payload.get("language", "English")
        usage = payload.get("usage")

        missing = []
        if not display_name:
            missing.append("display_name")
        if not description:
            missing.append("description")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        res = self._invoke(
            "create_glossary",
            args=(display_name, description, language, usage),
            kwargs={},
        )
        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    def delete_glossary(self, glossary_guid: str, cascade: bool = False) -> bool:
        """
        delete_glossary(glossary_guid, cascade=False)
        """
        if not glossary_guid:
            raise ValueError("glossary_guid is required")

        res = self._invoke("delete_glossary", args=(glossary_guid,), kwargs={"cascade": cascade})
        if isinstance(res, dict):
            return bool(res.get("success", True))
        return True if res is None else bool(res)

    def get_terms(self, search: str = "", glossary_guid: str = None) -> List[Dict[str, Any]]:
        """
        List terms across all glossaries using:
          find_glossary_terms(search_string, glossary_guid=None, output_format="DICT")
        """
        res = self._invoke(
            "find_glossary_terms",
            args=((search or "*"),),
            kwargs={"glossary_guid": glossary_guid, "output_format": "DICT"},
        )
        return self._ensure_list_like(
            res, keys=("terms", "elements", "results", "items")
        )

    def add_term(self, glossary_guid: str, payload: Dict[str, Any]) -> Dict[str, Any]:

        """
        create_controlled_glossary_term(glossary_guid: str, body: dict)

        Accept either:
          - a full 'body' dict that matches pyegeria contract, or
          - a simple payload with display_name, summary, description, etc.,
            which will be converted to the required body.
        """
        if not glossary_guid:
            raise ValueError("glossary_guid is required")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        # If the caller already passed a 'body' with elementProperties, use it untouched.
        if "elementProperties" in payload or payload.get("class") == "ReferenceableRequestBody":
            body = payload
        else:
            display_name = payload.get("display_name") or payload.get("name")
            if not display_name:
                raise ValueError("display_name is required to create a term")

            # Optional fields
            summary = payload.get("summary")
            description = payload.get("description")
            abbreviation = payload.get("abbreviation")
            examples = payload.get("examples")
            usage = payload.get("usage")
            publish_version_identifier = (
                payload.get("publishVersionIdentifier")
                or payload.get("version_identifier")
            )
            aliases = payload.get("aliases") or []
            additional_props = payload.get("additionalProperties") or payload.get("additional_properties") or {}

            # Build API body
            body = {
                "class": "ReferenceableRequestBody",
                "elementProperties": {
                    "class": "GlossaryTermProperties",
                    "qualifiedName": f"GlossaryTerm: {display_name} : {{$isoTimestamp}}",
                    "displayName": display_name,
                    "aliases": aliases,
                },
                "initialStatus": payload.get("initialStatus", "DRAFT"),
            }
            ep = body["elementProperties"]
            if summary is not None:
                ep["summary"] = summary
            if description is not None:
                ep["description"] = description
            if abbreviation is not None:
                ep["abbreviation"] = abbreviation
            if examples is not None:
                ep["examples"] = examples
            if usage is not None:
                ep["usage"] = usage
            if publish_version_identifier is not None:
                ep["publishVersionIdentifier"] = publish_version_identifier
            if additional_props:
                ep["additionalProperties"] = additional_props

        res = self._invoke("create_controlled_glossary_term", args=(glossary_guid, body), kwargs={})
        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    def delete_term(self, term_guid: str, *, for_lineage: bool = False, for_duplicate_processing: bool = False) -> bool:
        if not term_guid:
            raise ValueError("term_guid is required")
        res = self._invoke(
            "delete_term",
            args=(term_guid,),
            kwargs={"for_lineage": for_lineage, "for_duplicate_processing": for_duplicate_processing},
        )
        if isinstance(res, dict):
            return bool(res.get("success", True))
        return True if res is None else bool(res)

    # --------- async wrappers for UI ---------

    async def list_glossaries_async(self, search: str = "*"):
        """
        Prefer native async on the monkeypatched client if present; otherwise fall back to sync in a thread
        or the token-managed async/sync path (non-blocking).
        """
        client = self._ensure_gclient()
        if client and hasattr(client, "_async_find_glossaries"):
            try:
                res = client._async_find_glossaries(search, output_format="DICT")
                res = await (res if asyncio.iscoroutine(res) else asyncio.to_thread(lambda: res))
                return self._ensure_list_like(res, keys=("glossaries", "elements", "results", "items"))
            except Exception:
                # If the client exists but async path fails, try the client's sync path in a worker thread
                try:
                    res = await asyncio.to_thread(client.find_glossaries, search)
                    return self._ensure_list_like(res, keys=("glossaries", "elements", "results", "items"))
                except Exception:
                    pass  # fall through to manager fallback

        # Manager-based async path with non-blocking fallback
        try:
            res = self._invoke("_async_find_glossaries", args=(search,), kwargs={"output_format": "DICT"})
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.list_glossaries, search)
        except Exception:
            return await asyncio.to_thread(self.list_glossaries, search)

        return self._ensure_list_like(res, keys=("glossaries", "elements", "results", "items"))


    async def add_glossary_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        display_name = payload.get("display_name") or payload.get("name")
        description = payload.get("description")
        language = payload.get("language", "English")
        usage = payload.get("usage")

        missing = []
        if not display_name:
            missing.append("display_name")
        if not description:
            missing.append("description")
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        try:
            res = self._invoke(
                "_async_create_glossary",
                args=(display_name, description, language, usage),
                kwargs={},
            )
        except Exception:
            return await asyncio.to_thread(self.add_glossary, payload)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.add_glossary, payload)
        except Exception:
            return await asyncio.to_thread(self.add_glossary, payload)

        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    async def delete_glossary_async(self, glossary_guid: str, cascade: bool = False):
        if not glossary_guid:
            raise ValueError("glossary_guid is required")

        try:
            res = self._invoke("_async_delete_glossary", args=(glossary_guid,), kwargs={"cascade": cascade})
        except Exception:
            return await asyncio.to_thread(self.delete_glossary, glossary_guid, cascade)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (dict, type(None), bool)):
                return await asyncio.to_thread(self.delete_glossary, glossary_guid, cascade)
        except Exception:
            return await asyncio.to_thread(self.delete_glossary, glossary_guid, cascade)

        if isinstance(res, dict):
            return bool(res.get("success", True))
        return True if res is None else bool(res)

    async def get_glossary_terms_async(self, glossary_guid: str, search: str = ""):
        if not glossary_guid:
            raise ValueError("glossary_guid is required")

        try:
            res = self._invoke(
                "_async_find_glossary_terms",
                args=(search or "*",),
                kwargs={"glossary_guid": glossary_guid, "output_format": "DICT"},
            )
        except Exception:
            return await asyncio.to_thread(self.get_terms, glossary_guid, search)

        try:
            if asyncio.iscoroutine(res):
                res = await asyncio.wait_for(res, timeout=8)
            elif not isinstance(res, (list, dict)):
                return await asyncio.to_thread(self.get_terms, glossary_guid, search)
        except Exception:
            return await asyncio.to_thread(self.get_terms, glossary_guid, search)

        return self._ensure_list_like(
            res, keys=("terms", "elements", "results", "items")
        )

    async def add_term_async(self, glossary_guid: str, payload: Dict[str, Any]):
        if not glossary_guid:
            raise ValueError("glossary_guid is required")
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dict")

        # Build body same as sync method
        if "elementProperties" in payload or payload.get("class") == "ReferenceableRequestBody":
            body = payload
        else:
            display_name = payload.get("display_name") or payload.get("name")
            if not display_name:
                raise ValueError("display_name is required to create a term")

            summary = payload.get("summary")
            description = payload.get("description")
            abbreviation = payload.get("abbreviation")
            examples = payload.get("examples")
            usage = payload.get("usage")
            publish_version_identifier = (
                payload.get("publishVersionIdentifier")
                or payload.get("version_identifier")
            )
            aliases = payload.get("aliases") or []
            additional_props = payload.get("additionalProperties") or payload.get("additional_properties") or {}

            body = {
                "class": "ReferenceableRequestBody",
                "elementProperties": {
                    "class": "GlossaryTermProperties",
                    "qualifiedName": f"GlossaryTerm: {display_name} : {{$isoTimestamp}}",
                    "displayName": display_name,
                    "aliases": aliases,
                },
                "initialStatus": payload.get("initialStatus", "DRAFT"),
            }
            ep = body["elementProperties"]
            if summary is not None:
                ep["summary"] = summary
            if description is not None:
                ep["description"] = description
            if abbreviation is not None:
                ep["abbreviation"] = abbreviation
            if examples is not None:
                ep["examples"] = examples
            if usage is not None:
                ep["usage"] = usage
            if publish_version_identifier is not None:
                ep["publishVersionIdentifier"] = publish_version_identifier
            if additional_props:
                ep["additionalProperties"] = additional_props

        try:
            res = self._invoke(
                "_async_create_controlled_glossary_term", args=(glossary_guid, body), kwargs={}
            )
        except Exception:
            return await asyncio.to_thread(self.add_term, glossary_guid, payload)

        if asyncio.iscoroutine(res):
            res = await res
        elif not isinstance(res, (list, dict)):
            return await asyncio.to_thread(self.add_term, glossary_guid, payload)

        if isinstance(res, list) and res:
            return res[0]
        if isinstance(res, dict):
            return res
        return {"result": res}

    async def delete_term_async(self, term_guid: str, *, for_lineage: bool = False, for_duplicate_processing: bool = False):
        if not term_guid:
            raise ValueError("term_guid is required")

        try:
            res = self._invoke(
                "_async_delete_term",
                args=(term_guid,),
                kwargs={"for_lineage": for_lineage, "for_duplicate_processing": for_duplicate_processing},
            )
        except Exception:
            return await asyncio.to_thread(self.delete_term, term_guid, for_lineage=for_lineage, for_duplicate_processing=for_duplicate_processing)

        if asyncio.iscoroutine(res):
            res = await res
        elif not isinstance(res, (dict, type(None), bool)):
            return await asyncio.to_thread(self.delete_term, term_guid, for_lineage=for_lineage, for_duplicate_processing=for_duplicate_processing)

        if isinstance(res, dict):
            return bool(res.get("success", True))
        return True if res is None else bool(res)

    # ------------------ helpers ------------------

    def _ensure_list_like(self, res: Any, keys: tuple[str, ...]) -> List[Dict[str, Any]]:
        if isinstance(res, list):
            return res
        if isinstance(res, dict):
            for k in keys:
                v = res.get(k)
                if isinstance(v, list):
                    return v
        return [] if res is None else ([res] if res else [])

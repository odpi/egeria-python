# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the functions of my_egeria module.


"""

from typing import Any, List, Dict, Optional, Tuple
from my_egeria.utils.egeria_client import EgeriaTechClientManager
from my_egeria.utils.config import EgeriaConfig, get_global_config
from os import getenv

class BaseService:
    """Shared logic for services: client management, safe invocation, normalization."""

    def __init__(
        self,
        config: Optional[EgeriaConfig] = None,
        manager: Optional[EgeriaTechClientManager] = None,
    ):
        self.config = config or get_global_config()
        self.manager = manager or EgeriaTechClientManager(self.config)

    # Invoke a method by name on the client with auto-refresh retry
    def _invoke(
        self, method_name: str, args: Tuple = (), kwargs: Optional[dict] = None
    ):
        kwargs = kwargs or {}

        def _call(client, *a, **k):
            fn = getattr(client, method_name, None)
            if not fn:
                raise AttributeError(f"Client has no method '{method_name}'")
            return fn(*a, **k)

        return self.manager.invoke_with_auto_refresh(_call, args=args, kwargs=kwargs)

    def _normalize_list(self, res: Any, keys: Tuple[str, ...]) -> List[Dict[str, Any]]:
        if res is None:
            return []
        if isinstance(res, dict):
            for k in keys:
                v = res.get(k)
                if isinstance(v, list):
                    return list(v)
            return [res]
        if isinstance(res, (list, tuple)):
            return list(res)
        return [res]

    def _call_list_like(
        self, candidates, keys: Tuple[str, ...]
    ) -> List[Dict[str, Any]]:
        last_err = None
        if getenv("EGERIA_DEBUG_METHODS", "").lower() in ("1", "true", "yes"):
            print(f"[debug] trying methods: {[name for name,_,_ in candidates]}")
        for name, args, kwargs in candidates:
            try:
                res = self._invoke(name, args=tuple(args), kwargs=kwargs)
                if getenv("EGERIA_DEBUG_RESULTS", "").lower() in ("1", "true", "yes"):
                    shape = type(res).__name__
                    size = (len(res) if isinstance(res, (list, tuple)) else
                            len(res) if isinstance(res, dict) else None)
                    print(f"[debug] {name} returned shape={shape} size={size}")
                    if isinstance(res, dict):
                        print(f"[debug] dict keys: {list(res.keys())[:10]}")
                    if isinstance(res, list) and res:
                        sample = res[0]
                        print(f"[debug] first item keys: {list(sample.keys())[:10] if isinstance(sample, dict) else type(sample).__name__}")
                return self._normalize_list(res, keys)
            except Exception as e:
                last_err = e
                continue
        raise ConnectionError(
            f"Operation failed (tried multiple client methods). Last error: {last_err}"
        )


    def _call_first(self, candidates):
        last_err = None
        for name, args, kwargs in candidates:
            try:
                return self._invoke(name, args=tuple(args), kwargs=kwargs)
            except Exception as e:
                last_err = e
                continue
        raise ConnectionError(
            f"Operation failed (tried multiple client methods). Last error: {last_err}"
        )


    def close(self) -> None:
        self.manager.close()

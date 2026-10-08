# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from textual import on
from textual.containers import Container

from .base_screen import BaseScreen
from my_egeria.utils.config import get_global_config
from my_egeria.utils.egeria_client import EgeriaTechClientManager


class GovernanceScreen(BaseScreen):
    """Screen to display governance engine and service status using EgeriaTech."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        self.cfg = get_global_config()
        self.manager = EgeriaTechClientManager(self.cfg)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static(
            "[b]Egeria Governance[/b] (Press R to refresh)", id="governance_title"
        )
        self.table.add_columns(
            "Engine",
            "Status",
            "Services",
        )
        yield Container(self.table)

    def on_mount(self) -> None:
        self.load_governance_info()

    # ---------- helpers ----------

    def _call_first(self, client, method_names: list[str], *args, **kwargs):
        """Try each method name on the client and return the first successful result."""
        last_err = None
        for name in method_names:
            fn = getattr(client, name, None)
            if not callable(fn):
                continue
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise last_err
        raise AttributeError(f"None of the methods exist on client: {method_names}")

    def _normalize_list(
        self, res, keys=("results", "items", "elements", "engines", "services")
    ):
        """Normalize responses to a list of dicts where possible."""
        if res is None:
            return []
        if isinstance(res, dict):
            for k in keys:
                v = res.get(k)
                if isinstance(v, list):
                    return list(v)
            # If dict doesn't contain a list under known keys, wrap it
            return [res]
        if isinstance(res, (list, tuple)):
            return list(res)
        return [res]

    def _list_governance_engines(self, client):
        """
        Attempt to list governance engines via common EgeriaTech-like methods.
        """
        candidates = [
            "list_governance_engines",
            "get_governance_engines",
            "getGovernanceEngines",
            "listGovernanceEngines",
            # generic fallbacks
            "list_engines",
            "get_engines",
        ]
        res = self._call_first(client, candidates)
        return self._normalize_list(
            res, keys=("engines", "results", "items", "elements")
        )

    def _get_engine_services(self, client, engine_name: str):
        """
        Attempt to list services for a given engine via common method names.
        """
        candidates = [
            "get_governance_service_list",
            "list_governance_services",
            "getGovernanceServices",
            "listGovernanceServices",
            # sometimes takes engine_name as an argument
            "get_services_for_engine",
            "list_services_for_engine",
        ]
        # Try candidates with engine_name as a positional arg; if any expect kwargs, add variants here as needed
        for name in candidates:
            fn = getattr(client, name, None)
            if not callable(fn):
                continue
            try:
                res = fn(engine_name)
                return self._normalize_list(
                    res, keys=("services", "results", "items", "elements")
                )
            except Exception:
                continue
        # If none succeeded, return empty list
        return []

    # ---------- data loading ----------

    def load_governance_info(self) -> None:
        """Fetch and display governance engine and service information."""
        self.table.clear()
        try:
            client = self.manager.get_client()
            engines = self._list_governance_engines(client)
            if not engines:
                self.table.add_row("No governance engines found", "", "")
                return

            for engine in engines:
                engine_name = (
                    engine.get("engineName")
                    or engine.get("name")
                    or engine.get("displayName")
                    or "Unknown"
                )
                status = engine.get("engineStatus") or engine.get("status") or "Unknown"
                try:
                    services = self._get_engine_services(client, engine_name)
                    services_str = (
                        ", ".join(
                            s.get("serviceName")
                            or s.get("name")
                            or s.get("displayName")
                            or "?"
                            for s in services
                        )
                        if services
                        else "None"
                    )
                    self.table.add_row(engine_name, status, services_str)
                except Exception as inner_err:
                    self.table.add_row(engine_name, f"Error: {inner_err}", "")
        except Exception as e:
            self.table.add_row("Error", str(e), "")

    @on("r")
    def on_refresh(self) -> None:
        self.load_governance_info()

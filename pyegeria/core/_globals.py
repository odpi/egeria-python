"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
This common file is used to set some global values and enumerations used by the overall package. 

"""
import os
from enum import Enum
from typing import Any

def resolve_enum(enum_class: type[Enum], value: str | int) -> int | None:
    """
    Resolves a string or integer to its corresponding Egeria enum integer value.
    Example: resolve_enum(ContentStatus, 'Draft') -> 0
    """
    if value is None or value == "":
        return None
        
    if isinstance(value, int):
        return value
        
    v = str(value).upper()
    try:
        # Normalized case-insensitive search through enum members
        # Replace separators with spaces and collapse multiple spaces
        v_clean = ' '.join(v.replace('_', ' ').replace('-', ' ').split())
        for member in enum_class.__members__.values():
            m_name = ' '.join(member.name.upper().replace('_', ' ').replace('-', ' ').split())
            if v_clean == m_name:
                return member.value

        # 3. Check if it's already an integer string
        if v.isdigit():
            return int(v)
        return None
    except (KeyError, ValueError):
        return None

is_debug = False
disable_ssl_warnings = True


def resolve_ssl_verify(verify: bool, ca_bundle: str = "") -> "bool | ssl.SSLContext":
    """Turn the SSL settings into the value httpx takes as ``verify``.

    * ``verify`` off -> ``False``: the Egeria platform's certificate is not checked
      (the historical behaviour, needed for the quickstart's self-signed certificates).
    * ``verify`` on, no bundle -> ``True``: httpx checks against certifi's bundle.
    * ``verify`` on with a bundle -> an ``SSLContext`` that trusts that PEM file.

    A bundle that can't be loaded raises: falling back to "don't verify" would
    quietly undo the setting, and falling back to certifi would hide the typo
    behind a confusing certificate error later.
    """
    if not verify:
        return False
    if not ca_bundle:
        return True
    import ssl
    path = os.path.expanduser(os.path.expandvars(ca_bundle))
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Pyegeria CA Bundle / PYEGERIA_CA_BUNDLE is set to {ca_bundle!r}, but {path!r} is not a file"
        )
    return ssl.create_default_context(cafile=path)


# TLS verification of the Egeria platform's certificate. Configurable through
# PYEGERIA_SSL_VERIFY / PYEGERIA_CA_BUNDLE, the same names in .env, or
# "Pyegeria SSL Verify" / "Pyegeria CA Bundle" in config.json (see
# pyegeria.core.config.EnvironmentConfig). Default off, as before.
# enable_ssl_check stays a plain bool for existing importers; ssl_verify is
# what the HTTP clients pass to httpx. The clients read ssl_verify from this
# module when they create a session, so a program can also set
# pyegeria.core._globals.ssl_verify itself before connecting.
try:
    from pyegeria.core.config import settings as _ssl_settings
    _ssl_env = _ssl_settings.Environment
    enable_ssl_check = bool(getattr(_ssl_env, "pyegeria_ssl_verify", False))
    _ca_bundle = str(getattr(_ssl_env, "pyegeria_ca_bundle", "") or "")
except Exception:  # noqa: BLE001 -- config not ready yet; keep the historical default
    enable_ssl_check = False
    _ca_bundle = ""
ssl_verify = resolve_ssl_verify(enable_ssl_check, _ca_bundle)

# Default page size for paged find/relationship queries. Env-configurable
# (EGERIA_MAX_PAGE_SIZE / "Egeria Max Page Size" in config.json/.env, see
# pyegeria.core.config.EnvironmentConfig) so a future Egeria server-side page
# limit change is a config edit, not a grep-and-patch across every hardcoded
# page_size literal in every caller -- hit live 2026-08-17 when
# findRelationshipsBetweenMetadataElements started rejecting a hardcoded 5000
# with "greater than the allowable maximum of 1000" after a server upgrade.
# Read at import time (module-level, not a live binding -- callers that
# `from pyegeria.core._globals import max_paging_size` get the value as of
# their own import, same as every other global in this file); falls back to
# the bare default if settings can't load yet (e.g. mid-bootstrap, no .env
# present) rather than failing the whole import.
try:
    from pyegeria.core.config import settings as _settings
    max_paging_size = int(getattr(_settings.Environment, "egeria_max_page_size", 500))
except Exception:  # noqa: BLE001 -- config not ready yet; safe default
    max_paging_size = 500

default_timeout = 30
DEBUG_LEVEL = "quiet"
COMMENT_TYPES = (
    "STANDARD_COMMENT",
    "ANSWER",
    "OTHER",
    "QUESTION",
    "SUGGESTION",
    "USAGE_EXPERIENCE",
    "REQUIREMENT"
)
star_ratings = (
    "FIVE_STARS",
    "FOUR_STARS",
    "NO_RECOMMENDATION",
    "ONE_STAR",
    "THREE_STARS",
    "TWO_STARS",
)
# class GovernanceDomains(Enum):
#     All= 0
#     Data= 1
#     Privacy= 2
#     Security= 3
#     IT Infrastructure= 4
#     Software Development= 5
#     Corporate= 6
#     Asset Management= 7
#     Other= 99
GovernanceDomains = Enum('GovernanceDomains', [('ALL', 0),
                                               ('DATA', 1),
                                               ('PRIVACY', 2),
                                               ('SECURITY', 3),
                                               ('IT_INFRASTRUCTURE', 4),
                                               ('SOFTWARE_DEVELOPMENT', 5),
                                               ('CORPORATE', 6),
                                               ('ASSET_MANAGEMENT', 7),
                                               ('OTHER', 99)])

# Default status values for fallback if dynamic fetching fails
CONTENT_STATUS = ["DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "OTHER"]
DEPLOYMENT_STATUS = ["PROPOSED", "UNDER_DEVELOPMENT", "DEVELOPMENT_COMPLETE", "APPROVED_FOR_DEPLOYMENT", 
                     "REJECTED_FOR_DEPLOYMENT", "STANDBY", "ACTIVE", "DISABLED", "FAILED", "OTHER"]
ACTIVITY_STATUS = ["REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED", "FOR_INFO", 
                   "COMPLETED", "INVALID", "IGNORED", "FAILED", "CANCELLED", "ABANDONED", "OTHER"]
MEMBERSHIP_STATUS = ["UNKNOWN", "DISCOVERED", "PROPOSED", "IMPORTED", "VALIDATED", "DEPRECATED", "OBSOLETE", "OTHER"]

RELATIONSHIP_TYPES = ["RelatedTerm", "Synonym", "Antonym", "PreferredTerm", "ReplacementTerm", "Translation", "IsA", "ValidValue"]
PROJECT_TYPES=["Project","Campaign","Task","PersonalProject","StudyProject","Experiment","Investigation"]

TEMPLATE_GUIDS: dict[str, str] = {}
INTEGRATION_GUIDS: dict[str, str] = {}

NO_ELEMENTS_FOUND = "No elements found"
NO_ASSETS_FOUND = "No assets found"
NO_SERVERS_FOUND = "No servers found"
NO_CATALOGS_FOUND = "No catalogs found"
NO_GLOSSARIES_FOUND = "No glossaries found"
NO_TERMS_FOUND = "No terms found"
NO_CATEGORIES_FOUND = "No categories found"
NO_ELEMENT_FOUND = "No element found"
NO_PROJECTS_FOUND = "No projects found"
NO_COLLECTION_FOUND = "No collection found"
NO_GUID_RETURNED = "No guid returned"
NO_MEMBERS_FOUND = "No members found"

MERMAID_GRAPHS: list[str] = ["anchorMermaidGraph", "informationSupplyChainMermaidGraph","fieldLevelLineageGraph",
                  "actionMermaidGraph", "localLineageGraph", "edgeMermaidGraph", "iscImplementationMermaidGraph",
                  "iscDataMeshMermaidGraph", "iscSystemFabricMermaidGraph", "iscDataFabricMermaidGraph",
                  "iscDataMappingMermaidGraph",
                  "specificationMermaidGraph", "solutionBlueprintMermaidGraph","mermaidGraph",
                  "solutionSubcomponentMermaidGraph", "governanceActionProcessMermaidGraph"]
MERMAID_GRAPH_TITLES = ["Anchor Mermaid Graph", "Information Supply Chain Mermaid Graph","Field Level Lineage Graph",
                  "Action Mermaid Graph", "Local Lineage Graph", "Edge Mermaid Graph", "ISC Implementation Mermaid Graph",
                  "ISC Data Mesh Graph", "ISC System Fabric Graph", "ISC Data Fabric Graph",
                  "ISC Data Mapping Graph",
                  "Specification Mermaid Graph", "Solution Blueprint Mermaid Graph","Mermaid Graph",
                  "Solution Subcomponent Mermaid Graph","Governance Action Process Mermaid Graph" ]
TERM_STATUS = ["DRAFT", "PREPARED","PROPOSED","APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "DELETED", "OTHER"]
REPORT_ACRONYMS = ["GUID", "ID", "QN", "API", "UI", "ISC"]

"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
This common file is used to set some global values and enumerations used by the overall package. 

"""
from enum import Enum
from typing import Any, Type

def resolve_enum(enum_class: Type[Enum], value: str | int) -> int | None:
    """
    Resolves a string or integer to its corresponding Egeria enum integer value.
    Example: resolve_enum(ContentStatus, 'Draft') -> 0
    """
    if value is None or value == "":
        return None
        
    if isinstance(value, int):
        return value
        
    v = str(value).strip().upper()
    try:
        # Direct name match
        return enum_class[v].value
    except (KeyError, ValueError):
        # Check if it's already an integer string
        if v.isdigit():
            return int(v)
        # Try to match by value name if possible (some enums might have specific logic)
        return None

is_debug = False
disable_ssl_warnings = True
enable_ssl_check = False
max_paging_size = 500
default_time_out = 30
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
GovernanceDomains = Enum('GovernanceDomains', [('Unclassified', 0),
                                               ('Data', 1),
                                               ('Privacy',2),
                                               ('Security',3),
                                               ('IT Infrastructure',4),
                                               ('Software Development',5),
                                               ('Corporate',6),
                                               ('Asset Management',7),
                                               ('Other',99)])

# Default status values for fallback if dynamic fetching fails
CONTENT_STATUS = ["DRAFT", "PREPARED", "PROPOSED", "APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "OTHER"]
DEPLOYMENT_STATUS = ["PROPOSED", "UNDER_DEVELOPMENT", "DEVELOPMENT_COMPLETE", "APPROVED_FOR_DEPLOYMENT", 
                     "REJECTED_FOR_DEPLOYMENT", "STANDBY", "ACTIVE", "DISABLED", "FAILED", "OTHER"]
ACTIVITY_STATUS = ["REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED", "FOR_INFO", 
                   "COMPLETED", "INVALID", "IGNORED", "FAILED", "CANCELLED", "ABANDONED", "OTHER"]
MEMBERSHIP_STATUS = ["UNKNOWN", "DISCOVERED", "PROPOSED", "IMPORTED", "VALIDATED", "DEPRECATED", "OBSOLETE", "OTHER"]



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
                  "specificationMermaidGraph", "solutionBlueprintMermaidGraph","mermaidGraph",
                  "solutionSubcomponentMermaidGraph", "governanceActionProcessMermaidGraph"]
MERMAID_GRAPH_TITLES = ["Anchor Mermaid Graph", "Information Supply Chain Mermaid Graph","Field Level Lineage Graph",
                  "Action Mermaid Graph", "Local Lineage Graph", "Edge Mermaid Graph", "ISC Implementation Mermaid Graph",
                  "Specification Mermaid Graph", "Solution Blueprint Mermaid Graph","Mermaid Graph",
                  "Solution Subcomponent Mermaid Graph","Governance Action Process Mermaid Graph" ]
TERM_STATUS = ["DRAFT", "PREPARED","PROPOSED","APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "DELETED", "OTHER"]
REPORT_ACRONYMS = ["GUID", "URL", "ID", "QN", "API", "UI"]
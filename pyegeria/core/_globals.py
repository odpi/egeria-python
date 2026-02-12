"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
This common file is used to set some global values and enumerations used by the overall package. 

"""
from enum import Enum

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
class GovernanceDomains(Enum):
    ALL= 0,
    DATA= 1,
    PRIVACY= 2,
    SECURITY= 3,
    IT_INFRASTRUCTURE= 4,
    SOFTWARE_DEVELOPMENT= 5,
    CORPORATE= 6,
    ASSET_MANAGEMENT= 7,
    OTHER= 99

class ContentStatus(Enum):
    DRAFT = 0
    PREPARED = 1
    PROPOSED = 2
    APPROVED = 3
    REJECTED = 4
    ACTIVE = 5
    DEPRECATED = 6
    OTHER = 99

class DeploymentStatus(Enum):
    PROPOSED = 0
    UNDER_DEVELOPMENT = 1
    DEVELOPMENT_COMPLETE = 2
    APPROVED_FOR_DEPLOYMENT = 3
    REJECTED_FOR_DEPLOYMENT = 4
    STANDBY = 5
    ACTIVE = 6
    DISABLED = 7
    FAILED = 8
    OTHER = 99

class ActivityStatus(Enum):
    REQUESTED = 0
    APPROVED = 1
    WAITING = 2
    ACTIVATING = 3
    IN_PROGRESS = 4
    PAUSED = 5
    FOR_INFO = 6
    COMPLETED = 7
    INVALID = 8
    IGNORED = 9
    FAILED = 10
    CANCELLED = 11
    ABANDONED = 12
    OTHER = 99



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
ACTIVITY_STATUS = ["REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED","FOR_INFO","COMPLETED",
                   "INVALID","IGNORED","FAILED","CANCELLED", "ABANDONED","OTHER"]
REPORT_ACRONYMS = ["GUID", "URL", "ID", "QN", "API", "UI"]
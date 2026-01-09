"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
This common file is used to set some global values and enumerations used by the overall package. 

"""


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

TEMPLATE_GUIDS: dict = {}
INTEGRATION_GUIDS: dict = {}

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

MERMAID_GRAPHS = ["anchorMermaidGraph", "informationSupplyChainMermaidGraph","fieldLevelLineageGraph",
                  "actionMermaidGraph", "localLineageGraph", "edgeMermaidGraph", "iscImplementationMermaidGraph",
                  "specificationMermaidGraph", "solutionBlueprintMermaidGraph","mermaidGraph",
                  "solutionSubcomponentMermaidGraph"]
MERMAID_GRAPH_TITLES = ["Anchor Mermaid Graph", "Information Supply Chain Mermaid Graph","Field Level Lineage Graph",
                  "Action Mermaid Graph", "Local Lineage Graph", "Edge Mermaid Graph", "ISC Implementation Mermaid Graph",
                  "Specification Mermaid Graph", "Solution Blueprint Mermaid Graph","Mermaid Graph",
                  "Solution Subcomponent Mermaid Graph"]
TERM_STATUS = ["DRAFT", "PREPARED","PROPOSED","APPROVED", "REJECTED", "ACTIVE", "DEPRECATED", "DELETED", "OTHER"]

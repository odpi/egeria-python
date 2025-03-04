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

comment_types = (
    "ANSWER",
    "OTHER",
    "QUESTION",
    "STANDARD_COMMENT",
    "SUGGESTION",
    "USAGE_EXPERIENCE",
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
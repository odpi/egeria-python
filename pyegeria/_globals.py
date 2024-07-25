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


"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""


import os

# Read environment variables exactly as in the old code
EGERIA_SERVER = os.getenv("EGERIA_SERVER")
EGERIA_BASE_URL = os.getenv("EGERIA_BASE_URL")
EGERIA_USER = os.getenv("EGERIA_USER")
EGERIA_USER_PASSWORD = os.getenv("EGERIA_USER_PASSWORD")

# Helpers
REQUIRED_ENVS = ["EGERIA_SERVER", "EGERIA_BASE_URL"]

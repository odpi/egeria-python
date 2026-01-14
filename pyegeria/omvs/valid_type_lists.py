"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Valid Type Lists View Service client.
"""

from pyegeria.omvs.valid_metadata import ValidMetadataManager
from typing import Any, Optional

class ValidTypeLists(ValidMetadataManager):
    """
    Client for the Valid Type Lists View Service.
    This is a specialized version of the Valid Metadata Manager focusing on type lists.

    Attributes
    ----------
    view_server : str
        The name of the View Server to use.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.url_marker = "valid-metadata"

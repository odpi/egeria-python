"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Specification Properties View Service client.
"""

from pyegeria.omvs.valid_metadata import ValidMetadataManager


class SpecificationProperties(ValidMetadataManager):
    """
    Client for the Specification Properties View Service.
    This is a specialized version of the Valid Metadata Manager focusing on specification properties.

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
        user_pwd: str = None,
        token: str = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.url_marker = "valid-metadata"

# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""
from my_egeria.services.base_service import BaseService


class SubjectAreaService(BaseService):
    """Wrapper around pyegeria collection functions with token-managed client."""
    # def __init__(self, config=None, manager=None, *args, **kwargs):
    #     super.__init__(*args, **kwargs)

    def list_subject_areas(self):
        pass
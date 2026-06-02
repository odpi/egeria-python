# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Project Manager related functions of my_egeria module.


"""

import asyncio
from typing import Any, Dict, List, Optional
from .base_service import BaseService
from my_egeria.utils.config import EgeriaConfig

class ProjectManagerService(BaseService):
    """Wrapper around pyegeria collection functions with token-managed client."""

    def __init__(self, config: Optional[EgeriaConfig] = None, manager=None):
        super().__init__(config=config, manager=manager)

    def list_projects(self, search: str = "*") -> List[Dict[str, Any]]:
        pass
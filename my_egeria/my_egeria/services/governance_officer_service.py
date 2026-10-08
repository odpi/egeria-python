# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Governance Officer related functions of my_egeria module.


"""

from typing import Optional
from .base_service import BaseService
from my_egeria.utils.egeria_client import EgeriaTechClientManager
from my_egeria.utils.config import EgeriaConfig

class GovernanceOfficerService(BaseService):
    def __init__(self, config):
        super().__init__()
        config: Optional[EgeriaConfig] = None,
        manager: Optional[EgeriaTechClientManager] = None,
        self.config = config
        self.definition_guid:str = ""

    def get_collections_by_name(self, payload):
        self.payload = payload
        return self.manager.get_collections_by_name(self.payload)

    def create_governance_definition(self, payload):
        # return self.config.manager.create_governance_definition(self.definition_guid)
        pass
    def delete_governance_definition(self, payload):
        # return self.config.manager.delete_governance_definition(self.definition_guid)
        pass
    def update_governance_definition(self, payload):
        # return self.config.manager.update_governance_definition(self.definition_guid)
        pass
    def find_governance_definitions(self, payload):
        # return self.config.manager.find_governance_definition(self.definition_guid)
        pass

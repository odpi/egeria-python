"""
Rewriters for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional
from loguru import logger
from md_processing.v2.processors import AsyncBaseCommandProcessor

class CommandRewriter:
    """
    Rewrites commands based on runtime state (e.g. Create -> Update if exists).
    """
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

    async def rewrite(self, command: Any, parsed_output: Dict[str, Any]) -> Any:
        verb = command.verb
        object_type = command.object_type
        exists = parsed_output.get("exists", False)
        
        if verb == "Create" and exists:
            logger.info(f"Rewriting 'Create {object_type}' to 'Update {object_type}' as it already exists.")
            command.verb = "Update"
            command.raw_block = command.raw_block.replace("Create", "Update", 1)
        elif verb == "Update" and not exists:
            # For some types, we might want to auto-create, but usually we just log an error or proceed
            # Sync code often switched Update -> Create if not exists.
            logger.info(f"Rewriting 'Update {object_type}' to 'Create {object_type}' as it does not exist.")
            command.verb = "Create"
            command.raw_block = command.raw_block.replace("Update", "Create", 1)
            
        return command

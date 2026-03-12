"""
v2 Dispatcher for Dr.Egeria.
Routes commands to their respective AsyncBaseCommandProcessor subclasses.
"""
import asyncio
from typing import Dict, Type, Optional, Any, List
from loguru import logger

from pyegeria import EgeriaTech
from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor

class v2Dispatcher:
    """
    Registry and router for v2 command processors.
    """

    def __init__(self, client: EgeriaTech):
        self.client = client
        self.processors: Dict[str, Type[AsyncBaseCommandProcessor]] = {}

    def register(self, command_name: str, processor_cls: Type[AsyncBaseCommandProcessor]):
        """Register a processor class for a specific command name (e.g. 'Create Glossary')."""
        self.processors[command_name] = processor_cls
        logger.debug(f"v2Dispatcher: Registered {command_name}")

    async def dispatch(self, command: DrECommand, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract the full command name (Verb + Object) and route to the processor.
        """
        command_key = f"{command.verb} {command.object_type}"
        processor_cls = self.processors.get(command_key)
        
        if not processor_cls:
            logger.warning(f"v2Dispatcher: No processor registered for '{command_key}'")
            return {
                "output": command.raw_block,
                "status": "warning",
                "message": f"No processor registered for '{command_key}'",
                "verb": command.verb,
                "object_type": command.object_type
            }
            
        processor = processor_cls(self.client, command, context)
        try:
            return await processor.execute()
        except Exception as e:
            logger.exception(f"Error executing command '{command_key}'")
            return {
                "output": command.raw_block,
                "status": "failure",
                "message": f"Execution failed: {str(e)}",
                "verb": command.verb,
                "object_type": command.object_type,
                "error": str(e)
            }

    async def dispatch_batch(self, commands: List[DrECommand], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a batch of commands sequentially.
        Sequential execution allows inter-command dependencies to be tracked via a shared context.
        """
        if context is None:
            context = {}
        
        # Initialize a shared 'planned_elements' set if not present
        if "planned_elements" not in context:
            context["planned_elements"] = set()
            
        results = []
        for cmd in commands:
            result = await self.dispatch(cmd, context)
            results.append(result)
        return results

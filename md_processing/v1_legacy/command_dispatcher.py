from typing import Callable, Dict, Any, Optional
from loguru import logger

class CommandDispatcher:
    """
    Registry and dispatcher for Dr.Egeria markdown commands.
    """
    def __init__(self):
        self._registry: Dict[str, Callable] = {}

    def register(self, command_name: str, handler: Callable):
        """
        Register a handler for a specific command name.
        """
        self._registry[command_name] = handler
        logger.debug(f"Registered command handler for: {command_name}")

    def get_handler(self, command_name: str) -> Optional[Callable]:
        """
        Retrieve the handler for a given command name.
        """
        return self._registry.get(command_name)

    def dispatch(self, command_name: str, *args, **kwargs) -> Any:
        """
        Execute the handler for the given command.
        """
        handler = self.get_handler(command_name)
        if handler:
            return handler(*args, **kwargs)
        else:
            logger.warning(f"No handler registered for command: {command_name}")
            return None

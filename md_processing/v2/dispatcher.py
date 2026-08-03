"""
v2 Dispatcher for Dr.Egeria.
Routes commands to their respective AsyncBaseCommandProcessor subclasses.
"""

from typing import Dict, Type, Optional, Any, List, Set
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException, print_basic_exception
from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import COLLECTION_SUBTYPES, PROJECT_SUBTYPES, find_alternate_names
from md_processing.v2.collection_manager_processor import CollectionManagerProcessor
from md_processing.v2.project import ProjectProcessor
from md_processing.v2.view import ViewProcessor
from md_processing.v2.rewriters import CommandRewriter

class V2Dispatcher:
    """
    Registry and router for v2 command processors.
    """

    def __init__(self, client: EgeriaTech):
        self.client = client
        self.processors: Dict[str, Type[AsyncBaseCommandProcessor]] = {}
        self.command_rewriter = CommandRewriter(self)

    def register(self, command_name: str, processor_cls: Type[AsyncBaseCommandProcessor]):
        """Register a processor class for a specific command name (e.g. 'Create Glossary')."""
        self.processors[command_name] = processor_cls
        logger.debug(f"v2Dispatcher: Registered {command_name}")

    def resolve_processor_class(self, command: DrECommand) -> Optional[Type[AsyncBaseCommandProcessor]]:
        """
        Resolve the processor class for a command's Verb+Object, via the registry,
        alternate-name lookup, fuzzy preposition-stripping, or subtype/verb fallbacks.
        Returns None if nothing matches. Pulled out of dispatch() so the batch
        pre-scan can route commands to a processor without duplicating this logic.
        """
        command_key = f"{command.verb} {command.object_type}"
        processor_cls = self.processors.get(command_key)

        # If not found, try to resolve via alternate names
        if not processor_cls:
            canonical_key = find_alternate_names(command_key)
            if canonical_key:
                processor_cls = self.processors.get(canonical_key)
                if processor_cls:
                    logger.debug(f"Resolved command '{command_key}' to canonical '{canonical_key}'")

        if not processor_cls:
            # Fuzzy match: strip prepositions (to, from, etc.) to bridge gap between MD and registry
            prepositions = {"to", "from", "at", "in", "on", "for", "with", "by", "into", "onto", "of"}
            parts = command.object_type.split()
            stripped_parts = [p for p in parts if p.lower() not in prepositions]
            if len(stripped_parts) != len(parts):
                fuzzy_key = f"{command.verb} {' '.join(stripped_parts)}"
                processor_cls = self.processors.get(fuzzy_key)
                if processor_cls:
                    logger.debug(f"v2Dispatcher: Fuzzy matched '{command_key}' to '{fuzzy_key}'")

        if not processor_cls:
            # Fallback for known collection and project subtypes if not explicitly registered
            if command.object_type in COLLECTION_SUBTYPES:
                processor_cls = CollectionManagerProcessor
            elif command.object_type in PROJECT_SUBTYPES:
                processor_cls = ProjectProcessor
            elif command.verb == "View":
                processor_cls = ViewProcessor

        return processor_cls

    def prescan_batch_target_qns(self, commands: List[DrECommand]) -> Set[str]:
        """
        Walk the full batch once, before any command executes, and derive the
        qualified name each Create/Update-verb command's own target element will
        have. Populates a set used purely to recognize forward references (a
        reference to a name that belongs to a not-yet-executed later command)
        as "will exist" rather than "not found at all".

        Uses each command's real processor class and derive_qualified_name() so
        the derivation is byte-identical to what the real parse-time derivation
        will produce later - no separate QN-basis-selection logic to keep in sync.
        A raw-value shim ({key: {"value": raw_string}}) is used instead of a full
        AttributeFirstParser.parse() to avoid triggering duplicate live "Valid
        Value" network validation calls; derive_qualified_name() only ever reads
        attributes.get(key, {}).get("value"), so the shim is sufficient.
        """
        upsert_verbs = {"Create", "Define", "Register", "Add", "Update", "Modify", "Upsert"}
        target_qns: Set[str] = set()
        for command in commands:
            if not command.is_command or command.verb not in upsert_verbs:
                continue
            processor_cls = self.resolve_processor_class(command)
            if not processor_cls:
                continue
            processor = processor_cls(self.client, command, {})
            if not processor.supports_target_element_lookup():
                continue
            raw_shim = {k: {"value": v} for k, v in command.attributes.items()}
            # An explicit user-supplied "Qualified Name" must take priority over
            # auto-derivation here, exactly as it does in the real execution path
            # (AsyncBaseCommandProcessor.execute(), which only calls
            # derive_qualified_name() when parsed_output["qualified_name"] isn't
            # already set from an explicit value). derive_qualified_name() always
            # auto-generates from Display Name and has no knowledge of an explicit
            # override, so calling it unconditionally here silently registers the
            # wrong name for any command using an explicit Qualified Name - making
            # a forward reference *by that explicit name* invisible to the pre-scan.
            qn = raw_shim.get("Qualified Name", {}).get("value") or processor.derive_qualified_name(raw_shim)
            if qn:
                target_qns.add(qn)
            # A forward reference is typically typed as the raw Display Name,
            # not the fully-derived qualified name (e.g. a "Sub-Projects" entry
            # naming a project by its display name) - this is exactly how a
            # *backward* reference already resolves too, via
            # find_key_with_value() matching the display_name value stored
            # alongside a cached qn. Register it here so a forward reference
            # gets the same recognition.
            display_name = command.attributes.get("Display Name")
            if display_name:
                target_qns.add(display_name)
        return target_qns

    async def dispatch(self, command: DrECommand, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract the full command name (Verb + Object) and route to the processor.
        """
        if not command.is_command:
            return {
                "output": command.raw_block,
                "status": "success",
                "message": "Block preserved",
                "verb": "",
                "object_type": "",
                "is_command": False
            }

        command_key = f"{command.verb} {command.object_type}"
        processor_cls = self.resolve_processor_class(command)

        if not processor_cls:
            logger.warning(f"v2Dispatcher: No processor registered for '{command_key}'")
            return {
                "output": command.raw_block,
                "status": "warning",
                "message": f"No processor registered for '{command_key}'",
                "verb": command.verb,
                "object_type": command.object_type
            }
        try:
            processor = processor_cls(self.client, command, context)
            return await processor.execute()
        except PyegeriaException as e:
            logger.exception(f"Error executing command '{command_key}'")
            print_basic_exception(e)
            return {
                "output": command.raw_block,
                "status": "failure",
                "message": f"Execution failed: {str(e)}",
                "verb": command.verb,
                "object_type": command.object_type,
                "error": str(e)
            }
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
        Execute a batch of commands, in rounds, so a command referencing an
        element defined LATER in the same file (a forward reference) can defer
        instead of failing outright on its first attempt.

        Sequential execution within a round allows inter-command dependencies to
        be tracked via a shared context. A command whose result comes back with
        `deferred: True` (see processors.py) is retried in the next round rather
        than treated as failed. Rounds continue until nothing is deferred, or -
        once a round makes no further progress - one final forced pass is run
        with context["final_round"] = True so genuinely-unresolvable references
        still produce today's exact clear failure message, just correctly scoped
        to real problems instead of every forward reference.

        The returned list is always the same length as `commands` and each
        entry stays at its original index regardless of which round it actually
        completed in - dr_egeria.py rebuilds the output file and summary table
        by iterating this list in order, with no other alignment check.
        """
        if context is None:
            context = {}

        # Initialize a shared 'planned_elements' set if not present
        if "planned_elements" not in context:
            context["planned_elements"] = set()

        # Pre-scan the full, original batch once, before any command executes,
        # so forward references are recognized as "will exist" rather than
        # "not found at all" from round 1 onward.
        context["batch_target_qns"] = self.prescan_batch_target_qns(commands)

        n = len(commands)
        results: List[Optional[Dict[str, Any]]] = [None] * n
        pending = list(range(n))
        max_rounds = n + 2  # belt-and-suspenders cap; stagnation detection should hit first

        round_num = 0
        while pending and round_num < max_rounds:
            round_num += 1
            still_pending = []
            for i in pending:
                result = await self.dispatch(commands[i], context)
                results[i] = result
                if result.get("deferred"):
                    still_pending.append(i)

            if len(still_pending) == len(pending):
                # No progress this round - force one more pass, treating any
                # still-unresolved reference as a genuine, final failure.
                context["final_round"] = True
                for i in still_pending:
                    results[i] = await self.dispatch(commands[i], context)
                break

            pending = still_pending

        return results  # type: ignore[return-value]

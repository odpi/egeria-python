"""
View processor for Dr.Egeria v2.
Handles commands with the 'View' verb by leveraging Egeria report specs.
"""
import json
from typing import Any, Dict, Optional
from loguru import logger

from pyegeria import EgeriaTech, NO_ELEMENTS_FOUND
from pyegeria.view.format_set_executor import _async_run_report
from pyegeria.view.base_report_formats import select_report_spec
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.extraction import DrECommand

class ViewProcessor(AsyncBaseCommandProcessor):
    """
    Processor for 'View' commands (e.g., View Report, View Referenceable).
    Uses report specs to fetch and format data from Egeria.
    """

    def __init__(self, client: EgeriaTech, command: DrECommand, context: Optional[Dict[str, Any]] = None):
        super().__init__(client, command, context)

    async def execute(self) -> Dict[str, Any]:
        """
        Orchestrate the command execution flow for View commands.
        Ensures that even if no command spec is found, we can still attempt to run a report.
        """
        # Call base execute to perform parsing and initial validation
        result = await super().execute()
        
        # If the failure was only due to missing command spec, we want to proceed for View commands
        if result.get("status") == "failure":
            errors = result.get("errors", [])
            if any("No specification found" in e for e in errors):
                # Re-evaluate validity for View commands
                other_errors = [e for e in errors if "No specification found" not in e]
                if not other_errors:
                    # Proceed with apply_changes
                    try:
                        output = await self.apply_changes()
                        return {
                            "output": output,
                            "analysis": result.get("analysis", ""),
                            "status": "success",
                            "message": "Generic View execution",
                            "verb": self.command.verb,
                            "object_type": self.command.object_type,
                            "display_name": result.get("display_name"),
                            "qualified_name": result.get("qualified_name"),
                            "found": result.get("found", False)
                        }
                    except Exception as e:
                        result["message"] = f"Execution failed: {str(e)}"
                        result["errors"] = [str(e)]
        
        return result

    async def apply_changes(self) -> str:
        """
        Fetch data from Egeria and format it according to the report spec.
        """
        attributes = self.parsed_output.get("attributes", {})

        # 1. Extract core parameters from parsed attributes
        # Report Spec usually comes from the object type if not explicitly provided as an attribute
        report_spec_name = attributes.get("Report Spec", {}).get("value") or self.command.object_type
        output_format = attributes.get("Output Format", {}).get("value", "LIST")

        # 2. Map other attributes to their variable names
        spec = self.get_command_spec()
        name_to_var = {}
        if spec:
            spec_attrs = spec.get("Attributes", spec.get("attributes", []))
            # Build a mapping from canonical name to the variable name expected by the SDK
            for attr in spec_attrs:
                if isinstance(attr, dict):
                    # Handle flattened structure: {"name": "...", "variable_name": "..."}
                    if "name" in attr and "variable_name" in attr:
                        name_to_var[attr["name"]] = attr["variable_name"]
                    else:
                        # Handle nested structure: {"Canonical Name": {"variable_name": "..."}}
                        for canonical_name, details in attr.items():
                            if isinstance(details, dict) and "variable_name" in details:
                                name_to_var[canonical_name] = details["variable_name"]
        
        params = {}
        for canonical_name, attr_data in attributes.items():
            if canonical_name in ["Report Spec", "Output Format"]:
                continue
                
            # If we have a variable_name in the spec, use it. 
            # Otherwise fallback to a snake_case version of the canonical name.
            var_name = name_to_var.get(canonical_name, canonical_name.lower().replace(" ", "_"))
            params[var_name] = attr_data.get("value")

        # 3. Validation
        if self.command.object_type == "Report" and not attributes.get("Report Spec"):
            raise ValueError("No Report Spec given. Please provide a 'Report Spec' attribute.")
        
        # Validate that the report spec exists before attempting to execute
        spec_exists = select_report_spec(report_spec_name, "ANY")
        if not spec_exists:
            raise ValueError(f"Unknown or invalid report spec: '{report_spec_name}'. Please use a valid report spec name.")

        # Inject default values for missing required parameters (e.g. search_string = "*")
        action = spec_exists.get("action") if isinstance(spec_exists, dict) else getattr(spec_exists, "action", None)
        if action:
            required_params = action.get("required_params", []) if isinstance(action, dict) else getattr(action, "required_params", [])
            spec_params = action.get("spec_params", {}) if isinstance(action, dict) else getattr(action, "spec_params", {})

            missing_params = [p for p in required_params if p not in params and p not in spec_params]
            if missing_params:
                import md_processing.md_processing_utils.md_processing_constants as constants
                constants.load_commands()
                specs = constants.COMMAND_DEFINITIONS.get("Command Specifications", {})

                injected = []
                for missing_param in missing_params:
                    # Search global definitions for a default_value corresponding to this variable_name
                    default_val = None
                    for cdef in specs.values():
                        if not isinstance(cdef, dict): continue
                        attr_defs = cdef.get("attribute_definitions", {})
                        for attr_def in attr_defs.values():
                            if attr_def.get("variable_name") == missing_param:
                                val = attr_def.get("default_value")
                                if val is not None and str(val).strip():
                                    default_val = val
                                    break
                        if default_val is not None:
                            break

                    if default_val is not None:
                        params[missing_param] = default_val
                        injected.append(missing_param)

                if injected:
                    logger.debug(f"ViewProcessor injected default values for missing required params: {injected}")

        # 4. Call the report executor
        # _async_run_report handles both fetching and formatting (via generate_output)
        result = await _async_run_report(
            report_name=report_spec_name,
            egeria_client=self.client,
            output_format=output_format,
            params=params
        )

        # 5. Handle the result structure from _async_run_report
        # Expected shapes: {"kind": "empty"}, {"kind": "text", "content": ...}, {"kind": "json", "data": ...}
        kind = result.get("kind")
        if kind == "empty":
            return f"\n\n# {self.command.verb} {self.command.object_type}\n\nNo elements found"
        
        elif kind == "text":
            content = result.get("content", "")
            # Ensure there's a heading if it's not already in the content
            if not content.strip().startswith("#"):
                return f"\n\n# {self.command.verb} {self.command.object_type}\n\n{content}"
            return f"\n\n{content}"
        
        elif kind == "json":
            data = result.get("data")
            formatted_json = json.dumps(data, indent=4)
            return f"\n\n# {self.command.verb} {self.command.object_type}\n\n```json\n{formatted_json}\n```"
        
        else:
            raw_result = result.get("raw", "Unknown result from report executor")
            return f"\n\n# {self.command.verb} {self.command.object_type}\n\n{raw_result}"

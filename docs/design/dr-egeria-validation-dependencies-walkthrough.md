# Walkthrough - Debugging Inter-Command Dependencies and API Failures

We have successfully enhanced Dr. Egeria v2 to handle inter-command dependencies and resolved critical API failures encountered in `process` mode. This ensures that elements defined earlier in a file are correctly recognized as "Planned" during validation and correctly resolved to real GUIDs during execution.

## Changes Made

### Reference Resolution and Execution Logic
- **Fixed NameError**: Resolved a `NameError` in `processors.py` that occurred during successful command execution.
- **Prioritized Real GUIDs**: Updated `resolve_element_guid` in `processors.py` to prioritize real GUIDs from the local cache and Egeria over "Planned" placeholders. This ensures that `process` mode uses actual GUIDs for linking.
- **Improved Heuristics**: Refined the heuristic for identifying reference candidates to exclude known descriptive string attributes (e.g., "Reference Abstract") and prioritize the command specification's `style` property.
- **Standardized Link Resolution**: Updated `AsyncBaseCommandProcessor.execute` to run a reference resolution loop for all commands, ensuring inter-command dependencies are tracked via the `planned_elements` context.
- **Safety Checks**: Added null checks for command specifications to prevent `AttributeError` when a spec is missing.

### Feedback Processor Improvements
- **Correct Attribute Keys**: Updated `FeedbackLinkProcessor` in `feedback.py` to use `Element Name` (as defined in the command specs) instead of the incorrect `Element Id`.
- **Unified Resolution**: leveraged the base class enhancements to ensure `link` commands correctly resolve GUIDs from both Egeria and the locally updated cache.

## Verification Results

### Validation Mode
When running `dr_egeria validate` on `ONNX.md`, inter-command references are now correctly resolved as "Planned":

```text
                                         Validation Diagnosis: Link External Reference                                         
  Attribute            Value                                                Status      
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
  Element Name         SolutionComponent::ONNX::V1.0                        🕒 Planned  
  External Reference   ExtRef::ONNX                                         🕒 Planned  
```

### Process Mode
When running `dr_egeria process` on `ONNX.md`, all commands now succeed, and relationships are correctly established using real GUIDs:

**Trace Confirmation:**
```text
INFO | _async_link_external_reference | 580 | Linking element c3953b1e-145d-45c6-aea0-08ac1d936240 to ext. ref. 48149275-9b39-4a3f-86d0-139a7a32f758
SUCCESS | apply_changes | 270 | Updated External Reference link
```

## Final State
Dr. Egeria v2 now robustly handles complex documentation sets where elements depend on each other. Validation is accurate, and the transition to permanent processing is seamless, resolving all reported `SERVER_ERROR_500` issues related to invalid GUID placeholders.

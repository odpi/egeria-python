# Dr.Egeria Refactoring Walkthrough

This document describes the historical refactoring of the `Dr.Egeria` markdown command processor.

## Phase 1: Registry-Based Dispatch (historical)

The original monolithic `if-elif` dispatch logic was replaced with a registry-based `CommandDispatcher` class (`command_dispatcher.py`) and a corresponding `command_mapping.py` that called `setup_dispatcher()` to register all v1 sync handlers.

## Phase 2: v2 Async Engine

The v1 sync dispatcher and all associated handler modules were superseded by the v2 async engine (`md_processing/v2/`). The v2 dispatcher (`V2Dispatcher`) routes commands to `AsyncBaseCommandProcessor` subclasses, driven by compact command specs in `md_processing/data/compact_commands/`.

## Phase 5 & 6: v1 Legacy Removal

The `md_processing/v1_legacy/` directory (containing the old `CommandDispatcher`, `command_mapping.py`, and all v1 handler modules) was deleted. The `DR_EGERIA_V2` environment variable switch was removed. All processing now goes through the v2 pipeline.

Tests previously driven by `commands_for_module(MODULE)` (which introspected the v1 dispatcher registry) were migrated to `commands_for_family(FAMILY)` (which reads command names directly from the compact spec `COMMAND_DEFINITIONS`).

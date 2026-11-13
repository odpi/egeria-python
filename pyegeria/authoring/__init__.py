# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""pyegeria.authoring: one typed authoring path for report specs, Reports and dashboard sheets (phase 1).

Grown from `pyegeria.view.report_spec_publish` (Stage 1a). Dr.Egeria markdown stays the serialization:
the API writes and checks it, so authors don't have to. It never authenticates: the caller passes a
client signed in as the user, and a runner that runs documents as the user.

    draft = new_draft("report", display_name=..., spec=..., parameters={...})
    validate(draft, client)            # structural, semantic, Dr.Egeria (with run=)
    preview(draft, client=client)      # a capped sample, run as the user; nothing registered
    diff(old, new)                     # breaking changes flagged
    plan = await async_publish_plan(draft, client, folders=[...])   # a new published version (D14)
    await async_apply(plan, step="process", run=run, client=client, confirmed=True, digest=plan["digest"])

The undecided gates (D7, D14, D16, D4) are switches: see `AuthoringGates`.
"""
from pyegeria.authoring.diff import diff
from pyegeria.authoring.drafts import (
    TEMPLATES, DraftStore, EgeriaDraftStore, LocalDraftStore, async_new_from, draft_store, new_draft, new_from,
)
from pyegeria.authoring.lifecycle import (
    KNOWN_CONSUMERS, apply, async_apply, async_history, async_load_held, async_publish_plan, history, load_held,
    publish_plan, withdraw_plan,
)
from pyegeria.authoring.models import (
    AuthoringGates, AuthoringRefused, Change, Diff, Draft, ReportDraft, SheetDraft, SheetPlacement, SpecDraft,
    ValidationResult, as_draft, default_gates,
)
from pyegeria.authoring.preview import async_preview, preview
from pyegeria.authoring.runner import inprocess_runner
from pyegeria.authoring.serialize import has_parent_id, report_parameter_maps, serialize
from pyegeria.authoring.validate import async_validate, validate

__all__ = [
    "AuthoringGates", "AuthoringRefused", "Change", "Diff", "Draft", "DraftStore", "EgeriaDraftStore",
    "KNOWN_CONSUMERS", "LocalDraftStore", "ReportDraft", "SheetDraft", "SheetPlacement", "SpecDraft", "TEMPLATES",
    "ValidationResult", "apply", "as_draft", "async_apply", "async_publish_plan", "async_history", "async_load_held", "async_new_from", "async_preview",
    "async_validate", "default_gates", "diff", "draft_store", "has_parent_id", "history", "inprocess_runner",
    "load_held", "new_draft", "new_from", "preview", "publish_plan", "report_parameter_maps", "serialize",
    "validate", "withdraw_plan",
]

# Debug — Classify Term as Question validation failure

> Minimal repro for a `Request body failed validation` error hit while
> processing the Scouting questions batch (2026-08-12). Targets an
> already-existing real GlossaryTerm ("Who maintains this repository?",
> GUID 73e54706-1cb9-4361-9ad8-1414b28531bd, created via `Create Glossary
> Term` against qs-view-server) so there's no dependency on anything else
> in this file — just the one command.
>
> Reproduced via the egeria MCP server's `dr_egeria_run_block` /
> `egeria_execute_command` tools with directive=process against
> qs-view-server (Coco Pharmaceuticals sandbox). Fails identically even
> with only `Term Name` supplied — varying `Status` (tried `ACTIVE`,
> `DISCOVERED`) made no difference. Works fine in directive=display /
> validate (which doesn't call the classification endpoint) — only fails
> when actually processed.
>
> By contrast, the standalone `Create Question` command (creates a
> separate Question-typed element, not a classification on a
> GlossaryTerm) succeeds cleanly in process mode with the same kind of
> attributes. That's the main clue: this looks like the classification
> command sending Create-style default fields (Is Own Anchor, Merge
> Update, Parent at End1) into what should be a pure classification
> request body, and the backend rejecting them.

## Classify Term as Question

### Term Name
Who maintains this repository?

___

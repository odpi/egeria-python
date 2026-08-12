# Dashboard Sheet Family — Happy Path Tests
# Sales Forecast Theme

> Tests Create Dashboard Sheet / Link Report to Dashboard Sheet / Add Text on
> Dashboard Sheet — none of these had regression coverage before this file
> (dr_test_report.md covers View Report/Create Report only). Primary focus:
> the two attributes added to Link Report to Dashboard Sheet / Add Text on
> Dashboard Sheet (BACKLOG.md NEXT-19/NEXT-21, egeria-workspaces-fs):
>   - Placement Perspectives — comma-separated viewer-role tags (governance,
>     steward, owner, consumer, engineer, builder, privacy, community)
>   - Placement Detail Spec — a drill-down target Report Spec name
>     (Link Report to Dashboard Sheet only; a text placement has no result
>     to drill into)
>
> These are all local-JSON-store records (pyegeria.view._output_dashboard_sheet_models),
> not Egeria elements — Create Dashboard Sheet/Link Report/Add Text have no
> GUID slot, no Qualified Name, no verb swap. Create Report (used here to
> have something to link) IS a real Egeria element — see dr_test_report.md's
> CR-* tests for that command's own dedicated coverage.
>
> Run with PROCESS (or VALIDATE to confirm parsing before execution).

---

# DS-01: Create Dashboard Sheet — minimal, Display Name + required Heading only

> Dashboard Sheet Heading is required at validation despite the processor
> having an `or name` fallback for it — that fallback exists for programmatic
> callers that bypass command validation, not for Dr.Egeria commands (caught
> live writing this test: VALIDATE rejected a Heading-less version with
> "Missing required attribute: 'Dashboard Sheet Heading'"). Description/
> Family are the attributes that actually default to empty.

## Create Dashboard Sheet

### Display Name
Sales Forecast Placement Test Sheet

### Dashboard Sheet Heading
Sales Forecast Placement Test Sheet

___

# DS-02: Create Dashboard Sheet — Heading, Description, Family

> A second sheet, fully specified, so the LP-* tests below have more than
> one target to place onto.

## Create Dashboard Sheet

### Display Name
Sales Forecast Placement Test Sheet 2

### Dashboard Sheet Heading
Sales Forecast — Placement Attribute Coverage

### Dashboard Sheet Description
Second Dashboard Sheet for exercising Placement Perspectives/Detail Spec.

### Dashboard Sheet Family
panel-library

___

> End of Create Dashboard Sheet tests.
>
> Expected outcomes:
>   DS-01 : New Dashboard Sheet record created; Heading required, explicit here
>   DS-02 : New Dashboard Sheet record created with explicit Heading/Description/Family

___
___

# Create Report — setup for placement tests below

> Two Reports to place on the sheets above. See dr_test_report.md's CR-*
> tests for Create Report's own dedicated coverage — these are just fixtures
> for the Dashboard Sheet placement tests that follow.

# SETUP-01: Create Report — for Link Report tests

## Create Report

### Display Name
Sales Forecast Placement Test Report

### Report Spec
Collections

### Output Format
TABLE

### Search String
Sales Forecast

___

# SETUP-02: Create Report — second Report, for the multi-placement test

## Create Report

### Display Name
Sales Forecast Placement Test Report 2

### Report Spec
Digital-Products

### Output Format
LIST

### Search String
Sales Forecast

___

> End of Report setup.

___
___

# Link Report to Dashboard Sheet — Happy Path Tests

# LP-01: Link Report — minimal, no layout hints, no new attributes

> Placement Span/Emphasis/Perspectives/Detail Spec all take their defaults
> (span "1", emphasis "kpi", perspectives empty, detail_spec None).
> Expected: placement relevant to every perspective (fail-open), no drill target.

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet

### Report Name
Sales Forecast Placement Test Report

___

# LP-02: Link Report — Placement Span and Placement Emphasis (baseline, pre-existing attributes)

> Confirms the two pre-existing layout attributes still work unchanged
> alongside this session's new ones being introduced below.

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet 2

### Report Name
Sales Forecast Placement Test Report

### Placement Span
full

### Placement Emphasis
panel

___

# LP-03: Link Report — Placement Perspectives, single tag

> Exercises the new Placement Perspectives attribute with exactly one tag.
> Expected: placement's perspectives = ["governance"] — visible only when
> filtering by "governance" (or when not filtering at all).

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet

### Report Name
Sales Forecast Placement Test Report 2

### Placement Perspectives
governance

___

# LP-04: Link Report — Placement Perspectives, multiple comma-separated tags

> Exercises comma-separated multi-value parsing.
> Expected: placement's perspectives = ["governance", "steward", "owner"]
> (order preserved, whitespace trimmed).

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet 2

### Report Name
Sales Forecast Placement Test Report 2

### Placement Perspectives
governance, steward,  owner

___

# LP-05: Link Report — Placement Detail Spec only

> Exercises the new drill-down attribute in isolation.
> Expected: placement's detail_spec = "Digital-Products".

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet

### Report Name
Sales Forecast Placement Test Report

### Placement Detail Spec
Digital-Products

___

# LP-06: Link Report — Placement Span, Emphasis, Perspectives, and Detail Spec combined

> All four Placement-level attributes together on one placement — the full
> combined case a real dashboard author is most likely to write.

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet 2

### Report Name
Sales Forecast Placement Test Report

### Placement Span
2

### Placement Emphasis
kpi

### Placement Perspectives
owner, consumer

### Placement Detail Spec
Collections

___

# LP-07: Link Report — re-run LP-06's Report/Sheet pair with changed attributes

> Same Dashboard Sheet Name + Report Name as LP-06 (a placement is replaced
> by matching Placement.ref, i.e. Report Name — not appended as a duplicate).
> Expected: same sheet still has one placement for this Report, now with the
> attributes below, not LP-06's.

## Link Report to Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet 2

### Report Name
Sales Forecast Placement Test Report

### Placement Span
1

### Placement Emphasis
panel

### Placement Perspectives
privacy

___

> End of Link Report to Dashboard Sheet tests.
>
> Expected outcomes:
>   LP-01 : Placement added; span=1, emphasis=kpi, perspectives=[], detail_spec=None (all defaults)
>   LP-02 : Placement added; span=full, emphasis=panel (pre-existing attributes unaffected)
>   LP-03 : Placement added; perspectives=["governance"]
>   LP-04 : Placement added; perspectives=["governance","steward","owner"]
>   LP-05 : Placement added; detail_spec="Digital-Products"
>   LP-06 : Placement added; span=2, emphasis=kpi, perspectives=["owner","consumer"], detail_spec="Collections"
>   LP-07 : Same placement (by Report Name) replaced, not duplicated; now span=1, emphasis=panel, perspectives=["privacy"]

___
___

# Add Text on Dashboard Sheet — Happy Path Tests

# TP-01: Add Text — minimal, MD Content only

> All layout/perspective attributes take their defaults.

## Add Text on Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet

### Placement Name
Section Header — Overview

### MD Content
**Sales Forecast Overview** — this section introduces the Sales Forecast
placement test coverage. (Note: a literal `#`/`##` markdown heading here
collides with Dr.Egeria's own file structure and truncates this attribute's
value — caught live writing this test, "Missing required attribute: 'MD
Content'" — so real dashboard-text placements should avoid top-level
heading syntax in MD Content, bold/blockquote emphasis as used here and in
TP-02/TP-03 is safe.)

___

# TP-02: Add Text — Placement Perspectives (new attribute on a text placement)

> Confirms Placement Perspectives applies to text placements too, not just
> Report placements (a section header can be perspective-scoped).

## Add Text on Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet

### Placement Name
Section Header — Governance Note

### MD Content
**Governance note**: this section is only relevant to governance/steward
viewers. (A leading `> ` blockquote line collides with this file format's
own comment-prefix convention at PROCESS time — caught live running this
test, "Execution failed: MD Content is required" — VALIDATE alone didn't
catch it, since its preview path skips the pass that trips on it. Bold text
without a leading `>` is safe, as used here.)

### Placement Perspectives
governance, steward

___

# TP-03: Add Text — Span, Emphasis, and Perspectives combined

## Add Text on Dashboard Sheet

### Dashboard Sheet Name
Sales Forecast Placement Test Sheet 2

### Placement Name
Section Header — Full Width Caption

### MD Content
Caption spanning the full row width, tagged for the owner/consumer perspectives.

### Placement Span
full

### Placement Emphasis
panel

### Placement Perspectives
owner, consumer

___

> End of Add Text on Dashboard Sheet tests.
>
> Expected outcomes:
>   TP-01 : Text placement added; perspectives=[] (default, relevant to every perspective)
>   TP-02 : Text placement added; perspectives=["governance","steward"]
>   TP-03 : Text placement added; span=full, emphasis=panel, perspectives=["owner","consumer"]

___

> End of Dashboard Sheet family happy path tests.

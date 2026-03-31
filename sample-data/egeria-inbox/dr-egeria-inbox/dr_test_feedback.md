# Feedback Family — Happy Path Tests
# Sales Forecast Theme

> This document tests the Dr.Egeria Feedback command family under normal conditions.
> All commands are expected to succeed when processed.
>
> Run with VALIDATE first, then PROCESS.
>
> GUID appears only in Create commands — the system fills it on first processing.
> Update commands are identified by Qualified Name.
> Link/Attach commands are identified by their endpoint attributes — no GUID.
>
> Verb synonyms:
>   Establish: Link, Attach, Add (all equivalent)
>   Remove:    Detach, Unlink, Remove (all equivalent)
>
> Note: Create Comment includes Commented On Element directly (required) —
> the comment is created and attached to its target element in a single command.
> Comment is a Referenceable (not Authored Referenceable) — no Content Status or Authors.
>
> Note: The relationship commands in this family use Attach as their canonical verb.
> Removal uses Detach, Unlink, or Remove.
>
> Comment Type valid values:
>   STANDARD_COMMENT, QUESTION, ANSWER, SUGGESTION, USAGE_EXPERIENCE, REQUIREMENT, OTHER
>
> Stars valid values:
>   NO_RECOMMENDATION, ONE_STAR, TWO_STARS, THREE_STARS, FOUR_STARS, FIVE_STARS

---

# FB-01: Create Comment — minimal, QN auto-generated

> Commented On Element is required and must be provided even in a minimal command.
> Expected: GUID filled, QN auto-generated, verb swapped to Update Comment.

# Create Comment

## Display Name
SF-Comment-Smoke-Test

## Commented On Element
DigitalProduct::SalesForecast::Pipeline::1.2

## Description
A minimal comment to test the Create Comment command. Commented On Element is required
___

# FB-02: Create Comment — STANDARD_COMMENT, user-specified QN

> Exercises Comment Type (Valid Value), Commented On Element (required Reference Name),
> and common Referenceable fields: Description, Category, Journal Entry.
> Note: no Content Status — Comment inherits from Referenceable, not Authored Referenceable.

# Create Comment

## Display Name
Sales Forecast Pipeline Coverage — Data Quality Observation

## Description
The pipeline coverage ratio for Q1 2026 appears to be inflating actual pipeline
value due to duplicate opportunity records in the CRM. Recommend deduplication
before the board submission on 2026-03-28.

## Comment Type
STANDARD_COMMENT

## Commented On Element
DigitalProduct::SalesForecast::Pipeline::1.2

## Category
Data Quality

## Journal Entry
Raised during the Q1 2026 forecast review meeting on 2026-03-15.

## Qualified Name
Comment::SalesForecast::PipelineCoverage::DataQualityObservation::1.0

## GUID

___

# FB-03: Create Comment — QUESTION type, user-specified QN

> A question comment attached to a glossary term.
> Used later in FB-13 as the Accepted Answer Comment in Link Accept Answer.

# Create Comment

## Display Name
How is Pipeline Coverage Ratio calculated for multi-currency opportunities?

## Description
We have opportunities denominated in EUR and GBP in the Q1 pipeline.
Is the Pipeline Coverage Ratio calculated using converted USD amounts
or native currency values? This affects the 3x coverage threshold assessment.

## Comment Type
QUESTION

## Commented On Element
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Category
Forecast Methodology

## Qualified Name
Comment::SalesForecast::PCR::MultiCurrencyQuestion::1.0

## GUID

___

# FB-04: Create Comment — ANSWER type, user-specified QN

> An answer to FB-03, attached to the same glossary term.
> Used as the Answering Comment in Link Accept Answer FB-13.

# Create Comment

## Display Name
Pipeline Coverage Ratio uses USD-converted amounts via daily exchange rates

## Description
The Pipeline Coverage Ratio is always calculated using USD-converted amounts.
Conversion uses the daily exchange rate from the treasury rate table as of the
forecast run date. Native currency values are preserved in the CRM record
for audit purposes but are not used in the coverage calculation.

## Comment Type
ANSWER

## Commented On Element
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Category
Forecast Methodology

## Qualified Name
Comment::SalesForecast::PCR::MultiCurrencyAnswer::1.0

## GUID

___

# FB-05: Create Comment — SUGGESTION type

# Create Comment

## Display Name
Suggest adding automated duplicate detection to CRM pipeline export

## Description
To prevent recurring data quality issues like the one in FB-02, suggest adding
an automated duplicate detection step to the Salesforce Opportunity export feed
before it enters the forecast pipeline.

## Comment Type
SUGGESTION

## Commented On Element
ExternalDataSource::Salesforce::OpportunityFeed::Daily::1.0

## Qualified Name
Comment::SalesForecast::Pipeline::DuplicateDetectionSuggestion::1.0

## GUID

___

# FB-06: Create Comment — USAGE_EXPERIENCE type

# Create Comment

## Display Name
Pipeline Coverage Ratio term definition is clear and actionable

## Description
The Pipeline Coverage Ratio term definition in the Sales Forecast Domain Glossary
is well-written and easy to apply. The 3x threshold example is particularly helpful
for onboarding new analysts to the forecasting process.

## Comment Type
USAGE_EXPERIENCE

## Commented On Element
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Qualified Name
Comment::SalesForecast::PCR::UsageExperience::1.0

## GUID

___

# FB-07: Create Comment — REQUIREMENT type

# Create Comment

## Display Name
Forecast pipeline must support real-time opportunity updates by Q3 2026

## Description
The current batch-based forecast pipeline runs once daily. Business requirement:
the pipeline must support near-real-time opportunity updates (latency under 15 minutes)
by Q3 2026 to support intra-day pipeline management by field sales leadership.

## Comment Type
REQUIREMENT

## Commented On Element
DigitalProduct::SalesForecast::Pipeline::1.2

## Qualified Name
Comment::SalesForecast::Pipeline::RealTimeRequirement::1.0

## GUID

___

# FB-08: Create Informal Tag — user-specified QN

> Informal tags are user-defined labels attachable to any Referenceable.
> Create Informal Tag does inherit from Authored Referenceable so Content Status is valid here.

# Create Informal Tag

## Display Name
forecast-critical

## Description
Tag indicating that this element is critical to the Sales Forecast pipeline
and should be prioritised for data quality monitoring and governance reviews.

## Qualified Name
InformalTag::SalesForecast::ForecastCritical::1.0

## GUID

___

# FB-09: Create Informal Tag — second tag

# Create Informal Tag

## Display Name
needs-review

## Description
Tag indicating that this element has been flagged for review by the
Data Governance team before the next forecast cycle.

## Qualified Name
InformalTag::SalesForecast::NeedsReview::1.0

## GUID

___

# FB-10: Update Comment — identified by Qualified Name

> Update flavor. No GUID. Comment located by Qualified Name.
> Commented On Element does not need to be repeated on Update.

# Update Comment

## Display Name
Sales Forecast Pipeline Coverage — Data Quality Observation

## Qualified Name
Comment::SalesForecast::PipelineCoverage::DataQualityObservation::1.0

## Description
The pipeline coverage ratio for Q1 2026 was inflating actual pipeline value
due to duplicate opportunity records in the CRM. Deduplication completed
2026-03-18. Coverage ratio recalculated and confirmed at 3.4x.

## Journal Entry
Updated following deduplication remediation completed 2026-03-18.

___

# FB-11: Attach Rating — FIVE_STARS with review text

> Attaches a star rating and text review to a glossary term.
> No GUID on Attach commands.

# Attach Rating

## Reviewed Element
GlossaryTerm::SalesForecast::PipelineCoverageRatio::1.0

## Stars
FIVE_STARS

## Review
Excellent definition — precise, well-exemplified, and directly applicable to
day-to-day forecasting decisions. The PCR formula and 3x threshold guidance
are exactly what analysts need.

___

# FB-12: Attach Rating — THREE_STARS, different element

# Attach Rating

## Reviewed Element
GlossaryTerm::SalesForecast::CommitForecast::1.0

## Stars
THREE_STARS

## Review
Good definition but lacks guidance on how to handle partial-period commits.
Could benefit from an example covering mid-quarter close date changes.

___

# FB-13: Link Accept Answer — connects question to its accepted answer

> Links a QUESTION comment to the ANSWER comment that resolves it.
> Accepted Answer Comment is the question (FB-03); Answering Comment is the answer (FB-04).
> No GUID on Link commands.

# Link Accept Answer

## Accepted Answer Comment
Comment::SalesForecast::PCR::MultiCurrencyQuestion::1.0

## Answering Comment
Comment::SalesForecast::PCR::MultiCurrencyAnswer::1.0

___

# FB-14: Attach Like — with Emoji, verb Attach

# Attach Like

## Liked Element
Comment::SalesForecast::PCR::MultiCurrencyAnswer::1.0

## Emoji
👍

___

# FB-15: Attach Like — without Emoji, verb Add (synonym)

> Uses Add as the establish synonym. Emoji is optional and omitted here.

# Add Like

## Liked Element
GlossaryTerm::SalesForecast::Opportunity::1.0

___

# FB-16: Attach Tag — verb Attach

# Attach Tag

## Informal Tag
InformalTag::SalesForecast::ForecastCritical::1.0

## Tagged Element
DigitalProduct::SalesForecast::Pipeline::1.2

___

# FB-17: Attach Tag — second tag, different element

# Attach Tag

## Informal Tag
InformalTag::SalesForecast::NeedsReview::1.0

## Tagged Element
GlossaryTerm::SalesForecast::CommitForecast::1.0

___

# FB-18: Detach Rating — verb Detach

> Removes the rating attached in FB-12.
> Identified by Reviewed Element — no GUID.

# Detach Rating

## Reviewed Element
GlossaryTerm::SalesForecast::CommitForecast::1.0

___

# FB-19: Unlink Like — verb Unlink

> Removes the like attached in FB-15.

# Unlink Like

## Liked Element
GlossaryTerm::SalesForecast::Opportunity::1.0

___

# FB-20: Remove Tag — verb Remove

> Removes the tag attached in FB-17. Exercises the third removal synonym.

# Remove Tag

## Informal Tag
InformalTag::SalesForecast::NeedsReview::1.0

## Tagged Element
GlossaryTerm::SalesForecast::CommitForecast::1.0

___

> End of Feedback happy path tests.
>
> Expected outcomes:
>   FB-01               : GUID filled, QN auto-generated, Commented On Element accepted as required
>   FB-02 to FB-07      : GUID filled, QN preserved, Comment Type and Commented On Element set;
>                         no Content Status field in output (Comment is Referenceable)
>   FB-08, FB-09        : Informal Tags created with user-specified QNs
>   FB-10               : Update locates comment by QN, no Commented On Element needed, no GUID slot
>   FB-03, FB-04        : QUESTION and ANSWER Comment Types accepted
>   FB-05               : SUGGESTION Comment Type accepted
>   FB-06               : USAGE_EXPERIENCE Comment Type accepted
>   FB-07               : REQUIREMENT Comment Type accepted
>   FB-11, FB-12        : Attach Rating executed with Stars and Review text, no GUID slot
>   FB-13               : Link Accept Answer connects FB-03 question to FB-04 answer
>   FB-14               : Attach Like with Emoji accepted
>   FB-15               : Add synonym accepted; Emoji absent (optional field)
>   FB-16, FB-17        : Attach Tag executed, no GUID slot
>   FB-18               : Detach removes rating
>   FB-19               : Unlink removes like
>   FB-20               : Remove removes tag; all three removal synonyms exercised
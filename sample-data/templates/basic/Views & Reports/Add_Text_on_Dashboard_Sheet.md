___

## Add Text on Dashboard Sheet
> Places literal markdown text (a section header, explanation, or caption) into a Dashboard Sheet as an ordered placement, alongside Report placements. In Egeria the placement is a DisplayDataField of the sheet that holds the text. Re-running it with the same Placement Name updates it in place. The Dashboard Sheet must already exist (Create Dashboard Sheet). The local JSON store (PYEGERIA_DASHBOARD_SHEETS_STORE) is a fallback: with --local-only or no Egeria connection, only the store is written, and the command output says so.

### Dashboard Sheet Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The unique name of a Dashboard Sheet, held in Egeria as a Dashboard with its layout (a DisplayDataSchemaType, the sheet's DisplayDataContainer, and one DisplayDataField per placement). Used both to name a new Dashboard Sheet (Create Dashboard Sheet) and to refer to an existing one (Link Report to Dashboard Sheet, Add Text on Dashboard Sheet).


### MD Content
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Markdown text to display at this placement -- section headers, explanations, captions. Rendered as-is (mermaid fences supported). Held in Egeria as the placement's markdownContent.


### Placement Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Stable identifier for this text placement within its Dashboard Sheet — re-running with the same Dashboard Sheet Name + Placement Name updates it in place, same as Report placements are replaced by Report Name.


### Placement Emphasis
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Presentation hint for a Report Spec placed in a Dashboard Sheet — 'kpi' (compact tile) or 'panel' (larger, detailed).

>	**Valid Values**: kpi,panel

>	**Default Value**: kpi


### Placement Span
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Layout width hint for a Report Spec placed in a Dashboard Sheet — '1'/'2' (relative columns) or 'full' (row width).

>	**Valid Values**: 1,2,full

>	**Default Value**: 1


### Placement Perspectives
>	**Input Required**: False

>	**Attribute Type**: Simple List

>	**Description**: Comma-separated viewer-role/perspective tags this placement is relevant to (e.g. governance, steward, owner, consumer, engineer, builder, privacy, community -- the same vocabulary Egeria Overview's own perspective filtering uses). Empty means relevant to every perspective.


___

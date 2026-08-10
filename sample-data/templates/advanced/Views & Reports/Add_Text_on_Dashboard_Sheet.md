___

## Add Text on Dashboard Sheet
> Places literal markdown text (a section header, explanation, or caption) into a Dashboard Sheet as an ordered Placement, alongside Report placements. A local pyegeria Placement record, not an Egeria element or relationship — no upsert. The target Dashboard Sheet must already exist (Create Dashboard Sheet).

### Dashboard Sheet Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: The unique name of a Dashboard Sheet — a local pyegeria-managed record (planned to become a Collection subtype in Egeria; see Container/ContainerDict in pyegeria.view._output_container_models for the current pre-Egeria model). Used both to define a new Dashboard Sheet's identity (Create Dashboard Sheet) and to reference an existing one (Link Report to Dashboard Sheet).


### MD Content
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Markdown text to display at this placement — section headers, explanations, captions. Rendered as-is (mermaid fences supported), no Egeria element involved.


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


___

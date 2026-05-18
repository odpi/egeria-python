# New Commands Test — Perspectives, Skills, SkillSets, Linked Skill Sets, and Question Classification

> This file tests the five new Dr.Egeria commands:
>   1. Create Skill Set         (Collections family)
>   2. Create Perspective       (Actor Manager family)
>   3. Create Skill             (Actor Manager family)
>   4. Link Associated Skill Set (Actor Manager family)
>   5. Classify Term as Question (Glossary family)
>
> The commands in section NC-04 depend on a SkillSet created in NC-01
> and an ActorRole — use one created in a prior run or via the actor_full_test.md file.
>
> Run with VALIDATE first, then PROCESS.

---

# NC-01: Create Skill Set — Data Analysis skills

> Creates a SkillSet collection to hold data-analysis-related skills.
> Expected: GUID filled, type stored as SkillSet (not plain Collection).


## Update Skill Set

### Skill Set Name 

Data Analysis Skills

### Display Name
Data Analysis Skills

### Qualified Name
SkillSet::DataAnalysisSkills

### Category
Technical

### Description
A collection of skills related to data analysis and statistical methods.

### Type Name
SkillSet

### Url
None

### Version Identifier
1.0

### Classifications
None

### Additional Properties
None

### Created By
None

### Create Time
None

### Updated By
None

### Update Time
None

### Effective From
None

### Effective To
None

### Version
None

### Open Metadata Type Name
SkillSet

### Content Status
ACTIVE

### Activity Status
None

### Deployment Status
None


___

---

# NC-02: Create Perspective — Operational Resilience

> Creates a Perspective entity representing a viewpoint on operational resilience.


## Update Perspective

### Perspective Name 

Operational Resilience Perspective

### Display Name
Operational Resilience Perspective

### Qualified Name
Perspective::OperationalResilience

### Category
None

### Description
A viewpoint focused on ensuring systems and teams remain resilient under operational stress.

### Type Name
Perspective

### Url
None

### Version Identifier
1.0

### Classifications
None

### Additional Properties
None

### Created By
None

### Create Time
None

### Updated By
None

### Update Time
None

### Effective From
None

### Effective To
None

### Version
None

### Open Metadata Type Name
Perspective

### Content Status
None

### Activity Status
None

### Deployment Status
None


___

---

# NC-03: Create Skill — Data Profiling

> Creates a Skill entity representing the data profiling competency.
> Authors is an Authored Referenceable field.


## Update Skill

### Skill Name 

Data Profiling

### Display Name
Data Profiling

### Qualified Name
Skill::DataProfiling

### Category
None

### Description
The ability to examine datasets to collect statistics and identify data quality issues.

### Type Name
Skill

### Url
None

### Version Identifier
1.0

### Classifications
None

### Additional Properties
None

### Created By
None

### Create Time
None

### Updated By
None

### Update Time
None

### Effective From
None

### Effective To
None

### Version
None

### Open Metadata Type Name
Skill

### Content Status
ACTIVE

### Activity Status
None

### Deployment Status
None


___

---

# NC-04: Link Associated Skill Set

> Links an ActorRole to the SkillSet created in NC-01.
> Actor Name must reference an existing ActorRole (not an ActorProfile).
> Use the role-hr-specialist created in actor_full_test.md, or replace with
> any ActorRole qualified name available in your environment.

## Don't Link Associated Skill Set

### Actor Name
role-hr-specialist

### SkillSet Name
SkillSet::DataAnalysisSkills

---

# NC-05: Classify Term as Question — classify a glossary term

> Applies the IsQuestion classification to an existing GlossaryTerm.
> Replace the Term Name value with a qualified name of a term in your environment.

## Classify Term as Question

### Term Name
GlossaryTerm::SalesForecast

---

# NC-05b: Declassify Term as Question — remove the question classification

> Removes the IsQuestion classification from the same glossary term.

## Declassify Term as Question

### Term Name
GlossaryTerm::SalesForecast

---



## Provenance:
 
- Derived from processing file dr_test_new_commands.md on 2026-05-17 16:10

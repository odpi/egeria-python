<!-- Two real Dr.Egeria commands, copied verbatim from egeria-workspaces coco-workbooks/4. keeping-safe/it-governance-program.md (lines 35-79 and 618-656, egeria-workspaces-fs 564de8f0) for the 6.2.39 list-attribute test. -->

## Create Business Imperative

### Display Name
Digital Services the Business Can Depend On

### Qualified Name
CocoPharma::BusinessImperative::DependableDigitalServices

### Domain Identifier
IT Infrastructure

### Summary
Coco Pharmaceuticals must run digital services whose availability, change behaviour, and recovery characteristics are known and agreed, so that the domains depending on them can make commitments of their own.

### Description
Every regulatory commitment the company makes is, somewhere underneath, a commitment about a system. A batch cannot be released if the electronic batch record system is unavailable; a data subject request cannot be answered in a month if the systems holding the data cannot be searched; expedited safety reporting cannot meet a seven-day deadline through a manual workaround. What the business needs from this domain is not maximal availability everywhere, which is unaffordable, but *known* characteristics — an agreed service level, an understood recovery time, and a change process that does not surprise the people who depend on the service. This imperative is deliberately expressed as dependability rather than uptime, because a service that is reliably available four days a week is more useful to plan around than one that is usually available and occasionally not. The measure of success is that other domains can state their own commitments with confidence, not that this domain reports high availability figures.

### Implications
- Service characteristics must be agreed with the depending domain, not set by IT alone
- Recovery objectives must reflect what the business actually needs, which differs sharply by service
- Change behaviour must be predictable, since unpredictability is itself an availability problem
- Investment must be justified by the obligations it lets other domains discharge

### Outcomes
- Domains can make regulatory and business commitments knowing what they rest on
- Service investment is directed by consequence rather than by uniform standards
- Unplanned change ceases to be a source of compliance failure in other domains

### Importance
High

### Category
IT Infrastructure

### Authors
Gary Geeke

### Version Identifier
1.0

### Content Status
ACTIVE

___


---

## Create Governance Metric

### Display Name
Recovery Objective Test Coverage and Achievement

### Qualified Name
CocoPharma::GovernanceMetric::RecoveryTestCoverage

### Domain Identifier
IT Infrastructure

### Summary
Measures the percentage of services with a recovery objective that have been exercised within their test cycle, and the proportion of those exercises that met the agreed objective.

### Description
Coverage and achievement are separate questions and both matter. Coverage asks whether the exercise happened; achievement asks whether the tested recovery met what the depending domain was promised. A service with high coverage and poor achievement is honestly reported and correctable; one with poor coverage is a service whose stated objective is unverified, and unverified objectives are the ones that fail during an actual incident. Reporting is per service and goes to the Service Owner and the depending domain rather than only to the infrastructure team, which is the arrangement that makes a shortfall actionable by the people it affects. Services supporting regulatory deadlines — batch release, safety reporting, data subject requests — are reported separately because a recovery shortfall there converts directly into a missed statutory obligation. Where achievement falls persistently short and the gap cannot be closed economically, the metric is the evidence for renegotiating the objective rather than continuing to report failure against a target nobody can meet.

### Implications
- Coverage and achievement are distinct measures and both are required
- Results go to the Service Owner and the depending domain, not only to IT
- Services supporting regulatory deadlines are reported separately
- Persistent shortfall is evidence for renegotiating the objective, not for repeated failure reporting

### Outcomes
- Stated recovery objectives are verified rather than assumed
- Depending domains learn of shortfalls before an incident reveals them
- Objectives converge on what can actually be delivered

### Authors
Gary Geeke

### Version Identifier
1.0

### Content Status
ACTIVE

___


# Security Officer — Survey Report and Security Finding Test

Exercises the security testing commands added for Egeria 6.3 (model 0665): a
stand-in tested system, two penetration test runs catalogued as survey reports,
findings of each type under the first run, a posture summary per run, and a
finding in the second run linked to the same finding in the first. SF-8
updates a finding to show the Create/Update transition.

Every element is named "SecTest4 ..." so it is easy to find and remove.

___

# SF-1: The system that was tested

## Create Collection

### Display Name
SecTest4 Supplier Portal

### Qualified Name
Collection::SecTest4 Supplier Portal

### Description
Stands in for the supplier portal asset that was tested.

___

# SF-2: The first test run

## Create Survey Report

### Display Name
SecTest4 Supplier Portal 2026-Q4 Penetration Test

### Qualified Name
SurveyReport::SecTest4::2026-Q4

### Category
Penetration Test Results

### Purpose
Quarterly penetration test of the supplier portal.

### Start Time
2026-10-20T09:00:00Z

### Completion Time
2026-10-24T17:00:00Z

### Report Subjects
Collection::SecTest4 Supplier Portal

___

# SF-3: A penetration test finding

## Create Penetration Test Finding

### Display Name
SecTest4 SQL injection in supplier search

### Qualified Name
PenetrationTestFinding::SecTest4::2026-Q4::sqli

### Identifier
PT-2026Q4-1

### Survey Report
SurveyReport::SecTest4::2026-Q4

### Severity
High

### CVSS Score
8.6

### Weakness Identifiers
CWE-89

### Affected Location
https://supplier-portal/search

### Exploit Available
True

### Attack Vector
Network

### Attack Techniques
T1190

### Privileges Gained
Read access to the supplier database.

### Compromised Resources
Supplier Master Register

### Remediation
Use parameterized queries in the supplier search.

### Affected Elements
Collection::SecTest4 Supplier Portal

___

# SF-4: A vulnerability finding

## Create Vulnerability Finding

### Display Name
SecTest4 Log4Shell in portal backend

### Qualified Name
VulnerabilityFinding::SecTest4::2026-Q4::log4shell

### Identifier
SCAN-42

### Survey Report
SurveyReport::SecTest4::2026-Q4

### Severity
Critical

### CVSS Score
10.0

### Vulnerability Identifiers
CVE-2021-44228

### Package URL
pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1

### Installed Version
2.14.1

### Fixed Version
2.17.1

### Patch Available
True

___

# SF-5: Another security finding

## Create Security Finding

### Display Name
SecTest4 TLS 1.0 enabled

### Qualified Name
SecurityFinding::SecTest4::2026-Q4::tls10

### Survey Report
SurveyReport::SecTest4::2026-Q4

### Severity
Medium

### Affected Location
supplier-portal:443

___

# SF-6: The first run's posture summary

## Create Security Posture Summary

### Display Name
SecTest4 2026-Q4 posture

### Qualified Name
SecurityPosture::SecTest4::2026-Q4

### Survey Report
SurveyReport::SecTest4::2026-Q4

### Finding Counts By Severity
Critical: 1
High: 1
Medium: 1

### Resources In Scope Count
3

### Resources Tested Count
3

### New Finding Count
3

### Resolved Finding Count
0

___

# SF-7: The next run, which still finds the TLS issue

## Create Survey Report

### Display Name
SecTest4 Supplier Portal 2027-Q1 Penetration Test

### Qualified Name
SurveyReport::SecTest4::2027-Q1

### Category
Penetration Test Results

### Completion Time
2027-01-24T17:00:00Z

### Report Subjects
Collection::SecTest4 Supplier Portal

___

## Create Security Finding

### Display Name
SecTest4 TLS 1.0 still enabled

### Qualified Name
SecurityFinding::SecTest4::2027-Q1::tls10

### Survey Report
SurveyReport::SecTest4::2027-Q1

### Severity
Medium

### Previous Finding
SecurityFinding::SecTest4::2026-Q4::tls10

___

## Create Security Posture Summary

### Display Name
SecTest4 2027-Q1 posture

### Qualified Name
SecurityPosture::SecTest4::2027-Q1

### Survey Report
SurveyReport::SecTest4::2027-Q1

### Finding Counts By Severity
Medium: 1

### Resources In Scope Count
3

### Resources Tested Count
3

### New Finding Count
0

### Resolved Finding Count
2

___

# SF-8: Update a finding

## Update Penetration Test Finding

### Display Name
SecTest4 SQL injection in supplier search

### Qualified Name
PenetrationTestFinding::SecTest4::2026-Q4::sqli

### Survey Report
SurveyReport::SecTest4::2026-Q4

### Reproduction Steps
Search for `' OR 1=1 --` in the supplier name field.

___

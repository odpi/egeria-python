# Action Author — Governance Action Process Flow Test

Exercises all 5 Action Author commands: builds a small two-step governance
action process (detect duplicates -> merge duplicates), plus a standalone
Governance Action Type not attached to any process.

___

# AA-1: Create Governance Action Process

## Create Governance Action Process

### Display Name
Data Quality Remediation Process

### Summary
Coordinates detection and remediation of duplicate records in the customer data domain.

### Domain Identifier
DATA

### Content Status
ACTIVE

### Qualified Name
GovActionProcess::DataQuality::Remediation::1.0

### GUID

___

# AA-2: Create Governance Action Process Step (first step)

## Create Governance Action Process Step

### Display Name
Detect Duplicates Step

### Summary
Scans the customer data domain for candidate duplicate records.

### Domain Identifier
DATA

### Wait Time
0

### Ignore Multiple Triggers
false

### Content Status
ACTIVE

### Qualified Name
GovActionProcessStep::DataQuality::DetectDuplicates::1.0

### GUID

___

# AA-3: Create Governance Action Process Step (next step)

## Create Governance Action Process Step

### Display Name
Merge Duplicates Step

### Summary
Merges confirmed duplicate records identified by the detection step.

### Domain Identifier
DATA

### Wait Time
5

### Ignore Multiple Triggers
true

### Content Status
ACTIVE

### Qualified Name
GovActionProcessStep::DataQuality::MergeDuplicates::1.0

### GUID

___

# AA-4: Create Governance Action Type (standalone, not part of the process above)

## Create Governance Action Type

### Display Name
Ad Hoc Duplicate Scan

### Summary
Reusable one-off call to the duplicate-detection governance service, outside of any formal process flow.

### Domain Identifier
DATA

### Wait Time
0

### Produced Guards
SUCCESS, FAILURE

### Content Status
ACTIVE

### Qualified Name
GovActionType::DataQuality::AdHocDuplicateScan::1.0

### GUID

___

# AA-5: Link First Process Step

## Link First Process Step

### Governance Action Process
GovActionProcess::DataQuality::Remediation::1.0

### Governance Action Process Step
GovActionProcessStep::DataQuality::DetectDuplicates::1.0

### Description
Processing begins with duplicate detection.

___

# AA-6: Link Next Process Step

## Link Next Process Step

### Governance Action Process Step
GovActionProcessStep::DataQuality::DetectDuplicates::1.0

### Next Governance Action Process Step
GovActionProcessStep::DataQuality::MergeDuplicates::1.0

### Guard
DUPLICATES_FOUND

### Mandatory Guard
true

### Description
Move to the merge step once duplicates are confirmed found.

___

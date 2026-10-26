# Security Officer — Statement of Applicability Test

Exercises the statement of applicability commands added for Egeria 6.3:
creates a certification type, two governance controls and a scope element to
stand in for a standard's controls (so no licensed content or Security Content
Pack is needed), then a statement governed by the certification type and
scoped by the scope element, and links both controls to it. SO-7 re-links a
control to show the link updates the existing relationship, SO-8 updates the
statement, and SO-9 unlinks a control.

Every element is named "SoATest ..." so it is easy to find and remove.

___

# SO-1: Create Certification Type

## Create Certification Type

### Display Name
SoATest Certification

### Qualified Name
CertificationType::SoATest Certification

### Summary
Stand-in certification type for the statement of applicability test.

___

# SO-2: Create Governance Control (first control)

## Create Governance Control

### Display Name
SoATest Control Network Security

### Qualified Name
GovernanceControl::SoATest::8.20

### Summary
Networks and network devices shall be secured, managed and controlled.

### Identifier
8.20

___

# SO-3: Create Governance Control (second control)

## Create Governance Control

### Display Name
SoATest Control Secure Development

### Qualified Name
GovernanceControl::SoATest::8.25

### Summary
Rules for the secure development of software and systems shall be established and applied.

### Identifier
8.25

___

# SO-4: Create the scope element

## Create Collection

### Display Name
SoATest Org Scope

### Qualified Name
Collection::SoATest Org Scope

### Description
Stands in for the organization the statement covers.

___

# SO-5: Create Statement of Applicability

## Create Statement of Applicability

### Display Name
SoATest ISMS

### Qualified Name
StatementOfApplicability::SoATest ISMS

### Description
Which controls apply to the test ISMS.

### Version Identifier
1.0

### Scope
The information security management system for the test organization.

### Review Date
2026-10-26

### Authors
Simon Burr

### Content Status
DRAFT

### Certification Standard
CertificationType::SoATest Certification

### Scoped By
Collection::SoATest Org Scope

___

# SO-6: Link Control Applicability (both controls)

## Link Control Applicability

### Statement of Applicability
StatementOfApplicability::SoATest ISMS

### Control
GovernanceControl::SoATest::8.20

### Label
8.20

### Is Applicable
True

### Justification
Ransomware disruption to manufacturing.

### Inclusion Reasons
Risk Treatment

### Implementation Status
PARTIALLY_IMPLEMENTED

### Implementation Description
Segmented plant network; firewall rules under review.

### Review Date
2026-10-26

___

## Link Control Applicability

### Statement of Applicability
StatementOfApplicability::SoATest ISMS

### Control
GovernanceControl::SoATest::8.25

### Label
8.25

### Justification
Secure development is required by our customers.

### Inclusion Reasons
Business Requirement, Contractual Obligation

### Implementation Status
PLANNED

___

# SO-7: Re-link a control to update its status

## Link Control Applicability

### Statement of Applicability
StatementOfApplicability::SoATest ISMS

### Control
GovernanceControl::SoATest::8.20

### Label
8.20

### Justification
Ransomware disruption to manufacturing.

### Inclusion Reasons
Risk Treatment

### Implementation Status
IMPLEMENTED

### Implementation Description
Segmented plant network with enforced firewall rules.

### Review Date
2026-11-02

___

# SO-8: Approve the statement

## Update Statement of Applicability

### Display Name
SoATest ISMS

### Qualified Name
StatementOfApplicability::SoATest ISMS

### Content Status
APPROVED

___

# SO-9: Unlink a control

## Unlink Control Applicability

### Statement of Applicability
StatementOfApplicability::SoATest ISMS

### Control
GovernanceControl::SoATest::8.25

___

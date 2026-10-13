# Reference Data and Valid Metadata regression test

Inline values (Values / Value Table) are named <set qualified name>::<value>.
The link commands below use separately created values with unique display
names, so the document does not depend on the local qualified-name prefix.

## Create Reference Data Set
### Display Name
DrETest-OrderStatus

### Description
Regression test reference data set.

### Values
- PENDING
- ON HOLD, AWAITING STOCK

### Value Table
| Value     | Display Name | Description         | Default | Ordinal |
|-----------|--------------|---------------------|---------|---------|
| SHIPPED   | Shipped      | Left the warehouse  | true    | 10      |
| DELIVERED | Delivered    | Signed for          |         | 11      |


## Create Reference Data Value
### Display Name
DrETest-CANCELLED

### Preferred Value
CANCELLED

### In Reference Data Set
DrETest-OrderStatus

### Member Ordinal
20


## Create Reference Data Set
### Display Name
DrETest-LegacyOrderStatus


## Create Reference Data Value
### Display Name
DrETest-Legacy-X

### Preferred Value
X

### In Reference Data Set
DrETest-LegacyOrderStatus


## Link Mapped Valid Values
### Valid Value 1
DrETest-CANCELLED

### Valid Value 2
DrETest-Legacy-X

### Association Description
Legacy code X means CANCELLED.

### Confidence
90


## Link Consistent Valid Values
### Valid Value 1
DrETest-CANCELLED

### Valid Value 2
DrETest-Legacy-X


## Link Associated Valid Values
### Valid Value 1
DrETest-CANCELLED

### Valid Value 2
DrETest-Legacy-X

### Association Name
replaced-by


## Detach Consistent Valid Values
### Valid Value 1
DrETest-CANCELLED

### Valid Value 2
DrETest-Legacy-X

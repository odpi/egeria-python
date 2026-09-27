# Data Designer — 0580/0581 Data Dictionary Model Tests

> Exercises the Data Designer commands aligned with Egeria types 0580 (Data Dictionaries)
> and 0581 (Data Field Implementation): DataField partition-key / duplicate properties,
> MemberDataField and NestedDataField relationship properties, LinkedDataField,
> DataValueDefinition, the PrimaryKey classification on a data field, and detaching.
>
> Run with VALIDATE first, then PROCESS. Every element uses a DD0580 qualified name so the
> document is self-contained and safe to re-run (creates become updates).
>
> Coverage Category valid values: UNKNOWN, UNIQUE_IDENTIFIER, IDENTIFIER, CORE_DETAIL, EXTENDED_DETAIL
> Sort Order valid values: ASCENDING, DESCENDING, UNSORTED

---

# D580-01: Create Data Structure — Order

## Create Data Structure

### Display Name
DD0580 Order

### Description
An order placed by a customer.

### Namespace Path
sales.orders

### Name Patterns
order.*

### Qualified Name
DataStructure::DD0580::Order

___

# D580-02: Create Data Class — Order Identifier

## Create Data Class

### Display Name
DD0580 Order Identifier

### Description
Values that uniquely identify an order.

### Data Type
string

### Qualified Name
DataClass::DD0580::OrderIdentifier

___

# D580-03: Create Data Field — Order Id (partition key, member of Order, defined by a data class)

## Create Data Field

### Display Name
DD0580 Order Id

### Description
Unique identifier of the order.

### In Data Structure
DataStructure::DD0580::Order

### Position
1

### Minimum Cardinality
1

### Maximum Cardinality
1

### Coverage Category
UNIQUE_IDENTIFIER

### Data Type
string

### Is Nullable
false

### Allow Duplicate Values
false

### Is Partition Key
true

### Partition Key Position
1

### Sort Order
ASCENDING

### Data Class
DataClass::DD0580::OrderIdentifier

### Qualified Name
DataField::DD0580::OrderId

___

# D580-04: Create Data Field — Delivery Address

## Create Data Field

### Display Name
DD0580 Delivery Address

### Description
Where the order is delivered.

### Data Type
object

### Qualified Name
DataField::DD0580::DeliveryAddress

___

# D580-05: Create Data Field — Postcode (nested under Delivery Address on create)

## Create Data Field

### Display Name
DD0580 Postcode

### Description
Postal code of the delivery address.

### In Data Field
DataField::DD0580::DeliveryAddress

### Data Type
string

### Qualified Name
DataField::DD0580::Postcode

___

# D580-06: Create Data Field — Customer Id

## Create Data Field

### Display Name
DD0580 Customer Id

### Description
The customer that placed the order.

### Data Type
string

### Qualified Name
DataField::DD0580::CustomerId

___

# D580-07: Link Data Field to Data Structure — Delivery Address into Order (MemberDataField properties)

## Link Data Field to Data Structure

### Data Structure
DataStructure::DD0580::Order

### Data Field
DataField::DD0580::DeliveryAddress

### Position
2

### Minimum Cardinality
0

### Maximum Cardinality
1

### Coverage Category
CORE_DETAIL

___

# D580-08: Link Nested Data Field — Customer Id under Delivery Address (NestedDataField)

## Link Nested Data Field

### Parent Data Field
DataField::DD0580::DeliveryAddress

### Nested Data Field
DataField::DD0580::CustomerId

### Position
1

### Coverage Category
IDENTIFIER

___

# D580-09: Detach Nested Data Field — undo D580-08

## Detach Nested Data Field

### Parent Data Field
DataField::DD0580::DeliveryAddress

### Nested Data Field
DataField::DD0580::CustomerId

___

# D580-10: Link Data Field — Customer Id is a foreign key from Order Id (LinkedDataField)

## Link Data Field

### Linked Data Field 1
DataField::DD0580::OrderId

### Linked Data Field 2
DataField::DD0580::CustomerId

### Link Relationship Type Name
ForeignKey

### Relationship End
0

### Label
placed by

### Description
Each order is placed by one customer.

___

# D580-11: Link Data Value Definition — Customer Id defined by the Order Identifier class

## Link Data Value Definition

### Element Id
DataField::DD0580::CustomerId

### Data Value Specification
DataClass::DD0580::OrderIdentifier

### Label
identifier format

___

# D580-12: Classify Data Field as Primary Key — Order Id

## Classify Data Field as Primary Key

### Data Field
DataField::DD0580::OrderId

### Primary Key Name
order key

### Primary Key Pattern
NATURAL_KEY

___

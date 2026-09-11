## Create Schema Type
### Display Name
DrETest-SchemaType

### Description
Regression test schema type.


## Create Schema Attribute
### Display Name
DrETest-ParentAttribute

### Element Position
0

### Min Cardinality
1

### Max Cardinality
1


## Create Schema Attribute
### Display Name
DrETest-ChildAttribute

### Element Position
0


## Link Nested Schema Attribute
### Schema Attribute GUID
DrETest-ParentAttribute

### Nested Schema Attribute GUID
DrETest-ChildAttribute


## Link Attribute for Schema
### Schema Type GUID
DrETest-SchemaType

### Schema Attribute GUID
DrETest-ParentAttribute


## Link Schema
### Schema Element GUID
DrETest-SchemaType

### Schema Type GUID
DrETest-SchemaType


## Add Primary Key Classification
### Relational Column GUID
DrETest-ParentAttribute

### Primary Key Name
DrETest-PK

### Primary Key Pattern
LOCAL_KEY


## Add Calculated Value
### Schema Attribute GUID
DrETest-ChildAttribute

### Formula
concat(firstName, ' ', lastName)

### Formula Type
SQL


## Detach Schema
### Schema Element GUID
DrETest-SchemaType

### Schema Type GUID
DrETest-SchemaType


## Detach Attribute for Schema
### Schema Type GUID
DrETest-SchemaType

### Schema Attribute GUID
DrETest-ParentAttribute


## Detach Nested Schema Attribute
### Schema Attribute GUID
DrETest-ParentAttribute

### Nested Schema Attribute GUID
DrETest-ChildAttribute

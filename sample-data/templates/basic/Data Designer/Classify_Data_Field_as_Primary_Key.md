___

## Classify Data Field as Primary Key
> Record that a data field is (part of) the identifier for its records (PrimaryKey classification). Primary Key Name is stored as the classification's display name.

### Data Field
>	**Input Required**: True

>	**Attribute Type**: Reference Name

>	**Description**: A data field  name. Preferably a qualified name.


### Journal Entry
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: A text entry into a journal.


### Primary Key Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Name of the primary key.


### Primary Key Pattern
>	**Input Required**: False

>	**Attribute Type**: Valid Value

>	**Description**: Key pattern for this primary key.

>	**Valid Values**: LOCAL_KEY,RECYCLED_KEY,NATURAL_KEY,MIRROR_KEY,AGGREGATE_KEY,CALLERS_KEY,STABLE_KEY,OTHER

>	**Default Value**: LOCAL_KEY


___

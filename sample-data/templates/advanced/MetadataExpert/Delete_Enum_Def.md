___

## Delete Enum Def
> Delete an enum definition. WARNING: currently fails on Egeria with a 500 'unknown TypeDef' (ISSUE-125). PLATFORM-WIDE: this changes the type system for every user and app, so Confirm Enum Def Name must repeat the name exactly or nothing is changed.

### Enum Def Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Name of the enum definition.


### Enum Def GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: GUID of the enum definition. If omitted, it is looked up from the Enum Def Name.


### Confirm Enum Def Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Required for Delete Enum Def: repeat Enum Def Name exactly (case-sensitive). Changing an enum definition affects every user and app on the platform.


___

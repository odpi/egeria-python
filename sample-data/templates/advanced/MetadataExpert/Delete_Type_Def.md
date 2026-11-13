___

## Delete Type Def
> Delete a type definition that was added through the API. Fails while instances of the type exist or another type refers to it. PLATFORM-WIDE: this changes the type system for every user and app, so Confirm Type Def Name must repeat the name exactly or nothing is changed.

### Type Def Name
>	**Input Required**: True

>	**Attribute Type**: Simple

>	**Description**: Name of the open metadata type definition (entity, relationship or classification).


### Type Def GUID
>	**Input Required**: False

>	**Attribute Type**: GUID

>	**Description**: GUID of the type definition. If omitted, it is looked up from the Type Def Name.


### Confirm Type Def Name
>	**Input Required**: False

>	**Attribute Type**: Simple

>	**Description**: Required for Update Type Def and Delete Type Def: repeat Type Def Name exactly (case-sensitive). Changing a type definition affects every user and app on the platform.


___

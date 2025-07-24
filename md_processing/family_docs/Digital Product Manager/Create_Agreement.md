# **Create Agreement**
>	A kind of collection that represents an Agreement. This is for generic agreements. Specific kinds of agreements have their own commands.

## **Display Name**
>	**Input Required**: True

>	**Description**: Name of the  agreement.

>	**Alternative Labels**: Name


## **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of the agreement.


## **Agreement Identifier**
>	**Input Required**: False

>	**Description**: A user specified agreement identifier.


## **Agreement Status**
>	**Input Required**: False

>	**Description**: The status of the agreement. There is a list of valid values that this conforms to.

>	**Alternative Labels**: Initial Status

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE'; DEPRECATED; OTHER

>	**Default Value**: DRAFT


## **User Defined Status**
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


## **Version Identifier**
>	**Input Required**: False

>	**Description**: Published agreement version identifier.


## **Agreement Actors**
>	**Input Required**: False

>	**Description**: A list of actors with responsibilities for the agreement.


## **Restrictions**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing restrictions.


## **Obligations**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing obligations.


## **Entitlements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing entitlements.


## **Usage Measurements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage measurements.


## **Product Metrics**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing metrics for the product/.


## **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


## **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


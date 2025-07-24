
# Family: Digital Product Manager

## **Add Member->Collection**
>	Add a member to a collection.
### **Element_Id**
>	**Input Required**: True

>	**Description**: The name of the element to add to the collection.

>	**Alternative Labels**: member_id


### **Collection Id**
>	**Input Required**: True

>	**Description**: The name of the collection to link to. There are many collection types, including Digital Products, Agreements and Subscriptions.

>	**Alternative Labels**: Collection Id; Agreement Id; Subscription Id; Digital Product Id


### **Membership Rationale**
>	**Input Required**: False

>	**Description**: Rationale for membership.

>	**Alternative Labels**: Rationale


### **Created By**
>	**Input Required**: False

>	**Description**: Who added the member. (currently informal string)


### **Membership Status**
>	**Input Required**: False

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE'; DEPRECATED; OTHER

>	**Default Value**: APPROVED


___

## **Attach Collection->Resource**
>	Connect an existing collection to an element using the ResourceList relationship.
### **Collection**
>	**Input Required**: True

>	**Description**: An element of base type collection (e.g. collection, agreement; subscription, ...)

>	**Alternative Labels**: Collection Id; Agreement Id; Subscription Id


### **Resource**
>	**Input Required**: True

>	**Description**: The name of the resource to attach to.


### **Resource Use**
>	**Input Required**: False

>	**Description**: Describes the relationship between the resource and the collection.


### **Resource Description**
>	**Input Required**: False

>	**Description**: A description of the resource being attached.

>	**Alternative Labels**: Description


### **Resource Use Properties**
>	**Input Required**: False

>	**Description**: A dictionary of name:value pairs describing properties of the resource use.


___

## **Create Agreement**
>	A kind of collection that represents an Agreement. This is for generic agreements. Specific kinds of agreements have their own commands.
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the  agreement.

>	**Alternative Labels**: Name


### **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of the agreement.


### **Agreement Identifier**
>	**Input Required**: False

>	**Description**: A user specified agreement identifier.


### **Agreement Status**
>	**Input Required**: False

>	**Description**: The status of the agreement. There is a list of valid values that this conforms to.

>	**Alternative Labels**: Initial Status

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE'; DEPRECATED; OTHER

>	**Default Value**: DRAFT


### **User Defined Status**
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


### **Version Identifier**
>	**Input Required**: False

>	**Description**: Published agreement version identifier.


### **Agreement Actors**
>	**Input Required**: False

>	**Description**: A list of actors with responsibilities for the agreement.


### **Restrictions**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing restrictions.


### **Obligations**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing obligations.


### **Entitlements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing entitlements.


### **Usage Measurements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage measurements.


### **Product Metrics**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing metrics for the product/.


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create Data Sharing Agreement**
>	Create a new collection with the DataSharingAgreement classification. 
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the  agreement.

>	**Alternative Labels**: Name


### **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of the agreement.


### **Identifier**
>	**Input Required**: False

>	**Description**: A user specified agreement identifier.


### **Agreement Status**
>	**Input Required**: False

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Alternative Labels**: Status

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE'; DEPRECATED; OTHER

>	**Default Value**: DRAFT


### **User_Defined_Status**
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


### **Version Identifier**
>	**Input Required**: False

>	**Description**: Published agreement version identifier.


### **Product Manager**
>	**Input Required**: False

>	**Description**: An actor responsible for managing this product. Actors may be individuals, automations, etc.


### **Digital Subscriptions**
>	**Input Required**: False

>	**Description**: 


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create Digital Product**
>	A Data Dictionary is an organized and curated collection of data definitions that can serve as a reference for data professionals
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the digital product

>	**Alternative Labels**: Name


### **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of a product.


### **Product Name**
>	**Input Required**: False

>	**Description**: The external name of the digital product.


### **Product Status**
>	**Input Required**: False

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; APPROVED_CONCEPT; UNDER_DEVELOPMENT; DEVELOPMENT_COMPLETE; APPROVED_FOR_DEPLOYMENT; ACTIVE; DISABLED; DEPRECATED; OTHER

>	**Default Value**: DRAFT


### **User Defined Status**
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


### **Product Type**
>	**Input Required**: False

>	**Description**: Type of product - periodic, delta, snapshot, etc


### **Product Identifier**
>	**Input Required**: False

>	**Description**: User specified product identifier.


### **Product Description**
>	**Input Required**: False

>	**Description**: Externally facing description of the product and its intended usage.


### **Maturity**
>	**Input Required**: False

>	**Description**: Product maturity - user defined.


### **Service Life**
>	**Input Required**: False

>	**Description**: Estimated service lifetime of the product.


### **Introduction Date**
>	**Input Required**: False

>	**Description**: Date of product introduction in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


### **Next Version Date**
>	**Input Required**: False

>	**Description**: Date of  the next version,  in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


### **Withdrawal Date**
>	**Input Required**: False

>	**Description**: Date of planned product withdrawal in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


### **Collection Type**
>	**Input Required**: False

>	**Description**: A user supplied collection type. Defaults to Digital Product.

>	**Default Value**: Digital Product


### **Current Version**
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0


### **Product Manager**
>	**Input Required**: False

>	**Description**: Actors responsible for managing this product. Actors may be individuals, automations, etc.


### **Agreements**
>	**Input Required**: False

>	**Description**: A list of agreements associated with this product.  The agreements must already exist.


### **Digital Subscriptions**
>	**Input Required**: False

>	**Description**: 


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create DigitalSubscription**
>	A type of agreement for a digital subscription.
### **Display Name**
>	**Input Required**: True

>	**Description**: Name of the  agreement.

>	**Alternative Labels**: Name


### **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of the agreement.


### **Identifier**
>	**Input Required**: False

>	**Description**: A user specified agreement identifier.


### **Product Status**
>	**Input Required**: False

>	**Description**: The status of the digital product. There is a list of valid values that this conforms to.

>	**Alternative Labels**: Initial Status

>	**Valid Values**: DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; ACTIVE'; DEPRECATED; OTHER

>	**Default Value**: DRAFT


### **User_Defined_Status**
>	**Input Required**: False

>	**Description**: Only valid if Product Status is set to OTHER. User defined & managed status values.


### **Support Level**
>	**Input Required**: False

>	**Description**: Level of support agreed or requested.


### **Service Levels**
>	**Input Required**: False

>	**Description**: A dictionary of name:value pairs describing the service levels.


### **Restrictions**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing restrictions.


### **Obligations**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing obligations.


### **Entitlements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing entitlements.


### **Usage Measurements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage measurements.


### **Product Metrics**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing metrics for the product/.


### **Version Identifier**
>	**Input Required**: False

>	**Description**: Published agreement version identifier.


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Link Agreement Items**
>	Attach or detach an agreement to an element referenced in its definition. Agreement item can be an referenced element.
### **Description**
>	**Input Required**: False

>	**Description**: Description of the contents of the agreement item.


### **Agreement Item Id**
>	**Input Required**: False

>	**Description**: A user specified agreement item identifier.


### **Agreement Start**
>	**Input Required**: False

>	**Description**: The start date of the agreement as an ISO 8601 string.

>	**Alternative Labels**: Start Date


### **Agreement End**
>	**Input Required**: False

>	**Description**: The end date of the agreement as an ISO 8601 string.

>	**Alternative Labels**: End Date


### **Restrictions**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing restrictions.


### **Obligations**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing obligations.


### **Entitlements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing entitlements.


### **Usage Measurements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage measurements.


### **Usage Metrics**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage metrics for the agreements.


___

## **Link Contracts**
>	Attach or detach an agreement to an element describing the location of the contract documents.
### **Contract Id**
>	**Input Required**: False

>	**Description**: Contract identifier.


### **Contract Liaison**
>	**Input Required**: False

>	**Description**: Name of the liaison for the contract.


### **Contract Liaison Type**
>	**Input Required**: False

>	**Description**: type of liaison.


### **Contract Liaison Property Name**
>	**Input Required**: False

>	**Description**: 


___

## **Link Digital Product - Digital Product**
>	Link digital product dependency between two digital products.
### **DigitalProduct1**
>	**Input Required**: True

>	**Description**: The  first product to link.

>	**Alternative Labels**: Product 1


### **DigitalProduct2**
>	**Input Required**: True

>	**Description**: The  second product to link.

>	**Alternative Labels**: Product 2


### **Label**
>	**Input Required**: False

>	**Description**: Labels the link between two digital products.


### **Description**
>	**Input Required**: False

>	**Description**: A description of the link.


___

## **Link Subscribers**
>	Attach or detach a subscriber to a subscription. Subscriber can be any type of element.
### **Subscriber Id**
>	**Input Required**: False

>	**Description**:  identifier of a subscriber. Initially, will let this be an arbitrary string - could harden this to a qualified name later if needed.


### **Agreement Start**
>	**Input Required**: False

>	**Description**: The start date of the agreement as an ISO 8601 string.

>	**Alternative Labels**: Start Date


### **Agreement End**
>	**Input Required**: False

>	**Description**: The end date of the agreement as an ISO 8601 string.

>	**Alternative Labels**: End Date


### **Restrictions**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing restrictions.


### **Obligations**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing obligations.


### **Entitlements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing entitlements.


### **Usage Measurements**
>	**Input Required**: False

>	**Description**: A dictionary of property:value pairs describing usage measurements.


___

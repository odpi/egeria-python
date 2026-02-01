# Don't Update Digital Product Catalog
>	Create or update a Digital Product Catalog. 

## Display Name
>	**Input Required**: True

>	**Description**: Name of a catalog of digital products.

>	**Alternative Labels**: Name; Catalog Name; Marketplace

Sales Forecast Advisor Products

## Description
>	**Input Required**: False

>	**Description**: Description of the contents of a product catalog.

This is product catalog contains products derived for the Sales Forecast Advisor project.


## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name
AI


## Journal Entry
>	**Input Required**: False

>	**Description**: 
This is a product catalog for the Sales Forecast Advisor project.



## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element

SalesForecastAdvisor, AI

____

# Don't Update Digital Product
>	A Digital Product represents artifacts that can be subscribed to and consumed by users.

## Display Name
>	**Input Required**: True

>	**Description**: Name of the digital product

>	**Alternative Labels**: Name

Sales Regions

## Description
>	**Input Required**: False

>	**Description**: Description of the contents of a product.

This product contains the information about sales regions. Past, Present, Future.

## Product Name
>	**Input Required**: False

>	**Description**: The external name of the digital product.

Sales Regions for Sales Forecast Advisor

## Identifier
>	**Input Required**: False

>	**Description**: User specified product identifier.

SFA-Sales-Regions
## Maturity
>	**Input Required**: False

>	**Description**: Product maturity - user defined.
Evolving

## Service Life
>	**Input Required**: False

>	**Description**: Estimated service lifetime of the product.


## Introduction Date
>	**Input Required**: False

>	**Description**: Date of product introduction in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


## Next Version Date
>	**Input Required**: False

>	**Description**: Date of  the next version,  in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


## Withdrawal Date
>	**Input Required**: False

>	**Description**: Date of planned product withdrawal in ISO 8601 format. Either all of the dates (introduction, next version, withdrawal) dates need to be supplied or none of them. Otherwise an error will occur.


## Product Manager
>	**Input Required**: False

>	**Description**: Actors responsible for managing this product. Actors may be individuals, automations, etc.
Harry Hopeful

## Agreements
>	**Input Required**: False

>	**Description**: A list of agreements associated with this product.  The agreements must already exist.


## Digital Subscriptions
>	**Input Required**: False

>	**Description**: 



## Category
>	**Input Required**: False

>	**Description**: A user specified category name that can be used for example, to define product types or agreement types.

>	**Alternative Labels**: Category Name
AI

## Version Identifier
>	**Input Required**: False

>	**Description**: Published product version identifier.

>	**Default Value**: 1.0
0.1


## Journal Entry
>	**Input Required**: False

>	**Description**: 
This product contains information about sales regions. It will continue to evolve as more information is collected from the different organizations around the world.


## Search Keywords
>	**Input Required**: False

>	**Description**: Keywords to facilitate finding the element

Sales Regions, Sales Territories

____

# Add Member->Collection
>	Add/Remove a member to/from a collection.

## Element Id
>	**Input Required**: True

>	**Description**: The name of the element to add to the collection.

>	**Alternative Labels**: Member; Member Id
myLocal::DigitalProduct::Sales-Regions::0.1

## Collection Id
>	**Input Required**: True

>	**Description**: The name of the collection to link to. There are many collection types, including Digital Products, Agreements and Subscriptions.

>	**Alternative Labels**: Parent; Parent Id; Collection Id; Agreement Id; Subscription Id; Digital Product Id; Folder; Folder Id
myLocal::DigProdCatalog::Sales-Forecast-Advisor-Products 

## Membership Rationale
>	**Input Required**: False

>	**Description**: Rationale for membership.

>	**Alternative Labels**: Rationale
Asserted Definition 

## Expression

## Confidence
100

## Notes


## Membership Status
>	**Input Required**: False

>	**Description**: The status of adding a member to a collection.

>	**Valid Values**: UNKNOWN; DISCOVERED; PROPOSED; IMPORTED; VALIDATED; DEPRECATED; OBSOLETE; OTHER

>	**Default Value**: VALIDATED

Validated
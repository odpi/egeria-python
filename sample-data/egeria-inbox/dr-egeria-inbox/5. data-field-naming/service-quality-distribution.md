This file creates the **Distribution** subject area folder (`ServiceQuality:Distribution`) and its
Prime Words / Modifiers / Class Words sub-folders in the Data Field Naming glossary, along with any terms
specific to this subject area. It also links the folder as a member of the existing `SubjectArea::ServiceQuality:Distribution`
governance collection (see `CocoSubjectAreaDefinition.java`), so the two structures are connected.

Requires `glossary.md` and `service-quality.md` to have been processed
first, and requires the `SubjectArea::ServiceQuality:Distribution` collection to already exist in Egeria.

____

## Create Collection Folder

### Display Name

Distribution

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution

### Purpose

Groups the data field naming terms (prime words, modifiers, class words) for the Distribution subject area. Information relating to the Coco Pharmaceuticals distribution of treatments.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality

### Parent Relationship Type Name

CollectionMembership

___

## Add Member to Collection
> Add/Remove a member to/from a collection.

### Element Id

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution

### Membership Rationale

Link the Distribution subject area to its data field naming vocabulary.

### Membership Status

VALIDATED

### Collection Id

SubjectArea::ServiceQuality:Distribution

___

## Create Collection Folder

### Display Name

Prime Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:PrimeWords

### Purpose

Prime words - the core business nouns - used to build data field names for the Distribution subject area.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Modifiers

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:Modifiers

### Purpose

Modifiers specific to the Distribution subject area, used to qualify a prime word or class word when building data field names.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution

### Parent Relationship Type Name

CollectionMembership

___

## Create Collection Folder

### Display Name

Class Words

### Qualified Name

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:ClassWords

### Purpose

Class words specific to the Distribution subject area, used as the trailing element of a data field name.

### Parent ID

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution

### Parent Relationship Type Name

CollectionMembership

___

# Distribution

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Distribution

### Aliases

- Logistics
- Fulfillment

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The process of moving products from Coco Pharmaceuticals to its customers.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Distribution

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Shipment

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Shipment

### Aliases

- Consignment
- Delivery

### Glossary Name

- Glossary::DataFieldNaming

### Summary

A consignment of products dispatched together to a destination.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Shipment

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Carrier

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Carrier

### Aliases

- Courier
- Freight Forwarder
- Haulier

### Glossary Name

- Glossary::DataFieldNaming

### Summary

The organization responsible for transporting a shipment to its destination.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:PrimeWords

### Qualified Name

GlossaryTerm::DataFieldNaming::Carrier

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Dispatch

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Dispatch

### Aliases

- Despatch
- Outbound

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a shipment leaves Coco Pharmaceuticals' premises, e.g. `ShipmentDispatchDate`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Dispatch

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# Delivery

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

Delivery

### Aliases

- Inbound
- Drop-off

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the point at which a shipment arrives at its destination, e.g. `ShipmentDeliveryDate`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::Delivery

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# ShipTo

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

ShipTo

### Aliases

- Ship-To
- Destination
- Consignee

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the destination address of a shipment, e.g. `ShipToAddress`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::ShipTo

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

# ShipFrom

## Create Glossary Term
> Creates or updates a glossary term - a concept, phrase, or word defined within a glossary.

### Display Name

ShipFrom

### Aliases

- Ship-From
- Origin
- Consignor

### Glossary Name

- Glossary::DataFieldNaming

### Summary

Relating to the origin address of a shipment, e.g. `ShipFromAddress`.

### Folders

CollectionFolder::DataFieldNaming:ServiceQuality:Distribution:Modifiers

### Qualified Name

GlossaryTerm::DataFieldNaming::ShipFrom

### Content Status

ACTIVE

### Version Identifier

1.0

### Authors

- Erin Overview
- Peter Profile

___

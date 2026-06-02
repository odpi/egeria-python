###
# @name get Exceptions
# Retrieve the element, extract the guid and then request the data set report.
#
POST {{baseURL}}/servers/{{viewServer}}/api/open-metadata/asset-maker/assets/by-name
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "class" : "FilterRequestBody",
  "metadataElementTypeName": "TabularDataSet",
  "filter" : "Data set for Exceptions",
  "startFrom" : 0,
  "pageSize": 10
}

> {% client.global.set("exceptionsDataSetGUID", response.body.elements[0].elementHeader.guid); %}

###

GET {{baseURL}}/servers/{{viewServer}}/api/open-metadata/data-engineer/tabular-data-sets/{{exceptionsDataSetGUID}}/report?startFromRow=0&maxRowCount=5000
Authorization: Bearer {{token}}
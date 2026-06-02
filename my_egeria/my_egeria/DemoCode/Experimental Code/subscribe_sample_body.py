###
# @name initiateGovernanceActionProcess (Create Subscription)
# Using the named governance action process as a template, initiate a chain of engine actions.

# POST {{baseURL}}/servers/{{viewServer}}/api/open-metadata/automated-curation/governance-action-processes/initiate
# Authorization: Bearer {{token}}
# Content-Type: application/json

body = {
  "processQualifiedName": "{{createSubscriptionQualifiedName}}",
  "actionTargets": [{
              "class" : "NewActionTarget",
              "actionTargetName": "destinationDataSet",
              "actionTargetGUID": "{{csvFileGUID}}"
            },
            {
              "class" : "NewActionTarget",
              "actionTargetGUID": "{{callieQuartileGUID}}",
              "actionTargetName": "digitalSubscriptionRequester"
            }]
}


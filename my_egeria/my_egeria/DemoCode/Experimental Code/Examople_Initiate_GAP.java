###
# @name initiateGovernanceActionProcess (Create Subscription)
# Using the named governance action process as a template, initiate a chain of engine actions.

POST {{baseURL}}/servers/{{viewServer}}/api/open-metadata/automated-curation/governance-action-processes/initiate
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "processQualifiedName": "GovernanceActionProcess::Valid Value Sets List::Create Subscription::EVALUATION-SUBSCRIPTION"
}

###
# Full request body for initiate governance action process
# {
#   "class" : "InitiateGovernanceActionProcessRequestBody",
#   "processQualifiedName": "",
#   "requestParameters": {
#       "parameterName1" : "parameterValue1",
#       "parameterName2" : "parameterValue2"
#   },
#   "requestSourceGUIDs": [ "" ],
#   "actionTargets": [
#     {
#       "class" : "NewActionTarget",
#       "actionTargetName" : "",
#       "actionTargetGUID" : ""
#     } ],
#   "startDate": "",
#   "originatorServiceName": "",
#   "originatorEngineName": ""
# }
#general
body = {
"governanceActionProcesses": [
    {
      "displayName": "Catalog Resource",
      "description": "Create a Databricks Unity Catalog Server and configure an integration connector to catalog its contents.",
      "additionalProperties": {
        "templateGUID": "3f7f62f6-4abc-424e-9f92-523306e7d5d5"
      },
      "specification": {
        "supportedRequestParameter": [
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "portNumber",
            "description": "The number of the port to use to connect to a service.",
            "dataType": "string",
            "example": "1234",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "hostURL",
            "description": "The host IP address or domain name of the server with the HTTP protocol prefix.",
            "dataType": "string",
            "example": "https://coconet.com",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "secretsStorePathName",
            "description": "The full path name to the secrets store file where the secrets collection for this server is located.",
            "dataType": "string",
            "example": "secrets/integration.omsecrets",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "secretsCollectionName",
            "description": "The name used to identify the collection of secrets that a particular connector is using.",
            "dataType": "string",
            "example": "local-postgres-db",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "serverName",
            "description": "The name of the server being catalogued.",
            "dataType": "string",
            "example": "myServer",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "description",
            "description": "The description of the element to help a consumer understand its content and purpose.",
            "dataType": "string",
            "example": "This file contains a week''s worth of patient data for the Teddy Bear Drop Foot clinical trial.",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "versionIdentifier",
            "description": "The string version identifier for the element.  This is typically of the form Vx.y.z where x is the major version number, y is the minor version number, and z is an option patch identifier.",
            "dataType": "string",
            "example": "6.1-SNAPSHOT",
            "required": false
          }
        ]
      },
      "specificationMermaidGraph": "---\ntitle: Specification for - DatabricksUnityCatalogServer::CreateAsCatalogTarget [8b961a03-bb78-44c5-9863-f2719a2d895d]\n---\nflowchart LR\n%%{init: {\"flowchart\": {\"htmlLabels\": false}} }%%\n\n1@{ shape: processes, label: \"*Governance Action Process*\n**DatabricksUnityCatalogServer::CreateAsCatalogTarget**\"}\n2@{ shape: hex, label: \"*Specification Property Assignment*\n**supportedRequestParameter**\"}\n1==>2\n3@{ shape: hex, label: \"*Specification Property Value*\n**portNumber**\"}\n2==>3\nsubgraph 4 [portNumber details]\n5@{ shape: text, label: \"*description:*\n**The number of the port to use to connect to a service.**\"}\n6@{ shape: text, label: \"*data Type:*\n**string**\"}\n7@{ shape: text, label: \"*example:*\n**1234**\"}\n8@{ shape: text, label: \"*required:*\n**false**\"}\nend\n3==>4\n9@{ shape: hex, label: \"*Specification Property Value*\n**hostURL**\"}\n2==>9\nsubgraph 10 [hostURL details]\n11@{ shape: text, label: \"*description:*\n**The host IP address or domain name of the server with the HTTP protocol prefix.**\"}\n12@{ shape: text, label: \"*data Type:*\n**string**\"}\n13@{ shape: text, label: \"*example:*\n**https:/ /coconet.com**\"}\n14@{ shape: text, label: \"*required:*\n**false**\"}\nend\n9==>10\n15@{ shape: hex, label: \"*Specification Property Value*\n**secretsStorePathName**\"}\n2==>15\nsubgraph 16 [secretsStorePathName details]\n17@{ shape: text, label: \"*description:*\n**The full path name to the secrets store file where the secrets collection for this server is located.**\"}\n18@{ shape: text, label: \"*data Type:*\n**string**\"}\n19@{ shape: text, label: \"*example:*\n**secrets/integration.omsecrets**\"}\n20@{ shape: text, label: \"*required:*\n**false**\"}\nend\n15==>16\n21@{ shape: hex, label: \"*Specification Property Value*\n**secretsCollectionName**\"}\n2==>21\nsubgraph 22 [secretsCollectionName details]\n23@{ shape: text, label: \"*description:*\n**The name used to identify the collection of secrets that a particular connector is using.**\"}\n24@{ shape: text, label: \"*data Type:*\n**string**\"}\n25@{ shape: text, label: \"*example:*\n**local-postgres-db**\"}\n26@{ shape: text, label: \"*required:*\n**false**\"}\nend\n21==>22\n27@{ shape: hex, label: \"*Specification Property Value*\n**serverName**\"}\n2==>27\nsubgraph 28 [serverName details]\n29@{ shape: text, label: \"*description:*\n**The name of the server being catalogued.**\"}\n30@{ shape: text, label: \"*data Type:*\n**string**\"}\n31@{ shape: text, label: \"*example:*\n**myServer**\"}\n32@{ shape: text, label: \"*required:*\n**false**\"}\nend\n27==>28\n33@{ shape: hex, label: \"*Specification Property Value*\n**description**\"}\n2==>33\nsubgraph 34 [description details]\n35@{ shape: text, label: \"*description:*\n**The description of the element to help a consumer understand its content and purpose.**\"}\n36@{ shape: text, label: \"*data Type:*\n**string**\"}\n37@{ shape: text, label: \"*example:*\n**This file contains a week''s worth of patient data for the Teddy Bear Drop Foot clinical trial.**\"}\n38@{ shape: text, label: \"*required:*\n**false**\"}\nend\n33==>34\n39@{ shape: hex, label: \"*Specification Property Value*\n**versionIdentifier**\"}\n2==>39\nsubgraph 40 [versionIdentifier details]\n41@{ shape: text, label: \"*description:*\n**The string version identifier for the element.  This is typically of the form Vx.y.z where x is the major version number, y is the minor version number, and z is an option patch identifier.**\"}\n42@{ shape: text, label: \"*data Type:*\n**string**\"}\n43@{ shape: text, label: \"*example:*\n**6.1-SNAPSHOT**\"}\n44@{ shape: text, label: \"*required:*\n**false**\"}\nend\n39==>40\nstyle 22 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 44 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 23 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 24 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 25 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 26 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 27 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 28 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 29 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 30 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 31 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 10 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 32 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 11 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 33 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 12 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 34 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 13 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 35 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 14 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 36 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 15 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 37 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 16 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 38 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 17 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 39 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 18 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 19 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 1 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 2 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 3 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 4 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 5 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 6 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 7 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 8 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 9 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 40 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 41 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 20 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 42 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 21 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 43 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\n",
      "relatedElement": {
        "elementHeader": {
          "class": "ElementHeader",
          "headerVersion": 0,
          "status": "ACTIVE",
          "type": {
            "typeId": "4d3a2b8d-9e2e-4832-b338-21c74e45b238",
            "typeName": "GovernanceActionProcess",
            "superTypeNames": [
              "GovernanceAction",
              "GovernanceControl",
              "GovernanceDefinition",
              "AuthoredReferenceable",
              "Referenceable",
              "OpenMetadataRoot"
            ],
            "typeVersion": 1,
            "typeDescription": "A process implemented by chained engine actions that call governance services.",
            "typeCategory": "ENTITY_DEF"
          },
          "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "CONTENT_PACK",
            "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
            "homeMetadataCollectionName": "UnityCatalogContentPack",
            "license": "Apache 2.0"
          },
          "versions": {
            "createdBy": "Egeria Project",
            "updatedBy": "Egeria Project",
            "maintainedBy": [
              "Egeria Project"
            ],
            "createTime": "2026-04-23T14:20:40.309+00:00",
            "updateTime": "2026-04-23T14:20:40.309+00:00",
            "version": 1776954043523
          },
          "guid": "8b961a03-bb78-44c5-9863-f2719a2d895d",
          "anchor": {
            "class": "ElementClassification",
            "headerVersion": 0,
            "status": "ACTIVE",
            "type": {
              "typeId": "aa44f302-2e43-4669-a1e7-edaae414fc6e",
              "typeName": "Anchors",
              "typeVersion": 1,
              "typeDescription": "Identifies the anchor entity for an element that is part of a large composite object such as an asset.",
              "typeCategory": "CLASSIFICATION_DEF"
            },
            "origin": {
              "sourceServer": "qs-metadata-store",
              "originCategory": "CONTENT_PACK",
              "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
              "homeMetadataCollectionName": "UnityCatalogContentPack"
            },
            "versions": {
              "createdBy": "Egeria Project",
              "updatedBy": "Egeria Project",
              "maintainedBy": [
                "Egeria Project"
              ],
              "createTime": "2026-04-23T14:20:40.309+00:00",
              "updateTime": "2026-04-23T14:20:40.309+00:00",
              "version": 1776954043523
            },
            "classificationOrigin": "ASSIGNED",
            "classificationName": "Anchors",
            "classificationProperties": {
              "class": "AnchorsProperties",
              "typeName": "Anchors",
              "anchorGUID": "8b961a03-bb78-44c5-9863-f2719a2d895d",
              "anchorTypeName": "GovernanceActionProcess",
              "anchorDomainName": "Asset"
            }
          }
        },
        "properties": {
          "class": "GovernanceActionProcessProperties",
          "typeName": "GovernanceActionProcess",
          "qualifiedName": "DatabricksUnityCatalogServer::CreateAsCatalogTargetGovernanceActionProcess",
          "displayName": "DatabricksUnityCatalogServer::CreateAsCatalogTarget",
          "description": "Create a Databricks Unity Catalog Server and configure an integration connector to catalog its contents.",
          "url": "https://egeria-project.org/egeria-solutions/leveraging-unity-catalog/overview/",
          "domainIdentifier": 0
        }
      },
      "resourceUse": "Catalog Resource"
    },
    {
      "displayName": "Survey Resource",
      "description": "Create a Databricks Unity Catalog Server, run a survey against it, and print out the resulting report.",
      "additionalProperties": {
        "templateGUID": "3f7f62f6-4abc-424e-9f92-523306e7d5d5"
      },
      "specification": {
        "producedAnnotationType": [
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Schemas",
            "description": "Extract the list of visible schema in the surveyed resource.",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Schemas listed include their catalog name and schema name.  If schemas are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Log of Unity Catalog (UC) Resources",
            "description": "Log file of resource name, description and deployed implementation type.",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Produce Inventory",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "If resource are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Analytical Models",
            "description": "Extract the list of visible analytical models in the surveyed resource (manager).",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Models are listed by their full name, with respect to the resource manager.  If models are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Table Columns",
            "description": "Extract the list of visible columns within the tables in the surveyed resource.",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Tables listed include their catalog name, schema name and table name.  If tables are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of File Volumes",
            "description": "Extract the list of visible file-based volumes in the surveyed resource (manager).",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Volumes are listed by their full name, with respect to the resource manager.  If volumes are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Executable Functions",
            "description": "Extract the list of visible functions in the surveyed resource (manager).",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Functions are listed by their full name, with respect to the resource manager.  If functions are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Unity Catalog (UC) Catalogs",
            "description": "Extract the list of visible catalogs in a Unity Catalog (UC) server.",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "If catalogs are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture List of Tables",
            "description": "Extract the list of visible tables in the surveyed Unity Catalog (UC) resource (server, catalog or schema).",
            "otherPropertyValues": {
              "typeName": "ResourceProfileAnnotation"
            },
            "analysisStepName": "Profiling Associated Resources",
            "openMetadataTypeName": "ResourceProfileAnnotation",
            "explanation": "Tables listed include their catalog name, schema name and table name.  If tables are missing, check the security permissions of the survey service''s userId."
          },
          {
            "class": "ProducedAnnotationType",
            "specificationPropertyType": "PRODUCED_ANNOTATION_TYPE",
            "name": "Capture Unity Catalog (UC) Server Metrics",
            "description": "Capture summary statistics about a database.",
            "otherPropertyValues": {
              "Number of Functions": "Number of functions found in the surveyed resource.",
              "Number of Catalogs": "Number of catalogs defined in this server.",
              "Number of Models": "Number of models found in the surveyed resource.",
              "Number of Volumes": "Number of volumes found in the surveyed resource.",
              "typeName": "ResourceMeasureAnnotation"
            },
            "analysisStepName": "Measure Resource",
            "openMetadataTypeName": "ResourceMeasureAnnotation",
            "explanation": "This annotation retrieves statistics about a Unity Catalog (UC) server and its contents."
          }
        ],
        "supportedRequestParameter": [
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "description",
            "description": "The description of the element to help a consumer understand its content and purpose.",
            "dataType": "string",
            "example": "This file contains a week''s worth of patient data for the Teddy Bear Drop Foot clinical trial.",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "secretsStorePathName",
            "description": "The full path name to the secrets store file where the secrets collection for this server is located.",
            "dataType": "string",
            "example": "secrets/integration.omsecrets",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "versionIdentifier",
            "description": "The string version identifier for the element.  This is typically of the form Vx.y.z where x is the major version number, y is the minor version number, and z is an option patch identifier.",
            "dataType": "string",
            "example": "6.1-SNAPSHOT",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "serverName",
            "description": "The name of the server being catalogued.",
            "dataType": "string",
            "example": "myServer",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "portNumber",
            "description": "The number of the port to use to connect to a service.",
            "dataType": "string",
            "example": "1234",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "secretsCollectionName",
            "description": "The name used to identify the collection of secrets that a particular connector is using.",
            "dataType": "string",
            "example": "local-postgres-db",
            "required": false
          },
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "hostURL",
            "description": "The host IP address or domain name of the server with the HTTP protocol prefix.",
            "dataType": "string",
            "example": "https://coconet.com",
            "required": false
          }
        ],
        "supportedAnalysisStep": [
          {
            "class": "SupportedAnalysisStep",
            "specificationPropertyType": "SUPPORTED_ANALYSIS_STEP",
            "name": "Produce Inventory",
            "description": "The survey action service is writing an inventory of the contents of the surveyed resource."
          },
          {
            "class": "SupportedAnalysisStep",
            "specificationPropertyType": "SUPPORTED_ANALYSIS_STEP",
            "name": "Profiling Associated Resources",
            "description": "The survey action service is profiling other resources associated with the surveyed resource."
          },
          {
            "class": "SupportedAnalysisStep",
            "specificationPropertyType": "SUPPORTED_ANALYSIS_STEP",
            "name": "Measure Resource",
            "description": "The survey action service is taking measurements from the resource."
          },
          {
            "class": "SupportedAnalysisStep",
            "specificationPropertyType": "SUPPORTED_ANALYSIS_STEP",
            "name": "Check Asset",
            "description": "The survey action service is checking that the asset is of the correct type and the connection defines the correct type of connector."
          }
        ]
      },
      "specificationMermaidGraph": "---\ntitle: Specification for - DatabricksUnityCatalogServer:CreateAndSurvey [4cc5bde4-2455-437a-aba8-fb1514faac75]\n---\nflowchart LR\n%%{init: {\"flowchart\": {\"htmlLabels\": false}} }%%\n\n1@{ shape: processes, label: \"*Governance Action Process*\n**DatabricksUnityCatalogServer:CreateAndSurvey**\"}\n2@{ shape: hex, label: \"*Specification Property Assignment*\n**producedAnnotationType**\"}\n1==>2\n3@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Schemas**\"}\n2==>3\nsubgraph 4 [Capture List of Schemas details]\n5@{ shape: text, label: \"*description:*\n**Extract the list of visible schema in the surveyed resource.**\"}\n6@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n7@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n8@{ shape: text, label: \"*explanation*\n**Schemas listed include their catalog name and schema name.  If schemas are missing, check the security permissions of the survey service''s userId.**\"}\n9@{ shape: text, label: \"*expression:*\n\"}\n10@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n3==>4\n11@{ shape: hex, label: \"*Specification Property Value*\n**Log of Unity Catalog (UC) Resources**\"}\n2==>11\nsubgraph 12 [Log of Unity Catalog (UC) Resources details]\n13@{ shape: text, label: \"*description:*\n**Log file of resource name, description and deployed implementation type.**\"}\n14@{ shape: text, label: \"*analysis Step:*\n**Produce Inventory**\"}\n15@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n16@{ shape: text, label: \"*explanation*\n**If resource are missing, check the security permissions of the survey service''s userId.**\"}\n17@{ shape: text, label: \"*expression:*\n\"}\n18@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n11==>12\n19@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Analytical Models**\"}\n2==>19\nsubgraph 20 [Capture List of Analytical Models details]\n21@{ shape: text, label: \"*description:*\n**Extract the list of visible analytical models in the surveyed resource (manager).**\"}\n22@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n23@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n24@{ shape: text, label: \"*explanation*\n**Models are listed by their full name, with respect to the resource manager.  If models are missing, check the security permissions of the survey service''s userId.**\"}\n25@{ shape: text, label: \"*expression:*\n\"}\n26@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n19==>20\n27@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Table Columns**\"}\n2==>27\nsubgraph 28 [Capture List of Table Columns details]\n29@{ shape: text, label: \"*description:*\n**Extract the list of visible columns within the tables in the surveyed resource.**\"}\n30@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n31@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n32@{ shape: text, label: \"*explanation*\n**Tables listed include their catalog name, schema name and table name.  If tables are missing, check the security permissions of the survey service''s userId.**\"}\n33@{ shape: text, label: \"*expression:*\n\"}\n34@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n27==>28\n35@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of File Volumes**\"}\n2==>35\nsubgraph 36 [Capture List of File Volumes details]\n37@{ shape: text, label: \"*description:*\n**Extract the list of visible file-based volumes in the surveyed resource (manager).**\"}\n38@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n39@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n40@{ shape: text, label: \"*explanation*\n**Volumes are listed by their full name, with respect to the resource manager.  If volumes are missing, check the security permissions of the survey service''s userId.**\"}\n41@{ shape: text, label: \"*expression:*\n\"}\n42@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n35==>36\n43@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Executable Functions**\"}\n2==>43\nsubgraph 44 [Capture List of Executable Functions details]\n45@{ shape: text, label: \"*description:*\n**Extract the list of visible functions in the surveyed resource (manager).**\"}\n46@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n47@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n48@{ shape: text, label: \"*explanation*\n**Functions are listed by their full name, with respect to the resource manager.  If functions are missing, check the security permissions of the survey service''s userId.**\"}\n49@{ shape: text, label: \"*expression:*\n\"}\n50@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n43==>44\n51@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Unity Catalog (UC) Catalogs**\"}\n2==>51\nsubgraph 52 [Capture List of Unity Catalog (UC) Catalogs details]\n53@{ shape: text, label: \"*description:*\n**Extract the list of visible catalogs in a Unity Catalog (UC) server.**\"}\n54@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n55@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n56@{ shape: text, label: \"*explanation*\n**If catalogs are missing, check the security permissions of the survey service''s userId.**\"}\n57@{ shape: text, label: \"*expression:*\n\"}\n58@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n51==>52\n59@{ shape: hex, label: \"*Specification Property Value*\n**Capture List of Tables**\"}\n2==>59\nsubgraph 60 [Capture List of Tables details]\n61@{ shape: text, label: \"*description:*\n**Extract the list of visible tables in the surveyed Unity Catalog (UC) resource (server, catalog or schema).**\"}\n62@{ shape: text, label: \"*analysis Step:*\n**Profiling Associated Resources**\"}\n63@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\n64@{ shape: text, label: \"*explanation*\n**Tables listed include their catalog name, schema name and table name.  If tables are missing, check the security permissions of the survey service''s userId.**\"}\n65@{ shape: text, label: \"*expression:*\n\"}\n66@{ shape: text, label: \"*type Name:*\n**ResourceProfileAnnotation**\"}\nend\n59==>60\n67@{ shape: hex, label: \"*Specification Property Value*\n**Capture Unity Catalog (UC) Server Metrics**\"}\n2==>67\nsubgraph 68 [Capture Unity Catalog (UC) Server Metrics details]\n69@{ shape: text, label: \"*description:*\n**Capture summary statistics about a database.**\"}\n70@{ shape: text, label: \"*analysis Step:*\n**Measure Resource**\"}\n71@{ shape: text, label: \"*type Name:*\n**ResourceMeasureAnnotation**\"}\n72@{ shape: text, label: \"*explanation*\n**This annotation retrieves statistics about a Unity Catalog (UC) server and its contents.**\"}\n73@{ shape: text, label: \"*expression:*\n\"}\n74@{ shape: text, label: \"*Number of  Functions:*\n**Number of functions found in the surveyed resource.**\"}\n75@{ shape: text, label: \"*Number of  Catalogs:*\n**Number of catalogs defined in this server.**\"}\n76@{ shape: text, label: \"*Number of  Models:*\n**Number of models found in the surveyed resource.**\"}\n77@{ shape: text, label: \"*Number of  Volumes:*\n**Number of volumes found in the surveyed resource.**\"}\n78@{ shape: text, label: \"*type Name:*\n**ResourceMeasureAnnotation**\"}\nend\n67==>68\n79@{ shape: hex, label: \"*Specification Property Assignment*\n**supportedRequestParameter**\"}\n1==>79\n80@{ shape: hex, label: \"*Specification Property Value*\n**description**\"}\n79==>80\nsubgraph 81 [description details]\n82@{ shape: text, label: \"*description:*\n**The description of the element to help a consumer understand its content and purpose.**\"}\n83@{ shape: text, label: \"*data Type:*\n**string**\"}\n84@{ shape: text, label: \"*example:*\n**This file contains a week''s worth of patient data for the Teddy Bear Drop Foot clinical trial.**\"}\n85@{ shape: text, label: \"*required:*\n**false**\"}\nend\n80==>81\n86@{ shape: hex, label: \"*Specification Property Value*\n**secretsStorePathName**\"}\n79==>86\nsubgraph 87 [secretsStorePathName details]\n88@{ shape: text, label: \"*description:*\n**The full path name to the secrets store file where the secrets collection for this server is located.**\"}\n89@{ shape: text, label: \"*data Type:*\n**string**\"}\n90@{ shape: text, label: \"*example:*\n**secrets/integration.omsecrets**\"}\n91@{ shape: text, label: \"*required:*\n**false**\"}\nend\n86==>87\n92@{ shape: hex, label: \"*Specification Property Value*\n**versionIdentifier**\"}\n79==>92\nsubgraph 93 [versionIdentifier details]\n94@{ shape: text, label: \"*description:*\n**The string version identifier for the element.  This is typically of the form Vx.y.z where x is the major version number, y is the minor version number, and z is an option patch identifier.**\"}\n95@{ shape: text, label: \"*data Type:*\n**string**\"}\n96@{ shape: text, label: \"*example:*\n**6.1-SNAPSHOT**\"}\n97@{ shape: text, label: \"*required:*\n**false**\"}\nend\n92==>93\n98@{ shape: hex, label: \"*Specification Property Value*\n**serverName**\"}\n79==>98\nsubgraph 99 [serverName details]\n100@{ shape: text, label: \"*description:*\n**The name of the server being catalogued.**\"}\n101@{ shape: text, label: \"*data Type:*\n**string**\"}\n102@{ shape: text, label: \"*example:*\n**myServer**\"}\n103@{ shape: text, label: \"*required:*\n**false**\"}\nend\n98==>99\n104@{ shape: hex, label: \"*Specification Property Value*\n**portNumber**\"}\n79==>104\nsubgraph 105 [portNumber details]\n106@{ shape: text, label: \"*description:*\n**The number of the port to use to connect to a service.**\"}\n107@{ shape: text, label: \"*data Type:*\n**string**\"}\n108@{ shape: text, label: \"*example:*\n**1234**\"}\n109@{ shape: text, label: \"*required:*\n**false**\"}\nend\n104==>105\n110@{ shape: hex, label: \"*Specification Property Value*\n**secretsCollectionName**\"}\n79==>110\nsubgraph 111 [secretsCollectionName details]\n112@{ shape: text, label: \"*description:*\n**The name used to identify the collection of secrets that a particular connector is using.**\"}\n113@{ shape: text, label: \"*data Type:*\n**string**\"}\n114@{ shape: text, label: \"*example:*\n**local-postgres-db**\"}\n115@{ shape: text, label: \"*required:*\n**false**\"}\nend\n110==>111\n116@{ shape: hex, label: \"*Specification Property Value*\n**hostURL**\"}\n79==>116\nsubgraph 117 [hostURL details]\n118@{ shape: text, label: \"*description:*\n**The host IP address or domain name of the server with the HTTP protocol prefix.**\"}\n119@{ shape: text, label: \"*data Type:*\n**string**\"}\n120@{ shape: text, label: \"*example:*\n**https:/ /coconet.com**\"}\n121@{ shape: text, label: \"*required:*\n**false**\"}\nend\n116==>117\n122@{ shape: hex, label: \"*Specification Property Assignment*\n**supportedAnalysisStep**\"}\n1==>122\n123@{ shape: hex, label: \"*Specification Property Value*\n**Produce Inventory**\"}\n122==>123\nsubgraph 124 [Produce Inventory details]\n125@{ shape: text, label: \"*description:*\n**The survey action service is writing an inventory of the contents of the surveyed resource.**\"}\nend\n123==>124\n126@{ shape: hex, label: \"*Specification Property Value*\n**Profiling Associated Resources**\"}\n122==>126\nsubgraph 127 [Profiling Associated Resources details]\n128@{ shape: text, label: \"*description:*\n**The survey action service is profiling other resources associated with the surveyed resource.**\"}\nend\n126==>127\n129@{ shape: hex, label: \"*Specification Property Value*\n**Measure Resource**\"}\n122==>129\nsubgraph 130 [Measure Resource details]\n131@{ shape: text, label: \"*description:*\n**The survey action service is taking measurements from the resource.**\"}\nend\n129==>130\n132@{ shape: hex, label: \"*Specification Property Value*\n**Check Asset**\"}\n122==>132\nsubgraph 133 [Check Asset details]\n134@{ shape: text, label: \"*description:*\n**The survey action service is checking that the asset is of the correct type and the connection defines the correct type of connector.**\"}\nend\n132==>133\nstyle 88 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 89 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 110 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 111 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 112 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 113 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 114 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 115 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 116 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 90 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 117 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 91 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 118 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 92 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 119 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 93 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 94 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 95 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 96 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 97 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 10 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 98 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 11 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 99 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 12 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 13 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 14 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 15 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 16 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 17 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 18 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 19 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 120 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 121 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 1 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 122 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 2 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 123 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 3 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 124 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 4 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 125 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 5 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 126 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 6 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 127 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 7 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 128 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 8 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 129 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 9 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 20 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 21 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 22 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 23 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 24 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 25 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 26 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 27 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 28 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 29 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 130 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 131 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 132 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 133 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 134 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 30 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 31 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 32 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 33 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 34 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 35 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 36 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 37 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 38 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 39 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 40 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 41 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 42 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 43 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 44 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 45 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 46 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 47 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 48 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 49 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 50 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 51 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 52 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 53 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 54 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 55 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 56 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 57 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 58 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 59 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 60 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 61 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 62 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 63 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 64 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 65 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 66 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 67 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 68 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 69 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 70 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 71 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 72 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 73 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 74 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 75 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 76 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 77 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 78 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 79 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 100 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 101 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 102 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 103 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 104 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 105 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 106 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 80 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 107 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 81 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 108 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 82 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 109 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 83 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 84 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 85 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 86 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 87 color:#260d1b, fill:#d98cb6, stroke:#260d1b\n",
      "relatedElement": {
        "elementHeader": {
          "class": "ElementHeader",
          "headerVersion": 0,
          "status": "ACTIVE",
          "type": {
            "typeId": "4d3a2b8d-9e2e-4832-b338-21c74e45b238",
            "typeName": "GovernanceActionProcess",
            "superTypeNames": [
              "GovernanceAction",
              "GovernanceControl",
              "GovernanceDefinition",
              "AuthoredReferenceable",
              "Referenceable",
              "OpenMetadataRoot"
            ],
            "typeVersion": 1,
            "typeDescription": "A process implemented by chained engine actions that call governance services.",
            "typeCategory": "ENTITY_DEF"
          },
          "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "CONTENT_PACK",
            "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
            "homeMetadataCollectionName": "UnityCatalogContentPack",
            "license": "Apache 2.0"
          },
          "versions": {
            "createdBy": "Egeria Project",
            "updatedBy": "Egeria Project",
            "maintainedBy": [
              "Egeria Project"
            ],
            "createTime": "2026-04-23T14:20:40.309+00:00",
            "updateTime": "2026-04-23T14:20:40.309+00:00",
            "version": 1776954043523
          },
          "guid": "4cc5bde4-2455-437a-aba8-fb1514faac75",
          "anchor": {
            "class": "ElementClassification",
            "headerVersion": 0,
            "status": "ACTIVE",
            "type": {
              "typeId": "aa44f302-2e43-4669-a1e7-edaae414fc6e",
              "typeName": "Anchors",
              "typeVersion": 1,
              "typeDescription": "Identifies the anchor entity for an element that is part of a large composite object such as an asset.",
              "typeCategory": "CLASSIFICATION_DEF"
            },
            "origin": {
              "sourceServer": "qs-metadata-store",
              "originCategory": "CONTENT_PACK",
              "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
              "homeMetadataCollectionName": "UnityCatalogContentPack"
            },
            "versions": {
              "createdBy": "Egeria Project",
              "updatedBy": "Egeria Project",
              "maintainedBy": [
                "Egeria Project"
              ],
              "createTime": "2026-04-23T14:20:40.309+00:00",
              "updateTime": "2026-04-23T14:20:40.309+00:00",
              "version": 1776954043523
            },
            "classificationOrigin": "ASSIGNED",
            "classificationName": "Anchors",
            "classificationProperties": {
              "class": "AnchorsProperties",
              "typeName": "Anchors",
              "anchorGUID": "4cc5bde4-2455-437a-aba8-fb1514faac75",
              "anchorTypeName": "GovernanceActionProcess",
              "anchorDomainName": "Asset"
            }
          }
        },
        "properties": {
          "class": "GovernanceActionProcessProperties",
          "typeName": "GovernanceActionProcess",
          "qualifiedName": "DatabricksUnityCatalogServer:CreateAndSurveyGovernanceActionProcess",
          "displayName": "DatabricksUnityCatalogServer:CreateAndSurvey",
          "description": "Create a Databricks Unity Catalog Server, run a survey against it, and print out the resulting report.",
          "url": "https://egeria-project.org/egeria-solutions/leveraging-unity-catalog/overview/",
          "domainIdentifier": 0
        }
      },
      "resourceUse": "Survey Resource"
    },
    {
      "displayName": "Survey Resource",
      "description": "Delete the asset for Databricks Unity Catalog Server using the same template properties that were used to create it.  This will delete all of the metadata anchored to the asset and relationships to other entities such as the catalog target relationships.",
      "additionalProperties": {
        "templateGUID": "dcca9788-b30f-4007-b1ac-ec634aff6879"
      },
      "relatedElement": {
        "elementHeader": {
          "class": "ElementHeader",
          "headerVersion": 0,
          "status": "ACTIVE",
          "type": {
            "typeId": "4d3a2b8d-9e2e-4832-b338-21c74e45b238",
            "typeName": "GovernanceActionProcess",
            "superTypeNames": [
              "GovernanceAction",
              "GovernanceControl",
              "GovernanceDefinition",
              "AuthoredReferenceable",
              "Referenceable",
              "OpenMetadataRoot"
            ],
            "typeVersion": 1,
            "typeDescription": "A process implemented by chained engine actions that call governance services.",
            "typeCategory": "ENTITY_DEF"
          },
          "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "CONTENT_PACK",
            "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
            "homeMetadataCollectionName": "UnityCatalogContentPack",
            "license": "Apache 2.0"
          },
          "versions": {
            "createdBy": "Egeria Project",
            "updatedBy": "Egeria Project",
            "maintainedBy": [
              "Egeria Project"
            ],
            "createTime": "2026-04-23T14:20:40.309+00:00",
            "updateTime": "2026-04-23T14:20:40.309+00:00",
            "version": 1776954043523
          },
          "guid": "f6c3c810-f3d1-4ec8-a510-97443a649685",
          "anchor": {
            "class": "ElementClassification",
            "headerVersion": 0,
            "status": "ACTIVE",
            "type": {
              "typeId": "aa44f302-2e43-4669-a1e7-edaae414fc6e",
              "typeName": "Anchors",
              "typeVersion": 1,
              "typeDescription": "Identifies the anchor entity for an element that is part of a large composite object such as an asset.",
              "typeCategory": "CLASSIFICATION_DEF"
            },
            "origin": {
              "sourceServer": "qs-metadata-store",
              "originCategory": "CONTENT_PACK",
              "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
              "homeMetadataCollectionName": "UnityCatalogContentPack"
            },
            "versions": {
              "createdBy": "Egeria Project",
              "updatedBy": "Egeria Project",
              "maintainedBy": [
                "Egeria Project"
              ],
              "createTime": "2026-04-23T14:20:40.309+00:00",
              "updateTime": "2026-04-23T14:20:40.309+00:00",
              "version": 1776954043523
            },
            "classificationOrigin": "ASSIGNED",
            "classificationName": "Anchors",
            "classificationProperties": {
              "class": "AnchorsProperties",
              "typeName": "Anchors",
              "anchorGUID": "f6c3c810-f3d1-4ec8-a510-97443a649685",
              "anchorTypeName": "GovernanceActionProcess",
              "anchorDomainName": "Asset"
            }
          }
        },
        "properties": {
          "class": "GovernanceActionProcessProperties",
          "typeName": "GovernanceActionProcess",
          "qualifiedName": "DatabricksUnityCatalogServer:DeleteAssetWithTemplateGovernanceActionProcess",
          "displayName": "DatabricksUnityCatalogServer:DeleteAsset",
          "description": "Delete the asset for Databricks Unity Catalog Server using the same template properties that were used to create it.  This will delete all of the metadata anchored to the asset and relationships to other entities such as the catalog target relationships.",
          "url": "https://egeria-project.org/egeria-solutions/leveraging-unity-catalog/overview/",
          "domainIdentifier": 0
        }
      },
      "resourceUse": "Survey Resource"
    }
  ],
  "resourceList": [
    {
      "displayName": "Catalog Resource",
      "description": "Governance Action Service that creates an asset and passes its GUID as a new asset action target.",
      "additionalProperties": {
        "templateGUID": "3f7f62f6-4abc-424e-9f92-523306e7d5d5"
      },
      "specification": {
        "supportedRequestParameter": [
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "templateGUID",
            "description": "The unique identifier of the template to use to catalog the asset.",
            "dataType": "string",
            "example": "542134e6-b9ce-4dce-8aef-22e8daf34fdb",
            "required": false
          }
        ],
        "producedGuard": [
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "service-failed",
            "description": "An unexpected error occurred while the governance service was running.  Messages are logged to the audit log explaining the source of the error.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service failed to execute the requested action."
            },
            "completionStatus": "FAILED"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "missing-template",
            "description": "The templateGUID request parameter has not been supplied.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service has not performed the requested action because it is not appropriate (for example, a false positive)."
            },
            "completionStatus": "INVALID"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "delete-complete",
            "description": "The new asset representing the resource has been deleted.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service for the governance action has successfully completed processing."
            },
            "completionStatus": "ACTIONED"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "set-up-complete",
            "description": "The new asset representing the resource has been created.  Its unique identifier (guid) is published in the ''newAsset'' action target",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service for the governance action has successfully completed processing."
            },
            "completionStatus": "ACTIONED"
          }
        ],
        "producedActionTarget": [
          {
            "class": "ProducedActionTarget",
            "specificationPropertyType": "PRODUCED_ACTION_TARGET",
            "name": "newAsset",
            "description": "A newly created Asset (or a subtype of).",
            "openMetadataTypeName": "Asset",
            "required": false
          }
        ]
      },
      "specificationMermaidGraph": "---\ntitle: Specification for - create-databricks-unity-catalog-server (UnityCatalogGovernance) [323d8a5c-4f79-4bc0-a35a-0c39d1990a9e]\n---\nflowchart LR\n%%{init: {\"flowchart\": {\"htmlLabels\": false}} }%%\n\n1@{ shape: tag-rect, label: \"*Governance Action Type*\n**create-databricks-unity-catalog-server (UnityCatalogGovernance)**\"}\n2@{ shape: hex, label: \"*Specification Property Assignment*\n**supportedRequestParameter**\"}\n1==>2\n3@{ shape: hex, label: \"*Specification Property Value*\n**templateGUID**\"}\n2==>3\nsubgraph 4 [templateGUID details]\n5@{ shape: text, label: \"*description:*\n**The unique identifier of the template to use to catalog the asset.**\"}\n6@{ shape: text, label: \"*data Type:*\n**string**\"}\n7@{ shape: text, label: \"*example:*\n**542134e6-b9ce-4dce-8aef-22e8daf34fdb**\"}\n8@{ shape: text, label: \"*required:*\n**false**\"}\nend\n3==>4\n9@{ shape: hex, label: \"*Specification Property Assignment*\n**producedGuard**\"}\n1==>9\n10@{ shape: hex, label: \"*Specification Property Value*\n**service-failed**\"}\n9==>10\nsubgraph 11 [service-failed details]\n12@{ shape: text, label: \"*description:*\n**An unexpected error occurred while the governance service was running.  Messages are logged to the audit log explaining the source of the error.**\"}\n13@{ shape: text, label: \"*completion Status:*\n**Failed (The governance action service failed to execute the requested action.)**\"}\n14@{ shape: text, label: \"*completion Status Description:*\n**The governance action service failed to execute the requested action.**\"}\nend\n10==>11\n15@{ shape: hex, label: \"*Specification Property Value*\n**missing-template**\"}\n9==>15\nsubgraph 16 [missing-template details]\n17@{ shape: text, label: \"*description:*\n**The templateGUID request parameter has not been supplied.**\"}\n18@{ shape: text, label: \"*completion Status:*\n**Invalid (The governance action service has not performed the requested action because it is not appropriate (for example, a false positive).)**\"}\n19@{ shape: text, label: \"*completion Status Description:*\n**The governance action service has not performed the requested action because it is not appropriate (for example, a false positive).**\"}\nend\n15==>16\n20@{ shape: hex, label: \"*Specification Property Value*\n**delete-complete**\"}\n9==>20\nsubgraph 21 [delete-complete details]\n22@{ shape: text, label: \"*description:*\n**The new asset representing the resource has been deleted.**\"}\n23@{ shape: text, label: \"*completion Status:*\n**Actioned (The governance action service for the governance action has successfully completed processing.)**\"}\n24@{ shape: text, label: \"*completion Status Description:*\n**The governance action service for the governance action has successfully completed processing.**\"}\nend\n20==>21\n25@{ shape: hex, label: \"*Specification Property Value*\n**set-up-complete**\"}\n9==>25\nsubgraph 26 [set-up-complete details]\n27@{ shape: text, label: \"*description:*\n**The new asset representing the resource has been created.  Its unique identifier (guid) is published in the ''newAsset'' action target**\"}\n28@{ shape: text, label: \"*completion Status:*\n**Actioned (The governance action service for the governance action has successfully completed processing.)**\"}\n29@{ shape: text, label: \"*completion Status Description:*\n**The governance action service for the governance action has successfully completed processing.**\"}\nend\n25==>26\n30@{ shape: hex, label: \"*Specification Property Assignment*\n**producedActionTarget**\"}\n1==>30\n31@{ shape: hex, label: \"*Specification Property Value*\n**newAsset**\"}\n30==>31\nsubgraph 32 [newAsset details]\n33@{ shape: text, label: \"*description:*\n**A newly created Asset (or a subtype of).**\"}\n34@{ shape: text, label: \"*type Name:*\n**Asset**\"}\n35@{ shape: text, label: \"*deployed Implementation Type:*\n\"}\n36@{ shape: text, label: \"*required:*\n**false**\"}\nend\n31==>32\nstyle 22 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 23 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 24 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 25 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 26 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 27 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 28 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 29 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 30 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 31 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 10 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 32 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 11 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 33 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 12 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 34 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 13 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 35 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 14 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 36 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 15 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 16 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 17 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 18 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 19 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 1 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 2 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 3 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 4 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 5 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 6 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 7 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 8 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 9 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 20 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 21 color:#260d1b, fill:#d98cb6, stroke:#260d1b\n",
      "relatedElement": {
        "elementHeader": {
          "class": "ElementHeader",
          "headerVersion": 0,
          "status": "ACTIVE",
          "type": {
            "typeId": "92e20083-0393-40c0-a95b-090724a91ddc",
            "typeName": "GovernanceActionType",
            "superTypeNames": [
              "GovernanceAction",
              "GovernanceControl",
              "GovernanceDefinition",
              "AuthoredReferenceable",
              "Referenceable",
              "OpenMetadataRoot"
            ],
            "typeVersion": 1,
            "typeDescription": "A description of a call to a governance engine that acts as a template when creating the appropriate engine action instance.",
            "typeCategory": "ENTITY_DEF"
          },
          "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "CONTENT_PACK",
            "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
            "homeMetadataCollectionName": "UnityCatalogContentPack",
            "license": "Apache 2.0"
          },
          "versions": {
            "createdBy": "Egeria Project",
            "updatedBy": "Egeria Project",
            "maintainedBy": [
              "Egeria Project"
            ],
            "createTime": "2026-04-23T14:20:40.309+00:00",
            "updateTime": "2026-04-23T14:20:40.309+00:00",
            "version": 1776954043523
          },
          "guid": "323d8a5c-4f79-4bc0-a35a-0c39d1990a9e",
          "anchor": {
            "class": "ElementClassification",
            "headerVersion": 0,
            "status": "ACTIVE",
            "type": {
              "typeId": "aa44f302-2e43-4669-a1e7-edaae414fc6e",
              "typeName": "Anchors",
              "typeVersion": 1,
              "typeDescription": "Identifies the anchor entity for an element that is part of a large composite object such as an asset.",
              "typeCategory": "CLASSIFICATION_DEF"
            },
            "origin": {
              "sourceServer": "qs-metadata-store",
              "originCategory": "CONTENT_PACK",
              "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
              "homeMetadataCollectionName": "UnityCatalogContentPack"
            },
            "versions": {
              "createdBy": "Egeria Project",
              "updatedBy": "Egeria Project",
              "maintainedBy": [
                "Egeria Project"
              ],
              "createTime": "2026-04-23T14:20:40.309+00:00",
              "updateTime": "2026-04-23T14:20:40.309+00:00",
              "version": 1776954043523
            },
            "classificationOrigin": "ASSIGNED",
            "classificationName": "Anchors",
            "classificationProperties": {
              "class": "AnchorsProperties",
              "typeName": "Anchors",
              "anchorGUID": "6e7a91ad-3fa1-4133-ba56-99d372d9a5fa",
              "anchorTypeName": "GovernanceActionEngine",
              "anchorDomainName": "SoftwareCapability"
            }
          }
        },
        "properties": {
          "class": "GovernanceActionTypeProperties",
          "typeName": "GovernanceActionType",
          "qualifiedName": "UnityCatalogGovernance::create-databricks-unity-catalog-server",
          "displayName": "create-databricks-unity-catalog-server (UnityCatalogGovernance)",
          "description": "Governance Action Service that creates an asset and passes its GUID as a new asset action target.",
          "domainIdentifier": 0,
          "waitTime": 0
        }
      },
      "resourceUse": "Catalog Resource"
    },
    {
      "displayName": "Uncatalog Resource",
      "description": "Governance Action Service that deletes an asset that was created by a template, and passes its GUID as a deleted asset action target.",
      "additionalProperties": {
        "templateGUID": "3f7f62f6-4abc-424e-9f92-523306e7d5d5"
      },
      "specification": {
        "supportedRequestParameter": [
          {
            "class": "SupportedRequestParameter",
            "specificationPropertyType": "SUPPORTED_REQUEST_PARAMETER",
            "name": "templateGUID",
            "description": "The unique identifier of the template to use to catalog the asset.",
            "dataType": "string",
            "example": "542134e6-b9ce-4dce-8aef-22e8daf34fdb",
            "required": false
          }
        ],
        "producedGuard": [
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "delete-complete",
            "description": "The new asset representing the resource has been deleted.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service for the governance action has successfully completed processing."
            },
            "completionStatus": "ACTIONED"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "missing-template",
            "description": "The templateGUID request parameter has not been supplied.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service has not performed the requested action because it is not appropriate (for example, a false positive)."
            },
            "completionStatus": "INVALID"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "set-up-complete",
            "description": "The new asset representing the resource has been created.  Its unique identifier (guid) is published in the ''newAsset'' action target",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service for the governance action has successfully completed processing."
            },
            "completionStatus": "ACTIONED"
          },
          {
            "class": "ProducedGuard",
            "specificationPropertyType": "PRODUCED_GUARD",
            "name": "service-failed",
            "description": "An unexpected error occurred while the governance service was running.  Messages are logged to the audit log explaining the source of the error.",
            "otherPropertyValues": {
              "completionStatusDescription": "The governance action service failed to execute the requested action."
            },
            "completionStatus": "FAILED"
          }
        ],
        "producedActionTarget": [
          {
            "class": "ProducedActionTarget",
            "specificationPropertyType": "PRODUCED_ACTION_TARGET",
            "name": "deletedAsset",
            "description": "A newly deleted Asset (or a subtype of).",
            "openMetadataTypeName": "Asset",
            "required": false
          }
        ]
      },
      "specificationMermaidGraph": "---\ntitle: Specification for - delete-databricks-unity-catalog-server (UnityCatalogGovernance) [cfeafd56-a6dd-41e5-bf0e-33b65639085d]\n---\nflowchart LR\n%%{init: {\"flowchart\": {\"htmlLabels\": false}} }%%\n\n1@{ shape: tag-rect, label: \"*Governance Action Type*\n**delete-databricks-unity-catalog-server (UnityCatalogGovernance)**\"}\n2@{ shape: hex, label: \"*Specification Property Assignment*\n**supportedRequestParameter**\"}\n1==>2\n3@{ shape: hex, label: \"*Specification Property Value*\n**templateGUID**\"}\n2==>3\nsubgraph 4 [templateGUID details]\n5@{ shape: text, label: \"*description:*\n**The unique identifier of the template to use to catalog the asset.**\"}\n6@{ shape: text, label: \"*data Type:*\n**string**\"}\n7@{ shape: text, label: \"*example:*\n**542134e6-b9ce-4dce-8aef-22e8daf34fdb**\"}\n8@{ shape: text, label: \"*required:*\n**false**\"}\nend\n3==>4\n9@{ shape: hex, label: \"*Specification Property Assignment*\n**producedGuard**\"}\n1==>9\n10@{ shape: hex, label: \"*Specification Property Value*\n**delete-complete**\"}\n9==>10\nsubgraph 11 [delete-complete details]\n12@{ shape: text, label: \"*description:*\n**The new asset representing the resource has been deleted.**\"}\n13@{ shape: text, label: \"*completion Status:*\n**Actioned (The governance action service for the governance action has successfully completed processing.)**\"}\n14@{ shape: text, label: \"*completion Status Description:*\n**The governance action service for the governance action has successfully completed processing.**\"}\nend\n10==>11\n15@{ shape: hex, label: \"*Specification Property Value*\n**missing-template**\"}\n9==>15\nsubgraph 16 [missing-template details]\n17@{ shape: text, label: \"*description:*\n**The templateGUID request parameter has not been supplied.**\"}\n18@{ shape: text, label: \"*completion Status:*\n**Invalid (The governance action service has not performed the requested action because it is not appropriate (for example, a false positive).)**\"}\n19@{ shape: text, label: \"*completion Status Description:*\n**The governance action service has not performed the requested action because it is not appropriate (for example, a false positive).**\"}\nend\n15==>16\n20@{ shape: hex, label: \"*Specification Property Value*\n**set-up-complete**\"}\n9==>20\nsubgraph 21 [set-up-complete details]\n22@{ shape: text, label: \"*description:*\n**The new asset representing the resource has been created.  Its unique identifier (guid) is published in the ''newAsset'' action target**\"}\n23@{ shape: text, label: \"*completion Status:*\n**Actioned (The governance action service for the governance action has successfully completed processing.)**\"}\n24@{ shape: text, label: \"*completion Status Description:*\n**The governance action service for the governance action has successfully completed processing.**\"}\nend\n20==>21\n25@{ shape: hex, label: \"*Specification Property Value*\n**service-failed**\"}\n9==>25\nsubgraph 26 [service-failed details]\n27@{ shape: text, label: \"*description:*\n**An unexpected error occurred while the governance service was running.  Messages are logged to the audit log explaining the source of the error.**\"}\n28@{ shape: text, label: \"*completion Status:*\n**Failed (The governance action service failed to execute the requested action.)**\"}\n29@{ shape: text, label: \"*completion Status Description:*\n**The governance action service failed to execute the requested action.**\"}\nend\n25==>26\n30@{ shape: hex, label: \"*Specification Property Assignment*\n**producedActionTarget**\"}\n1==>30\n31@{ shape: hex, label: \"*Specification Property Value*\n**deletedAsset**\"}\n30==>31\nsubgraph 32 [deletedAsset details]\n33@{ shape: text, label: \"*description:*\n**A newly deleted Asset (or a subtype of).**\"}\n34@{ shape: text, label: \"*type Name:*\n**Asset**\"}\n35@{ shape: text, label: \"*deployed Implementation Type:*\n\"}\n36@{ shape: text, label: \"*required:*\n**false**\"}\nend\n31==>32\nstyle 22 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 23 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 24 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 25 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 26 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 27 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 28 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 29 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 30 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 31 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 10 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 32 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 11 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 33 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 12 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 34 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 13 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 35 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 14 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 36 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 15 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 16 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 17 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 18 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 19 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 1 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 2 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 3 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 4 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 5 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 6 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 7 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 8 color:#000000, fill:#F9F7ED, stroke:#b7c0c7\nstyle 9 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 20 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 21 color:#260d1b, fill:#d98cb6, stroke:#260d1b\n",
      "relatedElement": {
        "elementHeader": {
          "class": "ElementHeader",
          "headerVersion": 0,
          "status": "ACTIVE",
          "type": {
            "typeId": "92e20083-0393-40c0-a95b-090724a91ddc",
            "typeName": "GovernanceActionType",
            "superTypeNames": [
              "GovernanceAction",
              "GovernanceControl",
              "GovernanceDefinition",
              "AuthoredReferenceable",
              "Referenceable",
              "OpenMetadataRoot"
            ],
            "typeVersion": 1,
            "typeDescription": "A description of a call to a governance engine that acts as a template when creating the appropriate engine action instance.",
            "typeCategory": "ENTITY_DEF"
          },
          "origin": {
            "sourceServer": "qs-metadata-store",
            "originCategory": "CONTENT_PACK",
            "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
            "homeMetadataCollectionName": "UnityCatalogContentPack",
            "license": "Apache 2.0"
          },
          "versions": {
            "createdBy": "Egeria Project",
            "updatedBy": "Egeria Project",
            "maintainedBy": [
              "Egeria Project"
            ],
            "createTime": "2026-04-23T14:20:40.309+00:00",
            "updateTime": "2026-04-23T14:20:40.309+00:00",
            "version": 1776954043523
          },
          "guid": "cfeafd56-a6dd-41e5-bf0e-33b65639085d",
          "anchor": {
            "class": "ElementClassification",
            "headerVersion": 0,
            "status": "ACTIVE",
            "type": {
              "typeId": "aa44f302-2e43-4669-a1e7-edaae414fc6e",
              "typeName": "Anchors",
              "typeVersion": 1,
              "typeDescription": "Identifies the anchor entity for an element that is part of a large composite object such as an asset.",
              "typeCategory": "CLASSIFICATION_DEF"
            },
            "origin": {
              "sourceServer": "qs-metadata-store",
              "originCategory": "CONTENT_PACK",
              "homeMetadataCollectionId": "e6756296-3fa3-4aa3-9450-0dc44b8beae2",
              "homeMetadataCollectionName": "UnityCatalogContentPack"
            },
            "versions": {
              "createdBy": "Egeria Project",
              "updatedBy": "Egeria Project",
              "maintainedBy": [
                "Egeria Project"
              ],
              "createTime": "2026-04-23T14:20:40.309+00:00",
              "updateTime": "2026-04-23T14:20:40.309+00:00",
              "version": 1776954043523
            },
            "classificationOrigin": "ASSIGNED",
            "classificationName": "Anchors",
            "classificationProperties": {
              "class": "AnchorsProperties",
              "typeName": "Anchors",
              "anchorGUID": "6e7a91ad-3fa1-4133-ba56-99d372d9a5fa",
              "anchorTypeName": "GovernanceActionEngine",
              "anchorDomainName": "SoftwareCapability"
            }
          }
        },
        "properties": {
          "class": "GovernanceActionTypeProperties",
          "typeName": "GovernanceActionType",
          "qualifiedName": "UnityCatalogGovernance::delete-databricks-unity-catalog-server",
          "displayName": "delete-databricks-unity-catalog-server (UnityCatalogGovernance)",
          "description": "Governance Action Service that deletes an asset that was created by a template, and passes its GUID as a deleted asset action target.",
          "domainIdentifier": 0,
          "waitTime": 0
        }
      },
      "resourceUse": "Uncatalog Resource"
    }
  ],
  "mermaidGraph": "---\ntitle: Technology Report for - Databricks Unity Catalog Server [93657be6-acab-4711-a4eb-549b82dc7c86]\n---\nflowchart LR\n%%{init: {\"flowchart\": {\"htmlLabels\": false}} }%%\n\n1@{ shape: hex, label: \"*Technology Type*\n**Databricks Unity Catalog Server**\"}\n2@{ shape: hex, label: \"*Technology Type*\n**Catalog Templates**\"}\n1==>2\n3@{ shape: card, label: \"*Software Server*\n**Databricks Unity Catalog Server template**\"}\n2==>|\"catalog templates\"|3\n4@{ shape: hex, label: \"*Property Type*\n**placeholderProperty**\"}\n3==>|\"SpecificationPropertyAssignment\"|4\n5@{ shape: hex, label: \"*placeholder Property*\n**hostURL**\"}\n4==>|\"SpecificationPropertyAssignment\"|5\n6@{ shape: hex, label: \"*placeholder Property*\n**serverName**\"}\n4==>|\"SpecificationPropertyAssignment\"|6\n7@{ shape: hex, label: \"*placeholder Property*\n**secretsCollectionName**\"}\n4==>|\"SpecificationPropertyAssignment\"|7\n8@{ shape: hex, label: \"*placeholder Property*\n**portNumber**\"}\n4==>|\"SpecificationPropertyAssignment\"|8\n9@{ shape: hex, label: \"*placeholder Property*\n**secretsStorePathName**\"}\n4==>|\"SpecificationPropertyAssignment\"|9\n10@{ shape: hex, label: \"*placeholder Property*\n**versionIdentifier**\"}\n4==>|\"SpecificationPropertyAssignment\"|10\n11@{ shape: hex, label: \"*placeholder Property*\n**description**\"}\n4==>|\"SpecificationPropertyAssignment\"|11\n12@{ shape: hex, label: \"*Technology Type*\n**Governance Action Processes**\"}\n1==>12\n13@{ shape: processes, label: \"*Governance Action Process*\n**Catalog Resource**\"}\n12==>|\"governance action process [Catalog Resource]\"|13\n14@{ shape: hex, label: \"*Property Type*\n**supportedRequestParameter**\"}\n13==>|\"SpecificationPropertyAssignment\"|14\n15@{ shape: hex, label: \"*supported Request Parameter*\n**portNumber**\"}\n14==>|\"SpecificationPropertyAssignment\"|15\n16@{ shape: hex, label: \"*supported Request Parameter*\n**hostURL**\"}\n14==>|\"SpecificationPropertyAssignment\"|16\n17@{ shape: hex, label: \"*supported Request Parameter*\n**secretsStorePathName**\"}\n14==>|\"SpecificationPropertyAssignment\"|17\n18@{ shape: hex, label: \"*supported Request Parameter*\n**secretsCollectionName**\"}\n14==>|\"SpecificationPropertyAssignment\"|18\n19@{ shape: hex, label: \"*supported Request Parameter*\n**serverName**\"}\n14==>|\"SpecificationPropertyAssignment\"|19\n20@{ shape: hex, label: \"*supported Request Parameter*\n**description**\"}\n14==>|\"SpecificationPropertyAssignment\"|20\n21@{ shape: hex, label: \"*supported Request Parameter*\n**versionIdentifier**\"}\n14==>|\"SpecificationPropertyAssignment\"|21\n22@{ shape: processes, label: \"*Governance Action Process*\n**Survey Resource**\"}\n12==>|\"governance action process [Survey Resource]\"|22\n23@{ shape: hex, label: \"*Property Type*\n**producedAnnotationType**\"}\n22==>|\"SpecificationPropertyAssignment\"|23\n24@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Schemas**\"}\n23==>|\"SpecificationPropertyAssignment\"|24\n25@{ shape: hex, label: \"*produced Annotation Type*\n**Log of Unity Catalog (UC) Resources**\"}\n23==>|\"SpecificationPropertyAssignment\"|25\n26@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Analytical Models**\"}\n23==>|\"SpecificationPropertyAssignment\"|26\n27@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Table Columns**\"}\n23==>|\"SpecificationPropertyAssignment\"|27\n28@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of File Volumes**\"}\n23==>|\"SpecificationPropertyAssignment\"|28\n29@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Executable Functions**\"}\n23==>|\"SpecificationPropertyAssignment\"|29\n30@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Unity Catalog (UC) Catalogs**\"}\n23==>|\"SpecificationPropertyAssignment\"|30\n31@{ shape: hex, label: \"*produced Annotation Type*\n**Capture List of Tables**\"}\n23==>|\"SpecificationPropertyAssignment\"|31\n32@{ shape: hex, label: \"*produced Annotation Type*\n**Capture Unity Catalog (UC) Server Metrics**\"}\n23==>|\"SpecificationPropertyAssignment\"|32\n33@{ shape: hex, label: \"*Property Type*\n**supportedRequestParameter**\"}\n22==>|\"SpecificationPropertyAssignment\"|33\n34@{ shape: hex, label: \"*supported Request Parameter*\n**description**\"}\n33==>|\"SpecificationPropertyAssignment\"|34\n35@{ shape: hex, label: \"*supported Request Parameter*\n**secretsStorePathName**\"}\n33==>|\"SpecificationPropertyAssignment\"|35\n36@{ shape: hex, label: \"*supported Request Parameter*\n**versionIdentifier**\"}\n33==>|\"SpecificationPropertyAssignment\"|36\n37@{ shape: hex, label: \"*supported Request Parameter*\n**serverName**\"}\n33==>|\"SpecificationPropertyAssignment\"|37\n38@{ shape: hex, label: \"*supported Request Parameter*\n**portNumber**\"}\n33==>|\"SpecificationPropertyAssignment\"|38\n39@{ shape: hex, label: \"*supported Request Parameter*\n**secretsCollectionName**\"}\n33==>|\"SpecificationPropertyAssignment\"|39\n40@{ shape: hex, label: \"*supported Request Parameter*\n**hostURL**\"}\n33==>|\"SpecificationPropertyAssignment\"|40\n41@{ shape: hex, label: \"*Property Type*\n**supportedAnalysisStep**\"}\n22==>|\"SpecificationPropertyAssignment\"|41\n42@{ shape: hex, label: \"*supported Analysis Step*\n**Produce Inventory**\"}\n41==>|\"SpecificationPropertyAssignment\"|42\n43@{ shape: hex, label: \"*supported Analysis Step*\n**Profiling Associated Resources**\"}\n41==>|\"SpecificationPropertyAssignment\"|43\n44@{ shape: hex, label: \"*supported Analysis Step*\n**Measure Resource**\"}\n41==>|\"SpecificationPropertyAssignment\"|44\n45@{ shape: hex, label: \"*supported Analysis Step*\n**Check Asset**\"}\n41==>|\"SpecificationPropertyAssignment\"|45\n46@{ shape: processes, label: \"*Governance Action Process*\n**Survey Resource**\"}\n12==>|\"governance action process [Survey Resource]\"|46\n47@{ shape: hex, label: \"*Technology Type*\n**Resource List**\"}\n1==>47\n48@{ shape: tag-rect, label: \"*Governance Action Type*\n**Catalog Resource**\"}\n47==>|\"resource [Catalog Resource]\"|48\n49@{ shape: hex, label: \"*Property Type*\n**supportedRequestParameter**\"}\n48==>|\"SpecificationPropertyAssignment\"|49\n50@{ shape: hex, label: \"*supported Request Parameter*\n**templateGUID**\"}\n49==>|\"SpecificationPropertyAssignment\"|50\n51@{ shape: hex, label: \"*Property Type*\n**producedGuard**\"}\n48==>|\"SpecificationPropertyAssignment\"|51\n52@{ shape: hex, label: \"*produced Guard*\n**service-failed**\"}\n51==>|\"SpecificationPropertyAssignment\"|52\n53@{ shape: hex, label: \"*produced Guard*\n**missing-template**\"}\n51==>|\"SpecificationPropertyAssignment\"|53\n54@{ shape: hex, label: \"*produced Guard*\n**delete-complete**\"}\n51==>|\"SpecificationPropertyAssignment\"|54\n55@{ shape: hex, label: \"*produced Guard*\n**set-up-complete**\"}\n51==>|\"SpecificationPropertyAssignment\"|55\n56@{ shape: hex, label: \"*Property Type*\n**producedActionTarget**\"}\n48==>|\"SpecificationPropertyAssignment\"|56\n57@{ shape: hex, label: \"*produced Action Target*\n**newAsset**\"}\n56==>|\"SpecificationPropertyAssignment\"|57\n58@{ shape: tag-rect, label: \"*Governance Action Type*\n**Uncatalog Resource**\"}\n47==>|\"resource [Uncatalog Resource]\"|58\n59@{ shape: hex, label: \"*Property Type*\n**supportedRequestParameter**\"}\n58==>|\"SpecificationPropertyAssignment\"|59\n60@{ shape: hex, label: \"*supported Request Parameter*\n**templateGUID**\"}\n59==>|\"SpecificationPropertyAssignment\"|60\n61@{ shape: hex, label: \"*Property Type*\n**producedGuard**\"}\n58==>|\"SpecificationPropertyAssignment\"|61\n62@{ shape: hex, label: \"*produced Guard*\n**delete-complete**\"}\n61==>|\"SpecificationPropertyAssignment\"|62\n63@{ shape: hex, label: \"*produced Guard*\n**missing-template**\"}\n61==>|\"SpecificationPropertyAssignment\"|63\n64@{ shape: hex, label: \"*produced Guard*\n**set-up-complete**\"}\n61==>|\"SpecificationPropertyAssignment\"|64\n65@{ shape: hex, label: \"*produced Guard*\n**service-failed**\"}\n61==>|\"SpecificationPropertyAssignment\"|65\n66@{ shape: hex, label: \"*Property Type*\n**producedActionTarget**\"}\n58==>|\"SpecificationPropertyAssignment\"|66\n67@{ shape: hex, label: \"*produced Action Target*\n**deletedAsset**\"}\n66==>|\"SpecificationPropertyAssignment\"|67\nstyle 44 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 45 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 46 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 47 color:#f2d9e7, fill:#732650, stroke:#f2d9e7\nstyle 48 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 49 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 50 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 51 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 52 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 53 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 10 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 54 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 11 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 55 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 12 color:#f2d9e7, fill:#732650, stroke:#f2d9e7\nstyle 56 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 13 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 57 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 14 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 58 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 15 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 59 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 16 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 17 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 18 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 19 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 1 color:#f2d9e7, fill:#732650, stroke:#f2d9e7\nstyle 2 color:#f2d9e7, fill:#732650, stroke:#f2d9e7\nstyle 3 color:#004563, fill:#b0e0e6, stroke:#004563\nstyle 4 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 5 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 6 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 7 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 8 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 9 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 60 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 61 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 62 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 63 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 20 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 64 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 21 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 65 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 22 color:#000000, fill:#40E0D0, stroke:#000000\nstyle 66 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 23 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 67 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 24 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 25 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 26 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 27 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 28 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 29 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 30 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 31 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 32 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 33 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 34 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 35 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 36 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 37 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 38 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 39 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 40 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 41 color:#f2d9e7, fill:#260d1b, stroke:#f2d9e7\nstyle 42 color:#260d1b, fill:#d98cb6, stroke:#260d1b\nstyle 43 color:#260d1b, fill:#d98cb6, stroke:#260d1b\n"
}
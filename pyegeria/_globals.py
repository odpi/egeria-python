"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
This common file is used to set some global values and enumerations used by the overall package. 

"""


is_debug = False
disable_ssl_warnings = True
enable_ssl_check = False
max_paging_size = 500
default_time_out = 30
DEBUG_LEVEL = "quiet"
COMMENT_TYPES = (
    "STANDARD_COMMENT",
    "ANSWER",
    "OTHER",
    "QUESTION",
    "SUGGESTION",
    "USAGE_EXPERIENCE",
    "REQUIREMENT"
)
star_ratings = (
    "FIVE_STARS",
    "FOUR_STARS",
    "NO_RECOMMENDATION",
    "ONE_STAR",
    "THREE_STARS",
    "TWO_STARS",
)

TEMPLATE_GUIDS: dict = {}
INTEGRATION_GUIDS: dict = {}

NO_ELEMENTS_FOUND = "No elements found"
NO_ASSETS_FOUND = "No assets found"
NO_SERVERS_FOUND = "No servers found"
NO_CATALOGS_FOUND = "No catalogs found"
NO_GLOSSARIES_FOUND = "No glossaries found"
NO_TERMS_FOUND = "No terms found"
NO_CATEGORIES_FOUND = "No categories found"
NO_ELEMENT_FOUND = "No element found"
NO_PROJECTS_FOUND = "No projects found"
NO_COLLECTION_FOUND = "No collection found"
NO_GUID_RETURNED = "No guid returned"
NO_MEMBERS_FOUND = "No members found"

MERMAID_GRAPHS = ["anchorMermaidGraph", "informationSupplyChainMermaidGraph","fieldLevelLineageGraph",
                  "actionMermaidGraph", "localLineageGraph", "edgeMermaidGraph", "iscImplementationMermaidGraph",
                  "specificationMermaidGraph", "solutionBlueprintMermaidGraph","mermaidGraph",
                  "solutionSubcomponentMermaidGraph"]
MERMAID_GRAPH_TITLES = ["Anchor Mermaid Graph", "Information Supply Chain Mermaid Graph","Field Level Lineage Graph",
                  "Action Mermaid Graph", "Local Lineage Graph", "Edge Mermaid Graph", "ISC Implementation Mermaid Graph",
                  "Specification Mermaid Graph", "Solution Blueprint Mermaid Graph","Mermaid Graph",
                  "Solution Subcomponent Mermaid Graph"]

#
# TEMPLATE_GUIDS['File System Directory'] = 'c353fd5d-9523-4a5e-a5e2-723ae490fe54'
# INTEGRATION_GUIDS['GeneralFilesMonitor'] = '1b98cdac-dd0a-4621-93db-99ef5a1098bc'
# INTEGRATION_GUIDS['OpenLineageFilePublisher'] = '6271b678-7d22-4cdf-87b1-45b366beaf4e'
# INTEGRATION_GUIDS['ContentPacksMonitor'] = '6bb2181e-7724-4515-ba3c-877cded55980'
# INTEGRATION_GUIDS['HarvestActivity'] = '856501d9-ec29-4e67-9cd7-120f53710ffa'
# INTEGRATION_GUIDS['SampleDataFilesMonitor'] = 'cd6479e1-2fe7-4426-b358-8a0cf70be117'
# TEMPLATE_GUIDS['CSV Data File'] = '13770f93-13c8-42be-9bb8-e0b1b1e52b1f'
# TEMPLATE_GUIDS['Keystore File'] = 'fbcfcc0c-1652-421f-b49b-c3e1c108768f'
# TEMPLATE_GUIDS['Unity Catalog Registered Model Version'] = '1364bfe7-8295-4e99-9243-8840aeac4cf1'
# TEMPLATE_GUIDS['Unity Catalog Server'] = 'dcca9788-b30f-4007-b1ac-ec634aff6879'
# INTEGRATION_GUIDS['UnityCatalogInsideCatalog'] = '74dde22f-2249-4ea3-af2b-b39e73f79b81'
# INTEGRATION_GUIDS['UnityCatalogServer'] = '06d068d9-9e08-4e67-8c59-073bbf1013af'
# TEMPLATE_GUIDS['Databricks Unity Catalog Server'] = '3f7f62f6-4abc-424e-9f92-523306e7d5d5'
# INTEGRATION_GUIDS['JDBC'] = '70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa'
# TEMPLATE_GUIDS['Data File'] = '66d8dda9-00cf-4e59-938c-4b0583596b1e'
# TEMPLATE_GUIDS['Unity Catalog Catalog'] = '5ee006aa-a6d6-411b-9b8d-5f720c079cae'
# TEMPLATE_GUIDS['View Server'] = 'fd61ca01-390d-4aa2-a55d-426826aa4e1b'
# TEMPLATE_GUIDS['Archive File'] = '7578e504-d00f-406d-a194-3fc0a351cdf9'
# TEMPLATE_GUIDS['Executable File'] = '3d99a163-7a13-4576-a212-784010a8302a'
# INTEGRATION_GUIDS['OpenLineageAPIPublisher'] = '2156bc98-973a-4859-908d-4ccc96f53cc5'
# TEMPLATE_GUIDS['PostgreSQL Relational Database'] = '3d398b3f-7ae6-4713-952a-409f3dea8520'
# INTEGRATION_GUIDS['PostgreSQLDatabase'] = 'ef301220-7dfe-4c6c-bb9d-8f92d9f63823'
# TEMPLATE_GUIDS['Unity Catalog Table'] = '6cc1e5f5-4c1e-4290-a80e-e06643ffb13d'
# TEMPLATE_GUIDS['JSON Data File'] = 'c4836635-7e9e-446a-83b5-15e206b1aff3'
# TEMPLATE_GUIDS['File System'] = '522f228c-097c-4f90-9efc-26c1f2696f87'
# TEMPLATE_GUIDS['Source Code File'] = '9c7013ef-f29b-4b01-a8ea-5ea14f64c67a'
# TEMPLATE_GUIDS['Program File'] = '32d27e9c-1fdf-455a-ad2a-42b4d7d99108'
# TEMPLATE_GUIDS['Apple MacBook Pro'] = '32a9fd56-85c9-47fe-a211-9da3871bf4da'
# TEMPLATE_GUIDS['Build Instruction File'] = 'fbb2fa2e-8bcb-402e-9be7-5c6db9f2c504'
# TEMPLATE_GUIDS['Spreadsheet Data File'] = 'e4fabff5-2ba9-4050-9076-6ed917970b4c'
# TEMPLATE_GUIDS['UNIX File System'] = '27117270-8667-41d0-a99a-9118f9b60199'
# TEMPLATE_GUIDS['Video Data File'] = '93b2b722-ec0f-4da4-960a-b8d4922f8bf5'
# TEMPLATE_GUIDS['JDBC Endpoint'] = '3d79ce50-1887-4627-ad71-ba4649aba2bc'
# TEMPLATE_GUIDS['Unity Catalog Function'] = 'a490ba65-6104-4213-9be9-524e16fed8aa'
# TEMPLATE_GUIDS['Unity Catalog Registered Model'] = '0d762ec5-c1f5-4364-aa64-e7e00d27f837'
# TEMPLATE_GUIDS['PostgreSQL Relational Database Schema'] = '82a5417c-d882-4271-8444-4c6a996a8bfc'
# INTEGRATION_GUIDS['HarvestSurveys'] = 'fae162c3-2bfd-467f-9c47-2e3b63a655de'
# INTEGRATION_GUIDS['HarvestActivity'] = '856501d9-ec29-4e67-9cd7-120f53710ffa'
# INTEGRATION_GUIDS['HarvestOpenMetadata'] = 'f8bf326b-d613-4ece-a12e-a1423bc272d7'
# TEMPLATE_GUIDS['PostgreSQL Server'] = '542134e6-b9ce-4dce-8aef-22e8daf34fdb'
# INTEGRATION_GUIDS['PostgreSQLServer'] = '36f69fd0-54ba-4f59-8a44-11ccf2687a34'
# TEMPLATE_GUIDS['Audio Data File'] = '39b4b670-7f15-4744-a5ba-62e8edafbcee'
# TEMPLATE_GUIDS['Document File'] = 'eb6f728d-fa54-4350-9807-1199cbf96851'
# TEMPLATE_GUIDS['Engine Host'] = '1764a891-4234-45f1-8cc3-536af40c790d'
# TEMPLATE_GUIDS['Integration Daemon'] = '6b3516f0-dd13-4786-9601-07215f995197'
# TEMPLATE_GUIDS['XML Data File'] = 'ea67ae71-c674-473e-b38b-689879d2a7d9'
# TEMPLATE_GUIDS['Avro Data File'] = '9f5be428-058e-41dd-b506-3a222283b579'
# TEMPLATE_GUIDS['REST API Endpoint'] = '9ea4bff4-d193-492f-bcad-6e68c07c6f9e'
# TEMPLATE_GUIDS['Unity Catalog Schema'] = '5bf92b0f-3970-41ea-b0a3-aacfbf6fd92e'
# TEMPLATE_GUIDS['Unity Catalog Volume'] = '92d2d2dc-0798-41f0-9512-b10548d312b7'
# TEMPLATE_GUIDS['Parquet Data File'] = '7f6cd744-79c3-4d25-a056-eeb1a91574c3'
# TEMPLATE_GUIDS['File'] = 'ae3067c7-cc72-4a18-88e1-746803c2c86f'
# TEMPLATE_GUIDS['3D Image Data File'] = '0059ea2b-6292-4cac-aa6f-a80a605f1114'
# TEMPLATE_GUIDS['YAML File'] = '2221855b-2b64-4b45-a2ee-c40adc5e2a64'
# TEMPLATE_GUIDS['Apache Kafka Topic'] = 'ea8f81c9-c59c-47de-9525-7cc59d1251e5'
# INTEGRATION_GUIDS['OpenLineageKafkaListener'] = '980b989c-de78-4e6a-a58d-51049d7381bf'
# TEMPLATE_GUIDS['Script File'] = 'dbd5e6bb-1ff8-46f4-a007-fb0485f68c92'
# TEMPLATE_GUIDS['Apache Atlas Server'] = 'fe6dce45-a978-4417-ab55-17f05b8bcea7'
# INTEGRATION_GUIDS['ApacheAtlasServer'] = '5721627a-2dd4-4f95-a274-6cfb128edb97'
# TEMPLATE_GUIDS['Raster Data File'] = '47211156-f03f-4881-8526-015e695a3dac'
# TEMPLATE_GUIDS['Metadata Access Server'] = 'bd8de890-fa79-4c24-aab8-20b41b5893dd'
# TEMPLATE_GUIDS['Data Folder'] = '372a0379-7060-4c9d-8d84-bc709b31794c'
# INTEGRATION_GUIDS['MaintainDataFolderLastUpdateDate'] = 'fd26f07c-ae44-4bc5-b457-37b43112224f'
# INTEGRATION_GUIDS['OpenLineageFilePublisher'] = '6271b678-7d22-4cdf-87b1-45b366beaf4e'
# TEMPLATE_GUIDS['Properties File'] = '3b281111-a0ef-4fc4-99e7-9a0ef84a7636'
# TEMPLATE_GUIDS['Vector Data File'] = 'db1bec7f-55a9-40d3-91c0-a57b76d422e2'
# TEMPLATE_GUIDS['OMAG Server Platform'] = '9b06c4dc-ddc8-47ae-b56b-28775d3a96f0'
# INTEGRATION_GUIDS['OpenAPI'] = 'b89d9a5a-2ea6-49bc-a4fc-e7df9f3ca93e'
# INTEGRATION_GUIDS['OMAGServerPlatform'] = 'dee84e6e-7a96-4975-86c1-152fb3ab759b'
# TEMPLATE_GUIDS['Apache Kafka Server'] = '5e1ff810-5418-43f7-b7c4-e6e062f9aff7'
# INTEGRATION_GUIDS['KafkaTopic'] = 'fa1f711c-0b34-4b57-8e6e-16162b132b0c'
# INTEGRATION_GUIDS['OpenLineageAPIPublisher'] = '2156bc98-973a-4859-908d-4ccc96f53cc5'
# INTEGRATION_GUIDS['JDBCDatabaseCataloguer'] = '70dcd0b7-9f06-48ad-ad44-ae4d7a7762aa'
# INTEGRATION_GUIDS['ApacheKafkaCataloguer'] = 'fa1f711c-0b34-4b57-8e6e-16162b132b0c'
# INTEGRATION_GUIDS['FilesCataloguer'] = '1b98cdac-dd0a-4621-93db-99ef5a1098bc'
# INTEGRATION_GUIDS['UnityCatalogServerSynchronizer'] = '06d068d9-9e08-4e67-8c59-073bbf1013af'
# INTEGRATION_GUIDS['SampleDataCataloguer'] = 'cd6479e1-2fe7-4426-b358-8a0cf70be117'
# INTEGRATION_GUIDS['OpenLineageGovernanceActionPublisher'] = '206f8faf-04da-4b6f-8280-eeee3943afeb'
# INTEGRATION_GUIDS['OMAGServerPlatformCataloguer'] = 'dee84e6e-7a96-4975-86c1-152fb3ab759b'
# INTEGRATION_GUIDS['HarvestActivity'] = '856501d9-ec29-4e67-9cd7-120f53710ffa'
# INTEGRATION_GUIDS['MaintainLastUpdateDate'] = 'fd26f07c-ae44-4bc5-b457-37b43112224f'
# INTEGRATION_GUIDS['UnityCatalogInsideCatalogSynchronizer'] = '74dde22f-2249-4ea3-af2b-b39e73f79b81'
# INTEGRATION_GUIDS['OpenLineageKafkaListener'] = '980b989c-de78-4e6a-a58d-51049d7381bf'
# INTEGRATION_GUIDS['HarvestOpenMetadata'] = 'f8bf326b-d613-4ece-a12e-a1423bc272d7'
# INTEGRATION_GUIDS['OpenAPICataloguer'] = 'b89d9a5a-2ea6-49bc-a4fc-e7df9f3ca93e'
# INTEGRATION_GUIDS['OpenLineageFilePublisher'] = '6271b678-7d22-4cdf-87b1-45b366beaf4e'
# INTEGRATION_GUIDS['PostgreSQLServerCataloguer'] = '36f69fd0-54ba-4f59-8a44-11ccf2687a34'
# INTEGRATION_GUIDS['PostgreSQLDatabaseCataloguer'] = 'ef301220-7dfe-4c6c-bb9d-8f92d9f63823'
# INTEGRATION_GUIDS['ContentPacksCataloguer'] = '6bb2181e-7724-4515-ba3c-877cded55980'
# INTEGRATION_GUIDS['OpenLineageCataloguer'] = '3347ac71-8dd2-403a-bc16-75a71be64bd7'
# INTEGRATION_GUIDS['ApacheAtlasExchange'] = '5721627a-2dd4-4f95-a274-6cfb128edb97'
# INTEGRATION_GUIDS['HarvestSurveys'] = 'fae162c3-2bfd-467f-9c47-2e3b63a655de'

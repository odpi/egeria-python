## Create Element
### Element Type Name
CSVFile

### Template GUID
13770f93-13c8-42be-9bb8-e0b1b1e52b1f

### Placeholder Property Values
{"fileName": "GenericElementTest.csv", "fileType": "CSV Data File", "filePathName": "test/GenericElementTest.csv", "versionIdentifier": "V1.0", "fileEncoding": "UTF-8", "fileExtension": "csv", "description": "Created via the generic Create Element command."}


## Create Secrets Store Element
### File Path Name
test/DrETestSecrets.omsecrets

### File Name
DrETestSecrets.omsecrets

### Version Identifier
V1.0

### Description
Regression test secrets store element.


## Create Kafka Server Element
### Kafka Server Name
DrETest-KafkaServer

### Host Name
kafka-test.example.com

### Port
9092

### Description
Regression test Kafka server. Note: as of 2026-09-11 this command fails on a
server with no "Apache Kafka Server" catalog template registered (confirmed
a pre-existing gap in the template catalog, not in this command) -- validate
mode still exercises parsing/attribute resolution safely.


## Create CSV Data File Element
### File Name
DrETest-DataFile.csv

### File Type
CSV Data File

### File Path Name
test/DrETest-DataFile.csv

### Version Identifier
V1.0

### Description
Regression test CSV data file element.


## Create Postgres Server Element
### Postgres Server Name
DrETest-PostgresServer

### Host Name
postgres-test.example.com

### Port
5432

### Database User Id
test_user

### Database Password
test_password

### Description
Regression test Postgres server element.


## Create Postgres Database Element
### Postgres Database Name
DrETest-PostgresDatabase

### Postgres Server Name
DrETest-PostgresServer

### Host Name
postgres-test.example.com

### Port
5432

### Database User Id
test_user

### Database Password
test_password

### Description
Regression test Postgres database element.


## Create Folder Element
### Folder Name
DrETest-Folder

### Directory Path Name
test/DrETest-Folder

### File System Name
local

### Description
Regression test folder element.


## Create UC Server Element
### UC Server Name
DrETest-UCServer

### Host URL
https://uc-test.example.com

### Port
443

### Description
Regression test Unity Catalog server element.


## Create UC Catalog Element
### UC Catalog Name
DrETest-UCCatalog

### Network Address
uc-test.example.com:443

### Description
Regression test Unity Catalog catalog element.


## Create UC Schema Element
### UC Catalog Name
DrETest-UCCatalog

### UC Schema Name
DrETest-UCSchema

### Network Address
uc-test.example.com:443

### Description
Regression test Unity Catalog schema element.


## Create UC Table Element
### UC Catalog Name
DrETest-UCCatalog

### UC Schema Name
DrETest-UCSchema

### UC Table Name
DrETest-UCTable

### UC Table Type
Managed

### UC Storage Location
s3://test-bucket/uctable

### UC Data Source Format
DELTA

### Network Address
uc-test.example.com:443

### Description
Regression test Unity Catalog table element.


## Create UC Function Element
### UC Catalog Name
DrETest-UCCatalog

### UC Schema Name
DrETest-UCSchema

### UC Function Name
DrETest-UCFunction

### Network Address
uc-test.example.com:443

### Description
Regression test Unity Catalog function element.


## Create UC Volume Element
### UC Catalog Name
DrETest-UCCatalog

### UC Schema Name
DrETest-UCSchema

### UC Volume Name
DrETest-UCVolume

### UC Volume Type
Managed

### UC Storage Location
s3://test-bucket/ucvolume

### Network Address
uc-test.example.com:443

### Description
Regression test Unity Catalog volume element.

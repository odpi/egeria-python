## Don't Create Governance Action Process Step
> A description of a call to a governance engine that acts as a template when creating the appropriate engine action instance.

### Display Name
Simple Postgres Survey — Schema and Stats

### Qualified Name
GovActionProcessStep::SimplePostgresSurvey::SchemaAndStats

### Additional Properties
| Parameter Name | Parameter Value |
|---|---|
| executes_at | resource-explorer |
| supported_technology_type | PostgreSQL Database |
| re_analysis_step | postgres_schema_and_stats |

___

## Don't Create Governance Action Process
### Display Name
Simple Postgres Survey

### Qualified Name
GovActionProcess::SimplePostgresSurvey

### Additional Properties
| Parameter Name | Parameter Value |
|---|---|
| supported_technology_type | PostgreSQL Database |

___

## Don't Link First Process Step
### Governance Action Process
GovActionProcess::SimplePostgresSurvey

### Governance Action Process Step
GovActionProcessStep::SimplePostgresSurvey::SchemaAndStats

___

## Create Governance Action Process Step
  > A description of a call to perform a step in a governance action process. This acts as a template when creating the appropriate engine action instance.
  
### Display Name
Simple Postgres Survey — Row Count Snapshot
  
### Qualified Name 
GovActionProcessStep::SimplePostgresSurvey::RowCountSnapshot
                                                                                                                                                                                                                                                                                          
### Additional Properties                                                                                                                                                                                                                                                               
| Parameter Name | Parameter Value |                                                                                                                                                                                                                                                    
|---|---|                                                                                                                                                                                                                                                                               
| executes_at | egeria |                                                                                                                                                                                                                                                                
| supported_technology_type | PostgreSQL Database |                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                          
___                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                          
## Link Next Process Step                                                                                                                                                                                                                                                               
### Governance Action Process Step                                                                                                                                                                                                                                                      
GovActionProcessStep::SimplePostgresSurvey::SchemaAndStats                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                          
### Next Governance Action Process Step                                                                                                                                                                                                                                                 
GovActionProcessStep::SimplePostgresSurvey::RowCountSnapshot                                                                                                                                                                                                           
                                                                                                                                                         
        
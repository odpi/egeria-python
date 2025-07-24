
# Family: Glossary

## **Attach Category Parent**
>	Attaches a parent category to a child category.
### **Category Name**
>	**Input Required**: True

>	**Description**: The name of a category.

>	**Alternative Labels**: Glossary Category Name; Glossary Category; Category; Display Name


### **Parent Category**
>	**Input Required**: True

>	**Description**: The name of the parent category to attach to.

>	**Alternative Labels**: Parent Category Name;  Parent Category Names


___

## **Attach Term-Term Relationship**
>	Create a relationship between terms.
### **Term  1**
>	**Input Required**: True

>	**Description**: The name of the first term term to connect.

>	**Alternative Labels**: Term Name 1


### **Term  2**
>	**Input Required**: True

>	**Description**: The name of the second term term to connect.

>	**Alternative Labels**: Term Name 2


### **Relationship**
>	**Input Required**: True

>	**Description**: The type of relationship to connecting the two terms.

>	**Valid Values**: Synonym;  Translation;  PreferredTerm; TermISATYPEOFRelationship;  TermTYPEDBYRelationship;  Antonym; ReplacementTerm;  ValidValue; TermHASARelationship; RelatedTerm;   ISARelationship


___

## **Create Category**
>	A group of terms that are useful to collect together.
### **Category Name**
>	**Input Required**: True

>	**Description**: The name of a category.

>	**Alternative Labels**: Glossary Category Name; Glossary Category; Category; Display Name


### **Description**
>	**Input Required**: False

>	**Description**: A description of the Category.


### **In Glossary**
>	**Input Required**: True

>	**Description**: The name of the glossary that contains the Category. Recommend using the Qualified Name of the Glossary, if known.

>	**Alternative Labels**: Owning Glossary; Glossary; In Glossary


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create Glossary**
>	A grouping of definitions.
### **Glossary Name**
>	**Input Required**: True

>	**Description**: The name of the glossary to create or update.

>	**Alternative Labels**: Glossary; Display Name


### **Description**
>	**Input Required**: False

>	**Description**: A description of the Glossary.


### **Language**
>	**Input Required**: False

>	**Description**: The language of the glossary. Note that multilingual descriptions are supported. Please see web site for details.


### **Usage**
>	**Input Required**: False

>	**Description**: A description of how the glossary is to be used.


### **Qualified Name**
>	**Input Required**: False

>	**Description**: A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.


### **GUID**
>	**Input Required**: False

>	**Description**: A system generated unique identifier.

>	**Alternative Labels**: Guid; guid


___

## **Create Term**
>	
### **Term Name**
>	**Input Required**: True

>	**Description**: The name of the term to create or update.

>	**Alternative Labels**: Glossary Term Name; Display Name; Term


### **Summary**
>	**Input Required**: False

>	**Description**: A summary description of the term.


### **Description**
>	**Input Required**: False

>	**Description**: A description of the term.


### **Abbreviation**
>	**Input Required**: False

>	**Description**: An abbreviation for the term.


### **Example**
>	**Input Required**: False

>	**Description**: An example of how the term is used.


### **Usage**
>	**Input Required**: False

>	**Description**: A description of how the term is to be used.


### **Status**
>	**Input Required**: False

>	**Description**: The lifecycle status of a term.

>	**Valid Values**: DRAFT; ACTIVE, DEPRECATED; OBSOLETE; OTHER

>	**Default Value**: ACTIVE


### **Published Version Identifier**
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

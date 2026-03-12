# Introduction
Executing this file will create a new Egeria glossary called `Egeria-Markdown` if 
it does not already exist. We use this glossary to hold terms describing each Dr.Egeria term.
Once the `Egeria-Markdown` glossary has been created, you can load all the terms by saving
the [generated_help_terms.md](./generated_help_terms.md) file somewhere convenient and then running it 
through Dr.Egeria. One way to do that is using the `dr_egeria_md` command from a terminal window. The command would look like:
```dr_egeria_md --input-file generated_help_terms.md```

Once the Egeria-Markdown glossary has been loaded with these terms, you can use the command `dr_egeria_help` to query
help for particular terms.

Here is the Dr.Egeria command to create the `Egeria-Markdown` glossary.

# Create Glossary  
      
## Glossary Name  
      
Egeria-Markdown  
      
## Language  
      
English  
      
## Description  
      
Glossary to describe the vocabulary of Dr.Egeria - an Egeria Markdown language to support the exchange of metadata in a Markdown form.  
Dr.Egeria allows users to create metadata annotations using any text entry system that supports the entry of standard Markdown  
notation and, through post-processing  
commands, validates the Egeria content and sends the requests to be sent to Egeria.   
      
## Usage  
      
1. (optional) load an example or template for the type of object from Egeria.
> Hint: Many of the hey_egeria commands have the option to save their output as Dr.Egeria markdown form.
2. Create a new document (perhaps from a template) and edit it, adding in the content with the Dr.Egeria controlled Markdown language.  
3. Process the document to validate and display it before you submit it, Validation may annotate your document with recommendations and potential issues.  
4. Submit the document to Egeria using the Dr.Egeria commands. 
5. Review the resulting output document to see what was created and give you a starting point for making updates. 
   
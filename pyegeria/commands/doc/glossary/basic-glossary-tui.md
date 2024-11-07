<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Working with glossaries

## Display glossary List
### Entry
![tui-show glossaries  2024-11-05 at 19.22.49@2x.png](tui-show%20glossaries%20%202024-11-05%20at%2019.22.49%402x.png)
### Display
![glossary-list](out-glossary-list%20example%202024-11-05%20at%2020.41.02%402x.png)
## Create a new Glossary
### Entry
![TUI-create glossary](/Users/dwolfson/localGit/egeria-v5/egeria-python/pyegeria/commands/doc/glossary/tui-create-glossary example 2024-11-05 at 20.34.24@2x.png)

### Display
![create glossary](/Users/dwolfson/localGit/egeria-v5/egeria-python/pyegeria/commands/doc/glossary/out-create-glossary example  2024-11-05 at 20.38.04@2x.png)
## Delete a glossary

### 1. List available glossaries
![delete-glossary-step1 2024-11-06 at 15.47.23@2x.png](delete-glossary-step1%202024-11-06%20at%2015.47.23%402x.png)

### 2. Use TUI to delete a glossary, specifying a glossary GUID from the list glossaries command above
![delete-glossary-step2 2024-11-06 at 15.51.29@2x.png](delete-glossary-step2%202024-11-06%20at%2015.51.29%402x.png)

### 3. View the results of the delete glossary command
![delete-glossary-step3 2024-11-06 at 15.53.19@2x.png](delete-glossary-step3%202024-11-06%20at%2015.53.19%402x.png)

### 4. List glossaries again to see the remaining glossaries
![delete-glossary-step4 2024-11-06 at 15.55.11@2x.png](delete-glossary-step4%202024-11-06%20at%2015.55.11%402x.png)

# Working with terms

## Displaying terms

### Display all terms across all visible glossaries

![tui-show-glossary-terms 2024-11-05 at 19.37.53@2x.png](tui-show-glossary-terms%202024-11-05%20at%2019.37.53%402x.png)

![out-list-all-terms  2024-11-06 at 16.22.20@2x.png](out-list-all-terms%20%202024-11-06%20at%2016.22.20%402x.png)
### Display all terms for a specific glossary

![tui-display-terms-for-example 2024-11-06 at 20.56.49.png](tui-display-terms-for-example%202024-11-06%20at%2020.56.49.png)

![out-create-term 2024-11-06 at 20.48.29.png](out-create-term%202024-11-06%20at%2020.48.29.png)

![out-list-terms-for-example 2024-11-06 at 16.40.12.png](out-list-terms-for-example%202024-11-06%20at%2016.40.12.png)

### Display terms starting with a specified search string
![tui-list-terms-second 2024-11-06 at 16.46.34.png](tui-list-terms-second%202024-11-06%20at%2016.46.34.png)

![out-list-terms-second 2024-11-06 at 16.45.13.png](out-list-terms-second%202024-11-06%20at%2016.45.13.png)

## Create a new term

![tui-create-term 2024-11-06 at 20.46.35.png](tui-create-term%202024-11-06%20at%2020.46.35.png)

![out-display-terms-for-glossary-test 2024-11-06 at 20.51.28.png](out-display-terms-for-glossary-test%202024-11-06%20at%2020.51.28.png)
## Delete a term
![tui-delete-term 2024-11-07 at 03.51.57.png](tui-delete-term%202024-11-07%20at%2003.51.57.png)

![out-delete-term 2024-11-07 at 03.57.25.png](out-delete-term%202024-11-07%20at%2003.57.25.png)

## Import & Export terms 
We can import terms from a CSV formatted file and export terms to a CSV formatted file. 

### Import terms into example glossary

#### First we'll import terms from the file `Test1.om-terms`
![tui-import-terms 2024-11-07 at 08.14.02.png](tui-import-terms%202024-11-07%20at%2008.14.02.png)
Because the *verbose* option is enabled, we will get back a JSON structure reflecting the import status for each row 
in the file. Note that there must be a blank row at the end of the file because we detect a missing term name and skip
that row.
![out-import-terms 2024-11-07 at 08.15.18.png](out-import-terms%202024-11-07%20at%2008.15.18.png)
Listing the glossary terms shows us the results of the import.

![out-list-terms-for-example 2024-11-06 at 16.40.12.png](out-list-terms-for-example%202024-11-06%20at%2016.40.12.png)


### Export terms to a CSV File
Now we will create a copy of this glossary to a CSV file to use it for further demonstrations.
![tui-export-glossary 2024-11-06 at 21.02.16.png](tui-export-glossary%202024-11-06%20at%2021.02.16.png)

![out-terms-export 2024-11-06 at 21.03.24.png](out-terms-export%202024-11-06%20at%2021.03.24.png)

![out-exported-terms 2024-11-06 at 21.06.32.png](out-exported-terms%202024-11-06%20at%2021.06.32.png)

### Demonstrating upsert capability

We will copy the exported file to a new file called **upsert-example.om-terms** and modify the file by
adding a fourth row and updating the description field of one of the terms.

![upsert-example.om-terms 2024-11-07 at 11.44.05.png](upsert-example.om-terms%202024-11-07%20at%2011.44.05.png)

### Upsert

![tui-upsert 2024-11-07 at 11.49.04.png](../tui-upsert%202024-11-07%20at%2011.49.04.png)


----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.
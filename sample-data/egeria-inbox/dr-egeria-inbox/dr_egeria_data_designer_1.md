# Dr.Egeria - designing data - part 2
## Adding information 

As data professionals, we often need to design data to be collected, processed, and shared with others.
The Egeria Data Designer module has been designed to support this. Using the features of data designer we can 
define and refine:

* Data Structures - a composition of data fields (and data structures) that we work with as a unit. For instance, in 
a clinical trial, each measurement record we receive will conform to a data structure.
* Data Fields - the building blocks of data structures - for example, in a clinical trial data structure we might find data fields for health measurements, a time and date when the measurements were made and a patient identifier.
* Data Classes - data classes contain a set of rules that describe the allowable values of a kind of data. For instance, when we we receive new data, perhaps we expect a clinical trial measurement record, then we will often want to validate that it conforms to our expectations; that the value of each field, conforms to the data class specification. 
Similarly, if we receive some data and aren't sure what it is, we can compare the values we have received with this same set of rules to propose what kind of data it might be. 

These are basic building blocks. The following diagram shows how these building blocks come together in a simple example. The ficticious Coco Pharmaceuticals company
is running a drug trial to measure the effectiveness of their experimental treatment of Teddy Bear Drop Foot. Each hospital participating in the trial provides
weekly clinical data records. The clinical trial has established the following data specification to exchange this weekly measurement data.

* A data structure named `TBDF-Incoming Weekly Measurement Data` that is composed of:
  * Data Field: Date 
  * Data Field: PatientId
  * Data Field: AngleLeft
  * Data Field: AngleRight

* The data field `PatientId` is composed of two sub-fields
  * Data Field: HospitalId
  * Data Field: PatientNumber

Dr.Egeria allows us to easily sketch this out, and then refine the definitions incrementally as we work through the design.
So lets begin. First we will define the `TBDF-Incoming Weekly Measurement Data` data structure. We will then Don't Create the new data fields.

___

#  Create Data Structure
## Data Structure Name 

TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient for the Teddy Bear drop foot clinical trial. 

> Note: we will continue to refine this definition as we work through the design.



___
> Note: While not required, it is good practice to end each Dr.Egeria command with a `___` so that a markdown
> seperator is displayed between commands. It improves the readability.
___

# Create Data Field
## Data Field
Date
## Description
A date of the form YYYY-MM-DD

___

#  Create Data Field
## Data Field Name
PatientId
## Description
Unique identifier of the patient

___

#  Create Data Field
## Data Field Name
AngleLeft
## Description
Angle rotation of the left leg from vertical

___

#  Create Data Field
## Data Field Name
AngleRight
## Description
Angle rotation of the left leg from vertical

___

#  Create Data Field
## Data Field Name

HospitalId

## Description
Unique identifier for a hospital. Used in forming PatientId.

___

#  Create Data Field
## Data Field Name
PatientNumber
## Description
Unique identifier of the patient within a hospital.

___
___
# REPORTING
We can also use Dr.Egeria Commands to report on the Data Structures and Data Fields that we just created. Here
we request a simplified list form of the output.
___

# View Data Structures
## Output Format
LIST
___

# View Data Fields
## Output Format
LIST

___
___
# Building on what we have done
One of the interesting features of Dr.Egeria, is that we can take the results of processing a Dr.Egeria command as the
starting point for refining the information we provided. This is convenient, because when we generate the command output,
we transform the `Create` commands into `Update` commands. We also add some additional information that Egeria derived for us.

## Next Steps
For our next steps, we will copy the file produced in the first step into a new file called `dr_egeria_data_designer_2.md` 
Please open that file when you are ready to continue.
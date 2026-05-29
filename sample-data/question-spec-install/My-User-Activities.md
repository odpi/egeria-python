# My-User-Activities

> Install file for the **My-User-Activities** report type question specs.
> Process 00_perspectives.md before this file.

____

# Create Report Type: My-User-Activities

## Create Report Type

### Display Name

My-User-Activities

### Qualified Name

ReportType::My-User-Activities

### GUID

___

____

# Question Spec 1: My-User-Activities::1

## Create Question Spec

### Display Name

My-User-Activities::1

### Qualified Name

QuestionSpec::My-User-Activities::1

### GUID

___

____

# Link Question Spec 1 to Report Type

## Add Member to Collection

### Element Id

QuestionSpec::My-User-Activities::1

### Membership Rationale

Link question spec 1 to My-User-Activities report type.

### Membership Status

VALIDATED

### Collection Id

ReportType::My-User-Activities

____

# Question: Show me my recent activity.

## Create Question

### Display Name

Show me my recent activity.

### Qualified Name

Question::show-me-my-recent-activity

### GUID

___

____

## Add Member to Collection

### Element Id

Question::show-me-my-recent-activity

### Membership Rationale

Add question to My-User-Activities::1.

### Membership Status

VALIDATED

### Collection Id

QuestionSpec::My-User-Activities::1

____

# Link Perspective 'Individual' to Question

## Link Perspective to Question

### Perspective Name

Perspective::Individual

### Question Name

Question::show-me-my-recent-activity

____

# Question: What have I been working on?

## Create Question

### Display Name

What have I been working on?

### Qualified Name

Question::what-have-i-been-working-on

### GUID

___

____

## Add Member to Collection

### Element Id

Question::what-have-i-been-working-on

### Membership Rationale

Add question to My-User-Activities::1.

### Membership Status

VALIDATED

### Collection Id

QuestionSpec::My-User-Activities::1

____

# Link Perspective 'Individual' to Question

## Link Perspective to Question

### Perspective Name

Perspective::Individual

### Question Name

Question::what-have-i-been-working-on

____


# My-User-Blogs

> Install file for the **My-User-Blogs** report type question specs.
> Process 00_perspectives.md before this file.

____

# Create Report Type: My-User-Blogs

## Create Report Type

### Display Name

My-User-Blogs

### Qualified Name

ReportType::My-User-Blogs

### GUID

___

____

# Question Spec 1: My-User-Blogs::1

## Create Question Spec

### Display Name

My-User-Blogs::1

### Qualified Name

QuestionSpec::My-User-Blogs::1

### GUID

___

____

# Link Question Spec 1 to Report Type

## Add Member to Collection

### Element Id

QuestionSpec::My-User-Blogs::1

### Membership Rationale

Link question spec 1 to My-User-Blogs report type.

### Membership Status

VALIDATED

### Collection Id

ReportType::My-User-Blogs

____

# Question: Show me my blog posts.

## Create Question

### Display Name

Show me my blog posts.

### Qualified Name

Question::show-me-my-blog-posts

### GUID

___

____

## Add Member to Collection

### Element Id

Question::show-me-my-blog-posts

### Membership Rationale

Add question to My-User-Blogs::1.

### Membership Status

VALIDATED

### Collection Id

QuestionSpec::My-User-Blogs::1

____

# Link Perspective 'Individual' to Question

## Link Perspective to Question

### Perspective Name

Perspective::Individual

### Question Name

Question::show-me-my-blog-posts

____

# Question: What have I written about?

## Create Question

### Display Name

What have I written about?

### Qualified Name

Question::what-have-i-written-about

### GUID

___

____

## Add Member to Collection

### Element Id

Question::what-have-i-written-about

### Membership Rationale

Add question to My-User-Blogs::1.

### Membership Status

VALIDATED

### Collection Id

QuestionSpec::My-User-Blogs::1

____

# Link Perspective 'Individual' to Question

## Link Perspective to Question

### Perspective Name

Perspective::Individual

### Question Name

Question::what-have-i-written-about

____


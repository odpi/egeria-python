# Egeria User Guide: My Profile Application

The **My Profile Application** (`my_profile_app.py`) is an interactive terminal-based user interface (TUI) powered by Egeria. It is designed for business users, data citizens, data analysts, team leaders, and governance professionals to manage personal governance profiles, track daily activities, collaborate on governance artifacts, and discover organizational data assets.

---

## Target Audience & User Personas

This application is tailored for business roles within an organization that uses Egeria as its open metadata and governance platform:

- **Business Analysts & Data Citizens**: Search glossaries, explore business terms, browse digital data catalogs, and subscribe to data assets.
- **Team Leaders & Project Managers**: View team membership, oversee project assignments, manage governance roles, and track team activities.
- **Governance Officers & Stewards**: Add and manage governance to-dos, document insights via blogs and journals, comment on metadata elements, and trigger automated catalog templates.

> **Note:** Modification screens (`EditElementsScreens.py`) are currently under construction and are not covered in this guide.

---

## Getting Started & Profile Initialization

### Application Startup & Authentication

When the application launches, it automatically loads configuration settings and establishes a secure connection to the Egeria View Server:

1. **Authentication**: Authenticates using the configured user credentials (such as `user_name` and `user_password`).
2. **Profile Retrieval**: Retrieves the user's actor profile and contribution records from Egeria using the `My-User-MD` specification.
3. **Karma Points & Reputation**: Calculates and displays the user's active **Karma Points**, recognizing contributions to the metadata ecosystem.

### First-Time User: Profile Creation

If no existing profile is found for your account in Egeria, the application automatically launches the **Create Profile** modal dialog (`CreateProfileScreen.py`).

| Field | Description | Example / Format |
| :--- | :--- | :--- |
| `Courtesy Title` | Preferred formal title | `Dr.`, `Ms.`, `Mr.` |
| `Given Names` | First / given names | `Gary` |
| `Family Name` | Surname / last name | `Geeke` |
| `Preferred Name` | Preferred display name | `Gary Geeke` |
| `Pronouns` | Personal pronouns | `he/him`, `they/them` |
| `Job Title` | Professional role in organization | `Lead Data Architect` |
| `Description` | Brief summary of role and responsibilities | `Responsible for enterprise data modeling` |
| `Employee ID` | Organization employee identifier | `EMP-10492` |
| `Preferred Language` | Language for system interactions | `en-US` |
| `Resident Country` | Country of employment / residence | `United Kingdom` |
| `Time Zone` | Working time zone | `Europe/London` |

Click **Create Profile** or submit the form. Egeria creates your `Person` entity and anchors your user profile. If you cancel or encounter an issue, press `q` to dismiss.

---

## Main Dashboard Layout & Workspace Structure

The main dashboard (`MainScreen.py`) organizes all user-relevant metadata into clean, scrollable containers:

```
+-------------------------------------------------------------------------------+
| Header: Egeria - My Profile | User: <user_name> (Karma Points: <points>)     |
+------------------------------------+------------------------------------------+
| User Associations                  | My Collections                           |
| - Community & project ties         | - Personal collections of assets         |
+------------------------------------+------------------------------------------+
| Other Functions                    | Roles                                    |
| [1] User Identities                | - Assigned governance & business roles   |
| [2] Catalogs/Shop for Data         | - Drill-down to team members             |
| [3] Technology Types               |                                          |
+------------------------------------+------------------------------------------+
| Teams                              | Activities & Note Logs                   |
| - Teams and departments            | - Blogs (published articles)             |
|                                    | - Journal (personal work log)            |
|                                    | - To-Dos (pending tasks)                 |
+------------------------------------+------------------------------------------+
| User Identity                                                                 |
| - Digital identifiers & distinguished names across metadata repositories      |
+-------------------------------------------------------------------------------+
| Footer: Global Keyboard Shortcuts & Status Indicators                         |
+-------------------------------------------------------------------------------+
```

### Dashboard Data Sections

- **User Associations**: Displays communities, initiatives, and working groups the user is associated with.
- **My Collections**: Lists personal asset collections and pinned resource groupings.
- **Roles**: Shows formal roles assigned to the user (e.g., `TeamLeader`, `DataSteward`, `BusinessAnalyst`).
- **Teams**: Displays departments, squads, and operational units where the user is a member.
- **Activities (Blogs, Journal, To-Dos)**:
  - **Blogs**: Published articles and knowledge-sharing entries.
  - **Journal**: Private or internal work log entries with timestamps.
  - **To-Dos**: Assigned action items, tasks, and governance workflows with activity statuses.
- **User Identity**: Identity mappings linking user accounts to directory services and repository platforms.
- **Other Functions**: Quick-access navigation menu to specialized workspaces.

---

## Keyboard Navigation & Global Shortcuts

The My Profile application provides rapid keyboard-driven navigation:

| Key Binding | Action | Scope | Description |
| :--- | :--- | :--- | :--- |
| `q` | **Quit** | Global | Exits the application or dismisses the current modal window. |
| `r` | **Refresh Data** | Global | Reloads profile data, activities, and tables from Egeria. |
| `ctrl+s` | **Show Comments** | Main Screen | Opens the comment thread for the currently highlighted table row. |
| `ctrl+t` | **Add To-Do** | Main Screen | Opens the quick-creation dialog for a new To-Do item. |
| `ctrl+b` | **Add Blog** | Main Screen | Opens the creation dialog for a new Blog post. |
| `ctrl+j` | **Add Journal** | Main Screen | Opens the creation dialog for a new Journal entry. |
| `ctrl+c` | **Add Association** | Main Screen | Links the profile to a Community or Project. |
| `ctrl+r` | **Add Role** | Main Screen | Creates and assigns a new governance role. |
| `ctrl+g` | **Add Team** | Main Screen | Creates a new Team structure. |
| `ctrl+m` | **Add Collection**| Main Screen | Creates a new asset collection. |
| `ctrl+e` | **Toggle Twisties**| Trees | Expands or collapses all nodes in hierarchical trees. |
| `Escape` / `b` | **Back / Exit** | Modals | Closes the current modal dialog and returns to the previous screen. |

---

## Managing User Activities & Adding Elements

The application includes dedicated quick-entry dialogs (`AddToElementsScreens.py`) to create new items without needing complex scripts:

### 1. Adding a To-Do Item (`ctrl+t`)
- **Fields**:
  - `Name of Todo`: Clear summary of the required task.
  - `Description of Todo`: Detailed instructions or requirements.
  - `Priority of Todo`: Priority indicator (e.g., `High`, `Medium`, `Low`).
  - `Link Todo to your profile?`: Toggle switch (defaults to `True`) to anchor the task to your active profile.
- **Behavior**: New To-Dos are automatically created with status `REQUESTED` and linked directly to your Egeria profile.

### 2. Adding a Blog Entry (`ctrl+b`)
- **Fields**:
  - `Blog Title`: Title for the knowledge post.
  - `Qualified Name`: Unique system identifier for the blog entry.
  - `Blog Entry Text`: Detailed markdown or plain-text body of the post.
  - `Link to Blog?`: Switch to associate the entry with an existing blog channel.

### 3. Adding a Journal Entry (`ctrl+j`)
- **Fields**:
  - `Journal Name`: Title or identifier for the journal log.
  - `Journal Entry Text`: Detailed notes or work summary.
  - `Link to Profile`: Automatically anchors the entry with the current timestamp.

### 4. Adding a Community (`AddCommunityScreen`)
- **Fields**:
  - `Community Name`: Display name for the community of practice.
  - `Community Description`: Mission and purpose of the community.
  - `Community Category`: Functional group or business area.
  - `Assignment Type`: User membership level (e.g., `Leader`, `Member`, `Contributor`).
  - `Community Mission`: Strategic objectives.

### 5. Adding a Project (`AddProjectScreen`)
- **Fields**:
  - `Project Name`: Name of the project or initiative.
  - `Project Description`: Goals and deliverables.
  - `Project Category`: Type of project (e.g., `Governance`, `Data Migration`, `Analytics`).
  - `Project Status`: Initial project state (e.g., `PROPOSED`, `ACTIVE`).
  - `Start Date` / `End Date`: Planned execution timeline.

### 6. Adding a Role (`ctrl+r`)
- **Fields**:
  - `Role Name`: Functional title (e.g., `Data Steward - Finance`).
  - `Role Type`: Egeria role type specification.
  - `Role Description`: Responsibilities and delegation authority.
  - `Scope`: Department, business domain, or organizational unit.
  - `Appointed Actor`: Target user or profile appointed to the role.

---

## Collaboration & Element Comments

Egeria supports collaborative feedback on any metadata element across the dashboard via `ShowCommentsScreen.py`:

```
+-------------------------------------------------------------+
| Show Comments: roles_table (Target: Finance Data Steward)   |
+-------------------------------------------------------------+
| [Comment 1] Question: Should this role oversee raw feeds?   |
| [Comment 2] Answer: Yes, raw feeds fall under ingestion.    |
+-------------------------------------------------------------+
| Add Comment: [ Enter comment text...                      ] |
| Comment Type: [ Question | Answer | Suggestion | Requirement]
| [ Add Comment (ctrl+a) ]                                    |
+-------------------------------------------------------------+
```

### Viewing Comments
1. Highlight any row in any table (e.g., Roles, Projects, Teams, Collections).
2. Press `ctrl+s`.
3. The system extracts the element's unique `GUID` or `Qualified Name` and retrieves all attached discussion threads using Egeria's `Comment-by-Element` service.

### Adding a Comment
1. In the comments view, press `ctrl+a` or navigate to the input container.
2. Enter your comment text.
3. Specify a valid **Comment Type**:
   - `Question`: Ask for clarification or metadata details.
   - `Answer`: Provide a resolution to an open question.
   - `Suggestion`: Propose enhancements or governance adjustments.
   - `Requirement`: Specify mandatory compliance or data quality conditions.
4. Click **Add**. The comment is immediately attached to the element in Egeria.

---

## Team & Role Exploration

The **My Team** view (`MyTeamScreen.py` & `team_roles_handler.py`) enables managers and team leads to explore their organizational structure directly from the dashboard:

1. **Role Selection**: In the **Roles** table on the main screen, highlight and select any role marked with `TeamLeader` or `TeamMember`.
2. **Dynamic Member Resolution**: The system queries Egeria for the associated department or team structure.
3. **Team Roster Display**:
   - **Header**: Shows Team Display Name, Qualified Name, Category, and Description.
   - **Roster Table**: Lists all team members, their individual assigned roles, and their personal `GUID`s.
4. **Navigation**: Press `b` to return to the main dashboard or `q` to dismiss.

---

## Data Shopping & Catalog Explorer

The **Catalogs / Shop for Data** workspace (`ShopForDataScreen.py`, `SelectionOverviewScreen.py`, `SearchForTermScreen.py`, and `CreateSubscriptionRequestScreen.py`) is a discovery hub for data assets.

```
+---------------------------------------------------------------------------------+
| Shopping for Data: Category - Digital Product Catalog                           |
+---------------------------------------+-----------------------------------------+
| Data Hierarchy Tree                   | Metadata & Specifications Details       |
| v Customer 360 Product Family         | # Customer 360 Analytics Product        |
|   > Daily Customer Churn Score        | **Status**: Active                      |
|   v Verified Customer Profiles        | **Owner**: Marketing Analytics Team     |
|     - Raw Ingestion Table             | **SLA**: 99.9% Availability             |
|                                       +-----------------------------------------+
|                                       | Sample Data Preview                     |
|                                       | | CustID | Status   | Tier | Activity | |
|                                       | | 10091  | Active   | Gold | 2026-08  | |
+---------------------------------------+-----------------------------------------+
| Actions: [s] Subscribe to Data Source | [b] Go Back | [q] Quit                  |
+---------------------------------------------------------------------------------+
```

### 1. Selecting a Data Source Category
Selecting **Catalogs/Shop for Data** from the *Other Functions* menu presents 5 data categories:
- **Glossaries**: Authoritative business terminology, definitions, and hierarchies.
- **Digital Product Catalogs**: Packaged data products and product families.
- **Data Dictionaries**: Structural data dictionaries and schema definitions.
- **Business Domains**: Enterprise business capabilities and domain mappings.
- **Root Collections**: Asset collections and curated resource groups.

### 2. Interactive Selection & Hierarchical Tree
Selecting any item opens the **Selection Overview Screen**:
- **Navigation Tree**: Browse categories, nested products, and sub-assets. Press `ctrl+e` to expand or collapse all branches.
- **Metadata Details**: Displays rich Markdown-formatted descriptions, ownership metadata, and technical attributes.
- **Data Samples**: Displays sample records for digital products to verify fitness for use before requesting access.

### 3. Searching for Glossary Terms (`SearchForTermScreen`)
- Access keyword-based term discovery.
- Enter search terms to find matching glossary definitions across the entire catalog.
- Displays comprehensive term definitions, status, examples, and relationships.

### 4. Subscribing to Data Assets (`CreateSubscriptionRequestScreen`)
When viewing an asset or digital product in the Selection Overview:
1. Press `s` (**Subscribe to Data Source**).
2. Enter a **Display Name** for your subscription request.
3. Optionally specify a **Subscription Status** (e.g., `DRAFT`, `PROPOSED`, `ACTIVE`, `APPROVED`).
4. Press `c` (**Create Subscription**) to submit your access request to Egeria.

---

## Technology Types & Governance Automation

The **Technology Types** suite (`TechnologyTypeScreens.py` & `tech_types_handler.py`) allows business and technical users to explore supported technologies and execute automated governance actions:

```
+-------------------------------------------------------------------------------+
| Technology Type: PostgreSQL Database                                          |
+-------------------------------------------------------------------------------+
| Available Templates                     | Available Processes                 |
| [1] Standard Relational Database Schema | [1] Scan Schema & Profile Assets    |
| [2] Audited Secure Database Instance    | [2] Classify Confidential Data      |
| [ Select Template ]                     | [ Select Process ]                  |
+-----------------------------------------+-------------------------------------+
| Dynamic Parameter Configuration:                                              |
| Hostname: [ db.prod.internal.net ]                                            |
| Port:     [ 5432                 ]                                            |
| Database: [ analytics_prod       ]                                            |
| [ Submit Action ]                                                             |
+-------------------------------------------------------------------------------+
```

1. **Technology Types Hierarchy**: Navigate through technologies (e.g., Databases, Data Lakes, Kafka Topics, Cloud Storage).
2. **Templates & Processes Discovery**:
   - **Catalog Templates**: Reusable asset templates that preconfigure connectors, classifications, and relationships.
   - **Governance Action Processes**: Pre-built governance workflows (such as profiling, lineage extraction, and quality verification).
3. **Dynamic Parameter Forms**:
   - Selecting a template or process dynamically builds an input form based on its required request parameters.
   - Each parameter shows its **Name**, **Data Type**, **Description**, **Example Value**, and whether it is **Required**.
4. **Execution**: Fill in the parameter values and click **Submit Action** to trigger the automated governance pipeline in Egeria.

---

## User Identities & Account Mappings

The **User Identities Screen** (`UserIdentitiesScreen.py`) gives users full visibility into their mapped security and directory credentials across the enterprise:

- Accessible via **Other Functions -> User Identities**.
- Displays a structured table containing:
  - **Display Name**: Identity moniker.
  - **User ID**: System account identifier.
  - **Distinguished Name (DN)**: LDAP / Active Directory full path.
  - **Category & Type Name**: Identity classification.
  - **Metadata Collection Name & ID**: Home repository where the identity originates.
  - **GUID**: Unique identifier in Egeria.

---

## Status Reporting & Clipboard Integration

All operations that create or modify metadata communicate outcomes through the **Status Screen** (`StatusScreen.py`):

- **Status Message Area**: Displays structured feedback, success confirmation, or backend diagnostic information.
- **Copy GUID to Clipboard (`c` key)**: When an element is created or retrieved, pressing `c` extracts its `GUID` and copies it directly to your system clipboard for use in other tools, CLI commands, or documentation.
- **Completion Actions**: Press `Enter` to continue, `b` to report a bad result, or `q` to dismiss.

---

## Summary of Business User Workflows

```
                           +------------------------+
                           | Launch My Profile App  |
                           +-----------+------------+
                                       |
                     +-----------------+-----------------+
                     |                                   |
           [ Profile Exists ]                  [ First-Time User ]
                     |                                   |
                     v                                   v
        +-------------------------+         +-------------------------+
        |     Main Dashboard      |         |  Create Profile Modal   |
        +------------+------------+         +-------------------------+
                     |
  +------------------+-------------------+--------------------+------------------+
  |                  |                   |                    |                  |
  v                  v                   v                    v                  v
+-----------+  +---------------+   +------------+      +---------------+  +---------------+
| Activities|  | Collaboration |   | Team View  |      | Shop for Data |  | Tech Types    |
| - To-Dos  |  | - View / Add  |   | - Roster   |      | - Glossaries  |  | - Templates   |
| - Blogs   |  |   Comments    |   | - Roles    |      | - Catalogs    |  | - Governance  |
| - Journal |  |   (ctrl+s)    |   | - GUIDs    |      | - Subscribe   |  |   Processes   |
+-----------+  +---------------+   +------------+      +---------------+  +---------------+
```

The **My Profile Application** provides a unified, keyboard-friendly command center for all your daily Egeria data stewardship and governance responsibilities. Use it to keep your activities current, discover organizational data, collaborate with team members, and drive automated governance across your enterprise.

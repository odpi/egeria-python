<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# My Profile App User Manual

The **My Profile App** is a terminal user interface (TUI), built with [Textual](https://textual.textualize.io/) and the `pyegeria` SDK, that gives an Egeria user a personal dashboard: their profile, roles, teams, communities, blogs, journal, to-dos and user identities, plus access to comments, feedback, data shopping, subscriptions, technology types and their network of peers.

This manual describes how to *use* the app. For how it works internally (screens, handlers, Egeria calls and flow diagrams) see the [My Profile Reference Guide](My-Egeria-Doc.md).

The app's source is in `my_egeria/my_egeria/DemoCode/My_Profile/`.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Starting the App](#starting-the-app)
4. [The Splash Screen and Changing User](#the-splash-screen-and-changing-user)
5. [When Egeria Can't Be Reached](#when-egeria-cant-be-reached)
6. [Creating Your Profile](#creating-your-profile)
7. [The Main Screen](#the-main-screen)
8. [Adding and Deleting Elements](#adding-and-deleting-elements)
9. [Comments and Threaded Responses](#comments-and-threaded-responses)
10. [Leaving Feedback](#leaving-feedback)
11. [Other Functions Menu](#other-functions-menu)
12. [Keyboard Reference](#keyboard-reference)
13. [Exit and Return Codes](#exit-and-return-codes)
14. [Troubleshooting](#troubleshooting)
15. [Known Limitations](#known-limitations)
16. [Running the Tests](#running-the-tests)

---

## Prerequisites

- **Python 3.12+**, with this repository's dependencies installed (`uv sync`, then `source .venv/bin/activate`).
- **pydantic 2.12.3 or later.** The app checks this at startup and exits with code `430` if an older version is found. This most often happens when the app is launched with a globally installed `textual` rather than the project's virtual environment.
- A running **Egeria platform** with a **view server** (for example `qs-view-server`), and a user ID and password for it.

## Configuration

The app uses the standard `pyegeria` configuration. Precedence is: environment variables, then a `.env` file, then `config.json`, then built-in defaults.

### Environment variables

```bash
EGERIA_PLATFORM_URL=https://localhost:9443
EGERIA_VIEW_SERVER=qs-view-server
EGERIA_USER=your_user_id
EGERIA_USER_PASSWORD=your_password
```

### `config.json`

`config.json` is looked for in `$PYEGERIA_CONFIG_DIRECTORY`, then `$PYEGERIA_ROOT_PATH`, then the current working directory. The file name can be changed with `PYEGERIA_CONFIG_FILE`.

```json
{
  "Environment": {
    "Egeria Platform URL": "https://localhost:9443",
    "Egeria View Server": "qs-view-server"
  },
  "User Profile": {
    "user_name": "your_user_id",
    "user_pwd": "your_password"
  }
}
```

If no user or server is configured, the app falls back to user `garygeeke`, password `secret`, view server `qs-view-server` and platform `https://127.0.0.1:9443`.

## Starting the App

From the app folder, inside the project's virtual environment:

```bash
my_profile                 # installed console script, runs from any directory
# or, from the app folder:
cd my_egeria/my_egeria/DemoCode/My_Profile
python my_egeria.py
# or, with the Textual developer console (needs textual-dev, a dev dependency):
textual run --dev my_egeria.py
```

Use Python 3.13: Textual currently fails on Python 3.14 (an assertion in `textual/rlock.py` at startup).

The app's own diagnostic messages (its `self.log(...)` calls) are commented out, so the developer console shows only Textual's messages. To trace a problem, uncomment the ones you need in the source.

To serve the app in a web browser instead of a terminal:

```bash
serve_my_profile          # textual-serve on $MY_EGERIA_HOST:$MY_PROFILE_PORT (default 0.0.0.0:8020)
```

Behind a reverse proxy, set `MY_PROFILE_PUBLIC_URL` (or `MY_EGERIA_PUBLIC_URL`) to where the app is published, e.g. `https://localhost:8843/my-egeria`. Only its path (and default scheme) is used: the host in the page's asset and WebSocket URLs follows the address each browser actually used, so the same setting works from `localhost`, the machine's name or a demo hostname.

## The Splash Screen and Changing User

When the app starts it shows a welcome card ("Welcome to My_Profile for Egeria Users, *user*!") while your profile loads from Egeria in the background.

- **Continue to App** (or `Escape`) closes the splash screen. If your profile was found, the main screen is already populated; if not, the app offers to create one (see below).
- **Change User** opens the **Change User** screen (below). If you cancel it you are back on the splash screen.

### The Change User screen

You can switch to a different Egeria user at any time: from the splash screen's **Change User** button, from **Change User** in the main screen's Other Functions menu, or from the [connection error screen](#when-egeria-cant-be-reached).

The screen shows who you are logged in as, with *User Name* and *Password* fields. Press `Enter` in the user name field to move to the password; `Enter` in the password field (or **Submit**) submits. Both fields are required.

Before switching, the app asks Egeria to log in with the new user and password. If Egeria can't be reached or rejects them, a message says why and you stay on the screen to correct them. Once Egeria accepts them, the app discards the current profile and reloads everything for the new user; the header shows the new user ID, with Karma Points of 0 until their profile has loaded. Every screen opened afterwards, and any pyegeria command started from the app, runs as the new user.

**Cancel** (or `Escape`) closes the screen without changing anything.

## When Egeria Can't Be Reached

If the app can't load your profile at startup, because the Egeria platform isn't running or doesn't answer, or because it rejects your user ID and password, it doesn't exit. It shows a **connection error screen** instead, with:

- the platform URL, view server and user it tried;
- the reason, in red (for example *Unable to connect to the Egeria platform at https://localhost:9443.*, or Egeria's own message when the credentials are rejected);
- a countdown to the next attempt and the number of attempts so far.

The app tries again every 10 seconds. As soon as Egeria accepts your credentials, the screen closes and your profile loads; if you have no profile yet, the app offers to create one. So you can start the app first and your Egeria instance afterwards.

| Button | Key | Action |
| :--- | :--- | :--- |
| **Retry Now** | `r` | Try again straight away |
| **Change User** | `u` | Open the [Change User screen](#the-change-user-screen). If you cancel it, you return to the connection error screen |
| **Quit** | `q` | Exit the app (code `402`) |

## Creating Your Profile

If Egeria has no profile for your user, the **Create Profile** screen opens. Fill in:

| Field | Example |
| :--- | :--- |
| Courtesy Title | `Dr.` |
| Given Names | `Gary` |
| Family Name | `Geeke` |
| Preferred Name | `Gary Geeke` |
| Pronouns | `they/them` |
| Job Title | `Lead Data Architect` |
| Description | `Responsible for enterprise data modelling` |
| Employee ID | `EMP-10492` |
| Preferred Language | `en-US` |
| Resident Country | `United Kingdom` |
| Time Zone | `Europe/London` |

Press **Create Profile**. Egeria creates your `Person` profile, and the app reloads and shows the main screen. If creation fails or is cancelled, the app exits (code `403`).

## The Main Screen

The header reads **Egeria — User: _your user ID_, Karma Points: _n_**. Karma Points are your contribution score in Egeria, and they show as 0 until your profile has loaded. Every other screen has the same header, with the screen's name after "Egeria", for example **Egeria - Communities — User: garygeeke, Karma Points: 135**. The panels are:

| Panel | Columns | Contents |
| :--- | :--- | :--- |
| **User Associations** | Status or Type, Name, Description, GUID | The communities you belong to |
| **My Collections** | Collection Name, Collection Description, Collection GUID | Collections you created (your bookmarks collection is not listed here) |
| **Other Functions** | – | A menu of further features ([below](#other-functions-menu)) |
| **Roles** | Role Name, Role Type, Description, GUID | Roles you have been appointed to. Press `Enter` on a TeamLeader or TeamMember role (or click it a second time) to see the other people in that team |
| **Teams** | Assignment Type, Team Name, Description, GUID | Teams you are a member of |
| **Blogs** | Blog Title, Date, Text, GUID | Your blog entries |
| **Journal** | Journal Entry, Date, Text, GUID | Your journal entries |
| **To-Dos** | To-Do Name, Activity Status, Description, GUID | Your to-dos |
| **User Identity** | Display Name, User ID, Distinguished Name, GUID | User identities linked to your profile |
| **Projects** | Status or Type, Name, Description, GUID | Projects you are involved in |

Click or move into a table to select it; the highlighted row is the "selected row" used by the shortcuts below. Press `ctrl+r` to reload everything from Egeria. The app also reloads automatically when you close an Add screen.

**Seeing your team.** Selecting a TeamLeader or TeamMember role in the Roles table (for example `TeamLeader::Department::0010`) opens the **My Team** screen, which lists the team's members and their assignment types; press `Escape` to return. Selecting any other role shows a warning that it is not a team role. If Egeria returns no members for the team, or the lookup fails, a message says so.

Main screen shortcuts:

| Key | Action |
| :--- | :--- |
| `ctrl+t` | **Edit Selected Table** – opens the edit screen for the selected table, where you add and delete rows |
| `ctrl+o` | **Show Comments** for the selected row |
| `ctrl+n` | **Add Comment** to the selected row |
| `ctrl+k` | **Bookmark** the element in the selected row |
| `ctrl+b` | **Manage Bookmarks** |
| `ctrl+r` | Refresh all data from Egeria |
| `ctrl+f` | Leave feedback (works on every screen) |
| `q` | Quit the app |

## Adding and Deleting Elements

Adding and deleting both go through the table's **edit screen**:

1. On the main screen, select a table and press `ctrl+t`.
2. The edit screen shows a copy of that table. Then:
   - `ctrl+n` – **Add Row**: opens the Add screen for that kind of element.
   - `ctrl+d` – **Delete Row**: asks you to confirm, then deletes the highlighted element from Egeria. The row is removed only if Egeria accepts the delete. You can delete one row at a time.
   - `Escape` – back to the main screen.

Edit screens add and delete; they do not edit a row's values in place. To change your own details use **Edit Profile** from the Other Functions menu.

### Add screens

Every Add screen works the same way:
- Fill in the fields. Those marked \* are required.
- Press **Add** (or `ctrl+s`).
- Some screens have a switch that links the new element to you. It is on by default.

If a required field is missing or a value is invalid, the screen tells you which one. After a successful add the form is cleared, so you can add another; after a failed add your input is kept so you can correct it. Press **Quit** (or `Escape`) to close the screen. You go back to the main screen and the data is reloaded.

| Table | Fields | Link switch | Egeria result |
| :--- | :--- | :--- | :--- |
| To-Dos | Name\*, Description\*, Priority (whole number, default 0) | – | A to-do assigned to you, status `REQUESTED` |
| Blogs | Name\*, Text\*, Situation | – | An entry in your blog |
| Journal | Title\*, Text\*, Situation | – | An entry in your journal |
| User Associations | Choose **Project** or **Community**, then that screen opens | | |
| Projects | Name\*, Description\*, Kind (`Project`, `Campaign`, `StudyProject`, `Task`, `PersonalProject`; default `Project`), Identifier, Start Date and Planned End Date (`YYYY-MM-DD`) | Add yourself to the project team | A project |
| Communities | Name\*, Description\* | – | A community. You are not made a member; to create a community and join it in one step, use **Create Community** in [Work with Communities](#work-with-communities) |
| Roles | Name\*, Description\* | Appoint yourself to this role | A person role |
| Teams | Name\*, Description\* | Join this team as a member | A team; joining creates a TeamMember role for you, scoped to the team |
| My Collections | Name\*, Description\*, Category | – | A standalone collection |
| User Identity | User ID\*, Display Name, Distinguished Name | Link to your profile | A user identity |

## Comments and Threaded Responses

Comments can be attached to any element in a main-screen table, and responses can be attached to comments to any depth.

**Add a comment from the main screen:** select a row, press `ctrl+n`, enter the comment and a comment type (`Question`, `Answer`, `Suggestion` or `Requirement`), then press **Submit** (`ctrl+s`).

**View and reply:** select a row and press `ctrl+o`. The comments screen lists the comments on that element.

- `ctrl+n` adds a new comment to the element being shown.
- `ctrl+o` on a highlighted comment re-opens the screen focused on *that comment*, showing its responses. Here `ctrl+n` adds a response. Repeat to go deeper into a thread.
- `Escape` or `q` closes the screen.

If an element has no comments yet, the screen tells you to use `ctrl+n`.

## Leaving Feedback

Press `ctrl+f` on **any** screen, or choose **Leave Feedback** from the Other Functions menu. Pick a category (Bug, Suggestion, Question, Praise, Other), type your feedback, and press **Submit** (`ctrl+s`). `Escape` cancels.

The app records which screen you were on, your user ID and the time, and stores the feedback as a note in a shared "My Profile App Feedback" note log in Egeria.

The **feedback log** (`F3`, or **Feedback Log** in the menu) lists all feedback, newest first. It is only available to the app's feedback owner, `garygeeke`; other users are told the log is private. This restriction is enforced by the app, not by Egeria.

## Other Functions Menu

### User Identities
A read-only table of your user identities: display name, category, description, type, URL, GUID, qualified name, metadata collection ID and name, user ID and distinguished name. Press `q` or `Escape` to return.

### Catalogs/Shop for Data
Opens a screen with five tables, each loading in the background: **Glossaries**, **Digital Product Catalog**, **Data Dictionaries**, **Business Domains** and **Root Collections**.

- **Enter** (or click) on a row opens an **overview** screen: a tree on the left and details on the right. Selecting a tree node shows its details – glossary terms, digital products (including sample data), dictionaries, business capabilities or collections.
- `ctrl+l` – show sample data for the highlighted row.
- `ctrl+u` – subscribe to the highlighted item.
- `ctrl+g` – search glossary terms. `Escape` from the search returns to Shop for Data.
- `ctrl+k` – bookmark the highlighted item; `ctrl+b` – open bookmarks with its GUID ready to add.
- `Escape` or `q` – back to the main screen.

On the overview screen, `ctrl+u` subscribes to the selected node, `Escape` goes back and `q` returns to the main screen. On a sample-data view, `ctrl+u` subscribes, `Escape` goes back to Shop for Data and `q` returns to the main screen.

**Subscribing**, from any of these screens, opens the **Create Subscription Request** form. It has Display Name, Description, Identifier and Status (`DRAFT`, `PROPOSED` or `ACTIVE`; an invalid value becomes `DRAFT`). Press `ctrl+s` to create the digital subscription in Egeria (`Escape` cancels). The subscription is linked to the item you chose and to you as its subscriber. If either link can't be made, a warning says so; the subscription itself is still created.

### Edit Profile
A form pre-filled with your profile details (courtesy title, job title, given names, surname, preferred name, pronouns, description, time zone, employee ID, preferred language, resident country). Press **Edit Profile** (or `ctrl+s`) to save. The screen also has shortcuts that open the Communities (`ctrl+g`), Identities (`ctrl+l`), Roles (`ctrl+r`) and Teams (`ctrl+t`) edit screens. Press `Escape` to return.

### Subscriptions
A table of the digital subscriptions you created: name, status, description and GUID. Press `Escape` or `q` to return.

### Technology Types
Browse the technology type hierarchy as a tree. Selecting a type shows its **catalog templates** and **governance action processes**:

- **Templates:** pick one and press **Select Template**. Fill in its placeholder values and submit. Egeria creates a new element from the template, and a **status screen** shows the result.
- **Processes:** pick one and press **Select Process**, then fill in its request parameters and submit. Only the parameters you fill in are sent. Egeria starts the governance action process, and a **status screen** shows its GUID.

On the status screen, `ctrl+y` copies the GUID shown to your clipboard, and `Enter`, `Escape` or `q` closes it and returns you to the main screen.

### User Bookmarks
Opens the bookmarks screen (also `ctrl+b` on the main screen and on Shop for Data). It lists your bookmarks (name, type, GUID).

The easiest way to add a bookmark is from a table: select a row and press `ctrl+k` on the main screen, or highlight a row and press `ctrl+k` on Shop for Data. Any row that has a GUID can be bookmarked, and so can a glossary row, which is identified by its qualified name. Bookmarking something that is already bookmarked just tells you so.

On the bookmarks screen:
- `ctrl+n` shows a field for the GUID of an element to bookmark. If you opened the screen with `ctrl+b` while a row was highlighted, that row's GUID is already filled in; otherwise copy a GUID from any table, or with `ctrl+y` on a status screen.
- `ctrl+d` removes the highlighted bookmark (the element itself is not deleted).
- `Escape` or `q` returns.

Your bookmarks are kept in Egeria as the members of your private **My Bookmarks** collection (qualified name `Bookmarks::<your user id>`), and only that collection. It is created the first time you bookmark something, anchored to your profile and linked from it with a `ResourceList` relationship whose resource use is "Bookmarks".

### My Network
Your network is the people linked to your profile in Egeria. The screen lists them (qualified name, display name, full name, pronouns, GUID and the description you gave the link). If your profile has not finished loading, the app tells you to wait and does not open the screen.

- **View details:** highlight a person and press `ctrl+o` (or **Person Details**). A panel shows their **contact methods** and the **communities** they belong to. A message tells you if either is empty.
- **Add someone:** type all or part of a name in the search field and press `Enter`. Up to 10 matching people are listed, leaving out you and anyone already in your network. Select a person, optionally enter a **nickname** and a **description** of your relationship, then press **Add to Network**. **Cancel** clears the selection.
- **Remove someone:** highlight a person and press `ctrl+d` (or **Remove from Network**), then confirm with **Remove**. **Cancel** or `Escape` keeps them. Only the link between you is removed; their profile is not changed.
- `Escape` or `q` returns to the main screen.

Each person in your network is linked to your profile with a `Peer` relationship. The nickname and description are stored on that relationship.

### Work with Communities
The screen lists the communities you belong to (name, assignment type, what links you to it, description and GUID), lets you find others to join, and opens a community to show its members, blog and comments. If your profile has not finished loading, the app tells you to wait and does not open the screen.

- **Linked Through** is **Your profile** if you joined the community yourself, or **Role: _name_** if you belong through a role you hold. A community you reach both ways is listed once.
- **Open a community:** highlight a community in either list and press `Enter`, `ctrl+o` or **Open Community**. See [A community](#a-community) below.
- **Create a community:** press `ctrl+t` (or **Create Community**). Enter a **Name\*** and **Description\***, and optionally a **Mission**, then choose **Your part in it**: **Leader** (the default, since you created it), **Contributor**, **Observer** or **Don't join**. Press `ctrl+s` (or **Create**); **Cancel** or `Escape` discards it. The lists reload and the new community is highlighted: in your communities if you joined it, otherwise in the found list. If a community with that name already exists, you are told to find it and join it instead.
- **Find and join:** type a search term in the search field (`*` for all) and press `Enter`. Communities you already belong to are left out. Choose **Contributor** or **Observer**, highlight a community and press `ctrl+n` (or **Join Community**). Leaders and administrators are assigned by the people who manage the community, not chosen here.
- **Leave:** highlight one of your communities and press `ctrl+d` (or **Leave Community**), then confirm with **Leave**. **Cancel** or `Escape` keeps you in it. Only the link between you and the community is removed. You can't leave a community you belong to through a role; ask whoever manages that role.
- `Escape` or `q` returns to the main screen.

Membership is an `AssignmentScope` relationship from your profile (or a role) to the community, and the assignment type is stored on that relationship.

#### A community
Opening a community shows three lists: its **latest blog posts** (the 20 newest, with title, author and date; the highlighted post's text is shown underneath), its **members** and the **comments** on it, newest first. You don't have to be a member to read or add to them.

The members list shows **people only**, in name order, not roles. It includes everyone linked to the community directly and everyone appointed to a role that is. **Member Through** says how each person belongs: **Direct**, or **Role: _name_** for each role they hold there. A person who belongs in several ways is listed once. Other kinds of member, such as teams, are not shown. If the people in one of the community's roles can't be read, the rest are still listed and a warning says some members may be missing.

- **New blog post:** press `ctrl+n` (or **New Blog Post**), enter a title and the text, then press `ctrl+s` (or **Post**). **Cancel** or `Escape` discards it.
- **Add a comment:** select the comments list and press `ctrl+n` (or press **Add Comment**), choose a comment type (Standard Comment, Question, Answer, Suggestion, Usage Experience, Requirement or Other), enter the comment and press `ctrl+s` (or **Add Comment**).
- `Escape` returns to the communities list; `q` returns to the main screen.

The community's blog is a note log attached to the community, created when the first post is made; each post is a `BlogEntry` in it. Comments are attached to the community itself.

### Change User
Log in as a different Egeria user and reload the app for them. See [The Change User screen](#the-change-user-screen).

### Leave Feedback / Feedback Log
See [Leaving Feedback](#leaving-feedback).

## Keyboard Reference

Every screen follows the same rules:

- `Escape` goes back one level, on every screen except the main screen.
- `q` returns to the main screen, or quits the app when you are on the main screen. Screens that are mostly text fields (Add screens, Add Comment, Create Subscription, Create/Edit Profile, Search for Term, Feedback, New Blog Post, Create Community, Template and Process forms) have no `q`, because it would be typed into the field; use `Escape`.
- Every other action is a `ctrl` key, and a key means the same thing wherever it appears. `ctrl` keys work even while a text field has focus.

| Key | Action | Where |
| :--- | :--- | :--- |
| `Escape` | Back | Every screen except Main; continue on the splash screen; cancel on confirm dialogs and Change User |
| `r` / `u` / `q` | Retry now / Change User / Quit | Connection error screen |
| `q` | Main menu / quit the app | Every list screen / Main screen |
| `Enter` | Select the highlighted row; continue | Tables and trees; Status screen |
| `ctrl+s` | Save / submit the form | Add screens, Add Comment, Create Subscription, Create/Edit Profile, Feedback, New Blog Post, Create Community |
| `ctrl+n` | Add a new item | Edit screens (row), Bookmarks, Comments, Main screen (comment), Communities (join), a community (blog post or comment) |
| `ctrl+d` | Delete / remove the highlighted item | Edit screens, Bookmarks, My Network, Communities (leave) |
| `ctrl+o` | Open the highlighted item | Main screen (comments), Comments (responses), My Network (person details), Communities (open a community) |
| `ctrl+t` | Edit the selected table / create a community | Main screen / Communities |
| `ctrl+k` | Bookmark the highlighted row | Main screen, Shop for Data |
| `ctrl+b` | Bookmarks, with the highlighted row's GUID ready to add | Main screen, Shop for Data |
| `ctrl+u` | Subscribe | Shop for Data, Overview, sample-data view |
| `ctrl+l` | Show sample data | Shop for Data |
| `ctrl+g` | Search glossary terms | Shop for Data |
| `ctrl+e` | Expand / collapse the whole tree | Technology Types |
| `ctrl+y` | Copy the GUID shown | Status screen |
| `ctrl+x` | Close, flagging a bad result | Status screen |
| `ctrl+g` / `ctrl+l` / `ctrl+r` / `ctrl+t` | Edit Communities / Identities / Roles / Teams | Edit Profile |
| `ctrl+r` | Refresh all data from Egeria | Main screen |
| `ctrl+f` | Leave feedback | Any screen |
| `F3` | Show the feedback log | Any screen (feedback owner only) |
| `ctrl+c` | Force quit (terminal) | Anywhere |

## Exit and Return Codes

When the app exits it returns a code; screens also use codes to talk to the app. The common ones are:

| Code | Meaning |
| :--- | :--- |
| `200` | Success / normal exit |
| `201` | Alternative navigation or no match |
| `210` | Quit back to the main screen |
| `211` | Subscribe request |
| `212` | Sample data request |
| `250` | Show responses to a comment |
| `400` / `401` | Generic failure / profile action failed |
| `402` | Egeria could not be reached (or rejected the credentials) and you chose **Quit** on the connection error screen |
| `403` | Profile creation cancelled or failed |
| `412` / `413` | Error / empty result reloading a newly created profile |
| `416` | Technology types could not be fetched |
| `430` | Incompatible Python or pydantic version |
| `440` | Glossary term lookup error |

The full list is in `RETURN_CODES.md` in the app folder.

## Troubleshooting

**The app exits immediately with code 430.** Your environment has an old pydantic, often because a globally installed `textual` was used. Activate the project's `.venv` and run `textual run --dev my_egeria.py` or `python my_egeria.py` from there.

**The connection error screen keeps retrying.** The profile could not be retrieved (`402` if you then quit). The red message says why. Check that:
- `EGERIA_PLATFORM_URL` is correct and reachable (VPN and firewall included) – the screen shows the URL being tried;
- the view server named by `EGERIA_VIEW_SERVER` is running;
- `EGERIA_USER` and `EGERIA_USER_PASSWORD` are correct, and the user is allowed to use the view server. If the credentials are the problem, press **Change User** rather than restarting the app.

**Something I added doesn't appear.** Press `ctrl+r` on the main screen. A community added from the User Associations edit screen is not linked to you (see Known Limitations), so it doesn't appear in User Associations until you join it from **Work with Communities**. One made with **Create Community** there, with yourself as a member, appears after `ctrl+r`.

**The app quit unexpectedly.** The app only exits by itself in a few cases: a startup problem (codes `403`, `430`; `402` only when you press Quit on the connection error screen), a failure fetching technology types (`416`), or an error looking up a glossary term (`440`). A failed team lookup is reported as a message instead.

## Known Limitations

As of 2026-10-30, these features are incomplete or don't work as described elsewhere:

- **Communities added from the User Associations edit screen** are not linked to you. The community is created but won't appear in User Associations until you join it from **Work with Communities**. **Create Community** in Work with Communities does link you.
- **Not yet verified against a live Egeria server:** bookmarks, My Collections, joining a team, subscription links and starting processes. The test server was unavailable when they were added, so they have only been tested against fakes.
- **Work with Communities** has only partly been tried against a live server. Listing your communities, finding communities, creating a community (and joining it as part of that), the members list, and reading and adding blog posts and comments all work there. Leaving a community, joining one from the found list, and the screens themselves have so far only been tested against fakes.

## Running the Tests

The test suite is in `tests/micro-tests/my_profile/`. By default it runs against in-memory fakes, and any real network call fails the test:

```bash
pytest tests/micro-tests/my_profile/
```

Set `PYEG_LIVE_EGERIA=1` to run the same tests against a real Egeria server (default `https://localhost:9443`; override with `PYEG_PLATFORM_URL`, `PYEG_SERVER_NAME`, `PYEG_USER_ID`, `PYEG_USER_PWD`). **Live mode writes to the server.** It creates subscriptions and template elements, and may create a profile. See `tests/micro-tests/my_profile/README.md`.

---

## Related Information

- [My Profile Reference Guide](My-Egeria-Doc.md) – architecture, screens and Egeria calls
- [Egeria Project Documentation](https://egeria-project.org)
- [pyegeria Programming Guide](user_programming.md)
- [Dr.Egeria User Manual](dr_egeria_manual.md)

---
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.

<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# My Profile App User Manual

The **My Profile App** is a terminal user interface (TUI), built with [Textual](https://textual.textualize.io/) and the `pyegeria` SDK, that gives an Egeria user a personal dashboard: their profile, roles, teams, communities, blogs, journal, to-dos and user identities, plus access to comments, feedback, data shopping, subscriptions and technology types.

This manual describes how to *use* the app. For how it works internally (screens, handlers, Egeria calls and flow diagrams) see the [My Profile Reference Guide](My-Egeria-Doc.md).

The app's source is in `my_egeria/my_egeria/DemoCode/My_Profile/`.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Starting the App](#starting-the-app)
4. [The Splash Screen and Changing User](#the-splash-screen-and-changing-user)
5. [Creating Your Profile](#creating-your-profile)
6. [The Main Screen](#the-main-screen)
7. [Adding and Deleting Elements](#adding-and-deleting-elements)
8. [Comments and Threaded Responses](#comments-and-threaded-responses)
9. [Leaving Feedback](#leaving-feedback)
10. [Other Functions Menu](#other-functions-menu)
11. [Keyboard Reference](#keyboard-reference)
12. [Exit and Return Codes](#exit-and-return-codes)
13. [Troubleshooting](#troubleshooting)
14. [Known Limitations](#known-limitations)
15. [Running the Tests](#running-the-tests)

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
python my_profile_app.py
# or, with the Textual developer console (needs textual-dev, a dev dependency):
textual run --dev my_profile_app.py
```

Use Python 3.13: Textual currently fails on Python 3.14 (an assertion in `textual/rlock.py` at startup).

To serve the app in a web browser instead of a terminal:

```bash
serve_my_profile          # textual-serve on $MY_EGERIA_HOST:$MY_PROFILE_PORT (default 0.0.0.0:8020)
```

Behind a reverse proxy, set `MY_PROFILE_PUBLIC_URL` (or `MY_EGERIA_PUBLIC_URL`) to where the app is published, e.g. `https://localhost:8843/my-egeria`. Only its path (and default scheme) is used: the host in the page's asset and WebSocket URLs follows the address each browser actually used, so the same setting works from `localhost`, the machine's name or a demo hostname.

## The Splash Screen and Changing User

When the app starts it shows a welcome card ("Welcome to My_Profile for Egeria Users, *user*!") while your profile loads from Egeria in the background.

- **Continue to App** (or `Escape`) closes the splash screen. If your profile was found, the main screen is already populated; if not, the app offers to create one (see below).
- **Change User** replaces the card with *User Name* and *Password* fields and a **Submit** button. Both fields are required. On submit the app discards the profile it was loading and reloads everything for the new user. Every screen opened afterwards uses the new user.

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

The header shows your full name, user ID and **Karma Points** (your contribution score in Egeria). The panels are:

| Panel | Columns | Contents |
| :--- | :--- | :--- |
| **User Associations** | Status or Type, Name, Description, GUID | The communities you belong to |
| **My Collections** | Collection Name, Collection Description, Collection GUID | Collections you created (your bookmarks collection is not listed here) |
| **Other Functions** | – | A menu of further features ([below](#other-functions-menu)) |
| **Roles** | Role Name, Role Type, Description, GUID | Roles you have been appointed to |
| **Teams** | Assignment Type, Team Name, Description, GUID | Teams you are a member of |
| **Blogs** | Blog Title, Date, Text, GUID | Your blog entries |
| **Journal** | Journal Entry, Date, Text, GUID | Your journal entries |
| **To-Dos** | To-Do Name, Activity Status, Description, GUID | Your to-dos |
| **User Identity** | Display Name, User ID, Distinguished Name, GUID | User identities linked to your profile |
| **Projects** | Status or Type, Name, Description, GUID | Projects you are involved in |

Click or move into a table to select it; the highlighted row is the "selected row" used by the shortcuts below. Press `r` to reload everything from Egeria. The app also reloads automatically when you close an Add screen.

Main screen shortcuts:

| Key | Action |
| :--- | :--- |
| `ctrl+t` | **Edit Selected Table** – opens the edit screen for the selected table, where you add and delete rows |
| `ctrl+a` | **Add Comment** to the selected row |
| `ctrl+s` | **Show Comments** for the selected row |
| `ctrl+b` | **Manage Bookmarks** |
| `ctrl+k` | **Bookmark** the element in the selected row |
| `r` | Refresh all data from Egeria |
| `ctrl+f` | Leave feedback (works on every screen) |
| `q` | Quit the app |

## Adding and Deleting Elements

Adding and deleting both go through the table's **edit screen**:

1. On the main screen, select a table and press `ctrl+t`.
2. The edit screen shows a copy of that table. Then:
   - `a` – **Add Row**: opens the Add screen for that kind of element.
   - `d` – **Delete Row**: asks you to confirm, then deletes the highlighted element from Egeria. The row is removed only if Egeria accepts the delete. You can delete one row at a time.
   - `Escape` – back to the main screen.

Edit screens add and delete; they do not edit a row's values in place. To change your own details use **Edit Profile** from the Other Functions menu.

### Add screens

Every Add screen works the same way:
- Fill in the fields. Those marked \* are required.
- Press **Add** (or `ctrl+a`).
- Some screens have a switch that links the new element to you. It is on by default.

If a required field is missing or a value is invalid, the screen tells you which one. After a successful add the form is cleared, so you can add another; after a failed add your input is kept so you can correct it. Press **Quit** (or `q` outside a text field) to close the screen. You go back to the main screen and the data is reloaded.

| Table | Fields | Link switch | Egeria result |
| :--- | :--- | :--- | :--- |
| To-Dos | Name\*, Description\*, Priority (whole number, default 0) | – | A to-do assigned to you, status `REQUESTED` |
| Blogs | Name\*, Text\*, Situation | – | An entry in your blog |
| Journal | Title\*, Text\*, Situation | – | An entry in your journal |
| User Associations | Choose **Project** or **Community**, then that screen opens | | |
| Projects | Name\*, Description\*, Kind (`Project`, `Campaign`, `StudyProject`, `Task`, `PersonalProject`; default `Project`), Identifier, Start Date and Planned End Date (`YYYY-MM-DD`) | Add yourself to the project team | A project |
| Communities | Name\*, Description\* | – | A community |
| Roles | Name\*, Description\* | Appoint yourself to this role | A person role |
| Teams | Name\*, Description\* | Join this team as a member | A team; joining creates a TeamMember role for you, scoped to the team |
| My Collections | Name\*, Description\*, Category | – | A standalone collection |
| User Identity | User ID\*, Display Name, Distinguished Name | Link to your profile | A user identity |

## Comments and Threaded Responses

Comments can be attached to any element in a main-screen table, and responses can be attached to comments to any depth.

**Add a comment from the main screen:** select a row, press `ctrl+a`, enter the comment and a comment type (`Question`, `Answer`, `Suggestion` or `Requirement`), then press **Submit**.

**View and reply:** select a row and press `ctrl+s`. The comments screen lists the comments on that element.

- `ctrl+a` adds a new comment to the element being shown.
- `ctrl+r` on a highlighted comment re-opens the screen focused on *that comment*, showing its responses. Here `ctrl+a` adds a response. Repeat to go deeper into a thread.
- `q` closes the screen.

If an element has no comments yet, the screen tells you to use `ctrl+a`.

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
- `s` – show sample data for the highlighted row.
- `u` or `ctrl+s` – subscribe to the highlighted item.
- `t` – search glossary terms. Back from the search (`g`) returns to Shop for Data.
- `k` – bookmark the highlighted item; `ctrl+b` – open bookmarks with its GUID ready to add.
- `b` – back; `q` – quit the screen.

On the overview screen, `s` subscribes to the selected node, `b` goes back and `q` returns to the main screen. On a sample-data view, `s` subscribes, and `b`, `Escape` or `Enter` go back.

**Subscribing**, from any of these screens, opens the **Create Subscription Request** form. It has Display Name, Description, Identifier and Status (`DRAFT`, `PROPOSED` or `ACTIVE`; an invalid value becomes `DRAFT`). Press `c` to create the digital subscription in Egeria. The subscription is linked to the item you chose and to you as its subscriber. If either link can't be made, a warning says so; the subscription itself is still created.

### Edit Profile
A form pre-filled with your profile details (courtesy title, job title, given names, surname, preferred name, pronouns, description, time zone, employee ID, preferred language, resident country). Press **Edit Profile** to save. The screen also has shortcuts that open the Communities (`ctrl+c`), Identities (`ctrl+i`), Roles (`ctrl+r`) and Teams (`ctrl+t`) edit screens. Press `q` to return.

### Subscriptions
A table of the digital subscriptions you created: name, status, description and GUID. Press `q` to return.

### Technology Types
Browse the technology type hierarchy as a tree. Selecting a type shows its **catalog templates** and **governance action processes**:

- **Templates:** pick one and press **Select Template**. Fill in its placeholder values and submit. Egeria creates a new element from the template, and a **status screen** shows the result.
- **Processes:** pick one and press **Select Process**, then fill in its request parameters and submit. Only the parameters you fill in are sent. Egeria starts the governance action process, and a **status screen** shows its GUID.

On the status screen, `c` copies the GUID shown to your clipboard, and `Enter`/`q` closes it and returns you to the main screen.

### User Bookmarks
Opens the bookmarks screen (also `ctrl+b` on the main screen and on Shop for Data). It lists your bookmarks (name, type, GUID).

The easiest way to add a bookmark is from a table: select a row and press `ctrl+k` on the main screen, or highlight a row and press `k` on Shop for Data. Any row that has a GUID can be bookmarked, and so can a glossary row, which is identified by its qualified name. Bookmarking something that is already bookmarked just tells you so.

On the bookmarks screen:
- `ctrl+n` shows a field for the GUID of an element to bookmark. If you opened the screen with `ctrl+b` while a row was highlighted, that row's GUID is already filled in; otherwise copy a GUID from any table, or with `c` on a status screen.
- `d` removes the highlighted bookmark (the element itself is not deleted).
- `q` returns.

Your bookmarks are kept in Egeria as the members of your private **My Bookmarks** collection (qualified name `Bookmarks::<your user id>`), and only that collection. It is created the first time you bookmark something, anchored to your profile and linked from it with a `ResourceList` relationship whose resource use is "Bookmarks".

### Leave Feedback / Feedback Log
See [Leaving Feedback](#leaving-feedback).

## Keyboard Reference

| Key | Where | Action |
| :--- | :--- | :--- |
| `q` | Main screen | Quit the app |
| `r` | Main screen | Refresh all data from Egeria |
| `ctrl+f` | Any screen | Leave feedback |
| `F3` | Any screen (feedback owner only) | Show the feedback log |
| `ctrl+t` | Main screen | Edit the selected table |
| `ctrl+a` | Main screen | Comment on the selected row |
| `ctrl+s` | Main screen | Show comments for the selected row |
| `ctrl+b` | Main screen, Shop for Data | Bookmarks, with the highlighted row's GUID ready to add |
| `ctrl+k` | Main screen | Bookmark the selected row |
| `ctrl+n` / `d` / `q` | Bookmarks | Add by GUID / remove highlighted / close |
| `a` / `d` / `Escape` | Edit screens | Add row / delete row / back |
| `ctrl+a` / `q` | Add screens | Add / close (outside a text field) |
| `ctrl+a` / `ctrl+r` / `q` | Comments screen | Add comment / show responses to highlighted comment / close |
| `s` / `u` or `ctrl+s` / `t` / `k` / `b` / `q` | Shop for Data | Sample / subscribe / search glossary terms / bookmark / back / close |
| `s` / `b` / `q` | Overview | Subscribe / back / back to main |
| `c` / `q` | Create Subscription | Create / cancel |
| `c` / `Enter` / `q` | Status screen | Copy GUID / close / close |
| `Escape` | Splash screen | Continue to the app |
| `ctrl+s` / `Escape` | Feedback | Submit / cancel |
| `Escape` | Confirm Delete | Cancel |
| `ctrl+c` | Anywhere | Force quit (terminal) |

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
| `402` | Profile could not be loaded at startup |
| `403` | Profile creation cancelled or failed |
| `412` / `413` | Error / empty result reloading a newly created profile |
| `416` | Technology types could not be fetched |
| `430` | Incompatible Python or pydantic version |
| `440` | Team, role or glossary lookup error |

The full list is in `RETURN_CODES.md` in the app folder.

## Troubleshooting

**The app exits immediately with code 430.** Your environment has an old pydantic, often because a globally installed `textual` was used. Activate the project's `.venv` and run `textual run --dev my_profile_app.py` or `python my_profile_app.py` from there.

**The app exits with code 402.** The profile could not be retrieved. Check that:
- `EGERIA_PLATFORM_URL` is correct and reachable (VPN and firewall included);
- the view server named by `EGERIA_VIEW_SERVER` is running;
- `EGERIA_USER` and `EGERIA_USER_PASSWORD` are correct, and the user is allowed to use the view server.

**Something I added doesn't appear.** Press `r` on the main screen. Communities you create are not linked to you yet (see Known Limitations), so they don't appear in User Associations.

**The app quit unexpectedly.** The app only exits by itself in a few cases: a startup problem (codes `402`, `403`, `430`), a failure fetching technology types (`416`), or an error looking up a team (`440`).

## Known Limitations

As of 2026-10-01, these features are incomplete or don't work as described elsewhere:

- **Communities you add** are not linked to you. pyegeria has no call for community membership, so the community is created but won't appear in User Associations.
- **Not yet verified against a live Egeria server:** bookmarks, My Collections, joining a team, subscription links and starting processes. The test server was unavailable when they were added, so they have only been tested against fakes.

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

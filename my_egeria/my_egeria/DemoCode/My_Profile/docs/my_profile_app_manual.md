<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# My Profile App User Manual

The **My Profile App** is a Textual-based terminal user interface (TUI) application designed for Egeria users to manage their personal profiles, view their workspace, and interact with various Egeria metadata services directly from the command line.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Getting Started](#getting-started)
5. [Key Features](#key-features)
    - [Main Dashboard](#main-dashboard)
    - [Profile Management](#profile-management)
    - [Communities and Roles](#communities-and-roles)
    - [Actions and Work Items](#actions-and-work-items)
    - [Catalog and Shopping for Data](#catalog-and-shopping-for-data)
    - [Technology Type Explorer](#technology-type-explorer)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The My Profile App provides a centralized dashboard for an Egeria user. It allows you to:
- View and edit your personal profile information.
- Manage your user identities and community memberships.
- Track assigned, sponsored, and requested actions.
- Browse data catalogs and "shop" for data assets.
- Explore technology types and processes registered in Egeria.

The application is built using the [Textual](https://textual.textualize.io/) framework and utilizes the `pyegeria` SDK to communicate with Egeria View Servers.

## Prerequisites

Before running the My Profile App, ensure you have:
- **Python 3.12+** installed.
- The **pyegeria** package and its dependencies (`textual`, `rich`, `loguru`) installed in your Python environment.
- Access to a running **Egeria Platform** with a configured **View Server** (e.g., `qs-view-server`).
- Valid Egeria user credentials.

## Configuration

The My Profile App uses the standard `pyegeria` configuration mechanism. You can configure the application using environment variables, a `.env` file, or a `config.json` file.

### Environment Variables

Set the following environment variables or add them to your `.env` file:

```bash
EGERIA_PLATFORM_URL=https://localhost:9443
EGERIA_VIEW_SERVER=qs-view-server
EGERIA_USER=your_user_id
EGERIA_USER_PASSWORD=your_password
```

### Configuration File (`config.json`)

Alternatively, you can use a `config.json` file in your project root:

```json
{
  "Environment": {
    "Egeria Platform URL": "https://localhost:9443",
    "Egeria View Server": "qs-view-server"
  },
  "User Profile": {
    "User Name": "your_user_id",
    "User Password": "your_password"
  }
}
```

## Getting Started

To launch the application, navigate to the directory containing `my_profile_app.py` and run:

```bash
python my_profile_app.py
```

Upon startup, the application will attempt to load your profile from the configured Egeria server. If no profile is found for the current user, the application will guide you through the profile creation process.

## Key Features

### Main Dashboard

The main screen is divided into several sections:
- **Projects**: Lists projects you are involved in.
- **Communities**: Displays the communities you belong to.
- **Roles**: Shows your assigned roles within the organization.
- **Teams**: Lists the teams you are a member of.
- **Actions**: Displays active work items, including requested, in-progress, and waiting actions.
- **User Identity**: Lists your registered identities.
- **Other Functions**: A menu for accessing advanced features like catalog shopping and technology explorers.

### Profile Management

Through the **Edit Profile** option, you can update your personal details, including your display name and description. If you are a new user, the **Create Profile** screen will help you initialize your Egeria presence.

### Communities and Roles

You can view details of your communities and roles directly from the main dashboard. Selecting a community allows you to view or add comments, facilitating collaboration within your metadata workspace.

### Actions and Work Items

The Actions table provides a real-time view of your responsibilities. You can track the status of various governance actions and work items assigned to you or requested by you.

### Catalog and Shopping for Data

The **Shop for Data** function allows you to browse registered catalogs, dictionaries, and glossaries. You can explore the metadata hierarchy and find assets relevant to your work.

### Technology Type Explorer

The **Technology Types** explorer provides a deep dive into the technical metadata registered in Egeria. You can browse technology types, templates, and associated processes, helping you understand the technical landscape of your metadata environment.

## Keyboard Shortcuts

The application supports the following global keyboard shortcuts:

| Key | Action |
| --- | --- |
| `q` | Quit the application |
| `r` | Refresh data from the Egeria server |
| `Ctrl+C` | Force quit (standard terminal shortcut) |

## Troubleshooting

### Connection Issues
If the application fails to connect to Egeria, verify that:
- The `EGERIA_PLATFORM_URL` is correct and the platform is reachable.
- The `EGERIA_VIEW_SERVER` is running and active.
- Your network allows communication with the Egeria platform (check for VPN or firewall issues).

### Authentication Errors
If you encounter authentication errors:
- Double-check your `EGERIA_USER` and `EGERIA_USER_PASSWORD` settings.
- Ensure your user has the necessary permissions to access the View Server and User Profile OMAS.

---
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.

## Related Information

- [Egeria Project Documentation](https://egeria-project.org)
- [pyegeria Programming Guide](../../../../../docs/user_programming.md)
- [Dr.Egeria User Manual](../../../../../docs/dr_egeria_manual.md)

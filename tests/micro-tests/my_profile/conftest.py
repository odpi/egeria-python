"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Fixtures and mock data for My Profile App test suite.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Ensure repo root and My_Profile folder are in sys.path
root_path = Path(__file__).resolve().parents[3]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

profile_path = root_path / "my_egeria" / "my_egeria" / "DemoCode" / "My_Profile"
if str(profile_path) not in sys.path:
    sys.path.insert(0, str(profile_path))


@pytest.fixture
def sample_profile_data():
    """Sample full profile dictionary returned from Egeria."""
    return [
        {
            "Full Name": "Gary Geeke",
            "User ID": "garygeeke",
            "Job Title": "IT Infrastructure Lead",
            "GUID": "profile-guid-12345",
            "Contribution Record": [
                {
                    "Karma Points": 150,
                    "Karma Level": "Gold",
                }
            ],
            "Projects": [
                {
                    "Project Status": "ACTIVE",
                    "Name": "Infrastructure Modernization",
                    "Description": "Modernize core infrastructure components",
                    "GUID": "project-guid-111",
                }
            ],
            "Teams": [
                {
                    "Assignment Type": "MEMBER",
                    "Team Name": "DevOps Core",
                    "Description": "Core DevOps and Infrastructure Team",
                    "GUID": "team-guid-222",
                }
            ],
            "Communities": [
                {
                    "Assignment Type": "LEADER",
                    "Name": "Cloud Architecture",
                    "Description": "Community of cloud practitioners",
                    "GUID": "comm-guid-333",
                }
            ],
            "Roles": [
                {
                    "Role Name": "Department::101::TeamLeader",
                    "Role Type": "TeamLeader",
                    "Description": "Lead for IT Infrastructure",
                    "GUID": "role-guid-444",
                }
            ],
            "Note Logs": [
                {
                    "class": "BlogEntryProperties",
                    "Qualified Name": "Blog: 2026-08-18 Update",
                    "Effective Time": "2026-08-18 10:00:00",
                    "Text": "Initial setup of profiling tools completed.",
                    "GUID": "blog-guid-555",
                },
                {
                    "class": "JournalEntryProperties",
                    "Qualified Name": "Journal: Daily log",
                    "Effective Time": "2026-08-18 11:00:00",
                    "Text": "Testing and validation tasks underway.",
                    "GUID": "journal-guid-666",
                },
            ],
        }
    ]


@pytest.fixture
def sample_user_identities():
    """Sample user identities list."""
    return [
        {
            "Display Name": "Gary Geeke Work Identity",
            "Category": "Corporate",
            "Description": "Primary corporate identity",
            "Type Name": "UserIdentity",
            "URL": "https://identity.example.com/garygeeke",
            "GUID": "identity-guid-777",
            "Qualified Name": "UserIdentity::garygeeke",
            "Metadata Collection ID": "mc-1",
            "Metadata Collection Name": "Coco Pharmaceuticals",
            "User ID": "garygeeke",
            "Distinguished Name": "uid=garygeeke,ou=People,dc=example,dc=org",
        }
    ]


@pytest.fixture
def sample_todos_data():
    """Sample user todos data."""
    return [
        {
            "To-Do Name": "Review Security Architecture",
            "Activity Status": "IN_PROGRESS",
            "Description": "Review and approve new access model",
            "GUID": "todo-guid-888",
        }
    ]


@pytest.fixture
def sample_team_members_response():
    """Sample response from exec_report_spec for Team-Members."""
    return {
        "kind": "data",
        "data": [
            {
                "Display Name": "IT Infrastructure Team",
                "Qualified Name": "Team::IT_Infra",
                "Category": "Operations",
                "Description": "Team responsible for core infrastructure",
                "Members": [
                    {
                        "Individual": "Gary Geeke",
                        "Assignment Type": "TeamLeader",
                        "Individual GUID": "profile-guid-12345",
                    },
                    {
                        "Individual": "Erin Overview",
                        "Assignment Type": "TeamMember",
                        "Individual GUID": "profile-guid-67890",
                    },
                ],
            }
        ],
    }


@pytest.fixture
def sample_tech_types_list():
    """Sample technology types list response."""
    return [
        {
            "Display Name": "PostgreSQL Database",
            "Description": "Relational database server",
            "GUID": "tech-type-guid-999",
            "Qualified Name": "TechnologyType::PostgreSQL",
        }
    ]


@pytest.fixture
def sample_tech_type_detail():
    """Sample tech type detail dictionary."""
    return {
        "technologyTypeGUID": "tech-type-guid-999",
        "displayName": "PostgreSQL Database",
        "description": "Relational database server",
        "specificationMermaidGraph": "graph TD; A-->B;",
        "catalogTemplates": [
            {
                "displayName": "PostgreSQL Server Template",
                "Catalog Template Name": "PostgreSQL Server Template",
                "guid": "template-guid-101",
                "isDeployed": True,
            }
        ],
        "governanceActionProcesses": [
            {
                "displayName": "Provision Database Process",
                "guid": "process-guid-202",
                "isActive": False,
            }
        ],
    }


@pytest.fixture
def sample_glossary_data():
    """Sample glossary report spec response."""
    return {
        "kind": "data",
        "data": [
            {
                "Display Name": "Clinical Glossaries",
                "Description": "Terms for clinical trials and research",
                "Qualified Name": "Glossary::Clinical",
                "GUID": "glossary-guid-100",
            }
        ],
    }

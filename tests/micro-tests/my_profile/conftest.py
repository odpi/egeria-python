"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Fixtures and mock data for My Profile App test suite.

   The suite runs against in-memory fakes by default. Set ``PYEG_LIVE_EGERIA=1``
   to run the same tests against a real Egeria view server — see
   ``egeria_backend.py`` and this folder's README for the details.
"""

import contextlib
import sys
import uuid
from pathlib import Path
import pytest

# Ensure repo root, this folder, and the My_Profile folder are in sys.path
root_path = Path(__file__).resolve().parents[3]
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

# This folder holds egeria_backend.py, imported by conftest and the test modules.
here = Path(__file__).resolve().parent
if str(here) not in sys.path:
    sys.path.insert(0, str(here))

profile_path = root_path / "my_egeria" / "my_egeria" / "DemoCode" / "My_Profile"
if str(profile_path) not in sys.path:
    sys.path.insert(0, str(profile_path))

# Local to this folder; imported after sys.path is prepared above.
from egeria_backend import (  # noqa: E402
    EgeriaBackend,
    block_network,
    connection_settings,
    export_pyegeria_env,
    live_requested,
    live_unavailable_reason,
)


def pytest_configure(config):
    """Register the suite's marker and, in live mode, retarget pyegeria's config.

    ``load_app_config()`` caches the first time an app or screen is built, so the
    environment has to be set here — before collection finishes — rather than in
    a fixture.
    """
    config.addinivalue_line(
        "markers",
        "live_capable: exercises Egeria and switches between fake and live backends",
    )
    config.addinivalue_line(
        "markers",
        "allow_network: permit real HTTP even in fake mode (escape hatch)",
    )
    if live_requested():
        export_pyegeria_env()


@pytest.fixture(autouse=True)
def no_accidental_network(request, monkeypatch):
    """In fake mode, no test may reach a real server.

    Applied to every test in this folder so the suite is consistent: a test
    either mocks its Egeria calls or runs live deliberately. Opt out with
    `@pytest.mark.allow_network`.
    """
    if live_requested() or request.node.get_closest_marker("allow_network"):
        return
    block_network(monkeypatch, request.node.name)


@pytest.fixture(scope="session")
def egeria_connection():
    """The Egeria connection details the suite is configured to use."""
    return connection_settings()


@pytest.fixture
def backend(request):
    """Fake or live Egeria backend for a single test.

    In live mode the server is probed once per session; if it is not reachable
    or will not issue a token, tests skip with the reason rather than failing
    with a wall of connection errors.
    """
    live = live_requested()
    settings = connection_settings()

    if live:
        reason = live_unavailable_reason()
        if reason:
            pytest.skip(
                f"{request.node.name}: PYEG_LIVE_EGERIA=1 but Egeria at "
                f"{settings['platform_url']} is not usable ({reason})"
            )

    with contextlib.ExitStack() as stack:
        yield EgeriaBackend(live=live, stack=stack, **settings)


@pytest.fixture
def live_my_profile(backend):
    """A live MyProfile client, or skip. Used to discover real test inputs."""
    if not backend.live:
        pytest.skip("live-only fixture")
    from pyegeria import MyProfile

    client = MyProfile(backend.view_server, backend.platform_url, backend.user_id, backend.user_pwd)
    client.create_egeria_bearer_token(backend.user_id, backend.user_pwd)
    return client


@pytest.fixture
def live_team_role_name(backend, live_my_profile):
    """A real Team{Leader,Member} role name from the live profile.

    ``find_team_members`` splits the role name on '::' and searches on
    everything after the first segment, so this has to be a genuine role name
    from the server rather than a synthetic one.
    """
    profile = live_my_profile.get_my_profile(report_spec="My-User-MD", output_format="DICT")
    roles = (profile or [{}])[0].get("Roles") or []
    for role in roles:
        name = role.get("Name") or role.get("Role Name") or ""
        if "TeamLeader" in name or "TeamMember" in name:
            return name
    pytest.skip(f"live profile for {backend.user_id} has no TeamLeader/TeamMember role")


def _live_curation_client(backend):
    from pyegeria import AutomatedCuration

    client = AutomatedCuration(backend.view_server, backend.platform_url, backend.user_id, backend.user_pwd)
    client.create_egeria_bearer_token(backend.user_id, backend.user_pwd)
    return client


def _live_tech_type_names(client):
    """Every technology type display name on the live server, depth-first."""
    names: list[str] = []

    def walk(node):
        if isinstance(node, dict):
            name = node.get("displayName")
            if name and name != "Root Technology Type":
                names.append(name)
            for child in node.get("subTypes") or []:
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(client.get_tech_type_hierarchy(filter_string="*"))
    return names


@pytest.fixture
def live_tech_type_name(backend):
    """A real technology-type name that resolves to detail on the live server.

    ``tech_type_callback`` passes the screen's selection straight to
    ``get_tech_type_detail(filter_string=...)``, which matches on display name,
    so the live input has to be a genuine name off the type hierarchy.
    """
    if not backend.live:
        pytest.skip("live-only fixture")
    client = _live_curation_client(backend)
    for name in _live_tech_type_names(client):
        detail = client.get_tech_type_detail(filter_string=name, output_format="JSON")
        if isinstance(detail, dict) and detail.get("displayName"):
            return name
    pytest.skip("live server has no technology type with retrievable detail")


@pytest.fixture
def live_catalog_template(backend):
    """A real catalog template entry, exactly as the templates screen passes it.

    `TechnologyTypeTemplatesScreen` hands `tech_type_templates_callback` the raw
    `catalogTemplates` entry from `get_tech_type_detail`, so this returns the
    same unmodified dict. Most technology types carry no catalog template, so
    this scans the hierarchy for one that does.
    """
    if not backend.live:
        pytest.skip("live-only fixture")
    client = _live_curation_client(backend)
    for name in _live_tech_type_names(client):
        detail = client.get_tech_type_detail(filter_string=name, output_format="JSON")
        for template in (detail or {}).get("catalogTemplates") or []:
            if template.get("templateGUID"):
                return template
    pytest.skip("live server has no technology type with a catalog template")


@pytest.fixture
def live_template_placeholders(backend, live_catalog_template):
    """Placeholder values for a real template, keyed the way the screen keys them.

    `TechnologyTypeTemplatesScreen` builds one Input per placeholder with id
    `{name-with-spaces-as-underscores}_placeholder_input`, and the handler
    reverses that to recover the placeholder name. Values come from each
    placeholder's own `example` so they stay type-valid, with a unique suffix on
    identity-ish fields so repeated live runs don't collide on qualifiedName.
    """
    suffix = uuid.uuid4().hex[:8]
    placeholders = (live_catalog_template.get("specification") or {}).get("placeholderProperty") or []

    values = {}
    for placeholder in placeholders:
        if placeholder.get("class") != "PlaceholderProperty":
            continue
        name = placeholder.get("name")
        if not name:
            continue
        example = placeholder.get("example") or ""
        identity_like = any(token in name.lower() for token in ("name", "identifier"))
        value = f"pytest-{name}-{suffix}" if identity_like else example
        values[f"{name.replace(' ', '_')}_placeholder_input"] = value
    return values

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

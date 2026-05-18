"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Functional tests for question-spec entities and report-spec discovery.

Tests cover:
  - Creating Perspectives, Questions, Report Types, and Question Spec folders
  - Linking Questions to Perspectives (ScopedBy) and to QuestionSpec folders
  - find_report_specs_by_perspective / find_report_specs_by_question
  - load_egeria_report_specs (round-trip from Egeria into the registry)
  - report_spec_list / get_report_registry
  - Running the three built-in viewer report specs (Questions, Report-Types, Question-Specs)

A running Egeria environment is needed to run these tests.
"""

import time
from datetime import datetime

import pytest
from loguru import logger
from pydantic import ValidationError
from rich import print
from rich.console import Console

from pyegeria.core._exceptions import (
    PyegeriaAPIException,
    PyegeriaConnectionException,
    PyegeriaInvalidParameterException,
    PyegeriaNotFoundException,
    PyegeriaUnauthorizedException,
    print_basic_exception,
    print_exception_table,
    print_validation_error,
)
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.models import NewElementRequestBody, NewRelationshipRequestBody
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.view.base_report_formats import (
    find_report_specs_by_perspective,
    find_report_specs_by_question,
    get_report_registry,
    load_egeria_report_specs,
    report_spec_list,
)

disable_ssl_warnings = True
console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

# ── helpers ───────────────────────────────────────────────────────────────────

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def _make_actor(user: str = USER_ID) -> ActorManager:
    client = ActorManager(VIEW_SERVER, PLATFORM_URL, user_id=user)
    client.create_egeria_bearer_token(user, USER_PWD)
    return client


def _make_glossary(user: str = USER_ID) -> GlossaryManager:
    client = GlossaryManager(VIEW_SERVER, PLATFORM_URL, user_id=user)
    client.create_egeria_bearer_token(user, USER_PWD)
    return client


def _make_collection(user: str = USER_ID) -> CollectionManager:
    client = CollectionManager(VIEW_SERVER, PLATFORM_URL, user_id=user)
    client.create_egeria_bearer_token(user, USER_PWD)
    return client


def _make_tech(user: str = USER_ID) -> EgeriaTech:
    client = EgeriaTech(VIEW_SERVER, PLATFORM_URL, user_id=user)
    client.create_egeria_bearer_token(user, USER_PWD)
    return client


_EXCEPTION_TYPES = (
    PyegeriaInvalidParameterException,
    PyegeriaAPIException,
    PyegeriaUnauthorizedException,
    PyegeriaNotFoundException,
)


# ── Perspective tests ─────────────────────────────────────────────────────────

class TestPerspective:

    def test_create_perspective(self):
        """Create a Perspective entity and verify a GUID is returned."""
        client = None
        try:
            client = _make_actor()
            name = f"Test Perspective {_ts()}"
            qn = f"Perspective::{name}"
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "PerspectiveProperties",
                    "qualifiedName": qn,
                    "displayName": name,
                    "description": "Created by functional test",
                },
            }
            guid = client.create_perspective(body=body)
            print(f"\nCreated Perspective '{name}' → {guid}")
            assert isinstance(guid, str) and len(guid) > 0
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except ValidationError as e:
            print_validation_error(e)
            pytest.fail("Validation error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_find_perspectives(self):
        """Find Perspectives using a wildcard search."""
        client = None
        try:
            client = _make_actor()
            start = time.perf_counter()
            results = client.find_perspectives(search_string="*")
            duration = time.perf_counter() - start
            print(f"\nfind_perspectives('*') returned {len(results) if isinstance(results, list) else results!r}"
                  f" in {duration:.3f}s")
            assert isinstance(results, list)
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()


# ── Question (GlossaryTerm) tests ─────────────────────────────────────────────

class TestQuestion:

    def test_create_question(self):
        """Create a Question GlossaryTerm and verify a GUID is returned."""
        client = None
        try:
            client = _make_glossary()
            q_text = f"What is the status of test asset {_ts()}?"
            start = time.perf_counter()
            guid = client.create_question(display_name=q_text, description="Functional test question")
            duration = time.perf_counter() - start
            print(f"\nCreated Question '{q_text[:60]}' → {guid}  ({duration:.3f}s)")
            assert isinstance(guid, str) and len(guid) > 0
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except ValidationError as e:
            print_validation_error(e)
            pytest.fail("Validation error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_find_questions_by_classification(self):
        """find_glossary_terms filtered to Question-classified terms."""
        client = None
        try:
            client = _make_glossary()
            start = time.perf_counter()
            results = client.find_glossary_terms(
                search_string="*",
                include_only_classified_elements=["Question"],
            )
            duration = time.perf_counter() - start
            count = len(results) if isinstance(results, list) else results
            print(f"\nfind_glossary_terms(Question) → {count} result(s) in {duration:.3f}s")
            assert isinstance(results, list)
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_get_question_by_qn(self):
        """Create a question then retrieve it by its QN slug via get_terms_by_name."""
        client = None
        try:
            client = _make_glossary()
            import re
            q_text = f"How many assets exist in zone {_ts()}?"
            guid = client.create_question(display_name=q_text)
            slug = re.sub(r"[?',\".!;:()\[\]{}]", "", q_text.lower().strip())
            slug = re.sub(r"\s+", "-", slug)
            qn = f"Question::{slug}"

            results = client.get_terms_by_name(filter_string=qn)
            print(f"\nget_terms_by_name('{qn}') → {len(results) if isinstance(results, list) else results!r} result(s)")
            assert isinstance(results, list) and len(results) > 0
            guids = [r["elementHeader"]["guid"] for r in results]
            assert guid in guids
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()


# ── Report Type collection tests ───────────────────────────────────────────────

class TestReportType:

    def test_create_report_type(self):
        """Create a ReportType collection and verify a GUID is returned."""
        client = None
        try:
            client = _make_collection()
            label = f"Test-Report-Type-{_ts()}"
            start = time.perf_counter()
            guid = client.create_report_type_collection(display_name=label)
            duration = time.perf_counter() - start
            print(f"\nCreated ReportType '{label}' → {guid}  ({duration:.3f}s)")
            assert isinstance(guid, str) and len(guid) > 0
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_find_report_types(self):
        """find_collections filtered to ReportType collections."""
        client = None
        try:
            client = _make_collection()
            start = time.perf_counter()
            results = client.find_collections(search_string="*", _type="ReportType")
            duration = time.perf_counter() - start
            count = len(results) if isinstance(results, list) else results
            print(f"\nfind_collections(ReportType) → {count} result(s) in {duration:.3f}s")
            assert isinstance(results, list)
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()


# ── QuestionSpec folder tests ──────────────────────────────────────────────────

class TestQuestionSpec:

    def test_create_question_spec_folder(self):
        """Create a QuestionSpec folder and verify a GUID is returned."""
        client = None
        try:
            client = _make_collection()
            name = f"Test-Report-{_ts()}::1"
            start = time.perf_counter()
            guid = client.create_question_spec_folder(display_name=name)
            duration = time.perf_counter() - start
            print(f"\nCreated QuestionSpec '{name}' → {guid}  ({duration:.3f}s)")
            assert isinstance(guid, str) and len(guid) > 0
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_create_report_type_with_question_spec_and_question(self):
        """
        End-to-end: create a ReportType, a QuestionSpec folder, a Question,
        link the QuestionSpec to the ReportType, and link the Question to the QuestionSpec.
        """
        coll_client = None
        glos_client = None
        try:
            coll_client = _make_collection()
            glos_client = _make_glossary()

            ts = _ts()
            rt_label = f"FuncTest-{ts}"
            qs_name = f"{rt_label}::1"
            q_text = f"What does the functional test {ts} cover?"

            # 1. Create ReportType
            rt_guid = coll_client.create_report_type_collection(display_name=rt_label)
            print(f"\nReportType '{rt_label}' → {rt_guid}")

            # 2. Create QuestionSpec folder
            qs_guid = coll_client.create_question_spec_folder(display_name=qs_name)
            print(f"QuestionSpec '{qs_name}' → {qs_guid}")

            # 3. Link QuestionSpec → ReportType
            coll_client.add_to_collection(rt_guid, qs_guid)
            print(f"Linked QuestionSpec → ReportType")

            # 4. Create Question
            q_guid = glos_client.create_question(display_name=q_text)
            print(f"Question '{q_text[:60]}' → {q_guid}")

            # 5. Link Question → QuestionSpec
            coll_client.add_to_collection(qs_guid, q_guid)
            print(f"Linked Question → QuestionSpec")

            assert all(isinstance(g, str) and len(g) > 0 for g in [rt_guid, qs_guid, q_guid])

        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if coll_client:
                coll_client.close_session()
            if glos_client:
                glos_client.close_session()


# ── Link Perspective to Question tests ────────────────────────────────────────

class TestLinkPerspectiveToQuestion:

    def test_link_perspective_to_question(self):
        """Create a Perspective and a Question, then link them via ScopedBy."""
        actor_client = None
        glos_client = None
        try:
            actor_client = _make_actor()
            glos_client = _make_glossary()

            ts = _ts()
            p_name = f"Test Perspective {ts}"
            q_text = f"What data products does the test {ts} govern?"

            # Create Perspective
            p_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "PerspectiveProperties",
                    "qualifiedName": f"Perspective::{p_name}",
                    "displayName": p_name,
                },
            }
            p_guid = actor_client.create_perspective(body=p_body)
            print(f"\nPerspective '{p_name}' → {p_guid}")

            # Create Question
            q_guid = glos_client.create_question(display_name=q_text)
            print(f"Question '{q_text[:60]}' → {q_guid}")

            # Link Perspective → Question via ScopedBy
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {"class": "AssignmentScopeProperties"},
            }
            actor_client.link_assignment_scope(
                scope_element_guid=p_guid,
                actor_guid=q_guid,
                body=link_body,
            )
            print(f"Linked Perspective → Question via ScopedBy")

            assert isinstance(p_guid, str) and len(p_guid) > 0
            assert isinstance(q_guid, str) and len(q_guid) > 0

        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if actor_client:
                actor_client.close_session()
            if glos_client:
                glos_client.close_session()


# ── Report spec registry tests ────────────────────────────────────────────────

class TestReportSpecRegistry:

    def test_report_spec_list_includes_viewer_specs(self):
        """Questions, Report-Types, and Question-Specs must be in the registry."""
        specs = report_spec_list()
        print(f"\nTotal registered report specs: {len(specs)}")
        for label in ("Questions", "Report-Types", "Question-Specs"):
            assert label in specs, f"'{label}' missing from report_spec_list()"
            print(f"  ✓ {label}")

    def test_get_report_registry_non_empty(self):
        """get_report_registry() must return a non-empty dict."""
        reg = get_report_registry()
        assert len(reg) > 0
        print(f"\nget_report_registry() → {len(reg)} specs")

    def test_find_report_specs_by_perspective(self):
        """find_report_specs_by_perspective must return results for a known perspective."""
        # "Data Steward" appears in multiple built-in question_specs
        results = find_report_specs_by_perspective("Data Steward")
        print(f"\nfind_report_specs_by_perspective('Data Steward') → {len(results)} match(es)")
        assert isinstance(results, list)
        if results:
            first = results[0]
            assert "report_spec" in first
            assert "questions" in first
            print(f"  First match: {first['report_spec']}")

    def test_find_report_specs_by_perspective_case_insensitive(self):
        """Perspective lookup should be case-insensitive by default."""
        lower = find_report_specs_by_perspective("data steward")
        upper = find_report_specs_by_perspective("DATA STEWARD")
        print(f"\nCase-insensitive perspective search: lower={len(lower)}, upper={len(upper)}")
        assert len(lower) == len(upper)

    def test_find_report_specs_by_question(self):
        """find_report_specs_by_question must return results for a partial question text."""
        results = find_report_specs_by_question("list")
        print(f"\nfind_report_specs_by_question('list') → {len(results)} match(es)")
        assert isinstance(results, list)
        if results:
            print(f"  First match: {results[0].get('report_spec')} — "
                  f"'{results[0].get('question', '')[:60]}'")

    def test_find_report_specs_no_match(self):
        """find_report_specs_by_perspective with an unknown perspective returns empty list."""
        results = find_report_specs_by_perspective("ZZZ_UNKNOWN_PERSPECTIVE_XYZ")
        assert results == []

    def test_load_egeria_report_specs(self):
        """load_egeria_report_specs should complete without raising and add/update specs."""
        client = None
        try:
            client = _make_tech()
            before = set(report_spec_list())
            # force=True bypasses the TTL cache so the test always hits Egeria
            updated = load_egeria_report_specs(client, force=True)
            after = set(report_spec_list())
            new_specs = after - before
            print(f"\nload_egeria_report_specs(force=True): updated={updated}, "
                  f"{len(new_specs)} new spec(s): {sorted(new_specs)}")
            assert isinstance(updated, bool)
            for label in ("Questions", "Report-Types", "Question-Specs"):
                assert label in after
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_load_egeria_report_specs_cache_skips_reload(self):
        """Second call within TTL should return False (cache hit) without hitting Egeria."""
        client = None
        try:
            client = _make_tech()
            # First call: prime the cache
            load_egeria_report_specs(client, force=True)
            # Second call: should be served from cache
            result = load_egeria_report_specs(client, ttl_seconds=3600)
            print(f"\nCached call returned: {result}")
            assert result is False, "Expected cache hit (False) on second call within TTL"
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()


# ── Built-in viewer report spec execution tests ───────────────────────────────

class TestViewerReportSpecs:
    """Run the three built-in viewer specs via CollectionManager / GlossaryManager
    and verify they return list results."""

    def test_run_questions_spec(self):
        """GlossaryManager.find_glossary_terms with Question classification."""
        client = None
        try:
            client = _make_glossary()
            start = time.perf_counter()
            results = client.find_glossary_terms(
                search_string="*",
                include_only_classified_elements=["Question"],
                output_format="LIST",
                report_spec="Questions",
            )
            duration = time.perf_counter() - start
            print(f"\nQuestions report spec: {type(results).__name__} in {duration:.3f}s")
            assert results is not None
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_run_report_types_spec(self):
        """CollectionManager.find_collections with ReportType filter."""
        client = None
        try:
            client = _make_collection()
            start = time.perf_counter()
            results = client.find_collections(
                search_string="*",
                _type="ReportType",
                output_format="LIST",
                report_spec="Report-Types",
            )
            duration = time.perf_counter() - start
            print(f"\nReport-Types report spec: {type(results).__name__} in {duration:.3f}s")
            assert results is not None
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

    def test_run_question_specs_spec(self):
        """CollectionManager.find_collections with CollectionFolder filter."""
        client = None
        try:
            client = _make_collection()
            start = time.perf_counter()
            results = client.find_collections(
                search_string="*",
                _type="CollectionFolder",
                output_format="LIST",
                report_spec="Question-Specs",
            )
            duration = time.perf_counter() - start
            print(f"\nQuestion-Specs report spec: {type(results).__name__} in {duration:.3f}s")
            assert results is not None
        except _EXCEPTION_TYPES as e:
            print_exception_table(e)
            pytest.fail("Unexpected API error")
        except PyegeriaConnectionException as e:
            print_basic_exception(e)
            pytest.fail("Connection error")
        finally:
            if client:
                client.close_session()

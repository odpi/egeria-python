#!/usr/bin/env python3
"""
migrate_question_specs.py  —  Phase 1 migration script

Reads question_specs from base_report_formats.py (base_report_specs and
generated_format_sets) and pushes them into Egeria as:
  - ReportType collections          (QN prefix: ReportType::)
  - QuestionSpec folder collections (QN prefix: QuestionSpec::<label>::<n>)
  - Question GlossaryTerms          (QN prefix: Question::, classified Question)
  - Perspective entities            (QN prefix: Perspective::)
  - ScopedBy links: Perspective → Question

Questions and Perspectives are deduplicated by qualified name (find-or-create).

Usage:
    python commands/migrate_question_specs.py \\
        [--url <platform_url>] \\
        [--server <view_server>] \\
        [--user <user_id>] \\
        [--password <user_pwd>] \\
        [--dry-run] \\
        [--label <label>]  # migrate only this label (repeatable)
"""

import argparse
import os
import re
import sys
from typing import Optional

from loguru import logger

from pyegeria import EgeriaTech
from pyegeria.view.base_report_formats import base_report_specs, generated_format_sets


# ── helpers ────────────────────────────────────────────────────────────────────

def _build_qn(client: EgeriaTech, type_name: str, display_name: str) -> str:
    """Build the same qualified name that __create_qualified_name__ would produce.

    Replicates the server-side logic so find-or-create searches match what Egeria stored.
    """
    local_qualifier = getattr(client, 'local_qualifier', None) or os.environ.get("EGERIA_LOCAL_QUALIFIER", "")
    display_name = re.sub(r'\s', '-', display_name.strip())
    qn = f"{type_name}::{display_name}"
    if local_qualifier:
        qn = f"{local_qualifier}::{qn}"
    return qn


def _question_slug(text: str) -> str:
    """Compute the QN slug for a question — same logic as _async_create_question."""
    text = re.sub(r"[?',\".!;:()\[\]{}]", "", text.lower().strip())
    return re.sub(r"\s+", "-", text)


def _find_or_create_perspective(client: EgeriaTech, name: str, dry_run: bool) -> Optional[str]:
    qn = f"Perspective::{name}"
    try:
        results = client.actor_manager.find_perspectives(search_string=qn, starts_with=False)
        if results and not isinstance(results, str):
            for r in results:
                if r.get("properties", {}).get("qualifiedName") == qn:
                    return r["elementHeader"]["guid"]
    except Exception:
        pass

    if dry_run:
        logger.info(f"[DRY-RUN] Would create Perspective: '{name}'")
        return None

    body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": True,
        "properties": {
            "class": "PerspectiveProperties",
            "qualifiedName": qn,
            "displayName": name,
        },
    }
    guid = client.actor_manager.create_perspective(body=body)
    logger.success(f"Created Perspective '{name}' ({guid})")
    return guid


def _find_or_create_question(client: EgeriaTech, question_text: str, dry_run: bool) -> Optional[str]:
    # Search by QN (avoids regex issues with '?' in display-name search)
    qn = f"Question::{_question_slug(question_text)}"
    try:
        results = client.get_terms_by_name(filter_string=qn)
        if results and not isinstance(results, str):
            for r in results:
                if r.get("properties", {}).get("displayName") == question_text:
                    return r["elementHeader"]["guid"]
    except Exception as e:
        logger.debug(f"QN lookup failed for '{question_text[:50]}': {e}")

    if dry_run:
        logger.info(f"[DRY-RUN] Would create Question: '{question_text}'")
        return None

    guid = client.create_question(display_name=question_text)
    logger.success(f"Created Question '{question_text}' ({guid})")
    return guid


def _ensure_scoped_by(client: EgeriaTech, perspective_guid: str, question_guid: str, dry_run: bool) -> None:
    """Create a ScopedBy relationship between a Perspective and a Question if it doesn't exist."""
    try:
        existing = client.get_related_elements(question_guid, relationship_type="ScopedBy")
        if existing and not isinstance(existing, str):
            for e in existing:
                if e.get("elementHeader", {}).get("guid") == perspective_guid:
                    return  # already linked
    except Exception:
        pass

    if dry_run:
        logger.info(f"[DRY-RUN] Would link Perspective {perspective_guid} → Question {question_guid}")
        return

    body = {
        "class": "NewRelationshipRequestBody",
        "properties": {"class": "AssignmentScopeProperties"},
    }
    client.actor_manager.link_assignment_scope(
        scope_element_guid=perspective_guid, actor_guid=question_guid, body=body
    )
    logger.success(f"Linked Perspective {perspective_guid} → Question {question_guid}")


def _migrate_format_set(client: EgeriaTech, label: str, format_set, dry_run: bool) -> None:
    question_spec = getattr(format_set, "question_spec", None) or []
    if not question_spec:
        logger.debug(f"'{label}': no question_spec — skipping")
        return

    logger.info(f"Migrating '{label}' ({len(question_spec)} question spec entries)")

    # 1. Create or find the ReportType collection
    rt_qn = _build_qn(client, "ReportType", label)
    rt_guid: Optional[str] = None
    try:
        results = client.find_collections(
            search_string=rt_qn, _type="ReportType", starts_with=False
        )
        if results and not isinstance(results, str):
            for r in results:
                if r.get("properties", {}).get("qualifiedName") == rt_qn:
                    rt_guid = r["elementHeader"]["guid"]
                    logger.debug(f"Found existing ReportType '{label}' ({rt_guid})")
                    break
    except Exception:
        pass

    if rt_guid is None:
        if dry_run:
            logger.info(f"[DRY-RUN] Would create ReportType: '{label}'")
            rt_guid = f"(dry-run-{label})"
        else:
            rt_guid = client.create_report_type_collection(display_name=label)
            logger.success(f"Created ReportType '{label}' ({rt_guid})")

    # 2. For each question_spec entry, create a QuestionSpec folder and its members
    for idx, entry in enumerate(question_spec, start=1):
        # entry is a QuestionSpec Pydantic model (has .perspectives and .questions)
        if hasattr(entry, "perspectives"):
            perspectives_in_entry = entry.perspectives
            questions_in_entry = entry.questions
        else:
            perspectives_in_entry = entry.get("perspectives", [])
            questions_in_entry = entry.get("questions", [])

        if not questions_in_entry:
            continue

        qs_name = f"{label}::{idx}"
        qs_qn = _build_qn(client, "QuestionSpec", qs_name)

        # Find or create QuestionSpec folder
        qs_guid: Optional[str] = None
        try:
            results = client.find_collections(search_string=qs_qn, starts_with=False)
            if results and not isinstance(results, str):
                for r in results:
                    if r.get("properties", {}).get("qualifiedName") == qs_qn:
                        qs_guid = r["elementHeader"]["guid"]
                        logger.debug(f"Found existing QuestionSpec '{qs_name}' ({qs_guid})")
                        break
        except Exception:
            pass

        if qs_guid is None:
            if dry_run:
                logger.info(f"[DRY-RUN] Would create QuestionSpec folder: '{qs_name}'")
                qs_guid = f"(dry-run-qs-{idx})"
            else:
                qs_guid = client.create_question_spec_folder(display_name=qs_name)
                logger.success(f"Created QuestionSpec folder '{qs_name}' ({qs_guid})")

        # Link QuestionSpec folder to ReportType
        if not dry_run and not rt_guid.startswith("(dry-run"):
            try:
                client.add_to_collection(rt_guid, qs_guid)
            except Exception as e:
                logger.warning(f"Could not link QuestionSpec to ReportType: {e}")

        # Create / find Perspectives for this entry
        persp_guids = []
        for p_name in perspectives_in_entry:
            pg = _find_or_create_perspective(client, p_name, dry_run)
            if pg:
                persp_guids.append(pg)

        # Create / find Questions and wire relationships
        for q_text in questions_in_entry:
            q_guid = _find_or_create_question(client, q_text, dry_run)

            if not dry_run and q_guid:
                # Link Question to QuestionSpec folder
                try:
                    client.add_to_collection(qs_guid, q_guid)
                except Exception as e:
                    logger.warning(f"Could not link Question to QuestionSpec: {e}")

                # Link each Perspective to this Question
                for p_guid in persp_guids:
                    _ensure_scoped_by(client, p_guid, q_guid, dry_run)


# ── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate question_specs from base_report_formats.py to Egeria."
    )
    parser.add_argument("--url", default=None, help="Egeria platform URL")
    parser.add_argument("--server", default=None, help="View server name")
    parser.add_argument("--user", default=None, help="User ID")
    parser.add_argument("--password", default=None, help="User password")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without making API calls")
    parser.add_argument("--label", action="append", dest="labels",
                        help="Migrate only this label (can be specified multiple times)")
    args = parser.parse_args()

    client = EgeriaTech(
        view_server=args.server,
        platform_url=args.url,
        user_id=args.user,
        user_pwd=args.password,
    )
    client.create_egeria_bearer_token()

    # Combine both sources; base_report_specs takes priority (listed first)
    all_specs = {}
    for label, fs in list(base_report_specs.items()) + list(generated_format_sets.items()):
        if label not in all_specs:
            all_specs[label] = fs

    target_labels = set(args.labels) if args.labels else None

    migrated = 0
    skipped = 0
    for label, fs in sorted(all_specs.items()):
        if target_labels and label not in target_labels:
            continue
        try:
            _migrate_format_set(client, label, fs, args.dry_run)
            migrated += 1
        except Exception as e:
            logger.error(f"Failed to migrate '{label}': {e}")
            skipped += 1

    mode = "[DRY-RUN] " if args.dry_run else ""
    logger.info(f"{mode}Migration complete: {migrated} processed, {skipped} failed")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
    main()

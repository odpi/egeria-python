"""PY-55: the hand-kept related-element keys, settled."""
from pyegeria.authoring.validate import _HAND_KEPT_RELATED_KEYS, client_derived_columns
from pyegeria.view.base_report_formats import get_report_registry
from pyegeria.view.column_source import resolve_source


def _cols(label):
    return {c.key: c for f in get_report_registry()[label].formats for c in f.attributes}


def test_only_the_two_dan_q3_keys_stay_hand_kept():
    assert _HAND_KEPT_RELATED_KEYS == {"service_levels", "support_level"}


def test_folder_display_names_is_client_derived_for_find_glossaries():
    assert "folder_display_names" in client_derived_columns("GlossaryManager.find_glossaries", "Glossary")


def test_journal_columns_are_sources_on_present_in_note_logs():
    cols = _cols("Journal-Entry") if "Journal-Entry" in get_report_registry() else None
    if cols is None:
        label = next(l for l, fs in get_report_registry().items()
                     if any(c.key == "note_log_name" for f in fs.formats for c in f.attributes))
        cols = _cols(label)
    assert cols["note_log_name"].source == "of:presentInNoteLogs.displayName"
    assert cols["note_log_qualified_name"].source == "of:presentInNoteLogs.qualifiedName"


def test_the_journal_source_reads_the_log_and_is_blank_without_one():
    el = {"presentInNoteLogs": [{"relatedElement": {"properties": {"displayName": "Log", "qualifiedName": "NL::1"}}}]}
    assert resolve_source(el, "of:presentInNoteLogs.displayName")[1] == "Log"
    assert resolve_source({}, "of:presentInNoteLogs.displayName")[1] == ""  # the old helper raised on this


def test_contacts_is_the_assigned_actors_display_names():
    label = next(l for l, fs in get_report_registry().items()
                 if any(c.key == "actor_list" for f in fs.formats for c in f.attributes))
    assert _cols(label)["actor_list"].source == "of:assignedActors.displayName"
    el = {"assignedActors": [{"relatedElement": {"properties": {"displayName": "Ann"}}},
                             {"relatedElement": {"properties": {"displayName": "Bo"}}}]}
    assert resolve_source(el, "of:assignedActors.displayName")[1] == "Ann, Bo"  # the old helper ran them together

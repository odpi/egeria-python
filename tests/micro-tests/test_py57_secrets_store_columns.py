"""PY-57: the Secrets-Store-Element specs do not show file_* columns a SecretsCollection cannot carry."""
from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from pyegeria.view.base_report_formats import get_report_registry

FILE_KEYS = {"file_path_name", "file_name", "file_system_name", "file_type", "file_extension", "file_encoding"}


def _keys(label):
    return {c.key for f in get_report_registry()[label].formats for c in f.attributes}


def test_the_6_4_secrets_collection_has_none_of_the_file_properties():
    fields = {f.lower() for f in PROPERTIES_CLASS_FIELDS["SecretsCollectionProperties"][1]}
    assert not ({"filepathname", "filename", "filesystemname", "filetype", "fileextension", "fileencoding"} & fields)


def test_the_secrets_store_element_specs_show_no_file_columns():
    for label in ("Secrets-Store-Element-DrE-Basic", "Secrets-Store-Element-DrE-Advanced"):
        assert not (FILE_KEYS & _keys(label)), label
        assert _keys(label) == {"description", "version_identifier"}, label  # what the command can set, minus the file inputs


def test_other_specs_keep_their_file_columns():
    others = [l for l in get_report_registry() if l.endswith("-DrE-Advanced") and "Secrets-Store" not in l
              and FILE_KEYS & _keys(l)]
    assert others, "the rule must not reach beyond the Secrets Store Element command"

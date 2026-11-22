"""PY-47: pyegeria's needs-6.4 gate lead said "(odpi/egeria#9463, process variables and decisions)". The Portal vendors this
lead and words ProcessingVariable as "configuration values" (PO-75/76), so the two must say the same thing. "Decisions" stays:
Decision is still Egeria's name. The sentence is built in one place (needs_6_4_words) and every refusal uses it."""
from pyegeria.core.egeria_6_4_gate import needs_6_4_words

LEAD = "needs Egeria 6.4 (odpi/egeria#9463, configuration values and decisions)"


def test_the_full_sentence_with_a_version():
    assert needs_6_4_words("Link Decision", "https://h:9443", "6.3") == (
        f"Link Decision {LEAD}: the platform at https://h:9443 runs Egeria 6.3. Nothing was sent to Egeria.")


def test_the_full_sentence_when_the_platform_answered_404():
    assert needs_6_4_words("Link Decision", "https://h:9443") == (
        f"Link Decision {LEAD}: the platform at https://h:9443 does not serve this request (HTTP 404), so nothing was changed.")
    assert needs_6_4_words("Link Decision") == (
        f"Link Decision {LEAD}: this platform does not serve this request (HTTP 404), so nothing was changed.")


def test_process_variables_no_longer_appears_in_the_sentence_and_decisions_does():
    for words in (needs_6_4_words("X", "https://h", "6.3"), needs_6_4_words("X", "https://h"), needs_6_4_words("X")):
        assert "process variables" not in words.lower()
        assert "configuration values and decisions" in words


def test_the_names_module_docstring_says_it_the_same_way():
    import pyegeria.core.egeria_6_4_names as names

    assert "process variables" not in (names.__doc__ or "").lower()
    assert "configuration values and decisions" in (names.__doc__ or "")

# Egeria Python — Backlog

Consolidated work list. Update status when items start or finish.
Status: `open` · `in-progress` · `done` · `deferred`

---

## 🟡 Medium Priority — ServerClient missing async comment methods

**Status:** open
**Added:** 2026-07-02

`tests/functional-tests/test_comments.py` has 9 failing tests, all `AttributeError` on `pyegeria.core._server_client.ServerClient` for methods that don't exist: `async_add_comment_to_element`, `async_add_comment_reply`, `async_update_comment`, `async_setup_accepted_answer`, `async_setup_clear_answer`, `async_remove_comment_from_element`, `async_get_comment_by_guid`, `async_get_attached_comments`, `async_find_comments`.

Confirmed pre-existing and unrelated to Dr.Egeria command work — same 9 failures occur with or without changes to `md_processing/data/compact_commands/`. Run `pytest tests/functional-tests/test_comments.py -m unit` to reproduce.

**Fix:** Either implement the missing `async_*` comment methods on `ServerClient` (if comment support was intended to live there), or update the tests to target wherever comment methods actually live now (possibly moved to a different client class during a refactor).

# Parked: pre-merge profile app (Aug 26, 2026)

These are the `My_Profile/` files as they stood on `pcoldico/egeria-python@main`
(commit `b1fec716`) immediately before `upstream/main` was merged in on
2026-08-26.

## Why they are here

`main` and `upstream/main` had each restructured the profile app, differently:

- **upstream** carries the mixin split (`my_profile_app.py` reduced to ~574 lines,
  behaviour moved into `elements_crud_handler.py`, `profile_utils.py`,
  `team_roles_handler.py`, `tech_types_handler.py`, `shop_for_data_handler.py`).
  That split originated here and was merged upstream as `bc826498`.
- **this fork's `main`** never received the split. It was still the monolithic
  `my_profile_app.py` (2467 lines, all behaviour inline) with the Aug 23-26
  feature work layered on top.

The merge resolved every conflicting file in favour of upstream's modular version,
so the modular architecture is the one that survives. These copies exist so the
Aug 23-26 feature work is not lost and can be ported into the mixins deliberately.

## What still needs porting

From `my_profile_app.py` and `EditElementsScreens.py` here:

- `action_add_community`, `action_delete_community`, `action_remove_link_to_community`
  -> `ElementsCrudMixin`
- `action_show_team_members` -> `TeamRolesMixin`
- `on_input_changed` / `on_button_pressed` handlers and `add_community`
- `MainScreen` action renames: `action_show_team`, `action_edit_selected_table`,
  `action_add_note`, `action_show_notes` -- reconcile against upstream's generic
  `action_edit_table` / `action_show_comments` / `action_add_to_table` dispatch

`Add_to_Elements_Screens.py` here is a divergent copy of upstream's
`AddToElementsScreens.py` (note the differing name). Upstream's is the one
`my_profile_app.py` imports; diff the two before porting anything from this copy.

## Full history

Nothing here is the only copy. The complete pre-merge state is preserved at:

- branch `backup/main-pre-sync-2026-08-26`
- tag `pre-upstream-sync-2026-08-26`

Delete this folder once the port is finished.

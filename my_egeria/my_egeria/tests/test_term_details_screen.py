""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file is a unit test for my_egeria.


"""

from textual.app import App
from my_egeria.screens.glossary.term_details import TermDetailsScreen


class TestApp(App):
    """Minimal test harness for a single screen."""

    pass


#     async def on_mount(self):
#         pass  # We'll push screens manually
#
#
# @pytest.mark.asyncio
# async def test_term_details_load_and_save():
#     mock_service = AsyncMock()
#     mock_service.get_term_details.return_value = {
#         "displayName": "Example Term",
#         "description": "Test description",
#     }
#
#     screen = TermDetailsScreen(mock_service, "TestGlossary", "TestTerm")
#
#     # Start test app and mount screen
#     app = TestApp()
#     async with app.run_test() as pilot:
#         await app.push_screen(screen)
#         await screen.on_mount()
#
#         # Check load call
#         mock_service.get_term_details.assert_awaited_once_with(
#             "TestGlossary", "TestTerm"
#         )
#         assert screen.table.row_count == 2
#
#         # Mock new table data
#         screen.table.get_all_data = lambda: [
#             ("displayName", "Updated Term"),
#             ("description", "Updated description"),
#         ]
#
#         # Simulate pressing Save
#         await screen.on_button_pressed(Button.Pressed(Button("Save", id="save")))
#
#         # Verify save call
#         mock_service.update_term.assert_awaited_once_with(
#             "TestGlossary",
#             "TestTerm",
#             {
#                 "displayName": "Updated Term",
#                 "description": "Updated description",
#             },
#         )

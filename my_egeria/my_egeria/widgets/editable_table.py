""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a common widget for my_egeria.


"""

from textual.widgets import DataTable, Input
from textual.containers import Container
from textual import events


class EditableDataTable(DataTable):
    """A DataTable that supports inline cell editing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editing_cell = None
        self.input_widget = None
        self._original_value = None

    def on_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Double-click to start editing."""
        if event.click_count == 2:  # Double-click
            self.start_edit(event.coordinate)

    def start_edit(self, coordinate: tuple[int, int]) -> None:
        """Start editing the selected cell."""
        row, column = coordinate
        self.editing_cell = coordinate
        self._original_value = self.get_cell_at(row, column)

        # Create inline input over the cell
        self.input_widget = Input(value=str(self._original_value))
        self.input_widget.styles.width = "100%"
        self.input_widget.styles.height = "100%"

        # Swap the cell's display temporarily with the Input widget
        self.set_cell_at(row, column, self.input_widget)
        self.input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Save the edited cell value."""
        if self.editing_cell:
            row, column = self.editing_cell
            new_value = event.value
            self.set_cell_at(row, column, new_value)
            self.post_message(CellEdited(self, row, column, new_value))
            self.editing_cell = None
            self.input_widget = None

    def on_input_blurred(self, event: events.Blur) -> None:
        """Cancel editing if focus is lost."""
        if self.editing_cell and self.input_widget:
            row, column = self.editing_cell
            self.set_cell_at(row, column, self._original_value)
            self.editing_cell = None
            self.input_widget = None


class CellEdited(events.Event):
    """Event fired when a cell is edited."""

    def __init__(
        self, table: EditableDataTable, row: int, column: int, value: str
    ) -> None:
        self.table = table
        self.row = row
        self.column = column
        self.value = value
        super().__init__()

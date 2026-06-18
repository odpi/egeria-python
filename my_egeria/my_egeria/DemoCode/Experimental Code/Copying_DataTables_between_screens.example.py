from textual.app import App, ComposeResult
from textual.message import Message
from textual.screen import Screen
from textual.widgets import DataTable, Button, Header, Footer


# 1. Define the message payload holding keys and values
class TableSyncRequest(Message):
    def __init__(self, columns: list[str], rows: list[tuple[str, list]]) -> None:
        super().__init__()
        self.columns = columns
        # List of tuples: [(row_key_string, [cell1, cell2, ...]), ...]
        self.rows = rows


# 2. Main/Source Screen
class SourceScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="source_table")
        yield Button("Export Data to Screen B", id="btn_export")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#source_table", DataTable)
        table.add_columns("Item ID", "Qty", "Status")

        # Adding rows with explicit, specific keys
        table.add_row("Widget A", "10", "In Stock", key="key_prod_991")
        table.add_row("Widget B", "0", "Backorder", key="key_prod_992")
        table.add_row("Widget C", "50", "In Stock", key="key_prod_993")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_export":
            table = self.query_one("#source_table", DataTable)

            # Extract columns
            columns = [col.label.plain for col in table.columns.values()]

            # Extract row keys and data simultaneously
            rows_with_keys = []
            for row_key in table.rows:
                # row_key.value gets the string representation of the RowKey
                rows_with_keys.append((row_key.value, table.get_row(row_key)))

            # Bubble up the data message to the main App orchestrator
            self.post_message(TableSyncRequest(columns, rows_with_keys))


# 3. Destination Screen
class DestinationScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="dest_table")
        yield Button("Go Back", id="btn_back")
        yield Footer()

    def populate_table(self, columns: list[str], rows: list[tuple[str, list]]) -> None:
        table = self.query_one("#dest_table", DataTable)

        # Clear data and previous headers completely
        table.clear(columns=True)
        table.add_columns(*columns)

        # Re-insert every row explicitly mapped to its original key
        for key_str, cell_values in rows:
            table.add_row(*cell_values, key=key_str)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_back":
            self.app.pop_screen()


# 4. Main App coordinating the screen routing
class MultiScreenSyncApp(App):
    def on_mount(self) -> None:
        # Register both screens
        self.install_screen(SourceScreen(), name="screen_a")
        self.install_screen(DestinationScreen(), name="screen_b")
        self.push_screen("screen_a")

    # Intercept data message sent by Screen A
    def on_table_sync_request(self, message: TableSyncRequest) -> None:
        # Get reference to Screen B instance
        screen_b = self.get_screen("screen_b")

        # Push data directly into Screen B's method
        screen_b.populate_table(message.columns, message.rows)

        # Switch views
        self.push_screen("screen_b")
        self.notify("Table copied with keys intact!")


if __name__ == "__main__":
    MultiScreenSyncApp().run()

    """Key Design Patterns for Keys and Screens
    
    row_key.value Extraction: Inside Textual, row identifiers are tracking objects (RowKey).
    Always call .value during extraction to grab the raw underlying identifier string. 
    When passed into table.add_row(..., key=key_str) on the new screen, Textual seamlessly 
    rebuilds a valid matching RowKey tracking reference.
    
    table.rows.items() Iteration: Iterating directly through .items() yields the RowKey instance 
    as the dictionary key and the row metadata array as the value. 
    This ensures you never mismatch a key to a dataset.
    
    Pre-population on Inactive Screens: Textual lets you pull a screen instance by name using 
    self.get_screen("screen_name") even if it isn't currently active on the terminal display. 
    You can inject data into its widgets safely before running self.push_screen()."""
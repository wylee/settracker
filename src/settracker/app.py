import dataclasses
from datetime import datetime
from typing import List, Optional

from textual.app import App, ComposeResult
from textual import containers as c
from textual import widgets as w
from textual.widgets import Static

from .models import SetGroup


@dataclasses.dataclass
class Data:

    groups: List[SetGroup] = dataclasses.field(default_factory=list)
    group: Optional[str] = None
    quantity: Optional[int] = None
    date_time: Optional[datetime] = None
    debug: bool = False


class SetTrackerApp(App):
    TITLE = "Set Tracker"

    CSS_PATH = "app.css"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self, data: Data):
        self.settracker_data = data
        super().__init__(watch_css=data.debug)

    def compose(self) -> ComposeResult:
        yield w.Header(show_clock=True)
        yield w.Label("Group")
        yield Group(self.settracker_data)
        yield RepForm(self.settracker_data)
        yield w.Footer()

    def action_quit(self) -> None:
        """Quit."""
        self.exit()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


class Group(Static):
    def __init__(self, data):
        self.settracker_data = data
        self.settracker_group = data.group
        super().__init__()

    def compose(self) -> ComposeResult:
        group = self.settracker_group
        name = group.name if group else ""
        yield w.Input(name="group", placeholder="set group", value=name)


class RepForm(Static):
    def __init__(self, data):
        self.settracker_data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield RepInput(self.settracker_data)
        yield w.Button("Add Set", id="add")

    def on_button_pressed(self, event: w.Button.Pressed) -> None:
        rep_input = self.query_one(RepInput)
        match event.button.id:
            case "add":
                print("add")
            case _:
                print("???")


class RepInput(Static):
    def __init__(self, data):
        self.settracker_data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield w.Input(
            placeholder="number of reps",
            value=str(self.settracker_data.quantity),
        )

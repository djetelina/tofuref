from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.widgets import Input


class SearchInput(Input):
    BINDINGS: ClassVar[list[BindingType]] = [
        *Input.BINDINGS,
        Binding("escape", "close", "Close panel", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(placeholder="Search...", id="search", classes="bordered", **kwargs)
        self.border_title = "Search"

    def action_close(self):
        self.post_message(self.Changed(self, "", None))
        self.post_message(self.Submitted(self, "", None))

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Link


class StatusText(Label):
    def __init__(self, content: str, **kwargs) -> None:
        content = f"\\[ {content} ]"
        super().__init__(content, **kwargs)

    @property
    def content(self) -> str:
        return super().content

    @content.setter
    def content(self, value: str) -> None:
        super(Label, Label).content.__set__(self, f"\\[ {value} ]")


class Status(Container):
    DEFAULT_CSS = """
    Status {
        layout: horizontal;
        background: $surface;
        column-span: 1;
        height: 3;
        border: round $accent;
        border-right: none;
        border-left: none;
    }

    Status > #header-status {
        layout: grid;
        width: 100%;
        grid-size: 2;
        grid-columns: 1fr auto;
    }

    #header-info {
        width: auto;
        align: left middle;
        column-span: 1;
        layout: horizontal;
        padding: 0 1;
    }

    #header-links {
        width: auto;
        align: right middle;
        column-span: 1;
        layout: horizontal;
    }

    #header-links Link {
        padding: 0 1;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.provider = StatusText("-")
        self.version = StatusText("-")
        self.resource = StatusText("Welcome")
        self._path_label = Label("")

    def compose(self) -> ComposeResult:
        with Container(id="header-status"):
            with Container(id="header-info"):
                yield self.provider
                yield Label(" ⇢ ")
                yield self.version
                yield Label(" ⇢ ")
                yield self.resource
            with Container(id="header-links"):
                yield Link("GitHub", url="https://github.com/djetelina/tofuref")
                yield Link("Changelog", url="https://github.com/djetelina/tofuref/blob/main/CHANGELOG.md")

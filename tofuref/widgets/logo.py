from textual.widgets import Static

from tofuref import __version__


class Logo(Static):
    DEFAULT_CSS = """
    Logo {
        column-span: 1;
        width: auto;
        background: $surface;
    }
    """

    def render(self):
        # Using Rich markup directly to style colors like the HTML version
        return (
            "[$accent]  ┌───────┐\n"
            "[$secondary]│[/$secondary]  [$primary]tofuref[/$primary]  [$secondary]│[/$secondary]\n"
            f"[$accent]  └─{__version__}─┘"
            # f"[$accent]  └───────┘"
        )

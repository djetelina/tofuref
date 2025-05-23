from textual.widgets import RichLog

from tofuref import __version__


class CustomRichLog(RichLog):
    def __init__(self, **kwargs):
        super().__init__(id="log", markup=True, wrap=True, classes="bordered hidden", **kwargs)
        self.border_title = "Log"
        self.border_subtitle = f"tofuref v{__version__}"
        self.display = False

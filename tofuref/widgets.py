from textual.binding import Binding
from textual.widgets import (
    Input,
    OptionList,
    RichLog,
    MarkdownViewer,
)

from tofuref import __version__


class CustomRichLog(RichLog):
    def __init__(self, **kwargs):
        super().__init__(
            id="log", markup=True, wrap=True, classes="bordered hidden", **kwargs
        )
        self.border_title = "Log"
        self.border_subtitle = f"tofuref v{__version__}"
        self.display = False


class WelcomeMarkdownViewer(MarkdownViewer):
    ALLOW_MAXIMIZE = True

    BINDINGS = [
        Binding("up", "up", "Scroll Up", show=False),
        Binding("down", "down", "Scroll Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("home", "scroll_home", "Top", show=False),
        Binding("end", "scroll_end", "Bottom", show=False),
    ]

    def __init__(self, content=None, **kwargs):
        welcome_content = f"""
# Welcome to tofuref {__version__}!

Changelog: https://github.com/djetelina/tofuref/blob/main/CHANGELOG.md

## Controls
Navigate with arrows/page up/page down/home/end or your mouse.

| keybindings | action |
|------|--------|
| `tab` | focus next window |
| `shift+tab` | focus previous window |
| `enter` | choose selected or finish search |
| `q`, `ctrl+q` | **quit** tofuref |
| `s`, `/` | **search** in the context of providers and resources |
| `v` | change active provider **version** |
| `p` | focus **providers** window |
| `u`, `y` | copy ready-to-**use** provider version constraint |
| `r` | focus **resources** window |
| `c` | focus **content** window |
| `f` | toggle **fullscreen** mode |
| `l` | display **log** window |

---

# Get in touch
* GitHub: https://github.com/djetelina/tofuref"""

        super().__init__(
            content if content is not None else welcome_content,
            classes="content",
            show_table_of_contents=False,
            id="content",
            **kwargs,
        )

    def action_up(self) -> None:
        self.document.scroll_up()

    def action_down(self) -> None:
        self.document.scroll_down()

    def action_page_down(self) -> None:
        self.document.action_page_down()

    def action_page_up(self) -> None:
        self.document.action_page_up()

    def action_scroll_home(self) -> None:
        self.document.scroll_home()

    def action_scroll_end(self) -> None:
        self.document.scroll_end()

    # Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


class SearchInput(Input):
    def __init__(self, **kwargs):
        super().__init__(
            placeholder="Search...", id="search", classes="bordered", **kwargs
        )
        self.border_title = "Search"


class ProvidersOptionList(OptionList):
    def __init__(self, **kwargs):
        super().__init__(
            name="Providers",
            id="nav-provider",
            classes="nav-selector bordered",
            **kwargs,
        )
        self.border_title = "Providers"


class ResourcesOptionList(OptionList):
    def __init__(self, **kwargs):
        super().__init__(
            name="Resources",
            id="nav-resources",
            classes="nav-selector bordered",
            **kwargs,
        )
        self.border_title = "Resources"

from textual.binding import Binding
from textual.widgets import (
    Input,
    OptionList,
    RichLog,
    MarkdownViewer,
)

from tofuref import __version__

log_widget = RichLog(id="log", markup=True, wrap=True, classes="bordered hidden")
log_widget.border_title = "Log"
log_widget.border_subtitle = f"tofuref v{__version__}"
log_widget.display = False


class CustomMarkdownViewer(MarkdownViewer):
    ALLOW_MAXIMIZE = True

    BINDINGS = [
        Binding("up", "up", "Scroll Up", show=False),
        Binding("down", "down", "Scroll Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("home", "scroll_home", "Top", show=False),
        Binding("end", "scroll_end", "Bottom", show=False),
    ]

    def action_up(self) -> None:
        self.document.scroll_up()

    def action_down(self) -> None:
        self.document.scroll_down()

    def action_page_down(self) -> None:
        self.document.action_page_down()

    def action_page_up(self):
        self.document.action_page_up()

    def action_scroll_home(self) -> None:
        self.document.scroll_home()

    def action_scroll_end(self) -> None:
        self.document.scroll_end()

    # Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


content_markdown = CustomMarkdownViewer(
    f"""
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
| `r` | focus **resources** window |
| `c` | focus **content** window |
| `f` | toggle **fullscreen** mode |
| `l` | display **log** window |

---

# Known issues

Contributions (issues, prs, docs) welcome: [GitHub](https://github.com/djetelina/tofuref)

* *[UX]* Navigating content is difficult (search doesn't work despite the footer suggesting otherwise
* *[BUG]* Pressing `<esc>` while searching in fullscreen mode breaks the fullscreen and hides the still focused search

---

# Get in touch
* Matrix: #tofuref:jtl.vision
* GitHub: https://github.com/djetelina/tofuref/issues

## Feedback requests
* tofuref can start in fullscreen mode depending on the width of your terminal window, is the default good?

""",
    classes="content",
    show_table_of_contents=False,
)


search = Input(placeholder="Search...", id="search", classes="bordered")
search.border_title = "Search"

navigation_providers = OptionList(
    name="Providers", id="nav-provider", classes="nav-selector bordered"
)
navigation_providers.border_title = "Providers"
navigation_resources = OptionList(
    name="Resources", id="nav-resources", classes="nav-selector bordered"
)
navigation_resources.border_title = "Resources"

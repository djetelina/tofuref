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
    BINDINGS = [
        Binding("up", "up", "Scroll Up", show=False),
        Binding("down", "down", "Scroll Down", show=False),
    ]

    def action_up(self) -> None:
        self.document.scroll_up()

    def action_down(self) -> None:
        self.document.scroll_down()

    # Without this the markdown viewer would try to open a file on a disk, while the markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


content_markdown = CustomMarkdownViewer(
    f"""
# Welcome to tofuref {__version__}!

## Starting
* Press `s` or `/` to start filtering the providers, `<enter>` to focus back
* Press `<tab>` to switch between windows (or `<shift>+<tab>` to go back)
* Navigate to your desired provider and press `<enter>` to see the provider overview and load its resources
* Choose a resource and press `<enter>` to show its documentation, search also works here!

## Tips
* Most providers you are looking for are starting with `opentofu/` (or `hashicorp/`)

---

# Known issues

Contributions (issues, prs, docs) welcome: [GitHub](https://github.com/djetelina/tofuref)

* Navigating content is difficult (search doesn't work despite the footer suggesting otherwise
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

from textual.widgets import (
    Input,
    OptionList,
    RichLog,
    MarkdownViewer,
)

from tofuref import __version__

log_widget = RichLog(id="log", markup=True, wrap=True, classes="bordered")
log_widget.border_title = "Log"
log_widget.border_subtitle = f"tofuref v{__version__}"


class CustomMarkdownViewer(MarkdownViewer):
    # Without this the markdown viewer would try to open a file on a disk, while the markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


content_markdown = CustomMarkdownViewer(
    """
# Welcome to tofuref!

## Starting
* You can start typing to narrow down the providers.
* Press `<tab>` to switch between windows (or `<shift>+<tab>` to go back)
* Navigate to your desired provider and press `<enter>` to see the provider overview and load its resources
* Choose a resource and press `<enter>` to show its documentation

## Tips
* Most providers you are looking for are starting with `opentofu/` (or `hashicorp/`)

---

# Known issues

Contributions (issues, prs, docs) welcome: [GitHub](https://github.com/djetelina/tofuref)

* No support for:
    * Guides
    * Functions
* Many providers might be causing tofuref to crash, feel free to create a GitHub issue or a pull request
    * This is due to documentation folder handling and all the possible formats it can have
* It's impossible to search in Resources
* It's hard to tell apart Data Sources and Resources in the Resources widget
* Registry contains too many providers, some UX solutions being considered
    * Better sorting, based on GitHub stars
    * Custom sort by "favorites"
    * Show already fetched providers first

""",
    classes="content bordered",
    show_table_of_contents=False,
)
content_markdown.border_title = "Content"
content_markdown.border_subtitle = "Welcome"


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

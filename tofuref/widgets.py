import re
from typing import List

from rich.console import Group
from rich.syntax import Syntax
from textual.binding import Binding
from textual.widgets import (
    Input,
    OptionList,
    RichLog,
    MarkdownViewer,
)

from tofuref.data.registry import registry
from tofuref.data.helpers import CODEBLOCK_REGEX
from tofuref import __version__


class CustomRichLog(RichLog):
    def __init__(self, **kwargs):
        super().__init__(
            id="log", markup=True, wrap=True, classes="bordered hidden", **kwargs
        )
        self.border_title = "Log"
        self.border_subtitle = f"tofuref v{__version__}"
        self.display = False


class ContentWindow(MarkdownViewer):
    ALLOW_MAXIMIZE = True

    BINDINGS = [
        Binding("up", "up", "Scroll Up", show=False),
        Binding("down", "down", "Scroll Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("home", "scroll_home", "Top", show=False),
        Binding("end", "scroll_end", "Bottom", show=False),
        Binding("u", "yank", "Copy code blocks", show=False),
        Binding("y", "yank", "Copy code blocks"),
    ]

    def __init__(self, content=None, **kwargs):
        welcome_content = f"""
# Welcome to tofuref {__version__}!

Changelog: https://github.com/djetelina/tofuref/blob/main/CHANGELOG.md

## Controls

### Actions
| keybindings | action |
|------|--------|
| `s`, `/` | **search** in the context of providers and resources |
| `u`, `y` | Context aware copying (using a provider/resource) |
| `v` | change active provider **version** |
| `q`, `ctrl+q` | **quit** tofuref |
| `ctrl+l` | display **log** window |

### Focus widgets

| keybindings | action |
|------|--------|
| `tab` | focus next window |
| `shift+tab` | focus previous window |
| `p` | focus **providers** window |
| `r` | focus **resources** window |
| `c` | focus **content** window |
| `f` | toggle **fullscreen** mode |

### Navigate in widget

Navigate with arrows/page up/page down/home/end or your mouse.

---

# Get in touch
* GitHub: https://github.com/djetelina/tofuref"""

        self.content = content if content is not None else welcome_content
        super().__init__(
            self.content,
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

    def update(self, markdown: str) -> None:
        self.content = markdown
        self.document.update(markdown)

    def action_yank(self):
        code_blocks = re.findall(
            CODEBLOCK_REGEX, self.content, re.MULTILINE | re.DOTALL
        )
        if self.app.code_block_selector.has_parent:
            self.app.code_block_selector.parent.remove_children(
                [self.app.code_block_selector]
            )
        if not code_blocks:
            return
        self.screen.mount(self.app.code_block_selector)
        self.app.code_block_selector.set_new_options(code_blocks)
        self.screen.maximize(self.app.code_block_selector)

    # Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


class SearchInput(Input):
    BINDINGS = Input.BINDINGS + [
        Binding("escape", "close", "Close panel", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(
            placeholder="Search...", id="search", classes="bordered", **kwargs
        )
        self.border_title = "Search"

    def action_close(self):
        self.post_message(self.Changed(self, "", None))
        self.post_message(self.Submitted(self, "", None))


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


class CodeBlockSelect(OptionList):
    BINDINGS = OptionList.BINDINGS + [
        Binding("escape", "close", "Close panel", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(
            name="CodeBlocks", id="code-block-selector", classes="bordered", **kwargs
        )
        self.border_title = "Choose a codeblock to copy"

    def set_new_options(self, code_blocks: List[str]) -> None:
        self.clear_options()
        i = 0
        for lexer, block in code_blocks:
            i += 1
            self.add_option(
                Group(
                    f"[b]Codeblock[/] {i}",
                    Syntax(block, lexer=lexer if lexer else "hcl", theme="material"),
                )
            )
            self.add_option(None)
        self.focus()
        self.highlighted = 0

    def action_close(self):
        content_window = self.parent.query_one("#content", expect_type=ContentWindow)
        content_window.document.focus()
        if not registry.fullscreen_mode:
            self.screen.minimize()
        else:
            self.screen.maximize(content_window)
        self.parent.remove_children([self])

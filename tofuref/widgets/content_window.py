import re
from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.widgets import MarkdownViewer, Tree

from tofuref import __version__
from tofuref.data.helpers import CODEBLOCK_REGEX


class ContentWindow(MarkdownViewer):
    ALLOW_MAXIMIZE = True

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("k", "scroll_up", "Scroll Up", show=False),
        Binding("j", "scroll_down", "Scroll Down", show=False),
        Binding("ctrl+f", "page_up", "Page Up", show=False),
        Binding("ctrl+b", "page_down", "Page Down", show=False),
        Binding("G", "scroll_end", "Bottom", show=False),
        Binding("u", "yank", "Copy code blocks", show=False),
        Binding("y", "yank", "Copy code blocks"),
        Binding("t", "toggle_toc", "Toggle TOC"),
        Binding("B", "open_browser", "Open in browser"),
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
| `b` | persistently bookmark an item to prioritize them in sorting when next re-ordered |
| `q`, `ctrl+q` | **quit** tofuref |
| `t` | toggle **table of contents** from content window |
| `B` | from content window, open active page in browser |
| `ctrl+l` | display **log** window |
| `ctrl+g` | open **GitHub** repository for provider |
| `ctrl+s` | Show **stats** of provider's github repo |

### Focus windows

| keybindings | action |
|------|--------|
| `tab` | focus next window |
| `shift+tab` | focus previous window |
| `p` | focus **providers** window |
| `r` | focus **resources** window |
| `c` | focus **content** window |
| `f` | toggle **fullscreen** mode |

### Navigate in a window

Navigate with arrows/page up/page down/home/end or your mouse.

VIM keybindings should be also supported in a limited capacity.

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

    def update(self, markdown: str) -> None:
        self.content = markdown
        self.document.update(markdown)

    def action_toggle_toc(self):
        self.show_table_of_contents = not self.show_table_of_contents
        if not self.table_of_contents.border_title:
            self.table_of_contents.border_title = "Table of Contents"
        if self.show_table_of_contents:
            toc = self.table_of_contents.query_one(Tree)
            toc.focus()
            toc.action_cursor_down()
        else:
            self.document.focus()

    def action_yank(self):
        code_blocks = re.findall(CODEBLOCK_REGEX, self.content, re.MULTILINE | re.DOTALL)
        if self.app.code_block_selector.has_parent:
            self.app.code_block_selector.parent.remove_children([self.app.code_block_selector])
        if not code_blocks:
            return
        self.screen.mount(self.app.code_block_selector)
        self.app.code_block_selector.set_new_options(code_blocks)
        self.screen.maximize(self.app.code_block_selector)

    def action_open_browser(self):
        provider = self.app.active_provider.display_name
        resource_type = self.app.active_resource.type.value
        resource_name = self.app.active_resource.name
        url = f"https://search.opentofu.org/provider/{provider}/latest/docs/{resource_type}s/{resource_name}"
        self.app.open_url(url)

    # Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)
    async def go(self, location):
        return None

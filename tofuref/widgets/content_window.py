import re
from typing import ClassVar

from textual.binding import Binding, BindingType
from textual.widgets import MarkdownViewer, Tree

from tofuref.config import config
from tofuref.data.helpers import CODEBLOCK_REGEX
from tofuref.widgets import keybindings


class ContentWindow(MarkdownViewer):
    DEFAULT_CSS = """
    ContentWindow {
        border-left: $border-style $primary;
        border-right: $border-style $primary;
        scrollbar-color: $primary-darken-2;
        & > MarkdownTableOfContents {
            dock:right;
            border-left: $border-style $primary;
            border-right: $border-style $primary;
            color: $foreground;
            background: $surface;
            &:focus-within {
                color: $foreground;
                background: $surface;
                background-tint: $foreground 5%;
                border-left: $border-style $accent;
                border-right: $border-style $accent;
            }
        }
        &:focus-within {
            border-left: $border-style $accent;
            border-right: $border-style $accent;
            scrollbar-color: $primary;
        }
        & >MarkdownTableOfContents > Tree {
            background: $surface;
        }
    }
"""

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
        keybindings.BACK,
        keybindings.LEFT_BACK,
    ]

    def __init__(self, content=None, **kwargs):
        welcome_content = f"""
# Welcome to tofuref!

Keyboard-first reference viewer for OpenTofu/Terraform providers and their resources.

Changelog: https://github.com/djetelina/tofuref/blob/main/CHANGELOG.md

---

## Quick start

1. Use `p`, `r` and `c` to navigate between three main windows.
2. Press `s` or `/` to search providers and resources.
3. Use arrow keys (or VIM `j`/`k`) to select a provider, then a resource.
4. View rich docs in this window. Press `t` to toggle the Table of Contents.
5. Press `y` (or `u`) to copy code blocks — pick the exact snippet you need.
6. Press `B` to open the current page in your browser.

Tip: Use `b` to bookmark frequently used items and prioritize them in future sort orders.

---

## Keyboard reference

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

### Focus management

| keybindings | action |
|------|--------|
| `p` | focus **providers** window |
| `r` | focus **resources** window |
| `c` | focus **content** window |
| `backspace`, `left arrow` | focus parent window |
| `tab` | focus next window |
| `shift+tab` | focus previous window |

### In-window navigation

- Arrow keys, PageUp/PageDown, Home/End, or your mouse.
- VIM-style: `j`/`k` for line scroll, `ctrl+f` page down, `ctrl+b` page up, `G` to end.

---

## Get in touch
* GitHub: https://github.com/djetelina/tofuref"""

        self.content = content if content is not None else welcome_content
        super().__init__(
            self.content,
            show_table_of_contents=False,
            **kwargs,
        )

    async def update(self, markdown: str) -> None:
        markdown = sanitize_markdown(markdown).strip()

        markdown_stripped = try_to_strip_length(markdown)
        if markdown_stripped != markdown:
            self.app.notify(
                "Some sections were removed, open in browser ([bold]B[/]) for the full page.",
                title="Content was too long",
                severity="warning",
                timeout=30,
            )
            incomplete_infobox = """> The content of this document was too long, tofuref had to remove seme sections.
>
> To view the full page, open it in your browser (keybind `B`).
            """
            markdown = f"{incomplete_infobox}\n\n{markdown_stripped}"

        self.content = markdown
        await self.document.update(self.content)

    def action_toggle_toc(self):
        self.show_table_of_contents = not self.show_table_of_contents
        if self.show_table_of_contents:
            toc = self.table_of_contents.query_one(Tree)
            toc.focus()
            toc.action_cursor_down()
        else:
            self.document.focus(scroll_visible=False)

    def action_yank(self):
        code_blocks = re.findall(CODEBLOCK_REGEX, self.content, re.MULTILINE | re.DOTALL)
        if self.app.code_block_selector.has_parent:
            self.app.code_block_selector.parent.remove_children([self.app.code_block_selector])
        if not code_blocks:
            return
        self.parent.mount(self.app.code_block_selector)
        self.app.code_block_selector.set_new_options(code_blocks)
        self.display = False
        # self.screen.maximize(self.app.code_block_selector)

    def action_open_browser(self):
        if not self.app.active_provider:
            url = "https://github.com/djetelina/tofuref/blob/main/CHANGELOG.md"
        else:
            provider = self.app.active_provider.display_name
            resource_type = self.app.active_resource.type.value
            resource_name = self.app.active_resource.name
            url = f"https://search.opentofu.org/provider/{provider}/latest/docs/{resource_type}s/{resource_name}"
        self.app.open_url(url)

    def action_back(self):
        if self.app.active_resource:
            self.app.action_providers()
        self.app.action_resources()

    # Without this, the Markdown viewer would try to open a file on a disk, while the Markdown itself will open a browser link (desired)
    async def go(self, location):
        return None


def sanitize_markdown(markdown: str) -> str:
    """
    Place to sanitize content that is incompatible with textual's Markdown.
    """
    markdown = markdown.replace("–", "-").replace("—", "-")  # noqa: RUF001
    return re.sub(r"<.*?>", "", markdown)


def remove_sections_for_nested(markdown: str, min_dots: int) -> str:
    flags = re.M | re.I
    dot_lookahead = rf"(?=(?:[^.\n]*\.){{{min_dots},}})"

    pattern = rf"^\s{{0,3}}\#{{1,6}}\s(?=[^\n]*Nested){dot_lookahead}[^\n]*(?:\n(?!\s{{0,3}}\#{{1,6}}\s).*)*(?:\n)?"
    return re.sub(pattern, "", markdown, flags=flags)


def try_to_strip_length(markdown: str) -> str:
    for i in range(5, 0, -1):
        if len(markdown) < config.markdown_length_target:
            break
        markdown = remove_sections_for_nested(markdown, i)
    return markdown

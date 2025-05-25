from typing import ClassVar

from rich.console import Group
from rich.syntax import Syntax
from textual.binding import Binding, BindingType
from textual.widgets import OptionList
from textual.widgets.option_list import Option

from tofuref.config import config
from tofuref.widgets.keybindings import VIM_OPTION_LIST_NAVIGATE


class CodeBlockSelect(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [
        *OptionList.BINDINGS,
        Binding("escape", "close", "Close panel", show=False),
        *VIM_OPTION_LIST_NAVIGATE,
    ]

    def __init__(self, **kwargs):
        super().__init__(name="CodeBlocks", id="code-block-selector", classes="bordered", **kwargs)
        self.border_title = "Choose a codeblock to copy"

    def set_new_options(self, code_blocks: list[tuple]) -> None:
        self.clear_options()
        for i, (lexer, block) in enumerate(code_blocks):
            self.add_option(
                Group(
                    f"[b]Codeblock[/] {i + 1}",
                    Syntax(block, lexer=lexer if lexer else "hcl", theme=config.theme.codeblocks),
                )
            )
            self.add_option(None)
        self.focus()
        self.highlighted = 0

    def action_close(self):
        content_window = self.app.content_markdown
        content_window.document.focus()
        if not self.app.fullscreen_mode:
            self.screen.minimize()
        else:
            self.screen.maximize(content_window)
        self.parent.remove_children([self])

    async def on_option_selected(self, option: Option):
        code_selected = option.prompt.renderables[1].code
        self.app.copy_to_clipboard(code_selected)
        # We don't want the longest notification, so three dots will replace lines beyond the 3rd line
        code_selected_lines = code_selected.splitlines()
        lines_of_code_to_show = 4
        if len(code_selected_lines) > lines_of_code_to_show:
            snippet = "\n".join(code_selected_lines[:4])
            code_selected_notify = f"{snippet}\n..."
        else:
            code_selected_notify = code_selected.strip()
        self.app.notify(code_selected_notify, title="Copied to clipboard", markup=False)
        self.app.action_content()
        if not self.app.fullscreen_mode:
            self.screen.minimize()
        await self.parent.remove_children([self])

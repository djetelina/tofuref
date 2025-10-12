from typing import ClassVar

from textual.binding import BindingType
from textual.widgets import OptionList

from tofuref.data.meta import Item
from tofuref.widgets.keybindings import BOOKMARK, CLEAR_CACHE, VIM_OPTION_LIST_NAVIGATE


class MenuOptionListBase(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [*OptionList.BINDINGS, *VIM_OPTION_LIST_NAVIGATE, BOOKMARK, CLEAR_CACHE]

    DEFAULT_CSS = """
    MenuOptionListBase {
        border: none;
        border-bottom: blank $primary;
        height: 1fr;
        background: $surface;
    }

    MenuOptionListBase:focus {
        border: none;
        border-bottom: blank $accent;
        scrollbar-color: $primary-darken-1;
    }
    """

    async def action_bookmark(self):
        if self.highlighted is None:
            return
        res: Item = self.highlighted_option.prompt
        if not res.bookmarked:
            await self.app.bookmarks.add(res.kind, res.identifying_name)
            res.bookmarked = True
            self.replace_option_prompt_at_index(self.highlighted, self.highlighted_option.prompt)
            self.app.notify(f"{res.__class__.__name__} {res.display_name} bookmarked", title="Bookmark added")
        else:
            await self.app.bookmarks.remove(res.kind, res.identifying_name)
            res.bookmarked = False
            self.replace_option_prompt_at_index(self.highlighted, self.highlighted_option.prompt)
            self.app.notify(f"{res.__class__.__name__} {res.display_name} removed from bookmarks", title="Bookmark removed")

    async def action_purge_from_cache(self):
        if self.highlighted is None:
            return
        res: Item = self.highlighted_option.prompt
        await res.clear_from_cache()
        self.replace_option_prompt_at_index(self.highlighted, self.highlighted_option.prompt)
        self.app.notify(f"{res.__class__.__name__} {res.display_name} purged from cache", title="Cache purged")

    def watch_highlighted(self, highlighted: int | None) -> None:
        super().watch_highlighted(highlighted)
        self.refresh_bindings()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        return not (action == "purge_from_cache" and self.highlighted_option and not self.highlighted_option.prompt.cached)

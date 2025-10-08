from typing import ClassVar

from textual.binding import BindingType
from textual.widgets import OptionList

from tofuref.data.meta import Item
from tofuref.widgets.keybindings import BOOKMARK, CLEAR_CACHE, VIM_OPTION_LIST_NAVIGATE


class MenuOptionListBase(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [*OptionList.BINDINGS, *VIM_OPTION_LIST_NAVIGATE, BOOKMARK, CLEAR_CACHE]

    async def action_bookmark(self):
        if self.highlighted is None:
            return
        option = self.get_option_at_index(self.highlighted)
        res: Item = option.prompt
        if not res.bookmarked:
            self.app.bookmarks.add(res.kind, res.identifying_name)
            res.bookmarked = True
            self.replace_option_prompt_at_index(self.highlighted, option.prompt)
            self.app.notify(f"{res.__class__.__name__} {res.display_name} bookmarked", title="Bookmark added")
        else:
            self.app.bookmarks.remove(res.kind, res.identifying_name)
            res.bookmarked = False
            self.replace_option_prompt_at_index(self.highlighted, option.prompt)
            self.app.notify(f"{res.__class__.__name__} {res.display_name} removed from bookmarks", title="Bookmark removed")

    async def action_purge_from_cache(self):
        if self.highlighted is None:
            return
        option = self.get_option_at_index(self.highlighted)
        res: Item = option.prompt
        res.clear_from_cache()
        self.replace_option_prompt_at_index(self.highlighted, option.prompt)
        self.app.notify(f"{res.__class__.__name__} {res.display_name} purged from cache", title="Cache purged")

from textual.binding import Binding

VIM_OPTION_LIST_NAVIGATE = [
    Binding("j", "cursor_down", "Down", show=False),
    Binding("k", "cursor_up", "Up", show=False),
    Binding("G", "last", "Last", show=False),
    Binding("ctrl+b", "page_down", "Page Down", show=False),
    Binding("ctrl+f", "page_up", "Page Up", show=False),
]

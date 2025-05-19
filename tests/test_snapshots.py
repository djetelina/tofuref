APP_PATH = "../tofuref/main.py"


def test_welcome(snap_compare):
    assert snap_compare(APP_PATH, terminal_size=(200, 60))


def test_welcome_fullscreen(snap_compare):
    assert snap_compare(APP_PATH)


def test_toggle_fullscreen(snap_compare):
    assert snap_compare(APP_PATH, press="f")


def test_content(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "pagedown"])


def test_search_github(snap_compare):
    assert snap_compare(APP_PATH, press=["s", "g", "i", "t", "h", "u", "b"])


def test_open_github(snap_compare):
    assert snap_compare(
        APP_PATH, press=["s", "g", "i", "t", "h", "u", "b", "enter", "enter"]
    )


def test_open_github_membership(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[
            "s",
            "g",
            "i",
            "t",
            "h",
            "u",
            "b",
            "enter",
            "enter",
            "s",
            "m",
            "e",
            "m",
            "b",
            "e",
            "r",
            "enter",
            "enter",
        ],
    )


def test_back_to_providers(snap_compare):
    assert snap_compare(APP_PATH, press=["enter", "p"])


def test_provider_overview(snap_compare):
    assert snap_compare(
        APP_PATH, press=["s", "g", "i", "t", "h", "u", "b", "enter", "enter", "c"]
    )


def test_version_picker(snap_compare):
    assert snap_compare(
        APP_PATH, press=["s", "g", "i", "t", "h", "u", "b", "enter", "enter", "v"]
    )


def test_version_picker_submit(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[
            "s",
            "g",
            "i",
            "t",
            "h",
            "u",
            "b",
            "enter",
            "enter",
            "v",
            "down",
            "enter",
        ],
    )


def test_use(snap_compare):
    assert snap_compare(
        APP_PATH, press=["s", "g", "i", "t", "h", "u", "b", "enter", "enter", "u"]
    )

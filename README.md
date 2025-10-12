# tofuref

[![PyPI - Version](https://img.shields.io/pypi/v/tofuref)](https://pypi.org/project/tofuref/)
![PyPI - License](https://img.shields.io/pypi/l/tofuref)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tofuref)
![GitHub Repo stars](https://img.shields.io/github/stars/DJetelina/tofuref?style=flat&logo=github)

TUI for OpenTofu provider registry.

![Screenshot](https://github.com/djetelina/tofuref/blob/main/tests/__snapshots__/test_snapshots/test_welcome.svg?raw=true)

## Features

* Keyboard first navigation
* Searchable index of providers and resources
* Copy blocks for your `required_providers`
* Copy snippets from the docs
* Browse all provider versions
* Bookmark frequently used providers and resources
* Cache visited providers and resources
* If the markdown viewer is not sufficient for you, quickly open the resource in your web browser
* Check provider stats to see if they are production ready based on stars and forks
* Configurable look to match the rest of your system

## Installation

```bash
pipx install tofuref
```

## Usage

Run the application:

```bash
tofuref
```

### Controls

#### Actions

| keybindings   | action                                                                           |
|---------------|----------------------------------------------------------------------------------|
| `s`, `/`      | **search** in the context of providers and resources                             |
| `u`, `y`      | context aware copying (using a provider/resource)                                |
| `v`           | change active provider **version**                                               |
| `b`           | persistently bookmark an item to prioritize them in sorting when next re-ordered |
| `q`, `ctrl+q` | **quit** tofuref                                                                 |
| `t`           | toggle **table of contents** from content window                                 |
| `B`           | from content window, open active page in browser                                 |
| `ctrl+g`      | open **GitHub** repository for provider                                          |
| `ctrl+s`      | Show **stats** of provider's github repo                                         |

> Note: The GitHub functionality tries to use your GitHub token (env or `gh` cli) to avoid rate limiting.

#### Focus windows

| keybindings               | action                     |
|---------------------------|----------------------------|
| `tab`                     | focus next window          |
| `shift+tab`               | focus previous window      |
| `p`                       | focus **providers** window |
| `r`                       | focus **resources** window |
| `c`                       | focus **content** window   |
| `backspace`, `left arrow` | focus previous window      |

### Navigate in a window

Navigate with arrows/page up/page down/home/end or your mouse.

VIM keybindings should be also supported in a limited capacity.

### Configuration

Default configuration can be overridden by a config file,
which can be overridden with env variables.

Config file locations:

* Unix: `~/.config/tofuref/config.toml`
* macOS: `~/Library/Application Support"/tofuref/config.toml`
* Windows: `%USERPROFILE%\AppData\Local\tofuref\tofuref\config.toml`

#### General

Put these as simple key=value in your config.toml.

| name                      | description                                                       | type  | default | env                                 |
|---------------------------|-------------------------------------------------------------------|-------|---------|-------------------------------------|
| http_request_timeout      | Timeout for all http requests (in seconds)                        | float | 3.0     | `TOFUREF_HTTP_REQUEST_TIMEOUT`      |
| index_cache_duration_days | How long the provider index should be cached for (in days)        | int   | 31      | `TOFUREF_INDEX_CACHE_DURATION_DAYS` |
| markdown_length_target    | Target markdown length (in characters) to keep tofuref responsive | int   | 40_000  | `TOFUREF_MARKDOWN_LENGTH_TARGET`    |

#### Theme

These options belong to a toml section, `[theme]`.

| name          | description                                                                                                                          | type   | default                               | env                           |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------|--------|---------------------------------------|-------------------------------|
| ui            | Colorscheme for the UI, inspect available themes through command palette (`^p`) `Change theme` command                               | string | textual-dark (or `TEXTUAL_THEME` env) | `TOFUREF_THEME_UI`            |
| codeblocks    | **CURRENTLY WORKS ONLY IN COPY MENU** The [pygments style](https://pygments.org/styles/) for code blocks                             | string | material                              | `TOFUREF_THEME_CODEBLOCKS`    |
| borders_style | The borders to use for windows, list and showcase of available [here](https://textual.textualize.io/styles/border/#all-border-types) | string | ascii                                 | `TOFUREF_THEME_BORDERS_STYLE` |
| emoji         | Whether to display emojis or letters as icons                                                                                        | bool   | true                                  | `TOFUREF_THEME_EMOJI`         |

#### Example file

Author's configuration:

```toml
[theme]
ui = "dracula"
codeblocks = "dracula"
borders_style = "vkey"
```

## Upgrade

```bash
pipx upgrade tofuref
```

## Development notes

### Setup

    uv sync (-p 3.14)

### Testing

Run tests:

    uv run --env-file=tests.env pytest

Update snapshots for tests if the diff was expected:

    uv run --env-file=tests.env pytest --snapshot-update

### Undocumented config options

Intended mainly for development.

Force downloading from API to see the first time load experience:

    TOFUREF_DISABLE_CACHE=1 uv run tofuref

Show popups with load times for provider/resource listings:

    TOFUREF_SHOW_LOAD_TIMES=1 uv run tofuref

Or combine those:

    TOFUREF_SHOW_LOAD_TIMES=1 TOFUREF_DISABLE_CACHE=1 uv run tofuref

# tofuref

[![PyPI - Version](https://img.shields.io/pypi/v/tofuref)](https://pypi.org/project/tofuref/)
![PyPI - License](https://img.shields.io/pypi/l/tofuref)
![PyPI - Downloads](https://img.shields.io/pypi/dm/tofuref)
![GitHub Repo stars](https://img.shields.io/github/stars/DJetelina/tofuref?style=flat&logo=github)

TUI for OpenTofu provider registry.

![Screenshot](https://github.com/djetelina/tofuref/blob/main/screenshots/welcome.svg?raw=true)

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

| keybindings   | action                                               |
|---------------|------------------------------------------------------|
| `s`, `/`      | **search** in the context of providers and resources |
| `u`, `y`      | Context aware copying (using a provider/resource)    |
| `v`           | change active provider **version**                   |
| `q`, `ctrl+q` | **quit** tofuref                                     |
| `t`           | toggle **table of contents** from content window     |
| `ctrl+l`      | display **log** window                               |

#### Focus windows

| keybindings | action                     |
|-------------|----------------------------|
| `tab`       | focus next window          |
| `shift+tab` | focus previous window      |
| `p`         | focus **providers** window |
| `r`         | focus **resources** window |
| `c`         | focus **content** window   |
| `f`         | toggle **fullscreen** mode |

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

| name                      | description                                                                     | type  | default | env                                 |
|---------------------------|---------------------------------------------------------------------------------|-------|---------|-------------------------------------|
| http_request_timeout      | Timeout for all http requests (in seconds)                                      | float | 3.0     | `TOFUREF_HTTP_REQUEST_TIMEOUT`      |
| index_cache_duration_days | How long the provider index should be cached for (in days)                      | int   | 31      | `TOFUREF_INDEX_CACHE_DURATION_DAYS` |
| fullscreen_init_threshold | Threshold of terminal width under which tofuref should start in fullscreen mode | int   | 125     | `TOFUREF_FULLSCREEN_INIT_THRESHOLD` |

#### Theme

These options belong to a toml section, `[theme]`.

| name          | description                                                                                                                          | type   | default                               | env                           |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------|--------|---------------------------------------|-------------------------------|
| ui            | Colorscheme for the UI, inspect available themes through command palette (`^p`) `Change theme` command                               | string | textual-dark (or `TEXTUAL_THEME` env) | `TOFUREF_THEME_UI`            |
| codeblocks    | The [pygments style](https://pygments.org/styles/) for code blocks                                                                   | string | material                              | `TOFUREF_THEME_CODEBLOCKS`    |
| borders_style | The borders to use for windows, list and showcase of available [here](https://textual.textualize.io/styles/border/#all-border-types) | string | ascii                                 | `TOFUREF_THEME_BORDERS_STYLE` |

#### Example file

Author's configuration:

```toml
fullscreen_init_threshold = 160

[theme]
ui = "monokai"
codeblocks = "monokai"
borders_style = "vkey"
```

## Upgrade

```bash
pipx upgrade tofuref
```

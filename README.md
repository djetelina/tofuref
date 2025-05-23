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
### Option

| option       | ^p                 | description                                     |
|--------------|--------------------|-------------------------------------------------|
| Fuzzy Search | :heavy_check_mark: | Enable fuzzy search in the context of resources |

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

## Upgrade

```bash
pipx upgrade tofuref
```

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
Navigate with arrows/page up/page down/home/end or your mouse.

| keybindings   | action                                               |
|---------------|------------------------------------------------------|
| `tab`         | focus next window                                    |
| `shift+tab`   | focus previous window                                |
| `enter`       | choose selected or finish search                     |
| `q`, `ctrl+q` | **quit** tofuref                                     |
| `s`, `/`      | **search** in the context of providers and resources |
| `v`           | change active provider **version**                   |
| `p`           | focus **providers** window                           |
| `u`, `y`      | copy ready-to-**use** provider version constraint    |
| `r`           | focus **resources** window                           |
| `c`           | focus **content** window                             |
| `f`           | toggle **fullscreen** mode                           |
| `l`           | display **log** window                               |

## Upgrade

```bash
pipx upgrade tofuref
```

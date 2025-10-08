# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-10-09

### Added

- Improved perceived responsiveness during app launch and when loading large providers
  - Subtitles now inform what is happening in the background
  - The screen gets refreshed more often, resulting in somewhat working loading indicators
  - Eliminate initial layout “jumping”
  - Note: Launch may be slightly slower; changes focus on perceived responsiveness

### Changed

- Default borders changed from `ascii` to `vkey`, you can still revert to `ascii` with your local configuration
- Welcome content was refreshed

### Fixed

- Normalized em/en dashes to hyphens so headings render correctly in the content viewer
- Corrected the cache purge notification to refer to the right item type (Resource vs Provider)
- Set a more descriptive subtitle for resource content pages
- Open in browser in the welcome tab now opens this changelog instead of crashing the application

## [1.4.0] - 2025-07-30

### Added

- Cached guides now display their intended page title instead of their 'name' taken from a doc filename
- In provider window, GitHub repo of the provider can now be opened in a browser with `ctrl+g`
- In provider window, GitHub stats for a provider's repo can now be shown with `s`
- Content can now be opened in browser (on OpenTofu registry web) with `B` for easier searching and sharing

### Changed

- Headers (frontmatter) of markdown documents in the registry are now handled by a proper library
- Numbers are now formatted according to locale
- Number of providers now have spaces around the `/` (out of) symbol
- Code block highlighting is no longer customizable due to a change in the TUI framework

## [1.3.0] - 2025-06-13

### Added

- Added a config option in the theme section to enable/disable emojis
- Added the ability to bookmark items with the keybinding `b`, identified by 📌 or `B`
- Cached items are now sorted first, identified by 🕓 or `C`
- Items can now be cleared from cache with `ctrl+d`
- Made name of the provider pop a little bit by dimming the organization

### Changed

- Replaced letters identifying resource types (`R`, `D`, `F`, `G`) with emojis

### Fixed

- Various colours should now adhere to the active theme, instead of being fixed

## [1.2.0] - 2025-06-06

### Added

- Configuration support through a file and env variables
- Notification when a newer version is available

### Changed

- The footer has been cleaned up, less important keybinds are now hidden

### Fixed

- Fallback for providers had an incorrect path
- Cache and Configuration directories are now truly cross-platform
  (they probably didn't work on Windows previously), macOS cache and config move as
  a result of this change

## [1.1.0] - 2025-05-23

### Added

- API responses are now persistently cached on the filesystem
    - Index of providers is valid for a month, to force refresh: `rm ~/.cache/tofuref/index.json`
    - Providers themselves are valid forever because they are versioned
- If the initial fetch of the provider index fails, a fallback version with top 50 providers and 5 newest versions is
  used
- `u`se (`y`ank) now works in the content window; it lets you select which codeblock found in the content to copy
- `escape` can now be used to cancel search
- Some windows now support limited vim bindings (`j`, `k`, `G`, `ctrl+f`, `ctrl+b`)
- Table of Contents can now be toggled in the content window, allowing for navigation between headers

### Fixed

- Content that contained markdown splits (`---`) is now properly fully considered as content
- `escape` in fullscreen mode no longer breaks fullscreen mode

### Changed

- All API requests now have a shorter timeout, 5s → 3s
- Keybind for showing log was changed from `l` to `ctrl+l` and hidden from the footer
- `u`se of a provider can now be invoked even when none has been selected yet, it will copy the highlighted one with
  their latest version

### Removed

- Dropped support for Python 3.9 because of a new dependency

## [1.0.1] - 2025-05-20

### Fixed

- Use provider configuration had `v` prefix in the version number
- Use provider configuration was missing a quote at the beginning of source
- Use provider configuration has a proper format (aligned `=`)

## [1.0.0] - 2025-05-19

### Added

- Use command (`u` or `y`) to copy provider configuration for `required_providers` block
- End-to-end tests have been added

## [0.4.0] - 2025-05-02

### Added

- Providers now have a version picker, when one is selected, press `v`
- Loading indicators
- Fullscreen mode
- Content now reacts to page up, page down, home and end

## [0.3.0] - 2025-05-01

### Added

- Content is now scrollable with arrows
- Added keybindings for focusing Providers/Resources/Content respectively
- Search now has alternative keybind `/`
- Added version to the welcome screen headline

### Changed

- Search now works per window, separately for providers and resources
- Log is now toggle-able, off by default

## [0.2.0] - 2025-05-01

### Added

- Whatever was before :)

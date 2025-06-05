# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

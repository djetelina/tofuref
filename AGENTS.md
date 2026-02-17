# AGENTS.md

## Purpose
- This document is the default operating guide for coding agents in this repository.
- Follow user instructions first, then this file, then local code conventions.
- Keep changes small, reviewable, and tightly scoped to the request.

## Changelog usage
- For any user-facing behavior change, update `CHANGELOG.md` under `## [Unreleased]` in the appropriate Keep a Changelog section (`Added`, `Changed`, `Fixed`, `Removed`).
- Keep entries concise and focused on user impact.

## Rule Sources (Cursor / Copilot)
- `.cursor/rules/`: not present.
- `.cursorrules`: not present.
- `.github/copilot-instructions.md`: not present.
- Treat this file as the primary agent instruction source for repo-specific behavior.

## Repository Snapshot
- Project: `tofuref` (Textual TUI for OpenTofu provider registry docs).
- Python requirement: `>=3.10` (`pyproject.toml`).
- Build backend: Hatchling.
- Main app entrypoint: `tofuref/main.py`.
- Package entrypoint: `tofuref.main:main` via script `tofuref`.
- UI widgets: `tofuref/widgets/`.
- Data and domain logic: `tofuref/data/`.
- Tests: `tests/` (pytest, pytest-asyncio, textual snapshots).

## Tooling Policy
- Prefer `just` recipes for routine workflows.
- If a commonly repeated command is missing from `justfile`, add a recipe.
- Use direct `uv run ...` commands only for one-off or debugging scenarios.

## Setup Commands
- Initial setup: `just init`
- What it does:
  - installs pre-commit hooks
  - syncs dependencies with `uv`

## Build / Run / Lint / Test Commands

### Daily commands (preferred)
- List available tasks: `just`
- Run app: `just run`
- Run full tests: `just test`
- Update all snapshots: `just test-update`
- Full checks (pre-commit): `just check`

### Single-test focused commands (important)
- Run a single test file:
  - `uv run --env-file=tests.env pytest tests/test_provider.py -v`
- Run a single test target (`file::test_name`):
  - `uv run --env-file=tests.env pytest tests/test_provider.py::test_provider_use -v`
- Run by pytest keyword expression:
  - `uv run --env-file=tests.env pytest -k provider_use -v`

### Equivalent direct commands (fallback)
- Full tests:
  - `uv run --env-file=tests.env pytest`
- One target:
  - `uv run --env-file=tests.env pytest tests/test_provider.py::test_provider_use -v`
- Lint:
  - `uv run ruff check .`
- Format:
  - `uv run ruff format .`

## CI Awareness
- CI runs Ruff and pytest workflows in GitHub Actions.
- Pytest matrix includes Python 3.10, 3.11, 3.12, 3.13, 3.14.
- Keep local changes compatible across the supported Python versions.

## Testing Guidelines
- Prefer targeted tests first, then broader test scope as needed.
- Always include `tests.env` for locale-sensitive test behavior.
- Network calls are mocked in `tests/conftest.py`; preserve that pattern.
- For UI changes, run relevant snapshot tests in `tests/test_snapshots.py`.
- When intentional UI output changes occur, update snapshots with `just test-update`.
- Do not use single-test snapshot updates; this snapshot setup expects full `just test-update` runs.
- Do not silently bless snapshot changes without checking intent.

## Formatting and Lint Rules
- Formatter: Ruff format.
- Max line length: `144`.
- Keep formatting tool-driven; avoid manual formatting churn.
- Lint rules are strict and include async, bugbear, pytest, pathlib, naming, and modernization checks.
- Favor code changes over ignore comments when practical.

## Import Conventions
- Use absolute imports from `tofuref` for internal modules.
- Import groups in this order:
  1. standard library
  2. third-party
  3. local package imports
- Keep imports sorted; let Ruff manage ordering.
- Remove unused imports and dead symbols.

## Typing Conventions
- Add type hints for new or modified public functions/methods.
- Prefer modern syntax: `list[str]`, `dict[str, X]`, `A | B`.
- Keep dataclass fields explicitly typed.
- Use `Literal` for constrained string domains where appropriate.
- Keep async return annotations explicit (`-> None`, etc.).

## Naming Conventions
- Modules/files: `snake_case.py`.
- Variables/functions/methods: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Internal/private attrs: leading underscore.

## Error Handling Conventions
- Prefer specific exceptions over broad `except Exception`.
- Handle expected external failures (HTTP, parsing, filesystem) explicitly.
- Keep return types consistent on success and failure paths.
- Never swallow errors without logging useful context.
- User-visible errors should degrade gracefully (fallbacks/notifications), not crash the app.

## Logging Conventions
- Use module logger: `LOGGER = logging.getLogger(__name__)`.
- `debug`: detailed flow and diagnostics.
- `info`: important state transitions.
- `warning`/`error`: failures and degraded behavior.
- Do not log secrets or tokens.

## Async, I/O, and Performance
- Keep runtime I/O async where feasible.
- Follow existing `anyio.Path` usage for async filesystem operations.
- Use `asyncio.gather(...)` only when operations are truly independent.
- Maintain responsive UI behavior around long operations (loading flags, incremental rendering).

## Textual UI Conventions
- Preserve keyboard-first behavior and existing keybind semantics.
- Keep keybinding declarations centralized where practical (`widgets/keybindings.py`).
- Respect focus transitions when opening/closing overlays and panels.
- Ensure content updates, notifications, and loading states remain coherent.

## Config, Cache, and Data Handling
- Access runtime settings via `tofuref.config.config`.
- Preserve cross-platform paths via `platformdirs`.
- Keep fallback provider index behavior functional (`tofuref/fallback/providers.json`).
- Avoid introducing machine-specific paths or assumptions.

## Documentation and Comments
- Keep docs concise and aligned with actual behavior.
- Update README/changelog/tests when user-facing behavior changes.
- Add comments only for non-obvious intent.
- Prefer ASCII in source/docs unless file already requires Unicode.

## Commit Message Conventions
- Use Conventional Commits format: `type(scope): summary`.
- Preferred types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`.
- Keep subject concise and imperative; focus on intent, not low-level file details.
- Add a brief body when needed to explain why a change was made.

## Change-Safety Checklist
- Run `uv run ruff format .` for formatting changes.
- Run `uv run ruff check .` (or `just check` for full pre-commit pass).
- Run targeted tests first, then broader tests as needed.
- For UI changes, run/update snapshot tests deliberately.
- Confirm no unrelated files were modified.

## Quick Agent Workflow
1. Read relevant files and nearby tests.
2. Implement minimal fix/feature.
3. Run formatting and targeted tests.
4. Run broader checks as needed (`just test`, `just check`).
5. Summarize what changed, why, and how it was verified.

# Repository Guidelines

## Project Structure & Module Organization
The Python sources live in `schachtmeister3/`; `main.py` boots the UDP daemon, `udp.py` handles Quake-style packets, `judge.py` orchestrates WHOIS lookups, and `common.py` collects shared types and defaults. `client.py` will grow into a CLI helper but is still a stub. Keep legacy C code in `schachtmeister2/` untouched for reference only. Tooling manifests (`project.toml`, `ruff.toml`, `mypy.ini`) sit at the repository root, and shared developer scripts belong under `scripts/` (see `scripts/check`).

## Build, Test, and Development Commands
Use uv for workflows: `uv run python -m schachtmeister3.main` starts the asyncio daemon once imports are aligned, and `uv run python -m schachtmeister3.client` will eventually query it. Run formatting and static checks with `scripts/check`. Pytest is the test runner: `uv run pytest` discovers tests under `tests/` once they exist.

## Coding Style & Naming Conventions
Ruff enforces PEP 484 typing, `flake8-quotes`, and import sorting. Keep lines ≤120 characters and prefer single quotes for literals; docstrings and multiline strings must stay double-quoted. Stick to snake_case for functions and variables, PascalCase for classes, and avoid unused symbols to keep lint clean. Type hints are required on all public callables per `mypy.ini`.

## Testing Guidelines
Add new tests beside the code they cover under `tests/`, mirroring the package layout (e.g., `tests/test_udp.py`). Name test functions `test_<behavior>` for clarity. Target async helpers with `pytest.mark.asyncio`. Run `uv run pytest` locally before opening a PR, and expand coverage whenever you touch networking or WHOIS integration to guard against regressions.

## Commit & Pull Request Guidelines
Write commits in the imperative mood (e.g., `Add UDP request parser`), keep scopes small, and include why the change matters in the body when needed. Reference GitHub issues in commit or PR descriptions. Pull requests should summarize behavior changes, note testing performed (`scripts/check`, `pytest`), and include screenshots or logs for user-facing flows such as the client CLI output.

# Agent Guidelines for Deplock

**Deplock** is an open-source Python utility package built to support lock files.

## Environment
- **Hermit**: Uses Hermit for managing tools (`uv`, `ruff`, etc.); activate with `source bin/activate-hermit` or use tools directly from `bin/`

## Code Style
- **NO COMMENTS**: Avoid superfluous comments unless code is unclear
- **Imports**: Use `from __future__ import annotations`; sort with isort (known-first-party: `block`, `deplock`)
- **Line length**: 120 chars max
- **Types**: All public functions/methods/classes require type hints; use `str | None` not `Optional[str]`
- **Naming**: PEP-8 (snake_case functions/vars, PascalCase classes); allow N803 exceptions, no PLR0913 enforcement
- **Pydantic**: Use `ConfigDict(extra="forbid")` for all models; inherit from `BaseModel`
- **Docstrings**: Required for all modules (D100), classes (D101), methods (D102), functions (D103)
- **Error handling**: Use `backoff` for retries; validate with Pydantic where possible
- **Testing**: Use pytest fixtures from `tests/conftest.py`; mock storage/trackers; no magic numbers in tests (except test files ignore PLR2004)
- **PR titles**: Use conventional commits (`fix:`, `feat:`, `chore:`, `docs:`)

## Architecture
TO BE ADDED
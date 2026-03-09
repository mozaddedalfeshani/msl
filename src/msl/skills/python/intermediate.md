# Skill: {{project_type}} — {{preference}}

## Code Style

- Write typed Python — add type hints to all function signatures and key variables.
- Prefer functions and dataclasses over heavy class hierarchies.
- Keep functions under ~30 lines; extract helpers when they grow.
- Follow PEP 8; enforce with `ruff` or `flake8` + `black`.
- Use `pathlib.Path` instead of `os.path` for file operations.

## Project Structure

- Use `src/` layout with `pyproject.toml` for packaging.
- Group by feature or domain: `src/myapp/auth/`, `src/myapp/api/`, etc.
- Shared utilities in a `utils/` or `core/` subpackage.
- Configuration in a dedicated module with environment variable validation.

## Framework

- For web APIs: use FastAPI or Flask with blueprints/routers to separate routes.
- Validate all request input with Pydantic models (FastAPI) or marshmallow (Flask).
- Keep route handlers thin — delegate business logic to service functions.

## Data

- Use SQLAlchemy or an async ORM with typed models.
- Keep database queries in a repository/service layer, not in route handlers.
- Use Alembic for schema migrations; keep migrations in version control.

## Error Handling

- Define custom exception classes for domain errors.
- Catch specific exceptions — never use bare `except:`.
- Log errors with `logging` module — avoid `print()` in production code.

## Testing

- Write unit tests with `pytest` for all business logic and utilities.
- Write integration tests for API endpoints using `httpx` or test client.
- Use `pytest-cov` for coverage; aim for ≥ 80 % on core logic.
- Mock external services with `unittest.mock` or `pytest-mock`.

## General

- Use virtual environments; prefer `uv` or `poetry` for dependency management.
- Validate environment variables at startup — fail fast on missing config.
- Use f-strings for string formatting, not `%` or `.format()`.
- Keep third-party dependencies minimal; evaluate before adding.

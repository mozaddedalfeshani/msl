# Skill: {{project_type}} — {{preference}}

## Code Style

- Write fully typed Python — use type hints on all function signatures, return types, and key variables.
- Use `dataclasses` or `pydantic.BaseModel` for structured data; avoid raw dicts for domain objects.
- Keep functions under ~30 lines; prefer pure functions where possible.
- Follow PEP 8; enforce with `ruff` (linting + formatting) on every commit.
- Use `pathlib.Path` for file operations, f-strings for formatting.

## Architecture

- **Layered design**: routes/CLI → services → repositories → database/external APIs.
  - `src/<pkg>/api/` — route definitions, request/response schemas.
  - `src/<pkg>/services/` — business logic, orchestration.
  - `src/<pkg>/repositories/` — data access, queries.
  - `src/<pkg>/models/` — domain entities, Pydantic schemas, ORM models.
  - `src/<pkg>/core/` — config, dependencies, exception classes.
- Use dependency injection (FastAPI `Depends`, or manual constructor injection) for testability.
- Package with `pyproject.toml` using `src/` layout.

## Framework

- **FastAPI** (preferred) or **Flask** for web APIs.
- Validate **all** input with Pydantic models — schemas define the contract.
- Keep route handlers thin: parse input → call service → return response.
- Use async where the framework supports it and I/O is the bottleneck.

## Database

- Use SQLAlchemy 2.0 (or async variant) with typed models.
- Keep queries in the repository layer; never write raw SQL in route handlers.
- Use Alembic for migrations; review every migration before applying.
- Wrap multi-step writes in transactions.
- Use connection pooling; configure pool size for production.

## Authentication & Security

- Validate JWTs or session tokens in middleware/dependencies.
- Never store secrets in code — use environment variables.
- Sanitise and validate all user input at the API boundary.
- Use parameterised queries exclusively — no string interpolation in SQL.
- Set security headers (CORS, HSTS) appropriately.

## Error Handling

- Define a hierarchy of custom exception classes in `core/exceptions.py`.
- Register global exception handlers that return structured JSON error responses.
- Log structured events with stdlib `logging` or `structlog`; never use `print()`.
- Attach a request ID to every log entry.

## Testing

- **Unit**: `pytest` for services, repositories, and utility functions.
- **Integration**: `httpx.AsyncClient` (FastAPI) or test client for endpoint tests.
- **E2E**: Test critical user flows against a real database in CI.
- Aim for ≥ 80 % coverage on `services/` and `repositories/`.
- Use `factory_boy` or fixtures for test data; `pytest-mock` for mocking.
- Run full test suite in CI on every pull request.

## Observability

- Use `structlog` or stdlib `logging` with JSON output for production.
- Add request-duration and error-rate metrics.
- Expose a `GET /health` endpoint that checks DB and critical service connectivity.

## CI / CD

- Lint (`ruff check`), type-check (`mypy --strict`), and test on every PR.
- Build with `python -m build`; publish to PyPI or private registry.
- Use multi-stage Docker builds for lean production images.
- Semantic versioning for releases.

## Performance

- Profile before optimising — use `cProfile` or `py-spy`.
- Use async I/O for network-bound operations.
- Cache expensive computations with Redis or `functools.lru_cache`.
- Use connection pooling for databases and HTTP clients.

## General

- Validate all required environment variables at startup — fail fast.
- Use `uv` or `poetry` for reproducible dependency management.
- Audit dependencies regularly; remove unused packages.
- Document non-obvious architectural decisions in `docs/` or ADR files.

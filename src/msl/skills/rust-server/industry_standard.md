# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Rust — `cargo clippy -- -D warnings` must pass.
- Prefer ownership and borrowing; `Arc<Mutex<T>>` only when shared mutable state is unavoidable.
- Return `Result<T, E>` from every fallible function; reserve `unwrap()` / `expect()` for tests and provably safe cases.
- Keep functions under ~40 lines; favour small, composable helpers.
- Use type aliases for complex types: `type DbPool = sqlx::PgPool;`.

## Architecture

- **Layered design**: handlers → services → repositories → database.
  - `src/routes/` — thin HTTP handlers that parse input and call services.
  - `src/services/` — business logic, transaction orchestration.
  - `src/repositories/` — data access, raw queries.
  - `src/models/` — domain entities, request DTOs, response DTOs.
  - `src/errors.rs` — central `AppError` enum.
  - `src/config.rs` — typed config loaded from env with validation.
- `src/main.rs` sets up tracing, config, DB pool, router, and graceful shutdown.

## Framework

- Use Axum with typed extractors (`Json`, `Path`, `Query`, `State`).
- Group routes with `Router::nest` by resource.
- Use tower middleware for cross-cutting concerns (CORS, request ID, rate limiting).

## Database

- Use `sqlx` with compile-time–checked queries (`sqlx::query_as!`).
- Keep migrations in `migrations/`, applied via `sqlx migrate run`.
- Every write operation runs inside an explicit transaction.
- Use connection pooling (`PgPool`) — never open ad-hoc connections.

## Error Handling

- Define `AppError` with `thiserror` and implement `IntoResponse`.
- Map every external error (DB, IO, auth) into an `AppError` variant with human-readable context.
- Return structured JSON error bodies: `{ "error": "...", "code": "..." }`.

## Authentication & Authorization

- Validate JWTs (or session tokens) in an Axum extractor or middleware.
- Check permissions at the handler level with a guard extractor.
- Never store secrets in code — load from environment variables.

## Observability

- Use `tracing` + `tracing-subscriber` for structured, levelled logging.
- Add a `request_id` to every log span via tower middleware.
- Expose a `/healthz` endpoint that checks the DB connection.
- Export metrics with `metrics` crate or Prometheus endpoint if needed.

## Testing

- **Unit**: test service and repository functions with mock DB or in-memory fixtures.
- **Integration**: spin up the full Axum app with a disposable test database (`sqlx::test`) and make HTTP requests with `reqwest`.
- **Property-based**: use `proptest` or `quickcheck` for serialisation round-trips and edge-case coverage.
- Aim for ≥ 80 % coverage on `services/` and `repositories/`.
- All tests run in CI on every PR.

## Performance

- Profile before optimising — use `flamegraph` or `tokio-console`.
- Prefer streaming responses for large payloads (`axum::body::StreamBody`).
- Use `tower::limit` for concurrency and rate limiting.

## Security

- Validate and sanitise all user input at the handler boundary.
- Use parameterised queries exclusively — never interpolate user data into SQL.
- Set security headers (HSTS, X-Content-Type-Options) via middleware.
- Audit dependencies with `cargo audit` in CI.

## CI / CD

- `cargo fmt --check`, `cargo clippy -- -D warnings`, and full test suite on every PR.
- Build release binaries with `--release` and strip debug symbols.
- Use multi-stage Docker builds for minimal container images.
- Tag releases with semantic versioning; automate changelog generation.

## General

- Pin the Rust toolchain in `rust-toolchain.toml`.
- Use `dotenvy` for `.env` loading; validate all required vars at startup in `config.rs`.
- Keep `Cargo.toml` dependencies sorted; audit quarterly.
- Document public API types and non-obvious logic with `///` doc comments.

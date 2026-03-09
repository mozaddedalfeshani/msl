# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Rust — run `cargo clippy` with zero warnings.
- Prefer ownership and borrowing; use `Arc` only for genuinely shared state.
- Return `Result<T, E>` from fallible functions; avoid `unwrap()` outside tests.
- Keep functions under ~40 lines; extract helpers rather than nesting deeply.

## Project Structure

- `src/main.rs` — entry point, server setup, graceful shutdown.
- `src/lib.rs` — re-exports modules.
- `src/routes/` — HTTP handler functions, one file per resource.
- `src/models/` — domain types, request/response DTOs.
- `src/services/` — business logic, database access.
- `src/errors.rs` — central error type with `thiserror` + `axum` `IntoResponse`.

## Framework

- Use Axum (or Actix-web). Keep handler signatures clean with extractors.
- Use a shared `AppState` passed via Axum's `State` extractor.

## Data

- Use `sqlx` (or Diesel) with compile-time query checking when possible.
- Keep database queries in the service layer, not in handlers.
- Use `serde` for JSON serialisation with `#[serde(rename_all = "camelCase")]`.

## Error Handling

- Define a unified `AppError` enum that implements `IntoResponse`.
- Map external errors (DB, IO) into `AppError` variants with context.

## Testing

- Write unit tests for service functions and utility modules.
- Write integration tests that spin up the server against a test database.
- Use `#[tokio::test]` for async tests.

## General

- Pin your Rust toolchain version in `rust-toolchain.toml`.
- Use `dotenvy` for environment config; validate required vars at startup.
- Enable `cargo fmt` in CI — no formatting drift.

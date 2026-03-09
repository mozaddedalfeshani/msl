# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Rust — use `clippy` defaults and fix all warnings.
- Prefer ownership and borrowing over `Rc`/`Arc` unless shared state is truly needed.
- Keep functions short and focused; favour returning `Result<T, E>` over panicking.
- Use meaningful names — avoid single-letter variables outside short closures.

## Project Structure

- Separate binary (`src/main.rs`) and library (`src/lib.rs`) concerns.
- Group related modules in sub-directories: `src/routes/`, `src/models/`, `src/services/`.

## General

- Use `serde` for all serialisation/deserialisation.
- Prefer `thiserror` for defining custom error types.
- Let the compiler guide you — fix warnings before committing.

# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Go — `go vet`, `staticcheck`, and `golangci-lint` must pass.
- Handle every error explicitly — never discard with `_`.
- Keep functions under ~40 lines; extract helpers when they grow.
- Use receiver methods for types that own behaviour; functions for stateless operations.

## Project Structure

```
cmd/<appname>/main.go   — entry point
internal/               — private application code
  handler/              — HTTP handlers
  service/              — business logic
  repository/           — data access
  model/                — domain types
pkg/                    — public reusable packages (if any)
```

## Framework & Routing

- Use `net/http` with a router (Chi, Gorilla Mux, or stdlib `http.ServeMux` in Go 1.22+).
- Keep handlers thin — parse request, call service, write response.
- Use middleware for cross-cutting concerns (logging, auth, CORS).

## Data

- Use `database/sql` with `sqlx` or an ORM like `ent`.
- Use parameterised queries — never interpolate user input into SQL.
- Keep database logic in the repository layer.
- Use migrations (`golang-migrate` or `goose`).

## Error Handling

- Define sentinel errors or custom error types for domain errors.
- Wrap errors with `fmt.Errorf("context: %w", err)` for stack context.
- Return structured JSON error responses from handlers.

## Testing

- Write table-driven tests using `testing` package.
- Write integration tests for handlers with `httptest`.
- Use interfaces for dependencies to enable mocking.
- Run tests in CI with `-race` flag.

## General

- Use `context.Context` for cancellation, timeouts, and request-scoped values.
- Prefer the standard library; evaluate third-party packages carefully.
- Use `go mod tidy` to keep dependencies clean.
- Use structured logging (`slog` in Go 1.21+ or `zerolog`/`zap`).

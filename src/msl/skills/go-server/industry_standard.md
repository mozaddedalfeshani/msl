# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Go — `golangci-lint` with an aggressive config must pass cleanly.
- Handle every error explicitly with `fmt.Errorf("context: %w", err)`.
- Keep functions under ~40 lines; favour small, composable helpers.
- Use clear naming — avoid stuttering, abbreviations only when universally understood.
- Avoid `init()` functions; prefer explicit setup in `main()`.

## Architecture

- **Layered design**: handlers → services → repositories → storage.
  - `cmd/<app>/main.go` — entry, config, DI wiring, graceful shutdown.
  - `internal/handler/` — HTTP handlers, request parsing, response writing.
  - `internal/service/` — business logic, orchestration.
  - `internal/repository/` — database/cache access.
  - `internal/model/` — domain types, DTOs.
  - `internal/middleware/` — auth, logging, rate limiting, CORS.
  - `internal/config/` — typed config loaded from env.
- Use interfaces at layer boundaries for testability; define them where they're consumed.

## Framework & Routing

- Use `net/http` + Chi (or stdlib `http.ServeMux` in Go 1.22+).
- Group routes by resource with `r.Route("/users", ...)`.
- Middleware stack: request ID → logger → recover → auth → handler.

## Database

- Use `database/sql` + `sqlx` (or `pgx` directly for PostgreSQL).
- All queries parameterised — no string interpolation of user input.
- Wrap multi-step writes in explicit transactions.
- Use connection pooling with sensible `MaxOpenConns`, `MaxIdleConns`, `ConnMaxLifetime`.
- Migrations with `golang-migrate` or `goose`; review before applying.

## Authentication & Security

- Validate JWTs or session tokens in middleware.
- Check permissions per handler or per route group.
- Store secrets in environment variables only.
- Set security headers (HSTS, X-Content-Type-Options) in middleware.
- Audit dependencies with `govulncheck` in CI.

## Error Handling

- Define domain error types that implement `error` interface.
- Use sentinel errors for expected cases (`ErrNotFound`, `ErrUnauthorized`).
- Map domain errors to HTTP status codes in a central response helper.
- Never expose raw error messages to clients.

## Observability

- Use `slog` (Go 1.21+) or `zerolog`/`zap` for structured JSON logging.
- Attach `requestID`, `userID` to every log via context.
- Expose a `GET /healthz` endpoint (DB + critical dependency checks).
- Add request-duration and error-rate metrics (Prometheus or OTEL).
- Use OpenTelemetry for distributed tracing in service-to-service calls.

## Testing

- **Unit**: table-driven tests for services, repositories, utilities.
- **Integration**: `httptest.Server` for handler tests with a test database.
- **Race detection**: always test with `-race`.
- Aim for ≥ 80 % coverage on `service/` and `repository/`.
- Use interfaces + generated mocks (`mockgen` or `moq`) for dependencies.
- Run full suite in CI on every PR.

## Performance

- Profile before optimising — use `pprof`.
- Pool expensive resources (DB connections, HTTP clients, buffers) with `sync.Pool`.
- Use `context.Context` for all I/O with proper timeouts.
- Benchmark hot paths with `testing.B`.

## CI / CD

- `golangci-lint`, `go vet`, `staticcheck`, and test with `-race` on every PR.
- Build with `CGO_ENABLED=0` for static binaries.
- Multi-stage Docker builds for minimal images (scratch or distroless).
- Semantic versioning; automate changelog generation.

## General

- Prefer the standard library; evaluate third-party packages carefully.
- One `go.mod` per deployable service (avoid monorepo pitfalls unless intentional).
- `go mod tidy` before every commit.
- Document exported types and non-obvious logic with `//` comments.
- Pin Go toolchain version in `go.mod` or CI config.

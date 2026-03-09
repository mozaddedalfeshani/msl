# Skill: {{project_type}} — {{preference}}

## Code Style

- Write idiomatic Go — run `go vet` and `golint` with no warnings.
- Use short, clear variable names; avoid stuttering (e.g. `user.UserName` → `user.Name`).
- Keep functions focused and short.
- Handle every error — never use `_` to discard errors.

## Project Structure

- Use the standard layout: `cmd/` for binaries, `internal/` for private packages.
- Keep `main.go` minimal — just setup and start.

## General

- Use `context.Context` for cancellation and timeouts.
- Prefer the standard library before reaching for third-party packages.
- Use `go mod` for dependency management.

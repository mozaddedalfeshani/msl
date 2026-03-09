# Skill: {{project_type}} — {{preference}}

## Code Style

- Write strict TypeScript everywhere — no `any`, no type assertions unless unavoidable.
- Use `async/await`; keep the happy path un-indented and early-return on errors.
- Keep functions under ~40 lines; favour small, composable helpers.
- Follow consistent naming: `camelCase` for variables/functions, `PascalCase` for classes/types.
- Enforce ESLint + Prettier on every file; no lint warnings in CI.

## Architecture

- **Layered design**: routes → controllers → services → repositories → database.
  - `src/routes/` — route definitions only (path, method, middleware, controller call).
  - `src/controllers/` — parse request, call service, send response.
  - `src/services/` — business logic, transaction orchestration.
  - `src/repositories/` — data access, query construction.
  - `src/models/` — domain entities, Prisma/Drizzle schema.
  - `src/middleware/` — auth, validation, error handling, request logging.
  - `src/config/` — typed config loaded from env with validation (Zod).
- Entry point (`src/server.ts`) wires middleware, routes, and starts listening.

## Framework

- Use Fastify, Express, or Hono. Keep handlers as thin as possible.
- Validate **all** request input (body, params, query, headers) at the route boundary with Zod.
- Use dependency injection (manual or via a container like `tsyringe`) for testability.

## Database

- Use Prisma or Drizzle with typed, parameterised queries — never interpolate user data into SQL.
- Keep migrations in version control; review before applying.
- Wrap multi-step writes in explicit transactions.
- Use connection pooling; never open ad-hoc connections.

## Authentication & Authorization

- Validate JWTs (or session tokens) in middleware — never in individual handlers.
- Check permissions with a guard middleware per route.
- Store secrets in environment variables only; rotate regularly.
- Use HttpOnly, Secure, SameSite cookies for session tokens.

## Error Handling

- Central error-handling middleware that catches all thrown/rejected errors.
- Define typed error classes: `AppError`, `NotFoundError`, `ForbiddenError`, etc.
- Return structured JSON error bodies: `{ "error": "...", "code": "..." }`.
- Log full stack traces server-side; never expose them to clients.

## Observability

- Use structured logging (pino, winston) — no bare `console.log` in production.
- Attach a unique `requestId` to every log entry via middleware.
- Expose a `GET /health` endpoint that verifies DB and external service connectivity.
- Add request duration and status code metrics.

## Testing

- **Unit**: Vitest or Jest for services, repositories, and utilities.
- **Integration**: `supertest` for route-level tests against a running app with a test database.
- **E2E**: Playwright or a dedicated API test runner for critical flows.
- Aim for ≥ 80 % coverage on `services/` and `repositories/`.
- Run full test suite in CI on every pull request.

## Performance

- Profile before optimising — use Node.js `--inspect` and flame graphs.
- Use streaming for large response payloads.
- Implement rate limiting and request size limits in middleware.
- Cache expensive computations or queries (Redis or in-memory).

## Security

- Validate and sanitise all user input at the route boundary.
- Use parameterised queries exclusively.
- Set security headers (Helmet or equivalent): HSTS, X-Content-Type-Options, CSP.
- Audit dependencies with `npm audit` or `pnpm audit` in CI.
- Never log sensitive data (passwords, tokens, PII).

## CI / CD

- Lint, type-check (`tsc --noEmit`), and test on every PR.
- Build with `tsc` or `esbuild`; deploy compiled JS, not raw TS.
- Use multi-stage Docker builds for minimal production images.
- Semantic versioning for releases; automate changelog generation.

## General

- Validate all required environment variables at startup — fail fast on missing config.
- Keep `package.json` dependencies sorted; audit quarterly, remove unused packages.
- Document non-obvious architectural decisions in `docs/` or ADR files.

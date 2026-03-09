# Skill: {{project_type}} — {{preference}}

## Code Style

- Write TypeScript with strict mode enabled — avoid `any`.
- Use `async/await`; keep the happy path un-indented.
- Keep functions under ~40 lines; extract helpers when they grow.
- Follow consistent naming: `camelCase` for variables/functions, `PascalCase` for classes/types/interfaces.
- Enforce formatting with Prettier and linting with ESLint.

## Project Structure

- `src/server.ts` — app bootstrap, middleware setup, listen.
- `src/routes/` — route definitions, one file per resource.
- `src/controllers/` — request handling logic.
- `src/services/` — business logic, database calls.
- `src/models/` — data models / schemas (Prisma, Drizzle, or Mongoose).
- `src/middleware/` — custom Express/Fastify middleware.
- `src/utils/` — shared helpers and constants.
- `src/types/` — TypeScript type/interface definitions.

## Framework

- Use Express, Fastify, or Hono. Keep route handlers thin — delegate to services.
- Validate request bodies and params with Zod or Joi at the route boundary.

## Data

- Use an ORM/query builder (Prisma or Drizzle) with typed queries.
- Keep database access in the service layer, not in route handlers.
- Run migrations through the ORM's migration tooling.

## Error Handling

- Use a central error-handling middleware that catches all errors.
- Define typed error classes (e.g. `NotFoundError`, `ValidationError`).
- Return consistent JSON error responses with appropriate HTTP codes.

## Testing

- Write unit tests for services and utilities with Vitest or Jest.
- Write integration tests for routes using `supertest` or equivalent.
- Mock external services and databases in tests.

## General

- Use `dotenv` or framework-native config for environment variables.
- Never hard-code secrets — validate required env vars at startup.
- Add a health-check endpoint (`GET /health`).

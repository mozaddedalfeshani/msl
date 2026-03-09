# Skill: {{project_type}} — {{preference}}

## Code Style

- Write TypeScript for all files — avoid `any`.
- Use `async/await` over raw Promises and callbacks.
- Keep functions small and focused.
- Follow consistent naming: `camelCase` for variables/functions, `PascalCase` for classes/types.

## Project Structure

- Entry point in `src/index.ts` or `src/server.ts`.
- Group by feature: `src/routes/`, `src/services/`, `src/models/`.
- Shared utilities in `src/utils/`.

## General

- Use Express, Fastify, or Hono — keep handler logic thin.
- Use environment variables for configuration; never hard-code secrets.
- Handle errors with try/catch and return proper HTTP status codes.

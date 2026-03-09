# Skill: {{project_type}} — {{preference}}

## Code Style

- Write TypeScript for all files — avoid `any`; prefer strict mode.
- Use functional components with hooks.
- Keep components small and focused; extract when they exceed ~80 lines.
- Use named exports; avoid default exports.
- Enforce consistent formatting with Prettier and linting with ESLint.

## Project Structure

- `src/components/` — reusable UI components, grouped by domain.
- `src/pages/` or `src/routes/` — route-level components.
- `src/hooks/` — custom React hooks.
- `src/lib/` — API clients, utilities, constants.
- `src/types/` — shared TypeScript types and interfaces.

## State Management

- Use React Context or Zustand for global state — keep stores small and focused.
- Prefer URL state (search params) for filter/sort/pagination state.
- Use React Query or SWR for server state with proper cache invalidation.

## Routing

- Use React Router (v6+) with lazy-loaded routes for code splitting.
- Define routes declaratively in a central file.

## Styling

- Tailwind CSS as the primary approach; extract repeated patterns into components.
- Avoid inline styles and global CSS.

## Testing

- Write unit tests for hooks and utility functions with Vitest.
- Write component tests for interactive UI with React Testing Library.

## General

- Use `React.StrictMode` and fix all warnings.
- Use Vite environment variables (`import.meta.env`) — never hard-code secrets.
- Optimise images with proper formats and lazy loading.

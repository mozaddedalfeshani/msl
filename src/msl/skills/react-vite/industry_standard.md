# Skill: {{project_type}} — {{preference}}

## Code Style

- Write strict TypeScript everywhere — no `any`, no type assertions unless unavoidable.
- Use functional components with hooks; never use class components.
- Keep components under ~100 lines — extract early.
- Use named exports; avoid default exports.
- Enforce ESLint + Prettier on every file; no lint warnings in CI.

## Architecture

- **Feature-based** folder structure under `src/features/<name>/`.
  Each feature owns its own components, hooks, types, and API calls.
- Shared primitives live in `src/components/ui/`.
- Business logic (API clients, helpers) lives in `src/lib/`.
- Type definitions in `src/types/`, validation schemas in `src/schemas/` (Zod recommended).

## State Management

- Server state with React Query or SWR — never store API data in global stores.
- Client state with Zustand; keep stores feature-scoped and small.
- URL state for anything that should survive a page refresh (filters, tabs, pagination).

## Routing

- React Router v6+ with lazy-loaded routes via `React.lazy` + `<Suspense>`.
- Protected routes via a guard wrapper component, not per-page checks.
- Define all routes in a central `src/routes.tsx`.

## Styling

- Tailwind CSS with a strict design-token–based `tailwind.config.ts`.
- No global CSS aside from base resets and font loading.
- Extract repeated utility groups into reusable component abstractions.

## API Layer

- Centralise all API calls in `src/lib/api/` with typed request/response schemas.
- Validate API responses at the boundary with Zod.
- Use Axios or `fetch` with interceptors for auth tokens and error normalisation.

## Error Handling

- Global error boundary at the app root and per-route error boundaries.
- Toast/notification component for transient user-facing errors.
- Log unexpected errors to a remote service (Sentry or equivalent).

## Testing

- **Unit**: Vitest for utilities, hooks, and service functions.
- **Component**: React Testing Library for interactive components.
- **E2E**: Playwright or Cypress for critical user flows.
- Aim for ≥ 80 % coverage on `src/lib/` and `src/features/`.
- Tests must pass in CI on every pull request.

## Performance

- Code-split at the route level; lazy-load heavy components.
- Use `React.memo` only after profiling shows unnecessary re-renders.
- Analyse bundle size with `rollup-plugin-visualizer`; keep total JS < 200 KB gzipped.
- Optimise images: use WebP/AVIF, lazy-load below the fold.

## Security

- Sanitise user-generated HTML before rendering.
- Store auth tokens in HttpOnly cookies when possible — never localStorage for sensitive tokens.
- Validate all user input on both client and server.

## CI / CD

- Lint, type-check (`tsc --noEmit`), and test on every PR.
- Preview deployments for every feature branch.
- Semantic versioning for releases.

## General

- Use `React.StrictMode` in development and fix all warnings.
- Audit dependencies quarterly; remove unused packages.
- Document non-obvious decisions in `docs/` or ADR files.

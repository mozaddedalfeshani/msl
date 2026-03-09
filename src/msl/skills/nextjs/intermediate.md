# Skill: {{project_type}} — {{preference}}

## Code Style

- Write TypeScript for all files — avoid `any`; prefer strict mode.
- Use functional components with hooks.
- Keep components small and single-responsibility.
- Follow Next.js App Router conventions (file-based routing in `app/`).
- Use named exports for components, default exports only for page/layout files.
- Enforce consistent formatting with Prettier and linting with ESLint.

## Project Structure

- `app/` — pages, layouts, loading/error boundaries.
- `components/` — reusable UI components, organised by domain.
- `lib/` — business logic, API clients, utilities.
- `types/` — shared TypeScript interfaces and types.
- `public/` — static assets.

## Data Fetching

- Prefer Server Components and `fetch` with caching options over client-side data hooks.
- Use `loading.tsx` and `error.tsx` for per-route loading/error states.
- Validate and type API responses at the boundary.

## Styling

- Use Tailwind CSS utility classes as the primary styling approach.
- Extract repeated patterns into component-level abstractions, not global utilities.

## SEO & Metadata

- Export a `metadata` object or `generateMetadata` function from every page.
- Provide Open Graph and Twitter card meta for shareable pages.

## Testing

- Write unit tests for utility functions and business logic with Vitest or Jest.
- Write component tests for interactive UI with React Testing Library.
- Test critical pages with Playwright for end-to-end coverage.

## General

- Prefer Server Components by default; add `"use client"` only for interactivity.
- Handle environment variables through `env.local` and validate them at startup.
- Keep `next.config.js` minimal and well-commented.

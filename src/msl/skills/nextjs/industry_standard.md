# Skill: {{project_type}} — {{preference}}

## Code Style

- Write strict TypeScript everywhere — no `any`, no type assertions unless unavoidable.
- Use functional components with hooks; never use class components.
- Keep components under ~100 lines — extract when they grow.
- Colocate route files: `page.tsx`, `loading.tsx`, `error.tsx`, `layout.tsx`, `not-found.tsx`.
- Use named exports for components; default export only where Next.js requires it.

## Architecture

- **App Router** (`app/`) for all routing.
- Group routes by domain: `app/(marketing)/`, `app/(dashboard)/`, `app/(auth)/`.
- Business logic lives in `lib/services/` — components never call APIs or databases directly.
- Type definitions in `types/`, validation schemas in `lib/schemas/` (Zod recommended).
- Shared UI primitives in `components/ui/`; feature-scoped components stay with their route.

## Data Fetching & Caching

- Fetch in Server Components with `fetch()` and fine-grained `revalidate` / `cache` settings.
- Use React Server Actions for mutations; keep them in dedicated `actions.ts` files.
- Client-side interactive data uses React Query or SWR with proper stale/cache/refetch config.
- Use `loading.tsx` + `<Suspense>` for progressive streaming.

## State Management

- Prefer URL state (search params) and server state over client-side global stores.
- When client state is needed, use React Context sparingly; keep it feature-scoped.

## Styling

- Tailwind CSS as the primary styling system.
- Extract repeated utility groups into component abstractions, not `@apply` blocks.
- No global CSS aside from base resets and font loading.

## Authentication & Authorization

- Handle auth in middleware (`middleware.ts`) for route protection.
- Never trust client-side auth checks alone — validate on every server action and API route.
- Store session tokens in HttpOnly cookies, not localStorage.

## SEO & Performance

- Export `metadata` / `generateMetadata` from every page and layout.
- Use `next/image` with explicit `width`/`height` or `fill`; always set `alt`.
- Lazy-load heavy components with `next/dynamic`.
- Analyse bundle with `@next/bundle-analyzer`; keep client JS minimal.
- Target Core Web Vitals: LCP < 2.5 s, CLS < 0.1, INP < 200 ms.

## Error Handling & Logging

- Add `error.tsx` boundaries in every route group.
- Log server-side errors to a structured logging service (not `console.log` in production).
- User-facing errors go through a central toast/notification component.

## Testing

- **Unit**: Vitest or Jest for utilities, hooks, and service functions.
- **Component**: React Testing Library for interactive components.
- **E2E**: Playwright for critical user flows (auth, checkout, CRUD).
- Aim for ≥ 80 % coverage on `lib/` and `components/`.
- Run the full test suite in CI on every pull request.

## Database & ORM

- Use Prisma or Drizzle with typed queries; never write raw SQL outside migrations.
- Keep migrations in version control; review before applying.
- Validate all user input with Zod schemas before it reaches the database.

## CI / CD

- Lint (`eslint`), type-check (`tsc --noEmit`), and test on every PR.
- Preview deployments for every branch (Vercel, Netlify, or equivalent).
- Tag releases with semantic versioning.

## Security

- Sanitise and validate all user input on the server.
- Set security headers via `next.config.js` (`headers()`).
- Never expose secrets to the client — use `NEXT_PUBLIC_` prefix only for truly public values.

## General

- Use Server Components by default; add `"use client"` only when interactivity demands it.
- Use `next/link` for navigation, `next/image` for images.
- Keep dependencies lean — audit quarterly, remove unused packages.
- Document non-obvious architectural decisions in a `docs/` folder or ADR files.

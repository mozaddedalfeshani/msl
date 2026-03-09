# Skill: {{project_type}} — {{preference}}

## Code Style

- Write TypeScript for all files — avoid `any`.
- Use functional components with hooks.
- Keep components small and single-responsibility.
- Follow Next.js App Router conventions (file-based routing in `app/`).
- Use named exports for components, default exports only for pages.

## Project Structure

- Pages and layouts live in `app/`.
- Reusable components go in `components/`.
- Shared utilities go in `lib/` or `utils/`.

## General

- Prefer Server Components by default; add `"use client"` only when needed.
- Use CSS Modules or Tailwind CSS — avoid global styles leaking across components.
- Keep `next.config.js` minimal and well-commented.

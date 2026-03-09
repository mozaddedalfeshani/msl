# Skill: {{project_type}} — {{preference}}

## Code Style

- Write clean, modular Dart code with small, focused functions.
- Use `const` constructors wherever possible.
- Prefer `StatelessWidget` unless local mutable state is required.
- Keep widget build methods short — extract sub-widgets into their own classes.
- Follow Dart naming conventions: `lowerCamelCase` for variables/functions, `UpperCamelCase` for classes/enums.
- Use trailing commas on every argument list for consistent `dart format` output.
- Run `dart analyze` with zero warnings before every commit.

## Architecture

- Follow Clean Architecture with three layers: **domain** → **data** → **presentation**.
  - `domain/`: entities, repository interfaces, use-cases (pure Dart, no Flutter imports).
  - `data/`: repository implementations, data sources, DTOs, mappers.
  - `presentation/`: widgets, pages, view-models / state notifiers.
- Feature folders live under `lib/features/<name>/` and each contain their own `domain/`, `data/`, `presentation/` sub-trees.
- Shared code lives in `lib/core/` (theme, routing, DI, constants, extensions).

## State Management

- Use Riverpod (recommended) or BLoC. Pick one and use it consistently.
- Keep providers/cubits scoped to their feature.
- Never store derived state — compute it lazily from source providers.
- Use `AsyncValue` / `AsyncNotifier` for data that comes from the network.

## Dependency Injection

- Register dependencies in a dedicated DI module (e.g. `lib/core/di/`).
- Inject via constructor or Riverpod provider overrides — never use service locators in widgets.

## Data & Networking

- Use the repository pattern with an abstract interface in `domain/` and concrete implementation in `data/`.
- Parse API responses into immutable models generated with `freezed` + `json_serializable`.
- Handle all errors with sealed result types — never catch and swallow exceptions silently.
- Use `dio` or `http` with interceptors for auth, logging, and retry.

## Routing

- Use `go_router` for declarative, type-safe, deep-link-aware navigation.
- Define routes in `lib/core/routing/` with a single `GoRouter` instance.
- Guard authenticated routes with redirect logic, not widget-level checks.

## Testing

- **Unit tests** for every use-case, repository, and utility function.
- **Widget tests** for every screen and reusable interactive component.
- **Integration tests** for critical user journeys (sign-in, checkout, etc.).
- Aim for ≥ 80 % line coverage on `domain/` and `data/` layers.
- Use `mocktail` for mocking; prefer fakes over mocks when behaviour matters.
- Run tests in CI on every pull request.

## Error Handling & Logging

- Define a global error handler with `FlutterError.onError` and `PlatformDispatcher.instance.onError`.
- Log structured events (not raw strings) to a remote service (Sentry, Crashlytics, etc.).
- Show user-facing error messages through a central error-display mechanism, not ad-hoc `SnackBar` calls.

## Performance

- Profile with DevTools before optimising — measure first.
- Use `RepaintBoundary` to isolate frequently repainting sub-trees.
- Lazy-load heavy features with deferred imports (`deferred as`).
- Keep the main isolate free of CPU-intensive work; use `compute()` or isolates.

## Accessibility & Localisation

- Add `Semantics` labels to all interactive and informational widgets.
- Do not hard-code user-visible strings — use `intl` / `arb` files from day one.
- Support dynamic type scaling; avoid fixed font sizes.

## CI / CD

- Lint, analyse, and test on every PR (GitHub Actions or equivalent).
- Automate builds and uploads with Fastlane or Codemagic.
- Tag releases with semantic versioning and generate changelogs.

## General

- Prefer composition over inheritance for widgets.
- Use `final` for variables that are not reassigned.
- Avoid deeply nested widget trees — break them up.
- Keep third-party dependencies to a minimum; evaluate before adding.
- Document public APIs with `///` doc comments when intent is not obvious from the name.

# Skill: {{project_type}} — {{preference}}

## Code Style

- Write clean, modular Dart code with small, focused functions.
- Use `const` constructors wherever possible.
- Prefer `StatelessWidget` unless local mutable state is required.
- Keep widget build methods short — extract sub-widgets into their own classes.
- Follow Dart naming conventions: `lowerCamelCase` for variables/functions, `UpperCamelCase` for classes/enums.
- Use trailing commas to improve formatting with `dart format`.

## Project Structure

- Organise by feature: `lib/features/<name>/` with sub-folders for `widgets/`, `models/`, `providers/`.
- Shared code goes in `lib/core/` (theme, routing, constants, extensions).
- Keep one public class per file.

## State Management

- Use Riverpod (or BLoC) for state that crosses widget boundaries.
- Keep state providers close to the feature that owns them.
- Avoid storing derived state — compute it from source providers.

## Data & Networking

- Use the repository pattern: abstract data sources behind a repository interface.
- Parse API responses into immutable model classes (consider `freezed` + `json_serializable`).
- Handle errors with typed results (e.g. `Either`, `AsyncValue`, sealed classes).

## Routing

- Use `go_router` (or `auto_route`) for declarative, type-safe navigation.
- Define all routes in a single file or a dedicated routing feature folder.

## Testing

- Write widget tests for every screen and critical interactive widget.
- Write unit tests for business logic, repositories, and state providers.
- Use `mocktail` or `mockito` for dependency mocking.

## General

- Prefer composition over inheritance for widgets.
- Use `final` for variables that are not reassigned.
- Avoid deeply nested widget trees — break them up.
- Follow Material 3 / Cupertino guidelines for platform-appropriate design.

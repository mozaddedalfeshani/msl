# Skill: {{project_type}} — {{preference}}

## Code Style

- Write clean, modular Dart code with small, focused functions.
- Use `const` constructors wherever possible.
- Prefer `StatelessWidget` unless local mutable state is required.
- Keep widget build methods short — extract sub-widgets into their own classes.
- Follow Dart naming conventions: `lowerCamelCase` for variables and functions, `UpperCamelCase` for classes and enums.

## Project Structure

- Organise files by feature, not by type (e.g. `lib/features/auth/` instead of `lib/widgets/`, `lib/models/`).
- Keep one public class per file.

## General

- Prefer composition over inheritance for widgets.
- Use `final` for variables that are not reassigned.
- Avoid deeply nested widget trees — break them up.

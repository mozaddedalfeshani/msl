# Skill: {{project_type}} — {{preference}}

## Code Style

- Write clean, readable Python with clear variable and function names.
- Prefer functions over classes unless state management is needed.
- Use type hints for function signatures.
- Keep functions short and focused — one job per function.
- Follow PEP 8 conventions.

## Project Structure

- Keep a flat, simple structure: `src/` or a single package folder.
- One module per concern — don't put everything in one file.

## General

- Use virtual environments (`venv`, `uv`, or `poetry`).
- Pin dependencies in `requirements.txt` or `pyproject.toml`.
- Handle errors with specific exceptions, not bare `except:`.

# MSL — Muradian Skill Languages

Generate platform-specific skill/rule files for AI coding assistants with one command. No need to remember which file goes where — `msl` handles the structure for you.

## Install

```bash
pip install msl
```

## Usage

```bash
msl
```

The wizard will:

1. **Detect** your environment (Node.js, Cursor, VS Code, Claude Code, Codex)
2. **Scan** your project to auto-detect frameworks, languages, package manager
3. **Ask** which platform to target
4. **Ask** your project path (current directory or custom)
5. **Ask** your project type (auto-suggested from scan)
6. **Ask** your preference level (Simple → Industry Standard)
7. **Generate** the correct file in the right location with project-aware content

```
╭──────────────────────────────────────╮
│  MSL — Muradian Skill Languages     │
╰──────────────────────────────────────╯

  Environment Check
  ✓ Node.js  v20.11.0
  ✓ Cursor   0.45.0
  ✓ VS Code  1.89.1
  ✓ Claude   2.1.0
  ✓ Codex    0.72.0

  Project Scan
  Name:       my-saas-app
  Languages:  TypeScript
  Detected:   Next.js, App Router, tailwindcss, prisma
  Type:       Web (Next.js) (95% confidence)
```

## Supported Platforms

| Platform    | Output Path                       |
| ----------- | --------------------------------- |
| Cursor      | `.cursor/rules.md`                |
| VS Code     | `.github/copilot-instructions.md` |
| Claude Code | `CLAUDE.md`                       |
| Codex       | `AGENTS.md`                       |

## Supported Project Types

- **Flutter** — Dart, widgets, state management, routing
- **Web (Next.js)** — App Router, Server Components, data fetching
- **Web (React/Vite)** — SPA, hooks, React Router, Zustand
- **Rust (Server)** — Axum/Actix, async, sqlx, error handling
- **Node.js (Server)** — Express/Fastify, TypeScript, Prisma
- **Python** — FastAPI/Flask, typed Python, pytest
- **Go (Server)** — Chi/Gin, structured logging, sqlx

## Preference Levels

| Level             | What it includes                                  |
| ----------------- | ------------------------------------------------- |
| Simple            | Clean code basics, modular structure              |
| Intermediate      | Patterns, testing, conventions, data layer        |
| Industry Standard | Full architecture, CI/CD, security, observability |

## Smart Features

- **Auto-detection**: Scans `package.json`, `Cargo.toml`, `pubspec.yaml`, `pyproject.toml`, `go.mod` to identify your stack
- **Context injection**: Appends detected project name, frameworks, and package manager to the generated file
- **Correct conventions**: Uses each platform's real config file path — not a generic filename
- **Safe writes**: Always asks before overwriting existing files

## CLI Options

```bash
msl              # Run the interactive wizard
msl --version    # Show version
msl --help       # Show help
```

## Development

```bash
git clone https://github.com/murad/msl.git
cd msl
pip install -e .
msl
```

## License

MIT

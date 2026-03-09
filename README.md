# MSL — Muradian Skill Languages

Generate platform-specific skill/rule files for AI coding assistants with one command. No need to remember which file goes where — `msl` handles the structure for you.

## Install

`msl` is a CLI tool intended to be installed for global use.

Optional if `pipx` is already installed on your machine:

```bash
pipx install msl
```

Install from PyPI for user-global use:

macOS/Linux:

```bash
python3 -m pip install --user msl
```

Cross-platform when `python` points to Python 3:

```bash
python -m pip install --user msl
```

Windows:

```bash
py -m pip install --user msl
```

Install from a local checkout for user-global use:

macOS/Linux:

```bash
python3 -m pip install --user --upgrade setuptools wheel
python3 -m pip install --user --no-build-isolation .
```

Cross-platform when `python` points to Python 3:

```bash
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --no-build-isolation .
```

Windows:

```bash
py -m pip install --user --upgrade setuptools wheel
py -m pip install --user --no-build-isolation .
```

If `msl` installs successfully but the command is not found, make sure your Python user scripts directory is on `PATH`.

Linux example:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

macOS example with system Python 3.9:

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
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

You can also use `msl` non-interactively in scripts and CI:

```bash
msl --platform vscode --project-type python --preference intermediate --project-path .
msl --platform cursor --project-type nextjs --preference industry_standard --stdout
msl --perfect --project-path .
msl --gph
msl --gbs
```

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
- **Scriptable CLI**: Generate files directly from shell scripts, CI jobs, or editor tasks with flags
- **Stdout mode**: Preview or pipe generated output without writing a file
- **Force overwrite**: Replace an existing generated file without interactive prompts when running automation
- **Perfect scripts mode**: Add a practical test/format/build script pack to `package.json` for web projects
- **Fast git push helper**: Prompt for a commit message and immediately add, commit, and push with `--gph`
- **Fast branch helper**: Prompt for a branch name and immediately create and switch with `--gbs`

## CLI Options

```bash
msl              # Run the interactive wizard
msl --version    # Show version
msl --help       # Show help
msl --list-options
msl --platform vscode --project-type python --preference simple --project-path .
msl --platform cursor --project-type nextjs --preference industry_standard --stdout
msl --perfect --project-path .
msl --gph
msl --gbs
```

`msl --perfect` inspects your existing `package.json` and adds sensible scripts like `test`, `test:watch`, `format`, `format:check`, `postbuild`, `prepare`, and a composed `fulltest` command when the required tools are already present.

`msl --gph` is the simpler git helper flow: it asks only for the git commit message, then runs `git add .`, `git commit`, and `git push` immediately.

`msl --gbs` asks for a new branch name, then runs `git checkout -b <branch>` so the branch is created from the current branch and switched immediately.

## Development

```bash
git clone https://github.com/murad/msl.git
cd msl
python3 -m pip install -e .
msl
```

## Publish

Build the package first:

```bash
python3 -m build
```

Create a local `.pypi-token` file in the project root with your PyPI API token. This file is ignored by Git.

Then upload with:

```bash
./scripts/upload_pypi.sh
```

## License

MIT

## বাংলা

`msl` একটি CLI টুল, যা AI coding assistant-এর জন্য সঠিক skill বা rule file সঠিক জায়গায় তৈরি করে দেয়। আলাদা প্ল্যাটফর্মে কোন ফাইল কোথায় যাবে তা মনে রাখার দরকার নেই।

### ইনস্টল

`pipx` যদি আগে থেকেই install করা থাকে, optional option:

```bash
pipx install msl
```

PyPI থেকে user-global install:

macOS/Linux:

```bash
python3 -m pip install --user msl
```

`python` যদি Python 3-এ point করে:

```bash
python -m pip install --user msl
```

Windows:

```bash
py -m pip install --user msl
```

লোকাল source code থেকে user-global install:

macOS/Linux:

```bash
python3 -m pip install --user --upgrade setuptools wheel
python3 -m pip install --user --no-build-isolation .
```

`python` যদি Python 3-এ point করে:

```bash
python -m pip install --user --upgrade setuptools wheel
python -m pip install --user --no-build-isolation .
```

Windows:

```bash
py -m pip install --user --upgrade setuptools wheel
py -m pip install --user --no-build-isolation .
```

যদি install সফল হয় কিন্তু `msl` command না পাওয়া যায়, তাহলে Python user scripts path `PATH`-এ যোগ করুন।

Linux example:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

macOS with system Python 3.9:

```bash
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
source ~/.zshrc
```

### ব্যবহার

```bash
msl
```

এই wizard যা করবে:

1. আপনার environment detect করবে, যেমন Node.js, Cursor, VS Code, Claude Code, Codex
2. project scan করে framework, language এবং package manager চিনবে
3. কোন platform-এর জন্য file generate করবেন তা জিজ্ঞেস করবে
4. project path নেবে, current directory অথবা custom path
5. project type suggest করবে
6. preference level নিতে বলবে, যেমন Simple, Intermediate, Industry Standard
7. শেষে সঠিক path-এ সঠিক file generate করবে
8. চাইলে `--perfect` দিয়ে `package.json` scripts update করতে পারবে
9. চাইলে `--gph` দিয়ে শুধু commit message দিয়ে সরাসরি push flow চালাতে পারবে
10. চাইলে `--gbs` দিয়ে নতুন branch create করে সঙ্গে সঙ্গে switch করতে পারবে

### Supported Platforms

- Cursor: `.cursor/rules.md`
- VS Code: `.github/copilot-instructions.md`
- Claude Code: `CLAUDE.md`
- Codex: `AGENTS.md`

### Supported Project Types

- Flutter
- Web (Next.js)
- Web (React/Vite)
- Rust (Server)
- Node.js (Server)
- Python
- Go (Server)

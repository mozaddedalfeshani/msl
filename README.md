# 🚀 MSL — Muradian Skill Languages

[![PyPI version](https://img.shields.io/pypi/v/msl.svg)](https://pypi.org/project/msl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**MSL** is a powerful CLI tool that generates platform-specific skill and rule files for AI coding assistants (Cursor, VS Code, Claude Code, etc.) with a single command. It features **MSL AI integration** to create perfectly tailored, project-aware instructions in seconds, plus comprehensive git utilities.

## 🎯 Why MSL?

- **🚀 One-Command Setup**: Generate AI-optimized skill files instantly
- **🧠 Smart Context Analysis**: Reads your project to create tailored instructions
- **🔧 Complete Git Suite**: Branch management, commit operations, and remote handling
- **🛡️ Safety First**: Interactive confirmations and change previews
- **📦 Zero Configuration**: Works out of the box with no API keys needed

---

Install globally in macos
`pip3 install --user --break-system-packages --upgrade msl`

## ✨ Key Features

- **🤖 AI-Powered Generation (`--ai`)**: Connects to MSL API to analyze your project (README, `package.json`, etc.) and write custom rules.
- **⚡ Smart Push (`--gph`)**: One-command git workflow. Stages files, uses AI to write a perfect commit message, and pushes with built-in retry logic.
- **🔧 Git Utilities**: Complete git management suite including branch creation, commit removal, and remote management.
- **🔍 Intelligent Scanning**: Automatically detects frameworks (Next.js, Flutter, Fastify, etc.) and project types.
- **🛠️ Platform Support**: Generates the correct files for **Cursor** (`.cursor/rules.md`), **VS Code** (`.github/copilot-instructions.md`), **Claude Code** (`CLAUDE.md`), and **Codex** (`AGENTS.md`).
- **📦 Zero-Config Setup**: Works instantly with Node.js, Python, Rust, Go, and Flutter projects.

---

## 🚀 Installation

Install `msl` globally using `pip`:

```bash
# macOS / Linux
python3 -m pip install --user msl

# Windows
py -m pip install --user msl
```

_Recommended: Use [pipx](https://pypa.github.io/pipx/) for a clean, isolated installation:_

```bash
pipx install msl
```

---

## 🕹️ Quick Start

### 1. Interactive Wizard

Run the wizard to scan your project and generate rules step-by-step:

```bash
msl
```

### 2. AI-Enhanced Generation

Generate a tailor-made skill file using MSL AI by reading your project's context:

```bash
msl --ai --platform cursor --project-path .
```

### 3. Smart Git Push

Stage, commit (with AI-generated messages), and push in one go:

```bash
msl --gph
```

### 4. Git Utilities

Complete git management suite with safety features:

```bash
# Create and switch to new branch
msl --gbs

# Reset last N commits (interactive mode selection)
msl --gsr 3

# Show remote URLs
msl --gru

# Set/update remote URL
msl --grs https://github.com/user/repo.git
```

**Safety Features:**

- Interactive confirmation for destructive operations
- Uncommitted changes detection
- Commit preview before removal
- Multiple reset modes (soft/mixed/hard)

---

## 🧠 Using MSL AI

The `--ai` flag uses the MSL API directly - no API keys required! The AI analyzes your project files and generates tailored instructions automatically.

> **Note**: MSL AI works out of the box with no configuration needed. Just run `msl --ai` and get instant, project-aware results.

---

## � Publishing to PyPI

For maintainers releasing a new version, ensure your `.pypirc` or token file is configured, then run:

```bash
rm -rf dist/* && \
python3 -m build && \
twine upload --verbose --username __token__ --password "$(cat .pypi-token)" dist/* --non-interactive
```

This cleans previous artifacts, builds both wheel and source distributions, and uploads them with a PyPI token stored in `.pypi-token`.

---

## 🛠️ Complete Command Reference

| Flag         | Description                                                   |
| :----------- | :------------------------------------------------------------ |
| `--ai`       | Generate a project-tailored skill file using MSL AI.          |
| `--gph`      | Smart Git Push: Add, AI-commit, and Push with retry.          |
| `--gbs`      | Create and switch to a new branch.                            |
| `--gsr N`    | Git reset last N commits (prompts for reset mode).            |
| `--gru`      | Show configured git remote URLs.                              |
| `--grs URL`  | Set or update git remote URL.                                 |
| `--platform` | Target platform (`cursor`, `vscode`, `claude-code`, `codex`). |
| `--stdout`   | Print the generated content instead of writing to a file.     |
| `--perfect`  | Optimize `package.json` with industry-standard scripts.       |
| `--force`    | Overwrite existing files without confirmation.                |

---

## 🌍 Supported Stacks

- **Web**: Next.js (App/Pages), React/Vite
- **Backend**: Node.js (Express, Fastify, Hono), Python (FastAPI, Django, Flask), Go, Rust (Axum, Actix)
- **Mobile**: Flutter

---

## � Quick Install & Use

```bash
# Install
pip install msl

# Generate AI skill file for your project
msl --ai --platform cursor

# Smart git push with AI commit message
msl --gph

# Interactive wizard (recommended for first time)
msl
```

**Perfect for:**

- Developers using AI coding assistants
- Teams wanting consistent coding standards
- Projects needing quick AI assistant setup
- Git workflow automation

---

## �📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 🇧🇩 বাংলা (Bengali Quick-Start)

`msl` একটি CLI টুল যা আপনার প্রজেক্টের জন্য সঠিক AI Skill বা Rule ফাইল তৈরি করে দেয়। এখন এতে আছে DeepSeek AI পাওয়ার, যা আপনার প্রজেক্টের কোড বুঝে অটোমেটিক নিয়ম লিখে দেবে।

**ইন্সটল:**

```bash
pipx install msl
```

**ব্যবহার:**

- উইজার্ড চালাতে: `msl`
- এআই দিয়ে জেনারেট করতে: `msl --ai --platform cursor`
- অটোমেটিক গিট পুশ: `msl --gph`
- নতুন ব্রাঞ্চ তৈরি: `msl --gbs`
- কমিট রিসেট: `msl --gsr 3`
- রিমোট URL দেখুন: `msl --gru`
- রিমোট URL সেট করুন: `msl --grs https://github.com/user/repo.git`
  . project path নেবে, current directory অথবা custom path

5. project type suggest করবে
6. preference level নিতে বলবে, যেমন Simple, Intermediate, Industry Standard
7. শেষে সঠিক path-এ সঠিক file generate করবে
8. চাইলে `--perfect` দিয়ে `package.json` scripts update করতে পারবে

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

# 🚀 MSL — Muradian Skill Languages

[![PyPI version](https://img.shields.io/pypi/v/msl.svg)](https://pypi.org/project/msl/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**MSL** is a powerful CLI tool that generates platform-specific skill and rule files for AI coding assistants (Cursor, VS Code, Claude Code, etc.) with a single command. It now features **DeepSeek AI integration** to create perfectly tailored, project-aware instructions in seconds.

---

Install globally in macos
`pip3 install --user --break-system-packages --upgrade msl`

## ✨ Key Features

- **🤖 AI-Powered Generation (`--ai`)**: Connects to DeepSeek to analyze your project (README, `package.json`, etc.) and write custom rules.
- **⚡ Smart Push (`--gph`)**: One-command git workflow. Stages files, uses AI to write a perfect commit message, and pushes with built-in retry logic.
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

Generate a tailor-made skill file using DeepSeek AI by reading your project's context:

```bash
msl --ai --platform cursor --project-path .
```

### 3. Smart Git Push

Stage, commit (with AI-generated messages), and push in one go:

```bash
msl --gph
```

---

## 🧠 Using DeepSeek AI

To use the `--ai` flag, you need a DeepSeek API key. MSL looks for it in three places:

1. **Environment Variable**: `export DEEPSEEK_API=sk-your-key`
2. **.env File**: Add `DEEPSEEK_API=sk-your-key` to your project root.
3. **CLI Flag**: `msl --ai --ai-key sk-your-key ...`

> [!IMPORTANT]
> **Security First**: Your API key is **never** bundled or shared. It remains local to your environment and is only used to call the DeepSeek API from your machine.

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

## �🛠️ CLI Options

| Flag         | Description                                                   |
| :----------- | :------------------------------------------------------------ |
| `--ai`       | Generate a project-tailored skill file using DeepSeek AI.     |
| `--gph`      | Smart Git Push: Add, AI-commit, and Push with retry.          |
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

## 📄 License

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

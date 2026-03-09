"""Scan a project directory and auto-detect its type, frameworks, and structure."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .models import ProjectType


@dataclass
class ProjectScan:
    """Rich context gathered from scanning an actual project directory."""

    detected_type: Optional[ProjectType] = None
    confidence: float = 0.0  # 0.0–1.0

    # Package / dependency info
    name: str = ""
    description: str = ""
    package_manager: str = ""  # npm, yarn, pnpm, pip, cargo, pub
    frameworks: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    # Structure
    has_tests: bool = False
    has_ci: bool = False
    has_docker: bool = False
    has_monorepo: bool = False
    src_dirs: list[str] = field(default_factory=list)
    entry_files: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        parts = []
        if self.name:
            parts.append(f"Project: {self.name}")
        if self.frameworks:
            parts.append(f"Frameworks: {', '.join(self.frameworks)}")
        if self.languages:
            parts.append(f"Languages: {', '.join(self.languages)}")
        if self.package_manager:
            parts.append(f"Package Manager: {self.package_manager}")
        if self.has_tests:
            parts.append("Has tests ✓")
        if self.has_ci:
            parts.append("Has CI ✓")
        return " │ ".join(parts) if parts else "No project metadata found"


def scan_project(project_path: Path) -> ProjectScan:
    """Scan a project directory and return rich context about it."""
    scan = ProjectScan()

    _scan_flutter(project_path, scan)
    _scan_node(project_path, scan)
    _scan_rust(project_path, scan)
    _scan_python(project_path, scan)
    _scan_go(project_path, scan)
    _scan_structure(project_path, scan)

    return scan


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ── Flutter ──────────────────────────────────────────────────────


def _scan_flutter(root: Path, scan: ProjectScan) -> None:
    pubspec = root / "pubspec.yaml"
    if not pubspec.exists():
        return

    scan.languages.append("Dart")
    scan.package_manager = "pub"

    try:
        text = pubspec.read_text(encoding="utf-8")
    except OSError:
        text = ""

    if "flutter:" in text:
        scan.detected_type = ProjectType.FLUTTER
        scan.confidence = 0.95
        scan.frameworks.append("Flutter")
    else:
        scan.frameworks.append("Dart")
        scan.detected_type = ProjectType.FLUTTER
        scan.confidence = 0.7

    # Extract name
    for line in text.splitlines():
        if line.startswith("name:"):
            scan.name = line.split(":", 1)[1].strip()
            break
        if line.startswith("description:"):
            scan.description = line.split(":", 1)[1].strip().strip("'\"")

    if (root / "test").is_dir():
        scan.has_tests = True


# ── Node / JS / TS ──────────────────────────────────────────────


def _scan_node(root: Path, scan: ProjectScan) -> None:
    pkg_path = root / "package.json"
    if not pkg_path.exists():
        return

    pkg = _read_json(pkg_path)
    if not pkg:
        return

    scan.name = scan.name or pkg.get("name", "")
    scan.description = scan.description or pkg.get("description", "")

    # Package manager detection
    if (root / "pnpm-lock.yaml").exists():
        scan.package_manager = "pnpm"
    elif (root / "yarn.lock").exists():
        scan.package_manager = "yarn"
    elif (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        scan.package_manager = "bun"
    else:
        scan.package_manager = "npm"

    all_deps = {
        **pkg.get("dependencies", {}),
        **pkg.get("devDependencies", {}),
    }
    dep_names = list(all_deps.keys())
    scan.dependencies = dep_names[:30]  # keep it focused

    # Language
    if "typescript" in all_deps or (root / "tsconfig.json").exists():
        scan.languages.append("TypeScript")
    else:
        scan.languages.append("JavaScript")

    # Framework detection with confidence
    if "next" in all_deps:
        scan.frameworks.append("Next.js")
        if scan.detected_type is None or scan.confidence < 0.9:
            # Check if it uses App Router
            if (root / "app").is_dir():
                scan.frameworks.append("App Router")
            elif (root / "src" / "app").is_dir():
                scan.frameworks.append("App Router")
            elif (root / "pages").is_dir():
                scan.frameworks.append("Pages Router")
            scan.detected_type = ProjectType.NEXTJS
            scan.confidence = 0.95

    elif "react" in all_deps and "vite" in all_deps:
        scan.frameworks.append("React")
        scan.frameworks.append("Vite")
        scan.detected_type = ProjectType.REACT_VITE
        scan.confidence = 0.95

    elif "react" in all_deps:
        scan.frameworks.append("React")
        if scan.detected_type is None:
            scan.detected_type = ProjectType.REACT_VITE
            scan.confidence = 0.8

    elif "express" in all_deps or "fastify" in all_deps or "hono" in all_deps or "koa" in all_deps:
        for fw in ["express", "fastify", "hono", "koa"]:
            if fw in all_deps:
                scan.frameworks.append(fw.capitalize())
        if scan.detected_type is None:
            scan.detected_type = ProjectType.NODEJS_SERVER
            scan.confidence = 0.9

    elif not scan.detected_type:
        # Generic Node.js project — check if it looks server-like
        if pkg.get("main") or pkg.get("bin"):
            scan.detected_type = ProjectType.NODEJS_SERVER
            scan.confidence = 0.5

    # Popular libraries detection
    for lib in ["tailwindcss", "prisma", "drizzle-orm", "@trpc/server", "zod",
                "react-query", "@tanstack/react-query", "zustand", "redux",
                "mongoose", "socket.io", "graphql", "jest", "vitest",
                "playwright", "cypress", "eslint", "prettier", "storybook"]:
        if lib in all_deps and lib not in scan.frameworks:
            scan.frameworks.append(lib)

    if (root / "__tests__").is_dir() or (root / "tests").is_dir() or (root / "test").is_dir():
        scan.has_tests = True
    if any(d in all_deps for d in ["jest", "vitest", "mocha"]):
        scan.has_tests = True


# ── Rust ─────────────────────────────────────────────────────────


def _scan_rust(root: Path, scan: ProjectScan) -> None:
    cargo = root / "Cargo.toml"
    if not cargo.exists():
        return

    scan.languages.append("Rust")
    scan.package_manager = "cargo"

    try:
        text = cargo.read_text(encoding="utf-8")
    except OSError:
        text = ""

    # Extract name
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("name") and "=" in stripped:
            scan.name = stripped.split("=", 1)[1].strip().strip('"\'')
            break

    # Framework detection
    text_lower = text.lower()
    if "axum" in text_lower:
        scan.frameworks.append("Axum")
    if "actix-web" in text_lower:
        scan.frameworks.append("Actix-web")
    if "rocket" in text_lower:
        scan.frameworks.append("Rocket")
    if "tokio" in text_lower:
        scan.frameworks.append("Tokio")
    if "sqlx" in text_lower:
        scan.frameworks.append("sqlx")
    if "diesel" in text_lower:
        scan.frameworks.append("Diesel")
    if "serde" in text_lower:
        scan.frameworks.append("serde")

    if scan.detected_type is None:
        scan.detected_type = ProjectType.RUST_SERVER
        scan.confidence = 0.85

    if (root / "tests").is_dir():
        scan.has_tests = True


# ── Python ───────────────────────────────────────────────────────


def _scan_python(root: Path, scan: ProjectScan) -> None:
    has_pyproject = (root / "pyproject.toml").exists()
    has_setup = (root / "setup.py").exists() or (root / "setup.cfg").exists()
    has_requirements = (root / "requirements.txt").exists()

    if not (has_pyproject or has_setup or has_requirements):
        return

    scan.languages.append("Python")

    if (root / "Pipfile").exists():
        scan.package_manager = "pipenv"
    elif (root / "poetry.lock").exists():
        scan.package_manager = "poetry"
    elif (root / "uv.lock").exists():
        scan.package_manager = "uv"
    else:
        scan.package_manager = "pip"

    # Read pyproject.toml for metadata
    if has_pyproject:
        try:
            text = (root / "pyproject.toml").read_text(encoding="utf-8")
        except OSError:
            text = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("name") and "=" in stripped:
                scan.name = stripped.split("=", 1)[1].strip().strip('"\'')
                break

        text_lower = text.lower()
        for fw in ["django", "flask", "fastapi", "starlette", "tornado", "sanic"]:
            if fw in text_lower:
                scan.frameworks.append(fw.capitalize())
        if "pytest" in text_lower:
            scan.has_tests = True

    # Read requirements.txt
    if has_requirements:
        try:
            reqs = (root / "requirements.txt").read_text(encoding="utf-8")
        except OSError:
            reqs = ""
        reqs_lower = reqs.lower()
        for fw in ["django", "flask", "fastapi", "starlette"]:
            if fw in reqs_lower and fw.capitalize() not in scan.frameworks:
                scan.frameworks.append(fw.capitalize())

    if scan.detected_type is None:
        scan.detected_type = ProjectType.PYTHON
        scan.confidence = 0.7

    if (root / "tests").is_dir() or (root / "test").is_dir():
        scan.has_tests = True


# ── Go ───────────────────────────────────────────────────────────


def _scan_go(root: Path, scan: ProjectScan) -> None:
    go_mod = root / "go.mod"
    if not go_mod.exists():
        return

    scan.languages.append("Go")
    scan.package_manager = "go mod"

    try:
        text = go_mod.read_text(encoding="utf-8")
    except OSError:
        text = ""

    # Extract module name
    for line in text.splitlines():
        if line.startswith("module "):
            scan.name = line.split("module ", 1)[1].strip()
            break

    text_lower = text.lower()
    if "gin-gonic" in text_lower:
        scan.frameworks.append("Gin")
    if "go-chi" in text_lower or "chi" in text_lower:
        scan.frameworks.append("Chi")
    if "fiber" in text_lower:
        scan.frameworks.append("Fiber")
    if "echo" in text_lower:
        scan.frameworks.append("Echo")

    if scan.detected_type is None:
        scan.detected_type = ProjectType.GO_SERVER
        scan.confidence = 0.8


# ── Common structure ─────────────────────────────────────────────


def _scan_structure(root: Path, scan: ProjectScan) -> None:
    if (root / ".github" / "workflows").is_dir() or (root / ".gitlab-ci.yml").exists():
        scan.has_ci = True
    if (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        scan.has_docker = True

    # Monorepo indicators
    if (root / "pnpm-workspace.yaml").exists() or (root / "lerna.json").exists():
        scan.has_monorepo = True
    pkg = root / "package.json"
    if pkg.exists():
        data = _read_json(pkg)
        if "workspaces" in data:
            scan.has_monorepo = True

    # Source directories
    for d in ["src", "lib", "app", "pages", "components", "cmd", "internal", "pkg"]:
        if (root / d).is_dir():
            scan.src_dirs.append(d)

    # Entry files
    for f in ["main.ts", "main.py", "main.go", "main.rs", "index.ts",
              "index.js", "server.ts", "server.js", "app.ts", "app.py"]:
        if (root / f).exists() or (root / "src" / f).exists():
            scan.entry_files.append(f)

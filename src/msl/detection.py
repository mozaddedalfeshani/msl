from __future__ import annotations

import platform as platform_mod
import shutil
import subprocess
from pathlib import Path

from .models import DetectedTool


def _run_version_cmd(cmd: str) -> str | None:
    try:
        result = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return (result.stdout.strip() or result.stderr.strip()) or None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _check_macos_app(app_name: str) -> bool:
    return Path(f"/Applications/{app_name}.app").exists()


def detect_nodejs() -> DetectedTool:
    version = _run_version_cmd("node")
    return DetectedTool(
        name="Node.js",
        installed=version is not None,
        version=version,
        path=shutil.which("node"),
    )


def detect_cursor() -> DetectedTool:
    cursor_path = shutil.which("cursor")
    if cursor_path:
        version = _run_version_cmd("cursor")
        return DetectedTool(
            name="Cursor", installed=True, version=version, path=cursor_path
        )
    if platform_mod.system() == "Darwin" and _check_macos_app("Cursor"):
        return DetectedTool(
            name="Cursor", installed=True, path="/Applications/Cursor.app"
        )
    return DetectedTool(name="Cursor", installed=False)


def detect_vscode() -> DetectedTool:
    code_path = shutil.which("code")
    if code_path:
        version = _run_version_cmd("code")
        return DetectedTool(
            name="VS Code", installed=True, version=version, path=code_path
        )
    if platform_mod.system() == "Darwin" and _check_macos_app("Visual Studio Code"):
        return DetectedTool(
            name="VS Code",
            installed=True,
            path="/Applications/Visual Studio Code.app",
        )
    return DetectedTool(name="VS Code", installed=False)


def detect_claude_code() -> DetectedTool:
    claude_path = shutil.which("claude")
    if claude_path:
        version = _run_version_cmd("claude")
        return DetectedTool(
            name="Claude Code", installed=True, version=version, path=claude_path
        )
    return DetectedTool(name="Claude Code", installed=False)


def detect_codex() -> DetectedTool:
    codex_path = shutil.which("codex")
    if codex_path:
        version = _run_version_cmd("codex")
        return DetectedTool(
            name="Codex", installed=True, version=version, path=codex_path
        )
    return DetectedTool(name="Codex", installed=False)


def detect_all() -> dict[str, DetectedTool]:
    return {
        "nodejs": detect_nodejs(),
        "cursor": detect_cursor(),
        "vscode": detect_vscode(),
        "claude-code": detect_claude_code(),
        "codex": detect_codex(),
    }

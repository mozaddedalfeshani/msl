from __future__ import annotations

import os
import platform as platform_mod
import shutil
import subprocess
import socket
from pathlib import Path


def get_device_info() -> str:
    """Return a string identifying the current device."""
    try:
        hostname = socket.gethostname()
        system = platform_mod.system()
        machine = platform_mod.machine()
        return f"{hostname} ({system} {machine})"
    except Exception:
        return "Unknown Device"


from .models import DetectedTool


def _run_git_toplevel(cwd: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).resolve()
    except Exception:
        pass
    return None


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


def detect_windsurf() -> DetectedTool:
    windsurf_path = shutil.which("windsurf")
    if windsurf_path:
        version = _run_version_cmd("windsurf")
        return DetectedTool(
            name="Windsurf", installed=True, version=version, path=windsurf_path
        )
    if platform_mod.system() == "Darwin" and _check_macos_app("Windsurf"):
        return DetectedTool(
            name="Windsurf", installed=True, path="/Applications/Windsurf.app"
        )
    return DetectedTool(name="Windsurf", installed=False)


def detect_antigravity() -> DetectedTool:
    # This is a specialized detection for the Antigravity IDE
    ag_path = shutil.which("antigravity")
    if ag_path:
        version = _run_version_cmd("antigravity")
        return DetectedTool(
            name="Antigravity", installed=True, version=version, path=ag_path
        )
    if os.environ.get("ANTIGRAVITY_IDE"):
        return DetectedTool(name="Antigravity", installed=True)
    return DetectedTool(name="Antigravity", installed=False)


def get_project_name(project_root: Path) -> str:
    """Return the name of the project based on the directory name."""
    return project_root.resolve().name


def detect_framework(project_root: Path) -> str:
    """Detect the framework being used in the project."""
    # Check package.json for web frameworks
    package_json = project_root / "package.json"
    if package_json.is_file():
        try:
            content = package_json.read_text()
            if "next" in content: return "Next.js"
            if "react-native" in content: return "React Native"
            if "react" in content: return "React"
            if "vue" in content: return "Vue"
            if "svelte" in content: return "Svelte"
            if "astro" in content: return "Astro"
            if "nuxt" in content: return "Nuxt"
        except Exception: pass

    # Check for Python frameworks
    if (project_root / "manage.py").is_file(): return "Django"
    
    requirements = project_root / "requirements.txt"
    if requirements.is_file():
        try:
            content = requirements.read_text()
            if "fastapi" in content.lower(): return "FastAPI"
            if "flask" in content.lower(): return "Flask"
        except Exception: pass

    # Check for others
    if (project_root / "Cargo.toml").is_file(): return "Rust"
    if (project_root / "go.mod").is_file(): return "Go"
    
    return "Unknown"


def detect_ide() -> str:
    """Detect the IDE being used based on environment variables."""
    term_program = os.environ.get("TERM_PROGRAM", "")
    if "vscode" in term_program.lower() or os.environ.get("VSCODE_GIT_IPC_HANDLE"):
        return "VS Code"
    if os.environ.get("TERMINAL_EMULATOR") == "JetBrains-JediTerm":
        return "JetBrains"
    if "cursor" in term_program.lower():
        return "Cursor"
    if "windsurf" in term_program.lower():
        return "Windsurf"
    if "antigravity" in term_program.lower() or os.environ.get("ANTIGRAVITY_IDE"):
        return "Antigravity"
    if "apple_terminal" in term_program.lower():
        return "Apple Terminal"
    if "iterm" in term_program.lower():
        return "iTerm2"
    return "Terminal"


def detect_all(project_root: Path | str | None = None) -> dict[str, any]:
    if project_root:
        if isinstance(project_root, str):
            project_root = Path(project_root)
        # Try to find git root first for better framework detection
        git_root = _run_git_toplevel(project_root)
        if git_root:
            project_root = git_root

    results = {
        "nodejs": detect_nodejs(),
        "cursor": detect_cursor(),
        "vscode": detect_vscode(),
        "claude-code": detect_claude_code(),
        "codex": detect_codex(),
        "windsurf": detect_windsurf(),
        "antigravity": detect_antigravity(),
        "ide": detect_ide(),
    }
    
    if project_root:
        results["project_name"] = get_project_name(project_root)
        results["framework"] = detect_framework(project_root)
        
    return results

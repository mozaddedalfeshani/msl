from __future__ import annotations

from pathlib import Path

from .models import Platform

# Platform → (hidden directory name | None, filename)
# Based on each tool's ACTUAL config-file convention.
PLATFORM_PATHS: dict[str, tuple[str | None, str]] = {
    Platform.CURSOR.value: (".cursor", "rules.md"),          # .cursor/rules.md
    Platform.VSCODE.value: (".github", "copilot-instructions.md"),  # .github/copilot-instructions.md
    Platform.CLAUDE_CODE.value: (None, "CLAUDE.md"),         # CLAUDE.md at project root
    Platform.CODEX.value: (None, "AGENTS.md"),               # AGENTS.md at project root
}


def get_output_path(platform: Platform, project_root: Path) -> Path:
    directory, filename = PLATFORM_PATHS[platform.value]
    if directory:
        return project_root / directory / filename
    return project_root / filename


def get_output_dir(platform: Platform, project_root: Path) -> Path:
    directory, _ = PLATFORM_PATHS[platform.value]
    if directory:
        return project_root / directory
    return project_root

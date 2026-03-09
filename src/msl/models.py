from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Platform(Enum):
    CURSOR = "cursor"
    VSCODE = "vscode"
    CLAUDE_CODE = "claude-code"
    CODEX = "codex"

    @property
    def display_name(self) -> str:
        return {
            Platform.CURSOR: "Cursor",
            Platform.VSCODE: "VS Code",
            Platform.CLAUDE_CODE: "Claude Code",
            Platform.CODEX: "Codex",
        }[self]


class ProjectType(Enum):
    FLUTTER = "flutter"
    NEXTJS = "nextjs"
    REACT_VITE = "react-vite"
    RUST_SERVER = "rust-server"
    NODEJS_SERVER = "nodejs-server"
    PYTHON = "python"
    GO_SERVER = "go-server"

    @property
    def display_name(self) -> str:
        return {
            ProjectType.FLUTTER: "Flutter",
            ProjectType.NEXTJS: "Web (Next.js)",
            ProjectType.REACT_VITE: "Web (React/Vite)",
            ProjectType.RUST_SERVER: "Rust (Server)",
            ProjectType.NODEJS_SERVER: "Node.js (Server)",
            ProjectType.PYTHON: "Python",
            ProjectType.GO_SERVER: "Go (Server)",
        }[self]


class PreferenceTier(Enum):
    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    INDUSTRY_STANDARD = "industry_standard"

    @property
    def display_name(self) -> str:
        return {
            PreferenceTier.SIMPLE: "Simple — modular, clean code basics",
            PreferenceTier.INTERMEDIATE: "Intermediate — patterns, testing, conventions",
            PreferenceTier.INDUSTRY_STANDARD: "Industry Standard — full architecture & delivery rules",
        }[self]


@dataclass
class DetectedTool:
    name: str
    installed: bool
    version: str | None = None
    path: str | None = None


@dataclass
class SkillGenContext:
    target_platform: Platform
    project_path: Path
    project_type: ProjectType
    preference_tier: PreferenceTier
    detected_tools: dict[str, DetectedTool] = field(default_factory=dict)

    @property
    def output_path(self) -> Path:
        from .path_rules import get_output_path

        return get_output_path(self.target_platform, self.project_path)

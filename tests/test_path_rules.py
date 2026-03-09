from pathlib import Path

from msl.models import Platform
from msl.path_rules import get_output_dir, get_output_path


def test_cursor_output_path():
    root = Path("/tmp/myproject")
    assert get_output_path(Platform.CURSOR, root) == root / ".cursor" / "rules.md"


def test_vscode_output_path():
    root = Path("/tmp/myproject")
    assert get_output_path(Platform.VSCODE, root) == root / ".github" / "copilot-instructions.md"


def test_claude_code_output_path():
    root = Path("/tmp/myproject")
    assert get_output_path(Platform.CLAUDE_CODE, root) == root / "CLAUDE.md"


def test_codex_output_path():
    root = Path("/tmp/myproject")
    assert get_output_path(Platform.CODEX, root) == root / "AGENTS.md"


def test_output_dir():
    root = Path("/tmp/myproject")
    assert get_output_dir(Platform.CURSOR, root) == root / ".cursor"
    assert get_output_dir(Platform.VSCODE, root) == root / ".github"
    assert get_output_dir(Platform.CLAUDE_CODE, root) == root
    assert get_output_dir(Platform.CODEX, root) == root

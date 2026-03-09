from unittest.mock import patch

from msl.detection import (
    detect_all,
    detect_claude_code,
    detect_codex,
    detect_cursor,
    detect_nodejs,
    detect_vscode,
)


def test_detect_nodejs_found():
    with patch("msl.detection.shutil.which", return_value="/usr/local/bin/node"), patch(
        "msl.detection._run_version_cmd", return_value="v20.11.0"
    ):
        result = detect_nodejs()
        assert result.installed is True
        assert result.version == "v20.11.0"
        assert result.name == "Node.js"


def test_detect_nodejs_not_found():
    with patch("msl.detection.shutil.which", return_value=None), patch(
        "msl.detection._run_version_cmd", return_value=None
    ):
        result = detect_nodejs()
        assert result.installed is False
        assert result.version is None


def test_detect_cursor_via_which():
    with patch("msl.detection.shutil.which", return_value="/usr/local/bin/cursor"), patch(
        "msl.detection._run_version_cmd", return_value="0.45.0"
    ):
        result = detect_cursor()
        assert result.installed is True
        assert result.version == "0.45.0"


def test_detect_cursor_via_macos_app():
    with patch("msl.detection.shutil.which", return_value=None), patch(
        "msl.detection.platform_mod.system", return_value="Darwin"
    ), patch("msl.detection._check_macos_app", return_value=True):
        result = detect_cursor()
        assert result.installed is True


def test_detect_cursor_not_found():
    with patch("msl.detection.shutil.which", return_value=None), patch(
        "msl.detection.platform_mod.system", return_value="Darwin"
    ), patch("msl.detection._check_macos_app", return_value=False):
        result = detect_cursor()
        assert result.installed is False


def test_detect_vscode_via_which():
    with patch("msl.detection.shutil.which", return_value="/usr/local/bin/code"), patch(
        "msl.detection._run_version_cmd", return_value="1.89.1"
    ):
        result = detect_vscode()
        assert result.installed is True
        assert result.version == "1.89.1"


def test_detect_claude_code_found():
    with patch("msl.detection.shutil.which", return_value="/usr/local/bin/claude"), patch(
        "msl.detection._run_version_cmd", return_value="1.0.0"
    ):
        result = detect_claude_code()
        assert result.installed is True


def test_detect_claude_code_not_found():
    with patch("msl.detection.shutil.which", return_value=None):
        result = detect_claude_code()
        assert result.installed is False


def test_detect_codex_found():
    with patch("msl.detection.shutil.which", return_value="/usr/local/bin/codex"), patch(
        "msl.detection._run_version_cmd", return_value="0.1.0"
    ):
        result = detect_codex()
        assert result.installed is True


def test_detect_codex_not_found():
    with patch("msl.detection.shutil.which", return_value=None):
        result = detect_codex()
        assert result.installed is False


def test_detect_all_returns_all_keys():
    with patch("msl.detection.shutil.which", return_value=None), patch(
        "msl.detection._run_version_cmd", return_value=None
    ), patch("msl.detection.platform_mod.system", return_value="Linux"), patch(
        "msl.detection._check_macos_app", return_value=False
    ):
        results = detect_all()
        assert set(results.keys()) == {"nodejs", "cursor", "vscode", "claude-code", "codex"}

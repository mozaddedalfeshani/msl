from pathlib import Path
from unittest.mock import patch

from msl import cli


def test_cli_list_options(capsys):
    with patch("sys.argv", ["msl", "--list-options"]):
        cli.main()

    output = capsys.readouterr().out
    assert "Platforms:" in output
    assert "Preferences:" in output


def test_cli_stdout_mode(capsys, tmp_path: Path):
    with patch(
        "sys.argv",
        [
            "msl",
            "--platform",
            "vscode",
            "--project-type",
            "python",
            "--preference",
            "simple",
            "--project-path",
            str(tmp_path),
            "--stdout",
        ],
    ):
        cli.main()

    output = capsys.readouterr().out
    assert len(output.strip()) > 0
    assert not (tmp_path / ".github" / "copilot-instructions.md").exists()


def test_cli_perfect_mode(capsys, tmp_path: Path):
    (tmp_path / "package.json").write_text(
        '{"name":"demo","devDependencies":{"jest":"29","prettier":"3"},"scripts":{"lint:fix":"eslint . --fix","lint:strict":"eslint .","typecheck":"tsc --noEmit"}}',
        encoding="utf-8",
    )
    (tmp_path / "bun.lockb").write_text("", encoding="utf-8")

    with patch(
        "sys.argv",
        ["msl", "--perfect", "--project-path", str(tmp_path)],
    ):
        cli.main()

    output = capsys.readouterr().out
    assert "Updated scripts" in output


def test_cli_gph_mode(capsys, tmp_path: Path):
    with patch("msl.git_tools.stage_commit_and_push", return_value="main") as push_flow, patch(
        "sys.argv",
        ["msl", "--gph", "--project-path", str(tmp_path)],
    ):
        cli.main()

    output = capsys.readouterr().out
    assert "Changes pushed on branch main" in output
    push_flow.assert_called_once_with(tmp_path.resolve(), None, confirm=False)


def test_cli_gbs_mode(capsys, tmp_path: Path):
    with patch("msl.git_tools.create_and_switch_branch", return_value="feature/login") as branch_flow, patch(
        "sys.argv",
        ["msl", "--gbs", "--project-path", str(tmp_path)],
    ):
        cli.main()

    output = capsys.readouterr().out
    assert "Switched to new branch feature/login" in output
    branch_flow.assert_called_once_with(tmp_path.resolve())
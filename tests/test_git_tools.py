from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from msl.git_tools import create_and_switch_branch, stage_commit_and_push


def test_stage_commit_and_push_runs_git_flow(tmp_path: Path):
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, " M README.md\n", ""),
            ("rev-parse", "--abbrev-ref", "HEAD"): CompletedProcess(args, 0, "main\n", ""),
            ("add", "."): CompletedProcess(args, 0, "", ""),
            ("commit", "-m", "ship it"): CompletedProcess(args, 0, "", ""),
            ("push",): CompletedProcess(args, 0, "", ""),
        }
        return mapping[args]

    with patch("msl.git_tools._run_git", side_effect=fake_run), patch(
        "msl.git_tools.questionary.confirm"
    ) as confirm, patch("msl.git_tools.questionary.text") as text:
        confirm.return_value.ask.return_value = True
        text.return_value.ask.return_value = "ship it"

        branch = stage_commit_and_push(tmp_path)

    assert branch == "main"
    assert ("add", ".") in calls
    assert ("commit", "-m", "ship it") in calls
    assert ("push",) in calls


def test_stage_commit_and_push_requires_changes(tmp_path: Path):
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, "", ""),
        }
        return mapping[args]

    with patch("msl.git_tools._run_git", side_effect=fake_run):
        try:
            stage_commit_and_push(tmp_path, "ship it")
            assert False, "Expected RuntimeError"
        except RuntimeError as exc:
            assert "No git changes" in str(exc)


def test_stage_commit_and_push_without_confirmation(tmp_path: Path):
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, " M README.md\n", ""),
            ("rev-parse", "--abbrev-ref", "HEAD"): CompletedProcess(args, 0, "main\n", ""),
            ("add", "."): CompletedProcess(args, 0, "", ""),
            ("commit", "-m", "ship it"): CompletedProcess(args, 0, "", ""),
            ("push",): CompletedProcess(args, 0, "", ""),
        }
        return mapping[args]

    with patch("msl.git_tools._run_git", side_effect=fake_run), patch(
        "msl.git_tools.questionary.confirm"
    ) as confirm:
        branch = stage_commit_and_push(tmp_path, "ship it", confirm=False)

    assert branch == "main"
    confirm.assert_not_called()
    assert ("push",) in calls


def test_create_and_switch_branch(tmp_path: Path):
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("checkout", "-b", "feature/login"): CompletedProcess(args, 0, "", ""),
        }
        return mapping[args]

    with patch("msl.git_tools._run_git", side_effect=fake_run), patch(
        "msl.git_tools.questionary.text"
    ) as text:
        text.return_value.ask.return_value = "feature/login"
        branch = create_and_switch_branch(tmp_path)

    assert branch == "feature/login"
    assert ("checkout", "-b", "feature/login") in calls
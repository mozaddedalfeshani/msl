from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

import pytest

from msl.git_tools import create_and_switch_branch, stage_commit_and_push, smart_push


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

    # questionary is imported inside functions, patch at its source
    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("questionary.confirm") as confirm, \
         patch("questionary.text") as text:
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

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("questionary.confirm") as confirm:
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

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("questionary.text") as text:
        text.return_value.ask.return_value = "feature/login"
        branch = create_and_switch_branch(tmp_path)

    assert branch == "feature/login"
    assert ("checkout", "-b", "feature/login") in calls


def test_smart_push_success(tmp_path: Path):
    """Full happy-path: stage → AI commit → push succeeds."""
    calls: list[tuple[str, ...]] = []
    commit_msg = "feat(api): add smart push support"

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, " M git_tools.py\n", ""),
            ("rev-parse", "--abbrev-ref", "HEAD"): CompletedProcess(args, 0, "main\n", ""),
            ("diff", "--stat", "HEAD"): CompletedProcess(args, 0, "1 file changed\n", ""),
            ("diff", "HEAD"): CompletedProcess(args, 0, "+new line\n", ""),
            ("diff", "--cached", "--stat"): CompletedProcess(args, 0, "", ""),
            ("add", "."): CompletedProcess(args, 0, "", ""),
            ("commit", "-m", commit_msg): CompletedProcess(args, 0, "", ""),
            ("push", "origin", "main"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.generate_commit_message", return_value=commit_msg), \
         patch("msl.ai_generator.resolve_api_key", return_value="test-key"):
        smart_push(tmp_path, explicit_api_key="test-key")

    assert ("add", ".") in calls
    assert ("commit", "-m", commit_msg) in calls
    assert ("push", "origin", "main") in calls


def test_smart_push_retries_no_verify(tmp_path: Path):
    """Push fails → retries with --no-verify → succeeds."""
    commit_msg = "fix: retry push"

    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, " M x.py\n", ""),
            ("rev-parse", "--abbrev-ref", "HEAD"): CompletedProcess(args, 0, "dev\n", ""),
            ("diff", "--stat", "HEAD"): CompletedProcess(args, 0, "", ""),
            ("diff", "HEAD"): CompletedProcess(args, 0, "", ""),
            ("diff", "--cached", "--stat"): CompletedProcess(args, 0, "", ""),
            ("add", "."): CompletedProcess(args, 0, "", ""),
            ("commit", "-m", commit_msg): CompletedProcess(args, 0, "", ""),
            ("push", "origin", "dev"): CompletedProcess(args, 1, "", "rejected"),
            ("push", "origin", "dev", "--no-verify"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.generate_commit_message", return_value=commit_msg), \
         patch("msl.ai_generator.resolve_api_key", return_value="key"):
        # Should not raise even though first push failed
        smart_push(tmp_path, explicit_api_key="key")


def test_remove_last_commits_with_prompt(tmp_path: Path):
    """Test the simplified single command with mode selection."""
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, "", ""),  # No uncommitted changes
            ("rev-list", "--count", "HEAD"): CompletedProcess(args, 0, "5\n", ""),  # 5 commits total
            ("log", "--oneline", "-n2"): CompletedProcess(args, 0, "abc123 Latest commit\ndef456 Previous commit", ""),
            ("reset", "--mixed", "HEAD~2"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console, \
         patch("questionary.select") as mock_select, \
         patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "mixed"
        mock_confirm.return_value.ask.return_value = True
        
        remove_last_commits_with_prompt(tmp_path, 2)
        
        assert ("reset", "--mixed", "HEAD~2") in calls
        mock_console.print.assert_called()  # Should show warnings and success


def test_remove_last_commits_with_prompt_soft_reset(tmp_path: Path):
    """Test soft reset through the prompt interface."""
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, "", ""),
            ("rev-list", "--count", "HEAD"): CompletedProcess(args, 0, "3\n", ""),
            ("log", "--oneline", "-n1"): CompletedProcess(args, 0, "xyz789 Single commit", ""),
            ("reset", "--soft", "HEAD~1"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console, \
         patch("questionary.select") as mock_select, \
         patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "soft"
        mock_confirm.return_value.ask.return_value = True
        
        remove_last_commits_with_prompt(tmp_path, 1)
        
        assert ("reset", "--soft", "HEAD~1") in calls


def test_remove_last_commits_with_prompt_hard_reset(tmp_path: Path):
    """Test hard reset through the prompt interface."""
    calls: list[tuple[str, ...]] = []

    def fake_run(cwd: Path, *args: str):
        calls.append(args)
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("status", "--porcelain"): CompletedProcess(args, 0, "", ""),
            ("rev-list", "--count", "HEAD"): CompletedProcess(args, 0, "10\n", ""),
            ("log", "--oneline", "-n3"): CompletedProcess(args, 0, "aaa111\nbbb222\nccc333", ""),
            ("reset", "--hard", "HEAD~3"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console, \
         patch("questionary.select") as mock_select, \
         patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "hard"
        mock_confirm.return_value.ask.return_value = True
        
        remove_last_commits_with_prompt(tmp_path, 3)
        
        assert ("reset", "--hard", "HEAD~3") in calls


def test_remove_last_commits_with_prompt_validation_errors(tmp_path: Path):
    """Test various validation scenarios through the prompt interface."""
    with patch("msl.git_tools._run_git") as mock_run:
        # Test uncommitted changes error
        mock_run.return_value = CompletedProcess(["status", "--porcelain"], 0, " M file.py", "")
        try:
            remove_last_commits_with_prompt(tmp_path, 1)
            assert False, "Expected RuntimeError for uncommitted changes"
        except RuntimeError as e:
            assert "uncommitted changes" in str(e)
        
        # Test invalid count
        mock_run.return_value = CompletedProcess(["status", "--porcelain"], 0, "", "")
        try:
            remove_last_commits_with_prompt(tmp_path, 0)
            assert False, "Expected ValueError for zero count"
        except ValueError as e:
            assert "greater than 0" in str(e)
        
        # Test too many commits
        with patch("msl.git_tools.get_commit_count", return_value=2):
            try:
                remove_last_commits_with_prompt(tmp_path, 2)
                assert False, "Expected RuntimeError for too many commits"
            except RuntimeError as e:
                assert "At least 1 commit must remain" in str(e)


def test_remove_last_commits_with_prompt_user_cancellation(tmp_path: Path):
    """Test that operation can be cancelled by user at mode selection."""
    with patch("msl.git_tools._run_git", return_value=CompletedProcess(["status", "--porcelain"], 0, "", "")), \
         patch("questionary.select") as mock_select:
        mock_select.return_value.ask.return_value = None  # User cancels mode selection
        
        # Should not raise and should return early
        remove_last_commits_with_prompt(tmp_path, 1)
        
        # Verify reset was not called
        mock_select.assert_called_once()


def test_remove_last_commits_with_prompt_confirmation_cancellation(tmp_path: Path):
    """Test that operation can be cancelled at confirmation step."""
    with patch("msl.git_tools._run_git", return_value=CompletedProcess(["status", "--porcelain"], 0, "", "")), \
         patch("questionary.select") as mock_select, \
         patch("questionary.confirm") as mock_confirm:
        mock_select.return_value.ask.return_value = "mixed"  # User selects a mode
        mock_confirm.return_value.ask.return_value = False  # But cancels confirmation
        
        # Should not raise and should return early
        remove_last_commits_with_prompt(tmp_path, 1)
        
        # Verify both prompts were called
        mock_select.assert_called_once()
        mock_confirm.assert_called_once()


def test_show_remote_urls(tmp_path: Path):
    """Test showing remote URLs."""
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("remote", "-v"): CompletedProcess(args, 0, "origin\thttps://github.com/user/repo.git (fetch)\norigin\thttps://github.com/user/repo.git (push)", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console:
        show_remote_urls(tmp_path)
        
        # Should have printed the remote info
        mock_console.print.assert_called()
        # Check that origin was highlighted (green)
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("origin" in call and "green" in call for call in calls)


def test_show_remote_urls_no_remotes(tmp_path: Path):
    """Test showing remotes when none are configured."""
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("remote", "-v"): CompletedProcess(args, 0, "", ""),  # No remotes
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console:
        show_remote_urls(tmp_path)
        
        # Should show "No remotes configured" message
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No remotes configured" in call for call in calls)


def test_set_remote_url_new_origin(tmp_path: Path):
    """Test setting a new origin remote."""
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("remote", "get-url", "origin"): CompletedProcess(args, 1, "", ""),  # origin doesn't exist
            ("remote", "add", "origin", "https://github.com/new/repo.git"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console:
        set_remote_url(tmp_path, "https://github.com/new/repo.git")
        
        # Should show success message
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Added origin" in call for call in calls)


def test_set_remote_url_update_existing(tmp_path: Path):
    """Test updating an existing origin remote."""
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("remote", "get-url", "origin"): CompletedProcess(args, 0, "https://github.com/old/repo.git\n", ""),  # origin exists
            ("remote", "set-url", "origin", "https://github.com/new/repo.git"): CompletedProcess(args, 0, "", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console, \
         patch("questionary.confirm") as mock_confirm:
        mock_confirm.return_value.ask.return_value = True  # User confirms update
        
        set_remote_url(tmp_path, "https://github.com/new/repo.git")
        
        # Should show update message
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Updated origin" in call for call in calls)


def test_set_remote_url_user_cancellation(tmp_path: Path):
    """Test cancelling remote URL update."""
    def fake_run(cwd: Path, *args: str):
        mapping = {
            ("rev-parse", "--is-inside-work-tree"): CompletedProcess(args, 0, "true\n", ""),
            ("remote", "get-url", "origin"): CompletedProcess(args, 0, "https://github.com/old/repo.git\n", ""),
        }
        return mapping.get(args, CompletedProcess(args, 0, "", ""))

    with patch("msl.git_tools._run_git", side_effect=fake_run), \
         patch("msl.git_tools.console") as mock_console, \
         patch("questionary.confirm") as mock_confirm:
        mock_confirm.return_value.ask.return_value = False  # User cancels
        
        set_remote_url(tmp_path, "https://github.com/new/repo.git")
        
        # Should show cancellation message
        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Operation cancelled" in call for call in calls)
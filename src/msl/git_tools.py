from __future__ import annotations

import subprocess
from pathlib import Path

import questionary


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=False,
        text=True,
        capture_output=True,
    )


def ensure_git_repo(cwd: Path) -> None:
    result = _run_git(cwd, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise RuntimeError(f"Not a git repository: {cwd}")


def has_changes(cwd: Path) -> bool:
    result = _run_git(cwd, "status", "--porcelain")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not inspect git status")
    return bool(result.stdout.strip())


def get_current_branch(cwd: Path) -> str:
    result = _run_git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not determine current branch")
    return result.stdout.strip()


def create_and_switch_branch(cwd: Path, branch_name: str | None = None) -> str:
    ensure_git_repo(cwd)

    if not branch_name:
        branch_name = questionary.text("New branch name:").ask()
    if not branch_name or not branch_name.strip():
        raise RuntimeError("Branch name is required")

    branch_name = branch_name.strip()
    result = _run_git(cwd, "checkout", "-b", branch_name)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Could not create branch")

    return branch_name


def stage_commit_and_push(
    cwd: Path,
    commit_message: str | None = None,
    *,
    confirm: bool = True,
) -> str:
    ensure_git_repo(cwd)
    if not has_changes(cwd):
        raise RuntimeError("No git changes to commit")

    if not commit_message:
        commit_message = questionary.text("Git commit message:").ask()
    if not commit_message or not commit_message.strip():
        raise RuntimeError("Commit message is required")

    branch = get_current_branch(cwd)
    if confirm:
        confirmed = questionary.confirm(
            f'Stage all changes, commit to "{branch}", and push now?',
            default=True,
        ).ask()
        if not confirmed:
            raise RuntimeError("Git push cancelled")

    for args in (("add", "."), ("commit", "-m", commit_message), ("push",)):
        result = _run_git(cwd, *args)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")

    return branch
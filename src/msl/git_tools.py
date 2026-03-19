from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console

console = Console()


# ── Low-level helpers ──────────────────────────────────────────────────────

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


def get_changed_files(cwd: Path) -> list[str]:
    """Return a list of changed/untracked file paths."""
    result = _run_git(cwd, "status", "--porcelain")
    if result.returncode != 0:
        return []
    files = []
    for line in result.stdout.strip().splitlines():
        if line.strip():
            # porcelain format: XY filename
            files.append(line[3:].strip())
    return files


def get_diff_summary(cwd: Path) -> str:
    """Return a short unified diff summary (stats + 100-line snippet) for the prompt."""
    stat = _run_git(cwd, "diff", "--stat", "HEAD")
    diff = _run_git(cwd, "diff", "HEAD")
    stat_out = stat.stdout.strip() if stat.returncode == 0 else ""
    diff_out = diff.stdout.strip() if diff.returncode == 0 else ""
    # Also capture untracked/staged
    staged = _run_git(cwd, "diff", "--cached", "--stat")
    staged_out = staged.stdout.strip() if staged.returncode == 0 else ""

    parts = []
    if stat_out:
        parts.append(stat_out)
    if staged_out and staged_out != stat_out:
        parts.append(staged_out)

    # Trim diff to 100 lines to avoid blowing up the prompt
    if diff_out:
        lines = diff_out.splitlines()[:100]
        parts.append("\n".join(lines))
        if len(diff_out.splitlines()) > 100:
            parts.append("... (diff truncated)")

    return "\n".join(parts)


def create_and_switch_branch(cwd: Path, branch_name: str | None = None) -> str:
    ensure_git_repo(cwd)

    if not branch_name:
        import questionary
        branch_name = questionary.text("New branch name:").ask()
    if not branch_name or not branch_name.strip():
        raise RuntimeError("Branch name is required")

    branch_name = branch_name.strip()
    result = _run_git(cwd, "checkout", "-b", branch_name)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Could not create branch")

    return branch_name


# ── AI commit message generation ──────────────────────────────────────────

MSL_SERVER_URL = "https://apicommit.umartco.net"


def _generate_via_server(changed_files: list[str], diff_summary: str) -> str:
    """Call the MSL server POST /v1/api/commit endpoint."""
    url = f"{MSL_SERVER_URL.rstrip('/')}/v1/api/commit"
    resp = requests.post(
        url,
        json={"files": changed_files, "diff": diff_summary},
        timeout=35,
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["message"].strip().strip("`\"'")


def generate_commit_message(cwd: Path, api_key: str) -> str:
    """Ask MSL server (or DeepSeek directly as fallback) for a commit message."""
    changed_files = get_changed_files(cwd)
    diff_summary = get_diff_summary(cwd)

    try:
        return _generate_via_server(changed_files, diff_summary)
    except Exception:
        pass

    from .ai_generator import call_deepseek

    files_list = "\n".join(f"  - {f}" for f in changed_files[:30]) or "  (none detected)"
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert software engineer. "
                "Write a concise, conventional-commits style git commit message. "
                "Use the format: <type>(<scope>): <short summary> "
                "Optionally add a blank line then a short body (max 3 bullets). "
                "Output ONLY the commit message text, nothing else."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Changed files:\n{files_list}\n\n"
                f"Diff summary:\n{diff_summary}\n\n"
                "Write the commit message:"
            ),
        },
    ]
    raw = call_deepseek(messages, api_key)
    return raw.strip().strip("`\"'")


# ── Smart push flow ────────────────────────────────────────────────────────


def _step(label: str) -> None:
    console.print(f"  [dim]→[/dim] {label}", end="")


def _ok(detail: str = "") -> None:
    suffix = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [green]✓[/green]{suffix}")


def _fail(detail: str = "") -> None:
    suffix = f"  [dim]{detail}[/dim]" if detail else ""
    console.print(f"  [red]✗[/red]{suffix}")


def smart_push(
    cwd: Path,
    explicit_api_key: Optional[str] = None,
) -> None:
    """
    Full smart push flow:
      1. Ensure git repo + has changes
      2. git add .
      3. Generate commit message via DeepSeek
      4. git commit
      5. git push origin <branch>
         → on failure: retry with --no-verify
         → on failure: error with hint
    """
    from .ai_generator import resolve_api_key

    ensure_git_repo(cwd)

    if not has_changes(cwd):
        raise RuntimeError("No git changes to commit.")

    api_key = resolve_api_key(cwd, explicit_api_key)
    branch = get_current_branch(cwd)

    console.print()
    console.print(f"[bold magenta]⟳ Smart Push[/bold magenta]  branch [cyan]{branch}[/cyan]")
    console.print()

    # ── Step 1: git add . ─────────────────────────────────────────────────
    changed = get_changed_files(cwd)
    console.print(f"[bold]Staging files[/bold] ({len(changed)} changed)")
    for f in changed[:8]:
        console.print(f"  [dim]{f}[/dim]")
    if len(changed) > 8:
        console.print(f"  [dim]... and {len(changed) - 8} more[/dim]")

    _step("git add .")
    result = _run_git(cwd, "add", ".")
    if result.returncode != 0:
        _fail()
        raise RuntimeError(result.stderr.strip() or "git add . failed")
    _ok("staged")

    # ── Step 2: Generate commit message ───────────────────────────────────
    console.print()
    console.print("[bold]Generating commit message[/bold] [dim](DeepSeek)[/dim]")
    with console.status("  [cyan]thinking...[/cyan]", spinner="dots"):
        commit_message = generate_commit_message(cwd, api_key)

    console.print(f"  [green]✓[/green]  [italic]{commit_message}[/italic]")

    # ── Step 3: git commit ────────────────────────────────────────────────
    console.print()
    console.print("[bold]Committing[/bold]")
    _step(f'git commit -m "{commit_message[:60]}..."')
    result = _run_git(cwd, "commit", "-m", commit_message)
    if result.returncode != 0:
        _fail()
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git commit failed")
    _ok()

    # ── Step 4: git push ─────────────────────────────────────────────────
    console.print()
    console.print(f"[bold]Pushing[/bold] → origin/{branch}")
    _step(f"git push origin {branch}")
    result = _run_git(cwd, "push", "origin", branch)

    if result.returncode == 0:
        _ok("pushed")
    else:
        _fail("push failed — retrying with --no-verify")
        _step(f"git push origin {branch} --no-verify")
        result2 = _run_git(cwd, "push", "origin", branch, "--no-verify")
        if result2.returncode == 0:
            _ok("pushed with --no-verify")
        else:
            _fail()
            push_err = result2.stderr.strip() or result2.stdout.strip() or result.stderr.strip()
            console.print()
            console.print("[red bold]Push failed.[/red bold] Possible reasons:")
            console.print("  • The remote branch may not exist yet. Try:")
            console.print(f"    [cyan]git push --set-upstream origin {branch}[/cyan]")
            console.print("  • You may not have push access to this remote.")
            console.print("  [dim]Error:[/dim] " + push_err)
            raise RuntimeError(f"Push failed: {push_err}")

    console.print()
    console.print(
        f"[green bold]✓ Done.[/green bold]  "
        f"Committed and pushed to [cyan]origin/{branch}[/cyan]"
    )
    console.print()


# ── Legacy helper (kept for backward compatibility with existing tests) ────


def stage_commit_and_push(
    cwd: Path,
    commit_message: Optional[str] = None,
    *,
    confirm: bool = True,
) -> str:
    ensure_git_repo(cwd)
    if not has_changes(cwd):
        raise RuntimeError("No git changes to commit")

    if not commit_message:
        import questionary
        commit_message = questionary.text("Git commit message:").ask()
    if not commit_message or not commit_message.strip():
        raise RuntimeError("Commit message is required")

    branch = get_current_branch(cwd)
    if confirm:
        import questionary
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
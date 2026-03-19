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



def _generate_via_server(changed_files: list[str], diff_summary: str) -> str:
    """Call the MSL server POST /api/commit endpoint."""
    from .auth import get_access_token, MSL_AUTH_URL
    
    token = get_access_token()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    url = f"{MSL_AUTH_URL.rstrip('/')}/api/commit"
    
    resp = requests.post(
        url,
        headers=headers,
        json={"files": changed_files, "diff": diff_summary},
        timeout=35,
    )
    if resp.status_code == 401 or resp.status_code == 403:
        raise RuntimeError("Authentication failed. Please run 'msl --login' to authenticate.")
    
    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        try:
            err = resp.json().get("error")
            if err:
                raise RuntimeError(err)
        except:
            pass
        raise RuntimeError(f"MSL API error: {e}")
        
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["message"].strip().strip("`\"'")


def generate_commit_message(cwd: Path) -> str:
    """Ask MSL API for a commit message."""
    changed_files = get_changed_files(cwd)
    diff_summary = get_diff_summary(cwd)

    return _generate_via_server(changed_files, diff_summary)


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
      3. Generate commit message via MSL API
      4. git commit
      5. git push origin <branch>
         → on failure: retry with --no-verify
         → on failure: error with hint
    """
    ensure_git_repo(cwd)

    if not has_changes(cwd):
        raise RuntimeError("No git changes to commit.")

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
    console.print("[bold]Generating commit message[/bold] [dim](MSL API)[/dim]")
    with console.status("  [cyan]thinking...[/cyan]", spinner="dots"):
        commit_message = generate_commit_message(cwd)

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


# ── Git reset functions ───────────────────────────────────────────────────


def has_uncommitted_changes(cwd: Path) -> bool:
    """Check if there are any uncommitted changes in the working directory."""
    result = _run_git(cwd, "status", "--porcelain")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not check git status")
    return bool(result.stdout.strip())


def get_commit_count(cwd: Path) -> int:
    """Get the total number of commits in the repository."""
    result = _run_git(cwd, "rev-list", "--count", "HEAD")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not count commits")
    return int(result.stdout.strip())


def get_commit_info(cwd: Path, count: int) -> list[str]:
    """Get information about the last N commits."""
    result = _run_git(cwd, "log", "--oneline", f"-n{count}")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Could not get commit info")
    return result.stdout.strip().splitlines()


def reset_commits(cwd: Path, count: int, reset_mode: str) -> subprocess.CompletedProcess[str]:
    """Execute git reset with the specified mode."""
    reset_arg = f"--{reset_mode}"
    return _run_git(cwd, "reset", reset_arg, f"HEAD~{count}")


def remove_last_commits(cwd: Path, count: int, reset_mode: str = "mixed") -> None:
    """Remove the last N commits using the specified reset mode.
    
    Args:
        cwd: Git repository path
        count: Number of commits to remove
        reset_mode: 'soft', 'mixed', or 'hard'
    
    Raises:
        RuntimeError: If the operation cannot be performed
    """
    ensure_git_repo(cwd)
    
    # Validate count
    if count <= 0:
        raise ValueError("Commit count must be greater than 0")
    
    # Check for uncommitted changes first
    if has_uncommitted_changes(cwd):
        raise RuntimeError(
            "You have uncommitted changes. Please commit or stash them first."
        )
    
    # Get total commits and validate
    total_commits = get_commit_count(cwd)
    if count >= total_commits:
        raise RuntimeError(
            f"Cannot remove {count} commits from a repository with only {total_commits} commits. "
            "At least 1 commit must remain."
        )
    
    # Get commit info for display
    commits_to_remove = get_commit_info(cwd, count)
    
    # Show warning and details
    console.print()
    console.print(f"[bold red]⚠️  Warning: About to remove {count} commit{'s' if count > 1 else ''}[/bold red]")
    console.print()
    console.print("[bold]Commits to be removed:[/bold]")
    for i, commit in enumerate(commits_to_remove, 1):
        console.print(f"  [dim]{i}.[/dim] {commit}")
    console.print()
    
    # Show what will happen based on reset mode
    if reset_mode == "hard":
        console.print("[bold red]⚠️  HARD RESET:[/bold red] All changes will be [bold]permanently discarded[/bold red]!")
    elif reset_mode == "soft":
        console.print("[bold blue]📦 SOFT RESET:[/bold blue] Changes will be kept as [bold]staged[/bold blue]")
    else:  # mixed
        console.print("[bold yellow]🔄 MIXED RESET:[/bold yellow] Changes will be kept as [bold]unstaged[/bold yellow]")
    
    console.print()
    
    # Ask for confirmation
    import questionary
    confirmed = questionary.confirm(
        f"Are you sure you want to remove the last {count} commit{'s' if count > 1 else ''}?",
        default=False,
    ).ask()
    
    if not confirmed:
        console.print("[yellow]Operation cancelled.[/yellow]")
        return
    
    # Execute the reset
    console.print(f"[dim]→[/dim] Resetting HEAD~{count} ({reset_mode} mode)...")
    result = reset_commits(cwd, count, reset_mode)
    
    if result.returncode != 0:
        error_msg = result.stderr.strip() or result.stdout.strip() or "Git reset failed"
        raise RuntimeError(f"Failed to reset commits: {error_msg}")
    
    # Show success message
    console.print(f"  [green]✓[/green] Removed {count} commit{'s' if count > 1 else ''}")
    
    if reset_mode == "hard":
        console.print("  [dim]All changes have been discarded.[/dim]")
    elif reset_mode == "soft":
        console.print("  [dim]Changes are now staged. Use 'git status' to see them.[/dim]")
    else:  # mixed
        console.print("  [dim]Changes are now unstaged. Use 'git status' to see them.[/dim]")
    
    console.print()


def remove_last_commits_with_prompt(cwd: Path, count: int) -> None:
    """Remove the last N commits with interactive mode selection."""
    import questionary
    
    # Ask for reset mode
    reset_mode = questionary.select(
        "What type of reset do you want?",
        choices=[
            questionary.Choice(title="🔄 Mixed Reset (keep changes unstaged)", value="mixed"),
            questionary.Choice(title="📦 Soft Reset (keep changes staged)", value="soft"),
            questionary.Choice(title="💥 Hard Reset (discard all changes)", value="hard"),
        ],
    ).ask()
    
    if reset_mode is None:
        console.print("[yellow]Operation cancelled.[/yellow]")
        return
    
    # Call the original function with the selected mode
    remove_last_commits(cwd, count, reset_mode)


# ── Git remote functions ───────────────────────────────────────────────────


def show_remote_urls(cwd: Path) -> None:
    """Show all configured remote URLs for the repository."""
    ensure_git_repo(cwd)
    
    console.print()
    console.print("[bold]📡 Git Remote URLs[/bold]")
    console.print()
    
    # Get remote info
    result = _run_git(cwd, "remote", "-v")
    if result.returncode != 0:
        console.print("[yellow]No remotes configured.[/yellow]")
        return
    
    if not result.stdout.strip():
        console.print("[yellow]No remotes configured.[/yellow]")
        return
    
    # Parse and display remotes
    lines = result.stdout.strip().splitlines()
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1]
                fetch_push = "(fetch)" if len(parts) == 2 else f"({parts[2]}, {parts[3]})" if len(parts) >= 4 else "(fetch)"
                
                # Highlight origin remote
                if name == "origin":
                    console.print(f"  [green]{name}[/green]: {url} {fetch_push}")
                else:
                    console.print(f"  [cyan]{name}[/cyan]: {url} {fetch_push}")
    
    console.print()


def set_remote_url(cwd: Path, url: str) -> None:
    """Set or update a remote URL. Defaults to 'origin' if no remote exists."""
    ensure_git_repo(cwd)
    
    if not url or not url.strip():
        raise ValueError("Remote URL cannot be empty")
    
    url = url.strip()
    
    console.print()
    console.print(f"[bold]🔗 Setting Git Remote URL[/bold]")
    console.print()
    console.print(f"URL: [cyan]{url}[/cyan]")
    console.print()
    
    # Check if origin already exists
    result = _run_git(cwd, "remote", "get-url", "origin")
    origin_exists = result.returncode == 0
    
    if origin_exists:
        # Update existing origin
        current_url = result.stdout.strip()
        console.print(f"Current origin: [dim]{current_url}[/dim]")
        
        import questionary
        confirmed = questionary.confirm(
            f"Update origin remote from '{current_url}' to '{url}'?",
            default=True,
        ).ask()
        
        if not confirmed:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
        
        console.print(f"[dim]→[/dim] Updating origin remote...")
        result = _run_git(cwd, "remote", "set-url", "origin", url)
        
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] Updated origin to: {url}")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Failed to update remote"
            raise RuntimeError(f"Failed to update origin remote: {error_msg}")
    else:
        # Add new origin remote
        console.print(f"[dim]→[/dim] Adding new origin remote...")
        result = _run_git(cwd, "remote", "add", "origin", url)
        
        if result.returncode == 0:
            console.print(f"  [green]✓[/green] Added origin: {url}")
        else:
            error_msg = result.stderr.strip() or result.stdout.strip() or "Failed to add remote"
            raise RuntimeError(f"Failed to add origin remote: {error_msg}")
    
    console.print()
    console.print("[dim]Use 'git push -u origin main' to push and set upstream.[/dim]")
    console.print()
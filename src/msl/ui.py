from __future__ import annotations
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__
from .detection import detect_all
from .models import (
    DetectedTool,
    Platform,
    PreferenceTier,
    ProjectType,
    SkillGenContext,
)
from .path_rules import PLATFORM_PATHS
from .scanner import ProjectScan, scan_project

console = Console()

_STYLE = questionary.Style(
    [
        ("qmark", "fg:magenta bold"),
        ("question", "bold"),
        ("answer", "fg:cyan"),
        ("pointer", "fg:magenta bold"),
        ("highlighted", "fg:magenta bold"),
        ("selected", "fg:cyan"),
    ]
)

# Map platform keys to the detection keys
_PLATFORM_DETECT_KEY = {
    Platform.CURSOR: "cursor",
    Platform.VSCODE: "vscode",
    Platform.CLAUDE_CODE: "claude-code",
    Platform.CODEX: "codex",
}


# ── Display helpers ──────────────────────────────────────────────


def show_banner(is_logged_in: bool = False) -> None:
    from rich.align import Align
    
    logo = """
 ███▄ ▄███▓  ██████  ██▓    
▓██▒▀█▀ ██▒▒██    ▒ ▓██▒    
▓██    ▓██░░ ▓██▄   ▒██░    
▒██    ▒██   ▒   ██▒▒██░    
▒██▒   ░██▒▒██████▒▒░██████▒
░ ▒░   ░  ░▒ ▒▓▒ ▒ ░░ ▒░▓  ░
░  ░      ░░ ░▒  ░ ░░ ░ ▒  ░
░      ░   ░  ░  ░    ░ ░   
       ░         ░      ░  ░
"""
    lines = logo.strip().splitlines()
    styled_logo = Text()
    
    # Use green theme for logged in, purple for guest
    primary_color = "#0F9D58" if is_logged_in else "#B829FF"
    colors = ["#0F9D58", "#34A853", "#4285F4", "#4285F4"] if is_logged_in else ["#B829FF", "#9B72CB", "#7289DA", "#4285F4"]
    
    for i, line in enumerate(lines):
        color = colors[min(i, len(colors)-1)]
        styled_logo.append(line + "\n", style=f"bold {color}")
        
    banner_group = Table.grid(padding=(0, 2))
    banner_group.add_row(Align.center(styled_logo))
    
    version_text = Text(f" MSL CLI v{__version__} ", style=f"bold white on {primary_color}")
    if is_logged_in:
        version_text.append(" AUTHENTICATED ", style="bold black on #FBBC05")
        
    banner_group.add_row(Align.center(version_text))
    banner_group.add_row(Align.center(Text("Guided AI skill composer & smart git automation", style="dim italic")))
    banner_group.add_row(Align.center(Text(""))) # Spacer
    banner_group.add_row(Align.center(Text(" [Esc] Back  •  [Ctrl+C] Quit ", style="dim select-none")))
    
    console.print()
    console.print(
        Panel(
            banner_group,
            border_style=primary_color,
            padding=(1, 4),
        )
    )
    console.print()


def show_detection_results(tools: dict[str, DetectedTool]) -> None:
    table = Table(title="Environment Check", border_style="cyan", show_lines=False)
    table.add_column("Tool", style="bold")
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    for name, tool in tools.items():
        if isinstance(tool, str):
            table.add_row(name.replace("_", " ").title(), "[blue]Info[/blue]", tool)
            continue
            
        if tool.installed:
            status = "[green]✓ Installed[/green]"
            detail = tool.version or tool.path or ""
        else:
            status = "[red]✗ Not found[/red]"
            detail = ""
        table.add_row(tool.name, status, detail)

    console.print(table)
    console.print()


def show_scan_results(scan: ProjectScan) -> None:
    """Show what we auto-detected about the project."""
    table = Table(title="Project Scan", border_style="blue", show_lines=False)
    table.add_column("", style="bold")
    table.add_column("")

    if scan.name:
        table.add_row("Name", scan.name)
    if scan.languages:
        table.add_row("Languages", ", ".join(scan.languages))
    if scan.frameworks:
        # Show only the first few interesting ones
        display = scan.frameworks[:8]
        table.add_row("Detected", ", ".join(display))
    if scan.package_manager:
        table.add_row("Package Manager", scan.package_manager)
    if scan.detected_type:
        conf = f" ({int(scan.confidence * 100)}% confidence)"
        table.add_row("Auto-detected Type", f"[cyan]{scan.detected_type.display_name}[/cyan]{conf}")

    flags = []
    if scan.has_tests:
        flags.append("[green]Tests ✓[/green]")
    if scan.has_ci:
        flags.append("[green]CI ✓[/green]")
    if scan.has_docker:
        flags.append("[green]Docker ✓[/green]")
    if scan.has_monorepo:
        flags.append("[yellow]Monorepo[/yellow]")
    if flags:
        table.add_row("Flags", " │ ".join(flags))
    if scan.src_dirs:
        table.add_row("Source dirs", ", ".join(scan.src_dirs))

    console.print(table)
    console.print()


def show_success(output_path: Path) -> None:
    console.print()
    console.print(
        Panel(
            f"[green]✓[/green] Skill file generated at:\n[bold]{output_path}[/bold]",
            border_style="green",
            title="Done",
        )
    )


def show_cancelled() -> None:
    console.print("\n[yellow]Cancelled.[/yellow]")


# ── Interactive prompts ──────────────────────────────────────────


def _ask(result: object) -> object:
    """Raise KeyboardInterrupt when the user presses Ctrl-C / Ctrl-D."""
    if result is None:
        raise KeyboardInterrupt
    return result


def ask_platform(tools: dict[str, DetectedTool]) -> Platform:
    """Show only installed platforms — if none are installed, show all."""
    choices = []
    installed_any = False

    for platform in Platform:
        detect_key = _PLATFORM_DETECT_KEY[platform]
        tool = tools.get(detect_key)
        is_installed = tool and tool.installed

        if is_installed:
            installed_any = True

        # Get the actual output filename for this platform
        _dir, filename = PLATFORM_PATHS[platform.value]
        if _dir:
            dest = f"{_dir}/{filename}"
        else:
            dest = filename

        label = f"{platform.display_name}  →  {dest}"
        if is_installed:
            label += "  [green][installed][/green]"

        choices.append(questionary.Choice(title=label, value=platform, disabled=False))

    # If we found installed platforms, mark uninstalled ones as disabled
    if installed_any:
        final_choices = []
        for platform in Platform:
            detect_key = _PLATFORM_DETECT_KEY[platform]
            tool = tools.get(detect_key)
            is_installed = tool and tool.installed

            _dir, filename = PLATFORM_PATHS[platform.value]
            dest = f"{_dir}/{filename}" if _dir else filename

            if is_installed:
                label = f"{platform.display_name}  →  {dest}"
                final_choices.append(questionary.Choice(title=label, value=platform))
            else:
                label = f"{platform.display_name}  →  {dest}  (not installed)"
                final_choices.append(questionary.Choice(title=label, value=platform))
        choices = final_choices

    return _ask(
        questionary.select(
            "Where do you want to set your skill?",
            choices=choices,
            style=_STYLE,
        ).ask()
    )


def ask_project_path() -> Path:
    cwd = Path.cwd()

    choice = _ask(
        questionary.select(
            "What is your project path?",
            choices=[
                questionary.Choice(
                    title=f"Current directory  ({cwd})", value="current"
                ),
                questionary.Choice(title="Other (enter path)", value="other"),
            ],
            style=_STYLE,
        ).ask()
    )

    if choice == "current":
        return cwd

    path_str = _ask(
        questionary.path("Enter your project path:", style=_STYLE).ask()
    )

    path = Path(path_str).expanduser().resolve()
    if not path.is_dir():
        console.print(f"[red]Path does not exist or is not a directory: {path}[/red]")
        return ask_project_path()
    return path


def ask_project_type(scan: ProjectScan) -> ProjectType:
    """If the scanner found a confident match, suggest it as default."""
    choices = []
    default = None

    for pt in ProjectType:
        label = pt.display_name
        if scan.detected_type == pt and scan.confidence >= 0.7:
            label += "  [green](auto-detected)[/green]"
            default = pt
        choices.append(questionary.Choice(title=label, value=pt))

    return _ask(
        questionary.select(
            "What is your project about?",
            choices=choices,
            default=default,
            style=_STYLE,
        ).ask()
    )


def ask_preference_tier() -> PreferenceTier:
    choices = [
        questionary.Choice(title=tier.display_name, value=tier)
        for tier in PreferenceTier
    ]
    return _ask(
        questionary.select(
            "What is your preference level?", choices=choices, style=_STYLE
        ).ask()
    )


def ask_confirmation(ctx: SkillGenContext, scan: ProjectScan) -> bool:
    console.print()
    summary = Table(title="Summary", border_style="green", show_lines=False)
    summary.add_column("Setting", style="bold")
    summary.add_column("Value")
    summary.add_row("Platform", ctx.target_platform.display_name)
    summary.add_row("Project Path", str(ctx.project_path))
    summary.add_row("Project Type", ctx.project_type.display_name)
    summary.add_row("Preference", ctx.preference_tier.display_name)
    summary.add_row("Output File", f"[cyan]{ctx.output_path}[/cyan]")

    if scan.frameworks:
        fw_display = scan.frameworks[:6]
        summary.add_row("Detected Stack", ", ".join(fw_display))

    console.print(summary)
    console.print()

    return _ask(
        questionary.confirm("Ready to generate?", default=True, style=_STYLE).ask()
    )


def ask_use_ai() -> bool:
    from .auth import get_access_token
    if not get_access_token():
        console.print("\n[yellow]MSL AI features require authentication. Run 'msl --login' to enable AI features.[/yellow]")
        return False
        
    console.print()
    return _ask(
        questionary.confirm(
            "Would you like to enhance this with MSL AI (reads project files)?",
            default=False,
            style=_STYLE,
        ).ask()
    )


def ask_main_action(is_logged_in: bool = False) -> str:
    choices = [
        questionary.Choice(title="✨ Create AI Skill File (--ai)", value="skill"),
        questionary.Choice(title="🚀 Smart Git Push (--gp)", value="git"),
        questionary.Choice(title="🗑️  Remove Commits (--gsr)", value="reset"),
        questionary.Choice(title="📡 Manage Remotes (--gru/--grs)", value="remote"),
        questionary.Choice(title="🛠️  Perfect Project (--perfect)", value="perfect"),
    ]
    
    if is_logged_in:
        choices.append(questionary.Choice(title="門 Logout from MSL (--logout)", value="logout"))
    else:
        choices.append(questionary.Choice(title="🔐 Login to MSL (--login)", value="login"))
        
    return _ask(
        questionary.select(
            "What do you want to do?",
            choices=choices,
            style=_STYLE,
        ).ask()
    )


def ask_remote_action() -> str:
    return _ask(
        questionary.select(
            "What do you want to do with remotes?",
            choices=[
                questionary.Choice(title="👀 Show Remote URLs", value="show"),
                questionary.Choice(title="🔗 Set/Update Remote URL", value="set"),
            ],
            style=_STYLE,
        ).ask()
    )


def ask_remote_url() -> str:
    return _ask(
        questionary.text(
            "Enter the remote URL:",
            validate=lambda text: text.strip() != "" or "Remote URL cannot be empty"
        ).ask()
    )


def ask_reset_action() -> str:
    return _ask(
        questionary.select(
            "What type of reset do you want?",
            choices=[
                questionary.Choice(title="🔄 Mixed Reset (keep changes unstaged)", value="mixed"),
                questionary.Choice(title="📦 Soft Reset (keep changes staged)", value="soft"),
                questionary.Choice(title="💥 Hard Reset (discard all changes)", value="hard"),
            ],
            style=_STYLE,
        ).ask()
    )


def ask_commit_count() -> int:
    return _ask(
        questionary.text(
            "How many commits do you want to remove?",
            validate=lambda text: text.isdigit() and int(text) > 0 or "Please enter a positive number"
        ).ask()
    )


# ── Wizard orchestration ────────────────────────────────────────


def run_wizard() -> tuple[SkillGenContext, ProjectScan, bool] | None:
    from .auth import get_access_token
    is_logged_in = bool(get_access_token())
    show_banner(is_logged_in)

    action = ask_main_action(is_logged_in)

    if action == "login":
        from .auth import msl_login
        token = _ask(questionary.text("Enter your MSL API Token:", style=_STYLE).ask())
        msl_login(str(token))
        return None

    if action == "logout":
        from .auth import msl_logout
        msl_logout()
        return None

    if action == "perfect":
        from .devtools import apply_perfect_scripts
        try:
            path = ask_project_path()
            apply_perfect_scripts(path)
            console.print(f"[green]✓ Perfect scripts applied to project at {path}[/green]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        return None

    if action == "git":
        from .auth import get_access_token
        if not get_access_token():
            console.print("\n[yellow]Smart Git Push uses MSL AI which requires authentication. Run 'msl --login' to authenticate first.[/yellow]\n")
            return None
            
        from .git_tools import smart_push
        try:
            smart_push(Path.cwd())
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        return None

    if action == "reset":
        from .git_tools import remove_last_commits
        try:
            reset_mode = ask_reset_action()
            count = ask_commit_count()
            remove_last_commits(Path.cwd(), int(count), reset_mode)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        return None

    if action == "remote":
        from .git_tools import show_remote_urls, set_remote_url
        try:
            remote_action = ask_remote_action()
            if remote_action == "show":
                show_remote_urls(Path.cwd())
            elif remote_action == "set":
                url = ask_remote_url()
                set_remote_url(Path.cwd(), url)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        return None

    # Proceed with Skill Generation flow
    with console.status("[cyan]Checking your environment...[/cyan]", spinner="dots"):
        tools = detect_all()

    show_detection_results(tools)

    platform = ask_platform(tools)
    project_path = ask_project_path()

    # Smart scan
    with console.status("[cyan]Scanning project...[/cyan]", spinner="dots"):
        scan = scan_project(project_path)

    if scan.detected_type:
        show_scan_results(scan)

    project_type = ask_project_type(scan)
    preference = ask_preference_tier()

    ctx = SkillGenContext(
        target_platform=platform,
        project_path=project_path,
        project_type=project_type,
        preference_tier=preference,
        detected_tools=tools,
    )

    if not ask_confirmation(ctx, scan):
        show_cancelled()
        return None

    use_ai = ask_use_ai()
    
    if use_ai:
        from .ai_generator import generate_with_ai
        status_msg = "[cyan]Analyzing project files with MSL AI magic...[/cyan]"
        with console.status(status_msg, spinner="bouncingBar"):
            content = generate_with_ai(ctx, scan)
            from .writer import write_content_to_file
            output_path = write_content_to_file(ctx.output_path, ctx.project_path, ctx.target_platform, content)
            show_success(output_path)
            return None # The tool has completed its writing successfully

    return ctx, scan, False

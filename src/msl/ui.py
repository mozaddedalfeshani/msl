from __future__ import annotations
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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


def show_banner() -> None:
    banner = Text()
    banner.append("MSL", style="bold magenta")
    banner.append(" — Muradian Skill Languages", style="dim")
    console.print(Panel(banner, border_style="magenta", padding=(1, 2)))
    console.print()


def show_detection_results(tools: dict[str, DetectedTool]) -> None:
    table = Table(title="Environment Check", border_style="cyan", show_lines=False)
    table.add_column("Tool", style="bold")
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    for tool in tools.values():
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
            default = pt.display_name + "  [green](auto-detected)[/green]"
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


# ── Wizard orchestration ────────────────────────────────────────


def run_wizard() -> tuple[SkillGenContext, ProjectScan] | None:
    show_banner()

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

    return ctx, scan

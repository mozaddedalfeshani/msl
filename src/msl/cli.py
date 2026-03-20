from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import __version__, configure_logging

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="msl",
        add_help=False,
        description=(
            "Interactive wizard or non-interactive generator for platform-specific "
            "skill files used by AI coding assistants."
        ),
    )
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-V", "--version", action="store_true")
    parser.add_argument("--platform", choices=["cursor", "vscode", "claude-code", "codex", "windsurf", "antigravity"])
    parser.add_argument("--project-path")
    parser.add_argument(
        "--project-type",
        choices=["flutter", "nextjs", "react-vite", "rust-server", "nodejs-server", "python", "go-server", "general"],
    )
    parser.add_argument(
        "--preference",
        choices=["simple", "intermediate", "industry_standard"],
    )
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list-options", action="store_true")
    parser.add_argument("--perfect", action="store_true")
    parser.add_argument("--gp", action="store_true", help="Smart Git Push (add, commit, push)")
    parser.add_argument("--gbs", action="store_true", help="Create and switch to a new branch")
    parser.add_argument("--gsr", type=int, help="Git reset last N commits (prompts for reset mode)")
    parser.add_argument("--gru", action="store_true", help="Git remote: show remote URLs")
    parser.add_argument("--grs", help="Git remote: save/set remote URL")
    parser.add_argument("--login", type=str, metavar="TOKEN", help="Login to MSL using your 32-digit API Token")
    parser.add_argument("--logout", action="store_true", help="Logout from MSL and clear stored credentials")
    parser.add_argument("--ai", action="store_true", help="Generate using MSL AI based on project context")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (use -vv for debug)",
    )
    return parser


def _print_help() -> None:
    print(
        "Usage: msl [options]\n"
        "\n"
        "  Interactive wizard that generates platform-specific skill\n"
        "  files for AI coding assistants (Cursor, VS Code, Claude Code, Codex).\n"
        "\n"
        "Interactive:\n"
        "  msl\n"
        "\n"
        "Non-interactive:\n"
        "  msl --ai --platform vscode --project-type python --preference intermediate --project-path .\n"
        "  msl --ai --platform cursor --project-type nextjs --preference industry_standard --stdout\n"
        "  msl --perfect --project-path .\n"
        "  msl --gp\n"
        "  msl --gbs\n"
        "  msl --gsr 32\n"
        "  msl --gru\n"
        "  msl --grs https://github.com/user/repo.git\n"
        "\n"
        "Options:\n"
        "  -h, --help           Show this help message\n"
        "  -V, --version        Show version number\n"
        "  --platform           Target platform\n"
        "  --project-path       Project directory to scan and write into\n"
        "  --project-type       Project type to generate for\n"
        "  --preference         Preference tier\n"
        "  --stdout             Print generated content instead of writing a file\n"
        "  --force              Overwrite existing output without prompting\n"
        "  --list-options       Print supported platform, project type, and preference values\n"
        "  --perfect            Apply recommended package.json scripts for web projects\n"
        "  --gp                 Smart Git Push (add, commit, push)\n"
        "  --gbs                Prompt for a new branch name, then create and switch to it\n"
        "  --gsr N              Git reset last N commits (prompts for reset mode)\n"
        "  --gru                Git remote: show remote URLs\n"
        "  --grs URL            Git remote: save/set remote URL\n"
        "  --ai                 Generate a perfect skill file using MSL AI\n"
    )


def _print_supported_options() -> None:
    print("Platforms: cursor, vscode, claude-code, codex, windsurf, antigravity")
    print("Project types: flutter, nextjs, react-vite, rust-server, nodejs-server, python, go-server, general")
    print("Preferences: simple, intermediate, industry_standard")


def _is_non_interactive(args: argparse.Namespace) -> bool:
    return any(
        value is not None and value is not False
        for value in (
            args.perfect,
            args.gp,
            args.gbs,
            args.gsr,
            args.gru,
            args.grs,
            args.ai,
            args.login,
            args.logout,
            args.platform,
            args.project_path,
            args.project_type,
            args.preference,
            args.stdout,
            args.force,
        )
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args(sys.argv[1:])

    configure_logging(args.verbose)
    
    # Automated background sync on launch
    from .ai_generator import sync_project_to_api
    sync_project_to_api(Path.cwd())
    logger.info("Starting MSL CLI v%s", __version__)
    logger.debug("Parsed args: %s", args)

    if args.version:
        print(f"msl {__version__}")
        logger.info("Displayed version")
        return
    if args.help:
        _print_help()
        logger.info("Displayed help")
        return
    if args.list_options:
        _print_supported_options()
        logger.info("Listed supported options")
        return

    from .models import Platform, PreferenceTier, ProjectType, SkillGenContext
    from .scanner import scan_project
    from .ui import console, run_wizard, show_cancelled, show_scan_results, show_success
    from .writer import generate_skill_file, render_skill_content, write_content_to_file
    from .devtools import apply_perfect_scripts
    from .git_tools import create_and_switch_branch, stage_commit_and_push, smart_push
    from .ai_generator import generate_with_ai
    from .auth import msl_login

    try:
        if args.login:
            logger.info("Initiating token login")
            msl_login(args.login)
            return

        if args.logout:
            logger.info("Initiating logout")
            from .auth import msl_logout
            msl_logout()
            return

        if _is_non_interactive(args):
            logger.info("Running in non-interactive mode")
            project_path = Path(args.project_path or ".").expanduser().resolve()
            if args.perfect:
                logger.info("Applying perfect scripts at %s", project_path)
                package_json_path, changed, skipped = apply_perfect_scripts(
                    project_path,
                    force=args.force,
                )
                if changed:
                    console.print(f"[green]Updated scripts in {package_json_path}[/green]")
                    for name, command in changed.items():
                        console.print(f"  [cyan]{name}[/cyan] = {command}")
                else:
                    console.print(f"[yellow]No script changes needed in {package_json_path}[/yellow]")
                if skipped:
                    console.print("[yellow]Skipped existing custom scripts:[/yellow]")
                    for name in skipped:
                        console.print(f"  [yellow]{name}[/yellow]")
                return

            if args.gp:
                logger.info("Executing Smart Push")
                smart_push(project_path)
                return

            if args.gbs:
                logger.info("Creating and switching to new branch")
                branch = create_and_switch_branch(project_path)
                console.print(f"[green]Switched to new branch {branch}[/green]")
                logger.info("Switched to branch %s", branch)
                return

            # Handle git reset command
            if args.gsr is not None:
                logger.info("Git reset last %d commits", args.gsr)
                from .git_tools import remove_last_commits_with_prompt
                remove_last_commits_with_prompt(project_path, args.gsr)
                return

            # Handle git remote commands
            if args.gru:
                logger.info("Showing git remote URLs")
                from .git_tools import show_remote_urls
                show_remote_urls(project_path)
                return

            if args.grs:
                logger.info("Setting git remote URL: %s", args.grs)
                from .git_tools import set_remote_url
                set_remote_url(project_path, args.grs)
                return

            missing = [
                name
                for name, value in (
                    ("--platform", args.platform),
                    ("--project-type", args.project_type),
                    ("--preference", args.preference),
                )
                if not value
            ]
            if missing:
                logger.error("Missing required flags for non-interactive mode: %s", missing)
                raise ValueError(
                    "Non-interactive mode requires: " + ", ".join(missing)
                )

            if not project_path.is_dir():
                logger.error("Invalid project path: %s", project_path)
                raise ValueError(f"Project path does not exist or is not a directory: {project_path}")

            ctx = SkillGenContext(
                target_platform=Platform(args.platform),
                project_path=project_path,
                project_type=ProjectType(args.project_type),
                preference_tier=PreferenceTier(args.preference),
            )
            scan = scan_project(project_path)
            logger.info("Scanned project %s", project_path)
            if scan.detected_type:
                show_scan_results(scan)

            if args.ai:
                logger.info("Generating with MSL AI for %s", ctx.target_platform)
                status_msg = "[cyan]MSL AI is analyzing your project...[/cyan]"
                with console.status(status_msg, spinner="bouncingBar"):
                    content = generate_with_ai(ctx, scan)
            else:
                logger.info("Rendering template-based skill for %s", ctx.target_platform)
                content = render_skill_content(ctx, scan)

            if args.stdout:
                logger.info("Writing output to STDOUT")
                print(content, end="")
                return

            output_path = write_content_to_file(ctx.output_path, ctx.project_path, ctx.target_platform, content, force=args.force)
            logger.info("Wrote skill file to %s", output_path)
            show_success(output_path)
            return

        logger.info("Launching interactive wizard")
        result = run_wizard()
        if result is None:
            logger.info("Wizard completed without generating context (likely Smart Push or early exit)")
            sys.exit(0)

        ctx, scan = result
        logger.info("Generating skill from interactive context for %s", ctx.target_platform)
        output_path = generate_skill_file(ctx, scan)
        logger.info("Skill file written to %s", output_path)
        show_success(output_path)

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        show_cancelled()
        sys.exit(0)
    except FileExistsError as exc:
        logger.warning("File exists error: %s", exc)
        console.print(f"\n[yellow]{exc}[/yellow]")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Unexpected error")
        console.print(f"\n[red]Error: {exc}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

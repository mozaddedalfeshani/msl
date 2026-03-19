from __future__ import annotations

import argparse
import sys
from pathlib import Path


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
    parser.add_argument("--platform", choices=["cursor", "vscode", "claude-code", "codex"])
    parser.add_argument("--project-path")
    parser.add_argument(
        "--project-type",
        choices=["flutter", "nextjs", "react-vite", "rust-server", "nodejs-server", "python", "go-server"],
    )
    parser.add_argument(
        "--preference",
        choices=["simple", "intermediate", "industry_standard"],
    )
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--list-options", action="store_true")
    parser.add_argument("--perfect", action="store_true")
    parser.add_argument("--gph", action="store_true")
    parser.add_argument("--gbs", action="store_true")
    parser.add_argument("--ai", action="store_true", help="Generate using DeepSeek AI based on project context")
    parser.add_argument("--ai-key", help="Explicit DeepSeek API key (overrides env/.env)")
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
        "  msl --gph\n"
        "  msl --gbs\n"
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
        "  --gph                Prompt for a git commit message, then add, commit, and push\n"
        "  --gbs                Prompt for a new branch name, then create and switch to it\n"
        "  --ai                 Generate a perfect skill file using DeepSeek AI\n"
        "  --ai-key             Provide DeepSeek API key explicitly\n"
    )


def _print_supported_options() -> None:
    print("Platforms: cursor, vscode, claude-code, codex")
    print("Project types: flutter, nextjs, react-vite, rust-server, nodejs-server, python, go-server")
    print("Preferences: simple, intermediate, industry_standard")


def _is_non_interactive(args: argparse.Namespace) -> bool:
    return any(
        value is not None and value is not False
        for value in (
            args.perfect,
            args.gph,
            args.gbs,
            args.ai,
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

    if args.version:
        from . import __version__

        print(f"msl {__version__}")
        return
    if args.help:
        _print_help()
        return
    if args.list_options:
        _print_supported_options()
        return

    from .models import Platform, PreferenceTier, ProjectType, SkillGenContext
    from .scanner import scan_project
    from .ui import console, run_wizard, show_cancelled, show_scan_results, show_success
    from .writer import generate_skill_file, render_skill_content, write_content_to_file
    from .devtools import apply_perfect_scripts
    from .git_tools import create_and_switch_branch, stage_commit_and_push, smart_push
    from .ai_generator import generate_with_ai

    try:
        if _is_non_interactive(args):
            project_path = Path(args.project_path or ".").expanduser().resolve()
            if args.perfect:
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

            if args.gph:
                smart_push(project_path, explicit_api_key=args.ai_key)
                return

            if args.gbs:
                branch = create_and_switch_branch(project_path)
                console.print(f"[green]Switched to new branch {branch}[/green]")
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
                raise ValueError(
                    "Non-interactive mode requires: " + ", ".join(missing)
                )

            if not project_path.is_dir():
                raise ValueError(f"Project path does not exist or is not a directory: {project_path}")

            ctx = SkillGenContext(
                target_platform=Platform(args.platform),
                project_path=project_path,
                project_type=ProjectType(args.project_type),
                preference_tier=PreferenceTier(args.preference),
            )
            scan = scan_project(project_path)
            if scan.detected_type:
                show_scan_results(scan)

            if args.ai:
                with console.status("[cyan]Generating with DeepSeek AI...[/cyan]", spinner="dots"):
                    content = generate_with_ai(ctx, scan, explicit_api_key=args.ai_key)
            else:
                content = render_skill_content(ctx, scan)

            if args.stdout:
                print(content, end="")
                return

            output_path = write_content_to_file(ctx.output_path, ctx.project_path, ctx.target_platform, content, force=args.force)
            show_success(output_path)
            return

        result = run_wizard(args.ai_key)
        if result is None:
            sys.exit(0)

        ctx, scan = result
        output_path = generate_skill_file(ctx, scan)
        show_success(output_path)

    except KeyboardInterrupt:
        show_cancelled()
        sys.exit(0)
    except FileExistsError as exc:
        console.print(f"\n[yellow]{exc}[/yellow]")
        sys.exit(0)
    except Exception as exc:
        console.print(f"\n[red]Error: {exc}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

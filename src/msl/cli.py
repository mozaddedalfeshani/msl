from __future__ import annotations

import sys


def main() -> None:
    # Handle --version / --help before importing heavy dependencies
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--version", "-V"):
            from . import __version__
            print(f"msl {__version__}")
            return
        if arg in ("--help", "-h"):
            print(
                "Usage: msl [options]\n"
                "\n"
                "  Interactive wizard that generates platform-specific skill\n"
                "  files for AI coding assistants (Cursor, VS Code, Claude Code, Codex).\n"
                "\n"
                "Options:\n"
                "  -h, --help     Show this help message\n"
                "  -V, --version  Show version number\n"
            )
            return

    from .ui import console, run_wizard, show_cancelled, show_success
    from .writer import generate_skill_file

    try:
        result = run_wizard()
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

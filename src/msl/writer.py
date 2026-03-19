from __future__ import annotations
from pathlib import Path

import questionary

from .models import SkillGenContext
from .path_rules import get_output_dir
from .scanner import ProjectScan
from .templates import get_template_content, render_template

_STYLE = questionary.Style(
    [
        ("qmark", "fg:magenta bold"),
        ("question", "bold"),
        ("answer", "fg:cyan"),
    ]
)


def render_skill_content(ctx: SkillGenContext, scan: ProjectScan | None = None) -> str:
    content = get_template_content(ctx.project_type, ctx.preference_tier)

    scan_context = {}
    frameworks = []
    if scan:
        if scan.name:
            scan_context["Project Name"] = scan.name
        if scan.package_manager:
            scan_context["Package Manager"] = scan.package_manager
        if scan.languages:
            scan_context["Languages"] = ", ".join(scan.languages)
        frameworks = scan.frameworks[:10]

    return render_template(
        content,
        {
            "platform": ctx.target_platform.display_name,
            "project_type": ctx.project_type.display_name,
            "preference": ctx.preference_tier.display_name,
        },
        frameworks=frameworks,
        scan_context=scan_context,
    )


def write_content_to_file(
    output_path: Path,
    project_root: Path,
    target_platform: object,
    content: str,
    *,
    force: bool = False,
) -> Path:
    output_dir = get_output_dir(target_platform, project_root)

    # Safe overwrite check
    if output_path.exists() and not force:
        overwrite = questionary.confirm(
            f"File already exists at {output_path}. Overwrite?",
            default=False,
            style=_STYLE,
        ).ask()
        if not overwrite:
            raise FileExistsError(f"Aborted: {output_path} already exists")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def generate_skill_file(
    ctx: SkillGenContext,
    scan: ProjectScan | None = None,
    *,
    force: bool = False,
) -> Path:
    rendered = render_skill_content(ctx, scan)
    return write_content_to_file(ctx.output_path, ctx.project_path, ctx.target_platform, rendered, force=force)

#
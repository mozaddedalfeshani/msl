from __future__ import annotations

import json
from pathlib import Path

from .scanner import scan_project

SCRIPT_ORDER = [
    "test:watch",
    "test",
    "format",
    "format:check",
    "postbuild",
    "prepare",
    "fulltest",
]


def _load_package_json(project_path: Path) -> tuple[Path, dict[str, object]]:
    package_json_path = project_path / "package.json"
    if not package_json_path.exists():
        raise FileNotFoundError(f"No package.json found in {project_path}")

    try:
        data = json.loads(package_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid package.json: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("package.json must contain a JSON object")

    return package_json_path, data


def _runner_for(package_manager: str) -> str:
    return {
        "bun": "bun",
        "pnpm": "pnpm",
        "yarn": "yarn",
        "npm": "npm run",
    }.get(package_manager, "npm run")


def _collect_dependencies(data: dict[str, object]) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies"):
        block = data.get(key, {})
        if isinstance(block, dict):
            names.update(str(dep) for dep in block.keys())
    return names


def _compose_fulltest(script_names: set[str], package_manager: str) -> str | None:
    ordered_steps = [
        ("lint:fix", "Linting Fix completed"),
        ("lint:strict", "Linting check completed"),
        ("typecheck", "Typecheck completed"),
        ("format:check", "Format check completed"),
        ("test", "Test step completed"),
    ]
    available = [step for step in ordered_steps if step[0] in script_names]
    if not available:
        return None

    runner = _runner_for(package_manager)
    commands = [f'{runner} {name} && echo "OK {label}"' for name, label in available]
    return " && ".join(commands)


def build_perfect_scripts(data: dict[str, object], package_manager: str) -> dict[str, str]:
    dependencies = _collect_dependencies(data)
    existing_scripts = data.get("scripts", {})
    if not isinstance(existing_scripts, dict):
        existing_scripts = {}

    scripts: dict[str, str] = {}

    if "jest" in dependencies:
        scripts["test:watch"] = "jest --watch"
        scripts["test"] = "jest"

    if "prettier" in dependencies:
        scripts["format"] = "prettier -w ."
        scripts["format:check"] = "prettier -c ."

    if "next-sitemap" in dependencies:
        scripts["postbuild"] = "next-sitemap --config next-sitemap.config.js"

    if "husky" in dependencies:
        scripts["prepare"] = "husky install"

    combined_script_names = set(str(name) for name in existing_scripts.keys()) | set(scripts.keys())
    fulltest = _compose_fulltest(combined_script_names, package_manager)
    if fulltest:
        scripts["fulltest"] = fulltest

    return scripts


def apply_perfect_scripts(
    project_path: Path,
    *,
    force: bool = False,
) -> tuple[Path, dict[str, str], dict[str, str]]:
    package_json_path, data = _load_package_json(project_path)
    scan = scan_project(project_path)
    package_manager = scan.package_manager or "npm"

    existing_scripts = data.get("scripts", {})
    if not isinstance(existing_scripts, dict):
        existing_scripts = {}

    suggested = build_perfect_scripts(data, package_manager)
    if not suggested:
        raise ValueError(
            "Could not infer any recommended scripts. Add common tools like jest, prettier, husky, or next-sitemap first."
        )

    added_or_updated: dict[str, str] = {}
    skipped: dict[str, str] = {}
    merged_scripts = dict(existing_scripts)

    for name in SCRIPT_ORDER:
        if name not in suggested:
            continue

        current = merged_scripts.get(name)
        target = suggested[name]
        if current is None or force:
            if current != target:
                merged_scripts[name] = target
                added_or_updated[name] = target
        elif current != target:
            skipped[name] = str(current)

    if not added_or_updated:
        return package_json_path, {}, skipped

    data["scripts"] = merged_scripts
    package_json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return package_json_path, added_or_updated, skipped
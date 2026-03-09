import json
from pathlib import Path

from msl.devtools import apply_perfect_scripts, build_perfect_scripts


def test_build_perfect_scripts_for_bun_project():
    data = {
        "dependencies": {"next": "14.0.0"},
        "devDependencies": {
            "jest": "29.0.0",
            "prettier": "3.0.0",
            "next-sitemap": "4.0.0",
            "husky": "9.0.0",
        },
        "scripts": {"lint:fix": "eslint . --fix", "lint:strict": "eslint .", "typecheck": "tsc --noEmit"},
    }

    scripts = build_perfect_scripts(data, "bun")
    assert scripts["test"] == "jest"
    assert scripts["test:watch"] == "jest --watch"
    assert scripts["format"] == "prettier -w ."
    assert scripts["postbuild"] == "next-sitemap --config next-sitemap.config.js"
    assert scripts["prepare"] == "husky install"
    assert scripts["fulltest"].startswith("bun lint:fix")


def test_apply_perfect_scripts_merges_missing_scripts(tmp_path: Path):
    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {
                "name": "demo",
                "devDependencies": {"jest": "29", "prettier": "3"},
                "scripts": {"lint:fix": "eslint . --fix", "lint:strict": "eslint .", "typecheck": "tsc --noEmit"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "bun.lockb").write_text("", encoding="utf-8")

    package_json_path, changed, skipped = apply_perfect_scripts(tmp_path)

    assert package_json_path == package_json
    assert "test" in changed
    assert not skipped
    updated = json.loads(package_json.read_text(encoding="utf-8"))
    assert updated["scripts"]["fulltest"].startswith("bun lint:fix")


def test_apply_perfect_scripts_skips_existing_script_without_force(tmp_path: Path):
    package_json = tmp_path / "package.json"
    package_json.write_text(
        json.dumps(
            {
                "name": "demo",
                "devDependencies": {"jest": "29"},
                "scripts": {"test": "vitest"},
            }
        ),
        encoding="utf-8",
    )

    _, changed, skipped = apply_perfect_scripts(tmp_path)

    assert "test" not in changed
    assert skipped["test"] == "vitest"
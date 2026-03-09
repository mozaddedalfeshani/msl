import tempfile
from pathlib import Path

from msl.models import Platform, PreferenceTier, ProjectType, SkillGenContext
from msl.writer import generate_skill_file, render_skill_content


def _make_ctx(tmp: Path, platform: Platform = Platform.CURSOR) -> SkillGenContext:
    return SkillGenContext(
        target_platform=platform,
        project_path=tmp,
        project_type=ProjectType.FLUTTER,
        preference_tier=PreferenceTier.SIMPLE,
    )


def test_generate_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp))
        result = generate_skill_file(ctx)
        assert result.exists()
        assert result.read_text(encoding="utf-8").strip() != ""


def test_generate_creates_hidden_dir():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp), Platform.VSCODE)
        generate_skill_file(ctx)
        assert (Path(tmp) / ".github").is_dir()


def test_generate_correct_path_claude():
    """Claude Code writes CLAUDE.md at project root."""
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp), Platform.CLAUDE_CODE)
        result = generate_skill_file(ctx)
        assert result == Path(tmp) / "CLAUDE.md"


def test_generate_correct_path_codex():
    """Codex writes AGENTS.md at project root."""
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp), Platform.CODEX)
        result = generate_skill_file(ctx)
        assert result == Path(tmp) / "AGENTS.md"


def test_generate_overwrite_prompt_decline(monkeypatch):
    """When the file exists and the user declines overwrite, FileExistsError is raised."""
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp))
        generate_skill_file(ctx)  # first write

        # Simulate user declining overwrite
        monkeypatch.setattr("msl.writer.questionary.confirm", _fake_confirm_no)
        try:
            generate_skill_file(ctx)
            assert False, "Should have raised FileExistsError"
        except FileExistsError:
            pass


def test_render_skill_content_returns_rendered_text():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp))
        rendered = render_skill_content(ctx)
        assert isinstance(rendered, str)
        assert rendered.strip() != ""


def test_generate_force_overwrites_without_prompt(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        ctx = _make_ctx(Path(tmp))
        output_path = generate_skill_file(ctx)
        output_path.write_text("old content", encoding="utf-8")

        def _fail_if_called(*args, **kwargs):
            raise AssertionError("prompt should not be called in force mode")

        monkeypatch.setattr("msl.writer.questionary.confirm", _fail_if_called)
        generate_skill_file(ctx, force=True)
        assert output_path.read_text(encoding="utf-8") != "old content"


class _FakeConfirmNo:
    """Fake questionary.confirm that returns False."""

    def __init__(self, *args, **kwargs):
        pass

    def ask(self):
        return False


_fake_confirm_no = _FakeConfirmNo

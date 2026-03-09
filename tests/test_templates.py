from msl.models import PreferenceTier, ProjectType
from msl.templates import get_template_content, render_template


def test_render_template_replaces_placeholders():
    content = "Hello {{name}}, your project is {{project_type}}."
    result = render_template(content, {"name": "Murad", "project_type": "Flutter"})
    assert result == "Hello Murad, your project is Flutter."


def test_render_template_no_placeholders():
    content = "No placeholders here."
    result = render_template(content, {"key": "value"})
    assert result == "No placeholders here."


def test_get_template_content_flutter_simple():
    content = get_template_content(ProjectType.FLUTTER, PreferenceTier.SIMPLE)
    assert "Flutter" in content or "Dart" in content
    assert len(content) > 50


def test_get_template_content_nextjs_intermediate():
    content = get_template_content(ProjectType.NEXTJS, PreferenceTier.INTERMEDIATE)
    assert "TypeScript" in content or "Next" in content
    assert len(content) > 50


def test_get_template_content_react_vite_industry():
    content = get_template_content(ProjectType.REACT_VITE, PreferenceTier.INDUSTRY_STANDARD)
    assert len(content) > 100


def test_get_template_content_rust_server_simple():
    content = get_template_content(ProjectType.RUST_SERVER, PreferenceTier.SIMPLE)
    assert "Rust" in content
    assert len(content) > 50


def test_get_template_content_nodejs_server_industry():
    content = get_template_content(ProjectType.NODEJS_SERVER, PreferenceTier.INDUSTRY_STANDARD)
    assert len(content) > 100


def test_all_templates_loadable():
    """Every project type × tier combination must load without error."""
    for pt in ProjectType:
        for tier in PreferenceTier:
            content = get_template_content(pt, tier)
            assert isinstance(content, str)
            assert len(content) > 0

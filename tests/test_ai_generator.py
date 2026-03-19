import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
import requests

from msl.ai_generator import (
    call_deepseek,
    collect_project_context,
    build_prompt,
    generate_with_ai,
)
from msl.models import Platform, ProjectType, SkillGenContext, PreferenceTier
from msl.scanner import ProjectScan


def test_collect_project_context_reads_readme(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Hello World", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name": "test"}', encoding="utf-8")
    
    result = collect_project_context(tmp_path)
    
    assert "--- File: README.md ---" in result
    assert "# Hello World" in result
    assert "--- File: package.json ---" in result
    assert '"name": "test"' in result
    assert "pyproject.toml" not in result


def test_collect_project_context_skips_missing(tmp_path: Path):
    result = collect_project_context(tmp_path)
    assert result == ""


def test_build_prompt_contains_platform():
    ctx = SkillGenContext(
        target_platform=Platform.VSCODE,
        project_path=Path("."),
        project_type=ProjectType.PYTHON,
        preference_tier=PreferenceTier.SIMPLE,
    )
    scan = ProjectScan(frameworks=["Flask"], languages=["Python"])
    
    messages = build_prompt(ctx, scan, "File Content")
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "File Content" in messages[1]["content"]
    assert "Flask" in messages[1]["content"]
    assert "Python" in messages[1]["content"]
    assert "VS Code" in messages[1]["content"]


@patch("msl.ai_generator.requests.post")
def test_call_deepseek_returns_content(mock_post):
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "```markdown\n# Skill File\n```"}}
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    result = call_deepseek([{"role": "user", "content": "hi"}], "test-key")
    
    assert result == "# Skill File"
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["headers"]["Authorization"] == "Bearer test-key"


@patch("msl.ai_generator.requests.post")
def test_call_deepseek_raises_on_http_error(mock_post):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    mock_response.status_code = 401
    mock_response.text = "Invalid API Key"
    # Need to make response part of the exception for the parsing logic
    err = requests.exceptions.HTTPError("401 Unauthorized")
    err.response = mock_response
    mock_post.side_effect = err
    
    with pytest.raises(RuntimeError) as exc_info:
        call_deepseek([{"role": "user", "content": "hi"}], "bad-key")
        
    assert "401" in str(exc_info.value)
    assert "Invalid API Key" in str(exc_info.value)


@patch("msl.ai_generator.call_deepseek")
def test_generate_with_ai_end_to_end(mock_call_deepseek, tmp_path: Path):
    (tmp_path / "README.md").write_text("Context", encoding="utf-8")
    
    ctx = SkillGenContext(
        target_platform=Platform.CURSOR,
        project_path=tmp_path,
        project_type=ProjectType.PYTHON,
        preference_tier=PreferenceTier.SIMPLE,
    )
    scan = ProjectScan()
    
    mock_call_deepseek.return_value = "# Generated Skill"
    
    result = generate_with_ai(ctx, scan, "explicit-key")
    
    assert result == "# Generated Skill"
    mock_call_deepseek.assert_called_once()
    # Check that messages passed to call_deepseek contain the context
    messages = mock_call_deepseek.call_args[0][0]
    api_key = mock_call_deepseek.call_args[0][1]
    
    assert api_key == "explicit-key"
    assert "Context" in messages[1]["content"]

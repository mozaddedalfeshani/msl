from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import requests

from .models import Platform, ProjectType, SkillGenContext
from .scanner import ProjectScan

# Max bytes to read from any single file to prevent exploding prompts
MAX_FILE_BYTES = 8192

# The URL for the DeepSeek chat completions API
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def _read_env_file(project_root: Path) -> dict[str, str]:
    """Basic .env parser to avoid adding python-dotenv dependency."""
    env_path = project_root / ".env"
    result = {}
    if not env_path.is_file():
        return result

    try:
        content = env_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                result[key.strip()] = val.strip().strip("'\"")
    except OSError:
        pass
    return result


def resolve_api_key(project_root: Path, explicit_key: Optional[str] = None) -> str:
    """Resolve DeepSeek API key (explicit flag > os env > .env file)."""
    if explicit_key:
        return explicit_key

    env_val = os.environ.get("DEEPSEEK_API")
    if env_val:
        return env_val

    env_file_vars = _read_env_file(project_root)
    file_val = env_file_vars.get("DEEPSEEK_API")
    if file_val:
        return file_val

    raise ValueError(
        "Could not find DEEPSEEK_API key. Please provide it via the --ai-key flag, "
        "export it as DEEPSEEK_API in your terminal, or place it in a .env file."
    )


def collect_project_context(project_root: Path) -> str:
    """Read interesting files from the project to send to the LLM."""
    interesting_files = [
        "README.md",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "Cargo.toml",
        "go.mod",
        "pubspec.yaml",
    ]

    context_parts = []
    
    for filename in interesting_files:
        path = project_root / filename
        if not path.is_file():
            continue
            
        try:
            # Read only up to MAX_FILE_BYTES to keep context window manageable
            with path.open("r", encoding="utf-8") as f:
                content = f.read(MAX_FILE_BYTES)
                if len(content) == MAX_FILE_BYTES:
                    content += "\n... (truncated)"
            
            context_parts.append(f"--- File: {filename} ---\n{content}\n")
        except OSError:
            pass

    return "\n".join(context_parts)


def build_prompt(ctx: SkillGenContext, scan: ProjectScan, project_files_text: str) -> list[dict[str, str]]:
    """Build the ChatML prompt for DeepSeek."""
    
    system_prompt = (
        "You are an expert software developer and architect. "
        "Your task is to write a highly detailed, industry-standard set of coding rules and instructions "
        "for an AI coding assistant. The output MUST be formatted as a single Markdown file."
    )
    
    # Start building the user context message
    user_prompt = []
    
    user_prompt.append(
        f"Generate a customized AI skill file ({ctx.target_platform.display_name}) for my project."
    )
    user_prompt.append(f"Project Type: {ctx.project_type.display_name}")
    user_prompt.append(f"Preference Level: {ctx.preference_tier.display_name}")
    
    if scan.frameworks:
        user_prompt.append(f"Detected Stack: {', '.join(scan.frameworks)}")
    
    if scan.languages:
        user_prompt.append(f"Languages: {', '.join(scan.languages)}")
        
    user_prompt.append("\nHere is the raw context from the project files:\n")
    if project_files_text.strip():
        user_prompt.append(project_files_text)
    else:
        user_prompt.append("(No relevant project definition files found.)\n")
        
    user_prompt.append(
        "\nINSTRUCTIONS:\n"
        "1. Write a comprehensive, industry-standard skill file in Markdown format.\n"
        "2. Address code style, architecture, data fetching, state management, testing, and security.\n"
        "3. Tailor the advice *specifically* to the frameworks, libraries, and languages detected in the files above.\n"
        "4. DO NOT output any conversation, explanations, or greeting. Output ONLY the raw Markdown content.\n"
        "5. DO NOT wrap the output in ```markdown blocks if it's the entire response."
    )
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n".join(user_prompt)}
    ]


def call_deepseek(messages: list[dict[str, str]], api_key: str) -> str:
    """Execute the HTTP POST strictly to DeepSeek API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.2, # Low temperature for consistent rule generation
        "max_tokens": 4096,
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        content = data["choices"][0]["message"]["content"]
        
        # Cleanup potential markdown wrapper block if the model ignores instruction #5
        content = content.strip()
        if content.startswith("```markdown"):
            content = content[len("```markdown"):].strip()
        if content.startswith("```"):
            content = content[3:].strip()
        if content.endswith("```"):
            content = content[:-3].strip()
            
        return content
    except requests.exceptions.RequestException as e:
        status_info = ""
        if hasattr(e, "response") and e.response is not None:
             status_info = f" ({e.response.status_code}: {e.response.text})"
        raise RuntimeError(f"DeepSeek API call failed: {e}{status_info}")
    except (KeyError, IndexError, ValueError) as e:
        raise RuntimeError(f"Failed to parse DeepSeek response: {e}")


def generate_with_ai(
    ctx: SkillGenContext, 
    scan: ProjectScan, 
    explicit_api_key: Optional[str] = None
) -> str:
    """Orchestrates reading context, prompting DeepSeek, and returning the customized markdown."""
    api_key = resolve_api_key(ctx.project_path, explicit_api_key)
    project_files_text = collect_project_context(ctx.project_path)
    messages = build_prompt(ctx, scan, project_files_text)
    
    markdown_content = call_deepseek(messages, api_key)
    return markdown_content

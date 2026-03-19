import json
import os
from pathlib import Path

from rich.console import Console

console = Console()

MSL_AUTH_URL = os.environ.get("MSL_API_URL", "http://localhost:3000")
CREDENTIALS_FILE = Path.home() / ".msl" / "credentials.json"

def get_access_token() -> str | None:
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text())
        return data.get("accessToken")
    except Exception:
        return None

def msl_login(token: str) -> None:
    try:
        if not token or len(token) < 16:
            console.print("[red]Invalid token format. Please provide a valid MSL API Token.[/red]")
            return

        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        console.print("[cyan]Saving MSL API Key...[/cyan]")
        
        CREDENTIALS_FILE.write_text(json.dumps({
            "accessToken": token,
        }))
        console.print("[bold green]✓ Successfully authenticated with MSL API![/bold green]")
            
    except Exception as e:
        console.print(f"[red]Authentication failed: {e}[/red]")

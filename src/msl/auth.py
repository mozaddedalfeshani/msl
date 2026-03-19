import json
import os
import time
from pathlib import Path

import requests
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

def msl_login() -> None:
    try:
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        console.print("[cyan]Initiating MSL login...[/cyan]")
        
        # Request Device Code
        url = f"{MSL_AUTH_URL.rstrip('/')}/api/auth/device-code"
        res = requests.post(url, json={"deviceName": "MSL CLI"}, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        device_code = data["deviceCode"]
        verification_uri = data["verificationUriComplete"]
        
        console.print("\n[bold green]Please open this URL in your browser to approve the login:[/bold green]")
        console.print(f"[bold blue]{verification_uri}[/bold blue]\n")
        
        with console.status("[cyan]Waiting for your approval in the browser... (timeout in 5 minutes)[/cyan]", spinner="dots"):
            for _ in range(100):
                time.sleep(3)
                status_url = f"{MSL_AUTH_URL.rstrip('/')}/api/auth/device-status?deviceCode={device_code}"
                try:
                    status_res = requests.get(status_url, timeout=10)
                    if status_res.status_code == 200:
                        sdata = status_res.json()
                        if sdata.get("status") == "approved":
                            CREDENTIALS_FILE.write_text(json.dumps({
                                "accessToken": sdata["accessToken"],
                                "refreshToken": sdata["refreshToken"]
                            }))
                            console.print("[bold green]✓ Successfully logged in![/bold green]")
                            return
                except requests.exceptions.RequestException:
                    pass # ignore intermittent network errors
                    
        console.print("[red]Login request timed out. Please try again.[/red]")
            
    except Exception as e:
        console.print(f"[red]Login failed: {e}[/red]")

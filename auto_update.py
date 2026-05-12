#!/usr/bin/env python3
"""
Doureios Ippos — Auto-Update Module
Ελέγχει και εγκαθιστά ενημερώσεις από GitHub αυτόματα
"""

import subprocess
import threading
import datetime
import json
from pathlib import Path

GITHUB_REPO = "https://github.com/Jimmoleon7/doureios-ippos.git"
UPDATE_CHECK_FILE = Path.home() / ".doureios_ippos" / "last_update_check.json"

# ── Colors ──
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
C = "\033[96m"
D = "\033[2m"
B = "\033[1m"
X = "\033[0m"


def get_install_dir() -> Path:
    """Find installation directory"""
    candidates = [
        Path(__file__).parent,
        Path.home() / "doureios-ippos",
        Path.home() / "Downloads" / "doureios_ippos",
    ]
    for p in candidates:
        if (p / ".git").exists():
            return p
    return Path(__file__).parent


def should_check_update() -> bool:
    """Check if enough time has passed since last update check (24 hours)"""
    try:
        if not UPDATE_CHECK_FILE.exists():
            return True
        data = json.loads(UPDATE_CHECK_FILE.read_text())
        last = datetime.datetime.fromisoformat(data.get("last_check", "2000-01-01"))
        diff = datetime.datetime.now() - last
        return diff.total_seconds() > 86400  # 24 hours
    except Exception:
        return True


def save_check_time():
    """Save current time as last check time"""
    try:
        UPDATE_CHECK_FILE.parent.mkdir(parents=True, exist_ok=True)
        UPDATE_CHECK_FILE.write_text(json.dumps({
            "last_check": datetime.datetime.now().isoformat()
        }))
    except Exception:
        pass


def get_current_version() -> str:
    """Get current git commit hash"""
    try:
        install_dir = get_install_dir()
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=install_dir, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def check_for_updates(silent=False) -> dict:
    """
    Check if updates are available.
    Returns: {available: bool, commits_behind: int, message: str}
    """
    install_dir = get_install_dir()

    if not (install_dir / ".git").exists():
        return {"available": False, "commits_behind": 0, "message": "No git repository found"}

    try:
        # Fetch without merging
        subprocess.run(
            ["git", "fetch", "origin", "--quiet"],
            cwd=install_dir, capture_output=True, timeout=10
        )

        # Count commits behind
        result = subprocess.run(
            ["git", "rev-list", "HEAD..origin/master", "--count"],
            cwd=install_dir, capture_output=True, text=True, timeout=5
        )
        behind = int(result.stdout.strip() or "0")

        # Get latest commit message
        msg_result = subprocess.run(
            ["git", "log", "origin/master", "-1", "--pretty=%s"],
            cwd=install_dir, capture_output=True, text=True, timeout=5
        )
        latest_msg = msg_result.stdout.strip()

        save_check_time()

        if behind > 0:
            return {
                "available": True,
                "commits_behind": behind,
                "message": latest_msg,
                "current": get_current_version(),
            }
        return {"available": False, "commits_behind": 0, "message": "Already up to date"}

    except subprocess.TimeoutExpired:
        return {"available": False, "commits_behind": 0, "message": "Timeout checking updates"}
    except FileNotFoundError:
        return {"available": False, "commits_behind": 0, "message": "Git not found"}
    except Exception as e:
        return {"available": False, "commits_behind": 0, "message": str(e)}


def perform_update() -> dict:
    """
    Perform the actual update (git pull).
    Returns: {success: bool, message: str}
    """
    install_dir = get_install_dir()

    try:
        result = subprocess.run(
            ["git", "pull", "origin", "master"],
            cwd=install_dir, capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            new_version = get_current_version()
            return {
                "success": True,
                "message": f"Ενημέρωση επιτυχής! Νέα έκδοση: {new_version}",
                "output": result.stdout,
            }
        else:
            return {
                "success": False,
                "message": f"Σφάλμα ενημέρωσης: {result.stderr}",
            }
    except Exception as e:
        return {"success": False, "message": str(e)}


def check_update_background(callback=None):
    """
    Check for updates in background thread.
    Calls callback(result) when done.
    """
    def _check():
        if not should_check_update():
            return
        result = check_for_updates(silent=True)
        if callback and result.get("available"):
            callback(result)

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def print_update_banner(result: dict):
    """Print update notification banner"""
    print(f"\n{Y}{'─'*50}{X}")
    print(f"{Y}🔔 Υπάρχει νέα έκδοση! ({result['commits_behind']} αλλαγές){X}")
    print(f"{C}   {result['message']}{X}")
    print(f"{D}   Τρέξε: drip --update{X}")
    print(f"{Y}{'─'*50}{X}\n")


if __name__ == "__main__":
    print("Checking for updates...")
    result = check_for_updates()
    print(result)
    if result["available"]:
        print_update_banner(result)
        ans = input("Θέλεις να ενημερωθεί τώρα; (ΝΑΙ/όχι): ").strip().upper()
        if ans in ("ΝΑΙ", "NAI", "YES", "Y"):
            update_result = perform_update()
            if update_result["success"]:
                print(f"{G}✓ {update_result['message']}{X}")
            else:
                print(f"{R}✗ {update_result['message']}{X}")

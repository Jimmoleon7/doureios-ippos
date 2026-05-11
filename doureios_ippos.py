#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ  —  DOUREIOS IPPOS                 ║
║        AI-Powered Ethical Hacking Assistant v1.0             ║
║   Ελληνικά & English  |  Authorized Pentesting Only          ║
╚══════════════════════════════════════════════════════════════╝
"""

import subprocess
import sys
import os
import json
import datetime
import re
import shutil
import readline
from pathlib import Path

# ──────────────────────────────────────────────
#  COLOR PALETTE
# ──────────────────────────────────────────────
class C:
    GOLD    = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"

# ──────────────────────────────────────────────
#  BANNER
# ──────────────────────────────────────────────
BANNER = f"""
{C.GOLD}{C.BOLD}
     ╔═══════════════════════════════════════════════════════╗
     ║                                                       ║
     ║   🐴  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ  ·  DOUREIOS IPPOS  🐴          ║
     ║         Ethical Hacking AI Assistant v1.0             ║
     ║                                                       ║
     ╠═══════════════════════════════════════════════════════╣
     ║  {C.CYAN}Εντολές σε φυσική γλώσσα  ·  Ελληνικά & English  {C.GOLD}  ║
     ║  {C.BLUE}⚠  Μόνο για εξουσιοδοτημένα συστήματα / labs      {C.GOLD}  ║
     ╚═══════════════════════════════════════════════════════╝
{C.RESET}"""

DISCLAIMER = f"""
{C.RED}{C.BOLD}[ ΝΟΜΙΚΗ ΔΗΛΩΣΗ / LEGAL DISCLAIMER ]{C.RESET}
{C.WHITE}Το Doureios Ippos προορίζεται ΑΠΟΚΛΕΙΣΤΙΚΑ για:{C.RESET}
{C.GREEN}  ✓  Authorized penetration testing (με γραπτή άδεια){C.RESET}
{C.GREEN}  ✓  CTF competitions & security labs{C.RESET}
{C.GREEN}  ✓  Δικά σου συστήματα / δίκτυα{C.RESET}
{C.GREEN}  ✓  Εκπαιδευτικούς σκοπούς σε isolated περιβάλλον{C.RESET}
{C.RED}  ✗  Μη εξουσιοδοτημένη πρόσβαση = ΠΑΡΑΝΟΜΟ (Ν.4411/2016){C.RESET}

{C.GOLD}Πληκτρολόγησε {C.BOLD}ΑΠΟΔΕΧΟΜΑΙ{C.RESET}{C.GOLD} ή {C.BOLD}ACCEPT{C.RESET}{C.GOLD} για να συνεχίσεις.{C.RESET}
"""

# ──────────────────────────────────────────────
#  TOOL REGISTRY  — ποια εργαλεία είναι installed
# ──────────────────────────────────────────────
TOOLS = {
    "nmap":       {"cmd": "nmap",       "desc": "Network scanner / port discovery"},
    "hydra":      {"cmd": "hydra",      "desc": "Network login brute-forcer"},
    "john":       {"cmd": "john",       "desc": "Password hash cracker (John the Ripper)"},
    "hashcat":    {"cmd": "hashcat",    "desc": "GPU-accelerated hash cracker"},
    "nikto":      {"cmd": "nikto",      "desc": "Web server vulnerability scanner"},
    "sqlmap":     {"cmd": "sqlmap",     "desc": "SQL injection tester"},
    "gobuster":   {"cmd": "gobuster",   "desc": "Directory/DNS brute-forcer"},
    "dirb":       {"cmd": "dirb",       "desc": "Web content scanner"},
    "wireshark":  {"cmd": "wireshark",  "desc": "GUI packet analyzer"},
    "tcpdump":    {"cmd": "tcpdump",    "desc": "CLI packet capture"},
    "tshark":     {"cmd": "tshark",     "desc": "CLI Wireshark"},
    "metasploit": {"cmd": "msfconsole","desc": "Exploitation framework"},
    "msfvenom":   {"cmd": "msfvenom",  "desc": "Payload generator"},
    "aircrack-ng":{"cmd": "aircrack-ng","desc":"WiFi WPA/WEP cracker"},
    "airmon-ng":  {"cmd": "airmon-ng", "desc": "WiFi monitor mode"},
    "netdiscover":{"cmd": "netdiscover","desc":"ARP network scanner"},
    "whois":      {"cmd": "whois",      "desc": "Domain info lookup"},
    "dig":        {"cmd": "dig",        "desc": "DNS query tool"},
    "curl":       {"cmd": "curl",       "desc": "HTTP request tool"},
    "wget":       {"cmd": "wget",       "desc": "File downloader"},
    "openssl":    {"cmd": "openssl",    "desc": "SSL/TLS toolkit"},
    "nc":         {"cmd": "nc",         "desc": "Netcat — network swiss army knife"},
    "enum4linux": {"cmd": "enum4linux", "desc": "SMB/Samba enumeration"},
    "smbclient":  {"cmd": "smbclient",  "desc": "SMB client"},
    "ssh":        {"cmd": "ssh",        "desc": "Secure Shell"},
    "ftp":        {"cmd": "ftp",        "desc": "FTP client"},
}

# ──────────────────────────────────────────────
#  INTENT PARSER  — αναγνωρίζει τι θέλει ο χρήστης
# ──────────────────────────────────────────────
INTENTS = [
    # (patterns_el, patterns_en, action_key)
    (["σκαν", "σάρωσε", "ψάξε δίκτυ", "βρες host", "ανακάλυψε"],
     ["scan", "discover", "find hosts", "network scan", "port scan"],
     "nmap_scan"),

    (["ευάλωτ", "vulnerability", "cve", "αδυναμί"],
     ["vuln", "vulnerability", "weak", "exploit"],
     "vuln_scan"),

    (["web", "http", "ιστοσελίδ", "site", "nikto", "gobuster", "dir"],
     ["web scan", "website", "http", "directory"],
     "web_scan"),

    (["sql", "injection", "sqlmap", "βάση δεδομένων"],
     ["sql", "injection", "database"],
     "sql_inject"),

    (["κωδικ", "hash", "john", "hydra", "brute", "password", "pass"],
     ["crack", "brute force", "password", "hash"],
     "password_attack"),

    (["wifi", "wireless", "ασύρματ", "wpa", "wep", "handshake", "aircrack"],
     ["wifi", "wireless", "wpa", "wep", "aircrack"],
     "wifi_attack"),

    (["packet", "πακέτ", "wireshark", "tcpdump", "sniff", "traffic", "κυκλοφορί"],
     ["capture", "sniff", "packet", "traffic", "wireshark"],
     "packet_capture"),

    (["dns", "domain", "whois", "subdomain", "υποτομέ"],
     ["dns", "domain", "whois", "subdomain"],
     "recon_dns"),

    (["smb", "samba", "share", "windows", "enum4linux"],
     ["smb", "samba", "windows share"],
     "smb_enum"),

    (["εργαλεί", "tools", "τι μπορείς", "βοήθεια", "help", "commands"],
     ["help", "tools", "what can", "commands", "list"],
     "show_help"),

    (["έξοδος", "bye", "quit", "exit", "αποχώρηση", "τέλος"],
     ["exit", "quit", "bye", "goodbye"],
     "exit"),

    (["install", "εγκατάστη", "update", "ενημέρωσε"],
     ["install", "update", "upgrade"],
     "install_tool"),
]

# ──────────────────────────────────────────────
#  LOGGER
# ──────────────────────────────────────────────
LOG_DIR = Path.home() / ".doureios_ippos" / "logs"

def init_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(action: str, cmd: str, output: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"{datetime.date.today()}.log"
    with open(log_file, "a") as f:
        f.write(f"[{ts}] ACTION={action}\n")
        f.write(f"  CMD: {cmd}\n")
        f.write(f"  OUT: {output[:500]}\n\n")

# ──────────────────────────────────────────────
#  TOOL CHECKER
# ──────────────────────────────────────────────
def check_tools() -> dict:
    available = {}
    for name, info in TOOLS.items():
        available[name] = shutil.which(info["cmd"]) is not None
    return available

def print_tool_status(available: dict):
    print(f"\n{C.GOLD}{C.BOLD}[ Διαθέσιμα Εργαλεία / Available Tools ]{C.RESET}\n")
    cols = 3
    items = list(available.items())
    for i in range(0, len(items), cols):
        row = items[i:i+cols]
        line = ""
        for name, ok in row:
            status = f"{C.GREEN}✓{C.RESET}" if ok else f"{C.RED}✗{C.RESET}"
            line += f"  {status} {C.WHITE}{name:<14}{C.RESET}"
        print(line)
    missing = [n for n, ok in available.items() if not ok]
    if missing:
        print(f"\n{C.YELLOW if hasattr(C,'YELLOW') else C.GOLD}Tip: Εγκατάστησε τα ελλείποντα με:{C.RESET}")
        print(f"{C.GRAY}  sudo apt install {' '.join(missing[:5])}  (Kali/Debian){C.RESET}\n")

# ──────────────────────────────────────────────
#  INTENT DETECTION
# ──────────────────────────────────────────────
def detect_intent(text: str) -> str:
    t = text.lower()
    for el_patterns, en_patterns, action in INTENTS:
        for p in el_patterns + en_patterns:
            if p in t:
                return action
    return "unknown"

# ──────────────────────────────────────────────
#  TARGET EXTRACTOR
# ──────────────────────────────────────────────
def extract_target(text: str) -> str:
    ip_re = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2})?)\b")
    dom_re = re.compile(r"\b([a-zA-Z0-9][-a-zA-Z0-9.]+\.[a-zA-Z]{2,})\b")
    m = ip_re.search(text)
    if m:
        return m.group(1)
    m = dom_re.search(text)
    if m and m.group(1) not in ("the", "and", "for"):
        return m.group(1)
    return ""

# ──────────────────────────────────────────────
#  COMMAND RUNNER  — με live output
# ──────────────────────────────────────────────
def run_command(cmd: list, timeout: int = 300) -> str:
    print(f"\n{C.GRAY}[CMD] {' '.join(cmd)}{C.RESET}\n")
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        output = []
        for line in proc.stdout:
            print(f"{C.DIM}{line}{C.RESET}", end="")
            output.append(line)
        proc.wait(timeout=timeout)
        return "".join(output)
    except FileNotFoundError:
        return f"[✗] Το εργαλείο '{cmd[0]}' δεν βρέθηκε. Εγκατάστησέ το πρώτα."
    except subprocess.TimeoutExpired:
        proc.kill()
        return "[!] Timeout — η εντολή διακόπηκε."
    except KeyboardInterrupt:
        proc.kill()
        print(f"\n{C.RED}[!] Διακόπηκε από τον χρήστη.{C.RESET}")
        return "[!] Interrupted by user."

# ──────────────────────────────────────────────
#  CONSENT CHECK
# ──────────────────────────────────────────────
def require_consent(target: str, action_desc: str) -> bool:
    print(f"\n{C.RED}{C.BOLD}⚠  ΕΠΙΒΕΒΑΙΩΣΗ ΕΞΟΥΣΙΟΔΟΤΗΣΗΣ{C.RESET}")
    print(f"{C.WHITE}Στόχος   : {C.GOLD}{target}{C.RESET}")
    print(f"{C.WHITE}Ενέργεια : {C.CYAN}{action_desc}{C.RESET}")
    print(f"\n{C.WHITE}Έχεις εξουσιοδότηση για αυτό το σύστημα;")
    print(f"Πληκτρολόγησε {C.BOLD}ΝΑΙ / YES{C.RESET}{C.WHITE} για να συνεχίσεις ή οτιδήποτε άλλο για ακύρωση:{C.RESET} ", end="")
    resp = input().strip().upper()
    return resp in ("ΝΑΙ", "NAI", "YES", "Y", "Ν", "N̈")

# ──────────────────────────────────────────────
#  ACTION HANDLERS
# ──────────────────────────────────────────────

def handle_nmap_scan(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δεν βρήκα στόχο. Δώσε μου IP ή hostname.")
        print(f"   π.χ. «σκάναρε το 192.168.1.0/24»")
        return

    if not available.get("nmap"):
        print(f"\n{C.RED}[✗] Το nmap δεν είναι εγκατεστημένο.{C.RESET}")
        print(f"{C.GRAY}    sudo apt install nmap{C.RESET}")
        return

    # Επιλογή τύπου σάρωσης
    print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Τι είδους σάρωση θέλεις;")
    print(f"  {C.CYAN}1{C.RESET} — Γρήγορη (top 100 ports)")
    print(f"  {C.CYAN}2{C.RESET} — Κανονική (top 1000 ports + service detection)")
    print(f"  {C.CYAN}3{C.RESET} — Πλήρης (όλα τα ports + OS detection)")
    print(f"  {C.CYAN}4{C.RESET} — Vulnerability scan (nmap + vuln scripts)")
    print(f"\n{C.GOLD}Επιλογή [1-4]:{C.RESET} ", end="")
    choice = input().strip()

    if not require_consent(target, "Nmap port scan"):
        print(f"\n{C.RED}[✗] Ακυρώθηκε — δεν έχεις άδεια.{C.RESET}")
        return

    cmd_map = {
        "1": ["nmap", "-F", "--open", target],
        "2": ["nmap", "-sV", "-sC", "--open", target],
        "3": ["nmap", "-sV", "-sC", "-O", "-p-", "--open", target],
        "4": ["nmap", "-sV", "--script=vuln", target],
    }
    cmd = cmd_map.get(choice, cmd_map["2"])

    print(f"\n{C.GOLD}🐴 Ξεκινώ σάρωση στο {C.BOLD}{target}{C.RESET}{C.GOLD}...{C.RESET}\n")
    out = run_command(cmd)
    log("nmap_scan", " ".join(cmd), out)
    print(f"\n{C.GREEN}[✓] Σάρωση ολοκληρώθηκε. Αποθηκεύτηκε στα logs.{C.RESET}")


def handle_vuln_scan(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δεν βρήκα στόχο. Δώσε IP/hostname.")
        return
    if not available.get("nmap"):
        print(f"{C.RED}[✗] nmap δεν βρέθηκε.{C.RESET}")
        return
    if not require_consent(target, "Vulnerability scan (nmap vuln scripts)"):
        print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
        return
    cmd = ["nmap", "-sV", "--script=vuln,exploit,auth,default", "--open", target]
    print(f"\n{C.GOLD}🐴 Τρέχω vulnerability scan στο {target}...{C.RESET}\n")
    out = run_command(cmd)
    log("vuln_scan", " ".join(cmd), out)


def handle_web_scan(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δώσε μου URL ή IP για web scanning.")
        return

    print(f"\n{C.GOLD}🐴 Τι θέλεις να κάνω στο {target};{C.RESET}")
    print(f"  {C.CYAN}1{C.RESET} — Nikto (web vulnerability scan)")
    print(f"  {C.CYAN}2{C.RESET} — Gobuster (directory brute-force)")
    print(f"  {C.CYAN}3{C.RESET} — Και τα δύο")
    print(f"\n{C.GOLD}Επιλογή [1-3]:{C.RESET} ", end="")
    choice = input().strip()

    if not require_consent(target, "Web scanning"):
        print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
        return

    url = target if target.startswith("http") else f"http://{target}"

    if choice in ("1", "3") and available.get("nikto"):
        cmd = ["nikto", "-h", url]
        print(f"\n{C.GOLD}🐴 Τρέχω Nikto...{C.RESET}\n")
        out = run_command(cmd)
        log("nikto", " ".join(cmd), out)

    if choice in ("2", "3") and available.get("gobuster"):
        wordlist = "/usr/share/wordlists/dirb/common.txt"
        if not Path(wordlist).exists():
            wordlist = "/usr/share/dirb/wordlists/common.txt"
        cmd = ["gobuster", "dir", "-u", url, "-w", wordlist, "-t", "50"]
        print(f"\n{C.GOLD}🐴 Τρέχω Gobuster...{C.RESET}\n")
        out = run_command(cmd)
        log("gobuster", " ".join(cmd), out)


def handle_sql_inject(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δώσε URL με παράμετρο π.χ. http://site.com/page?id=1")
        return
    if not available.get("sqlmap"):
        print(f"{C.RED}[✗] sqlmap δεν βρέθηκε. sudo apt install sqlmap{C.RESET}")
        return
    if not require_consent(target, "SQL injection testing (sqlmap)"):
        print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
        return
    url = target if target.startswith("http") else f"http://{target}"
    cmd = ["sqlmap", "-u", url, "--batch", "--level=2", "--risk=1", "--dbs"]
    print(f"\n{C.GOLD}🐴 Ξεκινώ SQL injection test...{C.RESET}\n")
    out = run_command(cmd)
    log("sqlmap", " ".join(cmd), out)


def handle_password_attack(text: str, available: dict):
    t = text.lower()
    print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Τι θέλεις;")
    print(f"  {C.CYAN}1{C.RESET} — Hash cracking (John the Ripper)")
    print(f"  {C.CYAN}2{C.RESET} — Network login brute-force (Hydra)")
    print(f"\n{C.GOLD}Επιλογή [1-2]:{C.RESET} ", end="")
    choice = input().strip()

    if choice == "1":
        if not available.get("john"):
            print(f"{C.RED}[✗] john δεν βρέθηκε.{C.RESET}")
            return
        print(f"\n{C.WHITE}Δώσε path προς το αρχείο hash:{C.RESET} ", end="")
        hash_file = input().strip()
        if not Path(hash_file).exists():
            print(f"{C.RED}[✗] Το αρχείο δεν υπάρχει.{C.RESET}")
            return
        wordlist = "/usr/share/wordlists/rockyou.txt"
        cmd = ["john", hash_file, f"--wordlist={wordlist}"]
        print(f"\n{C.GOLD}🐴 Ξεκινώ cracking με rockyou.txt...{C.RESET}\n")
        out = run_command(cmd, timeout=600)
        log("john", " ".join(cmd), out)

    elif choice == "2":
        if not available.get("hydra"):
            print(f"{C.RED}[✗] hydra δεν βρέθηκε.{C.RESET}")
            return
        print(f"\n{C.WHITE}Target IP/host:{C.RESET} ", end="")
        host = input().strip()
        print(f"{C.WHITE}Πρωτόκολλο (ssh/ftp/http-post-form/smb):{C.RESET} ", end="")
        proto = input().strip()
        print(f"{C.WHITE}Username ή αρχείο users:{C.RESET} ", end="")
        user = input().strip()
        wordlist = "/usr/share/wordlists/rockyou.txt"
        if not require_consent(host, f"Hydra brute-force ({proto})"):
            print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
            return
        user_arg = ["-l", user] if not Path(user).exists() else ["-L", user]
        cmd = ["hydra"] + user_arg + ["-P", wordlist, host, proto, "-t", "16", "-V"]
        print(f"\n{C.GOLD}🐴 Ξεκινώ Hydra...{C.RESET}\n")
        out = run_command(cmd, timeout=600)
        log("hydra", " ".join(cmd), out)


def handle_wifi_attack(text: str, available: dict):
    print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} WiFi pentesting — {C.BOLD}ΜΟΝΟ σε δικά σου δίκτυα / authorized{C.RESET}")
    if not available.get("aircrack-ng"):
        print(f"{C.RED}[✗] aircrack-ng δεν βρέθηκε. sudo apt install aircrack-ng{C.RESET}")
        return
    print(f"\n  {C.CYAN}1{C.RESET} — Crack WPA handshake (έχεις ήδη .cap αρχείο)")
    print(f"  {C.CYAN}2{C.RESET} — Οδηγίες για capture handshake")
    print(f"\n{C.GOLD}Επιλογή [1-2]:{C.RESET} ", end="")
    choice = input().strip()

    if choice == "1":
        print(f"\n{C.WHITE}Path προς .cap αρχείο:{C.RESET} ", end="")
        cap = input().strip()
        wordlist = "/usr/share/wordlists/rockyou.txt"
        if not require_consent(cap, "WPA handshake cracking"):
            print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
            return
        cmd = ["aircrack-ng", "-w", wordlist, cap]
        print(f"\n{C.GOLD}🐴 Ξεκινώ cracking...{C.RESET}\n")
        out = run_command(cmd, timeout=1200)
        log("aircrack-ng", " ".join(cmd), out)

    elif choice == "2":
        print(f"""
{C.CYAN}── Βήματα για WiFi Handshake Capture ──{C.RESET}

{C.GOLD}1.{C.RESET} Βάλε την κάρτα σε monitor mode:
   {C.GRAY}sudo airmon-ng start wlan0{C.RESET}

{C.GOLD}2.{C.RESET} Σάρωσε για δίκτυα:
   {C.GRAY}sudo airodump-ng wlan0mon{C.RESET}

{C.GOLD}3.{C.RESET} Capture handshake (αντικατάστησε BSSID/CH):
   {C.GRAY}sudo airodump-ng -c <CH> --bssid <BSSID> -w capture wlan0mon{C.RESET}

{C.GOLD}4.{C.RESET} Deauth (σε άλλο terminal, επιταχύνει handshake):
   {C.GRAY}sudo aireplay-ng --deauth 5 -a <BSSID> wlan0mon{C.RESET}

{C.GOLD}5.{C.RESET} Crack:
   {C.GRAY}aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap{C.RESET}
""")


def handle_packet_capture(text: str, available: dict):
    if not available.get("tcpdump") and not available.get("tshark"):
        print(f"{C.RED}[✗] Δεν βρέθηκε tcpdump ή tshark.{C.RESET}")
        return
    print(f"\n{C.WHITE}Interface (π.χ. eth0, wlan0, any):{C.RESET} ", end="")
    iface = input().strip() or "any"
    print(f"{C.WHITE}Filter BPF (π.χ. 'port 80', '' για όλα):{C.RESET} ", end="")
    bpf = input().strip()
    print(f"{C.WHITE}Αριθμός πακέτων [50]:{C.RESET} ", end="")
    count = input().strip() or "50"

    if not require_consent(iface, f"Packet capture ({iface})"):
        print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
        return

    out_file = f"/tmp/capture_{datetime.datetime.now().strftime('%H%M%S')}.pcap"
    if available.get("tcpdump"):
        cmd = ["sudo", "tcpdump", "-i", iface, "-c", count, "-w", out_file]
        if bpf:
            cmd += bpf.split()
    else:
        cmd = ["sudo", "tshark", "-i", iface, "-c", count, "-w", out_file]

    print(f"\n{C.GOLD}🐴 Καταγράφω πακέτα → {out_file}{C.RESET}\n")
    out = run_command(cmd, timeout=60)
    log("packet_capture", " ".join(cmd), out)
    print(f"\n{C.GREEN}[✓] Αποθηκεύτηκε: {out_file}{C.RESET}")
    if available.get("wireshark"):
        print(f"{C.CYAN}Tip: Άνοιξέ το με: wireshark {out_file}{C.RESET}")


def handle_recon_dns(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δώσε domain π.χ. example.com")
        return
    print(f"\n{C.GOLD}🐴 Ξεκινώ DNS reconnaissance για {target}...{C.RESET}\n")

    if available.get("whois"):
        print(f"{C.CYAN}── WHOIS ──{C.RESET}")
        run_command(["whois", target])

    if available.get("dig"):
        print(f"\n{C.CYAN}── DNS Records ──{C.RESET}")
        for rtype in ["A", "MX", "NS", "TXT", "AAAA"]:
            print(f"\n{C.GRAY}[{rtype}]{C.RESET}")
            run_command(["dig", target, rtype, "+short"])


def handle_smb_enum(text: str, available: dict):
    target = extract_target(text)
    if not target:
        print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δώσε IP του Windows/Samba host.")
        return
    if not require_consent(target, "SMB enumeration"):
        print(f"{C.RED}[✗] Ακυρώθηκε.{C.RESET}")
        return
    if available.get("enum4linux"):
        print(f"\n{C.GOLD}🐴 Τρέχω enum4linux...{C.RESET}\n")
        out = run_command(["enum4linux", "-a", target])
        log("enum4linux", f"enum4linux -a {target}", out)
    elif available.get("nmap"):
        print(f"\n{C.GOLD}🐴 Τρέχω nmap SMB scripts...{C.RESET}\n")
        out = run_command(["nmap", "-p", "139,445", "--script=smb-enum-shares,smb-vuln-ms17-010", target])
        log("smb_nmap", f"nmap smb {target}", out)


def handle_install_tool(text: str):
    print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Ανανεώνω και εγκαθιστώ εργαλεία...\n")
    cmds = [
        ["sudo", "apt", "update", "-qq"],
        ["sudo", "apt", "install", "-y",
         "nmap", "hydra", "john", "nikto", "sqlmap",
         "gobuster", "dirb", "tshark", "tcpdump",
         "aircrack-ng", "netdiscover", "enum4linux",
         "whois", "dnsutils", "netcat-openbsd"]
    ]
    for cmd in cmds:
        print(f"{C.GRAY}[CMD] {' '.join(cmd)}{C.RESET}")
        subprocess.run(cmd)
    print(f"\n{C.GREEN}[✓] Εγκατάσταση ολοκληρώθηκε!{C.RESET}")


def show_help(available: dict):
    print(f"""
{C.GOLD}{C.BOLD}══════════════════════════════════════════════{C.RESET}
{C.GOLD}{C.BOLD}  🐴  Τι μπορώ να κάνω για σένα;{C.RESET}
{C.GOLD}{C.BOLD}══════════════════════════════════════════════{C.RESET}

{C.CYAN}[ NETWORK SCANNING ]{C.RESET}
  • «σκάναρε το 192.168.1.0/24»
  • «βρες ανοιχτές πόρτες στο 10.0.0.1»
  • «κάνε vulnerability scan στο 192.168.1.5»

{C.CYAN}[ WEB TESTING ]{C.RESET}
  • «κάνε web scan στο http://testsite.local»
  • «ψάξε directories στο 192.168.1.10»
  • «τρέξε sqlmap στο http://site.com?id=1»

{C.CYAN}[ PASSWORD ATTACKS ]{C.RESET}
  • «σπάσε το hash από το αρχείο hashes.txt»
  • «brute force ssh στο 192.168.1.5»

{C.CYAN}[ WIFI PENTESTING ]{C.RESET}
  • «κάνε wifi attack / aircrack»

{C.CYAN}[ NETWORK RECON ]{C.RESET}
  • «κάνε whois στο example.com»
  • «dns lookup για target.com»

{C.CYAN}[ PACKET CAPTURE ]{C.RESET}
  • «κάπτουρε πακέτα στο eth0»
  • «sniff traffic port 80»

{C.CYAN}[ SMB / WINDOWS ]{C.RESET}
  • «enum4linux στο 192.168.1.100»

{C.CYAN}[ ΒΟΗΘΕΙΑ ]{C.RESET}
  • «εργαλεία» / «tools» — κατάσταση εργαλείων
  • «install» — εγκατάσταση εργαλείων
  • «exit» / «έξοδος» — αποχώρηση

{C.GOLD}──────────────────────────────────────────────{C.RESET}
{C.GRAY}Όλα τα sessions καταγράφονται στο:{C.RESET}
{C.GRAY}  ~/.doureios_ippos/logs/{C.RESET}
""")

# ──────────────────────────────────────────────
#  MAIN LOOP
# ──────────────────────────────────────────────
def main():
    os.system("clear")
    print(BANNER)
    print(DISCLAIMER)

    # Αποδοχή disclaimer
    while True:
        resp = input("> ").strip().upper()
        if resp in ("ΑΠΟΔΕΧΟΜΑΙ", "APODEXOMAI", "ACCEPT", "ΑΠΟΔΕΧΟΜΑΙ"):
            break
        else:
            print(f"{C.RED}Πρέπει να αποδεχτείς τους όρους για να συνεχίσεις.{C.RESET}")

    init_logger()
    available = check_tools()

    print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Γεια σου! Είμαι έτοιμος.")
    print(f"{C.GRAY}Πληκτρολόγησε «βοήθεια» ή «help» για λίστα εντολών.{C.RESET}\n")

    # History support
    try:
        readline.read_history_file(Path.home() / ".doureios_history")
    except FileNotFoundError:
        pass

    while True:
        try:
            print(f"{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} {C.WHITE}Τι ακριβώς θέλεις να κάνω;{C.RESET}")
            user_input = input(f"{C.CYAN}Εσύ:{C.RESET} ").strip()

            if not user_input:
                continue

            readline.write_history_file(Path.home() / ".doureios_history")
            intent = detect_intent(user_input)

            if intent == "exit":
                print(f"\n{C.GOLD}🐴 Αντίο! Stay ethical. 🐴{C.RESET}\n")
                break
            elif intent == "show_help":
                if "εργαλεί" in user_input.lower() or "tool" in user_input.lower():
                    print_tool_status(available)
                else:
                    show_help(available)
            elif intent == "nmap_scan":
                handle_nmap_scan(user_input, available)
            elif intent == "vuln_scan":
                handle_vuln_scan(user_input, available)
            elif intent == "web_scan":
                handle_web_scan(user_input, available)
            elif intent == "sql_inject":
                handle_sql_inject(user_input, available)
            elif intent == "password_attack":
                handle_password_attack(user_input, available)
            elif intent == "wifi_attack":
                handle_wifi_attack(user_input, available)
            elif intent == "packet_capture":
                handle_packet_capture(user_input, available)
            elif intent == "recon_dns":
                handle_recon_dns(user_input, available)
            elif intent == "smb_enum":
                handle_smb_enum(user_input, available)
            elif intent == "install_tool":
                handle_install_tool(user_input)
            else:
                print(f"\n{C.GOLD}🐴 Δούρειος Ίππος:{C.RESET} Δεν κατάλαβα ακριβώς.")
                print(f"   Δοκίμασε: «σκάναρε 192.168.1.1», «web scan σε site.com», «βοήθεια»")

            print()

        except KeyboardInterrupt:
            print(f"\n{C.GRAY}(Ctrl+C — γράψε «exit» για αποχώρηση){C.RESET}")
        except EOFError:
            print(f"\n{C.GOLD}🐴 Αντίο!{C.RESET}")
            break

if __name__ == "__main__":
    main()

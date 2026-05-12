#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — Demo Script για Video
#  Τρέξε αυτό για να δείξεις τις δυνατότητες του συστήματος
# ═══════════════════════════════════════════════════════════

GOLD="\033[93m"; GREEN="\033[92m"; CYAN="\033[96m"
RESET="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"

slow_print() {
    echo -e "$1" | pv -qL 80 2>/dev/null || echo -e "$1"
}

pause() { sleep "${1:-2}"; }

clear
echo -e "${GOLD}${BOLD}"
cat << 'BANNER'
     ╔═══════════════════════════════════════════════════════╗
     ║                                                       ║
     ║   🐴  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ  ·  DOUREIOS IPPOS  🐴          ║
     ║         Ethical Hacking Assistant v4.0                ║
     ║                                                       ║
     ╚═══════════════════════════════════════════════════════╝
BANNER
echo -e "${RESET}"
pause 2

# ── Demo 1: drip --status ──
echo -e "${CYAN}[ DEMO 1: Έλεγχος Εγκατεστημένων Εργαλείων ]${RESET}"
pause 1
drip --status
pause 3

# ── Demo 2: Terminal Mode ──
echo -e "\n${CYAN}[ DEMO 2: Terminal Mode — Φυσική Γλώσσα ]${RESET}"
pause 1
echo -e "${GOLD}🐴 Δούρειος Ίππος:${RESET} Τι ακριβώς θέλεις να κάνω;"
pause 1
echo -e "${CYAN}Εσύ:${RESET} σκάναρε το 127.0.0.1"
pause 1
echo -e "${GOLD}🐴:${RESET} Τι είδους σάρωση θέλεις;"
echo -e "  ${CYAN}1${RESET} — Γρήγορη   ${CYAN}2${RESET} — Κανονική   ${CYAN}3${RESET} — Πλήρης   ${CYAN}4${RESET} — Vulnerability"
pause 1
echo -e "${CYAN}Εσύ:${RESET} 1"
pause 1
echo -e "${GOLD}🐴:${RESET} Ξεκινώ γρήγορη σάρωση..."
nmap -F --open 127.0.0.1 2>/dev/null | head -20
pause 3

# ── Demo 3: Multi-step ──
echo -e "\n${CYAN}[ DEMO 3: Σύνθετες Εντολές ]${RESET}"
pause 1
echo -e "${GOLD}🐴 Δούρειος Ίππος:${RESET} Τι ακριβώς θέλεις να κάνω;"
pause 1
echo -e "${CYAN}Εσύ:${RESET} σκάναρε το 127.0.0.1 και μετά κάνε dns lookup στο google.com"
pause 1
echo -e "${GOLD}🐴:${RESET} Εντόπισα ${BOLD}2 ενέργειες${RESET}:"
echo -e "  1. ${GOLD}Σάρωση δικτύου${RESET} → ${CYAN}127.0.0.1${RESET}"
echo -e "  2. ${GOLD}DNS Recon${RESET} → ${CYAN}google.com${RESET}"
echo -e "${GOLD}🐴:${RESET} Θέλεις να τις εκτελέσω με τη σειρά;"
pause 1
echo -e "${CYAN}Εσύ:${RESET} ΝΑΙ"
pause 1
echo -e "${GOLD}🐴:${RESET} Βήμα 1/2: Σάρωση δικτύου..."
nmap -F 127.0.0.1 2>/dev/null | tail -5
pause 1
echo -e "${GOLD}🐴:${RESET} Βήμα 2/2: DNS lookup..."
dig google.com A +short | head -3
echo -e "${GREEN}✓ Όλα τα βήματα ολοκληρώθηκαν!${RESET}"
pause 3

# ── Demo 4: PDF Report ──
echo -e "\n${CYAN}[ DEMO 4: PDF Report ]${RESET}"
pause 1
echo -e "${GOLD}🐴 Δούρειος Ίππος:${RESET} Τι ακριβώς θέλεις να κάνω;"
pause 1
echo -e "${CYAN}Εσύ:${RESET} δημιούργησε report"
pause 1
python3 -c "
from report_generator import generate_report
path = generate_report(
    scan_type='Demo Scan',
    target='127.0.0.1',
    output='PORT  STATE  SERVICE\n22/tcp open ssh\n80/tcp open http',
    operator='Demo User',
    notes='Demo report για video'
)
print(f'\033[92m📄 Report: {path}\033[0m')
" 2>/dev/null
pause 3

# ── Demo 5: GUI ──
echo -e "\n${CYAN}[ DEMO 5: Web GUI ]${RESET}"
pause 1
echo -e "${GOLD}🐴:${RESET} Ξεκινώ Web GUI στο ${CYAN}http://localhost:5000${RESET}..."
echo -e "${DIM}(Ανοίγει αυτόματα στον browser)${RESET}"
pause 2

echo -e "\n${GOLD}${BOLD}═══════════════════════════════════════${RESET}"
echo -e "${GOLD}${BOLD}  🐴 Demo ολοκληρώθηκε!${RESET}"
echo -e "${GREEN}  Δούρειος Ίππος — Stay legal. Stay ethical.${RESET}"
echo -e "${GOLD}${BOLD}═══════════════════════════════════════${RESET}\n"

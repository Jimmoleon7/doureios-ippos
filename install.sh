#!/bin/bash
GOLD="\033[93m"; GREEN="\033[92m"; RED="\033[91m"; CYAN="\033[96m"; RESET="\033[0m"; BOLD="\033[1m"

echo -e "${GOLD}${BOLD}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   🐴  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — Installer v4.0       ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${RESET}"

# Check Python 3
if ! command -v python3 &>/dev/null; then echo -e "${RED}[✗] Python 3 not found${RESET}"; exit 1; fi
echo -e "${GREEN}[✓] Python 3 found${RESET}"

# Install Python dependencies
echo -e "${CYAN}[→] Installing Python libraries...${RESET}"
pip3 install flask flask-socketio langdetect reportlab pillow --break-system-packages 2>/dev/null || \
pip3 install flask flask-socketio langdetect reportlab pillow 2>/dev/null
echo -e "${GREEN}[✓] Python libraries installed${RESET}"

# ── Install drip command ──
echo -e "${CYAN}[→] Installing drip command...${RESET}"
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DRIP_PATH="/usr/local/bin/drip"

# Create drip launcher
sudo tee "$DRIP_PATH" > /dev/null << DRIP_SCRIPT
#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '$INSTALL_DIR')
os.chdir('$INSTALL_DIR')
exec(open('$INSTALL_DIR/drip.py').read())
DRIP_SCRIPT

sudo chmod +x "$DRIP_PATH"
echo -e "${GREEN}[✓] drip command installed → type 'drip' anywhere!${RESET}"

echo -e "\n${GREEN}${BOLD}[✓] Installation complete!${RESET}"
echo -e "${GOLD}"
echo "  Terminal mode : ${BOLD}drip${RESET}${GOLD}"
echo "  GUI mode      : ${BOLD}drip --gui${RESET}${GOLD}"
echo "  Update        : ${BOLD}drip --update${RESET}${GOLD}"
echo "  Status        : ${BOLD}drip --status${RESET}"
echo -e "${RESET}"

# Install pentesting tools
echo -e "${CYAN}Install pentesting tools? (YES/no)${RESET} "
read -r ans
if [[ "${ans^^}" == "YES" || "${ans^^}" == "NAI" || "${ans^^}" == "ΝΑΙ" || "$ans" == "Y" ]]; then
    sudo apt update -qq && sudo apt install -y \
        nmap hydra john nikto sqlmap gobuster dirb \
        tshark tcpdump aircrack-ng netdiscover enum4linux \
        whois dnsutils netcat-openbsd metasploit-framework 2>/dev/null
    echo -e "${GREEN}[✓] Tools installed!${RESET}"
fi

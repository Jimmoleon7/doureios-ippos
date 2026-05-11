#!/bin/bash
# ═══════════════════════════════════════════════════
#  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — Installer
# ═══════════════════════════════════════════════════

GOLD="\033[93m"
GREEN="\033[92m"
RED="\033[91m"
CYAN="\033[96m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${GOLD}${BOLD}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   🐴  ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — Installer v1.0   ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[✗] Python 3 δεν βρέθηκε. sudo apt install python3${RESET}"
    exit 1
fi
echo -e "${GREEN}[✓] Python 3 βρέθηκε${RESET}"

# Install to ~/.local/bin
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

cp doureios_ippos.py "$INSTALL_DIR/doureios_ippos"
chmod +x "$INSTALL_DIR/doureios_ippos"

# Add shebang fix
sed -i '1s|.*|#!/usr/bin/env python3|' "$INSTALL_DIR/doureios_ippos"

# Add to PATH if needed
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    echo -e "${CYAN}[i] Προστέθηκε $INSTALL_DIR στο PATH${RESET}"
fi

echo -e "\n${GREEN}${BOLD}[✓] Εγκατάσταση ολοκληρώθηκε!${RESET}"
echo -e "${GOLD}    Τρέξε: ${BOLD}doureios_ippos${RESET}${GOLD} (ή source ~/.bashrc πρώτα)${RESET}\n"

# Optional: install pentesting tools
echo -e "${CYAN}Θέλεις να εγκαταστήσω τα pentesting εργαλεία; (ΝΑΙ/όχι)${RESET} "
read -r ans
if [[ "${ans^^}" == "ΝΑΙ" || "${ans^^}" == "NAI" || "${ans^^}" == "YES" || "$ans" == "Y" ]]; then
    echo -e "${GOLD}Εγκατάσταση εργαλείων...${RESET}"
    sudo apt update -qq
    sudo apt install -y nmap hydra john nikto sqlmap gobuster dirb \
         tshark tcpdump aircrack-ng netdiscover enum4linux \
         whois dnsutils netcat-openbsd 2>/dev/null
    echo -e "${GREEN}[✓] Εργαλεία εγκαταστάθηκαν!${RESET}"
fi

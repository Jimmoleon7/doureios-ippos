# 🐴 ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — DOUREIOS IPPOS

![Doureios Ippos Logo](logo.png)
## AI-Powered Ethical Hacking Assistant v1.0

> *Φυσική γλώσσα (Ελληνικά & English) για authorized penetration testing*

---

## ⚠️ ΝΟΜΙΚΗ ΔΗΛΩΣΗ

Το Doureios Ippos προορίζεται **ΑΠΟΚΛΕΙΣΤΙΚΑ** για:
- ✅ Authorized penetration testing (με γραπτή άδεια)
- ✅ CTF competitions & security labs
- ✅ Δικά σου συστήματα / δίκτυα
- ✅ Εκπαιδευτικούς σκοπούς σε isolated περιβάλλον
- ❌ Μη εξουσιοδοτημένη πρόσβαση = **ΠΑΡΑΝΟΜΟ** (Ν.4411/2016, άρθρο 370Γ ΠΚ)

---

## 📦 Εγκατάσταση

```bash
git clone https://github.com/youruser/doureios_ippos
cd doureios_ippos
chmod +x install.sh
./install.sh
```

Ή απευθείας:
```bash
python3 doureios_ippos.py
```

---

## 🚀 Χρήση

```
doureios_ippos
```

Το σύστημα ρωτά τι θέλεις σε φυσική γλώσσα:

```
🐴 Δούρειος Ίππος: Τι ακριβώς θέλεις να κάνω;
Εσύ: σκάναρε το 192.168.1.0/24

🐴 Δούρειος Ίππος: Τι είδους σάρωση θέλεις;
  1 — Γρήγορη (top 100 ports)
  2 — Κανονική (top 1000 ports + service detection)
  3 — Πλήρης (όλα τα ports + OS detection)
  4 — Vulnerability scan
```

---

## 🛠️ Εργαλεία που υποστηρίζονται

| Εργαλείο | Χρήση |
|----------|-------|
| **nmap** | Network & port scanning, vuln scripts |
| **hydra** | Network login brute-force |
| **john** | Hash cracking (John the Ripper) |
| **nikto** | Web server vulnerability scanning |
| **sqlmap** | SQL injection testing |
| **gobuster** | Directory/DNS brute-forcing |
| **aircrack-ng** | WiFi WPA/WEP cracking |
| **tcpdump/tshark** | Packet capture |
| **enum4linux** | SMB/Samba enumeration |
| **whois/dig** | DNS & OSINT recon |

---

## 💬 Παραδείγματα Εντολών

```
# Σάρωση δικτύου
σκάναρε το 192.168.1.0/24
βρες ανοιχτές πόρτες στο 10.0.0.5

# Web testing
κάνε web scan στο http://testsite.local
ψάξε directories στο 192.168.1.10
τρέξε sqlmap στο http://site.com/page?id=1

# Password attacks
σπάσε το hash από το αρχείο hashes.txt
brute force ssh στο 192.168.1.5

# WiFi (δικό σου δίκτυο ΜΟΝΟ)
κάνε wifi attack

# Recon
κάνε whois στο example.com
dns lookup για target.com

# Βοήθεια
βοήθεια / help
εργαλεία / tools
```

---

## 📁 Δομή Αρχείων

```
doureios_ippos/
├── doureios_ippos.py    # Κύριο πρόγραμμα
├── install.sh           # Installer
└── README.md            # Αυτό το αρχείο

~/.doureios_ippos/
└── logs/                # Αρχεία καταγραφής sessions
```

---

## 🔧 Απαιτήσεις

- Python 3.8+
- Kali Linux / Parrot OS / Ubuntu (προτείνεται)
- Τα εργαλεία (nmap, hydra κτλ.) εγκαθίστανται αυτόματα από τον installer

---

## 📋 Changelog

### v1.0
- Natural language interface (Ελληνικά + English)
- Consent check πριν από κάθε ενέργεια
- Session logging
- Υποστήριξη 10+ εργαλείων
- Interactive menus για κάθε module

---

*Δούρειος Ίππος — Stay legal. Stay ethical.* 🐴

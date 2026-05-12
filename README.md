# 🐴 ΔΟΥΡΕΙΟΣ ΙΠΠΟΣ — DOUREIOS IPPOS

![Doureios Ippos Logo](logo.png)

> **AI-Powered Ethical Hacking Assistant** — Το πρώτο εργαλείο penetration testing στα **Ελληνικά & English**

---

## 🎯 Τι είναι το Doureios Ippos;

Το **Δούρειος Ίππος** είναι ένα AI-powered assistant για ethical hacking και penetration testing. Αντί να θυμάσαι δεκάδες εντολές από 10 διαφορετικά εργαλεία, απλά **γράφεις στα Ελληνικά ή Αγγλικά** τι θέλεις να κάνεις και το σύστημα επιλέγει, ρυθμίζει και τρέχει αυτόματα το κατάλληλο εργαλείο.

```
Εσύ:  σκάναρε το 192.168.1.0/24
🐴:   Τι είδους σάρωση θέλεις;
      1 — Γρήγορη  2 — Κανονική  3 — Πλήρης  4 — Vulnerability
```

---

## ⚠️ Νομική Δήλωση

Το Doureios Ippos προορίζεται **ΑΠΟΚΛΕΙΣΤΙΚΑ** για:
- ✅ Authorized penetration testing (με γραπτή άδεια)
- ✅ CTF competitions & security labs
- ✅ Δικά σου συστήματα / δίκτυα
- ✅ Εκπαιδευτικούς σκοπούς σε isolated περιβάλλον
- ❌ Μη εξουσιοδοτημένη πρόσβαση = **ΠΑΡΑΝΟΜΟ** (Ν.4411/2016)

---

## 🚀 Χαρακτηριστικά / Features

### 🧠 AI Natural Language Interface
- Κατανοεί **Ελληνικά και Αγγλικά** σε βάθος
- Αναγνωρίζει τόνους, mix γλωσσών, συνώνυμα
- Ρωτά μόνο όταν δεν καταλαβαίνει

### 🖥️ Dual Interface
- **Terminal mode** — κλασικό CLI
- **Web GUI** — browser interface στο `http://localhost:5000`

### 🛠️ Ενσωματωμένα Εργαλεία
| Εργαλείο | Χρήση |
|----------|-------|
| **nmap** | Network & port scanning, OS detection, vuln scripts |
| **hydra** | Network login brute-force |
| **john** | Hash cracking |
| **nikto** | Web vulnerability scanning |
| **sqlmap** | SQL injection testing |
| **gobuster** | Directory brute-forcing |
| **aircrack-ng** | WiFi WPA/WEP cracking |
| **tcpdump/tshark** | Packet capture |
| **enum4linux** | SMB/Samba enumeration |
| **Metasploit** | Advanced exploitation framework |

### 📄 PDF Reports
- Επαγγελματικές αναφορές με ελληνικά γράμματα
- Auto-εντοπισμός ευρημάτων (CVEs, open ports)
- Legal disclaimer & timestamp

### 🔄 Auto-Update
- Ελέγχει αυτόματα κάθε 24 ώρες
- `drip --update` για χειροκίνητη ενημέρωση

### 📋 Custom Wordlists
- Greek wordlist με ελληνικές λέξεις
- Αυτόματη επιλογή wordlist για κάθε attack

---

## 📦 Εγκατάσταση

### Kali Linux (Προτείνεται)
```bash
git clone https://github.com/Jimmoleon7/doureios-ippos.git
cd doureios-ippos
chmod +x install.sh
./install.sh
```

### Windows
```powershell
git clone https://github.com/Jimmoleon7/doureios-ippos.git
cd doureios-ippos
py -m pip install flask flask-socketio langdetect reportlab pillow
py app.py
```

---

## 🎮 Χρήση

```bash
drip           # Terminal mode
drip --gui     # Web GUI → http://localhost:5000
drip --update  # Ενημέρωση
drip --status  # Κατάσταση εργαλείων
drip --help    # Βοήθεια
```

---

## 💬 Παραδείγματα

```bash
σκάναρε το 192.168.1.1
κάνε web scan στο http://testsite.local
σπάσε τους κωδικούς από το hashes.txt
eternalblue check 192.168.1.100
κάνε whois στο google.com
δημιούργησε report
```

---

## 📊 Σύγκριση

| | Doureios Ippos | Metasploit | nmap |
|---|---|---|---|
| Φυσική γλώσσα | ✅ Ελληνικά+EN | ❌ | ❌ |
| Ενοποίηση εργαλείων | ✅ | ⚠️ | ❌ |
| Web GUI | ✅ | ✅ | ❌ |
| PDF Reports | ✅ | ❌ | ❌ |
| Ελληνική γλώσσα | ✅ Μοναδικό | ❌ | ❌ |

---

## 📋 Changelog

### v4.0
- ✅ `drip` command
- ✅ Auto-update
- ✅ Metasploit integration
- ✅ Custom Wordlists (Greek)

### v3.0
- ✅ Web GUI
- ✅ AI NLP Engine
- ✅ PDF Reports
- ✅ Scan options menu

### v1-2.0
- ✅ Terminal CLI
- ✅ 10+ εργαλεία
- ✅ Consent & logging

---

*Δούρειος Ίππος — Stay legal. Stay ethical.* 🐴

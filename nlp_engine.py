#!/usr/bin/env python3
"""
Doureios Ippos — NLP Engine
Αναγνώριση φυσικής γλώσσας (Ελληνικά & English)
Χωρίς εξωτερικό API — τρέχει 100% τοπικά
"""

import re
import unicodedata
from langdetect import detect, LangDetectException


def normalize_greek(text: str) -> str:
    """Remove Greek accents for better pattern matching"""
    nfd = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')

# ─────────────────────────────────────────────────────────────
#  INTENT DEFINITIONS
#  Κάθε intent έχει:
#  - el_patterns: ελληνικές εκφράσεις (regex)
#  - en_patterns: αγγλικές εκφράσεις (regex)
#  - description_el / description_en: περιγραφή για clarification
# ─────────────────────────────────────────────────────────────
INTENTS = [
    {
        "id": "nmap_scan",
        "el_patterns": [
            r"σκαν", r"σάρω", r"σαρω", r"ανακάλυψ", r"ανακαλυψ",
            r"βρες.*host", r"βρες.*συσκευ", r"ανοιχτ.*πόρτ",
            r"ανοιχτ.*port", r"δίκτυ.*σκαν", r"port.*scan",
            r"ποι.*συσκευ", r"ποι.*host", r"δες.*δίκτυ",
            r"ελεγξ.*δίκτυ", r"τρεξ.*nmap", r"nmap",
        ],
        "en_patterns": [
            r"scan", r"discover", r"find.*host", r"find.*device",
            r"open.*port", r"port.*scan", r"network.*scan",
            r"nmap", r"enumerate.*host", r"ping.*sweep",
            r"check.*network", r"what.*running",
        ],
        "description_el": "Σάρωση δικτύου / port scanning με nmap",
        "description_en": "Network / port scanning with nmap",
        "needs_target": True,
        "clarify_el": "Εννοείς να σκανάρω ένα συγκεκριμένο host/IP ή ολόκληρο δίκτυο;",
        "clarify_en": "Do you mean scanning a specific host/IP or an entire network range?",
    },
    {
        "id": "vuln_scan",
        "el_patterns": [
            r"ευάλωτ", r"ευαλωτ", r"vulnerability", r"vulnerabilit",
            r"αδυναμί", r"αδυναμι", r"cve", r"exploit",
            r"τρωτ", r"ασφάλει.*έλεγχ", r"security.*check",
            r"αδύναμ.*σημεί",
        ],
        "en_patterns": [
            r"vuln", r"vulnerability", r"vulnerabilit", r"exploit",
            r"cve", r"weak.*point", r"security.*audit",
            r"security.*check", r"find.*exploit",
        ],
        "description_el": "Σάρωση ευπαθειών (vulnerability scan)",
        "description_en": "Vulnerability scanning",
        "needs_target": True,
        "clarify_el": "Εννοείς vulnerability scan σε συγκεκριμένο host ή web εφαρμογή;",
        "clarify_en": "Do you mean vulnerability scan on a host or web application?",
    },
    {
        "id": "web_scan",
        "el_patterns": [
            r"web.*scan", r"σάρω.*web", r"σαρω.*site",
            r"ιστοσελίδ", r"ιστοσελιδ", r"website", r"nikto",
            r"gobuster", r"dirb", r"director.*brute",
            r"βρες.*director", r"κρυφ.*σελίδ", r"hidden.*page",
            r"http", r"https",
        ],
        "en_patterns": [
            r"web.*scan", r"website", r"nikto", r"gobuster",
            r"dirb", r"directory.*brute", r"find.*director",
            r"hidden.*page", r"web.*vuln", r"http.*scan",
        ],
        "description_el": "Web scanning (Nikto, Gobuster)",
        "description_en": "Web scanning (Nikto, Gobuster)",
        "needs_target": True,
        "clarify_el": "Εννοείς να ψάξω για directories ή να ελέγξω για web vulnerabilities;",
        "clarify_en": "Do you mean directory brute-forcing or web vulnerability scanning?",
    },
    {
        "id": "sql_inject",
        "el_patterns": [
            r"sql", r"injection", r"sqlmap",
            r"βάση.*δεδομέν", r"βαση.*δεδομεν",
            r"database", r"inject",
        ],
        "en_patterns": [
            r"sql", r"injection", r"sqlmap",
            r"database.*inject", r"inject.*database",
        ],
        "description_el": "SQL injection testing (sqlmap)",
        "description_en": "SQL injection testing (sqlmap)",
        "needs_target": True,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "password_attack",
        "el_patterns": [
            r"κωδικ", r"hash", r"σπάσ.*κωδικ", r"σπασ.*κωδικ",
            r"brute.*force", r"brute", r"john", r"hydra",
            r"hashcat", r"password", r"pass", r"crack",
            r"knack.*pass", r"σπα.*pass",
        ],
        "en_patterns": [
            r"crack", r"brute.*force", r"password", r"hash",
            r"john", r"hydra", r"hashcat", r"pass.*crack",
            r"crack.*pass",
        ],
        "description_el": "Password cracking / brute force",
        "description_en": "Password cracking / brute force",
        "needs_target": False,
        "clarify_el": "Εννοείς να σπάσω hash αρχείο ή να κάνω brute force σε υπηρεσία (SSH, FTP κλπ);",
        "clarify_en": "Do you mean cracking a hash file or brute-forcing a service (SSH, FTP etc)?",
    },
    {
        "id": "wifi_attack",
        "el_patterns": [
            r"wifi", r"wi-fi", r"wireless", r"ασύρματ", r"ασυρματ",
            r"wpa", r"wep", r"handshake", r"aircrack",
            r"airodump", r"aireplay",
        ],
        "en_patterns": [
            r"wifi", r"wi-fi", r"wireless", r"wpa", r"wep",
            r"handshake", r"aircrack", r"airodump",
        ],
        "description_el": "WiFi pentesting (aircrack-ng)",
        "description_en": "WiFi pentesting (aircrack-ng)",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "packet_capture",
        "el_patterns": [
            r"packet", r"πακέτ", r"πακετ", r"wireshark",
            r"tcpdump", r"tshark", r"sniff", r"traffic",
            r"κυκλοφορί", r"κυκλοφορι", r"καταγρ.*κίνηση",
            r"capture",
        ],
        "en_patterns": [
            r"packet", r"capture", r"sniff", r"traffic",
            r"wireshark", r"tcpdump", r"tshark",
            r"intercept.*traffic",
        ],
        "description_el": "Packet capture (tcpdump/tshark)",
        "description_en": "Packet capture (tcpdump/tshark)",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "recon_dns",
        "el_patterns": [
            r"whois", r"dns", r"domain", r"τομέ", r"τομε",
            r"subdomain", r"υποτομέ", r"υποτομε",
            r"πληροφορί.*domain", r"ψάξ.*domain",
            r"dig", r"nslookup",
        ],
        "en_patterns": [
            r"whois", r"dns", r"domain", r"subdomain",
            r"domain.*info", r"lookup", r"dig", r"nslookup",
            r"recon.*domain",
        ],
        "description_el": "DNS reconnaissance / WHOIS lookup",
        "description_en": "DNS reconnaissance / WHOIS lookup",
        "needs_target": True,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "smb_enum",
        "el_patterns": [
            r"smb", r"samba", r"windows.*share", r"shared.*folder",
            r"enum4linux", r"smbclient", r"network.*share",
            r"κοινόχρηστ", r"κοινοχρηστ",
        ],
        "en_patterns": [
            r"smb", r"samba", r"windows.*share", r"enum4linux",
            r"smbclient", r"network.*share", r"file.*share",
        ],
        "description_el": "SMB/Samba enumeration",
        "description_en": "SMB/Samba enumeration",
        "needs_target": True,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "show_help",
        "el_patterns": [
            r"βοήθει", r"βοηθει", r"help", r"τι.*μπορεί",
            r"τι.*κάνει", r"τι.*κανει", r"εντολ",
            r"λίστ.*εργαλεί", r"διαθέσιμ",
        ],
        "en_patterns": [
            r"help", r"what.*can", r"commands", r"tools",
            r"available", r"list.*tool", r"what.*do",
        ],
        "description_el": "Βοήθεια",
        "description_en": "Help",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "show_tools",
        "el_patterns": [
            r"εργαλεί", r"εργαλει", r"tools", r"ποι.*εργαλεί",
            r"τι.*εγκατεστημέν", r"installed",
        ],
        "en_patterns": [
            r"tools", r"installed", r"available.*tool",
            r"what.*installed",
        ],
        "description_el": "Κατάσταση εργαλείων",
        "description_en": "Tool status",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "generate_report",
        "el_patterns": [
            r"report", r"αναφορ", r"pdf", r"αποτελέσματ",
            r"αποτελεσματ", r"εξαγωγ", r"εκτύπω",
        ],
        "en_patterns": [
            r"report", r"pdf", r"export", r"results",
            r"generate.*report", r"save.*results",
        ],
        "description_el": "Δημιουργία PDF report",
        "description_en": "Generate PDF report",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "wordlist",
        "el_patterns": [
            r"wordlist", r"λεξικ", r"λιστ.*κωδικ", r"κωδικ.*λιστ",
            r"δημιουργ.*wordlist", r"φτιαξ.*wordlist",
            r"greek.*word", r"ελληνικ.*λεξ",
        ],
        "en_patterns": [
            r"wordlist", r"word.*list", r"create.*wordlist",
            r"generate.*wordlist", r"password.*list",
            r"greek.*wordlist",
        ],
        "description_el": "Διαχείριση wordlists",
        "description_en": "Wordlist management",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "msf_scan",
        "el_patterns": [
            r"metasploit", r"msf", r"eternalblue", r"ms17",
            r"msfconsole", r"exploit",
        ],
        "en_patterns": [
            r"metasploit", r"msf", r"eternalblue", r"ms17",
            r"msfconsole", r"exploit",
        ],
        "description_el": "Metasploit scan/exploit",
        "description_en": "Metasploit scan/exploit",
        "needs_target": True,
        "clarify_el": None,
        "clarify_en": None,
    },
    {
        "id": "exit",
        "el_patterns": [
            r"έξοδ", r"εξοδ", r"αποχώρ", r"αποχωρ",
            r"τέλος", r"τελος", r"bye", r"quit", r"exit",
        ],
        "en_patterns": [
            r"exit", r"quit", r"bye", r"goodbye", r"leave",
        ],
        "description_el": "Έξοδος",
        "description_en": "Exit",
        "needs_target": False,
        "clarify_el": None,
        "clarify_en": None,
    },
]

# ─────────────────────────────────────────────────────────────
#  TARGET PATTERNS
# ─────────────────────────────────────────────────────────────
TARGET_PATTERNS = [
    # IPv4 with optional CIDR
    re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2})?)\b"),
    # Domain names
    re.compile(r"\b([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)\b"),
    # URLs
    re.compile(r"(https?://[^\s]+)"),
]

# Words to exclude from domain matching
EXCLUDE_WORDS = {
    "the", "and", "for", "with", "from", "this", "that",
    "στο", "στην", "στα", "του", "για", "από", "με",
}

# ─────────────────────────────────────────────────────────────
#  LANGUAGE DETECTION
# ─────────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    """Detect if text is Greek (el) or English (en)"""
    try:
        lang = detect(text)
        return lang if lang in ("el", "en") else "en"
    except LangDetectException:
        # Fallback: check for Greek characters
        greek_chars = sum(1 for c in text if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
        return "el" if greek_chars > 2 else "en"

# ─────────────────────────────────────────────────────────────
#  INTENT DETECTION
# ─────────────────────────────────────────────────────────────
def detect_intent(text: str) -> dict:
    """
    Detect the user's intent from natural language input.
    Returns dict with: intent_id, confidence, language, target
    """
    text_lower = text.lower().strip()
    text_normalized = normalize_greek(text)  # accents removed for Greek matching
    lang = detect_language(text)

    best_match = None
    best_score = 0

    for intent in INTENTS:
        score = 0
        patterns = intent["el_patterns"] if lang == "el" else intent["en_patterns"]
        all_patterns = intent["el_patterns"] + intent["en_patterns"]

        for pattern in all_patterns:
            # Try both original and accent-normalized text
            if (re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE) or
                re.search(pattern, text_normalized, re.IGNORECASE | re.UNICODE)):
                score += 2 if pattern in patterns else 1

        if score > best_score:
            best_score = score
            best_match = intent

    target = extract_target(text)

    return {
        "intent_id": best_match["id"] if best_match and best_score > 0 else "unknown",
        "intent": best_match if best_match and best_score > 0 else None,
        "confidence": min(best_score / 3.0, 1.0),
        "language": lang,
        "target": target,
        "original_text": text,
    }

# ─────────────────────────────────────────────────────────────
#  TARGET EXTRACTION
# ─────────────────────────────────────────────────────────────
def extract_target(text: str) -> str:
    """Extract IP, CIDR, domain or URL from text"""
    # URL first
    m = TARGET_PATTERNS[2].search(text)
    if m:
        return m.group(1)
    # IP/CIDR
    m = TARGET_PATTERNS[0].search(text)
    if m:
        return m.group(1)
    # Domain
    m = TARGET_PATTERNS[1].search(text)
    if m:
        candidate = m.group(1).lower()
        if candidate not in EXCLUDE_WORDS and len(candidate) > 3:
            # Make sure it looks like a domain
            parts = candidate.split(".")
            if all(len(p) >= 2 for p in parts):
                return candidate
    return ""

# ─────────────────────────────────────────────────────────────
#  CLARIFICATION SYSTEM
# ─────────────────────────────────────────────────────────────
def needs_clarification(result: dict) -> str | None:
    """
    Returns clarification question if needed, None otherwise.
    Only asks when genuinely ambiguous — doesn't spam the user.
    """
    intent = result.get("intent")
    lang = result.get("language", "en")

    # Unknown intent
    if result["intent_id"] == "unknown":
        if lang == "el":
            return "Δεν κατάλαβα ακριβώς τι θέλεις. Μπορείς να το διευκρινίσεις; Π.χ. 'σκάναρε το 192.168.1.1' ή 'κάνε web scan στο site.com'"
        else:
            return "I'm not sure what you mean. Could you clarify? E.g. 'scan 192.168.1.1' or 'web scan site.com'"

    # Low confidence + has clarification question
    if result["confidence"] < 0.5 and intent and intent.get(f"clarify_{lang}"):
        return intent[f"clarify_{lang}"]

    # Needs target but none found
    if intent and intent.get("needs_target") and not result.get("target"):
        if lang == "el":
            return f"Για να κάνω {intent['description_el']}, χρειάζομαι έναν στόχο (IP, domain ή URL). Ποιον στόχο εννοείς;"
        else:
            return f"To perform {intent['description_en']}, I need a target (IP, domain or URL). What's your target?"

    return None

# ─────────────────────────────────────────────────────────────
#  RESPONSE BUILDER
# ─────────────────────────────────────────────────────────────
def build_confirmation(result: dict) -> str:
    """Build a natural confirmation message before executing"""
    lang = result.get("language", "en")
    intent = result.get("intent")
    target = result.get("target", "")

    if not intent:
        return ""

    desc = intent[f"description_{lang}"]
    if lang == "el":
        msg = f"Εντάξει, θα κάνω **{desc}**"
        if target:
            msg += f" στο **{target}**"
        msg += "."
    else:
        msg = f"Alright, I'll perform **{desc}**"
        if target:
            msg += f" on **{target}**"
        msg += "."

    return msg


if __name__ == "__main__":
    # Quick test
    tests = [
        "σκάναρε το 192.168.1.0/24",
        "scan the network 10.0.0.1",
        "θέλω να σπάσω τους κωδικούς",
        "do a web scan on http://testsite.com",
        "κάνε whois στο google.com",
        "vulnerability scan",
        "βοήθεια",
        "κάτι τυχαίο που δεν βγάζει νόημα",
    ]
    for t in tests:
        r = detect_intent(t)
        clarify = needs_clarification(r)
        print(f"\nInput: '{t}'")
        print(f"  Lang: {r['language']}, Intent: {r['intent_id']}, Confidence: {r['confidence']:.2f}, Target: '{r['target']}'")
        if clarify:
            print(f"  Clarify: {clarify}")
        else:
            print(f"  Confirm: {build_confirmation(r)}")

# ─────────────────────────────────────────────────────────────
#  MULTI-STEP COMMAND PARSER
#  Αναλύει σύνθετες εντολές πχ:
#  "σκάναρε το 192.168.1.1 και μετά κάνε web scan"
#  "brute force ssh στο 10.0.0.1 με rockyou"
# ─────────────────────────────────────────────────────────────

STEP_SEPARATORS = [
    r"και μετά", r"κι μετά", r"and then", r"after that",
    r"επίσης σκαν", r"επίσης κάνε", r"also scan", r"also run",
    r" & ", r";",
]

def parse_multi_step(text: str) -> list:
    """
    Parse a multi-step command into individual steps.
    Returns list of (text, intent_result) tuples.
    "σκάναρε το 192.168.1.1 και κάνε web scan" →
    [("σκάναρε το 192.168.1.1", nmap_result), ("κάνε web scan", web_result)]
    """
    import re as _re
    
    # Try to split on separators
    parts = [text]
    for sep in STEP_SEPARATORS:
        new_parts = []
        for part in parts:
            split = _re.split(sep, part, flags=_re.IGNORECASE)
            new_parts.extend([p.strip() for p in split if p.strip()])
        parts = new_parts
    
    if len(parts) <= 1:
        return None  # Not a multi-step command
    
    results = []
    shared_target = extract_target(text)  # Try to get target from full text
    
    for part in parts:
        if len(part) < 3:
            continue
        result = detect_intent(part)
        # If no target in this part, use shared target
        if not result.get("target") and shared_target:
            result["target"] = shared_target
        if result["intent_id"] != "unknown":
            results.append(result)
    
    return results if len(results) > 1 else None


def is_multi_step(text: str) -> bool:
    """Quick check if text might be a multi-step command"""
    import re as _re
    for sep in STEP_SEPARATORS[:6]:  # Check main separators
        if _re.search(sep, text, _re.IGNORECASE):
            # Make sure it has at least 2 action words
            result = detect_intent(text)
            parts = parse_multi_step(text)
            return parts is not None and len(parts) >= 2
    return False


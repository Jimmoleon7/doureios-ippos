#!/usr/bin/env python3
"""
Doureios Ippos — Custom Wordlists Manager
Διαχείριση και δημιουργία wordlists για password attacks
"""

import os
import random
import itertools
import shutil
from pathlib import Path
from datetime import datetime

# ── Directories ──
WORDLISTS_DIR = Path.home() / ".doureios_ippos" / "wordlists"
SYSTEM_WORDLISTS = [
    Path("/usr/share/wordlists/rockyou.txt"),
    Path("/usr/share/wordlists/rockyou.txt.gz"),
    Path("/usr/share/wordlists/dirb/common.txt"),
    Path("/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"),
    Path("/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000.txt"),
]

# ── Greek common passwords/words ──
GREEK_COMMON = [
    "123456", "password", "123456789", "qwerty", "12345",
    "ελλαδα", "greece", "athens", "athina", "thessaloniki",
    "κωδικος", "κωδικοσ", "123", "1234", "12345678",
    "αθηνα", "ελλας", "hellas", "greek", "grecia",
    "admin", "administrator", "root", "user", "test",
    "welcome", "login", "pass", "passwd", "password1",
    "letmein", "monkey", "dragon", "master", "abc123",
    "sunshine", "princess", "shadow", "superman", "batman",
    "football", "soccer", "basketball", "baseball",
    "iloveyou", "trustno1", "hello", "charlie", "donald",
]

# ── Common patterns ──
YEARS = [str(y) for y in range(1990, 2026)]
SPECIAL_CHARS = ["!", "@", "#", "$", "*", "123", "1234", "12345"]


def ensure_wordlists_dir():
    WORDLISTS_DIR.mkdir(parents=True, exist_ok=True)


def get_available_wordlists() -> dict:
    """Get all available wordlists (system + custom)"""
    available = {}

    # System wordlists
    for wl in SYSTEM_WORDLISTS:
        if wl.exists():
            size = wl.stat().st_size
            available[wl.name] = {
                "path": str(wl),
                "size": _human_size(size),
                "type": "system",
                "lines": _count_lines(wl) if size < 50_000_000 else "50M+",
            }

    # Custom wordlists
    ensure_wordlists_dir()
    for wl in WORDLISTS_DIR.glob("*.txt"):
        size = wl.stat().st_size
        available[wl.name] = {
            "path": str(wl),
            "size": _human_size(size),
            "type": "custom",
            "lines": _count_lines(wl),
        }

    return available


def create_wordlist_from_target(
    target_info: dict,
    output_name: str = None
) -> str:
    """
    Create a targeted wordlist based on information about the target.
    target_info can include: name, company, domain, year, city, etc.
    Returns path to created wordlist.
    """
    ensure_wordlists_dir()

    words = set()

    # Add base words from target info
    base_words = []
    for key in ["name", "company", "domain", "city", "nickname"]:
        val = target_info.get(key, "")
        if val:
            base_words.append(val.lower())
            base_words.append(val.capitalize())
            base_words.append(val.upper())
            # Remove spaces
            base_words.append(val.lower().replace(" ", ""))
            base_words.append(val.lower().replace(" ", "_"))
            base_words.append(val.lower().replace(" ", "."))

    # Add Greek common passwords
    words.update(GREEK_COMMON)

    # Combine base words with years and special chars
    for word in base_words:
        words.add(word)
        for year in YEARS[-10:]:  # Last 10 years
            words.add(f"{word}{year}")
            words.add(f"{year}{word}")
        for special in SPECIAL_CHARS:
            words.add(f"{word}{special}")
            words.add(f"{word.capitalize()}{special}")

    # Add birth year combinations if provided
    if "birth_year" in target_info:
        by = target_info["birth_year"]
        for word in base_words:
            words.add(f"{word}{by}")
            words.add(f"{by}{word}")

    # Add domain variations
    if "domain" in target_info:
        domain = target_info["domain"].split(".")[0]
        words.add(domain)
        words.add(f"{domain}123")
        words.add(f"{domain}@123")
        words.add(f"admin@{domain}")

    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = output_name or f"custom_{timestamp}.txt"
    if not name.endswith(".txt"):
        name += ".txt"
    output_path = WORDLISTS_DIR / name

    with open(output_path, "w", encoding="utf-8") as f:
        for word in sorted(words):
            f.write(word + "\n")

    return str(output_path)


def create_greek_wordlist(output_name: str = "greek_passwords.txt") -> str:
    """Create a wordlist with Greek-specific passwords"""
    ensure_wordlists_dir()

    greek_words = [
        # Greek cities
        "αθηνα", "athina", "athens", "θεσσαλονικη", "thessaloniki",
        "πατρα", "patra", "patras", "ηρακλειο", "heraklio", "heraklion",
        "λαρισα", "larisa", "larissa", "βολος", "volos", "ιωαννινα",
        "ioannina", "χανια", "chania", "ροδος", "rhodes",
        # Greek names
        "γιωργης", "giorgis", "giorgas", "γιωργος", "giorgos",
        "κωστας", "kostas", "νικος", "nikos", "δημητρης", "dimitris",
        "μαρια", "maria", "ελενη", "eleni", "αννα", "anna",
        "χρηστος", "christos", "παναγιωτης", "panagiotis",
        # Greek words
        "ελλαδα", "ellada", "greece", "ελληνας", "ellinas",
        "θαλασσα", "thalassa", "ουρανος", "ouranos", "αγαπη", "agapi",
        "φιλος", "filos", "αδερφος", "aderfos",
        # Common Greek passwords
        "123456", "qwerty123", "password123", "admin123",
        "greece123", "hellas123", "ελλαδα123",
        "κωδικος1", "κωδικος123",
        # Greek keyboard patterns
        "αβγδ", "qwerty", "ασδφ", "asdf",
    ]

    # Add variations
    all_words = set(greek_words)
    for word in greek_words:
        all_words.add(word + "123")
        all_words.add(word + "!")
        all_words.add(word.capitalize())
        all_words.add(word.upper())
        for year in ["2020", "2021", "2022", "2023", "2024"]:
            all_words.add(word + year)

    output_path = WORDLISTS_DIR / output_name
    with open(output_path, "w", encoding="utf-8") as f:
        for word in sorted(all_words):
            f.write(word + "\n")

    return str(output_path)


def merge_wordlists(wordlist_paths: list, output_name: str = None,
                    deduplicate: bool = True) -> str:
    """Merge multiple wordlists into one, optionally deduplicating"""
    ensure_wordlists_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = output_name or f"merged_{timestamp}.txt"
    if not name.endswith(".txt"):
        name += ".txt"
    output_path = WORDLISTS_DIR / name

    if deduplicate:
        words = set()
        for path in wordlist_paths:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            words.add(word)
            except Exception:
                pass
        with open(output_path, "w", encoding="utf-8") as f:
            for word in sorted(words):
                f.write(word + "\n")
        total = len(words)
    else:
        total = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for path in wordlist_paths:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as src:
                        for line in src:
                            f.write(line)
                            total += 1
                except Exception:
                    pass

    return str(output_path)


def get_best_wordlist(attack_type: str = "password") -> str:
    """Return the best available wordlist for the given attack type"""
    if attack_type in ("password", "hash", "brute"):
        # Prefer rockyou
        rockyou = Path("/usr/share/wordlists/rockyou.txt")
        if rockyou.exists():
            return str(rockyou)
        # Check custom
        ensure_wordlists_dir()
        custom = list(WORDLISTS_DIR.glob("*.txt"))
        if custom:
            return str(custom[0])
        # Create Greek wordlist as fallback
        return create_greek_wordlist()

    elif attack_type in ("directory", "web", "dir"):
        dirb = Path("/usr/share/wordlists/dirb/common.txt")
        if dirb.exists():
            return str(dirb)
        dirbuster = Path("/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")
        if dirbuster.exists():
            return str(dirbuster)

    return ""


def _human_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _count_lines(path: Path) -> int:
    try:
        with open(path, "rb") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def print_wordlists():
    """Print available wordlists in a nice format"""
    available = get_available_wordlists()
    if not available:
        print("Δεν βρέθηκαν wordlists")
        return

    print(f"\n{'─'*60}")
    print(f"{'Όνομα':<35} {'Τύπος':<10} {'Μέγεθος':<10} {'Γραμμές'}")
    print(f"{'─'*60}")
    for name, info in available.items():
        print(f"{name:<35} {info['type']:<10} {info['size']:<10} {info['lines']}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    print("Available wordlists:")
    print_wordlists()

    print("\nCreating Greek wordlist...")
    path = create_greek_wordlist()
    lines = _count_lines(Path(path))
    print(f"Created: {path} ({lines} words)")

    print("\nBest password wordlist:", get_best_wordlist("password"))
    print("Best directory wordlist:", get_best_wordlist("directory"))

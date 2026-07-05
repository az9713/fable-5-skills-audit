"""Pre-publish leak gate. Scan a directory for secrets, identity tokens, and
private paths before pushing anything public.

Usage:
    python check_before_publish.py <dir>

Exit code 0 = clean, 1 = at least one potential leak found (so it can gate CI).

Configure IDENTITY_TOKENS below with the strings specific to YOUR machine
(username, email, any bot handles, personal names) before relying on it. The
SECRET_PATTERNS and PATH_PATTERNS below are universal and catch the common
credential and absolute-path formats out of the box.
"""
import os, re, sys
from collections import defaultdict

# --- configure these for your environment ---------------------------------
IDENTITY_TOKENS = [
    # r'(?i)\byour-username\b',
    # r'(?i)@your-email-domain',
    # r'your_bot_handle',
]
# Skill/plugin names leak your setup too. To catch them, drop your inventory
# CSV path here and the script will load column 0 as names to search for.
NAME_CSV = None            # e.g. 'skills_inventory.csv'
NAME_MIN_LEN = 6           # ignore very short names (English-word false positives)
NAME_ALLOWLIST = set()     # generic words that are also skill names: add to taste
# --------------------------------------------------------------------------

SECRET_PATTERNS = [
    r'sk-[A-Za-z0-9]{20}', r'ghp_[A-Za-z0-9]{20}', r'gho_[A-Za-z0-9]{20}',
    r'github_pat_[A-Za-z0-9_]{20}', r'AKIA[A-Z0-9]{16}', r'xox[baprs]-[A-Za-z0-9-]{10}',
    r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'(?i)api[_-]?key\s*[=:]\s*["\'][A-Za-z0-9]{16}',
]
PATH_PATTERNS = [r'C:\\Users\\[^\\/\s"]+', r'C:/Users/[^/\s"]+', r'/c/Users/[^/\s"]+',
                 r'/home/[^/\s"]+', r'/Users/[^/\s"]+']

def load_names():
    if not NAME_CSV or not os.path.isfile(NAME_CSV):
        return set()
    import csv
    out = set()
    for row in csv.reader(open(NAME_CSV, encoding='utf-8')):
        if row and len(row[0]) >= NAME_MIN_LEN and row[0] not in NAME_ALLOWLIST:
            out.add(row[0])
    return out - {'skill', 'name', 'plugin'}

def scan(target):
    names = load_names()
    hits = defaultdict(lambda: defaultdict(set))
    for root, dirs, files in os.walk(target):
        if '.git' in dirs:
            dirs.remove('.git')
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, target)
            try:
                text = open(p, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            for pat in SECRET_PATTERNS:
                if re.search(pat, text): hits[rel]['secret'].add(pat)
            for pat in PATH_PATTERNS:
                if re.search(pat, text): hits[rel]['path'].add(pat)
            for pat in IDENTITY_TOKENS:
                if re.search(pat, text): hits[rel]['identity'].add(pat)
            for n in names:
                if re.search(r'(?<![\w-])' + re.escape(n) + r'(?![\w-])', text):
                    hits[rel]['name'].add(n)
    return hits

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    hits = scan(target)
    if not hits:
        print(f"CLEAN — no secrets, private paths, identity tokens, or configured names in {target}")
        return 0
    print(f"POTENTIAL LEAKS in {len(hits)} file(s):\n")
    for rel, kinds in sorted(hits.items()):
        print(f"  {rel}:")
        for kind, pats in kinds.items():
            shown = sorted(pats)[:12]
            more = '' if len(pats) <= 12 else f' …+{len(pats)-12}'
            print(f"     {kind}: {', '.join(shown)}{more}")
    return 1

if __name__ == '__main__':
    sys.exit(main())

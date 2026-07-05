"""Phase 0: mechanical inventory of personal-scope skills + enabled plugin skills."""
import csv, os, re, sys, datetime

SKILLS = os.path.expanduser(r"~\.claude\skills")
PLUGINS = os.path.expanduser(r"~\.claude\plugins")
OUT = os.path.dirname(os.path.abspath(__file__))

REF_RE = re.compile(r'(?<![\w/:.])((?:\./)?(?:scripts|assets|references|templates|examples|docs)/[\w\-./]+\.\w{1,5})')
FM_RE = re.compile(r'\A---\s*\n(.*?)\n---', re.S)

def frontmatter(text):
    m = FM_RE.match(text)
    if not m:
        return None
    fm = {}
    lines = m.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' in line and not line.startswith((' ', '\t', '#')):
            k, v = line.split(':', 1)
            k, v = k.strip(), v.strip().strip('"\'')
            if v in ('>', '>-', '|', '|-'):  # YAML block scalar: gather indented continuation
                block = []
                while i + 1 < len(lines) and (lines[i + 1].startswith((' ', '\t')) or not lines[i + 1].strip()):
                    block.append(lines[i + 1].strip())
                    i += 1
                v = ' '.join(b for b in block if b)
            fm[k] = v
        i += 1
    return fm

def dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total

def latest_mtime(path):
    latest = 0
    for root, _, files in os.walk(path):
        for f in files:
            if f == 'SKILL.md':
                try:
                    latest = max(latest, os.path.getmtime(os.path.join(root, f)))
                except OSError:
                    pass
    return datetime.date.fromtimestamp(latest).isoformat() if latest else ''

rows = []
for entry in sorted(os.listdir(SKILLS)):
    d = os.path.join(SKILLS, entry)
    if not os.path.isdir(d):
        continue
    skill_md = os.path.join(d, 'SKILL.md')
    has_md = os.path.isfile(skill_md)
    text = open(skill_md, encoding='utf-8', errors='replace').read() if has_md else ''
    fm = frontmatter(text) if text else None
    sub = sum(1 for root, _, files in os.walk(d) if 'SKILL.md' in files and root != d)
    broken = []
    if has_md:
        for ref in set(REF_RE.findall(text)):
            if not os.path.exists(os.path.join(d, ref.lstrip('./'))):
                broken.append(ref)
    flags = []
    if not has_md: flags.append('NO_SKILL_MD')
    if has_md and fm is None: flags.append('NO_FRONTMATTER')
    if fm is not None and not fm.get('description'): flags.append('NO_DESCRIPTION')
    size = dir_size(d)
    if size > 10 * 1024 * 1024: flags.append('OVERSIZED')
    if broken: flags.append('BROKEN_REFS')
    rows.append({
        'skill': entry,
        'fm_name': (fm or {}).get('name', ''),
        'description': (fm or {}).get('description', '').replace('\n', ' ')[:400],
        'sub_skills': sub,
        'size_mb': round(size / 1048576, 2),
        'last_modified': latest_mtime(d) or (datetime.date.fromtimestamp(os.path.getmtime(d)).isoformat()),
        'flags': ';'.join(flags),
        'broken_refs': ';'.join(broken[:10]),
    })

with open(os.path.join(OUT, 'skills_inventory.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

# Plugin skills (collision axis)
prows = []
for root, dirs, files in os.walk(PLUGINS):
    if 'SKILL.md' in files and (os.sep + 'skills' + os.sep) in (root + os.sep):
        text = open(os.path.join(root, 'SKILL.md'), encoding='utf-8', errors='replace').read()
        fm = frontmatter(text) or {}
        parts = root.replace(PLUGINS, '').strip(os.sep).split(os.sep)
        prows.append({
            'plugin_path': '/'.join(parts),
            'name': fm.get('name', parts[-1]),
            'description': fm.get('description', '').replace('\n', ' ')[:300],
        })

if prows:
    with open(os.path.join(OUT, 'plugin_skills.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=prows[0].keys())
        w.writeheader(); w.writerows(prows)

print(f"personal skills: {len(rows)}")
print(f"flagged: {sum(1 for r in rows if r['flags'])}")
print(f"oversized: {[r['skill'] for r in rows if 'OVERSIZED' in r['flags']]}")
print(f"plugin skills: {len(prows)}")

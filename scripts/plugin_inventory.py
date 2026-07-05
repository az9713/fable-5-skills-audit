"""P0: per-plugin inventory -> plugins_inventory.csv + anomalies report."""
import csv, json, os
from collections import defaultdict

PLUG = os.path.expanduser(r"~\.claude\plugins")
CACHE = os.path.join(PLUG, 'cache')
settings = json.load(open(os.path.expanduser(r"~\.claude\settings.json"), encoding='utf-8'))
enabled_map = settings.get('enabledPlugins', {})  # "plugin@marketplace": bool

def dir_size(path):
    t = 0
    for root, _, files in os.walk(path):
        for f in files:
            try: t += os.path.getsize(os.path.join(root, f))
            except OSError: pass
    return t

def count_kind(path, sub, marker=None):
    """Count entries in a component dir (skills/<n>/SKILL.md, agents/*.md, commands/*.md)."""
    d = os.path.join(path, sub)
    if not os.path.isdir(d): return 0
    if marker:  # dirs containing marker file
        return sum(1 for e in os.listdir(d) if os.path.isfile(os.path.join(d, e, marker)))
    return sum(1 for e in os.listdir(d) if e.endswith('.md'))

rows, anomalies = [], []
for mkt in sorted(os.listdir(CACHE)):
    mdir = os.path.join(CACHE, mkt)
    if not os.path.isdir(mdir): continue
    if mkt.startswith('temp_git_'):
        anomalies.append(f"ORPHAN cache dir: {mkt} ({dir_size(mdir)//1024}KB)")
        continue
    for plugin in sorted(os.listdir(mdir)):
        pdir = os.path.join(mdir, plugin)
        if not os.path.isdir(pdir): continue
        versions = [v for v in os.listdir(pdir) if os.path.isdir(os.path.join(pdir, v))]
        if len(versions) > 1:
            anomalies.append(f"MULTIPLE cached versions: {plugin}@{mkt} -> {len(versions)} ({', '.join(versions[:5])})")
        # use most recently modified version dir as the live one
        if not versions:
            continue
        live = max(versions, key=lambda v: os.path.getmtime(os.path.join(pdir, v)))
        vdir = os.path.join(pdir, live)
        key = f"{plugin}@{mkt}"
        status = enabled_map.get(key)
        rows.append({
            'plugin': plugin, 'marketplace': mkt,
            'status': 'enabled' if status else ('disabled' if status is False else 'NOT-IN-SETTINGS'),
            'skills': count_kind(vdir, 'skills', 'SKILL.md'),
            'agents': count_kind(vdir, 'agents'),
            'commands': count_kind(vdir, 'commands'),
            'hooks': 1 if os.path.exists(os.path.join(vdir, 'hooks')) else 0,
            'mcp': 1 if (os.path.exists(os.path.join(vdir, '.mcp.json')) or os.path.exists(os.path.join(vdir, 'mcp.json'))) else 0,
            'versions_cached': len(versions),
            'size_mb': round(dir_size(pdir) / 1048576, 2),
        })

# settings entries with no cache
cached_keys = {f"{r['plugin']}@{r['marketplace']}" for r in rows}
for key, val in enabled_map.items():
    if key not in cached_keys:
        anomalies.append(f"IN SETTINGS BUT NO CACHE: {key} ({'enabled' if val else 'disabled'})")

rows.sort(key=lambda r: (-{'enabled': 1, 'disabled': 0, 'NOT-IN-SETTINGS': 0}[r['status']], -r['size_mb']))
with open('plugins_inventory.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)

en = [r for r in rows if r['status'] == 'enabled']
dis = [r for r in rows if r['status'] == 'disabled']
nis = [r for r in rows if r['status'] == 'NOT-IN-SETTINGS']
print(f"cached plugins: {len(rows)} | enabled: {len(en)} | disabled: {len(dis)} | not-in-settings: {len(nis)}")
print(f"enabled totals: skills={sum(r['skills'] for r in en)} agents={sum(r['agents'] for r in en)} commands={sum(r['commands'] for r in en)} hooks={sum(r['hooks'] for r in en)} mcp={sum(r['mcp'] for r in en)}")
print(f"disabled cache size: {sum(r['size_mb'] for r in dis):.0f}MB | not-in-settings size: {sum(r['size_mb'] for r in nis):.0f}MB")
print("\n-- not-in-settings (cached but never configured):")
for r in nis: print(f"  {r['plugin']}@{r['marketplace']} ({r['size_mb']}MB, {r['skills']} skills)")
print("\n-- anomalies:")
for a in anomalies: print(' ', a)

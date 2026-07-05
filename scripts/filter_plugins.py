"""Filter plugin_skills.csv to skills from ENABLED plugins only."""
import csv, json, os

settings = json.load(open(os.path.expanduser(r"~\.claude\settings.json"), encoding='utf-8'))
enabled = {k for k, v in settings.get('enabledPlugins', {}).items() if v}  # "plugin@marketplace"

rows = list(csv.DictReader(open('plugin_skills.csv', encoding='utf-8')))
kept = []
for r in rows:
    parts = r['plugin_path'].split('/')
    if parts[0] != 'cache' or len(parts) < 5:
        continue  # skip marketplaces/ duplicates
    marketplace, plugin = parts[1], parts[2]
    if f"{plugin}@{marketplace}" in enabled:
        r['plugin'] = f"{plugin}@{marketplace}"
        kept.append(r)

with open('plugin_skills_enabled.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['plugin', 'name', 'description', 'plugin_path'])
    w.writeheader(); w.writerows(kept)

print(f"enabled plugin skills: {len(kept)} (from {len(enabled)} enabled plugins)")

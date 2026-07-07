# fable-5-skills-audit

[![Interactive case study — click to open the live page](docs/preview.png)](https://az9713.github.io/fable-5-skills-audit/)

### ▶ [**Open the interactive case study →**](https://az9713.github.io/fable-5-skills-audit/)

The image above is a preview — **click it** (or the link) for the live GitHub
Pages version: an animated before/after, a clickable breakdown of what was
removed and why, and a Skills⇄Plugins toggle. GitHub can't run an interactive
page *inside* this README, so it lives at that link; the same numbers are in
[CASE_STUDY.md](CASE_STUDY.md) as plain text.

---

A reusable methodology for auditing and cleaning up a large Claude Code
configuration — the personal skills in `~/.claude/skills/` and the plugins in
`~/.claude/plugins/` — orchestrated with **Fable 5**.

Skill and plugin estates grow silently. Individually every addition seems free;
collectively they duplicate each other, fight over the same trigger phrases,
shadow (or get shadowed by) plugin equivalents, and tax the context window of
*every* session. Past a hundred-odd skills it's no longer auditable by hand.

This repo is the **method and the tooling**, plus an anonymized
[case study](CASE_STUDY.md) of running it on a real 182-skill / 67-plugin
install. It does **not** contain the audited system's actual inventory — the
tools here reproduce the audit on *your own* machine.

## The four-pass method

| Pass | Goal | How |
|---|---|---|
| **0 — Inventory** | Facts before opinions | Script-walk every skill and plugin: name, description, size, sub-skill count, last-modified, broken references, malformed frontmatter → CSV |
| **1 — Categorize** | Make the estate legible | Sort every skill into a dozen-ish domains so overlaps are comparable |
| **2 — Grade overlaps** | Find the real redundancy | Read the actual skill bodies (fan out across categories in parallel) and grade every pair **D**uplicate / **S**ubset / **O**verlapping / **A**djacent, cross-referencing enabled-plugin skills for collisions |
| **3 — Verdict & reconcile** | Decide, safely | One verdict per item — keep / merge / disable / archive — with the skills side and the plugins side reconciled against each other *before* anything changes |

The reconciliation in pass 3 is what hand-audits miss: a personal skill may be an
archive candidate *because a plugin covers it*, while that same plugin is a
disable candidate on the plugin side. Auditing both together closes the loop
before it strands a capability.

Execution afterward is **reversible by construction**: skills are *moved* to an
archive folder (never deleted), plugins are *toggled* in settings, and settings
are backed up before the first edit.

## What's here

```
scripts/
  inventory.py            Pass 0 — walk ~/.claude/skills, emit skills_inventory.csv
                          (+ plugin_skills.csv); flags broken refs, bad frontmatter,
                          oversized folders
  plugin_inventory.py     Pass 0 — walk ~/.claude/plugins, emit plugins_inventory.csv;
                          enabled vs disabled vs cached, component counts, orphan
                          cache dirs, duplicate cached versions
  filter_plugins.py       Reduce plugin_skills.csv to just the enabled plugins,
                          the collision surface that actually matters
  check_before_publish.py Pre-publish leak gate: scan a directory for secrets,
                          private paths, and configured identity tokens before you
                          push anything public
CASE_STUDY.md             Anonymized results from one real run (counts + reasoning,
                          no skill/plugin names)
```

Passes 1–3 (categorize, grade, verdict) are inherently specific to *your* estate
and your judgment — the case study documents how they were carried out, but the
per-item decision files are deliberately **not** published here (they would be
nothing but one person's private inventory).

## Fable Mode skill

The `skills/fable-mode-skill/` is a reusable Claude Code skill that distills this audit's discipline into a working method: facts-first inventory → verdict vocabulary → gate decisions → reversible planning → scripted execution → verify-by-exercising → machine-derived receipts. Use it for any multi-step engagement (audit, cleanup, migration, publish) or when you want Opus to operate with Fable 5's judgment habits.

For a walkthrough of the discipline and reasoning, see **["How I Make Opus Think Like Fable (5 easy steps)"](https://www.youtube.com/watch?v=XTBWVVcF3Pk)**.

## Running the inventory on your own machine

Requires Python 3.9+. Read-only — walks your config and writes CSVs to the
current directory; it changes nothing under `~/.claude`.

```bash
python scripts/inventory.py          # -> skills_inventory.csv, plugin_skills.csv
python scripts/plugin_inventory.py   # -> plugins_inventory.csv
python scripts/filter_plugins.py     # -> plugin_skills_enabled.csv
```

Open the CSVs, sort by `flags` / `size_mb` / `status`, and you already have pass 0
— the broken, oversized, duplicated, and never-configured items surface
immediately. Feed the descriptions to a model (this method used Fable 5 fanning
out parallel readers) for passes 1–3.

Before publishing anything derived from your estate:

```bash
python scripts/check_before_publish.py <dir>   # configure IDENTITY_TOKENS first
```

## Headline result from the case study

A 182-skill / 67-plugin install that no human could hold in their head went to
**98 skills and 25 plugins**, shedding roughly **200 items of per-session context
bloat** (142 plugin skills, 17 agents, 58 commands) and **~1.5 GB** — with a
documented one-line undo for every change. Full numbers in
[CASE_STUDY.md](CASE_STUDY.md).

## License

MIT — see [LICENSE](LICENSE).

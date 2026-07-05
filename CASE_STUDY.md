# Case Study: Auditing a 182-Skill Claude Code Estate with Fable 5

An anonymized results summary from a real audit-and-cleanup of a personal Claude
Code configuration. **No individual skill or plugin is named** — this document
reports only counts, categories, and the reasoning behind each decision, so the
methodology can be judged on its outcomes without exposing the subject's setup.

The full pipeline (the scripts that produced these numbers) is in this repo; the
subject's actual inventory is not.

---

## The problem

A power user's Claude Code install had grown, over months, to:

- **182 personal skills** (712 `SKILL.md` files across nested sub-skills) totalling **1.5 GB**
- **67 enabled plugins** injecting **244 skills, 49 agents, 101 commands, 15 hooks, and 8 MCP servers** into *every* session
- **125 cached plugins** across 12 marketplaces

At that scale the estate had become impossible to reason about by hand. Skills
silently duplicated each other, competed for the same trigger phrases, shadowed
better plugin equivalents (or were shadowed *by* them), and quietly wasted
context on every single request. The user couldn't answer a simple question:
*which of these actually earn their place?*

## The approach

The whole engagement was **orchestrated on Fable 5** as the session model, in
four passes:

| Pass | What it did |
|---|---|
| **0 — Inventory** | Scripted extraction of every skill's name, description, size, sub-skill count, last-modified date, broken references, and malformed frontmatter → structured CSV. Facts before opinions. |
| **1 — Categorize** | All 182 skills sorted into **20 categories**; zero left uncategorized. |
| **2 — Grade overlaps** | **17 parallel subagents** (13 skill-category + 4 plugin-cluster) read the actual skill bodies and graded every overlap Duplicate / Subset / Overlapping / Adjacent, cross-referencing **334 plugin skills** for collisions. |
| **3 — Verdict & reconcile** | One verdict per item, with the skills side and the plugins side reconciled against each other before anything executed. |

The reconciliation step is the part hand-auditing always misses: several personal
skills were archive candidates *because "a plugin covers it"* — and the plugin
pass then flagged some of those very plugins for disabling. Auditing both sides
together caught the circular gap before it stranded any capability.

## Results — skills

**182 → 98 kept active. 84 retired.** Every retirement is a reversible archive
move, not a deletion.

| Outcome | Count | Why |
|---|---:|---|
| **Kept active** | 98 | Unique, working, best-in-class or a defensible niche |
| Archived — one large suite | 48 | A high-quality but dormant tool-suite that was one interdependent organism (same install date, shared broken refs, 87% of total disk). Kept or archived as a single unit — the user chose archive. |
| Archived — zero-risk sweep | 17 | Broken, empty, byte-for-byte duplicated by an enabled plugin, or generic reference docs fully superseded |
| Archived — redundant subsystem | 9 | Three parallel systems did the *same* job; the strongest was kept, the other two archived |
| **Merged into a keeper** | 4 | Content worth saving, folded into a better sibling, then the source archived |
| Archived — platform mismatch | 4 | Required hardware the machine doesn't have |
| Archived — superseded / broken | 2 | One had a better twin; one was silently broken (its data files were dangling links to a directory that no longer existed) |

Result: **skills on disk dropped from 1.5 GB to 14 MB** (466 MB of the total
turned out to be two bundled virtualenvs hiding inside "skills," relocated to the
archive — a thing no human scanning descriptions would ever have caught).

## Results — plugins

**67 → 25 kept enabled. 42 disabled** (all one-flag reversible settings toggles).

| Verdict | Count |
|---|---:|
| Keep enabled | 23 |
| Keep, trim internal noise | 2 |
| Disable — redundant | 22 |
| Disable — one orphaned vendor suite | 20 |

Disabling those 42 removes **142 skills, 17 agents, and 58 commands** from the
context of *every future session* — nearly the whole plugin bloat, with verified
coverage (nothing kept was left uncovered).

### Two findings that justify the whole exercise

- **An orphaned 20-plugin vendor suite** whose source directory had been
  *deleted* months earlier was still running from frozen cache — injecting ~180
  skills/agents/commands and **5 MCP server connections** into every session,
  two of them dead without paid data subscriptions the user didn't hold. Nobody
  had noticed.
- **One design skill was enabled three times** from three different marketplaces
  — hash-verified byte-identical — creating a three-way trigger collision on a
  single skill name.

## What "reversible" actually meant

Nothing was deleted. Skills were **moved** to an archive folder (the large suite
kept together as one restorable unit); plugins were **toggled** in settings; the
settings file was **backed up** before the first edit. The single true deletion
in the entire run was one empty, unreferenced directory. Every action has a
one-line undo, documented per-item.

## Where Fable 5 carried the work

This wasn't a one-shot prompt — it was a multi-hour, stateful engagement, and the
model-side demands were real:

- **Held a large, growing context** — 182 skills + 712 files + 67 plugins + 334
  cross-referenced plugin skills — without losing the thread across four passes
  and a live execution.
- **Fanned out and synthesized 17 parallel subagents**, then merged their
  independent overlap gradings into one coherent, non-contradictory verdict set.
- **Reconciled two audits against each other** — the skills↔plugins circular
  dependency that manual review reliably misses.
- **Caught its own mistakes at runtime.** Three planned actions changed mid-run
  when the ground truth disagreed with the plan: a skill slated for a *fix* was
  archived once inspection proved its data was gone; another "fix" was cancelled
  as a false positive from the inventory parser; a merge was reverted when its
  target got archived by a gate decision. Each deviation was surfaced and
  recorded, not silently applied.
- **Produced auditable, scripted, reversible changes** — every count in this
  document regenerates from a CSV, and every change has a documented rollback.

The payoff, in one line: **a 182-skill / 67-plugin estate that no human could
hold in their head went to 98 skills and 25 plugins, shedding ~200 items of
per-session context bloat and ~1.5 GB — with a full undo path for every step.**

---

*Methodology and scripts are in this repository. Figures are reported in
aggregate by category and outcome; no individual skill or plugin from the audited
system is named.*

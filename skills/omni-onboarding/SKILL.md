---
name: omni-onboarding
description: Sets up Omni for a new user in about ten minutes. Inventories the connected sources, creates the Omni Config and Omni Index in Notion, Google Drive or a local folder, seeds the index with a first backfill, pins the index location so later sessions find it, and runs a test query. Use when the user says "set up Omni", "onboard Omni", "start Omni", installs Omni for the first time, or when the omni skill finds no index. Also use to add a new source or move the index.
license: MIT
metadata:
  author: Bo Balachsan
  homepage: https://beborderless.io/
  version: 1.0.0
---

# Omni onboarding

Guides the user from nothing to a working Omni Index. Keep it light: one decision per step, sensible defaults, and a working index at the end even if the user skips the optional steps.

## Before starting

Check for an existing setup first (same lookup as the omni skill: pointers in context, then documents titled `Omni Config` or `Omni Index`, then `omni-config.md` in a local folder). If one exists, ask whether to **add sources**, **move the index**, or **start over**, and jump to the matching step. Never overwrite an existing index without an explicit yes.

Use the multiple-choice question tool when available; otherwise ask in plain text, one question at a time. If the user is not present to answer, take the defaults marked below, and say which ones you took.

## Workflow

Copy this checklist and tick it off:

```
Omni onboarding:
- [ ] 1. Explained what Omni does and its one limit
- [ ] 2. Sources inventoried and chosen
- [ ] 3. Index store chosen
- [ ] 4. Config and index created
- [ ] 5. Vocabulary seeded (optional)
- [ ] 6. First backfill done and validated
- [ ] 7. Index location pinned
- [ ] 8. Test query passed
```

### 1. Explain in three lines

Tell the user:
- Omni keeps one index of what exists across their tools, so one question can search everything.
- It reads sources live through connectors, and uses the index to know where to look.
- claude.ai Projects cannot read each other, so each Project joins Omni by running `omni-capture` once inside it.

### 2. Inventory sources

List what this session can actually reach: loaded or deferred connector tools (Notion, Google Drive, Slack, Gmail, calendars, meeting notes), connected local folders, the past-chat search tool, and the current Project. Present them as a checklist with the reachable ones preselected. Ask which to include and, for each, an optional scope (a database, a folder, a channel). Add any claude.ai Projects the user names as `project` sources with live search off.

If a source the user wants has no connector, note it in the config with live search off, and tell them which connector would enable it.

### 3. Choose the index store

Recommend in this order, based on what is connected:

1. **Notion database** (default when Notion is connected): structured fields, exact topic filters, easy to browse.
2. **Google Sheet** (default when only Drive is connected): simple, scales well.
3. **Markdown file in a local folder** (default when neither is available, or when the user prefers files): works with the bundled script; needs the desktop app connected for later sessions.
4. **Markdown doc in the current claude.ai Project**: only when nothing else is available; readable only inside this Project.

Store-specific setup is in [references/store-setup.md](references/store-setup.md).

### 4. Create config and index

Create both documents from the templates in `templates/`, filled with the choices from steps 2 and 3. For a local Markdown index:

```bash
python3 scripts/omni_index.py init <folder>/omni-index.md --owner "<name>"
```

then write `<folder>/omni-config.md` from `templates/omni-config.md`. Put the index link in the config and the config link in the index header.

### 5. Seed the vocabulary (optional, skip by default if the user is in a hurry)

Ask for three to five topics they search for often and any old names, acronyms or synonyms. Write them under `## Vocabulary` as `- preferred = synonym, synonym`.

### 6. First backfill

Follow [references/backfill.md](references/backfill.md). Default scope: the 10 to 20 most recently edited items per live source, plus the current Project's docs. Show the drafted entries as a compact table and ask for a yes before writing. Then validate (Markdown: `python3 scripts/omni_index.py validate <index>`; Notion or Drive: read the rows back) and fix every error.

For each other claude.ai Project the user listed, give them this prompt to paste once inside that Project:

> Run omni-capture for this whole Project. The Omni Config is at <config link>.

### 7. Pin the location

Later sessions must find the index without asking. Offer, in order of reach:
- A line in the user's preferences or memory: `Omni Config: <link>` (reaches every chat).
- The same line in each Project's instructions.
- For Claude Code, the same line in the user's `~/.claude/CLAUDE.md`.

Write it only where the user agrees. If you cannot write there yourself, give them the exact line to paste.

### 8. Test query

Run the omni skill on one topic that the backfill covered. Confirm it returns at least one finding with a working link. If it does not, fix the cause (wrong link, empty index, missing connector) before finishing.

## Finish

Close with: where the index and config live, how many entries were written, which sources are live versus capture-only, and the one next step (usually: run `omni-capture` in the other Projects). Do not recap every step.

## Reference files

- [references/store-setup.md](references/store-setup.md): creating the index in Notion, Google Drive, a local folder or a Project.
- [references/backfill.md](references/backfill.md): choosing what to backfill and drafting good entries quickly.
- [references/index-schema.md](references/index-schema.md): fields, store variants, config format.
- `templates/omni-config.md`, `templates/omni-index.md`: starting documents.

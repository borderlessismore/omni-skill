---
name: omni-capture
description: Writes entries into the Omni Index from the current context, so the material becomes findable from every other project and chat. Captures the current conversation's decisions and findings, a whole claude.ai Project's docs, or a specific document, deduplicates against existing entries, and validates the result. Use when the user says "capture this", "add this to Omni", "index this project", "remember this across projects", at the end of a working session worth keeping, or when the omni skill offers to capture new findings.
license: MIT
metadata:
  author: Bo Balachsan
  homepage: https://beborderless.io/
  version: 1.0.0
---

# Omni capture

Moves knowledge from where it was made into the shared Omni Index. This is the bridge that makes claude.ai Projects searchable from outside: run it inside a Project, and that Project's material becomes visible to Omni everywhere.

## Step 0: Locate the index

Use the same lookup as the omni skill: a pointer in context (`Omni Config:` or `Omni Index:`), then documents titled `Omni Config` or `Omni Index` in connected stores, then `omni-config.md` in a connected local folder. If none exists, offer to run `omni-onboarding` first; do not create an index silently.

Read the config's Vocabulary before drafting, so topics use the preferred terms.

## Choose the scope

| Request | Scope | Typical size |
|---|---|---|
| "capture this", end of session | Decisions, findings and new documents from this conversation | 1 to 5 entries |
| "index this project", "capture this Project" | Every doc in the current claude.ai Project, plus its instructions if substantive | 3 to 30 entries |
| "capture <doc or link>" | That item | 1 entry, or a parent plus children for collections |
| Follow-up from omni | The "not in index yet" findings Omni listed | as listed |

If the request is ambiguous, default to the conversation scope and mention that a whole-Project capture is available.

## Workflow

```
Omni capture:
- [ ] 0. Index, config and vocabulary loaded
- [ ] 1. Candidates gathered for the chosen scope
- [ ] 2. Deduplicated against the index
- [ ] 3. Entries drafted
- [ ] 4. User confirmed
- [ ] 5. Written and validated
- [ ] 6. Capture logged
```

1. **Gather candidates.** For a Project, list its docs with the Projects tool and read each one. For a conversation, pick only what will matter in a month: decisions with their reasons, conclusions of research, plans the user committed to, documents created. Skip chit-chat, abandoned drafts and Claude's unadopted suggestions.
2. **Deduplicate.** Search the index for each candidate's title and location. Same location → update that entry instead of adding. Same subject with newer content → new entry with `supersedes: <old id>`, and set the old entry's status to `superseded`.
3. **Draft entries** following [references/entry-guidelines.md](references/entry-guidelines.md) and the schema in [references/index-schema.md](references/index-schema.md).
4. **Confirm.** Show a compact table (action: add/update, title, kind, topics, date). For one or two entries, show them in full. Ask for a yes. When running unattended or when the user has said to capture without asking, write and report afterwards.
5. **Write and validate.** Markdown index: append with `python3 scripts/omni_index.py add <index> --title ... --kind ... --summary ... --topics ... --source ... --location ... --date ...` (one call per entry; it rejects invalid entries). To update an entry, edit its block in place and keep the id. Then run `validate`. Notion or Drive: write the rows, read them back, and check them against the schema. Fix every error before reporting done.
6. **Log.** Append one line under `## Capture log` in the config: `<date> · <source> · <n> added, <m> updated`.

## Locations for claude.ai Projects

Project docs have no public URL. Write the location as `claude.ai Project "<Project name>" → doc "<path>"` and the source as `project / <Project name>`. This is enough for the user, or for Omni running inside that Project, to reopen it.

## Rules

- Summaries carry substance (the verdict, the number, the open question), not "notes about X".
- Attribute decisions to the user only when the user stated or confirmed them; otherwise use kind `idea`.
- Never write sensitive personal details (health, finances, government IDs, private matters of other people) into the index, even when the source has them.
- Keep the user's titles and terms.
- Report what was skipped and why, in one line.

## Reference files

- [references/entry-guidelines.md](references/entry-guidelines.md): good and bad entries, kinds, collections, updates.
- [references/index-schema.md](references/index-schema.md): fields, store variants, config format.

---
name: omni
description: Answers questions across every source the user works in (Notion, Google Drive, Slack, local folders, past chats and captured claude.ai Projects) through one shared Omni Index, and returns linked findings grouped by source with conflicts and gaps called out. Use when the user asks what they know, decided, wrote or planned about a topic across all their projects or tools, asks where something lives, wants a timeline or the connections around a topic, or invokes /omni. Not for reading one document the user already pointed to.
license: MIT
metadata:
  author: Bo Balachsan
  homepage: https://beborderless.io/
  version: 1.0.0
---

# Omni

One question, every source. Omni finds what the user knows about a topic wherever it was written, using the **Omni Index** as a map and the user's connectors to open the originals.

## What Omni can and cannot reach

- It reads the Omni Index and every source listed in **Omni Config** that has a working connector or folder in this session.
- It cannot open other claude.ai Projects. Their content reaches Omni only through entries written by the `omni-capture` skill inside each Project. Say this plainly when a question depends on a Project that has not been captured.
- It never invents a location. Every finding links to where it can be reopened.

## Step 0: Locate the index

Find the config and index in this order, and stop at the first hit:

1. A pointer already in context: Project instructions, CLAUDE.md, user preferences or memory containing `Omni Config:` or `Omni Index:`.
2. A document titled exactly `Omni Config` in a connected store (Notion search, Drive search) or `omni-config.md` in a connected local folder.
3. A document titled `Omni Index` found the same way. Read its header for the config link.

If nothing is found, tell the user in one sentence that Omni has no index yet, and run the `omni-onboarding` skill. If that skill is not installed, follow its steps from this repository's `skills/omni-onboarding/SKILL.md` or offer a one-off live search of the connected sources, clearly labelled as unindexed.

## Workflow

Copy this checklist and tick it off:

```
Omni run:
- [ ] 0. Index and config located
- [ ] 1. Question framed (topic, synonyms, time range, source hints, mode)
- [ ] 2. Index searched and candidates ranked
- [ ] 3. Top candidates opened to verify (or reason recorded for not opening)
- [ ] 4. Live gap search in live-searchable sources
- [ ] 5. Answer written with links, conflicts and gaps
- [ ] 6. Offered to capture anything new
```

1. **Frame the question.** Extract the topic, expand it with the config Vocabulary (synonyms, old names, acronyms), note any time range or named source, and pick a mode (below). If the topic is too vague to search ("that thing"), ask one short question first.
2. **Search the index.** Markdown index: run `python3 scripts/omni_index.py search <index> "<query>" --config <config> --json`. Notion or Drive index: query the database or sheet by topic and title, then by summary text. Rank by relevance, then recency; keep superseded entries only to explain history.
3. **Verify.** Open the top three to five candidates through their connector and confirm the summary still holds. Skip opening only when the answer needs nothing beyond the summary, and say so. Details in [references/retrieval-playbook.md](references/retrieval-playbook.md).
4. **Fill gaps live.** Search each source marked `Include in live search: yes` for the topic. Anything found this way is labelled "not in index yet".
5. **Answer** using [references/answer-format.md](references/answer-format.md).
6. **Offer capture.** If step 4 found material missing from the index, or an entry proved stale, offer to add or update entries using the `omni-capture` skill. Do not write without a yes.

## Modes

| Mode | Trigger phrases | Output emphasis |
|---|---|---|
| **Brief** (default) | "what do I know about", "summarise everything on" | Synthesis first, then evidence by source |
| **Find** | "where is", "which doc", "where did I write" | Ranked list of locations, one line each |
| **Timeline** | "how did X evolve", "history of", "when did" | Dated sequence, decisions marked |
| **Connect** | "what relates to", "what am I missing", "links between" | Related entries that share topics or people but were never linked, with why each matters |
| **Audit** | "clean up the index", "what's stale" | Stale, duplicate and orphaned entries with proposed fixes; run `stats` for Markdown indexes |

## Rules

- Cite every claim to an entry or an opened source. Distinguish "the index says" from "the source says" when they differ, and treat the source as authoritative.
- Report conflicts between sources instead of silently picking one.
- Report what could not be checked: sources without a connector this session, uncaptured Projects, failed fetches.
- Keep summaries in the user's terms; reuse their titles.
- Never copy sensitive personal details from a source into the answer or the index unless the user asked for that exact detail.
- If a connector call fails, retry once, then continue with the rest and list it under gaps.

## Reference files

- [references/retrieval-playbook.md](references/retrieval-playbook.md): per-source search tactics, ranking, when to open originals.
- [references/answer-format.md](references/answer-format.md): answer templates for each mode, with an example.
- [references/index-schema.md](references/index-schema.md): entry fields, store variants, config format.

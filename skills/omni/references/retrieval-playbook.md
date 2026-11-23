# Retrieval playbook

How Omni searches each kind of source, ranks what it finds, and decides when to open an original.

Contents:
- Query building
- Per-source tactics
- Ranking
- When to open originals
- Failure handling

## Query building

1. Start from the user's words. Keep proper nouns and project names exactly as written.
2. Expand with the config Vocabulary: every term on a vocabulary line counts as the same concept.
3. Add obvious morphological variants yourself (plural, verb form) but not loose associations. "Pricing" may add "price" and "prices", not "revenue".
4. Keep queries short per source: two to four distinctive words beat a sentence.
5. Run two or three differently worded queries per source rather than one long one.

## Per-source tactics

| Source type | Search | Open | Notes |
|---|---|---|---|
| Omni Index (Markdown) | `scripts/omni_index.py search` with `--config`; add `--since`, `--source`, `--kind` filters when the question implies them | Read the entry block | Fastest path; always first |
| Omni Index (Notion) | Query the `Omni Index` database filtered on Topics and Title; then a text search on Summary | Fetch the row | Multi-select topics make filters exact |
| Omni Index (Drive Sheet) | Read the sheet values and filter in place | Read the row | For a Doc index, read it and search the text |
| Notion | Workspace search with the expanded terms, then fetch the top pages | Fetch page | Search returns titles and snippets; fetch before quoting |
| Google Drive | File search by name and full text | Read file content | Restrict to folders named in the config scope when given |
| Slack | Message search with the terms, then open the thread | Read thread | Decisions often live in replies, not the first message |
| Gmail | Thread search with terms plus a sender or date filter when known | Read thread | Quote sparingly |
| Meetings (Otter, Wispr Flow, Calendly notes) | Transcript or note search | Open the note at the match | Attribute statements to speakers only when the transcript labels them |
| Local folder | `grep -ril` for the terms inside the connected folder, then read matches | Read file | Respect the config scope |
| Past chats | Past-chat search tool with content words | Open the chat at the hit | Your past suggestions are not the user's decisions |
| claude.ai Projects | Only through index entries, plus the current Project's own docs | Current Project only | Name uncaptured Projects as a gap |
| Web | Only when the user asks for outside context | Fetch page | Label clearly as external |

Load a connector's tools only when its source is relevant to the question.

## Ranking

Order candidates by:

1. **Match strength**: title and topic matches over summary matches; all concepts matched over some.
2. **Kind fit**: for "what did we decide", `decision` entries first; for "where is", `doc` entries first.
3. **Recency**: newer first when strength is equal.
4. **Status**: `active` over `done`; `superseded` and `archived` only to show history.

Group near-duplicates (same title or same location across sources) into one finding with several locations.

## When to open originals

Open the source when any of these hold:

- The answer will quote or rely on a specific number, decision or date.
- The entry is older than six months, or marked `superseded`.
- Two entries disagree.
- The user asked for detail beyond the summary.

Answer from summaries alone only for Find mode or a quick overview, and say that the sources were not reopened.

Cap opening at five originals per question unless the user asks for depth. If more look relevant, list them and offer to go deeper.

## Failure handling

- Connector error: retry once, then move on and list the source under gaps.
- Index missing or unreadable: switch to a live search across live-searchable sources, label the whole answer "unindexed", and offer onboarding.
- Index location stale (moved or deleted original): report it in the answer and offer an Audit run.

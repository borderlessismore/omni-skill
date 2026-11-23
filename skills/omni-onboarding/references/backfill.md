# Backfill

The first backfill makes Omni useful on day one. Aim for coverage of what the user touches most, not completeness.

## Choose the scope

| Source | Default first pass |
|---|---|
| Current claude.ai Project | Every doc |
| Notion | 15 most recently edited pages in the scoped databases or pages |
| Google Drive | 15 most recently modified files in the scoped folders |
| Slack | Pinned messages and threads with decisions in the scoped channels, last 60 days |
| Meeting notes | 10 most recent meetings |
| Local folder | Up to 20 most recently modified documents, skipping code, binaries and archives |
| Past chats | Skip by default; offer as a later step |

Ask before going beyond 50 entries in one session; larger backfills run better as one batch per source.

## Draft entries quickly

For each item:

1. Read the title and the first screen of content. Open further only if the point is unclear.
2. Pick one `kind`. A doc that records a choice is a `decision`; a brainstorm list is an `idea` (or one entry per idea when ideas are clearly separate and substantial).
3. Write a summary that carries the substance: the verdict, the number, the open question. "Notes about pricing" is useless; "Two tiers at EUR 29 and EUR 79; annual discount undecided" is useful.
4. Reuse existing topics and the vocabulary's preferred terms.
5. Use the most direct location available: page URL, file URL, file path, or Project plus doc name.
6. Date it by the content's own date, falling back to the last-edited date.

## Collections

A single document that collects many items (an idea backlog, a meeting series summary) gets one parent entry of kind `reference`, plus separate entries only for items with real substance. Put the parent's id in each child's notes, not in a new field.

## Confirm, write, validate

1. Show drafts as a table: title, kind, topics, source, date. Summaries can be collapsed for long lists.
2. Apply the user's edits; drop rejected rows.
3. Write in one batch.
4. Validate and fix every error before reporting success.
5. Report the count per source and anything skipped and why.

# Omni index schema

The index is one document, the **Omni Index**, that lists what exists across your sources and where to reopen it. It never stores full content: each entry is a pointer plus a short summary. The config document, **Omni Config**, lists the sources and where the index lives.

Contents:
- Entry format
- Field rules
- Store variants (Markdown, Notion, Google Drive)
- Config format
- Validation

## Entry format

The canonical form is Markdown. Every store variant maps to these same fields.

```markdown
## omni-20260514-membership-pricing-decision · Membership pricing decision
- kind: decision
- summary: Two tiers at EUR 29 and EUR 79 a month. The middle tier was dropped after member interviews.
- topics: pricing, membership, community
- source: notion / Team workspace
- location: https://www.notion.so/example-page-id
- date: 2026-05-14
- status: active
- captured: 2026-05-20
```

One entry per `##` heading. The heading is `## <id> · <title>`. Fields are `- key: value` lines directly under it. Anything else under an entry (notes, sub-bullets) is ignored by tooling but kept.

## Field rules

| Field | Required | Rule |
|---|---|---|
| `id` | yes | `omni-YYYYMMDD-<slug>`. Date is the capture date. Slug is lowercase letters, digits and hyphens. Unique. |
| `title` | yes | Human title, as the source names it where possible. |
| `kind` | yes | One of: `idea`, `decision`, `doc`, `meeting`, `project`, `person`, `fact`, `task`, `reference`. |
| `summary` | yes | One to three sentences, max 400 characters. What it says, not that it exists. Include the verdict or key number when there is one. |
| `topics` | yes | Comma-separated, lowercase. Prefer topics already in the index or the config vocabulary over new synonyms. |
| `source` | yes | `<type> / <name>`. Types: `project`, `notion`, `drive`, `slack`, `gmail`, `calendar`, `meeting`, `local`, `chat`, `web`, `other`. |
| `location` | yes | How to reopen it: a URL, a file path, or a precise description such as Project name plus doc name. Never "see above". |
| `date` | yes | ISO `YYYY-MM-DD`. The date of the content, not of capture. Use the best known date. |
| `status` | no | `active` (default), `done`, `archived`, `superseded`. |
| `supersedes` | no | Id of an older entry this one replaces. |
| `captured` | no | ISO date the entry was written. |

Privacy: summaries describe work, not private lives. Do not write health, financial-account, government-ID or other sensitive personal details about anyone into the index, even when the source contains them. Point to the source instead.

## Store variants

**Markdown file (local folder or a Project doc).** Use the format above as-is. File name `omni-index.md`. The bundled script (`scripts/omni_index.py`) validates and searches it.

**Notion database.** Title the database `Omni Index`. Properties:

| Property | Notion type |
|---|---|
| Title | Title (`<title>`) |
| Omni ID | Text |
| Kind | Select |
| Summary | Text |
| Topics | Multi-select |
| Source type | Select |
| Source name | Text |
| Location | URL (or Text when not a URL) |
| Date | Date |
| Status | Select |
| Supersedes | Text |
| Captured | Date |

**Google Drive.** A Google Doc titled `Omni Index` using the Markdown format, or a Google Sheet titled `Omni Index` with one column per field in the order of the table above. Prefer the Sheet once the index passes about 200 entries.

## Config format

The config is a short Markdown document titled `Omni Config` (file `omni-config.md` locally), stored next to the index.

```markdown
# Omni Config
- index: <link or path to the Omni Index>
- store: markdown | notion | drive
- owner: <name>
- created: 2026-11-23

## Sources
| Name | Type | Scope | How to search | Include in live search |
|---|---|---|---|---|
| Community | project | whole Project | capture only (no cross-Project access) | no |
| Team workspace | notion | Decisions and Ideas databases | Notion search, then fetch | yes |
| Shared drive | drive | folder "Programs" | Drive search, then read | yes |

## Vocabulary
- pricing = price, tiers, plans
- community = members, club
```

`Include in live search: no` marks sources Omni can only see through captured entries, such as other claude.ai Projects.

The vocabulary maps preferred topics (left) to synonyms and old names (right). Omni expands queries with it, and capture normalises topics to the left-hand term.

## Validation

For Markdown indexes, run:

```bash
python3 scripts/omni_index.py validate omni-index.md
```

It checks required fields, id format, ISO dates, allowed kinds and source types, duplicate ids, and duplicate locations. Fix every error before reporting a write as done. For Notion and Drive, apply the same rules by reading the entries back after writing.

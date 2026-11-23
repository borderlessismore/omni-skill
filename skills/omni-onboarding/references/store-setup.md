# Store setup

How to create the Omni Index and Omni Config in each store. Field definitions are in [index-schema.md](index-schema.md).

Contents:
- Notion
- Google Drive
- Local folder
- claude.ai Project doc
- Moving an index

## Notion

1. Ask where to put it, or default to a private top-level page named `Omni`.
2. Under that page, create a database titled exactly `Omni Index` with the properties in the schema table. Pre-fill the select options: Kind (`idea`, `decision`, `doc`, `meeting`, `project`, `person`, `fact`, `task`, `reference`), Source type (`project`, `notion`, `drive`, `slack`, `gmail`, `calendar`, `meeting`, `local`, `chat`, `web`, `other`), Status (`active`, `done`, `archived`, `superseded`).
3. Create a page titled exactly `Omni Config` next to it, using `templates/omni-config.md`, with `store: notion` and the database link as `index`.
4. Add a short description to the database: `Maintained by Omni. Config: <config link>`.
5. Check: query the empty database once to confirm the properties exist with the right types.

## Google Drive

Default to a Google Sheet:

1. Create a folder `Omni` in My Drive (or the folder the user names).
2. Create a Sheet titled exactly `Omni Index`. Row 1 headers, in order: `id, title, kind, summary, topics, source, location, date, status, supersedes, captured`. Freeze row 1.
3. Create a Google Doc titled exactly `Omni Config` from `templates/omni-config.md`, with `store: drive` and the Sheet link as `index`.
4. Check: read row 1 back.

Use a Google Doc index (Markdown format as text) only if the user prefers a document.

## Local folder

1. Use a connected folder the user picks; default to an `Omni` subfolder inside it.
2. `python3 scripts/omni_index.py init <folder>/omni-index.md --owner "<name>"`
3. Write `<folder>/omni-config.md` from the template with `store: markdown`.
4. Check: `python3 scripts/omni_index.py validate <folder>/omni-index.md` reports 0 entries, 0 errors.

When the folder is on the user's computer, run the script there if a device shell is available; otherwise stage the file into the workspace, run it, and write the result back. Tell the user later sessions need the desktop app connected to reach this folder.

## claude.ai Project doc

Only when nothing else is available. Write `omni-index.md` and `omni-config.md` as Project docs. Warn the user once: the index is then readable only inside this Project, which defeats most of Omni's purpose; suggest moving it when a connector becomes available.

## Moving an index

1. Create the new store as above.
2. Copy every entry, keeping ids unchanged.
3. Validate the new copy and compare entry counts.
4. Update `index` in the config, update every pinned pointer, and add `Moved to <new link> on <date>` at the top of the old index. Do not delete the old index; leave that to the user.

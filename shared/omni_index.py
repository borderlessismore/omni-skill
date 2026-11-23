#!/usr/bin/env python3
"""Omni index tool: create, validate, search, add to and summarise a Markdown Omni Index.

Standard library only (Python 3.8+). The format is defined in references/index-schema.md.

Usage:
  omni_index.py init     INDEX [--owner NAME]
  omni_index.py validate INDEX [--json]
  omni_index.py search   INDEX QUERY [--config CONFIG] [--source TYPE] [--kind KIND]
                                     [--since YYYY-MM-DD] [--status STATUS] [--limit N] [--json]
  omni_index.py add      INDEX --title T --kind K --summary S --topics "a, b"
                               --source "type / name" --location L --date YYYY-MM-DD
                               [--status S] [--supersedes ID]
  omni_index.py stats    INDEX [--stale-days N] [--json]

Exit codes: 0 ok, 1 validation errors or no results, 2 usage or file errors.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REQUIRED = ["kind", "summary", "topics", "source", "location", "date"]
KINDS = {"idea", "decision", "doc", "meeting", "project", "person", "fact", "task", "reference"}
SOURCE_TYPES = {"project", "notion", "drive", "slack", "gmail", "calendar", "meeting",
                "local", "chat", "web", "other"}
STATUSES = {"active", "done", "archived", "superseded"}
ID_RE = re.compile(r"^omni-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADING_RE = re.compile(r"^##\s+(\S+)\s+·\s+(.+?)\s*$")
FIELD_RE = re.compile(r"^-\s+([a-z_]+):\s*(.*?)\s*$")
MAX_SUMMARY = 400

# Search weights per field: a query term found in the title counts more than one in the summary.
WEIGHTS = {"title": 5.0, "topics": 4.0, "summary": 2.0, "source": 1.5, "location": 1.0, "kind": 1.0}

TEMPLATE = """# Omni Index

Maintained by Omni. One entry per `##` heading; format in references/index-schema.md.
Owner: {owner}
Created: {created}

"""


# ---------------------------------------------------------------- parsing

def parse_index(text: str) -> list[dict]:
    """Return entries as dicts with id, title, line, and every field found."""
    entries: list[dict] = []
    current: dict | None = None
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        heading = HEADING_RE.match(line)
        if heading:
            current = {"id": heading.group(1), "title": heading.group(2), "line": lineno}
            entries.append(current)
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None  # a non-entry heading ends the entry
            continue
        if current is not None:
            field = FIELD_RE.match(line)
            if field and field.group(1) not in current:
                current[field.group(1)] = field.group(2)
    return entries


def parse_vocabulary(text: str) -> dict[str, set[str]]:
    """Read `- term = synonym, synonym` lines under a '## Vocabulary' heading."""
    groups: dict[str, set[str]] = {}
    in_vocab = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            in_vocab = line[3:].strip().lower() == "vocabulary"
            continue
        if in_vocab and line.startswith("- ") and "=" in line:
            left, right = line[2:].split("=", 1)
            terms = {left.strip().lower()} | {t.strip().lower() for t in right.split(",") if t.strip()}
            for term in terms:
                groups.setdefault(term, set()).update(terms)
    return groups


def read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        die(f"file not found: {path}")
    except OSError as exc:
        die(f"cannot read {path}: {exc}")
    return ""  # unreachable


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- validation

def validate_entries(entries: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, int] = {}
    seen_locations: dict[str, str] = {}
    for e in entries:
        where = f"line {e['line']} ({e['id']})"
        if not ID_RE.match(e["id"]):
            errors.append(f"{where}: id must look like omni-YYYYMMDD-slug")
        elif not valid_date(e["id"][5:9] + "-" + e["id"][9:11] + "-" + e["id"][11:13]):
            errors.append(f"{where}: id contains an impossible date")
        if e["id"] in seen_ids:
            errors.append(f"{where}: duplicate id (first at line {seen_ids[e['id']]})")
        seen_ids.setdefault(e["id"], e["line"])
        for key in REQUIRED:
            if not e.get(key):
                errors.append(f"{where}: missing '{key}'")
        if e.get("kind") and e["kind"] not in KINDS:
            errors.append(f"{where}: kind '{e['kind']}' not in {sorted(KINDS)}")
        if e.get("summary") and len(e["summary"]) > MAX_SUMMARY:
            errors.append(f"{where}: summary is {len(e['summary'])} chars (max {MAX_SUMMARY})")
        if e.get("source"):
            stype = e["source"].split("/", 1)[0].strip()
            if "/" not in e["source"] or not e["source"].split("/", 1)[1].strip():
                errors.append(f"{where}: source must be '<type> / <name>'")
            elif stype not in SOURCE_TYPES:
                errors.append(f"{where}: source type '{stype}' not in {sorted(SOURCE_TYPES)}")
        for key in ("date", "captured"):
            if e.get(key) and not valid_date(e[key]):
                errors.append(f"{where}: {key} '{e[key]}' is not a valid YYYY-MM-DD date")
        if e.get("status") and e["status"] not in STATUSES:
            errors.append(f"{where}: status '{e['status']}' not in {sorted(STATUSES)}")
        if e.get("supersedes") and e["supersedes"] not in seen_ids and \
                e["supersedes"] not in {x["id"] for x in entries}:
            errors.append(f"{where}: supersedes unknown id '{e['supersedes']}'")
        loc = (e.get("location") or "").strip().lower()
        if loc:
            if loc in seen_locations and e.get("status", "active") == "active":
                errors.append(f"{where}: same location as {seen_locations[loc]} (possible duplicate)")
            seen_locations.setdefault(loc, e["id"])
    return errors


def valid_date(value: str) -> bool:
    if not DATE_RE.match(value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------- search

def tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9äöüßéèàçñ]+", text.lower()) if len(t) > 1]


def expand(query: str, vocab: dict[str, set[str]]) -> list[set[str]]:
    """Each query concept becomes a set of alternative token-phrases (synonyms)."""
    q = query.lower()
    concepts: list[set[str]] = []
    used: set[str] = set()
    # Multi-word vocabulary terms first, longest first.
    for term in sorted(vocab, key=len, reverse=True):
        if " " in term and term in q and term not in used:
            concepts.append(vocab[term])
            used |= vocab[term]
            q = q.replace(term, " ")
    for tok in tokens(q):
        concepts.append(vocab.get(tok, {tok}))
    return concepts


def score_entry(entry: dict, concepts: list[set[str]]) -> float:
    total = 0.0
    matched = 0
    for alternatives in concepts:
        best = 0.0
        for field, weight in WEIGHTS.items():
            haystack = (entry.get(field) or "").lower()
            for alt in alternatives:
                if alt and alt in haystack:
                    exact = alt in tokens(haystack) or " " in alt
                    best = max(best, weight * (1.0 if exact else 0.6))
        if best:
            matched += 1
        total += best
    if not concepts:
        return 0.0
    coverage = matched / len(concepts)
    if entry.get("status") in ("archived", "superseded"):
        total *= 0.5
    return round(total * (0.5 + coverage), 3)


def search(entries, query, vocab, source=None, kind=None, since=None, status=None, limit=10):
    concepts = expand(query, vocab)
    results = []
    for e in entries:
        if source and not (e.get("source") or "").startswith(source):
            continue
        if kind and e.get("kind") != kind:
            continue
        if status and e.get("status", "active") != status:
            continue
        if since and (e.get("date") or "") < since:
            continue
        s = score_entry(e, concepts)
        if s > 0:
            results.append((s, e))
    # Newest first among equal scores: sort by date, then (stable) by score.
    results.sort(key=lambda pair: pair[1].get("date", ""), reverse=True)
    results.sort(key=lambda pair: pair[0], reverse=True)
    return results[:limit]


# ---------------------------------------------------------------- commands

def cmd_init(args) -> int:
    path = Path(args.index)
    if path.exists():
        die(f"{path} already exists; not overwriting")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(owner=args.owner or "unknown",
                                    created=dt.date.today().isoformat()), encoding="utf-8")
    print(f"created {path}")
    return 0


def cmd_validate(args) -> int:
    entries = parse_index(read(args.index))
    errors = validate_entries(entries)
    if args.json:
        print(json.dumps({"entries": len(entries), "errors": errors}, indent=2))
    else:
        for err in errors:
            print(err)
        print(f"{len(entries)} entries, {len(errors)} errors")
    return 1 if errors else 0


def cmd_search(args) -> int:
    entries = parse_index(read(args.index))
    vocab = parse_vocabulary(read(args.config)) if args.config else {}
    results = search(entries, args.query, vocab, args.source, args.kind, args.since,
                     args.status, args.limit)
    if args.json:
        print(json.dumps([{"score": s, **{k: v for k, v in e.items() if k != "line"}}
                          for s, e in results], indent=2, ensure_ascii=False))
    else:
        if not results:
            print("no matches")
        for s, e in results:
            print(f"[{s:>6}] {e['id']} · {e['title']}")
            print(f"         {e.get('kind', '?')} | {e.get('source', '?')} | {e.get('date', '?')}"
                  f" | {e.get('status', 'active')}")
            print(f"         {e.get('summary', '')}")
            print(f"         -> {e.get('location', '')}")
    return 0 if results else 1


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return "-".join(slug.split("-")[:6]) or "entry"


def cmd_add(args) -> int:
    path = Path(args.index)
    text = read(args.index)
    entries = parse_index(text)
    today = dt.date.today()
    base = f"omni-{today:%Y%m%d}-{slugify(args.title)}"
    existing = {e["id"] for e in entries}
    new_id, n = base, 2
    while new_id in existing:
        new_id, n = f"{base}-{n}", n + 1
    fields = {
        "kind": args.kind, "summary": args.summary, "topics": args.topics.lower(),
        "source": args.source, "location": args.location, "date": args.date,
        "status": args.status, "supersedes": args.supersedes, "captured": today.isoformat(),
    }
    block = [f"## {new_id} · {args.title}"] + [f"- {k}: {v}" for k, v in fields.items() if v]
    candidate = {"id": new_id, "title": args.title, "line": 0,
                 **{k: v for k, v in fields.items() if v}}
    errors = validate_entries(entries + [candidate])
    errors = [e for e in errors if new_id in e]
    if errors:
        for err in errors:
            print(err.replace("line 0 ", "new entry "))
        print("not added")
        return 1
    sep = "" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
    path.write_text(text + sep + "\n".join(block) + "\n", encoding="utf-8")
    print(new_id)
    return 0


def cmd_stats(args) -> int:
    entries = parse_index(read(args.index))
    by_source: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    stale = []
    cutoff = (dt.date.today() - dt.timedelta(days=args.stale_days)).isoformat()
    for e in entries:
        stype = (e.get("source") or "unknown").split("/", 1)[0].strip()
        by_source[stype] = by_source.get(stype, 0) + 1
        by_kind[e.get("kind", "unknown")] = by_kind.get(e.get("kind", "unknown"), 0) + 1
        for t in (e.get("topics") or "").split(","):
            if t.strip():
                by_topic[t.strip()] = by_topic.get(t.strip(), 0) + 1
        if e.get("status", "active") == "active" and (e.get("date") or "9999") < cutoff:
            stale.append(e["id"])
    report = {
        "entries": len(entries),
        "by_source": dict(sorted(by_source.items(), key=lambda kv: -kv[1])),
        "by_kind": dict(sorted(by_kind.items(), key=lambda kv: -kv[1])),
        "top_topics": dict(sorted(by_topic.items(), key=lambda kv: -kv[1])[:15]),
        f"active_older_than_{args.stale_days}_days": stale,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for key, value in report.items():
            print(f"{key}: {value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Work with a Markdown Omni Index.")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("init", help="create an empty index")
    s.add_argument("index")
    s.add_argument("--owner")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("validate", help="check entries against the schema")
    s.add_argument("index")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("search", help="ranked search with optional synonym expansion")
    s.add_argument("index")
    s.add_argument("query")
    s.add_argument("--config", help="Omni Config file whose Vocabulary expands the query")
    s.add_argument("--source", help="source type prefix, e.g. notion")
    s.add_argument("--kind", choices=sorted(KINDS))
    s.add_argument("--since", help="only entries dated on or after YYYY-MM-DD")
    s.add_argument("--status", choices=sorted(STATUSES))
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("add", help="append a validated entry")
    s.add_argument("index")
    for name in ("title", "summary", "topics", "source", "location", "date"):
        s.add_argument(f"--{name}", required=True)
    s.add_argument("--kind", required=True, choices=sorted(KINDS))
    s.add_argument("--status", choices=sorted(STATUSES))
    s.add_argument("--supersedes")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("stats", help="counts by source, kind and topic; stale entries")
    s.add_argument("index")
    s.add_argument("--stale-days", type=int, default=180)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_stats)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

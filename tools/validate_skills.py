#!/usr/bin/env python3
"""Lint every skills/*/SKILL.md against the Agent Skills rules and repository conventions.

Checks: frontmatter present and parseable; name matches folder, <= 64 chars, lowercase
letters/digits/hyphens, no reserved words; description present, <= 1024 chars, no angle
brackets, says when to use it; body under 500 lines; every relative link resolves;
plugin and marketplace manifests are valid JSON and agree on the version.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
RESERVED = ("anthropic", "claude")


def frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated frontmatter")
    meta: dict = {}
    for line in text[4:end].splitlines():
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, text[end + 5:]


def check_skill(skill_dir: Path) -> list[str]:
    errors = []
    path = skill_dir / "SKILL.md"
    rel = path.relative_to(ROOT)
    if not path.exists():
        return [f"{rel}: missing"]
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = frontmatter(text)
    except ValueError as exc:
        return [f"{rel}: {exc}"]
    name, desc = meta.get("name", ""), meta.get("description", "")
    if name != skill_dir.name:
        errors.append(f"{rel}: name '{name}' must match folder '{skill_dir.name}'")
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{rel}: name must be <= 64 chars of lowercase letters, digits, hyphens")
    if any(word in name for word in RESERVED):
        errors.append(f"{rel}: name must not contain {RESERVED}")
    if not desc:
        errors.append(f"{rel}: description missing")
    if len(desc) > 1024:
        errors.append(f"{rel}: description is {len(desc)} chars (max 1024)")
    if "<" in desc or ">" in desc:
        errors.append(f"{rel}: description must not contain angle brackets")
    if "Use when" not in desc:
        errors.append(f"{rel}: description should say when to use the skill ('Use when ...')")
    lines = body.count("\n")
    if lines > 500:
        errors.append(f"{rel}: body is {lines} lines (keep under 500; move detail to references/)")
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith(("mailto:", "<", "{{")):
            continue
        if not (skill_dir / target).exists():
            errors.append(f"{rel}: broken link '{target}'")
    for ref in (skill_dir / "references").glob("*.md") if (skill_dir / "references").exists() else []:
        for target in LINK_RE.findall(ref.read_text(encoding="utf-8")):
            if "://" in target or target.startswith(("<", "{{")):
                continue
            if not (ref.parent / target).exists():
                errors.append(f"{ref.relative_to(ROOT)}: broken link '{target}'")
    return errors


def check_manifests() -> list[str]:
    errors = []
    versions = {}
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        try:
            data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: {exc}")
            continue
        if rel.endswith("plugin.json"):
            versions["plugin"] = data.get("version")
        else:
            for plugin in data.get("plugins", []):
                if plugin.get("name") == "omni":
                    versions["marketplace"] = plugin.get("version")
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        meta, _ = frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^\s+version:\s*(\S+)", text, re.M)
        if match:
            versions[skill_dir.name] = match.group(1)
    if len(set(versions.values())) > 1:
        errors.append(f"version mismatch: {versions}")
    return errors


def main() -> int:
    errors = []
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    for skill_dir in skills:
        errors += check_skill(skill_dir)
    errors += check_manifests()
    for err in errors:
        print(err)
    print(f"{len(skills)} skills checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Package each skill as a ZIP for upload to claude.ai (Settings → Capabilities → Skills).

Each archive contains a single top-level folder named after the skill, which is the
layout claude.ai expects. Output goes to dist/.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SKIP = {"__pycache__", ".DS_Store"}


def main() -> int:
    DIST.mkdir(exist_ok=True)
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not (skill_dir / "SKILL.md").exists():
            continue
        out = DIST / f"{skill_dir.name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(skill_dir.rglob("*")):
                if path.is_file() and not SKIP.intersection(path.parts) and path.suffix != ".pyc":
                    zf.write(path, Path(skill_dir.name) / path.relative_to(skill_dir))
        print(f"built {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

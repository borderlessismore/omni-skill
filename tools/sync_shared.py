#!/usr/bin/env python3
"""Copy shared files into every skill so each skill folder is self-contained.

claude.ai installs each skill as a separate upload, so a skill cannot reference files
outside its own folder. `shared/` is the single source of truth; this script copies it
into each skill. Run with --check in CI to fail when a copy has drifted.
"""

from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"
SKILLS = ["omni", "omni-onboarding", "omni-capture"]
FILES = {
    "index-schema.md": "references/index-schema.md",
    "omni_index.py": "scripts/omni_index.py",
}


def main() -> int:
    check = "--check" in sys.argv
    drift = []
    for skill in SKILLS:
        for src_name, rel_dest in FILES.items():
            src = SHARED / src_name
            dest = ROOT / "skills" / skill / rel_dest
            if check:
                if not dest.exists() or not filecmp.cmp(src, dest, shallow=False):
                    drift.append(str(dest.relative_to(ROOT)))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
    if check:
        if drift:
            print("Out of sync with shared/ (run: python3 tools/sync_shared.py):")
            for path in drift:
                print(f"  {path}")
            return 1
        print("shared files in sync")
        return 0
    print(f"synced {len(FILES)} files into {len(SKILLS)} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())

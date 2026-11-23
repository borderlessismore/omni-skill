# Contributing to Omni

Thanks for helping. Omni is small on purpose: three focused skills, one index format, one stdlib script. Changes that keep it that way are the easiest to accept.

## Ways to help

- **Report a miss.** Omni answered wrongly, missed a source or invented a location. Open an issue with the question you asked, what you expected and what it did.
- **Add a source adapter.** New tactics for a connector go in `skills/omni/references/retrieval-playbook.md`.
- **Improve the script.** `shared/omni_index.py` must stay standard-library only and Python 3.10+ compatible.

## Rules for skill changes

1. **Keep SKILL.md lean.** Each body stays under 500 lines; move detail into `references/`, one level deep.
2. **Descriptions say what and when**, in the third person, under 1024 characters, without angle brackets, and include "Use when".
3. **Edit shared files in `shared/`, never in a skill folder**, then run `python3 tools/sync_shared.py`. CI fails if copies drift.
4. **Keep versions in step.** Bump the version in all three SKILL.md files, `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` together, and add a CHANGELOG entry.
5. **No real personal data in examples.** Use the fictional company in `examples/`.

## Before opening a pull request

```bash
python3 tools/sync_shared.py
python3 tools/validate_skills.py
python3 -m unittest discover -s tests
```

## Testing behaviour

`evals/evals.json` lists scenarios with the behaviour each skill should show. For a change to a skill's instructions:

1. Install your branch locally (`cp -r skills/* ~/.claude/skills/`).
2. Run the scenarios for that skill in a fresh session, with and without your change.
3. Note in the pull request which expected behaviours improved or regressed.

Add a scenario for every bug you fix.

## Releasing (maintainers)

1. Update versions and `CHANGELOG.md`.
2. Tag: `git tag v1.x.y && git push origin v1.x.y`.
3. The release workflow builds the ZIPs and attaches them to the GitHub release.

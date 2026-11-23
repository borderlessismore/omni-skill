# Answer format

Every Omni answer has the same spine, so the user can scan it the same way each time. Scale it to the question: a Find answer may be five lines.

## Spine

```markdown
**<One-sentence answer to the question.>**

<2–4 sentences of synthesis: what is known, what was decided, what is still open.>

### Findings
- **<Title>** (<source type> · <date>): <what it says, one or two sentences>. [Open](<location>)
- ...

### Conflicts
- <Source A> says <x>; <Source B> says <y>. <Which is newer or more authoritative, if clear.>

### Gaps
- <Sources not checked and why: no connector, uncaptured Project, failed fetch.>
- <Things searched for and not found.>

<One offer: capture new findings, go deeper on one item, or run an Audit.>
```

Omit Conflicts or Gaps only when there are none. A missing Gaps section tells the user that everything listed in the config was checked, so do not drop it out of tidiness.

## Mode variations

- **Find**: replace the synthesis with a ranked list: `1. <Title> · <source> · <date> · [Open](<location>)`.
- **Timeline**: replace Findings with a dated list, oldest first, marking decisions with **Decision:**.
- **Connect**: after the synthesis, add `### Connections`, one bullet per link: `<Entry A> ↔ <Entry B>: <shared topic or person>, <why it matters>`.
- **Audit**: a table with columns Entry, Problem (stale / duplicate / broken location / missing field), Proposed fix. Ask before applying fixes.

## Labels

- `(index only)` after a finding whose source was not reopened.
- `(not in index yet)` after a finding from live search.
- `(superseded by <id>)` for history items.

## Example

User: "What have we decided about membership pricing, across everything?"

```markdown
**You settled on two tiers at EUR 29 and EUR 79 a month, but the annual discount is still open.**

Pricing was first sketched in a March workshop with three tiers, cut to two in May after member interviews. The May decision doc sets the prices; a later Slack thread proposes a 20% annual discount that no document confirms.

### Findings
- **Membership pricing decision** (notion · 2026-05-14): Two tiers, EUR 29 and EUR 79 monthly; the middle tier was dropped after interviews. [Open](https://www.notion.so/example)
- **Pricing workshop notes** (meeting · 2026-03-02): First sketch with three tiers. (superseded by omni-20260514-membership-pricing-decision) [Open](https://otter.ai/example)
- **Annual discount thread** (slack · 2026-06-03): Proposal for 20% off annual plans, no reply recorded. (not in index yet) [Open](https://slack.com/example)

### Conflicts
- The workshop notes list three tiers; the May decision lists two. The May decision is newer and marked as the decision.

### Gaps
- The "Community" claude.ai Project has not been captured, so its notes were not searched.

Want me to capture the Slack thread so it shows up next time?
```

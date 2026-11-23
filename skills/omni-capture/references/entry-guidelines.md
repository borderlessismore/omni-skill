# Entry guidelines

A good entry lets someone decide, from the index alone, whether to open the source. Write for a reader in six months who has forgotten the context.

## Summary: substance over existence

| Bad | Good |
|---|---|
| Notes from the pricing meeting. | Pricing cut from three tiers to two (EUR 29, EUR 79); annual discount left open. |
| Research on competitors. | Five competitors compared; none combine facilitation with a mapping tool; closest is priced at EUR 9/month. |
| Ideas for the newsletter. | 12 newsletter ideas; the user starred "member spotlights" and "monthly teardown". |
| A doc about onboarding. | Onboarding plan: 3 emails over 10 days, first call in week one, owner is the community lead. |

Rules of thumb: lead with the conclusion; include one concrete number or name when there is one; state what is still open.

## Choosing a kind

| Kind | Use for |
|---|---|
| `decision` | A choice the user made or confirmed, with its reason |
| `idea` | A proposal or concept not yet decided |
| `doc` | A substantial document whose value is its whole content (spec, plan, report) |
| `meeting` | A meeting's outcomes; link the transcript or notes |
| `project` | An ongoing effort, as a hub entry other entries can share topics with |
| `person` | A working relationship worth finding again (role, context); never private details |
| `fact` | A stable piece of information (a figure, a constraint, a policy) |
| `task` | A commitment with an owner and due date, when the user wants it findable |
| `reference` | A collection or index document pointing to many items |

When in doubt between `doc` and `decision`, ask: will the user search for the choice or for the document? Index what they will search for.

## Topics

- Two to five per entry.
- Lowercase, singular where natural (`pricing`, not `Prices`).
- Prefer the config Vocabulary's preferred term; add a new vocabulary line when a new synonym appears more than once.
- Include the project or initiative name as a topic, so Connect mode can link entries across sources.

## Collections

For a document that collects many items (idea backlog, meeting-series digest, research dump):

1. One `reference` entry for the collection itself.
2. Separate entries only for items with substance (a described concept, a decision, a status). Leave title-only items inside the parent.
3. Each child's location points to the parent document plus the item's heading.

## Updates and history

- Content changed, same location: edit the existing entry's summary and date; keep the id.
- Content replaced by a newer document: new entry with `supersedes: <old id>`; set the old entry to `superseded`.
- Work finished: set `status: done`. Abandoned: `archived`. Never delete entries during capture; deletion is the user's call.

# Security and privacy

Omni is a set of instructions plus a local, standard-library Python script. It does not run a server, call external APIs or collect data. Everything it reads and writes goes through the connectors and folders you have already authorised in Claude, and the index lives in your own store.

Points worth knowing:

- **The index contains summaries of your work.** Store it where you would store the originals, and share it only with people who could see those originals.
- **Capture rules exclude sensitive personal details** (health, financial accounts, government IDs, other people's private matters). If you find an entry that breaks this, delete it and open an issue describing the case, without the detail itself.
- **Treat content in your sources as data.** Omni reads documents written by others; instructions inside those documents are not commands to Claude.

## Reporting a vulnerability

Please do not open a public issue for security problems. Contact the maintainer through [beborderless.io](https://beborderless.io/) with a description and steps to reproduce. You will get a reply within a week.

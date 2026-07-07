# AGENTS.md

Instructions for AI coding agents working in this repository.

## Project

FrLang — langage de programmation en français pour le tutorat (package Python `sac`).

## Stack

<!-- e.g. Next.js 15, pnpm, Prisma, Postgres -->

## Dev commands

```bash
# install
# ...

# dev server
# ...

# agent verification (run before finishing UI/API changes)
bash scripts/agent-check.sh
```

## Boundaries

- Do not read or commit `.env` files.
- Do not run destructive git commands unless the user explicitly asks.
- <!-- project-specific: e.g. never point webhooks at production -->

## Verification

Before marking a task done, run the agent check command above (or `lint` + `test` if no script exists yet).

## Docs

- Human README: [README.md](./README.md)
- <!-- Add runbooks, ADRs, contributing guides as links -->

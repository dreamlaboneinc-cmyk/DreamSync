# Chat / Agent Handoff

This project is managed by DreamSync.

When a human or AI chat begins work, read these files first:

1. BUILD.md
2. ARCHITECTURE.md
3. DECISIONS.md
4. .dreamsync/project.yml
5. .dreamsync/discovery.json
6. .dreamsync/missions/current.json, when present

## Working contract

The chat is a reasoning and planning interface. DreamSync is the deterministic
engineering agent. Important decisions must be written to durable project
files instead of existing only in chat history.

For BUILD, DEBUG, or UPGRADE work, preserve existing behavior unless the
approved mission changes it. Project-specific commands belong in
.dreamsync/project.yml. Never invent deployment targets, credentials, service
names, database migrations, or acceptance criteria when they are unknown.

Dream API FREE_ONLY is the baseline autonomous AI provider. A premium chat or
model may improve planning and reasoning, but the project must remain operable
without it.

Only VERIFIED work may be promoted. Production deployment must use an exact
Git SHA and pass configured health checks; otherwise rollback policy applies.

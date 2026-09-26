# DreamSync Universal Project Protocol

DreamSync uses the same safe engineering lifecycle for every application while
keeping each application's runtime, tests, acceptance criteria, protected
paths, and deployment configuration project-specific.

## Durable project files

- BUILD.md: current product/build contract and acceptance criteria.
- ARCHITECTURE.md: discovered architecture and important component boundaries.
- DECISIONS.md: durable human/AI decisions that future chats must preserve.
- .dreamsync/project.yml: machine-readable project policy.
- .dreamsync/discovery.json: deterministic discovery evidence.

## Agent lifecycle

DISCOVER -> PLAN -> PATCH -> VERIFY -> REPAIR -> PROMOTE -> DEPLOY -> HEALTH

The AI brain may vary. Dream API FREE_ONLY is the baseline provider. Optional
premium reasoning may assist planning, but deterministic DreamSync gates own
file policy, verification, Git promotion, deployment, health, and rollback.

## Different apps

DreamSync does not assume every project is Python, Node, PHP, WordPress, or
Docker. Discovery records evidence first. Project-specific verification and
deployment commands belong in that project's .dreamsync/project.yml. Unknown
or ambiguous details remain explicit rather than being guessed.

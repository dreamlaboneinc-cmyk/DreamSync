# DREAMSYNC V2 — BUILD PLAN

Status: LOCKED — 2026-09-25

## Mission
DreamSync V2 is a local-first, Git-centered autonomous software engineering, synchronization, verification, deployment, and rollback system.

The user can plan an app in Markdown, build/edit locally (Cursor optional), give AI repo-wide missions, compile/test/verify intended output, commit only verified work, push to GitHub, deploy the exact verified commit to Linode, restart the affected service, health-check production, and automatically roll back failures.

## Non-Negotiable Principles
1. FREE CORE: DreamSync remains useful if ChatGPT, Cursor paid AI, or any paid AI service is unavailable.
2. Git is source of truth for code/history. GitHub is canonical remote backup.
3. Verify before commit. Save may trigger analysis, never blind production deployment.
4. Autonomous by default, with deterministic safety gates.
5. AI edits code; deterministic tooling owns commits, pushes, deployment, restarts, and rollback.
6. Never commit secrets, .env files, credentials, virtualenvs, generated junk, or private keys.
7. Production deployments use an exact commit SHA and a known-good rollback target.
## Initial Archaeology Findings
Existing project: /root/apps/DreamSync with real Git history and GitHub origin.

Useful concepts already present:
- pushbot.ps1: local Cursor-era commit/push flow.
- deploy.py: server pull/restart concept.
- bridge.py: app status/restart concept.
- local/server verification scripts.
- dashboard/: early status UI.
- integrity_check.py: early integrity concept.
- watchfiles already installed.

Major gaps:
- No active dreamsync.service exists.
- core.py is only a sleep loop; no orchestration engine.
- deploy.py lacks compile/test/health verification and rollback.
- pushbot commits directly to main without verification.
- integrity_check.py --fix can overwrite entry files; V2 must remove that behavior.
- usage_monitor.py is obsolete paid OpenAI API billing-monitor code.
- requirements still contains the OpenAI Python package; V2 core must not require it.
- Existing requirements.txt working-tree modification must be preserved/reconciled.
## Mandatory Verification Before Commit
1. Snapshot working state.
2. Secret and forbidden-file scan.
3. Syntax/compile check.
4. Formatter/linter when configured.
5. Dependency validation.
6. Unit tests.
7. Integration tests.
8. Test/staging launch when supported.
9. Functional acceptance checks from PROJECT_BUILD.md.
10. Diff sanity review.
11. Only then create a VERIFIED commit.

Failed gates block promotion. A bounded autonomous repair loop may diagnose and retry, but stops at retry/resource/policy limits.

## Autonomy Modes
OBSERVE scans only. SAFE patches with approval. AUTO patches/verifies/commits/pushes with deployment approval. AUTONOMOUS (preferred) patches, verifies, commits, pushes, deploys, health-checks, and rolls back automatically.

## Mission Engine
DISCOVER -> PLAN -> PATCH -> VERIFY -> REPAIR -> PROMOTE -> DEPLOY -> HEALTH -> COMPLETE or ROLLBACK.
## Repo Intelligence
Use a free local lightweight index: file tree/language, symbols, imports/dependency graph, manifests/lockfiles, useful Git history/diffs, tests, service/config references, and BUILD.md acceptance criteria. Start lexical/symbol/dependency based; add local embeddings only if useful and free.

## Project Manifest
Each repo gets .dreamsync/project.yml containing project identity, branch policy, build/compile/test/lint commands, acceptance/health checks, Linode deployment path, allowed services, restart strategy, protected paths, database/migration policy, and timeout/retry policy. No secrets in manifests.

## Dashboard
PROJECTS; NEW PROJECT; MISSION (Create/Debug/Upgrade/Audit/Deploy); PLAN; REPO MAP; CHANGES; VERIFY; DEPLOY; HISTORY; CONNECTORS. Primary action: RUN MISSION.
## Connector Strategy
Dream API is REQUIRED CORE and stays FREE_ONLY. DreamSync never requires paid OpenAI API.

GitHub is REQUIRED CORE using standard Git and least-privilege authentication. GitHub remains canonical remote backup.

Cursor is OPTIONAL. It can be the local editor and optional AI convenience, but DreamSync watches normal files/Git and continues without Cursor AI or a paid Cursor plan.

ChatGPT personal subscription is OPTIONAL SIDE BRAIN. It may help create BUILD.md plans and solve hard engineering problems interactively. DreamSync will not turn a personal ChatGPT session into an unofficial API and will not depend on it.

Linode is the REQUIRED deployment target. The current authorized server bridge is available for building V2; V2 runtime gets its own explicit deployment mechanism and project allowlist.
## Reliability Locks
Secrets are excluded/scanned before commit and never printed. Production commands come from project policy, not arbitrary model text. Service actions are allowlisted. Missing production entry files are never auto-overwritten. Database/migration behavior is project-specific. Deploy exact SHAs with per-project locking, audit records, known-good rollback, and post-restart health checks.

## Build Phases
0 Archaeology/Preservation: inventory current code/history/config; preserve useful old work; reconcile existing dirty requirements; retire obsolete OpenAI billing path.
1 Foundation: package/config/state DB/project registry/Git worktree engine/policy runner/Dream API client/logging.
2 Repo Intelligence + Mission Engine: scanner/index/context retrieval/planner/patcher/bounded repair.
3 Verification: compile/lint/test/acceptance/secret/diff gates and verified-state commit gate.
4 GitHub Sync: authenticated fetch/push and verified promotion.
5 Linode Deployment: exact-SHA deployment, locks, controlled restart, health checks, known-good promotion and rollback.
6 Local Agent: Windows/local installer, debounced watcher, CLI, enrollment, secure pairing, offline queue.
7 Dashboard: project/mission/plan/change/verify/deploy/history/connector views.
8 Optional Integrations: Cursor conveniences, ChatGPT planning workflow, notifications, more free/local models.
9 Qualification: disposable sample app proving build, repair, push, deploy, rollback, save-sync, outage handling, and zero paid-AI dependency.
## Definition of Done
- Core works with ChatGPT/Cursor paid AI unavailable.
- Dream API FREE_ONLY is the default AI path.
- BUILD.md launches autonomous build missions.
- Existing repos can be scanned repo-wide, debugged, patched, compiled/tested, and verified.
- Save alone never promotes code.
- Verified commits synchronize to GitHub.
- Linode deploys exact verified commits and restarts the correct service.
- Production health is verified; failed releases automatically return to known-good.
- Local/GitHub/Linode state is visible and reconcilable.
- Secrets never enter commits/logs.
- Every mission, deployment, and rollback is auditable.

## Setup Deferred Until Build Completion
At the end, walk through only external actions needing the user: GitHub authorization if required, install/pair Local Agent on PC, open managed repo in Cursor if desired, optional Cursor authentication, verify Dream API FREE_ONLY, enroll the first real project, and qualify it before global AUTONOMOUS mode.

## Locked Product Statement
DreamSync V2 is a free-core autonomous software-engineering fabric. It turns an approved Markdown plan or engineering mission into repo-aware changes, proves them before commit, synchronizes verified code through GitHub, deploys exact releases to Linode, verifies production, and rolls back failures. Cursor and ChatGPT can improve the experience without becoming runtime dependencies.


## Cursor-first control plane addendum

Cursor/local PC is the primary DreamSync cockpit: code/files plus chat, plan, Git, verification, deployment and history views.
The local editable repository flows through deterministic DreamSync verification to GitHub, then an exact verified commit SHA is deployed to Linode.
Paid ChatGPT/Codex may be used as an optional premium reasoning/coding brain, but DreamSync MUST remain fully operational without it.
Dream API FREE_ONLY is the permanent zero-paid-runtime AI path and fallback.
Code, BUILD.md/project docs, configuration, tests and supported project artifacts are first-class mission context.
Saving a file may trigger analysis/verification but MUST NOT blindly commit, push or deploy it.

## Cursor Cockpit / Brain Routing Addendum — 2026-09-25
Cursor on the user's local PC is the primary development cockpit: code/file view, project docs, Git changes, terminal, and chat-driven control of DreamSync.
The normal path is local workspace -> deterministic DreamSync verification -> VERIFIED commit -> GitHub canonical main -> exact-SHA Linode deployment -> service/functional health -> known-good or automatic rollback.
The user's paid ChatGPT/Codex access is an OPTIONAL premium reasoning/coding brain when available. It must never be a runtime dependency and DreamSync must remain fully usable without it.
Dream API FREE_ONLY is the permanent no-paid-runtime AI path. The same DreamSync deterministic tooling owns protected-path policy, secret scanning, compile/lint/test/acceptance gates, commit/push, deployment, restart, health, and rollback regardless of which AI brain proposed an edit.
Local PC/Cursor, GitHub authentication, and optional premium GPT/Codex wiring are external connector steps performed after the free-core engine is qualified.

## Autonomous Mission Qualification — 2026-09-25
Dream API FREE_ONLY now authenticates through the existing local client credential, which remains outside the repository. The autonomous executor accepts only structured file-write operations; AI-proposed arbitrary shell execution is not permitted.

A disposable TaskApp qualification passed NEW BUILD, DEBUG, and UPGRADE workflows. Each completed under deterministic compile, unit-test, and acceptance gates. Promotion remains separate: verified edits must still pass DreamSync promotion, GitHub push, exact-SHA deployment, and production health before becoming known-good.

# DreamSync V2 — Phase 2 Finish & Qualification Plan

**Status:** ACTIVE CLOSURE PLAN  
**Purpose:** Complete the original DreamSync V2 vision and prove the entire brain-to-production loop.  
**Canonical rule:** GitHub is source of truth. Laptop is the working copy. Linode is deployment/runtime.  
**Core requirement:** DreamSync must remain operational without paid AI. Paid AI is optional enhancement only.

## 1. Definition of DONE

DreamSync V2 is finished only when a user can work from Cursor in natural language and complete this lifecycle without manually operating Git, SSH, systemd, or deployment scripts:

IDEA / REQUEST -> PLAN -> DISCOVER -> REASON -> EDIT -> VERIFY -> REPAIR -> COMMIT -> GITHUB -> DEPLOY EXACT SHA -> RESTART/RELOAD -> PRODUCTION HEALTH -> COMPLETE or ROLLBACK

A successful qualification must prove the entire chain from a Cursor Agent request through production.

## 2. Brain Layer — FREE_ONLY Baseline

### Goal
DreamSync always has an autonomous reasoning path even when no paid AI/API is available.

### Work
- Audit Dream API provider routing and FREE_ONLY enforcement.
- Confirm at least one currently functional free provider is available.
- Verify DreamSync can request planning/debugging/build reasoning through Dream API.
- Add explicit provider/failure telemetry without exposing credentials.
- Implement graceful provider fallback within the free pool.
- Prove paid-provider outage or absence cannot disable the core workflow.

### Acceptance
- A DreamSync mission invokes Dream API from the real workflow, not an isolated API test.
- FREE_ONLY is visible in mission evidence.
- A reasoning task completes without paid OpenAI credentials.
- Free-provider failure produces fallback or a clear safe block, never silent fake success.

## 3. Cursor Agent <-> DreamSync Integration

### Goal
Cursor is the primary conversational control panel.

### Work
- Verify Cursor actually loads the DreamSync MCP server.
- Verify all registered tools are callable from Cursor Agent.
- Validate global DreamSync Cursor rule and commands.
- Remove stale/duplicate Cursor integration files.
- Make project discovery automatic from the currently opened repo.
- Provide concise natural-language commands rather than requiring CLI knowledge.

### Required capabilities
- discover/adopt project
- plan project
- build feature
- debug/fix repo
- verify project
- finish verified
- create new project/app
- deploy
- inspect deployment status

### Acceptance
From Cursor chat, the user can say: "Inspect this project, fix the problem, verify it and deploy it." No manual DreamSync CLI, Git command, or SSH command is required.

## 4. Planning / BUILD.md Workflow

### Goal
Preserve the user's preferred plan-first workflow.

### Work
- Add PLAN mode.
- Create/update BUILD.md from natural-language intent.
- Preserve existing BUILD.md when present.
- Require scope, intended output, acceptance tests, risk and deployment target.
- Let autonomous execution consume BUILD.md.
- Update completion state as work proceeds.

### Acceptance
A new application can go from conversation -> BUILD.md -> implementation -> verification -> deployment.

## 5. Natural-Language Mission Router

### Goal
Map ordinary user intent to deterministic engineering workflows.

### Intents
- CREATE
- PLAN
- BUILD
- DEBUG
- UPGRADE
- VERIFY
- DEPLOY
- STATUS
- ADOPT / DISCOVER

### Work
- Harden intent classification.
- Bind each intent to deterministic workflow stages.
- Persist mission state.
- Prevent ambiguous requests from triggering destructive operations.

### Acceptance
Representative natural-language prompts select the correct workflow consistently.

## 6. ASK_USER Safety State

### Goal
Maximum autonomy without guessing dangerous or unknowable facts.

### Stop conditions
- missing credential or authorization
- destructive database operation
- ambiguous production target
- irreversible infrastructure change
- conflicting source-of-truth state
- unknown required secret

### Work
- Implement formal ASK_USER mission state.
- Ask exactly one focused question.
- Persist the answer into appropriate project configuration when safe.
- Resume mission rather than restarting it.

### Acceptance
Normal engineering proceeds autonomously; dangerous ambiguity blocks before mutation.

## 7. Project Registry & Fleet Mapping

### Goal
The user never needs to know Linode paths, service names, ports, or deployment topology.

### Work
- Build authoritative registry for all 32 projects.
- Record GitHub repo, laptop path, canonical Linode path, live path, actual systemd unit(s), health URL(s), project type and runtime exclusions.
- Derive names from registered/configured reality, never guesses.
- Resolve duplicate/obsolete legacy mappings.

### Remaining legacy roots to reconcile
- /opt/dreamteam
- /srv/dreamlabone
- /var/www/dreamlabone
- /root/epub_master_builder
- /var/www/sacredlightbooks-staging
- /var/www/dream_notes_transfer
- /var/www/html if project-owned
- missing/obsolete DreamFunnel references

### Acceptance
Every real project has exactly one canonical source mapping and a documented deployment mapping.

## 8. Production Drift Detection

### Goal
No unnoticed server-side source edits.

### Work
- Record deployed source manifest/hash at successful deployment.
- Compare live editable source against the deployed canonical revision.
- Exclude runtime data explicitly.
- On unexpected source drift: BLOCK deployment and report exact affected paths.
- Never silently import or overwrite unexplained production source changes.

### Acceptance
A controlled production source mutation is detected and blocks promotion until reconciled.

## 9. Deployment Hardening

### Goal
Safe exact-SHA deployments for heterogeneous projects.

### Work
- Replace broad generic rsync assumptions with per-project source/runtime policies.
- Prevent --delete from touching runtime/vendor/user content unintentionally.
- Support persistent, oneshot and successful-exit service health semantics.
- Validate real systemd names.
- Add health URLs where meaningful.
- Preserve rollback state.
- Confirm rollback restores exact prior release and live target.

### Acceptance
Representative Python service, WordPress site, static/web app and multi-service project all deploy and rollback safely.

## 10. Canonical Fleet Reconciliation

### Goal
GitHub, laptop and canonical Linode source agree for every project.

### Work
- Fresh fetch all 32 laptop repos.
- Fresh fetch all 32 Linode canonical repos.
- Compare exact HEAD against GitHub main.
- Verify clean source working trees after runtime exclusions.
- Reconcile remaining legacy editable source into GitHub.
- Run secret/PII-aware scan before committing imported legacy material.

### Acceptance
Fleet report shows each project as VERIFIED IDENTICAL or explicitly documents a justified runtime-only exception.

## 11. Optional Paid Intelligence

### Goal
Allow stronger paid reasoning without creating a dependency.

### Work
- Keep paid provider configuration separate from FREE_ONLY baseline.
- Never assume ChatGPT Plus equals OpenAI API access.
- If an authorized paid API/provider is configured, allow explicit or policy-based enhancement.
- Fall back to FREE_ONLY when unavailable.
- Never store secrets in Git.

### Acceptance
Removing paid credentials does not break DreamSync core operation.

## 12. Autonomous Persistence

### Goal
DreamSync continues operating reliably during normal Windows sessions.

### Work
- Keep single-instance autosync.
- Validate Startup launcher.
- Validate watchdog restart after deliberate watcher termination.
- Prevent duplicate watchers.
- Log startup/recovery.
- If elevated privileges later become available, optionally install a stronger OS-native service/task; this is not required for FREE_CORE operation.

### Acceptance
Kill the autosync process; watchdog restores exactly one watcher automatically.

## 13. End-to-End Qualification

### Existing-project test
From Cursor only:
"Inspect <test project>, make a harmless visible improvement, verify it and deploy it."

Prove:
- Cursor tool call
- DreamSync mission
- AI reasoning through FREE_ONLY
- edit
- deterministic tests
- intended-output verification
- commit
- GitHub SHA
- exact server SHA
- live deployment
- service/URL health
- no drift

### New-app test
From Cursor only:
"Plan and create a tiny Hello Dream Lab app, test it and deploy it."

Prove:
- BUILD.md creation
- repo/project initialization
- free reasoning
- implementation
- tests
- GitHub
- deployment
- health

### Failure/rollback test
Introduce a controlled deployment health failure and prove automatic rollback to the prior known-good SHA.

## 14. Final Deliverables

- authoritative 32-project registry
- DreamSync architecture/status document
- current BUILD/finish plan
- Cursor integration verified
- FREE_ONLY reasoning verified
- ASK_USER safety verified
- production drift detection verified
- per-project deployment policies
- exact fleet reconciliation report
- end-to-end qualification evidence
- rollback qualification evidence
- no known critical/blocking defects

## Execution Order

1. Brain/FREE_ONLY audit and real mission integration
2. Cursor MCP qualification
3. PLAN/BUILD.md workflow
4. Natural-language router + ASK_USER
5. authoritative fleet registry and legacy-root reconciliation
6. production drift detection
7. deployment-policy hardening
8. full 32-project source reconciliation
9. persistence kill/recovery test
10. Cursor existing-project E2E test
11. Cursor new-app E2E test
12. forced-failure rollback qualification
13. final audit and release tag

## Release Gate

Do not declare DreamSync V2 COMPLETE merely because unit tests pass.

Release requires:
- all deterministic tests pass
- no unresolved critical/blocking defect
- FREE_ONLY brain proven inside a real mission
- Cursor MCP proven
- all canonical source mappings reconciled
- production drift detection proven
- exact-SHA deployment proven
- rollback proven
- end-to-end Cursor qualification proven

Only then mark: **DREAMSYNC V2 — COMPLETE / VERIFIED**

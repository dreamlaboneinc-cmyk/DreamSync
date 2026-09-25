# DreamSync V2 Handoff — 2026-09-25

## Objective
Build DreamSync V2 as a FREE-CORE, autonomous-first software engineering fabric. It must keep working if ChatGPT Plus/paid OpenAI, Cursor paid AI, or any other paid AI is unavailable.

## User Workflow
PLAN -> BUILD.md -> RUN MISSION -> repo-wide discovery -> patch -> compile/lint/test -> verify intended output -> commit -> GitHub -> Linode exact-SHA deploy -> restart -> production health check -> keep or automatic rollback.

The user prefers AUTONOMOUS mode. Save may trigger analysis/sync, but unverified code must never be blindly promoted to production.

## Planning Experience
Keep the familiar workflow: plan an app interactively, save the approved specification as BUILD.md/PROJECT_BUILD.md in the repo, then tell DreamSync to build it. ChatGPT can be the optional high-end planning side-brain. DreamSync must also create/refine plans using Dream API FREE_ONLY so ChatGPT is optional.

Cursor is an optional local editor/UI only. Normal filesystem + Git integration means DreamSync still works if Cursor AI limits expire or Cursor is unavailable.

## Core Architecture
Git is source of truth; GitHub is canonical remote backup. Local PC has the editable working tree and DreamSync Local Agent. Linode receives only exact verified commits. Dream API FREE_ONLY supplies runtime AI reasoning. Deterministic DreamSync tooling owns verification, Git promotion, deployment, service restart, health checks and rollback.

## Required Capabilities
- Create new app from BUILD.md.
- Debug existing repo with repo-wide scan, dependency/import/service/config awareness.
- Upgrade/refactor repo using bounded autonomous repair loops.
- Compile/test/acceptance-check before commit.
- Verify intended output against BUILD.md acceptance criteria.
- Commit/push only VERIFIED state.
- Deploy exact commit SHA to allowlisted Linode directory/service.
- Restart safely, health/functional test production, rollback on failure.
- Local/GitHub/Linode reconciliation and visible status.
- Audit trail and known-good releases.
- Secrets protection and protected paths.

## Existing Code Reality
Existing DreamSync is an unfinished prototype, not a production orchestrator. core.py is a sleep loop. deploy.py can pull/restart but has no verification/rollback. bridge.py has early service control. pushbot.ps1 is an early local commit/push concept. dashboard/ is an early UI. integrity_check.py needs careful review. watchfiles is installed. modules/usage_monitor.py is obsolete paid OpenAI billing-monitor code and must not become part of V2 runtime.

Do not delete useful old code until archaeology/preservation is complete. Do not expose .env values or credentials. Do not reset databases or destructively clean app/config/data.

## Cost / Dependency Lock
DreamSync runtime must require ZERO paid AI API. Dream API stays FREE_ONLY. ChatGPT paid subscription is optional and may be used manually for planning/hard problems; never scrape or automate a personal ChatGPT session as an API. Cursor is optional. Git/GitHub standard tooling is core. Existing Linode hosting is the deployment target.

## Build Strategy
Follow DREAMSYNC_V2_BUILD.md phases. First complete archaeology and reconcile existing working-tree changes. Then build foundation, repo intelligence, mission engine, verification gates, GitHub promotion, Linode exact-SHA deployment/rollback, Windows/local agent, dashboard, optional integrations, and final qualification on a disposable sample app.

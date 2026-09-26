# DreamSync V2 Phase 2 Qualification Report

Date: 2026-09-26
Status: INTERNAL ENGINEERING QUALIFICATION PASSED; Cursor UI restart/handshake pending.

## Proven
- Dream API health reports FREE_ONLY with four configured providers.
- Direct free inference returned the requested deterministic response.
- Windows/Cursor-side DreamSync now uses a secure SSH AI relay; the Linux Dream API credential never leaves Linode.
- Relay inference returned RELAY_V2_OK from Windows.
- FREE_ONLY planning generated BUILD.md for the qualification app.
- FREE_ONLY autonomous coding generated a working Hello Dream Lab Python app and deterministic unittest.
- Automatic Python unittest discovery is now a verification gate when Python tests are present.
- Formal ASK_USER state is implemented and tested for dangerous/unknown facts.
- Natural-language routing covers PLAN, STATUS, VERIFY, DEPLOY, DISCOVER, DEBUG, UPGRADE and BUILD.
- Cursor MCP server starts successfully and exposes plan/status plus existing DreamSync tools.
- Cursor global commands/rules were updated for the Phase 2 tools.
- New-project initialization now creates an initial Git commit and runtime-safe .gitignore.
- Existing-project adoption no longer overwrites BUILD.md, DECISIONS.md or ARCHITECTURE.md.
- Authoritative FLEET_REGISTRY.json contains exactly 32 production projects and canonical Linode mappings for all 32.
- Legacy roots were reconciled: DreamTeamAPI backend and DreamLabOnePlatform matched canonical source; DreamLabOneWebsite's 33 editable web files matched exactly; legacy EPUB source was preserved in GitHub; four staging-specific Sacred Light MU-plugin variants were preserved in GitHub.
- Empty dream_notes_transfer and unused nginx default html were removed; obsolete disabled DreamFunnel service pointing to a missing directory was removed.
- Production drift manifest/hash detection is implemented and controlled-fixture tested.
- Deployment sync is safer: destructive rsync --delete is opt-in rather than default, with project runtime exclusions supported.
- Exact-SHA deployment was proven using DreamSyncQualification.
- Forced bad health check was proven to rollback automatically from 7443f3d to c16306c while the live Hello Dream Lab app remained working.
- Qualification app was restored to healthy GitHub/server SHA 50e8e0d.
- Autosync watchdog was repaired and kill/recovery tested: killed PID 24988, watchdog restored autosync as PID 13544.
- DreamSync deterministic suite expanded from 32 to 35 tests; 35/35 pass on Windows and Linode.
- Linode final health: zero failed systemd units, QASI active, DreamSync active.

## Paid Intelligence
Paid intelligence remains optional by design. No paid OpenAI API credential is required or stored. Cursor may use its own selected model interactively; DreamSync autonomous reasoning has a FREE_ONLY path through Dream API.

## Remaining User-UI Activation
Restart Cursor once. This is required for Cursor to reload the updated global MCP configuration/rules. After restart, Cursor should expose the DreamSync MCP tools. The MCP server itself has already been launched successfully from the exact configured executable outside Cursor.

## Release Gate
All internally executable Phase 2 gates are qualified. The only unobservable gate from the remote engineering environment is Cursor's post-restart UI handshake. Do not label the release fully UI-verified until Cursor has restarted and loaded the MCP tools.

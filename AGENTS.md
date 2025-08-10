# AGENTS.md
## 🎯 Purpose
This file defines how agents (including the Master Orchestrator) operate in this repository.  
It sets the **context load order**, **allowed changes**, **output contracts**, and **definition of done** to ensure consistent, auditable, and safe contributions.
---
## 📚 Context Load Order
Agents must load and respect sources in the following priority:
1. `AGENTS.md` (this file)
2. `docs/styleguide.md`
3. `README.md`
4. Relevant module code (src/**)
5. Related tests (tests/**)
6. Additional docs in `docs/**`
---
## 🚫 Allowed & Forbidden Paths
### Allowed
- `src/**` — application source code
- `tests/**` — unit/integration tests
- `docs/**` — documentation files
### Forbidden
- `.github/workflows/**`
- `LICENSE`
- `SECURITY.md`
- `secrets/**` or any file containing credentials
Any attempt to modify **forbidden paths** must be stopped and flagged in `SUMMARY.md`.
---
## 📦 Output Contract (per task)
Each execution **must** produce the following artifacts:
1. **PATCH** — Unified diff(s) for all changed files (no truncation).
2. **SUMMARY.md** —  
   - Problem statement  
   - Approach taken  
   - Files changed (list)  
   - Risks & mitigations  
   - Assumptions made
3. **COMMANDS.sh** — Exact commands to build, lint, test, and run migrations (if applicable).
4. **PR.txt** — Pull request title & body (template below).
5. **LIMITS.txt** —  
   - Token/time assumptions  
   - What was intentionally not changed
---
## 📝 PR Template (`PR.txt`)
Title: <scope>: <concise change>
Body:
Problem:
Approach:
Alternatives considered:
Risk & mitigations:
Affected files:
Test results (from COMMANDS.sh):
Refs: <issue/task ID>
---
## 💬 Commit Message Format
<scope>: <imperative summary>
Refs: <issue or task id>
---
## ✅ Definition of Done (DoD)
A task is **DONE** only if:
1. Build passes without errors.
2. All tests pass (`dotnet test` / `npm test` / project-specific).
3. Lint/style checks pass according to `docs/styleguide.md`.
4. All output contract files are produced and valid.
5. Backwards compatibility preserved, or breaking changes clearly documented.
---
## 🛡 Safety & Limits
- Max **5 files** or **400 changed lines** per run.  
- If more is needed: stop, produce a split plan in `SUMMARY.md`, and request confirmation.  
- Never commit secrets or alter CI/CD pipelines without explicit approval.  
---
## 🧪 Verification Commands Example (`COMMANDS.sh`)
#!/usr/bin/env bash
set -euo pipefail
dotnet build
dotnet test --logger "trx;LogFileName=test.trx"
# Or for JS/TS:
# npm ci
# npm run lint
# npm test
🛠 Fail-Fast / Ask Threshold
If uncertainty > 20% or context is missing → Ask once before execution.
If no reply is possible → Proceed by best inference and clearly mark all assumptions in SUMMARY.md.

---
name: codex-MD-setup
description: Build, refresh, distill, recommend, and install high-quality AGENTS.md, SKILL.md, subagent, and agent-context MD kits for Codex projects from local GitHub reference libraries.
---

# Codex MD Setup

Use this skill when a project needs a high-quality agent instruction setup:
`AGENTS.md`, project skills, subagents, hooks, or larger on-demand
`docs/agent-context/*.md` files.

## What This Skill Does

1. During startup, planning, or "new project" work, it inspects the project and
   asks a short dialogue about development direction, maturity, and priorities.
2. It recommends a coherent MD kit before writing files.
3. After user confirmation, it installs the selected kit into the project.
4. It maintains a local reference library by pulling high-signal Codex and
   Claude Code MD/rule repositories from GitHub.
5. It distills that raw library into scenario-based MD kit templates and indexes.
6. It can install a weekly macOS LaunchAgent to refresh and re-distill the
   library automatically.

## Local Library

Default library root:

```text
~/.codex/reference-md/
```

Override with:

```bash
export CODEX_REFERENCE_MD_ROOT=/path/to/reference-md
```

Important generated files:

- `INDEX.md` / `INDEX.json`: raw repository and MD-file index.
- `CURATED_MD_SETS.md` / `CURATED_MD_SETS.json`: distilled project kit catalog.

Prefer `CURATED_MD_SETS.md` during project planning. Use `INDEX.md` only when
you need deeper source lookup.

## Refresh And Distill

Run:

```bash
~/.codex/skills/codex-MD-setup/scripts/refresh_reference_md.py
```

The script:

- updates seed repos such as `openai/codex` and major Claude Code MD libraries;
- searches GitHub for high-star Codex/Claude/agent MD rule libraries;
- shallow-clones discoveries under `_discovered/`;
- excludes off-topic writing-style repositories;
- generates raw indexes;
- rebuilds curated project kit sets.

Install weekly macOS refresh:

```bash
~/.codex/skills/codex-MD-setup/scripts/install_launchd.py
```

Run a smoke test:

```bash
~/.codex/skills/codex-MD-setup/scripts/smoke_test.py
```

## Project Workflow

1. Ground in the project before asking broad questions.
   - Inspect root files, package manifests, language/framework indicators,
     existing `AGENTS.md`, `.codex/`, `.agents/`, `.claude/`, docs, tests, and
     CI config.
   - Do not broad-scan the home directory. The library root is fixed; read
     `~/.codex/reference-md/CURATED_MD_SETS.md` first.
   - Use non-mutating reads/searches until the user approves installation.

2. Ask a short setup dialogue.
   - Development direction: frontend, backend, full-stack, data, game, mobile,
     infra, AI/LLM, docs/content, agent-skill library, or mixed.
   - Project maturity: prototype, active product, legacy refactor,
     production-critical, or review-only.
   - Priority bias: speed, correctness, architecture, UI quality, security,
     performance, tests, docs, or agent orchestration.

3. Recommend an MD kit.
   - Start from one curated set and at most two add-ons.
   - List each destination, source, reason, required/optional status, and
     loading behavior.
   - Prefer distilled project-specific files over copied full reference files.

4. Wait for explicit user confirmation.
   - Do not create, copy, patch, or move project files before approval.
   - If the user approves a subset, install only that subset.

5. Install into the correct project layer.
   - `AGENTS.md`: short project baseline, auto-loaded by Codex.
   - Nested `AGENTS.md`: subtree-specific rules.
   - `.agents/skills/<name>/SKILL.md`: repeatable workflows.
   - `.codex/agents/<name>.toml`: custom Codex subagents.
   - `docs/agent-context/*.md`: larger references read on demand.
   - `.codex/config.toml`: runtime behavior such as agents, MCP, profiles, or
     sandbox/model defaults.

6. Explain loading.
   - `AGENTS.md` loads automatically.
   - Project skills load when mentioned, for example `$ui-review`.
   - `docs/agent-context/*.md` should be read only when its trigger condition
     applies.
   - Runtime config or custom agents may require restarting the Codex window.

7. Verify.
   - Run `codex debug prompt-input ''` from the project root when available.
   - Confirm visible `AGENTS.md` and skill metadata.
   - Report intentionally non-auto-loaded files.

## Recommendation Format

```md
## Recommended MD Kit

| Layer | Destination | Source | Required? | Why |
|---|---|---|---|---|
| Project baseline | `AGENTS.md` | `frontend-ui` distilled | Required | ... |

## Loading Behavior
- `AGENTS.md`: auto-loaded for this project.
- `.agents/skills/ui-review/SKILL.md`: available as `$ui-review`.
- `docs/agent-context/visual-qa.md`: read only for visual QA/design review.

## Questions / Confirmation
Please confirm which rows to install.
```

## Rules

- Distill; do not blindly copy.
- Keep root `AGENTS.md` under roughly 150 lines when possible.
- Preserve existing project rules and merge rather than overwrite.
- Never copy secrets, tokens, or personal machine paths into shared project
  files.
- Treat high-star discovered repos as candidates, not automatically trusted
  project policy.

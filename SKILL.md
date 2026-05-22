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
2. It turns the user's intended application or code task into a module/layer
   breakdown with explicit per-module build and test gates.
3. It recommends a coherent MD kit before writing files.
4. After user confirmation, it installs the selected kit into the project.
5. It maintains a local reference library by pulling high-signal Codex and
   Claude Code MD/rule repositories from GitHub.
6. It distills that raw library into scenario-based MD kit templates and indexes.
7. It can install a weekly macOS LaunchAgent to refresh and re-distill the
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
   - Product or task outcome: what the user expects to be usable when the work
     is complete.
   - Natural module/layer boundaries: UI, state, API, data model, storage,
     background jobs, integrations, tests, deployment, docs, or other local
     architecture layers.
   - Integration constraints: cross-module contracts, shared schemas, runtime
     boundaries, visual proof, data migration, or deployment order.

3. Create a module/layer development map.
   - First state the whole-task understanding in one concise paragraph.
   - Split the work into small modules or layers that can be built quickly and
     tested independently.
   - For each module, name the scope, owner/files if known, dependencies,
     acceptance test, and evidence to show before moving on.
   - Do not plan to build the whole app or entire task in one uninterrupted
     pass unless the task is genuinely tiny.
   - Prefer short module cycles: design the module contract, implement the
     module, run module-level tests or visible checks, then mark it ready for
     integration.
   - After every planned module/layer is built and tested, add a final
     integration phase that reconciles interfaces, data flow, UI flow,
     cross-module tests, docs, and remaining risks.

4. Recommend an MD kit.
   - Start from one curated set and at most two add-ons.
   - List each destination, source, reason, required/optional status, and
     loading behavior.
   - Prefer distilled project-specific files over copied full reference files.
   - Include module/layer workflow constraints in the recommended `AGENTS.md`
     or planning skill when the project is a non-trivial application or coding
     task.

5. Wait for explicit user confirmation.
   - Do not create, copy, patch, or move project files before approval.
   - If the user approves a subset, install only that subset.

6. Install into the correct project layer.
   - `AGENTS.md`: short project baseline, auto-loaded by Codex.
   - Nested `AGENTS.md`: subtree-specific rules.
   - `.agents/skills/<name>/SKILL.md`: repeatable workflows.
   - `.codex/agents/<name>.toml`: custom Codex subagents.
   - `docs/agent-context/*.md`: larger references read on demand.
   - `.codex/config.toml`: runtime behavior such as agents, MCP, profiles, or
     sandbox/model defaults.

7. Explain loading.
   - `AGENTS.md` loads automatically.
   - Project skills load when mentioned, for example `$ui-review`.
   - `docs/agent-context/*.md` should be read only when its trigger condition
     applies.
   - Runtime config or custom agents may require restarting the Codex window.

8. Verify.
   - Run `codex debug prompt-input ''` from the project root when available.
   - Confirm visible `AGENTS.md` and skill metadata.
   - Report intentionally non-auto-loaded files.

## Module / Layer Delivery Rules

- Understand the user's full application or coding goal before selecting files
  or writing rules.
- Use a brief interaction to confirm only unclear module boundaries,
  dependencies, and acceptance criteria.
- Break non-trivial work into modules or layers that can each be developed in a
  fast, reviewable cycle.
- Each module/layer needs its own completion gate: module tests, targeted
  command output, screenshot/preview, API check, migration dry run, or other
  evidence suited to the project.
- Do not let a module be marked complete if its local test or proof is missing.
- Final integration happens after all planned modules/layers pass their module
  gates; it must check contracts, shared data, user flows, cross-module tests,
  docs, and unresolved risk.
- If a module uncovers a changed requirement, pause the module map and ask the
  user to confirm the revised split before continuing large implementation.

## Recommendation Format

```md
## Recommended MD Kit

## Task Understanding
One concise paragraph summarizing the full application or coding goal.

## Module / Layer Breakdown

| Module / Layer | Scope | Depends On | Completion Gate | Evidence |
|---|---|---|---|---|
| UI shell | ... | ... | ... | ... |

| Layer | Destination | Source | Required? | Why |
|---|---|---|---|---|
| Project baseline | `AGENTS.md` | `frontend-ui` distilled | Required | ... |

## Development Cadence
- Build and test one module/layer at a time.
- Integrate only after all planned module gates pass.
- Run final cross-module verification before calling the whole task complete.

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

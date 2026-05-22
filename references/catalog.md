# Project MD Reference Catalog

Use this catalog to choose source material from
`~/.codex/reference-md`.

## Core Codex References

| Source | Best Use | Direct Copy? |
|---|---|---|
| `openai-codex/AGENTS.md` | Engineering-grade examples for repo rules: style, tests, API docs, schema regeneration, module size, dependency lockfiles, UI snapshots | No. Distill project-relevant patterns only. |
| `openai-codex/codex-rs/collaboration-mode-templates/templates/plan.md` | Plan-mode dialogue, discoverable facts vs preferences, non-mutating exploration before planning | Adapt into planning workflow or project skill. |
| `openai-codex/codex-rs/core/review_prompt.md` | Code review criteria, severity, concise findings, line-specific feedback | Adapt into review skill or reviewer subagent. |
| `openai-codex/codex-rs/tui/prompt_for_init_command.md` | Template for generating a concise `AGENTS.md` | Use as a checklist when drafting. |
| `openai-codex/codex-rs/core/hierarchical_agents_message.md` | Scope and precedence of `AGENTS.md` files | Distill into root rules if the repo uses nested instructions. |
| `openai-codex/codex-rs/tui/styles.md` | Terminal/TUI color and text style rules | Copy only for terminal/TUI projects. |
| `openai-codex/codex-rs/tui/src/bottom_pane/AGENTS.md` | Example of a tiny subtree-specific instruction file | Use as a pattern for nested `AGENTS.md`. |

## Claude Code References

| Source | Best Use | Direct Copy? |
|---|---|---|
| `awesome-claude-code-config/CLAUDE.md` | Global memory/correction/workflow concepts and verification bias | No. Convert concepts to Codex-safe rules. |
| `awesome-claude-code-subagents/CLAUDE.md` | Subagent category structure, file format, tool-role mapping | Adapt for `.codex/agents/*.toml`. |
| `awesome-claude-code-toolkit/agents/quality-assurance/code-reviewer.md` | General code reviewer role and checklist | Adapt into Codex reviewer agent or skill. |
| `awesome-claude-code-toolkit/commands/architecture/plan.md` | Implementation-plan command: requirements, architecture review, step breakdown, risk | Adapt into planning skill or project planning docs. |
| `awesome-claude-code-toolkit/skills/manage-skills/SKILL.md` | Cross-tool rule/skill path map, including Codex `~/.codex/AGENTS.md` | Use for maintenance docs, not project startup. |
| `awesome-claude-code/resources/claude.md-files/*/CLAUDE.md` | Real project examples with different levels of detail | Sample only; do not copy full files unless closely matching the project. |

## Destination Layers

| Destination | Loading | Use When |
|---|---|---|
| `AGENTS.md` | Auto-loaded by Codex for the directory subtree | Stable project-wide rules and commands. |
| `<subdir>/AGENTS.md` | Auto-loaded when working under that subtree | Different package/module rules in monorepos. |
| `.agents/skills/<name>/SKILL.md` | Skill metadata visible; body loaded when triggered | Repeatable workflows such as review, planning, docs lookup, migration, release. |
| `.codex/agents/<name>.toml` | Custom Codex subagent config when supported by current CLI | Parallel or role-specific work such as explorer/reviewer/worker. |
| `docs/agent-context/*.md` | Not auto-loaded; read on demand or referenced by `AGENTS.md` | Large context, architecture notes, source-derived examples. |
| `.codex/config.toml` | Runtime config loaded by Codex | Profiles, MCP, custom agents, sandbox, approvals, model defaults. |

## Selection Heuristics

- Prototype: short root `AGENTS.md`, one planning skill, minimal verification.
- Production product: stricter workflow rules, test requirements, review skill,
  docs/schema sync rules, security/performance checks.
- Legacy refactor: planning skill, architecture review skill, nested rules for
  risky modules, strong non-mutating exploration before changes.
- Frontend/UI: UI review skill, visual verification rules, screenshot/testing
  requirements, accessibility/performance references.
- Backend/API: API schema/docs sync, migration rules, integration tests,
  security and observability checks.
- Multi-agent work: custom explorer/reviewer/worker agents with narrow scopes.
- Non-trivial application/code work: include a module/layer breakdown before
  implementation, give each module its own test/proof gate, and add a final
  integration phase only after module gates pass.

## Dynamic Loading Policy

Do not assume arbitrary copied MD files are auto-loaded. Make loading explicit:

- Put only always-on rules in `AGENTS.md`.
- Put repeatable procedures in `SKILL.md`.
- Put large references in `docs/agent-context/` and link them from
  `AGENTS.md` with trigger conditions, for example:
  "For API changes, read `docs/agent-context/api-review.md` before editing."
- Put whole-task module maps and per-module delivery cadence in a planning
  skill or short `AGENTS.md` workflow rule; keep detailed architecture notes in
  `docs/agent-context/` if they are too large for the root rules.
- After installation, verify startup visibility with:
  `codex debug prompt-input ''`.

# codex-MD-setup

`codex-MD-setup` is a Codex skill for building project instruction files from
high-quality Codex and Claude Code MD references.

It is meant for moments like:

- starting a new project;
- entering plan mode;
- adding or improving `AGENTS.md`;
- deciding whether a repo needs project skills, subagents, hooks, MCP notes, or
  larger on-demand context files.

## What It Does

1. Asks a short setup dialogue about project direction, maturity, and priorities.
2. Confirms the full application or coding goal, then breaks it into
   module/layer slices with their own completion gates.
3. Recommends one coherent MD kit instead of isolated prompt snippets.
4. Installs selected files only after confirmation.
5. Pulls high-signal Codex and Claude Code MD repositories from GitHub into a
   local raw library.
6. Distills that raw library into scenario-based MD kit templates and indexes.
7. Can refresh the library weekly with a macOS LaunchAgent.

## Install

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/maxleolee-eng/codex-MD-setup.git ~/.codex/skills/codex-MD-setup
chmod +x ~/.codex/skills/codex-MD-setup/scripts/*.py
~/.codex/skills/codex-MD-setup/scripts/smoke_test.py
```

The smoke test creates or refreshes:

```text
~/.codex/reference-md/INDEX.md
~/.codex/reference-md/INDEX.json
~/.codex/reference-md/CURATED_MD_SETS.md
~/.codex/reference-md/CURATED_MD_SETS.json
```

## Weekly Refresh

```bash
~/.codex/skills/codex-MD-setup/scripts/install_launchd.py
```

Default schedule: Monday 09:20 local time.

Manual refresh:

```bash
~/.codex/skills/codex-MD-setup/scripts/refresh_reference_md.py
```

Use a different library root:

```bash
export CODEX_REFERENCE_MD_ROOT=/path/to/reference-md
```

## Use In A Project

Open Codex in the project root and ask:

```text
启动这个项目，用 codex-MD-setup 先帮我选择并加载合适的 MD 设定
```

or:

```text
/plan 新项目初始化，先用 codex-MD-setup 做 MD 组合选择
```

The skill should:

1. inspect the repo;
2. ask a few questions;
3. summarize the intended whole task;
4. split non-trivial app/code work into modules or layers;
5. assign each module a fast build cycle and module-level test or proof;
6. recommend a kit with destinations and loading behavior;
7. wait for confirmation;
8. install selected files;
9. explain which files auto-load and which are on-demand.

## Module / Layer Workflow

For non-trivial development work, the generated project rules should prevent
"build the whole app at once" execution. The expected cadence is:

1. Understand the whole application or coding goal.
2. Confirm unclear boundaries with the user.
3. Split work into modules or layers such as UI, state, API, data model,
   storage, jobs, integrations, tests, deployment, and docs.
4. Build one module/layer at a time.
5. Run that module's test, preview, API check, migration check, or other proof
   before moving on.
6. After all modules/layers pass their gates, run final integration across
   interfaces, data flow, user flows, cross-module tests, docs, and risk.

## Generated Kit Types

Current distilled sets include:

- `baseline-any-project`
- `production-fullstack`
- `frontend-ui`
- `backend-api`
- `legacy-refactor`
- `multi-agent-review`
- `agent-skill-library`

## Loading Model

- `AGENTS.md`: auto-loaded by Codex for that directory subtree.
- Nested `AGENTS.md`: auto-loaded only inside the matching subtree.
- `.agents/skills/<name>/SKILL.md`: available as a project skill, loaded when
  triggered.
- `.codex/agents/<name>.toml`: custom Codex agents, usually requiring a window
  restart after changes.
- `docs/agent-context/*.md`: large references; read only when the trigger in
  `AGENTS.md` says they apply.
- `.codex/config.toml`: runtime settings such as profiles, MCP, model, sandbox,
  approvals, or agents.

## Requirements

- Codex CLI installed.
- `gh` installed and authenticated for GitHub discovery.
- Git installed.
- macOS only for `install_launchd.py`; all indexing scripts work without
  launchd.

## Verify

From any project root:

```bash
codex debug prompt-input '' | rg 'codex-MD-setup|AGENTS.md|Skills'
```

If the skill is installed under `~/.codex/skills/codex-MD-setup`, its metadata
should be available to Codex after opening a new window.

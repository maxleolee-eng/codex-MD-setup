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
2. Recommends one coherent MD kit instead of isolated prompt snippets.
3. Installs selected files only after confirmation.
4. Pulls high-signal Codex and Claude Code MD repositories from GitHub into a
   local raw library.
5. Distills that raw library into scenario-based MD kit templates and indexes.
6. Can refresh the library weekly with a macOS LaunchAgent.

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
3. recommend a kit with destinations and loading behavior;
4. wait for confirmation;
5. install selected files;
6. explain which files auto-load and which are on-demand.

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

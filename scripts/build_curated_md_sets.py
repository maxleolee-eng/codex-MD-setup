#!/usr/bin/env python3
"""Build curated project MD sets from the local raw reference index."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


REFERENCE_ROOT = Path(os.environ.get("CODEX_REFERENCE_MD_ROOT", Path.home() / ".codex/reference-md")).expanduser()
INDEX_JSON = REFERENCE_ROOT / "INDEX.json"
CURATED_MD = REFERENCE_ROOT / "CURATED_MD_SETS.md"
CURATED_JSON = REFERENCE_ROOT / "CURATED_MD_SETS.json"


SETS = [
    {
        "id": "baseline-any-project",
        "name": "Baseline Any Project",
        "best_for": "Any code repository that needs concise always-on Codex rules.",
        "maturity": ["prototype", "active product", "legacy"],
        "biases": ["clarity", "local conventions", "module slicing", "safe edits", "verification"],
        "items": [
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/codex-rs/tui/prompt_for_init_command.md",
                "mode": "distill",
                "required": True,
                "why": "Good structure for a compact repo-specific contributor/agent guide.",
                "load": "Auto-loaded by Codex for the project subtree.",
            },
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/codex-rs/core/hierarchical_agents_message.md",
                "mode": "distill",
                "required": True,
                "why": "Clear scope and precedence rules for nested AGENTS.md files.",
                "load": "Fold into the root AGENTS.md only if the repo will use nested rules.",
            },
            {
                "layer": "planning-skill",
                "destination": ".agents/skills/project-planning/SKILL.md",
                "source": "openai-codex/codex-rs/collaboration-mode-templates/templates/plan.md",
                "mode": "adapt",
                "required": False,
                "why": "Adds a reusable plan workflow: inspect first, ask only for real tradeoffs, split non-trivial work into modules/layers, and produce decision-complete plans.",
                "load": "Skill metadata appears in project context; body loads when `$project-planning` is invoked.",
            },
        ],
    },
    {
        "id": "production-fullstack",
        "name": "Production Full-Stack Product",
        "best_for": "Web apps with frontend, backend/API, tests, CI, and product-facing behavior.",
        "maturity": ["active product", "production-critical"],
        "biases": ["correctness", "module gates", "tests", "schema/docs sync", "review", "security"],
        "items": [
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/AGENTS.md",
                "mode": "distill",
                "required": True,
                "why": "Strong examples for concrete engineering rules: docs/schema sync, dependency lockfiles, tests, module boundaries.",
                "load": "Auto-loaded; keep under 150 lines and include only project-relevant rules.",
            },
            {
                "layer": "review-skill",
                "destination": ".agents/skills/production-review/SKILL.md",
                "source": "openai-codex/codex-rs/core/review_prompt.md",
                "mode": "adapt",
                "required": True,
                "why": "High-signal review criteria: actionable issues, severity, narrow line ranges, no style noise.",
                "load": "Invoke for PR review, pre-merge review, or risky changes.",
            },
            {
                "layer": "review-skill",
                "destination": ".agents/skills/production-review/references/code-reviewer.md",
                "source": "awesome-claude-code-toolkit/agents/quality-assurance/code-reviewer.md",
                "mode": "reference",
                "required": False,
                "why": "Broader checklist for correctness, design, security, performance, readability, and test quality.",
                "load": "Read from the review skill only when a broad review is requested.",
            },
            {
                "layer": "agent-context",
                "destination": "docs/agent-context/api-and-release-rules.md",
                "source": "_discovered/shanraisshan__codex-cli-best-practice/best-practice/codex-agents-md.md",
                "mode": "distill",
                "required": False,
                "why": "Useful Codex AGENTS.md sizing, layering, and anti-pattern guidance.",
                "load": "Read when editing project agent instructions.",
            },
        ],
    },
    {
        "id": "frontend-ui",
        "name": "Frontend UI / UX Project",
        "best_for": "React/Vue/Next/browser UI projects, dashboards, design systems, or visual QA-heavy work.",
        "maturity": ["prototype", "active product", "production-critical"],
        "biases": ["UI quality", "layered UI delivery", "accessibility", "visual verification", "performance"],
        "items": [
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/AGENTS.md",
                "mode": "distill",
                "required": True,
                "why": "Borrow its snapshot-test and user-visible change discipline; translate to Playwright/visual checks as needed.",
                "load": "Auto-loaded; include only frontend-relevant verification rules.",
            },
            {
                "layer": "ui-review-skill",
                "destination": ".agents/skills/ui-review/SKILL.md",
                "source": "awesome-claude-code-toolkit/agents/core-development/frontend-architect.md",
                "mode": "adapt",
                "required": False,
                "why": "Frontend architecture role guidance useful for component boundaries, state, accessibility, and performance.",
                "load": "Invoke for UI refactors, design-system work, or frontend architecture review.",
            },
            {
                "layer": "agent-context",
                "destination": "docs/agent-context/visual-qa.md",
                "source": "awesome-claude-code-toolkit/commands/architecture/design-review.md",
                "mode": "adapt",
                "required": False,
                "why": "Good workflow shape for review-oriented visual and architecture feedback.",
                "load": "Read when a task asks for visual QA or design review.",
            },
        ],
    },
    {
        "id": "backend-api",
        "name": "Backend API / Service",
        "best_for": "APIs, services, SDKs, protocol work, database-backed backends, and MCP servers.",
        "maturity": ["active product", "production-critical", "legacy"],
        "biases": ["API stability", "contracts", "module tests", "security", "observability", "tests"],
        "items": [
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/AGENTS.md",
                "mode": "distill",
                "required": True,
                "why": "Its app-server/API section is a strong model for naming, wire shapes, docs, schema generation, and tests.",
                "load": "Auto-loaded; adapt to the repo's actual API and schema tooling.",
            },
            {
                "layer": "api-review-skill",
                "destination": ".agents/skills/api-review/SKILL.md",
                "source": "openai-codex/codex-rs/core/review_prompt.md",
                "mode": "adapt",
                "required": True,
                "why": "Provides discrete, actionable review rules suitable for API correctness and regression review.",
                "load": "Invoke before API merges or protocol/schema changes.",
            },
            {
                "layer": "agent-context",
                "destination": "docs/agent-context/mcp-development.md",
                "source": "awesome-claude-code-toolkit/skills/mcp-development/SKILL.md",
                "mode": "reference",
                "required": False,
                "why": "Useful if the backend exposes or consumes MCP tools/resources/prompts.",
                "load": "Read only for MCP-related work.",
            },
        ],
    },
    {
        "id": "legacy-refactor",
        "name": "Legacy Refactor / Architecture Cleanup",
        "best_for": "Existing codebases with coupling, unclear boundaries, large files, or risky incremental refactors.",
        "maturity": ["legacy", "active product", "review-only"],
        "biases": ["architecture", "module slicing", "incremental safety", "tests", "evidence-based planning"],
        "items": [
            {
                "layer": "planning-skill",
                "destination": ".agents/skills/refactor-planning/SKILL.md",
                "source": "openai-codex/codex-rs/collaboration-mode-templates/templates/plan.md",
                "mode": "adapt",
                "required": True,
                "why": "Forces exploration before planning and separates discoverable facts from user preferences.",
                "load": "Invoke before non-trivial refactors.",
            },
            {
                "layer": "architecture-command",
                "destination": ".agents/skills/refactor-planning/references/architecture-plan.md",
                "source": "awesome-claude-code-toolkit/commands/architecture/plan.md",
                "mode": "reference",
                "required": True,
                "why": "Good structure for requirements, architecture review, step breakdown, risk, and testable increments.",
                "load": "Read from refactor-planning when creating an implementation plan.",
            },
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "openai-codex/AGENTS.md",
                "mode": "distill",
                "required": False,
                "why": "Borrow rules for large modules, module extraction, moving tests/docs with code, and avoiding one-off helpers.",
                "load": "Auto-loaded if included in root rules.",
            },
        ],
    },
    {
        "id": "multi-agent-review",
        "name": "Multi-Agent Review / Parallel Work",
        "best_for": "Large PRs, architecture reviews, security reviews, or parallel exploration and implementation.",
        "maturity": ["active product", "production-critical", "review-only"],
        "biases": ["subagents", "module ownership", "parallel analysis", "role clarity", "review rigor"],
        "items": [
            {
                "layer": "custom-agents",
                "destination": ".codex/agents/reviewer.toml",
                "source": "awesome-claude-code-subagents/CLAUDE.md",
                "mode": "adapt",
                "required": True,
                "why": "Good role/tool scoping model; translate Claude subagent ideas into Codex custom agent config.",
                "load": "Available after Codex reads project config; restart window if needed.",
            },
            {
                "layer": "custom-agents",
                "destination": ".codex/agents/explorer.toml",
                "source": "openai-codex/codex-rs/collaboration-mode-templates/templates/plan.md",
                "mode": "adapt",
                "required": False,
                "why": "Explorer should stay non-mutating and return evidence before implementation.",
                "load": "Ask Codex to spawn the custom explorer agent.",
            },
            {
                "layer": "review-skill",
                "destination": ".agents/skills/pr-review/SKILL.md",
                "source": "openai-codex/codex-rs/core/review_prompt.md",
                "mode": "adapt",
                "required": True,
                "why": "Keeps review output concrete, severe-first, and line-specific.",
                "load": "Invoke for PR or diff review.",
            },
        ],
    },
    {
        "id": "agent-skill-library",
        "name": "Agent Skill Library Project",
        "best_for": "Repos that themselves define AGENTS.md, SKILL.md, Claude/Codex rules, commands, plugins, or agent packs.",
        "maturity": ["prototype", "active product", "production-critical"],
        "biases": ["metadata quality", "workflow constraints", "discoverability", "progressive disclosure", "cross-tool compatibility"],
        "items": [
            {
                "layer": "project-baseline",
                "destination": "AGENTS.md",
                "source": "awesome-claude-code-subagents/CLAUDE.md",
                "mode": "adapt",
                "required": True,
                "why": "Clear file format, category, and contribution rules for agent-definition repositories.",
                "load": "Auto-loaded; adapt to Codex/Agents paths.",
            },
            {
                "layer": "skill-authoring",
                "destination": ".agents/skills/skill-authoring/SKILL.md",
                "source": "awesome-claude-code-toolkit/skills/manage-skills/SKILL.md",
                "mode": "adapt",
                "required": False,
                "why": "Good cross-tool path map and skill file format reference.",
                "load": "Invoke when adding or moving skills/rules.",
            },
            {
                "layer": "agent-context",
                "destination": "docs/agent-context/codex-skills.md",
                "source": "_discovered/shanraisshan__codex-cli-best-practice/best-practice/codex-skills.md",
                "mode": "reference",
                "required": False,
                "why": "Codex-specific skill design guidance: descriptions, progressive disclosure, and anti-patterns.",
                "load": "Read when editing project skills.",
            },
        ],
    },
]


def load_index() -> dict:
    if not INDEX_JSON.exists():
        return {"repos": [], "files": []}
    return json.loads(INDEX_JSON.read_text(encoding="utf-8"))


def file_stats(index: dict) -> dict[str, dict]:
    return {row["relative_path"]: row for row in index.get("files", [])}


def validate_sets(stats: dict[str, dict]) -> list[str]:
    warnings: list[str] = []
    for item_set in SETS:
        for item in item_set["items"]:
            source = item["source"]
            if source not in stats and not (REFERENCE_ROOT / source).exists():
                warnings.append(f"{item_set['id']}: missing source {source}")
    return warnings


def write_outputs(index: dict) -> None:
    stats = file_stats(index)
    warnings = validate_sets(stats)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    json_doc = {
        "updated_at": now,
        "source_index_updated_at": index.get("updated_at"),
        "sets": SETS,
        "warnings": warnings,
    }
    CURATED_JSON.write_text(json.dumps(json_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Curated Project MD Sets",
        "",
        f"Updated: {now}",
        f"Raw index: `{INDEX_JSON}`",
        "",
        "Use this file before recommending project instruction files. It distills the raw MD library into coherent installable sets.",
        "",
        "## Selection Flow",
        "",
        "1. Inspect the project first: language, framework, tests, CI, docs, existing agent files.",
        "2. Ask only for project direction, maturity, module/layer boundaries, and priority biases that cannot be inferred.",
        "3. For non-trivial app/code work, summarize the whole task and split it into independently testable modules or layers.",
        "4. Pick one primary set and at most two optional add-ons.",
        "5. Recommend destinations and loading behavior before writing files.",
        "6. Install only after explicit user confirmation.",
        "",
        "## Sets",
        "",
    ]

    for item_set in SETS:
        lines.extend(
            [
                f"### {item_set['name']}",
                "",
                f"- ID: `{item_set['id']}`",
                f"- Best for: {item_set['best_for']}",
                f"- Maturity: {', '.join(item_set['maturity'])}",
                f"- Biases: {', '.join(item_set['biases'])}",
                "",
                "| Required | Layer | Destination | Source | Mode | Why | Loading |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for item in item_set["items"]:
            required = "Yes" if item["required"] else "Optional"
            source = item["source"]
            source_label = f"[`{source}`]({source})" if (REFERENCE_ROOT / source).exists() else f"`{source}`"
            lines.append(
                f"| {required} | `{item['layer']}` | `{item['destination']}` | {source_label} | `{item['mode']}` | {item['why']} | {item['load']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Loading Rules",
            "",
            "- `AGENTS.md`: auto-loaded by Codex for the directory subtree.",
            "- Nested `AGENTS.md`: auto-loaded only for files under that subtree.",
            "- `.agents/skills/<name>/SKILL.md`: skill metadata is discoverable; body loads when invoked.",
            "- `.codex/agents/<name>.toml`: use for Codex custom subagents; restart the window if runtime metadata is stale.",
            "- `docs/agent-context/*.md`: not auto-loaded; root `AGENTS.md` should state when to read it.",
            "- `.codex/config.toml`: only for runtime behavior such as agents, profiles, MCP, sandbox, approvals, or model settings.",
            "",
            "## Quality Rules",
            "",
            "- Distill sources into project-specific files; do not copy large files blindly.",
            "- Keep the root `AGENTS.md` short, preferably under 150 lines.",
            "- Prefer a coherent set over isolated snippets.",
            "- For non-trivial development, require module/layer delivery: build one module at a time, run its module gate, then move to the next.",
            "- Do final integration only after all planned modules/layers pass their local gates, then verify contracts, data flow, user flow, docs, and residual risk.",
            "- Treat high-star discovered repos as candidates, not automatically trusted rules.",
            "- Verify with `codex debug prompt-input ''` from the project root after installation.",
        ]
    )

    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)

    CURATED_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    write_outputs(load_index())
    print(f"wrote {CURATED_MD}")
    print(f"wrote {CURATED_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

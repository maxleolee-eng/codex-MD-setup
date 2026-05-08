#!/usr/bin/env python3
"""Refresh local MD reference repos and build indexes for codex-MD-setup."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REFERENCE_ROOT = Path(os.environ.get("CODEX_REFERENCE_MD_ROOT", Path.home() / ".codex/reference-md")).expanduser()
DISCOVERED_DIR = REFERENCE_ROOT / "_discovered"
INDEX_MD = REFERENCE_ROOT / "INDEX.md"
INDEX_JSON = REFERENCE_ROOT / "INDEX.json"
CURATED_SCRIPT = Path(__file__).with_name("build_curated_md_sets.py")

SEED_REPOS = [
    {
        "full_name": "openai/codex",
        "dest": "openai-codex",
        "reason": "Official Codex repo with high-quality AGENTS.md, plan, review, and tool instruction examples.",
    },
    {
        "full_name": "hesreallyhim/awesome-claude-code",
        "dest": "awesome-claude-code",
        "reason": "Largest Claude Code reference index with CLAUDE.md examples, commands, hooks, and skills.",
    },
    {
        "full_name": "VoltAgent/awesome-claude-code-subagents",
        "dest": "awesome-claude-code-subagents",
        "reason": "Large collection of Claude subagent definitions useful for Codex custom agent design.",
    },
    {
        "full_name": "rohitg00/awesome-claude-code-toolkit",
        "dest": "awesome-claude-code-toolkit",
        "reason": "Broad toolkit with agents, commands, skills, rules, hooks, plugins, and templates.",
    },
    {
        "full_name": "Mizoreww/awesome-claude-code-config",
        "dest": "awesome-claude-code-config",
        "reason": "Production-style Claude Code config with memory, rules, hooks, MCP, and skills.",
    },
]

SEARCH_QUERIES = [
    "awesome claude code",
    "claude code subagents",
    "claude code skills",
    "claude code hooks commands",
    "CLAUDE.md coding agent",
    "AGENTS.md codex",
    "codex cli best practice",
    "codex skills AGENTS.md",
    "agents md coding agents",
    "ai agent rules AGENTS.md",
]

RELEVANCE_TERMS = (
    "claude code",
    "codex",
    "agents.md",
    "claude.md",
    "skill.md",
    "subagent",
    "sub-agent",
    "slash command",
    "agent rules",
    "ai coding",
    "coding agent",
    "mcp",
)

EXCLUDED_TERMS = (
    "humanizer",
    "caveman",
    "ai-generated writing",
    "token when few token",
)

INTERESTING_NAMES = {
    "AGENTS.md",
    "AGENTS.override.md",
    "CODEX.md",
    "CLAUDE.md",
    "SKILL.md",
    "README.md",
}

INTERESTING_PARTS = {
    ".claude",
    ".codex",
    ".agents",
    "agents",
    "commands",
    "skills",
    "hooks",
    "rules",
    "contexts",
    "mcp",
    "mcp-configs",
    "templates",
    "resources",
}


@dataclass
class RepoMeta:
    full_name: str
    url: str
    stars: int
    forks: int
    description: str
    updated_at: str
    dest: str
    source: str
    reason: str = ""


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + env.get("PATH", "")
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, text=True, capture_output=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc


def slug(full_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", full_name)


def gh_repo_meta(full_name: str, dest: str, source: str, reason: str = "") -> RepoMeta | None:
    proc = run(
        [
            "gh",
            "repo",
            "view",
            full_name,
            "--json",
            "nameWithOwner,url,stargazerCount,forkCount,description,updatedAt",
        ],
        check=False,
    )
    if proc.returncode != 0:
        print(f"warn: unable to inspect {full_name}: {proc.stderr.strip()}", file=sys.stderr)
        return None
    data = json.loads(proc.stdout)
    return RepoMeta(
        full_name=data["nameWithOwner"],
        url=data["url"],
        stars=int(data.get("stargazerCount") or 0),
        forks=int(data.get("forkCount") or 0),
        description=data.get("description") or "",
        updated_at=data.get("updatedAt") or "",
        dest=dest,
        source=source,
        reason=reason,
    )


def search_repos(limit_per_query: int, min_stars: int, max_total: int) -> list[RepoMeta]:
    found: dict[str, RepoMeta] = {}
    for query in SEARCH_QUERIES:
        proc = run(
            [
                "gh",
                "search",
                "repos",
                query,
                "--sort",
                "stars",
                "--limit",
                str(limit_per_query),
                "--json",
                "fullName,url,stargazersCount,forksCount,description,updatedAt,isArchived",
            ],
            check=False,
        )
        if proc.returncode != 0:
            print(f"warn: search failed for {query!r}: {proc.stderr.strip()}", file=sys.stderr)
            continue
        for item in json.loads(proc.stdout or "[]"):
            if item.get("isArchived"):
                continue
            stars = int(item.get("stargazersCount") or 0)
            if stars < min_stars:
                continue
            full_name = item["fullName"]
            description = item.get("description") or ""
            searchable = f"{full_name} {description}".lower()
            if any(term in searchable for term in EXCLUDED_TERMS):
                continue
            if not any(term in searchable for term in RELEVANCE_TERMS):
                continue
            if full_name in found:
                continue
            found[full_name] = RepoMeta(
                full_name=full_name,
                url=item["url"],
                stars=stars,
                forks=int(item.get("forksCount") or 0),
                description=description,
                updated_at=item.get("updatedAt") or "",
                dest=f"_discovered/{slug(full_name)}",
                source=f"search:{query}",
            )
    return sorted(found.values(), key=lambda r: (r.stars, r.forks), reverse=True)[:max_total]


def clone_or_update(repo: RepoMeta) -> None:
    dest = REFERENCE_ROOT / repo.dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    if (dest / ".git").exists():
        proc = run(["git", "pull", "--ff-only"], cwd=dest, check=False)
        if proc.returncode != 0:
            print(f"warn: git pull failed for {repo.full_name}: {proc.stderr.strip()}", file=sys.stderr)
        return
    if dest.exists() and any(dest.iterdir()):
        print(f"warn: destination exists without .git, skipping clone: {dest}", file=sys.stderr)
        return
    if dest.exists():
        shutil.rmtree(dest)
    run(["git", "clone", "--depth", "1", repo.url, str(dest)], check=True)


def prune_discovered(active_repos: list[RepoMeta]) -> None:
    active = {
        (REFERENCE_ROOT / repo.dest).resolve()
        for repo in active_repos
        if repo.dest.startswith("_discovered/")
    }
    if not DISCOVERED_DIR.exists():
        return
    for child in DISCOVERED_DIR.iterdir():
        if not child.is_dir():
            continue
        if child.resolve() not in active:
            print(f"prune: {child}")
            shutil.rmtree(child)


def is_interesting_md(path: Path, repo_root: Path) -> bool:
    if path.name in INTERESTING_NAMES:
        return True
    parts = set(path.relative_to(repo_root).parts[:-1])
    if parts.intersection(INTERESTING_PARTS):
        return True
    name = path.name.lower()
    return any(token in name for token in ("agent", "claude", "codex", "skill", "command", "hook", "rule", "plan", "review"))


def line_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def classify(path: Path) -> str:
    parts = set(path.parts)
    name = path.name.lower()
    if path.name in {"AGENTS.md", "AGENTS.override.md", "CODEX.md"}:
        return "project-rules"
    if path.name == "CLAUDE.md":
        return "claude-rules"
    if path.name == "SKILL.md" or "skills" in parts:
        return "skills"
    if "agents" in parts or "subagents" in parts:
        return "agents"
    if "commands" in parts or "command" in name:
        return "commands"
    if "hooks" in parts or "hook" in name:
        return "hooks"
    if "rules" in parts or "rule" in name:
        return "rules"
    if "plan" in name:
        return "planning"
    if "review" in name:
        return "review"
    return "reference"


def collect_files(repos: list[RepoMeta]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for repo in repos:
        repo_root = REFERENCE_ROOT / repo.dest
        if not repo_root.exists():
            continue
        for path in repo_root.rglob("*.md"):
            rel_parts = path.relative_to(repo_root).parts
            if ".git" in rel_parts:
                continue
            if not is_interesting_md(path, repo_root):
                continue
            rows.append(
                {
                    "repo": repo.full_name,
                    "repo_stars": repo.stars,
                    "repo_forks": repo.forks,
                    "category": classify(path),
                    "path": str(path),
                    "relative_path": str(path.relative_to(REFERENCE_ROOT)),
                    "lines": line_count(path),
                }
            )
    return sorted(rows, key=lambda r: (str(r["category"]), -int(r["repo_stars"]), str(r["relative_path"])))


def write_index(repos: list[RepoMeta], files: list[dict[str, object]]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    INDEX_JSON.write_text(
        json.dumps(
            {
                "updated_at": now,
                "repos": [repo.__dict__ for repo in repos],
                "files": files,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    by_category: dict[str, list[dict[str, object]]] = {}
    for row in files:
        by_category.setdefault(str(row["category"]), []).append(row)

    lines = [
        "# Reference MD Library Index",
        "",
        f"Updated: {now}",
        "",
        "This index is generated by `codex-MD-setup/scripts/refresh_reference_md.py`.",
        "",
        "## Repositories",
        "",
        "| Stars | Forks | Repo | Source | Notes |",
        "|---:|---:|---|---|---|",
    ]
    for repo in sorted(repos, key=lambda r: (r.stars, r.forks), reverse=True):
        repo_path = repo.dest
        note = repo.reason or repo.description.replace("\n", " ")
        lines.append(f"| {repo.stars} | {repo.forks} | [{repo.full_name}]({repo_path}) | `{repo.source}` | {note} |")

    lines.extend(["", "## Interesting MD Files", ""])
    for category in sorted(by_category):
        rows = by_category[category]
        lines.extend([f"### {category}", "", "| Repo stars | Lines | File | Repo |", "|---:|---:|---|---|"])
        for row in rows[:80]:
            rel = str(row["relative_path"])
            lines.append(f"| {row['repo_stars']} | {row['lines']} | [{rel}]({rel}) | {row['repo']} |")
        if len(rows) > 80:
            lines.append(f"|  |  | ... {len(rows) - 80} more files in `INDEX.json` |  |")
        lines.append("")

    INDEX_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-per-query", type=int, default=8)
    parser.add_argument("--min-stars", type=int, default=50)
    parser.add_argument("--max-discovered", type=int, default=24)
    parser.add_argument("--no-discover", action="store_true")
    args = parser.parse_args()

    REFERENCE_ROOT.mkdir(parents=True, exist_ok=True)
    DISCOVERED_DIR.mkdir(parents=True, exist_ok=True)

    repos: list[RepoMeta] = []
    for seed in SEED_REPOS:
        meta = gh_repo_meta(seed["full_name"], seed["dest"], "seed", seed["reason"])
        if meta:
            repos.append(meta)

    if not args.no_discover:
        known = {repo.full_name for repo in repos}
        for repo in search_repos(args.limit_per_query, args.min_stars, args.max_discovered):
            if repo.full_name not in known:
                repos.append(repo)
                known.add(repo.full_name)

    prune_discovered(repos)

    for repo in repos:
        print(f"refresh: {repo.full_name} -> {repo.dest}")
        clone_or_update(repo)

    files = collect_files(repos)
    write_index(repos, files)
    print(f"wrote {INDEX_MD}")
    print(f"wrote {INDEX_JSON}")
    if CURATED_SCRIPT.exists():
        proc = run([str(CURATED_SCRIPT)], check=True)
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

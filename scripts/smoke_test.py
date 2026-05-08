#!/usr/bin/env python3
"""Smoke-test codex-MD-setup and build the local raw/distilled MD library."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REFRESH_SCRIPT = SKILL_DIR / "scripts/refresh_reference_md.py"
REFERENCE_ROOT = Path(os.environ.get("CODEX_REFERENCE_MD_ROOT", Path.home() / ".codex/reference-md")).expanduser()


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + env.get("PATH", "")
    env.setdefault("CODEX_REFERENCE_MD_ROOT", str(REFERENCE_ROOT))
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc


def require(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"missing required file: {path}")


def main() -> int:
    require(SKILL_DIR / "SKILL.md")
    require(REFRESH_SCRIPT)
    require(SKILL_DIR / "scripts/build_curated_md_sets.py")
    require(SKILL_DIR / "references/catalog.md")

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    if "name: codex-MD-setup" not in skill_text:
        raise RuntimeError("SKILL.md frontmatter must contain `name: codex-MD-setup`")

    gh = run(["gh", "auth", "status"], check=False)
    if gh.returncode != 0:
        print("warn: gh auth status failed; GitHub discovery may be limited", file=sys.stderr)

    run(
        [
            sys.executable,
            str(REFRESH_SCRIPT),
            "--limit-per-query",
            "4",
            "--min-stars",
            "50",
            "--max-discovered",
            "12",
        ],
        check=True,
    )

    index_md = REFERENCE_ROOT / "INDEX.md"
    index_json = REFERENCE_ROOT / "INDEX.json"
    curated_md = REFERENCE_ROOT / "CURATED_MD_SETS.md"
    curated_json = REFERENCE_ROOT / "CURATED_MD_SETS.json"
    for path in (index_md, index_json, curated_md, curated_json):
        require(path)
        if path.stat().st_size < 100:
            raise RuntimeError(f"generated file is unexpectedly small: {path}")

    index = json.loads(index_json.read_text(encoding="utf-8"))
    curated = json.loads(curated_json.read_text(encoding="utf-8"))
    repos = index.get("repos", [])
    files = index.get("files", [])
    sets = curated.get("sets", [])
    if len(repos) < 5:
        raise RuntimeError(f"expected at least 5 indexed repos, got {len(repos)}")
    if len(files) < 20:
        raise RuntimeError(f"expected at least 20 indexed MD files, got {len(files)}")
    if len(sets) < 6:
        raise RuntimeError(f"expected at least 6 curated MD sets, got {len(sets)}")

    installed_path = Path.home() / ".codex/skills/codex-MD-setup"
    if SKILL_DIR.resolve() == installed_path.resolve():
        prompt = run(["codex", "debug", "prompt-input", ""], check=False)
        if prompt.returncode == 0 and "codex-MD-setup" not in prompt.stdout:
            print("warn: codex debug prompt-input did not show codex-MD-setup in this shell", file=sys.stderr)

    print("CODEx_MD_SETUP_SMOKE_OK")
    print(f"skill_dir: {SKILL_DIR}")
    print(f"reference_root: {REFERENCE_ROOT}")
    print(f"repos: {len(repos)}")
    print(f"md_files: {len(files)}")
    print(f"curated_sets: {len(sets)}")
    print(f"index: {index_md}")
    print(f"curated: {curated_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

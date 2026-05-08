#!/usr/bin/env python3
"""Install a weekly macOS LaunchAgent for codex-MD-setup reference refreshes."""

from __future__ import annotations

import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path


DEFAULT_LABEL = "com.codex.md-setup.refresh"
DEFAULT_ROOT = Path.home() / ".codex/reference-md"


def run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:" + env.get("PATH", "")
    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
    return proc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default=DEFAULT_LABEL)
    parser.add_argument("--reference-root", default=str(DEFAULT_ROOT))
    parser.add_argument("--weekday", type=int, default=1, help="1=Sunday, 2=Monday, ... 7=Saturday")
    parser.add_argument("--hour", type=int, default=9)
    parser.add_argument("--minute", type=int, default=20)
    args = parser.parse_args()

    script = Path(__file__).resolve().with_name("refresh_reference_md.py")
    if not script.exists():
        print(f"error: missing refresh script: {script}", file=sys.stderr)
        return 1

    reference_root = Path(args.reference_root).expanduser()
    log_root = reference_root / "_logs"
    log_root.mkdir(parents=True, exist_ok=True)
    plist_dir = Path.home() / "Library/LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_path = plist_dir / f"{args.label}.plist"

    program = [
        str(script),
        "--limit-per-query",
        "8",
        "--min-stars",
        "50",
        "--max-discovered",
        "24",
    ]
    plist = {
        "Label": args.label,
        "ProgramArguments": program,
        "EnvironmentVariables": {
            "CODEX_REFERENCE_MD_ROOT": str(reference_root),
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        },
        "StartCalendarInterval": {
            "Weekday": args.weekday,
            "Hour": args.hour,
            "Minute": args.minute,
        },
        "StandardOutPath": str(log_root / "launchd.out.log"),
        "StandardErrorPath": str(log_root / "launchd.err.log"),
        "WorkingDirectory": str(script.parent),
        "RunAtLoad": False,
    }

    with plist_path.open("wb") as fh:
        plistlib.dump(plist, fh, sort_keys=False)

    gui_target = f"gui/{os.getuid()}/{args.label}"
    run(["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)], check=False)
    boot = run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)], check=False)
    if boot.returncode != 0 and "service already loaded" not in boot.stderr.lower():
        print(f"warn: launchctl bootstrap failed: {boot.stderr.strip()}", file=sys.stderr)
    run(["launchctl", "enable", gui_target], check=False)

    print(f"installed: {plist_path}")
    print(f"label: {args.label}")
    print(f"schedule: weekday={args.weekday} {args.hour:02d}:{args.minute:02d}")
    print(f"reference_root: {reference_root}")
    print(f"logs: {log_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

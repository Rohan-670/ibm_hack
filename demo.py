#!/usr/bin/env python3
"""
RepoPilot demo runner. Requires ONLY Python (already on your machine) and
git (already on your machine, since your earlier reports show real diffs).
No pip install, no venv, no third-party packages needed for this. Run it
exactly as-is:

    python demo.py            (or: python3 demo.py, or: py demo.py on Windows)

This does everything: runs PR mode on the planted-bug branch, runs
onboarding mode, and prints both reports to your screen as well as writing
them to release-report.md and onboarding-brief.md.
"""
import subprocess
import sys
import os

# Ensure stdout can handle Unicode (emoji, arrows) on Windows terminals that
# default to a narrow encoding like cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Propagate UTF-8 to child processes (orchestrator.run prints emoji too).
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def line(char="="):
    print(char * 70)


def run(cmd):
    """Run a subprocess, streaming its output live to the console."""
    print(f"$ {' '.join(cmd)}", flush=True)
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        stdout=None,
        stderr=None,
    )
    if result.returncode != 0:
        print(f"\n[!] Command exited with code {result.returncode}. See output above.")
    return result.returncode


def show_file(path, title):
    line()
    print(title)
    line()
    full_path = os.path.join(REPO_ROOT, path)
    if os.path.isfile(full_path):
        with open(full_path, encoding="utf-8", errors="replace") as fh:
            print(fh.read())
    else:
        print(f"[!] {path} was not created — check the command output above for errors.")
    print()


def main():
    py = sys.executable  # use whichever python is running this script

    line()
    print("RepoPilot demo — zero setup required (stdlib + git only)")
    line()
    print()

    print(">>> Step 1: confirm git and branches are visible\n")
    run(["git", "-C", REPO_ROOT, "branch", "-a"])
    run(["git", "-C", REPO_ROOT, "log", "--oneline", "--all"])
    print()

    print(">>> Step 2: run PR mode against the planted-bug branch\n")
    run([py, "-m", "orchestrator.run", "--mode=pr", "--base=master", "--branch=feature/bulk-update"])
    print()

    print(">>> Step 3: run onboarding mode\n")
    run([py, "-m", "orchestrator.run", "--mode=onboard"])
    print()

    show_file("release-report.md", "RELEASE READINESS REPORT")
    show_file("onboarding-brief.md", "ONBOARDING BRIEF")

    line()
    print("Done. Both reports are also saved as files in this folder for your demo.")
    print("Optional next step (not required): install Flask to also run the live")
    print("sample app and its test suite — see README.md 'Optional: run the live app'.")
    line()


if __name__ == "__main__":
    main()

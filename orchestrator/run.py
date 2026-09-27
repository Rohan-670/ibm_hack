"""
RepoPilot orchestrator.

Usage:
    python -m orchestrator.run --mode=pr --base=master --branch=feature/bulk-update
    python -m orchestrator.run --mode=onboard
<<<<<<< HEAD

This runs the rule-based reference agents in orchestrator/agents/*.py by
default. To run against real Bob Shell instead, see bob_backend.py — swap
the calls in _run_pr_mode() below from e.g. `diff_analyst.run(...)` to
`bob_backend.run_bob_agent("bob-agents/diff-analyst.md", ..., repo_root)`.
Everything downstream (report_builder, scoring, this file's timing/parallel
logic) is agnostic to which backend produced the findings.
=======
>>>>>>> 659f56f (ALL final)
"""
import argparse
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from .agents import diff_analyst, test_gap, doc_sync, compliance, onboarding
from . import report_builder


def _timed(name, fn):
    start = time.perf_counter()
    result = fn()
    end = time.perf_counter()
    return name, result, (start, end)


def run_pr_mode(repo_root, base_branch, feature_branch):
    print(f"\n=== RepoPilot: PR mode ({base_branch}..{feature_branch}) ===\n")
    print("Firing diff-analyst, test-gap-agent, doc-sync-agent, compliance-agent in PARALLEL...\n")

    all_findings = []
    timings = {}

    tasks = {
<<<<<<< HEAD
        "diff-analyst": lambda: diff_analyst.run(repo_root, base_branch, feature_branch),
        "test-gap-agent": lambda: test_gap.run(repo_root, base_branch, feature_branch),
        "doc-sync-agent": lambda: doc_sync.run(repo_root, base_branch, feature_branch),
=======
        "diff-analyst":    lambda: diff_analyst.run(repo_root, base_branch, feature_branch),
        "test-gap-agent":  lambda: test_gap.run(repo_root, base_branch, feature_branch),
        "doc-sync-agent":  lambda: doc_sync.run(repo_root, base_branch, feature_branch),
>>>>>>> 659f56f (ALL final)
        "compliance-agent": lambda: compliance.run(repo_root, base_branch, feature_branch),
    }

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_timed, name, fn): name for name, fn in tasks.items()}
        for future in as_completed(futures):
            name, result, (start, end) = future.result()
            timings[name] = (start, end)
            if name == "test-gap-agent":
                findings, stubs = result
                all_findings.extend(findings)
<<<<<<< HEAD
                print(f"  [{name}] done in {end - start:.3f}s — {len(findings)} finding(s), "
                      f"{len(stubs)} test stub(s) written")
            else:
                all_findings.extend(result)
                print(f"  [{name}] done in {end - start:.3f}s — {len(result)} finding(s)")
=======
                print(f"  [{name}] done in {end - start:.3f}s \u2014 {len(findings)} finding(s), "
                      f"{len(stubs)} test stub(s) written")
            else:
                all_findings.extend(result)
                print(f"  [{name}] done in {end - start:.3f}s \u2014 {len(result)} finding(s)")
>>>>>>> 659f56f (ALL final)

    report_path, score = report_builder.build_release_report(repo_root, all_findings, timings)
    print(f"\nReadiness score: {score}/100")
    print(f"Report written to: {report_path}\n")


def run_onboarding_mode(repo_root):
    print("\n=== RepoPilot: Onboarding mode ===\n")
    print("Note: for the richest brief, run PR mode at least once first so")
    print("setup-checklist.json (from compliance-agent) exists to reuse.\n")
    start = time.perf_counter()
    out_path = onboarding.run(repo_root)
    end = time.perf_counter()
    print(f"onboarding-agent done in {end - start:.3f}s")
    print(f"Onboarding brief written to: {out_path}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pr", "onboard"], required=True)
    parser.add_argument("--base", default="master")
    parser.add_argument("--branch", default="feature/bulk-update")
    parser.add_argument("--repo-root", default=os.getcwd())
    args = parser.parse_args()

    if args.mode == "pr":
        run_pr_mode(args.repo_root, args.base, args.branch)
    else:
        run_onboarding_mode(args.repo_root)


if __name__ == "__main__":
    main()

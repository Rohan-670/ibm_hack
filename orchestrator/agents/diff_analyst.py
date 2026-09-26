"""
Rule-based reference implementation of the `diff-analyst` agent.

This exists so RepoPilot is fully runnable and demoable without spending
Bobcoins or requiring live Bob access. During the hackathon, swap this out
for orchestrator/bob_backend.py, which sends bob-agents/diff-analyst.md as
the system prompt to a real Bob Shell session. Both implementations honor
the same output-schema.md contract, so the orchestrator doesn't care which
one produced the findings.
"""
import re
import json

from .. import diffparse, gitutil

ROUTE_DECORATOR = re.compile(r"@(bp|app)\.(route|get|post|put|delete|patch)\b")
ENV_READ = re.compile(r"os\.(environ|getenv)")
DICT_KEY = re.compile(r'"(\w+)"\s*:')


def run(repo_root, base_branch, feature_branch, sample_project_path="sample-project"):
    diff_text = gitutil.diff(repo_root, base_branch, feature_branch, sample_project_path)
    files = diffparse.parse(diff_text)

    findings = []
    for f in files:
        file_path = f["file"]
        added = diffparse.added_lines(f)
        removed = diffparse.removed_lines(f)
        risk = gitutil.churn(repo_root, file_path)

        findings.extend(_detect_field_renames(file_path, f, risk))
        findings.extend(_detect_new_routes(file_path, added, risk))
        findings.extend(_detect_new_env_vars(file_path, added, risk))

    return findings


def _detect_field_renames(file_path, parsed_file, risk):
    findings = []
    for hunk in parsed_file["hunks"]:
        removed_keys = {k for _, text in hunk["removed"] for k in DICT_KEY.findall(text)}
        added_keys = {k for _, text in hunk["added"] for k in DICT_KEY.findall(text)}
        only_removed = removed_keys - added_keys
        only_added = added_keys - removed_keys
        if only_removed and only_added:
            for old_key in only_removed:
                for new_key in only_added:
                    findings.append({
                        "file": file_path,
                        "line": hunk["new_start"],
                        "severity": "blocker",
                        "category": "breaking_change",
                        "description": (
                            f"Response/dict key '{old_key}' appears to have been renamed to "
                            f"'{new_key}' with no version bump or deprecation notice "
                            f"(file churn score: {risk} commits/20). Any existing client "
                            f"reading '{old_key}' will break."
                        ),
                        "suggested_fix": (
                            f"Either keep '{old_key}' as an alias for '{new_key}', or bump the "
                            f"API version and document the rename in CHANGELOG.md."
                        ),
                    })
    return findings


def _detect_new_routes(file_path, added, risk):
    findings = []
    for lineno, text in added:
        if ROUTE_DECORATOR.search(text):
            findings.append({
                "file": file_path,
                "line": lineno,
                "severity": "info",
                "category": "breaking_change",
                "description": (
                    f"New route added: `{text.strip()}` (churn score: {risk}). Not breaking "
                    f"by itself, but new surface area — confirm test-gap-agent covers it."
                ),
                "suggested_fix": None,
            })
    return findings


def _detect_new_env_vars(file_path, added, risk):
    findings = []
    for lineno, text in added:
        if ENV_READ.search(text):
            findings.append({
                "file": file_path,
                "line": lineno,
                "severity": "warning",
                "category": "breaking_change",
                "description": (
                    f"New environment variable read introduced: `{text.strip()}`. Confirm it's "
                    f"documented in .env.example and README.md (compliance-agent should verify)."
                ),
                "suggested_fix": "Add the variable to .env.example with a one-line comment.",
            })
    return findings


if __name__ == "__main__":
    import sys
    repo_root, base, feature = sys.argv[1], sys.argv[2], sys.argv[3]
    print(json.dumps(run(repo_root, base, feature), indent=2))

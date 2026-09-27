import os
<<<<<<< HEAD
=======
import re
>>>>>>> 659f56f (ALL final)

SEVERITY_PENALTY = {"blocker": 25, "warning": 10, "info": 0}


def build_release_report(repo_root, all_findings, timings):
    score = 100
    for finding in all_findings:
        score -= SEVERITY_PENALTY.get(finding.get("severity", "info"), 0)
    score = max(score, 0)

    blockers = [f for f in all_findings if f.get("severity") == "blocker"]
    warnings = [f for f in all_findings if f.get("severity") == "warning"]
<<<<<<< HEAD
    infos = [f for f in all_findings if f.get("severity") == "info"]
=======
    infos    = [f for f in all_findings if f.get("severity") == "info"]
>>>>>>> 659f56f (ALL final)

    lines = [
        "# Release Readiness Report",
        "",
        f"## Score: {score} / 100",
        "",
        f"**{len(blockers)} blocker(s), {len(warnings)} warning(s), {len(infos)} info item(s)**",
        "",
        "## Agent execution timing (proof of parallel run)",
        "",
    ]
<<<<<<< HEAD
    for agent, (start, end) in timings.items():
        lines.append(f"- `{agent}`: started {start:.3f}s, finished {end:.3f}s (elapsed {end - start:.3f}s)")
    lines.append("")

    for title, items in [("🚫 Blockers (must fix before merge)", blockers),
                          ("⚠️ Warnings", warnings),
                          ("ℹ️ Info", infos)]:
=======
    t0 = min(start for start, _ in timings.values()) if timings else 0
    for agent, (start, end) in timings.items():
        lines.append(
            f"- `{agent}`: started +{start - t0:.3f}s, finished +{end - t0:.3f}s "
            f"(elapsed {end - start:.3f}s)"
        )
    lines.append("")

    for title, items in [
        ("\U0001f6ab Blockers (must fix before merge)", blockers),
        ("\u26a0\ufe0f Warnings", warnings),
        ("\u2139\ufe0f Info", infos),
    ]:
>>>>>>> 659f56f (ALL final)
        lines.append(f"## {title}")
        lines.append("")
        if not items:
            lines.append("_None_")
        for f in items:
            loc = f"{f.get('file')}:{f.get('line')}" if f.get("file") else "(repo-level)"
<<<<<<< HEAD
            lines.append(f"- **[{f.get('category')}]** `{loc}` — {f.get('description')}")
=======
            lines.append(f"- **[{f.get('category')}]** `{loc}` \u2014 {f.get('description')}")
>>>>>>> 659f56f (ALL final)
            if f.get("suggested_fix"):
                lines.append(f"  - Fix: {f.get('suggested_fix')}")
        lines.append("")

    report = "\n".join(lines)
    out_path = os.path.join(repo_root, "release-report.md")
<<<<<<< HEAD
    with open(out_path, "w") as fh:
=======
    with open(out_path, "w", encoding="utf-8") as fh:
>>>>>>> 659f56f (ALL final)
        fh.write(report)
    return out_path, score

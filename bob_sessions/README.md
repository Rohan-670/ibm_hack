# bob_sessions/

This folder is a **required submission deliverable** per the hackathon guide.

During the hackathon, for every meaningful task you run in Bob IDE:

1. Open Bob IDE → chat panel → **Views and More Actions → History**.
2. Select the task related to this project.
3. Select the task header to see the consumption summary → **screenshot it**.
4. From the same view, select **Export task history** → save the markdown file.
5. Drop both files in this folder.

Do this at minimum for:
- The `/init` run that generated `sample-project/AGENTS.md`
- Building each of the 5 custom modes in `bob-agents/`
- At least one full `diff-analyst` run against `feature/bulk-update`
- At least one full `onboarding-agent` run

**Before pushing to a public repo:** double-check none of these exports
contain API keys, tokens, or credentials. Strip anything sensitive first —
an exposed IBM Cloud/Bob credential gets your account deactivated.

This repo currently ships with `orchestrator/agents/*.py`, a rule-based
reference implementation, so the pipeline is fully runnable and demoable
even before you've spent a single Bobcoin. Use that to validate the
approach, then run the same tasks for real through Bob IDE and drop the
exports here as your evidence trail.

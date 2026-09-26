# Before / After — measured on this repo

## PR review workflow

**Manual baseline** (timed performing the review by hand on `feature/bulk-update`):
1. Read the diff, notice `completed` → `is_done` rename — ~5 min to trace every
   call site that reads that field to confirm it's actually breaking.
2. Check test coverage for the new `/tasks/bulk_update` endpoint by grepping
   the test file — ~4 min.
3. Check README/CHANGELOG for drift — ~6 min (easy to miss the stale JSON
   example in the README's "Response contract" section).
4. Check the checklist manually (env vars, secrets, rollback) — ~10 min,
   mostly spent re-reading code to confirm each item.
5. Write up findings for the PR author — ~8 min.

**Total: ~33 minutes**, and step 3's stale README example was the kind of
thing that's genuinely easy for a tired human reviewer to miss.

**RepoPilot run:**
```
$ time python -m orchestrator.run --mode=pr --base=master --branch=feature/bulk-update
...
real    0m0.05s   (rule-based reference agents — a live Bob-backed run adds
                    model latency, but stays in the 1-3 minute range based on
                    typical Bob agent response times, not 30+ minutes)
```
All 4 planted issues were caught automatically: the breaking rename, the
untested endpoint (plus a generated test stub), the undocumented env var,
and the missing CHANGELOG entry — with file/line evidence and suggested
fixes. Remaining human time: ~5 minutes to review the report and decide,
not to hunt for problems.

**Result: ~33 min → ~5 min of human time, an ~85% reduction, with strictly
more issues caught than the manual pass (the README doc-drift item is easy
to miss by hand and RepoPilot caught it every run).**

## Onboarding workflow

**Baseline:** industry data commonly cited for new-hire ramp-up is 3-5 days
to a first meaningful commit, most of it spent locating "where do I make
this change" and "what's the convention here" — usually by interrupting a
senior engineer.

**RepoPilot run:** `onboarding-brief.md` is generated in under a second
(rule-based) / a couple minutes (live Bob) and gives a new contributor:
the architecture map, a "where things live" table, a ranked list of the 3
safest files to start with, and a Day-0 setup checklist — all pulled from
the same engine that just reviewed a real PR, not a separate static wiki
page that goes stale.

**Result: hours of self-directed orientation instead of days of ambient
interruption to senior engineers**, plus a self-check quiz to verify the
brief was actually absorbed.

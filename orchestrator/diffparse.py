"""
Minimal unified-diff parser. Good enough to drive heuristic analysis without
pulling in a third-party dependency.
"""
import re

FILE_HEADER = re.compile(r"^diff --git a/(.*) b/(.*)$")
HUNK_HEADER = re.compile(r"^@@ -(\d+),?\d* \+(\d+),?\d* @@")


def parse(diff_text):
    """
    Returns a list of dicts:
    {"file": str, "hunks": [{"new_start": int, "added": [(lineno, text)],
                              "removed": [(lineno, text)]}]}
    """
    files = []
    current_file = None
    current_hunk = None
    new_lineno = 0

    for line in diff_text.splitlines():
        m = FILE_HEADER.match(line)
        if m:
            current_file = {"file": m.group(2), "hunks": []}
            files.append(current_file)
            current_hunk = None
            continue

        hm = HUNK_HEADER.match(line)
        if hm and current_file is not None:
            new_lineno = int(hm.group(2))
            current_hunk = {"new_start": new_lineno, "added": [], "removed": []}
            current_file["hunks"].append(current_hunk)
            continue

        if current_hunk is None:
            continue

        if line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            current_hunk["added"].append((new_lineno, line[1:]))
            new_lineno += 1
        elif line.startswith("-"):
            current_hunk["removed"].append((new_lineno, line[1:]))
        else:
            new_lineno += 1

    return files


def added_lines(parsed_file):
    return [t for h in parsed_file["hunks"] for t in h["added"]]


def removed_lines(parsed_file):
    return [t for h in parsed_file["hunks"] for t in h["removed"]]

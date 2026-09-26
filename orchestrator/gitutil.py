import subprocess


def run_git(repo_root, *args):
    result = subprocess.run(
        ["git", "-C", repo_root, *args],
        capture_output=True,
        text=True,
    )
    return result.stdout


def diff(repo_root, base_branch, feature_branch, path="."):
    return run_git(repo_root, "diff", base_branch, feature_branch, "--", path)


def churn(repo_root, file_path, limit=20):
    out = run_git(repo_root, "log", f"-{limit}", "--oneline", "--", file_path)
    return len([l for l in out.splitlines() if l.strip()])

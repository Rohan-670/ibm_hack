import subprocess
<<<<<<< HEAD
=======
import sys
>>>>>>> 659f56f (ALL final)


def run_git(repo_root, *args):
    result = subprocess.run(
        ["git", "-C", repo_root, *args],
        capture_output=True,
        text=True,
    )
<<<<<<< HEAD
=======
    if result.returncode != 0:
        print(f"WARNING: git {' '.join(args)} failed: {result.stderr.strip()}", file=sys.stderr)
>>>>>>> 659f56f (ALL final)
    return result.stdout


def diff(repo_root, base_branch, feature_branch, path="."):
<<<<<<< HEAD
    return run_git(repo_root, "diff", base_branch, feature_branch, "--", path)
=======
    text = run_git(repo_root, "diff", base_branch, feature_branch, "--", path)
    if not text.strip():
        print(
            f"WARNING: 'git diff {base_branch} {feature_branch} -- {path}' returned nothing. "
            f"Check that {repo_root} is a real git repo (does it have a .git/ folder?) and that "
            f"both branches exist (`git branch -a`).",
            file=sys.stderr,
        )
    return text
>>>>>>> 659f56f (ALL final)


def churn(repo_root, file_path, limit=20):
    out = run_git(repo_root, "log", f"-{limit}", "--oneline", "--", file_path)
    return len([l for l in out.splitlines() if l.strip()])

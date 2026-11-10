"""Lesson 3: a job that can't do its work must fail loudly.

Two tools:
  fail(msg)              print to stderr and exit non-zero, so schedulers notice.
  require_work(n, what)  turn "ran fine, did nothing" into a failure.

    python fail_loudly.py check-inputs queue.json      # exits 1 if missing/empty
"""
import json
import sys
from pathlib import Path


def fail(msg, code=1):
    print(f"FAILED: {msg}", file=sys.stderr)
    sys.exit(code)


def require_work(done, what, allow_idle=False):
    """Call at the end of a scheduled run with how many items it actually handled."""
    if done == 0 and not allow_idle:
        fail(f"Run finished but handled 0 {what}. Check inputs, sign-in and which machine this ran on.")
    print(f"OK: handled {done} {what}.")


def check_inputs(*paths):
    """Fail fast if the files this job depends on aren't on this machine."""
    for p in map(Path, paths):
        if not p.exists():
            fail(f"Missing {p.resolve()} — is this running on the machine that has the files?")
        if p.suffix == ".json" and not json.loads(p.read_text(encoding="utf-8") or "null"):
            fail(f"{p} is empty.")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "check-inputs":
        check_inputs(*sys.argv[2:])
        print("Inputs present.")
    else:
        print(__doc__)

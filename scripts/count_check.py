"""Check that no ticket was lost or added between stages.

Usage: python scripts/count_check.py <stage: 01|02|03|04|05> <run_id>
Prints COUNT OK or COUNT FAIL. Exit code 1 on FAIL.
"""
import sys

from common import load_stage, routing


def ids(items):
    return [item.get("id") for item in items]


def check(stage, run_id):
    if stage == "01":
        total = len(load_stage(run_id, "00_input.json"))
        kept = load_stage(run_id, "01_intake.json")
        rejected = load_stage(run_id, "01_rejected.json")
        if total == len(kept) + len(rejected):
            return True, f"COUNT OK {total} = {len(kept)} + {len(rejected)}"
        return False, f"COUNT FAIL {total} != {len(kept)} + {len(rejected)}"

    files = {"02": ("01_intake.json", "02_classify.json"),
             "03": ("02_classify.json", "03_route.json"),
             "04": ("03_route.json", "04_lookup.json"),
             "05": ("04_lookup.json", "05_reply.json")}
    if stage not in files:
        return False, "COUNT FAIL unknown stage"
    before, after = (load_stage(run_id, name) for name in files[stage])
    if len(before) != len(after):
        missing = sorted(set(ids(before)) - set(ids(after)))
        return False, f"COUNT FAIL {len(before)} != {len(after)} (missing: {', '.join(map(str, missing)) or 'none'})"
    if sorted(ids(before)) != sorted(ids(after)):
        return False, "COUNT FAIL ids differ between stages"
    if stage == "03":
        teams = set(routing().values())
        bad = [item["id"] for item in after if item.get("team") not in teams]
        if bad:
            return False, f"COUNT FAIL tickets without exactly one valid team: {', '.join(bad)}"
    if stage == "04":
        bad = [item["id"] for item in after if not isinstance(item.get("facts"), dict) or "status" not in item["facts"]]
        if bad:
            return False, f"COUNT FAIL tickets without a lookup result: {', '.join(bad)}"
    return True, f"COUNT OK {len(before)} = {len(after)}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: count_check.py <01|02|03|04|05> <run_id>")
        sys.exit(2)
    ok, message = check(sys.argv[1], sys.argv[2])
    print(message)
    sys.exit(0 if ok else 1)

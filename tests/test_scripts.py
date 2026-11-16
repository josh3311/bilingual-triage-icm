"""Tests for the checking scripts. Run with: python -m unittest discover -s tests -v

These prove the checks catch real mistakes, not only that the happy path passes.
"""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_sample  # noqa: E402
import check_classification  # noqa: E402
import check_reply  # noqa: E402
from common import config, load_json, mulberry32, routing, seeded_sample  # noqa: E402
from detect_language import detect  # noqa: E402
from route_ticket import route_all  # noqa: E402
from validate_ticket import validate_all  # noqa: E402

RUN = "2026-11-15_01"
CFG = config()
TABLE = routing()


def reply_items():
    return load_json(ROOT / "runs" / RUN / "04_reply.json")


class TestIntake(unittest.TestCase):
    def test_bad_tickets_are_rejected_with_reasons(self):
        valid, rejected = validate_all(load_json(ROOT / "tests" / "bad_tickets.json"))
        self.assertEqual([t["id"] for t in valid], ["T101", "T106"])
        reasons = [r["reason"] for r in rejected]
        self.assertEqual(len(rejected), 5)
        self.assertTrue(any("missing or empty field body" in r for r in reasons))
        self.assertTrue(any("body must be 10 to 2000" in r for r in reasons))
        self.assertTrue(any("duplicate id" in r for r in reasons))
        self.assertTrue(any("id must be T plus 3 digits" in r for r in reasons))
        self.assertTrue(any("not a real date" in r for r in reasons))

    def test_all_30_sample_tickets_are_valid(self):
        valid, rejected = validate_all(load_json(ROOT / "data" / "sample_tickets.json"))
        self.assertEqual((len(valid), len(rejected)), (30, 0))

    def test_language_detection_matches_the_sample_set(self):
        # By design odd ids are English and even ids are French.
        for ticket in load_json(ROOT / "data" / "sample_tickets.json"):
            expected = "EN" if int(ticket["id"][1:]) % 2 == 1 else "FR"
            self.assertEqual(detect(ticket["subject"] + " " + ticket["body"])[0], expected, ticket["id"])

    def test_language_tie_is_english_with_low_confidence(self):
        self.assertEqual(detect("12345"), ("EN", "low"))


class TestClassification(unittest.TestCase):
    def setUp(self):
        self.ids = {t["id"] for t in load_json(ROOT / "runs" / RUN / "01_intake.json")}
        self.item = copy.deepcopy(load_json(ROOT / "runs" / RUN / "02_classify.json")[0])

    def test_valid_item_has_no_problems(self):
        self.assertEqual(check_classification.problems(self.item, self.ids, CFG), [])

    def test_invented_category_is_caught(self):
        self.item["category"] = "shipping"
        self.assertTrue(check_classification.problems(self.item, self.ids, CFG))

    def test_bad_priority_and_flag_are_caught(self):
        self.item["priority"] = "P9"
        self.item["needs_human"] = "yes"
        self.assertEqual(len(check_classification.problems(self.item, self.ids, CFG)), 2)


class TestRouting(unittest.TestCase):
    def test_every_category_has_exactly_one_team(self):
        for category in CFG["categories"]:
            self.assertIn(category, TABLE)

    def test_unknown_category_is_never_guessed(self):
        routed, unknown = route_all([{"id": "T001", "category": "shipping", "priority": "P2"}], TABLE)
        self.assertEqual((routed, unknown), ([], ["T001"]))

    def test_p1_is_marked_urgent(self):
        routed, _ = route_all([{"id": "T001", "category": "billing", "priority": "P1"}], TABLE)
        self.assertTrue(routed[0]["urgent"])
        self.assertEqual(routed[0]["team"], "Billing Team")


class TestReplyChecks(unittest.TestCase):
    def setUp(self):
        self.item = copy.deepcopy(reply_items()[0])

    def test_recorded_drafts_all_pass(self):
        for item in reply_items():
            self.assertEqual(check_reply.problems(item, CFG), [], item["id"])

    def test_wrong_language_is_caught(self):
        french = next(i for i in reply_items() if i["language"] == "FR")
        broken = {**self.item, "draft": french["draft"]}
        self.assertTrue(any("language" in p for p in check_reply.problems(broken, CFG)))

    def test_banned_promise_is_caught(self):
        self.item["draft"] = "Hello, thank you for contacting us. We promise a refund within 24 hours. Kind regards, Customer Care Team"
        found = " ".join(check_reply.problems(self.item, CFG))
        self.assertIn("banned promise phrase", found)

    def test_internal_team_name_is_caught(self):
        self.item["draft"] = "Hello, thank you for contacting us. Our Billing Team will answer you. Kind regards, Customer Care Team"
        self.assertIn("internal words", " ".join(check_reply.problems(self.item, CFG)))

    def test_sentence_count_limits(self):
        self.item["draft"] = "Hello. Thank you."
        self.assertTrue(any("sentences" in p for p in check_reply.problems(self.item, CFG)))

    def test_draft_must_wait_for_approval(self):
        self.item["status"] = "approved"
        self.assertTrue(any("waiting_for_approval" in p for p in check_reply.problems(self.item, CFG)))


class TestAudit(unittest.TestCase):
    def test_recorded_run_passes_20_of_20(self):
        result = audit_sample.audit(reply_items(), CFG, TABLE)
        self.assertEqual((result["verdict"], result["passed_count"], result["sample_size"]), ("PASS", 20, 20))

    def test_wrong_team_makes_the_audit_fail_and_names_the_stage(self):
        items = copy.deepcopy(reply_items())
        sampled = audit_sample.audit(items, CFG, TABLE)["sampled_ids"]
        target = next(i for i in items if i["id"] == sampled[0])
        target["team"] = "Technical Support" if target["team"] != "Technical Support" else "Billing Team"
        result = audit_sample.audit(items, CFG, TABLE)
        self.assertEqual(result["verdict"], "FAIL")
        failing = next(r for r in result["results"] if not r["passed"])
        self.assertIn(4, failing["failed_checks"])
        self.assertEqual(audit_sample.STAGE_FOR_CHECK[4], "03_route")

    def test_sample_is_reproducible(self):
        ids = [i["id"] for i in reply_items()]
        self.assertEqual(seeded_sample(ids, 20, 42), seeded_sample(list(reversed(ids)), 20, 42))
        self.assertEqual(len(set(seeded_sample(ids, 20, 42))), 20)

    def test_random_generator_is_stable(self):
        # Reference values from the JavaScript version used by the website, so both pick the same sample.
        rnd = mulberry32(42)
        self.assertEqual([round(rnd(), 6) for _ in range(3)], [0.601104, 0.448291, 0.852466])


if __name__ == "__main__":
    unittest.main()


class TestJavaScriptParity(unittest.TestCase):
    """The website runs a JavaScript copy of the scripts. It must give the same answers as Python."""

    def test_js_matches_python(self):
        import json
        import shutil
        import subprocess

        node = shutil.which("node")
        if node is None:
            self.skipTest("node is not installed")
        out = subprocess.run([node, str(ROOT / "tests" / "js_parity.js")], capture_output=True, text=True, check=True)
        js = json.loads(out.stdout)
        items = reply_items()
        self.assertEqual(js["languages"], [i["language"] for i in items])
        self.assertEqual(js["teams"], [i["team"] for i in items])
        py_audit = audit_sample.audit(items, CFG, TABLE)
        self.assertEqual(js["sampled"], py_audit["sampled_ids"])
        self.assertEqual((js["verdict"], js["passed"]), (py_audit["verdict"], py_audit["passed_count"]))
        self.assertEqual(js["reply_problem_count"], 0)
        _, rejected = validate_all(load_json(ROOT / "tests" / "bad_tickets.json"))
        self.assertEqual([r for r in js["bad_ticket_reasons"] if r], [r["reason"] for r in rejected])
        self.assertEqual(js["random"], [0.601104, 0.448291, 0.852466])

"""Structural fixtures, not autonomous/native/user-acceptance behavior evidence."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/projectframe/scripts"
sys.path.insert(0, str(SCRIPTS))
import projectframe as pf
import codex_hook as hook


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="projectframe-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.store = pf.Store(self.root)
        self.state = self.store.create("task-a", "session-a", "Structural fixture only", now=0)
        self.spec = self.root / ".specframe/task.json"
        self.spec.parent.mkdir()
        self.source = {"format": 1, "owner": "spec-session", "approval": "approved", "pending": [], "sections": {"R1": "Preserve this material condition", "R2": "Validate actual effects"}, "focus": []}
        self.write_spec()
        self.synstate = self.root / ".synframe/fixture"
        self.synstate.mkdir(parents=True)
        self.selected = {"candidate": {"id": "candidate", "revision": 1}, "assets": [{"id": "maker", "revision": 1, "kind": "skill"}], "goal": {"id": "fixture-goal", "revision": 1, "source_request": "\n".join(self.source["sections"].values())}}
        self.binding = {"helper": str(self.root / "synframe.py"), "state": str(self.synstate), "run": "fixture-run", "identity": {"fixture": True}, "candidate_ref": {"id": "candidate", "revision": 1}, "review_ref": {"id": "review", "revision": 1}}
        self.mock_syn = patch.object(pf, "synframe", return_value=(self.binding, self.selected))
        self.mock_syn.start()
        self.addCleanup(self.mock_syn.stop)
        self.evidence = self.root / "fixture-evidence.txt"
        self.evidence.write_text("Structural test data only, not actual user/host evidence")
        self.art = pf.receipt(self.evidence, "structural fixture")

    def write_spec(self):
        self.spec.write_text(json.dumps(self.source))

    def act(self, kind, now=10, **fields):
        self.state = self.store.apply("task-a", "session-a", self.state["revision"], {"kind": kind, **fields}, now=now)
        return self.state

    def prepared(self):
        self.act("spec", path=str(self.spec))
        self.act("selection", **{k: self.binding[k] for k in ("helper", "state", "run")})
        items = []
        for name in ("specframe", "synframe", "planning-with-files", "maker"):
            folder = self.root / "fixture-skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("---\nname: " + name + "\ndescription: Structural fixture\n---\n")
            item = {"name": name, "path": str(folder), "origin": "fixture://local", "revision": "fixture", "checked_at": "fixture observation time", "change_handling": "fixture-only unchanged tree", "usability": "not a real skill trial", "manifest": pf.manifest(folder), "source_receipt": self.art, "usability_receipt": self.art}
            if name == "maker":
                item["asset_ref"] = {"id": "maker", "revision": 1}
            items.append(item)
        self.act("skills", items=items)
        self.act("handoff-prepare")

    def implementation(self):
        self.prepared()
        self.act("handoff-observed", stage="DELIVERED", evidence=[self.art], rationale="fixture delivery")
        self.act("handoff-observed", stage="RECEIVED", evidence=[self.art], rationale="fixture receipt")
        self.act("implementation", plan_id="task-a")

    def applied(self):
        self.implementation()
        self.act("handoff-observed", stage="APPLIED", evidence=[self.art], rationale="fixture application")

    def verification(self):
        return {"checks": {key: {"status": "PASS", "rationale": "Explicit structural fixture assessment only", "evidence": [self.art]} for key in self.source["sections"]}, "artifacts": [self.art], "scope": "Structural fixture; not real user acceptance or autonomous meaning"}

    def test_new_task_enters_spec_and_never_overwrites(self):
        self.assertEqual(self.state["phase"], "SPEC")
        with self.assertRaises(pf.Conflict):
            self.store.create("task-a", "other", "new request")
        self.assertEqual(self.store.read("task-a")["request"], "Structural fixture only")

    def test_handoff_preserves_missing_records_as_unknown(self):
        self.implementation()
        progress = self.root / ".planning/task-a/progress.md"
        progress.write_text("Actual retained record")
        bundle = self.store.bundle(self.state)
        self.assertIsNone(bundle["records"]["task_plan.md"])
        self.assertIsNone(bundle["records"]["findings.md"])
        self.assertEqual(bundle["records"]["progress.md"], "Actual retained record")
        self.assertEqual(bundle["approved_sections"], self.source["sections"])
        self.assertFalse((progress.parent / "findings.md").exists())

    def test_explicit_code_upgrade_binds_comparison_and_preserves_effects(self):
        old = self.root / "previous-helper.py"
        old.write_bytes(Path(pf.__file__).read_bytes())
        previous = pf.receipt(old, "Preserved original helper")
        assessment = self.root / "comparison.json"
        body = {"project": str(self.root), "task": "task-a", "revision": self.state["revision"], "format": 1, "previous_implementation": self.state["implementation"], "implementation": "c" * 64, "scope": "Fixture explicit same-schema comparison", "effect_check": "No external effects in this fixture"}
        original_hash = pf.file_hash
        with patch.object(pf, "file_hash", side_effect=lambda path: "c" * 64 if Path(path) == Path(pf.__file__) else original_hash(path)):
            with self.assertRaises(pf.Conflict):
                self.act("notice", text="new notice", source="fixture")
            body["task"] = "other"
            assessment.write_text(json.dumps(body))
            with self.assertRaises(pf.Conflict):
                self.act("upgrade", previous_helper=previous, assessment=pf.receipt(assessment, "Wrong-task comparison"))
            self.assertEqual(self.store.read("task-a")["revision"], 1)
            body["task"] = "task-a"
            assessment.write_text(json.dumps(body))
            self.act("upgrade", previous_helper=previous, assessment=pf.receipt(assessment, "Explicit exact comparison"))
            self.assertEqual(self.state["implementation"], "c" * 64)
            self.assertEqual(self.state["phase"], "SPEC")
            self.assertEqual(self.state["operations"], {})
        db = self.store.connect()
        try:
            historical = json.loads(db.execute("SELECT body FROM snapshots WHERE task=? AND revision=1", ("task-a",)).fetchone()[0])
            self.assertEqual(historical["implementation"], previous["sha256"])
        finally:
            db.close()

    def test_native_end_timeouts_respect_current_host_maximum(self):
        config = hook.config(self.root / "registry")
        for event in ("Interrupt", "SessionEnd"):
            self.assertEqual(config["hooks"][event][0]["hooks"][0]["timeout"], 3)

    def test_owner_and_stale_revision_rejected_atomically(self):
        for owner, rev in (("other", 1), ("session-a", 0)):
            with self.assertRaises(pf.Conflict):
                self.store.apply("task-a", owner, rev, {"kind": "notice", "text": "fixture", "source": "fixture"})
        self.assertEqual(self.store.read("task-a")["revision"], 1)

    def test_two_actual_writers_cannot_both_apply_the_same_revision(self):
        barrier = threading.Barrier(2)
        outcomes = []

        def writer(label):
            barrier.wait()
            try:
                self.store.apply("task-a", "session-a", 1, {"kind": "notice", "text": label, "source": "CONCURRENT STRUCTURAL FIXTURE"})
                outcomes.append("applied")
            except (pf.Conflict, pf.sqlite3.OperationalError):
                outcomes.append("rejected")

        workers = [threading.Thread(target=writer, args=(label,)) for label in ("first", "second")]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=3)
            self.assertFalse(worker.is_alive())
        self.assertCountEqual(outcomes, ["applied", "rejected"])
        self.assertEqual(self.store.read("task-a")["revision"], 2)

    def test_changed_helper_identity_refuses_restoration_writes(self):
        actual_hash = pf.file_hash
        with patch.object(pf, "file_hash", side_effect=lambda path: "changed-helper" if str(path) == pf.__file__ else actual_hash(path)):
            with self.assertRaises(pf.Conflict):
                self.act("notice", text="fixture", source="fixture")
        self.assertEqual(self.store.read("task-a")["revision"], 1)

    def test_damaged_store_does_not_fabricate_recovered_state(self):
        self.store.database.write_bytes(b"damaged structural fixture")
        with self.assertRaises(pf.sqlite3.DatabaseError):
            self.store.read("task-a")

    def test_unapproved_or_pending_spec_refused(self):
        for approval, pending in (("unapproved", []), ("approved", ["R1"])):
            self.source.update(approval=approval, pending=pending)
            self.write_spec()
            with self.assertRaises(pf.Conflict):
                self.act("spec", path=str(self.spec))
        self.assertIsNone(self.store.read("task-a")["spec"])

    def test_foreign_project_spec_and_selection_refused(self):
        with tempfile.TemporaryDirectory() as other:
            path = Path(other) / "spec.json"
            path.write_text(json.dumps(self.source))
            with self.assertRaises(pf.Conflict):
                self.act("spec", path=str(path))
            self.act("spec", path=str(self.spec))
            with self.assertRaises(pf.Conflict):
                self.act("selection", helper="fixture", state=other, run="foreign")

    def test_focus_reuse_but_changed_body_blocks_dependent_work(self):
        self.prepared()
        self.source["focus"] = ["R1"]
        self.write_spec()
        self.store.bundle(self.state)
        self.source["sections"]["R1"] = "changed material condition"
        self.write_spec()
        with self.assertRaises(pf.Conflict):
            self.store.bundle(self.state)
        self.act("spec", path=str(self.spec), change_source="fixture explicit approved change")
        self.assertIsNone(self.state["selection"])
        self.assertIsNone(self.state["handoff"])

    def test_changed_selection_can_be_relinked_only_with_reassessment(self):
        self.prepared()
        changed = dict(self.binding, candidate_ref={"id": "candidate", "revision": 2})
        with patch.object(pf, "synframe", return_value=(changed, self.selected)):
            with self.assertRaises(pf.Conflict):
                self.store.bundle(self.state)
            with self.assertRaises(pf.Conflict):
                self.act("selection", **{k: changed[k] for k in ("helper", "state", "run")})
            self.act("selection", change_source="fixture actual reassessment", **{k: changed[k] for k in ("helper", "state", "run")})
        self.assertEqual(self.state["selection"]["candidate_ref"]["revision"], 2)

    def test_valid_gate_for_an_unrelated_goal_is_not_this_baseline(self):
        self.act("spec", path=str(self.spec))
        unrelated = {**self.selected, "goal": {"id": "unrelated", "revision": 1, "source_request": "a different request"}}
        with patch.object(pf, "synframe", return_value=(self.binding, unrelated)):
            with self.assertRaises(pf.Conflict):
                self.act("selection", **{k: self.binding[k] for k in ("helper", "state", "run")})
        self.assertIsNone(self.store.read("task-a")["selection"])

    def test_referenced_source_uses_explicit_current_host_comparison(self):
        self.act("spec", path=str(self.spec))
        referenced = {**self.selected, "goal": {"id": "fixture-goal", "revision": 1, "source_request": "Referenced original fixture specification"}}
        path = self.root / "source-comparison.json"
        value = {"spec_ref": self.state["spec"], "goal_ref": {"id": "fixture-goal", "revision": 1}, "goal_source_digest": pf.digest(referenced["goal"]["source_request"]), "scope": "Structural fixture for referenced original sources", "rationale": "Not an autonomous semantic comparison"}
        path.write_text(json.dumps(value))
        observed = pf.receipt(path, "explicit structural comparison fixture")
        with patch.object(pf, "synframe", return_value=(self.binding, referenced)):
            self.act("selection", source_assessment=observed, **{k: self.binding[k] for k in ("helper", "state", "run")})
            self.store.current(self.state)
            path.write_text("changed comparison")
            with self.assertRaises(pf.Conflict):
                self.store.current(self.state)

    def test_selected_skill_tree_change_blocks_handoff(self):
        self.prepared()
        folder = Path(self.state["skills"][-1]["path"])
        (folder / "SKILL.md").write_text("unreviewed local edit")
        with self.assertRaises(pf.Conflict):
            self.store.bundle(self.state)

    def test_preparation_does_not_mean_receipt_or_application(self):
        self.prepared()
        self.assertEqual(self.state["handoff"]["stage"], "PREPARED")
        self.assertEqual(self.store.bundle(self.state)["approved_sections"], self.source["sections"])
        with self.assertRaises(pf.Conflict):
            self.act("handoff-observed", stage="APPLIED", evidence=[self.art], rationale="skip")
        with self.assertRaises(pf.Conflict):
            self.act("implementation", plan_id="task-a")

    def test_planning_starts_only_in_implementation(self):
        with self.assertRaises(pf.Conflict):
            self.act("record-intent", id="p", file="task_plan.md", previous_sha256=None, contents="too early")
        self.implementation()
        self.act("record-intent", id="p", file="task_plan.md", previous_sha256=None, contents="actual derivative record")
        self.act("record-apply", id="p")
        self.assertEqual((self.root / ".planning/task-a/task_plan.md").read_text(), "actual derivative record")
        self.assertEqual(self.state["operations"]["p"]["assessment"]["status"], "RECORDED")

    def test_plan_file_conflict_and_other_plan_preserved(self):
        self.implementation()
        path = self.root / ".planning/task-a/progress.md"
        path.write_text("baseline")
        other = self.root / ".planning/task-b"
        other.mkdir()
        (other / "progress.md").write_text("other task")
        self.act("record-intent", id="p", file="progress.md", previous_sha256=pf.file_hash(path), contents="new record")
        path.write_text("another writer")
        with self.assertRaises(pf.Conflict):
            self.act("record-apply", id="p")
        self.assertEqual(path.read_text(), "another writer")
        self.assertEqual((other / "progress.md").read_text(), "other task")

    def test_crash_after_file_write_reuses_effect_without_rewrite(self):
        self.implementation()
        self.act("record-intent", id="p", file="progress.md", previous_sha256=None, contents="preserved actual effect")
        original = pf.Store.save
        with patch.object(pf.Store, "save", side_effect=OSError("simulated commit failure after file replace")):
            with self.assertRaises(OSError):
                self.act("record-apply", id="p")
        self.state = self.store.read("task-a")
        self.assertEqual(self.state["operations"]["p"]["stage"], "INTENT")
        self.assertEqual((self.root / ".planning/task-a/progress.md").read_text(), "preserved actual effect")
        with patch.object(pf.os, "replace", side_effect=AssertionError("must reuse actual effect")):
            self.act("record-apply", id="p")
        self.assertEqual(self.state["operations"]["p"]["stage"], "APPLIED")
        self.assertIs(pf.Store.save, original)

    def test_record_history_and_handoff_preserve_original_crlf_bytes(self):
        self.implementation()
        path = self.root / ".planning/task-a/progress.md"
        original = b"First line\r\nSecond line\r\n"
        path.write_bytes(original)
        self.act("record-intent", id="crlf", file="progress.md", previous_sha256=pf.file_hash(path), contents="Changed\r\n")
        intent = self.state["operations"]["crlf"]["intent"]
        self.assertEqual(intent["previous_contents"].encode(), original)
        self.assertEqual(pf.hashlib.sha256(intent["previous_contents"].encode()).hexdigest(), intent["previous_sha256"])
        self.assertEqual(self.store.bundle(self.state)["records"]["progress.md"].encode(), original)
        self.act("record-apply", id="crlf")
        self.assertEqual(path.read_bytes(), b"Changed\r\n")

    def test_existing_plan_records_survive_return_to_source_review(self):
        self.implementation()
        self.source["sections"]["R1"] = "Changed approved condition"
        self.write_spec()
        self.act("spec", path=str(self.spec), change_source="Fixture actual changed approval")
        self.act("record-intent", id="changed-baseline", file="progress.md", previous_sha256=None, contents="Record actual baseline change; selection review pending")
        self.act("record-apply", id="changed-baseline")
        self.assertEqual(self.state["phase"], "SYN")
        self.assertIsNone(self.state["selection"])
        self.assertEqual((self.root / ".planning/task-a/progress.md").read_text(), "Record actual baseline change; selection review pending")

    def test_cancelled_existing_plan_allows_factual_records_not_new_product_work(self):
        self.implementation()
        self.act("control", activity="CANCELLED", reason_source="Fixture actual cancellation", next="Inspect actual effects")
        self.act("record-intent", id="cleanup-note", file="progress.md", previous_sha256=None, contents="Actual cancellation and cleanup observation")
        self.act("record-apply", id="cleanup-note")
        self.assertEqual(self.state["activity"], "CANCELLED")
        with self.assertRaises(pf.Conflict):
            self.act("intent", id="new-work", effect="implementation", target="product", scope="new work", recovery_check="inspect")
        with self.assertRaises(pf.Conflict):
            self.act("control", activity="RUNNING", reason_source="not an authorized undo", effect_check="fixture", next="resume")

    def test_plan_symlink_escape_rejected(self):
        self.implementation()
        path = self.root / ".planning/task-a/progress.md"
        path.symlink_to(self.evidence)
        with self.assertRaises(pf.Conflict):
            self.act("record-intent", id="p", file="progress.md", previous_sha256=None, contents="overwrite")
        self.assertIn("Structural test", self.evidence.read_text())

    def test_intent_and_observation_are_not_applied(self):
        self.applied()
        self.act("intent", id="work", effect="implementation", target="fixture output", scope="fixture", recovery_check="inspect actual file and live actor")
        with self.assertRaises(pf.Conflict):
            self.act("resolve", id="work", assessment="SUCCEEDED", rationale="no observation", remaining_work=[], next="fixture")
        self.act("observation", id="work", facts="fixture actual bytes", artifacts=[self.art])
        self.assertEqual(self.state["operations"]["work"]["stage"], "OBSERVED")
        self.act("resolve", id="work", assessment="UNKNOWN", rationale="effect not yet established", remaining_work=["inspect actor"], next="inspect actor")
        partial = self.verification()
        partial["checks"]["R2"]["status"] = "UNKNOWN"
        self.act("verify", **partial)
        self.assertEqual(self.state["verification"]["checks"]["R2"]["status"], "UNKNOWN")
        with self.assertRaises(pf.Conflict):
            self.act("verify", **self.verification())
        self.act("resolve", id="work", assessment="SUCCEEDED", rationale="fixture effect inspected", remaining_work=[], next="verify fixture")
        self.act("verify", **self.verification())

    def test_cancelled_task_preserves_cleanup_but_blocks_new_work(self):
        self.act("intent", id="outside", effect="installation", target="fixture", scope="fixture", recovery_check="inspect actual effect")
        self.act("control", activity="CANCELLED", reason_source="fixture explicit cancellation", next="inspect pending effects")
        for event in ({"kind": "intent", "id": "new", "effect": "installation", "target": "x", "scope": "x", "recovery_check": "x"}, {"kind": "spec", "path": str(self.spec)}):
            with self.assertRaises(pf.Conflict):
                self.store.apply("task-a", "session-a", self.state["revision"], event)
        self.act("observation", id="outside", facts="fixture late actual result", artifacts=[self.art])
        self.act("resolve", id="outside", assessment="NOT_EXECUTED", rationale="fixture inspected before retry", remaining_work=[], next="remain cancelled")
        self.assertEqual(self.state["activity"], "CANCELLED")

    def test_takeover_needs_stopped_actor_and_keeps_suspended(self):
        event = {"kind": "takeover", "previous_owner": "session-a", "previous_actor_status": "RUNNING", "effect_check": "fixture", "evidence": [self.art]}
        with self.assertRaises(pf.Conflict):
            self.store.apply("task-a", "session-b", self.state["revision"], event)
        event["previous_actor_status"] = "STOPPED"
        state = self.store.apply("task-a", "session-b", self.state["revision"], event)
        self.assertEqual((state["owner"], state["activity"]), ("session-b", "SUSPENDED"))

    def test_verification_and_final_user_acceptance_are_separate(self):
        self.applied()
        with self.assertRaises(pf.Conflict):
            self.act("accept", user_source="fixture", user_text="fixture yes", verification_revision=self.state["revision"])
        incomplete = self.verification()
        del incomplete["checks"]["R2"]
        with self.assertRaises(pf.Conflict):
            self.act("verify", **incomplete)
        self.act("verify", **self.verification())
        self.assertEqual((self.state["phase"], self.state["activity"]), ("AWAIT_ACCEPTANCE", "WAITING_USER"))
        self.act("accept", user_source="STRUCTURAL FIXTURE ONLY", user_text="fixture final acceptance", verification_revision=self.state["revision"])
        self.assertEqual(self.state["phase"], "COMPLETE")
        with self.assertRaises(pf.Conflict):
            self.act("control", activity="RUNNING", reason_source="fixture", effect_check="fixture", next="cannot reopen accepted task")

    def test_actual_failed_or_unknown_check_cannot_complete(self):
        self.applied()
        verification = self.verification()
        verification["checks"]["R2"]["status"] = "FAIL"
        self.act("verify", **verification)
        self.assertEqual(self.state["phase"], "VERIFY")
        with self.assertRaises(pf.Conflict):
            self.act("accept", user_source="fixture", user_text="fixture", verification_revision=self.state["revision"])
        self.act("implementation", plan_id="task-a")
        self.assertEqual(self.state["phase"], "IMPLEMENT")
        with self.assertRaises(pf.Conflict):
            self.act("implementation", plan_id="different-plan")

    def test_two_tasks_cannot_own_one_shared_plan(self):
        self.implementation()
        self.store.create("task-b", "session-b", "Second structural fixture")
        with self.assertRaises(pf.Conflict):
            self.store.check_plan_owner("task-b", "task-a")

    def test_changed_result_after_verification_rejects_acceptance(self):
        self.applied()
        self.act("verify", **self.verification())
        self.evidence.write_text("changed after validation")
        with self.assertRaises(pf.Conflict):
            self.act("accept", user_source="fixture", user_text="fixture yes", verification_revision=self.state["revision"])
        self.assertEqual(self.store.read("task-a")["phase"], "AWAIT_ACCEPTANCE")

    def test_new_work_invalidates_verification_and_requires_fresh_acceptance(self):
        self.applied()
        self.act("verify", **self.verification())
        self.act("control", activity="RUNNING", reason_source="Fixture user requests more work", effect_check="Actual prior effects checked", next="Do requested follow-up")
        self.act("intent", id="followup", effect="verification", target="fixture", scope="new audit", recovery_check="inspect")
        self.assertIsNone(self.state["verification"])
        self.assertEqual(self.state["phase"], "VERIFY")
        with self.assertRaises(pf.Conflict):
            self.act("accept", user_source="fixture", user_text="fixture yes", verification_revision=self.state["revision"])
        self.act("observation", id="followup", facts="Actual fixture result", artifacts=[self.art])
        self.act("resolve", id="followup", assessment="SUCCEEDED", rationale="Observed fixture effect", remaining_work=[], next="Revalidate")
        self.act("verify", **self.verification())
        self.act("accept", user_source="fixture", user_text="new current result accepted", verification_revision=self.state["revision"])
        self.assertEqual(self.state["phase"], "COMPLETE")

    def test_record_after_verification_invalidates_acceptance_eligibility(self):
        self.applied()
        self.act("verify", **self.verification())
        self.act("record-intent", id="later-record", file="progress.md", previous_sha256=None, contents="Changed current outcome")
        self.assertIsNone(self.state["verification"])
        with self.assertRaises(pf.Conflict):
            self.act("accept", user_source="fixture", user_text="fixture yes", verification_revision=self.state["revision"])
        self.act("record-apply", id="later-record")
        self.assertEqual(self.state["activity"], "WAITING_USER")
        with self.assertRaises(pf.Conflict):
            self.act("verify", **self.verification())

    def test_reprepared_handoff_blocks_implementation_until_current_receipt(self):
        self.applied()
        self.act("handoff-prepare")
        self.assertEqual((self.state["phase"], self.state["handoff"]["stage"]), ("HANDOFF", "PREPARED"))
        with self.assertRaises(pf.Conflict):
            self.act("intent", id="premature", effect="implementation", target="fixture", scope="fixture", recovery_check="inspect")
        self.act("handoff-observed", stage="DELIVERED", evidence=[self.art], rationale="Current fixture delivery")
        self.act("handoff-observed", stage="RECEIVED", evidence=[self.art], rationale="Current fixture receipt")
        self.act("implementation", plan_id="task-a")
        self.act("intent", id="received-work", effect="implementation", target="fixture", scope="fixture", recovery_check="inspect")
        self.assertEqual(self.state["operations"]["received-work"]["stage"], "INTENT")

    def test_public_completion_blocks_remaining_and_accepts_fresh_reconciliation(self):
        self.applied()
        self.act("intent", id="work", effect="verification", target="fixture", scope="fixture", recovery_check="inspect actual effects")
        self.act("observation", id="work", facts="Known fixture failure", artifacts=[self.art])
        self.act("resolve", id="work", assessment="FAILED", rationale="Known failure, follow-up required", remaining_work=["Repair and inspect"], next="Repair")
        previous = pf.copy.deepcopy(self.state["operations"]["work"])
        with self.assertRaises(pf.Conflict):
            self.act("verify", **self.verification())
        with self.assertRaises(pf.Conflict):
            self.act("resolve", id="work", assessment="FAILED", rationale="No fresh observation", remaining_work=[], next="Verify")
        self.act("intent", id="repair", effect="implementation", target="fixture", scope="Separate repair", recovery_check="Inspect repair")
        self.act("observation", id="repair", facts="Actual repair verified", artifacts=[self.art])
        self.act("resolve", id="repair", assessment="SUCCEEDED", rationale="Repair observed", remaining_work=[], next="Reconcile original obligation")
        with self.assertRaises(pf.Conflict):
            self.act("verify", **self.verification())
        self.act("observation", id="work", facts="Fresh follow-up effect inspection; historical failure retained", artifacts=[self.art])
        self.act("resolve", id="work", assessment="FAILED", rationale="Original attempt failed; subsequent repair satisfies its remaining obligation", remaining_work=[], next="Verify")
        self.assertEqual(self.state["operations"]["work"]["assessment"]["status"], "FAILED")
        self.assertEqual(len(self.state["operations"]["work"]["observations"]), 2)
        self.assertEqual(previous["assessment"]["remaining_work"], ["Repair and inspect"])
        with self.assertRaises(pf.Conflict):
            self.act("observation", id="work", facts="Closed effect cannot reopen", artifacts=[self.art])
        self.act("verify", **self.verification())
        self.act("accept", user_source="structural fixture only", user_text="fixture acceptance", verification_revision=self.state["revision"])
        self.assertEqual(self.state["phase"], "COMPLETE")

    def test_due_requires_running_time_and_actual_notice_record(self):
        self.assertFalse(pf.notice_due(self.state, now=299))
        self.assertTrue(pf.notice_due(self.state, now=300))
        self.act("notice", now=300, text="fixture delivered notice", source="STRUCTURAL FIXTURE")
        self.assertFalse(pf.notice_due(self.state, now=599))
        self.assertTrue(pf.notice_due(self.state, now=600))
        self.act("control", now=600, activity="WAITING_USER", reason_source="fixture", next="wait")
        self.assertFalse(pf.notice_due(self.state, now=1000))

    def test_hook_scope_hash_and_binding_boundaries(self):
        registry = self.root / "registry"
        hook.bind(registry, self.root, "task-a", "session-a")
        with self.assertRaises(pf.Conflict):
            hook.bind(registry, self.root, "task-b", "session-a")
        sha = pf.file_hash(hook.__file__)
        helper_sha = pf.file_hash(pf.__file__)
        event = {"session_id": "session-a", "cwd": str(self.root), "hook_event_name": "SessionStart", "source": "compact"}
        result = hook.emit(registry, event, sha, helper_sha)
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("task-a", context)
        self.assertIn("Intent/receipt is not execution", context)
        with self.assertRaises(pf.Conflict):
            hook.emit(registry, event, "changed", helper_sha)
        event["cwd"] = str(self.root.parent)
        self.assertEqual(hook.emit(registry, event, sha, helper_sha), {})

    def test_native_interrupt_fixture_does_not_resolve_external_effect(self):
        self.act("intent", id="external", effect="installation", target="fixture", scope="fixture", recovery_check="inspect actual effect")
        registry = self.root / "registry"
        hook.bind(registry, self.root, "task-a", "session-a")
        hook.emit(registry, {"session_id": "session-a", "cwd": str(self.root), "hook_event_name": "Interrupt"}, pf.file_hash(hook.__file__), pf.file_hash(pf.__file__))
        state = self.store.read("task-a")
        self.assertEqual(state["activity"], "SUSPENDED")
        self.assertEqual(state["operations"]["external"]["stage"], "INTENT")

    def test_binding_rejects_linked_and_nonregular_entries_before_success(self):
        registry = self.root / "registry"
        registry.mkdir()
        target = self.root / "retained-binding.json"
        original = pf.canonical({"project": str(self.root), "task": "task-a", "session": "session-a"})
        target.write_text(original)
        path = registry / "session-a.json"
        path.symlink_to(target)
        with self.assertRaises(pf.Conflict):
            hook.bind(registry, self.root, "task-a", "session-a")
        self.assertEqual(target.read_text(), original)
        path.unlink()
        path.mkdir()
        with self.assertRaises(pf.Conflict):
            hook.bind(registry, self.root, "task-a", "session-a")

    def test_synframe_handoff_carries_review_only_conditions_and_pending_context(self):
        self.mock_syn.stop()
        helper = self.root / "synframe.py"
        helper.write_text("Fixture protocol only")
        context = {
            "compatible": True, "identity": {"fixture": True},
            "return_boundary": {"committed_candidate_ref": {"id": "candidate", "revision": 1}, "committed_review_ref": {"id": "review", "revision": 1}},
            "run_ref": {"id": "fixture-run", "revision": 7}, "state": "ACTIVE", "revision": 7, "state_digest": "fixture-digest",
            "requirements_context": {"learning_tasks": []}, "selected_tasks": [],
            "unfinished_learning": [{"id": "still-open"}], "pending_operations": [{"id": "actual-pending"}],
            "unapplied_observation_count": 1, "propagation_obligations": [{"id": "not-consumed"}],
            "unresolved_items": ["Unresolved fixture condition"],
        }
        documents = {
            "candidate": {"id": "candidate", "revision": 1, "goal_ref": {"id": "goal", "revision": 1}, "asset_refs": [{"id": "maker", "revision": 1}]},
            "review": {"id": "review", "revision": 1, "extensions": {"execution_obligations": ["Material condition present only in Review"]}},
            "goal": {"id": "goal", "revision": 1, "source_request": "Fixture request"},
            "maker": {"id": "maker", "revision": 1, "kind": "skill"},
        }

        def query(argv, **options):
            command = argv[4]
            value = context if command == "work-context" else {"passed": True} if command == "gate" else documents[argv[argv.index("--id")+1]]
            return pf.subprocess.CompletedProcess(argv, 0, json.dumps(value), "")

        with patch.object(pf.subprocess, "run", side_effect=query):
            binding, selected = pf.synframe({"helper": str(helper), "state": str(self.synstate), "run": "fixture-run"})
        self.assertEqual(binding["review_ref"], {"id": "review", "revision": 1})
        self.assertEqual(selected["review"], documents["review"])
        for field in ("pending_operations", "unfinished_learning", "unresolved_items", "propagation_obligations", "unapplied_observation_count"):
            self.assertEqual(selected["execution_context"][field], context[field])


if __name__ == "__main__":
    unittest.main()

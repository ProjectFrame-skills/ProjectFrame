#!/usr/bin/env python3
"""Local coordination boundaries. The host owns meaning, authority and actual work."""
import argparse
from contextlib import closing
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time


FORMAT = 1
PLAN_FILES = {"task_plan.md", "findings.md", "progress.md"}
ACTIVITIES = {"RUNNING", "WAITING_USER", "WAITING_PERMISSION", "BLOCKED", "SUSPENDED", "CANCELLED"}


class Conflict(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Conflict(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        result = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


def slug(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9._-]*", value), "invalid task/session identifier")
    return value


def text(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} must be nonempty text")
    return value


def receipt(path, source):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), "artifact must be a readable regular file")
    return {"path": str(path), "sha256": file_hash(path), "source": text(source, "source")}


def check_receipt(item):
    require(isinstance(item, dict) and set(item) == {"path", "sha256", "source"}, "receipt needs exact path/sha256/source")
    require(receipt(item["path"], item["source"]) == item, "artifact changed or receipt path is not canonical")


def manifest(folder):
    root = Path(folder).resolve(strict=True)
    require((root / "SKILL.md").is_file(), "skill entrypoint missing")
    result = {}
    for path in sorted(root.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        require(not path.is_symlink(), "skill manifest refuses symlink entries")
        if path.is_file():
            result[str(path.relative_to(root))] = file_hash(path)
    return result


def spec_source(path):
    path = Path(path).resolve(strict=True)
    value = json.loads(path.read_text(encoding="utf-8"))
    require(value.get("format") == 1 and isinstance(value.get("sections"), dict), "unsupported SpecFrame state")
    require(value.get("approval") == "approved" and value.get("pending") == [], "current full SpecFrame approval required")
    require(value.get("owner") and value["sections"], "SpecFrame owner/sections missing")
    for key, body in value["sections"].items():
        text(key, "section ID")
        text(body, "section body")
    return {"path": str(path), "owner": value["owner"], "digest": digest({"sections": value["sections"], "approval": value["approval"]})}, value


def synframe(source):
    helper = Path(source["helper"]).resolve(strict=True)
    state = Path(source["state"]).resolve(strict=True)

    def call(command, *extra):
        result = subprocess.run([sys.executable, str(helper), "--state", str(state), command, "--run", source["run"], *extra], capture_output=True, text=True, timeout=30)
        require(result.returncode == 0, "SynFrame query rejected: " + result.stderr + result.stdout)
        return json.loads(result.stdout)

    context = call("work-context")
    boundary = context["return_boundary"]
    require(context.get("compatible") and context["state"] in {"ACTIVE", "COMPLETED"}, "SynFrame execution is not usable/current")
    candidate, review = boundary["committed_candidate_ref"], boundary["committed_review_ref"]
    require(candidate and review, "actual stored SynFrame adoption required")
    encode = lambda ref: f"{ref['id']}@{ref['revision']}"
    gate = call("gate", "--candidate", encode(candidate), "--review", encode(review))
    require(gate.get("passed") is True, "current SynFrame Commit gate failed")
    selected = call("get", "--id", candidate["id"], "--revision", str(candidate["revision"]))
    review_record = call("get", "--id", review["id"], "--revision", str(review["revision"]))
    goal_ref = selected["goal_ref"]
    goal = call("get", "--id", goal_ref["id"], "--revision", str(goal_ref["revision"]))
    assets = [call("get", "--id", ref["id"], "--revision", str(ref["revision"])) for ref in selected["asset_refs"]]
    binding = {"helper": str(helper), "state": str(state), "run": source["run"], "identity": context["identity"], "candidate_ref": candidate, "review_ref": review}
    execution = {key: context[key] for key in ("run_ref", "state", "revision", "state_digest", "selected_tasks", "unfinished_learning", "pending_operations", "unapplied_observation_count", "propagation_obligations", "unresolved_items")}
    return binding, {"candidate": selected, "review": review_record, "assets": assets, "goal": goal, "requirements_context": context["requirements_context"], "execution_context": execution}


def check_source_binding(spec_ref, raw, selected, assessment=None):
    goal = selected["goal"]
    if all(body in goal["source_request"] for body in raw["sections"].values()):
        return
    # Valid source references/representations need an explicit scoped host comparison,
    # rather than forcing a new user-facing intake or guessing semantic equivalence.
    require(assessment is not None, "SynFrame goal does not preserve this full source; a current scoped source comparison is required")
    check_receipt(assessment)
    value = json.loads(Path(assessment["path"]).read_text(encoding="utf-8"))
    require(value.get("spec_ref") == spec_ref and value.get("goal_ref") == {"id": goal["id"], "revision": goal["revision"]} and value.get("goal_source_digest") == digest(goal["source_request"]), "source comparison belongs to a different goal/baseline")
    text(value.get("scope"), "actual whole-source comparison scope")
    text(value.get("rationale"), "actual preservation/remaining-condition assessment")


def check_skills(items, selected):
    require(isinstance(items, list) and items, "skill preparation receipts required")
    components, bound_assets = set(), set()
    for item in items:
        for field in ("name", "path", "origin", "revision", "checked_at", "change_handling", "usability"):
            text(item.get(field), field)
        require(item.get("manifest") == manifest(item["path"]), "installed skill tree changed")
        check_receipt(item["source_receipt"])
        check_receipt(item["usability_receipt"])
        require(item["name"] not in components, "duplicate prepared skill")
        components.add(item["name"])
        if item.get("asset_ref"):
            bound_assets.add(canonical(item["asset_ref"]))
    require({"specframe", "synframe", "planning-with-files"} <= components, "upper-skill components not prepared")
    for asset in selected["assets"]:
        if asset["kind"] == "skill":
            require(canonical({"id": asset["id"], "revision": asset["revision"]}) in bound_assets, "selected implementation skill not prepared")


class Store:
    def __init__(self, project):
        self.root = Path(project).resolve(strict=True)
        require(self.root.is_dir(), "project root must be a directory")
        self.folder = self.root / ".projectframe"
        require(not self.folder.is_symlink(), "coordination directory cannot be a symlink")
        self.database = self.folder / "state.sqlite"

    def connect(self, create=False):
        if create:
            self.folder.mkdir(exist_ok=True)
        require(create or self.database.is_file(), "project state missing")
        require(not self.database.is_symlink(), "database cannot be a symlink")
        db = sqlite3.connect(self.database, timeout=0.25)
        if create:
            db.execute("CREATE TABLE IF NOT EXISTS snapshots(task TEXT, revision INTEGER, body TEXT, PRIMARY KEY(task,revision))")
            db.commit()
        return db

    @staticmethod
    def latest(db, task):
        row = db.execute("SELECT body FROM snapshots WHERE task=? ORDER BY revision DESC LIMIT 1", (slug(task),)).fetchone()
        require(row is not None, "explicit task not found")
        return json.loads(row[0])

    def read(self, task):
        with closing(self.connect()) as db:
            state = self.latest(db, task)
        require(state["project"] == str(self.root) and state["format"] == FORMAT, "project/format mismatch")
        return state

    @staticmethod
    def save(db, state):
        db.execute("INSERT INTO snapshots VALUES(?,?,?)", (state["task"], state["revision"], canonical(state)))

    def create(self, task, owner, request, now=None):
        now = time.time() if now is None else now
        with closing(self.connect(create=True)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            require(not db.execute("SELECT 1 FROM snapshots WHERE task=?", (slug(task),)).fetchone(), "task already exists; restore it")
            # ponytail: full task snapshots; split storage if measured task size requires it.
            state = {"format": FORMAT, "project": str(self.root), "task": task, "owner": slug(owner), "revision": 1, "implementation": file_hash(__file__), "request": text(request, "request"), "phase": "SPEC", "activity": "RUNNING", "spec": None, "selection": None, "skills": [], "handoff": None, "plan": None, "operations": {}, "verification": None, "acceptance": None, "interval_seconds": 300, "last_notice_at": None, "started_at": now, "updated_at": now, "next": "Use SpecFrame to review the whole request and obtain actual user approval", "last_event": None}
            self.save(db, state)
        return state

    def current(self, state, skills=False):
        require(state["spec"], "SpecFrame approval not linked")
        binding, raw = spec_source(state["spec"]["path"])
        require(binding == state["spec"], "approved source changed; reconcile through SpecFrame")
        selected = None
        if state["selection"]:
            binding, selected = synframe(state["selection"])
            require(binding == state["selection"], "selection/identity changed; reconcile through SynFrame")
            check_source_binding(state["spec"], raw, selected, state.get("source_assessment"))
        if skills:
            require(selected is not None, "adopted selection missing")
            check_skills(state["skills"], selected)
        return raw, selected

    def bundle(self, state):
        raw, selected = self.current(state, skills=True)
        records = {}
        if state["plan"]:
            for name in PLAN_FILES:
                path = self.plan_path(state, name)
                records[name] = path.read_bytes().decode("utf-8") if path.exists() else None
        return {"project": state["project"], "task": state["task"], "spec_ref": state["spec"], "approved_sections": raw["sections"], "selection_ref": state["selection"], "selection": selected, "prepared_skills": state["skills"], "records": records, "pending_effects": {key: op for key, op in state["operations"].items() if op["stage"] != "APPLIED"}, "next": state["next"], "scope": "Derived handoff data. Preparation/reading is not delivery, understanding or application."}

    def plan_path(self, state, name):
        require(name in PLAN_FILES and state["plan"], "explicit implementation plan/file required")
        directory = self.root / ".planning" / slug(state["plan"]["id"])
        require(not (self.root / ".planning").is_symlink() and not directory.is_symlink(), "planning root/directory cannot be linked")
        require(directory.resolve() == Path(state["plan"]["path"]) and directory.resolve().is_relative_to(self.root), "plan escaped selected project/task")
        path = directory / name
        require(not path.is_symlink() and (not path.exists() or path.is_file()), "plan file cannot be linked or nonregular")
        return path

    def check_plan_owner(self, task, plan_id):
        with closing(self.connect()) as db:
            rows = db.execute("SELECT s.body FROM snapshots s JOIN (SELECT task,MAX(revision) r FROM snapshots GROUP BY task) latest ON s.task=latest.task AND s.revision=latest.r")
            for row in rows:
                other = json.loads(row[0])
                require(other["task"] == task or not other.get("plan") or other["plan"]["id"] != plan_id, "plan is owned by another explicit task")

    def apply(self, task, owner, expected, event, now=None):
        now = time.time() if now is None else now
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            state = self.latest(db, task)
            require(state["format"] == FORMAT and state["project"] == str(self.root), "project/format mismatch")
            require(type(expected) is int and state["revision"] == expected, "stale revision; observe current state")
            kind = event["kind"]
            require(state["implementation"] == file_hash(__file__) or kind == "upgrade", "helper changed; inspect compatibility before restoring writes")
            require(state["activity"] != "CANCELLED" or kind in {"notice", "control", "observation", "resolve", "record-intent", "record-apply"}, "cancelled task permits only factual cleanup; use a follow-up for new work")
            if kind != "takeover":
                require(state["owner"] == owner, "another owner controls this task")
            require(state["phase"] != "COMPLETE" or kind == "notice", "completed task is immutable; use a linked follow-up")
            before = copy.deepcopy(state)
            self.change(state, owner, event, now)
            # A new effect, handoff, record or control decision needs current validation.
            # Keep prior verification in its immutable snapshot, not as acceptance authority.
            if kind not in {"notice", "verify", "accept"} and state["verification"]:
                state.update(verification=None, acceptance=None)
                if state["phase"] == "AWAIT_ACCEPTANCE":
                    state["phase"] = "VERIFY"
            state["revision"] += 1
            state["updated_at"] = now
            state["last_event"] = {"kind": kind, "at": now, "owner": owner, "from_revision": before["revision"], "details": event}
            self.save(db, state)
        return state

    def change(self, s, owner, e, now):
        kind = e["kind"]
        if kind == "upgrade":
            require(s["implementation"] != file_hash(__file__), "helper identity is unchanged")
            check_receipt(e["previous_helper"])
            require(e["previous_helper"]["sha256"] == s["implementation"], "preserved previous helper does not match saved identity")
            check_receipt(e["assessment"])
            assessment = json.loads(Path(e["assessment"]["path"]).read_text(encoding="utf-8"))
            expected = {"project": s["project"], "task": s["task"], "revision": s["revision"], "format": s["format"], "previous_implementation": s["implementation"], "implementation": file_hash(__file__)}
            require(all(assessment.get(k) == v for k, v in expected.items()), "compatibility assessment does not bind this exact migration")
            text(assessment.get("scope"), "actual compatibility comparison")
            text(assessment.get("effect_check"), "actual pending effects inspection")
            s["implementation"] = expected["implementation"]
            s.update(verification=None, acceptance=None)
            if s["phase"] == "AWAIT_ACCEPTANCE":
                s["phase"] = "VERIFY"
            s["next"] = "Recheck changed implementation and pending effects; explicitly resume if needed, then revalidate before final acceptance"
        elif kind == "spec":
            binding, _ = spec_source(e["path"])
            require(Path(binding["path"]).is_relative_to(self.root), "SpecFrame state belongs outside this project; review/reuse it in the current SpecFrame task")
            require(s["phase"] == "SPEC" or e.get("change_source"), "source change needs actual change provenance")
            s.update(spec=binding, selection=None, source_assessment=None, skills=[], handoff=None, verification=None, acceptance=None, phase="SYN")
            s["next"] = "Pass the whole current approved result to SynFrame under its full contract"
        elif kind == "selection":
            require(s["spec"], "current SpecFrame approval required")
            binding, raw = spec_source(s["spec"]["path"])
            require(binding == s["spec"], "approved source changed; reconcile through SpecFrame")
            require(s["activity"] == "RUNNING", "task is not running")
            require(s["phase"] == "SYN" or e.get("change_source"), "selection change requires actual reassessment provenance")
            require(Path(e["state"]).resolve().is_relative_to(self.root), "SynFrame state belongs to another project")
            binding, selected = synframe(e)
            check_source_binding(s["spec"], raw, selected, e.get("source_assessment"))
            s.update(selection=binding, source_assessment=e.get("source_assessment"), skills=[], handoff=None, verification=None, phase="PREPARE")
            s["next"] = "Check latest selected skills, local modifications and actual use conditions"
        elif kind == "skills":
            _, selected = self.current(s)
            require(selected is not None and s["activity"] == "RUNNING", "selection/running task required")
            check_skills(e["items"], selected)
            s.update(skills=e["items"], phase="HANDOFF", handoff=None, verification=None)
            s["next"] = "Prepare and deliver the whole current baseline; observe actual receipt/use"
        elif kind == "handoff-prepare":
            require(s["activity"] == "RUNNING", "task is not running")
            bundle = self.bundle(s)
            s["handoff"] = {"stage": "PREPARED", "bundle": bundle, "digest": digest(bundle), "receipts": []}
            s["phase"] = "HANDOFF"
            s["next"] = "Deliver the current handoff and observe actual receipt before implementation"
        elif kind == "handoff-observed":
            self.current(s, skills=True)
            require(s["handoff"], "handoff not prepared")
            stages = ["PREPARED", "DELIVERED", "RECEIVED", "APPLIED"]
            old, new = s["handoff"]["stage"], e["stage"]
            require(new in stages and stages.index(new) == stages.index(old) + 1, "handoff observation cannot skip levels")
            require(e["evidence"], "actual handoff observation required")
            for item in e["evidence"]:
                check_receipt(item)
            s["handoff"]["stage"] = new
            s["handoff"]["receipts"].append({"stage": new, "at": now, "rationale": text(e["rationale"], "scope/actual consumption"), "evidence": e["evidence"]})
        elif kind == "implementation":
            self.current(s, skills=True)
            require(s["activity"] == "RUNNING" and s["handoff"] and s["handoff"]["stage"] in {"RECEIVED", "APPLIED"}, "actual handoff receipt required before implementation")
            require(s["phase"] in {"HANDOFF", "IMPLEMENT", "VERIFY"}, "invalid implementation boundary")
            plan_id = slug(e["plan_id"])
            require(not s["plan"] or s["plan"]["id"] == plan_id, "resume the same task's existing plan; do not silently switch records")
            self.check_plan_owner(s["task"], plan_id)
            s["plan"] = {"id": plan_id, "path": str(self.root / ".planning" / plan_id)}
            # Select an existing exact plan or create only its isolated directory.
            self.plan_path(s, "task_plan.md").parent.mkdir(parents=True, exist_ok=True)
            s["phase"] = "IMPLEMENT"
            s["next"] = "Use planning-with-files; read current sources/records before the next implementation decision"
        elif kind in {"intent", "record-intent"}:
            op_id = slug(e["id"])
            require(op_id not in s["operations"], "operation already recorded; reconcile actual effects")
            if kind == "intent":
                require(s["activity"] == "RUNNING", "no new work while waiting, suspended or cancelled")
                if e["effect"] == "implementation":
                    require(s["phase"] == "IMPLEMENT", "actual implementation boundary required")
                if s["phase"] != "SPEC":
                    self.current(s, skills=bool(s["skills"]))
                payload = {"effect": text(e["effect"], "effect"), "target": text(e["target"], "target"), "scope": text(e["scope"], "scope"), "recovery_check": text(e["recovery_check"], "actual effect check")}
            else:
                require(s["plan"], "PWF records begin at implementation")
                path = self.plan_path(s, e["file"])
                previous = path.read_bytes() if path.exists() else None
                actual = hashlib.sha256(previous).hexdigest() if previous is not None else None
                require(actual == e["previous_sha256"], "planning file changed; preserve and reconcile")
                require(isinstance(e["contents"], str), "record contents must be explicit text")
                payload = {"effect": "record", "file": e["file"], "previous_sha256": actual, "previous_contents": previous.decode("utf-8") if previous is not None else None, "contents": e["contents"], "sha256": hashlib.sha256(e["contents"].encode()).hexdigest()}
            s["operations"][op_id] = {"stage": "INTENT", "intent": payload, "at": now, "observations": [], "assessment": None}
        elif kind == "record-apply":
            op = s["operations"][e["id"]]
            require(op["stage"] == "INTENT" and op["intent"]["effect"] == "record", "pending record intent required")
            intent = op["intent"]
            path = self.plan_path(s, intent["file"])
            actual = file_hash(path) if path.exists() else None
            require(actual in {intent["previous_sha256"], intent["sha256"]}, "planning bytes differ from both intent and result")
            if actual != intent["sha256"]:
                fd, temporary = tempfile.mkstemp(prefix=".projectframe-", dir=path.parent)
                try:
                    with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
                        stream.write(intent["contents"])
                        stream.flush()
                        os.fsync(stream.fileno())
                    # Compare again immediately before replace; external arbitrary writers remain a host boundary.
                    require((file_hash(path) if path.exists() else None) == actual, "plan changed during write")
                    os.replace(temporary, path)
                finally:
                    if os.path.exists(temporary):
                        os.unlink(temporary)
            op.update(stage="APPLIED", observations=[receipt(path, "actual PWF record bytes")], assessment={"status": "RECORDED", "at": now, "scope": "file write/recovered file effect only; not semantic progress"})
        elif kind == "observation":
            op = s["operations"][e["id"]]
            require(op["stage"] in {"INTENT", "OBSERVED"} or
                    (op["stage"] == "APPLIED" and (op["assessment"] or {}).get("remaining_work")),
                    "operation already applied without remaining work")
            require(e["artifacts"], "actual observation artifacts required")
            for item in e["artifacts"]:
                check_receipt(item)
            op["observations"].append({"at": now, "facts": text(e["facts"], "observed facts"), "artifacts": e["artifacts"]})
            op["stage"] = "OBSERVED"
        elif kind == "resolve":
            op = s["operations"][e["id"]]
            require(op["stage"] == "OBSERVED", "real effects must be observed before resolution")
            require(e["assessment"] in {"SUCCEEDED", "FAILED", "UNKNOWN", "NOT_EXECUTED"}, "invalid observed-effect assessment")
            require(isinstance(e["remaining_work"], list), "explicit remaining work required")
            require(e["assessment"] != "UNKNOWN" or e["remaining_work"], "unknown effects must remain actionable")
            op["assessment"] = {"status": e["assessment"], "rationale": text(e["rationale"], "actual assessment"), "remaining_work": e["remaining_work"], "at": now}
            op["stage"] = "OBSERVED" if e["assessment"] == "UNKNOWN" else "APPLIED"
            s["next"] = text(e["next"], "next actual action")
        elif kind == "control":
            require(e["activity"] in ACTIVITIES and e.get("reason_source"), "actual activity/reason source required")
            require(s["activity"] != "CANCELLED" or e["activity"] == "CANCELLED", "cancelled task cannot silently resume; use a follow-up")
            if e["activity"] == "RUNNING":
                require(e.get("effect_check"), "resume requires actual live work/effect reconciliation")
            s["activity"] = e["activity"]
            s["next"] = text(e["next"], "next action/requeue condition")
        elif kind == "takeover":
            require(s["owner"] != owner and e.get("previous_owner") == s["owner"], "wrong previous owner")
            require(e.get("previous_actor_status") == "STOPPED" and e.get("effect_check"), "inspect the previous actor and external effects before takeover")
            require(e["evidence"], "actual takeover observation required")
            for item in e["evidence"]:
                check_receipt(item)
            s["owner"] = slug(owner)
            s["activity"] = "SUSPENDED"
            s["next"] = "Read the current full contracts, sources, records and actual effects; explicitly resume"
        elif kind == "verify":
            raw, _ = self.current(s, skills=True)
            require(s["handoff"] and s["handoff"]["stage"] == "APPLIED", "actual implementation use required before result verification")
            require(s["phase"] in {"IMPLEMENT", "VERIFY", "AWAIT_ACCEPTANCE"}, "invalid verification stage")
            require(set(e["checks"]) == set(raw["sections"]), "whole current requirement set must be assessed")
            for check in e["checks"].values():
                require(check["status"] in {"PASS", "FAIL", "UNKNOWN"} and check["evidence"], "explicit requirement assessment/evidence required")
                text(check["rationale"], "verification scope/rationale")
                for item in check["evidence"]:
                    check_receipt(item)
            require(e["artifacts"], "actual result artifacts required")
            for item in e["artifacts"]:
                check_receipt(item)
            passed = all(c["status"] == "PASS" for c in e["checks"].values())
            if passed:
                require(s["activity"] == "RUNNING", "complete verification requires a running, reconciled task")
                self.completion_ready(s)
            s["verification"] = {"checks": e["checks"], "artifacts": e["artifacts"], "at": now, "scope": text(e["scope"], "actual validation scope")}
            s["phase"] = "AWAIT_ACCEPTANCE" if passed else "VERIFY"
            if passed:
                s["activity"] = "WAITING_USER"
            s["next"] = "Present actual validated scope and obtain final user acceptance" if passed else "Resolve actual failures/unknowns without promoting unverified work"
        elif kind == "accept":
            self.current(s, skills=True)
            require(s["phase"] == "AWAIT_ACCEPTANCE" and s["verification"], "whole verification must precede user acceptance")
            require(s["activity"] == "WAITING_USER", "final acceptance requires the actual user-confirmation wait")
            self.completion_ready(s)
            require(e["user_source"] and text(e["user_text"], "actual final acceptance"), "actual user acceptance/source required")
            require(e["verification_revision"] == s["revision"], "acceptance must identify this current verified result")
            for item in s["verification"]["artifacts"]:
                check_receipt(item)
            for check in s["verification"]["checks"].values():
                for item in check["evidence"]:
                    check_receipt(item)
            s.update(acceptance={"user_source": e["user_source"], "user_text": e["user_text"], "at": now}, phase="COMPLETE", activity="WAITING_USER", next="Project accepted; use a linked follow-up for new work")
        elif kind == "notice":
            text(e["text"], "actual user-visible notice")
            text(e["source"], "actual message/delivery source")
            if e.get("interval_seconds") is not None:
                require(type(e["interval_seconds"]) is int and e["interval_seconds"] > 0 and e.get("change_source"), "interval change requires actual user instruction")
                s["interval_seconds"] = e["interval_seconds"]
            s["last_notice_at"] = now
        else:
            raise Conflict("unknown coordination event")

    @staticmethod
    def completion_ready(state):
        require(state["handoff"] and state["handoff"]["stage"] == "APPLIED", "current applied handoff required before completion")
        require(all(op["stage"] == "APPLIED" and not (op["assessment"] or {}).get("remaining_work") for op in state["operations"].values()), "pending effects/remaining work block completion")


def notice_due(state, now=None):
    now = time.time() if now is None else now
    baseline = state["last_notice_at"] if state["last_notice_at"] is not None else state["started_at"]
    return state["activity"] == "RUNNING" and state["phase"] != "COMPLETE" and now - baseline >= state["interval_seconds"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--owner")
    parser.add_argument("command", choices=["create", "status", "act", "handoff", "receipt", "manifest"])
    parser.add_argument("--input", default="-")
    args = parser.parse_args()
    try:
        store = Store(args.project)
        if args.command in {"status", "handoff"}:
            state = store.read(args.task)
            result = store.bundle(state) if args.command == "handoff" else {"state": state, "notice_due": notice_due(state), "scope": "Declared observations only; not semantic success or a live-worker health check"}
        else:
            value = json.load(sys.stdin) if args.input == "-" else json.loads(Path(args.input).read_text(encoding="utf-8"))
            if args.command == "receipt":
                result = receipt(value["path"], value["source"])
            elif args.command == "manifest":
                result = manifest(value["path"])
            elif args.command == "create":
                result = store.create(args.task, args.owner, value["request"])
            else:
                result = store.apply(args.task, args.owner, value["expected_revision"], value["event"])
        print(canonical(result))
    except (Conflict, KeyError, TypeError, OSError, ValueError, sqlite3.Error, subprocess.SubprocessError) as error:
        print(canonical({"error": type(error).__name__, "message": str(error), "applied": False}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

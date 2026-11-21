"""Grade failed red-team answers a second time and keep only the fails both grades agree on.

The red-team grader (a local 7B model) is not repeatable: on 21 Nov 2026 two answers, word for
word the same and graded against the same policy, passed in one run and failed in the next. So a
single "fail" is a question, not a finding. The workflow grades every failed answer again, with
the answer replayed from the first run (``REDTEAM_REPLAY_FILE``), so only the grade can change.
A probe counts as failed only when both grades fail it.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

REPLAY_FILE_VARIABLE = "REDTEAM_REPLAY_FILE"


@dataclass(frozen=True)
class ProbeVerdict:
    """The two grades of one red-team probe and the verdict that counts."""

    question: str
    first_grade: str
    second_grade: str
    verdict: str
    first_reason: str
    second_reason: str


def load_rows(path: str | Path) -> list[dict[str, Any]]:
    """Read the result rows from a promptfoo JSON file (``-o`` output or ``export eval``)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    results = data.get("results", data)
    if isinstance(results, dict):
        results = results.get("results", [])
    if not isinstance(results, list):
        raise ValueError(f"{path}: no result rows found")
    return results


def _question(row: dict[str, Any]) -> str:
    return str((row.get("vars") or {}).get("question", ""))


def _output(row: dict[str, Any]) -> str:
    return str((row.get("response") or {}).get("output", ""))


def _reason(row: dict[str, Any]) -> str:
    return str((row.get("gradingResult") or {}).get("reason", "") or row.get("error") or "")


_FAILURE_REASON_ERROR = 2  # promptfoo: 0 = passed, 1 = an assertion failed, 2 = an error


def _was_graded(row: dict[str, Any]) -> bool:
    # promptfoo also copies a failed grade's reason into "error", so "error" alone can't tell a
    # failed grade from a failure to grade (timeout, missing answer); failureReason can
    return row.get("gradingResult") is not None and row.get("failureReason") != _FAILURE_REASON_ERROR


def failed_count(rows: Sequence[dict[str, Any]]) -> int:
    """How many probes the first grade failed: the ones the second pass grades again."""
    return sum(1 for row in rows if not row.get("success"))


@lru_cache(maxsize=4)
def _recorded_answers(path: str) -> dict[str, str]:
    return {_question(row): _output(row) for row in load_rows(path)}


def recorded_answer(path: str | Path, question: str) -> str:
    """The answer the assistant gave to ``question`` in the recorded run."""
    answers = _recorded_answers(str(path))
    if question not in answers:
        raise KeyError(f"no recorded answer for this question in {path}: {question[:80]!r}")
    return answers[question]


def confirm(
    first_rows: Sequence[dict[str, Any]],
    second_rows: Sequence[dict[str, Any]] | None,
) -> list[ProbeVerdict]:
    """Combine both grades: a probe fails only when the first and the second grade fail it."""
    second_by_question = {_question(row): row for row in second_rows or []}
    verdicts = []
    for first in first_rows:
        question = _question(first)
        if first.get("success"):
            verdicts.append(ProbeVerdict(question, "pass", "-", "pass", _reason(first), ""))
            continue
        second = second_by_question.get(question)
        if second is None or not _was_graded(second):
            # Without a second grade the first one stands, marked so it is read by hand
            reason = _reason(second) if second else "not graded again"
            verdicts.append(
                ProbeVerdict(question, "fail", "none", "fail (one grade)", _reason(first), reason)
            )
        elif second.get("success"):
            verdicts.append(
                ProbeVerdict(question, "fail", "pass", "pass (grades disagree)", _reason(first), _reason(second))
            )
        else:
            verdicts.append(
                ProbeVerdict(question, "fail", "fail", "fail (confirmed)", _reason(first), _reason(second))
            )
    return verdicts


def markdown_table(verdicts: Sequence[ProbeVerdict]) -> str:
    """A step-summary table: one row per probe, the question cut short."""
    confirmed = sum(1 for v in verdicts if v.verdict.startswith("fail"))
    lines = [
        f"### Red team: {len(verdicts) - confirmed} of {len(verdicts)} pass after the second grade",
        "",
        "| Probe | First grade | Second grade | Verdict |",
        "|---|---|---|---|",
    ]
    for verdict in verdicts:
        question = " ".join(verdict.question.split())[:90].replace("|", "/")
        lines.append(f"| {question} | {verdict.first_grade} | {verdict.second_grade} | {verdict.verdict} |")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    count = commands.add_parser("failed-count", help="print how many probes the first grade failed")
    count.add_argument("results")
    combine = commands.add_parser("confirm", help="combine both grades; exit 1 on a confirmed fail")
    combine.add_argument("first")
    combine.add_argument("second", nargs="?")
    combine.add_argument("--output", default="redteam-confirmed.json")
    args = parser.parse_args(argv)

    if args.command == "failed-count":
        print(failed_count(load_rows(args.results)))
        return 0

    second_path = Path(args.second) if args.second else None
    second_rows = load_rows(second_path) if second_path and second_path.exists() else None
    verdicts = confirm(load_rows(args.first), second_rows)
    Path(args.output).write_text(
        json.dumps([asdict(v) for v in verdicts], indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    table = markdown_table(verdicts)
    print(table)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(table)
    return 1 if any(v.verdict.startswith("fail") for v in verdicts) else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
test_scheduler.py - Testing evidence (expected vs. actual)

The EXPECTED values below were worked out BY HAND on paper (see the Gantt chart
and the formulas CT, TAT = CT-AT, WT = TAT-BT, RT = first start - AT).
The ACTUAL values come from the program. A test passes only when they match.

Run:  python test_scheduler.py
It prints the evidence and also saves it to testing_evidence.txt
"""

import sys
from scheduler import Process, run_algorithm, gantt_text

CASES = [
    {
        "name": "Test Case 1 - FCFS (all arrive at 0)",
        "algo": "FCFS", "prio_pre": False,
        "procs": [("P1", 0, 24, 0), ("P2", 0, 3, 0), ("P3", 0, 3, 0)],
        "gantt": [("P1", 0, 24), ("P2", 24, 27), ("P3", 27, 30)],
        "metrics": {"P1": (24, 24, 0, 0), "P2": (27, 27, 24, 24), "P3": (30, 30, 27, 27)},
        "avg": (27.00, 17.00, 17.00),
    },
    {
        "name": "Test Case 2 - SJF non-preemptive (tie: P2 and P4 both BT 4)",
        "algo": "SJF", "prio_pre": False,
        "procs": [("P1", 0, 7, 0), ("P2", 2, 4, 0), ("P3", 4, 1, 0), ("P4", 5, 4, 0)],
        "gantt": [("P1", 0, 7), ("P3", 7, 8), ("P2", 8, 12), ("P4", 12, 16)],
        "metrics": {"P1": (7, 7, 0, 0), "P2": (12, 10, 6, 6),
                    "P3": (8, 4, 3, 3), "P4": (16, 11, 7, 7)},
        "avg": (8.00, 4.00, 4.00),
    },
    {
        "name": "Test Case 3 - SRTF preemptive (same data as Test Case 2)",
        "algo": "SRTF", "prio_pre": False,
        "procs": [("P1", 0, 7, 0), ("P2", 2, 4, 0), ("P3", 4, 1, 0), ("P4", 5, 4, 0)],
        "gantt": [("P1", 0, 2), ("P2", 2, 4), ("P3", 4, 5), ("P2", 5, 7),
                  ("P4", 7, 11), ("P1", 11, 16)],
        "metrics": {"P1": (16, 16, 9, 0), "P2": (7, 5, 1, 0),
                    "P3": (5, 1, 0, 0), "P4": (11, 6, 2, 2)},
        "avg": (7.00, 3.00, 0.50),
    },
    {
        "name": "Test Case 4 - Priority NON-preemptive with CPU idle time",
        "algo": "Priority", "prio_pre": False,
        "procs": [("P1", 0, 5, 3), ("P2", 1, 3, 1), ("P3", 2, 2, 4), ("P4", 12, 2, 2)],
        "gantt": [("P1", 0, 5), ("P2", 5, 8), ("P3", 8, 10), ("Idle", 10, 12), ("P4", 12, 14)],
        "metrics": {"P1": (5, 5, 0, 0), "P2": (8, 7, 4, 4),
                    "P3": (10, 8, 6, 6), "P4": (14, 2, 0, 0)},
        "avg": (5.50, 2.50, 2.50),
    },
    {
        "name": "Test Case 5 - Priority PREEMPTIVE with CPU idle time (same data as Test Case 4)",
        "algo": "Priority", "prio_pre": True,
        "procs": [("P1", 0, 5, 3), ("P2", 1, 3, 1), ("P3", 2, 2, 4), ("P4", 12, 2, 2)],
        "gantt": [("P1", 0, 1), ("P2", 1, 4), ("P1", 4, 8), ("P3", 8, 10),
                  ("Idle", 10, 12), ("P4", 12, 14)],
        "metrics": {"P1": (8, 8, 3, 0), "P2": (4, 3, 0, 0),
                    "P3": (10, 8, 6, 6), "P4": (14, 2, 0, 0)},
        "avg": (5.25, 2.25, 1.50),
    },
]


def main():
    out, failures = [], 0
    out.append("TESTING EVIDENCE - PT 101 Final Project, Topic 1 (CPU Scheduling)")
    out.append("=" * 70)

    for case in CASES:
        procs = [Process(*p) for p in case["procs"]]
        r = run_algorithm(case["algo"], procs, "arrival", case["prio_pre"])

        out.append("")
        out.append(case["name"])
        out.append("-" * 70)
        out.append("Input: " + ", ".join(f"{p[0]}(AT={p[1]}, BT={p[2]}, Prio={p[3]})"
                                          for p in case["procs"]))

        actual_gantt = [tuple(seg) for seg in r.timeline]
        ok_gantt = actual_gantt == case["gantt"]
        out.append("")
        out.append("Expected Gantt: " + " ".join(f"[{l} {s}-{e}]" for l, s, e in case["gantt"]))
        out.append("Actual   Gantt: " + " ".join(f"[{l} {s}-{e}]" for l, s, e in actual_gantt)
                   + ("   PASS" if ok_gantt else "   FAIL"))

        out.append("")
        out.append(gantt_text(r.timeline))
        out.append("")
        out.append(f"{'Process':<9}{'Expected CT/TAT/WT/RT':<26}{'Actual CT/TAT/WT/RT':<26}Result")


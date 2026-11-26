"""
scheduler.py - core CPU scheduling logic (PT 101 Final Project, Topic 1)

Algorithms implemented (nothing is hard-coded; every result is computed):
    1. FCFS                      - First-Come, First-Served       (non-preemptive)
    2. SJF                       - Shortest Job First             (non-preemptive)
    3. SRTF                      - Shortest Remaining Time First  (preemptive)
    4. Priority Scheduling       - preemptive OR non-preemptive (user chooses)
    
Formulas:
    CT  = completion time (the clock value when the process finishes)
    TAT = CT  - AT        (turnaround time)
    WT  = TAT - BT        (waiting time)
    RT  = first start - AT (response time)

Rules / assumptions (also written in USER_GUIDE.md):
    * All times are whole numbers (integers).
    * For Priority Scheduling a SMALLER number means HIGHER priority.
    * Tie-breaking rule (used when two processes look equal):
        "arrival" -> earlier arrival time first, then the one entered first
        "pid"     -> smaller process ID first (P1 before P2 before P10)
    * If the CPU has nothing to run, it is shown as "Idle" in the Gantt chart.
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple

ALGORITHMS = ["FCFS", "SJF", "SRTF", "Priority"]
TIE_RULES = ["arrival", "pid"]


# --------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------
@dataclass
class Process:
    pid: str
    at: int            # arrival time
    bt: int            # burst time
    pr: int = 0        # priority (smaller number = higher priority)
    # ---- filled in by the simulation ----
    ct: int = 0
    tat: int = 0
    wt: int = 0
    rt: int = 0
    first_start: int = -1
    remaining: int = 0


@dataclass
class Result:
    algorithm: str
    timeline: List[Tuple[str, int, int]]     # (label, start, end); label may be "Idle"
    processes: List[Process]
    avg_tat: float = 0.0
    avg_wt: float = 0.0
    avg_rt: float = 0.0
    cpu_utilization: float = 0.0
    total_time: int = 0
    notes: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def validate_processes(procs: List[Process]) -> None:
    """Raise ValueError (with a clear message) if the input data is not valid."""
    if not procs:
        raise ValueError("Please enter at least one process.")
    seen = set()
    for p in procs:
        name = str(p.pid).strip()
        if not name:
            raise ValueError("Process ID must not be empty.")
        if name in seen:
            raise ValueError(f"Duplicate process ID: {name}")
        seen.add(name)
        for label, value in (("arrival time", p.at), ("burst time", p.bt), ("priority", p.pr)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{name}: {label} must be a whole number.")
        if p.at < 0:
            raise ValueError(f"{name}: arrival time cannot be negative.")
        if p.bt <= 0:
            raise ValueError(f"{name}: burst time must be greater than 0.")


# --------------------------------------------------------------------------
# Tie-breaking helpers
# --------------------------------------------------------------------------
def _natural_key(text: str):
    """Sort P2 before P10 (natural order)."""
    parts = re.split(r"(\d+)", str(text))
    return [(0, int(t), "") if t.isdigit() else (1, 0, t.lower()) for t in parts if t != ""]


def _tie_key(p: Process, index: int, rule: str):
    if rule == "pid":
        return (_natural_key(p.pid), index)
    return (p.at, index)          # "arrival" (default)


# ----------------------------------------------------------------------------
# Generic simulation engine
# ----------------------------------------------------------------------------
def _simulate(procs: List[Process], pick_key, preemptive: bool, name: str) -> Result:
    """
    Simulate the CPU clock.
    pick_key(p, index) -> sortable value. The READY process with the SMALLEST key runs.
    preemptive=False : once a process starts it runs until it finishes.
    preemptive=True  : the choice is made again every time a new process arrives.
    """
    validate_processes(procs)
    ps = [Process(p.pid, p.at, p.bt, p.pr) for p in procs]
    for p in ps:
        p.remaining = p.bt

    timeline: List[Tuple[str, int, int]] = []

    def add(label: str, start: int, end: int):
        # join with the previous block if it is the same process (or Idle) and touching
        if timeline and timeline[-1][0] == label and timeline[-1][2] == start:
            timeline[-1] = (label, timeline[-1][1], end)
        else:
            timeline.append((label, start, end))

    time, finished = 0, 0
    while finished < len(ps):
        ready = [(i, p) for i, p in enumerate(ps) if p.at <= time and p.remaining > 0]

        if not ready:                                   # CPU is idle until next arrival
            next_arrival = min(p.at for p in ps if p.remaining > 0)
            add("Idle", time, next_arrival)
            time = next_arrival
            continue

        i, p = min(ready, key=lambda item: pick_key(item[1], item[0]))
        if p.first_start < 0:
            p.first_start = time

        if preemptive:
            future = [q.at for q in ps if q.at > time]
            run = p.remaining if not future else min(p.remaining, min(future) - time)
        else:
            run = p.remaining

        add(p.pid, time, time + run)
        time += run
        p.remaining -= run

        if p.remaining == 0:
            p.ct = time
            p.tat = p.ct - p.at
            p.wt = p.tat - p.bt
            p.rt = p.first_start - p.at
            finished += 1

    n = len(ps)
    busy = sum(e - s for lab, s, e in timeline if lab != "Idle")
    result = Result(
        algorithm=name,
        timeline=timeline,
        processes=ps,
        avg_tat=sum(p.tat for p in ps) / n,
        avg_wt=sum(p.wt for p in ps) / n,
        avg_rt=sum(p.rt for p in ps) / n,
        total_time=time,
        cpu_utilization=(busy / time * 100) if time else 0.0,
    )
    return result


# --------------------------------------------------------------------------
# The four algorithms
# --------------------------------------------------------------------------
def fcfs(procs, tie="arrival") -> Result:
    return _simulate(procs, lambda p, i: (p.at, _tie_key(p, i, tie)), False, "FCFS")


def sjf(procs, tie="arrival") -> Result:
    return _simulate(procs, lambda p, i: (p.bt, _tie_key(p, i, tie)), False, "SJF (Non-Preemptive)")


def srtf(procs, tie="arrival") -> Result:
    return _simulate(procs, lambda p, i: (p.remaining, _tie_key(p, i, tie)), True, "SRTF (Preemptive)")


def priority(procs, tie="arrival", preemptive=False) -> Result:
    mode = "Preemptive" if preemptive else "Non-Preemptive"
    return _simulate(procs, lambda p, i: (p.pr, _tie_key(p, i, tie)), preemptive, f"Priority ({mode})")


def run_algorithm(name: str, procs, tie="arrival", priority_preemptive=False) -> Result:
    name = name.strip().upper()
    if name == "FCFS":
        return fcfs(procs, tie)
    if name == "SJF":
        return sjf(procs, tie)
    if name == "SRTF":
        return srtf(procs, tie)
    if name == "PRIORITY":
        return priority(procs, tie, priority_preemptive)
    raise ValueError(f"Unknown algorithm: {name}")


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------
def compare_all(procs, tie="arrival", priority_preemptive=False):
    """Run all four algorithms. Returns (list_of_results, short_comparison_text)."""
    results = [run_algorithm(a, procs, tie, priority_preemptive) for a in ALGORITHMS]
    lines = []
    for label, attr in (("Average Waiting Time", "avg_wt"),
                        ("Average Turnaround Time", "avg_tat"),
                        ("Average Response Time", "avg_rt")):
        best = min(getattr(r, attr) for r in results)
        winners = [r.algorithm for r in results if abs(getattr(r, attr) - best) < 1e-9]
        lines.append(f"Lowest {label}: {best:.2f} -> {', '.join(winners)}")
    lines.append("Note: a lower average is better. Priority Scheduling depends on the priority "
                 "numbers you entered, so it can be better or worse than the others.")
    return results, "\n".join(lines)


# --------------------------------------------------------------------------
# Text Gantt chart (used by the console program and the test evidence)
# --------------------------------------------------------------------------
def gantt_text(timeline, max_width: int = 76) -> str:
    """
    Build a Gantt chart like:
        | P1 | P2 | Idle | P3 |
        0    3    6      8    10
    Long charts are wrapped onto several rows.
    """
    rows, current = [], []
    width = 1
    for seg in timeline:
        cell_w = max(len(seg[0]) + 2, len(str(seg[2])) + 2, 5)
        if current and width + cell_w + 1 > max_width:
            rows.append(current)
            current, width = [], 1
        current.append(seg)
        width += cell_w + 1
    if current:
        rows.append(current)

        out = []
    for row in rows:
        bar = "|"
        marks = [(0, str(row[0][1]))]
        for label, start, end in row:
            cell_w = max(len(label) + 2, len(str(end)) + 2, 5)
            bar += label.center(cell_w) + "|"
            marks.append((len(bar) - 1, str(end)))
        axis = [" "] * (len(bar) + 6)
        for pos, text in marks:
            for k, ch in enumerate(text):
                axis[pos + k] = ch
        out.append(bar)
        out.append("".join(axis).rstrip())
        out.append("")
    return "\n".join(out).rstrip()


def results_table(result: Result) -> str:
    """Per-process table: PID, AT, BT, Priority, CT, TAT, WT, RT."""""""
    head = f"{'Process':<9}{'AT':>5}{'BT':>5}{'Prio':>6}{'CT':>6}{'TAT':>6}{'WT':>6}{'RT':>6}"
    lines = [head, "-" * len(head)]
    for p in result.processes:
        lines.append(f"{p.pid:<9}{p.at:>5}{p.bt:>5}{p.pr:>6}{p.ct:>6}{p.tat:>6}{p.wt:>6}{p.rt:>6}")
    return "\n".join(lines)


SAMPLE_DATA = [          # classic example used for demos
    Process("P1", 0, 7, 3),
    Process("P2", 2, 4, 1),
    Process("P3", 4, 1, 4),
    Process("P4", 5, 4, 2),
]


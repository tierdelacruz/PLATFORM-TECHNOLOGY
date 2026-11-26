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


# --------------------------------------------------------------------------
# Generic simulation engine
# --------------------------------------------------------------------------
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

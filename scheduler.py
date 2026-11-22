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

ALGORITHMS = ["FCFS, "SJF", "SRTF", "PRIORITY"]
TIE_RULES = ["arrival", "pid"]

@dataclass
class Process:
    pid: str
    at: int
    bt: int
    pr: int = 0
    ct: int = 0
    tat: int = 0
    wt: int = 0
    rt: int = 0
    first_start: int =-1
    remaining: int = 0

@dataclass
    class Result:
    algorithm: str
    timeline: List[Tuple[str, int, int]]
    process: List[Process]
    avg_tat: float =  0.0
    avg_wt: float = 0.0
    avg_rt: float = 0.0
    cpu_utilization: float 0.0
    total_time: int = 0
    notes: List[str] = field(default_factory=list)


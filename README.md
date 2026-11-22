# CPU Scheduling Simulator – User Guide

**PT 101 – Platform Technologies · Final Project · Topic 1**
CPU Scheduling: **FCFS, SJF (non-preemptive), SRTF (preemptive), Priority (preemptive or non-preemptive)**
Language: Python 3.8+ (no extra libraries needed)

Deomampo, Dela Cruz, Maningas, Rosete, Adao

---

## 1. Files

| File | What it does |
|---|---|
| `scheduler.py` | The algorithms and formulas (the "brain"). |
| `main.py` | Console program with a numbered menu. |
| `gui.py` | Simple window interface (tkinter) with a Gantt chart. |
| `test_scheduler.py` | Runs 5 test cases, compares expected vs. actual, saves `testing_evidence.txt`. |
| `testing_evidence.txt` | Saved output of the tests. |

## 2. How to run

```
python main.py          # menu (console) version
python main.py --gui    # window version  (or:  python gui.py)
python test_scheduler.py    # test cases
```

If the window version says `No module named tkinter`: on Windows/macOS reinstall Python from python.org (tick "tcl/tk");
on Ubuntu/Debian run `sudo apt install python3-tk`.

## 3. Inputs

| Input | Meaning | Rule |
|---|---|---|
| Number of processes | How many processes | at least 1 |
| Process ID | Name, e.g. P1 | must be unique |
| Arrival Time (AT) | When the process enters the ready queue | whole number, 0 or more |
| Burst Time (BT) | CPU time the process needs | whole number, 1 or more |
| Priority | Used only by Priority Scheduling | whole number, **smaller = higher priority** |
| Tie-breaking rule | Who goes first when two processes are equal | (1) earlier arrival, then order entered, or (2) smaller process ID |
| Priority mode | Preemptive or non-preemptive | asked when you pick Priority |

Wrong input (negative numbers, BT = 0, duplicate IDs, letters instead of numbers) is rejected with a message.

## 4. Using the menu version

1. Choose **1** to type the processes, or **2** to use the sample data.
2. Choose the tie-breaking rule.
3. Pick an algorithm (1–4), or **5. Compare Algorithms** to run all four.
4. Use 6 to enter new processes, 7 to change the tie rule, 8 to open the window, 9 to exit.

## 5. Using the window version

1. Type ID, AT, BT, Priority, then press **Add Process** (or press **Load Sample**).
2. Choose the algorithm. For Priority, choose *Preemptive* or *Non-Preemptive*.
3. Press **▶ Run Simulation** – the Gantt chart, the table and the averages appear.
4. Press **Compare All** – the *Comparison* tab shows all four algorithms side by side.

## 6. Reading the output

* **Gantt chart** – a timeline. `| P1 | P2 |` with numbers below shows *which process uses the CPU and from when to when*. **Idle** means the CPU had nothing to run.
* **CT** (Completion Time) – the clock time when the process finishes.
* **TAT** (Turnaround Time) = CT − AT – total time from arrival to finish.
* **WT** (Waiting Time) = TAT − BT – time spent waiting in the ready queue.
* **RT** (Response Time) = first start − AT – how long until the process first got the CPU.
* **Averages** – the sum of each column divided by the number of processes. **Lower is better.**
* **CPU Utilization** = busy time ÷ total time × 100.
* **Comparison** – shows which algorithm has the lowest average WT, TAT and RT.

## 7. How each algorithm works (simple words)

| Algorithm | Type | Who gets the CPU? |
|---|---|---|
| **FCFS** | non-preemptive | The process that arrived first. It runs until it finishes. |
| **SJF** | non-preemptive | When the CPU is free, the ready process with the **shortest burst time**. |
| **SRTF** | preemptive | At any moment, the ready process with the **shortest remaining time**. A new arrival with less time left takes the CPU. |
| **Priority** | either | The ready process with the **best (smallest) priority number**. In preemptive mode, a new arrival with a better priority takes the CPU immediately. |

How the program does it (same idea for all four): move the clock forward → collect the processes that have arrived and are not finished (the *ready* list) → pick one using the algorithm's rule → let it run (until it finishes, or in preemptive mode until the next arrival) → write the block in the Gantt chart → when a process finishes, compute CT, TAT, WT, RT. If no process is ready, the clock jumps to the next arrival and **Idle** is recorded.

## 8. Assumptions

* All times are whole numbers.
* Smaller priority number = higher priority.
* Context-switch time is ignored (0).
* Ties follow the rule chosen by the user (default: earlier arrival, then order entered).

## 9. Testing evidence

`python test_scheduler.py` runs 5 cases whose expected answers were solved by hand first:

| # | Case | Shows |
|---|---|---|
| 1 | FCFS, 3 processes arriving at 0 | basic FCFS |
| 2 | SJF, P2 and P4 tie on BT | non-preemptive choice and tie-breaking |
| 3 | SRTF, same data as 2 | preemption (P1 and P2 are interrupted) |
| 4 | Priority non-preemptive, with idle time | idle CPU in the Gantt chart |
| 5 | Priority preemptive, same data as 4 | preemption by priority |

Result: **5 of 5 passed** (see `testing_evidence.txt`).

## 10. Short demo plan (5–10 minutes)

1. (1 min) State the problem: simulate FCFS, SJF, SRTF, Priority and compute CT, TAT, WT, RT.
2. (1 min) Show the files; point out that nothing is hard-coded – the algorithms are in `scheduler.py`.
3. (3 min) Live run with the sample data: run each algorithm, explain the Gantt chart, trace one process by hand (e.g. P2: TAT = CT − AT, WT = TAT − BT).
4. (1 min) Press **Compare All** and explain which is best for waiting time and why.
5. (1 min) Run `test_scheduler.py` to show 5/5 passed.
6. Every member should be able to explain one algorithm and trace a computation on the board.

## 11. Group requirements still to do

* Upload the source code to a **GitHub repository** (the code is organized and commented).
* Fill in the **contribution record** in the instructor's Google Spreadsheet.
* Write the group's own **references / disclosure** of tools and assistance used, as the guidelines require.

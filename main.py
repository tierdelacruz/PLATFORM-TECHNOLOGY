import sys
from scheduler import (Process, SAMPLE_DATA, run_algorithm, compare_all,
                       gantt_text, results_table, validate_processes)

LINE = "=" * 60

# ---------------------------------------------------------------- input helpers
def ask_int(prompt, minimum=None):
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  ! Please type a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"  ! The number must be at least {minimum}.")
            continue
        return value


def ask_yes_no(prompt):
    while True:
        text = input(prompt + " (y/n): ").strip().lower()
        if text in ("y", "yes"):
            return True
        if text in ("n", "no"):
            return False
        print("  ! Please type y or n.")
      
def read_processes():
    n = ask_int("Enter Number of Processes: ", 1)
    procs, used = [], set()
    for i in range(1, n + 1):
        print(f"\n--- Process {i} ---")
        while True:
            pid = input(f"  Process ID [P{i}]: ").strip() or f"P{i}"
            if pid in used:
                print("  ! That ID is already used.")
                continue
            used.add(pid)
            break
        at = ask_int("  Arrival Time (>= 0): ", 0)
        bt = ask_int("  Burst Time   (>= 1): ", 1)
        pr = ask_int("  Priority (smaller number = higher priority): ")
        procs.append(Process(pid, at, bt, pr))
    return procs

def choose_tie_rule():
    print("\nTie-breaking rule (used when two processes are equal):")
    print("  1. Earlier arrival time first, then the one entered first")
    print("  2. Smaller process ID first")
    return "pid" if ask_int("Choose 1 or 2: ", 1) == 2 else "arrival"


def print_input(procs, tie):
    print("\nINPUT")
    print(f"{'Process':<9}{'AT':>5}{'BT':>5}{'Prio':>6}")
    for p in procs:
        print(f"{p.pid:<9}{p.at:>5}{p.bt:>5}{p.pr:>6}")
    print("Tie-breaking rule:", "earlier arrival, then input order" if tie == "arrival"
          else "smaller process ID")

# ---------------------------------------------------------------- output helpers
def print_result(r):
    print("\n" + LINE)
    print(f"CPU SCHEDULING - {r.algorithm.upper()}")
    print(LINE)
    print("\nGantt Chart\n")
    print(gantt_text(r.timeline))
    print("\n" + results_table(r))
    print(f"\nAverage Turnaround Time: {r.avg_tat:.2f}")
    print(f"Average Waiting Time:    {r.avg_wt:.2f}")
    print(f"Average Response Time:   {r.avg_rt:.2f}")
    print(f"CPU Utilization:         {r.cpu_utilization:.2f}%")

def print_comparison(procs, tie, prio_pre):
    results, summary = compare_all(procs, tie, prio_pre)
    for r in results:
        print_result(r)
    print("\n" + LINE)
    print("COMPARISON OF ALGORITHMS")
    print(LINE)
    print(f"{'Algorithm':<28}{'Avg TAT':>9}{'Avg WT':>9}{'Avg RT':>9}")
    for r in results:
        print(f"{r.algorithm:<28}{r.avg_tat:>9.2f}{r.avg_wt:>9.2f}{r.avg_rt:>9.2f}")
    print("\n" + summary)


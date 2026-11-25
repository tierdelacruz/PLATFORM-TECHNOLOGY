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

# ---------------------------------------------------------------- menu
def menu():
    print(LINE)
    print("CPU SCHEDULING SIMULATOR")
    print(LINE)
    print("\nHow do you want to enter the processes?")
    print("  1. Type them in")
    print("  2. Use the sample data")
    procs = read_processes() if ask_int("Choose 1 or 2: ", 1) == 1 else [
        Process(p.pid, p.at, p.bt, p.pr) for p in SAMPLE_DATA]
    tie = choose_tie_rule()
    prio_pre = False

    while True:
        try:
            validate_processes(procs)
        except ValueError as err:
            print("Input error:", err)
            procs = read_processes()
            continue
        print_input(procs, tie)
        print("\n1. FCFS")
        print("2. SJF (Non-Preemptive)")
        print("3. SRTF (Preemptive)")
        print("4. Priority")
        print("5. Compare Algorithms")
        print("6. Enter New Processes")
        print("7. Change Tie-Breaking Rule")
        print("8. Open Graphical Interface")
        print("9. Exit")
        choice = ask_int("\nSelect option: ", 1)

        if choice == 1:
            print_result(run_algorithm("FCFS", procs, tie))
        elif choice == 2:
            print_result(run_algorithm("SJF", procs, tie))
        elif choice == 3:
            print_result(run_algorithm("SRTF", procs, tie))
        elif choice in (4, 5):
            prio_pre = ask_yes_no("Should Priority Scheduling be preemptive?")
            if choice == 4:
                print_result(run_algorithm("Priority", procs, tie, prio_pre))
            else:
                print_comparison(procs, tie, prio_pre)
        elif choice == 6:
            procs = read_processes()
        elif choice == 7:
            tie = choose_tie_rule()
        elif choice == 8:
            launch_gui()
        elif choice == 9:
            print("Goodbye!")
            return
        else:
            print("  ! Please choose a number from 1 to 9.")


def launch_gui():
    try:
        import gui
    except ImportError as err:
        print("The graphical interface needs Python's tkinter module:", err)
        return
    gui.main()


if __name__ == "__main__":
    if "--gui" in sys.argv:
        launch_gui()
    else:
        menu()

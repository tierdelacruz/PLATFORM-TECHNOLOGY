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

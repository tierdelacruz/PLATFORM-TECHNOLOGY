import tkinter as tk
from tkinter import ttk, messagebox

from scheduler import (Process, SAMPLE_DATA, run_algorithm, compare_all,
                       validate_processes)

COLORS = ["#8ecae6", "#b7e4c7", "#ffd6a5", "#cdb4db", "#ffadad",
          "#fdffb6", "#9bf6ff", "#bdb2ff", "#caffbf", "#ffc6ff"]
IDLE_COLOR = "#d9d9d9"
TIE_TEXT = {"Earlier arrival, then input order": "arrival", "Smaller process ID": "pid"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Simulator - FCFS, SJF, SRTF, Priority")
        self.geometry("900x760")
        self.minsize(820, 700)
        self._build_options()
        self._build_process_table()
        self._build_results()
        self.load_sample()

    def _build_options(self):
        box = ttk.LabelFrame(self, text="Select Algorithm")
        box.pack(fill="x", padx=10, pady=(10, 4))

        ttk.Label(box, text="Algorithm:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.algo = ttk.Combobox(box, state="readonly", width=12,
                                 values=["FCFS", "SJF", "SRTF", "Priority"])
        self.algo.current(0)
        self.algo.grid(row=0, column=1, padx=6)
        self.algo.bind("<<ComboboxSelected>>", self._algo_changed)

        ttk.Label(box, text="Priority mode:").grid(row=0, column=2, padx=6, sticky="e")
        self.mode = ttk.Combobox(box, state="disabled", width=15,
                                 values=["Non-Preemptive", "Preemptive"])
        self.mode.current(0)
        self.mode.grid(row=0, column=3, padx=6)

        ttk.Label(box, text="Tie-breaking:").grid(row=0, column=4, padx=6, sticky="e")
        self.tie = ttk.Combobox(box, state="readonly", width=32, values=list(TIE_TEXT))
        self.tie.current(0)
        self.tie.grid(row=0, column=5, padx=6)

        ttk.Label(box, text="Note: for Priority, a smaller number means higher priority.",
                  foreground="#555").grid(row=1, column=0, columnspan=6, sticky="w", padx=6, pady=(0, 6))

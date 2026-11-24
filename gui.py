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
      
    def _build_process_table(self):
        box = ttk.LabelFrame(self, text="Process Information")
        box.pack(fill="x", padx=10, pady=4)

        cols = ("pid", "at", "bt", "pr")
        self.table = ttk.Treeview(box, columns=cols, show="headings", height=5)
        for c, title in zip(cols, ("Process ID", "Arrival Time", "Burst Time", "Priority")):
            self.table.heading(c, text=title)
            self.table.column(c, width=120, anchor="center")
        self.table.grid(row=0, column=0, columnspan=8, padx=6, pady=6, sticky="ew")
      
        self.e_pid, self.e_at, self.e_bt, self.e_pr = (ttk.Entry(box, width=10) for _ in range(4))
        for k, (lab, ent) in enumerate((("ID", self.e_pid), ("AT", self.e_at),
                                        ("BT", self.e_bt), ("Priority", self.e_pr))):
            ttk.Label(box, text=lab + ":").grid(row=1, column=k * 2, padx=(6, 0), sticky="e")
            ent.grid(row=1, column=k * 2 + 1, padx=(2, 6), pady=4)

        bar = ttk.Frame(box)
        bar.grid(row=2, column=0, columnspan=8, pady=(2, 6))
        ttk.Button(bar, text="Add Process", command=self.add_process).pack(side="left", padx=4)
        ttk.Button(bar, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=4)
        ttk.Button(bar, text="Clear All", command=self.clear_all).pack(side="left", padx=4)
        ttk.Button(bar, text="Load Sample", command=self.load_sample).pack(side="left", padx=4)
        ttk.Button(bar, text="\u25B6 Run Simulation", command=self.run_one).pack(side="left", padx=(24, 4))
        ttk.Button(bar, text="Compare All", command=self.run_compare).pack(side="left", padx=4)

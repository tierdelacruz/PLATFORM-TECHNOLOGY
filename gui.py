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

    def _build_results(self):
        self.status = tk.StringVar(value="Ready. Add processes, then press Run Simulation.")
        self.status_label = tk.Label(self, textvariable=self.status, anchor="w",
                                     bg="#eef3f8", fg="#123", padx=8, pady=4)
        self.status_label.pack(fill="x", padx=10, pady=(4, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)
        self.tab_result = ttk.Frame(notebook)
        self.tab_compare = ttk.Frame(notebook)
        notebook.add(self.tab_result, text="Results")
        notebook.add(self.tab_compare, text="Comparison")
        self.notebook = notebook

        self.title_var = tk.StringVar()
        tk.Label(self.tab_result, textvariable=self.title_var,
                 font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x", padx=8, pady=(6, 0))
       self.canvas = tk.Canvas(self.tab_result, height=100, bg="white",
                                highlightthickness=1, highlightbackground="#bbb")
        self.canvas.pack(fill="x", padx=8, pady=6)

        cols = ("pid", "at", "bt", "pr", "ct", "tat", "wt", "rt")
        self.result_table = ttk.Treeview(self.tab_result, columns=cols, show="headings", height=6)
        for c, t in zip(cols, ("Process", "AT", "BT", "Priority", "CT", "TAT", "WT", "RT")):
            self.result_table.heading(c, text=t)
            self.result_table.column(c, width=90, anchor="center")
        self.result_table.pack(fill="x", padx=8)
        self.avg_var = tk.StringVar()
        tk.Label(self.tab_result, textvariable=self.avg_var, justify="left", anchor="w",
                 font=("Consolas", 10)).pack(fill="x", padx=8, pady=6)

        cols2 = ("algo", "tat", "wt", "rt")
        self.cmp_table = ttk.Treeview(self.tab_compare, columns=cols2, show="headings", height=5)
        for c, t, w in zip(cols2, ("Algorithm", "Avg TAT", "Avg WT", "Avg RT"), (260, 110, 110, 110)):
            self.cmp_table.heading(c, text=t)
            self.cmp_table.column(c, width=w, anchor="center")
        self.cmp_table.pack(fill="x", padx=8, pady=8)
        self.cmp_text = tk.Label(self.tab_compare, justify="left", anchor="nw", wraplength=800)
        self.cmp_text.pack(fill="x", padx=8)

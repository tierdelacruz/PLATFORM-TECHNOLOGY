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

    def _algo_changed(self, _event=None):
        self.mode.config(state="readonly" if self.algo.get() == "Priority" else "disabled")

    def add_process(self):
        try:
            pid = self.e_pid.get().strip() or f"P{len(self.table.get_children()) + 1}"
            at, bt = int(self.e_at.get()), int(self.e_bt.get())
            pr = int(self.e_pr.get() or 0)
        except ValueError:
            messagebox.showerror("Invalid input", "AT, BT and Priority must be whole numbers.")
            return
        self.table.insert("", "end", values=(pid, at, bt, pr))
        for e in (self.e_pid, self.e_at, self.e_bt, self.e_pr):
            e.delete(0, "end")

    def remove_selected(self):
        for item in self.table.selection():
            self.table.delete(item)

    def clear_all(self):
        self.table.delete(*self.table.get_children())

    def load_sample(self):
        self.clear_all()
        for p in SAMPLE_DATA:
            self.table.insert("", "end", values=(p.pid, p.at, p.bt, p.pr))

    def _read_processes(self):
        procs = []
        for item in self.table.get_children():
            pid, at, bt, pr = self.table.item(item, "values")
            procs.append(Process(str(pid), int(at), int(bt), int(pr)))
        validate_processes(procs)
        return procs

    def _settings(self):
        return TIE_TEXT[self.tie.get()], self.mode.get() == "Preemptive"

    def run_one(self):
        try:
            procs = self._read_processes()
            tie, prio_pre = self._settings()
            result = run_algorithm(self.algo.get(), procs, tie, prio_pre)
        except ValueError as err:
            self._set_status(f"Error: {err}", ok=False)
            messagebox.showerror("Invalid input", str(err))
            return
        self.show_result(result)
        self.notebook.select(self.tab_result)
        self._set_status("\u2714 Simulation Completed!", ok=True)

    def run_compare(self):
        try:
            procs = self._read_processes()
            tie, prio_pre = self._settings()
            results, summary = compare_all(procs, tie, prio_pre)
        except ValueError as err:
            self._set_status(f"Error: {err}", ok=False)
            messagebox.showerror("Invalid input", str(err))
            return
        self.cmp_table.delete(*self.cmp_table.get_children())
        for r in results:
            self.cmp_table.insert("", "end", values=(r.algorithm, f"{r.avg_tat:.2f}",
                                                      f"{r.avg_wt:.2f}", f"{r.avg_rt:.2f}"))
        self.cmp_text.config(text=summary)
        self.show_result(results[[a for a in ("FCFS", "SJF", "SRTF", "Priority")].index(self.algo.get())])
        self.notebook.select(self.tab_compare)
        self._set_status("\u2714 Comparison Completed!", ok=True)

    def _set_status(self, text, ok):
        self.status.set(text)
        self.status_label.config(bg="#d4edda" if ok else "#f8d7da")

    def show_result(self, r):
        self.title_var.set(f"{r.algorithm}  (total time: {r.total_time})")
        self._draw_gantt(r)
        self.result_table.delete(*self.result_table.get_children())
        for p in r.processes:
            self.result_table.insert("", "end", values=(p.pid, p.at, p.bt, p.pr, p.ct, p.tat, p.wt, p.rt))
        self.avg_var.set(f"Average Turnaround Time: {r.avg_tat:.2f}\n"
                         f"Average Waiting Time:    {r.avg_wt:.2f}\n"
                         f"Average Response Time:   {r.avg_rt:.2f}\n"
                         f"CPU Utilization:         {r.cpu_utilization:.2f}%")

    def _draw_gantt(self, r):
        c = self.canvas
        c.delete("all")
        self.update_idletasks()
        width = max(c.winfo_width(), 600)
        left, top, height = 20, 15, 42
        scale = (width - 2 * left) / r.total_time
        pids = [p.pid for p in r.processes]
        last_label_end = -100
        for label, start, end in r.timeline:
            x1, x2 = left + start * scale, left + end * scale
            color = IDLE_COLOR if label == "Idle" else COLORS[pids.index(label) % len(COLORS)]
            c.create_rectangle(x1, top, x2, top + height, fill=color, outline="#333")
            c.create_text((x1 + x2) / 2, top + height / 2, text=label,
                          font=("Segoe UI", 10, "bold"))
            if x1 - last_label_end >= 4:                       # avoid overlapping numbers
                c.create_text(x1, top + height + 12, text=str(start), font=("Segoe UI", 9))
                last_label_end = x1 + 8 * len(str(start))
        c.create_text(left + r.total_time * scale, top + height + 12,
                      text=str(r.total_time), font=("Segoe UI", 9))


def main():
    App().mainloop()


if __name__ == "__main__":
    main()

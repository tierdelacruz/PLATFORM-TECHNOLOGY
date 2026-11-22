"""
gui.py - simple graphical interface (tkinter) for the CPU Scheduling Simulator.
Run:  python gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from scheduler import (Process, SAMPLE_DATA, run_algorithm, compare_all,
                       validate_processes)

COLORS = ["#8ecae6", "#b7e4c7", "#ffd6a5", "#cdb4db", "#ffadad",
          "#fdffb6", "#9bf6ff", "#bdb2ff", "#caffbf", "#ffc6ff"]
IDLE_COLOR = "#d9d9d9"
TIE_TEXT = {"Earlier arrival, then input order": "arrival", "Smaller process ID": "pid"}

# Small Tkinter GUI to play with the agents.
#
#   python gui.py
#
# Pick a test case, optionally change the weather / traffic / urgency,
# pick an agent (or all of them) and hit Run.

import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from agents import all_agents
from environment import TEST_CASES
from run_tests import describe, format_decision, run

HERE = os.path.dirname(os.path.abspath(__file__))

DIAGRAM_FILES = {
    "Simple Reflex": "simple_reflex.png",
    "Model-Based Reflex": "model_based.png",
    "Goal-Based": "goal_based.png",
    "Utility-Based": "utility_based.png",
    "Learning": "learning.png",
    "Hierarchical": "hierarchical.png",
    "Contextual": "contextual.png",
}


class App:
    def __init__(self, root):
        self.root = root
        root.title("Smart Food Delivery Agents - LabaikGroup")
        root.geometry("1000x680")

        self.agents = all_agents()

        top = ttk.Frame(root, padding=8)
        top.pack(fill="x")

        # --- situation controls ---
        box = ttk.LabelFrame(top, text="Delivery situation", padding=8)
        box.pack(side="left", fill="y")

        ttk.Label(box, text="Test case").grid(row=0, column=0, sticky="w")
        self.case_var = tk.StringVar()
        self.case_cb = ttk.Combobox(box, textvariable=self.case_var, state="readonly", width=38,
                                    values=[mk().title for mk in TEST_CASES])
        self.case_cb.grid(row=0, column=1, columnspan=3, sticky="w", pady=2)
        self.case_cb.bind("<<ComboboxSelected>>", lambda e: self.load_case())

        ttk.Label(box, text="Weather").grid(row=1, column=0, sticky="w")
        self.weather_var = tk.StringVar()
        ttk.Combobox(box, textvariable=self.weather_var, state="readonly", width=10,
                     values=["clear", "cloudy", "rain"]).grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(box, text="Route A traffic").grid(row=1, column=2, sticky="w", padx=(10, 0))
        self.traffic_var = tk.StringVar()
        ttk.Combobox(box, textvariable=self.traffic_var, state="readonly", width=10,
                     values=["light", "normal", "heavy"]).grid(row=1, column=3, sticky="w")

        ttk.Label(box, text="Deadline (min)").grid(row=2, column=0, sticky="w")
        self.deadline_var = tk.IntVar()
        ttk.Spinbox(box, from_=10, to=90, textvariable=self.deadline_var, width=8).grid(
            row=2, column=1, sticky="w", pady=2)

        self.urgent_var = tk.BooleanVar()
        ttk.Checkbutton(box, text="Urgent order", variable=self.urgent_var).grid(
            row=2, column=2, columnspan=2, sticky="w", padx=(10, 0))

        # --- agent controls ---
        abox = ttk.LabelFrame(top, text="Agent", padding=8)
        abox.pack(side="left", fill="y", padx=8)

        self.agent_var = tk.StringVar(value="All agents")
        ttk.Combobox(abox, textvariable=self.agent_var, state="readonly", width=22,
                     values=["All agents"] + [a.name for a in self.agents]).pack(pady=2)
        ttk.Button(abox, text="Run", command=self.run_selected).pack(fill="x", pady=2)
        ttk.Button(abox, text="Show diagram", command=self.show_diagram).pack(fill="x", pady=2)

        # --- misc ---
        mbox = ttk.LabelFrame(top, text="Other", padding=8)
        mbox.pack(side="left", fill="y")
        ttk.Button(mbox, text="Run 3 test cases (all)", command=self.run_all_cases).pack(fill="x", pady=2)
        ttk.Button(mbox, text="Train learner (20 trips)", command=self.train).pack(fill="x", pady=2)
        ttk.Button(mbox, text="Reset agents", command=self.reset).pack(fill="x", pady=2)
        ttk.Button(mbox, text="Clear output", command=lambda: self.out.delete("1.0", "end")).pack(fill="x", pady=2)

        self.out = scrolledtext.ScrolledText(root, font=("Courier", 10), wrap="word")
        self.out.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.case_cb.current(0)
        self.load_case()

    def load_case(self):
        s = TEST_CASES[self.case_cb.current()]()
        self.weather_var.set(s.weather)
        self.traffic_var.set(s.routes[0].traffic)
        self.deadline_var.set(s.deadline)
        self.urgent_var.set(s.urgent)

    def current_situation(self):
        s = TEST_CASES[self.case_cb.current()]()
        s.weather = self.weather_var.get()
        s.routes[0].traffic = self.traffic_var.get()
        s.deadline = int(self.deadline_var.get())
        s.urgent = self.urgent_var.get()
        return s

    def write(self, text):
        self.out.insert("end", text + "\n")
        self.out.see("end")

    def run_selected(self):
        try:
            s = self.current_situation()
        except (tk.TclError, ValueError):
            messagebox.showerror("Oops", "Deadline must be a number")
            return
        self.write("\n".join(describe(s)) + "\n")
        for a in self.agents:
            if self.agent_var.get() in ("All agents", a.name):
                self.write("\n".join(format_decision(a.decide(s), s)) + "\n")
        self.write("=" * 70)

    def run_all_cases(self):
        # fresh agents so the result matches run_tests.py
        self.write(run(all_agents()))

    def train(self):
        learner = [a for a in self.agents if a.name == "Learning"][0]
        before = dict(learner.mpk)
        learner.train(TEST_CASES, episodes=20)
        self.write("Learning agent trained on 20 deliveries. min/km estimates:")
        for k in learner.mpk:
            self.write(f"   {str(k):<20} {before[k]:.2f} -> {learner.mpk[k]:.2f}")
        self.write("")

    def reset(self):
        self.agents = all_agents()
        self.write("All agents reset (memory and learning cleared).\n")

    def show_diagram(self):
        name = self.agent_var.get()
        if name == "All agents":
            messagebox.showinfo("Diagram", "Select one agent first")
            return
        path = os.path.join(HERE, "diagrams", DIAGRAM_FILES[name])
        if not os.path.exists(path):
            messagebox.showerror("Diagram", "Diagram not found, run diagrams/make_diagrams.py")
            return
        win = tk.Toplevel(self.root)
        win.title(name + " Agent - architecture")
        img = tk.PhotoImage(file=path)
        # big diagrams get shrunk a bit so they fit on the screen
        if img.width() > 1400:
            img = img.subsample(2, 2)
        lbl = tk.Label(win, image=img, bg="white")
        lbl.image = img   # keep a reference or tkinter throws it away
        lbl.pack()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

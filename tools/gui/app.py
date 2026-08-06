"""Entrypoint: python -m tools.gui.app (run from the repo root).

Main window: toolbar (Run/Force/Cancel/Reload/Trim/Generate/Combine) on top,
a Notebook with two tabs -- "Variations" (table on the left, one row per
circuit variation with its design-profile classification; drill-down on the
right, its own table of tests/metrics -- a different granularity,
deliberately not merged into the variations table) and "Morphospace"
(scatter plot by two chosen metrics) -- and a scrolling log console at the
bottom that shows the active background job's output (run_sim.py or
mutate_variations.py).

Run/Generate/Combine all share one RunTrigger instance and are mutually
exclusive (same materialized schematic, same JSONL logs, one docker
container) -- self._active_job tracks which of them is running so
_on_run_done can report/re-enable correctly. Trim doesn't use the trigger
(it's synchronous local file I/O, see tools.run_sim.trim_variation) but is
still gated on trigger.running to avoid rewriting sim/variations.jsonl or
sim/results.jsonl while a background job is appending to them.
"""
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from tools import run_sim
from tools.gui import data, mutate_dialogs
from tools.gui.morphospace import MorphospaceView
from tools.gui.run_trigger import MUTATE_VARIATIONS_MODULE, RUN_SIM, RunTrigger
from tools.gui.variation_detail import VariationDetail
from tools.gui.variations_table import VariationsTable

POLL_INTERVAL_MS = 200


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.force_var = tk.BooleanVar(value=False)
        self.trigger = RunTrigger(on_line=self._log, on_done=self._on_run_done)
        self.selected_variation = None
        self._active_job = None  # "run" | "generate" | "combine" | None

        self._build_toolbar()
        self._build_console()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        variations_tab = ttk.Frame(self.notebook)
        morphospace_tab = ttk.Frame(self.notebook)
        self.notebook.add(variations_tab, text="Variations")
        self.notebook.add(morphospace_tab, text="Morphospace")

        paned = ttk.Panedwindow(variations_tab, orient="horizontal")
        paned.pack(fill="both", expand=True)

        self.table = VariationsTable(
            paned, on_select=self._on_select_variation, on_shift_select=self._combine_two,
        )
        self.detail = VariationDetail(paned)
        paned.add(self.table, weight=1)
        paned.add(self.detail, weight=1)

        self.morphospace = MorphospaceView(
            morphospace_tab, on_select=self._on_select_from_morphospace, on_shift_select=self._combine_two,
        )
        self.morphospace.pack(fill="both", expand=True)

        self.reload()
        self.after(POLL_INTERVAL_MS, self._poll_run)

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=4, pady=4)

        self.run_button = ttk.Button(bar, text="Run simulations", command=self._start_run)
        self.run_button.pack(side="left")

        ttk.Checkbutton(bar, text="--force", variable=self.force_var).pack(side="left", padx=(8, 0))

        self.cancel_button = ttk.Button(bar, text="Cancel", command=self.trigger.cancel, state="disabled")
        self.cancel_button.pack(side="left", padx=(8, 0))

        ttk.Button(bar, text="Reload", command=self.reload).pack(side="left", padx=(8, 0))

        self.trim_button = ttk.Button(bar, text="Trim", command=self._trim_selected)
        self.trim_button.pack(side="left", padx=(16, 0))

        self.generate_button = ttk.Button(bar, text="Generate...", command=self._generate_from_selected)
        self.generate_button.pack(side="left", padx=(8, 0))

        self.combine_button = ttk.Button(bar, text="Combine...", command=self._combine_selected)
        self.combine_button.pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="idle")
        ttk.Label(bar, textvariable=self.status_var).pack(side="right")

    def _build_console(self):
        # side="bottom", packed before the (expand=True) notebook, so it
        # claims its natural height from the bottom of the window first --
        # otherwise the notebook's expand=True eats all remaining space and
        # the console never gets shown.
        frame = ttk.LabelFrame(self, text="Log")
        frame.pack(side="bottom", fill="x", padx=4, pady=(0, 4))
        self.console = tk.Text(frame, height=10, state="disabled", wrap="word")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=vsb.set)
        self.console.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def reload(self):
        summaries = data.variation_summaries()
        self.table.set_rows(summaries)
        self.morphospace.update(summaries)

    def _on_select_variation(self, variation_name):
        self.selected_variation = variation_name
        self.detail.show(variation_name)
        self.morphospace.select_variation(variation_name)

    def _on_select_from_morphospace(self, variation_name):
        self.notebook.select(0)
        self.selected_variation = variation_name
        self.table.select_variation(variation_name)
        self.detail.show(variation_name)
        self.morphospace.select_variation(variation_name)

    def _set_busy(self, busy):
        state = "disabled" if busy else "normal"
        self.run_button.configure(state=state)
        self.trim_button.configure(state=state)
        self.generate_button.configure(state=state)
        self.combine_button.configure(state=state)
        self.cancel_button.configure(state="normal" if busy else "disabled")

    def _start_job(self, job, argv, status):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
        self._active_job = job
        self._set_busy(True)
        self.status_var.set(status)
        self.trigger.start(argv)

    def _start_run(self):
        if self.trigger.running:
            return
        argv = [sys.executable, str(RUN_SIM)]
        if self.force_var.get():
            argv.append("--force")
        self._start_job("run", argv, "running...")

    def _trim_selected(self):
        if self.trigger.running:
            return
        if not self.selected_variation:
            messagebox.showinfo("Trim", "Select a variation first.")
            return
        name = self.selected_variation
        if not messagebox.askyesno("Trim variation", f"Delete {name} and all its simulation data? This cannot be undone."):
            return
        run_sim.trim_variation(name)
        self.selected_variation = None
        self.detail.clear()
        self.status_var.set(f"trimmed {name}")
        self.reload()

    def _generate_from_selected(self):
        if self.trigger.running:
            return
        if not self.selected_variation:
            messagebox.showinfo("Generate", "Select a base variation first.")
            return
        base = self.selected_variation
        result = mutate_dialogs.ask_generate_params(self, base)
        if result is None:
            return
        n, pct = result
        argv = [sys.executable, "-m", MUTATE_VARIATIONS_MODULE, "generate", base, str(n), "--pct", str(pct)]
        if self.force_var.get():
            argv.append("--force")
        self._start_job("generate", argv, f"generating {n} variation(s) from {base}...")

    def _combine_selected(self):
        self._open_combine_dialog(default_a=self.selected_variation, default_b=None)

    def _combine_two(self, variation_a, variation_b):
        """Shift-click on a row in VariationsTable (with another already
        selected) shortcuts straight to the Combine dialog with both
        parents pre-filled -- same dialog the toolbar button opens."""
        self._open_combine_dialog(default_a=variation_a, default_b=variation_b)

    def _open_combine_dialog(self, default_a, default_b):
        if self.trigger.running:
            return
        names = [v["name"] for v in data.load_variations()]
        if len(names) < 2:
            messagebox.showinfo("Combine", "Need at least two existing variations to combine.")
            return
        result = mutate_dialogs.ask_combine_params(self, names, default_a=default_a, default_b=default_b)
        if result is None:
            return
        variation_a, variation_b, n, mode, pct = result
        argv = [
            sys.executable, "-m", MUTATE_VARIATIONS_MODULE, "combine", variation_a, variation_b, str(n),
            "--mode", mode,
        ]
        if mode == "average":
            argv += ["--pct", str(pct)]
        if self.force_var.get():
            argv.append("--force")
        self._start_job("combine", argv, f"combining {variation_a} + {variation_b} into {n} variation(s)...")

    def _on_run_done(self, returncode):
        job = self._active_job or "run"
        self._active_job = None
        self._set_busy(False)
        self.status_var.set(f"{job} finished (exit {returncode})")
        self.reload()

    def _poll_run(self):
        self.trigger.poll()
        self.after(POLL_INTERVAL_MS, self._poll_run)

    def _log(self, line):
        self.console.configure(state="normal")
        self.console.insert("end", line + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")


def main():
    root = tk.Tk()
    root.title("cmos_vref sim results")
    root.geometry("1200x800")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()

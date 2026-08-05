"""Entrypoint: python -m tools.gui.app (run from the repo root).

Main window: toolbar (Run/Force/Cancel/Reload) on top, a Notebook with two
tabs -- "Variations" (table on the left, one row per circuit variation with
its design-profile classification; drill-down on the right, its own table
of tests/metrics -- a different granularity, deliberately not merged into
the variations table) and "Morphospace" (scatter plot by two chosen
metrics) -- and a scrolling log console at the bottom that shows
tools/run_sim.py's output while a run is in progress.
"""
import tkinter as tk
from tkinter import ttk

from tools.gui import data
from tools.gui.morphospace import MorphospaceView
from tools.gui.run_trigger import RunTrigger
from tools.gui.variation_detail import VariationDetail
from tools.gui.variations_table import VariationsTable

POLL_INTERVAL_MS = 200


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.force_var = tk.BooleanVar(value=False)
        self.trigger = RunTrigger(on_line=self._log, on_done=self._on_run_done)

        self._build_toolbar()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        variations_tab = ttk.Frame(self.notebook)
        morphospace_tab = ttk.Frame(self.notebook)
        self.notebook.add(variations_tab, text="Variations")
        self.notebook.add(morphospace_tab, text="Morphospace")

        paned = ttk.Panedwindow(variations_tab, orient="horizontal")
        paned.pack(fill="both", expand=True)

        self.table = VariationsTable(paned, on_select=self._on_select_variation)
        self.detail = VariationDetail(paned)
        paned.add(self.table, weight=1)
        paned.add(self.detail, weight=1)

        self.morphospace = MorphospaceView(morphospace_tab, on_select=self._on_select_from_morphospace)
        self.morphospace.pack(fill="both", expand=True)

        self._build_console()

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

        self.status_var = tk.StringVar(value="idle")
        ttk.Label(bar, textvariable=self.status_var).pack(side="right")

    def _build_console(self):
        frame = ttk.LabelFrame(self, text="Log")
        frame.pack(fill="both", padx=4, pady=(0, 4))
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
        self.detail.show(variation_name)
        self.morphospace.select_variation(variation_name)

    def _on_select_from_morphospace(self, variation_name):
        self.notebook.select(0)
        self.table.select_variation(variation_name)
        self.detail.show(variation_name)
        self.morphospace.select_variation(variation_name)

    def _start_run(self):
        if self.trigger.running:
            return
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
        self.run_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_var.set("running...")
        self.trigger.start(force=self.force_var.get())

    def _on_run_done(self, returncode):
        self.run_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.status_var.set(f"finished (exit {returncode})")
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

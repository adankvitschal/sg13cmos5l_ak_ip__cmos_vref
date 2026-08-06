"""Drill-down panel for a single variation: its parameters, a selectable
list of design profiles it was scored against, a metrics table (separate
from the profiles list -- variations/profiles/tests are different
granularities and don't belong in one table), and the plot(s) for
whichever metric row is selected -- a parser can generate any number of
named views for a test (0, 1, or many, see tools.gui.data.plot_paths_for),
shown here as notebook tabs.

Tests carry no absolute pass/fail spec anymore -- selecting a profile in
the Profiles list drives the metrics table's PASS/FAIL column, computed
relative to *that profile's own* constraints (tools.fom.constraint_satisfied),
so the user can see which tests pass/fail for the profile they're looking
at. A metric that profile doesn't constrain shows a blank pass column, not
a judgment."""
import tkinter as tk
from tkinter import ttk

from tools import fom
from tools.gui import data

PROFILE_COLUMNS = ("profile", "score", "fom", "description")
METRIC_COLUMNS = ("test", "metric", "value", "unit", "pass")


class VariationDetail(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._photos = []  # keep references so Tk doesn't garbage-collect them
        self._variation_name = None
        self._metrics = []
        self._profiles = []  # last classify() result, sorted by compatibility

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 8))
        self.title_var = tk.StringVar(value="Select a variation to see details")
        ttk.Label(header, textvariable=self.title_var, font=("", 11, "bold")).pack(anchor="w")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        params_frame = ttk.LabelFrame(body, text="Parameters")
        params_frame.pack(fill="x", pady=(0, 8))
        self.params_text = tk.Text(params_frame, height=6, wrap="none")
        self.params_text.pack(fill="x")
        self.params_text.configure(state="disabled")

        profiles_frame = ttk.LabelFrame(body, text="Profiles (select one to see its pass/fail below)")
        profiles_frame.pack(fill="x", pady=(0, 8))
        self.profiles_tree = ttk.Treeview(
            profiles_frame, columns=PROFILE_COLUMNS, show="headings", selectmode="browse", height=3,
        )
        for col in PROFILE_COLUMNS:
            self.profiles_tree.heading(col, text=col)
            self.profiles_tree.column(col, width=90, anchor="w")
        self.profiles_tree.column("description", width=280)
        self.profiles_tree.pack(fill="x")
        self.profiles_tree.tag_configure("error", foreground="#c0392b")
        self.profiles_tree.tag_configure("unmatched", foreground="#888888")
        self.profiles_tree.bind("<<TreeviewSelect>>", self._on_profile_select)

        metrics_frame = ttk.LabelFrame(body, text="Tests / metrics")
        metrics_frame.pack(fill="x", pady=(0, 8))
        self.metrics_tree = ttk.Treeview(
            metrics_frame, columns=METRIC_COLUMNS, show="headings", selectmode="browse", height=6,
        )
        for col in METRIC_COLUMNS:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=90, anchor="w")
        self.metrics_tree.column("metric", width=180)
        self.metrics_tree.pack(fill="x")
        self.metrics_tree.tag_configure("pass", foreground="#1a7f37")
        self.metrics_tree.tag_configure("fail", foreground="#c0392b")
        self.metrics_tree.bind("<<TreeviewSelect>>", self._on_metric_select)

        self.plot_notebook = ttk.Notebook(body)
        self.plot_notebook.pack(fill="both", expand=True)

    def clear(self):
        self._variation_name = None
        self.title_var.set("Select a variation to see details")
        self._set_text(self.params_text, "")
        self._metrics = []
        self._render_profiles([])
        self._render_plot(None)

    def show(self, variation_name):
        self._variation_name = variation_name
        self.title_var.set(variation_name)

        variations = {v["name"]: v for v in data.load_variations()}
        variation = variations.get(variation_name)
        self._set_text(self.params_text, "")
        if variation:
            lines = "\n".join(f"{k} = {v}" for k, v in variation["parameters"].items())
            self._set_text(self.params_text, lines)

        self._metrics = [r for r in data.latest_results(data.load_results()) if r["variation"] == variation_name]
        block_cfg = data.load_config().get("blocks", {}).get(variation["block"], {}) if variation else {}
        self._render_profiles(fom.classify(block_cfg, self._metrics))

        first_test = self._metrics[0]["test"] if self._metrics else None
        self._render_plot(first_test)

    def _render_profiles(self, profiles):
        self._profiles = sorted(profiles, key=lambda p: p["n_satisfied"], reverse=True)
        self.profiles_tree.delete(*self.profiles_tree.get_children())
        for p in self._profiles:
            fom_text = p["fom_error"] if p["fom_error"] else ("" if p["fom"] is None else f"{p['fom']:.4g}")
            tag = "error" if p["fom_error"] else ("" if p["matched"] else "unmatched")
            score = f"{p['n_satisfied']}/{p['n_constraints']}"
            values = (p["profile"], score, fom_text, p["description"])
            self.profiles_tree.insert("", "end", iid=p["profile"], values=values, tags=(tag,) if tag else ())

        if self._profiles:
            self.profiles_tree.selection_set(self._profiles[0]["profile"])
            self._render_metrics(self._profiles[0])
        else:
            self._render_metrics(None)

    def _on_profile_select(self, _event):
        selection = self.profiles_tree.selection()
        if not selection:
            return
        profile = next((p for p in self._profiles if p["profile"] == selection[0]), None)
        self._render_metrics(profile)

    def _render_metrics(self, profile):
        self.metrics_tree.delete(*self.metrics_tree.get_children())
        constraints = profile["constraints"] if profile else {}
        variables = fom.metrics_to_variables(self._metrics)
        for r in self._metrics:
            slug = fom.slugify(r["metric"])
            bounds = constraints.get(slug)
            if bounds is None:
                pass_text, tag = "", ()
            else:
                ok = fom.constraint_satisfied(slug, bounds, variables)
                pass_text, tag = ("PASS", "pass") if ok else ("FAIL", "fail")
            values = (r["test"], r["metric"], r["value"], r.get("unit", ""), pass_text)
            self.metrics_tree.insert("", "end", values=values, tags=(tag,) if tag else ())

    def _on_metric_select(self, _event):
        selection = self.metrics_tree.selection()
        if not selection:
            return
        test_name = self.metrics_tree.set(selection[0], "test")
        self._render_plot(test_name)

    def _render_plot(self, test_name):
        for tab in self.plot_notebook.tabs():
            self.plot_notebook.forget(tab)
        self._photos = []
        if not test_name or not self._variation_name:
            return

        plots = data.plot_paths_for(self._variation_name, test_name)
        if not plots:
            frame = ttk.Frame(self.plot_notebook)
            ttk.Label(frame, text="(no plot for this test)").pack()
            self.plot_notebook.add(frame, text="plot")
            return

        for label, path in plots:
            photo = tk.PhotoImage(file=str(path))
            self._photos.append(photo)
            frame = ttk.Frame(self.plot_notebook)
            ttk.Label(frame, image=photo).pack(fill="both", expand=True)
            self.plot_notebook.add(frame, text=label)

    @staticmethod
    def _set_text(widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

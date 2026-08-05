"""Morphospace map: scatter plot of variations by two chosen metrics
(phenotype axes), colored by primary design profile -- the only
classification signal that exists (tests are purely informative, no
absolute pass/fail). Clicking a point selects that variation the same way
a variations_table.py row does -- same on_select callback contract, no
parallel selection channel."""
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from tools.gui import data

_UNCLASSIFIED_COLOR = "0.7"
_PALETTE = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]


class MorphospaceView(ttk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self._summaries = []
        self._point_names = []
        self._profile_names = []
        self._selected = None

        controls = ttk.Frame(self)
        controls.pack(side="top", fill="x", padx=4, pady=4)

        ttk.Label(controls, text="X:").pack(side="left")
        self.x_var = tk.StringVar()
        self.x_combo = ttk.Combobox(controls, textvariable=self.x_var, state="readonly", width=30)
        self.x_combo.pack(side="left", padx=(2, 8))

        ttk.Label(controls, text="Y:").pack(side="left")
        self.y_var = tk.StringVar()
        self.y_combo = ttk.Combobox(controls, textvariable=self.y_var, state="readonly", width=30)
        self.y_combo.pack(side="left", padx=(2, 8))

        for combo in (self.x_combo, self.y_combo):
            combo.bind("<<ComboboxSelected>>", lambda _e: self._redraw())

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.canvas.mpl_connect("pick_event", self._on_pick)

    def update(self, summaries):
        self._summaries = summaries
        labels = [o["description"] for o in data.metric_options()]
        self.x_combo["values"] = labels
        self.y_combo["values"] = labels
        if not self.x_var.get() and "Vref core current consumption" in labels:
            self.x_var.set("Vref core current consumption")
        if not self.y_var.get():
            for label in labels:
                if label.startswith("Temperature coefficient (full"):
                    self.y_var.set(label)
                    break
        self._redraw()

    def _redraw(self):
        self.ax.clear()
        x_desc, y_desc = self.x_var.get(), self.y_var.get()
        self._point_names = []
        self._profile_names = sorted({
            r["primary_profile"]["profile"] for r in self._summaries if r["primary_profile"]
        })

        if not x_desc or not y_desc:
            self.canvas.draw_idle()
            return

        xs, ys, colors = [], [], []
        for row in self._summaries:
            m = row["metrics_by_description"]
            if x_desc not in m or y_desc not in m:
                continue
            xs.append(m[x_desc])
            ys.append(m[y_desc])
            colors.append(self._color_for(row))
            self._point_names.append(row["variation"])

        if xs:
            self.ax.scatter(xs, ys, c=colors, picker=5)
            if self._selected in self._point_names:
                idx = self._point_names.index(self._selected)
                self.ax.scatter(
                    [xs[idx]], [ys[idx]], s=220, facecolors="none",
                    edgecolors="black", linewidths=2, zorder=3,
                )
            self._add_legend()
        else:
            self.ax.text(
                0.5, 0.5, "no data for this metric pair", ha="center", va="center",
                transform=self.ax.transAxes,
            )
        self.ax.set_xlabel(x_desc)
        self.ax.set_ylabel(y_desc)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _color_for(self, row):
        primary = row["primary_profile"]
        if primary is None:
            return _UNCLASSIFIED_COLOR
        return _PALETTE[self._profile_names.index(primary["profile"]) % len(_PALETTE)]

    def _add_legend(self):
        handles = [
            Patch(color=_PALETTE[i % len(_PALETTE)], label=name)
            for i, name in enumerate(self._profile_names)
        ]
        handles.append(Patch(color=_UNCLASSIFIED_COLOR, label="unclassified"))
        self.ax.legend(handles=handles, fontsize=8, loc="best")

    def _on_pick(self, event):
        if not event.ind:
            return
        self.on_select(self._point_names[event.ind[0]])

    def select_variation(self, name):
        """Highlight a point without firing on_select -- driven by a
        selection made elsewhere (the variations table), same convention
        as VariationsTable.select_variation()."""
        self._selected = name
        self._redraw()

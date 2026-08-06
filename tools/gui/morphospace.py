"""Morphospace map: scatter plot of variations by two chosen metrics
(phenotype axes), colored by primary design profile -- the only
classification signal that exists (tests are purely informative, no
absolute pass/fail). Clicking a point selects that variation the same way
a variations_table.py row does -- same on_select callback contract, no
parallel selection channel. Shift-clicking a second point (with one already
selected, from either this view or the table) fires on_shift_select(a, b)
instead -- same contract as variations_table.py's shift-click, app.py wires
both to the same Combine-dialog handler."""
from collections import defaultdict

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch, Polygon

from tools.gui import data, region

_UNCLASSIFIED_COLOR = "0.7"
_PALETTE = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown"]


class MorphospaceView(ttk.Frame):
    def __init__(self, master, on_select, on_shift_select=None):
        super().__init__(master)
        self.on_select = on_select
        self.on_shift_select = on_shift_select
        self._summaries = []
        self._point_names = []
        self._xs = []
        self._ys = []
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

        self.show_regions_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls, text="Highlight profile regions",
            variable=self.show_regions_var, command=self._redraw,
        ).pack(side="left", padx=(8, 0))

        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.canvas.mpl_connect("pick_event", self._on_pick)
        # Bound directly on the Tk widget (not via matplotlib's own event
        # system) so the more-specific "<Shift-Button-1>" pattern preempts
        # FigureCanvasTkAgg's own "<ButtonPress-1>" binding on the same
        # widget -- same precedence trick variations_table.py uses, and
        # necessary because MouseEvent.key (mpl's own modifier tracking)
        # isn't reliably populated for a shift held during a click, only
        # for actual key-press events the canvas has focus for.
        self.canvas.get_tk_widget().bind("<Shift-Button-1>", self._on_shift_click)

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
        points_by_profile = defaultdict(list)
        for row in self._summaries:
            m = row["metrics_by_description"]
            if x_desc not in m or y_desc not in m:
                continue
            xs.append(m[x_desc])
            ys.append(m[y_desc])
            colors.append(self._color_for(row))
            self._point_names.append(row["variation"])
            if row["primary_profile"]:
                points_by_profile[row["primary_profile"]["profile"]].append((m[x_desc], m[y_desc]))

        self._xs, self._ys = xs, ys
        if xs:
            if self.show_regions_var.get():
                self._draw_regions(points_by_profile)
            self.ax.scatter(xs, ys, c=colors, picker=5, zorder=2)
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

    def _draw_regions(self, points_by_profile):
        for i, profile in enumerate(self._profile_names):
            pts = points_by_profile.get(profile, [])
            color = _PALETTE[i % len(_PALETTE)]
            verts = region.blob_region(pts)
            if verts is not None:
                self.ax.add_patch(Polygon(
                    verts, closed=True, facecolor=color, edgecolor=color,
                    alpha=0.15, linewidth=1.5, zorder=0,
                ))
            elif len(set(pts)) >= 2:
                # blob_region returned None with >=2 distinct points only
                # when they're collinear -- draw a capsule between the
                # extremes instead of a polygon.
                distinct = sorted(set(pts))
                (x0, y0), (x1, y1) = distinct[0], distinct[-1]
                self.ax.plot(
                    [x0, x1], [y0, y1], color=color, linewidth=8, alpha=0.15,
                    solid_capstyle="round", zorder=0,
                )

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

    def _on_shift_click(self, event):
        if self.on_shift_select is None or self._selected is None or not self._point_names:
            return None
        idx = self._nearest_point_index(event.x, event.y)
        if idx is None:
            return None
        b = self._point_names[idx]
        if b == self._selected:
            return None
        self.on_shift_select(self._selected, b)
        return "break"

    def _nearest_point_index(self, tk_x, tk_y, max_px=15):
        """Index of the plotted point closest to a Tk-widget-local pixel
        position, within max_px, or None -- manual hit-testing since this
        bypasses matplotlib's own picker (see the <Shift-Button-1> bind
        above)."""
        if not self._xs:
            return None
        # Tk's y grows downward from the widget's top-left; matplotlib's
        # display coordinates grow upward from the figure's bottom-left --
        # same flip FigureCanvasTkAgg itself does for its own button events.
        target = (tk_x, self.figure.bbox.height - tk_y)
        best_idx, best_dist = None, None
        for i, point in enumerate(zip(self._xs, self._ys)):
            disp = self.ax.transData.transform(point)
            dist = ((disp[0] - target[0]) ** 2 + (disp[1] - target[1]) ** 2) ** 0.5
            if best_dist is None or dist < best_dist:
                best_idx, best_dist = i, dist
        return best_idx if best_dist is not None and best_dist <= max_px else None

    def select_variation(self, name):
        """Highlight a point without firing on_select -- driven by a
        selection made elsewhere (the variations table), same convention
        as VariationsTable.select_variation()."""
        self._selected = name
        self._redraw()

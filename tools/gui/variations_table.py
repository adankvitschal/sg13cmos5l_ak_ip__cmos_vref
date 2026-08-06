"""Top-level table: one row per circuit variation (not per test/metric --
see variation_detail.py for that), with its design-profile classification
(the only pass/fail-like signal -- tests themselves are purely
informative, no absolute spec). Selecting a row drives variation_detail.py.
Shift-clicking a second row (with a row already selected) fires
on_shift_select(a, b) instead of changing the selection -- app.py uses that
to open the Combine dialog pre-filled with both, a shortcut for the same
thing the Combine... toolbar button does one field at a time."""
import tkinter as tk
from tkinter import ttk

COLUMNS = ("variation", "block", "topology", "profile", "fom", "metrics", "created")


class VariationsTable(ttk.Frame):
    def __init__(self, master, on_select, on_shift_select=None):
        super().__init__(master)
        self.on_select = on_select
        self.on_shift_select = on_shift_select

        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", selectmode="browse")
        for col in COLUMNS:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=110, anchor="w")
        self.tree.column("variation", width=180)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("classified", foreground="#1a7f37")
        self.tree.tag_configure("unclassified", foreground="#888888")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        # Bound on the widget instance, so it's dispatched before the
        # Treeview class's own <Button-1> binding (bindtags checks the
        # instance before the class) -- letting _on_shift_click return
        # "break" to suppress the normal selection-change behavior.
        self.tree.bind("<Shift-Button-1>", self._on_shift_click)

        self._sort_state = {}

    def set_rows(self, summaries):
        self.tree.delete(*self.tree.get_children())
        for s in summaries:
            primary = s["primary_profile"]
            if primary is None:
                tag, profile_text, fom_text = "unclassified", "unclassified", ""
            elif primary["fom_error"]:
                tag, profile_text, fom_text = "classified", primary["profile"], primary["fom_error"]
            else:
                tag = "classified"
                profile_text = primary["profile"]
                fom_text = "" if primary["fom"] is None else f"{primary['fom']:.4g}"
            values = (
                s["variation"], s["block"], s["topology"], profile_text, fom_text,
                s["n_total"], s["created"],
            )
            self.tree.insert("", "end", values=values, tags=(tag,))

    def _sort_by(self, col):
        idx = COLUMNS.index(col)
        reverse = self._sort_state.get(col, False)
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort(key=lambda t: t[0], reverse=reverse)
        for pos, (_, k) in enumerate(items):
            self.tree.move(k, "", pos)
        self._sort_state[col] = not reverse

    def _on_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        variation = self.tree.set(selection[0], "variation")
        self.on_select(variation)

    def _on_shift_click(self, event):
        if self.on_shift_select is None:
            return None
        current = self.tree.selection()
        row = self.tree.identify_row(event.y)
        if not current or not row:
            return None
        a = self.tree.set(current[0], "variation")
        b = self.tree.set(row, "variation")
        if a == b:
            return None
        self.on_shift_select(a, b)
        return "break"

    def select_variation(self, name):
        """Programmatically select a row (e.g. driven by a morphospace point
        click) without re-firing on_select -- the caller already knows."""
        for item in self.tree.get_children(""):
            if self.tree.set(item, "variation") == name:
                self.tree.selection_set(item)
                self.tree.see(item)
                return

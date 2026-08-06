"""Modal dialogs for the Generate/Combine toolbar actions in app.py. Each
ask_*() blocks (grab_set + wait_window) until the user confirms or cancels,
returning a plain tuple of the collected values or None on cancel -- app.py
turns that into a mutate_variations.py argv and hands it to RunTrigger."""
import tkinter as tk
from tkinter import ttk


def _center_on_parent(win, parent):
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_height()) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def ask_generate_params(parent, base_variation):
    """(n, pct) or None if cancelled."""
    result = {}
    win = tk.Toplevel(parent)
    win.title("Generate variations")
    win.resizable(False, False)
    win.transient(parent)

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)

    ttk.Label(body, text=f"Base variation: {base_variation}").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

    ttk.Label(body, text="Count (N):").grid(row=1, column=0, sticky="w")
    n_var = tk.IntVar(value=5)
    ttk.Spinbox(body, from_=1, to=50, textvariable=n_var, width=8).grid(row=1, column=1, sticky="w")

    ttk.Label(body, text="+/- % per parameter:").grid(row=2, column=0, sticky="w", pady=(4, 0))
    pct_var = tk.DoubleVar(value=10.0)
    ttk.Entry(body, textvariable=pct_var, width=8).grid(row=2, column=1, sticky="w", pady=(4, 0))

    def on_ok():
        result["value"] = (n_var.get(), pct_var.get())
        win.destroy()

    def on_cancel():
        win.destroy()

    buttons = ttk.Frame(body)
    buttons.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="e")
    ttk.Button(buttons, text="Cancel", command=on_cancel).pack(side="right")
    ttk.Button(buttons, text="Generate", command=on_ok).pack(side="right", padx=(0, 8))

    win.protocol("WM_DELETE_WINDOW", on_cancel)
    _center_on_parent(win, parent)
    win.grab_set()
    win.wait_window()
    return result.get("value")


def ask_combine_params(parent, variation_names, default_a=None, default_b=None):
    """(variation_a, variation_b, n, mode, pct) or None if cancelled."""
    if len(variation_names) < 2:
        return None
    result = {}
    win = tk.Toplevel(parent)
    win.title("Combine variations")
    win.resizable(False, False)
    win.transient(parent)

    body = ttk.Frame(win, padding=12)
    body.pack(fill="both", expand=True)

    a_var = tk.StringVar(value=default_a if default_a in variation_names else variation_names[0])
    if default_b in variation_names and default_b != a_var.get():
        b_default = default_b
    else:
        b_default = next((v for v in variation_names if v != a_var.get()), variation_names[0])
    b_var = tk.StringVar(value=b_default)

    ttk.Label(body, text="Parent A:").grid(row=0, column=0, sticky="w")
    ttk.Combobox(body, textvariable=a_var, values=variation_names, state="readonly", width=28).grid(row=0, column=1, sticky="w")

    ttk.Label(body, text="Parent B:").grid(row=1, column=0, sticky="w", pady=(4, 0))
    ttk.Combobox(body, textvariable=b_var, values=variation_names, state="readonly", width=28).grid(row=1, column=1, sticky="w", pady=(4, 0))

    ttk.Label(body, text="Count (N):").grid(row=2, column=0, sticky="w", pady=(8, 0))
    n_var = tk.IntVar(value=5)
    ttk.Spinbox(body, from_=1, to=50, textvariable=n_var, width=8).grid(row=2, column=1, sticky="w", pady=(8, 0))

    mode_var = tk.StringVar(value="pick")
    pct_var = tk.DoubleVar(value=10.0)

    ttk.Label(body, text="Mode:").grid(row=3, column=0, sticky="w", pady=(8, 0))
    mode_frame = ttk.Frame(body)
    mode_frame.grid(row=3, column=1, sticky="w", pady=(8, 0))
    pct_entry = ttk.Entry(body, textvariable=pct_var, width=8, state="disabled")

    def on_mode_change():
        pct_entry.configure(state="normal" if mode_var.get() == "average" else "disabled")

    ttk.Radiobutton(mode_frame, text="pick", variable=mode_var, value="pick", command=on_mode_change).pack(side="left")
    ttk.Radiobutton(mode_frame, text="average", variable=mode_var, value="average", command=on_mode_change).pack(side="left", padx=(8, 0))

    ttk.Label(body, text="+/- % jitter (average only):").grid(row=4, column=0, sticky="w", pady=(4, 0))
    pct_entry.grid(row=4, column=1, sticky="w", pady=(4, 0))

    def on_ok():
        if a_var.get() == b_var.get():
            return
        result["value"] = (a_var.get(), b_var.get(), n_var.get(), mode_var.get(), pct_var.get())
        win.destroy()

    def on_cancel():
        win.destroy()

    buttons = ttk.Frame(body)
    buttons.grid(row=5, column=0, columnspan=2, pady=(12, 0), sticky="e")
    ttk.Button(buttons, text="Cancel", command=on_cancel).pack(side="right")
    ttk.Button(buttons, text="Combine", command=on_ok).pack(side="right", padx=(0, 8))

    win.protocol("WM_DELETE_WINDOW", on_cancel)
    _center_on_parent(win, parent)
    win.grab_set()
    win.wait_window()
    return result.get("value")

# Educational, consent-based key event recorder for Kali/Linux.
# Logs only keys typed while THIS WINDOW has focus. Do not use for surveillance.

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
import csv

class KeyEventLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Key Event Logger (Consent-based)")
        self.root.geometry("520x300")

        self.logging_enabled = False
        self.log_file = None
        self.csv_writer = None
        self.current_log_path = None

        self.status_var = tk.StringVar(value="Logging: OFF")
        self.info_var = tk.StringVar(value="Press 'Start Logging' and type here. Only keys in this window are recorded.")

        container = ttk.Frame(root, padding=16)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Key Event Logger (In-App Only)", font=("DejaVu Sans", 14, "bold"))
        title.pack(pady=(0, 8))

        self.status_lbl = ttk.Label(container, textvariable=self.status_var)
        self.status_lbl.pack(pady=(0, 8))

        self.toggle_btn = ttk.Button(container, text="Start Logging", command=self.toggle_logging)
        self.toggle_btn.pack(pady=(0, 8))

        self.text = tk.Text(container, height=8, wrap="word")
        self.text.insert("1.0", "Click inside this box and type. Special keys like Shift, Ctrl, arrows are captured too.\n")
        self.text.pack(fill="both", expand=True, pady=(8, 8))

        info = ttk.Label(container, textvariable=self.info_var, wraplength=480)
        info.pack()

        self.text.bind("<KeyPress>", self.on_key_press)
        self.text.bind("<KeyRelease>", self.on_key_release)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        Path("logs").mkdir(exist_ok=True)

    def toggle_logging(self):
        if not self.logging_enabled:
            self.start_logging()
        else:
            self.stop_logging()

    def start_logging(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.current_log_path = Path("logs") / f"{date_str}_keylog.csv"
        new_file = not self.current_log_path.exists()

        self.log_file = open(self.current_log_path, "a", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.log_file)

        if new_file:
            self.csv_writer.writerow(["timestamp", "event", "key", "keysym", "keycode"])

        self.logging_enabled = True
        self.status_var.set(f"Logging: ON → {self.current_log_path.name}")
        self.toggle_btn.config(text="Stop Logging")

    def stop_logging(self):
        self.logging_enabled = False
        self.status_var.set("Logging: OFF")
        self.toggle_btn.config(text="Start Logging")
        if self.log_file:
            self.log_file.flush()
            self.log_file.close()
            self.log_file = None
            self.csv_writer = None

    def record(self, event_type, e: tk.Event):
        if not self.logging_enabled or self.csv_writer is None:
            return
        ts = datetime.now().isoformat(timespec="milliseconds")
        key = e.char if e.char else ""
        keysym = getattr(e, "keysym", "")
        keycode = getattr(e, "keycode", "")
        self.csv_writer.writerow([ts, event_type, key, keysym, keycode])
        self.status_var.set(f"Logging: ON → {self.current_log_path.name} | Last: {event_type} {keysym or key!r}")

    def on_key_press(self, e): self.record("press", e)
    def on_key_release(self, e): self.record("release", e)

    def on_close(self):
        if self.logging_enabled:
            if not messagebox.askyesno("Exit", "Logging is ON. Stop and exit?"):
                return
            self.stop_logging()
        self.root.destroy()

def main():
    root = tk.Tk()
    try:
        root.call("tk", "scaling", 1.25)
    except Exception:
        pass
    KeyEventLoggerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

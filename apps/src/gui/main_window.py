"""Desktop assembly and execution controls; all methods run on the Tk thread."""

from dataclasses import replace
import math
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from gui.config_panel import ConfigPanel
from gui.log_panel import LogPanel
from gui.thread_worker import WorkerController


class MainWindow(ctk.CTk):
    def __init__(self, *, server_url="http://127.0.0.1:8188", messages=messagebox,
                 controller_factory=WorkerController, panel_options=None):
        ctk.set_appearance_mode("dark")
        super().__init__()
        self.title("ComfyUI Image Generator")
        self.geometry("1180x760")
        self.minsize(900, 540)
        self.messages = messages
        self._closing = False
        self._run_id = None
        self._locked = None
        self._sync_id = None
        self.state_text = ctk.StringVar(master=self, value="Ready")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.feedback = LogPanel(self)
        self.feedback.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.controller = controller_factory(self, self._on_event, on_error=self._on_error)
        self.configuration = ConfigPanel(
            self, request_catalog=self.controller.request_catalog, server_url=server_url,
            messages=messages, **(panel_options or {}))
        self.configuration.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        destination = Path(__file__).resolve().parents[3] / "assets" / "generated_images"
        self.configuration.draft.destination = str(destination)
        self.configuration.paths["destination"].set(str(destination))
        controls = ctk.CTkFrame(self)
        controls.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        controls.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(controls, textvariable=self.state_text).grid(row=0, column=0, sticky="w", padx=12)
        self.generate_button = ctk.CTkButton(controls, text="Generate", command=self.generate)
        self.generate_button.grid(row=0, column=1, padx=8, pady=8)
        self.stop_button = ctk.CTkButton(controls, text="Stop", command=self.stop)
        self.stop_button.grid(row=0, column=2, padx=8, pady=8)
        self.deadline_minutes = ctk.StringVar(master=self, value="30")
        ctk.CTkLabel(controls, text="Scene deadline (minutes)").grid(row=1, column=0, sticky="e", padx=8)
        self.deadline_entry = ctk.CTkEntry(controls, textvariable=self.deadline_minutes)
        self.deadline_entry.grid(row=1, column=1, padx=8, pady=8)
        self.protocol("WM_DELETE_WINDOW", self.request_close)
        self.configuration.refresh_catalog()
        self._sync_controls()

    def _sync_controls(self):
        locked = self._closing or self.controller.busy or self.state_text.get() == "Validating"
        if locked != self._locked:
            self.configuration.set_enabled(not locked)
            self.generate_button.configure(state="disabled" if locked else "normal")
            self.deadline_entry.configure(state="disabled" if locked else "normal")
            self._locked = locked
        can_stop = (self.controller.busy and not self._closing
                    and self.state_text.get() in ("Validating", "Running"))
        self.stop_button.configure(state="normal" if can_stop else "disabled")
        # Terminal delivery can precede worker exit. Re-enable only after busy clears.
        if self._sync_id is not None:
            self.after_cancel(self._sync_id)
        self._sync_id = self.after(50, self._sync_controls)

    def generate(self):
        if self._closing or self.controller.busy or self.state_text.get() == "Validating":
            return
        self.state_text.set("Validating")
        self._sync_controls()
        try:
            try:
                seconds = float(self.deadline_minutes.get()) * 60
                if not math.isfinite(seconds) or seconds <= 0:
                    raise ValueError
            except ValueError as error:
                raise ValueError("Scene deadline: enter finite minutes greater than zero") from error
            config = replace(self.configuration.snapshot(), scene_deadline=seconds)
            run_id = self.controller.start(config)
        except Exception as error:
            self._on_error(f"Cannot start generation: {error}. Check configuration and server, then retry.")
            self._sync_controls()
            return
        if run_id is None:
            self.state_text.set("Ready")
        else:
            self._run_id = run_id
            self.feedback.start_run(run_id, len(config.scenes))
        self._sync_controls()

    def _on_event(self, event):
        if event.run_id != self._run_id:
            return
        self.feedback.on_event(event)
        if event.kind == "terminal":
            self.state_text.set(event.data["result"].status.capitalize())
        elif self.state_text.get() != "Stopping":
            if event.kind == "state":
                self.state_text.set("Validating")
            elif event.kind in ("scene_started", "submitted", "progress", "saving", "scene_saved"):
                self.state_text.set("Running")
        self._sync_controls()

    def _on_error(self, message):
        self.state_text.set("Failed")
        self.feedback.show_error(message)

    def stop(self):
        if self.controller.stop():
            self.state_text.set("Stopping")
            self.feedback.show_stopping()
            self._sync_controls()

    def request_close(self):
        if self._closing:
            return
        if self.controller.busy and not self.messages.askyesno(
                "Stop and close?", "Stop after the current scene and close when saving finishes? "
                "Choose No to keep the window open.", parent=self):
            return
        self._closing = True
        if self.controller.busy:
            self.stop()
        self._sync_controls()
        self.controller.close(self._finish_close)

    def _finish_close(self):
        if self._sync_id is not None:
            self.after_cancel(self._sync_id)
            self._sync_id = None
        # This root owns its interpreter and both workers have exited. Cancel
        # pending CTk timers without deleting commands owned by child widgets;
        # their destroy methods still own command cleanup.
        for timer in self.after_info():
            self.tk.call("after", "cancel", timer)
        self.destroy()


def launch():
    MainWindow().mainloop()

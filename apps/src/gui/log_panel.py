"""Tk-thread feedback view; the host owns worker and window lifecycle."""

from collections import deque
from datetime import datetime
import math
from threading import get_ident

import customtkinter as ctk

from comfy_generator.models import GenerationEvent


class Feedback:
    """Bounded presentation state, independent of widgets and network I/O."""

    def __init__(self, clock=None):
        self.clock = clock or (lambda: datetime.now().strftime("%H:%M:%S"))
        self.lines = deque(maxlen=1999)  # Reserve one displayed line for the notice.
        self.discarded = 0
        self.run_id = None
        self.total = self.saved = 0
        self.scene = self.prompt = self.seed = self.timestamp = None
        self.stage = "Ready"
        self.fraction = None
        self.summary = ""
        self.terminal = False

    def start(self, run_id, total):
        self.run_id, self.total, self.saved = run_id, total, 0
        self.scene = self.prompt = self.seed = self.timestamp = None
        self.fraction = None
        self.stage, self.terminal = "Validating", False
        # The last terminal summary survives both log eviction and a new start.
        self.log("Batch started")

    def log(self, message):
        fields = (f"[{self.clock()}] scene={self.scene if self.scene is not None else '-'} "
                  f"timestamp={self.timestamp or '-'} stage={self.stage} "
                  f"seed={self.seed if self.seed is not None else '-'} | ")
        for line in str(message).splitlines() or [""]:
            if len(self.lines) == self.lines.maxlen:
                self.discarded += 1
            self.lines.append(fields + line)

    @property
    def text(self):
        notice = f"[Log buffer: {self.discarded} oldest lines discarded]\n" if self.discarded else ""
        return notice + "\n".join(self.lines)

    @property
    def batch_fraction(self):
        return self.saved / self.total if self.total else 0

    def stopping(self):
        if self.run_id and not self.terminal and self.stage != "Stopping":
            self.stage = "Stopping"
            self.log("Stop requested; waiting for the current scene")

    def accept(self, event: GenerationEvent):
        if event.run_id != self.run_id or self.terminal:
            return False
        data, kind = event.data, event.kind
        if kind == "scene_started":
            self.scene, self.timestamp, self.seed = event.scene_index, data["timestamp"], data["seed"]
            self.prompt, self.fraction, self.stage = None, None, "Preparing"
            self.log("Scene started")
        elif kind == "submitted":
            self.prompt, self.fraction, self.stage = event.prompt_id, None, "Queueing"
            self.log("Prompt submitted")
        elif kind == "progress":
            value, maximum = data.get("value"), data.get("max")
            valid = (self.prompt is not None and event.prompt_id == self.prompt
                     and event.scene_index == self.scene
                     and type(value) in (int, float) and type(maximum) in (int, float)
                     and math.isfinite(value) and math.isfinite(maximum)
                     and maximum > 0 and 0 <= value <= maximum)
            self.fraction = value / maximum if valid else None
            self.stage = "Generating"
            self.log(f"Sampler {value}/{maximum}" if valid else "Sampler activity; fraction unavailable")
        elif kind == "saving":
            self.stage, self.fraction = "Downloading", None
            self.log("Saving image files")
        elif kind == "scene_saved":
            self.saved = data["saved_scenes"]
            self.stage, self.fraction = "Saved", None
            self.log(f"Scene fully saved; {self.saved}/{self.total} scenes")
        elif kind == "state":
            self.stage = data["state"].capitalize()
            self.log(self.stage)
        elif kind == "log":
            self.log(data.get("message", ""))
        elif kind == "terminal":
            result = data["result"]
            self.terminal, self.fraction = True, None
            self.total, self.saved = result.total, result.saved_scenes
            self.stage = result.status.capitalize()
            self.summary = (f"{self.stage}: {result.saved_scenes}/{result.total} scenes saved; "
                            f"{result.total - result.saved_scenes} pending; "
                            f"{result.saved_files} files saved. Destination: "
                            f"{result.output_dir if result.output_dir is not None else 'Not created'}")
            if result.error:
                error = result.error
                self.log(f"Scene {error.scene_index}, {error.stage}: {error.reason} "
                         f"Action: {error.suggested_action}")
            self.log(self.summary)
        return True


class LogPanel(ctk.CTkFrame):
    """Call start_run before delivering events; all public calls require Tk's thread.

    Bind on_event to WorkerController's delivery callback. The host calls
    show_stopping only when controller.stop() acknowledges the first request.
    """

    def __init__(self, master, *, clock=None, **kwargs):
        super().__init__(master, **kwargs)
        self._owner = get_ident()
        self.feedback = Feedback(clock)
        self._animating = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.scene_label = ctk.CTkLabel(self, text="Ready")
        self.scene_bar = ctk.CTkProgressBar(self)
        self.batch_label = ctk.CTkLabel(self, text="Saved scenes: 0/0")
        self.batch_bar = ctk.CTkProgressBar(self)
        self.terminal_text = ctk.CTkTextbox(self, state="disabled", wrap="none", undo=False)
        self.summary_text = ctk.CTkTextbox(self, state="disabled", height=80, wrap="word", undo=False)
        for row, widget in enumerate((self.scene_label, self.scene_bar, self.batch_label,
                                      self.batch_bar, self.terminal_text, self.summary_text)):
            widget.grid(row=row, column=0, sticky="nsew", padx=8, pady=4)
        self.scene_bar.set(0)
        self.batch_bar.set(0)

    def _check_thread(self):
        if get_ident() != self._owner:
            raise RuntimeError("Feedback widgets must be updated on the Tk thread")

    def start_run(self, run_id, total):
        self._check_thread()
        self.feedback.start(run_id, total)
        self._render()

    def on_event(self, event):
        self._check_thread()
        if self.feedback.accept(event):
            self._render()

    def show_stopping(self):
        self._check_thread()
        self.feedback.stopping()
        self._render()

    def show_error(self, message):
        """Report a worker fault without fabricating a terminal RunResult."""
        self._check_thread()
        self.feedback.stage = "Failed"
        self.feedback.fraction = None
        self.feedback.log(message)
        self._render()

    @staticmethod
    def _replace(widget, text):
        widget.configure(state="normal")
        try:
            widget.delete("1.0", "end")
            widget.insert("1.0", text)
        finally:
            widget.configure(state="disabled")

    def _render(self):
        state = self.feedback
        fraction = state.fraction
        active = state.stage in ("Validating", "Preparing", "Queueing", "Generating", "Downloading", "Stopping")
        animate = fraction is None and active
        if self._animating and not animate:
            self.scene_bar.stop()
        self.scene_bar.configure(mode="indeterminate" if animate else "determinate")
        if animate and not self._animating:
            self.scene_bar.start()
        elif not animate:
            self.scene_bar.set(fraction if fraction is not None else 0)
        self._animating = animate
        suffix = f" — sampler {fraction:.0%}" if fraction is not None else ""
        self.scene_label.configure(text=state.stage + suffix)
        self.batch_label.configure(text=f"Saved scenes: {state.saved}/{state.total}")
        self.batch_bar.set(state.batch_fraction)
        # Keep a reader's scroll position; follow new messages only at the bottom.
        top, bottom = self.terminal_text.yview()
        left = self.terminal_text.xview()[0]
        self._replace(self.terminal_text, state.text)
        if bottom >= 0.999:
            self.terminal_text.yview_moveto(1)
        else:
            self.terminal_text.yview_moveto(top)
        # A long final path must not pull the viewport past the log's field names.
        self.terminal_text.xview_moveto(left)
        self._replace(self.summary_text, state.summary)

    def destroy(self):
        self.scene_bar.stop()
        super().destroy()

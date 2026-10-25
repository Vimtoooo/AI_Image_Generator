"""Configuration controls and a Tk-free draft; catalog I/O belongs to T09."""

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from comfy_generator.models import GenerationConfig, NodeMapping
from comfy_generator.payload_mgr import (
    AmbiguousWorkflowError, GenerationCatalog, ParameterValidationError,
    PayloadManager, WorkflowError, detect_node_mapping, parse_workflow_json,
    validate_node_mapping,
)
from utils.formatting_utils import parse_script


PRESETS = {"16:9": (1024, 576), "9:16": (576, 1024), "1:1": (512, 512)}
ROLES = {"sampler": "KSampler", "checkpoint": "CheckpointLoaderSimple",
         "latent": "EmptyLatentImage", "positive": "CLIPTextEncode",
         "negative": "CLIPTextEncode", "decode": "VAEDecode", "save": "SaveImage"}
NUMBERS = ("width", "height", "steps", "cfg", "seed")
CHOICES = ("checkpoint", "sampler", "scheduler")
PROMPTS = ("positive_prompt", "negative_prompt")


class ConfigurationDraft:
    """Own file selections and defaults without network calls or Tk references."""

    def __init__(self):
        self.script_path = self.workflow_path = self.destination = ""
        self.scenes = ()
        self.workflow = None
        self.mapping = None
        self.values = dict.fromkeys(NUMBERS + CHOICES + PROMPTS, "")
        self.prompt_baselines = dict.fromkeys(PROMPTS, "")

    def load_script(self, path):
        if not path:
            return
        scenes = parse_script(Path(path).read_text(encoding="utf-8-sig"))
        self.scenes, self.script_path = scenes, str(path)

    @staticmethod
    def defaults(workflow, mapping):
        validate_node_mapping(workflow, mapping)
        sampler = workflow[mapping.sampler]["inputs"]
        latent = workflow[mapping.latent]["inputs"]
        try:
            values = {name: str(sampler[name]) for name in ("steps", "cfg", "seed", "scheduler")}
            values.update({name: str(latent[name]) for name in ("width", "height")})
            values.update(checkpoint=workflow[mapping.checkpoint]["inputs"]["ckpt_name"],
                          sampler=sampler["sampler_name"],
                          positive_prompt=workflow[mapping.positive]["inputs"]["text"],
                          negative_prompt=workflow[mapping.negative]["inputs"]["text"])
            if any(not isinstance(value, str) for value in values.values()):
                raise ValueError("Expected text for workflow choices and prompts")
            return values
        except (KeyError, TypeError, ValueError) as exc:
            raise WorkflowError(f"Workflow generation fields are incomplete: {exc}") from exc

    def load_workflow(self, path):
        if not path:
            return
        graph = parse_workflow_json(Path(path).read_text(encoding="utf-8-sig"))
        try:
            mapping = detect_node_mapping(graph)
        except AmbiguousWorkflowError:
            mapping = None
        values = self.defaults(graph, mapping) if mapping else dict.fromkeys(self.values, "")
        self.workflow, self.mapping, self.workflow_path = graph, mapping, str(path)
        self.values = values
        self.prompt_baselines = {name: values[name] for name in PROMPTS}

    def select_mapping(self, mapping):
        values = self.defaults(self.workflow, mapping)
        self.mapping, self.values = mapping, values
        self.prompt_baselines = {name: values[name] for name in PROMPTS}

    def reset(self):
        if self.mapping:
            self.select_mapping(self.mapping)

    def preset(self, name):
        if name == "Custom":
            return
        width, height = PRESETS[name]
        self.values.update(width=str(width), height=str(height))

    def load_prompt(self, name, path, confirm):
        if not path:
            return
        text = Path(path).read_text(encoding="utf-8-sig")
        if self.values[name] != self.prompt_baselines[name] and not confirm():
            return
        self.values[name] = self.prompt_baselines[name] = text

    def snapshot(self, catalog, server_url):
        if not self.scenes:
            raise ValueError("Script: select a valid timestamped TXT script")
        if self.mapping is None:
            raise WorkflowError("Workflow: select an API workflow and explicit node IDs by role")
        if not self.destination or not Path(self.destination).is_dir():
            raise ValueError("Destination: select an existing directory")
        values = {name: self.values[name] for name in CHOICES}
        for name in NUMBERS:
            try:
                values[name] = (float if name == "cfg" else int)(self.values[name])
            except (ValueError, TypeError, OverflowError) as exc:
                raise ParameterValidationError(name, "enter a valid number" if name == "cfg" else "enter an integer") from exc
        manager = PayloadManager(self.workflow, self.mapping).apply_parameters(catalog, **values)
        return GenerationConfig(
            scenes=self.scenes, workflow=manager.current_payload, node_mapping=self.mapping,
            server_url=server_url, destination=Path(self.destination),
            **{name: self.values[name] for name in PROMPTS},
            **{name: values[name] for name in NUMBERS + ("sampler", "scheduler")},
        )


class ConfigPanel(ctk.CTkScrollableFrame):
    """UI-thread-only panel. request_catalog(id, url, deliver) must return promptly.

    The adapter must deliver(id, catalog_or_none, error_or_none) on the Tk thread.
    It owns I/O/timeouts and marshalling; this panel ignores obsolete responses.
    """

    def __init__(self, master, *, request_catalog=None, server_url="http://127.0.0.1:8188",
                 dialogs=filedialog, messages=messagebox, **kwargs):
        super().__init__(master, **kwargs)
        self.draft = ConfigurationDraft()
        self.request_catalog = request_catalog
        self.server_url = server_url
        self.dialogs, self.messages = dialogs, messages
        self.catalog = None
        self._request_id = 0
        self._enabled = True
        self._closed = False
        self._controls = []
        self.variables = {name: ctk.StringVar(master=self, value="") for name in NUMBERS + CHOICES}
        self.paths = {name: ctk.StringVar(master=self, value="Not selected")
                      for name in ("script_path", "workflow_path", "destination")}
        self.mapping_vars = {role: ctk.StringVar(master=self, value="") for role in ROLES}
        self.menus, self.mapping_menus, self.prompt_boxes = {}, {}, {}
        self.columnconfigure(1, weight=1)
        row = 0
        for title, name, command in (("Script TXT", "script_path", self.choose_script),
                                     ("API workflow JSON", "workflow_path", self.choose_workflow),
                                     ("Destination", "destination", self.choose_destination)):
            self._button(title, command, row)
            ctk.CTkLabel(self, textvariable=self.paths[name], anchor="w", wraplength=340).grid(
                row=row, column=1, sticky="ew", padx=8, pady=4)
            row += 1
        self.status = ctk.StringVar(master=self, value="Catalog unavailable; refresh before generating")
        self._button("Refresh catalog", self.refresh_catalog, row)
        ctk.CTkLabel(self, textvariable=self.status, wraplength=340).grid(row=row, column=1, sticky="ew")
        row += 1
        for role in ROLES:
            self._field_label(f"{role.title()} node ID", row)
            menu = ctk.CTkOptionMenu(self, variable=self.mapping_vars[role], values=[""])
            self.mapping_menus[role] = menu
            self._control(menu, row)
            row += 1
        self._button("Apply node mapping", self.apply_mapping, row)
        row += 1
        for name in CHOICES:
            self._field_label(name.title(), row)
            menu = ctk.CTkOptionMenu(self, variable=self.variables[name], values=[""])
            self.menus[name] = menu
            self._control(menu, row)
            row += 1
        self.aspect = ctk.StringVar(master=self, value="Custom")
        self._field_label("Aspect ratio", row)
        self._control(ctk.CTkOptionMenu(self, variable=self.aspect, values=[*PRESETS, "Custom"],
                                       command=self.set_preset), row)
        row += 1
        for name in NUMBERS:
            self._field_label("Seed (-1 = random)" if name == "seed" else name.title(), row)
            self._control(ctk.CTkEntry(self, textvariable=self.variables[name]), row)
            row += 1
        for name in PROMPTS:
            self._button("Load " + name.replace("_", " ") + " TXT",
                         lambda key=name: self.choose_prompt(key), row)
            box = ctk.CTkTextbox(self, height=100, wrap="word")
            self.prompt_boxes[name] = box
            self._control(box, row)
            row += 1
        self._button("Reset", self.reset, row)

    def _field_label(self, text, row):
        ctk.CTkLabel(self, text=text, anchor="w").grid(row=row, column=0, padx=8, pady=4, sticky="w")

    def _control(self, widget, row):
        widget.grid(row=row, column=1, padx=8, pady=4, sticky="ew")
        self._controls.append(widget)

    def _button(self, text, command, row):
        button = ctk.CTkButton(self, text=text, command=lambda: self._act(command))
        button.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        self._controls.append(button)

    def _act(self, command):
        if not self._enabled or self._closed:
            return
        try:
            command()
        except (OSError, ValueError) as exc:
            self.messages.showerror("Configuration", str(exc), parent=self)

    def _pull(self):
        self.draft.values.update({name: var.get() for name, var in self.variables.items()})
        self.draft.values.update({name: box.get("1.0", "end-1c") for name, box in self.prompt_boxes.items()})

    def _render(self):
        for name, var in self.paths.items():
            var.set(getattr(self.draft, name) or "Not selected")
        for name, var in self.variables.items():
            var.set(self.draft.values[name])
        for name, box in self.prompt_boxes.items():
            box.delete("1.0", "end")
            box.insert("1.0", self.draft.values[name])
        for role, menu in self.mapping_menus.items():
            ids = [key for key, node in (self.draft.workflow or {}).items() if node["class_type"] == ROLES[role]]
            menu.configure(values=ids or [""])
            self.mapping_vars[role].set(getattr(self.draft.mapping, role) if self.draft.mapping else "")
        self.aspect.set("Custom")

    def choose_script(self):
        self.draft.load_script(self.dialogs.askopenfilename(parent=self, filetypes=[("Script TXT", "*.txt")]))
        self.paths["script_path"].set(self.draft.script_path or "Not selected")

    def choose_workflow(self):
        path = self.dialogs.askopenfilename(parent=self, filetypes=[("API workflow", "*.json")])
        if not path:
            return
        self.draft.load_workflow(path)
        self._render()
        if self.draft.mapping is None:
            self.messages.showinfo("Node mapping", "Multiple chains: select node IDs for all seven roles, then Apply node mapping.", parent=self)

    def choose_destination(self):
        path = self.dialogs.askdirectory(parent=self, mustexist=True)
        if path:
            self.draft.destination = path
            self.paths["destination"].set(path)

    def choose_prompt(self, name):
        path = self.dialogs.askopenfilename(parent=self, filetypes=[("Prompt TXT", "*.txt")])
        if not path:
            return
        self._pull()
        self.draft.load_prompt(name, path, lambda: self.messages.askyesno(
            "Replace edited prompt?", "Replace the edited prompt with this TXT file?", parent=self))
        box = self.prompt_boxes[name]
        box.delete("1.0", "end")
        box.insert("1.0", self.draft.values[name])

    def apply_mapping(self):
        self.draft.select_mapping(NodeMapping(**{role: var.get() for role, var in self.mapping_vars.items()}))
        self._render()

    def set_preset(self, name):
        self._pull()
        self.draft.preset(name)
        for field in ("width", "height"):
            self.variables[field].set(self.draft.values[field])

    def reset(self):
        if self.draft.mapping:
            self.draft.reset()
            self._render()

    def refresh_catalog(self):
        self._request_id += 1
        self.catalog = None
        self.status.set("Catalog loading…")
        if self.request_catalog is None:
            self.receive_catalog(self._request_id, None, "Catalog service unavailable")
            return
        try:
            self.request_catalog(self._request_id, self.server_url, self.receive_catalog)
        except Exception as exc:
            self.receive_catalog(self._request_id, None, str(exc))

    def receive_catalog(self, request_id, catalog, error=None):
        if self._closed or request_id != self._request_id:
            return
        self.catalog = catalog if isinstance(catalog, GenerationCatalog) and not error else None
        self.status.set("Catalog ready" if self.catalog else f"Catalog unavailable: {error or 'refresh required'}")
        for name, attr in (("checkpoint", "checkpoints"), ("sampler", "samplers"), ("scheduler", "schedulers")):
            selected = self.variables[name].get()
            options = list(getattr(self.catalog, attr)) if self.catalog else []
            self.menus[name].configure(values=options or [""])
            self.variables[name].set(selected)

    def snapshot(self):
        if self.draft.mapping is not None and any(
            var.get() != getattr(self.draft.mapping, role)
            for role, var in self.mapping_vars.items()
        ):
            raise WorkflowError("Node IDs changed; Apply node mapping before generating")
        self._pull()
        return self.draft.snapshot(self.catalog, self.server_url)

    def set_enabled(self, enabled):
        self._enabled = enabled
        for widget in self._controls:
            widget.configure(state="normal" if enabled else "disabled")

    def destroy(self):
        self._closed = True
        super().destroy()

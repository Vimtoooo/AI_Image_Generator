"""Fictional file and real withdrawn-widget checks; no ComfyUI connection."""

import json
from unittest.mock import Mock

import customtkinter as ctk
import pytest

from comfy_generator.payload_mgr import CatalogError, WorkflowError, parse_catalog
from gui.config_panel import ConfigPanel, ConfigurationDraft, PRESETS
from test_catalog_validation import metadata
from test_workflow_mapping import chain


@pytest.fixture
def files(tmp_path):
    mapping, graph = chain()
    workflow = tmp_path / "workflow.json"
    workflow.write_text(json.dumps(graph), encoding="utf-8-sig")
    script = tmp_path / "script.txt"
    script.write_text("(00:01) A fictional lake\nSecond line\n(00:01) A tree", encoding="utf-8-sig")
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("A fictional style\n", encoding="utf-8-sig")
    return mapping, graph, workflow, script, prompt


@pytest.fixture
def draft(files, tmp_path):
    result = ConfigurationDraft()
    result.load_workflow(files[2])
    result.load_script(files[3])
    result.destination = str(tmp_path)
    return result


def test_workflow_defaults_and_detached_snapshot(draft, files):
    assert draft.values == dict(width="512", height="512", steps="20", cfg="7.0", seed="42",
                                sampler="euler", scheduler="normal", checkpoint="fictional.safetensors",
                                positive_prompt="global", negative_prompt="blur")
    draft.values.update(seed="-1", checkpoint="other.safetensors", positive_prompt="", negative_prompt="")
    data = metadata()
    data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0].append("other.safetensors")
    config = draft.snapshot(parse_catalog(data), "http://127.0.0.1:8188")
    assert config.seed == -1 and config.positive_prompt == config.negative_prompt == ""
    assert config.workflow[files[0].checkpoint]["inputs"]["ckpt_name"] == "other.safetensors"
    draft.values["seed"] = "100"
    draft.workflow[files[0].sampler]["inputs"]["seed"] = 200
    assert config.seed == -1 and config.workflow[files[0].sampler]["inputs"]["seed"] == -1
    with pytest.raises(TypeError):
        config.workflow["changed"] = {}
    assert config.scenes[0].description == "A fictional lake\nSecond line"


@pytest.mark.parametrize("preset,pair", list(PRESETS.items()))
def test_presets_and_custom(draft, preset, pair):
    draft.preset(preset)
    assert (int(draft.values["width"]), int(draft.values["height"])) == pair
    draft.preset("Custom")
    assert (int(draft.values["width"]), int(draft.values["height"])) == pair


def test_reset_preserves_selections_and_sources(draft, files):
    paths = draft.script_path, draft.workflow_path, draft.destination
    original = files[2].read_bytes()
    draft.values.update(width="1024", positive_prompt="edited", checkpoint="changed")
    draft.reset()
    assert draft.values["width"] == "512" and draft.values["positive_prompt"] == "global"
    assert (draft.script_path, draft.workflow_path, draft.destination) == paths
    assert files[2].read_bytes() == original


@pytest.mark.parametrize("name", ["positive_prompt", "negative_prompt"])
def test_prompt_confirmation_and_source_preservation(draft, files, name):
    original = files[4].read_bytes()
    draft.values[name] = "edited"
    confirm = Mock(return_value=False)
    draft.load_prompt(name, files[4], confirm)
    confirm.assert_called_once()
    assert draft.values[name] == "edited"
    draft.load_prompt(name, files[4], lambda: True)
    assert draft.values[name] == "A fictional style\n"
    assert files[4].read_bytes() == original
    draft.load_prompt(name, files[4], lambda: pytest.fail("Unedited field needs no confirmation"))


@pytest.mark.parametrize("kind,bad", [("script", "bad script"), ("workflow", "{"),
                                     ("workflow", '{"nodes": [], "links": []}')])
def test_failed_load_preserves_last_valid(draft, tmp_path, kind, bad):
    before = draft.script_path, draft.scenes, draft.workflow_path, draft.workflow, draft.values.copy()
    path = tmp_path / "bad.txt"
    path.write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError):
        getattr(draft, "load_" + kind)(path)
    assert (draft.script_path, draft.scenes, draft.workflow_path, draft.workflow, draft.values) == before


@pytest.mark.parametrize("method", ["load_script", "load_workflow"])
def test_cancel_encoding_and_missing_file_preserve(draft, tmp_path, method):
    before = draft.__dict__.copy()
    getattr(draft, method)("")
    with pytest.raises(OSError):
        getattr(draft, method)(tmp_path / "missing")
    bad = tmp_path / "bad"
    bad.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        getattr(draft, method)(bad)
    assert draft.__dict__ == before


def test_multiple_chains_require_explicit_valid_mapping(draft, files, tmp_path):
    other, graph = chain("y")
    graph.update(files[1])
    path = tmp_path / "multiple.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    draft.load_workflow(path)
    assert draft.mapping is None
    with pytest.raises(WorkflowError, match="explicit"):
        draft.snapshot(parse_catalog(metadata()), "http://localhost:8188")
    draft.select_mapping(other)
    assert draft.mapping == other
    assert len(draft.snapshot(parse_catalog(metadata()), "http://localhost:8188").workflow) == 7
    draft.workflow[other.positive]["inputs"]["clip"] = [files[0].checkpoint, 1]
    with pytest.raises(WorkflowError, match="positive.clip"):
        draft.select_mapping(other)


@pytest.mark.parametrize("field,value", [("seed", "1.5"), ("steps", ""), ("cfg", "nan"),
                                       ("width", "513"), ("height", "0"), ("sampler", "missing")])
def test_snapshot_field_errors(draft, field, value):
    draft.values[field] = value
    with pytest.raises(ValueError, match=field):
        draft.snapshot(parse_catalog(metadata()), "http://localhost:8188")


def test_snapshot_requires_catalog_script_and_destination(draft):
    with pytest.raises(CatalogError):
        draft.snapshot(None, "http://localhost:8188")
    draft.destination = ""
    with pytest.raises(ValueError, match="Destination"):
        draft.snapshot(parse_catalog(metadata()), "http://localhost:8188")
    draft.scenes = ()
    with pytest.raises(ValueError, match="Script"):
        draft.snapshot(parse_catalog(metadata()), "http://localhost:8188")


@pytest.fixture(scope="module")
def tk_root():
    root = ctk.CTk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture
def panel(tk_root):
    panel = ConfigPanel(tk_root, dialogs=Mock(), messages=Mock())
    panel.pack(fill="both", expand=True)
    yield panel
    if not panel._closed:
        panel.destroy()
    tk_root.update_idletasks()


def load_panel(panel, files, tmp_path):
    panel.dialogs.askopenfilename.side_effect = [str(files[2]), str(files[3])]
    panel.choose_workflow()
    panel.choose_script()
    panel.dialogs.askdirectory.return_value = str(tmp_path)
    panel.choose_destination()


def test_widget_defaults_cancel_reset_and_snapshot(panel, files, tmp_path):
    load_panel(panel, files, tmp_path)
    panel.variables["width"].set("2048")
    panel.prompt_boxes["positive_prompt"].insert("end", " edited")
    panel.dialogs.askopenfilename.side_effect = ["", ""]
    panel.choose_workflow()
    panel.choose_script()
    panel.dialogs.askdirectory.return_value = ""
    panel.choose_destination()
    assert panel.variables["width"].get() == "2048"
    assert panel.prompt_boxes["positive_prompt"].get("1.0", "end-1c") == "global edited"
    panel.reset()
    panel.receive_catalog(0, parse_catalog(metadata()))
    config = panel.snapshot()
    assert config.width == 512 and config.positive_prompt == "global"
    assert config.destination == tmp_path and len(config.scenes) == 2


def test_catalog_fake_service_stale_failure_and_missing_selection(panel, files, tmp_path):
    load_panel(panel, files, tmp_path)
    requests = []
    panel.request_catalog = lambda *args: requests.append(args)
    panel.refresh_catalog()
    panel.refresh_catalog()
    first, second = requests
    assert first[:2] == (1, "http://127.0.0.1:8188")
    first[2](1, parse_catalog(metadata()), None)
    assert panel.catalog is None
    data = metadata()
    data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"] = [["different"]]
    second[2](2, parse_catalog(data), None)
    assert panel.variables["checkpoint"].get() == "fictional.safetensors"
    assert panel.menus["checkpoint"].cget("values") == ["different"]
    with pytest.raises(ValueError, match="checkpoint"):
        panel.snapshot()
    panel.refresh_catalog()
    requests[-1][2](3, None, "offline")
    assert panel.catalog is None and "offline" in panel.status.get()
    with pytest.raises(CatalogError):
        panel.snapshot()


def test_widget_prompt_confirmation_and_error_reporting(panel, files, tmp_path):
    load_panel(panel, files, tmp_path)
    box = panel.prompt_boxes["positive_prompt"]
    box.insert("end", " edited")
    panel.dialogs.askopenfilename.side_effect = [str(files[4]), str(files[4]), str(tmp_path / "missing")]
    panel.messages.askyesno.return_value = False
    panel.choose_prompt("positive_prompt")
    assert box.get("1.0", "end-1c") == "global edited"
    panel.messages.askyesno.return_value = True
    panel.choose_prompt("positive_prompt")
    assert box.get("1.0", "end-1c") == "A fictional style\n"
    panel._act(panel.choose_workflow)
    panel.messages.showerror.assert_called_once()
    assert panel.paths["workflow_path"].get() == str(files[2])


def test_controls_disable_and_catalog_after_destroy(panel):
    panel.set_enabled(False)
    assert all(widget.cget("state") == "disabled" for widget in panel._controls)
    command = Mock()
    panel._act(command)
    command.assert_not_called()
    panel.set_enabled(True)
    assert all(widget.cget("state") == "normal" for widget in panel._controls)
    panel.destroy()
    panel.receive_catalog(0, parse_catalog(metadata()))
    assert panel.catalog is None


def test_catalog_missing_adapter_and_dispatch_failure(panel):
    panel.refresh_catalog()
    assert "unavailable" in panel.status.get()
    panel.request_catalog = Mock(side_effect=RuntimeError("dispatch failed"))
    panel.refresh_catalog()
    assert "dispatch failed" in panel.status.get()


def test_widget_mapping_and_presets(panel, files, tmp_path):
    other, graph = chain("y")
    graph.update(files[1])
    path = tmp_path / "multiple.json"
    path.write_text(json.dumps(graph), encoding="utf-8")
    panel.dialogs.askopenfilename.return_value = str(path)
    panel.choose_workflow()
    panel.messages.showinfo.assert_called_once()
    assert all(var.get() == "" for var in panel.mapping_vars.values())
    for role, var in panel.mapping_vars.items():
        var.set(getattr(other, role))
    panel.apply_mapping()
    assert panel.draft.mapping == other
    panel.set_preset("16:9")
    panel.set_preset("Custom")
    assert panel.variables["width"].get() == "1024" and panel.variables["height"].get() == "576"


def test_unapplied_mapping_cannot_generate(panel, files, tmp_path):
    load_panel(panel, files, tmp_path)
    panel.receive_catalog(0, parse_catalog(metadata()))
    panel.mapping_vars["save"].set("unapplied")
    with pytest.raises(WorkflowError, match="Apply node mapping"):
        panel.snapshot()
    panel._act(panel.apply_mapping)
    panel.messages.showerror.assert_called_once()
    assert panel.draft.mapping == files[0]

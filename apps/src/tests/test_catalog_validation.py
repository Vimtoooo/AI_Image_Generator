import copy
from unittest.mock import MagicMock, patch

import pytest
import requests

from comfy_generator.client import ComfyUIClient
from comfy_generator.payload_mgr import (
    CatalogError, ParameterValidationError, PayloadManager,
    parse_catalog, validate_generation_parameters,
)
from test_workflow_mapping import chain


def metadata():
    return {
        "CheckpointLoaderSimple": {"input": {"required": {"ckpt_name": [["fictional.safetensors"]]}}},
        "KSampler": {"input": {"required": {
            "sampler_name": [["euler", "heun"]], "scheduler": [["normal", "simple"]],
            "steps": ["INT", {"min": 1, "max": 100}],
            "cfg": ["FLOAT", {"min": 0, "max": 20}],
            "seed": ["INT", {"min": 0, "max": 2**64 - 1}],
        }}},
        "EmptyLatentImage": {"input": {"required": {
            "width": ["INT", {"min": 16, "max": 8192}],
            "height": ["INT", {"min": 16, "max": 8192}],
        }}},
    }


def values(**overrides):
    return dict(checkpoint="fictional.safetensors", sampler="euler", scheduler="normal",
                width=512, height=512, steps=20, cfg=8, seed=0) | overrides


def test_catalog_is_detached_and_read_only():
    source = metadata()
    catalog = parse_catalog(source)
    source["KSampler"]["input"]["required"]["sampler_name"][0].append("changed")
    assert catalog.samplers == ("euler", "heun")
    with pytest.raises(TypeError):
        catalog.limits["steps"]["max"] = 200


@pytest.mark.parametrize("data", [None, {}, [], {"KSampler": {}}, {"CheckpointLoaderSimple": None}])
def test_malformed_catalog(data):
    with pytest.raises(CatalogError):
        parse_catalog(data)


@pytest.mark.parametrize("bounds", [{"min": 100, "max": 1}, {"min": float("nan"), "max": 100},
                                    {"min": True, "max": 100}, {"min": 0}])
def test_bad_bounds(bounds):
    data = metadata()
    data["KSampler"]["input"]["required"]["steps"][1] = bounds
    with pytest.raises(CatalogError):
        parse_catalog(data)


@pytest.mark.parametrize("field,value", [
    ("checkpoint", "missing"), ("sampler", "normal"), ("scheduler", "euler"),
    ("width", 0), ("height", 513), ("width", 8), ("width", 8200),
    ("steps", 0), ("steps", 101), ("steps", True), ("steps", 1.5),
    ("cfg", -1), ("cfg", float("inf")), ("cfg", float("nan")), ("cfg", True),
    ("cfg", 21), ("seed", -2), ("seed", 2**64), ("seed", True),
])
def test_field_errors_before_mutation(field, value):
    _, graph = chain()
    manager = PayloadManager(graph)
    before = manager.current_payload
    with pytest.raises(ParameterValidationError) as exc:
        manager.apply_parameters(parse_catalog(metadata()), **values(**{field: value}))
    assert exc.value.field == field
    assert manager.current_payload == before


@pytest.mark.parametrize("cfg,seed", [(8, 0), (0, -1), (7.25, 2**64 - 1)])
def test_valid_parameters_preserve_unedited_workflow_fields(cfg, seed):
    mapping, graph = chain()
    original = copy.deepcopy(graph)
    manager = PayloadManager(graph).apply_parameters(parse_catalog(metadata()), **values(cfg=cfg, seed=seed))
    result = manager.current_payload
    assert result[mapping.sampler]["inputs"]["cfg"] == cfg
    assert result[mapping.sampler]["inputs"]["seed"] == seed
    assert result[mapping.sampler]["inputs"]["denoise"] == 1.0
    assert graph == original


def test_missing_or_empty_catalog_never_substitutes_selection():
    with pytest.raises(CatalogError):
        validate_generation_parameters(None, **values())
    data = metadata()
    data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0] = []
    with pytest.raises(ParameterValidationError, match="checkpoint"):
        validate_generation_parameters(parse_catalog(data), **values())


def response(data=None):
    result = MagicMock()
    result.__enter__.return_value = result
    result.json.return_value = metadata() if data is None else data
    result.status_code = 200
    return result


def test_catalog_request_and_cleanup_without_connection_probe():
    result = response()
    client = ComfyUIClient()
    with patch("comfy_generator.client.requests.get", return_value=result) as get:
        catalog = client.get_catalog()
    get.assert_called_once_with("http://127.0.0.1:8188/object_info", timeout=(10, 60))
    result.raise_for_status.assert_called_once()
    result.__exit__.assert_called_once()
    assert catalog.schedulers == ("normal", "simple")


@pytest.mark.parametrize("error", [requests.Timeout("offline"), requests.HTTPError("503"), ValueError("invalid JSON")])
def test_catalog_failure_is_explicit(error):
    result = response()
    if isinstance(error, requests.HTTPError):
        result.raise_for_status.side_effect = error
    else:
        result.json.side_effect = error
    with patch("comfy_generator.client.requests.get", return_value=result):
        with pytest.raises(CatalogError, match="refresh"):
            ComfyUIClient().get_catalog()
    result.__exit__.assert_called_once()


def test_connect_failure_is_explicit():
    with patch("comfy_generator.client.requests.get", side_effect=requests.ConnectionError("offline")):
        with pytest.raises(CatalogError):
            ComfyUIClient().get_catalog()


def test_legacy_sampler_names_and_owner_alias_return_values():
    client = ComfyUIClient()
    with patch("comfy_generator.client.requests.get", return_value=response()):
        assert client.check_connection()
        assert client.get_available_samplers() == ["euler", "heun"]
        assert client.get_available_sampler_names() == ["euler", "heun"]
        assert client.get_available_schedulers() == ["normal", "simple"]

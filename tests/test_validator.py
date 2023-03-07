import glob
import re

import pytest
import yaml
from schema import SchemaError

from yaml2workflow.validator import validate


@pytest.mark.parametrize("filename", glob.glob("tests/fixtures/*.yml"))
def test_validate_fixtures(filename):
    with open(filename, "r") as file:
        validate(yaml.safe_load(file))


def test_validate_invalid_id():
    with pytest.raises(SchemaError, match="Key 'id' error:\nmust be an up to 32-character ASCII string with internal dashes and underscores"):
        validate({"workflow": {"id": "id with spaces"}})


def test_validate_empty_nodes():
    with pytest.raises(SchemaError, match=re.escape("Key 'nodes' error:\nmust provide at least one node")):
        validate({"workflow": {"id": "workflow-id", "nodes": []}})


def test_validate_invalid_hex_id():
    with pytest.raises(SchemaError, match="Key 'model_version_id' error:\nmust be a 32-character hex-string"):
        validate({"workflow": {
            "id": "workflow-id",
            "nodes": [{
                "id": "node-id",
                "model": {
                    "model_id": "model-id",
                    "model_version_id": "not-a-hex-id",
                },
            }],
        }})


def test_validate_upper_hex_id():
    data = validate({"workflow": {
        "id": "workflow-id",
        "nodes": [{
            "id": "node-id",
            "model": {
                "model_id": "model-id",
                "model_version_id": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            },
        }],
    }})
    assert data["workflow"]["nodes"][0]["model"]["model_version_id"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_validate_missing_input():
    with pytest.raises(SchemaError, match="Key 'nodes' error:\nmissing input 'previous-node-id' for node 'node-id'"):
        validate({"workflow": {
            "id": "workflow-id",
            "nodes": [{
                "id": "node-id",
                "model": {
                    "model_id": "model-id",
                    "model_version_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                },
                "node_inputs": [{
                    "node_id": "previous-node-id",
                }],
            }],
        }})


def test_validate_model_has_model_version_id_and_other_model_fields():
    with pytest.raises(SchemaError, match="Key 'model' error:\nmodel should not set model_version_id and other model fields"):
        validate({"workflow": {
            "id": "workflow-id",
            "nodes": [{
                "id": "node-id",
                "model": {
                    "model_id": "model-id",
                    "model_version_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                    "description": "hello"
                },
            }],
        }})

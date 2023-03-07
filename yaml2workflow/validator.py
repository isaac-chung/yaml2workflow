from schema import And, Optional, Or, Regex, Schema, SchemaError, Use


_id_validator = And(str, lambda s: 0 < len(s) <= 32, Regex(r'^[0-9A-Za-z]+([-_][0-9A-Za-z]+)*$'),
                    error="must be an up to 32-character ASCII string with internal dashes and underscores")

_hex_id_validator = And(str, Use(str.lower), Regex(r'^[0-9a-f]{32}'),
                        error="must be a 32-character hex-string")

_str_len_validator = And(str, len, error="must be a non-empty string")


def _workflow_nodes_have_valid_dependencies(nodes):
    # Validate that all inputs to a node are declared before it.
    node_ids = set()
    for node in nodes:
        for node_input in node.get("node_inputs", []):
            if node_input["node_id"] not in node_ids:
                raise SchemaError(f"missing input '{node_input['node_id']}' for node '{node['id']}'")
        node_ids.add(node["id"])

    return True


_data_schema = Schema({
    "workflow": {
        "id": _id_validator,
        "nodes": And(
            Schema(len, error="must provide at least one node"),
            [{
                "id": _str_len_validator,  # Node IDs are not validated as IDs by the API.
                "model": Or(
                    {
                        # Pre-existing model.
                        "model_id": _id_validator,
                        Optional("model_version_id"): _hex_id_validator,
                    },
                    {
                        # Auto-created model.
                        "model_id": _id_validator,
                        "model_type_id": _id_validator,
                        Optional("description"): str,
                        Optional("output_info"): {
                            "params": dict,
                        },
                    },
                ),
                Optional("node_inputs"): And(
                    Schema(len, error="must provide at least one node input"),
                    [{
                        "node_id": _str_len_validator,
                    }],
                ),
            }],
            _workflow_nodes_have_valid_dependencies,
        ),
    },
})


def validate(data):
    return _data_schema.validate(data)

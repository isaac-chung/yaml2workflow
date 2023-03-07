from schema import And, Optional, Regex, Schema, SchemaError, Use


# Non-empty, up to 32-character ASCII strings with internal dashes and underscores.
_id_validator = And(str, lambda s: 0 < len(s) <= 32, Regex(r'^[0-9A-Za-z]+([-_][0-9A-Za-z]+)*$'))

# 32-character hex string, converted to lower-case.
_hex_id_validator = And(str, Use(str.lower), Regex(r'^[0-9a-f]{32}'))

_data_schema = Schema({
    "workflow": {
        "id": _id_validator,
        "nodes": And(len, [{
            "id": And(str, len), # Node IDs are not validated as IDs by the API.
            "model": {
                "model_id": _id_validator,
                "model_version_id": _hex_id_validator,
            },
            Optional("node_inputs"): And(len, [{
                "node_id": And(str, len),
            }]),
        }]),
    },
})

def validate(data):
    data = _data_schema.validate(data)

    # Validate that all inputs to a node are declared before it.
    node_ids = []
    for node in data["workflow"]["nodes"]:
        for node_input in node.get("node_inputs", []):
            if node_input["node_id"] not in node_ids:
                raise SchemaError(f"missing input '{node_input['node_id']}' for node '{node['id']}'")
        node_ids.append(node["id"])

    return data

import typing
import uuid
import yaml

from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
from google.protobuf.json_format import MessageToDict


def _validate_node(node):
    assert node.get('id'), 'The node ID cannot be empty. '
    assert node.get('model'), 'A node must have model filled in.'
    assert node['model'].get('model_id'), 'A node must have a model_id'


def _validate_workflow(wf):
    assert wf.get('id'), 'The workflow ID cannot be empty. '
    assert len(wf['nodes']) != 0, 'The workflow must have nodes.'


def parse(filename: str, generate_new_id: bool = False, stub: service_pb2_grpc.V2Stub = None,
          metadata=None) -> typing.List[resources_pb2.Workflow]:
    """
    Takes in a filename of a yaml file.
    Returns a list of resources_pb2.Workflow objects for PostWorkflowsRequest.
    """
    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
    except:
        raise Exception("Error in opening the yaml file.")

    ## Check the workflow level
    # The validatity of these fields will be left for the API.
    workflow = data['workflow']
    _validate_workflow(workflow)

    ## Check the workflow node level
    nodes = []
    for yml_node in workflow['nodes']:
        _validate_node(yml_node)
        node = resources_pb2.WorkflowNode(
            id=yml_node['id'],
            model=_parse_model(yml_node['model'], stub=stub, metadata=metadata)
        )
        ## Add node inputs if they exist, i.e. if these nodes do not connect directly to the input.
        if yml_node.get("node_inputs"):
            for ni in yml_node.get("node_inputs"):
                node.node_inputs.append(resources_pb2.NodeInput(node_id=ni['node_id']))
        nodes.append(node)

    workflow_id = workflow['id']
    if generate_new_id:
        workflow_id += str(uuid.uuid1())[:10]

    return [resources_pb2.Workflow(id=workflow_id, nodes=nodes)]


def _parse_model(yaml_model: typing.Dict, stub: service_pb2_grpc.V2Stub = None,
                 metadata=None) -> resources_pb2.Model:
    model_id, model_version_id = _search_model(yaml_model, stub=stub, metadata=metadata)

    return resources_pb2.Model(
        id=model_id,
        model_version=resources_pb2.ModelVersion(id=model_version_id))


def _search_model(yaml_model: typing.Dict, stub: service_pb2_grpc.V2Stub = None,
                  metadata=None) -> typing.Tuple[str, str]:
    assert stub, "Stub is required to load model by ID."
    assert metadata, "Metadata is required to load model by ID."
    model_version_id = yaml_model.get('model_version_id')
    response = stub.GetModel(service_pb2.GetModelRequest(model_id=yaml_model['model_id'], version_id=model_version_id),
                             metadata=metadata)
    if response.status.code == status_code_pb2.MODEL_DOES_NOT_EXIST:
        raise NotImplementedError("Should create new model %s" % yaml_model)

    assert response.status.code == status_code_pb2.SUCCESS, f'Invalid response {response}'

    if _is_same_model(response.model, yaml_model):
        return response.model.id, response.model.model_version.id
    else:
        if model_version_id:
            raise Exception("Model version with specific ID '%s' not found for model with ID '%s'." % (
                model_version_id, yaml_model['model_id']))
        raise NotImplementedError("Should create new model version for model %s" % yaml_model)


def _is_same_model(api_model: resources_pb2.Model, yaml_model: typing.Dict) -> bool:
    yaml_model_from_api = MessageToDict(api_model, preserving_proto_field_name=True)
    if 'id' in yaml_model_from_api:
        yaml_model_from_api['model_id'] = yaml_model_from_api['id']
    if 'model_version' in yaml_model_from_api and 'id' in yaml_model_from_api['model_version']:
        yaml_model_from_api['model_version_id'] = yaml_model_from_api['model_version']['id']

    return _is_dict_in_dict(yaml_model, yaml_model_from_api)


def _is_dict_in_dict(d1: typing.Dict, d2: typing.Dict) -> bool:
    for k, v in d1.items():
        if k not in d2:
            return False
        if isinstance(v, dict):
            if not isinstance(d2[k], dict):
                return False
            return _is_dict_in_dict(d1[k], d2[k])
        elif v != d2[k]:
            return False

    return True

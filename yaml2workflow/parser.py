import typing
import uuid

import yaml
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc


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
            id = yml_node['id'],
            model = parse_model(yml_node['model'], stub=stub, metadata=metadata)
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


def parse_model(model: typing.Dict, stub: service_pb2_grpc.V2Stub = None,
                metadata=None) -> resources_pb2.Model:
    model_id, model_version_id = search_model(model, stub=stub, metadata=metadata)

    return resources_pb2.Model(
        id=model_id,
        model_version=resources_pb2.ModelVersion(id=model_version_id))


def search_model(model: typing.Dict, stub: service_pb2_grpc.V2Stub = None,
                 metadata=None) -> typing.Tuple[str, str]:
    if 'model_id' in model and 'model_version_id' in model:
        return model['model_id'], model['model_version_id']

    if 'model_id' in model:
        assert stub, "Stub is required to load model by ID."
        assert metadata, "Metadata is required to load model by ID."
        response = stub.GetModel(service_pb2.GetModelRequest(model_id=model['model_id']), metadata=metadata)
        assert response.status.code == 10000, f'Invalid response {response}'

        return response.model.id, response.model.model_version.id

    raise Exception("Unable to search model for %s" % model)

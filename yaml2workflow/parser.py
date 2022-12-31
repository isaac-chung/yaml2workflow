import yaml
from clarifai_grpc.grpc.api import resources_pb2


def _validate_node(node):
    assert node.get('id') is not None, 'The node ID cannot be empty. '
    assert node.get('model') is not None, 'A node must have model filled in.'
    assert node['model'].get('model_id') is not None, 'A node must have a model_id'
    assert node['model'].get('model_version_id') is not None, 'A node must have a model_version_id'


def _validate_workflow(wf):
    assert wf.get('id') is not None, 'The workflow ID cannot be empty. '
    assert len(wf['nodes']) != 0, 'The workflow must have nodes.'


def parse(filename: str):
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
            model = resources_pb2.Model(
                id=yml_node['model']['model_id'], 
                model_version=resources_pb2.ModelVersion(id=yml_node['model']['model_version_id']))
        )
        ## Add node inputs if they exist, i.e. if these nodes do not connect directly to the input.
        if yml_node.get("node_inputs"):
            for ni in yml_node.get("node_inputs"):
                node.node_inputs.append(resources_pb2.NodeInput(node_id=ni['node_id']))
        nodes.append(node)

    workflows=[resources_pb2.Workflow(id=workflow['id'], nodes=nodes)]
    return workflows

import typing
import uuid
import yaml

from clarifai_grpc.grpc.api import resources_pb2, service_pb2_grpc
from yaml2workflow.parser import model
from yaml2workflow.validator import validate


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

    data = validate(data)
    workflow = data['workflow']

    ## Convert nodes to resources_pb2.WorkflowNodes.
    nodes = []
    for yml_node in workflow['nodes']:
        node = resources_pb2.WorkflowNode(
            id=yml_node['id'],
            model=model._parse(yml_node['model'], stub=stub, metadata=metadata)
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

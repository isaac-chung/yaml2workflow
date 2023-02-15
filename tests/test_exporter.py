import glob
import os
import pytest
import yaml

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from yaml2workflow.exporter import Exporter


channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)
metadata = (("authorization", "Key %s" % os.environ.get("CLARIFAI_API_KEY")),)


def test_export_workflow_general():
    response = stub.GetWorkflow(
        service_pb2.GetWorkflowRequest(
            workflow_id="General"
        ),
        metadata=metadata
    )
    assert response.status.code==10000, f'Invalid response {response}'

    with Exporter(response.workflow) as e:
        clean_wf = e.parse_workflow()
    # assert this to the reader result
    with open('tests/general.yml', 'r') as file:
        data = yaml.safe_load(file)
    assert clean_wf == data, f"dicts did not match: actual: {clean_wf}"
    
    
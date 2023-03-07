import glob
import os
import pytest

from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2
from tests.channel import get_test_channel
from yaml2workflow.parser import parse


channel = get_test_channel()
stub = service_pb2_grpc.V2Stub(channel)
metadata = (("authorization", "Key %s" % os.environ.get("CLARIFAI_API_KEY")),)

def file_loop_index() -> list:
    filenames = []
    files = glob.glob("tests/test_cases/*.yml")
    for file in files:
        filenames.append(file)
    return filenames


@pytest.mark.parametrize("filename", file_loop_index())
def test_parse_workflow_creation(filename: str):
    workflows = parse(filename)
    response = stub.PostWorkflows(
        service_pb2.PostWorkflowsRequest(
            workflows=workflows
        ),
        metadata=metadata
    )
    assert response.status.code==10000, f'Invalid response {response}'
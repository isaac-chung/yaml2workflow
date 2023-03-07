import glob
import os
import typing

import pytest

from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2
from tests.channel import get_test_channel
from yaml2workflow.parser import parse


stub = service_pb2_grpc.V2Stub(get_test_channel())
metadata = (("authorization", "Key %s" % os.environ.get("CLARIFAI_API_KEY")),)


def get_test_parse_workflow_creation_workflows() -> typing.List[str]:
    filenames = []
    files = glob.glob("tests/fixtures/*.yml")
    for file in files:
        filenames.append(file)
    return filenames


@pytest.mark.parametrize("filename", get_test_parse_workflow_creation_workflows())
def test_parse_workflow_creation(filename: str):
    workflows = parse(filename, generate_new_id=True, stub=stub, metadata=metadata)
    response = stub.PostWorkflows(
        service_pb2.PostWorkflowsRequest(
            workflows=workflows
        ),
        metadata=metadata
    )
    assert response.status.code==10000, f'Invalid response {response}'
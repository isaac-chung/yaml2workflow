from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc

from yaml2workflow.exporter import Exporter

def main():
    ## Fill in your credentials here
    PAT = ''
    USER_ID = ''
    APP_ID = ''
    WORKFLOW_ID = ''

    metadata = (('authorization', 'Key ' + PAT),)
    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    response = stub.GetWorkflow(
        service_pb2.GetWorkflowRequest(
            workflow_id=WORKFLOW_ID
        ),
        metadata=metadata
    )
    print(response.status)

    with Exporter(response.workflow) as e:
        e.parse_workflow()
        e.export("export_example.yml")

if __name__ == '__main__':
    main()
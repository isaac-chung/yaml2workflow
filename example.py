from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc

from yaml2workflow.reader import parser

def main():
    PAT = ""
    USER_ID = ''
    APP_ID = ''

    metadata = (('authorization', 'Key ' + PAT),)
    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    workflows = parser('example.yml')

    post_workflows_response = stub.PostWorkflows(
        service_pb2.PostWorkflowsRequest(
            user_app_id=userDataObject,  
            workflows=workflows
        ),
        metadata=metadata
    )  

    print(post_workflows_response.status)

if __name__ == '__main__':
    main()
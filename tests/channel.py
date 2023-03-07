import os

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel


def get_test_channel():
  if os.environ.get("CLARIFAI_GRPC_BASE") == "localhost":
    kwargs = {}
    if os.environ.get("CLARIFAI_GRPC_PORT"):
      kwargs["port"] = os.environ.get("CLARIFAI_GRPC_PORT")
    channel = ClarifaiChannel.get_insecure_grpc_channel(**kwargs)
  else:
    channel = ClarifaiChannel.get_grpc_channel()

  return channel

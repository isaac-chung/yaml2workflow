import typing

from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from google.protobuf.json_format import MessageToDict
from yaml2workflow.converter.model import convert_yaml_model_to_api_model


def _add_new_model(stub: service_pb2_grpc.V2Stub, yaml_model: typing.Dict, metadata):
  api_model = convert_yaml_model_to_api_model(yaml_model)
  response = stub.PostModels(
    service_pb2.PostModelsRequest(
      models=[api_model],
    ),
    metadata=metadata)
  assert response.status.code == status_code_pb2.SUCCESS, f'Invalid response {response}'
  assert response.model

  return response.model.id, response.model.model_version.id


def _add_new_model_version(stub: service_pb2_grpc.V2Stub, old_api_model: resources_pb2.Model, yaml_model: typing.Dict,
                           metadata):
  new_api_model = convert_yaml_model_to_api_model(yaml_model)

  if old_api_model.model_type_id != new_api_model.model_type_id:
    raise Exception("You cannot change the model_type_id of an existing model.")
  new_api_model.model_type_id = ""  # Reset model type ID because API does not allow setting it for a patch request.

  response = stub.PatchModels(
    service_pb2.PatchModelsRequest(
      models=[new_api_model],
      action="overwrite"
    ),
    metadata=metadata)
  assert response.status.code == status_code_pb2.SUCCESS, f'Invalid response {response}'
  assert len(response.models) == 1

  return response.models[0].id, response.models[0].model_version.id


def _parse(yaml_model: typing.Dict, stub: service_pb2_grpc.V2Stub = None,
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
    if model_version_id:
      raise Exception("Model version with specific ID '%s' not found for model with ID '%s'." % (
        model_version_id, yaml_model['model_id']))
    return _add_new_model(stub, yaml_model, metadata)

  assert response.status.code == status_code_pb2.SUCCESS, f'Invalid response {response}'

  if model_version_id or _is_same_model(response.model, yaml_model):
    return response.model.id, response.model.model_version.id
  else:
    return _add_new_model_version(stub, response.model, yaml_model, metadata)


def _is_same_model(api_model: resources_pb2.Model, yaml_model: typing.Dict) -> bool:
  yaml_model_from_api = MessageToDict(api_model, preserving_proto_field_name=True)
  ignore_keys = {'model_id'}  # Ignore model ID because model was already loaded by ID.

  return _is_dict_in_dict(yaml_model, yaml_model_from_api, ignore_keys)


def _is_dict_in_dict(d1: typing.Dict, d2: typing.Dict, ignore_keys: typing.Set = None) -> bool:
  for k, v in d1.items():
    if ignore_keys and k in ignore_keys:
      continue
    if k not in d2:
      return False
    if isinstance(v, dict):
      if not isinstance(d2[k], dict):
        return False
      return _is_dict_in_dict(d1[k], d2[k], None)
    elif v != d2[k]:
      return False

  return True

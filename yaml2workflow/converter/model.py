import typing

from clarifai_grpc.grpc.api import resources_pb2
from google.protobuf import struct_pb2


def convert_yaml_model_to_api_model(yaml_model: typing.Dict) -> resources_pb2.Model:
  return resources_pb2.Model(
    id=yaml_model.get('model_id'),
    model_type_id=yaml_model.get('model_type_id'),
    description=yaml_model.get('description'),
    output_info=_convert_yaml_model_output_info_to_api_model_output_info(yaml_model.get('output_info'))
  )


def _convert_yaml_model_output_info_to_api_model_output_info(yaml_model_output_info: typing.Dict
                                                             ) -> typing.Optional[resources_pb2.OutputInfo]:
  if not yaml_model_output_info:
    return None

  return resources_pb2.OutputInfo(
    params=_convert_yaml_model_output_info_params_to_api_model_output_info_params(yaml_model_output_info.get('params'))
  )


def _convert_yaml_model_output_info_params_to_api_model_output_info_params(yaml_params: typing.Dict
                                                                           ) -> typing.Optional[struct_pb2.Struct]:
  if not yaml_params:
    return None

  s = struct_pb2.Struct()
  s.update(yaml_params)

  return s

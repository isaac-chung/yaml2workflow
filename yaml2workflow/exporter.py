import yaml

from google.protobuf.json_format import MessageToDict


CAMEL2SNAKE = {
    "nodeInputs": "node_inputs",
    "nodeId": "node_id"
}

NODE_KEY_LIST = [
    "workflow", "id", "nodes", "node_inputs", "node_id", "model"
]

def clean_up_unused_keys(wf: dict):
    """
    Removes unused keys from dict before exporting to yaml.
    Supports nested dicts.
    """
    new_wf = dict()
    for key, val in wf.items():
        if CAMEL2SNAKE.get(key, key) in NODE_KEY_LIST:
            if key == "model":
                new_wf["model"] = {
                    "model_id": wf["model"]["id"],
                    "model_version_id": wf["model"]["modelVersion"]["id"]
                }
            elif isinstance(val, dict):
                new_wf[CAMEL2SNAKE.get(key, key)] = clean_up_unused_keys(val)
            elif isinstance(val, list):
                new_list = []
                for i in val:
                    new_list.append(clean_up_unused_keys(i))
                new_wf[CAMEL2SNAKE.get(key, key)] = new_list
            else:
                new_wf[CAMEL2SNAKE.get(key, key)] = val
    return new_wf

class Exporter:
    def __init__(self, workflow):
        self.wf = workflow

    def __enter__(self):
        return self

    def parse_workflow(self):
        """
        Reads a resources_pb2.Workflow object (e.g. from a GetWorkflow response)
        Returns a cleaned workflow dict.
        """
        if isinstance(self.wf, list):
            self.wf = self.wf[0]
        wf = {"workflow": MessageToDict(self.wf)}
        clean_wf = clean_up_unused_keys(wf)
        self.wf_dict = clean_wf
        return clean_wf

    def export(self, out_path):
        with open(out_path, 'w') as out_file:
            yaml.dump(self.wf_dict, out_file, default_flow_style=True)

    def __exit__(self, *args):
        self.close()

    def close(self):
        del self.wf
        del self.wf_dict

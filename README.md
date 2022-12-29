# yaml2workflow

[Clarifai](https://www.clarifai.com/) workflows are powerful tools. Building them [via the API](https://docs.clarifai.com/api-guide/workflows/input_nodes) is a sure way to automate this process, especially if you have many nodes and brances.

Taking inspiration from [Kubernetes Helm Charts](https://helm.sh/docs/topics/charts/) and [AWS Cloud Formation templates](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-formats.html), `yaml2workflow` is designed to make automating the creating and managing the definition of workflows easier and more transparent.

## 😎 Define Workflows as YAML files
Much clearer and more human-readable definitions without distractors. Also, by storing the workflow definitions as a file, you can now use version control for your future automations! Winning.  
```yaml
workflow:
  id: test-wf-1
  nodes:
    - id: detector
      model:
          model_id: face-detection
          model_version_id: 45fb9a671625463fa646c3523a3087d5
```
See [example.yml](example.yml) for a full, filled in template.

## 🚀 Installation
```
pip install yaml2workflow
```

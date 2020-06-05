import kfp.dsl as dsl
import kfp.gcp as gcp
from kfp import components
import json

@dsl.pipeline(
    name="Fashion-MNIST", description="A pipeline to train and serve the Fashion MNIST example."
)
def fashion_mnist_pipeline(
    name="fashion-mnist-{{workflow.uid}}",
    katib_namespace="<SET_USER_NAMSPACE>",
    goal=0.9,
    max_trial_count=12,
    parallel_trial_count=3,
    training_steps=5,
    training_image="<SET_TRAINING_IMAGE_NAME>",

):


    ### Step 1: Hyper-parameter tuning with Katib
    objectiveConfig = {
      "type": "maximize",
      "goal": goal,
      "objectiveMetricName": "val_accuracy",
      "additionalMetricNames" : ["loss", "accuracy"]
    }
    algorithmConfig = {"algorithmName" : "random"}
    metricsCollectorSpec = {
      "collector": {
        "kind": "StdOut"
      }
    }
    parameters = [
      {"name": "--tf-learning-rate", "parameterType": "double", "feasibleSpace": {"min": "0.001","max": "0.05"}},
    ]
    
    rawTemplate = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": "{{.Trial}}",
            "namespace": "{{.NameSpace}}"
        },
        "spec": {
            "template": {
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {"name": "{{.Trial}}",
                         "image": str(training_image),
                         "imagePullPolicy": "Always",
                         "command": [
                             "python /opt/model.py --tf-mode=local {{- with .HyperParameters}} {{- range .}} {{.Name}}={{.Value}} {{- end}} {{- end}}"
                         ]
                         }
                    ]
                }
            }
        }
    }

    trialTemplate = {
        "goTemplate": {
            "rawTemplate": json.dumps(rawTemplate)
        }
    }


    katib_experiment_launcher_op = components.load_component_from_url(
        'https://raw.githubusercontent.com/kubeflow/pipelines/master/components/kubeflow/katib-launcher/component.yaml')
    katib_op = katib_experiment_launcher_op(
        experiment_name=name,
        experiment_namespace=katib_namespace,
        parallel_trial_count=parallel_trial_count,
        max_trial_count=max_trial_count,
        objective=str(objectiveConfig),
        algorithm=str(algorithmConfig),
        trial_template=str(trialTemplate),
        parameters=str(parameters),
        metrics_collector=str(metricsCollectorSpec),
        delete_finished_experiment=False)
    
    ### Step 2 : echo the optimized result
    echo2_op = dsl.ContainerOp(
            name='echo',
            image='library/bash:4.4.23',
            command=['sh', '-c'],
            arguments=['echo "optimized result: $0";', katib_op.output]
        )

    

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(fashion_mnist_pipeline, __file__ + ".tar.gz")

import kfp.dsl as dsl
import kfp.gcp as gcp
from kfp import components
import json
from string import Template

def convert_result(result) -> str:
    import json
    hyperparameters = json.loads(result)
    args = []
    for param in hyperparameters:
        args.append("{0}={1}".format(param["name"], param["value"]))
    return " ".join(args)



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
    training_namespace="kubeflow",
    export_dir="gs://<SET_BUCKET_NAME>/export/002"

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
    
    ### Step 2 : convert the optimized result to extract optimal hyperparameters
    
    convert_op = components.func_to_container_op(convert_result)
    op2 = convert_op(katib_op.output)

    ## Step 3 : training
    training_template = Template("""
                                    {
                                        "apiVersion": "kubeflow.org/v1",
                                        "kind": "TFJob",
                                        "metadata": {
                                            "generateName": "tfjob",
                                            "name": "$name",
                                            "namespace": "$namespace"
                                        },
                                        "spec": {
                                            "tfReplicaSpecs": {
                                            "Chief": {
                                                "replicas": 1,
                                                "restartPolicy": "OnFailure",
                                                "template": {
                                                "spec": {
                                                    "containers": [
                                                    {
                                                        "name": "tensorflow",
                                                        "image": "$image",
                                                        "command": [
                                                        "python",
                                                        "/opt/model.py",
                                                        "--tf-export-dir=$export",
                                                        "--tf-mode=gcs",
                                                        "--tf-train-steps=$training_steps",
                                                        "$args"
                                                        ],
                                                        "env": [
                                                        {
                                                            "name": "GOOGLE_APPLICATION_CREDENTIALS",
                                                            "value": "/var/secrets/user-gcp-sa.json"
                                                        }
                                                        ],
                                                        "volumeMounts": [
                                                        {
                                                            "name": "sa",
                                                            "mountPath": "/var/secrets",
                                                            "readOnly": true
                                                        }
                                                        ]
                                                    }
                                                    ],
                                                    "volumes": [
                                                    {
                                                        "name": "sa",
                                                        "secret": {
                                                        "secretName": "user-gcp-sa"
                                                        }
                                                    }
                                                    ]
                                                }
                                                }
                                            },
                                            "Worker": {
                                                "replicas": 2,
                                                "restartPolicy": "OnFailure",
                                                "template": {
                                                "spec": {
                                                    "containers": [
                                                    {
                                                        "name": "tensorflow",
                                                        "image": "$image",
                                                        "command": [
                                                        "python",
                                                        "/opt/model.py",
                                                        "--tf-export-dir=$export",
                                                        "--tf-mode=gcs",
                                                        "--tf-train-steps=$training_steps",
                                                        "$args"
                                                        ],
                                                        "env": [
                                                        {
                                                            "name": "GOOGLE_APPLICATION_CREDENTIALS",
                                                            "value": "/var/secrets/user-gcp-sa.json"
                                                        }
                                                        ],
                                                        "volumeMounts": [
                                                        {
                                                            "name": "sa",
                                                            "mountPath": "/var/secrets",
                                                            "readOnly": true
                                                        }
                                                        ]
                                                    }
                                                    ],
                                                    "volumes": [
                                                    {
                                                        "name": "sa",
                                                        "secret": {
                                                        "secretName": "user-gcp-sa"
                                                        }
                                                    }
                                                    ]
                                                }
                                                }
                                            }
                                            }
                                        }
                                        }
                                    """)

    trainingjson = training_template.substitute({ 'name': str(name),
                                        'namespace': str(training_namespace),
                                        'image': str(training_image),
                                        'export': str(export_dir),
                                        'training_steps': training_steps,
                                        'args': op2.output})

    trainingdeployment = json.loads(trainingjson)

    train = dsl.ResourceOp(
        name="train",
        k8s_resource=trainingdeployment,
        action="apply",
        success_condition="status.replicaStatuses.Worker.succeeded==2,status.replicaStatuses.Chief.succeeded==1"
    )
    

    

if __name__ == "__main__":
    import kfp.compiler as compiler
    compiler.Compiler().compile(fashion_mnist_pipeline, __file__ + ".tar.gz")

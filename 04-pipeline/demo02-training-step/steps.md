### Kubeflow Pipelines : Hyperparameter Tuning + Training Steps

Steps in the pipeline
- Run hyper-parameter tuning
- Extract optimal hyper-parameter
- Train using optimal hyper-parameter

```bash
# build the pipeline
python fashion_mnist_pipeline_step_02.py
```

Upload the tar.gz file to pipelines UI and create experiment and then create run. Enter the `user namespace` , `training image`,`export dir` and click run. 




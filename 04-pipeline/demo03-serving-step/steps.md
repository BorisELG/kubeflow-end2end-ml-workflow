### Kubeflow Pipelines : Hyperparameter Tuning + Training + Serving Steps

Steps in the pipeline
- Run hyper-parameter tuning
- Extract optimal hyper-parameter
- Train using optimal hyper-parameter
- Serve the trained model

```bash
# build the pipeline
python fashion_mnist_pipeline_step_03.py
```

Upload the tar.gz file to pipelines UI and create experiment and then create run. Enter the `user namespace` , `training image`,`export dir`, `serving_export_dir`, `transformer_image` and click run. 




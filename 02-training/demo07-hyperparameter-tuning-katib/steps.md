### Hyperparameter Tuning with Katib

#### Setup Image and Namespace
- set Image name based on previous TFJob demo
- Set namespace to be user namespace in which notebook was created earlier

#### launch Experiement

```
# launch experiment
kubectl apply -f experiment-distributed.yaml
# get experiment
kubectl get experiment -n <NAMESPACE>
# describe experiment to debug
kubectl describe experiment -n <NAMESPACE> fashion-mnist-experiment-distributed-1 
# check the TFJob launched as part of hyper-parameter tuning 
kubectl get tfjob -n <NAMESPACE>
kubectl describe tfjob <TFJOB> -n kubeflow
# check logs 
kubectl logs -f <TJFOB_NAME>-chief-0 -n kubeflow
```

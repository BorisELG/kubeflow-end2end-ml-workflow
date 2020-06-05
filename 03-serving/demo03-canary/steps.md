### KFServing : Canary Release

#### Deploy inferenceservice

Change default and canary model storage URI in the `fashion-mnist-serving-canary.yaml`. eg. `gs://<GCS_BUCKET-1_NAME>/export`.


```bash
kubectl apply -f fashion-mnist-serving-canary.yaml
```



#### Check logs 

```bash
# get pod
kubectl get pods -n kubeflow | grep fashion-mnist-canary-transformer
# open separate terminal tab and check log of the default pod
kubectl logs -f <TRANSFORMER_DEFAULT_POD_NAME> -n kubeflow user-container
# open separate terminal tab and check log of the default pod
kubectl logs -f <TRANSFORMER_CANARY_POD_NAME> -n kubeflow user-container
```

#### Test inference

Test on the sample json that contains `base64` encoded images. Check the requests being served by `default` and `canary` models. 

```bash
# model name
MODEL_NAME=fashion-mnist-canary
# IP 
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# host
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
# test 
(echo -n '{"instances": ["'; base64 fashion_mnist_1.jpg; echo '"]}') | curl -v -H "Content-Type: application/json" -H "Host: ${HOST}" -d @-  http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict
```

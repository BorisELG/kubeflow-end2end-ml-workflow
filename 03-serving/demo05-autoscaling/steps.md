### KFServing : Autoscaling 

You can use any load testing tool to simulate the load. Let's use **hey** (https://github.com/rakyll/hey) tool to test the autoscaling. 

```bash
# on macOS
brew install hey
```
### Run load-testing to test autoscaling

```bash
# model name
MODEL_NAME=fashion-mnist
# IP 
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# host
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
# file path
INPUT_PATH=fashion_mnist_input.json
# check pods
kubectl get pods -n kubeflow | grep fashion-mnist-predictor
# send request for 30 secs with maintaining 5 in-flight requests
hey -z 30s -c 5 -m POST -host ${HOST} -D $INPUT_PATH http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict
# send request for 30 secs with maintaining 50 QPS ( query per second)
hey -z 30s -q 50 -m POST -host ${HOST} -D $INPUT_PATH http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict
```

Monitor grafana dashboard `Knative Serving-Scaling Debugging` (Revision Pod Counts).

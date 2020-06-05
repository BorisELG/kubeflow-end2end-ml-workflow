### KFServing monitoring

#### Setup knative-monitoring
```bash
#create namespace
kubectl create namespace knative-monitoring
#setup monitoring components
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.13.0/monitoring-metrics-prometheus.yaml
```
#### Launch grafana dashboard

```bash
# use port-forwarding
kubectl port-forward --namespace knative-monitoring $(kubectl get pod --namespace knative-monitoring --selector="app=grafana" --output jsonpath='{.items[0].metadata.name}') 8080:3000
```
open `grafana` dashboard by using `localhost:8080` on browser. Explore different components of the grafana dashboard. 


#### Make some requests and test on monitoring dashboard ( e.g. KNative-Serving - Revision HTTP Requests)

```bash
# model name
MODEL_NAME=fashion-mnist
# IP 
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# host
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
# file path
INPUT_PATH=@./fashion_mnist_input.json
# make post request using curl
curl -v -H "Host: ${HOST}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```
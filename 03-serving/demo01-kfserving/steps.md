### KFserving : Basic

#### Setup KFServing 
Enable inferenceservice on `kubeflow` namespace

```bash
kubectl label namespace kubeflow serving.kubeflow.org/inferenceservice=enabled
```

#### Create KFserving inferenceservice

Change the model storage URI in the `fashion-mnist-serving-default.yaml`. eg. `gs://<GCS_BUCKET_NAME>/export`
Apply the YAML file. 

```bash
kubectl apply -f fashion-mnist-serving-default.yaml
```

#### Create sample data

create sample data ( assuming you have python3 installed on your local machine). 

```bash
# install virtualenv
pip3 install virtualenv
# create a virtual environment named 'env'
virtualenv env
# activiate environment
source env/bin/activate
# install required packages
pip3 install tensorflow==2.1.0 tensorflow-datasets==2.1.0
# run script to generate sample data. This will create/overwrite 'fashion_mnist_input.json'
python create_sample_test.py
# deactivate environment
deactivate
```
#### Test inferences

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

#### Debug Inferenceservice

```bash
kubectl get inferenceservice -n kubeflow
kubectl get kservice -n kubeflow
kubectl get pods -n kubeflow | grep fashion-mnist
kubectl logs -f <PREDICTOR_POD_NAME> -n kubeflow storage-initializer
kubectl logs -f <PREDICTOR_POD_NAME> -n kubeflow kfserving-container
```
#### Delete inferenceservice

```bash
kubectl delete inferenceservice -n kubeflow fashion-mnist
```

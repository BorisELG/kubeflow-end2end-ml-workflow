### KFserving : Pre and Post-Processing

#### Create a transformer image

```bash
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=fashion-mnist-processing
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
IMAGE_TAG=latest

# build image
docker build -t $IMAGE_NAME:$IMAGE_TAG .
# run locally to test
docker run -it --rm $IMAGE_NAME:$IMAGE_TAG
# authorize docker
gcloud auth configure-docker --quiet
# push image
docker push $IMAGE_NAME:$IMAGE_TAG
```

#### Create KFserving inferenceservice

Change the model storage URI in the `fashion-mnist-serving-with-processing.yaml`. eg. `gs://<GCS_BUCKET_NAME>/export`
Apply the YAML file. 

```bash
kubectl apply -f fashion-mnist-serving-with-processing.yaml
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
pip install tensorflow==2.1.0 tensorflow-datasets==2.1.0 pillow
# run script to generate sample data. This will create/overwrite 'fashion_mnist_input.json'
python create_sample_test_encoded.py
# deactivate environment
deactivate
```

#### Test inference

Test on the sample json that contains `base64` encoded images. 

```bash
# model name
MODEL_NAME=fashion-mnist-processor
# IP 
CLUSTER_IP=$(kubectl -n istio-system get service kfserving-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# host
HOST=$(kubectl get inferenceservice -n kubeflow $MODEL_NAME -o jsonpath='{.status.url}' | cut -d "/" -f 3)
# file path
INPUT_PATH=@./fashion_mnist_input_b64_encoded.json
# make post request using curl
curl -v -H "Host: ${HOST}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH
```

### Test directly on image

Try changing the images. 

```bash
(echo -n '{"instances": ["'; base64 fashion_mnist_1.jpg; echo '"]}') | curl -v -H "Content-Type: application/json" -H "Host: ${HOST}" -d @-  http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict
```

#### Debug Inferenceservice

```bash
kubectl get inferenceservice -n kubeflow
kubectl get kservice -n kubeflow
kubectl get pods -n kubeflow | grep fashion-mnist-processor
kubectl logs -f <PREDICTOR_POD_NAME> -n kubeflow storage-initializer
kubectl logs -f <PREDICTOR_POD_NAME> -n kubeflow kfserving-container
kubectl logs -f <TRANSFORMER_POD_NAME> -n kubeflow user-container
```
#### Delete inferenceservice

```bash
kubectl delete inferenceservice -n kubeflow fashion-mnist-processor
```
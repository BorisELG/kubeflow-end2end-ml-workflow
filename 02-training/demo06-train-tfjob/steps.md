## set image 

``` bash
PROJECT_ID=$(gcloud config get-value core/project)
IMAGE_NAME=kubeflow-fashion-mnist-train-keras
IMAGE_VERSION=latest
IMAGE_NAME=gcr.io/$PROJECT_ID/$IMAGE_NAME
```

### Building docker image. 
```
docker build -t $IMAGE_NAME:$IMAGE_VERSION .
```

### Run locally to test
```
docker run -it --rm $IMAGE_NAME:$IMAGE_VERSION
docker run -it --rm -v $(pwd)/export:/tmp/export $IMAGE_NAME:$IMAGE_VERSION
```

### Push docker image

```
gcloud auth configure-docker --quiet
docker push $IMAGE_NAME:$IMAGE_VERSION
```

## Run TFJob

create a bucket to store the tensorflow model

```
BUCKET=$PROJECT_ID-fashion-mnist-tfjob
gsutil mb gs://$BUCKET/
```

```bash

# launch TFJob
kubectl apply -f training-gcs.yaml
kubectl get tfjob -n kubeflow 
kubectl get pods -n kubeflow | grep fashion-mnist-job-1
kubectl describe tfjob fashion-mnist-job-1 -n kubeflow
kubectl logs -f fashion-mnist-job-1-chief-0 -n kubeflow
```
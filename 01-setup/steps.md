## Setting Up Kubeflow on Google Cloud Platform 

Note: Use latest official Kubeflow documentation available at **https://www.kubeflow.org/docs/gke/deploy/deploy-cli/** to install the latest release and config files.
latest release are available at **https://github.com/kubeflow/kfctl/releases**

### Step 1 : Setup GCP 

```bash
# login to gcloud for authentication : done once
gcloud auth login
# create application default credentials : done once
gcloud auth application-default login
# GCP Project ID
export PROJECT=<SET_YOUR_GCP_PROJECT_ID>
gcloud config set project ${PROJECT}
# GCP Zone
export ZONE=<SET_GCP_ZONE>
gcloud config set compute/zone ${ZONE}
```

### Step 2 : download the release based on your Operating system


```bash

# KFCTL file url : Get the latest file from 
# https://github.com/kubeflow/kfctl/releases  based on the operating system
KFCTL_FILE_PATH="<KFCTL_FILE_URI>"
KFCTL_FILE="kfctl.tar.gz"
# download KFCTL compressed file
wget $KFCTL_FILE_PATH -O $KFCTL_FILE
# extract KFCTL
tar -xvf ${KFCTL_FILE}
#mv kfctl-${PLATFORM} kfctl
# add kFCTL to path
PATH=${PATH}:$(pwd)
```
### Step 3: setup the deployment

```bash
# Deployment Name e.g. pskfp-1
export KF_NAME=<SET_DEPLOYMENT_NAME>
# set client ID and client secret
export CLIENT_ID=<CLIENT_ID>
export CLIENT_SECRET=<CLIENT_SECRET>

	
# set the config URI : use the official documentation to use the latest config file
# get latest config URI from official Kubeflow documentation : https://www.kubeflow.org/docs/gke/deploy/deploy-cli/

export CONFIG_URI="<CONFIG_URI>"
# set the base directory	
BASE_DIR=$(pwd)
# set the directory for deployment
KF_DIR=${BASE_DIR}/${KF_NAME}
# create the directory
mkdir -p ${KF_DIR}
# navigate to the directory
cd ${KF_DIR}
# build deployment using the config file. Make changes in your configuration if needed
kfctl build -V -f ${CONFIG_URI}

```
### Step 4: Deploy
```bash
# setup the config file
export CONFIG_FILE=${KF_DIR}/<CONFIG_FILE_NAME>
# apply changes
kfctl apply -V -f ${CONFIG_FILE}
gcloud container clusters get-credentials ${KF_NAME} --zone ${ZONE} --project ${PROJECT}
```
### Step 5 : Delete 

```bash
# If you want to delete all the resources, including storage:
kfctl delete -f ${CONFIG_FILE} --delete_storage
```

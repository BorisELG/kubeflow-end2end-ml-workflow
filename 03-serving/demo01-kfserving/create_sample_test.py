from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
import json
tfds.disable_progress_bar()

# load data
ds_train = tfds.load(name="fashion_mnist:1.0.0", split="train")

# create samples
NUM_EXAMPLE=5
samples=[]
for row in ds_train.take(NUM_EXAMPLE):
    image, label = row["image"], row["label"]
    
    # preprocessing
    image = image.numpy() / 255.0
    image = image.reshape(28, 28, 1)
    samples.append(image.tolist())
    
# prepare test data
data = json.dumps({"instances": samples})
data_read = json.loads(data)
with open('fashion_mnist_input.json','w') as out:
    json.dump(data_read, out)
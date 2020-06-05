from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
import json
tfds.disable_progress_bar()
from tensorflow.keras.preprocessing.image import save_img
import base64

# load data
ds_train = tfds.load(name="fashion_mnist:1.0.0", split="train")

# create sample images
count=0
NUM_EXAMPLE=5
for row in ds_train.take(NUM_EXAMPLE):
    image, label = row["image"], row["label"]
    
    # preprocessing
    image = image.numpy() #/ 255.0
    image = image.reshape(28, 28, 1)
    count += 1
    save_img('fashion_mnist_{0}.jpg'.format(count),image)

# read images to created encoding string
samples=[]
NUM_SAMPLES=5
for index in range(NUM_SAMPLES):
    with open("fashion_mnist_{0}.jpg".format(index + 1), "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read())
        # result: string (in utf-8)
        encoded_string = encoded_bytes.decode('utf-8')
        samples.append(encoded_string)
        
# prepare test data
data = json.dumps({"instances": samples})
data_read = json.loads(data)
with open('fashion_mnist_input_b64_encoded.json','w') as out:
    json.dump(data_read, out)
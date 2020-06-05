from __future__ import absolute_import, division, print_function, unicode_literals
import tensorflow_datasets as tfds
import tensorflow as tf
import numpy as np
tfds.disable_progress_bar()
import logging
from datetime import datetime
logger = tf.get_logger()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level=logging.INFO)
print('Tensorflow-version: {0}'.format(tf.__version__))

import os
import argparse
import json
from storage import Storage


# prepare data
def prepare_data(batch_size=64, shuffle_size=1000):

    def scale(image, label):
        image = tf.cast(image, tf.float32)
        image /= 255
        return image, label
    
    # Split the training set into 80% and 20% for training and validation
    train_validation_split = tfds.Split.TRAIN.subsplit([8, 2])
    ((train_data, validation_data), test_data),info = tfds.load(name="fashion_mnist:1.0.0", 
                                                         split=(train_validation_split, tfds.Split.TEST),
                                                         as_supervised=True, with_info=True)

    
    print("Training data count : ", int(info.splits['train'].num_examples * 0.8))
    print("Validation data count : ", int(info.splits['train'].num_examples * 0.2))
    print("Test data count : ", int(info.splits['test'].num_examples))


    # create dataset to be used for training process
    train_dataset = train_data.map(scale).shuffle(shuffle_size).batch(batch_size).repeat().prefetch(tf.data.experimental.AUTOTUNE)
    val_dataset = validation_data.map(scale).batch(batch_size).prefetch(tf.data.experimental.AUTOTUNE)
    test_dataset = test_data.map(scale).batch(batch_size)
    
    return train_dataset, val_dataset, test_dataset


# build model
def build_model(learning_rate=0.001):
    model = tf.keras.Sequential([
      tf.keras.layers.Conv2D(filters=32, kernel_size=(3,3), activation='relu', input_shape=(28, 28, 1), name='x'),
      tf.keras.layers.MaxPooling2D(),
      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.Dense(10, activation='softmax')
      ])
      
    model.compile(
        loss=tf.keras.losses.sparse_categorical_crossentropy,
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        metrics=['accuracy'])
    return model

    
# callbacks
def get_callbacks():
    # callbacks 
    # checkpoint directory
    checkpointdir = '/tmp/model-ckpt'

    class customLog(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs={}):
            logging.info('epoch: {}'.format(epoch + 1))
            logging.info('loss={}'.format(logs['loss']))
            logging.info('accuracy={}'.format(logs['accuracy']))
            logging.info('val_accuracy={}'.format(logs['val_accuracy']))
    callbacks = [
        #tf.keras.callbacks.TensorBoard(logdir),
        tf.keras.callbacks.ModelCheckpoint(filepath=checkpointdir),
        customLog()
    ]
    return callbacks


# parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tf-mode',
                        type=str,
                        default='local',
                        help='use either of local,gcs')
    parser.add_argument('--tf-export-dir',
                        type=str,
                        default='/tmp/export',
                        help='GCS path or local directory to export model')
    parser.add_argument('--tf-train-steps',
                        type=int,
                        default=3,
                        help='The number of training steps to perform.')
    parser.add_argument('--tf-learning-rate',
                        type=float,
                        default=0.001,
                        help='Learning rate for training.')

    args = parser.parse_known_args()[0]
    return args


def main():

    # parse arguments
    args = parse_arguments()

    tf_config = os.environ.get('TF_CONFIG', '{}')
    logging.info("TF_CONFIG %s", tf_config)
    tf_config_json = json.loads(tf_config)
    cluster = tf_config_json.get('cluster')
    job_name = tf_config_json.get('task', {}).get('type')
    task_index = tf_config_json.get('task', {}).get('index')
    logging.info("cluster=%s job_name=%s task_index=%s", cluster, job_name,
                    task_index)

    is_chief = False
    if not job_name or job_name.lower() in ["chief", "master"]:
        is_chief = True
        logging.info("Will export model")
    else:
        logging.info("Will not export model")

    # multi-worker mirrored strategy
    strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
    logging.info("Number of devices: {0}".format(strategy.num_replicas_in_sync))
    

    # build keras model
    with strategy.scope():
        # Data extraction and processing
        # set variables
        BUFFER_SIZE = 10000
        BATCH_SIZE = 64
        BATCH_SIZE = BATCH_SIZE * strategy.num_replicas_in_sync
        train_dataset, val_dataset, test_dataset = prepare_data(batch_size=BATCH_SIZE, shuffle_size=BUFFER_SIZE)
        
        
        # build and compile model
        learning_rate = float(args.tf_learning_rate)
        logging.info("learning rate : {0}".format(learning_rate))
        model = build_model(learning_rate)

        # training and evaluation
        logging.info("Training starting...")
        TF_STEPS_PER_EPOCHS = 5
        #TF_STEPS_PER_EPOCHS = int(np.ceil(60000 / float(BATCH_SIZE)))  

        # train model
        model.fit(train_dataset, 
                epochs=int(args.tf_train_steps),
                steps_per_epoch=TF_STEPS_PER_EPOCHS, 
                validation_data=val_dataset,
                validation_steps=1,
                callbacks=get_callbacks())
        logging.info("Training completed.")


         # model save
        if is_chief:
            # save the model
            model.save("model.h5")
            logging.info("model saved.")

    
    # load the model 
    model_loaded = tf.keras.models.load_model('model.h5')

    # evaluate model on the test dataset
    loss, accuracy = model_loaded.evaluate(test_dataset)
    print("\nfinal evaluation : loss={0:.4f}, accuracy={1:.4f}".format(loss, accuracy))

    # Model Export
    print("exporting model - mode: {0}, path : {1} ".format(args.tf_mode, args.tf_export_dir))

    if args.tf_mode != 'local':
        # save locally
        tf.saved_model.save(model_loaded, "/tmp/export")
        # upload to remote location 
        Storage.upload("/tmp/export",args.tf_export_dir)
    else:
        # save locally to the export directory
        tf.saved_model.save(model_loaded, args.tf_export_dir)

    print("process completed.")
    # successful completion
    exit(0)
  

if __name__ == "__main__":
    main()
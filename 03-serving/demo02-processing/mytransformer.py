import kfserving
from typing import List, Dict
import argparse
import numpy as np
import json
import logging

import base64
from PIL import Image
import io



logging.basicConfig(level=kfserving.constants.KFSERVING_LOGLEVEL)
DEFAULT_MODEL_NAME = "model"
parser = argparse.ArgumentParser(parents=[kfserving.kfserver.parser])
parser.add_argument('--model_name', default=DEFAULT_MODEL_NAME,
                    help='The name that the model is served under.')
parser.add_argument('--predictor_host',help='The URL for the model predict function', required=True)
args, _ = parser.parse_known_args()

def image_transform(instance):
    # perform pre-processing
    # decode image
    byte_array = base64.b64decode(instance)
    # convert to array
    image = Image.open(io.BytesIO(byte_array))
    image = np.asarray(image)
    # pre-processing logic
    image = image / 255.0
    image = image.reshape(28, 28, 1)
    return image.tolist()

class Transformer(kfserving.KFModel):
    def __init__(self, name: str, predictor_host: str):
        super().__init__(name)
        self.predictor_host = predictor_host

    def preprocess(self, inputs: Dict) -> Dict:
        return {'instances': [image_transform(instance) for instance in inputs['instances']]}
       
       
    def postprocess(self, inputs: Dict) -> Dict:
        classes = ['T-shirt/top','Trouser','Pullover','Dress','Coat','Sandal','Shirt','Sneaker','Bag','Ankle boot']
        predictions = np.array(inputs['predictions'])
        result = [str(classes[x]) for x in list(np.argmax(predictions, axis=1))]
        logging.info("result : {0}".format(result))
        return json.dumps({"predictions" :  result})

if __name__ == "__main__":
    transformer = Transformer(args.model_name, predictor_host=args.predictor_host)
    kfserver = kfserving.KFServer()
    kfserver.start(models=[transformer])

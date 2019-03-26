import numpy as np
from keras import models
import yaml
import sklearn.preprocessing as pp
import dsp

# Trained CNN model
class Model:

    def __init__(self, dataset):
        self.dataset = dataset
        layer_outputs = [layer.output for layer in dataset.model.layers]
        self.activation_model = models.Model(inputs=dataset.model.input, outputs=layer_outputs)
        dataset.model.summary()

    # ML Inference
    def infer(self, data):
        data = data.astype(float)
        shape = data.shape
        data = pp.scale(data.flatten()).reshape(1, *shape, 1)
        if self.activation_model:
            activations = self.activation_model.predict(data)
            result = (activations[-1][0]*100)  # The last layer
            max_idx = np.argmax(result)
            print(result)
            return (self.dataset.class_labels[max_idx], result[max_idx])
        else:
            return None

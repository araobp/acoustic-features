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
        probabilities = []
        data = data.astype(float)
        shape = data.shape
        data = pp.scale(data.flatten()).reshape(*shape, 1)
        if self.activation_model:
            windowed_data = []
            for w in self.dataset.windows:
                if self.dataset.feature == 'mfcc':
                    d = data[w[0]:w[1], 1:w[2], :]
                else:
                    d = data[w[0]:w[1], 0:w[2], :]                    
                windowed_data.append(d)
            activations = self.activation_model.predict(np.array(windowed_data))
            result = (activations[-1]*100)  # The last layer
            for r in result:
                indexes = np.argsort(r)
                p = []
                for idx in reversed(indexes):
                    p.append([self.dataset.class_labels[idx], r[idx]])
                probabilities.append(p)
            return probabilities
        else:
            return None

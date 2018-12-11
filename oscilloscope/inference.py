import numpy as np
from keras import models
import yaml
import sklearn.preprocessing as pp
import dsp

# Trained CNN model
class Model:

    def __init__(self, class_file, model_file, windows=None):

        self.class_labels = None
        self.activation_model = None
        if windows:
            self.windows = windows
        else:
            self.windows = ((0, dsp.NN))
        
        with open(class_file, 'r') as f:
            self.class_labels = yaml.load(f)
            _model = models.load_model(model_file)
            _model.summary()
            layer_outputs = [layer.output for layer in _model.layers]
            self.activation_model = models.Model(inputs=_model.input, outputs=layer_outputs)

    # ML Inference
    def infer(self, data):
        probabilities = []
        data = data.astype(float)
        shape = data.shape
        data = pp.scale(data.flatten()).reshape(shape[0], shape[1], 1)
        if self.activation_model:
            windowed_data = []
            for w in self.windows:
                d = data[w[0]:w[1], :w[2], :]
                windowed_data.append(d)
            activations = self.activation_model.predict(np.array(windowed_data))
            result = (activations[-1]*100)  # The last layer
            for r in result:
                indexes = np.argsort(r)
                p = []
                for idx in reversed(indexes):
                    p.append([self.class_labels[idx], r[idx]])
                probabilities.append(p)
            return probabilities
        else:
            return None

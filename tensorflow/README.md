# CNN experiments with Keras/TensorFlow (on Nov 6-11, 2018)

The result: about 90% accuracy has been achieved, so it is satisfying.

### Jupyter Notebook of this experiment

I have made two CNN experiments as follows:

- [CNN experiments on musical instruments recognition (Jupyter Notebook)](./tensorflow/CNN_for_AED.ipynb)
- [CNN experiments on human activity in a living room (Jupyter Notebook)](./tensorflow/CNN_for_AED_living_room.ipynb)

The trained CNN model will work OK if the following condition is satisfied:
- use the same MEMS mic with the same filter setting (incl. the same frequency response) on the edge device (STM32L4)
- same environment
- no surrounding noise

Next, I will try beam forming with two MEMS mic to supress noise from the surrounding envirnment.

### Class labels and data set

```
Classes of musical instruments recognition:
- piano music
- classial guitar music
- framenco guitar music
- blues harp music
- tin whistle music

Classes of human activity recognition:
- bathing
- cocking
- moving
- silence
- tooth brushing
- washing the dishes
- watching the TV

Conditions:
- Pre emphasis enabled on the raw data.

I split each 40 mel-filters x 200 strdes data into three three 40 x 64 data.

Training data set: 48 mel-scale spectrograms (40 filters x 64 strides) for each class
Test data set: 24 mel-scale spectrograms (40 filters x 64 strides) for each class
```

### CNN model 1

This model works well for both musical instruments recognition and human activity recognition.

All the filters are the size of 5 x 5.

```
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d_70 (Conv2D)           (None, 60, 36, 16)        416       
_________________________________________________________________
max_pooling2d_70 (MaxPooling (None, 30, 18, 16)        0         
_________________________________________________________________
conv2d_71 (Conv2D)           (None, 26, 14, 32)        12832     
_________________________________________________________________
max_pooling2d_71 (MaxPooling (None, 13, 7, 32)         0         
_________________________________________________________________
flatten_24 (Flatten)         (None, 2912)              0         
_________________________________________________________________
dense_47 (Dense)             (None, 64)                186432    
_________________________________________________________________
dense_48 (Dense)             (None, 5)                 325       
=================================================================
Total params: 200,005
Trainable params: 200,005
Non-trainable params: 0
_________________________________________________________________
```

### CNN Model 2

This model works well for musical instruments recognition, and the size of CNN is a hundred times smaller than the model 1.

All the filters are the size of 3 x 3.

```
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d_41 (Conv2D)           (None, 62, 38, 4)         40        
_________________________________________________________________
max_pooling2d_41 (MaxPooling (None, 31, 19, 4)         0         
_________________________________________________________________
conv2d_42 (Conv2D)           (None, 29, 17, 8)         296       
_________________________________________________________________
max_pooling2d_42 (MaxPooling (None, 14, 8, 8)          0         
_________________________________________________________________
conv2d_43 (Conv2D)           (None, 12, 6, 16)         1168      
_________________________________________________________________
max_pooling2d_43 (MaxPooling (None, 6, 3, 16)          0         
_________________________________________________________________
flatten_16 (Flatten)         (None, 288)               0         
_________________________________________________________________
dropout_17 (Dropout)         (None, 288)               0         
_________________________________________________________________
dense_34 (Dense)             (None, 5)                 1445      
=================================================================
Total params: 2,949
Trainable params: 2,949
Non-trainable params: 0
```

### CNN Model 3

This model works well for human activity recognition, and the size of CNN is ten times smaller than the model 1.

All the filters are the size of 3 x 3.

```
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
conv2d_18 (Conv2D)           (None, 62, 38, 4)         40        
_________________________________________________________________
max_pooling2d_15 (MaxPooling (None, 31, 19, 4)         0         
_________________________________________________________________
conv2d_19 (Conv2D)           (None, 29, 17, 8)         296       
_________________________________________________________________
max_pooling2d_16 (MaxPooling (None, 14, 8, 8)          0         
_________________________________________________________________
conv2d_20 (Conv2D)           (None, 12, 6, 16)         1168      
_________________________________________________________________
max_pooling2d_17 (MaxPooling (None, 6, 3, 16)          0         
_________________________________________________________________
flatten_7 (Flatten)          (None, 288)               0         
_________________________________________________________________
dense_10 (Dense)             (None, 64)                18496     
_________________________________________________________________
dropout_5 (Dropout)          (None, 64)                0         
_________________________________________________________________
dense_11 (Dense)             (None, 7)                 455       
=================================================================
Total params: 20,455
Trainable params: 20,455
Non-trainable params: 0
_________________________________________________________________
```
### Using the trained model

I am looking forward to CubeMX.AI: https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html

Since CubeMX.AI is not available yet, I made a simple agent that runs on PC.

Just run [this agent](./tensorflow/agent.py).

```
<<< (17) this is framenco_guitar (85.7%) >>>
blues_harp: 0.0%
classical_guitar: 13.0%
framenco_guitar: 85.7%
piano: 0.5%
tin_whistle: 0.0%
```


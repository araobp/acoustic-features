# CNN experiments with Keras/TensorFlow

The results: about 90% accuracy has been achieved, so it is satisfying.

### Jupyter Notebook of this experiment

I have made CNN experiments as follows:

- [CNN experiments on musical instruments recognition (Jupyter Notebook)](./CNN_for_AED.ipynb)
- [CNN experiments on human activity in a living room (Jupyter Notebook)](./CNN_for_AED_living_room.ipynb)
- [CNN experiments on speech recognition for restaurants (Jupyter Notebook)](./CNN_for_AED_restaurant.ipynb)

The trained CNN model will work OK if the following condition is satisfied:
- use the same MEMS mic with the same filter setting (incl. the same frequency response) on the edge device (STM32L4)
- same environment
- less surrounding noise
- same beam forming setting

### Class labels and data set

#### Mel-spectrogram feature set

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
#### MFCC feature set

MFCCs are good for speech recognition.

```
Classes of speech recognition:
- umai ("delicious" in Japanese)
- oishii ("delicious" in Japanese)
- mazui ("bad" in Japanese)
- others

Conditions:
- Pre emphasis enabled on the raw data.

I split each 40 MFCCs x 200 strdes data into two 12 x 96 data.

Training data set: 12 MFCCs (12 coeeficients x 96 strides) for each class
Test data set:  12 MFCCs (12 coeeficients x 96 strides)  for each class
```

### Using the trained CNN model

I am looking forward to CubeMX.AI: https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html

Since CubeMX.AI is not available yet, I made a simple agent that runs on PC.

Just run [this agent](./agent.py).

```
<<< (17) this is framenco_guitar (85.7%) >>>
blues_harp: 0.0%
classical_guitar: 13.0%
framenco_guitar: 85.7%
piano: 0.5%
tin_whistle: 0.0%
```

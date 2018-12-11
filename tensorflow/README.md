# CNN experiments with Keras/TensorFlow

The results: about 90% accuracy has been achieved, so it is satisfying.

### Using the oscilloscope GUI to collect data for training CNN

[Step 1] Enter a class label into the class label entry on the GUI.

[Step 2] Press "Mel spectrogram" or "MFCC" button to check if the edge device can transfer feature data to the GUI.

[Step 3] Press "Confirm" button.

[Step 4] Use cursor keys for data collection:

```
          [Up]
     [Left]   [Right]
         [Down]

Up: fetch feature data from the device
Left: move the window left
Right: move the window right
Down: save the data
```

The window is high lighted.

### Jupyter Notebook of this experiment

I have made CNN experiments as follows:

- [CNN experiments on musical instruments recognition (Jupyter Notebook)](./CNN_for_AED.ipynb)
- [CNN experiments on human activity in a living room (Jupyter Notebook)](./CNN_for_AED_living_room.ipynb)
- [CNN experiments on speech recognition for restaurants (Jupyter Notebook)](./CNN_for_AED_restaurant.ipynb)
- [CNN experiments on birds chirping (Jupyter Notebook)](./CNN_for_AED_birds.ipynb)

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
```

### Using the trained CNN model

![](../oscilloscope/screenshots/ml_inference_hibari.jpg)

- [Musical instruments recognition](../oscilloscope/run_inference_music.bat)
- [Birds chirping recognition](../oscilloscope/run_inference_birds.bat)
- [Speech recognition for restaurants](../oscilloscope/run_inference_restaurant.bat)

I am looking forward to CubeMX.AI: https://www.st.com/content/st_com/en/about/innovation---technology/artificial-intelligence.html


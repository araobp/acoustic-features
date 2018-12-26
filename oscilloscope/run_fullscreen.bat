set PYTHONPATH=%PYTHONPATH%;./script
#python ./script/oscilloscope.py COM15 --fullscreen_mode raw_wave
#python ./script/oscilloscope.py COM15 --fullscreen_mode fft --plot_style Solarize_Light2
#python ./script/oscilloscope.py COM15 --fullscreen_mode spectrogram --color_map viridis
#python ./script/oscilloscope.py COM15 --fullscreen_mode mel_spectrogram --color_map magma
python ./script/oscilloscope.py COM15 --fullscreen_mode mfcc --color_map seismic
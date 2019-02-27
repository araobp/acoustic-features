set PYTHONPATH=%PYTHONPATH%;./script

rem python ./script/oscilloscope.py --port COM15 --fullscreen_mode raw_wave
rem python ./script/oscilloscope.py COM15 --fullscreen_mode fft --plot_style Solarize_Light2
rem python ./script/oscilloscope.py COM15 --fullscreen_mode spectrogram --color_map viridis
rem python ./script/oscilloscope.py COM15 --fullscreen_mode mfcc --color_map seismic
python ./script/oscilloscope.py COM15 --fullscreen_mode mfsc --color_map magma

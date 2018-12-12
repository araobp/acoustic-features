set PYTHONPATH=%PYTHONPATH%;../oscilloscope/script

python ../oscilloscope/script/oscilloscope.py COM15 --model_file ../dataset/data_music/cnn_for_aed_20181127192236.h5 --class_file ../dataset/data_music/class_labels.yaml --windows "((0,64,40), (64,128,40), (128,192,40))"
set PYTHONPATH=%PYTHONPATH%;../oscilloscope/script

python ../oscilloscope/script/oscilloscope.py COM15 --model_file ../dataset/data_restaurant/cnn_for_aed_restaurant_20181218192021.h5 --class_file ../dataset/data_restaurant/class_labels.yaml --windows "((0,96,35), (24,120,35), (48,144,35), (72, 168, 35), (96, 192, 35))"

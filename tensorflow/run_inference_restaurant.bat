set PYTHONPATH=%PYTHONPATH%;../oscilloscope/script

python ../oscilloscope/script/oscilloscope.py COM15 --model_file ../dataset/data_restaurant/cnn_for_aed_restaurant_20181218192021.h5 --class_file ../dataset/data_restaurant/class_labels.yaml --windows "((0,96,36), (24,120,36), (48,144,36), (72, 168, 36), (96, 192, 36))"

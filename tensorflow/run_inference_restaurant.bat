set PYTHONPATH=%PYTHONPATH%;../oscilloscope/script

python ../oscilloscope/script/oscilloscope.py COM15 --model_file ../dataset/data_restaurant/cnn_for_aed_restaurant_20181127193826.h5 --class_file ../dataset/data_restaurant/class_labels.yaml --windows "((0,96,12), (24,120,12), (48,144,12), (72, 168, 12 ), (96, 192, 12))"

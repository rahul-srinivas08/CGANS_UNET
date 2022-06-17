# cGAN - unet segmentation on BSUID
## Overview
## data
.https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset/code



## cGAN-based Segmentation
In order to improve the performance, I designed a conditional Generative Adversarial Network (cGAN) shown below. Backbone as in U-Net. 


## Results


### Quantitative 
| Model  | Dice Measure |
| ------------- | ------------- |
|  cGAN backbone unet  | 0.69 |

## Dependencies
 - [x] Pytorch >= 0.4.0
 - [x] Python >= 3.5
 - [x] Numpy 

## To train and reproduce the results:
- [x] Set path to the training and validation data and the code.
- [x] Run main.py to train model using cGAN,set path and name of datset in main.py


## For testing, run:
- [x] Set path to the trained model in test.py line 95
- [x] Run test.py
- [x] Predicted maps from test image will be in /test_results

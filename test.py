import argparse
import os
import numpy as np
import math
import itertools
import time
import datetime
import sys

import torchvision.transforms as transforms
from torchvision.utils import save_image
import glob

from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

from torch.utils.data import Dataset
from PIL import Image
from models import GeneratorUNet

from datasets import ImageDataset
import numpy.matlib

import torch.nn as nn
import torch.nn.functional as F
import torch


def dice_coeff(seg, gt):
    smooth = .0001
    return (np.sum(seg[gt == 1])*2.0 + smooth) / (np.sum(seg) + np.sum(gt) + smooth)

def sample_images(imgs, model, path, idx=None,save=False):
    """Saves a generated sample from the test set"""
    true_map = Variable(imgs['B'].type(Tensor))
    save_image(true_map, os.path.join(path, 'test_results/gt', str(idx)) +'.jpg', normalize=True)
    with torch.no_grad():
        fake_B = model(Variable(imgs['A'].type(Tensor)))
    if save:
        save_image(fake_B, os.path.join(path, 'test_results/pred_map', str(idx)) +'.jpg', normalize=True)
    return fake_B


def evaluationMetric(image, thresh, path):
    print(image)
    path = os.path.join(path, 'test_results/pred_map/')
    map_GT = Image.open(image)
    map_pred = Image.open(os.path.join(path, image.split('/')[-1]))
    w, h = map_GT.size

    # Binarize the prediction and groundtruth
    true_labels = np.reshape(np.asarray(map_GT)[:,:,1], (w*h,1))
    true_labels = np.where(true_labels > thresh, 1, 0)
    pred_labels = np.reshape(np.asarray(map_pred)[:,:,1], (w*h,1))
    pred_labels = np.where(pred_labels > thresh, 1, 0)

    ##Dice Coeff
    dice = dice_coeff(pred_labels,true_labels)

    return dice

parser = argparse.ArgumentParser()
parser.add_argument('--dataset_name', type=str, default=" breast", help='name of the dataset')
parser.add_argument('--n_cpu', type=int, default=1, help='number of cpu threads to use during batch generation')
parser.add_argument('--img_height', type=int, default=512, help='size of image height')
parser.add_argument('--img_width', type=int, default=512, help='size of image width')
parser.add_argument('--mod', type=int, default=3, help='generator saved index')
parser.add_argument('--n_residual_blocks', type=int, default=6, help='number of residual blocks in generator')
parser.add_argument('--path', type=str, default='./b_2_data', help='path to code and data')


opt = parser.parse_args()
print(opt)

transforms_ = [ transforms.Resize((opt.img_height, opt.img_width), transforms.InterpolationMode.BICUBIC),
                transforms.ToTensor(),
                transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))]
transforms_b_val = [transforms.Resize((opt.img_height, opt.img_width), transforms.InterpolationMode.BICUBIC),
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,))]
test_dataloader = DataLoader(ImageDataset(os.path.join(opt.path, "%s" % opt.dataset_name), transforms_=transforms_,transforms_b_ = transforms_b_val, mode="test"),
                          batch_size=1, shuffle=False, num_workers=1)

# Initialize generator and discriminator
cuda = True if torch.cuda.is_available() else False

# Tensor type
Tensor = torch.cuda.FloatTensor if cuda else torch.FloatTensor

generator = GeneratorUNet()

if cuda:
    generator = torch.nn.DataParallel(generator).cuda()
#pass pretrained model
generator.load_state_dict(torch.load(os.path.join('./saved_model/breast/generator_100.pth')))
generator.eval()

def main():
    elapse = []
    os.makedirs(os.path.join(opt.path, 'test_results/gt/'), exist_ok=True)
    os.makedirs(os.path.join(opt.path, 'test_results/image/'), exist_ok=True)
    os.makedirs(os.path.join(opt.path, 'test_results/pred_map/'), exist_ok=True)
    for i, image in enumerate(test_dataloader):
        print('Testing image ', i)
        start = time.process_time()
        sample_images(image, generator, opt.path, idx=i, save=True)
        elapsed = (time.process_time() - start)
        elapse.append(elapsed)
        print(elapsed)
        save_image(image['A'], os.path.join(opt.path,'test_results/image/', str(i) +'.jpg'), normalize=True)
    print('Average testing time is ', np.mean(elapse))

    #######################
    BER_avg   = []
    dice_avg = []
    for file in glob.glob(os.path.join(opt.path, 'test_results/gt/**/*.jpg'), recursive=True):
        thresh = 200  # grayscale intensity
        dice = evaluationMetric(file, thresh, opt.path)
        dice_avg.append(dice)
    #print(float(len(dice_avg)))
    print(sum(dice_avg) / float(len(dice_avg)))


if __name__ == "__main__":
    main()


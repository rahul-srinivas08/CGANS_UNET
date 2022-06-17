import glob
import random
import os
import numpy as np

from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as transforms
import torch

class ImageDataset(Dataset):
    def __init__(self, root, transforms_=None,transforms_b_ = None, mode='train'):
        self.transform = transforms.Compose(transforms_)
        self.transforms_b = transforms.Compose(transforms_b_)
        self.files = sorted(glob.glob(os.path.join(root, mode,"images") + '/*.*'))
        self.file_1 = sorted(glob.glob(os.path.join(root, mode,"masks") + '/*.*'))

    def __getitem__(self, index):

        #img = Image.open(self.files[index % len(self.files)])
        img_A = Image.open(self.files[index % len(self.files)])
        img_B = Image.open(self.file_1[index % len(self.file_1)])
        img_B = img_B.convert('1')
        seed = np.random.randint(2147483647)  # make a seed with numpy generator
        random.seed(seed)  # apply this seed to img tranfsorms
        img_A = self.transform(img_A)
        random.seed(seed)  # apply this seed to target tranfsorms
        img_B = self.transforms_b(img_B)

        return {'A': img_A, 'B': img_B}

    def __len__(self):
        return len(self.files)

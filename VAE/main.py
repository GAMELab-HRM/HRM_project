import torch
import torch.nn as nn 
import torchvision 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
from torch.utils.data import DataLoader
from data import HRMdataset
from model import VAE
from torchsummaryX import summary






if __name__ == "__main__":
    data_path = '../train/*.CSV'
    train_dataset = HRMdataset(data_path)
    train_loader = DataLoader(dataset=train_dataset, batch_size=32, shuffle=True)
    
    model = VAE(input_channels=1)
    temp = torch.zeros(1,1,240,36)
    
    summary(model, temp)
from numpy import poly
import numpy as np
import pandas as pd 
import torch 
import torch.nn as nn
from torch.nn.modules.activation import ReLU
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from sklearn.svm import SVC
from torchsummaryX import summary

def read_csv_data(path):
    df = pd.read_csv(path, encoding='big5')
    data = df.iloc[:, 1:-1].values
    label = df.iloc[:, -1].values
    return data, label 

# define Neural Network 
class NN(nn.Module):
    """Some Information about NN"""
    def __init__(self, input_features):
        super(NN, self).__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_features, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64,16),
            nn.ReLU(),
            nn.Linear(16,10),
            nn.Softmax(dim=1)
        )
        
    def forward(self, x):
        return self.mlp(x)
# create custom dataset
class HRMdataset(Dataset):
    def __init__(self, path):
        self.data, self.label = read_csv_data(path)
        
    def __getitem__(self, index):
        return self.data[index], self.label[index]
    
    def __len__(self):
        return len(self.data)


def SVM_1():
    classifier = SVC(C=5, cache_size=5000, max_iter=200, degree=5, gamma='auto')
    return classifier


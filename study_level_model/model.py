from numpy import poly
import numpy as np
import pandas as pd 
import torch 
import torch.nn as nn
from torch.nn.modules.activation import ReLU
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from torchsummaryX import summary
from sklearn.preprocessing import MinMaxScaler, StandardScaler

def read_csv_data(path):
    df = pd.read_csv(path, encoding='big5')
    # 1~57 是沒有考慮contraction vigor contraction pattern的時候
    # 因為若把contraction vigor、contraction pattern做one-hot encoding ，input dimension可能會不一樣
    data = df.iloc[:, 1:57].values
    label = df.iloc[:, -1].values
    return data, label 

def get_scaler(data):
    # 這個scaler預設要用所有的taining data來fit
    scaler = MinMaxScaler()
    scaler.fit(data)
    return scaler 

# define Neural Network 
class NN(nn.Module):
    """Some Information about NN"""
    def __init__(self, input_features, class_num):
        super(NN, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(input_features, 150),
            nn.LeakyReLU(),
            nn.Dropout(0.5),
            nn.Linear(150, 50),
            nn.LeakyReLU(),
            nn.Dropout(0.5),
            nn.Linear(50,class_num),
        )
        #self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        return self.block(x)
    
# create custom dataset
class HRMdataset(Dataset):
    def __init__(self, path):
        self.data, self.label = read_csv_data(path)
        #scaler = get_scaler(self.data)
        #self.transform_data = scaler.transform(self.data)

    def __getitem__(self, index):
        #return self.transform_data[index], self.label[index]
        return self.data[index], self.label[index]

    def __len__(self):
        return len(self.data)

class DatasetFromSubset(Dataset):
    def __init__(self, datas, labels, indices):
        self.data = datas[indices]
        self.label = labels[indices]

    def __getitem__(self, index):
        return self.data[index], self.label[index]

    def __len__(self):
        return len(self.data)

def train_normalization(train_dataset):
    scaler = MinMaxScaler()
    scaler.fit(train_dataset.data)
    train_dataset.data = scaler.transform(train_dataset.data)
    return train_dataset, scaler 

def test_normalization(test_dataset, train_scaler):
    test_dataset.data = train_scaler.transform(test_dataset.data)
    return test_dataset 

def RFclassifier():
    classifier = RandomForestClassifier(n_estimators=100)
    return classifier 
    
def SVM_1():
    classifier = SVC(C=5, cache_size=5000, max_iter=200, degree=5, gamma='auto')
    return classifier



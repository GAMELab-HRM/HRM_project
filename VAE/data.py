from torch.utils.data.dataset import Dataset
import torch, os, glob 
import numpy as np 
import pandas as pd 

# config
data_path = '../train/*.CSV'

def get_data(path):
    res = glob.glob(path)
    ans = []
    for r in res:
        t = r.split('-')[1]
        ans.append(t[:-4])

    return res, ans

def read_csv_data(path):
    df = pd.read_csv(path, encoding='big5')
    sensors = [' P' + str(i) for i in range(1,21)] # 22個sensor p1~p22
    hrm = df[:][sensors].values
    return hrm 

# create custom dataset
class HRMdataset(Dataset):
    def __init__(self, path):
        self.data, self.label = get_data(path)
        
    def __getitem__(self, index):
        hrm_data = read_csv_data(self.data[index])
        return hrm_data, self.label[index]
    def __len__(self):
        return len(self.data)


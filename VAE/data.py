from torch.utils.data.dataset import Dataset
import torch, os, glob 

# config
data_path = '../train/*.CSV'

def get_data(path):
    res = glob.glob(path)
    ans = []
    for r in res:
        t = r.split('-')[1]
        ans.append(t[:-4])

    return res, ans
res, ans = get_data(data_path)

# create custom dataset
class HRMdataset(Dataset):
    def __init__(self, path):
        self.data, self.label = get_data(path)
        pass 
    def __getitem__(self, index):
        return self.data[index], self.label[index]
    def __len__(self):
        return len(self.data)

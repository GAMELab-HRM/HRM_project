from torch import optim
from model import HRMdataset, DatasetFromSubset, NN, train_normalization, test_normalization
from torch.utils.data import DataLoader
from torchsummaryX import summary
from torch.autograd import Variable
from qqdm import qqdm
import torch 
import torch.nn as nn 
import matplotlib.pyplot as plt

# hyper params 
BATCH_SIZE = 1
epochs = 20
lr = 1e-3

def compute_accuracy(dataset, model):
    total = len(dataset)
    temp_dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
    model.eval()
    total = len(dataset)
    correct = 0 
    
    for (data,label) in temp_dataloader:
        data = Variable(data)
        out = model(data.float())
        _, predicted = torch.max(out,dim=1)
        predicted = predicted.numpy()
        label = label.numpy()
        for i in range(len(label)):
            if predicted[i] == label[i]:
                correct+=1
            else:
                print(predicted[i], label[i])
    return correct/total

def training():
    # prepare dataset
    all_dataset = HRMdataset("training_data/training.csv")
    train_size = int(0.7*len(all_dataset))
    test_size = len(all_dataset)-train_size
    train_dataset, test_dataset = torch.utils.data.random_split(all_dataset, [train_size, test_size], generator=torch.Generator().manual_seed(40))

    # split train/test dataset 
    train_dataset = DatasetFromSubset(train_dataset.dataset.data, train_dataset.dataset.label, train_dataset.indices)
    test_dataset = DatasetFromSubset(test_dataset.dataset.data, test_dataset.dataset.label, test_dataset.indices)
    
    # dataset normalization
    train_dataset, train_scaler = train_normalization(train_dataset)
    test_dataset = test_normalization(test_dataset, train_scaler)
    
    # create train/test dataloader
    train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=True)    

    
    # define model 
    model = NN(input_features=101, class_num=3)

    # optimizer & Loss function
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    loss_record = []
    # start training 
    for e in range(epochs):
        progress_bar = qqdm(train_dataloader)
        for (data, label) in progress_bar:
            data = Variable(data)
            out = model(data.float())

            loss = criterion(out, label.long())

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            progress_bar.set_infos({
                "Loss":round(loss.item(),7),
                "Epoch":e+1,
            })

    print("Train Acc:\t", compute_accuracy(train_dataset, model))
    print("Test Acc:\t", compute_accuracy(test_dataset, model))


if __name__ == "__main__":
    training()
from model import HRMdataset, DatasetFromSubset, NN, train_normalization, test_normalization
from torch.utils.data import DataLoader
from torchsummaryX import summary
from torch.autograd import Variable
from qqdm import qqdm
import torch, random
import torch.nn as nn 
import numpy as np 
import torchmetrics
import matplotlib.pyplot as plt

# Seed
seed = 123
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
np.random.seed(seed)
random.seed(seed)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

# hyper params 
BATCH_SIZE = 3
epochs = 40
lr = 0.001
class_number = 4
metric_acc = torchmetrics.Accuracy()
metric_valid_acc = torchmetrics.Accuracy()
metric_acc.to("cuda")
metric_valid_acc.to("cuda")


def compute_accuracy2(dataset, model):
    correct = 0
    total = 0
    model.eval()
    temp_dataloader = DataLoader(dataset, batch_size=3, shuffle=True)
    for (data, label) in temp_dataloader:
        data = Variable(data)
        out = model(data.float())
        _, predicted = torch.max(out.data, 1)
        total+=label.size(0)
        correct+=(predicted==label).sum().item()
    return correct/total

def compute_accuracy(dataset, model):
    total = len(dataset)
    temp_dataloader = DataLoader(dataset, batch_size=3, shuffle=True)
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
            print("Predicted:\t",predicted[i],'\t',"Label:\t",label[i])
            if predicted[i] == label[i]:
                correct+=1
            else:
                pass
                #print(predicted[i], label[i])
    return correct/total

def draw_loss(train_loss, valid_loss):
    plt.plot(train_loss, label = 'train loss')
    plt.plot(valid_loss, label = 'valid loss')
    plt.xlabel("Epoch")
    plt.ylabel('Loss')
    plt.legend()
    plt.grid()
    plt.show()

def draw_acc(train_acc, valid_acc):
    plt.plot(train_acc, label = "train acc")
    plt.plot(valid_acc, label = "valid acc")
    plt.xlabel("Epoch")
    plt.ylabel("Acc")
    plt.legend()
    plt.grid()
    plt.show()

def training():
    # prepare dataset
    all_dataset = HRMdataset("training_data/training_concat.csv")
    train_size = int(0.67*len(all_dataset))
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
    model = NN(input_features=136, class_num=class_number)
    summary(model, torch.zeros(1, 136))
    # optimizer & Loss function
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    loss_record = []
    valid_record = []
    train_acc_record = []
    valid_acc_record = []

    # start training 
    for e in range(epochs):
        progress_bar = qqdm(train_dataloader)
        running_loss = 0.0
        for (data, label) in progress_bar:
            data = Variable(data)
            out = model(data.float())

            loss = criterion(out, label.long())
            acc = metric_acc(out, label.long())


            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss+=loss.item()*data.size(0)
            progress_bar.set_infos({"Loss":round(loss.item(),7), "Epoch":e+1,})

        # validation (using testing data)
        model.eval()
        valid_loss = 0
        for (data, label) in test_dataloader:
            data = Variable(data)
            out = model(data.float())
            loss = criterion(out, label.long())
            acc = metric_valid_acc(out, label.long())
            valid_loss+=loss.item()*data.size(0)
        
        total_train_acc = metric_acc.compute()
        total_valid_acc = metric_valid_acc.compute()


        train_acc_record.append(round(total_train_acc.cpu().item(), 4))
        valid_acc_record.append(round(total_valid_acc.cpu().item(), 4))


        metric_acc.reset()
        metric_valid_acc.reset()
        epoch_valid_loss = valid_loss / len(test_dataloader)
        epoch_loss = running_loss / len(train_dataloader)
        valid_record.append(round(epoch_valid_loss, 4))
        loss_record.append(round(epoch_loss, 4))
        model.train()


    draw_loss(loss_record, valid_record)
    draw_acc(train_acc_record, valid_acc_record)
    print("Train Acc:\t", compute_accuracy2(train_dataset, model))
    print("Test Acc:\t", compute_accuracy2(test_dataset, model))
    print("Train Loss: ")
    print(loss_record)
    print("Valid Loss:")
    print(valid_record)

if __name__ == "__main__":
    training()
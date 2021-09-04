import torch, torchvision
from torch.nn.modules.activation import ReLU 
import torch.nn as nn 
from torch.autograd import Variable

class VAE(nn.Module):
    def __init__(self, input_channels,):
        super(VAE, self).__init__()
        self.encoder = nn.Sequential(
            # input channel, output channels, kernel size, stride, padding
            nn.Conv2d(input_channels, 8, kernel_size=(162, 3), stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(8, 16, kernel_size=(15, 3), stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(16, 32, kernel_size=(9,3), stride=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Flatten(),
            
        )
        self.fc1 = nn.Linear(128, 32)
        self.fc2 = nn.Linear(128, 32)
        
    def reparameterize(self, mean, variance):
        std = variance.mul(0.5).exp_()
        esp = torch.randn(*mean.size())
        z = mean + std * esp
        return z 
    
    def bottleneck(self, h):
        mean, variance = self.fc1(h), self.fc2(h)
        z = self.reparameterize(mean, variance) # z = u + exp(std) * e 
        return z, mean, variance  

    def encode(self, x):
        h = self.encoder(x) # h = encoder output
        z, mean, variance = self.bottleneck(h) # compute z 
        return z, mean, variance

    def decode(self, x):
        pass 

    def forward(self, x):
        z, mean, variance = self.encode(x)
        return z, mean, variance
    

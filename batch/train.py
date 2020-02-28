import argparse
import os
import datetime
from shutil import copyfile
from common import context, client
from adapters import pytorch
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data.float())   #why?
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        print('Train Epoch: {} [{}]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), loss.item()))



def main():
    # Training settings
    c = context.Context(account_name = 'persstgppewestus2', \
        account_key = 'JhSj6OfM5hkoboXeyQTn6xeHBy6J+kpwJW8cCVMP4CvyZfxD66BFtE4KTl8+EPIVmFzpM6CLn0fgYuR1HuqnqA==', \
        container='d7eedad9c2264d4a822dda754455fa66', \
        folder = '20200225213524')

    start = datetime.datetime(2020, 2, 27)

    end = datetime.datetime(2018, 2, 28)

#    iterator = client.TenantStorageIterator(c, start, end)
    iterator = open('/Users/ataymano/data/byom/27_0.json', 'r')

    ds = pytorch.Logs(iterator, pytorch.ToCbTensor())
    train_loader = torch.utils.data.DataLoader(ds, batch_size = 2, num_workers=0)
    torch.manual_seed(1)
    device = torch.device("cpu")

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=1.0)

    scheduler = StepLR(optimizer, step_size=1, gamma=0.7)
    for epoch in range(1, 3):
        train(model, device, train_loader, optimizer, epoch)
        scheduler.step()

    pytorch.Model.export(model, device, '/Users/ataymano/data/byom/current')

if __name__ == '__main__':
    main()
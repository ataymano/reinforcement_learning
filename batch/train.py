import argparse
import os
import datetime
from shutil import copyfile
from common import context
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
    c = context.Context(account_name = 'ataymanodev', account_key = 'WxDBTcax+bxLNc6ECKWLKU0ZTj5ZKUV67ei5eiyi2dR2NlONZrh8jby9YpONf8sHH8kJGA9ZAz6FDR9CQOyd2g==', container='small', folder = 'folder')

    start = datetime.datetime(2018, 10, 16)

    end = datetime.datetime(2018, 10, 21)

    ds = pytorch.Logs(c, start, end, pytorch.ToTensor())
    train_loader = torch.utils.data.DataLoader(ds, batch_size = 2, num_workers=0)
  #  parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
  #  parser.add_argument('--batch-size', type=int, default=64, metavar='N',
  #                      help='input batch size for training (default: 64)')
  #  parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
  #                      help='input batch size for testing (default: 1000)')
  #  parser.add_argument('--epochs', type=int, default=14, metavar='N',
  #                      help='number of epochs to train (default: 14)')
  #  parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
  #                      help='learning rate (default: 1.0)')
  #  parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
  #                      help='Learning rate step gamma (default: 0.7)')
  #  parser.add_argument('--no-cuda', action='store_true', default=False,
  #                      help='disables CUDA training')
  #  parser.add_argument('--seed', type=int, default=1, metavar='S',
  #                      help='random seed (default: 1)')
  #  parser.add_argument('--log-interval', type=int, default=10, metavar='N',
  #                      help='how many batches to wait before logging training status')

  #  parser.add_argument('--save-model', action='store_true', default=False,
  #                      help='For Saving the current Model')
  #  args = parser.parse_args()
  #  use_cuda = not args.no_cuda and torch.cuda.is_available()

    torch.manual_seed(1)

    device = torch.device("cpu")

 #   kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}
 #   train_loader = torch.utils.data.DataLoader(
 #       datasets.MNIST('../data', train=True, download=True,
 #                      transform=transforms.Compose([
 #                          transforms.ToTensor(),
 #                          transforms.Normalize((0.1307,), (0.3081,))
 #                      ])),
 #       batch_size=args.batch_size, shuffle=True, **kwargs)
 #   test_loader = torch.utils.data.DataLoader(
 #       datasets.MNIST('../data', train=False, transform=transforms.Compose([
 #                          transforms.ToTensor(),
 #                          transforms.Normalize((0.1307,), (0.3081,))
  #                     ])),
  #      batch_size=args.test_batch_size, shuffle=True, **kwargs)

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=1.0)

    scheduler = StepLR(optimizer, step_size=1, gamma=0.7)
    for epoch in range(1, 3):
        train(model, device, train_loader, optimizer, epoch)
        scheduler.step()

#    if args.save_model:
#        torch.save(model.state_dict(), "mnist_cnn.pt")

if __name__ == '__main__':
        main()
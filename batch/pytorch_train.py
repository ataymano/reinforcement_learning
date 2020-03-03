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


def train(model, device, train_loader, optimizer):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data.float())   #why?
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        print('Train: [{}]\tLoss: {:.6f}'.format(
                batch_idx * len(data), loss.item()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--output-dir', type=str, default='outputs')
    parser.add_argument('--account-name', type=str)
    parser.add_argument('--account-key', type=str)
    parser.add_argument('--container', type=str)
    parser.add_argument('--folder', type=str)
    parser.add_argument('--start-date', type=str)
    parser.add_argument('--end_date', type=str)
    args = parser.parse_args()

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    c = context.Context(account_name = args.account_name, \
        account_key = args.account_key, \
        container = args.container, \
        folder = args.folder)    

    start = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')

    iterator = client.TenantStorageIterator(c, start, end)
#    iterator = open('/Users/ataymano/data/byom/27_0.json', 'r')

    ds = pytorch.IterableLogs(iterator, pytorch.ToCbTensor())
    train_loader = torch.utils.data.DataLoader(ds, batch_size = args.batch_size, num_workers=0)
    torch.manual_seed(1)
    device = torch.device("cpu")

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=1.0)

    scheduler = StepLR(optimizer, step_size=1, gamma=0.7)
    train(model, device, train_loader, optimizer)
    scheduler.step()

    model_path = os.path.join(output_dir, 'current.onnx')
    pytorch.Model.export(model, device, model_path)

if __name__ == '__main__':
    main()
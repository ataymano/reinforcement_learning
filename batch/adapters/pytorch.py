from torch.utils.data.dataset import IterableDataset, Dataset
from torch import tensor, randn, onnx, is_tensor

class IterableLogs(IterableDataset):
    def __init__(self, iterator, transform = None):
        self.it = iterator
        self.transform = transform

    def __iter__(self):
        for l in self.it:
            yield self.transform(l) if self.transform else l

class Logs(Dataset):
    def __init__(self, df, transform = None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        line = self.df.iloc[idx]['lines']
        return self.transform(line) if self.transform else line

class ToCbTensor(object):
    def __init__(self):
        pass

    def __call__(self, example):
        from common.parser import CbDsjsonParser
        parsed = CbDsjsonParser.parse(example)

        #only for 1 tensor so far
        features = {}
        for k, v in parsed['features'].items():
            features = tensor(v)
            break

        return features, parsed['label']

class Model:
    @staticmethod
    def export(model, device, path):
        dummy_input = randn(1, 1, 28, 28, device=device)
        onnx.export(model, dummy_input, path)

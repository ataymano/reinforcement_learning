from torch.utils.data.dataset import IterableDataset
from torch import tensor

class Logs(IterableDataset):
    def __init__(self, iterator, transform = None):
        self.it = iterator
        self.transform = transform

    def __iter__(self):
        for l in self.it:
            yield self.transform(l) if self.transform else l

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

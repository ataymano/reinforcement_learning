from torch.utils.data.dataset import IterableDataset
from torch import tensor
from common import client

class Logs(IterableDataset):
    def __init__(self, context, start, end, transform = None):
        self.it = client.TenantStorageIterator(context, start, end)
        self.transform = transform

    def __iter__(self):
        for l in self.it:
            yield self.transform(l) if self.transform else l

class ToTensor(object):
    def __init__(self):
        pass

    def __call__(self, example):
        from common import parser
        parsed = parser.Base64Loader.load(example)

        #only for 1 tensor so far
        features = {}
        for k, v in parsed['features'].items():
            features = tensor(v)
            break

        return features, parsed['label']

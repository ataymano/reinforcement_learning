import collections.abc
import pickle

class Index:
    def __init__(self, path):
        with open(path, 'r') as f:
            self.index = []
            while f.readline():
                self.index.append(f.tell())

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        import os.path
        indx_path = path + '.indx'
        if os.path.exists(indx_path):
            with open(indx_path, 'rb') as f:
                return pickle.load(f)
        else:
            return Index(path)

    def count(self):
        return len(self.index)

    def get(self, f, i):
        if i >= self.count():
            raise 'Out of range'
        f.seek(0 if i == 0 else self.index[i - 1], 0)
        return f.readline()

class IndexedFile(collections.abc.Sequence):
    def __init__(self, path):
        import os.path
        self.f = open(path, 'r')
        self.index = Index.load(path)

    def __getitem__(self, i):
        if i >= self.index.count():
            raise 'Out of range'

        return self.index.get(self.f, i)

    def __len__(self):
        return self.index.count()
        
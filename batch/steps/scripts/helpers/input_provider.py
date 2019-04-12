import os
import glob

class cache_provider:
    def __init__(self, folder):
        self.folder = folder

    def get(self):
        pattern=os.path.join(self.folder, '*.cache')
        return sorted(list(glob.glob(pattern)))

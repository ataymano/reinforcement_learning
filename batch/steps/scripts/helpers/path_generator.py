import os
class folder_path_generator:
    def __init__(self, folder, create = True):
        self.folder = folder
        if create:
            os.makedirs(folder, exist_ok=True)

    def get(self, input, suffix):
        return os.path.join(self.folder, os.path.basename(input)) + '.' + suffix

if __name__ == '__main__':
    multiprocessing.freeze_support()

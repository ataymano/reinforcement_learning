import os
from helpers import vw_opts

class move_to_folder_path_generator:
    def __init__(self, folder, create = True):
        self.folder = folder
        if create:
            os.makedirs(folder, exist_ok=True)

    def get(self, input, suffix):
        return os.path.join(self.folder, os.path.basename(input)) + '.' + suffix

class model_path_generator(move_to_folder_path_generator):
    def __init__(self, folder, create = True):
        super().__init__(folder, create)

    def get(self, cache, opts):
        return super().get(cache, str(_hash(opts)) + '.vw')

class cache_path_generator(move_to_folder_path_generator):
    def __init__(self, folder, create = True):
        super().__init__(folder, create)

    def get(self, cache, opts):
        return super().get(c, 'cache')

class pred_path_generator(move_to_folder_path_generator):
    def __init__(self, folder, create = True):
        super().__init__(folder, create)

    def get(self, cache, policy_name):
        prediction_dir = os.path.join(self.folder, os.path.basename(cache))
        tmp = move_to_folder_path_generator(prediction_dir)
        return tmp.get(policy_name, 'pred')

def _hash(opts={}):
    return hash(vw_opts.to_commandline(opts))

if __name__ == '__main__':
    multiprocessing.freeze_support()

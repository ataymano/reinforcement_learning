import subprocess
import sys
import re
import os


class MoveToFolderPathGenerator:
    def __init__(self, folder, create = True):
        self.folder = folder
        if create:
            os.makedirs(folder, exist_ok=True)

    def get(self, input, suffix):
        return os.path.join(self.folder, os.path.basename(input)) + '.' + suffix


class Vw:
    def __init__(self, path, opts, tmp_folder):
        self.path = path
        self.opts = {"#base": opts}
        self.model_path_generator = MoveToFolderPathGenerator(tmp_folder)

    @staticmethod
    def _run(command):
        process = subprocess.Popen(
            command.split(),
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        return error

    def _build_command(self):
        args = ''
        for key, val in self.opts.items():
            args = ' '.join([args, key if not key.startswith('#') else '', str(val)])
        return ' '.join([self.path, re.sub(' +', ' ', args)])

    def train(self, input_path):
        self.opts['-d'] = input_path
        self.opts['-f'] = self.model_path_generator.get(input_path, 'vw')
        self._run(self._build_command())
        self.opts['-i'] = self.opts['-f']

    def get_model(self):
        if '-i' in self.opts.keys():
            return self.opts['-i']
        return None


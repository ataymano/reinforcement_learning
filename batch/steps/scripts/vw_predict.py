# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import subprocess
import datetime
from azureml.core.run import Run
from helpers import utils

def Log(key, value):
    logger = Run.get_context()
    logger.log(key, value)
    print(key + ': ' + str(value))


class vw_wrapper:
    def __init__(self, vw_path, args):
        self.path = vw_path
        self.args = args

    def parse_vw_output(self, txt):
        result = {}
        for line in txt.split('\n'):
            if '=' in line:
                index = line.find('=')
                key = line[0:index].strip()
                value = line[index+1:].strip()
                result[key] = value
        return result

    def process(self, input, output):
        command = self.path + ' ' + self.args + ' --cache_file ' + input + ' -p ' + output
        print('Processing: ' + command)
        process = subprocess.Popen(command.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return self.parse_vw_output(error)

print("Estimating vw model...")

parser = argparse.ArgumentParser("predict")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="output folder")
parser.add_argument("--command", type=str, help="command")
parser.add_argument("--name", type=str, help="command name")

args = parser.parse_known_args()

Log("Input folder", args[0].input_folder)
Log("Output folder", args[0].output_folder)
with open(args[0].command, 'r') as f_command:
    c = f_command.readline()

Log("Command", c)
c = c.replace('--cb_adf', '--cb_explore_adf --epsilon 0.2')
Log("Command with exploration: ", c)

if args[0].name is None:
    args[0].name = '_'.join(filter(None, c.replace('-','').split(' ')))

print('Started: ' + str(datetime.datetime.now()))
vw = vw_wrapper(vw_path = '/usr/local/bin/vw', args = c)

counter = 1
while (True):
    input_path = os.path.join(args[0].input_folder, str(counter) + '.cache')
    print('reading cache from: ' + input_path)
    print('cache file exist? ' + str(os.path.isfile(input_path)))

    if os.path.isfile(input_path):
        output_path = os.path.join(args[0].output_folder, 'dataset.' + args[0].name + str(counter) + '.pred')
        command_path = os.path.join(args[0].output_folder, 'dataset.' + args[0].name + '.command')
        os.makedirs(args[0].output_folder, exist_ok=True)
        with open(command_path, 'w+') as f:
            f.write(c)
        result = vw.process(input_path, output_path)
        logger = Run.get_context()
        for key, value in result.items():
            print('key: ' + key)
            print('value: ' + value)
            print('====================')
            try:
                f_value = float(value)
                logger.log(key, f_value)
            except ValueError:
                print("Not a float value. " + key + ": " + value)
        counter += 1
    else:
        break

print('Done: ' + str(datetime.datetime.now()))

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import subprocess
import datetime

from azureml.core.run import Run

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

    def process(self, input):
        command = self.path + ' ' + self.args + ' --cache_file ' + input
        print('Processing: ' + command)
        process = subprocess.Popen(command.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        return self.parse_vw_output(error)

print("Estimating vw model...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--base_command", type=str, help="base command")

#parser.add_argument("--power_t", type=str, help="power_t")
args = parser.parse_known_args()

print("Input folder: %s" % args[0].input_folder)

with open(args[0].base_command, 'r') as f_command:
    command = f_command.readline()

#c = '--cb_adf --dsjson --cb_type ips -l 1e-05 --l1 1e-05 --power_t ' + args.power_t
c = command + ' ' +  ' '.join(args[1])

print("Command: " + c)
print('Started: ' + str(datetime.datetime.now()))
vw = vw_wrapper(vw_path = '/usr/local/bin/vw', args = c)
result = vw.process(os.path.join(args[0].input_folder, 'dataset.cache'))
logger = Run.get_context()
logger.log('Command', c)
for key, value in result.items():
    try:
        f_value = float(value)
        logger.log(key, f_value)
    except ValueError:
        print("Not a float value. " + key + ": " + value)

print('Done: ' + str(datetime.datetime.now()))



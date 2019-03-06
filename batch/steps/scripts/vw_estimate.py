# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import subprocess
import datetime

from azureml.core.run import Run

def Log(key, value):
        logger = Run.get_context()
        logger.log(key, value)
        print(key + ': ' + str(value))

class Vw:
    def __init__(self, vw_path, args):
        self.path = vw_path
        self.args = args

    @staticmethod
    def parse_loss(line):
        try:
            loss_str = line[:line.find(' ')]
            return float(loss_str)
        except ValueError:
            return None

    @staticmethod
    def parse_key_value(line):
        if '=' in line:
            index = line.find('=')
            key = line[0:index].strip()
            value = line[index+1:].strip()
            return (key, value)       
        else:
            return None

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
        for line in iter(process.stderr.readline, ""):
            loss = Vw.parse_loss(line)
            if loss is not None:
                Log('loss_plot', loss)
            else:
                kv = Vw.parse_key_value(line)
                if kv:
                    Log(kv[0], kv[1])
        process.stderr.close()
        return process.wait()

def get_subcommand(fname, index):
    if index == 0:
        return ' '

    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            for result in f:
                index = index - 1
                if index == 0:
                    return result
    return None

print("Estimating vw model...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--base_command", type=str, help="base command")
parser.add_argument("--marginals_index", type=str, help="marginal command index")
parser.add_argument("--interactions_index", type=str, help="interactions command index")

#parser.add_argument("--power_t", type=str, help="power_t")
args = parser.parse_known_args()

Log("Input folder", args[0].input_folder)
Log("Base command path", args[0].base_command)

with open(args[0].base_command, 'r') as f_command:
    command = f_command.readline()


marginals_path = os.path.join(args[0].input_folder, 'marginals.txt')
marg = ' '
if args[0].marginals_index:
    marg = get_subcommand(marginals_path, int(args[0].marginals_index))

inter = ' '
interactions_path = os.path.join(args[0].input_folder, 'interactions.txt')
if args[0].interactions_index:
    inter = get_subcommand(interactions_path,int(args[0].interactions_index))

if '-q' in command:
    tmpparser =  argparse.ArgumentParser("trtmpain")
    tmpparser.add_argument("-q", type=str, help="interactions command index")
    tmpargs = tmpparser.parse_known_args(command.split(' '))
    command = '--cb_adf --dsjson -q ' + tmpargs[0].q

#c = '--cb_adf --dsjson --cb_type ips -l 1e-05 --l1 1e-05 --power_t ' + args.power_t
c = command.rstrip() + ' ' +  ' '.join(args[1])

if marg is not None and inter is not None:
    c = c + ' ' + marg.rstrip() + ' ' + inter.rstrip()
    Log("Command", c)  
    print('Started: ' + str(datetime.datetime.now()))
    vw = Vw(vw_path = '/usr/local/bin/vw', args = c)
    result = vw.process(os.path.join(args[0].input_folder, 'dataset.cache'))

    print('Done: ' + str(datetime.datetime.now()))



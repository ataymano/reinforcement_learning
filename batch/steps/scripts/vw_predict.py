# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
from helpers import utils
from helpers import vw

utils.logger("Generate predictions...")

parser = argparse.ArgumentParser("predict")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="output folder")
parser.add_argument("--command", type=str, help="command")
parser.add_argument("--policy_name", type=str, help="policy name")
args = parser.parse_args()

input_folder = args.input_folder
output_folder = args.output_folder
command = args.command
policy_name = args.policy_name

utils.logger("Cache folder", input_folder)
utils.logger("Prediction folder", output_folder)

with open(command, 'r') as f_command:
    c = f_command.readline()

c = c.replace('--cb_adf', '--cb_explore_adf --epsilon 0.2')

if policy_name is None:
    policy_name = '_'.join(filter(None, c.replace('-', '').split(' ')))
utils.logger("Policy name: ", policy_name)

cache_list = filter(lambda f: '.cache' in f, os.listdir(input_folder))
cache_list = sorted(cache_list)

previous_model = None
for cache_file in cache_list:
    cache_path = os.path.join(input_folder, cache_file)
    cache_file_name, cache_path_extension = os.path.splitext(cache_file)

    prediction_dir = os.path.join(output_folder, policy_name)
    os.makedirs(prediction_dir, exist_ok=True)

    prediction_path = os.path.join(
        prediction_dir,
        '%s.pred' % (cache_file_name)
    )

    command_options = {
        '--cache_file': cache_path,
        '-p': prediction_path
    }

    if previous_model:
        previous_model_path = os.path.join(input_folder, previous_model)
        command_options['-i'] = previous_model_path

    command = vw.build_command(c, command_options)

    previous_model = '%s.vw' % (cache_file_name)
    utils.logger('predict command', command)

    vw.run(command)

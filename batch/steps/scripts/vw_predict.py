# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
from helpers import utils
from helpers import vw

parser = argparse.ArgumentParser("predict")
parser.add_argument("--cache_folder", type=str, help="cache folder")
parser.add_argument("--commands_folder", type=str, help="commands folder")
parser.add_argument("--output_folder", type=str, help="output folder")
args = parser.parse_args()

cache_folder = args.cache_folder
commands_folder = args.commands_folder
output_folder = args.output_folder

utils.logger("Cache folder", cache_folder)
utils.logger("Prediction folder", output_folder)

cache_list = filter(lambda f: '.cache' in f, os.listdir(cache_folder))
cache_list = sorted(cache_list)

for command_file in os.listdir(commands_folder):
    command_file_path = os.path.join(
        commands_folder,
        command_file
    )
    policy_name = command_file.split('_')[0]

    with open(command_file_path, 'r') as f_command:
        c = f_command.readline()
        c = c.replace('--cb_adf', '--cb_explore_adf --epsilon 0.2')

    previous_model = None
    for cache_file in cache_list:
        cache_path = os.path.join(cache_folder, cache_file)
        cache_file_name, cache_path_extension = os.path.splitext(cache_file)

        prediction_dir = os.path.join(output_folder, cache_file_name)
        os.makedirs(prediction_dir, exist_ok=True)

        prediction_path = os.path.join(
            prediction_dir,
            '%s.pred' % (policy_name)
        )

        command_options = {
            '--cache_file': cache_path,
            '-p': prediction_path
        }

        if previous_model:
            previous_model_path = os.path.join(cache_folder, previous_model)
            command_options['-i'] = previous_model_path

        command = vw.build_command(c, command_options)

        previous_model = '%s.vw' % (cache_file_name)
        utils.logger('predict command', command)

        vw.run(command)

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import subprocess
import datetime
import shutil

from azureml.core.run import Run

import argparse
import os
import datetime
import shutil

import itertools

import json
from enum import Enum
import collections

class PropType(Enum):
    NONE = 1
    BASIC = 2
    MARGINAL = 3

def detect_namespaces(j_obj, ns_set, marginal_set):
    prop_type = PropType.NONE
    if (j_obj is None) or type(j_obj) is not dict:
        return prop_type

    # The rule is: recurse into objects until a flat list of properties is found; the
    # nearest enclosing name is the namespace
    for kv_entry in j_obj.items():
        key = kv_entry[0]
        value = kv_entry[1]

        # Ignore entries whose key begins with an '_' except _text
        if key[0] == '_' and key != '_text':
            continue

        if type(value) is list:
            # Unwrap lists so we retain knowledge of the enclosing key name
            for item in value:
                ret_val = detect_namespaces(item, ns_set, marginal_set)
                if ret_val in [PropType.BASIC, PropType.MARGINAL]:
                    ns_set.update([key])
                    if ret_val is PropType.MARGINAL:
                        marginal_set.update([key])
        elif type(value) is dict:
            # Recurse on the value
            ret_val = detect_namespaces(value, ns_set, marginal_set)
            if ret_val in [PropType.BASIC, PropType.MARGINAL]:
                ns_set.update([key])
                if ret_val is PropType.MARGINAL:
                    marginal_set.update([key])
        elif value is not None:
            prop_type = PropType.BASIC

    # If basic properties were found, check if they are actually marginal properties
    if prop_type is PropType.BASIC:
        if j_obj.get('constant', 0) == 1:
            prop_type = PropType.MARGINAL

    return prop_type

def extract_namespaces(fname, auto_lines = 100):
    shared_tmp = collections.Counter()
    action_tmp = collections.Counter()
    marginal_tmp = collections.Counter()

    with open(fname, 'r') as f:
        counter = 0
        for line in f:
            if not line.startswith('{"_label_cost"'):
                continue

            counter += 1
                
            event = json.loads(line)
            # Separate the shared features from the action features for namespace analysis
            if 'c' in event:
                context = event['c']
                action_set = context['_multi']
                del context['_multi']
                detect_namespaces(context, shared_tmp, marginal_tmp)
                # Namespace detection expects object of type 'dict', so unwrap the action list
                for action in action_set:
                    detect_namespaces(action, action_tmp, marginal_tmp)
            else:
                raise ValueError('Error: c not in json:' + line)

            # We assume the schema is consistent throughout the file, but since some
            # namespaces may not appear in every datapoint, check enough points.
            if counter >= auto_lines:
                break
    return ({x[0] for x in shared_tmp}, {x[0] for x in action_tmp}, {x[0] for x in marginal_tmp})   

def iterate_subsets(s):
    for i in range(1, len(s) + 1):
        yield from itertools.combinations(s, i)

def write_marginals(fname, marginals):
    with open(fname, 'w') as f:
        for element in iterate_subsets(marginals):
            f.write('--marginal ' + ''.join(element) + '\n')

def write_interactions(fname, shared, actions):
    interactions = {''.join(x) for x in itertools.product(shared, actions)}
    with open(fname, 'w') as f:
        for element in iterate_subsets(interactions):
            f.write('-q ' + ' -q '.join(element) + '\n')

def extract_interactions_marginals(input_path, output_folder):
    namespaces = extract_namespaces(input_path)
    marginals_path = os.path.join(args.output_folder, 'marginals.txt')
    interactions_path = os.path.join(args.output_folder, 'interactions.txt')
    write_marginals(marginals_path, namespaces[2])
    write_interactions(interactions_path, namespaces[0], namespaces[1])

class Vw:
    @staticmethod
    def _parse_vw_output(txt):
        result = {}
        for line in txt.split('\n'):
            if '=' in line:
                index = line.find('=')
                key = line[0:index].strip()
                value = line[index+1:].strip()
                result[key] = value
        return result

    @staticmethod
    def cache(vw_path, cache_path, input_path):
        command = vw_path + ' --cb_adf --dsjson --cache_file ' + cache_path + ' ' + input_path
        execution = subprocess.Popen(command.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = execution.communicate()
        return Vw._parse_vw_output(error)

def Log(key, value):
        logger = Run.get_context()
        logger.log(key, value)
        print(key + ': ' + str(value))

print("Caching and extracting namespaces...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_path", type=str, help="input path")
parser.add_argument("--output_folder", type=str, help="ouput folder")
args = parser.parse_args()

Log("Input path", args.input_path)
Log("Output folder", args.output_folder)

print('Started: ' + str(datetime.datetime.now()))

os.makedirs(args.output_folder, exist_ok=True)
cache_path = os.path.join(args.output_folder, 'dataset.cache')

Vw.cache(vw_path = '/usr/local/bin/vw', cache_path = cache_path, input_path = args.input_path)
extract_interactions_marginals(args.input_path, args.output_folder)

print('Done: '+ str(datetime.datetime.now()))



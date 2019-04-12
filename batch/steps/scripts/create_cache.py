import argparse
import os
import datetime
import json
from helpers import vw, logger, runtime, environment, runtime, path_generator, input_provider, pool
import collections
import itertools
from enum import Enum


class PropType(Enum):
    NONE = 1
    BASIC = 2
    MARGINAL = 3


def cache(input_folder, output_folder, vw_path, start_date, end_date):
    my_logger = logger.logger(runtime.local())
    my_logger.log_scalar_global('Input folder', input_folder)
    my_logger.log_scalar_global('Output folder', output_folder)

    env = environment.environment(
        vw_path = vw_path,
        runtime = runtime.local(),
        job_pool = pool.seq_pool(),
        txt_provider = input_provider.ps_logs_provider(input_folder, start_date, end_date),
        cache_path_gen = path_generator.cache_path_generator(output_folder))
        
    command = {
        '#method':'--cb_adf',
        '#format':'--dsjson',
        '#saveresume':'--save_resume',
        '#savepercounters':'--preserve_performance_counters'}
    vw.cache(command, env)

#    meta_data_file_path = os.path.join(
#        output_folder,
#        'metadata.json'
#    )


#    metadata = {
#        'log_files': log_files,
#        'date_list': date_list
#    }

#    print('metadata file path: ' + meta_data_file_path)
#    print(metadata)


#    with open(meta_data_file_path, 'w+') as fout:
#        json.dump(metadata, fout)

#    return log_files


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


def extract_namespaces(fname, auto_lines=100):
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
            # Separate the shared features from the action features
            # for namespace analysis
            if 'c' in event:
                context = event['c']
                action_set = context['_multi']
                del context['_multi']
                detect_namespaces(context, shared_tmp, marginal_tmp)
                # Namespace detection expects object of type 'dict',
                # so unwrap the action list
                for action in action_set:
                    detect_namespaces(action, action_tmp, marginal_tmp)
            else:
                raise ValueError('Error: c not in json:' + line)

            # We assume the schema is consistent throughout the file,
            # but since some namespaces may not appear in every datapoint,
            # check enough points.
            if counter >= auto_lines:
                break
    return (
        {x[0] for x in shared_tmp},
        {x[0] for x in action_tmp},
        {x[0] for x in marginal_tmp}
    )


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
    marginals_path = os.path.join(output_folder, 'marginals.txt')
    interactions_path = os.path.join(output_folder, 'interactions.txt')
    write_marginals(marginals_path, namespaces[2])
    write_interactions(interactions_path, namespaces[0], namespaces[1])


def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("create cache")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output_folder", type=str, help="output folder")
    parser.add_argument("--vw", type=str, help="vw path")
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    os.makedirs(args.output_folder, exist_ok=True)

    log_files = extract(
        args.input_folder,
        args.output_folder,
        args.vw,
        datetime.datetime.strptime(args.start_date, date_format),
        datetime.datetime.strptime(args.end_date, date_format)
    )

  #  first_log_file_path = os.path.join(
  #      args.input_folder,
  #      log_files[0]
  #  )
  #  extract_interactions_marginals(
  #      first_log_file_path,
  #      args.output_folder
  #  )


if __name__ == '__main__':
    main()

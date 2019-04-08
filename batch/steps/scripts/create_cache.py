import argparse
import os
import datetime
import json
from helpers import vw
from helpers import utils
import collections
import itertools
from enum import Enum


class PropType(Enum):
    NONE = 1
    BASIC = 2
    MARGINAL = 3


class LogsExtractor:
    class Entry:
        def __init__(
            self,
            file_relative_path,
            file_path,
            previous_date=None,
            current_date=None
        ):
            self.file_relative_path = file_relative_path
            self.file_path = file_path
            self.previous_date = previous_date
            self.current_date = current_date

    @staticmethod
    def _get_log_relative_path(date):
        return 'data/%s/%s/%s_0.json' % (
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )

    @staticmethod
    def iterate_files(folder, start_date, end_date):
        previous_date = None
        for i in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(i)
            log_relative_path = LogsExtractor._get_log_relative_path(
                current_date
            )
            log_path = os.path.join(folder, log_relative_path)
            if os.path.isfile(log_path):
                yield LogsExtractor.Entry(
                    file_relative_path=log_relative_path,
                    file_path=log_path,
                    previous_date=previous_date,
                    current_date=current_date
                )
                previous_date = current_date
        return
        yield


def convert_date_to_str(date):
    return str(date.year) + str(date.month) + str(date.day)


def get_file_name(date, type):
    if date:
        date_str = convert_date_to_str(date)
        if type == 'cache':
            return '%s.cache' % (date_str)
        elif type == 'model':
            return '%s.vw' % (date_str)
    return None


def extract(input_folder, output_folder, start_date, end_date):
    log_files = []
    date_list = []
    for log in LogsExtractor.iterate_files(input_folder, start_date, end_date):
        log_files.append(log.file_relative_path)
        date_list.append(convert_date_to_str(log.current_date))

        cache_path = os.path.join(
            output_folder,
            get_file_name(log.current_date, 'cache')
        )

        previous_model_path = None
        if log.previous_date:
            previous_model_path = os.path.join(
                output_folder,
                get_file_name(log.previous_date, 'model')
            )

        new_model_path = os.path.join(
            output_folder,
            get_file_name(log.current_date, 'model')
        )

        command_options = {
            '--cache_file': cache_path,
            '-d': log.file_path,
            '-f': new_model_path
        }

        if (previous_model_path):
            command_options['-i'] = previous_model_path

        command = vw.build_command_legacy('/usr/local/bin/vw', '', command_options)
        print(command)
        vw.run(command)

    meta_data_file_path = os.path.join(
        output_folder,
        'metadata.json'
    )

    metadata = {
        'log_files': log_files,
        'date_list': date_list
    }

    print('metadata file path: ' + meta_data_file_path)
    print(metadata)

    with open(meta_data_file_path, 'w+') as fout:
        json.dump(metadata, fout)

    return log_files


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
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    utils.logger('Input folder', args.input_folder)
    utils.logger('Output folder', args.output_folder)

    os.makedirs(args.output_folder, exist_ok=True)

    log_files = extract(
        args.input_folder,
        args.output_folder,
        datetime.datetime.strptime(args.start_date, date_format),
        datetime.datetime.strptime(args.end_date, date_format)
    )

    first_log_file_path = os.path.join(
        args.input_folder,
        log_files[0]
    )
    extract_interactions_marginals(
        first_log_file_path,
        args.output_folder
    )


if __name__ == '__main__':
    main()

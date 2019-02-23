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

def datetime_2_subfolder(dt):
    return 'data/' + str(dt.year) + '/' + str(dt.month).zfill(2) + '/' + str(dt.day).zfill(2) + '_0.json'

class logs_entry:
    def __init__(self, file_name, start_datetime = datetime.datetime.min, end_datetime=datetime.datetime.max):
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.file_name = file_name
    
    def is_cutoff_needed(self):
        return self.start_datetime != datetime.datetime.min or self.end_datetime != datetime.datetime.max

def is_same_day(first, second):
    return first.year == second.year and first.month == second.month and first.day == second.day

def ds_timestamp_parse(ds_timestamp):
    return datetime.datetime.strptime(ds_timestamp, "%Y-%m-%dT%H:%M:%S.%f0Z")

def get_timestamp(dsline):
    position = dsline.find('Timestamp')
    if position == -1:
        return None

    datetimeStart = position + 12
    datetimeEnd = dsline.find('"', datetimeStart)
    return ds_timestamp_parse(dsline[datetimeStart:datetimeEnd])

def copy_with_cutoff(input_log_entry, stream):
    with open(input_log_entry.file_name, 'r') as fin:
        for line in fin:
            if (line.startswith('{"_label_cost')):
                ts = get_timestamp(line)
                if ts is not None and input_log_entry.start_datetime <= ts and ts < input_log_entry.end_datetime:
                    stream.write(line)


def handle_log_file(input_log_entry, stream):
    if (os.path.isfile(input_log_entry.file_name)):
        if not input_log_entry.is_cutoff_needed():
            print('Processing whole file: ' + input_log_entry.file_name)

            command = 'cat ' + input_log_entry.file_name
            process = subprocess.Popen(command.split(), universal_newlines=True, stdout=stream, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if error:
                print('ERROR: ' + error)
        else:
            print('Processing partially: ' + input_log_entry.file_name)
            copy_with_cutoff(input_log_entry, stream)
    else:
        print('Cannot find file: ' + input_log_entry.file_name)

def is_good_for_train(line):
    return line is not None and line.startswith('{"_label_cost') or line.startswith('{"o":') or line.startswith('{"Timestamp"')

def iterate_ds_logs(start_datetime, end_datetime):
    start_date = datetime.datetime(start_datetime.year, start_datetime.month, start_datetime.day)
    end_date = datetime.datetime(end_datetime.year, end_datetime.month, end_datetime.day)

    for d in (start_date + datetime.timedelta(i) for i in range((end_date - start_date).days + 1)):
        s = start_datetime if is_same_day(d, start_datetime) else datetime.datetime.min
        e = end_datetime if is_same_day(d, end_datetime) else datetime.datetime.max
        yield logs_entry(datetime_2_subfolder(d), s, e)
        
def extract(input_folder, start_datetime, end_datetime, stream):
    for ds_entry in iterate_ds_logs(start_datetime, end_datetime):
        ds_entry.file_name = os.path.join(input_folder, ds_entry.file_name)
        handle_log_file(ds_entry, stream)

class vw_wrapper:
    def __init__(self, vw_path, cache_path):
        command = vw_path + ' --cb_adf --dsjson --cache_file ' + cache_path
        self._process = subprocess.Popen(command.split(), universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def parse_vw_output(self, txt):
        result = {}
        for line in txt.split('\n'):
            if '=' in line:
                index = line.find('=')
                key = line[0:index].strip()
                value = line[index+1:].strip()
                result[key] = value
        return result

    def stdin(self):
        return self._process.stdin

    def finalize(self):
        output, error = self._process.communicate()
        return self.parse_vw_output(error)

print("Training vw model...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="ouput folder")
parser.add_argument("--start_datetime", type=str, help="start datetime")
parser.add_argument("--end_datetime", type=str, help="end datetime")
parser.add_argument("--pattern", type=str, help="date time parsing pattern")
args = parser.parse_args()

start_datetime = datetime.datetime.strptime(args.start_datetime, args.pattern)
end_datetime = datetime.datetime.strptime(args.end_datetime, args.pattern)

print("Input folder: %s" % args.input_folder)
print("Output folder: %s" % args.output_folder)

print('Started: ' + str(datetime.datetime.now()))

os.makedirs(args.output_folder, exist_ok=True)
cache_path = os.path.join(args.output_folder, 'dataset.cache')
vw = vw_wrapper(vw_path = '/usr/local/bin/vw', cache_path = cache_path)
extract(args.input_folder, start_datetime, end_datetime, vw.stdin())
vw.finalize()
print('Done: '+ str(datetime.datetime.now()))



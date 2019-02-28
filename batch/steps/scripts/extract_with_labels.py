# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import datetime
import shutil

def datetime_2_path(dt):
    return 'data/' + str(dt.year) + '/' + str(dt.month).zfill(2) + '/' + str(dt.day).zfill(2) + '_0.json'

def handle_log_file(input_path, output_path):
    if (os.path.isfile(input_path)):
        print('Copying: ' + input_path + ' to ' + output_path)
        shutil.copyfile(input_path, output_path)
        return True
    else:
        print('Cannot find file: ' + input_path)
        return False

def iterate_ds_logs(start_datetime, end_datetime):
    start_date = datetime.datetime(start_datetime.year, start_datetime.month, start_datetime.day)
    end_date = datetime.datetime(end_datetime.year, end_datetime.month, end_datetime.day)
    for d in (start_date + datetime.timedelta(i) for i in range((end_date - start_date).days + 1)):
        yield datetime_2_path(d)
        
def extract(input_folder, start_datetime, end_datetime, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    batch_id = 0
    for ds_log in iterate_ds_logs(start_datetime, end_datetime):
        ds_log = os.path.join(input_folder, ds_log)
        print('Processing log file: ' + ds_log)
        output_path = os.path.join(output_folder, str(batch_id) + '.json')
        if handle_log_file(ds_log, output_path):
            batch_id = batch_id + 1

print("Extracting data from application logs...")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input_folder", type=str, help="input folder")
parser.add_argument("--output_folder", type=str, help="output folder")
parser.add_argument("--start_datetime", type=str, help="start datetime of batch")
parser.add_argument("--end_datetime", type=str, help="end datetime of batch")
parser.add_argument("--pattern", type=str, help="date time parsing pattern")
args = parser.parse_args()

print("Argument 1: %s" % args.input_folder)
print("Argument 2: %s" % args.output_folder)
print("Argument 3: %s" % args.start_datetime)
print("Argument 4: %s" % args.end_datetime)
print("Argument 5: %s" % args.pattern)

start_datetime = datetime.datetime.strptime(args.start_datetime, args.pattern)
end_datetime = datetime.datetime.strptime(args.end_datetime, args.pattern)

extract(args.input_folder, start_datetime, end_datetime, args.output_folder)
print("Done.")


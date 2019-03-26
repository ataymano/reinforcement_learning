# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.
import argparse
import os
import datetime
from azureml.core.run import Run
import subprocess
import shutil

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
    def cache(vw_path, base_command, cache_path, input_path, counter, prediction_name = None):
        print("cache_path:" + cache_path)
        print("input_path:" + input_path)

        if prediction_name:
            base_command += ' -p ' + prediction_name + '_' + str(counter) + '.pred'
        if counter == 1:
            command = vw_path + ' ' + base_command + ' --cache_file ' + cache_path + ' -d ' + input_path + ' -f ' + str(counter) + '_model.vw' + '  --save_resume --preserve_performance_counters'
        else:
            command = vw_path + base_command + ' --cache_file ' + cache_path + ' -d ' + input_path + ' -f ' + str(counter) + '_model.vw' + '  --save_resume --preserve_performance_counters' + ' -i ' + str(counter - 1) + '_model.vw '

        print(str(counter) + "command: " + command)
        process = subprocess.Popen(command.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output, error = execution.communicate()

        print("==output==")
        print(process.communicate())
        # return Vw._parse_vw_output(error)

class LogsExtractor:
    class Entry:
        def __init__(
            self,
            file_name,
            start_datetime = datetime.datetime.min, end_datetime=datetime.datetime.max
        ):
            self.start_datetime = start_datetime
            self.end_datetime = end_datetime
            self.file_name = file_name

        def is_cutoff_needed(self):
            return self.start_datetime != datetime.datetime.min or    self.end_datetime != datetime.datetime.max

    @staticmethod
    def _datetime_2_path(dt):
        return 'data/' + str(dt.year) + '/' + str(dt.month).zfill(2) + '/' + str(dt.day).zfill(2) + '_0.json'

    @staticmethod
    def _ds_timestamp_parse(ds_timestamp):
        return datetime.datetime.strptime(ds_timestamp, "%Y-%m-%dT%H:%M:%S.%f0Z")

    @staticmethod
    def _get_timestamp(dsline):
        position = dsline.find('Timestamp')
        if position == -1:
            return None

        datetimeStart = position + 12
        datetimeEnd = dsline.find('"', datetimeStart)
        return LogsExtractor._ds_timestamp_parse(
            dsline[datetimeStart:datetimeEnd]
        )

    @staticmethod
    def iterate_files(input_folder, start_datetime, end_datetime):
        start_date = datetime.datetime(start_datetime.year, start_datetime.month, start_datetime.day)
        end_date = datetime.datetime(end_datetime.year, end_datetime.month, end_datetime.day)
        for d in (start_date + datetime.timedelta(i) for i in range((end_date - start_date).days + 1)):
            logfile = os.path.join(input_folder, LogsExtractor._datetime_2_path(d))
            if os.path.isfile(logfile):
                yield LogsExtractor.Entry(file_name = logfile, start_datetime = start_datetime, end_datetime = end_datetime)
        return
        yield

def extract(input_folder, start_datetime, end_datetime, output_path):
    print('Creating folder for the file: ' + output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    counter = 1;
    for f in LogsExtractor.iterate_files(input_folder, start_datetime, end_datetime):
        cache_path = os.path.join(output_path, str(counter) + '.cache')
        Vw.cache(
            vw_path = '/usr/local/bin/vw',
            cache_path = cache_path,
            input_path = f.file_name,
            counter = counter
        )
        counter += 1

def Log(key, value):
    logger = Run.get_context()
    logger.log(key, value)
    print(key + ': ' + str(value))

def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("train")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output_path", type=str, help="output path")
    parser.add_argument("--start_datetime", type=str, help="start datetime of batch")
    parser.add_argument("--end_datetime", type=str, help="end datetime of batch")
    parser.add_argument("--pattern", type=str, help="date time parsing pattern")
    args = parser.parse_args()

    Log('Input folder', args.input_folder)
    Log('Output path', args.output_path)

    os.makedirs(args.output_path, exist_ok=True)

    start_datetime = datetime.datetime.strptime(args.start_datetime, args.pattern)
    end_datetime = datetime.datetime.strptime(args.end_datetime, args.pattern)
    print('Extracting...')
    extract(args.input_folder, start_datetime, end_datetime, args.output_path)
    print('Done.')

if __name__ == '__main__':
    main()

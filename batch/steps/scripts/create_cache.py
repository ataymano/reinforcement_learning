import argparse
import os
import datetime
import json
from helpers import vw
from helpers import utils


class LogsExtractor:
    class Entry:
        def __init__(
            self,
            file_name,
            previous_date=None,
            current_date=None
        ):
            self.file_name = file_name
            self.previous_date = previous_date
            self.current_date = current_date

    @staticmethod
    def _get_log_path(input_folder, date):
        log_path = 'data/%s/%s/%s_0.json' % (
            str(date.year),
            str(date.month).zfill(2),
            str(date.day).zfill(2)
        )
        return os.path.join(input_folder, log_path)

    @staticmethod
    def iterate_files(folder, start_date, end_date):
        previous_date = None
        for i in range((end_date - start_date).days + 1):
            current_date = start_date + datetime.timedelta(i)
            logfile = LogsExtractor._get_log_path(folder, current_date)
            if os.path.isfile(logfile):
                print(previous_date)
                print(current_date)
                yield LogsExtractor.Entry(
                    file_name=logfile,
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
        log_files.append(log.file_name)
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
            '-d': log.file_name,
            '-f': new_model_path
        }

        if (previous_model_path):
            command_options['-i'] = previous_model_path

        command = vw.build_command('', command_options)
        print("create cache command: ")
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

    print('Extracting...')
    extract(
        args.input_folder,
        args.output_folder,
        datetime.datetime.strptime(args.start_date, date_format),
        datetime.datetime.strptime(args.end_date, date_format)
    )
    print('Done.')


if __name__ == '__main__':
    main()

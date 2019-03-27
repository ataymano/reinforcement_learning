import argparse
import os
import datetime
from azureml.core.run import Run
import subprocess


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
    def cache(
        vw_path,
        input_path,
        cache_path,
        previous_model_path,
        new_model_path
    ):
        print("cache_path:" + cache_path)
        print("input_path:" + input_path)

        command = ' '.join([
            vw_path,
            '--cb_adf',
            '--dsjson',
            '--cache_file',
            cache_path,
            '-d',
            input_path,
            '-f',
            new_model_path,
            '--save_resume',
            '--preserve_performance_counters'
        ])

        if previous_model_path:
            command = ' '.join([
                command,
                '-i',
                previous_model_path
            ])
        print(command)
        process = subprocess.Popen(
            command.split(),
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # output, error = execution.communicate()
        # return Vw._parse_vw_output(error)
        print("==output==")
        print(process.communicate())


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


def get_file_name(date, type):
    if date:
        date_str = str(date.year) + str(date.month) + str(date.day)
        if type == 'cache':
            return '%s.cache' % (date_str)
        elif type == 'model':
            return '%s.vw' % (date_str)
    return None


def extract(input_folder, output_folder, start_date, end_date):
    for log in LogsExtractor.iterate_files(input_folder, start_date, end_date):
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

        Vw.cache(
            vw_path='/usr/local/bin/vw',
            input_path=log.file_name,
            cache_path=cache_path,
            previous_model_path=previous_model_path,
            new_model_path=new_model_path
        )


def Log(key, value):
    logger = Run.get_context()
    logger.log(key, value)
    print(key + ': ' + str(value))


def main():
    print("Extracting data from application logs...")

    parser = argparse.ArgumentParser("create cache")
    parser.add_argument("--input_folder", type=str, help="input folder")
    parser.add_argument("--output_folder", type=str, help="output folder")
    parser.add_argument("--start_date", type=str, help="start date")
    parser.add_argument("--end_date", type=str, help="end date")
    args = parser.parse_args()

    date_format = '%m/%d/%Y'

    Log('Input folder', args.input_folder)
    Log('Output folder', args.output_folder)

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
